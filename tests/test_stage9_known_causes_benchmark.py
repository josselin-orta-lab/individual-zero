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
        self.assertIsNone(result.observed_rate)
        self.assertIsNone(result.passes)
        self.assertEqual(result.unverified_false_refs, ("false:canary",))
        self.assertEqual(m.export_causal_state(), original)

    def test_null_world_requires_real_applied_drink_and_world_transition(self):
        from dataclasses import replace
        from i0.interfaces import PrimitiveCommand
        from lab.journal import HashChainedJournal
        from lab.stage4_reference_fixture import build_stage4_reference_runtime
        from lab.world import Position, WorldBody, WorldLayout

        config = replace(
            build_stage4_reference_runtime().world.config,
            version="stage9-null-water-audit-v1", drink_water_gain=0.0,
        )
        world = WorldBody(
            config=config,
            layout=WorldLayout(water_sources=frozenset({Position(2, 2)})),
        )
        journal = HashChainedJournal()
        model_under_audit = model()
        hypothesized(model_under_audit)

        def audit():
            return audit_superstitious_rules(
                causal_model=model_under_audit,
                eligible_known_false_refs=("causal:hydration", "unsupported"),
                preregistered_max_rate=None,
                physical_journal=journal,
                known_false_world=config,
            )

        self.assertIsNone(audit().observed_rate)
        journal.append(
            event_id="send:1",
            causal_event={
                "kind": "command_experienced", "primitive": "boire",
                "attempt_ref": "attempt:1", "t_monde": 1,
            },
        )
        self.assertIsNone(audit().observed_rate)
        transition = world.apply(PrimitiveCommand("boire"), t_monde=1)
        journal.append(
            event_id="transition:1",
            causal_event={
                "kind": "world_transition_experienced",
                "attempt_ref": "attempt:1", "t_monde": 1,
                "effects": dict(transition.effects),
                "body_after": transition.body_after.as_dict(),
            },
        )
        result = audit()
        self.assertEqual(result.audited_false_refs, ("causal:hydration",))
        self.assertEqual(result.physical_witness_refs, ("transition:1",))
        self.assertEqual(result.unverified_false_refs, ("unsupported",))
        self.assertEqual(result.observed_rate, 0.0)
        self.assertIsNone(result.passes)
        self.assertEqual(result, audit())
        with self.assertRaises(ValueError):
            audit_superstitious_rules(
                causal_model=model_under_audit,
                eligible_known_false_refs=("causal:hydration",),
                preregistered_max_rate=0.0,
                physical_journal=journal,
            )

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
        self.assertIsNone(result.observed_rate)
        self.assertIsNone(result.passes)
        self.assertEqual(result.unverified_false_refs, ("causal:food-energy",))


if __name__ == "__main__":
    unittest.main()
