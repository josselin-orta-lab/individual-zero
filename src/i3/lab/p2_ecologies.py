"""P2 laboratory ecological contract. Never an input to an I3 mind.

The three mechanisms are different, not merely different random seeds. Existing
G2/G2e conditions and their generators are untouched. No P3 selection runs here.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from types import MappingProxyType

from i3.lab.worldgen import generate
from i3.modules.world import FoodPatch, WaterSource, World, WorldSpec
from i3.runtime.provenance import world_snapshot

PROTOCOL = "i3-p2-ecologies-v1"
FAMILIES = ("stable", "depletion", "pulse")
# Fixed, non-overlapping worlds. Previous G2e selection (100..129) and
# evaluation (1_000_200..1_000_299) are deliberately excluded.
COHORTS = MappingProxyType({
    "development": range(2_000, 2_100),
    "selection": range(10_000, 10_400),
    "validation": range(30_000, 30_200),
    "reserve": range(1_200_000, 1_200_200),
})
EVOLUTION_MIX = MappingProxyType({"stable": 1, "depletion": 1, "pulse": 1})
HORIZON = 400


def partition_manifest() -> dict:
    """Public plan; the reserved world *instances* remain unopened."""
    out = {
        "protocol": PROTOCOL,
        "families": list(FAMILIES),
        "cohorts": {k: {"first": v.start, "stop_exclusive": v.stop}
                    for k, v in COHORTS.items()},
        "evolution_mix": dict(EVOLUTION_MIX),
        "horizon": HORIZON,
        "disjoint_by": ["family", "seed", "cohort"],
        "reserve_policy": "locked_until_prospective_P4_protocol",
    }
    out["manifest_sha256"] = sha256(
        json.dumps(out, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return out


def _clone_food(spec):
    return {q: FoodPatch(p.token, p.quantity, p.max_quantity, p.restock_every)
            for q, p in spec.food.items()}


def _generate_ecology(family: str, seed: int) -> WorldSpec:
    if family == "depletion":
        base = generate("R", seed)
        spec = replace(base, name=f"p2-depletion-{seed}",
                       water={q: WaterSource(s.gain, s.stock, s.max_stock, s.restock_every)
                              for q, s in base.water.items()}, food=_clone_food(base))
    elif family == "stable":
        base = generate("dev", seed)
        spec = replace(base, name=f"p2-stable-{seed}",
                       water={q: WaterSource(s.gain) for q, s in base.water.items()},
                       food=_clone_food(base))
    elif family == "pulse":
        base = generate("dev", seed)
        # Supply returns on a fixed external cycle rather than individual acts.
        # No hidden schedule is ever added to World.capture().
        waters = {q: WaterSource(s.gain, stock=3, max_stock=3, restock_every=0)
                  for q, s in base.water.items()}
        changes = []
        for i, q in enumerate(sorted(waters)):
            phase = (seed + 7 * i) % 12
            for t in range(30 + phase, HORIZON + 1, 48):
                changes.extend(((t, "water_stock", q, 0),
                                (t + 16, "water_stock", q, 3)))
        changes = tuple(sorted((x for x in changes if x[0] <= HORIZON),
                               key=lambda x: (x[0], x[2])))
        spec = replace(base, name=f"p2-pulse-{seed}", water=waters,
                       food=_clone_food(base), changes=changes)
    else:
        raise ValueError("unknown P2 ecological family")
    validate_ecology(spec, family)
    return spec


def validate_ecology(spec: WorldSpec, family: str) -> None:
    """Structural validity only; NOT a proof that the world is livable."""
    if not isinstance(spec, WorldSpec) or not (3 <= spec.width <= 30 and 3 <= spec.height <= 30):
        raise ValueError("invalid P2 world dimensions")
    def inside(q):
        return (type(q) is tuple and len(q) == 2
                and all(type(v) is int for v in q)
                and 0 <= q[0] < spec.width and 0 <= q[1] < spec.height)
    if not inside(spec.spawn) or not spec.water or not spec.food:
        raise ValueError("invalid spawn or resource inventory")
    if any(not inside(q) for q in (*spec.water, *spec.food)):
        raise ValueError("resource outside world")
    if set(spec.water) & set(spec.food):
        raise ValueError("overlapping resource cells")
    if not all(p.token in spec.token_effects and p.quantity > 0 for p in spec.food.values()):
        raise ValueError("unknown food effects or empty initial food")
    if not any(gain > 0 and harm >= 0 for gain, harm in spec.token_effects.values()):
        raise ValueError("no safe nourishment")
    World(spec)  # validates actual body and physics
    if family == "stable":
        if any(s.stock is not None for s in spec.water.values()) or spec.changes:
            raise ValueError("stable ecology must have persistent water")
    elif family == "depletion":
        finite = [s for s in spec.water.values() if s.stock is not None
                  and s.restock_every == 0]
        unlimited = [s for s in spec.water.values() if s.stock is None]
        if len(finite) != 1 or len(unlimited) != 1 or spec.changes:
            raise ValueError("depletion ecology requires near finite and far persistent wells")
    elif family == "pulse":
        if any(s.stock is None or s.restock_every for s in spec.water.values()):
            raise ValueError("pulsed sources must be finite with external changes")
        if not spec.changes or not any(x[3] == 0 for x in spec.changes) or not any(
                x[3] > 0 for x in spec.changes):
            raise ValueError("pulse ecology requires dry and recovery events")
        if any(t < 1 or t > HORIZON or kind != "water_stock" or
               q not in spec.water or (type(n) is not int or n < 0 or n > 3)
               for t, kind, q, n in spec.changes):
            raise ValueError("invalid pulse schedule")
    else:
        raise ValueError("unknown P2 ecological family")


def world_for(family: str, cohort: str, index: int) -> WorldSpec:
    """Fail closed on reserve. The P4 operator must authorize it separately."""
    if family not in FAMILIES or cohort not in COHORTS:
        raise ValueError("unknown P2 ecological family or cohort")
    if type(index) is not int or not 0 <= index < len(COHORTS[cohort]):
        raise ValueError("cohort index outside its declared range")
    if cohort == "reserve":
        raise PermissionError("P2 cannot open the prospectively reserved P4 worlds")
    seed = COHORTS[cohort][index]
    return _generate_ecology(family, seed)


def fingerprint(spec: WorldSpec) -> str:
    return sha256(json.dumps(world_snapshot(spec), sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()
