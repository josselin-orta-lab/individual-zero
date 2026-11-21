"""F1K original custody, independent byte verification and technical reproduction.

No K-origin World.step on import. The --rehearsal path never reads a held-out
root; --release requires a remotely verified one-shot reservation before the
producer can execute even its first source tick. All original branches, null
sources and adverse outcomes are retained. No science verdict is issued here.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import gzip
import io
import json
import os
from pathlib import Path
import tarfile

ARMS = ("reference_p13", "reference_sham", "fixed_round_f1j")
FILES = (
    "F1K_ORIGINAL_NATIVE.json.gz",
    "F1K_TECHNICAL_REPRODUCTION.json.gz",
    "F1K_ORIGINALS_64_GZIP.tar.gz",
    "F1K_CUSTODY_MANIFEST.json",
)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(raw):
    return sha256(raw).hexdigest()


def deterministic_gzip(raw):
    b = io.BytesIO()
    with gzip.GzipFile(fileobj=b, mode="wb", filename="",
                       compresslevel=9, mtime=0) as out:
        out.write(raw)
    return b.getvalue()


def new_file(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as fd:
        fd.write(data)
        fd.flush()
        os.fsync(fd.fileno())


def exact_64_entries(report):
    roots = report.get("rows")
    if not isinstance(roots, list):
        raise ValueError("missing F1K original case records")
    if report["origin_count"] != len(roots):
        raise ValueError("population was silently truncated")
    for row in roots:
        origin = row["origin"]
        ident = origin["id"]
        if not (ident.startswith("K") or ident.startswith("DEV")):
            raise ValueError("unexpected origin identity")
        yield ident, "source", row["source"]
        for arm in ARMS:
            if arm in row["arms"]:
                record = row["arms"][arm]
            else:
                if row["source"]["valid_paid_personal_source"]:
                    raise ValueError("valid origin is missing pre-registered motor arm")
                record = {
                    "policy": arm,
                    "status": "NOT_EXECUTED_INVALID_PAID_PERSONAL_SOURCE",
                    "no_fabricated_native_steps": True,
                    "original_source_receipt_sha256":
                        row["source"]["source_receipt_sha256"],
                }
            yield ident, arm, record


class CaseWriter:
    def __init__(self, directory, origin_ids):
        self.path = Path(directory)
        self.path.mkdir(parents=True, exist_ok=False)
        self.expected = tuple(origin_ids)
        self.completed = []
        self.entries = []

    def __call__(self, row):
        ident = row["origin"]["id"]
        index = len(self.completed)
        if index >= len(self.expected) or self.expected[index] != ident:
            raise ValueError("out-of-order/duplicate scientific root")
        if row["case_sha256"] != digest(canonical({
            k:v for k,v in row.items() if k != "case_sha256"})):
            raise ValueError("origin was not sealed by native producer")
        source = row["source"]
        arms = row["arms"]
        for part in ("source", *ARMS):
            if part == "source":
                native = source
            elif part in arms:
                native = arms[part]
            else:
                if source["valid_paid_personal_source"]:
                    raise ValueError("valid paid source missing allocated arm")
                native = {
                    "policy": part,
                    "status": "NOT_EXECUTED_INVALID_PAID_PERSONAL_SOURCE",
                    "no_fabricated_native_steps": True,
                    "original_source_receipt_sha256":
                        source["source_receipt_sha256"],
                }
            item = {
                "schema": "i3-stage8f1k-native-origin-part/v0",
                "id": ident, "part": part, "native": native,
                "case_sha256": row["case_sha256"],
            }
            raw = canonical(item)
            compressed = deterministic_gzip(raw)
            relative = f"{ident}/{part}.json.gz"
            new_file(self.path / relative, compressed)
            self.entries.append({
                "path": relative, "id": ident, "part": part,
                "original_sha256": digest(raw),
                "gzip_sha256": digest(compressed),
                "original_bytes": len(raw), "gzip_bytes": len(compressed),
            })
        self.completed.append(ident)
        # A checkpoint index exists after EVERY native source+3-arm origin.
        # Never overwrite a previous negative/fatal receipt.
        checkpoint = {
            "schema": "i3-stage8f1k-incremental-custody/v0",
            "completed_origins": list(self.completed),
            "receipts": list(self.entries),
        }
        new_file(self.path / f"_checkpoint_{len(self.completed):02}.json",
                 canonical(checkpoint) + b"\n")


def _tar_files(directory, filenames):
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for relative in sorted(filenames):
            data = (Path(directory) / relative).read_bytes()
            info = tarfile.TarInfo(relative)
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o644
            tar.addfile(info, io.BytesIO(data))
    return deterministic_gzip(payload.getvalue())


def finalize(writer, report, technical, base, reservation=None):
    base = Path(base)
    if len(writer.completed) != report["origin_count"]:
        raise ValueError("incomplete first scientific original")
    if len(writer.entries) != 4 * report["origin_count"]:
        raise ValueError("not all source+three arms archived")
    orig = canonical(report)
    reproduce = canonical(technical)
    # Identical second technical reconstruction is a nonindependent
    # REPRODUCIBILITY proof, not another scientific sample or a retry.
    byte_equal = orig == reproduce
    new_file(base / "F1K_ORIGINAL_NATIVE.json.gz", deterministic_gzip(orig))
    new_file(base / "F1K_TECHNICAL_REPRODUCTION.json.gz",
             deterministic_gzip(reproduce))
    members = [row["path"] for row in writer.entries]
    members += [f"_checkpoint_{i:02}.json" for i in
                range(1, report["origin_count"]+1)]
    archive = _tar_files(writer.path, members)
    new_file(base / "F1K_ORIGINALS_64_GZIP.tar.gz", archive)
    index = {
        "schema": "i3-stage8f1k-original-and-technical-custody/v0",
        "phase": report["phase"], "worlds": report["worlds"],
        "roots": writer.completed, "native_part_count": len(writer.entries),
        "entries": writer.entries,
        "native_original_sha256": digest(orig),
        "native_technical_sha256": digest(reproduce),
        "technical_byte_identical": byte_equal,
        "originals_tar_gzip_sha256": digest(archive),
        "reservation_sha256": (digest(canonical(reservation))
                               if reservation is not None else None),
        "native_scientific_verdict": None,
        "original_preserved_even_if_reproduction_fails": True,
    }
    new_file(base / "F1K_CUSTODY_MANIFEST.json", canonical(index) + b"\n")
    if not byte_equal:
        raise ValueError("second technical construction differs: originals preserved")
    return index


def verify_bundle(folder, report=None):
    folder = Path(folder)
    original_compressed = (folder/"F1K_ORIGINAL_NATIVE.json.gz").read_bytes()
    original = gzip.decompress(original_compressed)
    if report is None:
        report = json.loads(original)
    if canonical(report) != original:
        raise ValueError("F1K original bytes do not match parsed source")
    technical = gzip.decompress(
        (folder/"F1K_TECHNICAL_REPRODUCTION.json.gz").read_bytes())
    index = json.loads((folder/"F1K_CUSTODY_MANIFEST.json").read_bytes())
    if (index["native_original_sha256"] != digest(original)
            or index["native_technical_sha256"] != digest(technical)
            or technical != original
            or index["native_part_count"] != 4 * report["origin_count"]
            or index["roots"] != report["origin_ids"]
            or index["phase"] != report["phase"]):
        raise ValueError("F1K provenance, technical replay or 4-arm count changed")
    archive = (folder/"F1K_ORIGINALS_64_GZIP.tar.gz").read_bytes()
    if index["originals_tar_gzip_sha256"] != digest(archive):
        raise ValueError("F1K archived native originals were swapped")
    expected = {}
    for (ident, part, native), meta in zip(
            exact_64_entries(report), index["entries"]):
        relative = f"{ident}/{part}.json.gz"
        if (meta["path"] != relative or meta["id"] != ident
                or meta["part"] != part or relative in expected):
            raise ValueError("duplicate/filtered native gzip part")
        expected[relative] = (native, meta)
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(archive)), mode="r:") as tar:
        members = {m.name:m for m in tar.getmembers()}
        if len(members) != 5 * report["origin_count"]:
            raise ValueError("missing original gzip or incremental checkpoint")
        for relative,(native,meta) in expected.items():
            compressed = tar.extractfile(members[relative]).read()
            raw = gzip.decompress(compressed)
            item = json.loads(raw)
            if (item["id"] != meta["id"] or item["part"] != meta["part"]
                    or item["native"] != native
                    or digest(compressed) != meta["gzip_sha256"]
                    or digest(raw) != meta["original_sha256"]
                    or len(raw) != meta["original_bytes"]
                    or len(compressed) != meta["gzip_bytes"]):
                raise ValueError("F1K original per-arm gzip source tampered")
    return {
        "status":"F1K_INDEPENDENT_BYTE_CUSTODY_PASS",
        "phase":index["phase"],
        "original_sha256":digest(original),
        "original_native_gzips":len(expected),
        "same_bytes_technical_reproduction":True,
        "roots":len(report["rows"]),
    }


def run(phase,base,reservation_file=None):
    """Native source generation ONLY after optional remote consumption check."""
    from tools import stage8f1k_policy_cost_value_prospective as P
    base=Path(base)
    base.mkdir(parents=True, exist_ok=False)
    if phase == "F1K_HELDOUT_RELEASE":
        from tools import stage8f1k_one_shot_reservation as R
        if reservation_file is None:
            raise PermissionError("F1K heldout requires issued remote reservation")
        receipt = R.load_receipt(Path(reservation_file))
        R.verify_remote(receipt)
        os.environ[P.RELEASE_ENV] = P.PREEXPOSURE_MAIN
        os.environ["I3_F1K_RESERVATION_RECEIPT"] = str(reservation_file)
        grid = P.release_grid()
        expected = [x["id"] for x in grid["origins"]]
    elif phase == "REHEARSAL_ONLY":
        receipt = None
        grid = P.rehearsal_grid()
        expected = [x["id"] for x in grid["origins"]]
    else:
        raise ValueError("unknown F1K release/rehearsal mode")
    writer=CaseWriter(base/"original_cases",expected)
    # This callback writes each receipt immediately after its real native
    # history exists. Even if later roots crash, earlier originals survive.
    first=P.produce(grid,phase,on_case=writer)
    # Save the first source BEFORE attempting the technical repetition.
    new_file(base/"F1K_FIRST_NATIVE.json.gz",
             deterministic_gzip(canonical(first)))
    second=P.produce(grid,phase)
    index=finalize(writer,first,second,base,receipt)
    print(json.dumps({
        "phase":phase,"roots":len(expected),
        "genuine_source_plus_arm_gzips":len(writer.entries),
        "technical_same_bytes":index["technical_byte_identical"],
        "original_sha256":index["native_original_sha256"],
        "scientific_verdict":None,
    },sort_keys=True))
    return index


def main():
    ap=argparse.ArgumentParser(description="F1K 16-root reserved-run custody")
    modes=ap.add_mutually_exclusive_group(required=True)
    modes.add_argument("--rehearsal",action="store_true")
    modes.add_argument("--release",action="store_true")
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--reservation",type=Path)
    args=ap.parse_args()
    if args.release and not args.reservation:
        ap.error("--release requires the pre-step remote reservation receipt")
    mode = "F1K_HELDOUT_RELEASE" if args.release else "REHEARSAL_ONLY"
    run(mode,args.output_dir,args.reservation)


if __name__=="__main__":
    main()
