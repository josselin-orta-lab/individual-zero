from __future__ import annotations

import unittest

from i0.modules import SymbolicPerception
from lab.world import (
    BerryEffect,
    BodyState,
    Position,
    ToolRecipe,
    WorldBody,
    WorldLayout,
    WorldPhysicsConfig,
)


def world() -> WorldBody:
    config = WorldPhysicsConfig(
        version="stage3-perception-test-v1",
        width=32,
        height=32,
        day_steps=300,
        night_steps=100,
        night_start_step=200,
        initial_body=BodyState(50.0, 60.0, 60.0, 100.0),
        initial_position=Position(2, 2),
        food_decay_per_step=0.0,
        water_decay_per_step=0.0,
        action_energy_costs={
            "se_deplacer": 0.0,
            "collecter": 0.0,
            "manger": 0.0,
            "boire": 0.0,
            "poser_une_pierre": 0.0,
            "fabriquer_outil": 0.0,
            "dormir": 0.0,
            "attendre": 0.0,
        },
        sleep_energy_gain=0.0,
        rest_integrity_gain=0.0,
        drink_water_gain=1.0,
        berry_effects={
            "berry_a": BerryEffect(1.0, 0.0),
            "berry_b": BerryEffect(1.0, -1.0),
        },
        creature_damage=1.0,
        danger_zone_damage=1.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )
    return WorldBody(
        config=config,
        layout=WorldLayout(
            creatures=frozenset({Position(3, 2)}),
            danger_zones=frozenset({Position(2, 3)}),
            lethal_zones=frozenset({Position(1, 2)}),
            oracle_canary="MUST_NOT_APPEAR",
        ),
    )


class SymbolicPerceptionTests(unittest.TestCase):
    def test_capture_uses_local_state_and_telemetry_only(self) -> None:
        instance = world()
        perception = SymbolicPerception()

        capture = perception.capture(
            local_state=instance.capture_local(t_monde=1).as_dict(),
            telemetry=instance.telemetry(),
        )

        self.assertEqual((capture.x, capture.y), (2, 2))
        self.assertEqual(len(capture.adjacent_creatures), 1)
        self.assertEqual(capture.adjacent_creatures[0].direction, "east")
        self.assertEqual(capture.body["integrity"], 100.0)

    def test_hidden_danger_and_lethality_are_absent_from_local_capture(self) -> None:
        local = world().capture_local(t_monde=1).as_dict()
        encoded = repr(local)

        self.assertNotIn("danger_zone", encoded)
        self.assertNotIn("lethal_zone", encoded)
        self.assertNotIn("MUST_NOT_APPEAR", encoded)


if __name__ == "__main__":
    unittest.main()
