"""Minimal adverse falsifier: a conservative survival veto can cause death.

These are mechanistic, one-life exploratory results, NOT an independent
ablation or proof of a general effect. Never force a motor action.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, COLLECT, EAT, _exogenous_food_impulse,
)


class SurvivalVetoCounterexample(unittest.TestCase):
    def test_favorable_food_cannot_rescue_low_energy_under_fixed_veto(self):
        with tempfile.TemporaryDirectory() as root:
            individual = IsolatedI2.create(
                Path(root) / "example.sqlite", learning=False,
                impulses=SCENARIOS["stable"], initial_energy=8,
            )
            collect = individual.step()
            self.assertEqual(collect.chosen, COLLECT)
            individual.advance_physics()
            individual.advance_physics()
            before = individual.audit()
            self.assertEqual((before["energy"], before["inventory"],
                              before["physical_ticks"]), (4, 1, 2))
            # Research-only analytic counterfactual, NOT an admitted action:
            # stable food would net -2 + 6, leaving 8 energy rather than 3.
            # The actual individual never sees this hypothetical information.
            hypothetical_eat_energy = min(
                100, before["energy"] - 2 +
                _exogenous_food_impulse(SCENARIOS["stable"],
                                        before["physical_ticks"]),
            )
            self.assertEqual(hypothetical_eat_energy, 8)
            refused = individual.step()
            self.assertIsNone(refused.chosen)
            self.assertEqual(refused.control_status, "VETOED")
            self.assertEqual(refused.energy, 3)
            self.assertEqual(refused.inventory, 1)
            self.assertEqual(refused.actual_uc_spent, 5)
            ticks = []
            while not individual.audit()["terminal"]:
                ticks.append(individual.advance_physics())
            audit = individual.audit()
            self.assertEqual(audit["physical_ticks"], 5)
            self.assertEqual(audit["energy"], 0)
            self.assertTrue(audit["terminal"])
            self.assertEqual(audit["revision"], 2)
            self.assertEqual(audit["actual_uc_spent"], 9)
            self.assertEqual(individual.decision_evidence()[1]
                             ["survival_reflex"]["state"], "CONSTRAIN")
            self.assertTrue(all(tick["external_motor_authority"] == "NONE"
                                for tick in ticks))
            # A counterfactual calculation is NOT an observed control arm.
            self.assertFalse(audit["m11_authenticated"])
            self.assertEqual(audit["science"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
