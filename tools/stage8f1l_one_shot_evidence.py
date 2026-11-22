"""F1L original custody, independent byte verification and canonical readback.

No L-origin World.step on import. --release requires remotely verified one-shot
reservation before the producer can execute its first source tick. All 128
original parts, invalid sources and adverse outcomes are retained without rerun.
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

ARMS = ("full", "full_sham", "stale_owned_t1_means")
FILES = (
    "F1L_ORIGINAL_NATIVE.json.gz",
    "F1L_CANONICAL_READBACK.json.gz",
    "F1L_ORIGINALS_128_GZIP.tar.gz",
    "F1L_CUSTODY_MANIFEST.json",
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


def exact_128_entries(report):
    roots = report.get("rows")
    if not isinstance(roots, list):
        raise ValueError("missing F1L original case records")
    if report["origin_count"] != len(roots):
        raise ValueError("population was silently truncated")
    for row in roots:
        origin = row["origin"]
        ident = origin["id"]
        if not (ident.startswith("L") or ident.startswith("DEV")):
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
                "schema": "i3-stage8f1l-native-origin-part/v0",
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
            "schema": "i3-stage8f1l-incremental-custody/v0",
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


def finalize(writer, report, technical, base, reservation=None, *, reproduction_kind=None):
    base = Path(base)
    if len(writer.completed) != report["origin_count"]:
        raise ValueError("incomplete first scientific original")
    if len(writer.entries) != 4 * report["origin_count"]:
        raise ValueError("not all source+three arms archived")
    orig = canonical(report)
    reproduce = canonical(technical)
    # Reproduce the native experience twice ONLY on disjoint DEV_R seeds.
    # K01..K16 are born/executed exactly ONCE; their second byte container
    # is a cold canonical READBACK, absolutely NOT a new native World.step.
    kind = reproduction_kind or (
        "DEV_R_NATIVE_REPETITION" if report["phase"]!="F1L_HELDOUT_RELEASE"
        else "F1L_CANONICAL_READBACK_NO_SECOND_NATIVE")
    expected_kind=("F1L_CANONICAL_READBACK_NO_SECOND_NATIVE"
                   if report["phase"]=="F1L_HELDOUT_RELEASE"
                   else "DEV_R_NATIVE_REPETITION")
    if kind!=expected_kind:
        raise ValueError("reexecution of heldout native source is forbidden")
    byte_equal = orig == reproduce
    new_file(base / "F1L_ORIGINAL_NATIVE.json.gz", deterministic_gzip(orig))
    secondary = ("F1L_CANONICAL_READBACK.json.gz"
                 if report["phase"]=="F1L_HELDOUT_RELEASE"
                 else "F1L_TECHNICAL_REPRODUCTION.json.gz")
    new_file(base / secondary, deterministic_gzip(reproduce))
    members = [row["path"] for row in writer.entries]
    members += [f"_checkpoint_{i:02}.json" for i in
                range(1, report["origin_count"]+1)]
    archive = _tar_files(writer.path, members)
    new_file(base / "F1L_ORIGINALS_128_GZIP.tar.gz", archive)
    index = {
        "schema": "i3-stage8f1l-original-and-technical-custody/v0",
        "phase": report["phase"], "worlds": report["worlds"],
        "roots": writer.completed, "native_part_count": len(writer.entries),
        "entries": writer.entries,
        "native_original_sha256": digest(orig),
        "native_technical_sha256": digest(reproduce),
        "reproduction_kind": kind,
        "secondary_filename": secondary,
        "technical_byte_identical": (byte_equal and
                                     kind=="DEV_R_NATIVE_REPETITION"),
        "canonical_readback_byte_identical": (byte_equal and
            kind=="F1L_CANONICAL_READBACK_NO_SECOND_NATIVE"),
        "heldout_native_passes": 1 if kind==
            "F1L_CANONICAL_READBACK_NO_SECOND_NATIVE" else 0,
        "originals_tar_gzip_sha256": digest(archive),
        "reservation_sha256": (digest(canonical(reservation))
                               if reservation is not None else None),
        "native_scientific_verdict": None,
        "original_preserved_even_if_reproduction_fails": True,
    }
    new_file(base / "F1L_CUSTODY_MANIFEST.json", canonical(index) + b"\n")
    if not byte_equal:
        raise ValueError("technical replay/readback differs: original retained")
    return index


def verify_bundle(folder, report=None):
    folder = Path(folder)
    original_compressed = (folder/"F1L_ORIGINAL_NATIVE.json.gz").read_bytes()
    original = gzip.decompress(original_compressed)
    if report is None:
        report = json.loads(original)
    if canonical(report) != original:
        raise ValueError("F1L original bytes do not match parsed source")
    index = json.loads((folder/"F1L_CUSTODY_MANIFEST.json").read_bytes())
    expected_kind = ("F1L_CANONICAL_READBACK_NO_SECOND_NATIVE"
                     if report["phase"]=="F1L_HELDOUT_RELEASE"
                     else "DEV_R_NATIVE_REPETITION")
    expected_secondary = ("F1L_CANONICAL_READBACK.json.gz"
                          if report["phase"]=="F1L_HELDOUT_RELEASE"
                          else "F1L_TECHNICAL_REPRODUCTION.json.gz")
    if (index.get("reproduction_kind")!=expected_kind
            or index.get("secondary_filename")!=expected_secondary
            or index.get("heldout_native_passes")!=
               (1 if report["phase"]=="F1L_HELDOUT_RELEASE" else 0)):
        raise ValueError("F1L native second pass disguised as readback")
    technical = gzip.decompress((folder/expected_secondary).read_bytes())
    if (index["native_original_sha256"] != digest(original)
            or index["native_technical_sha256"] != digest(technical)
            or technical != original
            or index.get("technical_byte_identical") is not (
                report["phase"]!="F1L_HELDOUT_RELEASE")
            or index.get("canonical_readback_byte_identical") is not (
                report["phase"]=="F1L_HELDOUT_RELEASE")
            or index["native_part_count"] != 4 * report["origin_count"]
            or index["roots"] != report["origin_ids"]
            or len(index["entries"]) != 4 * report["origin_count"]
            or index["phase"] != report["phase"]):
        raise ValueError("F1L provenance, technical replay or 4-arm count changed")
    archive = (folder/"F1L_ORIGINALS_128_GZIP.tar.gz").read_bytes()
    if index["originals_tar_gzip_sha256"] != digest(archive):
        raise ValueError("F1L archived native originals were swapped")
    expected = {}
    for (ident, part, native), meta in zip(
            exact_128_entries(report), index["entries"]):
        relative = f"{ident}/{part}.json.gz"
        if (meta["path"] != relative or meta["id"] != ident
                or meta["part"] != part or relative in expected):
            raise ValueError("duplicate/filtered native gzip part")
        expected[relative] = (native, meta)
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(archive)), mode="r:") as tar:
        all_members=tar.getmembers()
        members = {m.name:m for m in all_members}
        checkpoint_names={
            f"_checkpoint_{i:02}.json" for i in
            range(1,report["origin_count"]+1)}
        if (len(all_members)!=len(members)
                or set(members)!=set(expected)|checkpoint_names
                or any(not m.isfile() for m in all_members)):
            raise ValueError("duplicate, unsafe or missing native gzip/checkpoint")
        for i in range(1,report["origin_count"]+1):
            relative=f"_checkpoint_{i:02}.json"
            checkpoint=json.loads(tar.extractfile(members[relative]).read())
            if (checkpoint.get("schema")!="i3-stage8f1l-incremental-custody/v0"
                    or checkpoint.get("completed_origins")!=index["roots"][:i]
                    or checkpoint.get("receipts")!=index["entries"][:4*i]):
                raise ValueError("incremental checkpoint or original SHA chain changed")
        case_sha={r["origin"]["id"]:r["case_sha256"] for r in report["rows"]}
        for relative,(native,meta) in expected.items():
            compressed = tar.extractfile(members[relative]).read()
            raw = gzip.decompress(compressed)
            item = json.loads(raw)
            if (item["id"] != meta["id"] or item["part"] != meta["part"]
                    or item.get("case_sha256")!=case_sha[item["id"]]
                    or item["native"] != native
                    or digest(compressed) != meta["gzip_sha256"]
                    or digest(raw) != meta["original_sha256"]
                    or len(raw) != meta["original_bytes"]
                    or len(compressed) != meta["gzip_bytes"]):
                raise ValueError("F1L original per-arm gzip source tampered")
    return {
        "status":"F1L_INDEPENDENT_BYTE_CUSTODY_PASS",
        "phase":index["phase"],
        "original_sha256":digest(original),
        "original_native_gzips":len(expected),
        "same_bytes_technical_reproduction":index["technical_byte_identical"],
        "same_bytes_canonical_readback":index["canonical_readback_byte_identical"],
        "heldout_native_passes":index["heldout_native_passes"],
        "roots":len(report["rows"]),
    }


def run(base, reservation_file):
    """First and only F1L scientific source/arm execution, never DEV."""
    from tools import stage8f1l_scientific_native as P
    from tools import stage8f1l_one_shot_reservation as R
    receipt = R.load_receipt(Path(reservation_file))
    R.verify_remote(receipt)
    base = Path(base)
    base.mkdir(parents=True, exist_ok=False)
    grid = P.release_grid()
    expected = [r["id"] for r in grid["origins"]]
    if expected != R.ROOT_IDS:
        raise PermissionError("F1L preregistered reserve not exact")
    writer = CaseWriter(base / "original_cases", expected)
    # P creates a native-start lock with O_EXCL before the FIRST heldout birth.
    first = P.produce_release(reservation_file, on_case=writer)
    new_file(base / "F1L_FIRST_NATIVE.json.gz",
             deterministic_gzip(canonical(first)))
    # This is a canonical byte readback. ZERO second World.step.
    second = json.loads(canonical(first))
    index = finalize(
        writer, first, second, base, receipt,
        reproduction_kind="F1L_CANONICAL_READBACK_NO_SECOND_NATIVE",
    )
    print(json.dumps({
        "status": "F1L_SCIENTIFIC_ORIGINAL_UNAUDITED",
        "roots": len(expected), "native_source_plus_arm_gzips": len(writer.entries),
        "readback_byte_equal": index["canonical_readback_byte_identical"],
        "heldout_native_passes": index["heldout_native_passes"],
        "original_sha256": index["native_original_sha256"],
        "scientific_verdict": None,
    }, sort_keys=True))
    return index


def main():
    p = argparse.ArgumentParser(description="F1L 32-root first-only native custody")
    p.add_argument("--release", action="store_true", required=True)
    p.add_argument("--reservation", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    run(a.output_dir, a.reservation)


if __name__ == "__main__":
    main()
