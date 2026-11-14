"""Offline Stage6 mock parent-choice / genome-chain join, no World or life.

Claims are invented or caller supplied. This cannot authenticate a sealed G/S
receipt, retroactively preregister a draw seed, or authorize a new cohort.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import random

from i3.lab import stage6_light_genome_lineage_preflight as ancestry

KIND = "TOY_NO_WORLD"
FAMILIES = ("stable", "depletion", "pulse")
ARMS = ("selected", "random_parent")
PERSISTENCE_FIELDS = frozenset(("kind", "population", "generation", "arm", "slot", "family", "repeat", "censored", "steps_lived"))
DRAW_FIELDS = frozenset(("kind", "population", "generation", "arm", "slot", "parent_slot", "draw_seed", "parent_genome_sha256", "genome_sha256"))


def _int(x: object, lo: int, hi: int) -> bool:
    return type(x) is int and lo <= x <= hi


def _sha(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("ascii")).hexdigest()


def inspect_mock_parent_selection(founders: list[dict], offspring: list[dict],
                                  native_genomes: list[dict],
                                  persistence: list[dict], draws: list[dict], *,
                                  fixture_populations: tuple[int, ...] | None = None) -> dict:
    """Reconcile all G0/G1 selections with mutation and native-index claims.

    Does NOT attest the independently fixed origin of persistence, draw seeds,
    source timestamps or genome-index records. Only mock claims are accepted.
    """
    ancestry.custody._assert_inert()  # deny early, before data inspection
    pops = tuple(range(16)) if fixture_populations is None else fixture_populations
    if (type(pops) is not tuple or not pops or tuple(sorted(set(pops))) != pops or
            not all(_int(p, 0, 15) for p in pops)):
        raise ValueError("invalid fixture populations")
    n = len(pops)
    if (type(persistence) is not list or len(persistence) != n * (24*6 + 2*24*6) or
            type(draws) is not list or len(draws) != n*2*2*24):
        raise ValueError("incomplete G0/G1 persistence or parent draw claims")
    # Verify exact G0/G1/G2 genotype-v4 ancestry and claimed original index.
    genotype = ancestry.inspect_claimed_lineage(
        founders, offspring, native_genomes, fixture_populations=fixture_populations)
    parents = {}
    for row in native_genomes:
        parents[(row["population"], row["generation"], row["arm"], row["slot"])] = row["genome_sha256"]
    child_index = {
        (row["population"], row["generation"], row["arm"], row["slot"]): row
        for row in offspring
    }
    # Every mock persistence unit must have exactly six matching opportunities.
    receipt_by_person = defaultdict(dict)
    for row in persistence:
        if (type(row) is not dict or set(row) != PERSISTENCE_FIELDS or
                row["kind"] != KIND or not _int(row["population"], 0, 15) or
                row["population"] not in pops or
                not _int(row["generation"], 0, 1) or
                row["arm"] not in (("shared",) if row["generation"] == 0 else ARMS) or
                not _int(row["slot"], 0, 23) or row["family"] not in FAMILIES or
                not _int(row["repeat"], 0, 1) or
                type(row["censored"]) is not bool or
                not _int(row["steps_lived"], 1, 400) or
                (row["censored"] and row["steps_lived"] != 400)):
            raise ValueError("invalid toy persistence claim")
        key = row["population"], row["generation"], row["arm"], row["slot"]
        opp = row["family"], row["repeat"]
        if opp in receipt_by_person[key]:
            raise ValueError("duplicated persistence opportunity")
        receipt_by_person[key][opp] = (row["censored"], row["steps_lived"])
    expected_people = {
        (p, g, arm, slot)
        for p in pops for g in (0, 1)
        for arm in (("shared",) if g == 0 else ARMS)
        for slot in range(24)
    }
    if (set(receipt_by_person) != expected_people or
            any(set(o) != {(f, r) for f in FAMILIES for r in (0, 1)}
                for o in receipt_by_person.values())):
        raise ValueError("missing native-shaped persistence opportunities")
    # Source for selection of each arm is only its own G1 parent population.
    expected_draws = {
        (p, g, arm, s) for p in pops for g in (1, 2)
        for arm in ARMS for s in range(24)
    }
    seen = set()
    draw_seeds = set()
    for receipt in draws:
        if (type(receipt) is not dict or set(receipt) != DRAW_FIELDS or
                receipt["kind"] != KIND or not _int(receipt["population"], 0, 15) or
                receipt["population"] not in pops or
                not _int(receipt["generation"], 1, 2) or
                receipt["arm"] not in ARMS or
                not _int(receipt["slot"], 0, 23) or
                not _int(receipt["parent_slot"], 0, 23) or
                not _int(receipt["draw_seed"], 0, 2**63-1) or
                not all(ancestry._hash(receipt[k]) for k in
                        ("parent_genome_sha256", "genome_sha256"))):
            raise ValueError("invalid mock parent draw claim")
        p, g, arm, s = (receipt[k] for k in ("population", "generation", "arm", "slot"))
        key = (p, g, arm, s)
        if key not in expected_draws or key in seen or receipt["draw_seed"] in draw_seeds:
            raise ValueError("repeated or foreign mock parent draw")
        seen.add(key)
        draw_seeds.add(receipt["draw_seed"])
        prev_arm = "shared" if g == 1 else arm
        previous = [receipt_by_person[(p, g-1, prev_arm, idx)] for idx in range(24)]
        # Precompute sorted scores only for the selected arm. Uniform control
        # uses no fitness ranking or score in its selection branch.
        rng = random.Random(receipt["draw_seed"])
        if arm == "selected":
            ranked = sorted(range(24), key=lambda slot: (
                -sum(v[0] for v in previous[slot].values()),
                -sum(v[1] for v in previous[slot].values()), slot))
            chosen = rng.choices(ranked, weights=range(24, 0, -1), k=1)[0]
        else:
            chosen = rng.randrange(24)
        if receipt["parent_slot"] != chosen:
            raise ValueError("mock draw differs from declared parent selection rule")
        parent_key = (p, g-1, prev_arm, chosen)
        actual_child = child_index.get(key)
        if (actual_child is None or actual_child["parent_slot"] != chosen or
                receipt["parent_genome_sha256"] != parents[parent_key] or
                actual_child["parent_genome_sha256"] != parents[parent_key] or
                receipt["genome_sha256"] != parents[key] or
                actual_child["genome_sha256"] != parents[key]):
            raise ValueError("draw does not join exact parent and descendant genomes")
    if seen != expected_draws:
        raise ValueError("incomplete parent draw coverage")
    return {
        "schema": "i3-stage6-parent-selection-lineage-preflight/v1",
        "status": ("TOY_PARENT_SELECTION_LINEAGE_MATCH_NOT_ADMITTED" if n == 16
                   else "PARTIAL_TOY_PARENT_SELECTION_LINEAGE_MATCH_NOT_ADMITTED"),
        "checked_persistence_receipts": len(persistence),
        "checked_draws": len(draws),
        "checked_mutations": genotype["offspring_mutations_checked"],
        "source_authenticity_verified": False,
        "parent_draw_seeds_independently_committed": False,
        "original_biological_lives_verified": False,
        "parent_selection_statistically_identified": False,
        "owner_authorization": False,
        "new_worlds_opened": 0,
        "new_lives_created": 0,
        "science_verdict": "NOT_ISSUED",
        "input_scope": KIND,
        "claim_digest_sha256": _sha({"persistence": persistence, "draws": draws}),
    }


def run_life(*_args, **_kwargs):
    raise PermissionError("offline parent selection preflight cannot execute a life")


def authorize_science(*_args, **_kwargs):
    raise PermissionError("mock selection evidence is never an admission ticket")
