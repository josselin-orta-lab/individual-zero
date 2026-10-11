#!/usr/bin/env python3
"""Check a FULL I0 journal export without loading I0, Oracle or Bench.

Example:
  python3 scripts/verify_i0_journal.py /path/to/journal.jsonl \
    --expected-head <64-hex> --expected-count 3000

The trusted head/count are essential to detect a truncated but valid prefix.
Exit codes: 0 verified; 1 invalid; 2 malformed invocation or missing file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lab.independent_journal_audit import audit_export_bytes, audit_export_file


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("journal", type=Path)
    parser.add_argument("--durable-wal", action="store_true", help="Verify the fsynced per-entry WAL (final LF required) instead of a canonical export")
    parser.add_argument("--expected-head", help="Trusted full-export SHA-256 chain head")
    parser.add_argument("--expected-count", type=int, help="Trusted occurrence count")
    args = parser.parse_args(argv)
    try:
        if args.durable_wal:
            # WAL's per-record final LF is a deliberate durability envelope,
            # not part of canonical immutable-export bytes. Validate the
            # envelope strictly, then reuse the same independent provenance
            # auditor used for operator exports (no I0, Oracle or Bench).
            if args.journal.is_symlink() or not args.journal.is_file():
                raise ValueError("WAL must be a regular non-symlink file")
            wal = args.journal.read_bytes()
            if not wal or not wal.endswith(b"\n") or wal.endswith(b"\n\n"):
                raise ValueError("WAL has a missing or invalid record terminator")
            outcome = audit_export_bytes(
                wal[:-1], expected_head=args.expected_head,
                expected_count=args.expected_count,
            )
        else:
            outcome = audit_export_file(
                args.journal, expected_head=args.expected_head,
                expected_count=args.expected_count,
            )
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({
            "schema": "individual-zero-independent-audit-v1",
            "valid": False, "reason": str(exc),
            "physical_truth_verified": False,
        }, sort_keys=True))
        return 1
    print(json.dumps(outcome.as_dict(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
