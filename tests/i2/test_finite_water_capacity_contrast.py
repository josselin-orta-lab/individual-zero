"""Check paid water use and publish unselected outcomes, not a success script."""
import json
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.finite_water_capacity_contrast import capacity_contrast, POLICIES, WORLDS, CAPACITIES, HORIZON
from i2.runtime.isolated_prototype import DRINK

class FiniteWaterCapacityContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=capacity_contrast()

    def test_all_stock_counts_paid_and_audited(self):
        data=self.report
        self.assertEqual(data["general_survival_benefit"],"NOT_ESTABLISHED")
        for world in WORLDS:
            for stock in CAPACITIES:
                arms=data["worlds"][world][str(stock)]
                self.assertEqual(tuple(arms),tuple(row[0] for row in POLICIES))
                for name,arm in arms.items():
                    with self.subTest(world=world,stock=stock,policy=name):
                        consumed=sum(x==DRINK for x in arm["actions"])
                        self.assertLessEqual(consumed,stock)
                        self.assertEqual(arm["water_remaining"],stock-consumed)
                        self.assertEqual(arm["paid_uc"],arm["endpoint"]["actual_uc_spent"])
                        self.assertEqual(len(arm["actions"]),arm["endpoint"]["paid_decisions"])
                        self.assertLessEqual(arm["endpoint"]["ending_physical_tick"],HORIZON)
                        self.assertFalse(arm["m11_authenticated"])
                        if consumed==stock:
                            last=max(i for i,a in enumerate(arm["actions"]) if a==DRINK)
                            self.assertNotIn(True,arm["water_visible"][last+1:])

    def test_report_different_and_identical_outcomes_without_selection(self):
        print("I2_FINITE_WATER_CAPACITY_CONTRAST_V1="+json.dumps(
            self.report,sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    unittest.main()
