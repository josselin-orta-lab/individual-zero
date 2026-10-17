"""A2.38 fixed physical settings and four-arm assignment. Laboratory only."""
from dataclasses import replace

LOCK_SHA = "e1f276ffdc086c80a0360c3df7bd60fc2b7652dd"
TRAIN_SHA = "7c5e9634090741aff5d7b3110f888b9d81a11b978e349463d66b4cc5d4f97551"
ARMS = ("BASE", "ALTERNATE_NEED", "BOUNDED_MOVE", "BOTH")
STRATA = ("BLOCKED_THIRST_LOCAL_BERRY", "WATER_LOCAL_BERRY_E_SAFE",
          "WATER_LOCAL_BERRY_E_INVISIBLE_LETHAL", "MIXED_NEEDS_KNOWN_SAFE",
          "MIXED_NEEDS_CHANGED_INVISIBLE_LETHAL")
COSTS = dict(se_deplacer=2.0, collecter=1.0, manger=0.5, boire=0.5,
             attendre=0.35, dormir=0.25, poser_une_pierre=1.5,
             fabriquer_outil=1.5)


def references():
    from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
    from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
    from i1.modules.stage12_detectors import Stage12DetectionPolicy
    s11 = build_stage11_reference_runtime(enable_geography=True, autonomous_mortal=True)
    s10 = build_stage10_reference_runtime(autonomous_mortal=True)
    c11 = s11._stage11_config
    s9=c11.stage9; s8=s9.stage8; s7=s8.stage7; s6=s7.stage6; s4=s6.stage4
    needs=replace(s4.value_needs, version="a238-locked-needs",
        setpoints={**s4.value_needs.setpoints, "water":92.0, "food":77.0})
    plan=replace(s6.planning, version="a238-locked-plan",
        setpoints={**s6.planning.setpoints, "water":92.0, "food":77.0})
    s9=replace(s9,stage8=replace(s8,stage7=replace(s7,
        stage6=replace(s6,stage4=replace(s4,value_needs=needs),planning=plan))))
    c11=replace(c11, stage9=s9)
    sleep=replace(s10._stage10_config.sleep,version="a238-locked-sleep",
        fatigue_gain=0.0,night_weight=0.0,consolidation_weight=0.0)
    c10=replace(s10._stage10_config,stage9=s9,sleep=sleep)
    policy=Stage12DetectionPolicy(version="a238-locked-detection",
        window=12,stagnation_steps=3,stagnation_tolerance=.05,
        loop_repetitions=2,loop_max_period=2,entropy_min_samples=3,
        entropy_warning_fraction=.25,bias_min_outcomes_each=2,
        attribution_bias_threshold=.75)
    return s11,c11,c10,policy


def world_case(s11, c11, stratum, i):
    from i1lab.world import Position, BerryEffect
    from i1lab.injected_scenario import ScenarioEvent
    if stratum not in STRATA or type(i) is not int or not 0<=i<8:
        raise ValueError("unregistered factorial case")
    orig=Position(6+i%4,6+i//4)
    east=orig.moved("east")
    body=replace(s11.world.config.initial_body,energy=float(64+i%2),
        food=float(13+i%4),water=float(18+i%3),integrity=100.0)
    physics=replace(s11.world.config, version="a238-physical-v1",
        initial_position=orig,initial_body=body,food_decay_per_step=.20,
        water_decay_per_step=.40,action_energy_costs=COSTS,
        sleep_energy_gain=0.0,rest_integrity_gain=0.0,
        drink_water_gain=40.0,creature_damage=0.0,danger_zone_damage=10.0,
        berry_effects={"berry_a":BerryEffect(0,-100),
                       "berry_b":BerryEffect(6,0)})
    blocked=stratum==STRATA[0]
    layout=replace(s11.world._layout,obstacles=frozenset(),
        creatures=frozenset(),danger_zones=frozenset(),
        water_sources=frozenset({east if blocked else orig}),
        resources=(((orig if blocked else east),"berry_b",11+i%3),),
        lethal_zones=frozenset({east}) if stratum==STRATA[2] else frozenset())
    layout.validate(physics)
    geo=stratum in STRATA[3:]
    inputs=(ScenarioEvent(t_monde=9,sequence=0,operation="set_lethal_zone",
        payload={"position":east.as_dict(),"active":True}),) if stratum==STRATA[4] else ()
    return physics,layout,replace(c11,geographic=c11.geographic if geo else None),inputs,east
