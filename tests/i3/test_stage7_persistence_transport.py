"""New Stage7 lineage survival study: PURE unit tests, ZERO native births.

Synthetic fixture scores/receipts are never used as scientific observations.
All post-exposure 2026-11-15 Stage6 organisms remain CLOSED_NO_RETRY.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import stage7_persistence_transport as P

ROOT = "f5b19af3254e2eaaf8459ac7977f58a423dcacfeac141f7973705abcb354d012"
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
SOURCE = "5a56a9e52d4d2909bf2dfa64a4ec0066e0b3e814da25fd4df70ee56cc180edbf"


def technical_fixture(version, root_id):
    return {
        "schema": P.RECEIPT, "status": P.REHEARSAL_PASS,
        "python_version": version, "source_git_head": HEAD,
        "source_files_sha256": SOURCE,
        "allocation_sha256": root_id*64,
        "allocation_seed_commitment_sha256": root_id*64,
        "archive_root": "/tmp/i3-stage7-engineering-" + version,
        "last_chain_sha256": "f"*64,
        "result_file_sha256": "e"*64,
        "lives_archived": 11520, "worlds_planned": 288,
        "phase_count": 9, "scientific_admission": False,
        "no_retry": True, "workflow_run_id": 4567,
        "job_name": "engineering-" + version,
    }


def fixture_fitness(g, positive_pops=16):
    arms = ("shared",) if g == 0 else P.S.ARMS
    scores = {}
    for p in range(16):
        for arm in arms:
            for s in range(24):
                step_per_life = 100
                if g == 1 and arm == "selected":
                    step_per_life = 107
                if g == 2 and arm == "selected":
                    step_per_life = 120 if p < positive_pops else 90
                scores[p, arm, s] = (0, 6 * step_per_life)
    return scores


class Stage7PersistenceNoBirthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.archive = str(Path(cls.tmp.name) / "research")
        cls.proofs = {
            "3.11": technical_fixture("3.11", "a"),
            "3.12": technical_fixture("3.12", "b"),
        }
        cls.tech = P.make_plan(ROOT, HEAD, SOURCE, cls.archive)
        cls.science = P.make_plan(
            ROOT, HEAD, SOURCE, cls.archive, science=True,
            rehearsals=cls.proofs)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_immutable_new_scientific_estimand_no_exposure(self):
        self.assertEqual(P.verify_plan(self.tech), self.tech)
        self.assertEqual(P.verify_plan(self.science), self.science)
        self.assertEqual(self.science["status"],
                         "PROSPECTIVE_PERSISTENCE_SCIENCE_ALLOCATED_NOT_EXPOSED")
        self.assertEqual(self.science["planned_lives"], 11520)
        self.assertEqual(self.science["planned_worlds"], 288)
        self.assertEqual(self.science["lives_per_generation"], [2304, 4608, 4608])
        self.assertEqual(self.science["frozen_method"]["primary_sign_threshold"], 13)
        self.assertEqual(self.science["frozen_method"]["primary_generation"], 2)
        self.assertEqual(self.science["frozen_method"]["one_sided_exact_tail"],
                         {"numerator": 697, "denominator": 65536})
        self.assertEqual(self.science["actual_lives_at_allocation"], 0)
        self.assertTrue(self.science["prior_stage6_20261115_observations_not_reused"])
        self.assertNotEqual(self.tech["allocation_sha256"],
                            self.science["allocation_sha256"])
        self.assertEqual(len(self.science["worlds"]), 288)
        self.assertEqual(len(self.science["draws"]), 1536)

    def test_reject_two_old_foreign_forged_and_missing_rehearsals(self):
        for variant in (
            "missing", "status", "sha", "lives", "phase", "same_allocation",
            "same_archive", "version", "external", "science",
        ):
            with self.subTest(variant=variant):
                proof = deepcopy(self.proofs)
                if variant == "missing":
                    del proof["3.12"]
                elif variant == "status":
                    proof["3.12"]["status"] = "FAILURE"
                elif variant == "sha":
                    proof["3.11"]["source_git_head"] = "0"*40
                elif variant == "lives":
                    proof["3.11"]["lives_archived"] = 11519
                elif variant == "phase":
                    proof["3.12"]["phase_count"] = 8
                elif variant == "same_allocation":
                    proof["3.12"]["allocation_sha256"] = proof["3.11"]["allocation_sha256"]
                elif variant == "same_archive":
                    proof["3.12"]["archive_root"] = proof["3.11"]["archive_root"]
                elif variant == "version":
                    proof["3.12"]["python_version"] = "3.13"
                elif variant == "external":
                    proof["3.11"]["schema"] = "i3-stage6-rehearsal-receipt/v1"
                elif variant == "science":
                    proof["3.12"]["scientific_admission"] = True
                with self.assertRaises(PermissionError):
                    P.make_plan(ROOT, HEAD, SOURCE, self.archive,
                                science=True, rehearsals=proof)

    def test_frozen_metric_or_plan_changes_are_not_admitted(self):
        for field, value in (
            ("status", "PUBLISHED_PASS"),
            ("protocol", "stage6-old"),
            ("research_scope", "ALL_WORLDS"),
            ("planned_lives", 11),
            ("source_git_head", "0"*40),
            ("archive_root", self.archive+"-tryagain"),
            ("allocation_sha256", "0"*64),
            ("scientific_admission", False),
            ("prior_stage6_20261115_observations_not_reused", False),
        ):
            plan = deepcopy(self.science)
            plan[field] = value
            with self.subTest(field=field), self.assertRaises(
                    (ValueError, PermissionError)):
                P.verify_plan(plan)
        altered = deepcopy(self.science)
        altered["frozen_method"]["primary_sign_threshold"] = 9
        with self.assertRaises(PermissionError):
            P.verify_plan(altered)

    def test_body_observed_scores_are_complete_and_population_aggregated(self):
        for g in range(3):
            results = P.reduce_generation(g, fixture_fitness(g))
            self.assertEqual(len(results), 16 if g == 0 else 32)
            self.assertEqual(set(x["original_lives"] for x in results.values()),
                             {144})
            for x in results.values():
                self.assertEqual(x["survivors_at_horizon"], 0)
                self.assertEqual(x["horizon_survival_fraction"], 0.0)
        missing = fixture_fitness(2)
        del missing[2, "selected", 0]
        with self.assertRaises(ValueError):
            P.reduce_generation(2, missing)
        corrupt = fixture_fitness(2)
        corrupt[2, "selected", 0] = (7, 2401)
        with self.assertRaises(ValueError):
            P.reduce_generation(2, corrupt)

    def test_g2_advantage_13_pops_passes_but_12_does_not(self):
        for positives, expected in (
                (13, "PERSISTENCE_G2_ADVANTAGE_REPRODUCIBLE_F0"),
                (12, "PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0"),
                (16, "PERSISTENCE_G2_ADVANTAGE_REPRODUCIBLE_F0"),
                (0, "PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0")):
            with self.subTest(positives=positives):
                score = {
                    g: P.reduce_generation(g, fixture_fitness(g, positives))
                    for g in range(3)}
                result = P.persistence_analysis(score)
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["primary"]["positive"], positives)
                self.assertEqual(result["primary"]["negative"], 16-positives)
                self.assertEqual(len(result["generation_population_originals"]), 16)
                self.assertEqual(result["secondary"]["G1_positive_population_count"], 16)
                self.assertEqual(result["primary"]["one_sided_exact_tail_for_13"],
                                 {"numerator": 697, "denominator": 65536})
                self.assertFalse(result["design"]["G0_to_G1_to_G2_raw_steps_causal_comparison"])

    def test_zero_primary_signs_and_source_exact_no_retry(self):
        fixture = {g: P.reduce_generation(g, fixture_fitness(g))
                   for g in range(3)}
        for p in range(4):
            for s in range(24):
                fixture[2][p, "selected"]["total_steps"] = 144*100
                fixture[2][p, "selected"]["mean_steps"] = 100.0
        result = P.persistence_analysis(fixture)
        self.assertEqual(result["primary"]["positive"], 12)
        self.assertEqual(result["primary"]["zero"], 4)
        self.assertFalse(result["primary"]["threshold_met"])
        with self.assertRaises(PermissionError):
            P.run_full(self.science, self.archive,
                       "0"*64)
        with patch.object(P.G0, "_verify_checkout",
                          side_effect=PermissionError("source SHA differs")):
            with self.assertRaises(PermissionError):
                P.run_full(self.science, self.archive,
                           self.science["allocation_sha256"])
        self.assertFalse(Path(self.archive).exists())
        with self.assertRaises(PermissionError):
            P.run_full(self.science, self.archive+"-retry",
                       self.science["allocation_sha256"])
        self.assertFalse(Path(self.archive).exists())

    def test_end_to_end_ancestry_schedule_is_predeclared_without_birth(self):
        from i3.modules.genome import generation_zero
        genes = P.S.founder_genomes(self.tech)
        self.assertEqual(len(genes), 384)
        self.assertEqual(len(P.S.generation_cases(self.tech, 0, genes)), 2304)
        fake_fitness = {(p, "shared", s): (0, 600) for p in range(16)
                        for s in range(24)}
        children, parents = P.S.choose_descendants(
            self.tech, 1, genes, fake_fitness, "b"*64)
        self.assertEqual(len(children), 768)
        self.assertEqual(len(parents), 768)
        self.assertEqual(len(P.S.generation_cases(self.tech, 1, children)), 4608)
        self.assertEqual({r["arm"] for r in parents}, set(P.S.ARMS))


if __name__ == "__main__":
    unittest.main()
