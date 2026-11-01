"""Narrow exploratory battery checks, not independent scientific repeats."""
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.runtime.world_viability_probe import LOCKED_CASES, run_locked_battery


class LockedWorldViabilityProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_locked_battery()

    def test_exact_locked_cases_and_no_scientific_claim(self):
        self.assertEqual(self.report["case_count"], 7)
        self.assertEqual(
            [r["case"] for r in self.report["rows"]],
            [row[0] for row in LOCKED_CASES],
        )
        self.assertEqual(self.report["scientific_verdict"],
                         "EXPLORATORY_MODEL_SPECIFIC_ONLY")
        self.assertEqual(self.report["generalized_survival_benefit"],
                         "NOT_ESTABLISHED")
        self.assertFalse(self.report["m11_authenticated"])
        self.assertTrue(self.report["no_policy_tuning"])

    def test_negative_controls_record_no_unearned_attribution(self):
        rows = {x["case"]: x for x in self.report["rows"]}
        for name in ("adverse_no_food", "adverse_no_uc"):
            self.assertEqual(
                rows[name]["first_choice_classification"],
                "NO_ACTION_DIVERGENCE_IN_OBSERVED_HORIZON",
            )
        self.assertEqual(rows["adverse_no_uc"]["observational"]["paid_decisions"], 0)
        self.assertEqual(rows["adverse_no_uc"]["no_learning"]["paid_decisions"], 0)
        self.assertEqual(rows["adverse_no_uc"]["common_window_energy_delta"], 0)

    def test_every_comparable_energy_delta_is_accounted(self):
        for row in self.report["rows"]:
            o, f = row["observational"], row["no_learning"]
            self.assertLessEqual(o["ending_physical_tick"], row["planned_ticks"])
            self.assertLessEqual(f["ending_physical_tick"], row["planned_ticks"])
            self.assertEqual(o["real_world_survival"], "NOT_ESTABLISHED")
            self.assertEqual(f["real_world_survival"], "NOT_ESTABLISHED")
            if row["common_window_energy_delta"] is not None:
                self.assertEqual(o["ending_physical_tick"], f["ending_physical_tick"])
                self.assertTrue(o["right_censored"])
                self.assertTrue(f["right_censored"])
                self.assertEqual(
                    row["common_window_energy_delta"],
                    o["ending_energy"] - f["ending_energy"],
                )

    def test_stable_control_not_claimed_beneficial(self):
        rows = {x["case"]: x for x in self.report["rows"]}
        stable = rows["stable_full"]
        self.assertEqual(stable["first_choice_classification"],
                         "NO_ACTION_DIVERGENCE_IN_OBSERVED_HORIZON")
        self.assertEqual(stable["common_window_energy_delta"], 0)


if __name__ == "__main__":
    unittest.main()
