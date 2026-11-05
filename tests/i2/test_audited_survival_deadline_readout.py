"""Bound audited deadline observation to the existing owner readout."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, COLLECT

class AuditedDeadlineReadout(unittest.TestCase):
    def subject(self, energy):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return IsolatedI2.create(
            Path(tmp.name) / "life.sqlite", learning=True,
            impulses=SCENARIOS["stable"], initial_energy=energy,
            last_resort_exploration=True)

    def test_low_energy_collect_is_actually_too_late_at_normal_cadence(self):
        life = self.subject(4)
        first = life.step()
        self.assertEqual(first.chosen, COLLECT)
        projection = life.decision_evidence()[0]["two_step_collect_eat"]
        self.assertEqual(projection["ticks_before_second_action"], 2)
        self.assertEqual(projection["status"], "DEPLETED_BEFORE_SECOND_STEP")
        self.assertIsNone(projection["pre_food_energy"])
        self.assertEqual(projection["food_outcome"], "UNKNOWN")
        self.assertTrue(projection["researcher_only"])
        self.assertEqual(projection["motor_authority"], "NONE")
        self.assertEqual(life.audit()["revision"], 1)

    def test_adequate_energy_is_not_claimed_as_guaranteed_survival(self):
        life = self.subject(10)
        life.step()
        projection = life.decision_evidence()[0]["two_step_collect_eat"]
        self.assertEqual(projection["status"],
                         "PHYSICALLY_SEQUENCEABLE_OUTCOME_UNKNOWN")
        self.assertEqual(projection["pre_food_energy"], 6)
        self.assertEqual(projection["food_outcome"], "UNKNOWN")

if __name__ == "__main__":
    unittest.main()
