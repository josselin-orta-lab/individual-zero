"""Seeded environmental diversity, matched paid policies, descriptive only."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.seeded_varying_world_panel import SEEDS, POLICIES, schedule, run_panel

class VaryingWorldPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_panel()

    def test_predeclared_seeds_change_actual_hidden_regimes(self):
        regimes = [schedule(seed) for seed in SEEDS]
        self.assertEqual(len(set(regimes)), len(SEEDS))
        self.assertTrue(all(len(x) == 10 and x[0] == -8 for x in regimes))
        for bad in (True, 0, 102, 101.0, "101"):
            with self.subTest(seed=bad), self.assertRaises(ValueError):
                schedule(bad)

    def test_all_four_policies_use_same_seed_world_without_false_claims(self):
        report = self.report
        self.assertEqual(report["generalized_survival_benefit"], "NOT_ESTABLISHED")
        self.assertEqual(report["natural_learning"], "NOT_ESTABLISHED")
        self.assertEqual(set(report["results"]), {str(s) for s in SEEDS})
        for seed in SEEDS:
            row=report["results"][str(seed)]
            self.assertEqual(row["hidden_impulses_researcher_only"], schedule(seed))
            self.assertEqual(tuple(row["arms"]), tuple(x[0] for x in POLICIES))
            for arm in row["arms"].values():
                endpoint=arm["endpoint"]
                self.assertEqual(arm["audit_uc"],endpoint["actual_uc_spent"])
                self.assertEqual(len(arm["actions"]),endpoint["paid_decisions"])
                self.assertLessEqual(endpoint["ending_physical_tick"],16)
                self.assertFalse(arm["m11_authenticated"])
                self.assertGreaterEqual(arm["last_resort_raises"],0)
                self.assertGreaterEqual(arm["deadline_suppressions"],0)

if __name__ == "__main__":
    unittest.main()
