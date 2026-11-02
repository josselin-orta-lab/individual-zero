"""Four independently paid trajectories per environment, descriptive only."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.four_policy_survival_ablation import (
    run_four_policy_ablation, ENVIRONMENTS, POLICIES,
)


class FourPolicySurvivalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_four_policy_ablation()

    def test_four_fresh_paid_arms_in_each_world(self):
        report = self.report
        self.assertEqual(tuple(report["results"]), ENVIRONMENTS)
        self.assertEqual(report["general_survival_benefit"], "NOT_ESTABLISHED")
        self.assertFalse(report["m11_authenticated"])
        for env in ENVIRONMENTS:
            variants = report["results"][env]
            self.assertEqual(tuple(variants), tuple(name for name, *_ in POLICIES))
            for data in variants.values():
                endpoint = data["endpoint"]
                self.assertEqual(endpoint["actual_uc_spent"], data["uc_spent"])
                self.assertGreater(endpoint["paid_decisions"], 0)
                self.assertLessEqual(endpoint["ending_physical_tick"], 16)
                self.assertEqual(len(data["chosen_actions"]),
                                 endpoint["paid_decisions"])
                self.assertEqual(len(data["chosen_at_ticks"]),
                                 len(data["chosen_actions"]))
                self.assertGreaterEqual(data["deadline_suppressions"], 0)
                self.assertGreaterEqual(data["last_resort_raises"], 0)

    def test_control_policies_remain_distinguishable_and_traceable(self):
        for env in ENVIRONMENTS:
            variants = self.report["results"][env]
            self.assertEqual(variants["observational"]["deadline_suppressions"], 0)
            self.assertEqual(variants["observational"]["last_resort_raises"], 0)
            self.assertEqual(variants["last_resort"]["deadline_suppressions"], 0)
            self.assertEqual(variants["deadline"]["last_resort_raises"], 0)
        self.assertEqual(self.report["conclusion"],
                         "EXPLORATORY_MODEL_SPECIFIC_ONLY")


if __name__ == "__main__":
    unittest.main()
