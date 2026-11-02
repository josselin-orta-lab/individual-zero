"""Pure I2 parity-contract checks. No engine, I1 import or science cohort."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body, transition, COSTS
from i2.modules.native_birth_temperament import (
    BirthTemperament, CHANNELS, declared_temperament, birth_temperament,
)


class NativeBodyAndTemperamentContract(unittest.TestCase):
    def test_complete_finite_body_and_natural_v4_energy_costs(self):
        self.assertEqual(len(COSTS), 8)
        body = Body(50.0, 40.0, 40.0, 90.0)
        collected = transition(body, "collecter")
        self.assertEqual(collected.body, Body(49.0, 39.8, 39.6, 90.0))
        self.assertFalse(collected.terminal)
        ate = transition(body, "manger", berry_food_gain=10.0)
        self.assertEqual(ate.body, Body(49.5, 49.8, 39.6, 90.0))
        drank = transition(body, "boire", drink_water_gain=40.0)
        self.assertEqual(drank.body, Body(49.5, 39.8, 79.6, 90.0))

    def test_sleep_has_real_substrate_cost_and_no_water_calories(self):
        body = Body(50.0, 10.0, 50.0, 90.0)
        asleep = transition(body, "dormir")
        self.assertEqual(asleep.body, Body(53.0, 9.63, 49.6, 90.2))
        dry = transition(Body(50.0, 10.0, 0.2, 90.0), "dormir")
        self.assertEqual(dry.body.energy, 50.0)
        self.assertEqual(dry.body.integrity, 90.0)

    def test_terminal_reserves_and_no_future_payoff(self):
        x = transition(Body(20.0, 0.1, 30.0, 90.0), "attendre")
        self.assertTrue(x.terminal)
        self.assertIn("zero_food", x.reasons)
        y = transition(Body(20.0, 30.0, 0.2, 90.0), "boire", drink_water_gain=30.0)
        self.assertFalse(y.terminal)
        with self.assertRaises(ValueError):
            transition(Body(20.0, 30.0, 30.0, 90.0), "collecter", berry_food_gain=10.0)
        with self.assertRaises(ValueError):
            Body(float("nan"), 20.0, 30.0, 40.0)

    def test_five_immutable_traits_can_be_explicitly_paired(self):
        source = "research-pair:001"
        a = birth_temperament(individual_ref="i2:life:a", paired_research_source=source)
        b = birth_temperament(individual_ref="i2:life:b", paired_research_source=source)
        self.assertEqual(a, b)
        self.assertEqual(set(a.as_dict()), set(CHANNELS))
        self.assertEqual(declared_temperament(a.as_dict()), a)
        self.assertNotEqual(birth_temperament(individual_ref="i2:life:a"),
                            birth_temperament(individual_ref="i2:life:b"))
        with self.assertRaises(ValueError):
            declared_temperament({"exploration": 0.0})
        with self.assertRaises(ValueError):
            birth_temperament(individual_ref="i1:foreign")
        with self.assertRaises(ValueError):
            BirthTemperament(0, 0, 0, 0, float("inf"))


if __name__ == "__main__":
    unittest.main()
