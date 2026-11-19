"""Original gzip hash tampering tests, without any native births."""
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from i3.lab import stage8e2_independent_original_audit as A
from i3.lab import two_phase_panel as TP

SOURCE = "a" * 64
HEAD = "b" * 40


def identity():
    return {
        "population": 0, "generation": 0, "arm": "shared",
        "slot": 0, "family": "stable", "repeat": 0,
        "world_seed": 2 << 60, "world_sha256": "c"*64,
        "life_seed": 3 << 60, "genome_sha256": "d"*64,
        "source_sha256": SOURCE,
    }


class Stage8E2OriginalCustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.expected = [identity()]
        self.life = {"steps_lived": 2, "terminal": "dead", "trace": [{}, {}]}
        TP.generate(self.expected, lambda _: self.life, self.path)

    def audit(self):
        with patch.object(A.C, "_check_native_life", return_value=None):
            return A.audit_original_generation(
                self.path, self.expected, source_pin=SOURCE,
                source_head=HEAD, protocol="synthetic-only", generation=0)

    def test_originals_rehashed_without_running_native_world(self):
        r = self.audit()
        self.assertEqual(r["original_lives_verified"], 1)
        self.assertEqual(r["six_life_rows"][0]["steps_lived"], 2)
        self.assertFalse(r["scientific_claim_authorized"])

    def test_modified_gzip_rejected(self):
        path = self.path / "life-000.json.gz"
        path.write_bytes(path.read_bytes() + b"bad")
        with self.assertRaises(ValueError):
            self.audit()

    def test_missing_original_rejected(self):
        (self.path / "life-000.json.gz").unlink()
        with self.assertRaises(ValueError):
            self.audit()

    def test_tampered_decoded_original_rejected_even_if_gzip_sha_resealed(self):
        manifest_path = self.path / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["files"][0]["uncompressed_sha256"] = "0"*64
        raw = TP._dump(manifest)
        manifest_path.write_bytes(raw)
        (self.path / "MANIFEST.sha256").write_text(sha256(raw).hexdigest() + "\n")
        with self.assertRaises(ValueError):
            self.audit()

    def test_duplicate_or_foreign_case_rejected(self):
        wrong = [dict(self.expected[0], slot=1)]
        with patch.object(A.C, "_check_native_life", return_value=None):
            with self.assertRaises(ValueError):
                A.audit_original_generation(
                    self.path, wrong, source_pin=SOURCE,
                    source_head=HEAD, protocol="synthetic-only", generation=0)


if __name__ == "__main__":
    unittest.main()
