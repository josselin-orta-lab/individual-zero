"""Development worlds ONLY. Never the preregistered G2 test worlds.

They exist to debug the core before the first falsifier is frozen. Their
geometry and numbers deliberately differ from ``first_falsifier`` worlds.
"""
from __future__ import annotations

from i3.modules.world import FoodPatch, WaterSource, WorldSpec


def dev_open_field() -> WorldSpec:
    return WorldSpec(
        name="dev-open-field", width=14, height=14, spawn=(3, 3),
        body=(80.0, 55.0, 50.0, 90.0, 100.0),
        water={(9, 4): WaterSource(gain=30.0)},
        food={(4, 9): FoodPatch("red", 3, 3, restock_every=20),
              (10, 10): FoodPatch("blue", 3, 3, restock_every=20)},
        token_effects={"red": (12.0, 0.0), "blue": (6.0, -8.0)},
    )


def dev_long_corridor() -> WorldSpec:
    return WorldSpec(
        name="dev-long-corridor", width=6, height=1, spawn=(0, 0),
        body=(75.0, 50.0, 45.0, 95.0, 100.0),
        water={(5, 0): WaterSource(gain=30.0, stock=3, max_stock=3, restock_every=12)},
        food={(3, 0): FoodPatch("green", 2, 2, restock_every=10)},
        token_effects={"green": (15.0, 0.0)},
    )


DEV_WORLDS = (dev_open_field, dev_long_corridor)
