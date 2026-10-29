"""Adversarial, engine-free tests for the prospective A2-R statistical gate."""
import math
import unittest
from i1_a2r_statistics import ROLES, SEEDS, assess_a2r


def cohort(canonical=0.50, candidate=0.45):
    return [
        {"role": role, "seed": seed,
         "canonical_score": canonical, "candidate_score": candidate,
         "canonical_dead": False, "candidate_dead": False,
         "cold_m11_verified": True, "reward_modes_verified": True,
         "pre_reward_prefix_equal": True, "reward_difference_observed": True,
         "mechanism_exposed": True}
        for role in ROLES for seed in SEEDS
    ]


class FrozenGateTests(unittest.TestCase):
    def test_positive_pending_review_not_general_l3(self):
        r = assess_a2r(cohort())
        self.assertEqual(r["targeted_status"], "CONFIRMATORY_TARGETED_SIGNAL_PENDING_REVIEW")
        self.assertEqual(r["general_L3"], "NOT_ESTABLISHED")
        self.assertEqual(r["paired_comparisons"], 48)
        self.assertEqual(r["independent_temperament_blocks"], 24)

    def test_worse_candidate_no_go(self):
        self.assertEqual(assess_a2r(cohort(candidate=0.51))["targeted_status"], "NO_GO")

    def test_one_role_harm_is_not_concealed_by_average(self):
        rows = cohort(candidate=0.40)
        for r in rows:
            if r["role"] == "native":
                r["candidate_score"] = 0.51
        self.assertEqual(assess_a2r(rows)["targeted_status"], "NO_GO")

    def test_no_mechanistic_exposure(self):
        rows = cohort()
        for r in rows:
            if r["seed"] in SEEDS[:8]:
                r["mechanism_exposed"] = False
        self.assertEqual(assess_a2r(rows)["targeted_status"], "NOT_EXPOSED")

    def test_death_gate_prevents_apparent_gain(self):
        rows = cohort()
        rows[0]["candidate_dead"] = True
        self.assertEqual(assess_a2r(rows)["targeted_status"], "NO_GO")

    def test_all_equal_scores_are_not_benefit(self):
        r = assess_a2r(cohort(candidate=0.50))
        self.assertEqual(r["targeted_status"], "NO_GO")
        self.assertEqual(r["exact_one_sided_block_sign_test_p"], 1.0)

    def test_reject_missing_duplicate_and_foreign_seeds(self):
        rows = cohort()
        for bad in (rows[:-1], rows[:-1]+[rows[0]], rows[:-1]+[dict(rows[-1], seed=9999)]):
            with self.assertRaises(ValueError):
                assess_a2r(bad)

    def test_reject_tampered_or_ambiguous_measurements(self):
        for field, value in (
            ("canonical_score", math.nan), ("candidate_score", 1.01),
            ("canonical_score", True), ("cold_m11_verified", False),
            ("pre_reward_prefix_equal", False), ("reward_modes_verified", False),
        ):
            rows = cohort()
            rows[0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                assess_a2r(rows)

    def test_reject_motor_claim_without_reward_divergence(self):
        rows = cohort()
        rows[0]["reward_difference_observed"] = False
        with self.assertRaises(ValueError):
            assess_a2r(rows)

    def test_conservative_ties_and_seed_blocks(self):
        rows = cohort()
        for r in rows:
            if r["seed"] in SEEDS[:9]:
                r["candidate_score"] = r["canonical_score"]
        result = assess_a2r(rows)
        self.assertEqual(result["independent_positive_blocks"], 15)
        self.assertGreater(result["exact_one_sided_block_sign_test_p"], 0.025)
        self.assertEqual(result["targeted_status"], "NO_GO")

if __name__ == "__main__":
    unittest.main()
