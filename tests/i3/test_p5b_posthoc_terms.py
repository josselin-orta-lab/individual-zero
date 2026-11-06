"""P5b post-hoc decomposition falsifiers: pure synthetic paid-score witnesses."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p5b_posthoc_terms


def step(t, action="attendre", body=None, scores=None):
    return {"t": t, "action": action, "param": None,
            "pre_body": body if body is not None else [60]*5,
            "funding": "FUNDED", "scores": scores or []}


def candidate(option, base, bonus):
    return {"option": option, "base_return": base,
            "bonus": bonus, "score": base + bonus}


class P5bPosthocScoreTermsTests(unittest.TestCase):
    def test_bonus_only_score_difference_keeps_base_equal(self):
        full = {"early_witness": [
            step(1, "boire", scores=[candidate("drink", 4., 1.)])]}
        mask = {"early_witness": [
            step(1, "manger", scores=[candidate("drink", 4., 3.)])]}
        r = p5b_posthoc_terms.pair_terms(full, mask)
        self.assertEqual(r["first_action_difference_within_window"], 1)
        self.assertEqual(r["matched_funded_candidate_observations"], 1)
        self.assertEqual(r["option_score_delta_bonus_only"], 1)
        self.assertEqual(r["option_score_delta_base_only"], 0)
        self.assertIn("score_delta_bonus_only", r["pair_flags"])
        self.assertNotIn("any_base_delta", r["pair_flags"])

    def test_base_only_and_both_components_are_distinguished(self):
        full = {"early_witness": [
            step(1, scores=[candidate("eat", 5., 1.),
                            candidate("drink", 2., 2.)])]}
        mask = {"early_witness": [
            step(1, scores=[candidate("eat", 7., 1.),
                            candidate("drink", 4., 3.)])]}
        r = p5b_posthoc_terms.pair_terms(full, mask)
        self.assertEqual(r["option_score_delta_base_only"], 1)
        self.assertEqual(r["option_score_delta_both_terms"], 1)
        self.assertEqual(r["matched_funded_candidate_observations"], 2)

    def test_equal_total_can_hide_cancelled_component_changes(self):
        full = {"early_witness": [step(1, scores=[candidate("walk", 2., 1.)])]}
        mask = {"early_witness": [step(1, scores=[candidate("walk", 3., 0.)])]}
        r = p5b_posthoc_terms.pair_terms(full, mask)
        self.assertEqual(r["option_components_changed_but_score_cancelled"], 1)
        self.assertNotIn("any_score_delta", r["pair_flags"])

    def test_never_compare_unmatched_body_or_unfunded_option(self):
        full = {"early_witness": [
            step(1, body=[60]*5, scores=[candidate("sleep", 1., 2.)])]}
        mask = {"early_witness": [
            step(1, body=[50]*5, scores=[candidate("sleep", 30., 30.)])]}
        self.assertEqual(
            p5b_posthoc_terms.pair_terms(full, mask)["matched_funded_candidate_observations"], 0)

    def test_never_use_later_divergent_history_as_preaction_information(self):
        full = {"early_witness": [
            step(1, "boire", scores=[candidate("drink", 1., 0.)]),
            step(2, "boire", scores=[candidate("drink", 1., 0.)])]}
        treated = {"early_witness": [
            step(1, "manger", scores=[candidate("drink", 1., 0.)]),
            step(2, "boire", scores=[candidate("drink", 100., 0.)])]}
        r = p5b_posthoc_terms.pair_terms(full, treated)
        self.assertEqual(r["first_action_difference_within_window"], 1)
        self.assertEqual(r["matched_funded_candidate_observations"], 1)
        self.assertNotIn("any_score_delta", r["pair_flags"])


if __name__ == "__main__":
    unittest.main()
