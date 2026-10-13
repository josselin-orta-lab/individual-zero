#!/usr/bin/env python3
"""Read-only Stage12 issue-110 source provenance report from a canonical export."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from lab.stage12_attribution_provenance_audit import audit_stage12_attribution_provenance


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical_export", type=Path)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-count", required=True, type=int)
    args = parser.parse_args(argv)
    try:
        if (not args.canonical_export.is_file()
                or args.canonical_export.is_symlink()):
            raise ValueError("canonical export must be a regular non-symlink file")
        result = audit_stage12_attribution_provenance(
            args.canonical_export.read_bytes(),
            expected_head=args.expected_head,
            expected_count=args.expected_count,
        )
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("Attribution provenance audit refused: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
