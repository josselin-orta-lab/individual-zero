"""Explicit low-energy cohorts expose survival-policy failure without tuning."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.four_policy_survival_ablation import (
    POLICIES, ENVIRONMENTS, run_four_policy_ablation,
)


class ScarcityFourPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reports = {
            energy: run_four_policy_ablation(initial_energy=energy)
            for energy in (8, 16)
        }

    def test_low_energy_exposes_full_matched_four_arm_design(self):
        for energy, report in self.reports.items():
            self.assertEqual(report["initial_energy"], energy)
            self.assertFalse(report["m11_authenticated"])
            self.assertEqual(report["general_survival_benefit"], "NOT_ESTABLISHED")
            for env in ENVIRONMENTS:
                case = report["results"][env]
                self.assertEqual(tuple(case["arms"]),
                                 tuple(name for name, *_ in POLICIES))
                for arm in case["arms"].values():
                    endpoint = arm["endpoint"]
                    self.assertEqual(arm["uc_spent"], endpoint["actual_uc_spent"])
                    self.assertGreaterEqual(endpoint["paid_decisions"], 0)
                    self.assertLessEqual(endpoint["ending_physical_tick"], 16)
                for contrast in case["contrasts_vs_observational"].values():
                    self.assertTrue(contrast["no_causal_survival_attribution"])
                    if contrast["control_death_tick"] is not None or contrast[
                        "intervention_death_tick"] is not None:
                        self.assertIsNone(
                            contrast["energy_difference_only_common_nonterminal_window"])

    def test_deterministic_scarcity_results_visible_for_review(self):
        import json
        print("I2_SCARCITY_FOUR_POLICY_RESULTS=" + json.dumps(
            self.reports, sort_keys=True, separators=(",", ":")), flush=True)

    def test_negative_survival_evidence_is_preserved(self):
        # These are descriptive results for the exact fixed toy worlds.
        for energy in (8, 16):
            for env in ("adverse", "restoration"):
                case = self.reports[energy]["results"][env]
                for label, arm in case["arms"].items():
                    with self.subTest(energy=energy, env=env, policy=label):
                        self.assertEqual(arm["endpoint"]["modeled_death_tick"], 4)
                        self.assertEqual(arm["endpoint"]["ending_energy"], 0)
                        self.assertEqual(arm["food_contact_ticks"], [4])
                        self.assertEqual(arm["uc_spent"], 9)
                        self.assertEqual(arm["last_resort_raises"], 0)
        case = self.reports[8]["results"]["stable"]
        for label, arm in case["arms"].items():
            self.assertEqual(arm["endpoint"]["modeled_death_tick"], 8)
            self.assertEqual(arm["endpoint"]["ending_energy"], 0)
            self.assertEqual(arm["last_resort_raises"], 0)
        self.assertEqual(case["arms"]["combined"]["chosen_actions"],
                         case["arms"]["deadline"]["chosen_actions"])
        self.assertNotEqual(case["arms"]["combined"]["chosen_actions"],
                            case["arms"]["observational"]["chosen_actions"])
        for label, arm in self.reports[16]["results"]["stable"]["arms"].items():
            self.assertIsNone(arm["endpoint"]["modeled_death_tick"])
            self.assertTrue(arm["endpoint"]["right_censored"])
            self.assertEqual(arm["endpoint"]["ending_energy"], 8)
            self.assertEqual(arm["last_resort_raises"], 0)

    def test_bad_energy_is_refused_not_clamped(self):
        for invalid in (True, 0, -1, 101, 4.5):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                run_four_policy_ablation(initial_energy=invalid)


if __name__ == "__main__":
    unittest.main()
