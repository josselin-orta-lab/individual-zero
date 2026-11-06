"""P5b heldout preregistration and evidence controls, DEVELOPMENT fixtures only."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies, p4a_validation, p5b_schedule, p5b_heldout
from i3.modules.genome import generation_zero, digest as genome_digest
from i3.runtime.life import run_life
from i3.runtime.provenance import digest, world_snapshot


class P5bProspectiveScreenTests(unittest.TestCase):
    def test_allocation_is_independent_and_has_no_world_side_effect(self):
        with patch.object(p2_ecologies, "world_for",
                          side_effect=AssertionError("heldout world opened")):
            x = p5b_schedule.manifest()
            self.assertEqual(x, p5b_schedule.manifest())
            self.assertEqual(x["lives"], 1152)
            self.assertEqual(len(x["exposure"]), 24)
            self.assertEqual({i["index"] for i in x["exposure"]}, set(range(72, 96)))
            self.assertEqual({i["world_seed"] for i in x["exposure"]},
                             set(range(30072, 30096)))
            self.assertEqual(len(p4a_validation.verify_frozen_genomes()), 48)
        for triple in [(-1, "stable", 0), (4, "stable", 0),
                       (0, "bogus", 0), (0, "pulse", 2), (True, "pulse", 1)]:
            with self.assertRaises(ValueError):
                p5b_schedule.world_index(*triple)

    def test_launch_is_denied_before_first_world_when_no_approval(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(p2_ecologies, "world_for",
                              side_effect=AssertionError("validation opened early")):
                with self.assertRaises(RuntimeError):
                    p5b_heldout.run()

    def test_receipt_checks_actual_paid_scores_and_original_body_physics(self):
        spec = p2_ecologies.world_for("stable", "development", 19)
        genome = generation_zero(761)
        life = run_life(genome, spec, 1326, 400, keep_trace=True,
                        effect_readout="full", observer_mind_digest=True,
                        observer_decision_diagnostics=True)
        kw = dict(mode="full", population=0, arm="selected", slot=0,
                  family="stable", repeat=0, index=72, seed=1326,
                  world_hash=digest(world_snapshot(spec)),
                  genome_hash=genome_digest(genome))
        receipt = p5b_heldout._receipt(life, **kw)
        self.assertTrue(receipt["early_witness"])
        self.assertEqual(len(receipt["early_witness"]), min(life["steps_lived"], 12))
        corrupted = deepcopy(life)
        corrupted["trace"][0]["info"]["observer"]["score_witness"] = []
        with self.assertRaises(RuntimeError):
            p5b_heldout._receipt(corrupted, **kw)
        corrupted = deepcopy(life)
        corrupted["cognitive_accounting"]["totals"]["energy"]["unpaid"] = 1
        with self.assertRaises(RuntimeError):
            p5b_heldout._receipt(corrupted, **kw)
        corrupted = deepcopy(life)
        corrupted["trace"][0]["funding_phases"]["learning"]["work"]["replays"] += 1
        with self.assertRaises(RuntimeError):
            p5b_heldout._receipt(corrupted, **kw)

    def test_preaction_shared_option_score_is_not_late_body_confound(self):
        def step(t, body, action, base):
            return {
                "t": t, "action": action, "param": None,
                "pre_body": list(body), "funding": "FUNDED",
                "scores": [
                    {"option": "boire", "base_return": base,
                     "bonus": 0.0, "score": base}],
            }
        full = {"early_witness": [
            step(1, (60, 60, 60, 60, 60), "attendre", 1.0),
            step(2, (59, 59, 59, 60, 59), "boire", 1.0),
            step(3, (58, 58, 58, 60, 58), "boire", 1.0)]}
        treated = {"early_witness": [
            step(1, (60, 60, 60, 60, 60), "attendre", 1.0),
            step(2, (59, 59, 59, 60, 59), "manger", 0.5),
            step(3, (20, 20, 20, 20, 20), "boire", 1000.0)]}
        result = p5b_heldout._early_pair(full, treated)
        self.assertEqual(result["first_action_difference_within_window"], 2)
        self.assertEqual(result["first_shared_option_base_return_difference_before_action"], 2)
        self.assertEqual(result["first_shared_option_score_difference_before_action"], 2)
        self.assertEqual(result["matched_preaction_body_steps"], 2)
        other = deepcopy(treated)
        other["early_witness"][1]["scores"][0]["base_return"] = 1.0
        other["early_witness"][1]["scores"][0]["score"] = 1.0
        result = p5b_heldout._early_pair(full, other)
        self.assertIsNone(result["first_shared_option_score_difference_before_action"])

    def test_exact_n4_inference_floor_is_preserved(self):
        self.assertEqual(p5b_heldout.p5a_screen._two_sided_sign_flip_p(
            [1, 1, 1, 1]), 0.125)
        self.assertEqual(p5b_heldout.p5a_screen._holm_adjust(
            {"a": .02, "b": .03, "c": .5}),
            {"a": .06, "b": .06, "c": .5})


if __name__ == "__main__":
    unittest.main()
