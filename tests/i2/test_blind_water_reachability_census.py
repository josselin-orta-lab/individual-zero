"""No-script 64-life blind-water reachability census integrity."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.blind_water_reachability_census import census,ENERGIES,CAPACITIES,POLICIES,WORLDS
from i2.runtime.isolated_prototype import DRINK

class BlindWaterCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel=census()
    def test_all_paid_finite_stocks_and_terminal_controls_preserved(self):
        p=self.panel
        self.assertEqual(len(p["result"]),len(ENERGIES)*len(CAPACITIES)*len(POLICIES)*len(WORLDS))
        self.assertEqual(p["general_survival"],"NOT_ESTABLISHED")
        self.assertEqual(p["natural_learning"],"NOT_ESTABLISHED")
        for row in p["result"]:
            with self.subTest(world=row["world"],energy=row["energy"],stock=row["stock"],policy=row["policy"]):
                self.assertEqual(sum(x==DRINK for x in row["actions"]),row["water_uses"])
                self.assertLessEqual(row["water_uses"],row["stock"])
                self.assertEqual(row["exhausted"],row["water_uses"]==row["stock"])
                self.assertLessEqual(row["paid_uc"],60)
                self.assertFalse(row["m11"])
                if row["death_tick"] is not None:
                    self.assertFalse(row["censored"])
    def test_emit_all_outcomes_without_filtering(self):
        print("I2_BLIND_WATER_CENSUS_V1="+json.dumps(self.panel,sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    unittest.main()
