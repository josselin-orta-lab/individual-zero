"""Stage8-E2 two-generation native-v4 ancestry builder: pure engineering only.

Inputs MUST come from independently sealed G0/G1 original lives in a future
transport. Synthetic tests exercise contracts but never authenticate evidence.
No World, native birth, motor command or survival score is simulated here.
"""
from __future__ import annotations

from collections import Counter
import random
import re

from i3.lab import stage8e2_preexposure_schedule as P
from i3.lab import stage8c_parent_multiplicity_control as M
from i3.modules import genome as G

SCHEMA = "i3-stage8e2-genetic-lineage-preflight/v0"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def _seed(root: str, domain: str, p: int, generation: int,
          arm: str, slot: int) -> int:
    # Match the reserved numeric mutation namespace in native Stage6/8-C.
    base = (6 if domain == "mutation" else 5) << 60
    return base + (int(P.derive(root, domain, p, generation, arm, slot)[:16], 16)
                   & ((1 << 60) - 1))


def make_descendants(root: str, generation: int, parent_genomes: dict,
                     sealed_scores: dict, prior_manifest_sha256: str) -> tuple[dict, list]:
    """Selected rank and score-blind multiplicity matched control, 64x24.

    The score tuples must be derived from *six paid native lives* per parent.
    This pure function cannot establish that provenance, which a future
    original-level auditor MUST verify before results are admitted.
    """
    P._root(root)
    if generation not in (1, 2) or type(generation) is not int:
        raise ValueError("expected G1 or G2")
    if type(prior_manifest_sha256) is not str or not HEX64.fullmatch(prior_manifest_sha256):
        raise ValueError("unauthenticated parent-generation manifest")
    previous = ("shared",) if generation == 1 else ("S", "M")
    keys = {(p, arm, s) for p in range(P.POPULATIONS)
            for arm in previous for s in range(P.FOUNDERS)}
    if (type(parent_genomes) is not dict or set(parent_genomes) != keys
            or type(sealed_scores) is not dict or set(sealed_scores) != keys):
        raise ValueError("parent genomes and sealed fitness identities must match")
    for key in keys:
        G.validate(parent_genomes[key])
        score = sealed_scores[key]
        if (type(score) not in (tuple, list) or len(score) != 2
                or type(score[0]) is not int or type(score[1]) is not int
                or not 0 <= score[0] <= 6 or not 6 <= score[1] <= 2400):
            raise ValueError("invalid six-life sealed parent fitness")
    children, receipts = {}, []
    for p in range(P.POPULATIONS):
        prior_s = "shared" if generation == 1 else "S"
        prior_m = "shared" if generation == 1 else "M"
        rank = sorted(range(P.FOUNDERS),
                      key=lambda s: (-sealed_scores[p, prior_s, s][0],
                                     -sealed_scores[p, prior_s, s][1], s))
        selected = [
            random.Random(_seed(root, "selection", p, generation, "S", slot)).choices(
                rank, weights=range(P.FOUNDERS, 0, -1), k=1)[0]
            for slot in range(P.FOUNDERS)
        ]
        perm_key = bytes.fromhex(P.derive(root, "parent-permutation", p, generation))
        matched = M.matched_parent_draws(selected, population=p,
                                         generation=generation, key=perm_key)
        if sorted(Counter(selected).values()) != sorted(Counter(matched).values()):
            raise ValueError("parental multiplicity not preserved")
        for arm, parents, old_arm in (("S", selected, prior_s),
                                       ("M", matched, prior_m)):
            for slot, parent_slot in enumerate(parents):
                parent = parent_genomes[p, old_arm, parent_slot]
                mutation_seed = _seed(root, "mutation", p, generation, arm, slot)
                child = G.validate(G.mutate(parent, mutation_seed, scale=0.1))
                children[p, arm, slot] = child
                receipts.append({
                    "schema": SCHEMA, "population": p, "generation": generation,
                    "arm": arm, "slot": slot,
                    "parent_generation_arm": old_arm, "parent_slot": parent_slot,
                    "mutation_seed": mutation_seed,
                    "parent_genome_sha256": G.digest(parent),
                    "offspring_genome_sha256": G.digest(child),
                    "prior_generation_manifest_sha256": prior_manifest_sha256,
                    "selection_provenance_unverified": True,
                })
    if len(children) != P.POPULATIONS * 2 * P.FOUNDERS:
        raise ValueError("incomplete genotype lineage")
    return children, receipts


def audit_lineage_structure(root: str, generation: int, parent_genomes: dict,
                            offspring: dict, receipts: list) -> dict:
    """Reconstruct mutations from parents and expected seeds, no life archive."""
    P._root(root)
    expected = {(p, arm, s) for p in range(P.POPULATIONS)
                for arm in ("S", "M") for s in range(P.FOUNDERS)}
    if (type(offspring) is not dict or set(offspring) != expected
            or type(receipts) is not list or len(receipts) != len(expected)):
        raise ValueError("missing descendant genotype or receipt")
    seen, selections = set(), {}
    for r in receipts:
        if type(r) is not dict or r.get("schema") != SCHEMA:
            raise ValueError("foreign ancestry receipt")
        key = (r.get("population"), r.get("arm"), r.get("slot"))
        if key not in expected or key in seen or r.get("generation") != generation:
            raise ValueError("duplicate or foreign genotype receipt")
        seen.add(key)
        p, arm, slot = key
        old_arm = "shared" if generation == 1 else arm
        parent_slot = r.get("parent_slot")
        if (type(parent_slot) is not int or not 0 <= parent_slot < P.FOUNDERS
                or r.get("parent_generation_arm") != old_arm
                or r.get("mutation_seed") != _seed(root, "mutation", p, generation, arm, slot)
                or r.get("selection_provenance_unverified") is not True):
            raise ValueError("source-identity or mutation seed drift")
        parent = G.validate(parent_genomes[p, old_arm, parent_slot])
        child = G.validate(offspring[key])
        if (r.get("parent_genome_sha256") != G.digest(parent)
                or r.get("offspring_genome_sha256") != G.digest(child)
                or G.mutate(parent, r["mutation_seed"], scale=0.1) != child):
            raise ValueError("offspring does not reconstruct from native mutation")
        selections.setdefault((p, arm), []).append(parent_slot)
    for p in range(P.POPULATIONS):
        s, m = selections[p, "S"], selections[p, "M"]
        if sorted(Counter(s).values()) != sorted(Counter(m).values()):
            raise ValueError("S/M parent occupancy mismatch")
        permutation = M.blinded_permutation(
            population=p, generation=generation,
            key=bytes.fromhex(P.derive(root, "parent-permutation", p, generation)))
        # Receipts follow source construction slot order, but enforce by explicit indices.
        by_slot = {(r["population"], r["arm"], r["slot"]): r["parent_slot"]
                   for r in receipts}
        if any(by_slot[p, "M", slot] != permutation[by_slot[p, "S", slot]]
               for slot in range(P.FOUNDERS)):
            raise ValueError("control not a precommitted permutation")
    return {"schema": SCHEMA, "generation": generation,
            "genomes_reconstructed": len(seen),
            "population_units": P.POPULATIONS,
            "parental_occupancy_matched": True,
            "original_gzip_audited": False, "scientific_claim_authorized": False}
