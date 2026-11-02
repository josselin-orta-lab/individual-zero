"""A paid nonemergency first-choice divergence with matched past experience.

This intentionally reuses the established neutral world, but separates a
focused behavioral test from the seven-case locked scientific publication.
No researcher-forced motor action, threshold tuning or hidden world oracle.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    COLLECT, DRINK, EAT, world_demo,
)


class NonurgentMemoryPaidChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = world_demo("neutral", ticks=12, initial_energy=40,
                                last_resort_exploration=False)

    def test_first_divergence_has_same_prechoice_history_and_no_reflex(self):
        contrast = self.result["first_choice_contrast"]
        self.assertEqual(contrast["classification"],
                         "MATCHED_PRECHOICE_PROGRAMMED_VALUATION_CONTRAST")
        self.assertTrue(contrast["matched_prechoice"])
        self.assertIsNotNone(contrast["first_divergence_seq"])
        index = contrast["first_divergence_seq"] - 1
        observed = self.result["arms"]["observed_chosen"]["decisions"][index]
        fixed = self.result["arms"]["fixed"]["decisions"][index]
        self.assertEqual(observed["physical_ticks_before"],
                         fixed["physical_ticks_before"])
        self.assertGreater(observed["before_energy"], 4)
        self.assertEqual(observed["survival_reflex"]["state"], "NO_PREEMPTION")
        self.assertEqual(fixed["survival_reflex"]["state"], "NO_PREEMPTION")
        for field in ("before_energy", "before_inventory", "before_resources",
                      "visible", "physical_ticks_before", "uc_before",
                      "subjective_outcomes_available"):
            self.assertEqual(observed[field], fixed[field], field)
        self.assertNotEqual(observed["chosen"], fixed["chosen"])
        self.assertEqual(observed["chosen"], contrast["observational_action"])
        self.assertEqual(fixed["chosen"], contrast["fixed_action"])
        self.assertFalse(observed["last_resort_priority_applied"])
        self.assertFalse(fixed["last_resort_priority_applied"])
        self.assertFalse(observed["deadline_infeasible_collect_suppressed"])
        self.assertFalse(fixed["deadline_infeasible_collect_suppressed"])
        self.assertGreater(observed["uc_spent"], 0)
        self.assertGreater(fixed["uc_spent"], 0)
        self.assertTrue(observed["internal_admission"])
        self.assertTrue(fixed["internal_admission"])
        self.assertTrue(contrast["candidate_score_differences"])

    def test_different_outcomes_after_divergence_are_not_causal_learning_proof(self):
        self.assertFalse(self.result["m11_authenticated"])
        self.assertEqual(self.result["scientific_verdict"], "NOT_ESTABLISHED")
        self.assertTrue(self.result["first_choice_contrast"][
            "not_a_natural_learning_or_survival_verdict"])
        for name in ("observed_chosen", "fixed"):
            arm = self.result["arms"][name]
            self.assertGreater(arm["endpoint"]["actual_uc_spent"], 0)
            self.assertEqual(arm["audit"]["science"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
