"""Read-only independent consistency attestation for an I0 SQLite life file.

This does NOT reconstruct the cognitive runtime, query Oracle/Bench, attest
physical truth or certify M-11 end-to-end recovery.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from lab.sqlite_life_store import SQLiteLifeLedger


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--identity", required=True)
    parser.add_argument("--expect-generation", type=int)
    parser.add_argument("--expect-head")
    args = parser.parse_args()
    try:
        receipt = SQLiteLifeLedger.audit_read_only(
            path=str(args.db), expected_individual_id=args.identity,
        )
        if args.expect_generation is not None and receipt.generation != args.expect_generation:
            raise ValueError("current generation differs from trusted operator anchor")
        if args.expect_head is not None and receipt.journal_head != args.expect_head:
            raise ValueError("current journal head differs from trusted operator anchor")
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(status=2, message=f"SQLite life audit rejected: {exc}\n")
    print(json.dumps({
        "schema": "i0-sqlite-custody-audit-v1",
        "individual_id": receipt.individual_id,
        "generation": receipt.generation,
        "status": receipt.status,
        "journal_count": receipt.journal_count,
        "journal_head": receipt.journal_head,
        "state_hash": receipt.state_hash,
        "pending_intent": receipt.pending_intent,
        "may_recover": receipt.may_recover,
        "claim": "internal_consistency_only_not_independent_physical_truth",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
