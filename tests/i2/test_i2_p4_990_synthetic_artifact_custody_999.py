"""Pure no-birth tests for P4 #990 synthetic artifact custody verification."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.i2_p4_990_synthetic_artifact_custody import (
    MANIFEST, make_fixture, verify_fixture,
)


class SyntheticArtifactCustodyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "evidence"
        make_fixture(self.root)

    def test_both_completed_and_aborted_journals_are_readable(self):
        report = verify_fixture(self.root)
        self.assertEqual(report["real_native_births"], 0)
        self.assertEqual(report["states"], ["completed", "aborted"])
        self.assertEqual(report["files_verified"], 4)

    def test_round_trip_after_relocation_without_original_absolute_path(self):
        restored = Path(self.temp.name) / "restored-elsewhere"
        shutil.copytree(self.root, restored)
        result = verify_fixture(restored)
        self.assertEqual(result["files_verified"], 4)
        self.assertNotIn(str(self.root), (restored / MANIFEST).read_text())

    def test_replaced_aborted_journal_is_detected(self):
        with (self.root / "aborted" / "original.sqlite").open("ab") as out:
            out.write(b"tamper")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verify_fixture(self.root)

    def test_missing_aborted_journal_is_detected(self):
        (self.root / "aborted" / "original.sqlite").unlink()
        with self.assertRaisesRegex(ValueError, "manifest missing"):
            verify_fixture(self.root)

    def test_extra_unreceipted_file_is_detected(self):
        (self.root / "unlisted.txt").write_text("unexpected", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "manifest missing"):
            verify_fixture(self.root)

    def test_absolute_path_and_traversal_are_refused(self):
        manifest = self.root / MANIFEST
        original = manifest.read_text(encoding="utf-8")
        for path in ("/tmp/foreign.sqlite", "../outside.sqlite"):
            with self.subTest(path=path):
                first, remainder = original.splitlines()[0], original.splitlines()[1:]
                digest = first.split("  ", 1)[0]
                manifest.write_text(digest + "  " + path + "\n" +
                                    "\n".join(remainder) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "manifest path"):
                    verify_fixture(self.root)
        manifest.write_text(original, encoding="utf-8")

    def test_symlink_is_refused(self):
        outside = Path(self.temp.name) / "outside"
        outside.write_bytes(b"nothing-native")
        (self.root / "symlink").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            verify_fixture(self.root)

    def test_relabelled_aborted_as_completed_is_detected(self):
        p = self.root / "aborted" / "status.json"
        obj = json.loads(p.read_text(encoding="utf-8"))
        obj["state"] = "COMPLETED"
        p.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verify_fixture(self.root)


if __name__ == "__main__":
    unittest.main()
