#!/usr/bin/env python3
"""#988: seal an existing completed native I2 SQLite life, without a new birth.

This is a research-custody COPY, not authenticated M11 or a new state owner.
Never use the archived file for motor authority, stepping or resuming.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from i2.runtime.native_paid_cycle import NativePaidI2


def _completed(path):
    inspected = NativePaidI2.inspect(path)
    report = inspected.audit()
    if (type(report.get("revision")) is not int or
            type(report.get("max_steps")) is not int or
            type(report.get("terminal")) is not bool or
            not (report["terminal"] or
                 report["revision"] == report["max_steps"])):
        raise ValueError("only completed terminal or horizon-censored lives")
    return inspected, report


def archive_completed_life(source, destination):
    """Audit source, snapshot with SQLite backup, audit snapshot, publish once.

    This protects against accidental destructive custody mistakes, not
    concurrent malicious replacement, external rollback or forgery.
    """
    source, destination = Path(source), Path(destination)
    if (source.is_symlink() or not source.is_file() or
            destination.is_symlink() or os.path.lexists(destination) or
            not destination.parent.is_dir()):
        raise ValueError("existing regular source and new archive path required")
    if source.resolve() == destination.resolve():
        raise ValueError("source cannot be archive destination")
    initial, before = _completed(source)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                prefix=".i2-custody-", suffix=".sqlite",
                dir=destination.parent, delete=False) as out:
            temporary = Path(out.name)
        os.chmod(temporary, 0o600)
        with sqlite3.connect(source.resolve().as_uri() + "?mode=ro",
                             uri=True) as src_db:
            with sqlite3.connect(temporary) as archive_db:
                src_db.backup(archive_db)
        copied, after = _completed(temporary)
        # Confirm the observed whole audited endpoint and born identity.
        if (initial.life_ref != copied.life_ref or
                initial.genesis_ref != copied.genesis_ref or before != after):
            raise ValueError("archived identity or replay differs from original")
        # A second source check detects ordinary concurrent source changes.
        current, now = _completed(source)
        if (current.life_ref != initial.life_ref or
                current.genesis_ref != initial.genesis_ref or now != before):
            raise ValueError("source changed during archive extraction")
        digest = sha256(temporary.read_bytes()).hexdigest()
        # Atomic no-overwrite publication even under a competing writer.
        os.link(temporary, destination)
        return {
            "protocol": "i2-native-completed-life-custody-988",
            "source": str(source),
            "archive": str(destination),
            "archive_sha256": digest,
            "revision": after["revision"],
            "max_steps": after["max_steps"],
            "biological_terminal": after["terminal"],
            "right_censored": not after["terminal"],
            "remaining_uc": after["remaining_uc"],
            "site": after["site"],
            "body": after["body"],
            "cold_audit": "PASS",
            "original_unchanged": "AUDIT_ENDPOINT_MATCH",
            "m11_authenticated": False,
            "diagnostic_only": True,
        }
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Existing completed native I2 SQLite journal")
    parser.add_argument("archive", type=Path, help="New nonexisting archival SQLite path")
    args = parser.parse_args()
    print(json.dumps(archive_completed_life(args.source, args.archive),
                     sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
