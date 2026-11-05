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


def dev_wide_field() -> WorldSpec:
    """P1.1: water out of sight, many directions to choose from."""
    return WorldSpec(
        name="dev-wide-field", width=20, height=20, spawn=(4, 15),
        body=(72.0, 50.0, 40.0, 90.0, 100.0),
        water={(9, 11): WaterSource(gain=35.0)},
        food={(5, 13): FoodPatch("ochre", 3, 3, restock_every=15),
              (15, 4): FoodPatch("teal", 3, 3, restock_every=15)},
        token_effects={"ochre": (12.0, 0.0), "teal": (8.0, -5.0)},
    )


def dev_far_home() -> WorldSpec:
    """P1.1: water at home, food far away; staying alive needs returns."""
    return WorldSpec(
        name="dev-far-home", width=18, height=5, spawn=(1, 2),
        body=(80.0, 40.0, 70.0, 95.0, 100.0),
        water={(1, 2): WaterSource(gain=35.0)},
        food={(15, 1): FoodPatch("plum", 4, 4, restock_every=10),
              (16, 3): FoodPatch("plum", 4, 4, restock_every=10)},
        token_effects={"plum": (14.0, 0.0)},
    )


def dev_failing_well() -> WorldSpec:
    """P1.2: a near well runs dry for good; another lies out of sight."""
    return WorldSpec(
        name="dev-failing-well", width=15, height=10, spawn=(12, 7),
        body=(80.0, 65.0, 55.0, 95.0, 100.0),
        water={(11, 7): WaterSource(gain=28.0, stock=5, max_stock=5, restock_every=0),
               (2, 2): WaterSource(gain=28.0)},
        food={(12, 5): FoodPatch("lilac", 3, 3, restock_every=10),
              (3, 3): FoodPatch("lilac", 3, 3, restock_every=10)},
        token_effects={"lilac": (12.0, 0.0)},
    )


DEV_WORLDS = (dev_open_field, dev_long_corridor, dev_wide_field, dev_far_home, dev_failing_well)
