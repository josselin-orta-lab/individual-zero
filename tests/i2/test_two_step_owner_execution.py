"""Observe, rather than assume, a two-step I2 survival plan in one paid owner.

No researcher-forced action, no hidden payoff injected into cognition, no
general planning claim. The pure projection is compared against actual paid
and committed decisions with delayed first-person evidence.
"""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.two_step_survival_plan import assess_collect_then_eat
from i2.runtime.isolated_prototype import IsolatedI2, COLLECT, EAT, SCENARIOS


class TwoStepOwnerExecution(unittest.TestCase):
    def run_case(self, scenario):
        with tempfile.TemporaryDirectory() as tmp:
            life = IsolatedI2.create(
                Path(tmp) / "individual.sqlite", learning=True,
                impulses=SCENARIOS[scenario], initial_energy=10,
                last_resort_exploration=True,
            )
            meta, state, rows = life._read()
            claim = life._claim(
                state["revision"], state["energy"], state["inventory"],
                state["resources"], rows, physical_ticks=state["tick_count"])
            projection = assess_collect_then_eat(
                claim=claim, energy=state["energy"],
                inventory=state["inventory"], resources=state["resources"])
            self.assertEqual(projection.status,
                             "PHYSICALLY_SEQUENCEABLE_OUTCOME_UNKNOWN")
            first = life.step()
            self.assertEqual(first.chosen, COLLECT)
            self.assertEqual(first.actual_uc_spent, 4)
            self.assertEqual(first.energy, 8)
            self.assertEqual(first.inventory, 1)
            second = life.step()
            self.assertEqual(second.chosen, EAT)
            self.assertEqual(second.actual_uc_spent, 5)
            self.assertIsNotNone(second.admission_ref)
            self.assertEqual(second.inventory, 0)
            decisions = life.decision_evidence()
            self.assertEqual(decisions[0]["subjective_outcomes_available"], ())
            self.assertTrue(any(x["action"] == COLLECT
                                for x in decisions[1]["subjective_outcomes_available"]))
            self.assertFalse(any(x["action"] == EAT
                                 for x in decisions[1]["subjective_outcomes_available"]))
            self.assertEqual(life.audit()["actual_uc_spent"], 9)
            self.assertFalse(life.audit()["m11_authenticated"])
            return second

    def test_favorable_world_actual_two_step_effect(self):
        second = self.run_case("stable")
        self.assertEqual(second.energy, 12)
        self.assertFalse(second.terminal)

    def test_harmful_world_actual_two_step_effect(self):
        second = self.run_case("adverse")
        self.assertEqual(second.energy, 0)
        self.assertTrue(second.terminal)


if __name__ == "__main__":
    unittest.main()
