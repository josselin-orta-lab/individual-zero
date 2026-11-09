"""NON-EVIDENTIARY B1 WorldSpec preflight on a PUBLIC synthetic pair schedule.

This is a read-only, deterministic structural audit, NOT a new scientific
World source, World/life transport, owner permission or iid proof. It
instantiates WorldSpec values and calls P2's structural validation (which
transiently constructs a World to check physical consistency), but never
creates a Mind, initializes a scientific individual, advances a World step,
captures an observation or writes original life records.

Preserve P2's original code and existing admission barriers unchanged.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json

from . import p2_ecologies as P2
from . import stage2_survival_b1_sampling as B1
from .worldgen import generate
from i3.modules.world import FoodPatch, WaterSource
from i3.runtime.provenance import world_snapshot

SCHEMA = "i3-stage2-1-b1-synthetic-worldspec-audit/v1"
STATUS = "SYNTHETIC_SPEC_PREFLIGHT_NOT_PROSPECTIVE_AUTHORITY"


def _hash(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _clone_food(base):
    return {pos: FoodPatch(src.token, src.quantity, src.max_quantity,
                           src.restock_every) for pos, src in base.food.items()}


def _construct_f0_spec(family: str, seed: int):
    """Private F0-equivalent spec builder; NO source admission or life execution.

    Keep this a *separate copy* of the unchanged P2 semantics. Parity tests
    compare all three structures with P2 at old non-reserved seeds before
    the public-root synthetic 2^60 namespace is inspected.
    """
    if family not in P2.FAMILIES or type(seed) is not int or seed < 0:
        raise ValueError("invalid B1 WorldSpec family/seed")
    # B1 is not a development cohort; bypass the worldgen DEVELOPMENT
    # seed-range guard explicitly, without changing worldgen or P2.
    base = generate("R" if family == "depletion" else "dev", seed,
                    development=False)
    food = _clone_food(base)
    if family == "depletion":
        spec = replace(
            base, name=f"p2-depletion-{seed}", food=food,
            water={pos: WaterSource(src.gain, src.stock, src.max_stock,
                                    src.restock_every)
                   for pos, src in base.water.items()},
        )
    elif family == "stable":
        spec = replace(
            base, name=f"p2-stable-{seed}", food=food,
            water={pos: WaterSource(src.gain) for pos, src in base.water.items()},
        )
    else:
        water = {pos: WaterSource(src.gain, stock=3, max_stock=3,
                                  restock_every=0)
                 for pos, src in base.water.items()}
        changes = []
        for i, pos in enumerate(sorted(water)):
            phase = (seed + 7 * i) % 12
            for tick in range(30 + phase, P2.HORIZON + 1, 48):
                changes.extend(((tick, "water_stock", pos, 0),
                                (tick + 16, "water_stock", pos, 3)))
        changes = tuple(sorted(
            (item for item in changes if item[0] <= P2.HORIZON),
            key=lambda item: (item[0], item[2]),
        ))
        spec = replace(base, name=f"p2-pulse-{seed}", food=food,
                       water=water, changes=changes)
    P2.validate_ecology(spec, family)
    return spec


def _snapshot_digests(spec):
    """Two digests: full provenance and material structure excluding name.

    A unique seed-bearing name is NOT sufficient evidence that two actual
    generated ecological structures differ.
    """
    snapshot = world_snapshot(spec)
    full = _hash(snapshot)
    without_name = {key: value for key, value in snapshot.items()
                    if key != "name"}
    return full, _hash(without_name)


def _reject_spec_collision(seen: dict, digest: str, pair_id: str) -> None:
    if digest in seen:
        raise ValueError(
            f"duplicate ecological structure: {seen[digest]} and {pair_id}; "
            "no reroll, exclusion or convenient replacement permitted"
        )
    seen[digest] = pair_id


def audit_synthetic_preview(manifest=None) -> dict:
    """Audit ONLY the public B1 synthetic preview's actual WorldSpecs.

    No user-provided witness, new index registration or runner is accepted.
    No World is stepped. Return aggregated digest/collision evidence only,
    never individual world layouts, outcomes or full generation traces.
    """
    if manifest is None:
        manifest = B1.preview(B1.PREVIEW_WITNESS)
    B1.verify_preview(
        manifest, B1.PREVIEW_WITNESS, pairs=B1.PREVIEW_PAIRS,
    )
    seen_full, seen_unnamed = {}, {}
    world_hashes = []
    family_counts = Counter()
    for row in manifest["proposed_units"]:
        seed = row["world_seed"]
        if (type(seed) is not int or
                not B1.WORLD_BASE <= seed < B1.WORLD_BASE + (1 << B1.SEED_BITS)):
            raise ValueError("non-synthetic or legacy World seed in B1 preview")
        pair_id = row["pair_id"]
        spec = _construct_f0_spec(row["family"], seed)
        full, unnamed = _snapshot_digests(spec)
        _reject_spec_collision(seen_full, full, pair_id)
        _reject_spec_collision(seen_unnamed, unnamed, pair_id)
        world_hashes.append((pair_id, row["family"], full, unnamed))
        family_counts[row["family"]] += 1
    if dict(family_counts) != {
        name: manifest["family_counts"][name] for name in B1.FAMILIES
    }:
        raise ValueError("generated WorldSpec family counts changed")
    total = len(world_hashes)
    if total != B1.PREVIEW_PAIRS:
        raise ValueError("missing synthetic WorldSpec in B1 preflight")
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "public_synthetic_allocation_sha256": manifest["allocation_sha256"],
        "aggregate_worldspec_digest_sha256": _hash(world_hashes),
        "worldspec_structures_generated": total,
        "structural_world_validations": total,
        "unique_full_worldspec_digests": len(seen_full),
        "unique_name_independent_worldspec_digests": len(seen_unnamed),
        "ecological_families": {family: family_counts[family]
                               for family in B1.FAMILIES},
        "worlds_stepped": 0,
        "scientific_lives_executed": 0,
        "originals_written": 0,
        "independent_world_sampling_verified": False,
        "target_ecology_superpopulation_verified": False,
        "scientific_margin_approved": False,
        "external_witness_and_owner_admission": False,
        "scientific_verdict": "NOT_ISSUED",
    }


def main():
    print(json.dumps(audit_synthetic_preview(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
