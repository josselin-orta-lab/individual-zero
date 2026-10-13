"""GA-08 pure kernel tests, not evidence of an autonomous world judgement."""
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import PerceivedCell, PerceptualCapture
from i0.modules.stage12_spatial_goal_evidence import (
    preregister_spatial_subgoal, evaluate_spatial_goal_outcome,
    judge_spatial_agency, SpatialGoalPrecommit,
)


def perceive(*, time=1, x=2, y=2, blocked=False, visible=True, water=True):
    return PerceptualCapture(
        t_monde=time, x=x, y=y,
        body={"water": 20.0, "food": 40.0, "energy": 60.0, "integrity": 90.0},
        current_water_source=False, current_resources=(),
        adjacent=(PerceivedCell(
            direction="east", x=3, y=2, passable=not blocked,
            water_source=water if visible else False,
            resources=(), creature=False,
        ),),
        inventory={},
    )


def plan(*, blocked=False, visible=True, goal_measure="water", direction="east"):
    return preregister_spatial_subgoal(
        life_id="life:a", intent_ref="intent:a", assessment_ref="assessment:a",
        goal_ref="goal:water", option_ref="option:a",
        command_hash="signed-command-sha", goal_measure=goal_measure,
        command=PrimitiveCommand("se_deplacer", {"direction": direction}),
        capture=perceive(blocked=blocked, visible=visible),
    )


class SpatialGoalEvidenceTests(unittest.TestCase):
    def test_lived_success_and_subjective_self_distinct_computations(self):
        p = plan()
        self.assertIsNotNone(p)
        capture = perceive(time=2, x=3, y=2)
        outcome = evaluate_spatial_goal_outcome(
            p, capture=capture, world_step=2, diagnostic_paid=True,
        )
        self.assertEqual(outcome.outcome, "success")
        agency = judge_spatial_agency(
            p, capture=capture, world_step=2, agency_paid=True,
            physically_applied=True,
        )
        self.assertEqual(agency.agency, "self")

    def test_blocked_known_goal_cell_can_support_subjective_world(self):
        p = plan(blocked=True)
        capture = perceive(time=2, blocked=True)
        outcome = evaluate_spatial_goal_outcome(
            p, capture=capture, world_step=2, diagnostic_paid=True,
        )
        self.assertEqual(outcome.outcome, "failure")
        belief = judge_spatial_agency(
            p, capture=capture, world_step=2, agency_paid=True,
            physically_applied=True,
        )
        self.assertEqual(belief.agency, "world")
        self.assertEqual(belief.reason, "witnessed_goal_relevant_blocked_destination")

    def test_nonprogress_from_passable_cell_is_unknown_not_world(self):
        p = plan(blocked=False)
        belief = judge_spatial_agency(
            p, capture=perceive(time=2), world_step=2,
            agency_paid=True, physically_applied=True,
        )
        outcome = evaluate_spatial_goal_outcome(
            p, capture=perceive(time=2), world_step=2,
            diagnostic_paid=True,
        )
        self.assertEqual(outcome.outcome, "failure")
        self.assertEqual(belief.agency, "unknown")

    def test_nonexecuted_cannot_create_blame(self):
        p = plan(blocked=True)
        belief = judge_spatial_agency(
            p, capture=perceive(time=2, blocked=True),
            world_step=2, agency_paid=True, physically_applied=False,
        )
        self.assertEqual(belief.agency, "unavailable")

    def test_refused_uc_and_missing_capture_fail_closed(self):
        p = plan(blocked=True)
        judgement = judge_spatial_agency(
            p, capture=perceive(time=2, blocked=True), world_step=2,
            agency_paid=False, physically_applied=True,
        )
        self.assertEqual(judgement.agency, "unavailable")
        outcome = evaluate_spatial_goal_outcome(
            p, capture=None, world_step=2, diagnostic_paid=True,
        )
        self.assertEqual(outcome.outcome, "unknown")

    def test_wrong_or_hidden_target_refuses_precommit(self):
        self.assertIsNone(plan(visible=False))
        self.assertIsNone(plan(goal_measure="food"))
        self.assertIsNone(plan(direction="north"))

    def test_late_does_not_become_failure_or_world(self):
        p = plan(blocked=True)
        result = evaluate_spatial_goal_outcome(
            p, capture=perceive(time=3, blocked=True),
            world_step=3, diagnostic_paid=True,
        )
        belief = judge_spatial_agency(
            p, capture=perceive(time=3, blocked=True),
            world_step=3, agency_paid=True, physically_applied=True,
        )
        self.assertEqual(result.outcome, "unknown")
        self.assertEqual(belief.agency, "unavailable")

    def test_forged_position_direction_or_distance_fails(self):
        p = plan()
        for fake in (replace(p, distance_before=0),
                     replace(p, target=(5, 2)),
                     replace(p, direction="west"),
                     replace(p, sent_world_step=True)):
            with self.subTest(fake=fake):
                with self.assertRaises(ValueError):
                    fake.validate()

    def test_current_generation_image_roundtrip_and_forgery_rejection(self):
        p = plan(blocked=True)
        image = p.as_dict()
        restored = SpatialGoalPrecommit.from_dict(image)
        self.assertEqual(restored, p)
        self.assertEqual(restored.as_dict(), image)
        for changed in (
            {**image, "target": [4, 2]},
            {**image, "distance_before": 9},
            {**image, "sent_world_step": True},
            {**image, "origin": (2, 2)},
            {**image, "uncontracted_truth": "oracle"},
        ):
            with self.subTest(changed=changed):
                with self.assertRaises(ValueError):
                    SpatialGoalPrecommit.from_dict(changed)

    def test_prediction_not_input_to_either_computation(self):
        p = plan(blocked=True)
        self.assertNotIn("prediction_status", p.__dataclass_fields__)
        self.assertNotIn("criterion_outcome", p.__dataclass_fields__)
        self.assertNotIn("p47_attribution", p.__dataclass_fields__)


if __name__ == "__main__":
    unittest.main()
