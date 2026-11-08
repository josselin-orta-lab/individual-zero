"""Machine-readable frozen plan for Candidate-I 66/67 DEVELOPMENT.

Importing this module must not import Mind, World, runtime.life or generate any
study condition. 60/61, 62/63 and 64/65 are exposed and closed and are never
acceptance inputs.
"""
from __future__ import annotations

from hashlib import sha256
import json

PROTOCOL = "i3-stage1-candidate-i-development-66-67-v1"
FAMILIES = ("stable", "depletion", "pulse")
INDICES = (66, 67)
GENOME_SEEDS = (907, 908)
POLICIES = (
    "reference",
    "personal_relevance_candidate_h_v1",
    "personal_shared_prior_candidate_i_v1",
    "personal_shared_prior_candidate_i_omega0_ablation_v1",
)
REFERENCE, CANDIDATE_H, CANDIDATE_I, CANDIDATE_I_OMEGA0 = POLICIES
HORIZON = 400
REQUIRED_LIFECYCLE_STRESS_V2_COMMIT = (
    "fbaecde68d6fbcb5a9ec8c6d5908b4b1880137bd"
)


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
                life_seed = 7_510_000 + 1000 * f + 10 * w + g
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
            "FRESH_STAGE1_CANDIDATE_I_DEVELOPMENT_66_67",
        "previous_development":
            "44_65_EXPOSED_OR_CLOSED_NO_REUSE",
        "allocation_basis":
            "P2_DEVELOPMENT_COHORT_0_99_AND_REPOSITORY_COLLISION_SEARCH",
        "required_lifecycle_stress_v2_commit":
            REQUIRED_LIFECYCLE_STRESS_V2_COMMIT,
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
                "relevance_gated_Candidate-H_with_legacy_P1.3_"
                "fallback_addends_and_repaired_lifecycle_custody_v2",
            "candidate_i_native":
                "Candidate-I_shared_prior_native_genome_omega_"
                "with_repaired_lifecycle_custody_v2",
            "candidate_i_omega0":
                "same_genome_Candidate-I_first_contact_omega_zero_"
                "ablation_with_repaired_lifecycle_custody_v2",
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
    "bf1d87a7944b334ca0b4bccff43677c06071d5638ed352a3c1cd045096d77d26"
)


def validate_plan():
    value = plan()
    actual = digest(value)
    if actual != EXPECTED_PLAN_SHA256:
        raise ValueError("frozen Candidate-I 66/67 plan digest mismatch")
    return value


__all__ = [
    "PROTOCOL", "FAMILIES", "INDICES", "GENOME_SEEDS", "POLICIES",
    "REFERENCE", "CANDIDATE_H", "CANDIDATE_I", "CANDIDATE_I_OMEGA0",
    "HORIZON", "REQUIRED_LIFECYCLE_STRESS_V2_COMMIT",
    "EXPECTED_PLAN_SHA256", "canonical", "digest", "plan", "validate_plan",
]
