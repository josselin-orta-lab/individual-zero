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


def _paired_outcome_profile(received: Mapping) -> dict:
    """Expose *all* matched adverse outcomes, without inference or GO.

    No margin, rescue reward or pass/fail criterion is added. The observed
    240 paired blocks share worlds and genomes: they are not independent
    population samples. A death on step 400 is never a censoring event.
    """
    blocks = sorted({(p, index, seed) for p, index, seed, _ in received})
    if len(blocks) != F0.POPULATIONS * F0.WORLDS_PER_POPULATION * F0.KEEP:
        raise ValueError("incomplete finite matched blocks")
    records = {name: [] for name, _, _ in CONTRASTS}
    for p, index, seed in blocks:
        arm_rows = {arm: received[(p, index, seed, arm)] for arm in ARMS}
        family = arm_rows[ARMS[0]]["family"]
        for name, a, b in CONTRASTS:
            left, right = arm_rows[a], arm_rows[b]
            records[name].append({
                "population": p, "family": family,
                "gate_survived": left["terminal"] == "censored",
                "comparator_survived": right["terminal"] == "censored",
                "steps_delta": left["steps_lived"] - right["steps_lived"],
                "energy_delta": left["energy_paid"] - right["energy_paid"],
                "vigilance_delta": left["vigilance_paid"] - right["vigilance_paid"],
                "gate_dead_at_400": (left["terminal"] == "dead"
                                     and left["steps_lived"] == F0.HORIZON),
                "comparator_dead_at_400": (right["terminal"] == "dead"
                                           and right["steps_lived"] == F0.HORIZON),
            })

    def summarize(pairs):
        if not pairs:
            raise ValueError("empty paired family or population")
        survival = {
            "both_survived": 0, "gate_only_survived": 0,
            "comparator_only_survived": 0, "neither_survived": 0,
        }
        duration = {"gate_longer": 0, "gate_shorter": 0, "equal": 0}
        for item in pairs:
            a, b = item["gate_survived"], item["comparator_survived"]
            category = (
                "both_survived" if a and b else
                "gate_only_survived" if a else
                "comparator_only_survived" if b else "neither_survived"
            )
            survival[category] += 1
            delta = item["steps_delta"]
            duration["gate_longer" if delta > 0 else
                     "gate_shorter" if delta < 0 else "equal"] += 1
        n = len(pairs)
        if sum(survival.values()) != n or sum(duration.values()) != n:
            raise ValueError("paired outcomes failed reconciliation")
        return {
            "paired_blocks": n,
            "survival_discordance": survival,
            "lived_steps_direction": duration,
            "worst_gate_minus_comparator_lived_steps": min(
                r["steps_delta"] for r in pairs),
            "best_gate_minus_comparator_lived_steps": max(
                r["steps_delta"] for r in pairs),
            "death_on_step_400": {
                "gate": sum(r["gate_dead_at_400"] for r in pairs),
                "comparator": sum(r["comparator_dead_at_400"] for r in pairs),
            },
            "lower_paid_energy_but_shorter_life": sum(
                r["energy_delta"] < 0 and r["steps_delta"] < 0 for r in pairs),
            "lower_paid_vigilance_but_shorter_life": sum(
                r["vigilance_delta"] < 0 and r["steps_delta"] < 0 for r in pairs),
            "lower_paid_energy_but_worse_horizon_survival": sum(
                r["energy_delta"] < 0 and not r["gate_survived"]
                and r["comparator_survived"] for r in pairs),
            "observed_survival_difference": (
                survival["gate_only_survived"] -
                survival["comparator_only_survived"]) / n,
        }

    return {
        "status": "DESCRIPTIVE_ONLY_NO_SCIENTIFIC_VERDICT",
        "paired_blocks_per_contrast": len(blocks),
        "overall": {name: summarize(pairs) for name, pairs in records.items()},
        "by_family": {
            family: {name: summarize([r for r in records[name]
                                      if r["family"] == family])
                     for name in records}
            for family in F0.FAMILIES
        },
        "by_population": {
            p: {name: summarize([r for r in records[name]
                                 if r["population"] == p])
                for name in records}
            for p in range(F0.POPULATIONS)
        },
        "statistical_inference": "NOT_ESTABLISHED",
        "survival_noninferiority_certified": False,
        "causal_replay_selection_advantage": "NOT_ESTABLISHED",
    }


def _random_fixed_control_bridge(received: Mapping) -> dict:
    """The missing *third* paired contrast: RANDOM minus FIXED.

    Exposes a three-policy algebraic accounting check, NOT causal mediation.
    No independence, significance, claimed control equivalence or GO is
    inferred from identities, even if all arithmetic residuals are zero.
    """
    measures = ("lived_steps", "survival_at_400", "energy_paid_per_assigned_life",
                "vigilance_paid_per_assigned_life",
                "inactive_steps_per_assigned_life")
    sources = {
        "lived_steps": "steps_lived",
        "energy_paid_per_assigned_life": "energy_paid",
        "vigilance_paid_per_assigned_life": "vigilance_paid",
        "inactive_steps_per_assigned_life": "inactive_steps",
    }

    def value(row, metric):
        if metric == "survival_at_400":
            return int(row["terminal"] == "censored")
        return row[sources[metric]]

    blocks = sorted({(p, index, seed) for p, index, seed, _ in received})
    if len(blocks) != F0.POPULATIONS * F0.KEEP * F0.WORLDS_PER_POPULATION:
        raise ValueError("incomplete G0 matched control blocks")
    triples = []
    residuals = {metric: [] for metric in measures}
    for p, index, seed in blocks:
        fixed, gate, random = (received[(p, index, seed, arm)] for arm in ARMS)
        deltas = {}
        for metric in measures:
            f, g, r = (value(row, metric) for row in (fixed, gate, random))
            deltas[metric] = r - f
            residuals[metric].append(abs(fsum((g - f, -(g - r), -(r - f)))))
        triples.append({
            "population": p, "family": fixed["family"], "deltas": deltas,
            "random_survived": random["terminal"] == "censored",
            "fixed_survived": fixed["terminal"] == "censored",
        })

    def summary(group):
        if not group:
            raise ValueError("missing F0 control stratum")
        survival = {
            "both_survived": 0, "random_only_survived": 0,
            "fixed_only_survived": 0, "neither_survived": 0,
        }
        for item in group:
            r, f = item["random_survived"], item["fixed_survived"]
            survival["both_survived" if r and f else
                     "random_only_survived" if r else
                     "fixed_only_survived" if f else "neither_survived"] += 1
        return {
            "paired_blocks": len(group),
            "random_minus_fixed_mean": {
                metric: fsum(item["deltas"][metric] for item in group) / len(group)
                for metric in measures
            },
            "survival_discordance": survival,
            "random_shorter": sum(x["deltas"]["lived_steps"] < 0 for x in group),
            "random_longer": sum(x["deltas"]["lived_steps"] > 0 for x in group),
            "equal_lived_steps": sum(x["deltas"]["lived_steps"] == 0 for x in group),
        }

    return {
        "status": "DESCRIPTIVE_ONLY_NO_CAUSAL_DECOMPOSITION",
        "question": "random_full_policy_minus_fixed_full_policy",
        "paired_blocks": len(triples),
        "overall": summary(triples),
        "by_family": {
            family: summary([x for x in triples if x["family"] == family])
            for family in F0.FAMILIES
        },
        "by_population": {
            p: summary([x for x in triples if x["population"] == p])
            for p in range(F0.POPULATIONS)
        },
        "triangle_identity": "GATE_minus_FIXED = GATE_minus_RANDOM + RANDOM_minus_FIXED",
        "triangle_max_absolute_arithmetic_residual": {
            metric: max(residuals[metric]) for metric in measures
        },
        "causal_mediation_certified": False,
        "physical_replay_parity_proven": False,
        "scientific_verdict": "NOT_ISSUED",
    }


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
        "paired_outcome_profile": _paired_outcome_profile(received),
        "random_fixed_control_bridge": _random_fixed_control_bridge(received),
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
