"""B1 prospective matched-unit allocation *preview*, no World construction.

This module makes a deterministic, replayable proposed sample *schedule*.
It does not mint source authority, attest independent ecological draws,
invoke a World generator, instantiate a genome or run any scientific life.
The seed witness used in preview is deliberately synthetic and PUBLIC.
Independent, iid *pairs* remain a prospective statistical assumption,
not a consequence of hashing 1,500 different integers.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import hmac
import json
import re

from . import stage0_design as F0

SCHEMA = "i3-stage2-1-b1-prospective-pair-metadata/v1"
STATUS = "DRY_RUN_ALLOCATION_ONLY_NO_WORLD_EXPOSURE"
FAMILIES = F0.FAMILIES
POLICIES = ("reference", "p13_replay_gate_v1")
HORIZON = 400
# This is a computational *capacity scenario*, not the approved sample size.
PREVIEW_PAIRS = 1_500
PREVIEW_WITNESS = sha256(b"B1 PUBLIC SYNTHETIC METADATA PREVIEW NOT A STUDY SEED").hexdigest()
# Domain-separated, disjoint from P2, engineering and historical G2/G2e.
# The offsets are masked to 60 bits and must stay below the next prefix.
SEED_BITS = 60
OFFSET_MASK = (1 << SEED_BITS) - 1
WORLD_BASE = (1 << SEED_BITS)
GENOME_BASE = (2 << SEED_BITS)
LIFE_BASE = (3 << SEED_BITS)
MAX_PREVIEW_PAIRS = 10_000

OLD_SEED_RANGES = (
    (100, 130), (1_000_200, 1_000_300),  # historical G2/G2e
    (90_000, 91_000),  # ADR-0017 engineering
    *tuple(F0.COHORT_BOUNDS.values()),  # P2 DEVELOPMENT, SELECTION, VALIDATION, RESERVE
)


def _digest(obj) -> str:
    return sha256(json.dumps(
        obj, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _key(witness_hex: str) -> bytes:
    if (type(witness_hex) is not str or
            re.fullmatch(r"[0-9a-f]{64}", witness_hex) is None):
        raise ValueError("witness must be exactly 64 lowercase hexadecimal digits")
    if len(set(witness_hex)) == 1:
        raise ValueError("trivial witness is not accepted even for simulation")
    return bytes.fromhex(witness_hex)


def _hmac_digest(key: bytes, unit: int, domain: str, attempt=0) -> bytes:
    payload = f"i3-b1-alloc-v1|{unit}|{domain}|{attempt}".encode("ascii")
    return hmac.new(key, payload, digestmod=sha256).digest()


def _family(key: bytes, unit: int) -> str:
    # Rejection avoids modulo-3 bias. No arbitrary family balancing or
    # post-observation reshuffle may be used to massage finite counts.
    for attempt in range(1_000):
        value = _hmac_digest(key, unit, "family", attempt)[0]
        if value < 255:
            return FAMILIES[value % 3]
    raise RuntimeError("unexpected family sampling rejection exhaustion")


def _seed(key: bytes, unit: int, domain: str, base: int) -> int:
    value = int.from_bytes(_hmac_digest(key, unit, domain)[:8], "big") & OFFSET_MASK
    return base + value


def _check_separation(rows) -> None:
    for name, base in (("world_seed", WORLD_BASE),
                       ("genome_seed", GENOME_BASE),
                       ("life_seed", LIFE_BASE)):
        values = [r[name] for r in rows]
        if len(values) != len(set(values)):
            raise ValueError(f"duplicate {name}: no convenient resampling")
        if any(type(s) is not int or not base <= s < base + (1 << SEED_BITS)
               for s in values):
            raise ValueError(f"{name} outside its disjoint namespace")
        if any(lo <= s < hi for s in values for lo, hi in OLD_SEED_RANGES):
            raise ValueError(f"{name} overlaps a declared historical allocation")
    if len({r["world_seed"] for r in rows} |
           {r["genome_seed"] for r in rows} |
           {r["life_seed"] for r in rows}) != 3 * len(rows):
        raise ValueError("cross-domain seed overlap")


def preview(witness_hex: str, *, pairs: int = PREVIEW_PAIRS) -> dict:
    """Generate only identifiers, a synthetic preview, never real WorldSpecs.

    Newborn genotype and each generated World are proposed to be independently
    sampled for each unit, rather than recycling the 48 F0 known slots.
    Independence is NOT proven by unique PRF seeds; external witness,
    RNG assumptions, ecology correlation and WorldSpec collisions still
    require prospective review before scientific execution.
    """
    key = _key(witness_hex)
    if type(pairs) is not int or not 1 <= pairs <= MAX_PREVIEW_PAIRS:
        raise ValueError("paired-unit preview size outside bounded capacity")
    rows = [
        {
            "pair_id": f"b1-{i:06d}",
            "ordinal": i,
            "family": _family(key, i),
            "world_seed": _seed(key, i, "world", WORLD_BASE),
            "genome_seed": _seed(key, i, "genome", GENOME_BASE),
            "life_seed": _seed(key, i, "life", LIFE_BASE),
        }
        for i in range(pairs)
    ]
    _check_separation(rows)
    distribution = Counter(r["family"] for r in rows)
    manifest = {
        "schema": SCHEMA,
        "status": STATUS,
        "witness_sha256": sha256(key).hexdigest(),
        "witness_is_external_signed_source": False,
        "witness_is_authorized_for_scientific_births": False,
        "worldspec_generation_permitted": False,
        "individual_lives_executed": 0,
        "world_instances_created": 0,
        "pair_count": pairs,
        "policies_per_pair": list(POLICIES),
        "maximum_proposed_lives": pairs * len(POLICIES),
        "maximum_horizon_steps": pairs * len(POLICIES) * HORIZON,
        "source_scope": "KNOWN_F0_THREE_FAMILIES_ONLY",
        "family_rule": "HMAC_SHA256_BYTE_REJECTION_THEN_MOD3_NO_FORCED_BALANCING",
        "family_counts": {family: distribution[family] for family in FAMILIES},
        "generator_call_required_later":
            "WORLDGEN_EXPLICIT_development_false_WITH_P2_F0_FAMILY_SEMANTICS_NOT_RUN",
        "independent_iid_world_pairs_verified": False,
        "world_spec_digest_collisions_checked": False,
        "scientific_allocation_claimed": False,
        "scientific_verdict": "NOT_ISSUED",
        "proposed_units": rows,
    }
    manifest["allocation_sha256"] = _digest(manifest)
    return manifest


def verify_preview(manifest, witness_hex: str, *, pairs: int = PREVIEW_PAIRS) -> None:
    """Fail closed on amended counts, rerolled families, changed seeds or plan."""
    expected = preview(witness_hex, pairs=pairs)
    if type(manifest) is not dict or _digest(manifest) != _digest(expected):
        raise ValueError("B1 prospective preview differs from witnessed schedule")
    if manifest != expected:
        raise ValueError("B1 prospective preview unequal to witnessed schedule")


def structural_summary(manifest) -> dict:
    """Only dry-run metadata for GitHub logs; no actual lives or WorldSpecs."""
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ValueError("invalid preview")
    return {k: manifest[k] for k in (
        "schema", "status", "witness_sha256", "pair_count",
        "family_counts", "maximum_proposed_lives", "maximum_horizon_steps",
        "allocation_sha256", "world_instances_created",
        "individual_lives_executed", "scientific_verdict",
        "independent_iid_world_pairs_verified",
        "witness_is_authorized_for_scientific_births",
    )}


def main() -> None:
    # The CLI intentionally has no option to feed a real research-owner
    # witness and no command that can enter a World. It is *only* a
    # reproducible engineering demonstration of a proposed sampling plan.
    print(json.dumps(structural_summary(preview(PREVIEW_WITNESS)),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
