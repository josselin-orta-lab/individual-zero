"""Stage-2.1 gate population design and directional arithmetic; no World access.

PROPOSAL only, NOT preregistration, execution or authorization.
"""
from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import json
from math import comb, isfinite

from . import stage0_design as F0
from . import stage2_random_equal_mean as RANDOM

SCHEMA = "i3-stage2-1-selected-gate-design-v1"
ALPHA = 0.05
SURVIVAL_MARGIN = 0.05
INACTIVE_MARGIN = 0.05
ENDPOINTS = (
    "cognitive_energy_per_lived_step",
    "cognitive_vigilance_per_lived_step",
    "survival_at_400",
    "inactive_step_fraction",
)
VALIDATION_CONDITIONS = (
    "FIXED_on_FIXED_selected",
    "GATE_on_GATE_selected",
    "FIXED_on_GATE_selected",
    "RANDOM_on_GATE_selected",
    "ZERO_PERCEIVED_COST_on_GATE_selected",
)


def design(occupied_world_seeds=()):
    """Deterministic plan; all proposed worlds remain unopened."""
    stage0 = F0.manifest(occupied_world_seeds)
    populations, founders, keep = F0.POPULATIONS, F0.CANDIDATES, F0.KEEP
    repeats = F0.WORLDS_PER_POPULATION
    selection_lives = populations * founders * repeats * 2
    validation_lives = populations * keep * repeats * len(VALIDATION_CONDITIONS)
    result = {
        "schema": SCHEMA,
        "status": "PROPOSAL_SOFTWARE_ONLY_NOT_PREREGISTERED",
        "execution_authorized": False,
        "scientific_gate_authorized": False,
        "reference": "P1.3 funded-v2",
        "mechanism": "p13_replay_gate_v1_FROZEN_UNCHANGED",
        "random_mean_exact": [RANDOM.DEVELOPMENT_REPLAYS, RANDOM.DEVELOPMENT_SLEEP_STEPS],
        "random_count_schedule": RANDOM.SCHEMA,
        "population_count": populations,
        "founders_per_population": founders,
        "selected_per_architecture": keep,
        "independent_unit": "new_G0_genetic_population; not genome or life",
        "founder_seeds": stage0["founder_seeds"],
        "selection_worlds": stage0["worlds"]["selection"],
        "validation_worlds": stage0["worlds"]["validation"],
        "selection_policies": ["FIXED", "GATE"],
        "validation_conditions": list(VALIDATION_CONDITIONS),
        "selection_rule": stage0["selection_rule"],
        "horizon": F0.HORIZON,
        "endpoint_alpha_one_sided": ALPHA,
        "survival_noninferiority_absolute_margin": SURVIVAL_MARGIN,
        "inactive_noninferiority_absolute_margin": INACTIVE_MARGIN,
        "endpoints": list(ENDPOINTS),
        "selection_lives_ceiling": selection_lives,
        "validation_lives_ceiling": validation_lives,
        "total_lives_ceiling": selection_lives + validation_lives,
        "lived_steps_ceiling": (selection_lives + validation_lives) * F0.HORIZON,
        "source_and_custody": "PENDING_OWNER_AND_EXACT_TRANSPORT_FREEZE",
        "no_world_policy": "NO_SELECTION_VALIDATION_RESERVE_OR_OTHER_WORLD_OPENING",
    }
    result["sha256"] = sha256(json.dumps(result, sort_keys=True,
                                           separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return result


def _population_sign_test(positive_contrasts: Mapping[int, float]) -> dict:
    if (not isinstance(positive_contrasts, Mapping)
            or set(positive_contrasts) != set(range(F0.POPULATIONS))
            or any(type(p) is not int for p in positive_contrasts)):
        raise ValueError("require one contrast per each of eight independent populations")
    values = list(positive_contrasts.values())
    if any(type(v) not in (int, float) or not isfinite(v) for v in values):
        raise ValueError("contrasts must be finite real scalars, not booleans/lives")
    wins = sum(v > 0 for v in values)
    losses = sum(v < 0 for v in values)
    n = wins + losses
    p = sum(comb(n, k) for k in range(wins, n + 1)) / (2 ** n)
    return {
        "wins": wins, "losses": losses, "ties": F0.POPULATIONS - n,
        "effective_n": n, "p_one_sided": p, "directional_pass": p <= ALPHA,
    }


def directional_gate(population_deltas: Mapping[str, Mapping[int, float]]) -> dict:
    """Pure proposed arithmetic over signed population-level GATE minus FIXED.

    Receipts, source and population independence MUST be verified elsewhere.
    This cannot issue an automatic scientific verdict or adoption.
    """
    if not isinstance(population_deltas, Mapping) or set(population_deltas) != set(ENDPOINTS):
        raise ValueError("require all four prespecified endpoints")
    transformed = {}
    for name, d in population_deltas.items():
        if not isinstance(d, Mapping) or set(d) != set(range(F0.POPULATIONS)):
            raise ValueError("missing population contrasts")
        if any(type(v) not in (int, float) or not isfinite(v) for v in d.values()):
            raise ValueError("invalid population contrast")
        if name in ENDPOINTS[:2]:
            transformed[name] = {p: -v for p, v in d.items()}
        elif name == "survival_at_400":
            transformed[name] = {p: v + SURVIVAL_MARGIN for p, v in d.items()}
        else:
            transformed[name] = {p: INACTIVE_MARGIN - v for p, v in d.items()}
    results = {name: _population_sign_test(transformed[name]) for name in ENDPOINTS}
    return {
        "endpoints": results,
        "all_directional_tests_pass": all(r["directional_pass"] for r in results.values()),
        "scope": "eight_population_directional_median_only; not mean equivalence",
        "status": "ARITHMETIC_ONLY_NOT_A_SCIENTIFIC_VERDICT",
    }
