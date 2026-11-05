"""Integrated behavior: personally lived water benefit changes the next paid action.

Two independent fresh-genesis research lives share physical world, first
choice and UC. The sole difference is admitting prior chosen outcomes to
valuation. The researcher does not select either motor action.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, DRINK, COLLECT


class BlindWaterPaidChoiceTests(unittest.TestCase):
    def test_lived_benefit_changes_second_paid_choice(self):
        with tempfile.TemporaryDirectory() as root:
            arms = {}
            for learning in (False, True):
                life = IsolatedI2.create(
                    Path(root) / f"{learning}.sqlite",
                    learning=learning, impulses=SCENARIOS["adverse"],
                    initial_energy=4, initial_uc=60, resources=8,
                    restorative_water_study=True, water_effect_blind=True,
                    finite_water_capacity=2, deadline_aware=True,
                    last_resort_exploration=True,
                )
                first = life.step()
                self.assertEqual(first.chosen, DRINK)
                self.assertEqual(first.energy, 8)
                second = life.step()
                decisions = life.decision_evidence()
                arms[learning] = (first, second, decisions, life.audit())
            fixed_first, fixed_second, fixed_rows, fixed_audit = arms[False]
            learned_first, learned_second, learned_rows, learned_audit = arms[True]
            for field in ("before_energy", "visible", "uc_spent",
                          "subjective_outcomes_available", "uc_before"):
                self.assertEqual(fixed_rows[1][field], learned_rows[1][field],
                                 field)
            self.assertEqual(fixed_rows[1]["before_energy"], 8)
            self.assertEqual(fixed_rows[1]["candidate_scores"][DRINK], 1)
            self.assertEqual(learned_rows[1]["candidate_scores"][DRINK], 9)
            self.assertEqual(fixed_second.chosen, COLLECT)
            self.assertEqual(learned_second.chosen, DRINK)
            self.assertTrue(fixed_rows[1]["internal_admission"])
            self.assertTrue(learned_rows[1]["internal_admission"])
            self.assertFalse(fixed_rows[1]["last_resort_priority_applied"])
            self.assertFalse(learned_rows[1]["last_resort_priority_applied"])
            self.assertEqual(fixed_first.actual_uc_spent, learned_first.actual_uc_spent)
            self.assertEqual(fixed_second.actual_uc_spent, learned_second.actual_uc_spent)
            self.assertEqual(fixed_audit["actual_uc_spent"], learned_audit["actual_uc_spent"])
            self.assertFalse(fixed_audit["m11_authenticated"])
            self.assertFalse(learned_audit["m11_authenticated"])
            self.assertEqual(learned_audit["science"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
