"""Offline Stage-6-light genome ancestry audit; no native life or World access.

Recompute reference genome-v4 G0 and mutation bytes from supplied claims.
This is NOT an allocation audit, parent-choice RNG audit, or admission token.
The current preauthorization method must remain deny-all.  Do not import the
native genome/motor here: their implementation is checked separately in tests.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import random
import re

from i3.lab import stage6_light_native_custody_preflight as custody

ARMS = ("selected", "random_parent")
CHANNELS = ("energy", "food", "water", "integrity", "vigilance")
TEMPERAMENT = ("reward_sensitivity", "threat_sensitivity", "exploration",
               "goal_protection", "affiliation")
# Deliberately mirror genome-v4 insertion order, NOT alphabetical order.
GENE_ORDER = (
    *(f"{name}.{channel}" for name in ("theta", "p", "w") for channel in CHANNELS),
    "gamma1", "gamma2", "gamma3", "alpha", "beta_u", "lambda_r",
    "n_base", "h_max", "m_max",
    *(f"temperament.{name}" for name in TEMPERAMENT),
    "belief_rate", "omega",
)
SEED_MAX = 2**63 - 1
HASH = re.compile(r"[0-9a-f]{64}\Z")
FOUND_FIELDS = {"population", "slot", "seed", "genome", "genome_sha256"}
CHILD_FIELDS = {"population", "generation", "arm", "slot", "parent_slot",
                "mutation_seed", "parent_genome_sha256", "genome", "genome_sha256"}
NATIVE_FIELDS = {"population", "generation", "arm", "slot", "genome_sha256"}


def _int(value: object, low: int, high: int) -> bool:
    return type(value) is int and low <= value <= high


def _hash(value: object) -> bool:
    return type(value) is str and HASH.fullmatch(value) is not None


def _digest(genome: dict) -> str:
    # Exact native genome canonicalization is checked against genome.digest in CI.
    return sha256(json.dumps(genome, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("ascii")).hexdigest()


def _make(genes: dict) -> dict:
    if set(GENE_ORDER) != set(custody.GENE_KEYS) or set(GENE_ORDER) != set(custody.BOUNDS):
        raise RuntimeError("genome-v4 snapshot drift; audit must be revised")
    out = {key: round(float(genes[key]), 6) for key in GENE_ORDER}
    horizons = sorted(out[k] for k in ("gamma1", "gamma2", "gamma3"))
    for key, value in zip(("gamma1", "gamma2", "gamma3"), horizons):
        lo, hi = custody.BOUNDS[key]
        out[key] = min(hi, max(lo, value))
    genome = {"schema": "i3-genome-v4", "genes": out}
    custody._check_genome(genome, {"genome_sha256": _digest(genome)})
    return genome


def _generation_zero(seed: int) -> dict:
    rng = random.Random(f"i3-genome-g0:{seed}")
    return _make({key: rng.uniform(*custody.BOUNDS[key]) for key in GENE_ORDER})


def _mutate(parent: dict, seed: int) -> dict:
    custody._check_genome(parent, {"genome_sha256": _digest(parent)})
    rng = random.Random(f"i3-mutation:{_digest(parent)}:{seed}")
    child = {}
    for key in GENE_ORDER:
        lo, hi = custody.BOUNDS[key]
        child[key] = min(hi, max(lo,
                        parent["genes"][key] + rng.gauss(0.0, 0.1 * (hi-lo))))
    return _make(child)


def inspect_claimed_lineage(founders: list[dict], offspring: list[dict],
                            native_genomes: list[dict], *,
                            fixture_populations: tuple[int, ...] | None = None) -> dict:
    """Fail closed on exact G0/G1/G2 genotype ancestry and archive-claim joins.

    Inputs are caller-supplied claims, not authenticated native originals.  A
    partial population subset is allowed ONLY for explicit regression fixtures.
    Nothing here verifies which parent was *sampled* under weighted/uniform RNG,
    whether a seed was prospectively allocated, or when a file was first run.
    """
    custody._assert_inert()  # denial of live cohorts precedes every validation
    populations = tuple(range(16)) if fixture_populations is None else fixture_populations
    if (type(populations) is not tuple or not populations or
            tuple(sorted(set(populations))) != populations or
            not all(_int(p, 0, 15) for p in populations)):
        raise ValueError("invalid population fixture scope")
    total = len(populations)
    if (type(founders) is not list or len(founders) != total*24 or
            type(offspring) is not list or len(offspring) != total*2*2*24 or
            type(native_genomes) is not list or len(native_genomes) != total*5*24):
        raise ValueError("incomplete G0/G1/G2 genome lineage scope")
    rows = {}
    founder_seeds = set()
    for row in founders:
        if (type(row) is not dict or set(row) != FOUND_FIELDS or
                not _int(row["population"], 0, 15) or row["population"] not in populations or
                not _int(row["slot"], 0, 23) or
                not _int(row["seed"], 0, SEED_MAX) or not _hash(row["genome_sha256"])):
            raise ValueError("invalid founder identity")
        key = (row["population"], 0, "shared", row["slot"])
        if key in rows or row["seed"] in founder_seeds:
            raise ValueError("duplicate founder/seed")
        expected = _generation_zero(row["seed"])
        if row["genome"] != expected or row["genome_sha256"] != _digest(expected):
            raise ValueError("founder does not reproduce native genome-v4 G0")
        rows[key] = expected
        founder_seeds.add(row["seed"])
    mutation_seeds = set()
    generations = defaultdict(list)
    for row in offspring:
        if (type(row) is not dict or set(row) != CHILD_FIELDS or
                not _int(row["population"], 0, 15) or row["population"] not in populations or
                not _int(row["generation"], 1, 2) or
                row["arm"] not in ARMS or not _int(row["slot"], 0, 23) or
                not _int(row["parent_slot"], 0, 23) or
                not _int(row["mutation_seed"], 0, SEED_MAX) or
                not all(_hash(row[k]) for k in ("genome_sha256", "parent_genome_sha256"))):
            raise ValueError("invalid descendant ancestry claim")
        key = (row["population"], row["generation"], row["arm"], row["slot"])
        if key in rows or key in generations[row["generation"]] or row["mutation_seed"] in mutation_seeds:
            raise ValueError("duplicate descendant or mutation stream")
        generations[row["generation"]].append(key)
        mutation_seeds.add(row["mutation_seed"])
    for gen in (1, 2):
        for row in offspring:
            if row["generation"] != gen:
                continue
            parent_key = (row["population"], gen-1,
                          "shared" if gen == 1 else row["arm"], row["parent_slot"])
            if parent_key not in rows:
                raise ValueError("missing or cross-arm ancestral genotype")
            parent = rows[parent_key]
            if row["parent_genome_sha256"] != _digest(parent):
                raise ValueError("parent digest does not match prior-generation genotype")
            child = _mutate(parent, row["mutation_seed"])
            if row["genome"] != child or row["genome_sha256"] != _digest(child):
                raise ValueError("descendant not reproducible from parent and mutation seed")
            rows[(row["population"], gen, row["arm"], row["slot"])] = child
    if len(rows) != total*5*24:
        raise ValueError("missing genotype or duplicated lineage key")
    observed = {}
    for item in native_genomes:
        if (type(item) is not dict or set(item) != NATIVE_FIELDS or
                not _int(item["population"], 0, 15) or item["population"] not in populations or
                not _int(item["generation"], 0, 2) or
                item["arm"] not in (("shared",) if item["generation"] == 0 else ARMS) or
                not _int(item["slot"], 0, 23) or not _hash(item["genome_sha256"])):
            raise ValueError("invalid native-original index claim")
        key = (item["population"], item["generation"], item["arm"], item["slot"])
        if key in observed or key not in rows or item["genome_sha256"] != _digest(rows[key]):
            raise ValueError("missing, duplicated or different original genotype digest")
        observed[key] = item["genome_sha256"]
    if set(observed) != set(rows):
        raise ValueError("incomplete original-genotype index")
    return {
        "schema": "i3-stage6-genome-lineage-offline-preflight/v1",
        "status": ("GENOME_CHAIN_MATCH_ONLY_NOT_ADMITTED" if total == 16
                   else "PARTIAL_FIXTURE_MATCH_ONLY_NOT_ADMITTED"),
        "founder_genomes_checked": len(founders),
        "offspring_mutations_checked": len(offspring),
        "original_genotype_claims_joined": len(observed),
        "genome_v4_reproduction_checked": True,
        "native_original_bytes_read": False,
        "parent_sampling_law_verified": False,
        "external_seed_allocation_verified": False,
        "independent_source_custody_verified": False,
        "owner_authorization": False,
        "new_worlds_opened": 0,
        "new_lives_created": 0,
        "science_verdict": "NOT_ISSUED",
    }


def run_life(*_args, **_kwargs):
    raise PermissionError("offline genome ancestry audit cannot execute a life")


def authorize_science(*_args, **_kwargs):
    raise PermissionError("genome audit is not a scientific release")
