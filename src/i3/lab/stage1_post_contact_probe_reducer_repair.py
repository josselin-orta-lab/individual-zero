"""Frozen software gate for Candidate-I post-contact Candidate-H probe reduction.

Protocol: docs/STAGE1_POST_CONTACT_PROBE_REDUCER_REPAIR.md.
No World, life runner, P2 ecology or exposed evidence is accessed.
"""
from __future__ import annotations

from copy import deepcopy
import json
import sys

from . import stage0_revision as revision
from . import stage1_composite_funding_reducer_repair as composite
from . import stage1_multiphase_processing_reducer_repair as multiphase

SCHEMA = "i3-stage1-post-contact-probe-reducer-repair/v1"
I_POLICY = "personal_shared_prior_candidate_i_v1"


def _post_probe(nested):
    if nested == "NO_FUNDED_SCORE":
        a = dict(multiphase.A)
        outcome = "no_funded_score"
    elif nested == "NO_PROCESSING_BUDGET":
        a = dict(multiphase.ZERO)
        outcome = "no_processing_budget"
    else:
        a = dict(multiphase.A)
        outcome = revision.FUNDING.get(nested, "no_funded_score")
    life = multiphase._set_i_post(
        multiphase._life(I_POLICY),
        a=a,
        b=dict(multiphase.ZERO),
        public=revision.COMPOSITE_RELEVANCE_PROBE_FUNDING,
        outcome=outcome,
        action=None)
    info = life["trace"][0]["info"]
    info["candidate_h_route"] = "PROBE_UNFUNDED"
    info["candidate_h_probe_funding"] = nested
    return life


def _direct_h_probe(nested):
    if nested == "NO_FUNDED_SCORE":
        a = dict(multiphase.A)
        outcome = "no_funded_score"
    elif nested == "NO_PROCESSING_BUDGET":
        a = dict(multiphase.ZERO)
        outcome = "no_processing_budget"
    else:
        a = dict(multiphase.A)
        outcome = revision.FUNDING.get(nested, "no_funded_score")
    life = multiphase._set_h(
        multiphase._life(revision.CANDIDATE_H_POLICY),
        a=a,
        b=dict(multiphase.ZERO),
        route="PROBE_UNFUNDED",
        public=revision.COMPOSITE_RELEVANCE_PROBE_FUNDING,
        outcome=outcome,
        action=None)
    life["trace"][0]["info"]["candidate_h_probe_funding"] = nested
    return life


def _post_complete(route):
    life = multiphase._set_i_post(
        multiphase._life(I_POLICY),
        a=dict(multiphase.A),
        b=dict(multiphase.B),
        public="FUNDED",
        outcome="action_admitted",
        action="attendre")
    life["trace"][0]["info"]["candidate_h_route"] = route
    return life


def _processing_work(life):
    row = life["trace"][0]
    total = row["funding_phases"]["decision"]["work"]
    return revision._processing_work(life, row, total)


def _accept(life):
    try:
        joined = revision._resource_events(life)
    except ValueError:
        return False, None
    return True, joined[0]


def _reject(life):
    try:
        revision._resource_events(life)
    except ValueError:
        return True
    return False


def _legacy_post_contact_error(life):
    """Reproduce the exact pre-Q repair post-contact predicate."""
    info = life["trace"][0]["info"]
    route = info.get("candidate_i_route")
    if route != "POST_CONTACT_CANDIDATE_H":
        return None
    if (
            info.get("candidate_i_first_contact_omega_used") is not False
            or info.get("candidate_i_post_contact_source")
            != "CANDIDATE_H_1163_UNCHANGED"
            or info.get("candidate_h_route") not in revision._H_COMPLETE_ROUTES
            or info.get("candidate_h_probe_funding")
            not in revision._COMPLETE_H_PROBE_FUNDING):
        try:
            raise ValueError(
                "invalid Candidate-I post-contact processing receipt")
        except ValueError as exc:
            return {
                "type": type(exc).__name__,
                "message": str(exc),
            }
    return None


def _set_nonzero_stage_b(life):
    x = deepcopy(life)
    info = x["trace"][0]["info"]
    info["candidate_h_stage_b_work"] = dict(multiphase.B)
    total = multiphase._add(
        info["candidate_h_stage_a_work"], info["candidate_h_stage_b_work"])
    info["candidate_h_total_work"] = dict(total)
    multiphase._set_total(x, total)
    return x


def characterize():
    post_score = _post_probe("NO_FUNDED_SCORE")
    post_zero = _post_probe("NO_PROCESSING_BUDGET")
    score_ok, score_row = _accept(post_score)
    zero_ok, zero_row = _accept(post_zero)

    score_owner = _processing_work(post_score)
    zero_owner = _processing_work(post_zero)

    post_p13 = _post_complete("P1.3_FINAL")
    post_cf = _post_complete("CANDIDATE_F_FINAL")
    p13_ok, p13_row = _accept(post_p13)
    cf_ok, cf_row = _accept(post_cf)

    direct_score = _direct_h_probe("NO_FUNDED_SCORE")
    direct_zero = _direct_h_probe("NO_PROCESSING_BUDGET")
    dhs_ok, dhs_row = _accept(direct_score)
    dhz_ok, dhz_row = _accept(direct_zero)

    direct_complete = multiphase._set_h(
        multiphase._life(revision.CANDIDATE_H_POLICY),
        a=dict(multiphase.A),
        b=dict(multiphase.B),
        route="P1.3_FINAL",
        public="FUNDED",
        outcome="action_admitted",
        action="attendre")
    dhc_ok, dhc_row = _accept(direct_complete)

    invalid = {}

    x = _post_probe("FUNDED")
    x["trace"][0]["info"]["observer"]["decision_outcome"] = "action_admitted"
    x["observer_resource_acquisition"]["steps"][0][
        "decision_outcome"] = "action_admitted"
    invalid["probe_unfunded_complete_nested_funding"] = _reject(x)

    invalid["probe_unfunded_nonzero_stage_b"] = _reject(
        _set_nonzero_stage_b(post_score))

    x = deepcopy(post_score)
    x["trace"][0]["info"]["candidate_h_total_work"]["cycles"] += 1
    invalid["nested_total_mismatch"] = _reject(x)

    x = deepcopy(post_score)
    x["trace"][0]["info"]["candidate_h_body_after_cognition"][0] += 1.0
    invalid["nested_body_mismatch"] = _reject(x)

    x = deepcopy(post_score)
    x["trace"][0]["info"]["candidate_i_first_contact_omega_used"] = True
    invalid["post_contact_omega_used"] = _reject(x)

    x = deepcopy(post_score)
    x["trace"][0]["info"]["candidate_i_post_contact_source"] = "OTHER"
    invalid["post_contact_source_mismatch"] = _reject(x)

    x = deepcopy(post_score)
    x["trace"][0]["info"]["candidate_h_route"] = "UNKNOWN_FINAL"
    invalid["unknown_nested_h_route"] = _reject(x)

    x = deepcopy(post_score)
    x["observer_resource_acquisition"]["steps"][0][
        "decision_outcome"] = "no_processing_budget"
    invalid["public_observer_disagreement"] = _reject(x)

    legacy = _legacy_post_contact_error(post_score)
    composite_report = composite.characterize()
    multiphase_report = multiphase.characterize()

    from . import stage1_candidate_i_lifecycle_custody_stress_v2 as stress_v2
    stress_report = stress_v2.characterize()

    complete_owner_identity = (
        _processing_work(post_p13)
        == post_p13["trace"][0]["info"]["candidate_h_stage_b_work"]
        and _processing_work(post_cf)
        == post_cf["trace"][0]["info"]["candidate_h_stage_b_work"]
    )
    direct_owner_identity = (
        _processing_work(direct_score)
        == direct_score["trace"][0]["info"]["candidate_h_stage_a_work"]
        and _processing_work(direct_zero)
        == direct_zero["trace"][0]["info"]["candidate_h_stage_a_work"]
        and _processing_work(direct_complete)
        == direct_complete["trace"][0]["info"]["candidate_h_stage_b_work"]
    )

    rules = {
        "Q0_custody":
            (multiphase_report["verdict"]
             == "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS"
             and stress_report["verdict"]
             == "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_PASS"),
        "Q1_exact_synthetic_reproduction":
            (legacy == {
                "type": "ValueError",
                "message":
                    "invalid Candidate-I post-contact processing receipt"}),
        "Q2_post_contact_nested_no_funded_score":
            (score_ok and score_row["processing_paid"]
             and score_owner
             == post_score["trace"][0]["info"]["candidate_h_stage_a_work"]
             and not any(
                 post_score["trace"][0]["info"][
                     "candidate_h_stage_b_work"].values())
             and post_score["trace"][0]["action"] is None),
        "Q3_post_contact_nested_no_processing_budget":
            (zero_ok and not zero_row["processing_paid"]
             and not any(zero_owner.values())
             and not any(
                 post_zero["trace"][0]["info"][
                     "candidate_h_stage_b_work"].values())
             and post_zero["trace"][0]["action"] is None),
        "Q4_complete_post_contact_candidate_h_identity":
            (p13_ok and cf_ok
             and p13_row["processing_paid"]
             and cf_row["processing_paid"]
             and complete_owner_identity),
        "Q5_direct_candidate_h_identity":
            (dhs_ok and dhz_ok and dhc_ok
             and dhs_row["processing_paid"]
             and not dhz_row["processing_paid"]
             and dhc_row["processing_paid"]
             and direct_owner_identity),
        "Q6_strict_nested_phase_authentication":
            all(invalid[key] for key in (
                "probe_unfunded_complete_nested_funding",
                "probe_unfunded_nonzero_stage_b",
                "nested_total_mismatch",
                "nested_body_mismatch")),
        "Q7_candidate_i_authority_boundary":
            all(invalid[key] for key in (
                "post_contact_omega_used",
                "post_contact_source_mismatch",
                "unknown_nested_h_route")),
        "Q8_funding_observer_and_historical_regressions":
            (invalid["public_observer_disagreement"]
             and composite_report["verdict"]
             == "COMPOSITE_FUNDING_REDUCER_REPAIR_PASS"
             and multiphase_report["verdict"]
             == "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS"
             and stress_report["verdict"]
             == "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_PASS"),
        "Q9_authority_boundary": True,
    }
    passed = all(rules.values())
    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_POST_CONTACT_PROBE_REDUCER_REPAIR.md",
        "world_access": False,
        "runtime_life_access": False,
        "p2_ecology_access": False,
        "evidence_branch_access": False,
        "lives": 0,
        "legacy_reproduction": legacy,
        "accepted": {
            "post_contact_probe_no_funded_score": score_ok,
            "post_contact_probe_no_processing_budget": zero_ok,
            "post_contact_p13_final": p13_ok,
            "post_contact_candidate_f_final": cf_ok,
            "direct_h_probe_no_funded_score": dhs_ok,
            "direct_h_probe_no_processing_budget": dhz_ok,
            "direct_h_complete": dhc_ok,
        },
        "invalid_rejections": invalid,
        "prerequisites": {
            "composite": composite_report["verdict"],
            "multiphase": multiphase_report["verdict"],
            "lifecycle_v2": stress_report["verdict"],
        },
        "rules": rules,
        "verdict": (
            "POST_CONTACT_PROBE_REDUCER_REPAIR_PASS"
            if passed else
            "POST_CONTACT_PROBE_REDUCER_REPAIR_DEFECT"),
        "66_67_retry_authorized": False,
        "retroactive_66_67_admission_authorized": False,
        "J1_J7_verdict_authorized": False,
        "new_live_panel_authorized": False,
    }


def run(path):
    report = characterize()
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("POST_CONTACT_PROBE_REDUCER_REPAIR " + json.dumps({
        "verdict": report["verdict"],
        "rules": report["rules"],
        "accepted": report["accepted"],
        "invalid_rejections": report["invalid_rejections"],
    }, sort_keys=True))
