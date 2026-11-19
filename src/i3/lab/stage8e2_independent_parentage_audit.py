"""Stage8-E2 independent genetic parentage verifier, no native births.

Reconstructs every S ranked draw and M permutation, parent v4 digest and
offspring mutation independently of the Stage8-E2 lineage builder. Inputs
are ONLY admissible after original gzip audit of parental lives. This file
never starts a World or declares a scientific conclusion.
"""
from __future__ import annotations

from collections import Counter
import random
import re

from i3.lab import stage8e2_preexposure_schedule as P
from i3.lab import stage8c_parent_multiplicity_control as M
from i3.modules import genome as G

SCHEMA = "i3-stage8e2-independent-parentage-audit/v0"
SOURCE_SCHEMA = "i3-stage8e2-genetic-lineage-preflight/v0"
RECEIPT_KEYS = frozenset((
    "schema", "population", "generation", "arm", "slot",
    "parent_generation_arm", "parent_slot", "mutation_seed",
    "parent_genome_sha256", "offspring_genome_sha256",
    "prior_generation_manifest_sha256", "selection_provenance_unverified",
))
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def verify_parentage(root: str, generation: int, parents: dict,
                     parent_scores: dict, descendants: dict,
                     claims: list[dict], parent_manifest_sha256: str) -> dict:
    """Independently replay exactly the score-selected and blind parent draws."""
    P._root(root)
    if (type(generation) is not int or generation not in (1, 2)
            or type(parent_manifest_sha256) is not str
            or not HEX64.fullmatch(parent_manifest_sha256)):
        raise ValueError("foreign parental generation or seal")
    previous = ("shared",) if generation == 1 else ("S", "M")
    expected_parents = {(p, a, slot) for p in range(P.POPULATIONS)
                        for a in previous for slot in range(P.FOUNDERS)}
    expected_children = {(p, a, slot) for p in range(P.POPULATIONS)
                         for a in ("S", "M") for slot in range(P.FOUNDERS)}
    if (type(parents) is not dict or set(parents) != expected_parents
            or type(parent_scores) is not dict or set(parent_scores) != expected_parents
            or type(descendants) is not dict or set(descendants) != expected_children
            or type(claims) is not list or len(claims) != len(expected_children)):
        raise ValueError("incomplete parent/child/fitness coverage")
    for key in expected_parents:
        G.validate(parents[key])
        score = parent_scores[key]
        if (type(score) not in (tuple, list) or len(score) != 2
                or any(type(x) is not int for x in score)
                or not 0 <= score[0] <= 6 or not 6 <= score[1] <= 2400):
            raise ValueError("foreign six-life parental score")
    claims_by_key = {}
    for claim in claims:
        if (type(claim) is not dict or set(claim) != RECEIPT_KEYS
                or claim.get("schema") != SOURCE_SCHEMA
                or claim.get("generation") != generation
                or claim.get("prior_generation_manifest_sha256") != parent_manifest_sha256
                or claim.get("selection_provenance_unverified") is not True):
            raise ValueError("forged genetic receipt")
        key = (claim.get("population"), claim.get("arm"), claim.get("slot"))
        if key not in expected_children or key in claims_by_key:
            raise ValueError("duplicate or unplanned genetic receipt")
        claims_by_key[key] = claim
    if set(claims_by_key) != expected_children:
        raise ValueError("missing genetic receipt")

    mutation_seeds = set()
    tested = 0
    for p in range(P.POPULATIONS):
        source_s = "shared" if generation == 1 else "S"
        source_m = "shared" if generation == 1 else "M"
        slots = list(range(P.FOUNDERS))
        ranking = sorted(slots, key=lambda s: (
            -parent_scores[p, source_s, s][0],
            -parent_scores[p, source_s, s][1], s
        ))
        selected = []
        for slot in slots:
            bits = int(P.derive(root, "selection", p, generation, "S", slot)[:16], 16)
            seed = (5 << 60) + (bits & ((1 << 60) - 1))
            selected.append(random.Random(seed).choices(
                ranking, weights=range(P.FOUNDERS, 0, -1), k=1)[0])
        permutation = M.blinded_permutation(
            population=p, generation=generation,
            key=bytes.fromhex(P.derive(root, "parent-permutation", p, generation)))
        matched = [permutation[slot] for slot in selected]
        if sorted(Counter(selected).values()) != sorted(Counter(matched).values()):
            raise ValueError("unequal S/M parental occupancy")

        for arm, chosen, source_arm in (
                ("S", selected, source_s), ("M", matched, source_m)):
            for slot, parent_slot in enumerate(chosen):
                key = (p, arm, slot)
                row = claims_by_key[key]
                bits = int(P.derive(root, "mutation", p, generation, arm, slot)[:16], 16)
                seed = (6 << 60) + (bits & ((1 << 60) - 1))
                if (row["parent_slot"] != parent_slot
                        or type(row["parent_slot"]) is not int
                        or row["parent_generation_arm"] != source_arm
                        or type(row["mutation_seed"]) is not int
                        or row["mutation_seed"] != seed or seed in mutation_seeds):
                    raise ValueError("parent rank, permutation or mutation seed differs")
                mutation_seeds.add(seed)
                parent = parents[p, source_arm, parent_slot]
                actual = G.validate(descendants[key])
                if (G.digest(parent) != row["parent_genome_sha256"]
                        or G.digest(actual) != row["offspring_genome_sha256"]
                        or G.mutate(parent, seed, scale=0.1) != actual):
                    raise ValueError("offspring genome not derived from sealed parent")
                tested += 1
    if tested != 2 * P.POPULATIONS * P.FOUNDERS:
        raise ValueError("missing mutated descendants")
    return {
        "schema": SCHEMA, "status": "ALL_PARENTAGE_RECONSTRUCTED_NO_SCIENCE",
        "generation": generation, "population_units": P.POPULATIONS,
        "mutations_reconstructed": tested, "matched_occupancy": True,
        "parent_manifest_sha256": parent_manifest_sha256,
        "original_gzip_audited_here": False, "scientific_claim_authorized": False,
    }
