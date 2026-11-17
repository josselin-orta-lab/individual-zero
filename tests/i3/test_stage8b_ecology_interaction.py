"""Stage8-B frozen two-df ecological interaction: pure tests, ZERO lives.

All values are synthetic fixtures, never eligible as scientific evidence.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from i3.lab import stage8b_ecology_interaction as B


ROOT = "f5b19af3254e2eaaf8459ac7977f58a423dcacfeac141f7973705abcb354d012"
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
SOURCE = "5a56a9e52d4d2909bf2dfa64a4ec0066e0b3e814da25fd4df70ee56cc180edbf"


def rehearsals():
    def r(version, root):
        return {
            "schema": B.RECEIPT, "status": B.TECH_PASS,
            "python_version": version, "source_git_head": HEAD,
            "source_files_sha256": SOURCE,
            "allocation_sha256": root*64,
            "seed_commitment_sha256": root*64,
            "G2_holdout_worlds_sha256": root*64,
            "archive_root": "/tmp/stage8b-technical-" + version,
            "underlying_native_receipt_sha256": "c"*64,
            "archived_lives": 23040, "phase_count": 18,
            "scientific_admission": False, "no_retry": True,
            "workflow_run_id": 6789, "job_name": "engineering-" + version,
        }
    return {"3.11": r("3.11", "a"), "3.12": r("3.12", "b")}


def matrix(null=False):
    vals = []
    for i in range(32):
        x = ((i % 8) - 3.5)*0.7
        y = (((i * 7) % 13)-6)*0.9
        vals.append({
            "stable": 10.0,
            "depletion": 10.0 + (x if null else 25 + x),
            "pulse": 10.0 + (y if null else -18 + y),
        })
    return vals


class Stage8BNoBirthUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()
        cls.path = str(Path(cls.temp.name) / "originals")
        cls.rehearsals = rehearsals()
        cls.engineering = B.make_plan(ROOT, HEAD, SOURCE, cls.path)
        cls.science = B.make_plan(ROOT, HEAD, SOURCE, cls.path,
                                  science=True, rehearsals=cls.rehearsals)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_192_heldout_g2_worlds_reserved_before_any_birth(self):
        p = self.science
        self.assertEqual(B.verify_plan(p), p)
        self.assertEqual(B.verify_plan(self.engineering), self.engineering)
        self.assertEqual(p["planned_lives"], 23040)
        self.assertEqual(p["planned_worlds"], 576)
        self.assertEqual(p["planned_g2_holdout_worlds"], 192)
        self.assertEqual(p["planned_g2_native_lives"], 9216)
        self.assertEqual(p["all_originals_at_allocation"], 0)
        self.assertEqual(p["frozen_method"]["n_population_units"], 32)
        self.assertTrue(p["frozen_method"]["G2_worlds_precommitted_and_blind_to_parent_fitness"])
        self.assertEqual(p["preexposure_scientific_verdict"], "NOT_ISSUED")
        w = p["g2_holdout_reserved_worlds"]
        self.assertEqual(len({(x["population"], x["family"], x["repeat"])
                              for x in w}), 192)
        self.assertEqual(len({x["world_seed"] for x in w}), 192)
        self.assertEqual(set(x["family"] for x in w), {"stable", "depletion", "pulse"})
        self.assertEqual(len(p["inner_native_technical_plan"]["panels"]), 2)
        self.assertFalse(Path(self.path).exists())

    def test_new_stage8b_root_and_archive_cannot_reuse_rehearsals(self):
        self.assertNotEqual(self.engineering["allocation_sha256"],
                            self.science["allocation_sha256"])
        rr = deepcopy(self.rehearsals)
        rr["3.12"]["G2_holdout_worlds_sha256"] = rr["3.11"]["G2_holdout_worlds_sha256"]
        with self.assertRaises(PermissionError):
            B.make_plan(ROOT, HEAD, SOURCE, self.path,
                        science=True, rehearsals=rr)
        rr = deepcopy(self.rehearsals)
        rr["3.12"]["workflow_run_id"] = 777
        with self.assertRaises(PermissionError):
            B.make_plan(ROOT, HEAD, SOURCE, self.path,
                        science=True, rehearsals=rr)

    def test_omnibus_detects_any_ecological_heterogeneity_no_cherry_pick(self):
        result = B.omnibus(matrix())
        self.assertEqual(result["status"], B.SCIENCE_PASS)
        self.assertTrue(result["primary_success"])
        self.assertLess(result["p_value_two_sided_omnibus"], 0.025)
        self.assertEqual(result["n_populations"], 32)
        self.assertTrue(result["covariance_identifiable"])
        self.assertEqual(len(result["primary_population_vectors"]), 32)
        self.assertAlmostEqual(result["two_family_contrasts_means"]["depletion_minus_stable"], 25, delta=1)
        self.assertAlmostEqual(result["two_family_contrasts_means"]["pulse_minus_stable"], -18, delta=1)

    def test_null_and_singular_covariance_never_get_promoted(self):
        # Null has small random-ish population-level fluctuations, no mean.
        z = B.omnibus(matrix(null=True))
        self.assertEqual(z["status"], B.SCIENCE_NO)
        self.assertGreaterEqual(z["p_value_two_sided_omnibus"], 0.025)
        all_equal = B.omnibus([{"stable": 12, "depletion": 12, "pulse": 12}
                               for _ in range(32)])
        self.assertEqual(all_equal["status"], B.SCIENCE_NO)
        self.assertFalse(all_equal["covariance_identifiable"])
        self.assertFalse(all_equal["primary_success"])
        self.assertEqual(all_equal["p_value_two_sided_omnibus"], 1.0)

    def test_omnibus_invariant_to_relabelling_ecological_families(self):
        a = B.omnibus(matrix())
        reverse = [
            {"stable": r["pulse"], "depletion": r["stable"],
             "pulse": r["depletion"]} for r in matrix()]
        b = B.omnibus(reverse)
        self.assertAlmostEqual(a["hotelling_t_squared"], b["hotelling_t_squared"], places=8)
        self.assertAlmostEqual(a["p_value_two_sided_omnibus"],
                               b["p_value_two_sided_omnibus"], places=8)

    def test_all_population_vectors_required_and_finite(self):
        with self.assertRaises(ValueError):
            B.omnibus(matrix()[:31])
        v = matrix()
        del v[0]["pulse"]
        with self.assertRaises(ValueError):
            B.omnibus(v)
        v = matrix()
        v[17]["stable"] = float("nan")
        with self.assertRaises(ValueError):
            B.omnibus(v)

    def test_foreign_or_incomplete_old_rehearsals_cannot_admit(self):
        for variant in ("missing", "stage8a", "foreign_source", "incomplete",
                        "same_seed", "same_archive", "wrong_phase", "scientific",
                        "retry", "wrong_version"):
            rr = deepcopy(self.rehearsals)
            if variant == "missing":
                rr.pop("3.11")
            elif variant == "stage8a":
                rr["3.11"]["schema"] = "i3-stage8a-complete-native-rehearsal-receipt/v1"
            elif variant == "foreign_source":
                rr["3.11"]["source_git_head"] = "0"*40
            elif variant == "incomplete":
                rr["3.12"]["archived_lives"] = 23039
            elif variant == "same_seed":
                rr["3.12"]["seed_commitment_sha256"] = rr["3.11"]["seed_commitment_sha256"]
            elif variant == "same_archive":
                rr["3.12"]["archive_root"] = rr["3.11"]["archive_root"]
            elif variant == "wrong_phase":
                rr["3.12"]["phase_count"] = 9
            elif variant == "scientific":
                rr["3.12"]["scientific_admission"] = True
            elif variant == "retry":
                rr["3.11"]["no_retry"] = False
            else:
                rr["3.12"]["python_version"] = "3.13"
            with self.subTest(variant=variant), self.assertRaises(PermissionError):
                B.make_plan(ROOT, HEAD, SOURCE, self.path, science=True, rehearsals=rr)

    def test_prospective_plan_cannot_be_reinterpreted(self):
        for field, value in (
            ("status", "ALREADY_PASS"),
            ("scientific_admission", False),
            ("allocation_sha256", "0"*64),
            ("source_git_head", "0"*40),
            ("archive_root", self.path+"-retry"),
            ("planned_lives", 4),
            ("g2_holdout_worlds_sha256", "0"*64),
            ("g2_holdout_reserved_worlds", []),
            ("prior_stage8a_plan_sha256_for_nonreplay", "0"*64),
            ("no_retry", False),
        ):
            with self.subTest(field=field):
                p = deepcopy(self.science)
                p[field] = value
                with self.assertRaises((PermissionError, ValueError)):
                    B.verify_plan(p)
        p = deepcopy(self.science)
        p["frozen_method"]["alpha_omnibus"] = 0.9
        with self.assertRaises(PermissionError):
            B.verify_plan(p)

    def test_mocked_complete_source_exact_science_no_native_birth(self):
        with TemporaryDirectory() as td:
            root = str(Path(td) / "stage8b-unborn")
            p = B.make_plan(ROOT, HEAD, SOURCE, root,
                            science=True, rehearsals=self.rehearsals)
            fake_core = {
                "status": B.A.TECH_PASS,
                "original_lives": 23040,
                "plan_sha256": p["inner_native_technical_plan"]["allocation_sha256"],
                "panel_chain_sha256": ["a"*64, "b"*64],
            }
            fake_analysis = {
                "status": B.SCIENCE_NO, "primary": B.omnibus(matrix(null=True)),
                "all_native_lives_reverified": 23040,
                "parent_draws_reproduced": 3072, "mutations_reproduced": 3072,
            }
            with patch.object(B.G0, "_verify_checkout", return_value=None), \
                 patch.object(B.A, "run_once", return_value=fake_core) as fake, \
                 patch.object(B, "_reduce_originals", return_value=fake_analysis):
                result = B.run_once(p, root, p["allocation_sha256"])
                self.assertEqual(result["status"], B.SCIENCE_NO)
                self.assertEqual(fake.call_count, 1)
                self.assertTrue((Path(root) / "CLAIM.json").exists())
                self.assertTrue((Path(root) / "SCIENCE_FINAL.json").exists())
                self.assertFalse((Path(root) / "NATIVE_ORIGINALS").exists())
                with self.assertRaises(FileExistsError):
                    B.run_once(p, root, p["allocation_sha256"])

    def test_failed_second_panel_is_irreversibly_claimed(self):
        with TemporaryDirectory() as td:
            root = str(Path(td) / "stage8b-technical-no-retry")
            p = B.make_plan(ROOT, HEAD, SOURCE, root)
            with patch.object(B.G0, "_verify_checkout", return_value=None), \
                 patch.object(B.A, "run_once",
                              side_effect=RuntimeError("synthetic panel defect")):
                with self.assertRaises(RuntimeError):
                    B.run_once(p, root, p["allocation_sha256"])
            self.assertTrue((Path(root) / "FAILURE.json").exists())
            self.assertFalse((Path(root) / "SCIENCE_FINAL.json").exists())
            self.assertEqual(json.loads((Path(root) / "FAILURE.json").read_text())
                             ["status"], "TECHNICAL_NO_VERDICT_NO_RETRY")
            with patch.object(B.G0, "_verify_checkout", return_value=None):
                with self.assertRaises(FileExistsError):
                    B.run_once(p, root, p["allocation_sha256"])


if __name__ == "__main__":
    unittest.main()
