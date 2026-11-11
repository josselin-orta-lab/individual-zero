"""No-World decision-boundary audit of already-PUBLISHED Stage-2 summaries.

Prospectively frozen methods exercise:
docs/studies/stage2-replay-gate-selected-design/
POST_E3_INFERENCE_DECISION_ENVELOPE_PREFLIGHT_2026-11-11.md

No original bytes are reverified in this computation, no populations
are combined, and no scientifically accepted NI margin or iid ecological
claim is inferred. The exact finite-sample method is REUSED, not refit.
"""
from __future__ import annotations

from hashlib import sha256
from math import expm1, isfinite, log
from pathlib import Path
import json

from .stage2_exact_paired_survival import exact_paired_lower_bound

SCHEMA = "i3-stage2.1-post-e3-conditional-inference-no-scientific-go/v1"
ALPHA_SENSITIVITY_ONLY = 0.05
UNAPPROVED_NI_MARGIN = 0.05
B1_PUBLISHED_CONDITIONAL_LOWER = -0.04325164695153383
REFERENCE = "P1.3 funded-v2"
REPORT_ROOT = "src/i3/docs/studies/stage2-replay-gate-selected-design"

# These are immutable REPORT aggregates, not newly ingested original lives.
# Four distinct designs, no cross-study ecological exchangeability assumption.
HISTORICAL = (
    {
        "id": "b1-gate-fixed-96",
        "source": "B1_EXPLORATORY_DEVELOPMENT_RESULTS_2026-11-10.md",
        "source_commit": "50380d16b0b6e7ac1e91702060be83784ba85cc7",
        "treatment": "GATE",
        "control": "FIXED",
        "pairs": 96, "treatment_only": 13, "control_only": 5,
        "both": 25, "neither": 53,
        "treatment_survivors": 38, "control_survivors": 30,
        "intervention": "FULL_GATED_POLICY_VS_FIXED",
        "extra_causal_information_control": False,
    },
    {
        "id": "three-arm-gate-paid-random-64",
        "source": "THREE_ARM_EXPLORATORY_RESULTS_2026-11-10.md",
        "source_commit": "aaff20234b8a4f9d11595d6eb852371d0ce00f97",
        "treatment": "GATE",
        "control": "PAID_RANDOM_SCHEDULED_COUNT",
        "pairs": 64, "treatment_only": 4, "control_only": 4,
        "both": 23, "neither": 33,
        "treatment_survivors": 27, "control_survivors": 27,
        "intervention": "GATE_VS_RANDOM_POLICY_NOT_REALIZED_COUNT_MATCH",
        "extra_causal_information_control": False,
    },
    {
        "id": "content-priority-random-48",
        "source": "CONTENT_48_EXPLORATORY_RESULTS_2026-11-10.md",
        "source_commit": "459d0d9f90ea8edae95881d4e3110b91a24f85f5",
        "treatment": "TD_PRIORITY_REPLAY_CONTENT",
        "control": "RANDOM_REPLAY_CONTENT",
        "pairs": 48, "treatment_only": 1, "control_only": 7,
        "both": 16, "neither": 24,
        "treatment_survivors": 17, "control_survivors": 23,
        "intervention": "PAID_MEMORY_CONTENT_IDENTITY_NOT_READOUT_VISIBILITY",
        "extra_causal_information_control": False,
    },
    {
        "id": "next-decision-priority-random-24",
        "source": "NEXT_DECISION_24_RESULTS_2026-11-10.md",
        "source_commit": "20ca7efbf7797fa7b1f12983ce68906b754b312c",
        "treatment": "TD_PRIORITY_REPLAY_CONTENT",
        "control": "RANDOM_REPLAY_CONTENT",
        "pairs": 24, "treatment_only": 2, "control_only": 3,
        "both": 10, "neither": 9,
        "treatment_survivors": 12, "control_survivors": 13,
        "intervention": "FULL_LIVES_AND_ONE_DETACHED_ALTERNATE_NEXT_MOTOR",
        "extra_causal_information_control": False,
    },
)

REQUIRED_NEW_EVIDENCE = (
    "genuinely_delivered_personal_signal",
    "new_information_changed_born_native_action",
    "following_factual_body_and_post_paid_learning",
    "complete_model_and_host_cost",
    "independently_attested_target_ecology",
    "biologically_accepted_survival_NI_margin",
    "external_independent_methods_review",
    "new_source_scoped_original_world_authority",
)


def _sha(payload):
    return sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _check_report_row(row):
    """Reject partial/reclassified cohort data, never fill missing pairs."""
    keys = ("pairs", "treatment_only", "control_only", "both", "neither",
            "treatment_survivors", "control_survivors")
    if any(type(row.get(x)) is not int or row[x] < 0 for x in keys):
        raise ValueError("invalid/missing finite complete matched-pair counts")
    n = row["pairs"]
    if not n or any(
        row[k] > n for k in keys if k != "pairs"
    ):
        raise ValueError("invalid matched denominator")
    t, c, b, neither = (
        row["treatment_only"], row["control_only"], row["both"],
        row["neither"],
    )
    if t + c + b + neither != n:
        raise ValueError("incomplete or overlapping assigned outcome categories")
    if b + t != row["treatment_survivors"]:
        raise ValueError("treatment horizon survivors misreconstructed")
    if b + c != row["control_survivors"]:
        raise ValueError("control horizon survivors misreconstructed")
    if (not row.get("source", "").endswith(".md")
            or type(row.get("source_commit")) is not str
            or len(row["source_commit"]) != 40):
        raise ValueError("missing pinned published-source provenance")
    if row.get("extra_causal_information_control") is not False:
        raise ValueError("old full-policy comparisons relabeled as new readout")
    return n, t, c


def _conditional_old_row(row):
    n, plus, minus = _check_report_row(row)
    bound = exact_paired_lower_bound(
        pairs=n, gate_only=plus, fixed_only=minus,
        alpha=ALPHA_SENSITIVITY_ONLY,
    )
    if (bound["scientific_verdict"] != "NOT_ISSUED"
            or bound["independent_target_world_sampling_verified"] is not False
            or bound["owner_authorization_inferred"] is not False):
        raise AssertionError("reused conditional statistic overstated its authority")
    return {
        **row,
        "finite_paired_risk_difference": (plus - minus) / n,
        "one_sided_95pct_lower_if_iid": (
            bound["simultaneous_one_sided_lower_bound"]),
        "confidence_valid_for_original_ecology": False,
        "scientific_NI_claim_authorized": False,
        "native_extra_information_delivery_proven": False,
        "statistics_condition": "HYPOTHETICAL_IID_PAIRED_SAMPLING_ONLY",
    }


def _zero_iid_upper_sensitivity(*, success_count, unique_cases, alpha):
    """Only the 0-event closed-form iid-binomial sensitivity (not inference).

    E1 has 24 comparisons but only 12 distinct frozen source-form states:
    never interpret comparisons as independent cluster samples.
    """
    if (type(success_count) is not int or success_count != 0
            or type(unique_cases) is not int or unique_cases <= 0
            or type(alpha) not in (int, float) or not isfinite(alpha)
            or not 0 < alpha < 1):
        raise ValueError("strict 0/n finite hypothetical Bernoulli sensitivity")
    upper = -expm1(log(alpha) / unique_cases)
    return {
        "observed_event_count": success_count,
        "unique_fixed_software_cases": unique_cases,
        "hypothetical_one_sided_95pct_upper_if_iid": upper,
        "iid_source_sampling_verified": False,
        "ecological_confidence_bound_claim": False,
    }


def _manifest_fails_closed():
    """The historical science permission remains a hard external boundary."""
    manifest = json.loads((
        Path(__file__).resolve().parents[1] / "ACTIVE_SURFACE.json"
    ).read_text(encoding="utf-8"))
    g = manifest["governance"]
    if (manifest["current_stage"] != "2.1 replay gate"
            or manifest["reference"] != REFERENCE
            or manifest["canonical_status"] != "REPLAY_GATE_CAPACITY_SHOWN"
            or any(g[key] is not False for key in (
                "i3_registered", "fresh_lived_worlds_allowed",
                "next_scientific_cohort_authorized",
                "scientific_gate_authorized",
            ))):
        raise ValueError(
            "manifest stage/World authority changed; reclassify, do not claim GO"
        )
    return True


def audit():
    _manifest_fails_closed()
    rows = [_conditional_old_row(row) for row in HISTORICAL]
    if len({r["id"] for r in rows}) != len(rows):
        raise AssertionError("duplicate independent study label")
    if len({r["source_commit"] for r in rows}) != len(rows):
        raise AssertionError("reused original source under different old study")
    if abs(rows[0]["one_sided_95pct_lower_if_iid"]
           - B1_PUBLISHED_CONDITIONAL_LOWER) > 1e-10:
        raise AssertionError("B1 conditional lower not reproduced")
    # Deliberately demonstrates why a favorable conditional numerical gate
    # is NOT valid scientific NI from this DEVELOPMENT source.
    illustration_passes_number_only = (
        rows[0]["one_sided_95pct_lower_if_iid"]
        > -UNAPPROVED_NI_MARGIN
    )
    if not illustration_passes_number_only:
        raise AssertionError("frozen false-GO counterexample did not hold")
    if any(x["scientific_NI_claim_authorized"] for x in rows):
        raise AssertionError("no historical DEVELOPMENT NI is authorized")

    e3 = _zero_iid_upper_sensitivity(
        success_count=0, unique_cases=2, alpha=ALPHA_SENSITIVITY_ONLY
    )
    e1 = _zero_iid_upper_sensitivity(
        success_count=0, unique_cases=12, alpha=ALPHA_SENSITIVITY_ONLY
    )
    report = {
        "schema": SCHEMA,
        "source_kind": "PUBLISHED_FIXED_AGGREGATES_NO_ORIGINAL_REAUDIT",
        "old_studies_distinct_not_pooled": len(rows),
        "total_historical_lives_reexecuted": 0,
        "new_Worlds": 0, "new_scientific_lives": 0,
        "history": rows,
        "b1_hypothetical_5pp_NI_numerical_threshold_pass": (
            illustration_passes_number_only),
        "b1_5pp_margin_scientifically_accepted": False,
        "b1_independent_iid_ecology_attested": False,
        "b1_independent_methods_review_pass": False,
        "b1_NI_scientific_claim_authorized": False,
        "e3_native_score_change_in_informed_fixed_shapes": 1,
        "e3_native_admitted_motor_changes": 0,
        "e3": {
            **e3, "histories": 2, "no_support_control": 1,
            "actual_born_world_outcome": False,
            "frozen_source_candidate_closed_negative": True,
        },
        "e1": {
            **e1, "two_depth_comparisons_per_unique_case": 2,
            "total_correlated_depth_comparisons": 24,
            "changed_score_vectors": 3,
            "changed_motors": 0,
        },
        "next_decision_24_detached_alternate_motor": 1,
        "next_decision_24_different_alternate_motors_executed_in_World": 0,
        "required_new_causal_evidence": {x: False for x in REQUIRED_NEW_EVIDENCE},
        "stop_this_exact_E3_candidate": True,
        "general_thinking_useless_demonstrated": False,
        "general_thinking_useful_demonstrated": False,
        "full_scientific_stage2_closed": False,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False, "stage2_3_go": False,
        "engine_registration": False,
        "methods_disposition": "NO_VERDICT_ON_GENERAL_ADAPTIVE_THINKING",
        "bounded_candidate_verdict": "E3_FROZEN_CANDIDATE_NEGATIVE",
        "next_operation": (
            "INDEPENDENT_SCOPED_METHODS_REVIEW_OR_DISTINCT_SOURCE_JUSTIFIED_MECHANISM"
        ),
    }
    return {**report, "aggregate_sha256": _sha(report)}


if __name__ == "__main__":
    print("I3_STAGE2_POST_E3_INFERENCE_ENVELOPE=" + json.dumps(
        audit(), sort_keys=True, separators=(",", ":"), allow_nan=False
    ))
