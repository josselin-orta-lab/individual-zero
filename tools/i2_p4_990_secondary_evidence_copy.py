#!/usr/bin/env python3
"""Offline verified secondary copy of #990 research evidence, NEVER births I2.

A copy is NOT immutable independent M11 custody. An operator must select and
retain a genuinely separate storage destination; this tool has no network,
GitHub-tag, engine, or secret access.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile

MANIFEST = "SHA256SUMS.txt"
RECEIPT = "SECONDARY_COPY_RECEIPT.json"
PROTOCOL = "i2-p4-990-offline-secondary-copy-v1"
CONFIRM = "COPY-P4-990-TO-SECONDARY-STORAGE"


def _sha(path: Path) -> str:
    h = sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def _inventory(root: Path, *, copied=False) -> set[str]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("evidence root must be a real directory")
    files = set()
    for item in root.rglob("*"):
        if item.is_symlink():
            raise ValueError("symbolic link forbidden in research evidence")
        mode = item.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise ValueError("nonregular research evidence forbidden")
        rel = item.relative_to(root).as_posix()
        if rel == RECEIPT and not copied:
            raise ValueError("source must not have a secondary-copy receipt")
        files.add(rel)
    return files


def _read_manifest(root: Path, *, copied=False) -> dict:
    files = _inventory(root, copied=copied)
    if MANIFEST not in files:
        raise ValueError("missing SHA256SUMS.txt")
    raw = (root / MANIFEST).read_text(encoding="utf-8")
    records = {}
    for line in raw.splitlines():
        digest, separator, name = line.partition("  ")
        if (separator != "  " or len(digest) != 64 or
                any(ch not in "0123456789abcdef" for ch in digest)):
            raise ValueError("malformed research evidence manifest")
        if name.startswith("./"):
            name = name[2:]
        # Reject aliases, traversal and names that sha256sum would escape.
        if (not name or name.startswith("/") or "\\" in name or
                any(ord(ch) < 32 for ch in name) or
                PurePosixPath(name).as_posix() != name or
                ".." in PurePosixPath(name).parts or name in records or
                name in (MANIFEST, RECEIPT)):
            raise ValueError("unsafe or duplicate research manifest entry")
        records[name] = digest
    expected = files - {MANIFEST}
    if copied:
        expected.discard(RECEIPT)
    if not records or set(records) != expected:
        raise ValueError("unlisted, missing or invented evidence file")
    for rel, digest in records.items():
        if _sha(root / rel) != digest:
            raise ValueError("SHA256 mismatch in research evidence: " + rel)
    status_file = root / "study" / "status.json"
    status = None
    if status_file.is_file():
        status_obj = json.loads(status_file.read_text(encoding="utf-8"))
        status = status_obj.get("status")
        if status not in ("IN_PROGRESS", "ABORTED", "COMPLETED"):
            raise ValueError("unknown original study status")
    return {
        "manifest_sha256": sha256(raw.encode("utf-8")).hexdigest(),
        "file_count": len(records),
        "bytes": sum((root / rel).stat().st_size for rel in records),
        "study_status": status,
    }


def verify_copy(destination: Path) -> dict:
    destination = Path(destination)
    data = _read_manifest(destination, copied=True)
    receipt_path = destination / RECEIPT
    if not receipt_path.is_file() or receipt_path.is_symlink():
        raise ValueError("missing verified secondary-copy receipt")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    expected = {
        "protocol": PROTOCOL,
        "verdict": "LOCAL_READBACK_VERIFIED_ONLY",
        "independent_m11": False,
        **data,
    }
    if not isinstance(receipt, dict) or any(
            receipt.get(key) != value for key, value in expected.items()):
        raise ValueError("secondary-copy receipt does not match evidence")
    mode = receipt.get("storage_device_check")
    if mode not in ("DISTINCT_DEVICE_AT_COPY", "SYNTHETIC_SAME_DEVICE_ONLY"):
        raise ValueError("unrecognized secondary destination attestation")
    return {"verified": True, **data, "storage_device_check": mode,
            "independent_m11": False}


def copy_to_secondary(source: Path, destination: Path, *,
                      confirmation: str,
                      allow_same_device_for_synthetic_test=False) -> dict:
    """Never overwrite; stage, verify and read back an operator-selected copy.

    Device identity is a useful minimum operational check, not proof of a
    separate host, immutable custody, cloud availability or anti-rollback.
    """
    if confirmation != CONFIRM:
        raise ValueError("explicit secondary storage confirmation required")
    source, destination = Path(source), Path(destination)
    source_report = _read_manifest(source)
    if (destination.exists() or destination.is_symlink() or
            not destination.parent.is_dir() or destination.parent.is_symlink()):
        raise ValueError("destination must be a new path in a real directory")
    original = source.resolve()
    final = destination.resolve(strict=False)
    if final.is_relative_to(original) or original.is_relative_to(final):
        raise ValueError("source and secondary destination must be disjoint")
    same_device = source.stat().st_dev == destination.parent.stat().st_dev
    if same_device and allow_same_device_for_synthetic_test is not True:
        raise ValueError("secondary destination must use a different filesystem")
    device_check = ("SYNTHETIC_SAME_DEVICE_ONLY" if same_device else
                    "DISTINCT_DEVICE_AT_COPY")
    stage = Path(tempfile.mkdtemp(prefix=".p4-990-secondary-partial-",
                                  dir=destination.parent))
    # Retain partial staging evidence if export fails; never relabel it PASS.
    for rel in sorted(_inventory(source)):
        target = stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        with (source / rel).open("rb") as inp, target.open("xb") as out:
            shutil.copyfileobj(inp, out, length=1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
    if _read_manifest(stage) != source_report:
        raise ValueError("staged secondary copy differs from source")
    if _read_manifest(source) != source_report:
        raise ValueError("source mutated while copying evidence")
    receipt = {
        "protocol": PROTOCOL,
        "verdict": "LOCAL_READBACK_VERIFIED_ONLY",
        "independent_m11": False,
        "storage_device_check": device_check,
        **source_report,
    }
    with (stage / RECEIPT).open("x", encoding="utf-8") as out:
        json.dump(receipt, out, sort_keys=True, indent=2)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())
    verify_copy(stage)
    # Operational no-overwrite check. This is not an adversarially atomic
    # rename-against-competitors guarantee; a separate M11 witness is needed.
    if destination.exists() or destination.is_symlink():
        raise ValueError("secondary destination appeared during export")
    stage.rename(destination)
    return verify_copy(destination)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    exp = sub.add_parser("copy")
    exp.add_argument("source", type=Path)
    exp.add_argument("destination", type=Path)
    exp.add_argument("--confirm", required=True)
    exp.add_argument("--synthetic-allow-same-device", action="store_true")
    check = sub.add_parser("verify")
    check.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    if args.operation == "copy":
        report = copy_to_secondary(
            args.source, args.destination, confirmation=args.confirm,
            allow_same_device_for_synthetic_test=args.synthetic_allow_same_device)
    else:
        report = verify_copy(args.destination)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
