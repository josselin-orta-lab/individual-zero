"""Audited first divergent paid action: provenance, not posthoc success."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import world_demo

class FirstDivergentActionProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = world_demo("adverse", ticks=12, initial_energy=40,
                                last_resort_exploration=False)

    def test_both_paid_actions_share_first_person_past_and_motor_authority(self):
        report = self.report
        contrast = report["first_choice_contrast"]
        self.assertEqual(contrast["classification"],
                         "MATCHED_PRECHOICE_PROGRAMMED_VALUATION_CONTRAST")
        seq = contrast["first_divergence_seq"]
        self.assertIsNotNone(seq)
        arms = report["arms"]
        learned = arms["observed_chosen"]["decisions"][seq-1]
        fixed = arms["fixed"]["decisions"][seq-1]
        for key in ("before_energy", "before_inventory", "before_resources",
                    "visible", "physical_ticks_before", "uc_before",
                    "subjective_outcomes_available"):
            self.assertEqual(learned[key], fixed[key], key)
        for row in (learned, fixed):
            self.assertTrue(row["internal_admission"])
            self.assertGreater(row["uc_spent"], 0)
            self.assertEqual(row["survival_reflex"]["state"], "NO_PREEMPTION")
            self.assertFalse(row["last_resort_priority_applied"])
            self.assertFalse(row["deadline_infeasible_collect_suppressed"])
        self.assertNotEqual(learned["chosen"], fixed["chosen"])
        self.assertEqual(learned["chosen"], contrast["observational_action"])
        self.assertEqual(fixed["chosen"], contrast["fixed_action"])
        self.assertTrue(contrast["candidate_score_differences"])
        self.assertFalse(report["m11_authenticated"])

    def test_not_generalized_survival_claim(self):
        report=self.report
        self.assertEqual(report["scientific_verdict"], "NOT_ESTABLISHED")
        self.assertTrue(report["first_choice_contrast"][
            "not_a_natural_learning_or_survival_verdict"])

if __name__ == "__main__":
    unittest.main()
