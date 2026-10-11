"""Stage-4 deterministic compatibility fixture.

IMPORTANT: these values are for software replay compatibility only.
They are not campaign parameters, calibration results, or recommended values.
Scientific runs must provide their own preregistered P-xx registry.

The fixture traverses the minimal cognitive loop by starting thirsty with a
known water source two cells east, then continues for a full 300-step day.
"""

from __future__ import annotations

from i0.modules import (
    CompetitionConfig,
    GatekeeperConfig,
    GoalManagerConfig,
    PlanningConfig,
    StaticSafetyFacts,
    ValueNeedsConfig,
)
from lab.compute_budget import ComputeBudgetConfig
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage4_runtime import Stage4Config, Stage4Runtime
from lab.world import (
    BerryEffect,
    BodyState,
    Position,
    ToolRecipe,
    WorldLayout,
    WorldPhysicsConfig,
)


def build_stage4_reference_runtime(*, autonomous_mortal=False) -> Stage4Runtime:
    world = WorldPhysicsConfig(
        version="stage4-reference-world-v1",
        width=32,
        height=32,
        day_steps=300,
        night_steps=100,
        night_start_step=200,
        initial_body=BodyState(
            energy=50.0,
            food=60.0,
            water=20.0,
            integrity=100.0,
        ),
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
        drink_water_gain=40.0,
        berry_effects={
            "berry_a": BerryEffect(10.0, 0.0),
            "berry_b": BerryEffect(5.0, -100.0),
        },
        creature_damage=0.0,
        danger_zone_damage=10.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )

    stage4 = Stage4Config(
        version="stage4-reference-cognition-v1",
        perception_ttl_steps=5,
        value_needs=ValueNeedsConfig(
            version="stage4-reference-needs-v1",
            setpoints={
                "energy": 50.0,
                "food": 60.0,
                "water": 60.0,
                "integrity": 100.0,
            },
            weights={
                "energy": 1.0,
                "food": 1.0,
                "water": 1.0,
                "integrity": 1.0,
            },
            normalization_scales={
                "energy": 100.0,
                "food": 100.0,
                "water": 100.0,
                "integrity": 100.0,
            },
            p_min=0.1,
            contribution_ttl_steps=5,
        ),
        goals=GoalManagerConfig(
            version="stage4-reference-goals-v1",
            p_min=0.1,
            replacement_hysteresis=0.1,
            critical_pressure=0.9,
            impossible_failures_required=2,
            refractory_steps=3,
        ),
        gatekeeper=GatekeeperConfig(
            version="stage4-reference-gate-v1",
            k_slots=4,
            recency_window_steps=5,
            replacement_hysteresis=0.1,
            safety_threshold=0.8,
            queue_capacity=10,
            emission_quota=20,
            slot_quota=2,
            quota_window_steps=3,
            weights={
                "b": 1.0,
                "n": 1.0,
                "urg": 1.0,
                "risk": 1.0,
                "value": 1.0,
            },
        ),
        planning=PlanningConfig(
            version="stage4-reference-plan-v1",
            option_ttl_steps=20,
        ),
        competition=CompetitionConfig(
            version="stage4-reference-comp-v1",
            c_max=5,
            urgency_max=2.0,
            urgency_scale_cycles=2.0,
            leak=0.0,
            noise_sigma=0.0,
            gain=1.0,
            base_threshold=0.5,
            threshold_floor=0.1,
            inertia=0.1,
            residual=0.5,
            options_max=8,
            substitution_evidence={
                "se_deplacer": 1.0,
                "collecter": 1.0,
                "manger": 1.0,
                "boire": 1.0,
                "dormir": 1.0,
                "attendre": 0.0,
                "poser_une_pierre": 0.5,
                "fabriquer_outil": 0.5,
            },
        ),
        compute_budget=ComputeBudgetConfig(
            version="stage4-reference-budget-v1",
            cycle_ceiling=100,
            module_envelopes={
                "perception": 20,
                "value_needs": 10,
                "goal_manager": 10,
                "planning": 20,
                "bus": 10,
                "gatekeeper": 10,
                "competition": 30,
                "action_control": 10,
            },
            protected_modules=frozenset({
                "bus",
                "gatekeeper",
                "action_control",
            }),
            protected_capacity=20,
            operation_costs={
                "perception_publish": 1,
                "value_needs_cycle": 1,
                "goal_arbitrate": 1,
                "planning_build": 2,
                "bus_pour": 1,
                "gatekeeper_select": 1,
                "competition_register": 1,
                "competition_evaluate": 1,
                "control_admit": 1,
            },
        ),
    )

    return Stage4Runtime(
        world_config=world,
        layout=WorldLayout(
            water_sources=frozenset({Position(4, 2)}),
        ),
        safety_config=SafetyProtocolConfig(
            version="stage4-reference-safety-v1",
            lethal_max=2,
            mode="campaign",
        ),
        safety_facts=StaticSafetyFacts(),
        protected_integrity_threshold=20.0,
        config=stage4,
        autonomous_mortal=autonomous_mortal,
    )
