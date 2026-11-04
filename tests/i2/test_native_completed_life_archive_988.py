"""#988: offline custodial SQLite backup guards, no born research individuals."""
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.i2_native_completed_life_archive import archive_completed_life


def report(*, terminal=False, revision=3, max_steps=3, energy=80.0):
    return {
        "revision": revision, "max_steps": max_steps,
        "terminal": terminal, "remaining_uc": 55,
        "site": "camp", "body": {
            "energy": energy, "food": 50.0, "water": 50.0,
            "integrity": 90.0,
        },
        "m11_authenticated": False, "engine_registered": False,
    }


class CompletedNativeCustody988(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "original.sqlite"
        self.archive = Path(self.tmp.name) / "sealed.sqlite"
        with sqlite3.connect(self.source) as db:
            db.execute("CREATE TABLE journal(seq INTEGER PRIMARY KEY, item TEXT)")
            db.execute("INSERT INTO journal VALUES(1,'observed')")
        self.original = self.source.read_bytes()

    @staticmethod
    def _identity(result):
        obj = MagicMock()
        obj.life_ref = "i2:born:source"
        obj.genesis_ref = "genesis:source"
        obj.audit.return_value = result
        return obj

    @patch("tools.i2_native_completed_life_archive.NativePaidI2.inspect")
    def test_cold_audited_copy_digest_and_original_unchanged(self, inspect):
        inspect.return_value = self._identity(report())
        receipt = archive_completed_life(self.source, self.archive)
        self.assertTrue(self.archive.is_file())
        self.assertEqual(self.source.read_bytes(), self.original)
        with sqlite3.connect(self.archive) as db:
            self.assertEqual(db.execute("SELECT item FROM journal").fetchone(),
                             ("observed",))
        self.assertEqual(receipt["archive_sha256"],
                         sha256(self.archive.read_bytes()).hexdigest())
        self.assertEqual(receipt["cold_audit"], "PASS")
        self.assertTrue(receipt["right_censored"])
        self.assertFalse(receipt["m11_authenticated"])
        self.assertEqual(inspect.call_count, 3)

    @patch("tools.i2_native_completed_life_archive.NativePaidI2.inspect")
    def test_wal_source_is_archived_as_one_independently_readable_file(self, inspect):
        inspect.return_value = self._identity(report())
        with sqlite3.connect(self.source) as db:
            self.assertEqual(db.execute("PRAGMA journal_mode=WAL").fetchone(),
                             ("wal",))
            db.execute("INSERT INTO journal VALUES(2,'wal-committed')")
        receipt = archive_completed_life(self.source, self.archive)
        self.assertEqual(receipt["archive_sha256"],
                         sha256(self.archive.read_bytes()).hexdigest())
        for suffix in ("-wal", "-shm", "-journal"):
            self.assertFalse(Path(str(self.archive) + suffix).exists())
        with sqlite3.connect(self.archive.resolve().as_uri() + "?mode=ro",
                             uri=True) as copied:
            self.assertEqual(copied.execute("PRAGMA journal_mode").fetchone(),
                             ("delete",))
            self.assertEqual(copied.execute("PRAGMA integrity_check").fetchone(),
                             ("ok",))
            self.assertEqual(copied.execute(
                "SELECT item FROM journal ORDER BY seq").fetchall(),
                [("observed",), ("wal-committed",)])

    @patch("tools.i2_native_completed_life_archive.NativePaidI2.inspect")
    def test_refuses_incomplete_and_existing_destination(self, inspect):
        inspect.return_value = self._identity(
            report(terminal=False, revision=2, max_steps=3))
        with self.assertRaisesRegex(ValueError, "only completed"):
            archive_completed_life(self.source, self.archive)
        self.assertFalse(self.archive.exists())
        self.assertEqual(self.source.read_bytes(), self.original)
        self.archive.write_text("must-not-overwrite")
        with self.assertRaisesRegex(ValueError, "new archive"):
            archive_completed_life(self.source, self.archive)
        self.assertEqual(self.archive.read_text(), "must-not-overwrite")

    @patch("tools.i2_native_completed_life_archive.NativePaidI2.inspect")
    def test_refuses_changed_copy_replay_without_publishing(self, inspect):
        inspect.side_effect = [
            self._identity(report()),
            self._identity(report(energy=79.0)),
        ]
        with self.assertRaisesRegex(ValueError, "differs"):
            archive_completed_life(self.source, self.archive)
        self.assertFalse(self.archive.exists())
        self.assertEqual(list(self.archive.parent.glob(".i2-custody-*")), [])

    @patch("tools.i2_native_completed_life_archive.NativePaidI2.inspect")
    def test_refuses_source_mutation_detected_at_final_audit(self, inspect):
        inspect.side_effect = [
            self._identity(report()),
            self._identity(report()),
            self._identity(report(energy=79.0)),
        ]
        with self.assertRaisesRegex(ValueError, "source changed"):
            archive_completed_life(self.source, self.archive)
        self.assertFalse(self.archive.exists())

    @patch("tools.i2_native_completed_life_archive.NativePaidI2.inspect")
    def test_terminal_life_and_duplicate_refusal(self, inspect):
        inspect.return_value = self._identity(
            report(terminal=True, revision=2, max_steps=3))
        result = archive_completed_life(self.source, self.archive)
        self.assertTrue(result["biological_terminal"])
        self.assertFalse(result["right_censored"])
        with self.assertRaisesRegex(ValueError, "new archive"):
            archive_completed_life(self.source, self.archive)
        with self.assertRaisesRegex(ValueError, "new archive"):
            archive_completed_life(self.source, self.source)

    @patch("tools.i2_native_completed_life_archive.NativePaidI2.inspect")
    def test_symlink_source_refused_before_inspection(self, inspect):
        link = Path(self.tmp.name) / "alias.sqlite"
        link.symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "existing regular"):
            archive_completed_life(link, self.archive)
        inspect.assert_not_called()

    @patch("tools.i2_native_completed_life_archive.NativePaidI2.inspect")
    def test_symlink_destination_refused_before_inspection(self, inspect):
        self.archive.symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "new archive"):
            archive_completed_life(self.source, self.archive)
        inspect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
