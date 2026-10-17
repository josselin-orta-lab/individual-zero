"""GA-01/GA-04 first-person agency: no P-47/outcome-label circularity."""
from __future__ import annotations
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.stage12_goal_agency import (
    GOAL_AGENCY_VERSION, GoalAgencyService,
)
from test_action_control import capture_with_creature


def capture(*, step=1, berries=2, food=60.0):
    base = capture_with_creature(creature_direction=None)
    return replace(
        base, t_monde=step,
        inventory={"berry_a": berries, "berry_b": 0},
        body={**base.body, "food": food},
    )


def prepare(*, measure="food", command=None):
    service = GoalAgencyService()
    value = service.preregister(
        assessment_ref="assessment:1", intent_ref="goal-intent:1",
        life_id="life:1", goal_ref="goal:food", option_ref="option:1",
        command_hash="digest:1", world_step=1, measure=measure,
        command=command or PrimitiveCommand("manger", {"target": "berry_a"}),
        capture=capture(),
    )
    return service, value


class FirstPersonGoalAgencyTests(unittest.TestCase):
    def test_self_requires_separately_witnessed_goal_relevant_efference(self):
        service, commitment = prepare()
        self.assertEqual(commitment.policy_version, GOAL_AGENCY_VERSION)
        result = service.evaluate(
            capture=capture(step=2, berries=1, food=60.0),
            world_step=2, cue_ref="perception:2", paid=True,
        )
        self.assertEqual(result.subjective_agency, "self")
        self.assertEqual(result.intent_ref, commitment.intent_ref)
        self.assertIsNone(service.pending)
        self.assertIsNone(service.evaluate(
            capture=capture(step=2, berries=1), world_step=2,
            cue_ref="perception:2", paid=True,
        ))

    def test_no_food_gain_is_not_world_blame(self):
        service, _ = prepare()
        result = service.evaluate(
            capture=capture(step=2, berries=2, food=30.0),
            world_step=2, cue_ref="perception:2", paid=True,
        )
        self.assertEqual(result.subjective_agency, "unknown")

    def test_result_gain_alone_is_not_self_judgement(self):
        service, _ = prepare(measure="water")
        result = service.evaluate(
            capture=capture(step=2, berries=1, food=90.0),
            world_step=2, cue_ref="perception:2", paid=True,
        )
        self.assertEqual(result.subjective_agency, "unknown")

    def test_refused_uc_is_unavailable_not_unknown(self):
        service, _ = prepare()
        result = service.evaluate(
            capture=capture(step=2, berries=1),
            world_step=2, cue_ref=None, paid=False,
        )
        self.assertEqual(result.subjective_agency, "unavailable")
        self.assertIsNone(result.cue_ref)

    def test_missing_or_delayed_capture_is_unavailable(self):
        service, _ = prepare()
        result = service.evaluate(
            capture=None, world_step=3, cue_ref=None, paid=True,
        )
        self.assertEqual(result.subjective_agency, "unavailable")

    def test_double_commit_refused_and_pending_survives(self):
        service, _ = prepare()
        before = service.export_causal_state()
        with self.assertRaises(ValueError):
            service.preregister(
                assessment_ref="duplicate:1", intent_ref="goal-intent:2",
                life_id="life:1", goal_ref="goal:food", option_ref="option:2",
                command_hash="digest:2", world_step=1, measure="food",
                command=PrimitiveCommand("manger", {"target": "berry_a"}),
                capture=capture(),
            )
        self.assertEqual(service.export_causal_state(), before)

    def test_exact_cold_owner_restore_and_no_historic_rewind(self):
        source, _ = prepare()
        image = source.export_causal_state()
        fresh = GoalAgencyService()
        fresh.restore_causal_state(image)
        self.assertEqual(fresh.export_causal_state(), image)
        with self.assertRaises(ValueError):
            fresh.restore_causal_state(image)
        result = fresh.evaluate(
            capture=capture(step=2, berries=1),
            world_step=2, cue_ref="perception:2", paid=True,
        )
        self.assertEqual(result.subjective_agency, "self")

    def test_mutated_image_rejected_without_partial_install(self):
        service, _ = prepare()
        image = service.export_causal_state()
        image["pending_commitment"]["inventory_before"] = -1
        fresh = GoalAgencyService()
        before = fresh.export_causal_state()
        with self.assertRaises(ValueError):
            fresh.restore_causal_state(image)
        self.assertEqual(fresh.export_causal_state(), before)

    def test_prediction_is_not_a_service_input(self):
        service, _ = prepare()
        self.assertNotIn("prediction_status", service.export_causal_state())
        self.assertNotIn("outcome", service.export_causal_state())
        self.assertNotIn("p47_attribution", service.export_causal_state())


if __name__ == "__main__":
    unittest.main()
