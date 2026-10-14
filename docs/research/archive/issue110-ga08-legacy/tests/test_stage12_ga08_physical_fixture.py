"""GA-08 grounded physical sensor fixture, not an autonomous I0 trial.

A laboratory-issued movement tests actual WorldBody movement/obstruction and
authorized SymbolicPerception, with separate outcome and first-person policy.
The fixture never counts toward detector samples or scientific lives.
"""
import unittest
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_spatial_goal_evidence import (
    preregister_spatial_subgoal, evaluate_spatial_goal_outcome,
    judge_spatial_agency,
)
from lab.world import WorldBody, WorldLayout, Position
from test_stage3_runtime import physics


def grounded_case(blocked: bool):
    world = WorldBody(
        config=physics(),
        layout=WorldLayout(
            obstacles=frozenset({Position(3, 2)}) if blocked else frozenset(),
            water_sources=frozenset({Position(3, 2)}),
        ),
    )
    sense = SymbolicPerception()
    before = sense.capture(
        local_state=world.capture_local(t_monde=1).as_dict(),
        telemetry=world.telemetry(),
    )
    command = PrimitiveCommand("se_deplacer", {"direction": "east"})
    commit = preregister_spatial_subgoal(
        life_id="fixture-life", intent_ref="intent:1",
        assessment_ref="assessment:1", goal_ref="goal:water",
        option_ref="option:1", command_hash="fixture-command-digest",
        goal_measure="water", capture=before, command=command,
    )
    world.apply(command, t_monde=1)
    after = sense.capture(
        local_state=world.capture_local(t_monde=2).as_dict(),
        telemetry=world.telemetry(),
    )
    return commit, after


class Stage12GA08PhysicalFixtureTests(unittest.TestCase):
    def test_blocked_worldbody_and_perception_distinguish_goal_from_blame(self):
        commit, capture = grounded_case(True)
        self.assertIsNotNone(commit)
        outcome = evaluate_spatial_goal_outcome(
            commit, capture=capture, world_step=2, diagnostic_paid=True,
        )
        judgement = judge_spatial_agency(
            commit, capture=capture, world_step=2,
            agency_paid=True, physically_applied=True,
        )
        self.assertEqual((capture.x, capture.y), (2, 2))
        self.assertEqual((outcome.outcome, judgement.agency), ("failure", "world"))

    def test_free_worldbody_and_perception_are_distinct(self):
        commit, capture = grounded_case(False)
        self.assertIsNotNone(commit)
        outcome = evaluate_spatial_goal_outcome(
            commit, capture=capture, world_step=2, diagnostic_paid=True,
        )
        judgement = judge_spatial_agency(
            commit, capture=capture, world_step=2,
            agency_paid=True, physically_applied=True,
        )
        self.assertEqual((capture.x, capture.y), (3, 2))
        self.assertEqual((outcome.outcome, judgement.agency), ("success", "self"))


if __name__ == "__main__":
    unittest.main()
