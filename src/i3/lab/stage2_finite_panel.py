"""Finite Stage-2.1 proposed validation panel: read-only receipt arithmetic.

NO World import, no opening, no runtime dispatch, no owner admission and no
scientific inference. Synthetic rows in unit tests are NOT observed lives.
The selected founder IDs and supplied reduced records are *untrusted labels*:
this helper cannot attest original G/R custody, valid ranking, or source lock.
"""
from __future__ import annotations

from collections.abc import Mapping
from math import fsum, isfinite

from . import stage0_design as F0
from . import stage2_gate_design as G

SCHEMA = "i3-stage2-1-finite-panel-readout-v1"
STATUS = "SOFTWARE_ONLY_FINITE_PANEL_DESCRIPTIVE_NOT_SCIENTIFIC_VERDICT"
SELECTED_ARMS = ("FIXED", "GATE")
CONDITIONS = G.VALIDATION_CONDITIONS
FIELDS = frozenset((
    "condition", "population", "family", "world_index", "world_seed",
    "genome_seed", "life_seed", "terminal", "steps_lived",
    "cognitive_energy_paid", "cognitive_vigilance_paid", "inactive_steps",
    "sleep_steps", "replays_paid", "random_draws",
    "random_nominal_replays", "random_eligible_replays",
))


def selected_founders(selected: Mapping) -> dict:
    """Only check pool membership and shape, NOT whether selection was earned."""
    if not isinstance(selected, Mapping) or set(selected) != set(SELECTED_ARMS):
        raise ValueError("require FIXED and GATE selected founder maps")
    cleaned = {}
    for arm in SELECTED_ARMS:
        pools = selected[arm]
        if not isinstance(pools, Mapping) or set(pools) != set(range(F0.POPULATIONS)):
            raise ValueError("one selected founder set per named population required")
        if any(type(p) is not int for p in pools):
            raise ValueError("population IDs must be integers")
        cleaned[arm] = {}
        for p in range(F0.POPULATIONS):
            seeds = pools[p]
            if not isinstance(seeds, (tuple, list)) or len(seeds) != F0.KEEP:
                raise ValueError("require exactly five selected founders per population")
            if any(type(seed) is not int for seed in seeds) or len(set(seeds)) != F0.KEEP:
                raise ValueError("duplicate or invalid selected founder")
            allowed = {F0.founder_seed(p, slot) for slot in range(F0.CANDIDATES)}
            if not set(seeds) <= allowed:
                raise ValueError("founder is outside this population's independent G0 pool")
            cleaned[arm][p] = tuple(sorted(seeds))
    return cleaned


def _selection_arm(condition: str) -> str:
    return "FIXED" if condition == "FIXED_on_FIXED_selected" else "GATE"


def expected_cells(selected: Mapping) -> dict:
    """Exact proposed identities; returns no WorldSpecs, genetic states or lives."""
    chosen = selected_founders(selected)
    expected = {}
    for world in F0.world_rows("validation"):
        p = world["population"]
        for condition in CONDITIONS:
            for seed in chosen[_selection_arm(condition)][p]:
                key = (condition, p, world["index"], seed)
                if key in expected:
                    raise ValueError("duplicate planned cell")
                expected[key] = world
    if len(expected) != (F0.POPULATIONS * F0.WORLDS_PER_POPULATION *
                         F0.KEEP * len(CONDITIONS)):
        raise ValueError("incomplete prospective finite panel")
    return expected


def _strict_count(value, label, maximum):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"invalid {label}")


def _strict_paid(value, label):
    if type(value) not in (int, float) or not isfinite(value) or value < 0:
        raise ValueError(f"invalid {label}")


def _check_row(row, expected):
    if not isinstance(row, Mapping) or set(row) != FIELDS:
        raise ValueError("receipt must have the exact reduced field set")
    condition, p, index, seed = (row[key] for key in
                                 ("condition", "population", "world_index", "genome_seed"))
    if (condition not in CONDITIONS or type(p) is not int or
            type(index) is not int or type(seed) is not int):
        raise ValueError("invalid panel identity")
    key = (condition, p, index, seed)
    world = expected.get(key)
    if world is None:
        raise ValueError("receipt not allocated to this selected population and condition")
    if (row["family"] != world["family"] or
            type(row["world_seed"]) is not int or row["world_seed"] != world["world_seed"] or
            type(row["life_seed"]) is not int or row["life_seed"] != world["life_seed"]):
        raise ValueError("world/family/life allocation is not the proposed paired slot")
    n = row["steps_lived"]
    _strict_count(n, "steps_lived", F0.HORIZON)
    if not n or row["terminal"] not in ("dead", "censored"):
        raise ValueError("missing life or invalid death/censoring status")
    if row["terminal"] == "censored" and n != F0.HORIZON:
        raise ValueError("censoring is only permitted at the fixed horizon")
    # Death AT horizon remains "dead", never inferred from steps alone.
    for field in ("cognitive_energy_paid", "cognitive_vigilance_paid"):
        _strict_paid(row[field], field)
    for field in ("inactive_steps", "sleep_steps"):
        _strict_count(row[field], field, n)
    _strict_count(row["replays_paid"], "replays_paid", 16 * row["sleep_steps"])
    for field in ("random_draws", "random_nominal_replays", "random_eligible_replays"):
        _strict_count(row[field], field, 16 * row["sleep_steps"])
    if condition == "RANDOM_on_GATE_selected":
        draws = row["random_draws"]
        nominal = row["random_nominal_replays"]
        eligible = row["random_eligible_replays"]
        if (draws > row["sleep_steps"] or
                not 6 * draws <= nominal <= 7 * draws or
                not row["replays_paid"] <= eligible <= nominal):
            raise ValueError("RANDOM nominal/eligible/paid replay custody inconsistent")
    elif any(row[field] for field in (
            "random_draws", "random_nominal_replays", "random_eligible_replays")):
        raise ValueError("non-RANDOM arm contains RANDOM schedule receipts")
    return key


def _summary(rows):
    n = len(rows)
    lived = sum(r["steps_lived"] for r in rows)
    censored = sum(r["terminal"] == "censored" for r in rows)
    energy = fsum(r["cognitive_energy_paid"] for r in rows)
    vigilance = fsum(r["cognitive_vigilance_paid"] for r in rows)
    inactive = sum(r["inactive_steps"] for r in rows)
    return {
        "assigned": n, "censored_at_400": censored, "deaths": n - censored,
        "survival_fraction": censored / n,
        "steps_lived": lived, "mean_lived_steps": lived / n,
        "energy_paid_total": energy, "vigilance_paid_total": vigilance,
        "energy_paid_per_assigned_life": energy / n,
        "vigilance_paid_per_assigned_life": vigilance / n,
        "energy_paid_per_lived_step": energy / lived,
        "vigilance_paid_per_lived_step": vigilance / lived,
        "inactive_steps": inactive, "inactive_fraction_lived": inactive / lived,
        "sleep_steps": sum(r["sleep_steps"] for r in rows),
        "replays_paid": sum(r["replays_paid"] for r in rows),
        "random_draws": sum(r["random_draws"] for r in rows),
        "random_nominal_replays": sum(r["random_nominal_replays"] for r in rows),
        "random_eligible_replays": sum(r["random_eligible_replays"] for r in rows),
    }


def reduce_finite_panel(selected: Mapping, rows: list) -> dict:
    """Validate exactly 1200 supplied reduced rows, return only descriptions.

    Missing/duplicate cells or corrupt billing fail closed. This cannot
    verify selected rank provenance or sealed original hashes, and even
    1200 structurally valid rows MUST NOT become a scientific GO.
    """
    expected = expected_cells(selected)
    if type(rows) is not list:
        raise ValueError("an explicit complete list of reduced rows is required")
    if len(rows) != len(expected):
        raise ValueError("NO_VERDICT: incomplete or oversized finite panel")
    observed = {}
    for row in rows:
        key = _check_row(row, expected)
        if key in observed:
            raise ValueError("NO_VERDICT: duplicate population/world/genome/condition")
        observed[key] = row
    if set(observed) != set(expected):
        raise ValueError("NO_VERDICT: missing validation cells")
    populations = {}
    for p in range(F0.POPULATIONS):
        per_condition = {
            arm: _summary([r for k, r in observed.items()
                           if k[1] == p and k[0] == arm])
            for arm in CONDITIONS
        }
        if any(s["assigned"] != F0.KEEP * F0.WORLDS_PER_POPULATION
               for s in per_condition.values()):
            raise ValueError("invalid per-population denominator")
        populations[p] = per_condition
    family_results = {}
    for family in F0.FAMILIES:
        by_arm = {
            arm: _summary([r for r in observed.values()
                           if r["family"] == family and r["condition"] == arm])
            for arm in CONDITIONS
        }
        family_results[family] = {
            "by_condition": by_arm,
            "gate_minus_fixed_survival": (
                by_arm["GATE_on_GATE_selected"]["survival_fraction"] -
                by_arm["FIXED_on_FIXED_selected"]["survival_fraction"]),
        }
    contrasts = {
        "GATE_selected_minus_FIXED_selected": (
            "GATE_on_GATE_selected", "FIXED_on_FIXED_selected"),
        "GATE_minus_FIXED_same_GATE_genomes": (
            "GATE_on_GATE_selected", "FIXED_on_GATE_selected"),
        "GATE_minus_RANDOM_same_GATE_genomes": (
            "GATE_on_GATE_selected", "RANDOM_on_GATE_selected"),
        "GATE_minus_ZERO_COST_same_GATE_genomes": (
            "GATE_on_GATE_selected", "ZERO_PERCEIVED_COST_on_GATE_selected"),
    }
    population_deltas = {
        name: {
            p: (by_arm[a]["survival_fraction"] - by_arm[b]["survival_fraction"])
            for p, by_arm in populations.items()
        }
        for name, (a, b) in contrasts.items()
    }
    return {
        "schema": SCHEMA,
        "status": STATUS, "scientific_verdict": "NOT_ISSUED",
        "source_and_original_custody": "NOT_AUTHENTICATED",
        "selected_rank_provenance": "NOT_AUTHENTICATED",
        "population_independence": "NOT_ESTABLISHED",
        "world_opening_authorized": False,
        "actual_scientific_study_executed_by_this_code": False,
        "finite_panel_cells": len(observed),
        "population_denominator_per_condition": F0.KEEP * F0.WORLDS_PER_POPULATION,
        "populations": populations, "families": family_results,
        "population_survival_deltas": population_deltas,
        "finite_panel_population_mean_survival_deltas": {
            name: fsum(v.values()) / F0.POPULATIONS
            for name, v in population_deltas.items()
        },
    }
