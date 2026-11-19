"""Stage8-E2 full source-locked native protocol tests, NO native births."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from i3.lab import stage8e2_technical_transport as T

ROOT = "0123456789abcdef" * 4
HEAD = "0123456789abcdef0123456789abcdef01234567"
SOURCE = "fedcba9876543210" * 4


class Stage8E2TechnicalTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()
        cls.base = Path(cls.temp.name)
        cls.plan = T.make_plan(ROOT, HEAD, SOURCE,
                               str(cls.base / "future-technical-originals"))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_exact_three_generation_budget_and_preexposure(self):
        p = self.plan
        self.assertEqual(T.verify_plan(p), p)
        self.assertEqual(p["planned_lives"], 64512)
        self.assertEqual(p["planned_lives_by_generation"], [9216, 18432, 36864])
        self.assertEqual(p["planned_original_gzip"], 64512)
        self.assertEqual(p["planned_mutations"], 6144)
        self.assertEqual(p["native_worldspecs"], 1152)
        self.assertEqual(len(p["native_preflight"]["g2_worldspecs"]), 384)
        self.assertEqual(p["founders"], 1536)
        self.assertFalse(p["scientific_admission"])
        self.assertEqual(p["science_verdict_before_exposure"], "NOT_ISSUED")
        self.assertEqual(p["frozen_method"]["two_sided_alpha"], 0.025)
        self.assertEqual(p["frozen_method"]["population_units"], 64)

    def test_any_pin_or_genetic_entropy_tampering_invalidates_plan(self):
        for field, replacement in (
            ("source_git_head", "1"*40),
            ("founder_allocation_sha256", "1"*64),
            ("mutation_allocation_sha256", "1"*64),
            ("g2_heldout_worlds_sha256", "1"*64),
            ("allocation_sha256", "0"*64),
            ("status", "USED"),
            ("scientific_admission", True),
        ):
            bad = deepcopy(self.plan)
            bad[field] = replacement
            with self.subTest(field=field), self.assertRaises(
                    (PermissionError, ValueError)):
                T.verify_plan(bad)

    def test_preexposure_bytes_must_match_before_archive_claim(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "preexposure.json"
            raw = T._canonical(self.plan)
            path.write_bytes(raw)
            target = Path(self.plan["archive_root"])
            with patch.object(T, "_assert_technical_environment",
                              side_effect=PermissionError("mocked-no-execution")):
                with self.assertRaises(PermissionError):
                    T.run_technical(str(path), sha256(raw).hexdigest())
            self.assertFalse(target.exists())
            with self.assertRaises(PermissionError):
                T.run_technical(str(path), "0"*64)

    def test_phase_chain_is_ordered_and_binds_artifacts(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            a = root / "a.json"
            b = root / "b.json"
            a.write_text("{}")
            b.write_text('{"ok":true}')
            record = T._append_phase(root, "G0", a, [])
            self.assertEqual(len(record), 1)
            with self.assertRaises(ValueError):
                T._append_phase(root, "SELECT_G1", b, record)
            record = T._append_phase(root, "SEAL_G0", b, record)
            self.assertEqual(record[1]["previous_chain_sha256"],
                             record[0]["chain_sha256"])
            self.assertEqual(len((root / "PHASES.jsonl").read_bytes().splitlines()), 2)


    def test_native_g1_cannot_start_before_g0_seal_and_parent_selection(self):
        from i3.lab import stage8e2_native_original_generation as GEN
        with TemporaryDirectory() as temp:
            archive = Path(temp) / "native-campaign"
            plan_path = Path(temp) / "frozen-before-g0.json"
            plan = T.make_plan(ROOT, HEAD, SOURCE, str(archive))
            frozen = T._canonical(plan)
            plan_path.write_bytes(frozen)
            archive.mkdir()
            (archive / "FROZEN_PLAN.json").write_bytes(frozen)
            T._write_new(archive / "CLAIM.json", {
                "schema": T.PLAN_SCHEMA + "/claim",
                "preexposure_file_sha256": sha256(frozen).hexdigest(),
                "plan_sha256": plan["allocation_sha256"],
                "status": "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
            })
            with patch.object(GEN, "_check_source", return_value=None), (
                    patch.object(GEN.N, "verify_native_preflight",
                                 return_value=plan["native_preflight"])):
                with self.assertRaises(PermissionError):
                    GEN.execute_technical_generation(
                        root=ROOT, generation=1, genomes={},
                        source_git_head=HEAD, source_files_sha256=SOURCE,
                        preflight=plan["native_preflight"],
                        custody_dir=str(archive / "PHYSICAL_G1"),
                        published_plan_path=str(plan_path),
                        published_plan_file_sha256=sha256(frozen).hexdigest())
            self.assertFalse((archive / "PHYSICAL_G1").exists())


if __name__ == "__main__":
    unittest.main()
