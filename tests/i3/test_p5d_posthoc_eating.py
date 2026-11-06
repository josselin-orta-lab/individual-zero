"""Adversarial synthetic tests for P5d original-only eating choice audit.

These are synthetic receipts, never new experimental lives.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab.p5d_posthoc_eating import classify_step, analyze_original


def step():
    return {
        "capture_inventory": [["berry", 1]],
        "paid_resource_scores": [{
            "option": "manger:tok0", "total_score": 1.0,
            "curiosity_computed": 0.1, "curiosity_applied": 0.,
            "risk_applied": -0.02}],
        "resource_options_scored": 1,
        "body_before_decision": [70., 30., 80., 75., 80.],
        "paid_decision_energy": 0.2,
        "decision_funding": "FUNDED",
        "decision_outcome": "action_admitted",
        "chosen_option": "attendre", "action": "attendre",
    }


class P5dOriginalEatingTests(unittest.TestCase):
    def test_offer_and_paid_score_do_not_imply_eating(self):
        result = classify_step(step())
        self.assertTrue(result["funded_meal_option"])
        self.assertTrue(result["meal_best_among_resource_scores_only"])
        self.assertTrue(result["energy_for_meal_after_paid_decision"])
        self.assertTrue(result["integrity_above_innate_veto_threshold"])
        self.assertFalse(result["selected_direct_meal"])
        self.assertFalse(result["physically_ate"])

    def test_missing_inventory_with_paid_eat_fails(self):
        s = step()
        s["capture_inventory"] = []
        with self.assertRaises(ValueError):
            classify_step(s)

    def test_unpaid_eating_and_motor_mismatch_fail(self):
        s = step()
        s["resource_options_scored"] = 0
        with self.assertRaises(ValueError):
            classify_step(s)
        s = step()
        s["action"] = "manger"
        s["chosen_option"] = "attendre"
        # This is an internal synthetic inconsistency: selected direct
        # eating can be absent when different winning plans lead to eating,
        # so check only the observable selection->action implication.
        s["chosen_option"] = "manger:tok0"
        s["action"] = "dormir"
        with self.assertRaises(ValueError):
            classify_step(s)

    def test_source_mismatch_stops_before_analysis(self):
        with patch("i3.lab.p5d_posthoc_eating.verify_original",
                   side_effect=ValueError("original byte hash mismatch")):
            with patch("i3.lab.p5d_posthoc_eating.read_raw", return_value=b"{}"):
                with self.assertRaises(ValueError):
                    analyze_original("synthetic-only.json")


if __name__ == "__main__":
    unittest.main()
