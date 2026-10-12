#!/usr/bin/env python3
"""Verify the full causal export and report Stage12 module occupancy receipts.

Operator-only, read-only. No I0 instance, Oracle or Bench is imported.
A trusted head and occurrence count should come from independent custody.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from lab.stage12_occupancy_audit import audit_stage12_occupancy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical_export", type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument("--expected-count", type=int)
    arguments = parser.parse_args(argv)
    try:
        path = arguments.canonical_export
        if not path.is_file() or path.is_symlink():
            raise ValueError("export must be a regular non-symlink file")
        result = audit_stage12_occupancy(
            path.read_bytes(), expected_head=arguments.expected_head,
            expected_count=arguments.expected_count,
        )
    except (OSError, ValueError, TypeError) as exc:
        print(f"Stage12 occupancy audit refused: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result.as_dict(), sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
