"""Issue #110 Option A: distinct births and atomic M11 spatial state recovery.

Full WorldBody transitions and separately constructed training equipment.
Subprocess os._exit kills the process; the only recovery is the current
SQLite generation. No old-state replay, no secondary WAL, no Oracle/Bench.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_first_planning_state import build_life

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs

WORLD = "near_food_free"
WATER = 70.0
SLEEP = "horizon_three"


def factory(identity: str):
    return build_life(
        WORLD, WATER, SLEEP, wal_path=None,
        m11_sqlite_custody=True, birth_life_id=identity,
    )[0]


def rows(source: bytes) -> list[dict]:
    return [json.loads(line) for line in source.splitlines()]


_CRASH_CHILD = r"""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "scripts"))
from run_stage12_issue110_first_planning_state import build_life
from lab.m11_transactional_mortal import M11TransactionalMortal
db, identity, position = sys.argv[1:]
runtime = build_life("near_food_free", 70.0, "horizon_three",
                     wal_path=None, m11_sqlite_custody=True,
                     birth_life_id=identity)[0]
with M11TransactionalMortal.birth(
    db_path=db, runtime=runtime, individual_id=identity,
) as owner:
    assert owner.run_step().world_step == 1
    def crash(point):
        if point == position:
            os._exit(73)
    owner.run_step(test_fault=crash)
    raise AssertionError("actual os._exit expected")
"""


class Stage12SpatialM11Tests(unittest.TestCase):
    def test_distinct_births_produce_distinct_cognitive_pair_references(self):
        with TemporaryDirectory() as folder:
            refsets = []
            for name in ("birth-a", "birth-b"):
                birth = "i0:issue110:spatial:" + name
                life = build_life(
                    WORLD, WATER, SLEEP,
                    wal_path=str(Path(folder) / (name + ".wal")),
                    birth_life_id=birth,
                )[0]
                self.assertEqual(life.individual_id, birth)
                # Step 6 is an actual sleeping step; only the waking
                # diagnostic in step 7 can emit the pair expiry receipt.
                for _ in range(8):
                    self.assertEqual(life.run_step().execution_status, "applied")
                raw = life.journal.canonical_bytes()
                audit_stage12_goal_progress(raw)
                audit_stage12_first_person_agency(raw)
                audit_stage12_attribution_pairs(raw)
                all_refs = {
                    row["event_id"] for row in rows(raw)
                    if row["causal_event"]["kind"] in (
                        "stage12_goal_progress_preregistered",
                        "stage12_goal_agency_judgement",
                        "stage12_attribution_pair_admitted",
                    )
                }
                self.assertTrue(all_refs)
                refs = {
                    row["event_id"] for row in rows(raw)
                    if row["causal_event"]["kind"] ==
                       "stage12_attribution_pair_admitted"
                }
                self.assertTrue(refs)
                refsets.append((all_refs, refs))
            self.assertTrue(refsets[0][0].isdisjoint(refsets[1][0]))
            self.assertTrue(refsets[0][1].isdisjoint(refsets[1][1]))

    def test_m11_cold_reconstructs_current_spatial_owners_without_replaying(self):
        identity = "i0:issue110:spatial:m11-current"
        with TemporaryDirectory() as folder:
            path = str(Path(folder) / "life.sqlite")
            with M11TransactionalMortal.birth(
                db_path=path, runtime=factory(identity),
                individual_id=identity,
            ) as owner:
                self.assertEqual(owner.run_step().generation, 1)
                self.assertEqual(owner.run_step().generation, 2)
                committed = owner.inspect()
                self.assertEqual(committed["world_step"], 2)
                pending = owner._runtime._meta_custody.goal_progress.pending
                self.assertIsNotNone(pending)
                self.assertEqual(pending.measure, "spatial_distance")
                self.assertIsNotNone(owner._runtime.stage3.control.goal_agency.pending)
            with self.assertRaises(RecoveryBlocked):
                M11TransactionalMortal.cold_recover(
                    db_path=path, individual_id=identity,
                    runtime_factory=lambda: factory(
                        "i0:issue110:spatial:wrong-birth"),
                )
            with M11TransactionalMortal.cold_recover(
                db_path=path, individual_id=identity,
                runtime_factory=lambda: factory(identity),
            ) as restored:
                self.assertEqual(restored.inspect(), committed)
                self.assertEqual(
                    restored._runtime._meta_custody.goal_progress.pending.measure,
                    "spatial_distance",
                )
                self.assertEqual(restored._runtime.individual_id, identity)
                third = restored.run_step()
                self.assertEqual(third.generation, 3)
                self.assertEqual(third.world_step, 3)
            with SQLiteLifeLedger.open_existing(
                path=path, expected_individual_id=identity,
            ) as ledger:
                latest = ledger.audit()
                self.assertEqual(latest.generation, 3)
                raw = ledger.export_canonical_journal()
            goal = audit_stage12_goal_progress(raw)
            agency = audit_stage12_first_person_agency(raw)
            self.assertEqual(goal.spatial_verified_progress, 1)
            self.assertGreaterEqual(agency.judgements_self, 1)

    def test_hard_crash_matrix_never_restores_uncommitted_spatial_step(self):
        identity = "i0:issue110:spatial:m11-hard-exit"
        for point, generation, recoverable in (
            ("after_private_execution", 1, False),
            ("after_sql_commit", 2, True),
        ):
            with self.subTest(point=point), TemporaryDirectory() as folder:
                db = str(Path(folder) / "crash.sqlite")
                child = subprocess.run(
                    [sys.executable, "-c", _CRASH_CHILD, db, identity, point],
                    capture_output=True, text=True, timeout=120,
                )
                self.assertEqual(child.returncode, 73, child.stderr)
                state = SQLiteLifeLedger.audit_read_only(
                    path=db, expected_individual_id=identity,
                )
                self.assertEqual(state.generation, generation)
                self.assertEqual(state.may_recover, recoverable)
                if recoverable:
                    with M11TransactionalMortal.cold_recover(
                        db_path=db, individual_id=identity,
                        runtime_factory=lambda: factory(identity),
                    ) as restored:
                        self.assertEqual(restored.inspect()["world_step"], 2)
                        self.assertEqual(
                            restored._runtime._meta_custody.goal_progress.pending.measure,
                            "spatial_distance",
                        )
                        self.assertEqual(restored.run_step().generation, 3)
                else:
                    with self.assertRaises(RecoveryBlocked):
                        M11TransactionalMortal.cold_recover(
                            db_path=db, individual_id=identity,
                            runtime_factory=lambda: factory(identity),
                        )


if __name__ == "__main__":
    unittest.main()
