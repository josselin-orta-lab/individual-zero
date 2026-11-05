"""Record actual paid choices, depletion and unfavorable counterexamples."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.finite_water_panel import (
    finite_water_panel, WORLDS, POLICIES, WATER_CAPACITY, HORIZON,
)

class FiniteWaterPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=finite_water_panel()

    def test_all_arms_audited_no_fabricated_survival(self):
        report=self.report
        self.assertEqual(report["general_survival_benefit"],"NOT_ESTABLISHED")
        self.assertEqual(report["natural_learning"],"NOT_ESTABLISHED")
        self.assertEqual(set(report["worlds"]),set(WORLDS))
        for world,arms in report["worlds"].items():
            self.assertEqual(tuple(arms),tuple(p[0] for p in POLICIES))
            for name,arm in arms.items():
                with self.subTest(world=world,policy=name):
                    ep=arm["endpoint"]
                    self.assertEqual(ep["actual_uc_spent"],arm["paid_uc"])
                    self.assertEqual(ep["paid_decisions"],len(arm["actions"]))
                    self.assertEqual(len(arm["actions"]),len(arm["water_visible"]))
                    self.assertLessEqual(ep["ending_physical_tick"],HORIZON)
                    self.assertFalse(arm["m11_authenticated"])
                    count=sum(x=="affordance:drink:water" for x in arm["actions"])
                    self.assertLessEqual(count,WATER_CAPACITY)
                    self.assertEqual(arm["water_remaining"],WATER_CAPACITY-count)
                    if count==WATER_CAPACITY:
                        last=max(i for i,a in enumerate(arm["actions"])
                                 if a=="affordance:drink:water")
                        self.assertNotIn(True,arm["water_visible"][last+1:])

    def test_report_actual_positive_and_negative_outcomes(self):
        print("I2_FINITE_WATER_PANEL_V1="+json.dumps(
            self.report,sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    unittest.main()
