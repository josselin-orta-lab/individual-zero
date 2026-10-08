from __future__ import annotations

import unittest

from lab.world import BerryEffect, BodyState, Position, ToolRecipe, WorldPhysicsConfig
from lab.world_generation import (
    WorldGenerationConfig,
    apply_generated_berry_effects,
    generate_world,
)


def physics() -> WorldPhysicsConfig:
    return WorldPhysicsConfig(
        version="generation-test-v1",
        width=32,
        height=32,
        day_steps=300,
        night_steps=100,
        night_start_step=200,
        initial_body=BodyState(50.0, 60.0, 60.0, 100.0),
        initial_position=Position(16, 16),
        food_decay_per_step=0.1,
        water_decay_per_step=0.2,
        action_energy_costs={
            "se_deplacer": 0.5,
            "collecter": 0.5,
            "manger": 0.2,
            "boire": 0.2,
            "poser_une_pierre": 0.5,
            "fabriquer_outil": 0.5,
            "dormir": 0.0,
            "attendre": 0.0,
        },
        sleep_energy_gain=1.0,
        rest_integrity_gain=0.0,
        drink_water_gain=10.0,
        berry_effects={
            "berry_a": BerryEffect(1.0, 0.0),
            "berry_b": BerryEffect(1.0, -1.0),
        },
        creature_damage=10.0,
        danger_zone_damage=15.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )


def generation() -> WorldGenerationConfig:
    return WorldGenerationConfig(
        version="generation-p52-test-v1",
        water_source_count=2,
        berry_a_cells=3,
        berry_b_cells=3,
        wood_cells=2,
        stone_cells=2,
        creature_count=2,
        danger_zone_count=2,
        quantity_per_resource_cell=4,
        nutritious_food_gain=12.0,
        toxic_food_gain=4.0,
        toxic_integrity_delta=-30.0,
    )


class WorldGenerationTests(unittest.TestCase):
    def test_same_seed_generates_identical_world(self) -> None:
        first = generate_world(
            physics=physics(),
            generation=generation(),
            seed=91,
            oracle_canary="canary",
        )
        second = generate_world(
            physics=physics(),
            generation=generation(),
            seed=91,
            oracle_canary="canary",
        )

        self.assertEqual(first, second)

    def test_different_seed_changes_layout_or_berry_identity(self) -> None:
        first = generate_world(
            physics=physics(),
            generation=generation(),
            seed=91,
        )
        second = generate_world(
            physics=physics(),
            generation=generation(),
            seed=92,
        )

        self.assertNotEqual(first, second)

    def test_generated_cells_do_not_overlap_and_avoid_birth_position(self) -> None:
        config = physics()
        generated = generate_world(
            physics=config,
            generation=generation(),
            seed=7,
        )

        positions = list(generated.layout.water_sources)
        positions += [row[0] for row in generated.layout.resources]
        positions += list(generated.layout.creatures)
        positions += list(generated.layout.danger_zones)

        self.assertEqual(len(positions), len(set(positions)))
        self.assertNotIn(config.initial_position, positions)

    def test_seed_selects_exactly_one_toxic_berry_species(self) -> None:
        config = physics()
        generated = generate_world(
            physics=config,
            generation=generation(),
            seed=33,
        )
        updated = apply_generated_berry_effects(
            physics=config,
            generation=generation(),
            generated=generated,
        )

        toxic = updated.berry_effects[generated.toxic_berry]
        nutritious = updated.berry_effects[generated.nutritious_berry]

        self.assertLess(toxic.integrity_delta, 0.0)
        self.assertEqual(nutritious.integrity_delta, 0.0)

    def test_generator_uses_explicit_counts_not_hidden_density(self) -> None:
        generated = generate_world(
            physics=physics(),
            generation=generation(),
            seed=11,
        )
        resource_counts = {}
        for _, kind, _ in generated.layout.resources:
            resource_counts[kind] = resource_counts.get(kind, 0) + 1

        self.assertEqual(len(generated.layout.water_sources), 2)
        self.assertEqual(resource_counts["berry_a"], 3)
        self.assertEqual(resource_counts["berry_b"], 3)
        self.assertEqual(resource_counts["wood"], 2)
        self.assertEqual(resource_counts["stone"], 2)
        self.assertEqual(len(generated.layout.creatures), 2)
        self.assertEqual(len(generated.layout.danger_zones), 2)


if __name__ == "__main__":
    unittest.main()
