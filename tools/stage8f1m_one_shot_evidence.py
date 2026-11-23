"""F1M one-shot custody: 384 original gzip parts, 32 incremental fsynced checks.

Stdlib ONLY. Original scientific World.step happens exclusively inside
stage8f1m_scientific_native after the protected remote GitHub reservation.
Canonical readback means no SECOND native decision or T6..T60 continuation.
"""
from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import tarfile

PARTS = (
    "source", "recent_t5", "stale_t5", "recent_sham_t5",
    "recent_carry", "recent_carry_sham", "recent_zero", "recent_zero_sham",
    "stale_carry", "stale_carry_sham", "stale_zero", "stale_zero_sham",
)
SCHEMA="i3-stage8f1m-incremental-original-part/v0"
CUSTODY_SCHEMA="i3-stage8f1m-first-only-native-custody/v0"


def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,
                      separators=(",",":"),allow_nan=False).encode("utf-8")


def digest(raw):
    return sha256(raw).hexdigest()


def new_file(path,data):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())


def compressed(raw):
    buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,mode="wb",filename="",mtime=0,compresslevel=9) as out:
        out.write(raw)
    return buffer.getvalue()


class CaseWriter:
    """Write each part immediately. The whole M root need not survive a crash."""
    def __init__(self,base,expected):
        self.base=Path(base)
        self.base.mkdir(parents=True,exist_ok=False)
        self.expected=tuple(expected)
        self.entries=[]
        self.completed=[]
        self._active_root=None
        self._active_count=0

    def part(self,root,kind,native):
        index=len(self.completed)
        if (index>=len(self.expected) or self.expected[index]!=root
                or self._active_count>=len(PARTS)
                or kind!=PARTS[self._active_count]
                or (self._active_root is not None and self._active_root!=root)):
            raise RuntimeError("duplicate, out-of-order or missing F1M original part")
        self._active_root=root
        raw=canonical({"schema":SCHEMA,"id":root,"part":kind,"native":native})
        gz=compressed(raw)
        rel=f"{root}/{kind}.json.gz"
        new_file(self.base/rel,gz)
        self.entries.append({
            "path":rel,"id":root,"part":kind,
            "original_sha256":digest(raw),"gzip_sha256":digest(gz),
            "original_bytes":len(raw),"gzip_bytes":len(gz)})
        self._active_count+=1

    def finalize_case(self,row):
        id_=row["origin"]["id"]
        if self.expected[len(self.completed)]!=id_:
            raise RuntimeError("unexpected completed M origin")
        if "case_sha256" not in row:
            from tools import stage8f1c_paid_postaction_learning as C
            row["case_sha256"]=C.digest(row)
        if not row["source"]["source_valid"]:
            # All 12 committed names retained, but no fabricated World.step.
            while self._active_count<len(PARTS):
                part=PARTS[self._active_count]
                self.part(id_,part,{
                    "status":"NOT_EXECUTED_UNFUNDED_OR_INCOMPLETE_SOURCE",
                    "source_sha256":row["source"]["source_receipt_sha256"],
                    "no_fabricated_native":True})
        if self._active_count!=len(PARTS):
            raise RuntimeError("valid M source incomplete original receipts")
        self.completed.append(id_)
        checkpoint={
            "schema":"i3-stage8f1m-incremental-case-checkpoint/v0",
            "root":id_,"case_sha256":row["case_sha256"],
            "completed_roots":list(self.completed),
            "entries":list(self.entries)}
        new_file(self.base/f"_checkpoint_{len(self.completed):02}.json",
                 canonical(checkpoint)+b"\n")
        self._active_root=None
        self._active_count=0


def _archive(root,names,dest):
    """Deterministic streaming, no in-memory 400+ MB tar file."""
    with Path(dest).open("xb") as fd:
        with gzip.GzipFile(fileobj=fd,filename="",mode="wb",mtime=0,compresslevel=6) as g:
            with tarfile.open(fileobj=g,mode="w|",format=tarfile.USTAR_FORMAT) as tar:
                for name in sorted(names):
                    data=(Path(root)/name).read_bytes()
                    item=tarfile.TarInfo(name)
                    item.size=len(data)
                    item.mode=0o644
                    item.mtime=0
                    item.uid=item.gid=0
                    item.uname=item.gname=""
                    tar.addfile(item,io.BytesIO(data))
        fd.flush()
        os.fsync(fd.fileno())


def file_digest(path):
    hasher=sha256()
    with Path(path).open("rb") as inp:
        for chunk in iter(lambda: inp.read(1024*1024),b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def finish(writer,index,root,reservation):
    root=Path(root)
    if (len(writer.completed)!=len(writer.expected) or
            len(writer.entries)!=12*len(writer.expected) or
            writer.completed!=list(writer.expected) or
            [r["origin"]["id"] for r in index["rows"]]!=list(writer.expected)):
        raise RuntimeError("F1M original 384 parts/32 population truncated")
    new_file(root/"F1M_NATIVE_INDEX.json",canonical(index)+b"\n")
    # The secondary file is a cold parse, not another native World.step.
    readback=json.loads((root/"F1M_NATIVE_INDEX.json").read_bytes())
    new_file(root/"F1M_CANONICAL_READBACK.json",canonical(readback)+b"\n")
    names=[x["path"] for x in writer.entries]
    names += [f"_checkpoint_{i:02}.json" for i in range(1,len(writer.completed)+1)]
    dest=root/"F1M_ORIGINALS_384_GZIP.tar.gz"
    _archive(writer.base,names,dest)
    manifest={
        "schema":CUSTODY_SCHEMA,"phase":"F1M_HELDOUT_RELEASE",
        "roots":writer.completed,"original_part_count":len(writer.entries),
        "part_names":list(PARTS),"entries":writer.entries,
        "checkpoint_count":len(writer.completed),
        "originals_tar_gzip_sha256":file_digest(dest),
        "native_index_sha256":digest(canonical(index)),
        "canonical_readback_sha256":digest(canonical(readback)),
        "byte_equal_readback_no_second_native":canonical(index)==canonical(readback),
        "heldout_native_passes":1,
        "origin_source_and_four_arms_and_shams_single_native_execution":True,
        "reservation_sha256":digest(canonical(reservation)),
        "scientific_verdict":None}
    new_file(root/"F1M_CUSTODY_MANIFEST.json",canonical(manifest)+b"\n")
    return manifest


def read_bundle(root,expected_ids,on_root):
    """Cold byte reader. Every named original part SHA must match the manifest."""
    root=Path(root)
    m=json.loads((root/"F1M_CUSTODY_MANIFEST.json").read_bytes())
    index=json.loads((root/"F1M_NATIVE_INDEX.json").read_bytes())
    readback=json.loads((root/"F1M_CANONICAL_READBACK.json").read_bytes())
    if (m["schema"]!=CUSTODY_SCHEMA or m["phase"]!="F1M_HELDOUT_RELEASE"
            or m["roots"]!=list(expected_ids)
            or m["original_part_count"]!=12*len(expected_ids)
            or len(m["entries"])!=12*len(expected_ids)
            or m["part_names"]!=list(PARTS)
            or m["checkpoint_count"]!=len(expected_ids)
            or index!=readback
            or digest(canonical(index))!=m["native_index_sha256"]
            or digest(canonical(readback))!=m["canonical_readback_sha256"]
            or not m["byte_equal_readback_no_second_native"]
            or m["heldout_native_passes"]!=1):
        raise ValueError("F1M science custody, one-pass, index or canonical readback invalid")
    archive=root/"F1M_ORIGINALS_384_GZIP.tar.gz"
    if file_digest(archive)!=m["originals_tar_gzip_sha256"]:
        raise ValueError("F1M aggregate original archive changed")
    required={f"{id_}/{part}.json.gz" for id_ in expected_ids for part in PARTS}
    required|={f"_checkpoint_{i:02}.json" for i in range(1,len(expected_ids)+1)}
    expected={e["path"]:e for e in m["entries"]}
    if len(expected)!=12*len(expected_ids):
        raise ValueError("duplicate original source path")
    if [r["origin"]["id"] for r in index["rows"]]!=list(expected_ids):
        raise ValueError("F1M native index does not bind 32 literal sources")
    if not callable(on_root):
        raise ValueError("streamed per-root cold callback mandatory")
    active={}
    emitted=[]
    with tarfile.open(archive,"r|gz") as tar:
        seen=set()
        for item in tar:
            name=item.name
            if (not item.isfile() or name in seen or name not in required):
                raise ValueError("duplicate/missing/unsafe F1M archive member")
            seen.add(name)
            raw=tar.extractfile(item).read()
            if name.startswith("_checkpoint_"):
                checkpoint=json.loads(raw)
                tick=int(name.split("_")[-1].split(".")[0])
                if (checkpoint.get("schema")!="i3-stage8f1m-incremental-case-checkpoint/v0"
                        or checkpoint.get("completed_roots")!=list(expected_ids)[:tick]
                        or checkpoint.get("entries")!=m["entries"][:12*tick]):
                    raise ValueError("incremental M source checkpoint changed")
                continue
            entry=expected[name]
            if (entry["gzip_sha256"]!=digest(raw)
                    or entry["gzip_bytes"]!=len(raw)):
                raise ValueError("original F1M compressed SHA mismatch: "+name)
            dec=gzip.decompress(raw)
            if (entry["original_sha256"]!=digest(dec)
                    or entry["original_bytes"]!=len(dec)):
                raise ValueError("original F1M raw SHA mismatch: "+name)
            part=json.loads(dec)
            if (part["schema"]!=SCHEMA
                    or part["id"]!=entry["id"] or part["part"]!=entry["part"]
                    or name!=f"{part['id']}/{part['part']}.json.gz"):
                raise ValueError("wrong F1M native original part identity")
            id_=part["id"]
            if id_!=expected_ids[len(emitted)]:
                raise ValueError("F1M tar identity out of order")
            if part["part"] in active:
                raise ValueError("duplicate original native part within source")
            active[part["part"]]=part["native"]
            if len(active)==len(PARTS):
                if set(active)!=set(PARTS):
                    raise ValueError("F1M missing T5, source or sham original")
                on_root(index["rows"][len(emitted)],dict(active))
                emitted.append(id_)
                active.clear()
        if seen!=required:
            raise ValueError("missing F1M original native gzip: "+str(required-seen))
    if emitted!=list(expected_ids) or active:
        raise ValueError("F1M cold audit omitted native root")
    return index,m,len(emitted)


def run(base,reservation_path):
    """SCIENTIFIC mode only. No CLI shortcut, no DEV_M or replays."""
    from tools import stage8f1m_one_shot_reservation as R
    from tools import stage8f1m_scientific_native as P
    receipt=R.load_receipt(reservation_path)
    R.verify_remote(receipt)
    grid=P.release_grid()
    base=Path(base)
    base.mkdir(parents=True,exist_ok=False)
    writer=CaseWriter(base/"original_parts",R.ROOT_IDS)
    index=P.produce_release(reservation_path,writer)
    manifest=finish(writer,index,base,receipt)
    # Independent byte readback of EVERY gzip before removing duplicate
    # unbundled copies. Archive preserves all 384 original bytes permanently.
    _,_,checked=read_bundle(base,R.ROOT_IDS,lambda meta,parts: None)
    if checked!=32:
        raise RuntimeError("original bytes not intact at first-only readback")
    import shutil
    shutil.rmtree(writer.base)
    print(json.dumps({
        "status":"F1M_FIRST_ONLY_NATIVE_NOT_YET_COLD_AUDITED",
        "origins":len(writer.completed),"original_gzip_parts":len(writer.entries),
        "unique_native_passes":manifest["heldout_native_passes"],
        "readback_without_second_world_step":True,
        "science_verdict":None},sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--science-only",action="store_true",required=True)
    p.add_argument("--reservation",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    run(a.output_dir,a.reservation)


if __name__=="__main__":
    main()
