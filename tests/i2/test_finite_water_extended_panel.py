"""Audit finite water stock across an independently declared longer horizon."""
import sys
import json
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.finite_water_extended_panel import run_extended_panel,STOCK,HORIZON,WORLDS,POLICIES

class FiniteWaterTwentyTickTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=run_extended_panel()

    def test_stock_and_censoring_are_accounted_without_forced_recontact(self):
        report=self.data
        self.assertEqual(report["general_survival_benefit"],"NOT_ESTABLISHED")
        self.assertEqual(report["natural_learning"],"NOT_ESTABLISHED")
        self.assertEqual(set(report["worlds"]),set(WORLDS))
        for world, arms in report["worlds"].items():
            self.assertEqual(tuple(arms),tuple(x[0] for x in POLICIES))
            for label, arm in arms.items():
                with self.subTest(world=world,policy=label):
                    endpoint=arm["endpoint"]
                    chosen=arm["actions"]
                    consumed=sum(a=="affordance:drink:water" for a in chosen)
                    self.assertLessEqual(consumed,STOCK)
                    self.assertEqual(arm["water_remaining"],STOCK-consumed)
                    self.assertEqual(arm["paid_uc"],endpoint["actual_uc_spent"])
                    self.assertEqual(len(chosen),endpoint["paid_decisions"])
                    self.assertEqual(len(chosen),len(arm["water_visible"]))
                    self.assertFalse(arm["m11_authenticated"])
                    self.assertLessEqual(endpoint["ending_physical_tick"],HORIZON)
                    if consumed==STOCK:
                        last=max(i for i,a in enumerate(chosen)
                                 if a=="affordance:drink:water")
                        self.assertNotIn(True,arm["water_visible"][last+1:])
                    if endpoint["right_censored"]:
                        self.assertEqual(endpoint["ending_physical_tick"],HORIZON)
                        self.assertIsNone(endpoint["modeled_death_tick"])

    def test_report_actual_exhaustion_and_recontact_not_an_assumed_success(self):
        print("I2_FINITE_WATER_20_TICK_V1="+json.dumps(
            self.data,sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    unittest.main()
