"""Development-level Stage12 detector evidence, never scientific acceptance."""
from __future__ import annotations

from copy import deepcopy
import unittest

from i0.modules.stage12_detectors import (
    LivedCognitiveObservation, Stage12DetectionPolicy, Stage12LivedDetectors,
)


def detector():
    return Stage12LivedDetectors(Stage12DetectionPolicy(
        version="stage12-evidence-dev-v1",
        window=12, stagnation_steps=4, stagnation_tolerance=0.05,
        loop_repetitions=3, loop_max_period=2,
        entropy_min_samples=4, entropy_warning_fraction=0.25,
        bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
    ))


def lived(t, *, context="st:same", option="option:idle", progress=None,
          outcome="unknown", agency="unknown", ref=None, origin="none"):
    return LivedCognitiveObservation(
        world_step=t, cycle=1, context_signature=context,
        active_goal_ref="goal:test", option_ref=option,
        progress_delta=progress, outcome=outcome, agency=agency,
        attribution_ref=ref, verification_origin=origin,
    )


class Stage12LivedDetectorsTests(unittest.TestCase):
    def test_unavailable_progress_is_unknown_not_pseudo_stagnation(self):
        owner = detector()
        for i in range(1, 7):
            outcome = owner.observe(lived(i))
        self.assertIsNone(outcome.stagnation)
        self.assertIsNone(outcome.reasoning_loop)
        self.assertTrue(outcome.low_context_entropy)
        self.assertIsNone(outcome.attribution_bias)

    def test_real_stagnation_without_claim_of_reasoning_loop(self):
        owner = detector()
        for i in range(1, 5):
            report = owner.observe(lived(
                i, option=f"distinct:{i}", context=f"st:{i}", progress=0,
            ))
        self.assertTrue(report.stagnation)
        self.assertIsNone(report.reasoning_loop)
        self.assertFalse(report.low_context_entropy)

    def test_repeated_two_cycle_reasoning_loop_detected_without_oracle(self):
        owner = detector()
        for i in range(1, 7):
            option = "option:a" if i % 2 else "option:b"
            report = owner.observe(lived(
                i, option=option, context=option, progress=0,
            ))
        self.assertTrue(report.stagnation)
        self.assertTrue(report.reasoning_loop)

    def test_entropy_is_not_a_consequence_or_reward(self):
        owner = detector()
        for i in range(1, 6):
            report = owner.observe(lived(i, progress=0.3))
        self.assertTrue(report.low_context_entropy)
        self.assertFalse(report.stagnation)

    def test_self_serving_and_self_blame_need_distinct_lived_verifications(self):
        for success_agent, failure_agent, expected in (
            ("self", "world", "self_serving_pattern"),
            ("world", "self", "self_blame_pattern"),
        ):
            with self.subTest(expected=expected):
                owner = detector()
                for i in range(1, 5):
                    success = i <= 2
                    report = owner.observe(lived(
                        i, context=f"st:{i}", progress=0.1,
                        outcome="success" if success else "failure",
                        agency=success_agent if success else failure_agent,
                        ref=f"lived:independent:{i}", origin="lived_physical",
                    ))
                self.assertEqual(report.attribution_bias, expected)
                self.assertEqual(report.verified_successes, 2)
                self.assertEqual(report.verified_failures, 2)
                before = owner.export_causal_state()
                with self.assertRaises(ValueError):
                    owner.observe(lived(
                        5, outcome="success", agency="self",
                        ref="lived:independent:1", origin="lived_physical",
                    ))
                self.assertEqual(owner.export_causal_state(), before)

    def test_oracle_verdict_and_unverified_credit_are_rejected(self):
        owner = detector()
        with self.assertRaises(ValueError):
            owner.observe(lived(
                1, outcome="success", agency="self",
                ref="oracle:1", origin="oracle",
            ))
        with self.assertRaises(ValueError):
            owner.observe(lived(1, outcome="success", agency="self"))
        self.assertEqual(owner.export_causal_state()["observations"], [])

    def test_export_restore_is_atomic_and_cannot_forget_verifications(self):
        owner = detector()
        for i in range(1, 6):
            owner.observe(lived(
                i, context=f"st:{i}", progress=0.1,
                outcome="success", agency="world",
                ref=f"independent:{i}", origin="independent_lived_modality",
            ))
        snapshot = owner.export_causal_state()
        rebuilt = detector()
        rebuilt.restore_causal_state(snapshot)
        self.assertEqual(rebuilt.export_causal_state(), snapshot)
        bad = deepcopy(snapshot)
        bad["observations"][-1]["cycle"] = 0
        with self.assertRaises(ValueError):
            rebuilt.restore_causal_state(bad)
        self.assertEqual(rebuilt.export_causal_state(), snapshot)
        with self.assertRaises(ValueError):
            rebuilt.restore_causal_state({
                **snapshot,
                "verified_attribution_refs": snapshot["verified_attribution_refs"][:-1],
            })
        self.assertEqual(rebuilt.export_causal_state(), snapshot)
        rebuilt.observe(lived(6, progress=None))
        with self.assertRaises(ValueError):
            rebuilt.restore_causal_state(snapshot)
        with self.assertRaises(ValueError):
            rebuilt.observe(lived(6, progress=0.5))


if __name__ == "__main__":
    unittest.main()
