from __future__ import annotations

import unittest

from lab.world import (
    BerryEffect,
    BodyState,
    Command,
    Position,
    ToolRecipe,
    WorldBody,
    WorldLayout,
    WorldPhysicsConfig,
)


def physics() -> WorldPhysicsConfig:
    return WorldPhysicsConfig(
        version="stage2-test-v1",
        width=32,
        height=32,
        day_steps=300,
        night_steps=100,
        night_start_step=200,
        initial_body=BodyState(
            energy=50.0,
            food=60.0,
            water=60.0,
            integrity=100.0,
        ),
        initial_position=Position(2, 2),
        food_decay_per_step=1.0,
        water_decay_per_step=2.0,
        action_energy_costs={
            "se_deplacer": 1.0,
            "collecter": 1.0,
            "manger": 0.5,
            "boire": 0.5,
            "poser_une_pierre": 1.0,
            "fabriquer_outil": 1.0,
            "dormir": 0.0,
            "attendre": 0.0,
        },
        sleep_energy_gain=3.0,
        rest_integrity_gain=1.0,
        drink_water_gain=20.0,
        berry_effects={
            "berry_a": BerryEffect(food_gain=15.0, integrity_delta=0.0),
            "berry_b": BerryEffect(food_gain=10.0, integrity_delta=-100.0),
        },
        creature_damage=25.0,
        danger_zone_damage=15.0,
        tool_recipe=ToolRecipe(
            wood_required=1,
            stone_required=1,
            collection_gain=2,
        ),
    )


class WorldPhysicsTests(unittest.TestCase):
    def test_normative_grid_and_day_shape_are_enforced(self) -> None:
        config = physics()
        config.validate()
        self.assertEqual((config.width, config.height), (32, 32))
        self.assertEqual(config.day_steps, 300)
        self.assertEqual(config.night_steps, 100)

    def test_border_is_impassable(self) -> None:
        config = physics()
        world = WorldBody(
            config=config,
            layout=WorldLayout(),
        )
        world._position = Position(1, 2)  # fixture only

        result = world.apply(
            Command("se_deplacer", {"direction": "west"}),
            t_monde=1,
        )

        self.assertEqual(result.position_after, Position(1, 2))
        self.assertEqual(result.effects["movement"], "blocked")

    def test_body_dynamics_are_bounded(self) -> None:
        world = WorldBody(config=physics(), layout=WorldLayout())

        for step in range(1, 200):
            world.apply(Command("attendre"), t_monde=step)

        for value in world.telemetry().values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 100.0)

    def test_collect_eat_drink_craft_and_shelter_are_deterministic(self) -> None:
        config = physics()
        layout = WorldLayout(
            water_sources=frozenset({Position(2, 2)}),
            resources=(
                (Position(2, 2), "berry_a", 2),
                (Position(2, 2), "wood", 1),
                (Position(2, 2), "stone", 5),
            ),
        )
        world = WorldBody(config=config, layout=layout)

        world.apply(Command("collecter", {"target": "berry_a"}), t_monde=1)
        world.apply(Command("collecter", {"target": "wood"}), t_monde=2)
        world.apply(Command("collecter", {"target": "stone"}), t_monde=3)
        crafted = world.apply(Command("fabriquer_outil"), t_monde=4)
        self.assertTrue(crafted.effects["tool_crafted"])

        world.apply(Command("collecter", {"target": "stone"}), t_monde=5)
        self.assertEqual(world.inventory()["stone"], 2)

        drank = world.apply(Command("boire"), t_monde=6)
        self.assertTrue(drank.effects["drank"])

        ate = world.apply(Command("manger", {"target": "berry_a"}), t_monde=7)
        self.assertEqual(ate.effects["ate"], "berry_a")

        # Need four stones at the same cell for the normative shelter.
        world._inventory["stone"] = 4  # fixture setup only
        for step in range(8, 12):
            placed = world.apply(Command("poser_une_pierre"), t_monde=step)
        self.assertTrue(placed.effects["shelter_formed"])

    def test_danger_zone_applies_damage_without_forcing_lethality(self) -> None:
        world = WorldBody(
            config=physics(),
            layout=WorldLayout(
                danger_zones=frozenset({Position(3, 2)}),
            ),
        )

        result = world.apply(
            Command("se_deplacer", {"direction": "east"}),
            t_monde=1,
        )

        self.assertFalse(result.lethal)
        self.assertEqual(result.effects["danger_zone_damage"], 15.0)
        self.assertEqual(result.body_after.integrity, 85.0)

    def test_lethal_zone_is_detected(self) -> None:
        world = WorldBody(
            config=physics(),
            layout=WorldLayout(
                lethal_zones=frozenset({Position(3, 2)}),
            ),
        )

        result = world.apply(
            Command("se_deplacer", {"direction": "east"}),
            t_monde=1,
        )

        self.assertTrue(result.lethal)
        self.assertIn("lethal_zone", result.lethal_reasons)

    def test_zero_integrity_is_detected_as_lethal(self) -> None:
        world = WorldBody(
            config=physics(),
            layout=WorldLayout(
                resources=((Position(2, 2), "berry_b", 1),),
            ),
        )
        world.apply(Command("collecter", {"target": "berry_b"}), t_monde=1)

        result = world.apply(
            Command("manger", {"target": "berry_b"}),
            t_monde=2,
        )

        self.assertTrue(result.lethal)
        self.assertEqual(result.body_after.integrity, 0.0)
        self.assertIn("zero_integrity", result.lethal_reasons)

    def test_world_state_round_trip_is_exact(self) -> None:
        world = WorldBody(
            config=physics(),
            layout=WorldLayout(
                resources=((Position(2, 2), "wood", 2),),
            ),
        )
        state = world.export_causal_state()
        world.apply(Command("collecter", {"target": "wood"}), t_monde=1)

        world.restore_causal_state(state)

        self.assertEqual(world.export_causal_state(), state)




class ScenarioForcedFailureTests(unittest.TestCase):
    def test_forced_failure_suppresses_only_primitive_effect_and_advances_schedule(self) -> None:
        world = make_world()
        world.apply_scenario_event(
            "set_action_failure_schedule",
            {
                "primitive": "se_deplacer",
                "schedule": [True, False],
            },
        )

        first = world.apply(
            command("se_deplacer", direction="east"),
            t_monde=1,
        )
        self.assertEqual(first.position_after, first.position_before)
        self.assertEqual(
            first.effects["scenario_forced_failure"],
            "se_deplacer",
        )
        self.assertTrue(
            first.effects["scenario_failure_attempt"]["forced"]
        )

        second = world.apply(
            command("se_deplacer", direction="east"),
            t_monde=2,
        )
        self.assertNotEqual(second.position_after, second.position_before)
        self.assertFalse(
            second.effects["scenario_failure_attempt"]["forced"]
        )

    def test_forced_failure_cursor_round_trips_in_causal_state(self) -> None:
        world = make_world()
        world.apply_scenario_event(
            "set_action_failure_schedule",
            {
                "primitive": "se_deplacer",
                "schedule": [True, False, True],
            },
        )
        world.apply(command("se_deplacer", direction="east"), t_monde=1)
        state = world.export_causal_state()

        restored = make_world()
        restored.restore_causal_state(state)
        result = restored.apply(
            command("se_deplacer", direction="east"),
            t_monde=2,
        )

        self.assertFalse(
            result.effects["scenario_failure_attempt"]["forced"]
        )
        self.assertEqual(
            result.effects["scenario_failure_attempt"]["attempt_index"],
            1,
        )

if __name__ == "__main__":
    unittest.main()
