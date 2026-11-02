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
        # Actual first CI found four distinct worlds among five
        # preregistered seeds. Do not regenerate seeds post hoc.
        self.assertEqual(len(set(regimes)), 4)
        self.assertTrue(all(len(x) == 10 and x[0] == -8 for x in regimes))
        for bad in (True, 0, 102, 101.0, "101"):
            with self.subTest(seed=bad), self.assertRaises(ValueError):
                schedule(bad)

    def test_all_four_policies_use_same_seed_world_without_false_claims(self):
        report = self.report
        self.assertEqual(report["generalized_survival_benefit"], "NOT_ESTABLISHED")
        self.assertEqual(report["natural_learning"], "NOT_ESTABLISHED")
        self.assertEqual(set(report["results"]), {str(s) for s in SEEDS})
        groups = report["seeded_world_groups_researcher_only"]
        self.assertTrue(report["unique_worlds_not_independent_population_samples"])
        self.assertEqual(report["distinct_world_count"], 4)
        self.assertGreaterEqual(report["distinct_exposed_world_count"], 1)
        self.assertLessEqual(report["distinct_exposed_world_count"], 4)
        self.assertEqual(sum(len(g["seeds"]) for g in groups), len(SEEDS))
        self.assertEqual(sum(g["fresh_lives"] for g in groups),
                         len(SEEDS) * len(POLICIES))
        self.assertEqual(sorted(x for g in groups for x in g["seeds"]),
                         sorted(SEEDS))
        for group in groups:
            self.assertEqual(group["hidden_impulses_researcher_only"],
                             schedule(group["seeds"][0]))
            for seed in group["seeds"]:
                self.assertEqual(schedule(seed),
                                 group["hidden_impulses_researcher_only"])
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

    def test_print_reviewable_predeclared_panel_outcomes(self):
        import json
        # Source-specific descriptive counts only, no survival GO.
        print("I2_SEEDED_VARYING_PANEL_RESULTS=" +
              json.dumps(self.report, sort_keys=True, separators=(",", ":")),
              flush=True)


if __name__ == "__main__":
    unittest.main()
