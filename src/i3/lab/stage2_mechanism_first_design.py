"""Mechanism-first Stage-2.1 paired G0 design: purely prospective arithmetic.

Unopened F0 identifiers and deterministically specified newborn genomes, NOT
selected founders or learned-state transplants. This is an ALTERNATIVE design,
not a revision of executed protocols, a World runner or scientific approval.
"""
from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import json
from math import fsum, isfinite

from . import stage0_design as F0

SCHEMA = "i3-stage2-1-mechanism-first-paired-g0-v1"
STATUS = "PROPOSED_SOFTWARE_ONLY_NOT_PREREGISTERED_NO_WORLD"
ARMS = ("FIXED_G0", "GATE_G0", "RANDOM_G0")
FIELDS = frozenset((
    "arm", "population", "family", "world_index", "world_seed",
    "genome_seed", "life_seed", "terminal", "steps_lived",
    "energy_paid", "vigilance_paid", "inactive_steps",
))
CONTRASTS = (
    ("GATE_minus_FIXED", "GATE_G0", "FIXED_G0"),
    ("GATE_minus_RANDOM", "GATE_G0", "RANDOM_G0"),
)


def fixed_founders(population: int) -> tuple[int, ...]:
    """Birth-seed-only G0, first five; never rank on any exposed life."""
    if type(population) is not int or not 0 <= population < F0.POPULATIONS:
        raise ValueError("unknown genetic population")
    return tuple(F0.founder_seed(population, i) for i in range(F0.KEEP))


def expected_cells(occupied_world_seeds=()) -> dict:
    """48 unopened F0 validation metadata slots x 5 G0 seeds x 3 arms."""
    F0.manifest(occupied_world_seeds)  # Proposal-only collision sanity, not live registry.
    cells = {}
    for world in F0.world_rows("validation"):
        p = world["population"]
        for seed in fixed_founders(p):
            for arm in ARMS:
                key = (p, world["index"], seed, arm)
                cells[key] = world
    if len(cells) != 720:
        raise ValueError("bad proposed paired panel")
    return cells


def proposal(occupied_world_seeds=()) -> dict:
    cells = expected_cells(occupied_world_seeds)
    worlds = F0.world_rows("validation")
    result = {
        "schema": SCHEMA,
        "status": STATUS,
        "execution_authorized": False, "scientific_gate_authorized": False,
        "source_and_original_custody": "UNATTESTED_NOT_LOCKED",
        "reference": "P1.3 funded-v2",
        "question": "same_genome_same_world_paid_replay_policy_mechanism_only",
        "genetic_sampling": "first_five_G0_birth_seeds_per_population_no_selection",
        "population_count": F0.POPULATIONS,
        "founder_seeds_by_population": {
            str(p): list(fixed_founders(p)) for p in range(F0.POPULATIONS)},
        "worlds": worlds, "conditions": list(ARMS),
        "proposed_lives": len(cells),
        "proposed_horizon_steps_ceiling": len(cells) * F0.HORIZON,
        "original_selected_pipeline_lives_ceiling": 5040,
        "selection_worlds_used": 0,
        "worlds_opened": 0,
        "primary_descriptive": "paired_lived_steps_and_physical_paid_cognition",
        "survival_noninferiority_certified": False,
        "environmental_transfer_certified": False,
        "no_world_policy": "NO_SELECTION_VALIDATION_RESERVE_OR_OTHER_WORLD_OPENING",
    }
    result["sha256"] = sha256(json.dumps(result, sort_keys=True,
                                         separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return result


def _validate_row(row: Mapping, cells: Mapping) -> tuple:
    if not isinstance(row, Mapping) or set(row) != FIELDS:
        raise ValueError("invalid exact reduced receipt fields")
    p, index, seed, arm = (row[k] for k in
                          ("population", "world_index", "genome_seed", "arm"))
    if (any(type(x) is not int for x in (p, index, seed)) or
            type(arm) is not str or arm not in ARMS):
        raise ValueError("invalid matched cell identifier")
    key = (p, index, seed, arm)
    world = cells.get(key)
    if world is None:
        raise ValueError("unknown or unselected founder/world/arm")
    if (row["family"] != world["family"] or
            type(row["world_seed"]) is not int or
            row["world_seed"] != world["world_seed"] or
            type(row["life_seed"]) is not int or
            row["life_seed"] != world["life_seed"]):
        raise ValueError("unpaired family, world or life seed")
    n = row["steps_lived"]
    if type(n) is not int or not 1 <= n <= F0.HORIZON:
        raise ValueError("missing/invalid lived steps")
    if row["terminal"] not in ("dead", "censored") or (
            row["terminal"] == "censored" and n != F0.HORIZON):
        raise ValueError("invalid death or horizon censoring")
    for field in ("energy_paid", "vigilance_paid"):
        v = row[field]
        if type(v) not in (int, float) or not isfinite(v) or v < 0:
            raise ValueError("invalid physical paid cognition")
    inactive = row["inactive_steps"]
    if type(inactive) is not int or not 0 <= inactive <= n:
        raise ValueError("invalid inactivity")
    return key


def _mean(rows: list, field: str) -> float:
    return fsum(row[field] for row in rows) / len(rows)


def descriptive_readout(rows: list, occupied_world_seeds=()) -> dict:
    """Describe paired lives after COMPLETE receipts; never a statistical gate.

    Original hashes, source lock, actual settlement and biological sampling
    must be checked outside this pure reduced-row calculator. No inference
    for unseen ecologies, no mean survival non-inferiority, no Stage-2.2 GO.
    """
    cells = expected_cells(occupied_world_seeds)
    if type(rows) is not list or len(rows) != len(cells):
        raise ValueError("NO_VERDICT: expected all 720 paired reduced rows")
    received = {}
    for row in rows:
        key = _validate_row(row, cells)
        if key in received:
            raise ValueError("NO_VERDICT: duplicate paired cell")
        received[key] = row
    if set(received) != set(cells):
        raise ValueError("NO_VERDICT: incomplete matched panel")

    blocks = {}
    family_contrasts = {family: {name: [] for name, _, _ in CONTRASTS}
                        for family in F0.FAMILIES}
    population_contrasts = {p: {name: [] for name, _, _ in CONTRASTS}
                            for p in range(F0.POPULATIONS)}
    for p, index, seed in sorted({(p, idx, seed) for p, idx, seed, _ in cells}):
        block = {arm: received[(p, index, seed, arm)] for arm in ARMS}
        family = block[ARMS[0]]["family"]
        differences = {}
        for name, a, b in CONTRASTS:
            ra, rb = block[a], block[b]
            d = {
                "lived_steps": ra["steps_lived"] - rb["steps_lived"],
                "survival_at_400": int(ra["terminal"] == "censored") -
                                   int(rb["terminal"] == "censored"),
                "energy_paid_per_assigned_life": ra["energy_paid"] - rb["energy_paid"],
                "vigilance_paid_per_assigned_life": ra["vigilance_paid"] -
                                                    rb["vigilance_paid"],
                "inactive_steps_per_assigned_life": ra["inactive_steps"] -
                                                    rb["inactive_steps"],
            }
            differences[name] = d
            family_contrasts[family][name].append(d)
            population_contrasts[p][name].append(d)
        blocks[(p, index, seed)] = differences

    def group_summary(group):
        return {
            name: {metric: _mean(ds, metric) for metric in (
                "lived_steps", "survival_at_400", "energy_paid_per_assigned_life",
                "vigilance_paid_per_assigned_life", "inactive_steps_per_assigned_life")}
            for name, ds in group.items()
        }

    by_population = {p: group_summary(v) for p, v in population_contrasts.items()}
    by_family = {family: group_summary(v) for family, v in family_contrasts.items()}
    all_groups = {
        name: {p: by_population[p][name] for p in by_population}
        for name, _, _ in CONTRASTS
    }
    return {
        "schema": SCHEMA, "status": "DESCRIPTIVE_ONLY_NO_SCIENTIFIC_VERDICT",
        "worlds_opened_by_helper": False,
        "actual_original_custody": "NOT_AUTHENTICATED",
        "population_independence": "NOT_ESTABLISHED",
        "selection_effect_tested": False,
        "survival_noninferiority_certified": False,
        "record_count": len(received), "paired_blocks": len(blocks),
        "by_population": by_population, "by_family": by_family,
        "equal_population_mean_contrasts": {
            name: {metric: fsum(all_groups[name][p][metric] for p in by_population) /
                   F0.POPULATIONS
                   for metric in by_population[0][name]}
            for name, _, _ in CONTRASTS
        },
        "exposure_time_warning": "paid_per_lived_step_may_improve_when_lives_end_earlier",
        "inference": "FINITE_UNOPENED_F0_DESIGN_ONLY_NO_NEW_FAMILY_GENERALIZATION",
    }
