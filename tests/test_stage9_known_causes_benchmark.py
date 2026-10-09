"""Known-cause Stage-9 lab probes: external truth never enters cognition."""
from __future__ import annotations

import unittest
from dataclasses import replace

from i0.modules.causal_lifecycle import CausalIntervention
from lab.stage9_known_causes_benchmark import (
    run_known_cause_probes, audit_superstitious_rules,
)
from test_stage9_causal_lifecycle import model, hypothesized, trial, publish_trial


class KnownCausesBenchmarkTests(unittest.TestCase):
    def test_physical_world_controls_have_traceable_expected_attributions(self):
        metrics = run_known_cause_probes()
        rows = {row.identifier: row for row in metrics.cases}
        self.assertEqual(len(rows), 7)
        self.assertEqual(
            (rows["drink-at-water"].comparator_status,
             rows["drink-at-water"].attribution),
            ("conforming", "self_compatible"),
        )
        self.assertEqual(rows["open-east-move"].attribution, "self_compatible")
        self.assertEqual(
            (rows["visible-obstacle"].comparator_status,
             rows["visible-obstacle"].attribution),
            ("nonconforming", "world_justified"),
        )
        self.assertEqual(rows["creature-day-control"].attribution, "self_compatible")
        self.assertEqual(
            (rows["creature-night-harm"].comparator_status,
             rows["creature-night-harm"].attribution),
            ("nonconforming", "world_justified"),
        )
        self.assertEqual(rows["hidden-danger-harm"].attribution, "uncertain")
        self.assertEqual(rows["creature-night-harm"].attribution, "world_justified")
        self.assertEqual(rows["two-visible-creatures-night"].attribution, "uncertain")
        self.assertEqual(metrics.ground_truthed_cases, 6)
        self.assertEqual(metrics.correct_links, 4)
        self.assertEqual(metrics.uncertain_cases, 2)
        self.assertEqual(metrics.false_self_links, 0)
        self.assertEqual(metrics.accuracy, 4 / 6)
        self.assertEqual(metrics, run_known_cause_probes())

    def test_attribution_truth_is_not_given_to_comparator(self):
        metrics = run_known_cause_probes()
        night = next(
            row for row in metrics.cases
            if row.identifier == "creature-night-harm"
        )
        self.assertEqual(night.known_cause, "world")
        self.assertTrue(night.correct_link)
        self.assertFalse(night.uncertain)
        self.assertFalse(night.false_self_link)

    def test_no_preregistered_superstition_threshold_means_no_verdict(self):
        m = model()
        hypothesized(m)
        result = audit_superstitious_rules(
            causal_model=m,
            eligible_known_false_refs=(),
            preregistered_max_rate=None,
        )
        self.assertIsNone(result.observed_rate)
        self.assertIsNone(result.passes)
        for threshold in (-0.1, 1.1, float("nan"), True):
            with self.subTest(threshold=threshold):
                with self.assertRaises(ValueError):
                    audit_superstitious_rules(
                        causal_model=m,
                        eligible_known_false_refs=("false:canary",),
                        preregistered_max_rate=threshold,
                    )

    def test_known_false_canary_is_read_only_and_threshold_explicit(self):
        m = model()
        hypothesized(m)
        original = m.export_causal_state()
        result = audit_superstitious_rules(
            causal_model=m,
            eligible_known_false_refs=("false:canary", "false:canary"),
            preregistered_max_rate=0.0,
        )
        self.assertEqual(result.audited_false_refs, ("false:canary",))
        self.assertEqual(result.observed_rate, 0.0)
        self.assertTrue(result.passes)
        self.assertEqual(m.export_causal_state(), original)

    def test_known_true_established_contingency_is_not_a_false_canary(self):
        m = model()
        hypothesized(m)
        publish_trial(m, trial(10, context="zone1"))
        publish_trial(m, trial(11, context="zone2"))
        self.assertEqual(m.get("causal:food-energy").causal_status, "etablie")
        result = audit_superstitious_rules(
            causal_model=m,
            eligible_known_false_refs=("causal:food-energy",),
            preregistered_max_rate=None,
        )
        # In this controlled calculation, the caller explicitly supplies the
        # false-canary set; this is NOT a claim that the tested rule is false.
        self.assertEqual(result.observed_rate, 1.0)
        self.assertIsNone(result.passes)


if __name__ == "__main__":
    unittest.main()
