"""Stage8-C science source-exact admission and inference tests: ZERO births."""
from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from i3.lab import stage8c_prospective_science as C
from i3.lab import stage8c_three_arm_transport as T

HEAD = "1234567890abcdef1234567890abcdef12345678"
SOURCE = "fedcba9876543210" * 4
ROOT = "1234567890abcdef" * 4


def synthetic_receipts(head=HEAD, source=SOURCE) -> dict:
    def one(version, token, root):
        return {
            "schema": T.RECEIPT_SCHEMA, "status": T.TECH_PASS,
            "python_version": version, "workflow_run_id": 8675309,
            "source_git_head": head, "source_files_sha256": source,
            "allocation_sha256": token*64,
            "archive_root": "/tmp/stage8c-source-test-" + root,
            "g2_holdout_worlds_sha256": root*64,
            "root_commitment_sha256": ("a" if version == "3.11" else "b")*64,
            "panel_audit_sha256": ("c" if version == "3.11" else "d")*64,
            "native_original_lives_rehashed": 32256,
            "native_mutations_reproduced": 4608, "phase_count": 18,
            "scientific_admission": False, "no_retry": True,
            "provenance": T.PROVENANCE,
        }
    return {"3.11": one("3.11", "e", "1"),
            "3.12": one("3.12", "f", "2")}


class Stage8CProspectiveScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory()
        cls.custody = str(Path(cls.tmp.name) / "new-science-originals")
        cls.receipts = synthetic_receipts()
        cls.plan = C.make_plan(ROOT, HEAD, SOURCE, cls.custody, cls.receipts)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exact_new_32_pop_admission_and_no_birth(self):
        p = self.plan
        self.assertEqual(p["schema"], C.SCHEMA)
        self.assertTrue(p["scientific_admission"])
        self.assertTrue(p["no_retry"])
        self.assertEqual(p["preexposure_scientific_result"], "NOT_ISSUED")
        self.assertEqual(p["planned_native_original_lives"], 32256)
        self.assertEqual(p["planned_worlds"], 576)
        self.assertEqual(p["planned_g2_heldout_worlds"], 192)
        self.assertEqual(p["planned_mutations"], 4608)
        self.assertEqual(p["frozen_method"], T.METHOD)
        self.assertEqual(p["frozen_scientific_inference"], C.PRIMARY)
        self.assertEqual(p["frozen_scientific_inference"]["n_population_units"], 32)
        self.assertEqual(p["frozen_scientific_inference"]["alpha_one_sided"], .025)
        self.assertEqual(p["frozen_scientific_inference"]["t_critical_df31"],
                         2.0395134463964077)
        self.assertEqual(p["source_git_head"], HEAD)
        self.assertEqual(p["source_files_sha256"], SOURCE)
        self.assertEqual(p["stage2_scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(C.verify_plan(p), p)
        self.assertEqual(C.make_plan(ROOT, HEAD, SOURCE, self.custody,
                                    self.receipts), p)
        self.assertFalse(Path(self.custody).exists())

    def test_native_transport_reused_only_as_separate_data_generator(self):
        p = self.plan
        inner = p["native_original_data_generator_plan"]
        self.assertFalse(inner["scientific_admission"])
        self.assertTrue(inner["science_generation_disabled"])
        self.assertEqual(inner["planned_original_lives"], 32256)
        self.assertEqual(inner["frozen_method"], T.METHOD)
        self.assertEqual(inner["source_git_head"], HEAD)
        self.assertEqual(inner["source_files_sha256"], SOURCE)
        self.assertEqual(len(inner["panels"]), 2)
        self.assertEqual(inner["g2_heldout_worlds_sha256"],
                         p["g2_heldout_worlds_sha256"])
        self.assertTrue(inner["archive_root"].endswith("/NATIVE_ORIGINALS"))
        self.assertEqual(T.verify_plan(inner), inner)
        self.assertFalse(Path(self.custody).exists())

    def test_reject_altered_method_admission_seeds_receipts(self):
        p = self.plan
        corruption = [
            ("frozen_scientific_inference", {**C.PRIMARY,
                                             "alpha_one_sided": .05}),
            ("root_hex", "abcdef0123456789"*4),
            ("source_files_sha256", "abcdef0123456789"*4),
            ("preexposure_scientific_result", "CLAIMED_POSITIVE"),
            ("scientific_admission", False),
            ("no_retry", False),
            ("g2_heldout_worlds_sha256", "a"*64),
            ("engineering_receipts", synthetic_receipts(head="0"*40)),
        ]
        for key, value in corruption:
            with self.subTest(key=key):
                bad = deepcopy(p)
                bad[key] = value
                with self.assertRaises((ValueError, PermissionError)):
                    C.verify_plan(bad)
        self.assertFalse(Path(self.custody).exists())

    def test_fail_closed_when_either_receipt_is_incomplete_or_off_source(self):
        bads = [
            ("3.12", "native_original_lives_rehashed", 32255),
            ("3.11", "scientific_admission", True),
            ("3.12", "source_git_head", "0"*40),
            ("3.12", "source_files_sha256", "f"*64),
            ("3.12", "allocation_sha256", self.receipts["3.11"]["allocation_sha256"]),
            ("3.11", "workflow_run_id", 99),
            ("3.12", "root_commitment_sha256",
             self.receipts["3.11"]["root_commitment_sha256"]),
        ]
        for version, field, new in bads:
            with self.subTest(version=version, field=field):
                r = deepcopy(self.receipts)
                r[version][field] = new
                with self.assertRaises(PermissionError):
                    C.make_plan(ROOT, HEAD, SOURCE, self.custody, r)
        self.assertFalse(Path(self.custody).exists())

    def test_prior_technical_rehearsals_not_valid_after_new_source_hash(self):
        # The two earlier PASS receipts on 4eae71e6... must be invalid here.
        old = synthetic_receipts(
            head="4eae71e6c7c93c011d2660221f742e89223a18e8",
            source="462a3e751f88e84bb824e773997826cd92fe025eeed1ce545419b5bfa8bdde57")
        with self.assertRaises(PermissionError):
            C.make_plan(ROOT, HEAD, SOURCE, self.custody, old)

    def test_authority_missing_cannot_create_science_admission(self):
        with patch.object(C.G0, "_pins", side_effect=PermissionError("deny")):
            with self.assertRaises(PermissionError):
                C.make_plan(ROOT, HEAD, SOURCE, self.custody, self.receipts)

    def test_bounded_original_g2_reduction_and_status(self):
        self.assertEqual(C.PRIMARY["primary_estimand"], T.METHOD["primary_estimand"])
        self.assertEqual(C.PRIMARY["test"], T.METHOD["primary_test"])
        self.assertEqual(C.PRIMARY["scope"], "F0_only")
        self.assertTrue(C.PRIMARY["technical_outcomes_not_used_for_inference"])
        self.assertEqual(T.reduce_primary_g2([float(12+i%3) for i in range(32)])["status"],
                         C.SCIENCE_PASS)
        self.assertEqual(T.reduce_primary_g2([float(-12+i%3) for i in range(32)])["status"],
                         C.SCIENCE_NO)
        self.assertEqual(T.reduce_primary_g2([10.]*32)["status"], C.SCIENCE_NO)

    def test_science_runs_only_after_published_sha_and_does_not_retry(self):
        p = self.plan
        with self.assertRaises(PermissionError):
            C.run_science(p, self.custody, "1"*64)
        with self.assertRaises(PermissionError):
            C.run_science(p, self.custody + "/forged", p["allocation_sha256"])
        self.assertFalse(Path(self.custody).exists())
        self.assertNotIn("run_life", inspect.getsource(C.make_plan))
        self.assertNotIn("world_for_stage6", inspect.getsource(C.make_plan))

    def test_cli_has_separate_science_and_no_old_original_import(self):
        source = inspect.getsource(C)
        self.assertIn("T.run_engineering(inner, inner[", source)
        self.assertIn("G0._verify_checkout(inner[", source)
        self.assertIn("T._panel_reaudit(panel, p_root)", source)
        self.assertIn("T.reduce_primary_g2(all_d)", source)
        self.assertIn('elif len(args) == 5 and args[1] == "run-science"', source)
        self.assertFalse(Path(self.custody).exists())


if __name__ == "__main__":
    unittest.main()
