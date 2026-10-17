"""GA-SPATIAL-01 real WorldBody transition *software fixture*, not an I0 life.

Shows physically observed nonpassability can support a cautious spatial cue,
but does not prove autonomous goal selection or metacognitive admission.
"""
from dataclasses import replace
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_spatial_cue_policy import evaluate_spatial_goal_cue
from lab.world import Position, WorldBody
from lab.stage11_reference_fixture import build_stage11_reference_runtime


def physical_spatial_cue(blocked: bool):
    base = build_stage11_reference_runtime()
    initial = base.world.config.initial_position
    target = Position(initial.x + 1, initial.y)
    world_config = replace(
        base.world.config, version="issue110-ga-spatial-physical-fixture-v1",
    )
    layout = replace(
        base.world._layout,
        obstacles=frozenset({target}) if blocked else frozenset(),
        water_sources=frozenset({target}),
    )
    world = WorldBody(config=world_config, layout=layout)
    perception = SymbolicPerception()
    before = perception.capture(
        local_state=world.capture_local(t_monde=1).as_dict(),
        telemetry=world.telemetry(),
    )
    command = PrimitiveCommand("se_deplacer", {"direction": "east"})
    transition = world.apply(command, t_monde=1)
    after = perception.capture(
        local_state=world.capture_local(t_monde=2).as_dict(),
        telemetry=world.telemetry(),
    )
    result = evaluate_spatial_goal_cue(
        pre=before, post=after, command=command,
        target_x=target.x, target_y=target.y,
        target_kind="water", admitted_and_executed=True,
    )
    return result, before, after, transition


class PhysicalSpatialCueFixtureTests(unittest.TestCase):
    def test_world_only_on_real_blocked_target_cue(self):
        result, before, after, transition = physical_spatial_cue(True)
        self.assertFalse(next(c for c in before.adjacent
                              if c.direction == "east").passable)
        self.assertEqual((before.x, before.y), (after.x, after.y))
        self.assertEqual(result.agency, "world")

    def test_self_on_real_free_displacement_toward_visible_target(self):
        result, before, after, transition = physical_spatial_cue(False)
        self.assertTrue(next(c for c in before.adjacent
                             if c.direction == "east").passable)
        self.assertEqual((after.x, after.y), (before.x + 1, before.y))
        self.assertEqual(result.agency, "self")


if __name__ == "__main__":
    unittest.main()
