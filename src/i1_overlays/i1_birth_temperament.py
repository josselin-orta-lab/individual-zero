"""Deterministic, individually varied, immutable I1 birth temperament.

Birth diversity is derived from the independently declared life identity,
never from hidden WorldBody state, future outcomes, or a mutable RNG. The
canonical Stage5 mapping projects the five raw traits exactly once, and the
result is frozen in Stage11Config and hence in the M11 birth contract.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256

from i1.temperament import (
    LinearTemperamentCurve,
    Temperament, TemperamentMappingConfig, TemperamentProjection,
)

VERSION = "i1-life-id-temperament-v1"
CHANNELS = (
    "reward_sensitivity", "threat_sensitivity", "exploration",
    "goal_protection", "affiliation",
)


def temperament_for_life(life_id: str) -> Temperament:
    if (type(life_id) is not str or not life_id.startswith("i1:")
            or not 1 <= len(life_id) <= 128):
        raise ValueError("I1 temperament requires a bounded distinct birth identity")
    coordinates = []
    for channel in CHANNELS:
        digest = sha256((VERSION + ":" + life_id + ":" + channel).encode("utf-8")).digest()
        # Exact deterministic integer-to-float map, no stochastic runtime draw.
        coordinates.append(round(2.0 * int.from_bytes(digest[:8], "big") / (2**64 - 1) - 1.0, 6))
    temperament = Temperament(*coordinates)
    temperament.validate()
    return temperament


def configure_birth_temperament(stage11_config, *, life_id: str):
    """Replace only actual Stage11 projected temperament before first birth."""
    if not type(stage11_config).__module__.startswith("i1lab."):
        raise TypeError("generated isolated I1 Stage11 config required")
    if VERSION in stage11_config.version:
        raise ValueError("birth temperament already installed")
    # Stage5's neutral reference was formerly retrieved by *birthing a
    # second autonomous mortal* merely to read a configuration table.
    # Reproduce its published pure projection constants here instead.
    # No other individual, WorldBody, Scheduler, WAL or journal is created.
    s9 = stage11_config.stage9
    s8 = s9.stage8
    s7 = s8.stage7
    s6 = s7.stage6
    s4 = s6.stage4
    mapping = TemperamentMappingConfig(
        version="stage5-reference-mapping-v1+" + VERSION,
        gatekeeper_base_weights=dict(s4.gatekeeper.weights),
        gatekeeper_alpha={
            "b": 0.4, "n": 0.5, "urg": 0.3,
            "risk": 0.6, "value": 0.7,
        },
        reward_extrinsic_alpha=0.5,
        risk_k_pi=0.7,
        risk_alpha_pi=0.8,
        uncertainty_k_chi=0.4,
        protective_threshold_delta=0.2,
        base_inertia=s4.competition.inertia,
        goal_protection_inertia_curve=LinearTemperamentCurve(
            at_minus_one=0.05,
            at_zero=s4.competition.inertia,
            at_plus_one=0.2,
        ),
        base_body_weights=dict(s4.value_needs.weights),
        integrity_weight_curve=LinearTemperamentCurve(
            at_minus_one=0.5,
            at_zero=s4.value_needs.weights["integrity"],
            at_plus_one=1.8,
        ),
        discount_beta=None,
    )
    mapping.validate()
    tau = temperament_for_life(life_id)
    params = TemperamentProjection(
        temperament=tau, mapping=mapping, individual_id=life_id,
    ).parameters
    # Stage11's descriptive projection alone is not enough: the canonical
    # Gatekeeper, Value/Needs and Competition owners must actually consume
    # the same derived parameters, just as Stage5Runtime does.
    stage4 = replace(
        s4, version=s4.version + "+" + VERSION,
        gatekeeper=replace(
            s4.gatekeeper, weights=dict(params.gatekeeper_weights),
        ),
        value_needs=replace(
            s4.value_needs, weights=dict(params.body_weights),
        ),
        competition=replace(s4.competition, inertia=params.inertia),
    )
    stage9 = replace(
        s9, stage8=replace(
            s8,
            # Stage11's live option evaluator consumes this exact Stage8
            # config. An unconnected gain would make the born individual's
            # reward sensitivity descriptive rather than motivational.
            evaluation=replace(
                s8.evaluation,
                version=s8.evaluation.version + "+" + VERSION,
                extrinsic_gain=(
                    s8.evaluation.extrinsic_gain
                    * params.extrinsic_value_gain
                ),
            ),
            stage7=replace(
                s7, stage6=replace(s6, stage4=stage4),
            ),
        ),
    )
    configured = replace(
        stage11_config, version=stage11_config.version + "+" + VERSION,
        stage9=stage9, temperament_parameters=params,
    )
    configured.validate()
    return configured
