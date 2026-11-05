"""No-birth negative tests for #990 secondary evidence copy."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.i2_p4_990_synthetic_artifact_custody import make_fixture
from tools.i2_p4_990_secondary_evidence_copy import (
    CONFIRM, MANIFEST, RECEIPT, copy_to_secondary, verify_copy,
)


class SecondaryCopyContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "synthetic-source"
        self.destination = self.root / "synthetic-remote-copy"
        make_fixture(self.source)

    def _copy(self):
        return copy_to_secondary(
            self.source, self.destination, confirmation=CONFIRM,
            allow_same_device_for_synthetic_test=True)

    def test_synthetic_only_secondary_copy_and_relocation(self):
        result = self._copy()
        self.assertTrue(result["verified"])
        self.assertEqual(result["file_count"], 4)
        self.assertFalse(result["independent_m11"])
        self.assertEqual(result["storage_device_check"],
                         "SYNTHETIC_SAME_DEVICE_ONLY")
        receipt = (self.destination / RECEIPT).read_text()
        self.assertNotIn(str(self.source), receipt)
        moved = self.root / "moved"
        self.destination.rename(moved)
        self.assertTrue(verify_copy(moved)["verified"])

    def test_requires_confirm_and_distinct_device_by_default(self):
        with self.assertRaisesRegex(ValueError, "confirmation"):
            copy_to_secondary(self.source, self.destination,
                              confirmation="DO-NOT-COPY")
        with self.assertRaisesRegex(ValueError, "different filesystem"):
            copy_to_secondary(self.source, self.destination,
                              confirmation=CONFIRM)
        self.assertFalse(self.destination.exists())

    def test_rejects_existing_destination_and_does_not_overwrite(self):
        self.destination.mkdir()
        marker = self.destination / "do-not-touch.txt"
        marker.write_text("preserve", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "new path"):
            self._copy()
        self.assertEqual(marker.read_text(), "preserve")

    def test_corrupted_original_refuses_before_copy(self):
        with (self.source / "aborted" / "original.sqlite").open("ab") as out:
            out.write(b"unexpected")
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            self._copy()
        self.assertFalse(self.destination.exists())

    def test_tampering_secondary_database_fails_readback(self):
        self._copy()
        with (self.destination / "completed" / "original.sqlite").open("ab") as f:
            f.write(b"tamper")
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            verify_copy(self.destination)

    def test_missing_aborted_file_is_not_silent(self):
        self._copy()
        (self.destination / "aborted" / "original.sqlite").unlink()
        with self.assertRaisesRegex(ValueError, "unlisted, missing"):
            verify_copy(self.destination)

    def test_manifest_path_traversal_and_symlink_refused(self):
        original = (self.source / MANIFEST).read_text()
        line = original.splitlines()[0]
        digest = line.split("  ", 1)[0]
        (self.source / MANIFEST).write_text(
            digest + "  ../outside.sqlite\n" + "\n".join(
                original.splitlines()[1:]) + "\n")
        with self.assertRaisesRegex(ValueError, "unsafe"):
            self._copy()
        (self.source / MANIFEST).write_text(original)
        (self.source / "link").symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            self._copy()

    def test_duplicate_receipt_and_unlisted_data_refused(self):
        (self.source / RECEIPT).write_text("forged", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "must not have"):
            self._copy()
        (self.source / RECEIPT).unlink()
        (self.source / "extra.txt").write_text("unlisted", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unlisted, missing"):
            self._copy()

    def test_rejects_receipt_forgery_and_copy_into_source(self):
        self._copy()
        (self.destination / RECEIPT).write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "receipt does not match"):
            verify_copy(self.destination)
        nested = self.source / "nested-copy"
        with self.assertRaisesRegex(ValueError, "disjoint"):
            copy_to_secondary(self.source, nested, confirmation=CONFIRM,
                              allow_same_device_for_synthetic_test=True)

    def test_source_and_copied_manifest_must_match(self):
        self._copy()
        (self.destination / MANIFEST).write_text(
            (self.destination / MANIFEST).read_text() + "a" * 64 +
            "  invented.sqlite\n")
        with self.assertRaisesRegex(ValueError, "unlisted, missing"):
            verify_copy(self.destination)


if __name__ == "__main__":
    unittest.main()
