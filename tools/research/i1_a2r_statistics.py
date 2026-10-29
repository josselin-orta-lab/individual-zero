"""Frozen A2-R reward comparison gate, no I1 engine, birth or M11 reader.

Independent inferential units are 24 temperament seeds, never the 96 lives.
The exact sign test assumes independent symmetric seed effects, not randomized
individual trajectories.
"""
from math import comb, isfinite, sqrt
from statistics import mean, stdev

SEEDS = tuple(range(2001, 2025))
ROLES = ("native", "reversed")
HORIZON = 192
MIN_BENEFIT = 0.015
T_CRITICAL_DF23_975 = 2.068657610419041
MAX_ONE_SIDED_SIGN_P = 0.025
MIN_ROLE_POSITIVE_PAIRS = 16
MIN_ROLE_MECHANISM_EXPOSURES = 18


def assess_a2r(pairs):
    """Assess exactly 48 cold-audited canonical-vs-deficit-reward pairs.

    The separate M11 observer must authenticate every provenance flag and
    compute the death-inclusive physiological scores before invoking this gate.
    """
    if type(pairs) is not list or len(pairs) != 2 * len(SEEDS):
        raise ValueError("A2-R requires exactly 48 complete paired records")
    expected = {(role, seed) for role in ROLES for seed in SEEDS}
    indexed = {}
    for item in pairs:
        if type(item) is not dict or item.get("role") not in ROLES or type(item.get("seed")) is not int:
            raise ValueError("invalid A2-R role or seed")
        key = (item["role"], item["seed"])
        if key not in expected or key in indexed:
            raise ValueError("duplicate or non-preregistered A2-R pair")
        for field in ("canonical_score", "candidate_score"):
            value = item.get(field)
            if type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 1:
                raise ValueError("invalid A2-R physiological score: " + field)
        for field in (
            "canonical_dead", "candidate_dead", "cold_m11_verified",
            "reward_modes_verified", "pre_reward_prefix_equal",
            "reward_difference_observed", "mechanism_exposed",
        ):
            if type(item.get(field)) is not bool:
                raise ValueError("invalid A2-R provenance or observation flag: " + field)
        if not (item["cold_m11_verified"] and item["reward_modes_verified"]
                and item["pre_reward_prefix_equal"]):
            raise ValueError("A2-R incomplete M11, intervention or birth parity")
        if item["mechanism_exposed"] and not item["reward_difference_observed"]:
            raise ValueError("A2-R motor mediation without a reward intervention")
        indexed[key] = item
    if set(indexed) != expected:
        raise ValueError("A2-R missing preregistered seed or role")

    by_role = {}
    for role in ROLES:
        records = [indexed[(role, seed)] for seed in SEEDS]
        differences = [r["canonical_score"] - r["candidate_score"] for r in records]
        by_role[role] = {
            "mean_canonical_minus_candidate": mean(differences),
            "positive_pairs": sum(d > 0 for d in differences),
            "reward_exposed_pairs": sum(r["reward_difference_observed"] for r in records),
            "mechanism_exposed_pairs": sum(r["mechanism_exposed"] for r in records),
            "canonical_deaths_by_horizon": sum(r["canonical_dead"] for r in records),
            "candidate_deaths_by_horizon": sum(r["candidate_dead"] for r in records),
        }
    effects = [
        ((indexed[("native", seed)]["canonical_score"] -
          indexed[("native", seed)]["candidate_score"]) +
         (indexed[("reversed", seed)]["canonical_score"] -
          indexed[("reversed", seed)]["candidate_score"])) / 2
        for seed in SEEDS
    ]
    avg = mean(effects)
    standard_error = stdev(effects) / sqrt(len(SEEDS))
    positives = sum(d > 0 for d in effects)
    # Exact binomial tail; ties conservatively count as nonpositive.
    p_sign = sum(comb(len(SEEDS), k) for k in range(positives, len(SEEDS) + 1)) / (2 ** len(SEEDS))
    exposed = all(
        by_role[role]["mechanism_exposed_pairs"] >= MIN_ROLE_MECHANISM_EXPOSURES
        and by_role[role]["reward_exposed_pairs"] >= MIN_ROLE_MECHANISM_EXPOSURES
        for role in ROLES
    )
    role_robust = all(
        by_role[role]["mean_canonical_minus_candidate"] > 0
        and by_role[role]["positive_pairs"] >= MIN_ROLE_POSITIVE_PAIRS
        for role in ROLES
    )
    safety = all(
        by_role[role]["candidate_deaths_by_horizon"]
        <= by_role[role]["canonical_deaths_by_horizon"]
        for role in ROLES
    )
    ci_low = avg - T_CRITICAL_DF23_975 * standard_error
    ci_high = avg + T_CRITICAL_DF23_975 * standard_error
    signal = avg >= MIN_BENEFIT and ci_low > 0 and p_sign <= MAX_ONE_SIDED_SIGN_P
    verdict = (
        "NOT_EXPOSED" if not exposed else
        "NO_GO" if not (signal and role_robust and safety) else
        "CONFIRMATORY_TARGETED_SIGNAL_PENDING_REVIEW"
    )
    return {
        "schema": "individual-zero-i1-a2r-frozen-reward-statistics/1",
        "horizon": HORIZON, "lives": 96,
        "paired_comparisons": len(pairs),
        "independent_temperament_blocks": len(SEEDS),
        "mean_canonical_minus_candidate": avg,
        "block_effects_by_seed": {str(seed): effects[i] for i, seed in enumerate(SEEDS)},
        "block_t95_ci_lower": ci_low,
        "block_t95_ci_upper": ci_high,
        "independent_positive_blocks": positives,
        "exact_one_sided_block_sign_test_p": p_sign,
        "sign_test_assumption": "independent_symmetric_seed_signs_not_randomized_96_lives",
        "by_role": by_role, "role_robust": role_robust,
        "safety_no_extra_deaths_per_role": safety,
        "mechanism_exposed": exposed, "targeted_status": verdict,
        "human_scientific_review_required": True,
        "general_L3": "NOT_ESTABLISHED", "historical_A1C_status": "NO_GO",
    }
