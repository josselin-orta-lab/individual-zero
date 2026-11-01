"""Narrow exploratory battery checks, not independent scientific repeats."""
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.runtime.world_viability_probe import (
    LOCKED_CASES, run_locked_battery, paired_tick_energy_time_course,
)


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

    def test_exact_result_readout_for_source_pinned_analysis(self):
        # The locked battery was already evaluated ONCE by setUpClass.
        # Print that exact in-process evidence, not a second scientific
        # replicate, extra cohort or selectively retained best-case run.
        rows = []
        for item in self.report["rows"]:
            a, b = item["observational"], item["no_learning"]
            t = item["time_course"]
            rows.append({
                "case": item["case"],
                "first_choice_classification": item["first_choice_classification"],
                "first_choice_tick": item["first_choice_tick"],
                "endpoint_classification": item["endpoint_classification"],
                "time_course_classification": t["classification"],
                "first_energy_separation_tick": t["first_observed_energy_separation_tick"],
                "energy_integral": t["complete_common_window_energy_delta_integral"],
                "common_window_energy_delta": item["common_window_energy_delta"],
                "observational": {
                    "energy": a["ending_energy"],
                    "death_tick": a["modeled_death_tick"],
                    "physical_ticks": a["ending_physical_tick"],
                    "paid_decisions": a["paid_decisions"],
                    "uc_spent": a["actual_uc_spent"],
                    "censored": a["right_censored"],
                },
                "no_learning": {
                    "energy": b["ending_energy"],
                    "death_tick": b["modeled_death_tick"],
                    "physical_ticks": b["ending_physical_tick"],
                    "paid_decisions": b["paid_decisions"],
                    "uc_spent": b["actual_uc_spent"],
                    "censored": b["right_censored"],
                },
            })
        print("I2_LOCKED_VIABILITY_V1_RESULTS=" + json.dumps(
            {"lock_id": self.report["lock_id"], "rows": rows,
             "scientific_verdict": self.report["scientific_verdict"]},
            sort_keys=True, separators=(",", ":"),
        ), flush=True)
        self.assertEqual(len(rows), len(LOCKED_CASES))

    def test_equal_nonterminal_window_energy_integral_and_null_controls(self):
        rows = {r["case"]: r for r in self.report["rows"]}
        for name in ("stable_full", "adverse_no_food", "adverse_no_uc"):
            row = rows[name]
            self.assertEqual(
                row["time_course"]["classification"],
                "COMMON_NONTERMINAL_WINDOW_DESCRIPTIVE_ONLY",
            )
            self.assertEqual(
                row["time_course"]["complete_common_window_energy_delta_integral"],
                0,
            )
            self.assertIsNone(
                row["time_course"]["first_observed_energy_separation_tick"],
            )
            self.assertEqual(
                len(row["time_course"]["observed_world_tick_deltas"]), 12,
            )

    def test_incomplete_and_terminal_windows_refuse_energy_integral(self):
        left = {"execution": {"trace": [
            {"physical_tick": 1, "physical_end_energy": 2, "terminal": False},
            {"physical_tick": 2, "physical_end_energy": 0, "terminal": True},
        ]}}
        right = {"execution": {"trace": [
            {"physical_tick": 1, "physical_end_energy": 3, "terminal": False},
            {"physical_tick": 2, "physical_end_energy": 2, "terminal": False},
            {"physical_tick": 3, "physical_end_energy": 1, "terminal": False},
        ]}}
        comparison = paired_tick_energy_time_course(left, right)
        self.assertEqual(
            comparison["classification"],
            "TERMINAL_OR_UNEQUAL_WINDOW_NO_ENERGY_INTEGRAL",
        )
        self.assertIsNone(comparison["complete_common_window_energy_delta_integral"])
        self.assertEqual(comparison["observed_world_tick_deltas"], [])
        self.assertEqual(comparison["common_observed_tick_count"], 2)
        self.assertEqual(comparison["first_observed_energy_separation_tick"], 1)
        right["execution"]["trace"][0]["physical_tick"] = 9
        misaligned = paired_tick_energy_time_course(left, right)
        self.assertEqual(
            misaligned["classification"], "MISALIGNED_PHYSICAL_TICKS_NO_COMPARISON"
        )
        self.assertEqual(misaligned["common_observed_tick_count"], 0)
        self.assertIsNone(misaligned["first_observed_energy_separation_tick"])


if __name__ == "__main__":
    unittest.main()
