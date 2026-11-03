"""Born-bounded longitudinal I2 life without rebirth or cognitive shortcuts.

This is a lifecycle engineering gate under #906, not an experiment proving
natural learning. Existing eight-tick cohorts keep the same default horizon.
"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import (
    HORIZON, MAX_BORN_STEPS, NativePaidI2, NativeRefusal,
)


class NativeLongLivedBirthTests(unittest.TestCase):
    BIRTH = Body(85, 90, 90, 100)
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)

    def test_long_life_remains_one_individual_after_original_horizon(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "long-life.sqlite"
            individual = NativePaidI2.create(
                path, body=self.BIRTH, temperament=self.TRAITS,
                learning=True, sleep_consolidation=True,
                max_steps=20, uc=1000, food_stock=0, water_stock=0,
                discovered_water_gain=0)
            born = individual.audit()
            self.assertEqual(born["revision"], 0)
            self.assertEqual(born["max_steps"], 20)
            self.assertEqual(born["body"], self.BIRTH.as_dict())
            self.assertEqual(born["temperament"], self.TRAITS.as_dict())
            balances = [born["remaining_uc"]]
            for i in range(20):
                actual = individual.step()
                self.assertEqual(actual["revision"], i + 1)
                self.assertFalse(actual["terminal"])
                self.assertEqual(actual["max_steps"], 20)
                self.assertEqual(actual["temperament"], born["temperament"])
                self.assertLessEqual(actual["remaining_uc"], balances[-1])
                balances.append(actual["remaining_uc"])
                if i in (7, 15, 19):
                    self.assertEqual(NativePaidI2.inspect(path).audit(), actual)
            self.assertLess(balances[-1], balances[0])
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute(
                    "SELECT COUNT(*) FROM events").fetchone()[0], 20)
                self.assertEqual(db.execute(
                    "SELECT COUNT(*) FROM native_physical_events").fetchone()[0], 20)
                self.assertEqual(db.execute(
                    "SELECT max_steps FROM native_genesis").fetchone()[0], 20)
                self.assertEqual(db.execute(
                    "SELECT COUNT(*) FROM native_genesis").fetchone()[0], 1)
            with self.assertRaises(NativeRefusal):
                individual.step()
            # A cold reader cannot acquire new motor authority after a life.
            with self.assertRaises(NativeRefusal):
                NativePaidI2.inspect(path).step()

    def test_lifetime_limit_is_born_immutable_and_small_cohorts_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            for invalid in (True, 0, -1, MAX_BORN_STEPS + 1, 3.0, "20"):
                with self.subTest(invalid=invalid):
                    with self.assertRaises(NativeRefusal):
                        NativePaidI2.create(
                            Path(folder) / ("bad-" + str(invalid) + ".sqlite"),
                            body=self.BIRTH, temperament=self.TRAITS,
                            max_steps=invalid)
            path = Path(folder) / "default.sqlite"
            individual = NativePaidI2.create(
                path, body=self.BIRTH, temperament=self.TRAITS,
                food_stock=0, water_stock=0, uc=500)
            self.assertEqual(individual.audit()["max_steps"], HORIZON)
            with sqlite3.connect(path) as db:
                db.execute("UPDATE native_genesis SET max_steps=20 WHERE id=1")
            with self.assertRaises(NativeRefusal):
                individual.audit()


if __name__ == "__main__":
    unittest.main()
