"""Stage-5 deterministic compatibility fixture.

These values are software-compatibility values only, not campaign calibration.
"""

from __future__ import annotations

from i0.temperament import (
    LinearTemperamentCurve,
    Temperament,
    TemperamentMappingConfig,
)
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.stage5_runtime import Stage5Config, Stage5Runtime


def build_stage5_reference_runtime(
    *,
    temperament: Temperament | None = None,
    individual_id: str = "i0-stage5-reference",
) -> Stage5Runtime:
    stage4 = build_stage4_reference_runtime()
    tau = temperament or Temperament(0.0, 0.0, 0.0, 0.0, 0.0)

    mapping = TemperamentMappingConfig(
        version="stage5-reference-mapping-v1",
        gatekeeper_base_weights=dict(stage4._config.gatekeeper.weights),
        gatekeeper_alpha={
            "b": 0.4,
            "n": 0.5,
            "urg": 0.3,
            "risk": 0.6,
            "value": 0.7,
        },
        reward_extrinsic_alpha=0.5,
        risk_k_pi=0.7,
        risk_alpha_pi=0.8,
        uncertainty_k_chi=0.4,
        protective_threshold_delta=0.2,
        base_inertia=stage4._config.competition.inertia,
        goal_protection_inertia_curve=LinearTemperamentCurve(
            at_minus_one=0.05,
            at_zero=stage4._config.competition.inertia,
            at_plus_one=0.2,
        ),
        base_body_weights=dict(stage4._config.value_needs.weights),
        integrity_weight_curve=LinearTemperamentCurve(
            at_minus_one=0.5,
            at_zero=stage4._config.value_needs.weights["integrity"],
            at_plus_one=1.8,
        ),
        discount_beta=None,
    )

    return Stage5Runtime(
        world_config=stage4.world.config,
        layout=stage4.world._layout,
        safety_config=stage4.stage3.substrate.safety._config,
        safety_facts=stage4.stage3.control._facts,
        protected_integrity_threshold=(
            stage4.stage3.control._config.protected_integrity_threshold
        ),
        config=Stage5Config(
            version="stage5-reference-v1",
            temperament=tau,
            mapping=mapping,
            stage4=stage4._config,
        ),
        individual_id=individual_id,
    )
