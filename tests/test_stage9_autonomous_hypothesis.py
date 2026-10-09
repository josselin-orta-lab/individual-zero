"""Stage 9: autonomous hypothesis review from actually lived food controls.

Spec v1.2.1 EN §§13.2, 13.4, DC-05, P-35, INV-03/25/27/33.
An observed correlation can acquire explicit alternatives only from genuine,
independent physical DC-09 transitions and a preregistered comparison pair.
No intervention, exploratory motive or unsafe test is manufactured here.
"""
from __future__ import annotations

import unittest

from i0.modules.causal_model import CausalModel, CausalModelConfig
from i0.modules.causal_lifecycle import CausalObservation


def model() -> CausalModel:
    return CausalModel(CausalModelConfig(
        version="stage9-autonomous-hypothesis-v1",
        n1=2, n2=2, n_sec=2, m_sec=2,
        food_control_pairs=(("berry_b", "berry_a"),),
    ))


def lived_meal(m: CausalModel, *, t: int, food: str, after: float) -> None:
    m.record_applied_food_exposure(
        t_monde=t, resource_kind=food, option_ref=f"option:{t}",
        motive_ref="goal:food", integrity_before=100.0,
    )
    m.observe_followup_capture(t_monde=t + 1, integrity=after)
    events = (
        {
            "event_id": f"command:{t}", "kind": "command_experienced",
            "t_monde": t, "primitive": "manger",
            "parameters": {"target": food},
        },
        {
            "event_id": f"transition:{t}",
            "kind": "world_transition_experienced",
            "t_monde": t,
            "body_after": {"integrity": after},
            "effects": {"ate": food},
        },
    )
    m.ingest_closed_autobiographical_episode(
        episode_ref=f"episode:{t}",
        event_refs=(f"command:{t}", f"transition:{t}"),
        autobiographical_events=events,
    )


def publish_physical_correlation(m: CausalModel) -> None:
    lived_meal(m, t=1, food="berry_b", after=90.0)
    lived_meal(m, t=3, food="berry_b", after=80.0)
    lived_meal(m, t=5, food="berry_a", after=100.0)
    changes = m.publish_causal_inference()
    assert [(x.contingency_ref, x.after) for x in changes] == [
        ("toxic:berry_b", "correlation_observee")
    ]
    m.publish()


class AutonomousHypothesisTests(unittest.TestCase):
    def test_explicit_preregistered_lived_control_promotes_next_publication(self):
        m = model()
        publish_physical_correlation(m)
        self.assertEqual(m.get("toxic:berry_b").causal_status, "correlation_observee")
        self.assertEqual(m.export_causal_state()["causal_reviews"], [])
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])
        (change,) = m.publish_causal_inference()
        self.assertEqual(change.before, "correlation_observee")
        self.assertEqual(change.after, "hypothese_causale")
        self.assertEqual(change.protocol, "matched_alternatives")
        reviews = m.export_causal_state()["causal_reviews"]
        self.assertEqual(len(reviews), 1)
        self.assertIn("episode:5", reviews[0])
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.get("toxic:berry_b").causal_status, "hypothese_causale")

    def test_observational_review_replays_exactly_from_snapshot(self):
        original = model()
        publish_physical_correlation(original)
        checkpoint = original.export_causal_state()
        twin = model()
        twin.restore_causal_state(checkpoint)
        self.assertEqual(checkpoint, twin.export_causal_state())
        self.assertEqual(
            original.publish_causal_inference(), twin.publish_causal_inference()
        )
        self.assertEqual(original.export_causal_state(), twin.export_causal_state())

    def test_unlived_control_claim_cannot_produce_autonomous_review(self):
        m = model()
        lived_meal(m, t=1, food="berry_b", after=90.0)
        lived_meal(m, t=3, food="berry_b", after=80.0)
        m.integrate_causal_observation(CausalObservation(
            identifier=(
                "causal-control:berry_b:"
                "causal-observation:episode:invented:transition:invented"
            ),
            contingency_ref="toxic:berry_b", predicate="toxic_item",
            subject_ref="berry_b", application_context="global",
            observation_context="food_consumption",
            episode_ref="episode:invented",
            observation_ref="transition:invented", observed_step=9,
            cause_present=False, effect_present=False,
            controlled_variables=(("primitive", "manger"),),
        ))
        self.assertEqual(
            [change.after for change in m.publish_causal_inference()],
            ["correlation_observee"],
        )
        m.publish()
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.get("toxic:berry_b").causal_status, "correlation_observee")
        self.assertEqual(m.export_causal_state()["causal_reviews"], [])

    def test_incidental_food_comparison_does_not_create_unsafe_test_option(self):
        m = model()
        publish_physical_correlation(m)
        m.publish_causal_inference()
        state = m.export_causal_state()
        self.assertEqual(state["pending_causal_interventions"], [])
        self.assertEqual(state["causal_interventions"], [])
        self.assertEqual(state["pending_causal_reviews"], [])
        # Separate safety use may already prohibit further consumption.
        self.assertEqual(m.get("toxic:berry_b").safety_status,
                         "etabli_pour_securite")


if __name__ == "__main__":
    unittest.main()
