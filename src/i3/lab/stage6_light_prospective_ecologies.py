"""Source-scoped Stage6 F0 ecological adapter; P2 historical bytes stay frozen.

P2's original _generate_ecology uses worldgen's development=True default and
cannot materialize prospective reserved seeds >= 1,000,000. The P2 implementation
is source-pinned by historical tests and MUST NOT be changed. This module
reproduces its three F0 transformations verbatim with explicit development=False
and accepts only a fresh, high-domain Stage6 world seed. It does not allocate
seeds, admit a cohort, start a life, or authorize scientific exposure.
"""
from __future__ import annotations

from dataclasses import replace

from i3.lab import p2_ecologies as P2
from i3.lab.worldgen import generate as generate_world
from i3.modules.world import WaterSource

FAMILIES = P2.FAMILIES
HORIZON = P2.HORIZON
STAGE6_WORLD_LO = 2 << 60
STAGE6_WORLD_HI = 3 << 60


def _build_family(family: str, seed: int):
    """Exact P2 F0 WorldSpec transforms; no native life or cognitive actor."""
    if family == "depletion":
        base = generate_world("R", seed, development=False)
        spec = replace(
            base, name=f"p2-depletion-{seed}",
            water={
                q: WaterSource(s.gain, s.stock, s.max_stock, s.restock_every)
                for q, s in base.water.items()},
            food=P2._clone_food(base))
    elif family == "stable":
        base = generate_world("dev", seed, development=False)
        spec = replace(
            base, name=f"p2-stable-{seed}",
            water={q: WaterSource(s.gain) for q, s in base.water.items()},
            food=P2._clone_food(base))
    elif family == "pulse":
        base = generate_world("dev", seed, development=False)
        waters = {
            q: WaterSource(s.gain, stock=3, max_stock=3, restock_every=0)
            for q, s in base.water.items()}
        changes = []
        for i, q in enumerate(sorted(waters)):
            phase = (seed + 7 * i) % 12
            for t in range(30 + phase, HORIZON + 1, 48):
                changes.extend(((t, "water_stock", q, 0),
                                (t + 16, "water_stock", q, 3)))
        changes = tuple(
            sorted((x for x in changes if x[0] <= HORIZON),
                   key=lambda x: (x[0], x[2])))
        spec = replace(
            base, name=f"p2-pulse-{seed}", water=waters,
            food=P2._clone_food(base), changes=changes)
    else:
        raise ValueError("unknown frozen P2 F0 ecological family")
    P2.validate_ecology(spec, family)
    return spec


def world_for_stage6(family: str, seed: int):
    """Only source/owner-bound Stage6 runners may use this high seed slot.

    This *pure factory* verifies the namespace but does NOT independently
    authenticate a source, owner, plan, population, birth or archive claim.
    """
    if type(seed) is not int or not STAGE6_WORLD_LO <= seed < STAGE6_WORLD_HI:
        raise PermissionError("Stage6 physical World seed outside fresh reserved namespace")
    if family not in FAMILIES:
        raise ValueError("Stage6 must retain the exact three F0 ecological families")
    return _build_family(family, seed)
