"""F1N one-shot 48-root, 336 original gzip SHA custody with streamed readback.

Write each ORIGINAL part immediately, exclusively once, fsync and checkpoint
before proceeding to the next root. If native science fails post-claim,
partial original_parts survive as immutable RAW Release or Actions artifact.
This module's readback and independent cold audit never call World.step.
"""
from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import shutil
import tarfile

from tools import stage8f1n_prereg_static_guard as FROZEN

PARTS = tuple(FROZEN.PARTS)
PART_SCHEMA = "i3-stage8f1n-native-incremental-receipt/v0"
CUSTODY_SCHEMA = "i3-stage8f1n-first-only-native-custody/v0"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(raw):
    return sha256(raw).hexdigest()


def file_digest(path):
    h = sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def new_file(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def compressed(raw):
    b = io.BytesIO()
    with gzip.GzipFile(fileobj=b, mode="wb", filename="", mtime=0,
                       compresslevel=9) as writer:
        writer.write(raw)
    return b.getvalue()


class CaseWriter:
    def __init__(self, base, roots):
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=False)
        self.roots = tuple(roots)
        self.entries = []
        self.completed = []
        self.cases = []
        self._active = None
        self._active_count = 0

    def part(self, root, kind, native):
        idx = len(self.completed)
        if (idx >= len(self.roots) or self.roots[idx] != root or
                (self._active is not None and self._active != root) or
                self._active_count >= len(PARTS) or
                kind != PARTS[self._active_count]):
            raise RuntimeError("F1N original part duplicate, missing or out of order")
        self._active = root
        raw = canonical({"schema": PART_SCHEMA, "id": root,
                         "part": kind, "native": native})
        zipped = compressed(raw)
        rel = f"{root}/{kind}.json.gz"
        new_file(self.base/rel, zipped)
        self.entries.append({"path": rel, "id": root, "part": kind,
                             "raw_sha256": digest(raw),
                             "gzip_sha256": digest(zipped),
                             "raw_bytes": len(raw), "gzip_bytes": len(zipped)})
        self._active_count += 1

    def finish_incomplete(self, origin, src, comparison):
        """Mark unexecuted originals WITHOUT performing or inventing a motor."""
        while self._active_count < len(PARTS):
            self.part(origin["id"], PARTS[self._active_count], {
                "status": "NOT_EXECUTED_UNFUNDED_OR_INCOMPLETE_SOURCE",
                "native_world_steps_created": 0,
                "source_receipt_sha256": digest(canonical(src)),
            })
        self.finalize_case(origin, comparison, False, False)

    def finalize_case(self, origin, comparison, source_valid, shams_neutral):
        root = origin["id"]
        if (len(self.completed) >= len(self.roots) or
                self.roots[len(self.completed)] != root or
                self._active_count != len(PARTS)):
            raise RuntimeError("F1N valid source missing original parts")
        self.cases.append({"origin": origin, "comparison": comparison,
                           "source_valid": source_valid,
                           "shams_neutral": shams_neutral})
        self.completed.append(root)
        checkpoint = {"schema": "i3-stage8f1n-incremental-checkpoint/v0",
                      "completed": len(self.completed),
                      "roots": list(self.completed),
                      "entries": list(self.entries),
                      "cases": list(self.cases)}
        new_file(self.base/f"_checkpoint_{len(self.completed):02d}.json",
                 canonical(checkpoint) + b"\n")
        self._active = None
        self._active_count = 0


def _archive(root, names, dest):
    """Deterministic constant-space tarball. Does NOT rerun a single life."""
    with Path(dest).open("xb") as f:
        with gzip.GzipFile(fileobj=f, filename="", mode="wb", mtime=0,
                           compresslevel=6) as writer:
            with tarfile.open(fileobj=writer, mode="w|",
                              format=tarfile.USTAR_FORMAT) as archive:
                for name in sorted(names):
                    raw = (Path(root)/name).read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size = len(raw)
                    info.mode = 0o644
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    archive.addfile(info, io.BytesIO(raw))
        f.flush()
        os.fsync(f.fileno())


def finish(writer, index, root, reservation):
    root = Path(root)
    if (list(writer.roots) != writer.completed or
            len(writer.cases) != len(writer.roots) or
            len(writer.entries) != len(writer.roots)*len(PARTS) or
            index["rows"] != writer.cases):
        raise RuntimeError("F1N 48 roots/336 original receipts incomplete")
    new_file(root/"F1N_NATIVE_INDEX.json", canonical(index) + b"\n")
    readback = json.loads((root/"F1N_NATIVE_INDEX.json").read_bytes())
    new_file(root/"F1N_CANONICAL_READBACK.json", canonical(readback) + b"\n")
    names = [entry["path"] for entry in writer.entries]
    names += [f"_checkpoint_{i:02d}.json" for i in range(1,len(writer.roots)+1)]
    tar = root/"F1N_ORIGINALS_336_GZIP.tar.gz"
    _archive(writer.base, names, tar)
    manifest = {
        "schema": CUSTODY_SCHEMA, "phase": "F1N_HELDOUT_RELEASE",
        "roots": writer.completed, "original_part_count": len(writer.entries),
        "part_names": list(PARTS), "entries": writer.entries,
        "checkpoint_count": len(writer.completed),
        "original_tar_sha256": file_digest(tar),
        "native_index_sha256": digest(canonical(index)),
        "canonical_readback_sha256": digest(canonical(readback)),
        "byte_equal_readback_no_native_rerun": index == readback,
        "heldout_native_passes": 1,
        "reservation_sha256": digest(canonical(reservation)),
        "scientific_verdict": None,
    }
    new_file(root/"F1N_CUSTODY_MANIFEST.json", canonical(manifest) + b"\n")
    return manifest


def read_bundle(root, expected_roots, on_root):
    """Verify every gzip and checkpoint; deliver only one bounded root at a time."""
    root = Path(root)
    m = json.loads((root/"F1N_CUSTODY_MANIFEST.json").read_bytes())
    index = json.loads((root/"F1N_NATIVE_INDEX.json").read_bytes())
    readback = json.loads((root/"F1N_CANONICAL_READBACK.json").read_bytes())
    ids = list(expected_roots)
    count = len(ids)*len(PARTS)
    if not (m.get("schema") == CUSTODY_SCHEMA and
            m.get("phase") == "F1N_HELDOUT_RELEASE" and
            m.get("roots") == ids and m.get("original_part_count") == count and
            len(m.get("entries",[])) == count and
            m.get("part_names") == list(PARTS) and
            m.get("checkpoint_count") == len(ids) and
            m.get("heldout_native_passes") == 1 and
            m.get("byte_equal_readback_no_native_rerun") is True and
            m.get("scientific_verdict") is None and
            index == readback and digest(canonical(index)) == m["native_index_sha256"] and
            digest(canonical(readback)) == m["canonical_readback_sha256"] and
            [r["origin"]["id"] for r in index["rows"]] == ids):
        raise ValueError("F1N original custody/index/readback incomplete or inconsistent")
    archive = root/"F1N_ORIGINALS_336_GZIP.tar.gz"
    if file_digest(archive) != m["original_tar_sha256"]:
        raise ValueError("F1N original aggregate tar SHA mismatch")
    entries = m["entries"]
    paths = {x["path"]: x for x in entries}
    if len(paths) != count:
        raise ValueError("duplicate F1N native gzip path")
    required = {f"{rid}/{kind}.json.gz" for rid in ids for kind in PARTS}
    required |= {f"_checkpoint_{n:02d}.json" for n in range(1,len(ids)+1)}
    active = {}
    emitted = []
    with tarfile.open(archive, mode="r|gz") as archive_stream:
        seen=set()
        for member in archive_stream:
            name = member.name
            if name not in required or name in seen or not member.isfile():
                raise ValueError("F1N tar unexpected, duplicate or unsafe member")
            seen.add(name)
            buf = archive_stream.extractfile(member).read()
            if name.startswith("_checkpoint_"):
                idx = int(name.removeprefix("_checkpoint_").removesuffix(".json"))
                ck = json.loads(buf)
                if (ck["schema"] != "i3-stage8f1n-incremental-checkpoint/v0" or
                        ck["completed"] != idx or ck["roots"] != ids[:idx] or
                        ck["entries"] != entries[:idx*len(PARTS)] or
                        ck["cases"] != index["rows"][:idx]):
                    raise ValueError("F1N incremental source checkpoint tampered")
                continue
            entry = paths[name]
            if (digest(buf) != entry["gzip_sha256"] or
                    len(buf) != entry["gzip_bytes"]):
                raise ValueError("F1N original gzip bytes changed: " + name)
            raw = gzip.decompress(buf)
            if (digest(raw) != entry["raw_sha256"] or
                    len(raw) != entry["raw_bytes"]):
                raise ValueError("F1N original decoded bytes changed: " + name)
            value = json.loads(raw)
            if not (value.get("schema") == PART_SCHEMA and
                    value.get("id") == entry["id"] and
                    value.get("part") == entry["part"] and
                    name == f'{entry["id"]}/{entry["part"]}.json.gz' and
                    canonical(value) == raw):
                raise ValueError("F1N original part canonical identity mismatch")
            original_root = entry["id"]
            if original_root in emitted:
                raise ValueError("F1N duplicate root after emission")
            active.setdefault(original_root, {})[entry["part"]] = value["native"]
            if len(active[original_root]) == len(PARTS):
                if len(active) != 1 or ids[len(emitted)] != original_root:
                    raise ValueError("F1N original parts not a contiguous ordered root")
                on_root(index["rows"][len(emitted)], active.pop(original_root))
                emitted.append(original_root)
        if seen != required or active or emitted != ids:
            raise ValueError("F1N archival missing or unverified source parts")
    return index, m, len(emitted)


def run(root, reservation):
    """Actual 48 science only after full remote first-only verification."""
    from tools import stage8f1n_one_shot_reservation as R
    from tools import stage8f1n_scientific_native as NATIVE
    receipt = R.load_receipt(reservation)
    R.verify_remote(receipt)
    base = Path(root)
    base.mkdir(parents=True, exist_ok=False)
    writer = CaseWriter(base/"original_parts", R.ROOT_IDS)
    index = NATIVE.produce_release(reservation, writer)
    manifest = finish(writer, index, base, receipt)
    checked = read_bundle(base, R.ROOT_IDS, lambda m, r: None)
    if checked[2] != len(R.ROOT_IDS):
        raise RuntimeError("F1N 48 original roots not all read back")
    shutil.rmtree(writer.base)
    print(json.dumps({"status": "F1N_FIRST_ONLY_NATIVE_NOT_YET_COLD_AUDITED",
          "origins": len(writer.completed), "original_gzips": len(writer.entries),
          "source_passes": manifest["heldout_native_passes"],
          "science_verdict": None}, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--science-only", action="store_true", required=True)
    ap.add_argument("--reservation", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    options = ap.parse_args()
    run(options.output_dir, options.reservation)


if __name__ == "__main__":
    main()