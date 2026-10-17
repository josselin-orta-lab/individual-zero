"""Cross-source M-11 / Stage12 fail-closed boundary (TEST ONLY).

SQLite coordinates Stage10/11, not Stage12's separately fsynced WAL.
No Stage12 atomic recovery, human approval or scientific GO is claimed.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from test_stage12_mortal_runtime import stage12_runtime


class M11Stage12CombinedSourceTests(unittest.TestCase):
    def test_stage12_wal_cannot_be_misrepresented_as_sqlite_atomic_life(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            runtime = stage12_runtime(str(root / "stage12-life.wal"))
            db = root / "forbidden-stage12.sqlite"
            self.assertTrue(runtime.journal.durable_wal_enabled)
            with self.assertRaisesRegex(RecoveryBlocked, "unsupported runtime"):
                M11TransactionalMortal.birth(
                    db_path=str(db), runtime=runtime,
                    individual_id="m11:stage12:must-not-certify",
                )
            self.assertFalse(db.exists())
            result = runtime.run_step()
            self.assertEqual(result.execution_status, "applied")
            self.assertEqual(runtime.scheduler.t_monde, 1)
            self.assertTrue(runtime.journal.verify())

    def test_stage11_sqlite_and_stage12_wal_remain_distinct_lives(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            db = root / "stage11.sqlite"
            stage11 = build_stage11_reference_runtime(
                autonomous_mortal=True, enable_geography=True,
            )
            with M11TransactionalMortal.birth(
                db_path=str(db), runtime=stage11,
                individual_id="m11:standalone:stage11",
            ) as life:
                sqlite_step = life.run_step()
                self.assertEqual(sqlite_step.generation, 1)
                self.assertEqual(sqlite_step.world_step, 1)

            stage12 = stage12_runtime(str(root / "stage12-life.wal"))
            result = stage12.run_step()
            self.assertEqual(result.execution_status, "applied")
            self.assertEqual(stage12.scheduler.t_monde, 1)
            self.assertTrue(stage12.journal.verify())

            committed = SQLiteLifeLedger.audit_read_only(
                path=str(db),
                expected_individual_id="m11:standalone:stage11",
            )
            self.assertEqual(committed.generation, 1)
            self.assertTrue(committed.may_recover)


if __name__ == "__main__":
    unittest.main()
