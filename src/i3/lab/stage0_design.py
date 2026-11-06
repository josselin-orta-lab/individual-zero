"""Stage-0 F0 gate design and arithmetic only; never instantiate a life.

A fixed design candidate, NOT preregistration or permission to expose worlds.
P2 metadata is copied as a source-pinned protocol snapshot, not a new generator;
repository integration tests require agreement with the actual P2 partition.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from hashlib import sha256
import json
from math import comb, isfinite

SCHEMA = "i3-stage0-f0-design-v1"
BASELINE = "5ff6e5a78c9804b0a49c7f947479b0dddfd3eb3e"
ECOLOGY_BLOB = "f7e277da48309aef698b327f328e1f786e313ae2"
FAMILIES = ("stable", "depletion", "pulse")
POPULATIONS, CANDIDATES, KEEP, REPEATS, HORIZON = 8, 40, 5, 2, 400
# Frozen P2 snapshot. Never enlarge a cohort to make a proposed study fit.
COHORT_BOUNDS = {
    "development": (2_000, 2_100), "selection": (10_000, 10_400),
    "validation": (30_000, 30_200), "reserve": (1_200_000, 1_200_200),
}
OFFSETS = {"development": 44, "selection": 72, "validation": 120}
KNOWN_ALLOCATED_THROUGH = {"development": 43, "selection": 71, "validation": 119}
WORLDS_PER_POPULATION = len(FAMILIES) * REPEATS


def _integer(value: int, lower: int, upper: int, name: str) -> int:
    if type(value) is not int or not lower <= value < upper:
        raise ValueError(f"invalid {name}")
    return value


def founder_seed(population: int, slot: int) -> int:
    """New candidate pools; no old P3 genome or learned state is loaded."""
    _integer(population, 0, POPULATIONS, "population")
    _integer(slot, 0, CANDIDATES, "candidate slot")
    return 2_000_000 + population * CANDIDATES + slot


def world_rows(cohort: str) -> list[dict]:
    """Return identifiers only. No generator/engine import, even for validation."""
    if cohort not in OFFSETS:
        raise ValueError("only planned development/selection/validation metadata")
    rows = []
    groups = 1 if cohort == "development" else POPULATIONS
    for population in range(groups):
        for f, family in enumerate(FAMILIES):
            for repeat in range(REPEATS):
                index = OFFSETS[cohort] + population * WORLDS_PER_POPULATION + f * REPEATS + repeat
                first, stop = COHORT_BOUNDS[cohort]
                _integer(index, 0, stop - first, "cohort index")
                if index <= KNOWN_ALLOCATED_THROUGH[cohort]:
                    raise ValueError("historical allocation overlap")
                rows.append({
                    "population": None if cohort == "development" else population,
                    "family": family, "repeat": repeat, "cohort": cohort,
                    "index": index, "world_seed": first + index,
                    # Paired across candidates and architecture arms, not inherited.
                    "life_seed": 3_000_000 + tuple(OFFSETS).index(cohort) * 1_000 + index,
                })
    return rows


def _digest(data: dict) -> str:
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def manifest(occupied_world_seeds: Iterable[int] = ()) -> dict:
    """Build a detached plan; reject additional known conflicts, never reserve/run.

The caller must supply any allocations made after BASELINE. This is not a
live allocation service, and a checksum is not execution authorization.
"""
    worlds = {cohort: world_rows(cohort) for cohort in OFFSETS}
    rows = [row for group in worlds.values() for row in group]
    seeds = [row["world_seed"] for row in rows]
    if len(seeds) != len(set(seeds)):
        raise ValueError("duplicate world seed, even across family labels")
    reserved = range(*COHORT_BOUNDS["reserve"])
    if any(seed in reserved for seed in seeds):
        raise ValueError("sealed reserve overlap")
    occupied = set()
    for seed in occupied_world_seeds:
        if type(seed) is not int or seed < 0:
            raise ValueError("invalid occupied world seed")
        occupied.add(seed)
    if occupied.intersection(seeds):
        raise ValueError("allocation already occupied; do not silently shift seeds")
    founders = [[founder_seed(p, slot) for slot in range(CANDIDATES)]
                for p in range(POPULATIONS)]
    if len({seed for pool in founders for seed in pool}) != POPULATIONS * CANDIDATES:
        raise ValueError("founder pools overlap")
    selection_lives = POPULATIONS * CANDIDATES * WORLDS_PER_POPULATION * 2
    validation_lives = POPULATIONS * KEEP * WORLDS_PER_POPULATION * 2
    data = {
        "schema": SCHEMA, "baseline": BASELINE, "p2_ecology_git_blob": ECOLOGY_BLOB,
        "status": "DESIGN_ONLY_NOT_PREREGISTERED", "execution_authorized": False,
        "population_kind": "independent_new_G0_candidate_pools_NOT_evolved_lineages",
        "populations": POPULATIONS, "candidates_per_population": CANDIDATES,
        "selected_per_architecture_population": KEEP, "horizon": HORIZON,
        "architecture_slots": ["reference_NOT_SOURCE_LOCKED", "candidate_NOT_IMPLEMENTED"],
        "founder_seeds": founders, "worlds": worlds,
        "selection_rule": ["censored_count_desc", "lived_steps_desc", "founder_seed_asc"],
        "analysis_unit": "paired_population_and_independently_allocated_ecology_block",
        "generalization_scope": "F0_only_NOT_whole_family_transfer",
        "sign_test_ties": "exclude_zero_differences_report_effective_n",
        "reserve": {"first": 1_200_000, "stop_exclusive": 1_200_200, "policy": "NEVER_OPEN"},
        "planned_selection_lives_two_architectures": selection_lives,
        "planned_validation_lives_two_architectures": validation_lives,
        "maximum_life_steps_excluding_development": (selection_lives + validation_lives) * HORIZON,
        "required_observer": "existing_observer_full_competition_with_on_off_parity",
        "cost_policy": "actual_phase_work_energy_vigilance_and_lived_time_NO_fictitious_parity",
        "unresolved": ["exact_candidate_and_reference_source_locks", "family_R_and_revision_endpoint",
                       "noninferiority_margin_and_power", "multiplicity_and_stopping_rules",
                       "energetic_receipt_adapter", "full_observer_parity_on_candidate",
                       "lineage_random_parent_design", "individuality_1026", "P5d_1054",
                       "prospective_registration_before_any_exposure"],
    }
    data["sha256"] = _digest(data)
    return data


def validate_manifest(data: dict, occupied_world_seeds: Iterable[int] = ()) -> None:
    """Accept exactly this fixed design; reject even rehashed policy changes."""
    expected = manifest(occupied_world_seeds)
    if type(data) is not dict or json.dumps(data, sort_keys=True, allow_nan=False) != json.dumps(
            expected, sort_keys=True, allow_nan=False):
        raise ValueError("not the fixed Stage-0 design candidate")


def rank_candidates(population: int, outcomes: Iterable[Mapping]) -> tuple[int, ...]:
    """Persistence-only selection from COMPLETE selection receipts, never validation.

Input fields: candidate_seed, world_index, terminal ('dead'/'censored'),
steps_lived. Missing/crashed receipts must block selection, not become deaths
or be dropped. This pure arithmetic helper neither reads nor runs an engine.
"""
    _integer(population, 0, POPULATIONS, "population")
    seeds = {founder_seed(population, slot) for slot in range(CANDIDATES)}
    indices = {r["index"] for r in world_rows("selection") if r["population"] == population}
    totals = {seed: [0, 0] for seed in seeds}
    seen = set()
    fields = {"candidate_seed", "world_index", "terminal", "steps_lived"}
    for row in outcomes:
        if not isinstance(row, Mapping) or set(row) != fields:
            raise ValueError("invalid selection receipt fields")
        seed, index, terminal, steps = (row[k] for k in
                                      ("candidate_seed", "world_index", "terminal", "steps_lived"))
        if type(seed) is not int or seed not in seeds or type(index) is not int or index not in indices:
            raise ValueError("foreign candidate or non-selection world")
        _integer(steps, 1, HORIZON + 1, "lived steps")
        if terminal not in ("dead", "censored") or (terminal == "censored" and steps != HORIZON):
            raise ValueError("crashed, unfinished or invalid terminal receipt")
        key = (seed, index)
        if key in seen:
            raise ValueError("duplicate candidate-world receipt")
        seen.add(key)
        totals[seed][0] += terminal == "censored"
        totals[seed][1] += steps
    if len(seen) != CANDIDATES * WORLDS_PER_POPULATION:
        raise ValueError("incomplete selection; no reranking of successful subset")
    return tuple(sorted(seeds, key=lambda seed: (-totals[seed][0], -totals[seed][1], seed))[:KEEP])


def population_sign_test(differences: Mapping[int, float]) -> dict:
    """Two-sided exact sign test on EIGHT block differences, not dependent lives.

The caller supplies one predeclared aggregate per population; this cannot
prove its provenance or independence. Exact zero is a tie; no tuned epsilon.
No non-inferiority, multiplicity adjustment or scientific GO is inferred here.
"""
    if (not isinstance(differences, Mapping) or len(differences) != POPULATIONS or
            any(type(p) is not int for p in differences) or set(differences) != set(range(POPULATIONS))):
        raise ValueError("require exactly eight identified population differences")
    values = list(differences.values())
    if any(type(x) not in (int, float) or not isfinite(x) for x in values):
        raise ValueError("population differences must be finite numbers, not booleans")
    wins, losses = sum(x > 0 for x in values), sum(x < 0 for x in values)
    n = wins + losses
    p = min(1.0, 2 * sum(comb(n, k) for k in range(min(wins, losses) + 1)) / 2**n)
    return {"populations": POPULATIONS, "wins": wins, "losses": losses,
            "ties": POPULATIONS - n, "effective_n": n, "p_two_sided": p,
            "minimum_p_at_effective_n": min(1.0, 2 / 2**n),
            "status": "ARITHMETIC_ONLY_NOT_A_SCIENTIFIC_VERDICT"}


if __name__ == "__main__":
    print(json.dumps(manifest(), sort_keys=True, indent=2))
