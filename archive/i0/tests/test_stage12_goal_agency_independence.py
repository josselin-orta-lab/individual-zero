"""GA-04 adversarial contract: judgement is not objective goal success.

Separates bodily goal criterion from witnessed goal-relevant inventory cue.
The current policy has no witnessed external mechanism, so world remains
unavailable as a positive category rather than fabricated from failure.
"""
from __future__ import annotations

from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.stage12_goal_agency import GoalAgencyService
from test_action_control import capture_with_creature


def perception(step: int, *, food: float, berries: int):
    base = capture_with_creature(creature_direction=None)
    return replace(
        base, t_monde=step,
        inventory={"berry_a": berries, "berry_b": 0},
        body={**base.body, "food": food},
    )


def first_person(*, food_after: float, berries_after: int):
    actor = GoalAgencyService()
    actor.preregister(
        assessment_ref="assessment:food:1",
        intent_ref="intent:food:1",
        life_id="life:001",
        goal_ref="goal:food:001",
        option_ref="option:ingest:001",
        command_hash="digest:one",
        world_step=1,
        measure="food",
        command=PrimitiveCommand("manger", {"target": "berry_a"}),
        capture=perception(1, food=60.0, berries=2),
    )
    return actor.evaluate(
        capture=perception(2, food=food_after, berries=berries_after),
        world_step=2, cue_ref="first-person-capture:2", paid=True,
    )


class GoalAgencyNegativeCausalityTests(unittest.TestCase):
    def test_self_judgement_with_no_goal_success(self):
        result = first_person(food_after=60.0, berries_after=1)
        self.assertEqual(result.subjective_agency, "self")

    def test_goal_success_does_not_create_self_judgement(self):
        result = first_person(food_after=90.0, berries_after=2)
        self.assertEqual(result.subjective_agency, "unknown")

    def test_failed_goal_does_not_create_world_blame(self):
        result = first_person(food_after=30.0, berries_after=2)
        self.assertEqual(result.subjective_agency, "unknown")

    def test_same_action_cue_different_goal_outcome_same_judgement(self):
        beliefs = {
            first_person(food_after=food, berries_after=1).subjective_agency
            for food in (0.0, 60.0, 80.0, 99.0)
        }
        self.assertEqual(beliefs, {"self"})


if __name__ == "__main__":
    unittest.main()
