"""Public software fixture for the Stage-10 waking-health slice.

Explicit dev-only P-39/P-40/P-41 constants. No sleep scheduling, `dormir`
action, consolidation, scientific parameters or held-out worlds.
"""
from i0.modules.sleep_pressure import SleepPressureConfig

from .stage9_reference_fixture import build_stage9_reference_runtime
from .stage10_health_runtime import Stage10HealthConfig, Stage10HealthRuntime


def build_stage10_health_reference_runtime():
    baseline = build_stage9_reference_runtime()
    return Stage10HealthRuntime(
        world_config=baseline.world.config,
        layout=baseline.world._layout,
        safety_config=baseline.stage3.substrate.safety._config,
        safety_facts=baseline.stage3.control._facts,
        protected_integrity_threshold=(
            baseline.stage3.control._config.protected_integrity_threshold
        ),
        config=Stage10HealthConfig(
            version="stage10-waking-health-development-v1",
            stage9=baseline._stage9_config,
            sleep=SleepPressureConfig(
                version="p39-p40-p41-waking-integration-dev-v1",
                fatigue_gain=0.6,
                sleep_fatigue_recovery=0.1,
                waking_recovery_profile_relief=0.05,
                fatigue_weight=0.5,
                consolidation_weight=0.3,
                night_weight=0.2,
                unconsolidated_episode_reference=8.0,
                memory_saturation_reference=2.0,
                natural_wake_threshold=0.2,
                alert_wake_threshold=0.65,
                max_consecutive_sleep_steps=5,
            ),
            memory_reference_capacity=16,
        ),
        equipment=baseline.equipment,
    )
