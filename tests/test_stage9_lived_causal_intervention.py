"""Stage-9 lived causal intervention producer (EN MVP 13.2, P-35, P-47).

The verification path requires an actually applied decision, next Perception
capture, DC-09 closed physical command + transition, and a separately
published AgencyComparator report. A typed claim alone is never evidence.
"""
from __future__ import annotations

import unittest

from i0.modules.causal_model import CausalModel
from test_stage9_causal_test_targets import hypothesis, model


def physical_episode(*, step, after, position):
    return (
        {
            "event_id": f"command:{step}",
            "kind": "command_experienced",
            "t_monde": step, "primitive": "boire", "parameters": {},
        },
        {
            "event_id": f"transition:{step}",
            "kind": "world_transition_experienced",
            "t_monde": step, "effects": {"drank": True},
            "body_after": {"water": after},
            "position_after": {"x": position[0], "y": position[1]},
        },
    )


def agency_episode(*, step, option_ref, after, status="conforming"):
    return {
        "event_id": f"agency:{step}",
        "kind": "agency_comparison",
        "t_monde": step + 1,
        "data": {
            "option_ref": option_ref,
            "sent_t_monde": step,
            "observed_t_monde": step + 1,
            "status": status,
            "attribution": (
                "self_compatible" if status == "conforming" else "uncertain"
            ),
            "effects": [{
                "variable": "water", "status": status,
                "predicted": 60.0, "observed": after,
                "precision": 0.0, "comparator_version": "p47-test-v1",
            }],
        },
    }


def evidence_path(
    m: CausalModel, *, step: int, position=(2, 2),
    before=20.0, after=60.0, option_ref=None, close=True,
    comparator=True, compare_status="conforming",
):
    option_ref = option_ref or f"option:drink:{step}"
    (row,) = m.record_applied_causal_action(
        t_monde=step, option_ref=option_ref,
        motive_type="active_goal", motive_ref="goal:drink",
        primitive="boire", current_water_source=True,
        position=position, water_before=before,
    )
    m.observe_causal_action_followup(t_monde=step + 1, water=after)
    if close:
        physical = physical_episode(step=step, after=after, position=position)
        (verified,) = m.ingest_closed_causal_action_episode(
            episode_ref=f"episode:physical:{step}",
            event_refs=tuple(x["event_id"] for x in physical),
            autobiographical_events=physical,
        )
        assert verified.identifier == row.identifier
    if comparator:
        agency = agency_episode(
            step=step, option_ref=option_ref,
            after=after, status=compare_status,
        )
        m.ingest_closed_agency_comparisons(
            episode_ref=f"episode:comparison:{step}",
            event_refs=(agency["event_id"],),
            autobiographical_events=(agency,),
        )
    return row


class LivedCausalInterventionProducerTests(unittest.TestCase):
    def test_full_lived_path_requires_previous_comparator_publication(self):
        m = model()
        hypothesis(m)
        evidence_path(m, step=10)
        self.assertEqual(m.promote_lived_causal_interventions(), ())
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])
        self.assertEqual(m.publish_causal_inference(), ())
        (trial,) = m.promote_lived_causal_interventions()
        self.assertEqual(trial.contingency_ref, "causal:hydration")
        self.assertEqual(trial.observation_ref, "transition:10")
        self.assertEqual(trial.episode_ref, "episode:comparison:10")
        self.assertEqual(trial.comparator_status, "conforming")
        self.assertEqual(trial.context_signature, "water_source:2,2")
        self.assertTrue(trial.observed_effect)
        self.assertEqual(m.promote_lived_causal_interventions(), ())
        self.assertEqual(
            [v.after for v in m.publish_causal_inference()],
            ["testee_par_intervention"],
        )
        self.assertEqual(len(m.export_causal_state()["causal_interventions"]), 1)

    def test_second_physical_context_needed_for_n2(self):
        m = model()
        hypothesis(m)
        for step, position in ((10, (2, 2)), (20, (2, 2))):
            evidence_path(m, step=step, position=position)
            m.publish_causal_inference()
            m.promote_lived_causal_interventions()
            m.publish_causal_inference()
        self.assertEqual(
            m.get("causal:hydration").causal_status,
            "testee_par_intervention",
        )
        evidence_path(m, step=30, position=(4, 4))
        m.publish_causal_inference()
        m.promote_lived_causal_interventions()
        self.assertEqual(
            [v.after for v in m.publish_causal_inference()],
            ["etablie"],
        )
        self.assertEqual(len(m.export_causal_state()["causal_interventions"]), 3)

    def test_no_credit_from_comparator_only_or_open_action(self):
        m = model()
        hypothesis(m)
        comparison = agency_episode(
            step=10, option_ref="option:drink:10", after=60.0,
        )
        m.ingest_closed_agency_comparisons(
            episode_ref="episode:comparison:10",
            event_refs=(comparison["event_id"],),
            autobiographical_events=(comparison,),
        )
        m.publish_causal_inference()
        self.assertEqual(m.promote_lived_causal_interventions(), ())
        self.assertEqual(m.get("causal:hydration").causal_status, "hypothese_causale")
        # Even an actually recorded decision cannot count without a closed
        # matching physical transition.
        m.record_applied_causal_action(
            t_monde=10, option_ref="option:drink:10",
            motive_type="active_goal", motive_ref="goal:drink",
            primitive="boire", current_water_source=True,
            position=(2, 2), water_before=20.0,
        )
        m.observe_causal_action_followup(t_monde=11, water=60.0)
        self.assertEqual(m.promote_lived_causal_interventions(), ())

    def test_inconsistent_physical_telemetry_prevents_intervention(self):
        m = model()
        hypothesis(m)
        evidence_path(m, step=10, close=False)
        # A forged body result in a closed event is not the captured value.
        events = physical_episode(step=10, after=45.0, position=(2, 2))
        self.assertEqual(m.ingest_closed_causal_action_episode(
            episode_ref="episode:physical:10",
            event_refs=tuple(v["event_id"] for v in events),
            autobiographical_events=events,
        ), ())
        m.publish_causal_inference()
        self.assertEqual(m.promote_lived_causal_interventions(), ())

    def test_snapshot_preserves_pending_physical_and_comparator_provenance(self):
        left = model()
        hypothesis(left)
        evidence_path(left, step=10)
        original = left.export_causal_state()
        twin = model()
        twin.restore_causal_state(original)
        self.assertEqual(original, twin.export_causal_state())
        self.assertEqual(left.publish_causal_inference(), twin.publish_causal_inference())
        self.assertEqual(
            left.promote_lived_causal_interventions(),
            twin.promote_lived_causal_interventions(),
        )
        self.assertEqual(left.export_causal_state(), twin.export_causal_state())
        self.assertEqual(left.publish_causal_inference(), twin.publish_causal_inference())
        self.assertEqual(left.export_causal_state(), twin.export_causal_state())

    def test_unconfigured_model_does_not_record_normal_drinking(self):
        from i0.modules.causal_model import CausalModel, CausalModelConfig
        m = CausalModel(CausalModelConfig("no-preregistered-test-v1", 2, 2, 2, 2))
        self.assertEqual(m.record_applied_causal_action(
            t_monde=10, option_ref="option:drink:10",
            motive_type="active_goal", motive_ref="goal:drink",
            primitive="boire", current_water_source=True,
            position=(2, 2), water_before=20.0,
        ), ())
        self.assertEqual(m.export_causal_state()["lived_causal_actions"], [])

    def test_refutation_uses_real_missing_water_effect(self):
        m = model()
        hypothesis(m)
        for step, position in ((10, (2, 2)), (20, (4, 4))):
            evidence_path(m, step=step, position=position)
            m.publish_causal_inference()
            m.promote_lived_causal_interventions()
            m.publish_causal_inference()
        self.assertEqual(m.get("causal:hydration").causal_status, "etablie")
        evidence_path(
            m, step=30, position=(6, 6), before=20.0,
            after=20.0, compare_status="nonconforming",
        )
        m.publish_causal_inference()
        (missing,) = m.promote_lived_causal_interventions()
        self.assertFalse(missing.observed_effect)
        self.assertEqual(
            [c.after for c in m.publish_causal_inference()],
            ["hypothese_causale"],
        )


if __name__ == "__main__":
    unittest.main()
