"""Stage-2 native-choice paid-depth E1: no born World or imposed motor."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage2_native_option_depth_choice as E
from i3.modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveWork, cognitive_cost, debit_cognition
)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import World
from i3.runtime import life as runtime


class NativeOptionDepthE1(unittest.TestCase):
    def test_exact_preregistered_grid_with_no_world_or_life(self):
        with (patch.object(World, "__init__", side_effect=AssertionError(
                "World MUST NOT open in this software study")),
              patch.object(runtime, "run_life", side_effect=AssertionError(
                "run_life MUST NOT execute in this software study"))):
            result = E.audit()
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertEqual(result["source_kind"], E.SOURCE_KIND)
        self.assertEqual(result["native_decision_calls"], 48)
        self.assertEqual(result["scenarios"], 12)
        self.assertEqual(result["pairwise_depth_comparisons"], 24)
        self.assertEqual(len(result["rows"]), 12)
        self.assertEqual(len(result["comparisons"]), 24)
        self.assertTrue(result["reference_parity"])
        self.assertEqual(result["worlds_opened"], 0)
        self.assertEqual(result["new_scientific_lives"], 0)
        self.assertEqual(result["science"], "NOT_ISSUED")
        self.assertFalse(result["stage2_2_go"])
        self.assertFalse(result["stage2_3_go"])
        self.assertIn(result["mechanism_verdict"], (
            "NATIVE_ACTION_DISCRIMINATION_SOFTWARE_ONLY",
            "NO_DECISION_DISCRIMINATION_ON_FROZEN_GRID"))
        self.assertEqual(len(result["payload_sha256"]), 64)
        print("I3_STAGE2_NATIVE_CHOICE_E1=" + json.dumps({
            "sha256": result["payload_sha256"],
            "calls": result["native_decision_calls"],
            "complete_comparable": result["complete_comparable"],
            "changed_scores": result["different_score_vector"],
            "changed_native_options": result["different_native_option"],
            "changed_motors": result["different_actual_motor"],
            "full_funding_action_discrimination":
                result["action_divergence_with_full_funding"],
            "funding_confound": result["incomplete_or_offered_confound"],
            "verdict": result["mechanism_verdict"],
            "science": result["science"],
            "worlds": result["worlds_opened"],
        }, sort_keys=True))

    def test_native_model_billing_motor_reserve_and_reference_parity(self):
        r = E.audit()
        for row in r["rows"]:
            self.assertIn(row["body_index"], (0, 1, 2))
            self.assertIn(row["context"], E.CONTEXTS)
            self.assertEqual(set(row["modes"]), set(E.MODES))
            plain, full = row["modes"]["reference"], row["modes"]["full"]
            self.assertTrue(E._parity(full, plain))
            for mode, item in row["modes"].items():
                with self.subTest(context=row["context"], body=row["body_index"],
                                  mode=mode):
                    self.assertEqual(item["source"], E.SOURCE_KIND)
                    self.assertEqual(item["scored_options"],
                                     len(item["score_rows"]))
                    self.assertLessEqual(item["scored_options"],
                                         item["offered_options"])
                    self.assertEqual(len({w["option"] for w
                                          in item["score_rows"]}),
                                     item["scored_options"])
                    self.assertTrue(item["no_real_World_debit"])
                    work = CognitiveWork(**item["work"])
                    e, v = cognitive_cost(BodyLaws(), work)
                    self.assertAlmostEqual(e, item["model_energy_paid"], 12)
                    self.assertAlmostEqual(v, item["model_vigilance_paid"], 12)
                    post, receipt = debit_cognition(
                        item["body"], BodyLaws(), work)
                    self.assertEqual(post, tuple(item["post_model_budget_body"]))
                    self.assertTrue(all(receipt[c]["unpaid"] == 0.
                                        for c in ("energy", "vigilance")))
                    if item["action"] is not None:
                        self.assertIn(item["action"], ACTION_COSTS)
                    if item["action"] not in (None, "dormir"):
                        self.assertGreaterEqual(
                            item["post_model_budget_body"][0] + 1e-12,
                            ACTION_COSTS[item["action"]])

    def test_only_complete_same_order_native_choices_count_as_information(self):
        r = E.audit()
        for contrast in r["comparisons"]:
            with self.subTest(context=contrast["context"],
                              body=contrast["body_index"],
                              mode=contrast["mode"]):
                self.assertIn(contrast["mode"], ("cap1", "cap4"))
                self.assertLessEqual(
                    contrast["motor_divergence_with_full_funding"],
                    contrast["complete_comparable"])
                if contrast["motor_divergence_with_full_funding"]:
                    self.assertTrue(contrast["complete_comparable"])
                    self.assertTrue(contrast["same_order"])
                    self.assertTrue(contrast["changed_scores"])
                    self.assertTrue(contrast["changed_actual_action"])
                if contrast["funding_or_offered_confound"]:
                    self.assertFalse(contrast["complete_comparable"])
        self.assertEqual(
            r["action_divergence_with_full_funding"],
            sum(c["motor_divergence_with_full_funding"] for c in r["comparisons"]))

    def test_both_no_budget_and_unknown_depth_are_rejected(self):
        with self.assertRaises(ValueError):
            E._fresh("unknown")
        with self.assertRaises(ValueError):
            E.LabDepthCapMind(midpoint(), E.SEED, depth_cap=0)
        with self.assertRaises(ValueError):
            E._capture(E.BODIES[0], "invented-source")
        body = (0.001, 60., 60., 80., 0.001)
        item = E._run(body, "water_here", "cap4")
        self.assertEqual(item["funding"], "NO_PROCESSING_BUDGET")
        self.assertIsNone(item["action"])
        self.assertIsNone(item["option"])
        self.assertEqual(item["work"], {
            "cycles": 0, "simulated_steps": 0,
            "memory_items": 0, "replays": 0})
        self.assertEqual(item["model_energy_paid"], 0.)
        self.assertEqual(item["model_vigilance_paid"], 0.)

    def test_repeatability_and_original_mind_does_not_acquire_policy_flag(self):
        a, b = E.audit(), E.audit()
        self.assertEqual(a, b)
        self.assertEqual(a["payload_sha256"], b["payload_sha256"])
        self.assertFalse(hasattr(Mind(midpoint(), E.SEED),
                                 "_stage2_lab_depth_cap"))
        for item in a["rows"]:
            self.assertEqual(
                item["modes"]["full"]["score_rows"],
                item["modes"]["reference"]["score_rows"])


if __name__ == "__main__":
    unittest.main()
