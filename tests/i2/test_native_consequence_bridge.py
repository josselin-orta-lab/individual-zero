"""Native I2 admitted-effect-to-body-to-need chain (research only)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_consequence_bridge import admitted_consequence


class NativeConsequenceBridgeTests(unittest.TestCase):
    def setUp(self):
        self.body = Body(50, 40, 40, 90)
        self.trait = BirthTemperament(0, 0.5, 0, 0, 0)

    def test_admitted_consumption_changes_food_and_endogenous_pressure(self):
        result = admitted_consequence(
            before=self.body, temperament=self.trait, action="manger",
            admitted=True, applied=True, berry_food_gain=20)
        self.assertEqual(result.after.food, 59.8)
        self.assertLess(result.needs_after.pressures["food"],
                        result.needs_before.pressures["food"])
        self.assertEqual(result.before, self.body)
        self.assertFalse(result.terminal)
        self.assertEqual(result.motor_authority, "NONE")
        self.assertFalse(result.m11_authenticated)

    def test_drink_restores_hydration_but_not_calories(self):
        result = admitted_consequence(
            before=self.body, temperament=self.trait, action="boire",
            admitted=True, applied=True, drink_water_gain=20)
        self.assertEqual(result.after.water, 59.6)
        self.assertEqual(result.after.energy, 49.5)
        self.assertLess(result.needs_after.pressures["water"],
                        result.needs_before.pressures["water"])

    def test_fatal_deprivation_blocks_reuse(self):
        before = Body(20, 0.1, 50, 90)
        result = admitted_consequence(
            before=before, temperament=self.trait,
            action="collecter", admitted=True, applied=True)
        self.assertTrue(result.terminal)
        self.assertIn("zero_food", result.lethal_reasons)
        with self.assertRaises(ValueError):
            admitted_consequence(
                before=result.after, temperament=self.trait,
                action="manger", admitted=True, applied=True,
                berry_food_gain=20)

    def test_no_unadmitted_or_counterfactual_effect(self):
        for admission, applied in ((False, True), (True, False),
                                   (False, False)):
            with self.subTest(admission=admission, applied=applied):
                with self.assertRaises(ValueError):
                    admitted_consequence(
                        before=self.body, temperament=self.trait,
                        action="manger", admitted=admission,
                        applied=applied, berry_food_gain=20)
        with self.assertRaises(ValueError):
            admitted_consequence(
                before=self.body, temperament=self.trait,
                action="collecter", admitted=True, applied=True,
                berry_food_gain=20)


if __name__ == "__main__":
    unittest.main()
