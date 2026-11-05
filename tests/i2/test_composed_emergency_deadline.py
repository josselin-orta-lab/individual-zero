"""One paid composition: futile long plan versus immediately offered food."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, COLLECT, EAT, DRINK,
)


class ComposedEmergencyDeadlineTests(unittest.TestCase):
    def life(self, energy, scenario="stable", *, combined=True):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        return IsolatedI2.create(
            Path(root.name) / "i2.sqlite", learning=True,
            impulses=SCENARIOS[scenario], initial_energy=energy,
            deadline_aware=combined, last_resort_exploration=True,
        )

    def test_without_inventory_futile_collect_loses_to_available_drink(self):
        life = self.life(4)
        first = life.step()
        self.assertEqual(first.chosen, DRINK)
        row = life.decision_evidence()[0]
        self.assertTrue(row["deadline_infeasible_collect_suppressed"])
        self.assertFalse(row["last_resort_priority_applied"])
        self.assertEqual(first.actual_uc_spent, 4)
        self.assertEqual(row["candidate_scores"][COLLECT], 0)

    def test_with_inventory_emergency_food_is_attempted_in_stable_world(self):
        life = self.life(8)
        self.assertEqual(life.step().chosen, COLLECT)
        life.advance_physics()
        life.advance_physics()
        second = life.step()
        self.assertEqual(second.chosen, EAT)
        self.assertEqual(second.energy, 8)
        row = life.decision_evidence()[1]
        self.assertTrue(row["deadline_infeasible_collect_suppressed"])
        # Food already wins after the physically impossible collect is
        # suppressed, so no extra synthetic priority is manufactured.
        self.assertFalse(row["last_resort_priority_applied"])
        self.assertEqual(second.actual_uc_spent, 5)
        self.assertEqual(row["candidate_scores"][COLLECT], 0)

    def test_same_world_state_adverse_food_retains_fatal_risk(self):
        life = self.life(8, "adverse")
        self.assertEqual(life.step().chosen, COLLECT)
        life.advance_physics()
        life.advance_physics()
        second = life.step()
        self.assertEqual(second.chosen, EAT)
        self.assertTrue(second.terminal)
        self.assertEqual(second.energy, 0)
        self.assertFalse(life.audit()["m11_authenticated"])

    def test_normal_energy_does_not_apply_either_priority(self):
        life = self.life(40)
        self.assertEqual(life.step().chosen, COLLECT)
        row = life.decision_evidence()[0]
        self.assertFalse(row["deadline_infeasible_collect_suppressed"])
        self.assertFalse(row["last_resort_priority_applied"])


if __name__ == "__main__":
    unittest.main()
