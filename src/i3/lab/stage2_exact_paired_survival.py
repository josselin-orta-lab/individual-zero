"""Exact finite-sample paired-survival risk-difference sensitivity.

Pure arithmetic on independent *iid* prospective matched pairs. This tool
cannot verify independent ecological draws, the scientific loss margin,
actual original data, World provenance or research-owner authorization.
It never imports/constructs World, Mind, engine, runtime, or experiment.

For D_i=1(GATE only survivor)-1(FIXED only survivor), the marginal counts
of GATE-only and FIXED-only survivors are individually Binomial(n,p)
under iid paired draws. Bonferroni on their exact one-sided Clopper-Pearson
bounds yields a finite-sample >=(1-alpha) lower bound on E[D] without
pretending that GATE/FIXED outcomes within a pair are independent.

The bound is conservative, unlike a promised optimal or guaranteed-
power sample size; Monte Carlo scenarios only estimate *conditional* power.
"""
from __future__ import annotations

from functools import lru_cache
from math import exp, fsum, isfinite, lgamma, log, log1p, sqrt
from random import Random

SCHEMA = "i3-stage2-1-exact-paired-survival-sensitivity/v1"
STATUS = "COMPUTATIONAL_STUDY_ONLY_NO_WORLD_OR_OWNER_GATE"
DEFAULT_ALPHA = 0.05
DEFAULT_MARGIN_FOR_SENSITIVITY_ONLY = 0.05


def _prob(value, name: str, *, zero_ok: bool = False) -> float:
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"{name} must be finite")
    if not (0 <= value < 1 if zero_ok else 0 < value < 1):
        raise ValueError(f"{name} outside allowed probability interval")
    return float(value)


def _count(n: int, label: str, *, allow_zero: bool = False) -> int:
    if type(n) is not int or (n < 0 if allow_zero else n <= 0):
        raise ValueError(f"{label} must be a valid integer count")
    return n


def _binomial_tail(n: int, k: int, p: float, upper: bool) -> float:
    """Stable finite binomial tail via summing relative to the modal term."""
    if not 0 <= k <= n:
        raise ValueError("count outside binomial support")
    if p == 0:
        return float(0 >= k if upper else 0 <= k)
    if p == 1:
        return float(n >= k if upper else n <= k)
    start, stop = (k, n) if upper else (0, k)
    mode = min(stop, max(start, int((n + 1) * p)))
    peak_log = (lgamma(n + 1) - lgamma(mode + 1)
                - lgamma(n - mode + 1)
                + mode * log(p) + (n - mode) * log1p(-p))
    # The ratios move away from the modal term, so each contribution <= 1
    # up to floating-point rounding; never calculate n! or comb(n,k).
    terms = [1.0]
    weight = 1.0
    for j in range(mode, start, -1):
        weight *= j * (1 - p) / ((n - j + 1) * p)
        terms.append(weight)
    weight = 1.0
    for j in range(mode, stop):
        weight *= (n - j) * p / ((j + 1) * (1 - p))
        terms.append(weight)
    return min(1.0, max(0.0, exp(peak_log) * fsum(terms)))


@lru_cache(maxsize=16384)
def _cp_bound(n: int, successes: int, tail_alpha: float, lower: bool) -> float:
    """Exact one-sided CP marginal bound; no asymptotic approximation."""
    if lower and successes == 0:
        return 0.0
    if not lower and successes == n:
        return 1.0
    low, high = 0.0, 1.0
    for _ in range(49):
        midpoint = (low + high) / 2
        tail = _binomial_tail(n, successes, midpoint, upper=lower)
        if lower:  # P_p(X >= successes) rises with p
            if tail < tail_alpha:
                low = midpoint
            else:
                high = midpoint
        else:  # P_p(X <= successes) falls with p
            if tail > tail_alpha:
                low = midpoint
            else:
                high = midpoint
    # Return the conservative end of the bisection interval.
    return low if lower else high


def exact_paired_lower_bound(*, pairs: int, gate_only: int, fixed_only: int,
                             alpha: float = DEFAULT_ALPHA) -> dict:
    """Lower confidence bound for P(GATE survives)-P(FIXED survives).

    Requires n iid units of the specific predeclared target G0/world pair
    distribution. Correlation *within* a pair is explicitly allowed.
    Pairwise shared Worlds/genomes or reuse across i can violate iid.
    Structural/missing lives cannot be converted into zero-difference ties.
    """
    n = _count(pairs, "pairs")
    gp = _count(gate_only, "gate_only", allow_zero=True)
    fp = _count(fixed_only, "fixed_only", allow_zero=True)
    if gp + fp > n:
        raise ValueError("paired discordances exceed assigned pairs")
    a = _prob(alpha, "alpha")
    tail = a / 2
    lower_gp = _cp_bound(n, gp, tail, True)
    upper_fp = _cp_bound(n, fp, tail, False)
    return {
        "schema": SCHEMA, "status": STATUS,
        "paired_independent_clusters_assumed": n,
        "gate_only_survivors": gp, "fixed_only_survivors": fp,
        "both_or_neither_survive": n - gp - fp,
        "observed_paired_risk_difference": (gp - fp) / n,
        "gate_only_probability_lower_cp": lower_gp,
        "fixed_only_probability_upper_cp": upper_fp,
        "simultaneous_one_sided_lower_bound": lower_gp - upper_fp,
        "alpha_one_sided_total": a,
        "procedure": "BONFERRONI_EXACT_ONE_SIDED_CLOPPER_PEARSON",
        "coverage_if_iid_pairs": "AT_LEAST_1_MINUS_ALPHA",
        "independent_target_world_sampling_verified": False,
        "owner_authorization_inferred": False,
        "scientific_verdict": "NOT_ISSUED",
    }


def simulate_conditional_rejection(*, pairs: int, gate_only_probability: float,
                                   fixed_only_probability: float,
                                   margin: float = DEFAULT_MARGIN_FOR_SENSITIVITY_ONLY,
                                   trials: int = 256, seed: int = 20261109) -> dict:
    """Run a reproducible numerical conditional-power campaign; no Worlds.

    Each synthetic trial samples iid trinary paired outcomes using
    predeclared probabilities. The estimated rejection fraction is
    conditional on this toy *model*, not observed GATE survival evidence.
    """
    n = _count(pairs, "pairs")
    reps = _count(trials, "trials")
    if reps > 10000 or n > 10000:
        raise ValueError("bounded computational sensitivity only")
    if type(seed) is not int:
        raise ValueError("deterministic integer simulation seed required")
    p_plus = _prob(gate_only_probability, "gate_only_probability", zero_ok=True)
    p_minus = _prob(fixed_only_probability, "fixed_only_probability", zero_ok=True)
    if p_plus + p_minus > 1:
        raise ValueError("paired discordance probabilities exceed 1")
    margin_ = _prob(margin, "margin")
    rng = Random(seed)
    rejections = 0
    for _ in range(reps):
        g = f = 0
        for _ in range(n):
            draw = rng.random()
            if draw < p_plus:
                g += 1
            elif draw < p_plus + p_minus:
                f += 1
        lower = exact_paired_lower_bound(pairs=n, gate_only=g, fixed_only=f)[
            "simultaneous_one_sided_lower_bound"]
        rejections += (lower > -margin_)
    rate = rejections / reps
    return {
        "schema": SCHEMA, "status": STATUS,
        "hypothetical_independent_pairs": n,
        "hypothetical_gate_only_probability": p_plus,
        "hypothetical_fixed_only_probability": p_minus,
        "hypothetical_true_mean_difference": p_plus - p_minus,
        "unapproved_loss_margin": margin_,
        "trials": reps, "seed": seed, "threshold_crossings": rejections,
        "conditional_rejection_fraction": rate,
        "monte_carlo_standard_error": sqrt(rate * (1 - rate) / reps),
        "power_or_size_interpretation": (
            "POWER_SENSITIVITY" if p_plus - p_minus > -margin_
            else "NULL_SIZE_DIAGNOSTIC"),
        "iid_world_sampling_proven": False,
        "exact_coverage_experimentally_proven": False,
        "scientific_lives": 0, "worlds_opened": 0,
        "owner_authorization_inferred": False,
        "scientific_verdict": "NOT_ISSUED",
    }


def computational_campaign() -> dict:
    """Fixed scenario grid; user may run on any supported Python version."""
    points = (240, 500, 1000, 1500)
    scenarios = ((0.10, 0.10), (0.15, 0.15), (0.30, 0.30),
                 (0.05, 0.10))
    cells = [simulate_conditional_rejection(
        pairs=n, gate_only_probability=plus, fixed_only_probability=minus,
        trials=256, seed=20261109 + n)
        for n in points for plus, minus in scenarios]
    return {
        "schema": SCHEMA, "status": STATUS,
        "conditions": "PURE_SYNTHETIC_IID_PAIRED_SURVIVAL_DRAWS",
        "no_actual_survival_data_read": True,
        "unapproved_margin": DEFAULT_MARGIN_FOR_SENSITIVITY_ONLY,
        "simulated_cells": cells,
        "dependence_and_new_family_transfer": "NOT_TESTED",
        "admission_or_scientific_execution": False,
    }


def main() -> None:
    import json
    print(json.dumps(computational_campaign(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
