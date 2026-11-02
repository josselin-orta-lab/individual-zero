"""Pre-choice invisibility under two differently timed hidden reversals.

Two fresh paid lives experience identical food until the same ninth
decision. Reversal can happen before or after that decision, but the
individual cannot distinguish the futures from its verified past.
"""
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT


class HiddenReversalIdentifiability(unittest.TestCase):
    def test_future_payoff_change_does_not_leak_into_predecision_scores(self):
        with tempfile.TemporaryDirectory() as root:
            arms = {}
            for label, trailing in (("still_restored", (6, -8)),
                                    ("already_retoxified", (-8, -8))):
                life = IsolatedI2.create(
                    Path(root) / (label + ".sqlite"), learning=True,
                    impulses=SCENARIOS["restoration"] + trailing,
                    initial_energy=40, initial_uc=60, resources=8,
                    last_resort_exploration=True,
                    extended_postcontact_study=True)
                life.run_world(ticks=18)
                arms[label] = (life.decision_evidence(), life.audit())
            safe, sa = arms["still_restored"]
            changed, ca = arms["already_retoxified"]
            self.assertEqual(len(safe), 9)
            self.assertEqual(len(changed), 9)
            for idx in range(9):
                a, c = safe[idx], changed[idx]
                for key in ("visible", "chosen", "before_energy",
                            "before_inventory", "before_resources",
                            "physical_ticks_before", "uc_before", "uc_spent",
                            "candidate_scores", "subjective_outcomes_available",
                            "last_resort_priority_applied"):
                    self.assertEqual(a[key], c[key], (idx, key))
            self.assertEqual(safe[8]["chosen"], EAT)
            self.assertEqual(changed[8]["chosen"], EAT)
            self.assertEqual(safe[8]["candidate_scores"][EAT], 9)
            self.assertFalse(sa["terminal"])
            self.assertTrue(ca["terminal"])
            self.assertEqual(ca["physical_ticks"], 18)
            self.assertEqual(sa["actual_uc_spent"], ca["actual_uc_spent"])
            self.assertFalse(sa["m11_authenticated"])
            self.assertFalse(ca["m11_authenticated"])


if __name__ == "__main__":
    unittest.main()
