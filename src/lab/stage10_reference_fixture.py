"""Stage-10 development-only reference fixture."""
from i0.modules.sleep_pressure import SleepPressureConfig
from i0.modules.consolidation_budget import ConsolidationBudgetConfig
from .stage9_reference_fixture import build_stage9_reference_runtime
from .stage10_runtime import Stage10Runtime, Stage10Config

def build_stage10_reference_runtime(*, start_fatigued=False):
    base = build_stage9_reference_runtime()
    runtime = Stage10Runtime(
        world_config=base.world.config,
        layout=base.world._layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
        config=Stage10Config(
            version="stage10-reference-dev-v1",
            stage9=base._stage9_config,
            sleep=SleepPressureConfig(
                version="stage10-sleep-p39-p40-test-v1",
                fatigue_gain=0.7,sleep_fatigue_recovery=0.3,
                waking_recovery_profile_relief=0.0,
                fatigue_weight=1.0,consolidation_weight=0.5,night_weight=0.3,
                unconsolidated_episode_reference=2.0,memory_saturation_reference=1.0,
                natural_wake_threshold=0.1,alert_wake_threshold=0.7,
                max_consecutive_sleep_steps=2,
            ),
            sleep_work=ConsolidationBudgetConfig(
                version="stage10-work-p42-test-v1",
                period_capacity_uc=30,step_slot_uc=8,
                operation_costs={
                    "episode_scan":1,"episode_replay":1,"rule_extraction":1,
                    "skill_compilation":1,"kappa_recalibration":1,
                    "index_maintenance":1,"pass_prepare":1,"pass_validate":1,
                },
            ),
            intrinsic_weight=4.0,memory_reference_capacity=16,sleep_option_uc=1,
            critical_body_thresholds={"integrity":25.0,"water":15.0},
            adjacent_threat_intensity=1.0,adjacent_threat_risk=1.0,
            critical_body_intensity=1.0,critical_body_risk=1.0,
            p_cons_min=0.5,
        ),
        equipment=base.equipment,
    )
    if start_fatigued:
        state = runtime.sleep_health.export_causal_state()
        state["fatigue"] = 1.0
        runtime.sleep_health.restore_causal_state(state)
    return runtime
