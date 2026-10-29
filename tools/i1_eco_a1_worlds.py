"""Prospective A1 pilot worlds. No hidden physical effect reaches I1.

Make two environments with identical visible topology and identical birth
conditions. Native I1 rewrites toxic berry_b at birth by NAME. Normalize
this native v4 physical policy *before* swapping the complete BerryEffect,
otherwise the reversed berry_a stays -100 while berry_b becomes -10 in
the native arm: an invalid asymmetric causal intervention.
"""
from dataclasses import replace

ROLES = ("native", "reversed")
VERSION = "i1-eco-v1-a1-one-cell-counterbalance-v1"
SPAWN = (8, 8)


def a1_world_parameters(birth_params, *, role):
    if type(role) is not str or role not in ROLES:
        raise ValueError("unregistered A1 berry role")
    if type(birth_params) is not dict or not {"world_config", "layout"} <= set(birth_params):
        raise ValueError("A1 requires registered native birth parameters")
    from i1lab.world import BerryEffect, Position, WorldBody, WorldLayout
    from i1lab.i1_natural_sleep import (
        DEFAULT_TOXIC_BERRY_INTEGRITY_DELTA, TOXIC_BERRY_POLICY,
    )

    base = birth_params["world_config"]
    effects = base.berry_effects
    if set(effects) != {"berry_a", "berry_b"}:
        raise ValueError("A1 requires two native berries")
    native_a, native_b = effects["berry_a"], effects["berry_b"]
    if not (native_a.food_gain > 0 and native_a.integrity_delta == 0
            and native_b.integrity_delta == -100.0 and native_a != native_b):
        raise ValueError("A1 physical role contrast differs from preregistration")
    # The native natural I1 policy reclassifies only berry_b at -100.
    # Use its own constant first; neither role will later be rewritten by
    # species name. Both roles retain exactly the same natural physiology.
    native_b = BerryEffect(native_b.food_gain,
                           DEFAULT_TOXIC_BERRY_INTEGRITY_DELTA)
    position = Position(*SPAWN)
    cfg = replace(
        base,
        version=base.version + "+" + TOXIC_BERRY_POLICY + "+" + VERSION,
        initial_position=position,
        berry_effects=(
            {"berry_a": native_a, "berry_b": native_b}
            if role == "native"
            else {"berry_a": native_b, "berry_b": native_a}
        ),
    )
    # Normative world remains 32x32; four obstacles isolate the accessible
    # birth cell. No scripted motor commands or externally exposed food labels.
    layout = WorldLayout(
        obstacles=frozenset((Position(7, 8), Position(9, 8),
                             Position(8, 7), Position(8, 9))),
        water_sources=frozenset((position,)),
        resources=((position, "berry_a", 6), (position, "berry_b", 6)),
        creatures=frozenset(), danger_zones=frozenset(),
        lethal_zones=frozenset(),
        oracle_canary="OPERATOR_ONLY_A1_BERRY_EFFECTS_NOT_FOR_I1",
    )
    cfg.validate()
    layout.validate(cfg)
    local = WorldBody(config=cfg, layout=layout).capture_local(t_monde=1).as_dict()
    if (layout.oracle_canary in str(local)
            or any(word in str(local)
                   for word in ("berry_effects", "integrity_delta", "food_gain"))):
        raise ValueError("hidden physical effect leaked to local perception")
    if (set(local["current_resources"]) != {"berry_a", "berry_b"}
            or not local["current_water_source"]
            or any(x["passable"] for x in local["adjacent"])):
        raise ValueError("A1 world does not offer exactly the frozen local choices")
    return {**birth_params, "world_config": cfg, "layout": layout}, local
