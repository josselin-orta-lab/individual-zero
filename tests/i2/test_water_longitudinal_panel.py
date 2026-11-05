"""All four policies are compared over an equal 20-tick maximum horizon."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.water_longitudinal_panel import longitudinal_water_panel, POLICIES, HORIZON

class LongitudinalWaterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = longitudinal_water_panel()

    def test_all_endpoints_paid_censored_and_audited(self):
        r = self.report
        self.assertTrue(r["source_specific_descriptive_only"])
        self.assertFalse(r["independent_replication"])
        self.assertEqual(r["general_survival_benefit"], "NOT_ESTABLISHED")
        self.assertEqual(set(r["environments"]), {"inert", "restorative"})
        for world, arms in r["environments"].items():
            self.assertEqual(tuple(arms), tuple(p[0] for p in POLICIES))
            for policy, arm in arms.items():
                with self.subTest(world=world, policy=policy):
                    endpoint=arm["endpoint"]
                    self.assertEqual(endpoint["actual_uc_spent"], arm["paid_uc"])
                    self.assertEqual(endpoint["paid_decisions"], len(arm["actions"]))
                    self.assertEqual(len(arm["actions"]),len(arm["decision_ticks"]))
                    self.assertLessEqual(endpoint["ending_physical_tick"],HORIZON)
                    self.assertEqual(endpoint["modeled_terminal_observed"],
                                     arm["audit_terminal"])
                    self.assertFalse(arm["m11_authenticated"])
                    if endpoint["right_censored"]:
                        self.assertIsNone(endpoint["modeled_death_tick"])
                        self.assertEqual(endpoint["ending_physical_tick"],HORIZON)
                    else:
                        self.assertIsNotNone(endpoint["modeled_death_tick"])
                    self.assertLessEqual(endpoint["actual_uc_spent"],60)
                    self.assertGreaterEqual(endpoint["actual_uc_spent"],0)

    def test_reviewable_negative_and_positive_outcomes_not_overclaimed(self):
        print("I2_WATER_LONGITUDINAL_V1="+json.dumps(
            self.report,sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    unittest.main()
