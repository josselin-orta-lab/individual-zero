"""Operator-only M-11 SQLite trial for current-generation mortal lives.

This is an opt-in development runner. It never boots Oracle or Bench and
never guesses the identity or a recoverable state from an older journal.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import uuid

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage10_reference_fixture import build_stage10_reference_runtime


def stage11():
    return build_stage11_reference_runtime(
        autonomous_mortal=True, enable_geography=True)


def stage10():
    return build_stage10_reference_runtime(
        autonomous_mortal=True, start_fatigued=True)


BUILDERS = {"stage11": stage11, "stage10": stage10}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="One SQLite-owned I0 development life; no historical rollback")
    parser.add_argument("--db", required=True, type=Path,
                        help="absolute exclusive birth DB or existing DB for --resume")
    parser.add_argument("--runtime", choices=sorted(BUILDERS), default="stage11")
    parser.add_argument("--steps", type=int, default=1,
                        help="actual requested world steps, positive, at most 600")
    parser.add_argument("--identity", type=str,
                        help="required for --resume; auto-generated once at birth")
    parser.add_argument("--resume", action="store_true",
                        help="open only the unique currently committed active generation")
    args = parser.parse_args(argv)
    if not args.db.is_absolute() or args.db.is_symlink() or not 1 <= args.steps <= 600:
        parser.error("absolute non-symlink DB path and 1..600 real steps required")
    if args.resume and not args.identity:
        parser.error("--resume requires the precise persistent --identity")
    if not args.resume and args.identity:
        parser.error("birth identity is generated exclusively; omit --identity")
    individual_id = args.identity if args.resume else "m11:individual:" + str(uuid.uuid4())
    factory = BUILDERS[args.runtime]
    life = None
    try:
        if args.resume:
            life = M11TransactionalMortal.cold_recover(
                db_path=str(args.db), individual_id=individual_id,
                runtime_factory=factory)
        else:
            if args.db.exists():
                raise RecoveryBlocked("birth path already exists, never overwrite a life")
            life = M11TransactionalMortal.birth(
                db_path=str(args.db), runtime=factory(),
                individual_id=individual_id)
        with life:
            result = []
            for _ in range(args.steps):
                receipt = life.run_step()
                result.append({"generation": receipt.generation,
                               "world_step": receipt.world_step,
                               "status": receipt.status,
                               "journal_count": receipt.journal_count,
                               "journal_head": receipt.journal_head})
                if receipt.status != "active":
                    break
            audit = SQLiteLifeLedger.audit_read_only(
                path=str(args.db), expected_individual_id=individual_id)
            output = {
                "schema": "m11-operator-sqlite-trial-v1",
                "individual_id": individual_id,
                "db_path": str(args.db),
                "runtime": args.runtime,
                "generation": audit.generation,
                "status": audit.status,
                "journal_count": audit.journal_count,
                "journal_head": audit.journal_head,
                "pending_intent": audit.pending_intent,
                "executed_steps": len(result),
                "last_world_step": result[-1]["world_step"] if result else None,
                "technical_validation": True,
                "operator_acceptance": None,
                "scientific_validation": None,
            }
            print(json.dumps(output, ensure_ascii=False, sort_keys=True))
            return 0
    except (RecoveryBlocked, OSError, ValueError, RuntimeError) as exc:
        # Fail closed. Explicit operator investigation of current SQLite DB;
        # never select an older generation or replay an already issued command.
        print(f"M11_SQLITE_STOP: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
