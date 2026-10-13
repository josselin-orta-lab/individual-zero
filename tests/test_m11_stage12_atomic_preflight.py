"""M11/Stage12 preregistered exclusive SQLite ownership smoke and cold roundtrip."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from test_stage12_mortal_runtime import stage12_runtime


def fresh():
    return stage12_runtime(None, m11_sqlite_custody=True)


class M11Stage12AtomicPreflightTests(unittest.TestCase):
    def test_legacy_wal_and_sqlite_authorities_cannot_be_combined(self):
        with TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "no secondary WAL"):
                stage12_runtime(str(Path(folder) / "double.wal"),
                                m11_sqlite_custody=True)
            classic = stage12_runtime(str(Path(folder) / "classic.wal"))
            with self.assertRaisesRegex(RecoveryBlocked, "unsupported runtime"):
                M11TransactionalMortal.birth(
                    db_path=str(Path(folder) / "rejected.sqlite"),
                    runtime=classic, individual_id="m11:stage12:uncoordinated",
                )
            self.assertTrue(classic.journal.durable_wal_enabled)

    def test_exclusive_private_step_and_exact_first_current_generation(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            original = fresh()
            with self.assertRaisesRegex(RuntimeError, "not directly dispatchable"):
                original.run_step()
            self.assertFalse(original.journal.durable_wal_enabled)
            path = root / "life.sqlite"
            individual_id = "m11:stage12:single-owner-life"
            with M11TransactionalMortal.birth(
                db_path=str(path), runtime=original,
                individual_id=individual_id,
            ) as life:
                with self.assertRaises(RuntimeError):
                    original.run_step()
                receipt = life.run_step()
                self.assertEqual(receipt.generation, 1)
                self.assertEqual(receipt.world_step, 1)
                self.assertEqual(receipt.outcome, "applied")
                self.assertGreater(receipt.journal_count, 0)
                audit = SQLiteLifeLedger.audit_read_only(
                    path=str(path), expected_individual_id=individual_id,
                )
                self.assertEqual(audit.generation, 1)
                self.assertEqual(audit.journal_head, receipt.journal_head)
                self.assertTrue(audit.may_recover)
            resumed = M11TransactionalMortal.cold_recover(
                db_path=str(path), individual_id=individual_id,
                runtime_factory=fresh,
            )
            with resumed:
                second = resumed.run_step()
                self.assertEqual(second.generation, 2)
                self.assertEqual(second.world_step, 2)


if __name__ == "__main__":
    unittest.main()
