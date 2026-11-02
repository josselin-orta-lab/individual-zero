"""Three fixed hidden-reversal timings, identical paid prechoice information.

Falsifies any implicit use of future food phase in I2's ninth decision.
The researcher compares schedules; subjects receive no change cue.
"""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, EAT


class ThreeWayHiddenReversalBoundary(unittest.TestCase):
    def test_three_hidden_timings_indistinguishable_at_ninth_choice(self):
        variants = {
            "never_before_horizon": (6, 6),
            "after_ninth_contact": (6, -8),
            "before_ninth_contact": (-8, -8),
        }
        with tempfile.TemporaryDirectory() as root:
            arms = {}
            for name, tail in variants.items():
                life = IsolatedI2.create(
                    Path(root) / (name + ".sqlite"),
                    learning=True, impulses=SCENARIOS["restoration"] + tail,
                    initial_energy=40, initial_uc=60, resources=8,
                    last_resort_exploration=True,
                    extended_postcontact_study=True)
                life.run_world(ticks=18)
                arms[name] = (life.decision_evidence(), life.audit())
        baseline, base_audit = arms["never_before_horizon"]
        self.assertEqual(len(baseline), 9)
        self.assertEqual(baseline[8]["chosen"], EAT)
        for name, (decisions, audit) in arms.items():
            with self.subTest(world=name):
                self.assertEqual(len(decisions), 9)
                for i in range(9):
                    for field in ("chosen", "visible", "before_energy",
                                  "before_inventory", "before_resources",
                                  "physical_ticks_before", "uc_before", "uc_spent",
                                  "candidate_scores", "subjective_outcomes_available",
                                  "last_resort_priority_applied"):
                        self.assertEqual(decisions[i][field], baseline[i][field])
                self.assertEqual(audit["actual_uc_spent"],
                                 base_audit["actual_uc_spent"])
                self.assertFalse(audit["m11_authenticated"])
        self.assertFalse(arms["never_before_horizon"][1]["terminal"])
        self.assertFalse(arms["after_ninth_contact"][1]["terminal"])
        self.assertTrue(arms["before_ninth_contact"][1]["terminal"])
        self.assertEqual(arms["before_ninth_contact"][1]["physical_ticks"], 18)
        self.assertEqual(arms["before_ninth_contact"][1]["energy"], 0)
        self.assertEqual(arms["never_before_horizon"][0][8]["energy_after"],
                         arms["after_ninth_contact"][0][8]["energy_after"])
        self.assertGreater(arms["after_ninth_contact"][0][8]["energy_after"],
                           arms["before_ninth_contact"][0][8]["energy_after"])


if __name__ == "__main__":
    unittest.main()
