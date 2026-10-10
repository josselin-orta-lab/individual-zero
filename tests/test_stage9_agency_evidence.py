"""Stage 9 §9.6/10.2: DC-09-backed P-47 evidence is not causal truth.

INV-01/03/07/25/27/33: sole owner, temporal barrier, exact snapshot,
provenance filtering, double-credit refusal and deterministic replay.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import unittest

from i0.contracts import PredictedConsequence
from i0.interfaces import PrimitiveCommand
from i0.modules.action_control import (
    ActionControl, ActionControlConfig, PreparedCommand, StaticSafetyFacts,
)
from i0.modules.agency_comparator import AgencyComparator, AgencyComparatorConfig
from i0.modules.causal_model import CausalModel, CausalModelConfig
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from test_action_control import capture_with_creature


def model():
    return CausalModel(CausalModelConfig(
        "agency-intake-v1", n1=2, n2=2, n_sec=2, m_sec=2,
    ))


def event(name="original", *, status="nonconforming", version="p47-test-v1"):
    return {
        "event_id": "dc09:" + name,
        "kind": "agency_comparison",
        "t_monde": 2,
        "data": {
            "option_ref": "option:a", "sent_t_monde": 1,
            "observed_t_monde": 2, "status": status,
            "attribution": "uncertain" if status != "conforming" else "self_compatible",
            "effects": [{
                "variable": "position_x",
                "status": status,
                "predicted": 4.0, "observed": 2.0 if status != "conforming" else 4.0,
                "precision": 0.0, "comparator_version": version,
            }],
        },
    }


class AgencyEvidenceTests(unittest.TestCase):
    def test_memory_closure_is_necessary_and_publication_is_deferred(self):
        m = model()
        e = event()
        self.assertEqual(m.published_agency_evidence(), ())
        self.assertEqual(m.ingest_closed_agency_comparisons(
            episode_ref="episode:1", event_refs=("unrelated",),
            autobiographical_events=(e,),
        ), ())
        admitted = m.ingest_closed_agency_comparisons(
            episode_ref="episode:1", event_refs=(e["event_id"],),
            autobiographical_events=(e,),
        )
        self.assertEqual(len(admitted), 1)
        self.assertEqual(admitted[0].source, "agency_comparator")
        self.assertEqual(admitted[0].event_ref, "dc09:original")
        self.assertEqual(admitted[0].episode_ref, "episode:1")
        self.assertEqual(m.published_agency_evidence(), ())
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.published_agency_evidence(), admitted)
        self.assertEqual(m.contingencies(), ())
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])

    def test_duplicate_event_cannot_be_credited_twice(self):
        m = model()
        e = event()
        m.ingest_closed_agency_comparisons(
            episode_ref="episode:1", event_refs=(e["event_id"],),
            autobiographical_events=(e,),
        )
        baseline = m.export_causal_state()
        with self.assertRaises(ValueError):
            m.ingest_closed_agency_comparisons(
                episode_ref="episode:2", event_refs=(e["event_id"],),
                autobiographical_events=(e,),
            )
        self.assertEqual(m.export_causal_state(), baseline)
        m.publish_causal_inference()
        with self.assertRaises(ValueError):
            m.ingest_closed_agency_comparisons(
                episode_ref="episode:3", event_refs=(e["event_id"],),
                autobiographical_events=(e,),
            )
        self.assertEqual(len(m.published_agency_evidence()), 1)

    def test_snapshot_restores_pending_and_published_exactly(self):
        left = model()
        e = event()
        left.ingest_closed_agency_comparisons(
            episode_ref="episode:1", event_refs=(e["event_id"],),
            autobiographical_events=(e,),
        )
        state = left.export_causal_state()
        twin = model()
        twin.restore_causal_state(state)
        self.assertEqual(twin.export_causal_state(), state)
        self.assertEqual(left.publish_causal_inference(), twin.publish_causal_inference())
        self.assertEqual(left.export_causal_state(), twin.export_causal_state())
        later = model()
        later.restore_causal_state(left.export_causal_state())
        self.assertEqual(later.published_agency_evidence(), left.published_agency_evidence())

    def test_forbidden_origin_or_incoherent_event_never_enters_snapshot(self):
        for change in (
            {"oracle_derived": True}, {"rollback_cancelled": True},
            {"counterfactual": True}, {"t_monde": 3},
        ):
            e = event()
            e.update(change)
            m = model()
            baseline = m.export_causal_state()
            with self.assertRaises(ValueError):
                m.ingest_closed_agency_comparisons(
                    episode_ref="episode:1", event_refs=(e["event_id"],),
                    autobiographical_events=(e,),
                )
            self.assertEqual(m.export_causal_state(), baseline)

    def test_agency_source_id_collision_cannot_launder_p47_evidence(self):
        original = event()
        for duplicate_kind in ("unrelated_telemetry", "agency_comparison"):
            for reversed_order in (False, True):
                with self.subTest(
                    kind=duplicate_kind, reversed=reversed_order,
                ):
                    m = model()
                    duplicate = {
                        **original,
                        "kind": duplicate_kind,
                    }
                    if duplicate_kind == "agency_comparison":
                        duplicate["data"] = {
                            **original["data"],
                            "option_ref": "option:contradictory",
                        }
                    variants = (
                        (duplicate, original)
                        if reversed_order else (original, duplicate)
                    )
                    baseline = m.export_causal_state()
                    with self.assertRaisesRegex(
                        ValueError,
                        "duplicate closed Memory agency event projection",
                    ):
                        m.ingest_closed_agency_comparisons(
                            episode_ref="episode:collision",
                            event_refs=(original["event_id"],),
                            autobiographical_events=variants,
                        )
                    self.assertEqual(m.export_causal_state(), baseline)
                    self.assertEqual(m.published_agency_evidence(), ())
                    # Invalid input must not consume the legitimate source.
                    (admitted,) = m.ingest_closed_agency_comparisons(
                        episode_ref="episode:valid",
                        event_refs=(original["event_id"],),
                        autobiographical_events=(original,),
                    )
                    self.assertEqual(admitted.event_ref, original["event_id"])

        # An event from another episode cannot invalidate a valid P-47
        # source and unrelated closed events do not make it ambiguous.
        m = model()
        outside = {
            **original,
            "event_id": "dc09:outside-closed-memory",
            "kind": "unrelated_telemetry",
        }
        other_closed_event = {
            "event_id": "dc09:unrelated",
            "kind": "unrelated_telemetry", "t_monde": 2,
        }
        (admitted,) = m.ingest_closed_agency_comparisons(
            episode_ref="episode:valid",
            event_refs=(original["event_id"], other_closed_event["event_id"]),
            autobiographical_events=(original, outside, other_closed_event),
        )
        self.assertEqual(admitted.event_ref, original["event_id"])

    def test_unversioned_legacy_projection_is_never_relabelled_p47(self):
        m = model()
        e = event()
        del e["data"]["effects"][0]["comparator_version"]
        self.assertEqual(m.ingest_closed_agency_comparisons(
            episode_ref="episode:1", event_refs=(e["event_id"],),
            autobiographical_events=(e,),
        ), ())
        self.assertEqual(m.export_causal_state()["pending_agency_evidence"], [])

    def test_missed_window_still_has_versioned_p47_provenance(self):
        comparator = AgencyComparator(AgencyComparatorConfig(
            version="p47-test-v1",
            tolerances={name: 0.0 for name in (
                "position_x", "position_y", "food", "water", "energy", "integrity",
            )},
            max_observation_window_steps=1,
        ))
        control = ActionControl(
            config=ActionControlConfig("mvp-v1.2.1", 15.0),
            safety_facts=StaticSafetyFacts(), protocol_mask=lambda _: False,
        )
        control.attach_agency_comparator(comparator)
        control.record_sent_prediction(
            prepared=PreparedCommand(
                command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
                source="decision", option_ref="option:1",
                predicted_consequences=(PredictedConsequence("position_x", 4.0, 0.0),),
                observation_window_steps=1,
            ), t_monde=1,
        )
        old = capture_with_creature(creature_direction=None)
        result = control.compare_capture(replace(old, t_monde=3))
        self.assertEqual(result.status, "indeterminable")
        self.assertEqual(result.effects[0]["status"], "expected_effect_missing")
        self.assertEqual(result.effects[0]["comparator_version"], "p47-test-v1")

    def test_real_stage9_path_from_action_control_via_memory_to_causal_model(self):
        # Integrated P-47 + DC-09 + phase-5 acceptance, no injected evidence.
        runtime = build_stage9_reference_runtime()
        for _ in range(12):
            self.assertEqual(runtime.run_step().execution_status, "applied")
        reports = runtime.causal_model.published_agency_evidence()
        self.assertGreater(len(reports), 0)
        self.assertEqual(len({v.event_ref for v in reports}), len(reports))
        self.assertTrue(all(v.source == "agency_comparator" for v in reports))
        self.assertTrue(all(v.episode_ref.startswith("episode:") for v in reports))
        self.assertTrue(all(
            effect[-1] == "p47-stage9-reference-v1"
            for report in reports for effect in report.effects
        ))
        self.assertEqual(runtime.causal_model.export_causal_state()["causal_interventions"], [])
        self.assertIn(
            b"causal_agency_evidence_admitted", runtime.journal.canonical_bytes()
        )

    def test_runtime_owns_only_causal_model_and_old_goldens_remain_separate(self):
        runtime = build_stage9_reference_runtime()
        self.assertEqual(
            sum(o.owner_id == "causal_model" for o in runtime.causal_owners), 1
        )
        self.assertEqual(runtime.causal_model.published_agency_evidence(), ())
        self.assertFalse(hasattr(runtime, "agency_evidence_cache"))


if __name__ == "__main__":
    unittest.main()
