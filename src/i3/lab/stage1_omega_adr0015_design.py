"""Prospective ADR-0015 Stage-1 omega gate design and arithmetic only.

No World/runtime import and no life execution. The design reuses the unopened
Stage-0 F0 selection/validation metadata. It freezes selection, equal-genome
omega ablation, survival non-inferiority, revision scoring and mechanism gates
before any exposure.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from math import comb, floor, fsum, isfinite

from i3.lab import stage0_design as S
from i3.modules.genome import (
    GENE_ORDER, digest, generation_zero, validate)

SCHEMA = "i3-stage1-omega-adr0015-design-v1"
BASELINE = "077d6b92fd19eaa6350ec79c370f44820f8dffb5"
REFERENCE_POLICY = "reference"
CANDIDATE_POLICY = "genomic_omega_frontier_information_v1"
OMEGA_ZERO_ARM = "candidate_omega_zero_validation_only"
ARMS = ("reference", "candidate", "omega_zero")
HORIZON = 400
FAMILIES = ("stable", "depletion", "pulse")
POPULATIONS = 8
CANDIDATES = 40
KEEP = 5
REPEATS = 2

# Historical G2e used a 3% family non-inferiority allowance. Each fresh family
# here has 8 populations * 2 worlds * 5 selected genomes = 80 lives.
FAMILY_LIVES_PER_ARM = POPULATIONS * REPEATS * KEEP
HISTORICAL_FAMILY_MARGIN_RATE = 0.03
FAMILY_SURVIVAL_MARGIN = floor(
    HISTORICAL_FAMILY_MARGIN_RATE * FAMILY_LIVES_PER_ARM)  # 2 / 80

REVISION_FAILURE_RANK = HORIZON + 1
DIRECTIONAL_POPULATIONS = 7
MIN_OMEGA_BENEFIT_FAMILIES = 2

SELECTION_FIELDS = {
    "candidate_seed", "world_index", "terminal", "steps_lived",
    "genome_digest",
}
VALIDATION_FIELDS = {
    "arm", "population", "family", "world_index", "founder_seed",
    "genome_digest", "terminal", "steps_lived",
    "revision_status", "revision_latency",
}
CUSTODY_FIELDS = {
    "source_lock", "world_lock", "observer_valid",
    "no_cognitive_shortfall", "rank0_replay_identical",
}


def _digest(data):
    return sha256(json.dumps(
        data, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


def _mean(values):
    values = tuple(values)
    if not values:
        raise ValueError("nonempty values required")
    if any(type(x) not in (int, float) or isinstance(x, bool)
           or not isfinite(x) for x in values):
        raise ValueError("finite numeric values required")
    return fsum(values) / len(values)


def _sign_test(values):
    """Two-sided exact sign test; zero ties excluded and reported."""
    values = tuple(values)
    if any(type(x) not in (int, float) or isinstance(x, bool)
           or not isfinite(x) for x in values):
        raise ValueError("finite sign-test differences required")
    wins = sum(x > 0 for x in values)
    losses = sum(x < 0 for x in values)
    n = wins + losses
    if n == 0:
        p = 1.0
    else:
        tail = sum(
            comb(n, k) for k in range(min(wins, losses) + 1)
        ) / (2 ** n)
        p = min(1.0, 2.0 * tail)
    return {
        "wins": wins,
        "losses": losses,
        "ties": len(values) - n,
        "effective_n": n,
        "p_two_sided": p,
        "status": "DESCRIPTIVE_EXACT_SIGN_TEST",
    }


def founder_seeds(population):
    if type(population) is not int or not 0 <= population < POPULATIONS:
        raise ValueError("invalid population")
    return tuple(
        S.founder_seed(population, slot)
        for slot in range(CANDIDATES)
    )


def _base_genome(seed):
    if type(seed) is not int:
        raise ValueError("integer founder seed required")
    return generation_zero(seed)


def omega_zero_genome(seed):
    """Same current genome except omega := 0 before birth."""
    original = _base_genome(seed)
    out = deepcopy(original)
    out["genes"]["omega"] = 0.0
    validate(out)
    for name in GENE_ORDER:
        if name == "omega":
            continue
        if out["genes"][name] != original["genes"][name]:
            raise RuntimeError("omega ablation changed a common gene")
    return out


def genome_for_arm(arm, seed):
    if arm in ("reference", "candidate"):
        return _base_genome(seed)
    if arm == "omega_zero":
        return omega_zero_genome(seed)
    raise ValueError("unknown validation arm")


def _world_rows(cohort):
    rows = S.world_rows(cohort)
    if cohort == "selection":
        expected = set(range(72, 120))
    elif cohort == "validation":
        expected = set(range(120, 168))
    else:
        raise ValueError("only selection/validation metadata")
    if {row["index"] for row in rows} != expected:
        raise RuntimeError("Stage-0 allocation contract changed")
    if any(row["family"] not in FAMILIES for row in rows):
        raise RuntimeError("foreign ecology in Stage-0 allocation")
    return rows


def plan(occupied_world_seeds=()):
    occupied = set(occupied_world_seeds)
    if any(type(x) is not int or isinstance(x, bool) or x < 0
           for x in occupied):
        raise ValueError("invalid occupied world seed")

    selection = _world_rows("selection")
    validation = _world_rows("validation")
    selection_seeds = {row["world_seed"] for row in selection}
    validation_seeds = {row["world_seed"] for row in validation}
    if selection_seeds & validation_seeds:
        raise RuntimeError("selection/validation seed overlap")
    if occupied & (selection_seeds | validation_seeds):
        raise ValueError("prospective allocation already occupied")
    reserve = set(range(*S.COHORT_BOUNDS["reserve"]))
    if (selection_seeds | validation_seeds) & reserve:
        raise RuntimeError("sealed reserve overlap")

    pools = {
        p: founder_seeds(p) for p in range(POPULATIONS)
    }
    selection_lives = (
        POPULATIONS * CANDIDATES * len(FAMILIES) * REPEATS * 2)
    validation_main_lives = (
        POPULATIONS * KEEP * len(FAMILIES) * REPEATS * 3)
    # One exact replay for rank-0 selected genome per population/world/arm.
    validation_replay_lives = (
        POPULATIONS * len(FAMILIES) * REPEATS * 3)

    data = {
        "schema": SCHEMA,
        "baseline": BASELINE,
        "status": "DESIGN_ONLY_NOT_EXECUTION_AUTHORIZATION",
        "execution_authorized": False,
        "genome_schema": "i3-genome-v4",
        "candidate_policy": CANDIDATE_POLICY,
        "reference_policy": REFERENCE_POLICY,
        "omega_zero_arm": OMEGA_ZERO_ARM,
        "populations": POPULATIONS,
        "candidates_per_population": CANDIDATES,
        "keep_per_architecture_population": KEEP,
        "horizon": HORIZON,
        "families": list(FAMILIES),
        "selection_worlds": selection,
        "validation_worlds": validation,
        "founder_seeds": {str(p): list(v) for p, v in pools.items()},
        "selection_rule": [
            "censored_count_desc", "lived_steps_desc", "founder_seed_asc"],
        "selection_arms": ["reference", "candidate"],
        "validation_arms": ["reference", "candidate", "omega_zero"],
        "omega_zero_selection": "NEVER_INDEPENDENTLY_SELECTED",
        "omega_zero_pairing": (
            "CANDIDATE_SELECTED_GENOME_COMMON30_IDENTICAL_OMEGA_FORCED_ZERO"),
        "family_survival_noninferiority": {
            "historical_margin_rate": HISTORICAL_FAMILY_MARGIN_RATE,
            "lives_per_family_arm": FAMILY_LIVES_PER_ARM,
            "max_survivor_deficit": FAMILY_SURVIVAL_MARGIN,
        },
        "revision": {
            "definition": "R-depletion-v1",
            "primary_complete_rank": (
                "latency_from_available_steps_if_REACQUIRED_else_401"),
            "failure_rank": REVISION_FAILURE_RANK,
            "directional_populations_required": DIRECTIONAL_POPULATIONS,
            "conditional_success_latency": "DESCRIPTIVE_ONLY",
        },
        "omega_selection": {
            "directional_populations_required": DIRECTIONAL_POPULATIONS,
            "population_shift": (
                "mean_selected_candidate_omega_minus_mean_candidate_pool_omega"),
            "pooled_selected_mean_must_be_positive": True,
        },
        "omega_zero_ablation": {
            "directional_populations_required": DIRECTIONAL_POPULATIONS,
            "pooled_candidate_survival_must_exceed_ablation": True,
            "families_with_positive_survival_difference_required":
                MIN_OMEGA_BENEFIT_FAMILIES,
        },
        "custody_floors": sorted(CUSTODY_FIELDS),
        "paired_world_sign_tests": "REPORT_DESCRIPTIVELY_NOT_NONINFERIORITY_TEST",
        "full_competition_observer": True,
        "resource_observer_on_validation_depletion": True,
        "rank0_exact_replay_per_validation_world_and_arm": True,
        "selection_lives": selection_lives,
        "validation_main_lives": validation_main_lives,
        "validation_replay_lives": validation_replay_lives,
        "maximum_lives": (
            selection_lives + validation_main_lives
            + validation_replay_lives),
        "maximum_life_steps": (
            selection_lives + validation_main_lives
            + validation_replay_lives) * HORIZON,
        "reserve": {
            "first": S.COHORT_BOUNDS["reserve"][0],
            "stop_exclusive": S.COHORT_BOUNDS["reserve"][1],
            "policy": "SEALED_NEVER_OPEN",
        },
        "prohibitions": [
            "NO_VALIDATION_RERANKING",
            "NO_OMEGA_ZERO_SELECTION",
            "NO_POST_EXPOSURE_MARGIN_CHANGE",
            "NO_FAMILY_SPECIFIC_OMEGA",
            "NO_CRASH_AS_DEATH",
            "NO_RETRY_OR_SEED_REPLACEMENT",
        ],
    }
    data["sha256"] = _digest(data)
    return data


def rank_selection(population, arm, receipts):
    """ADR-0015 persistence ranking with current-genome custody."""
    if arm not in ("reference", "candidate"):
        raise ValueError("only independently selected architecture arms")
    expected_seeds = set(founder_seeds(population))
    expected_worlds = {
        row["index"] for row in _world_rows("selection")
        if row["population"] == population
    }
    stripped = []
    seen = set()
    for row in receipts:
        if type(row) is not dict or set(row) != SELECTION_FIELDS:
            raise ValueError("invalid selection receipt fields")
        seed = row["candidate_seed"]
        index = row["world_index"]
        if seed not in expected_seeds or index not in expected_worlds:
            raise ValueError("foreign selection candidate/world")
        if row["genome_digest"] != digest(_base_genome(seed)):
            raise ValueError("selection genome digest mismatch")
        key = (seed, index)
        if key in seen:
            raise ValueError("duplicate selection receipt")
        seen.add(key)
        stripped.append({
            "candidate_seed": seed,
            "world_index": index,
            "terminal": row["terminal"],
            "steps_lived": row["steps_lived"],
        })
    return S.rank_candidates(population, stripped)


def _revision_rank(status, latency):
    if status == "REACQUIRED":
        if (type(latency) is not int or isinstance(latency, bool)
                or not 1 <= latency <= HORIZON):
            raise ValueError("invalid reacquisition latency")
        return latency
    if status in ("NO_EXPOSURE", "EXPOSED_NO_REACQUISITION"):
        if latency is not None:
            raise ValueError("failure/non-exposure latency must be None")
        return REVISION_FAILURE_RANK
    raise ValueError("unknown revision status")


def _validate_selected(selected, label):
    if type(selected) is not dict or set(selected) != set(range(POPULATIONS)):
        raise ValueError(f"complete {label} selected mapping required")
    out = {}
    for p in range(POPULATIONS):
        seeds = tuple(selected[p])
        if len(seeds) != KEEP or len(set(seeds)) != KEEP:
            raise ValueError(f"{label} must contain five unique selected seeds")
        if not set(seeds).issubset(founder_seeds(p)):
            raise ValueError(f"{label} includes foreign founder")
        out[p] = seeds
    return out


def _expected_validation_worlds():
    return {
        (row["population"], row["index"]): row
        for row in _world_rows("validation")
    }


def analyze_gate(selected_reference, selected_candidate, validation_receipts,
                 custody):
    """Pure prospective gate arithmetic on already verified validation rows.

    This function does not authenticate runtime evidence; an eventual runner
    must create these rows only after full receipt/source/world verification.
    """
    selected_reference = _validate_selected(
        selected_reference, "reference")
    selected_candidate = _validate_selected(
        selected_candidate, "candidate")

    if (type(custody) is not dict or set(custody) != CUSTODY_FIELDS
            or any(type(custody[k]) is not bool for k in custody)):
        raise ValueError("exact custody floor mapping required")

    worlds = _expected_validation_worlds()
    expected_count = POPULATIONS * len(FAMILIES) * REPEATS * KEEP * 3
    if len(validation_receipts) != expected_count:
        raise ValueError("incomplete validation; no successful-subset analysis")

    by_arm = {arm: [] for arm in ARMS}
    seen = set()
    for row in validation_receipts:
        if type(row) is not dict or set(row) != VALIDATION_FIELDS:
            raise ValueError("invalid validation receipt fields")
        arm = row["arm"]
        p = row["population"]
        index = row["world_index"]
        if arm not in ARMS or (p, index) not in worlds:
            raise ValueError("foreign validation arm/population/world")
        meta = worlds[(p, index)]
        if row["family"] != meta["family"]:
            raise ValueError("validation family/index mismatch")
        allowed = (
            selected_reference[p] if arm == "reference"
            else selected_candidate[p])
        seed = row["founder_seed"]
        if seed not in allowed:
            raise ValueError("validation genome was not selected")
        if row["genome_digest"] != digest(genome_for_arm(arm, seed)):
            raise ValueError("validation genome/ablation digest mismatch")
        terminal, steps = row["terminal"], row["steps_lived"]
        if (terminal not in ("dead", "censored")
                or type(steps) is not int or isinstance(steps, bool)
                or not 0 <= steps <= HORIZON
                or (terminal == "censored" and steps != HORIZON)):
            raise ValueError("invalid validation physical outcome")
        if meta["family"] == "depletion":
            _revision_rank(
                row["revision_status"], row["revision_latency"])
        elif (row["revision_status"] is not None
              or row["revision_latency"] is not None):
            raise ValueError("revision endpoint belongs only to depletion")
        key = (arm, p, index, seed)
        if key in seen:
            raise ValueError("duplicate validation receipt")
        seen.add(key)
        by_arm[arm].append(row)

    # Every selected seed must have exactly one row on every world in its block.
    for arm in ARMS:
        for p in range(POPULATIONS):
            allowed = (
                selected_reference[p] if arm == "reference"
                else selected_candidate[p])
            expected = {
                (arm, p, row["index"], seed)
                for row in _world_rows("validation")
                if row["population"] == p
                for seed in allowed
            }
            actual = {
                (row["arm"], row["population"], row["world_index"],
                 row["founder_seed"])
                for row in by_arm[arm] if row["population"] == p
            }
            if actual != expected:
                raise ValueError("validation membership incomplete or shifted")

    survival_family = {
        arm: {
            family: sum(
                row["terminal"] == "censored"
                for row in by_arm[arm] if row["family"] == family)
            for family in FAMILIES
        } for arm in ARMS
    }
    survival_population = {
        arm: {
            p: sum(
                row["terminal"] == "censored"
                for row in by_arm[arm] if row["population"] == p)
            for p in range(POPULATIONS)
        } for arm in ARMS
    }

    # ADR-0015 paired-world selected-survivor counts.
    world_differences = []
    family_world_differences = {family: [] for family in FAMILIES}
    for p in range(POPULATIONS):
        for meta in _world_rows("validation"):
            if meta["population"] != p:
                continue
            index = meta["index"]
            counts = {}
            for arm in ("reference", "candidate"):
                counts[arm] = sum(
                    row["terminal"] == "censored"
                    for row in by_arm[arm]
                    if row["population"] == p
                    and row["world_index"] == index)
            diff = counts["candidate"] - counts["reference"]
            world_differences.append(diff)
            family_world_differences[meta["family"]].append(diff)

    revision = {}
    for arm in ("reference", "candidate", "omega_zero"):
        per_population = {}
        all_ranks = []
        reacquired = 0
        for p in range(POPULATIONS):
            rows = [
                row for row in by_arm[arm]
                if row["population"] == p
                and row["family"] == "depletion"]
            ranks = tuple(
                _revision_rank(
                    row["revision_status"], row["revision_latency"])
                for row in rows)
            per_population[p] = {
                "mean_complete_rank": _mean(ranks),
                "reacquired": sum(
                    row["revision_status"] == "REACQUIRED" for row in rows),
                "ranks": ranks,
            }
            all_ranks.extend(ranks)
            reacquired += per_population[p]["reacquired"]
        revision[arm] = {
            "population": per_population,
            "pooled_mean_complete_rank": _mean(all_ranks),
            "reacquired": reacquired,
        }

    omega = {"population": {}}
    selected_values = []
    pool_values = []
    reference_selected_values = []
    for p in range(POPULATIONS):
        pool = tuple(
            _base_genome(seed)["genes"]["omega"]
            for seed in founder_seeds(p))
        cand = tuple(
            _base_genome(seed)["genes"]["omega"]
            for seed in selected_candidate[p])
        ref = tuple(
            _base_genome(seed)["genes"]["omega"]
            for seed in selected_reference[p])
        omega["population"][p] = {
            "pool_mean": _mean(pool),
            "candidate_selected_mean": _mean(cand),
            "candidate_shift": _mean(cand) - _mean(pool),
            "reference_selected_mean": _mean(ref),
            "reference_shift_negative_control": _mean(ref) - _mean(pool),
            "candidate_selected_values": cand,
            "reference_selected_values": ref,
        }
        selected_values.extend(cand)
        pool_values.extend(pool)
        reference_selected_values.extend(ref)
    omega.update({
        "pooled_pool_mean": _mean(pool_values),
        "pooled_candidate_selected_mean": _mean(selected_values),
        "pooled_candidate_shift":
            _mean(selected_values) - _mean(pool_values),
        "pooled_reference_selected_mean":
            _mean(reference_selected_values),
    })

    g1 = all(
        survival_family["candidate"][family]
        >= survival_family["reference"][family] - FAMILY_SURVIVAL_MARGIN
        for family in FAMILIES)

    revision_diffs = {
        p: (revision["reference"]["population"][p]["mean_complete_rank"]
            - revision["candidate"]["population"][p]["mean_complete_rank"])
        for p in range(POPULATIONS)
    }
    g2 = (
        sum(value > 0 for value in revision_diffs.values())
        >= DIRECTIONAL_POPULATIONS
        and revision["candidate"]["pooled_mean_complete_rank"]
        < revision["reference"]["pooled_mean_complete_rank"]
        and revision["candidate"]["reacquired"] >= 1)

    omega_shifts = {
        p: omega["population"][p]["candidate_shift"]
        for p in range(POPULATIONS)
    }
    g3 = (
        sum(value > 0 for value in omega_shifts.values())
        >= DIRECTIONAL_POPULATIONS
        and omega["pooled_candidate_selected_mean"] > 0.0
        and omega["pooled_candidate_shift"] > 0.0)

    ablation_pop_diffs = {
        p: (survival_population["candidate"][p]
            - survival_population["omega_zero"][p])
        for p in range(POPULATIONS)
    }
    g4 = (
        sum(value > 0 for value in ablation_pop_diffs.values())
        >= DIRECTIONAL_POPULATIONS
        and sum(survival_population["candidate"].values())
        > sum(survival_population["omega_zero"].values()))

    ablation_family_diffs = {
        family: (
            survival_family["candidate"][family]
            - survival_family["omega_zero"][family])
        for family in FAMILIES
    }
    g5 = (
        sum(value > 0 for value in ablation_family_diffs.values())
        >= MIN_OMEGA_BENEFIT_FAMILIES)

    g6 = all(custody.values())

    rules = {
        "G1_family_survival_noninferiority": g1,
        "G2_revision_complete_rank_superiority": g2,
        "G3_selection_shifts_omega_upward": g3,
        "G4_equal_genome_omega0_ablation_beaten": g4,
        "G5_not_single_family_omega_calibration": g5,
        "G6_custody_floors": g6,
    }
    return {
        "schema": "i3-stage1-omega-adr0015-gate-arithmetic/v1",
        "status": "ARITHMETIC_ONLY_NOT_SCIENTIFIC_EVIDENCE",
        "family_survival": survival_family,
        "population_survival": survival_population,
        "family_noninferiority_margin": FAMILY_SURVIVAL_MARGIN,
        "revision": revision,
        "revision_population_differences_reference_minus_candidate":
            revision_diffs,
        "omega_selection": omega,
        "omega_selection_shift_sign_test":
            _sign_test(tuple(omega_shifts.values())),
        "omega0_population_survival_differences":
            ablation_pop_diffs,
        "omega0_population_sign_test":
            _sign_test(tuple(ablation_pop_diffs.values())),
        "omega0_family_survival_differences":
            ablation_family_diffs,
        "paired_world_candidate_minus_reference_sign_test":
            _sign_test(world_differences),
        "paired_world_sign_tests_by_family": {
            family: _sign_test(values)
            for family, values in family_world_differences.items()
        },
        "revision_population_sign_test":
            _sign_test(tuple(revision_diffs.values())),
        "custody": dict(custody),
        "rules": rules,
        "would_pass_if_receipts_are_authentic": all(rules.values()),
        "interpretation": (
            "SEVEN_OF_EIGHT_DIRECTIONAL_RULES_ARE_NOT_CONVENTIONAL_"
            "SIGNIFICANCE_CLAIMS"),
    }


__all__ = [
    "ARMS", "BASELINE", "CANDIDATES", "CANDIDATE_POLICY",
    "DIRECTIONAL_POPULATIONS", "FAMILIES", "FAMILY_SURVIVAL_MARGIN",
    "HORIZON", "KEEP", "OMEGA_ZERO_ARM", "POPULATIONS",
    "REFERENCE_POLICY", "REVISION_FAILURE_RANK", "SCHEMA",
    "analyze_gate", "founder_seeds", "genome_for_arm", "omega_zero_genome",
    "plan", "rank_selection",
]
