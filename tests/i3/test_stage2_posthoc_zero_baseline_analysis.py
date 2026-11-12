"""No-World, post-hoc paired score reducer and source integrity checks."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_posthoc_zero_baseline_analysis as E
from i3.modules.world import World


class PosthocZeroChangeForecastTests(unittest.TestCase):
    def test_exact_source_all_assigned_no_world_and_adverse_units_preserved(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("no World allowed")), patch(
                              "i3.runtime.life.run_life",
                              side_effect=AssertionError("no new life")):
            report = E.audit()
        print("I3_STAGE2_POSTHOC_ZERO_BASELINE="+json.dumps(
            report, sort_keys=True, separators=(",", ":")))
        self.assertEqual(report["status"], "POSTHOC_PAIRED_SCORE_INTEGRITY_PASS")
        self.assertEqual(report["all_assigned_technical_units"], 4)
        self.assertEqual(report["all_assigned_actual_steps"], 320)
        self.assertEqual(report["all_events"]["events"], 320)
        self.assertEqual(report["original_engineering_lives_rerun"], 0)
        self.assertEqual(report["worlds_opened_for_this_reanalysis"], 0)
        self.assertEqual(report["scientific_lives"], 0)
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(report["source_sha256"], E.SOURCE_DIGEST)
        self.assertEqual(report["comparator_selection_timing"],
                         "POSTHOC_AFTER_ORIGINAL_OUTCOMES")
        self.assertTrue(report["baseline_was_not_equal_work_or_action_mediation_control"])
        self.assertTrue(report["within_trajectory_steps_are_not_independent_units"])
        self.assertTrue(report["unit_heterogeneity_prevents_generalization"])
        self.assertEqual(report["unit_mean_gain_positive"], 1)
        self.assertEqual(report["unit_mean_gain_negative"], 3)
        self.assertEqual(report["unit_mean_gain_tied"], 0)
        self.assertEqual(report["all_events"]["native_better_event_count"],284)
        self.assertEqual(report["all_events"]["zero_better_event_count"],32)
        self.assertEqual(report["all_events"]["tie_event_count"],4)
        self.assertAlmostEqual(
            report["all_events"]["mean_native_squared_loss"], 4.959767667078736)
        self.assertAlmostEqual(
            report["all_events"]["mean_zero_change_squared_loss"], 5.506659144100004)
        self.assertEqual(
            [(r["world"], r["seed"]) for r in report["rows"]], list(E.GRID))
        self.assertEqual(
            [r["source_count_bins"]["unseen_exact"]["events"]
             for r in report["rows"]], [6,6,6,6])
        self.assertEqual(
            [r["source_count_bins"]["seen_exact"]["events"]
             for r in report["rows"]], [74,74,74,74])
        self.assertEqual(len(report["canonical_source_extract_sha256"]), 64)

    def test_pure_forecast_score_is_hand_verifiable_and_target_matched(self):
        native, zero, gain = E.paired_score([1,0,0,0,0],
                                             [2,0,0,0,0])
        self.assertAlmostEqual(native, 0.2)
        self.assertAlmostEqual(zero, 0.8)
        self.assertAlmostEqual(gain, 0.6)
        a,b,c = E.paired_score([3,0,0,0,0],[1,0,0,0,0])
        self.assertAlmostEqual(a, 0.8)
        self.assertAlmostEqual(b, 0.2)
        self.assertAlmostEqual(c, -0.6)
        for a,b in (([0,0,0,0],[0,0,0,0,0]),
                    ([0,0,0,0,float('nan')],[0,0,0,0,0]),
                    ([0,0,0,0,True],[0,0,0,0,0])):
            with self.assertRaises(ValueError):
                E.paired_score(a,b)

    def test_fail_closed_on_mismatched_identity_or_missing_factual_event(self):
        original = json.loads(E.DATASET.read_text(encoding="utf-8"))
        for change in ("source", "population", "missing", "counterfactual",
                       "forecast", "censor", "seal"):
            bad = deepcopy(original)
            if change == "source":
                bad["source_ref"]["original_aggregate_sha256"] = "0"*64
            elif change == "population":
                bad["worlds"][0]["seed"] += 1
            elif change == "missing":
                bad["worlds"][0]["events"].pop()
            elif change == "counterfactual":
                bad["worlds"][0]["events"][0]["actual_delta"] = [0,0,0,0]
            elif change == "forecast":
                bad["worlds"][0]["events"][0]["forecast_delta"][0] = float("nan")
            elif change == "censor":
                bad["worlds"][0]["events"][0]["learning_status"] = "NO_FUNDED_LEARNING"
            elif change == "seal":
                bad["worlds"][0]["events"][0]["preoutcome_forecast_sha256"] = None
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    E.reduce_dataset(bad)

    def test_source_is_stable_read_only(self):
        before = E.DATASET.read_bytes()
        first = E.audit()
        second = E.audit()
        self.assertEqual(before, E.DATASET.read_bytes())
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
