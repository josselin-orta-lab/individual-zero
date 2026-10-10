"""Deterministic preregistered world generation for Stage 2.

All densities, quantities and berry consequences are explicit P-52 inputs.
The generator only maps a seed to a reproducible layout and contingency choice.

Spec: 17.2, 19.5, 20.3 Stage 2, P-52, INV-33.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .determinism import RandomStreamRegistry
from .world import BerryEffect, Position, WorldLayout, WorldPhysicsConfig


@dataclass(frozen=True, slots=True)
class WorldGenerationConfig:
    version: str
    water_source_count: int
    berry_a_cells: int
    berry_b_cells: int
    wood_cells: int
    stone_cells: int
    creature_count: int
    danger_zone_count: int
    quantity_per_resource_cell: int
    nutritious_food_gain: float
    toxic_food_gain: float
    toxic_integrity_delta: float

    def validate(self) -> None:
        if not self.version:
            raise ValueError("world generation version must not be empty")
        counts = (
            self.water_source_count,
            self.berry_a_cells,
            self.berry_b_cells,
            self.wood_cells,
            self.stone_cells,
            self.creature_count,
            self.danger_zone_count,
        )
        if any(value < 0 for value in counts):
            raise ValueError("world-generation counts must be non-negative")
        if self.quantity_per_resource_cell < 1:
            raise ValueError("resource cell quantity must be >= 1")
        if self.nutritious_food_gain < 0 or self.toxic_food_gain < 0:
            raise ValueError("berry food gains must be non-negative")
        if self.toxic_integrity_delta >= 0:
            raise ValueError("toxic berry must have a negative integrity delta")


@dataclass(frozen=True, slots=True)
class GeneratedWorld:
    layout: WorldLayout
    toxic_berry: str
    nutritious_berry: str


def generate_world(
    *,
    physics: WorldPhysicsConfig,
    generation: WorldGenerationConfig,
    seed: object,
    oracle_canary: str = "",
) -> GeneratedWorld:
    physics.validate()
    generation.validate()

    candidates = [
        Position(x, y)
        for y in range(1, physics.height - 1)
        for x in range(1, physics.width - 1)
        if Position(x, y) != physics.initial_position
    ]
    required = (
        generation.water_source_count
        + generation.berry_a_cells
        + generation.berry_b_cells
        + generation.wood_cells
        + generation.stone_cells
        + generation.creature_count
        + generation.danger_zone_count
    )
    if required > len(candidates):
        raise ValueError("world generation requests more unique cells than available")

    streams = RandomStreamRegistry(campaign_seed=seed)
    rng = streams.stream("world_layout")
    rng.shuffle(candidates)

    cursor = 0

    def take(count: int) -> list[Position]:
        nonlocal cursor
        values = candidates[cursor:cursor + count]
        cursor += count
        return values

    water = take(generation.water_source_count)
    berry_a = take(generation.berry_a_cells)
    berry_b = take(generation.berry_b_cells)
    wood = take(generation.wood_cells)
    stone = take(generation.stone_cells)
    creatures = take(generation.creature_count)
    danger = take(generation.danger_zone_count)

    toxic_berry = "berry_a" if rng.randrange(2) == 0 else "berry_b"
    nutritious_berry = "berry_b" if toxic_berry == "berry_a" else "berry_a"

    resources: list[tuple[Position, str, int]] = []
    for position in berry_a:
        resources.append((position, "berry_a", generation.quantity_per_resource_cell))
    for position in berry_b:
        resources.append((position, "berry_b", generation.quantity_per_resource_cell))
    for position in wood:
        resources.append((position, "wood", generation.quantity_per_resource_cell))
    for position in stone:
        resources.append((position, "stone", generation.quantity_per_resource_cell))

    return GeneratedWorld(
        layout=WorldLayout(
            water_sources=frozenset(water),
            resources=tuple(resources),
            creatures=frozenset(creatures),
            danger_zones=frozenset(danger),
            oracle_canary=oracle_canary,
        ),
        toxic_berry=toxic_berry,
        nutritious_berry=nutritious_berry,
    )


def apply_generated_berry_effects(
    *,
    physics: WorldPhysicsConfig,
    generation: WorldGenerationConfig,
    generated: GeneratedWorld,
) -> WorldPhysicsConfig:
    """Return a physics config with seeded berry identity but preregistered effects."""

    effects = {
        generated.nutritious_berry: BerryEffect(
            food_gain=generation.nutritious_food_gain,
            integrity_delta=0.0,
        ),
        generated.toxic_berry: BerryEffect(
            food_gain=generation.toxic_food_gain,
            integrity_delta=generation.toxic_integrity_delta,
        ),
    }
    updated = replace(physics, berry_effects=effects)
    updated.validate()
    return updated
