"""Adversarial contracts for the predeclared 12-block A1-C decision."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
from i1_eco_a1c_statistics import assess_a1c, ROLES, SEEDS


def table(v=0.06, exposed=True):
    return [
        {"role": role, "seed": seed,
         "difference": v + (seed - 106.5) * 0.0001,
         "mechanism_exposed": exposed}
        for role in ROLES for seed in SEEDS
    ]


class FrozenConfirmatoryCriterion(unittest.TestCase):
    def test_strong_consistent_effect_requires_review_not_general_L3(self):
        result = assess_a1c(table())
        self.assertEqual(result["targeted_status"],
                         "CONFIRMATORY_TARGETED_SIGNAL_PENDING_REVIEW")
        self.assertEqual(result["general_L3"], "NOT_ESTABLISHED")
        self.assertEqual(result["independent_temperament_blocks"], 12)
        self.assertEqual(result["paired_comparisons"], 24)
        self.assertLessEqual(result["exact_one_sided_block_signflip_p"], 0.025)

    def test_negative_or_tiny_effect_is_not_declared_learning(self):
        for effect in (0.0, -0.06, 0.005):
            with self.subTest(effect=effect):
                self.assertEqual(assess_a1c(table(effect))["targeted_status"], "NO_GO")

    def test_no_competitive_td_exposure_blocks_go(self):
        self.assertEqual(assess_a1c(table(exposed=False))["targeted_status"],
                         "NOT_EXPOSED")

    def test_effect_must_be_positive_in_both_roles(self):
        pairs = table()
        for row in pairs:
            if row["role"] == "reversed":
                row["difference"] = -0.01
        self.assertEqual(assess_a1c(pairs)["targeted_status"], "NO_GO")

    def test_malformed_and_missing_data_never_yield_valid_conclusion(self):
        a = table()
        for malformed in (a[:-1], a + [a[0]], [{**row, "difference": float("nan")}
                                             if i == 0 else row
                                             for i, row in enumerate(a)],
                          [{**row, "seed": 2} if i == 0 else row
                           for i, row in enumerate(a)],
                          [{**row, "mechanism_exposed": 1} if i == 0 else row
                           for i, row in enumerate(a)]):
            with self.assertRaises(ValueError):
                assess_a1c(malformed)


if __name__ == "__main__":
    unittest.main()
