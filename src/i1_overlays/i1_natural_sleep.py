"""I1-only versioned restoration of lived sleep motivation and recovery.

This is a fresh-birth policy, not a behavior script. It restores the
existing Stage10 fatigue, memory backlog, and night terms, gives the physical
action a real energy consequence, and enables bounded paid consolidation.
It never sends a command, edits innate danger knowledge, or changes I0.
"""
from __future__ import annotations

from dataclasses import replace

from i1.modules.consolidation_batch import BatchSelectionPolicy
from i1.modules.consolidation_budget import ConsolidationBudgetConfig
from i1.modules.consolidation_replay_agenda import ReplayAgendaPolicy
from i1.modules.consolidation_semantics import SemanticPassPolicy

POLICY = "i1-natural-sleep-fatigue-memory-night-energy-v2-procedural-batch"

# Explicit experimental values, not a discovered or learned food/water prior.
# Energy is deliberately ABSENT from the intrinsic sleep-pressure formula:
# the ordinary Value/Needs reward and personally lived Q carry that pathway.
SLEEP_ENERGY_GAIN = 3.0
FATIGUE_GAIN_PER_UC_FRACTION = 0.7
FATIGUE_RECOVERY_PER_SLEEP_STEP = 0.3
FATIGUE_WEIGHT = 0.65
CONSOLIDATION_WEIGHT = 0.25
NIGHT_WEIGHT = 0.20
SLEEP_INTRINSIC_WEIGHT = 0.9

# All real semantic work is charged to existing Stage10 P-42 custody.
# Small batches and per-period limits prevent unconstrained consolidation;
# a pass may defer rather than receive free work or synthetic evidence.
CONSOLIDATION_STEP_UC = 640
CONSOLIDATION_PERIOD_UC = 2560

# Ordinary birth metabolism, explicitly versioned and physically observable.
# These are provisional simulation units rather than biological constants.
LIVING_PHYSIOLOGY_POLICY = "i1-living-physical-defaults-v2-deprivation-canonical-only"
DEFAULT_STARVATION_DAMAGE = 0.5
DEFAULT_DEHYDRATION_DAMAGE = 1.0
DEFAULT_FOOD_DECAY = 0.20
DEFAULT_WATER_DECAY = 0.40
DEFAULT_REST_INTEGRITY_GAIN = 0.20
DEFAULT_ACTION_ENERGY_COSTS = {
    "se_deplacer": 2.0,
    "collecter": 1.0,
    "manger": 0.5,
    "boire": 0.5,
    "poser_une_pierre": 1.5,
    "fabriquer_outil": 1.5,
    "dormir": 0.25,
    "attendre": 0.35,
}


def enable_living_physiology_birth(world_config):
    """Replace inert reference defaults with a living, versioned I1 world.

    Preserve nonzero world-specific costs, decay and healing (e.g. a designed
    heldout environment). This is frozen before birth, never modified from
    an observed result. Historical experiments remain reproducible by their
    original source revision; no I0 or shared Lab world is changed.
    """
    if not type(world_config).__module__.startswith("i1lab."):
        raise TypeError("living physiology applies only to generated I1")
    if LIVING_PHYSIOLOGY_POLICY in world_config.version:
        raise ValueError("living I1 physiology was already installed")
    costs = dict(world_config.action_energy_costs)
    if set(costs) != set(DEFAULT_ACTION_ENERGY_COSTS):
        raise ValueError("unknown physical action-cost schema")
    if all(float(v) == 0.0 for v in costs.values()):
        costs = dict(DEFAULT_ACTION_ENERGY_COSTS)
    upgraded = replace(
        world_config,
        version=world_config.version + "+" + LIVING_PHYSIOLOGY_POLICY,
        starvation_integrity_damage_per_step=(
            DEFAULT_STARVATION_DAMAGE
            if world_config.starvation_integrity_damage_per_step == 0.0
            else world_config.starvation_integrity_damage_per_step
        ),
        dehydration_integrity_damage_per_step=(
            DEFAULT_DEHYDRATION_DAMAGE
            if world_config.dehydration_integrity_damage_per_step == 0.0
            else world_config.dehydration_integrity_damage_per_step
        ),
        food_decay_per_step=(
            DEFAULT_FOOD_DECAY if world_config.food_decay_per_step == 0.0
            else world_config.food_decay_per_step
        ),
        water_decay_per_step=(
            DEFAULT_WATER_DECAY if world_config.water_decay_per_step == 0.0
            else world_config.water_decay_per_step
        ),
        action_energy_costs=costs,
        rest_integrity_gain=(
            DEFAULT_REST_INTEGRITY_GAIN
            if world_config.rest_integrity_gain == 0.0
            else world_config.rest_integrity_gain
        ),
    )
    upgraded.validate()
    return upgraded


def enable_natural_sleep_birth(*, world_config, stage10_config):
    """Return fresh I1 physical and Stage10 configs, without mutating sources.

    Called before construction of a separately born mortal individual. The
    original frozen A2.38/A2.39 configurations remain unchanged, including
    their intentionally zeroed sleep motives and energy gain.
    """
    if (not type(world_config).__module__.startswith("i1lab.")
            or not type(stage10_config).__module__.startswith("i1lab.")):
        raise TypeError("natural sleep requires isolated generated I1 Lab configs")
    if (POLICY in world_config.version or POLICY in stage10_config.version):
        raise ValueError("I1 natural sleep policy already applied to birth config")
    world_config = enable_living_physiology_birth(world_config)
    world = replace(
        world_config,
        version=world_config.version + "+" + POLICY,
        sleep_energy_gain=max(
            float(world_config.sleep_energy_gain), SLEEP_ENERGY_GAIN
        ),
    )

    old_sleep = stage10_config.sleep
    sleep = replace(
        old_sleep,
        version=old_sleep.version + "+" + POLICY,
        fatigue_gain=FATIGUE_GAIN_PER_UC_FRACTION,
        sleep_fatigue_recovery=FATIGUE_RECOVERY_PER_SLEEP_STEP,
        waking_recovery_profile_relief=0.0,
        fatigue_weight=FATIGUE_WEIGHT,
        consolidation_weight=CONSOLIDATION_WEIGHT,
        night_weight=NIGHT_WEIGHT,
        unconsolidated_episode_reference=8.0,
        memory_saturation_reference=2.0,
        natural_wake_threshold=0.1,
        alert_wake_threshold=0.7,
        max_consecutive_sleep_steps=6,
    )
    # Only visible body channels may wake a sleeper. These are ALERTS that
    # resume deliberation, never orders to drink/eat or oracle danger labels.
    critical = dict(stage10_config.critical_body_thresholds)
    for measure, lower_bound in (
        ("energy", 10.0),
        ("food", 10.0),
        ("water", 15.0),
        ("integrity", 25.0),
    ):
        critical[measure] = max(float(critical.get(measure, 0.0)), lower_bound)

    selector = BatchSelectionPolicy(
        version=POLICY + ":selection",
        # Two independent successful episodes are required for even a
        # private procedure. A one-episode batch made compilation impossible.
        # Four is a bounded candidate set; every scan/replay/pass still pays UC.
        maximum_episodes=4,
        consequence_reference=1.0,
        surprise_reference=1.0,
        recency_window_steps=8,
        repetition_reference=1,
        weight_consequence=1.0,
        weight_surprise=1.0,
        weight_recency=1.0,
        weight_repetition=1.0,
        ageing_gain_per_step=0.1,
        scan_uc_per_episode=1,
    )
    semantic = SemanticPassPolicy(
        version=POLICY + ":sixpass",
        replay=ReplayAgendaPolicy(
            version=POLICY + ":replay",
            recent_window_steps=3,
            start_with_recent=True,
        ),
        skill_success_threshold=2,
        nearby_context_radius=1,
        rule_expiry_steps=20,
    )
    work = ConsolidationBudgetConfig(
        version=POLICY + ":work",
        period_capacity_uc=CONSOLIDATION_PERIOD_UC,
        step_slot_uc=CONSOLIDATION_STEP_UC,
        operation_costs={
            "semantic_plan_build": 1,
            "replay_agenda_scan": 1,
            "episode_scan": 1,
            "episode_replay": 1,
            "rule_extraction": 1,
            "skill_compilation": 1,
            "kappa_recalibration": 1,
            "index_maintenance": 1,
            "pass_prepare": 1,
            "pass_validate": 1,
        },
    )
    stage10 = replace(
        stage10_config,
        version=stage10_config.version + "+" + POLICY,
        sleep=sleep,
        sleep_work=work,
        selection_policy=selector,
        semantic_policy=semantic,
        intrinsic_weight=SLEEP_INTRINSIC_WEIGHT,
        critical_body_thresholds=critical,
        p_cons_min=0.1,
        maximum_passes_per_sleep_step=2,
        incremental_selection=True,
        paid_pending_index=True,
    )
    world.validate()
    stage10.validate()
    return world, stage10
