"""Frozen A1-C decision rule over 12 independent birth-temperament blocks.

Pure analysis. No I1 engine, M11, GitHub, files or wall-clock access.
This is *not* a stochastic-run p-value: the sign-flip is a model-based
symmetry sensitivity check for the deterministically paired seed blocks.
"""
from itertools import product
from math import isfinite, sqrt
from statistics import mean, stdev

SEEDS = tuple(range(101, 113))
ROLES = ("native", "reversed")
MIN_MEAN_BENEFIT = 0.0100
T_CRITICAL_DF11_975 = 2.200985160082949
MAX_ONE_SIDED_SIGN_FLIP_P = 0.025
MIN_ROLE_POSITIVE_PAIRS = 8
MIN_ROLE_MECHANISM_EXPOSURES = 9


def assess_a1c(pairs):
    """Return preregistered acceptance; never silently discard weak pairs.

    pairs: exactly 24 dict records with role, seed, difference (masked−canonical
    normalized deficit), and mechanism_exposed (M11/Stage8/Competition/motor).
    """
    if type(pairs) is not list:
        raise ValueError("A1-C requires a complete list of 24 pairs")
    expected = {(role, seed) for role in ROLES for seed in SEEDS}
    indexed = {}
    for p in pairs:
        if (type(p) is not dict or p.get("role") not in ROLES
                or type(p.get("seed")) is not int
                or type(p.get("difference")) not in (int, float)
                or not isfinite(p["difference"])
                or not -1 <= p["difference"] <= 1
                or type(p.get("mechanism_exposed")) is not bool):
            raise ValueError("invalid A1-C score or exposure record")
        key = (p["role"], p["seed"])
        if key in indexed or key not in expected:
            raise ValueError("duplicated or non-preregistered A1-C pair")
        indexed[key] = p
    if set(indexed) != expected:
        raise ValueError("A1-C cannot select or drop a paired seed")
    roles = {
        role: {
            "mean": mean(indexed[(role, seed)]["difference"] for seed in SEEDS),
            "positive_pairs": sum(indexed[(role, seed)]["difference"] > 0
                                  for seed in SEEDS),
            "mechanism_exposed_pairs": sum(
                indexed[(role, seed)]["mechanism_exposed"] for seed in SEEDS),
        } for role in ROLES
    }
    block_effects = [
        (indexed[("native", seed)]["difference"]
         + indexed[("reversed", seed)]["difference"]) / 2
        for seed in SEEDS
    ]
    average = mean(block_effects)
    se = stdev(block_effects) / sqrt(len(SEEDS))
    ci_low = average - T_CRITICAL_DF11_975 * se
    ci_high = average + T_CRITICAL_DF11_975 * se
    # Exact enumeration over 12 temperament blocks, not 24 pseudo-independent
    # roles and not 48 independent individual lives.
    observed_sum = sum(block_effects)
    upper_count = sum(
        sum(v * sign for v, sign in zip(block_effects, signs))
        >= observed_sum - 1e-12
        for signs in product((-1, 1), repeat=len(SEEDS))
    )
    p_value = upper_count / 4096
    mechanism = all(
        roles[role]["mechanism_exposed_pairs"]
        >= MIN_ROLE_MECHANISM_EXPOSURES for role in ROLES)
    role_robust = all(
        roles[role]["mean"] > 0 and
        roles[role]["positive_pairs"] >= MIN_ROLE_POSITIVE_PAIRS
        for role in ROLES)
    positive = (average >= MIN_MEAN_BENEFIT
                and ci_low > 0
                and p_value <= MAX_ONE_SIDED_SIGN_FLIP_P)
    result = (
        "NOT_EXPOSED" if not mechanism else
        "NO_GO" if not (role_robust and positive) else
        "CONFIRMATORY_TARGETED_SIGNAL_PENDING_REVIEW"
    )
    return {
        "schema": "individual-zero-i1-eco-a1c-frozen-statistics/1",
        "independent_temperament_blocks": len(SEEDS),
        "paired_comparisons": len(pairs),
        "mean_masked_minus_canonical": average,
        "block_effects_by_seed": {
            str(s): block_effects[i] for i, s in enumerate(SEEDS)},
        "block_standard_error": se,
        "t95_ci_lower": ci_low,
        "t95_ci_upper": ci_high,
        "exact_one_sided_block_signflip_p": p_value,
        "signflip_null_assumption": "symmetric_seed_block_effects_not_design_randomization",
        "by_role": roles,
        "all_preregistered_gates_passed": result == "CONFIRMATORY_TARGETED_SIGNAL_PENDING_REVIEW",
        "targeted_status": result,
        "human_scientific_review_required": True,
        "general_L3": "NOT_ESTABLISHED",
        "pilot_lives_included": False,
    }
