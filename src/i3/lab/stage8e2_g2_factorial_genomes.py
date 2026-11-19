"""Stage8-E2 G2 four-arm assembly and independent structural re-audit.

Consumes already formed, authenticated S/M G2 native v4 genotypes as inputs.
Does not select parents, generate descendants or create a single life.
"""
from __future__ import annotations

from hashlib import sha256
import json

from i3.lab import stage8e2_preexposure_schedule as P
from i3.lab import stage8e_reciprocal_locus_swap as SWAP
from i3.modules import genome as G

SCHEMA = "i3-stage8e2-four-arm-g2-genotype-assembly/v0"


def assemble_g2(paired: dict) -> dict:
    """Consume exactly 64x24 S/M offspring pairs; create four genome copies."""
    expected = {(p, slot) for p in range(P.POPULATIONS)
                for slot in range(P.FOUNDERS)}
    if type(paired) is not dict or set(paired) != expected:
        raise ValueError("incomplete or duplicated G2 S/M offspring pairs")
    by_arm = {}
    for (pop, slot), value in sorted(paired.items()):
        if type(value) is not dict or set(value) != {"S", "M"}:
            raise ValueError("G2 must have two authenticated parental arms")
        S, M = value["S"], value["M"]
        G.validate(S)
        G.validate(M)
        result = SWAP.reciprocal_gamma_horizon_block_swap(S, M)
        for arm in P.G2_ARMS:
            by_arm[pop, arm, slot] = result[arm]
    if len(by_arm) != 4 * P.POPULATIONS * P.FOUNDERS:
        raise ValueError("missing G2 factorial arm")
    return by_arm


def independent_genotype_audit(paired: dict, by_arm: dict) -> dict:
    """Recheck four-arm identities against native parents without SWAP helper."""
    expected = {(p, arm, s)
                for p in range(P.POPULATIONS)
                for arm in P.G2_ARMS for s in range(P.FOUNDERS)}
    if type(by_arm) is not dict or set(by_arm) != expected:
        raise ValueError("incomplete four-arm coverage")
    if type(paired) is not dict or set(paired) != {
        (p, s) for p in range(P.POPULATIONS) for s in range(P.FOUNDERS)
    }:
        raise ValueError("missing original S/M pairing")
    rows = []
    for p in range(P.POPULATIONS):
        for slot in range(P.FOUNDERS):
            original = paired[p, slot]
            if type(original) is not dict or set(original) != {"S", "M"}:
                raise ValueError("unrecognized S/M source")
            for parent in original.values():
                G.validate(parent)
            for arm in P.G2_ARMS:
                observed = by_arm[p, arm, slot]
                G.validate(observed)
                side = "S" if arm.startswith("S_") else "M"
                other = "M" if side == "S" else "S"
                source = original[side]
                supplier = original[side] if arm.endswith("sham") else original[other]
                if (set(observed) != set(source) or
                        any(observed[k] != source[k] for k in source if k != "genes")):
                    raise ValueError("identity or genome metadata modified")
                for gene in G.GENE_ORDER:
                    expected_value = (supplier if gene in SWAP.GAMMA_HORIZONS
                                      else source)["genes"][gene]
                    if observed["genes"][gene] != expected_value:
                        raise ValueError("unexpected G2 genome mutation or gamma donor")
                rows.append([p, arm, slot, G.digest(observed)])
    raw = json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return {
        "schema": SCHEMA, "state": "STRUCTURAL_ONLY_NO_SCIENCE",
        "g2_genome_copies": len(rows),
        "g2_planned_lives": len(rows) * 6,
        "four_arm_genome_sha256": sha256(raw).hexdigest(),
        "native_lives_created": 0, "original_gzip_audited": False,
        "scientific_claim_authorized": False,
    }
