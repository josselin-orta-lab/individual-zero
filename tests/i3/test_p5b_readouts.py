"""P5b effect readout gates and observer traces: development-only tests.

This file does NOT instantiate any new selection, validation or reserve world.
Readout gates do not change memory retention, learning payment or body law.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies
from i3.modules.body import W
from i3.modules.genome import generation_zero
from i3.modules.mind import Mind
from i3.runtime.life import run_life


class P5bReadoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = p2_ecologies.world_for("stable", "development", 18)
        cls.genome = generation_zero(761)

    def test_all_modes_preserve_original_paid_world_opportunity(self):
        modes = ("full", "blind_predictions", "blind_action_predictions",
                 "blind_sleep_forecast", "blind_sources", "blind_all")
        lives = [
            run_life(self.genome, self.spec, 1042, 70,
                     effect_readout=mode, observer_decision_diagnostics=True,
                     observer_mind_digest=True, keep_trace=True)
            for mode in modes
        ]
        self.assertEqual({x["manifest"]["world_sha256"] for x in lives},
                         {lives[0]["manifest"]["world_sha256"]})
        for mode, life in zip(modes, lives):
            self.assertEqual(life["effect_readout"], mode)
            self.assertEqual(life["cognitive_accounting"]["shortfall_steps"], 0)
            self.assertEqual(life["cognitive_accounting"]["pending_replays"], 0)
            self.assertGreater(life["cognitive_accounting"]["learning_updates"], 0)
            self.assertEqual(
                sum(life["observer_decision_diagnostics"][key]
                    for key in ("no_processing_budget", "no_funded_score",
                                "control_rejected", "action_admitted")),
                life["steps_lived"])
            self.assertGreaterEqual(life["observer_decision_diagnostics"]["offered_options"],
                                    life["observer_decision_diagnostics"]["scored_options"])
            for phase in ("offered", "scored"):
                self.assertEqual(
                    sum(life["observer_decision_diagnostics"][phase+"_families"].values()),
                    life["observer_decision_diagnostics"][phase+"_options"])
            self.assertGreater(life["observer_decision_diagnostics"]["offered_families"]["rest"],0)
            self.assertTrue(life["spatial_beliefs_sha256"])
            for step in life["trace"]:
                self.assertIn("observer", step["info"])
                if step["dead"]:
                    self.assertFalse(any(step["funding_phases"]["learning"]["work"].values()))
                for phase in ("decision", "learning"):
                    for ch in ("energy", "vigilance"):
                        bill = step["funding_phases"][phase]["accounting"][ch]
                        self.assertEqual(bill["unpaid"], 0)
                        self.assertAlmostEqual(bill["requested"], bill["paid"])

    def test_blind_predictions_and_source_gate_are_separate(self):
        m = Mind(self.genome, 12)
        m.effects.observe(("boire",), (0., -0.2, +20., 0., 0.))
        # Use a genuine personally learned result in each condition.
        from copy import deepcopy
        pred = deepcopy(m)
        pred.effect_readout = "blind_predictions"
        src = deepcopy(m)
        src.effect_readout = "blind_sources"
        both = deepcopy(m)
        both.effect_readout = "blind_all"
        self.assertTrue(m._read_source_sign(("boire",), W))
        self.assertTrue(pred._read_source_sign(("boire",), W))
        self.assertFalse(src._read_source_sign(("boire",), W))
        self.assertFalse(both._read_source_sign(("boire",), W))
        self.assertEqual(m._read_effect_prediction(("boire",))[0][W], 20.)
        self.assertEqual(src._read_effect_prediction(("boire",))[0][W], 20.)
        self.assertEqual(pred._read_effect_prediction(("boire",))[0], (0.,)*5)
        self.assertEqual(both._read_effect_prediction(("boire",))[0], (0.,)*5)
        for probe in (pred, src, both):
            self.assertEqual(probe.effects.stats, m.effects.stats)

    def test_action_and_sleep_predictions_are_independent_readout_gates(self):
        from copy import deepcopy
        from i3.modules.body import E, F, V
        m = Mind(self.genome, 21)
        m.effects.observe(("dormir",), (+4., -0.2, -0.4, 0., +5.))
        m.effects.observe(("boire",), (-0.2, -0.2, +19., 0., -0.1))
        action = deepcopy(m)
        action.effect_readout = "blind_action_predictions"
        sleep = deepcopy(m)
        sleep.effect_readout = "blind_sleep_forecast"
        both = deepcopy(m)
        both.effect_readout = "blind_predictions"
        self.assertEqual(action.effects.stats, sleep.effects.stats)
        self.assertEqual(action._read_plan_prediction(("boire",))[0], (0.,)*5)
        self.assertEqual(sleep._read_plan_prediction(("boire",))[0][2], 19.)
        self.assertEqual(both._read_plan_prediction(("boire",))[0], (0.,)*5)
        self.assertIsNotNone(action.drift()[1])
        self.assertIsNone(sleep.drift()[1])
        self.assertIsNone(both.drift()[1])
        self.assertEqual(m.effects.stats, action.effects.stats)
        self.assertEqual(m.effects.stats, sleep.effects.stats)

    def test_diagnostics_do_not_change_default_life(self):
        original = run_life(self.genome, self.spec, 99, 60)
        only_diagnostics = run_life(self.genome, self.spec, 99, 60,
                                    effect_readout="full",
                                    observer_decision_diagnostics=True)
        for key in ("terminal", "steps_lived", "actions", "trace_head",
                    "evidence_head", "final_body", "cognitive_accounting"):
            self.assertEqual(original[key], only_diagnostics[key])
        self.assertNotIn("observer_decision_diagnostics", original)
        self.assertNotIn("effect_readout", original)
        self.assertEqual(only_diagnostics["effect_readout"], "full")

    def test_fail_closed_bad_flags_and_world_cohorts(self):
        with self.assertRaises(ValueError):
            run_life(self.genome, self.spec, 32, 12,
                     effect_readout="inject_true_world_model")
        with self.assertRaises(TypeError):
            run_life(self.genome, self.spec, 32, 12,
                     observer_decision_diagnostics="yes")
        with patch.object(p2_ecologies, "world_for",
                          side_effect=AssertionError("P5b world opened")):
            # Pure construction and input guards do not open held-out worlds.
            with self.assertRaises(ValueError):
                Mind(self.genome, 88, effect_readout="oracle")


if __name__ == "__main__":
    unittest.main()
