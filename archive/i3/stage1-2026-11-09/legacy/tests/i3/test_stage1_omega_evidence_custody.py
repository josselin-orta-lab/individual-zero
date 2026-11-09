"""Deterministic Stage-1 omega evidence bundle custody; no I3 lives."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab.stage1_omega_evidence_custody import (
    FIXED_DATE, MANIFEST, bundle_directory, verify_bundle)


class OmegaEvidenceCustodyTests(unittest.TestCase):
    def _tree(self, root):
        root = Path(root)
        (root / "original").mkdir(parents=True)
        (root / "selection-shard.json").write_text(
            '{"status":"COMPLETE"}\n')
        (root / "original/life-001.json.gz").write_bytes(b"gzip-one")
        (root / "original/life-002.json.gz").write_bytes(b"gzip-two")

    def test_same_evidence_tree_produces_byte_identical_bundle(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            self._tree(Path(a) / "tree")
            self._tree(Path(b) / "tree")
            # Disturb filesystem metadata; bundle identity must ignore it.
            os.utime(Path(b) / "tree/selection-shard.json", (1000000, 1000000))
            out_a = Path(a) / "a.zip"
            out_b = Path(b) / "b.zip"
            ra = bundle_directory(
                Path(a) / "tree", out_a, label="selection-p0-reference")
            rb = bundle_directory(
                Path(b) / "tree", out_b, label="selection-p0-reference")
            self.assertEqual(out_a.read_bytes(), out_b.read_bytes())
            self.assertEqual(ra["bundle_sha256"], rb["bundle_sha256"])
            self.assertEqual(ra["tree_sha256"], rb["tree_sha256"])
            self.assertEqual(ra["file_count"], 3)

    def test_verification_matches_creation_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "tree"
            self._tree(root)
            out = Path(d) / "bundle.zip"
            made = bundle_directory(root, out, label="validation-p7-omega-zero")
            verified = verify_bundle(out)
            self.assertEqual(verified["status"], "VERIFIED")
            for key in (
                    "label", "bundle_bytes", "bundle_sha256",
                    "tree_sha256", "file_count",
                    "total_uncompressed_bytes"):
                self.assertEqual(verified[key], made[key])

            with zipfile.ZipFile(out) as archive:
                infos = archive.infolist()
                self.assertEqual(infos[0].filename, MANIFEST)
                self.assertTrue(all(info.date_time == FIXED_DATE
                                    for info in infos))
                self.assertEqual(
                    [x.filename for x in infos[1:]],
                    sorted(x.filename for x in infos[1:]))

    def test_symlink_is_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unsupported")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "tree"
            root.mkdir()
            (root / "real").write_text("x")
            try:
                os.symlink(root / "real", root / "alias")
            except OSError:
                self.skipTest("symlink creation denied")
            with self.assertRaisesRegex(ValueError, "symlinks"):
                bundle_directory(
                    root, Path(d) / "bundle.zip", label="bad")

    def test_output_inside_evidence_tree_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "tree"
            root.mkdir()
            (root / "x").write_text("x")
            with self.assertRaisesRegex(ValueError, "outside"):
                bundle_directory(
                    root, root / "bundle.zip", label="bad")

    def test_empty_tree_and_empty_label_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "tree"
            root.mkdir()
            with self.assertRaises(ValueError):
                bundle_directory(
                    root, Path(d) / "bundle.zip", label="empty")
            (root / "x").write_text("x")
            with self.assertRaises(ValueError):
                bundle_directory(
                    root, Path(d) / "bundle.zip", label="")

    def test_manifest_member_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "tree"
            self._tree(root)
            out = Path(d) / "bundle.zip"
            bundle_directory(root, out, label="good")
            tampered = Path(d) / "tampered.zip"
            # Rebuild the archive with one undeclared member.
            with zipfile.ZipFile(out, "r") as source, zipfile.ZipFile(
                    tampered, "w", compression=zipfile.ZIP_DEFLATED) as dest:
                for info in source.infolist():
                    dest.writestr(info, source.read(info.filename))
                dest.writestr("EXTRA", b"not-in-manifest")
            with self.assertRaisesRegex(ValueError, "members"):
                verify_bundle(tampered)

    def test_member_digest_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "tree"
            self._tree(root)
            out = Path(d) / "bundle.zip"
            bundle_directory(root, out, label="good")
            tampered = Path(d) / "tampered.zip"
            with zipfile.ZipFile(out, "r") as source, zipfile.ZipFile(
                    tampered, "w", compression=zipfile.ZIP_DEFLATED) as dest:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename == "selection-shard.json":
                        data = b"changed"
                    dest.writestr(info, data)
            with self.assertRaisesRegex(ValueError, "digest"):
                verify_bundle(tampered)

    def test_import_does_not_load_world_runtime_or_gate(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_omega_evidence_custody; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.stage1_omega_adr0015_design' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
