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


def lived_meal(
    m: CausalModel, *, t: int, food: str, after: float,
    position: tuple[int, int] = (2, 2),
) -> None:
    actual_step = t + 1
    # A genuine no-food same-site control, rather than a hidden WorldBody
    # damage label, is now prerequisite for harmful food causal observations.
    m.record_applied_ambient_integrity_control(
        t_monde=t, option_ref=f"option:wait:{t}",
        position=position, integrity_before=100.0,
    )
    m.observe_followup_capture(t_monde=actual_step, integrity=100.0)
    control = (
        {"event_id": f"wait-command:{t}", "kind": "command_experienced",
         "t_monde": t, "primitive": "attendre", "parameters": {}},
        {"event_id": f"wait-transition:{t}",
         "kind": "world_transition_experienced", "t_monde": t,
         "position_after": {"x": position[0], "y": position[1]},
         "body_after": {"integrity": 100.0},
         "effects": {"rest": "attendre"}},
    )
    assert m.ingest_closed_autobiographical_episode(
        episode_ref=f"episode:wait:{t}",
        event_refs=tuple(row["event_id"] for row in control),
        autobiographical_events=control,
    ) == ()
    m.record_applied_food_exposure(
        t_monde=actual_step, resource_kind=food, option_ref=f"option:{t}",
        motive_ref="goal:food", integrity_before=100.0,
        position_before=position,
        body_before={"energy":50.0, "food":60.0,
                     "water":50.0, "integrity":100.0},
    )
    m.observe_followup_capture(t_monde=actual_step + 1, integrity=after)
    events = (
        {
            "event_id": f"command:{t}", "kind": "command_experienced",
            "t_monde": actual_step, "primitive": "manger",
            "parameters": {"target": food},
        },
        {
            "event_id": f"transition:{t}",
            "kind": "world_transition_experienced",
            "t_monde": actual_step,
            "position_after": {"x": position[0], "y": position[1]},
            "body_after": {"integrity": after},
            "effects": {"ate": food},
        },
    )
    m.ingest_closed_autobiographical_episode(
        episode_ref=f"episode:{t}",
        event_refs=(f"command:{t}", f"transition:{t}"),
        autobiographical_events=events,
    )


def publish_ambiguous_food_history(m: CausalModel) -> None:
    """Exercise repeated harmful food plus a genuine benign control meal.

    Under issue #89 the harmful treatment arms remain associational because
    hidden synchronized causes are observationally equivalent. The actually
    consumed benign control is retained, but cannot manufacture treated
    observations that I0 never earned.
    """
    lived_meal(m, t=1, food="berry_b", after=90.0, position=(2, 2))
    lived_meal(m, t=3, food="berry_b", after=80.0, position=(3, 2))
    lived_meal(m, t=5, food="berry_b", after=70.0, position=(4, 2))
    lived_meal(m, t=7, food="berry_a", after=100.0, position=(5, 2))
    assert m.publish_causal_inference() == ()
    assert m.publish() == ()


class AutonomousHypothesisTests(unittest.TestCase):
    def test_repeated_harm_and_lived_control_do_not_create_food_causal_hypothesis(self):
        m = model()
        publish_ambiguous_food_history(m)
        fact = m.get("toxic:berry_b")
        self.assertIsNotNone(fact)
        self.assertEqual(fact.causal_status, "aucun")
        self.assertEqual(fact.safety_status, "aucun")
        self.assertEqual(m.export_causal_state()["causal_reviews"], [])
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])
        self.assertEqual(m.publish_causal_inference(), ())

    def test_ambiguous_food_history_replays_exactly_from_snapshot(self):
        original = model()
        publish_ambiguous_food_history(original)
        checkpoint = original.export_causal_state()
        twin = model()
        twin.restore_causal_state(checkpoint)
        self.assertEqual(checkpoint, twin.export_causal_state())
        self.assertEqual(original.publish_causal_inference(), ())
        self.assertEqual(twin.publish_causal_inference(), ())
        self.assertEqual(original.export_causal_state(), twin.export_causal_state())

    def test_unlived_control_claim_cannot_resurrect_withheld_treatment(self):
        m = model()
        publish_ambiguous_food_history(m)
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
        self.assertEqual(m.publish_causal_inference(), ())
        self.assertEqual(m.get("toxic:berry_b").causal_status, "aucun")
        self.assertEqual(m.export_causal_state()["causal_reviews"], [])

    def test_ambiguous_food_history_creates_no_unsafe_test_or_safety_veto(self):
        m = model()
        publish_ambiguous_food_history(m)
        state = m.export_causal_state()
        self.assertEqual(state["pending_causal_interventions"], [])
        self.assertEqual(state["causal_interventions"], [])
        self.assertEqual(state["pending_causal_reviews"], [])
        self.assertEqual(m.get("toxic:berry_b").safety_status, "aucun")


if __name__ == "__main__":
    unittest.main()
