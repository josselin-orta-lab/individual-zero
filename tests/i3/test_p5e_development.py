"""P5e fixed development-only competition pilot contract and adversarial tests."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab.p5e_development import classify_step, manifest


def step(*, meal_score=1.0, other_score=0.5,
         winner="manger:tok0", admitted="manger:tok0",
         action="manger", mechanism="raw_score_fallback"):
    return {
        "inventory_before_decision": [["berry", 1]],
        "paid_option_scores": [
            {"option": "manger:tok0", "total_score": meal_score},
            {"option": "attendre", "total_score": other_score}],
        "competition": {
            "status": "ACTION_ADMITTED" if admitted else "ALL_CONTROLS_REJECTED",
            "winner_before_control": winner,
            "selection_mechanism": mechanism,
            "control_attempts": [{
                "option": winner, "admitted": admitted == winner}],
            "final_admitted_option": admitted,
            "paid_competition_cycles": 1,
        },
        "physical_action": action,
        "paid_decision_work": {"cycles": 5},
    }


class P5eDevelopmentTests(unittest.TestCase):
    def test_allocation_is_new_and_development_only(self):
        m = manifest()
        self.assertEqual(m["cohort"], "DEVELOPMENT_ONLY")
        self.assertEqual(m["validation"], "NOT_OPENED")
        self.assertEqual(m["reserve"], "LOCKED")
        self.assertEqual(m["selection"], "NOT_OPENED")
        self.assertEqual(m["genome_seeds"], [901, 902])
        self.assertEqual(m["score_modes"], ["normal", "discard_curiosity_bonus"])
        self.assertEqual(m["horizon"], 120)
        self.assertEqual([a["development_index"] for a in m["allocation"]],
                         list(range(38, 44)))
        self.assertEqual(len(set(a["life_seed"] for a in m["allocation"])), 6)

    def test_true_raw_top_eating_wins_and_is_admitted(self):
        counts = classify_step(step())
        self.assertEqual(counts["meal_raw_top_or_tied_full"], 1)
        self.assertEqual(counts["meal_won_competition_before_control"], 1)
        self.assertEqual(counts["real_eating_actions"], 1)
        self.assertEqual(counts["meal_admitted_after_control"], 1)
        self.assertFalse(counts["meal_top_but_other_competition_winner"])

    def test_other_option_higher_is_not_misreported_as_meal_top(self):
        s = step(meal_score=-0.2, other_score=1.5,
                 winner="attendre", admitted="attendre", action="attendre")
        self.assertEqual(classify_step(s)["higher_scoring_nonmeal"], 1)
        self.assertEqual(classify_step(s)["rest_selected_over_meal"], 1)

    def test_accumulator_can_win_over_raw_score_without_forging_eating(self):
        s = step(winner="attendre", admitted="attendre", action="attendre",
                 mechanism="threshold_crossing")
        result = classify_step(s)
        self.assertEqual(result["meal_top_but_other_competition_winner"], 1)
        self.assertEqual(result["winner_by_threshold_crossing"], 1)
        self.assertEqual(result["real_eating_actions"], 0)

    def test_no_paid_score_is_distinct_from_competition_loss(self):
        s = step()
        s["paid_option_scores"] = []
        s["competition"] = None
        self.assertEqual(classify_step(s)["no_paid_meal_option"], 1)

    def test_forged_admitted_eating_and_unpaid_cycles_are_rejected(self):
        s = step()
        s["physical_action"] = "attendre"
        with self.assertRaises(RuntimeError):
            classify_step(s)
        s = step()
        s["competition"]["paid_competition_cycles"] = 10
        with self.assertRaises(RuntimeError):
            classify_step(s)


if __name__ == "__main__":
    unittest.main()
