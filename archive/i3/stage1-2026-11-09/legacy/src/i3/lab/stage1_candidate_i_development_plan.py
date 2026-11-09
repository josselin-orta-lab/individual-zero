"""Machine-readable frozen plan for Candidate-I 60/61 DEVELOPMENT.

Importing this module must not import Mind, World, runtime.life or generate any
study condition. Execution belongs to a later, separately reviewed runner after
the omega=0 runtime ablation exists.
"""
from __future__ import annotations

from hashlib import sha256
import json

PROTOCOL = "i3-stage1-candidate-i-development-60-61-v1"
FAMILIES = ("stable", "depletion", "pulse")
INDICES = (60, 61)
GENOME_SEEDS = (901, 902)
POLICIES = (
    "reference",
    "personal_relevance_candidate_h_v1",
    "personal_shared_prior_candidate_i_v1",
    "personal_shared_prior_candidate_i_omega0_ablation_v1",
)
REFERENCE, CANDIDATE_H, CANDIDATE_I, CANDIDATE_I_OMEGA0 = POLICIES
HORIZON = 400


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def plan():
    cases = []
    for f, family in enumerate(FAMILIES):
        for w, index in enumerate(INDICES):
            for g, genome_seed in enumerate(GENOME_SEEDS):
                block = f"{family}-{index}-g{genome_seed}"
                life_seed = 7_480_000 + 1000 * f + 10 * w + g
                for policy in POLICIES:
                    cases.append({
                        "case": block + ":" + policy,
                        "block": block,
                        "family": family,
                        "cohort": "development",
                        "index": index,
                        "world_seed": 2000 + index,
                        "genome_seed": genome_seed,
                        "life_seed": life_seed,
                        "policy": policy,
                    })
    return {
        "protocol": PROTOCOL,
        "horizon": HORIZON,
        "maximum_steps": HORIZON * len(cases),
        "allocation_contract":
            "FRESH_STAGE1_CANDIDATE_I_DEVELOPMENT_60_61",
        "previous_development":
            "44_59_EXPOSED_OR_CLOSED_NO_REUSE",
        "allocation_basis":
            "P2_DEVELOPMENT_COHORT_0_99_AND_REPOSITORY_COLLISION_SEARCH",
        "cases": cases,
        "scope":
            "CANDIDATE_I_LIVED_ENGINEERING_DEVELOPMENT_NOT_SCIENTIFIC_GATE",
        "failure_rule":
            "STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT",
        "observers": [
            "full_trace", "full_competition", "resource_acquisition",
            "decision_diagnostics", "mind_digest",
        ],
        "primary_question":
            "DOES_RUNNABLE_CANDIDATE_I_EXPRESS_FIRST_CONTACT_OMEGA_IN_"
            "LIVED_MULTI_RESOURCE_CONDITIONS_WITHOUT_WORSENING_"
            "CANDIDATE_H_COGNITIVE_AFFORDABILITY",
        "controls": {
            "reference": "P1.3_original_policy_and_cost",
            "candidate_h":
                "relevance_gated_Candidate-H_with_legacy_P1.3_fallback_addends",
            "candidate_i_native":
                "Candidate-I_shared_prior_native_genome_omega",
            "candidate_i_omega0":
                "same_genome_Candidate-I_first_contact_omega_zero_ablation",
        },
        "engineering_continuation_rules": [
            "J1_native_information_and_base_fallback_routes_both_observed",
            "J2_native_vs_omega0_common_state_first_contact_divergence_gt_0",
            "J3_native_positive_resource_uptakes_gt_0",
            "J4_native_nonfunded_fraction_le_candidate_h",
            "J5_native_processing_collapse_fraction_le_candidate_h",
            "J6_native_paid_energy_per_lived_step_le_candidate_h",
            "J7_native_paid_vigilance_per_lived_step_le_candidate_h",
        ],
        "survival_is_not_a_continuation_rule": True,
        "omega_direction_is_not_a_continuation_rule": True,
        "no_selection_validation_or_reserve": True,
    }


EXPECTED_PLAN_SHA256 = (
    "a8e8dc955a3324e3f78986b4e4de8d8894f8196e1ba7321b89f295016dc1c876"
)


def validate_plan():
    value = plan()
    actual = digest(value)
    if actual != EXPECTED_PLAN_SHA256:
        raise ValueError("frozen Candidate-I 60/61 plan digest mismatch")
    return value


__all__ = [
    "PROTOCOL", "FAMILIES", "INDICES", "GENOME_SEEDS", "POLICIES",
    "REFERENCE", "CANDIDATE_H", "CANDIDATE_I", "CANDIDATE_I_OMEGA0",
    "HORIZON", "EXPECTED_PLAN_SHA256", "canonical", "digest", "plan",
    "validate_plan",
]
