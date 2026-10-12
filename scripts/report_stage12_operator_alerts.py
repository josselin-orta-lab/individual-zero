#!/usr/bin/env python3
"""Inspect persistent Stage12 operator alerts in a complete causal export.

Read-only: no cognition, WorldBody, Oracle or Bench is instantiated. The
default exit code is 0 for valid evidence, including a real detected alert;
use --exit-on-alert for external operator monitoring to distinguish warnings.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from lab.stage12_operator_alert_audit import audit_stage12_operator_alerts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical_export", type=Path)
    parser.add_argument("--expected-head", help="Trusted externally retained SHA-256")
    parser.add_argument("--expected-count", type=int, help="Trusted occurrence count")
    parser.add_argument("--exit-on-alert", action="store_true")
    args = parser.parse_args(argv)
    try:
        path = args.canonical_export
        if not path.is_file() or path.is_symlink():
            raise ValueError("canonical export must be a regular non-symlink file")
        result = audit_stage12_operator_alerts(
            path.read_bytes(), expected_head=args.expected_head,
            expected_count=args.expected_count,
        )
    except (OSError, ValueError, TypeError) as exc:
        print("Stage12 operator alert audit refused: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result.as_dict(), sort_keys=True, ensure_ascii=False))
    return 2 if args.exit_on_alert and result.emitted_alerts else 0


if __name__ == "__main__":
    raise SystemExit(main())
