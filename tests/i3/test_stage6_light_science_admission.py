"""Prospective science admission contract: no World and no I3 life in tests.

Rehearsal receipts in this file are synthetic shape fixtures, never evidence
that any full 11,520-life technical rehearsal actually happened.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import stage6_light_native_gsr_transport as S

ROOT = "f5b19af3254e2eaaf8459ac7977f58a423dcacfeac141f7973705abcb354d012"
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
SOURCE = "5a56a9e52d4d2909bf2dfa64a4ec0066e0b3e814da25fd4df70ee56cc180edbf"


def synthetic_rehearsals():
    return {
        version: {
            "schema": "i3-stage6-rehearsal-receipt/v1",
            "status": "ENGINEERING_FULL_GSR_REHEARSAL_NO_SCIENCE",
            "python_version": version,
            "source_git_head": HEAD,
            "source_files_sha256": SOURCE,
            "allocation_sha256": ("a"*63 + str(i)),
            "last_chain_sha256": ("b"*63 + str(i)),
            "archive_sha256": ("c"*63 + str(i)),
            "reduction_sha256": ("d"*63 + str(i)),
            "lives_archived": 11520, "planned_worlds": 288,
            "phase_count": 9,
            "science_admission": False,
            "no_retry": True,
            "workflow_run_id": 123,
            "job_name": "engineering-" + version,
        } for i, version in enumerate(("3.11", "3.12"))
    }


class Stage6ProspectiveScienceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.destination = str(Path(cls.tmp.name) / "science-originals")
        cls.proofs = synthetic_rehearsals()
        cls.plan = S.make_science_plan(
            ROOT, HEAD, SOURCE, cls.destination, cls.proofs)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_separate_scope_exact_16_populations_no_exposure(self):
        plan = self.plan
        self.assertEqual(S.verify_science_plan(plan), plan)
        self.assertEqual(plan["schema"], S.SCIENCE_SCHEMA)
        self.assertEqual(plan["protocol"], S.SCIENCE_PROTOCOL)
        self.assertTrue(plan["scientific_admission"])
        self.assertEqual(plan["source_of_science_authorization"],
                         "ADR-0022_SEPARATE_SCOPE")
        self.assertEqual(plan["planned_lives"], 11520)
        self.assertEqual(plan["fixed_sign_threshold"], 13)
        self.assertEqual(plan["fixed_neutral_invalid_at"], 2)
        self.assertEqual(plan["actual_lives_at_allocation"], 0)
        self.assertNotEqual(plan["allocation_sha256"],
                            S.make_plan(ROOT, HEAD, SOURCE,
                                        self.destination)["allocation_sha256"])
        self.assertEqual(S.make_science_plan(ROOT, HEAD, SOURCE,
                                            self.destination, self.proofs), plan)

    def test_incomplete_forged_or_same_allocation_rehearsals_denied(self):
        for change in ("missing", "lives", "source", "status", "science",
                       "same_root", "python", "phase", "foreign_key"):
            with self.subTest(change=change):
                proofs = deepcopy(self.proofs)
                if change == "missing":
                    del proofs["3.12"]
                elif change == "lives":
                    proofs["3.12"]["lives_archived"] = 11519
                elif change == "source":
                    proofs["3.11"]["source_git_head"] = "0"*40
                elif change == "status":
                    proofs["3.11"]["status"] = "FAILURE"
                elif change == "science":
                    proofs["3.12"]["science_admission"] = True
                elif change == "same_root":
                    proofs["3.12"]["allocation_sha256"] = proofs["3.11"]["allocation_sha256"]
                elif change == "python":
                    proofs["3.11"]["python_version"] = "3.13"
                elif change == "phase":
                    proofs["3.12"]["phase_count"] = 8
                else:
                    proofs["3.12"]["winner"] = "positive"
                with self.assertRaises(PermissionError):
                    S.make_science_plan(ROOT, HEAD, SOURCE,
                                        self.destination, proofs)

    def test_post_exposure_mutation_or_repurpose_denied(self):
        for key, value in (
                ("status", "ALREADY_EXECUTED"),
                ("archive_root", self.destination+"-retry"),
                ("scientific_admission", False),
                ("fixed_primary", "omega"),
                ("fixed_sign_threshold", 12),
                ("planned_lives", 100),
                ("source_files_sha256", "0"*64),
                ("allocation_sha256", "0"*64),
        ):
            changed = deepcopy(self.plan)
            changed[key] = value
            with self.subTest(field=key), self.assertRaises(
                    (PermissionError, ValueError)):
                S.verify_science_plan(changed)

    def test_no_birth_when_sha_or_checkout_fails(self):
        root = Path(self.destination)
        with self.assertRaises(PermissionError):
            S.run_full(self.plan, self.destination,
                       "0"*64)
        self.assertFalse(root.exists())
        with patch.object(S.G0, "_verify_checkout",
                          side_effect=PermissionError("wrong source")):
            with self.assertRaises(PermissionError):
                S.run_full(self.plan, self.destination,
                           self.plan["allocation_sha256"])
        self.assertFalse(root.exists())
        with self.assertRaises(PermissionError):
            S.run_full(self.plan, self.destination+"-retry",
                       self.plan["allocation_sha256"])
        self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
