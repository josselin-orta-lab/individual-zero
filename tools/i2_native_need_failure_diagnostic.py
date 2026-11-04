#!/usr/bin/env python3
"""#986: read-only audit and classification of ONE existing completed native I2 life.

Never births, steps, resumes, modifies, or anticipates a native individual.
A full native cold audit MUST succeed before journal interpretation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from i2.modules.native_need_failure_opportunity_audit import (
    report_need_failure_opportunities,
)
from i2.modules.native_owner_support import saved_traits
from i2.runtime.native_paid_cycle import NativePaidI2


def diagnose_existing_life(path):
    path = Path(path)
    # This is the single native owner's complete independent physical and
    # cognitive cold replay, not a trusted verdict from the observer itself.
    verified = NativePaidI2.inspect(path).audit()
    revision = verified["revision"]
    if (type(revision) is not int or
            type(verified["max_steps"]) is not int or
            not (verified["terminal"] or revision == verified["max_steps"])):
        raise ValueError("only physically terminal or fully right-censored lives")
    # SQLite URI is encoded, read-only. A read transaction holds ONE snapshot
    # of both event tables and immutable genesis, without writing or birth.
    uri = "file:" + quote(str(path.resolve()), safe="/") + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.execute("BEGIN")
        birth = db.execute(
            "SELECT traits_json,need_failure_exploration,spatial_world "
            "FROM native_genesis WHERE id=1").fetchone()
        events = db.execute(
            "SELECT event_json FROM events ORDER BY seq").fetchall()
        physical = db.execute(
            "SELECT admitted_action,before_json,after_json "
            "FROM native_physical_events ORDER BY seq").fetchall()
    if (birth is None or birth[1] not in (0, 1) or birth[2] != 1 or
            len(events) != revision or len(physical) != revision):
        raise ValueError("cold-audited spatial genesis/journal mismatch")
    result = report_need_failure_opportunities(
        events=tuple(json.loads(x[0]) for x in events),
        physical=tuple(physical),
        traits=saved_traits(birth[0]),
        factor_enabled=bool(birth[1]),
    )
    return {
        "protocol": "i2-v23-need-failure-observation-986",
        "native_cold_audit": "PASS",
        "revision": revision,
        "biological_terminal": bool(verified["terminal"]),
        "right_censored": not verified["terminal"],
        "factor_enabled": bool(birth[1]),
        **result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sqlite", type=Path,
                        help="Existing, completed native I2 SQLite research life")
    parser.add_argument("--ticks", action="store_true",
                        help="Include all per-tick diagnostic reasons")
    args = parser.parse_args()
    result = diagnose_existing_life(args.sqlite)
    if not args.ticks:
        result.pop("ticks")
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
