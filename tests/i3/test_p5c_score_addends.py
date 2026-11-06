"""P5c DEVELOPMENT-only paid score component controls.

Four modes compute identical underlying original curiosity and risk contributions;
only which computed addends reach competition differs. No science worlds.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies
from i3.modules.genome import generation_zero
from i3.modules.mind import Mind
from i3.runtime.life import run_life

MODES = ("normal", "discard_curiosity_bonus",
         "discard_risk_penalty", "discard_both_bonus_terms")


class P5cScoreControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = p2_ecologies.world_for("stable", "development", 18)
        cls.genome = generation_zero(761)

    def test_unknown_score_addend_fails_before_opening_world(self):
        with patch.object(p2_ecologies, "world_for",
                          side_effect=AssertionError("world was opened")):
            with self.assertRaises(ValueError):
                Mind(self.genome, 761, score_addend_mode="oracle_bonus")
            with self.assertRaises(ValueError):
                run_life(self.genome, self.spec, 99, 12,
                         score_addend_mode="oracle_bonus")

    def test_default_life_with_and_without_observer_has_identical_receipts(self):
        normal = run_life(self.genome, self.spec, 99, 80, keep_trace=True)
        witness = run_life(self.genome, self.spec, 99, 80, keep_trace=True,
                           observer_decision_diagnostics=True)
        for name in ("trace_head", "evidence_head", "actions", "terminal",
                     "final_body", "cognitive_accounting", "steps_lived"):
            self.assertEqual(normal[name], witness[name], name)
        self.assertNotIn("score_addend_mode", normal)
        self.assertEqual(witness["score_addend_mode"], "normal")

    def test_modes_keep_real_paid_work_and_exact_score_component_contract(self):
        lives = [
            run_life(self.genome, self.spec, 1042, 85, keep_trace=True,
                     observer_decision_diagnostics=True,
                     observer_mind_digest=True, score_addend_mode=mode)
            for mode in MODES
        ]
        self.assertEqual(len({x["manifest"]["world_sha256"] for x in lives}), 1)
        self.assertEqual(len({x["genome"] for x in lives}), 1)
        for mode, life in zip(MODES, lives):
            self.assertEqual(life["score_addend_mode"], mode)
            acc = life["cognitive_accounting"]
            self.assertEqual(acc["shortfall_steps"], 0)
            self.assertEqual(acc["pending_replays"], 0)
            self.assertGreater(acc["learning_updates"], 0)
            self.assertEqual(sum(life["observer_decision_diagnostics"][state]
                                 for state in ("no_processing_budget", "no_funded_score",
                                               "control_rejected", "action_admitted")),
                             life["steps_lived"])
            witnessed = 0
            for step in life["trace"]:
                obs = step["info"]["observer"]
                self.assertEqual(len(obs["score_witness"]), obs["scored_options"])
                for item in obs["score_witness"]:
                    witnessed += 1
                    c = item["curiosity_bonus_computed"]
                    r = item["risk_penalty_computed"]
                    self.assertGreaterEqual(c, 0.0)
                    self.assertLessEqual(r, 0.0)
                    want_c = 0.0 if mode in (
                        "discard_curiosity_bonus", "discard_both_bonus_terms") else c
                    want_r = 0.0 if mode in (
                        "discard_risk_penalty", "discard_both_bonus_terms") else r
                    self.assertAlmostEqual(item["curiosity_bonus_applied"], want_c)
                    self.assertAlmostEqual(item["risk_penalty_applied"], want_r)
                    self.assertAlmostEqual(item["curiosity_risk_bonus"], want_c + want_r)
                    self.assertAlmostEqual(item["total_score"],
                                           item["base_return"] + want_c + want_r)
                    self.assertIsNotNone(item["first_forecast"])
                for phase in ("decision", "learning"):
                    for channel in ("energy", "vigilance"):
                        receipt = step["funding_phases"][phase]["accounting"][channel]
                        self.assertAlmostEqual(receipt["paid"], receipt["requested"])
                        self.assertAlmostEqual(receipt["unpaid"], 0.0)
                if step["dead"]:
                    self.assertFalse(any(step["funding_phases"]["learning"]["work"].values()))
            self.assertGreater(witnessed, 0)

    def test_component_masks_do_not_disable_personal_prediction_learning(self):
        for mode in MODES:
            life = run_life(self.genome, self.spec, 191, 90,
                            score_addend_mode=mode, observer_mind_digest=True)
            self.assertGreater(life["cognitive_accounting"]["learning_updates"], 0)
            self.assertTrue(life["outcome_model_sha256"])
            self.assertTrue(life["spatial_beliefs_sha256"])
            self.assertNotEqual(life["learning_intervention"], "discard_effects")


if __name__ == "__main__":
    unittest.main()
