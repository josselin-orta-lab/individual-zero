"""Stage8-E2 physical WorldSpec and per-life identity preflight, no birth.

This validates the SAME F0 physics factory used by native Stage8-C, without
running a life. It is a design preflight, not a scientific admission or audit
of original gzip. Future transport must consume these commitments unchanged.
"""
from __future__ import annotations

from hashlib import sha256
import json

from i3.lab import p2_ecologies as F0
from i3.lab import stage6_light_prospective_ecologies as NATIVE
from i3.lab import stage8e2_preexposure_schedule as P

SCHEMA = "i3-stage8e2-native-worldspec-and-identity-preflight/v0"
MASK = (1 << 60) - 1
BASE = {"world": 2 << 60, "life": 3 << 60, "founder": 4 << 60,
        "mutation": 6 << 60, "parent": 7 << 60}


def _seed(root: str, domain: str, prefix: str, *coords: object) -> int:
    return BASE[prefix] + (int(P.derive(root, domain, *coords)[:16], 16) & MASK)


def _world_row(root: str, p: int, g: int, family: str, repeat: int) -> dict:
    domain = "world-g" + str(g)
    seed = _seed(root, domain, "world", p, family, repeat)
    spec = NATIVE.world_for_stage6(family, seed)
    return {
        "population": p, "generation": g,
        "family": family, "repeat": repeat,
        "world_seed": seed, "world_sha256": F0.fingerprint(spec),
    }


def _identities(root: str):
    """Stream every planned life key; no genome or biology instantiated."""
    for p in range(P.POPULATIONS):
        for g in range(3):
            arms = ("shared",) if g == 0 else (
                P.G1_ARMS if g == 1 else P.G2_ARMS)
            for arm in arms:
                for slot in range(P.FOUNDERS):
                    for family in P.WORLD_FAMILIES:
                        for repeat in range(P.WORLD_REPEATS):
                            key = (p, g, arm, slot, family, repeat)
                            yield key, _seed(root, "identity", "life", *key), (
                                P.derive(root, "motor", *key))


def verify_native_preflight(root: str, *, expected: dict | None = None) -> dict:
    """Fully enumerate native WorldSpecs and birth identifiers, fail closed.

    Only WorldSpec construction and hashing take place. Zero actions, minds,
    lives, mutations, filiation, archive writes or trial allocation.
    """
    P._root(root)
    base = P.schedule(root)
    worlds = [_world_row(root, p, g, fam, rep)
              for p in range(P.POPULATIONS) for g in range(3)
              for fam in P.WORLD_FAMILIES for rep in range(P.WORLD_REPEATS)]
    if len(worlds) != 1152:
        raise ValueError("incomplete G0/G1/G2 F0 WorldSpecs")
    seen_seeds, seen_worlds = set(), set()
    for row in worlds:
        key = (row["population"], row["generation"], row["family"], row["repeat"])
        if key in seen_worlds or row["world_seed"] in seen_seeds:
            raise ValueError("duplicate native World opportunity or seed")
        seen_worlds.add(key)
        seen_seeds.add(row["world_seed"])
    world_sha = sha256(json.dumps(worlds, sort_keys=True,
                      separators=(",", ":")).encode("ascii")).hexdigest()
    expected_keys = P.EXPECTED_TOTAL
    life_count, identities, rngs = 0, set(), set()
    for key, life_seed, motor_stream in _identities(root):
        if key in identities or life_seed in seen_seeds or life_seed in rngs:
            raise ValueError("duplicated or overlapping life identity")
        if motor_stream in rngs:
            raise ValueError("reused individual motor stream")
        identities.add(key)
        rngs.add(life_seed)
        rngs.add(motor_stream)
        life_count += 1
    if life_count != expected_keys or len(identities) != expected_keys:
        raise ValueError("incomplete unique native life identities")
    # The G2 physical opportunity is unchanged across all four arms.
    g2 = [r for r in worlds if r["generation"] == 2]
    if len(g2) != 384:
        raise ValueError("G2 physical opportunity mismatch")
    payload = {
        "schema": SCHEMA, "status": "NATIVE_WORLDSPEC_PREFLIGHT_ONLY",
        "root_commitment_sha256": base["root_commitment_sha256"],
        "world_f0_factory": "stage6_light_prospective_ecologies.world_for_stage6",
        "physical_worlds_by_generation": {"G0": 384, "G1": 384, "G2": 384},
        "g2_worldspecs": g2, "all_worldspecs_sha256": world_sha,
        "all_worldspec_count": len(worlds),
        "unique_birth_identifiers": life_count,
        "planned_lives": base["planned_lives"],
        "horizon": P.HORIZON,
        "native_lives_created": 0, "science_admitted": False,
        "missing": ["GENOMES_AND_PARENTAGE", "PHASE_RECEIPTS",
                    "NATIVE_TRANSPORT", "ORIGINAL_GZIP_INDEPENDENT_AUDIT",
                    "EXACT_SOURCE_SCIENCE_GATE"],
    }
    payload["manifest_sha256"] = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    if expected is not None and (type(expected) is not dict or expected != payload):
        raise ValueError("native source, F0 physics, allocations or identities drifted")
    return payload
