"""Irreversible mortal-world contract tests for the vNext runtime.

No post-death continuation, rollback, masked retry, or physics substitution.
"""
from __future__ import annotations

import unittest

from i0.config import MVP_CYCLE_PHASE_COMPONENT_ORDER
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage2_runtime import ScriptedStage2Runtime
from lab.world import (
    BerryEffect, BodyState, Command, Position, ToolRecipe,
    WorldBody, WorldLayout, WorldPhysicsConfig,
)


def physics() -> WorldPhysicsConfig:
    return WorldPhysicsConfig(
        version="mortal-contract-v1", width=32, height=32,
        day_steps=300, night_steps=100, night_start_step=200,
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


def mortal(layout: WorldLayout) -> ScriptedStage2Runtime:
    return ScriptedStage2Runtime(
        config=physics(), layout=layout,
        phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
        safety_config=SafetyProtocolConfig(
            version="mortal-contract-v1", lethal_max=0, mode="campaign",
        ),
    )


class IrreversibleMortalityTests(unittest.TestCase):
    def test_lethal_zone_is_applied_and_dead_is_terminal(self):
        layout = WorldLayout(lethal_zones=frozenset({Position(3, 2)}))
        individual = mortal(layout)
        individual.open_step()
        result = individual.execute(Command("se_deplacer", {"direction": "east"}))
        self.assertEqual(result.status, "dead")
        self.assertEqual(individual.world.position, Position(3, 2))
        self.assertEqual(individual.scheduler.t_monde, 1)
        self.assertIsNone(individual.scheduler.active_attempt)
        self.assertTrue(individual.safety.dead)
        self.assertFalse(individual.safety.blocked)
        self.assertEqual(individual.bench.metrics.lethal_transitions, 1)
        with self.assertRaises(RuntimeError):
            individual.open_step()
        with self.assertRaises(RuntimeError):
            individual.execute(Command("attendre"))
        kinds = [e.causal_event["kind"] for e in individual.journal.entries]
        self.assertIn("death_confirmed", kinds)
        self.assertNotIn("snapshot_restored", kinds)
        self.assertNotIn("lethal_rollback_completed", kinds)
        self.assertEqual(individual.autobiographical_view(), ())

    def test_lethal_food_consumpion_preserves_physical_effects(self):
        layout = WorldLayout(
            resources=((Position(2, 2), "berry_b", 1),),
        )
        instance = mortal(layout)
        instance.open_step()
        collected = instance.execute(Command("collecter", {"target": "berry_b"}))
        self.assertEqual(collected.status, "applied")
        instance.open_step()
        command = Command("manger", {"target": "berry_b"})
        result = instance.execute(command)
        self.assertEqual(result.status, "dead")
        self.assertTrue(result.transition.lethal)
        self.assertEqual(instance.world.telemetry()["integrity"], 0.0)
        self.assertEqual(instance.world.inventory()["berry_b"], 0)

    def test_nonlethal_physics_matches_direct_world(self):
        layout = WorldLayout(danger_zones=frozenset({Position(3, 2)}))
        individual = mortal(layout)
        reference = WorldBody(config=physics(), layout=layout)
        command = Command("se_deplacer", {"direction": "east"})
        individual.open_step()
        actual = individual.execute(command)
        expected = reference.apply(command, t_monde=1)
        self.assertEqual(actual.status, "applied")
        self.assertEqual(actual.transition.as_dict(), expected.as_dict())
        self.assertEqual(
            individual.world.export_causal_state(),
            reference.export_causal_state(),
        )


if __name__ == "__main__":
    unittest.main()
