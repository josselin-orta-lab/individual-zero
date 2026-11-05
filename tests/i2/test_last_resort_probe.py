"""Separate opt-in survival probe: model-specific contrasts, not G3 or M11."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.last_resort_probe import (
    PROTOCOL_ID, CASES, run_last_resort_probe,
)


class LastResortComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One deterministic four-arm readout, reused by the tests below.
        cls.report = run_last_resort_probe()

    def test_two_environments_and_explicit_ablation(self):
        self.assertEqual(self.report["protocol_id"], PROTOCOL_ID)
        self.assertEqual(list(self.report["results"]),
                         [case[0] for case in CASES])
        self.assertEqual(self.report["scientific_verdict"], "NOT_ESTABLISHED")
        self.assertFalse(self.report["m11_authenticated"])
        for case in self.report["results"].values():
            self.assertEqual(set(case["arms"]),
                             {"observational_control", "survival_last_resort"})

    def test_favorable_emergency_contact_is_new_not_old_proof(self):
        case = self.report["results"]["hidden_restoration"]
        older = case["arms"]["observational_control"]
        emergency = case["arms"]["survival_last_resort"]
        self.assertEqual(older["endpoint"]["modeled_death_tick"], 16)
        self.assertIsNone(emergency["endpoint"]["modeled_death_tick"])
        self.assertEqual(emergency["endpoint"]["ending_energy"], 6)
        self.assertEqual(emergency["last_resort_paid_choice_ticks"], [16])
        self.assertEqual(emergency["contacts"][0]["tick"], 16)
        self.assertFalse(emergency["contacts"][0]["observed_later"])
        self.assertEqual(case["first_divergence"]["first_divergence_seq"], 8)
        self.assertTrue(case["first_divergence"]["matched_prechoice"])

    def test_adverse_emergency_remains_harmful_and_paid(self):
        case = self.report["results"]["persistent_adversity"]
        emergency = case["arms"]["survival_last_resort"]
        self.assertEqual(emergency["endpoint"]["modeled_death_tick"], 16)
        self.assertEqual(emergency["endpoint"]["ending_energy"], 0)
        self.assertEqual(emergency["last_resort_paid_choice_ticks"], [16])
        self.assertEqual(emergency["contacts"][0]["tick"], 16)
        self.assertFalse(emergency["contacts"][0]["observed_later"])
        self.assertGreater(emergency["endpoint"]["actual_uc_spent"], 0)
        self.assertTrue(case["first_divergence"]["matched_prechoice"])

    def test_exact_result_publication_once_per_environment(self):
        # This report is the SAME cached run per CI environment, not
        # an independent experiment each time a Python version repeats it.
        print("I2_LAST_RESORT_V1_RESULTS=" + json.dumps(
            self.report, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
