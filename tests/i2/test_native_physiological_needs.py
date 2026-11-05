"""Current-body needs and born trait tests; no motors or I1 imports."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_physiological_needs import assess_needs


class NativeNeedsTests(unittest.TestCase):
    def test_four_channels_make_real_current_body_pressures(self):
        t = BirthTemperament(0, 0, 0, 0, 0)
        result = assess_needs(Body(80, 10, 70, 100), t)
        self.assertEqual(result.leading_need, "food")
        self.assertIn("food", result.immediate_danger)
        self.assertEqual(result.pressures["energy"], 0)
        self.assertEqual(result.motor_authority, "NONE")

    def test_threat_trait_changes_priority_but_not_physics(self):
        b = Body(80, 70, 70, 50)
        lower = assess_needs(b, BirthTemperament(0, -1, 0, 0, 0))
        higher = assess_needs(b, BirthTemperament(0, 1, 0, 0, 0))
        self.assertLess(lower.pressures["integrity"], higher.pressures["integrity"])
        self.assertEqual(lower.deficits, higher.deficits)
        self.assertEqual(b.integrity, 50)

    def test_no_danger_is_not_false_survival(self):
        t = BirthTemperament(0, 0, 0, 0, 0)
        result = assess_needs(Body(100, 100, 100, 100), t)
        self.assertIsNone(result.leading_need)
        self.assertEqual(result.immediate_danger, ())

    def test_invalid_setpoints_refused(self):
        with self.assertRaises(ValueError):
            assess_needs(Body(50, 50, 50, 50),
                         BirthTemperament(0, 0, 0, 0, 0),
                         setpoints={"energy": 100})

if __name__ == "__main__":
    unittest.main()
