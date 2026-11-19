"""Stage8-E2 *pure* preexposure schedule prototype.

This creates no World, offspring, life or native seed allocation. Its only
purpose is to make a candidate allocation explicit and mechanically checkable.
Do not mistake this for a scientific preregistration or an execution gate.
"""
from __future__ import annotations

import hashlib
import hmac
import json

SCHEMA = "i3-stage8e2-pure-preexposure-schedule/v0"
POPULATIONS = 64
FOUNDERS = 24
WORLD_FAMILIES = ("stable", "depletion", "pulse")
WORLD_REPEATS = 2
G2_ARMS = ("S_sham", "M_sham", "S_swap", "M_swap")
G1_ARMS = ("S", "M")
HORIZON = 400
EXPECTED_G0 = 9_216
EXPECTED_G1 = 18_432
EXPECTED_G2 = 36_864
EXPECTED_TOTAL = 64_512


def _root(root_hex: str) -> bytes:
    if type(root_hex) is not str or len(root_hex) != 64:
        raise ValueError("one new 32-byte root required (lowercase hex)")
    try:
        root = bytes.fromhex(root_hex)
    except ValueError as exc:
        raise ValueError("invalid root encoding") from exc
    if root.hex() != root_hex or root == bytes(32):
        raise ValueError("root must be canonical nonzero lowercase hex")
    return root


def derive(root_hex: str, domain: str, *indices: object) -> str:
    """Separate deterministic HMAC namespace for each kind of future entropy."""
    root = _root(root_hex)
    if type(domain) is not str or domain not in (
        "world-g0", "world-g1", "world-g2", "identity", "motor",
        "mutation", "selection", "parent-permutation"
    ):
        raise ValueError("unregistered randomness domain")
    if any(type(i) not in (str, int) or type(i) is int and i < 0
           or type(i) is str and (not i or "/" in i) for i in indices):
        raise ValueError("invalid allocation coordinate")
    payload = json.dumps([SCHEMA, domain, *indices], separators=(",", ":"),
                         ensure_ascii=True).encode("ascii")
    return hmac.new(root, payload, hashlib.sha256).hexdigest()


def schedule(root_hex: str) -> dict:
    """Public candidate World commitments, without seeing a biological result.

    Different arms get the exact same physical World token for an opportunity,
    while their identity and motor randomness must be separately derived.
    A real WorldSpec generator must later bind each World token to physical
    parameters and rehash them before science can be authorized.
    """
    _root(root_hex)
    worlds = []
    for p in range(POPULATIONS):
        for family in WORLD_FAMILIES:
            for repeat in range(WORLD_REPEATS):
                worlds.append({
                    "population": p, "family": family, "repeat": repeat,
                    "world_token": derive(root_hex, "world-g2", p, family, repeat)
                })
    if len(worlds) != POPULATIONS * len(WORLD_FAMILIES) * WORLD_REPEATS:
        raise AssertionError("missing G2 opportunity")
    if len({w["world_token"] for w in worlds}) != len(worlds):
        raise AssertionError("G2 World token collision")
    counts = {
        "G0": POPULATIONS * FOUNDERS * 6,
        "G1": POPULATIONS * FOUNDERS * 6 * len(G1_ARMS),
        "G2": POPULATIONS * FOUNDERS * 6 * len(G2_ARMS),
    }
    if (counts["G0"], counts["G1"], counts["G2"]) != (
            EXPECTED_G0, EXPECTED_G1, EXPECTED_G2):
        raise AssertionError("wrong declared birth budget")
    return {
        "schema": SCHEMA, "status": "PURE_PROTOTYPE_NO_ADMISSION",
        "root_commitment_sha256": hashlib.sha256(bytes.fromhex(root_hex)).hexdigest(),
        "g2_world_opportunities": worlds, "worlds_reserved_count": len(worlds),
        "arms_g1": list(G1_ARMS), "arms_g2": list(G2_ARMS),
        "populations": POPULATIONS, "founders_per_population": FOUNDERS,
        "worlds_per_genome": 6, "horizon": HORIZON,
        "planned_lives": counts, "total_planned_lives": sum(counts.values()),
        "new_lives": 0, "worlds_instantiated": 0,
        "scientific_claim_authorized": False,
        "limits": [
            "NO_WORLD_SPEC_BOUND", "NO_NATIVE_LIFE_SEEDS_ALLOCATED",
            "NO_PARENTAGE_OR_MUTATIONS", "NO_TECHNICAL_RECEIPTS",
            "NO_SCIENTIFIC_GATE", "NO_BIRTHS"
        ],
    }


def check_three_roots(technical_py311: str, technical_py312: str,
                      prospective_science: str) -> bool:
    """Reject reuse between the planned two technical and scientific runs."""
    roots = [_root(x) for x in (
        technical_py311, technical_py312, prospective_science)]
    if len(set(roots)) != 3:
        raise ValueError("three different allocation roots are mandatory")
    return True
