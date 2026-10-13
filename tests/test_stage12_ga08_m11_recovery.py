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
