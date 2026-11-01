"""Same-world physical deadline falsifier; no planner-selected motor action."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.two_step_survival_plan import assess_collect_then_eat
from i2.runtime.isolated_prototype import IsolatedI2, SCENARIOS, COLLECT, EAT, PrototypeRefusal


class TwoStepDeadlineTests(unittest.TestCase):
    def start(self, energy):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        return IsolatedI2.create(Path(folder.name) / "life.sqlite",
            learning=False, impulses=SCENARIOS["stable"],
            initial_energy=energy, last_resort_exploration=True)

    def proposal(self, life, ticks):
        _meta, state, rows = life._read()
        claim = life._claim(state["revision"], state["energy"], state["inventory"],
            state["resources"], rows, physical_ticks=state["tick_count"])
        return assess_collect_then_eat(
            claim=claim, energy=state["energy"], inventory=state["inventory"],
            resources=state["resources"], ticks_before_second_action=ticks)

    def test_deadline_blocks_second_action_even_when_food_is_favorable(self):
        life = self.start(4)
        self.assertEqual(self.proposal(life, 2).status, "DEPLETED_BEFORE_SECOND_STEP")
        first = life.step()
        self.assertEqual(first.chosen, COLLECT)
        self.assertEqual(first.energy, 2)
        life.advance_physics()
        terminal = life.advance_physics()
        self.assertTrue(terminal["terminal"])
        self.assertTrue(life.audit()["terminal"])
        self.assertEqual(life.audit()["revision"], 1)
        with self.assertRaises(PrototypeRefusal):
            life.step()

    def test_immediate_second_action_still_depends_on_food_consequence(self):
        life = self.start(5)
        projection = self.proposal(life, 0)
        self.assertEqual(projection.status, "PHYSICALLY_SEQUENCEABLE_OUTCOME_UNKNOWN")
        first = life.step()
        self.assertEqual(first.chosen, COLLECT)
        second = life.step()
        self.assertEqual(second.chosen, EAT)
        self.assertEqual(second.energy, 7)
        self.assertEqual(life.audit()["actual_uc_spent"], 9)
        self.assertFalse(life.audit()["m11_authenticated"])


if __name__ == "__main__":
    unittest.main()
