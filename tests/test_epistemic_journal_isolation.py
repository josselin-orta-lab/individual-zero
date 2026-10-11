"""Adversarial no-oracle/no-technical-memory tests for MVP 1.3.1."""

from __future__ import annotations

import unittest

from lab.epistemic_guard import has_external_truth, project_lived_field
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.journal_views import AutobiographicalPolicy, JournalViews
from lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY


class EpistemicIsolationTests(unittest.TestCase):
    def test_hidden_nested_scenario_stays_in_full_journal_not_memory(self):
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        journal.append(event_id="scenario:1", causal_event={
            "emitter": "scenario", "kind": "external_input_received",
            "t_monde": 1, "attempt_ref": "step:1",
            "operation": "set_lethal_zone",
            "payload": {"position": {"x": 7, "y": 9}},
        })
        journal.append(event_id="goal:1", causal_event={
            "emitter": "stage4-runtime", "kind": "active_goal_changed",
            "t_monde": 1, "attempt_ref": "step:1", "cycle": 1,
            "data": {
                "before": None,
                "after": {"id": "goal:water", "goal_type": "drink",
                          "target": "water", "hidden_danger": [7, 9]},
                "future_scenario_schedule": [{"x": 7, "y": 9}],
            },
        })
        views.commit_autobiographical(
            t_monde=1, attempt_ref="step:1", event_refs=("goal:1",),
            policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
        )
        seen = views.autobiographical(policies={
            STAGE7_AUTOBIOGRAPHICAL_POLICY.version: STAGE7_AUTOBIOGRAPHICAL_POLICY,
        })
        self.assertEqual(seen[0]["data"]["after"], {
            "id": "goal:water", "goal_type": "drink", "target": "water",
        })
        self.assertEqual(len(seen), 1)
        self.assertNotIn("future_scenario_schedule", str(seen))
        self.assertNotIn("hidden_danger", str(seen))
        self.assertIn(b"set_lethal_zone", journal.canonical_bytes())
        self.assertIn(b"future_scenario_schedule", journal.canonical_bytes())
        self.assertTrue(journal.verify())

    def test_hidden_data_in_recognized_projection_is_rejected(self):
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        journal.append(event_id="goal:2", causal_event={
            "emitter": "stage4-runtime", "kind": "active_goal_changed",
            "t_monde": 1, "attempt_ref": "a",
            "data": {"after": {"id": "goal:1",
                               "oracle_canary": "SECRET"}}
        })
        before = journal.canonical_bytes()
        with self.assertRaisesRegex(ValueError, "hidden"):
            views.commit_autobiographical(
                t_monde=1, attempt_ref="a", event_refs=("goal:2",),
                policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
            )
        self.assertEqual(journal.canonical_bytes(), before)
        self.assertEqual(views.autobiographical(policies={}), ())

    def test_unknown_nested_fields_are_dropped_even_on_later_reads(self):
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        journal.append(event_id="st:1", causal_event={
            "kind": "s_t_published", "emitter": "stage4-runtime",
            "t_monde": 1, "attempt_ref": "a", "cycle": 1,
            "data": {"version": "s:1", "competitive_refs": ["c:1"],
                     "undocumented_detail": {"secret": "NOT_LIVED"}},
        })
        views.commit_autobiographical(
            t_monde=1, attempt_ref="a", event_refs=("st:1",),
            policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
        )
        output = views.autobiographical(policies={
            STAGE7_AUTOBIOGRAPHICAL_POLICY.version: STAGE7_AUTOBIOGRAPHICAL_POLICY,
        })
        self.assertEqual(output[0]["data"], {
            "version": "s:1", "competitive_refs": ["c:1"],
        })
        self.assertNotIn("NOT_LIVED", repr(output))

    def test_policy_cannot_request_technical_or_oracle_field(self):
        journal = HashChainedJournal()
        source = journal.append(event_id="command:policy", causal_event={
            "kind": "command_experienced", "t_monde": 1,
            "attempt_ref": "secret-attempt", "primitive": "attendre",
            "parameters": {}, "ground_truth": "NOT_A_MEMORY",
        })
        for key in ("attempt_ref", "event_hash", "ground_truth", "oracle_canary", "danger_zones"):
            policy = AutobiographicalPolicy(
                version="adversarial",
                allowed_fields_by_kind={"command_experienced": (key,)},
            )
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    policy.validate()
                with self.assertRaises(ValueError):
                    policy.project(source)
                with self.assertRaises(ValueError):
                    project_lived_field(
                        kind="command_experienced", field=key, value="untrusted",
                    )

    def test_custom_policy_cannot_promote_hidden_scenario_payload(self):
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        source = journal.append(event_id="technical:scenario", causal_event={
            "kind": "external_input_received",
            "emitter": "injected_scenario",
            "t_monde": 1, "attempt_ref": "a",
            "payload": {
                "operation": "set_lethal_zone",
                "position": {"x": 7, "y": 9},
            },
        })
        bypass = AutobiographicalPolicy(
            version="operator-forged-bypass",
            allowed_fields_by_kind={
                "external_input_received": ("t_monde", "payload"),
            },
        )
        original = journal.canonical_bytes()
        with self.assertRaisesRegex(ValueError, "technical"):
            bypass.validate()
        with self.assertRaisesRegex(ValueError, "technical"):
            bypass.project(source)
        with self.assertRaises(ValueError):
            views.commit_autobiographical(
                t_monde=1, attempt_ref="a",
                event_refs=("technical:scenario",), policy=bypass,
            )
        self.assertEqual(original, journal.canonical_bytes())
        self.assertEqual(views.autobiographical(policies={}), ())

    def test_custom_policy_cannot_promote_unapproved_source_field(self):
        for kind, field in (
            ("command_experienced", "payload"),
            ("world_transition_experienced", "scenario_schedule"),
            ("active_goal_changed", "world_snapshot"),
            ("observation_perceived", "hidden_geometry"),
            ("auto_segment_commit", "event_refs"),
            ("individual_death_confirmed", "reasons"),
        ):
            with self.subTest(kind=kind, field=field):
                policy = AutobiographicalPolicy(
                    version="forged",
                    allowed_fields_by_kind={kind: (field,)},
                )
                with self.assertRaises(ValueError):
                    policy.validate()
                with self.assertRaises(ValueError):
                    project_lived_field(
                        kind=kind, field=field, value={"x": 7, "y": 9},
                    )

    def test_reopened_journal_rejects_forged_technical_commit_policy(self):
        journal = HashChainedJournal()
        journal.append(event_id="technical:1", causal_event={
            "kind": "external_input_received", "t_monde": 1,
            "attempt_ref": "attempt:1",
            "payload": {"location": {"x": 5, "y": 8}},
        })
        journal.append(event_id="commit:1", causal_event={
            "kind": "auto_segment_commit", "t_monde": 1,
            "attempt_ref": "attempt:1", "event_refs": ["technical:1"],
            "filter_version": "malicious",
        })
        views = JournalViews(journal=journal)
        policy = AutobiographicalPolicy(
            version="malicious",
            allowed_fields_by_kind={
                "external_input_received": ("payload",),
            },
        )
        with self.assertRaisesRegex(ValueError, "technical"):
            views.autobiographical(policies={"malicious": policy})

    def test_reconstructed_commit_cannot_cross_steps_at_read_time(self):
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        journal.append(event_id="cmd:1", causal_event={
            "kind": "command_experienced", "attempt_ref": "a",
            "t_monde": 1, "primitive": "attendre", "parameters": {},
        })
        journal.append(event_id="commit:bad", causal_event={
            "kind": "auto_segment_commit", "attempt_ref": "b",
            "t_monde": 2, "event_refs": ["cmd:1"],
            "filter_version": "stage2-autobio-v1",
        })
        # Rehydrate the read interface from a journal containing a forged
        # technical commitment. In the live path only JournalViews can
        # legitimately register new commit IDs.
        views = JournalViews(journal=journal)
        policy = AutobiographicalPolicy(version="stage2-autobio-v1", allowed_fields_by_kind={
            "command_experienced": ("t_monde", "primitive", "parameters"),
        })
        with self.assertRaisesRegex(ValueError, "provenance"):
            views.autobiographical(policies={policy.version: policy})

    def test_external_truth_detected_at_arbitrary_depth(self):
        self.assertTrue(has_external_truth({
            "data": {"nested": [{"oracle_ground_truth": {"x": 3}}]},
        }))
        self.assertTrue(has_external_truth({
            "data": {"meta": {"source": "evaluation_bench"}},
        }))
        self.assertFalse(has_external_truth({
            "kind": "external_input_received",
            "payload": {"position": {"x": 3, "y": 4}},
        }))

    def test_independent_canonical_float_marker_preserves_lived_numeric_data(self):
        lived = project_lived_field(
            kind="active_goal_changed", field="data",
            value={"after": {"current_pressure": {
                "$f64": "0x1.0000000000000p-1",
            }}},
        )
        self.assertEqual(
            lived, {"after": {"current_pressure": {
                "$f64": "0x1.0000000000000p-1",
            }}},
        )
        with self.assertRaises(ValueError):
            project_lived_field(
                kind="active_goal_changed", field="data",
                value={"after": {"current_pressure": {
                    "$f64": "0x1.0000000000000p-1", "oracle_canary": "forged",
                }}},
            )

    def test_optional_lived_stream_uses_exact_same_nested_guard(self):
        from lab.compact_life_custody import BoundedLivedStream
        events = (
            ("goal:1", {
                "kind": "active_goal_changed", "t_monde": 1,
                "attempt_ref": "a", "cycle": 1,
                "data": {"after": {"id": "g", "oracle_canary": "FORBIDDEN"}},
            }),
            ("command:1", {
                "kind": "command_experienced", "t_monde": 1,
                "attempt_ref": "a", "primitive": "attendre",
                "parameters": {},
            }),
            ("world:1", {
                "kind": "world_transition_experienced", "t_monde": 1,
                "attempt_ref": "a", "position_after": {"x": 1, "y": 1},
                "body_after": {}, "effects": {},
            }),
        )
        cache = BoundedLivedStream(
            policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
            max_pending_events=4,
        )
        with self.assertRaisesRegex(ValueError, "hidden"):
            cache.commit_step(t_monde=1, attempt_ref="a", experienced=events)
        self.assertEqual(cache.pending_count, 0)
        self.assertEqual(cache.last_step, 0)

    def test_standalone_auditor_rejects_rehashed_nested_oracle_fact(self):
        journal = HashChainedJournal()
        journal.append(event_id="standalone:oracle-fault", causal_event={
            "kind": "technical_statement", "t_monde": 0,
            "data": {"meta": [{"oracle_ground_truth": {"x": 4}}]},
        })
        self.assertTrue(journal.verify())
        with self.assertRaisesRegex(ValueError, "oracle"):
            audit_export_bytes(journal.canonical_bytes())


if __name__ == "__main__":
    unittest.main()
