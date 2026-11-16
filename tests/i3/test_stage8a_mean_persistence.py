"""Stage8A confirmatory mean-test and source-bound admission, ZERO native lives.

Pure and synthetic tests only: NOT an engineering rehearsal or scientific data.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from i3.lab import stage8a_mean_persistence as E

ROOT = "f5b19af3254e2eaaf8459ac7977f58a423dcacfeac141f7973705abcb354d012"
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
SOURCE = "5a56a9e52d4d2909bf2dfa64a4ec0066e0b3e814da25fd4df70ee56cc180edbf"


def fake_receipt(version, seed):
    return {
        "schema": E.RECEIPT, "status": E.TECH_PASS,
        "python_version": version, "workflow_run_id": 9999,
        "source_git_head": HEAD, "source_files_sha256": SOURCE,
        "allocation_sha256": seed*64,
        "seed_commitment_sha256": seed*64,
        "archive_root": "/tmp/never-born-stage8-archive-" + version,
        "panel_receipt_sha256": "c"*64,
        "archived_lives": 23040, "phase_count": 18,
        "scientific_admission": False, "no_retry": True,
        "job_name": "engineering-" + version,
    }


class Stage8MeanProspectiveNoWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = TemporaryDirectory()
        cls.original = str(Path(cls.context.name) / "science")
        cls.receipts = {"3.11": fake_receipt("3.11", "a"),
                        "3.12": fake_receipt("3.12", "b")}
        cls.tech = E.make_plan(ROOT, HEAD, SOURCE, cls.original)
        cls.sci = E.make_plan(ROOT, HEAD, SOURCE, cls.original,
                              scientific=True, rehearsals=cls.receipts)

    @classmethod
    def tearDownClass(cls):
        cls.context.cleanup()

    def test_new_32_population_source_locked_full_count_without_exposure(self):
        p = self.sci
        self.assertEqual(E.verify_plan(p), p)
        self.assertEqual(E.verify_plan(self.tech), self.tech)
        self.assertEqual(E.make_plan(ROOT, HEAD, SOURCE, self.original,
                                     scientific=True, rehearsals=self.receipts), p)
        self.assertEqual(p["planned_original_lives"], 23040)
        self.assertEqual(p["planned_worlds"], 576)
        self.assertEqual(p["originals_existing_at_allocation"], 0)
        self.assertEqual(p["frozen_method"]["population_units"], 32)
        self.assertEqual(len(p["panels"]), 2)
        self.assertEqual(sum(panel["planned_lives"] for panel in p["panels"]), 23040)
        self.assertEqual(len({x["root_hex"] for x in p["panels"]}), 2)
        self.assertNotEqual(self.tech["allocation_sha256"], p["allocation_sha256"])
        all_ids = []
        for panel in p["panels"]:
            self.assertEqual(panel["scientific_admission"], False)
            self.assertEqual(len(panel["founders"]), 384)
            self.assertEqual(len(panel["draws"]), 1536)
            self.assertEqual(panel["planned_lives"], 11520)
            self.assertEqual(panel["planned_worlds"], 288)
            all_ids.extend(x["world_seed"] for x in panel["worlds"])
            all_ids.extend(x["life_seed"] for x in panel["worlds"])
            all_ids.extend(x["genome_seed"] for x in panel["founders"])
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertFalse(Path(self.original).exists())

    def test_one_sided_mean_advantage_can_pass_despite_eight_negative_populations(self):
        # 24 positive and 8 negative: NOT a universal sign criterion.
        r = E.reduce_population_mean([30.0]*24 + [-5.0]*8)
        self.assertEqual(r["status"], E.SCIENCE_PASS)
        self.assertEqual(r["positive"], 24)
        self.assertEqual(r["negative"], 8)
        self.assertGreater(r["one_sided_97_5_percent_lower_bound_steps"], 0)
        self.assertGreater(r["mean_difference_steps"], 0)

    def test_positive_mean_without_reliable_lower_bound_must_fail(self):
        vals = [52.0]*8 + [-8.0]*24
        r = E.reduce_population_mean(vals)
        self.assertGreater(r["mean_difference_steps"], 0)
        self.assertLessEqual(r["one_sided_97_5_percent_lower_bound_steps"], 0)
        self.assertEqual(r["status"], E.SCIENCE_NO)
        self.assertFalse(r["primary_success"])

    def test_negative_null_zero_variance_and_missing_population_fail(self):
        for values in ([0.0]*32, [-5.0]*32, [0.1]*32):
            r = E.reduce_population_mean(values)
            self.assertEqual(r["status"], E.SCIENCE_NO)
        with self.assertRaises(ValueError):
            E.reduce_population_mean([1.0]*31)
        with self.assertRaises(ValueError):
            E.reduce_population_mean([float("nan")]+[1.0]*31)
        with self.assertRaises(ValueError):
            E.reduce_population_mean([float("inf")]+[1.0]*31)

    def test_old_stage7_or_forged_incomplete_engineering_cannot_admit(self):
        for variant in ("missing", "foreign", "lives", "source", "phase",
                        "same_seed", "same_root", "wrong_job", "new_field"):
            rr = deepcopy(self.receipts)
            if variant == "missing":
                rr.pop("3.12")
            elif variant == "foreign":
                rr["3.12"]["schema"] = "i3-stage7-persistence-full-rehearsal/v1"
            elif variant == "lives":
                rr["3.12"]["archived_lives"] = 23039
            elif variant == "source":
                rr["3.11"]["source_git_head"] = "0"*40
            elif variant == "phase":
                rr["3.12"]["phase_count"] = 9
            elif variant == "same_seed":
                rr["3.12"]["seed_commitment_sha256"] = rr["3.11"]["seed_commitment_sha256"]
            elif variant == "same_root":
                rr["3.12"]["archive_root"] = rr["3.11"]["archive_root"]
            elif variant == "wrong_job":
                rr["3.12"]["job_name"] = "engineering-3.11"
            else:
                rr["3.12"]["observed_winner"] = "selected"
            with self.subTest(variant=variant), self.assertRaises(PermissionError):
                E.make_plan(ROOT, HEAD, SOURCE, self.original, scientific=True,
                            rehearsals=rr)

    def test_no_method_change_no_reroll_or_birth_on_source_failure(self):
        for field, value in (
                ("schema", "stage7"),
                ("planned_original_lives", 2),
                ("scientific_verdict_before_exposure", "PASS"),
                ("archive_root", self.original+"-retry"),
                ("source_files_sha256", "0"*64),
                ("allocation_sha256", "0"*64),
                ("no_retry", False),
                ("Stage6_and_Stage7_originals_not_reused", False),
        ):
            candidate = deepcopy(self.sci)
            candidate[field] = value
            with self.subTest(field=field), self.assertRaises(
                    (PermissionError, ValueError)):
                E.verify_plan(candidate)
        candidate = deepcopy(self.sci)
        candidate["frozen_method"]["t_critical_df31"] = 1.0
        with self.assertRaises(PermissionError):
            E.verify_plan(candidate)
        with self.assertRaises(PermissionError):
            E.run_once(self.sci, self.original, "0"*64)
        self.assertFalse(Path(self.original).exists())
        with patch.object(E.G0, "_verify_checkout", side_effect=PermissionError("dirty")):
            with self.assertRaises(PermissionError):
                E.run_once(self.sci, self.original,
                           self.sci["allocation_sha256"])
        self.assertFalse(Path(self.original).exists())



    def test_exact_horizon_death_is_not_a_censored_survivor(self):
        panel = self.sci["panels"][0]
        identity = {"genome_sha256": "f"*64, "life_seed": 123456,
                    "world_sha256": "e"*64}
        life = {
            "genome": identity["genome_sha256"],
            "life_seed": identity["life_seed"],
            "steps_lived": 400, "horizon": 400,
            "terminal": "dead", "trace": [{}]*400,
            "manifest": {
                "protocol": panel["protocol"],
                "world_sha256": identity["world_sha256"],
                "source": {
                    "git_head": panel["source_git_head"],
                    "sha256": panel["source_files_sha256"]},
            },
            "cognitive_accounting": {
                "status": "SETTLED_FOR_DECLARED_WORK",
                "shortfall_steps": 0,
            },
        }
        self.assertEqual(E._native_lifetime(life, identity, panel), (400, False))
        life["terminal"] = "censored"
        self.assertEqual(E._native_lifetime(life, identity, panel), (400, True))
        life["steps_lived"] = 399
        life["trace"] = [{}]*399
        with self.assertRaises(ValueError):
            E._native_lifetime(life, identity, panel)
        life["terminal"] = "dead"
        self.assertEqual(E._native_lifetime(life, identity, panel), (399, False))

    def test_mocked_one_shot_orchestrator_keeps_science_separate_without_worlds(self):
        # The entire native engine and science audit are mocked. A unit test
        # must never open a World or misrepresent a fixture as live evidence.
        with TemporaryDirectory() as tmp:
            root = str(Path(tmp) / "new-stage8-study")
            plan = E.make_plan(ROOT, HEAD, SOURCE, root,
                               scientific=True, rehearsals=self.receipts)
            fakecore = {"original_lives": 11520,
                        "phase_chain_sha256": "f"*64}
            fake_analysis = {
                "status": E.SCIENCE_NO,
                "primary": E.reduce_population_mean([0.0]*32),
                "native_original_lives_rechecked": 23040,
                "native_parent_draws_reproduced": 3072,
                "native_mutations_reproduced": 3072,
            }
            with patch.object(E.G0, "_verify_checkout", return_value=None), \
                 patch.object(E.P, "run_full",
                              side_effect=[fakecore, fakecore]) as native, \
                 patch.object(E, "_science_reduce",
                              return_value=fake_analysis) as reducer:
                core = E.run_once(plan, root, plan["allocation_sha256"])
                self.assertEqual(core["status"], E.SCIENCE_NO)
                self.assertEqual(core["original_lives"], 23040)
                self.assertEqual(native.call_count, 2)
                self.assertEqual(reducer.call_count, 1)
                self.assertTrue((Path(root) / "CLAIM.json").exists())
                self.assertTrue((Path(root) / "SCIENCE_FINAL.json").exists())
                self.assertFalse((Path(root) / "PANEL_0/G0").exists())
                with self.assertRaises(FileExistsError):
                    E.run_once(plan, root, plan["allocation_sha256"])

    def test_mocked_partial_engineering_failure_cannot_be_replayed(self):
        with TemporaryDirectory() as tmp:
            root = str(Path(tmp) / "failed-stage8-technical")
            plan = E.make_plan(ROOT, HEAD, SOURCE, root)
            stub = {"original_lives": 11520, "phase_chain_sha256": "a"*64}
            with patch.object(E.G0, "_verify_checkout", return_value=None), \
                 patch.object(E.P, "run_full",
                              side_effect=[stub, RuntimeError("fixture failure")]):
                with self.assertRaises(RuntimeError):
                    E.run_once(plan, root, plan["allocation_sha256"])
            failure = Path(root) / "FAILURE.json"
            self.assertTrue(failure.exists())
            self.assertEqual(__import__("json").loads(failure.read_text())["status"],
                             "TECHNICAL_NO_VERDICT_NO_RETRY")
            with self.assertRaises(FileExistsError):
                with patch.object(E.G0, "_verify_checkout", return_value=None):
                    E.run_once(plan, root, plan["allocation_sha256"])


if __name__ == "__main__":
    unittest.main()
