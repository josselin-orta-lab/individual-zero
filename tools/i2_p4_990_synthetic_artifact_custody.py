#!/usr/bin/env python3
"""Synthetic P4 #990 artifact custody rehearsal; never births an individual.

Fixture and verifier paths are explicit. This is NOT an independent M11
witness, a native SQLite archive audit, or an approved scientific execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

EXPECTED = ("completed", "aborted")
MANIFEST = "SHA256SUMS.txt"
PROTOCOL = "P4_990_SYNTHETIC_CUSTODY_REHEARSAL"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_root(root: Path) -> None:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("custody root must be a real directory")
    if any(item.is_symlink() for item in root.rglob("*")):
        raise ValueError("symlinks are forbidden in synthetic custody")


def make_fixture(root: Path) -> None:
    if root.exists() or root.is_symlink() or not root.parent.is_dir():
        raise ValueError("fixture directory must not already exist")
    root.mkdir(mode=0o700)
    try:
        for state in EXPECTED:
            folder = root / state
            folder.mkdir()
            with sqlite3.connect(folder / "original.sqlite") as conn:
                conn.execute("CREATE TABLE synthetic_events (tick INTEGER, marker TEXT)")
                conn.execute("INSERT INTO synthetic_events VALUES (?, ?)",
                             (1, "SYNTHETIC_NO_I2_BIRTH"))
                if state == "completed":
                    conn.execute("INSERT INTO synthetic_events VALUES (?, ?)",
                                 (2, "SYNTHETIC_COMPLETED"))
            (folder / "status.json").write_text(
                json.dumps({"protocol": PROTOCOL, "state": state.upper(),
                            "synthetic": True, "no_native_birth": True},
                           sort_keys=True) + "\n", encoding="utf-8")
        paths = sorted(
            p.relative_to(root).as_posix() for p in root.rglob("*")
            if p.is_file() and p.name != MANIFEST
        )
        (root / MANIFEST).write_text(
            "".join(f"{_digest(root / rel)}  {rel}\n" for rel in paths),
            encoding="utf-8")
        verify_fixture(root)
    except BaseException:
        # Never falsely label a partially produced rehearsal completed.
        raise


def verify_fixture(root: Path) -> dict:
    _check_root(root)
    manifest = root / MANIFEST
    if not manifest.is_file() or manifest.is_symlink():
        raise ValueError("missing safe custody manifest")
    listed = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise ValueError("malformed SHA-256 manifest entry")
        digest, relative = parts
        if any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("invalid digest")
        candidate = Path(relative)
        if (candidate.is_absolute() or ".." in candidate.parts or
                len(candidate.parts) != 2 or
                candidate.parts[0] not in EXPECTED or
                candidate.name not in ("status.json", "original.sqlite") or
                relative in listed):
            raise ValueError("invalid or duplicate manifest path")
        listed[relative] = digest
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and p.name != MANIFEST}
    if set(listed) != actual:
        raise ValueError("manifest missing or invents files")
    if set(listed) != {f"{state}/{name}" for state in EXPECTED
                      for name in ("status.json", "original.sqlite")}:
        raise ValueError("fixture incomplete")
    for relative, expected in listed.items():
        if _digest(root / relative) != expected:
            raise ValueError("SHA-256 mismatch: " + relative)
    for state in EXPECTED:
        folder = root / state
        status = json.loads((folder / "status.json").read_text(encoding="utf-8"))
        if status != {"protocol": PROTOCOL, "state": state.upper(),
                      "synthetic": True, "no_native_birth": True}:
            raise ValueError("invalid synthetic state marker")
        with sqlite3.connect(
                (folder / "original.sqlite").resolve().as_uri() + "?mode=ro",
                uri=True) as conn:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()
            events = conn.execute(
                "SELECT tick, marker FROM synthetic_events ORDER BY tick").fetchall()
        if integrity != ("ok",):
            raise ValueError("fixture SQLite integrity failure")
        expected_rows = [(1, "SYNTHETIC_NO_I2_BIRTH")]
        if state == "completed":
            expected_rows.append((2, "SYNTHETIC_COMPLETED"))
        if events != expected_rows:
            raise ValueError("invalid synthetic SQLite events")
    return {"protocol": PROTOCOL, "synthetic": True, "files_verified": len(listed),
            "states": list(EXPECTED), "real_native_births": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode in ("make", "verify"):
        command = sub.add_parser(mode)
        command.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    if args.mode == "make":
        make_fixture(args.directory)
    result = verify_fixture(args.directory)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
