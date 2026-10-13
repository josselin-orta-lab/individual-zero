"""Preregistered Stage12 M11 current-generation H120, development only.

Runs *real* WorldBody steps in a single SQLite-owned mortal life. No
Oracle/Bench; no extra Stage12 JSONL WAL. The exported canonical journal is
a read-only observation and is never a source for resuming the old life.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
# Direct script invocation otherwise sets sys.path[0] to scripts/, not root.
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger
from test_stage12_mortal_runtime import stage12_runtime

STEPS = 600
INDIVIDUAL = "m11:stage12:issue133-h600"


def fresh():
    return stage12_runtime(None, m11_sqlite_custody=True, paid_index=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    folder = args.output_dir
    folder.mkdir(parents=True, exist_ok=False)
    database = folder / "individual-current.sqlite"
    started = perf_counter()
    generations = []
    checkpoint_metrics = []
    life = fresh()
    config = life._stage10_config
    assert config.paid_pending_index and config.maximum_passes_per_sleep_step == 6
    assert config.selection_policy.maximum_episodes == 6
    assert config.sleep.consolidation_weight == 0
    assert config.sleep_work.step_slot_uc == 100
    assert config.sleep_work.period_capacity_uc == 600
    assert not life.journal.durable_wal_enabled
    with M11TransactionalMortal.birth(
        db_path=str(database), runtime=life, individual_id=INDIVIDUAL,
    ) as owner:
        for index in range(STEPS):
            receipt = owner.run_step()
            assert receipt.generation == index + 1
            assert receipt.world_step == index + 1
            assert receipt.journal_count > 0
            generations.append({"generation": receipt.generation,
                                "world_step": receipt.world_step,
                                "status": receipt.status,
                                "journal_head": receipt.journal_head})
            if receipt.world_step % 120 == 0:
                checkpoint_metrics.append({
                    "world_step": receipt.world_step,
                    "elapsed_seconds": perf_counter() - started,
                    "journal_count": receipt.journal_count,
                    "journal_head": receipt.journal_head,
                    "sqlite_file_bytes": database.stat().st_size,
                })
                print(json.dumps({"checkpoint": checkpoint_metrics[-1]}, sort_keys=True), flush=True)
            if receipt.status != "active":
                break
    before_recovery_seconds = perf_counter() - started
    audit = SQLiteLifeLedger.audit_read_only(
        path=str(database), expected_individual_id=INDIVIDUAL,
    )
    assert audit.pending_intent is False
    assert audit.generation == len(generations)
    assert audit.status in ("active", "dead")
    with SQLiteLifeLedger.open_existing(
        path=str(database), expected_individual_id=INDIVIDUAL,
    ) as store:
        journal = store.export_canonical_journal()
    (folder / "canonical-current-journal.jsonl").write_bytes(journal + b"\n")
    events = [json.loads(line)["causal_event"] for line in journal.splitlines()]
    kinds = [e["kind"] for e in events]
    H = "stage10_consolidation_version_activated"
    paid = "stage10_consolidation_index_maintenance_charged"
    retired = "stage10_consolidation_index_retired"
    activated = kinds.count(H)
    assert activated > 0, "no actual indexed h was published"
    assert kinds.count(paid) == activated == kinds.count(retired)
    committed = set()
    checkpoints = [e for e in events
                   if e["kind"] == "stage10_consolidation_pass_checkpointed"]
    # An active unpublished transaction may already have 1..5 durable
    # semantic checkpoints. Count only completed six-pass h publications.
    assert 6 * activated <= len(checkpoints) < 6 * (activated + 1)
    for i, e in enumerate(events):
        if e["kind"] != H:
            continue
        assert kinds[i - 1] == paid and kinds[i + 1] == retired
        refs = e["data"]["batch"]
        assert refs and not (set(refs) & committed)
        committed.update(refs)
        charge = events[i - 1]["data"]
        finish = events[i + 1]["data"]
        assert charge["episode_refs"] == refs == finish["episode_refs"]
        assert charge["requested_uc"] == len(refs)
        assert 0 <= charge["consumed_step_uc"] <= 100
        assert 0 <= charge["consumed_period_uc"] <= 600
    assert len(set(x["journal_head"] for x in generations)) == len(generations)
    assert not Path(str(database) + ".jsonl").exists()

    resumed_generation = None
    if audit.may_recover:
        with M11TransactionalMortal.cold_recover(
            db_path=str(database), individual_id=INDIVIDUAL,
            runtime_factory=fresh,
        ) as continuation:
            current = continuation.inspect()
            assert current["world_step"] == len(generations)
            receipt = continuation.run_step()
            resumed_generation = receipt.generation
            assert resumed_generation == len(generations) + 1
    result = {
        "schema": "m11-stage12-index-h600-v1",
        "preregistration": "docs/research/m11-stage12-issue133-opt1-h600-prereg-2026-10-13.fr.md",
        "source_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True,
            text=True, check=True).stdout.strip(),
        "python": sys.version.split()[0],
        "target_world_steps": STEPS,
        "checkpoint_metrics": checkpoint_metrics,
        "executed_world_steps": len(generations),
        "lifecycle_at_checkpoint": audit.status,
        "published_h": activated,
        "published_episode_refs": len(committed),
        "index_maintenance_charges": kinds.count(paid),
        "index_retirements": kinds.count(retired),
        "semantic_pass_checkpoints": len(checkpoints),
        "journal_count": audit.journal_count,
        "journal_head_sha256": audit.journal_head,
        "journal_export_sha256": sha256(journal).hexdigest(),
        "generation": audit.generation,
        "pending_intent": audit.pending_intent,
        "may_recover_current": audit.may_recover,
        "cold_resumed_next_generation": resumed_generation,
        "elapsed_seconds_to_checkpoint": before_recovery_seconds,
        "database_file_bytes": database.stat().st_size,
        "w_c": 0,
        "p42_step_slot_uc": 100,
        "p42_period_capacity_uc": 600,
        "oracle_used": False,
        "bench_used": False,
        "scientific_go": False,
        "operator_acceptance": None,
    }
    (folder / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
