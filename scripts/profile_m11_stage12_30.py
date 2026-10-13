"""Preregistered read-only instrumentation of 30 true M11/Stage12 steps.

Profile is external to cognition, uses no alternate state path and does not
relax M11 SQLite durability, consistency, or journal verification.
"""
from __future__ import annotations

import argparse
import cProfile
from hashlib import sha256
import json
from pathlib import Path
import pstats
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger
from test_stage12_mortal_runtime import stage12_runtime


def fresh():
    return stage12_runtime(None, m11_sqlite_custody=True, paid_index=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    folder = args.output_dir
    folder.mkdir(parents=True, exist_ok=False)
    dbpath = folder / "individual.sqlite"
    profile = cProfile.Profile()
    step_times = []
    results = []
    start = perf_counter()
    genesis = fresh()
    assert genesis._stage10_config.sleep.consolidation_weight == 0.0
    assert genesis._stage10_config.sleep_work.step_slot_uc == 100
    assert genesis._stage10_config.sleep_work.period_capacity_uc == 600
    assert genesis._stage10_config.paid_pending_index is True
    assert not genesis.journal.durable_wal_enabled
    with M11TransactionalMortal.birth(
        db_path=str(dbpath), runtime=genesis,
        individual_id="m11:stage12:profile30",
    ) as life:
        for i in range(30):
            stamp = perf_counter()
            profile.enable()
            try:
                receipt = life.run_step()
            finally:
                profile.disable()
            duration = perf_counter() - stamp
            step_times.append(duration)
            results.append({
                "generation": receipt.generation,
                "world_step": receipt.world_step,
                "status": receipt.status,
                "journal_count": receipt.journal_count,
                "journal_head": receipt.journal_head,
                "seconds": duration,
            })
            assert receipt.generation == i + 1 and receipt.world_step == i + 1
            if receipt.status != "active":
                break
    elapsed = perf_counter() - start
    profile.dump_stats(str(folder / "runtime-profile.prof"))
    stats = pstats.Stats(profile)
    important = {
        "SQLiteLifeLedger.audit": ("sqlite_life_store.py", "audit"),
        "SQLiteLifeLedger.commit_generation": ("sqlite_life_store.py", "commit_generation"),
        "SQLiteLifeLedger.begin_intent": ("sqlite_life_store.py", "begin_intent"),
        "M11TransactionalMortal.run_step": ("m11_transactional_mortal.py", "run_step"),
        "_copy_private_runtime": ("m11_transactional_mortal.py", "_copy_private_runtime"),
        "_runtime_image": ("m11_transactional_mortal.py", "_runtime_image"),
        "capture_registered_current_state": ("sqlite_runtime_custody.py", "capture_registered_current_state"),
        "canonical_causal_bytes": ("determinism.py", "canonical_causal_bytes"),
        "deepcopy": ("copy.py", "deepcopy"),
    }
    rows = {}
    for label, (filename, funcname) in important.items():
        entries = [(k, v) for k, v in stats.stats.items()
                   if k[0].endswith(filename) and k[2] == funcname]
        rows[label] = {
            "calls": sum(v[1] for _, v in entries),
            "self_seconds": sum(v[2] for _, v in entries),
            "cumulative_seconds": sum(v[3] for _, v in entries),
        }
    ranking = sorted(
        ((key, values) for key, values in stats.stats.items()),
        key=lambda item: item[1][3], reverse=True,
    )[:40]
    hot = [{
        "file": key[0].replace(str(ROOT) + "/", ""),
        "line": key[1], "function": key[2],
        "calls": value[1], "self_seconds": value[2],
        "cumulative_seconds": value[3],
    } for key, value in ranking]
    audit = SQLiteLifeLedger.audit_read_only(
        path=str(dbpath), expected_individual_id="m11:stage12:profile30",
    )
    assert audit.generation == len(results) and not audit.pending_intent
    assert audit.journal_head == results[-1]["journal_head"]
    out = {
        "schema": "m11-stage12-issue133-profile30-v1",
        "source_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True,
            text=True, check=True).stdout.strip(),
        "preregistration": "docs/research/m11-stage12-issue133-profile30-prereg-2026-10-13.fr.md",
        "python": sys.version.split()[0],
        "steps": len(results),
        "journal_count": audit.journal_count,
        "journal_head_sha256": audit.journal_head,
        "last_generation": audit.generation,
        "status": audit.status,
        "sqlite_bytes": dbpath.stat().st_size,
        "elapsed_seconds": elapsed,
        "step_seconds": step_times,
        "function_costs": rows,
        "top_40_cumulative": hot,
        "sqlite_current_verified": True,
        "w_c": 0,
        "no_runtime_change": True,
        "scientific_go": False,
    }
    (folder / "profile-summary.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "sha": out["source_sha"], "steps": out["steps"],
        "elapsed_seconds": elapsed, "profiled_functions": rows,
        "journal_head_sha256": audit.journal_head,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
