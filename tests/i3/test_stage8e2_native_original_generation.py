"""Stage8-E2 native original generation contract: no life is run by tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from i3.lab import stage8e2_native_original_generation as N
from i3.modules import genome as G

ROOT = "0123456789abcdef" * 4
SOURCE = "0123456789abcdef" * 4


class Stage8E2NativeOriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.founders = {(p, "shared", s): G.generation_zero(400000+p*24+s)
                        for p in range(64) for s in range(24)}

    def test_all_g0_original_case_identities_and_physical_pairing(self):
        cases = N.generation_cases(ROOT, 0, self.founders, SOURCE)
        self.assertEqual(len(cases), 9216)
        self.assertEqual(384, len({
            (c["population"], c["family"], c["repeat"]) for c in cases}))
        self.assertEqual(9216, len({c["life_seed"] for c in cases}))
        self.assertEqual(384, len({c["world_seed"] for c in cases}))
        self.assertEqual(9216, len({
            (c["population"], c["arm"], c["slot"], c["family"], c["repeat"])
            for c in cases}))
        self.assertEqual({c["source_sha256"] for c in cases}, {SOURCE})

    def test_missing_native_genome_fails_before_birth(self):
        incomplete = dict(self.founders)
        incomplete.pop((0, "shared", 0))
        with self.assertRaises(ValueError):
            N.generation_cases(ROOT, 0, incomplete, SOURCE)
        with self.assertRaises(ValueError):
            N.generation_cases(ROOT, 3, self.founders, SOURCE)

    def test_no_scientific_or_technical_runner_without_exact_source(self):
        with tempfile.TemporaryDirectory() as path:
            target = str(Path(path) / "never-created")
            with patch.object(N, "_check_source", side_effect=PermissionError("dirty")):
                with self.assertRaises(PermissionError):
                    N.execute_technical_generation(
                        root=ROOT, generation=0, genomes=self.founders,
                        source_git_head="0"*40, source_files_sha256=SOURCE,
                        preflight={}, custody_dir=target,
                        published_plan_path=str(Path(path) / "plan.json"),
                        published_plan_file_sha256="a"*64)
            self.assertFalse(Path(target).exists())


    def test_direct_birth_without_prepublished_plan_fails_before_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            target = str(Path(temp) / "PHYSICAL_G0")
            with patch.object(N, "_check_source", return_value=None), (
                    patch.object(N.N, "verify_native_preflight",
                                 return_value={"manifest_sha256": "a"*64})):
                with self.assertRaises(PermissionError):
                    N.execute_technical_generation(
                        root=ROOT, generation=0, genomes=self.founders,
                        source_git_head="0"*40, source_files_sha256=SOURCE,
                        preflight={"manifest_sha256": "a"*64},
                        custody_dir=target,
                        published_plan_path=str(Path(temp) / "missing-plan.json"),
                        published_plan_file_sha256="a"*64)
            self.assertFalse(Path(target).exists())


if __name__ == "__main__":
    unittest.main()
