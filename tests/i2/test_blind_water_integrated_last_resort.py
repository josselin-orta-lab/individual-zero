"""Blind water / hidden food: preserve the unforced integrated outcome.

This is a deliberately negative-capable behavioral observation, not a
forced rescue script or a survival-positive assertion. A previously
untried water effect must never be presented as known restorative.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    BLIND_WATER_EVIDENCE, RESTORATIVE_WATER_EVIDENCE,
    DRINK, EAT, IsolatedI2, SCENARIOS,
)


class BlindWaterIntegratedLastResort(unittest.TestCase):
    def test_identical_private_history_until_hidden_consequence_differs(self):
        with tempfile.TemporaryDirectory() as root:
            worlds = {}
            for world in ("adverse", "restoration"):
                life = IsolatedI2.create(
                    Path(root) / (world + ".sqlite"),
                    learning=True,
                    impulses=SCENARIOS[world] + (SCENARIOS[world][-1],) * 2,
                    extended_postcontact_study=True,
                    initial_energy=40, initial_uc=60, resources=8,
                    restorative_water_study=True, water_effect_blind=True,
                    finite_water_capacity=1,
                    last_resort_exploration=True, deadline_aware=True)
                life.run_world(ticks=20)
                worlds[world] = (life.decision_evidence(), life.audit())
            adverse, adverse_audit = worlds["adverse"]
            restored, restored_audit = worlds["restoration"]
            self.assertTrue(adverse)
            self.assertTrue(restored)
            for rows, audit in worlds.values():
                self.assertFalse(audit["m11_authenticated"])
                self.assertEqual(audit["science"], "NOT_ESTABLISHED")
                self.assertGreater(audit["actual_uc_spent"], 0)
                self.assertIn(DRINK, rows[0]["visible"])
                self.assertLessEqual(
                    sum(row["chosen"] == DRINK for row in rows), 1)
                # Report first-person chosen history, not hidden food phase.
                for index, row in enumerate(rows):
                    observed_food = [event for event in row[
                        "subjective_outcomes_available"] if event["action"] == EAT]
                    if index == 0:
                        self.assertEqual(observed_food, [])
                    self.assertGreaterEqual(row["uc_spent"], 0)
            # Hidden berry timing cannot change a decision while the
            # individual's actual body and observed history still match.
            for left, right in zip(adverse, restored):
                prechoice = ("visible", "before_energy", "before_inventory",
                             "before_resources", "physical_ticks_before",
                             "subjective_outcomes_available", "uc_before")
                if any(left[key] != right[key] for key in prechoice):
                    break
                for key in ("chosen", "candidate_scores",
                            "last_resort_priority_applied", "uc_spent"):
                    self.assertEqual(left[key], right[key], key)
            self.assertLessEqual(adverse_audit["water_remaining"], 1)
            self.assertLessEqual(restored_audit["water_remaining"], 1)


if __name__ == "__main__":
    unittest.main()
