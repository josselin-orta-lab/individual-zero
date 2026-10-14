"""GA08 M11 exact-generation cold recovery and abrupt os._exit boundaries.

The Stage12 spatial protocol is birth-frozen. Test never imposes motor choices.
"""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger
from test_stage12_ga08_owner_runtime import spawn_real_spatial_runtime
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "scripts"))

IDENTITY = "m11:stage12:ga08:physical-cold"

_SCRIPT = r"""
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / "tests"))
from lab.m11_transactional_mortal import M11TransactionalMortal
from test_stage12_ga08_owner_runtime import spawn_real_spatial_runtime
db, point = sys.argv[1:]
rt = spawn_real_spatial_runtime(None, m11_sqlite_custody=True)
with M11TransactionalMortal.birth(
    db_path=db, runtime=rt, individual_id="m11:stage12:ga08:physical-cold",
) as life:
    def fault(at):
        if point == at:
            os._exit(77)
    life.run_step(test_fault=fault)
    raise AssertionError("fault should have interrupted exactly once")
"""


def factory():
    return spawn_real_spatial_runtime(None, m11_sqlite_custody=True)


class GA08M11AtomicRecoveryTests(unittest.TestCase):
    def test_atomic_current_generation_roundtrip_before_and_after_waking_steps(self):
        with TemporaryDirectory() as folder:
            db = str(Path(folder) / "spatial.db")
            with M11TransactionalMortal.birth(
                db_path=db, runtime=factory(), individual_id=IDENTITY,
            ) as live:
                for t in range(1, 4):
                    got = live.run_step()
                    self.assertEqual(got.generation, t)
                    self.assertEqual(got.status, "active")
                before = live.inspect()
            audit = SQLiteLifeLedger.audit_read_only(
                path=db, expected_individual_id=IDENTITY,
            )
            self.assertTrue(audit.may_recover)
            self.assertEqual(audit.generation, 3)
            with M11TransactionalMortal.cold_recover(
                db_path=db, individual_id=IDENTITY, runtime_factory=factory,
            ) as resumed:
                self.assertEqual(resumed.inspect(), before)
                fourth = resumed.run_step()
                self.assertEqual(fourth.generation, 4)
                self.assertEqual(fourth.status, "active")
                self.assertEqual(fourth.world_step, 4)

    def test_cold_recovery_with_actual_pending_spatial_intention(self):
        """A true I0 goal commitment survives atomic recovery, exactly once."""
        from run_stage12_issue110_ga08_return_goal_science import (
            build_autonomous_life,
        )
        from lab.stage12_spatial_provenance_audit import (
            audit_stage12_spatial_provenance,
        )
        from lab.stage12_attribution_pair_audit import (
            audit_stage12_attribution_pairs,
        )
        identity = "m11:stage12:ga08:pending-spatial"
        def born():
            return build_autonomous_life(
                label="water_spatial", wal_path=None, m11_sqlite_custody=True,
            )[0]
        with TemporaryDirectory() as folder:
            path = str(Path(folder) / "pending.db")
            with M11TransactionalMortal.birth(
                db_path=path, runtime=born(), individual_id=identity,
            ) as owner:
                self.assertEqual(owner.run_step().world_step, 1)
                self.assertEqual(owner.run_step().world_step, 2)
                spatial_pending = owner._runtime._meta_custody.goal_progress.pending
                # Owner-internal read is for software testing only.
                self.assertIsNotNone(spatial_pending)
                self.assertEqual(spatial_pending.policy_version,
                                 "stage12-spatial-subcriterion-ga08-v1")
                before = owner.inspect()
            with M11TransactionalMortal.cold_recover(
                db_path=path, individual_id=identity, runtime_factory=born,
            ) as resumed:
                self.assertEqual(resumed.inspect(), before)
                self.assertIsNotNone(
                    resumed._runtime._meta_custody.goal_progress.pending,
                )
                actual = resumed.run_step()
                self.assertEqual(actual.world_step, 3)
                self.assertEqual(actual.generation, 3)
                self.assertEqual(actual.status, "active")
                # The recovered spatial intention closed exactly once.
                # At step 3, autonomous I0 may legitimately preregister
                # a distinct bodily water criterion for its next command.
                following = resumed._runtime._meta_custody.goal_progress.pending
                if following is not None:
                    self.assertNotEqual(
                        following.intent_ref, spatial_pending.intent_ref,
                    )
                    self.assertNotEqual(
                        getattr(following, "policy_version", None),
                        "stage12-spatial-subcriterion-ga08-v1",
                    )
                    self.assertEqual(following.sent_world_step, 3)
            with SQLiteLifeLedger.open_existing(
                path=path, expected_individual_id=identity,
            ) as ledger:
                journal = ledger.export_canonical_journal()
            spatial = audit_stage12_spatial_provenance(journal)
            pairs = audit_stage12_attribution_pairs(journal)
            self.assertEqual(spatial.preregistered, 1)
            self.assertEqual(spatial.verified_successes, 1)
            self.assertEqual(spatial.judgements_self, 1)
            self.assertEqual(pairs.admitted_pairs, 1)

    def test_real_os_exit_pre_and_post_sqlite_commit(self):
        for point in ("before_sql_commit", "after_sql_commit"):
            with self.subTest(point=point), TemporaryDirectory() as folder:
                db = str(Path(folder) / "crashed.db")
                child = subprocess.run(
                    [sys.executable, "-c", _SCRIPT, db, point],
                    capture_output=True, text=True, timeout=65,
                )
                self.assertEqual(child.returncode, 77, child.stderr)
                audit = SQLiteLifeLedger.audit_read_only(
                    path=db, expected_individual_id=IDENTITY,
                )
                if point == "before_sql_commit":
                    self.assertTrue(audit.pending_intent)
                    self.assertFalse(audit.may_recover)
                    with self.assertRaises(RecoveryBlocked):
                        M11TransactionalMortal.cold_recover(
                            db_path=db, individual_id=IDENTITY,
                            runtime_factory=factory,
                        )
                else:
                    self.assertFalse(audit.pending_intent)
                    self.assertTrue(audit.may_recover)
                    self.assertEqual(audit.generation, 1)
                    with M11TransactionalMortal.cold_recover(
                        db_path=db, individual_id=IDENTITY,
                        runtime_factory=factory,
                    ) as resumed:
                        next_step = resumed.run_step()
                        self.assertEqual(next_step.generation, 2)


if __name__ == "__main__":
    unittest.main()
