"""Deterministic, individually varied, immutable I1 birth temperament.

Birth diversity is derived from the independently declared life identity,
never from hidden WorldBody state, future outcomes, or a mutable RNG. The
canonical Stage5 mapping projects the five raw traits exactly once, and the
result is frozen in Stage11Config and hence in the M11 birth contract.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256

from i1.temperament import Temperament, TemperamentProjection

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
    # Retain the normative Stage5 projection mapping, inherited from its
    # reference and consistent with the nested Stage4 neutral contract.
    from .stage5_reference_fixture import build_stage5_reference_runtime
    reference = build_stage5_reference_runtime(autonomous_mortal=True)
    mapping = reference.stage5_config.mapping
    tau = temperament_for_life(life_id)
    params = TemperamentProjection(
        temperament=tau, mapping=mapping, individual_id=life_id,
    ).parameters
    configured = replace(
        stage11_config, version=stage11_config.version + "+" + VERSION,
        temperament_parameters=params,
    )
    configured.validate()
    return configured
