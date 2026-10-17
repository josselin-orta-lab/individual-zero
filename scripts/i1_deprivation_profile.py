"""Versioned I1-only birth-time physiology profile for issue #231.

Apply to a new I1-generated WorldPhysicsConfig before constructing its
autonomous mortal runtime. Never mutate a live body's physical contract.
Historical cohorts remain at zero deprivation damage unless opted in.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any

POLICY = "i1-gradual-zero-needs-integrity-v1"
STARVATION_DAMAGE_PER_STEP = 0.5
DEHYDRATION_DAMAGE_PER_STEP = 1.0


def enable_gradual_deprivation(physics: Any) -> Any:
    """Freeze delayed physical consequences into a fresh I1 birth config.

    WorldBody alone applies damage once, after each actual primitive and its
    replenishment. The normal M11 contract fingerprints these config fields.
    I0 and shared Lab config types are deliberately not supported.
    """
    if (not type(physics).__module__.startswith("i1lab.")
            or not hasattr(physics, "starvation_integrity_damage_per_step")
            or not hasattr(physics, "dehydration_integrity_damage_per_step")):
        raise TypeError("requires generated I1 WorldPhysicsConfig")
    updated = replace(
        physics,
        version=physics.version + "+" + POLICY,
        starvation_integrity_damage_per_step=STARVATION_DAMAGE_PER_STEP,
        dehydration_integrity_damage_per_step=DEHYDRATION_DAMAGE_PER_STEP,
    )
    updated.validate()
    return updated
