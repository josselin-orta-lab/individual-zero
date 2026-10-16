"""Frozen A2.39 physical fixture. No I1 births are performed here."""
from __future__ import annotations

from dataclasses import replace
from i1_a238_fixtures import COSTS, TRAIN_SHA, references
from i1_a239_lock import ARMS, STRATA

PHYSICS_VERSION = "a239-preregistered-world-v1"
POLICY = "a239-mortal-factorial-v1"


def world_case(s11, stage11_config, stratum: str, case_index: int, arm: str):
    from i1lab.world import BerryEffect, Position

    if (stratum not in STRATA or arm not in ARMS
            or type(case_index) is not int or not 0 <= case_index < 8):
        raise ValueError("unknown A2.39 physical cell")
    origin = Position(14 + case_index % 4, 14 + case_index // 4)
    east = origin.moved("east")
    food_first = stratum.startswith("FOOD_FIRST_")
    water = float(55 + case_index % 3 if food_first else 23 + case_index % 3)
    body = replace(s11.world.config.initial_body,
                   energy=float(68 + case_index % 2),
                   food=float(17 + case_index % 4),
                   water=water, integrity=100.0)
    world = replace(
        s11.world.config, version=PHYSICS_VERSION,
        initial_position=origin, initial_body=body,
        food_decay_per_step=.20, water_decay_per_step=.40,
        action_energy_costs=COSTS, sleep_energy_gain=0.0,
        rest_integrity_gain=0.0, drink_water_gain=40.0,
        creature_damage=0.0, danger_zone_damage=10.0,
        berry_effects={"berry_a": BerryEffect(0,-100),
                       "berry_b": BerryEffect(6,0)},
    )
    resource_site = east if food_first else origin
    water_sources = (
        frozenset() if food_first else
        frozenset({origin}) if stratum == "BOTH_LOCAL_GEO"
        else frozenset({east})
    )
    lethal = frozenset({east}) if stratum == "FOOD_FIRST_E_INVISIBLE_LETHAL" else frozenset()
    layout = replace(
        s11.world._layout,
        obstacles=frozenset(), creatures=frozenset(),
        danger_zones=frozenset(), lethal_zones=lethal,
        water_sources=water_sources,
        resources=((resource_site,"berry_b",9+case_index%3),),
    )
    world.validate()
    layout.validate(world)
    new_c11 = replace(stage11_config, geographic=(
        stage11_config.geographic if arm == "H1_GEO" else None))
    return world, layout, new_c11, (), east


def factor_flags(arm):
    if arm not in ARMS:
        raise ValueError("unknown A2.39 arm")
    return {
        "i1_a238_alternate_need": arm != "BASE",
        "i1_a238_bounded_move": False,
        "i1_a239_strict_unknown": arm in ("STRICT_UNKNOWN", "FOOD_FIRST_RISK"),
        "i1_a239_food_first_risk": arm == "FOOD_FIRST_RISK",
        "i1_a239_d2_uc": 1,
        "i1_a239_risk_uc": 3,
        "i1_a239_max_commitments": 2,
    }
