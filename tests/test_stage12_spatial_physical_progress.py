"""Physically grounded *software* contract tests for spatial progress + cues.

WorldBody commands here are fixed by the fixture, not autonomously selected
by I0. The ledger and cue policy must remain causally independent.
"""
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_progress import (
    LivedSpatialGoalIntent, Stage12GoalProgressLedger,
)
from i0.modules.stage12_spatial_cue_policy import evaluate_spatial_goal_cue
from lab.world import Position, WorldBody
from lab.stage11_reference_fixture import build_stage11_reference_runtime


def witnessed_case(blocked: bool, after_food: float | None = None):
    reference = build_stage11_reference_runtime()
    start = reference.world.config.initial_position
    target = Position(start.x + 1, start.y)
    config = replace(reference.world.config,
                     version="issue110-spatial-goal-witness-v1")
    layout = replace(
        reference.world._layout,
        obstacles=frozenset({target}) if blocked else frozenset(),
        water_sources=frozenset({target}),
    )
    physical = WorldBody(config=config, layout=layout)
    p = SymbolicPerception()
    before = p.capture(
        local_state=physical.capture_local(t_monde=1).as_dict(),
        telemetry=physical.telemetry(),
    )
    intent = LivedSpatialGoalIntent(
        intent_ref="intent:1", goal_ref="goal:water", option_ref="option:east",
        command_hash="action:hash", measure="spatial_distance",
        value_before=1.0, sent_world_step=1, observe_world_step=2,
        life_id="life:fixture", start_x=before.x, start_y=before.y,
        target_x=target.x, target_y=target.y,
        direction="east", target_kind="water",
    )
    ledger = Stage12GoalProgressLedger()
    ledger.preregister(intent)
    command = PrimitiveCommand("se_deplacer", {"direction": "east"})
    physical.apply(command, t_monde=1)
    after = p.capture(
        local_state=physical.capture_local(t_monde=2).as_dict(),
        telemetry=physical.telemetry(),
    )
    if after_food is not None:
        after = replace(after, body={**after.body, "food": after_food})
    # Independent source A: I0's action-control-compatible spatial cue.
    agency = evaluate_spatial_goal_cue(
        pre=before, post=after, command=command,
        target_x=target.x, target_y=target.y,
        target_kind="water", admitted_and_executed=True,
    )
    # Independent source B: strict goal criterion on the lived position.
    outcome = ledger.followup(
        world_step=after.t_monde, body=after.body,
        position=(after.x, after.y),
    )
    return agency, outcome


class SpatialPhysicalLedgerTests(unittest.TestCase):
    def test_free_target_has_self_and_progress(self):
        agency, outcome = witnessed_case(blocked=False)
        self.assertEqual(agency.agency, "self")
        self.assertEqual(outcome.criterion_outcome, "success")

    def test_blocked_target_has_world_and_no_progress(self):
        agency, outcome = witnessed_case(blocked=True)
        self.assertEqual(agency.agency, "world")
        self.assertEqual(outcome.criterion_outcome, "failure")

    def test_body_measure_cannot_flip_either_spatial_result(self):
        agency1, progress1 = witnessed_case(blocked=True, after_food=0.0)
        agency2, progress2 = witnessed_case(blocked=True, after_food=100.0)
        self.assertEqual(agency1.agency, agency2.agency)
        self.assertEqual(progress1.criterion_outcome, progress2.criterion_outcome)
        self.assertEqual(agency1.agency, "world")

    def test_missing_next_capture_cannot_make_failure(self):
        reference = build_stage11_reference_runtime()
        start = reference.world.config.initial_position
        ledger = Stage12GoalProgressLedger()
        ledger.preregister(LivedSpatialGoalIntent(
            intent_ref="intent:absent", goal_ref="goal:water",
            option_ref="option:east", command_hash="action:hash",
            measure="spatial_distance", value_before=1.0,
            sent_world_step=1, observe_world_step=2,
            life_id="life:fixture", start_x=start.x, start_y=start.y,
            target_x=start.x+1, target_y=start.y,
            direction="east", target_kind="water",
        ))
        outcome = ledger.followup(
            world_step=2, body={"water": 0.0}, position=None,
        )
        self.assertEqual(outcome.criterion_outcome, "unknown")


if __name__ == "__main__":
    unittest.main()
