#!/usr/bin/env python3
"""Read-only Stage12 goal/action alignment report from a canonical I0 export.

This script is for operators only and never changes an I0 life. The three
categories describe recorded justifications, NOT true internal intention.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from lab.stage12_alignment import evaluate_goal_action_alignment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical_export", type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument("--expected-count", type=int)
    options = parser.parse_args(argv)
    try:
        path = options.canonical_export
        if not path.is_file() or path.is_symlink():
            raise ValueError("export must be a regular, nonsymlink file")
        raw = path.read_bytes()
        report = evaluate_goal_action_alignment(
            raw, expected_head=options.expected_head,
            expected_count=options.expected_count,
        )
    except (ValueError, OSError, TypeError) as exc:
        print(f"stage12 alignment refused: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report.as_dict(), sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
