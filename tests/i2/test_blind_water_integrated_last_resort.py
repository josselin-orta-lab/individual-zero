"""Bounded blind-water sequence: learned resource, exhaustion, risky fallback.

No action is forced. Two hidden food regimes and a no-learning comparator
retain the same physical laws and fresh, paid single-owner identities.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, DRINK, EAT


class BlindWaterIntegratedLastResort(unittest.TestCase):
    def test_source_bound_recovery_then_exhaustion_is_not_future_knowledge(self):
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
            a, aa = worlds["adverse"]
            b, ba = worlds["restoration"]
            self.assertGreaterEqual(len(a), 9)
            self.assertGreaterEqual(len(b), 9)
            for index in range(9):
                for field in ("visible", "chosen", "before_energy",
                              "before_inventory", "before_resources",
                              "subjective_outcomes_available",
                              "candidate_scores", "uc_before",
                              "uc_spent", "last_resort_priority_applied"):
                    self.assertEqual(a[index][field], b[index][field],
                                     (index, field))
            for rows, state in worlds.values():
                self.assertEqual(rows[7]["chosen"], DRINK)
                self.assertNotIn(DRINK, rows[8]["visible"])
                self.assertEqual(rows[8]["chosen"], EAT)
                self.assertTrue(rows[8]["last_resort_priority_applied"])
                self.assertTrue(rows[8]["internal_admission"])
                self.assertEqual(state["water_remaining"], 0)
                self.assertFalse(state["m11_authenticated"])
            self.assertTrue(aa["terminal"])
            self.assertFalse(ba["terminal"])
            self.assertEqual(aa["physical_ticks"], 18)
            self.assertEqual(ba["physical_ticks"], 20)


if __name__ == "__main__":
    unittest.main()
