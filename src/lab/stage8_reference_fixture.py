"""Stage-8 deterministic online-learning compatibility fixture.

P-13/P-30/P-31/P-32 values are software-compatibility values only, not
campaign calibration.
"""

from __future__ import annotations

from i0.modules import TDLearningConfig, ValueFeatureConfig
from i0.modules.active_kappa import KappaConfig
from i0.modules.active_precision import PrecisionConfig
from i0.modules.stage8_evaluator import Stage8EvaluationConfig

from .stage7_reference_fixture import build_stage7_reference_runtime
from .stage8_runtime import Stage8Config, Stage8Runtime


def build_stage8_reference_runtime(*, autonomous_mortal: bool = False) -> Stage8Runtime:
    stage7 = build_stage7_reference_runtime(autonomous_mortal=autonomous_mortal)
    beta = stage7._stage7_config.stage6.evaluation.beta
    evidence_scale = (
        stage7._stage7_config.stage6.evaluation.evidence_scale
    )
    return Stage8Runtime(
        world_config=stage7.world.config,
        layout=stage7.world._layout,
        safety_config=stage7.stage3.substrate.safety._config,
        safety_facts=stage7.stage3.control._facts,
        protected_integrity_threshold=(
            stage7.stage3.control._config.protected_integrity_threshold
        ),
        config=Stage8Config(
            version="stage8-reference-v1",
            stage7=stage7._stage7_config,
            td=TDLearningConfig(
                version="p31-stage8-reference-v1",
                eta=0.05,
                lambda_e=0.8,
                beta=beta,
                evidence_scale=evidence_scale,
                features=ValueFeatureConfig(
                    version="p32-stage8-reference-v1",
                    feature_names=(
                        "bias",
                        "energy",
                        "food",
                        "water",
                        "integrity",
                        "x",
                        "y",
                        "is_night",
                        "goal_drink",
                        "goal_eat",
                        "goal_recover_energy",
                        "goal_restore_integrity",
                    ),
                    position_scale_x=31.0,
                    position_scale_y=31.0,
                ),
            ),
            precision=PrecisionConfig(
                version="stage8-precision-source-v1",
                prior_weight=2.0,
                initial_rmse_by_source={
                    "world_symbolic": 1.0,
                    "body_telemetry": 1.0,
                },
                variance_floor=0.0001,
                maximum_precision=100.0,
            ),
            kappa=KappaConfig(
                version="p33-stage8-reference-v1",
                classes=5,
                prior_strength=2.0,
                equipment_priors={},
            ),
            evaluation=Stage8EvaluationConfig(
                version="p13-stage8-reference-v1",
                n0=3.0,
                evidence_scale=evidence_scale,
                extrinsic_gain=1.0,
            ),
        ),
        equipment=stage7.equipment,
        autonomous_mortal=autonomous_mortal,
    )
