"""MVP v1.3 terminal death uses the unchanged physics with no life rewind."""
from __future__ import annotations

import unittest

from lab.mortal_execution import MortalStatus, MortalWorldBoundary
from lab.world import (
    BerryEffect, BodyState, Command, Position, ToolRecipe, WorldBody,
    WorldLayout, WorldPhysicsConfig,
)


def physics() -> WorldPhysicsConfig:
    return WorldPhysicsConfig(
        version="mvp-v1.3-mortal-world-smoke",
        width=32, height=32, day_steps=300, night_steps=100,
        night_start_step=200,
        initial_body=BodyState(50.0, 60.0, 60.0, 100.0),
        initial_position=Position(2, 2),
        food_decay_per_step=0.1, water_decay_per_step=0.2,
        action_energy_costs={
            "se_deplacer": 0.5, "collecter": 0.5,
            "manger": 0.2, "boire": 0.2,
            "poser_une_pierre": 0.5, "fabriquer_outil": 0.5,
            "dormir": 0.0, "attendre": 0.0,
        },
        sleep_energy_gain=1.0, rest_integrity_gain=0.0,
        drink_water_gain=10.0,
        berry_effects={
            "berry_a": BerryEffect(5.0, 0.0),
            "berry_b": BerryEffect(5.0, -100.0),
        },
        creature_damage=10.0, danger_zone_damage=15.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )


class MortalWorldBoundaryTests(unittest.TestCase):
    def test_unknown_lethal_zone_commits_actual_position_and_ends_life(self):
        layout = WorldLayout(lethal_zones=frozenset({Position(3, 2)}))
        physical = WorldBody(config=physics(), layout=layout)
        reference = WorldBody(config=physics(), layout=layout)
        boundary = MortalWorldBoundary(world=physical)
        move = Command("se_deplacer", {"direction": "east"})
        expected = reference.apply(move, t_monde=1)

        outcome = boundary.execute(move, t_monde=1)
        self.assertEqual(outcome.status, "dead")
        self.assertTrue(outcome.transition.lethal)
        self.assertEqual(outcome.transition.as_dict(), expected.as_dict())
        self.assertEqual(
            physical.export_causal_state(), reference.export_causal_state()
        )
        self.assertEqual(physical.position, Position(3, 2))
        self.assertEqual(boundary.status, MortalStatus.DEAD)
        self.assertEqual(boundary.terminal_death.world_step, 1)
        self.assertEqual(boundary.terminal_death.reasons, ("lethal_zone",))
        final_state = physical.export_causal_state()
        with self.assertRaises(RuntimeError):
            boundary.execute(Command("attendre"), t_monde=2)
        self.assertEqual(physical.export_causal_state(), final_state)
        self.assertEqual(boundary.last_world_step, 1)

    def test_lethal_berry_consumes_resource_and_preserves_injury(self):
        layout = WorldLayout(
            resources=((Position(2, 2), "berry_b", 1),),
        )
        physical = WorldBody(config=physics(), layout=layout)
        boundary = MortalWorldBoundary(world=physical)
        first = boundary.execute(
            Command("collecter", {"target": "berry_b"}), t_monde=1
        )
        self.assertEqual(first.status, "applied")
        result = boundary.execute(
            Command("manger", {"target": "berry_b"}), t_monde=2
        )
        self.assertEqual(result.status, "dead")
        self.assertIn("zero_integrity", result.transition.lethal_reasons)
        self.assertEqual(physical.telemetry()["integrity"], 0.0)
        self.assertEqual(physical.inventory()["berry_b"], 0)
        self.assertEqual(boundary.terminal_death.body.integrity, 0.0)
        with self.assertRaises(RuntimeError):
            boundary.execute(Command("attendre"), t_monde=3)

    def test_nonlethal_result_matches_unmodified_world_at_every_step(self):
        layout = WorldLayout(danger_zones=frozenset({Position(3, 2)}))
        actual_world = WorldBody(config=physics(), layout=layout)
        expected_world = WorldBody(config=physics(), layout=layout)
        boundary = MortalWorldBoundary(world=actual_world)
        commands = (
            Command("se_deplacer", {"direction": "east"}),
            Command("attendre"),
            Command("se_deplacer", {"direction": "west"}),
        )
        for t, command in enumerate(commands, start=1):
            observed = boundary.execute(command, t_monde=t)
            reference = expected_world.apply(command, t_monde=t)
            self.assertEqual(observed.status, "applied")
            self.assertEqual(observed.transition.as_dict(), reference.as_dict())
            self.assertEqual(
                actual_world.export_causal_state(),
                expected_world.export_causal_state(),
            )
        self.assertEqual(boundary.status, MortalStatus.ACTIVE)
        self.assertIsNone(boundary.terminal_death)

    def test_malformed_command_does_not_invent_a_world_step(self):
        physical = WorldBody(config=physics(), layout=WorldLayout())
        boundary = MortalWorldBoundary(world=physical)
        before = physical.export_causal_state()
        with self.assertRaises((ValueError, TypeError)):
            boundary.execute(Command("invalid_primitive"), t_monde=1)
        self.assertEqual(physical.export_causal_state(), before)
        self.assertEqual(boundary.status, MortalStatus.ACTIVE)
        with self.assertRaises(ValueError):
            boundary.execute(Command("attendre"), t_monde=2)
        self.assertEqual(boundary.last_world_step, 0)

    def test_physical_exception_halts_without_rewinding_world(self):
        class BrokenWorld(WorldBody):
            def apply(self, command, *, t_monde):
                super().apply(command, t_monde=t_monde)
                raise RuntimeError("unexpected post-mutation failure")

        physical = BrokenWorld(config=physics(), layout=WorldLayout())
        boundary = MortalWorldBoundary(world=physical)
        before = physical.export_causal_state()
        with self.assertRaisesRegex(RuntimeError, "post-mutation"):
            boundary.execute(
                Command("se_deplacer", {"direction": "east"}), t_monde=1,
            )
        self.assertEqual(boundary.status, MortalStatus.TECHNICAL_HALT)
        self.assertEqual(boundary.failed_step, 1)
        self.assertNotEqual(physical.export_causal_state(), before)
        self.assertEqual(physical.position, Position(3, 2))
        with self.assertRaises(RuntimeError):
            boundary.execute(Command("attendre"), t_monde=2)


if __name__ == "__main__":
    unittest.main()
