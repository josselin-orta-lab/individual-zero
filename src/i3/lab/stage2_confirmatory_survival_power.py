"""Prospective survival non-inferiority *power planning*, never a World runner.

Two calculations with deliberately separate scientific status:
1. Distribution-free one-sided Hoeffding coverage / guaranteed power if
   truly independent bounded paired survival contrasts are available.
2. A much smaller *normal approximation* under a hypothetical paired
   (GATE-only survival, FIXED-only survival, tie) distribution. It does
   not inherit exact error control from (1), and cannot justify exposure.

Nothing here samples source/genomes/Worlds, assigns an authorized arm,
reads held-out outcomes, computes an actual scientific gate or changes
the frozen P1.3 / replay policy. Margin and sampling frame are NOT approved.
"""
from __future__ import annotations

from math import ceil, isfinite, log, sqrt
from statistics import NormalDist
from typing import Any

from . import stage0_design as F0

SCHEMA = "i3-stage2-1-survival-confirmatory-power-sensitivity/v1"
STATUS = "SOFTWARE_ONLY_PROSPECTIVE_SENSITIVITY_NO_SCIENTIFIC_EXPOSURE"
ALPHA = 0.05
DESIRED_POWER = 0.80
HORIZON = F0.HORIZON


def _prob(x, name: str, *, inclusive_zero: bool = False) -> float:
    if type(x) not in (int, float) or not isfinite(x):
        raise ValueError(f"{name} must be a finite real number")
    if not (0 <= x < 1 if inclusive_zero else 0 < x < 1):
        raise ValueError(f"{name} must be a probability")
    return float(x)


def _effect(x: float) -> float:
    if type(x) not in (int, float) or not isfinite(x) or not -1 <= x <= 1:
        raise ValueError("assumed survival difference must be finite and in [-1,+1]")
    return float(x)


def one_sided_bounded_radius(independent_clusters: int, *,
                             alpha: float = ALPHA) -> float:
    """P(mu < sample_mean - radius) <= alpha, conditional on independence.

    Independent per-cluster D in [-1,1]. mu is the average of E[D_i].
    To generalize to a population average requires a justified sampling
    frame as well, NOT merely independent pseudo-random integer seeds.
    """
    if type(independent_clusters) is not int or independent_clusters <= 0:
        raise ValueError("positive integer count of independent clusters required")
    a = _prob(alpha, "alpha")
    return sqrt(2 * log(1 / a) / independent_clusters)


def bounded_power_requirement(*, margin: float, assumed_true_delta: float,
                              alpha: float = ALPHA,
                              power: float = DESIRED_POWER) -> dict[str, Any]:
    """Guaranteed >= power, if true E[D] >= assumed_true_delta.

    H0: E[D] <= -margin; H1: E[D] > -margin.
    With D = 1 (only GATE survived), -1 (only FIXED survived), 0 (tie),
    using a one-sided Hoeffding lower confidence bound.
    Since D in [-1,1], bounded power >= 1-beta follows when

      n >= 2*(sqrt(log(1/alpha))+sqrt(log(1/beta)))**2
           / (assumed_true_delta + margin)**2.

    This is very conservative but explicit distribution-free arithmetic.
    NO actual independence, margin, model or cohort is authorized here.
    """
    m = _prob(margin, "margin")
    alt = _effect(assumed_true_delta)
    a = _prob(alpha, "alpha")
    power_ = _prob(power, "power")
    if alt + m <= 0:
        raise ValueError("true effect does not exceed the non-inferiority null")
    n = ceil(2 * (sqrt(log(1 / a)) + sqrt(log(1 / (1 - power_))))**2
             / (alt + m)**2)
    return {
        "margin_survival_probability": m,
        "assumed_true_gate_minus_fixed": alt,
        "alpha_one_sided": a,
        "target_power": power_,
        "minimum_independent_clusters_for_hoeffding_power_bound": n,
        "two_policy_life_ceiling": 2 * n,
        "two_policy_horizon_steps_ceiling": 2 * n * HORIZON,
        "interpretation": "CONDITIONAL_DISTRIBUTION_FREE_BOUND_NOT_APPROVED_SAMPLE_SIZE",
        "independence_proven": False,
        "margin_approved": False,
        "worlds_authorized": False,
    }


def paired_normal_sensitivity(*, gate_only_survival: float,
                              fixed_only_survival: float,
                              margin: float, alpha: float = ALPHA,
                              power: float = DESIRED_POWER) -> dict[str, Any]:
    """Illustrative *asymptotic* pairs required under assumed trinary D.

    D = +1 if only GATE survives, -1 if only FIXED survives and 0
    otherwise. Var(D) = p+ + p- - (p+ - p-)**2.
    A normal-approximation size under fixed variance has NO exact
    one-sided coverage or power guarantee and MUST NOT drive admissions.
    """
    gp = _prob(gate_only_survival, "gate_only_survival", inclusive_zero=True)
    fp = _prob(fixed_only_survival, "fixed_only_survival", inclusive_zero=True)
    if gp + fp > 1:
        raise ValueError("paired discordance probabilities exceed one")
    m = _prob(margin, "margin")
    a = _prob(alpha, "alpha")
    power_ = _prob(power, "power")
    mu = gp - fp
    variance = gp + fp - mu * mu
    if mu + m <= 0:
        required = None
        status = "UNDER_OR_AT_NULL_UNSUITABLE_FOR_TARGET_POWER"
    elif variance == 0:
        required = None
        status = "DEGENERATE_ASSUMPTION_NO_NORMAL_APPROXIMATION"
    else:
        z = NormalDist().inv_cdf(1 - a) + NormalDist().inv_cdf(power_)
        required = ceil((z * z * variance) / ((mu + m) ** 2))
        status = "ILLUSTRATIVE_NORMAL_APPROXIMATION_ONLY"
    return {
        "assumed_gate_only_horizon_survival": gp,
        "assumed_fixed_only_horizon_survival": fp,
        "assumed_survival_tie_probability": 1 - gp - fp,
        "assumed_mean_gate_minus_fixed": mu,
        "assumed_pair_variance": variance,
        "margin": m,
        "alpha_one_sided": a,
        "target_power": power_,
        "approximate_independent_pairs": required,
        "status": status,
        "exact_type_i_control_established": False,
        "model_assumptions_verified": False,
        "admission_authorized": False,
    }


def sensitivity_campaign() -> dict[str, Any]:
    """Launch a *software-only* sensitivity study with fixed visible grid."""
    assumed_margins = (0.02, 0.05, 0.10)
    effects = (0.0, 0.02, 0.05)
    robust = [
        bounded_power_requirement(margin=m, assumed_true_delta=e)
        for m in assumed_margins for e in effects
    ]
    paired = [
        paired_normal_sensitivity(
            gate_only_survival=plus, fixed_only_survival=minus,
            margin=0.05)
        for plus, minus in ((0.10, 0.10), (0.15, 0.15),
                            (0.30, 0.30), (0.11, 0.09), (0.05, 0.10))
    ]
    f0_blocks = len(F0.world_rows("validation")) * F0.KEEP
    f0_worlds = len(F0.world_rows("validation"))
    # These are NOT independent samples. Their counts are included only
    # to show why no inference can be promoted by counting dependent lives.
    return {
        "schema": SCHEMA, "status": STATUS,
        "primary_proposed_estimand": (
            "expected_survival_at_step_400_G0_same_world_GATE_minus_FIXED"
        ),
        "survival_outcome": {
            "gate_only_survived": 1, "fixed_only_survived": -1,
            "both_or_neither_survived": 0,
            "death_at_step_400": "DEATH_NOT_SURVIVAL",
            "missing_or_structurally_invalid": "NO_VERDICT_NO_IMPUTATION",
        },
        "hypothesis": "H0_mu_at_most_minus_margin_vs_H1_mu_greater_minus_margin",
        "primary_margin_approved": False,
        "independent_target_population_specified": False,
        "meaningful_random_sampling_established": False,
        "historical_80_81_reused": False,
        "f0_candidate_worlds": f0_worlds,
        "f0_candidate_matched_blocks": f0_blocks,
        "f0_blocks_independent_for_inference": "NOT_ESTABLISHED",
        "existing_f0_indices_sufficient_for_robust_study": False,
        "world_source_or_indices_authorized": False,
        "conservative_fixed_sample_sensitivity": robust,
        "paired_model_assumption_sensitivity": paired,
        "primary_interpretation": (
            "NO_ADOPTION_OR_CONFIRMATORY_TEST_WITHOUT_INDEPENDENCE_MARGIN_SOURCE_"
            "CUSTODY_PREREGISTRATION_AND_OWNER_APPROVAL"
        ),
        "future_world_exposure": 0,
        "future_scientific_lives_executed": 0,
        "scientific_verdict": "NOT_ISSUED",
    }


def main() -> None:
    import json
    print(json.dumps(sensitivity_campaign(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
