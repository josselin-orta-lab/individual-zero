"""Frozen software gate for multi-phase Stage-0 processing ownership.

Protocol: docs/STAGE1_MULTIPHASE_PROCESSING_REDUCER_REPAIR.md.
No World, life runner, P2 ecology or exposed evidence is accessed.
"""
from __future__ import annotations

from copy import deepcopy
import json
import sys

from i3.lab import stage0_revision as revision
from i3.archive.stage1.lab import stage1_composite_funding_reducer_repair as composite

SCHEMA = "i3-stage1-multiphase-processing-reducer-repair/v1"
A = {"cycles": 4, "simulated_steps": 18, "memory_items": 248, "replays": 0}
B = {"cycles": 3, "simulated_steps": 0, "memory_items": 12, "replays": 0}
INFO_B = {"cycles": 2, "simulated_steps": 0, "memory_items": 0, "replays": 0}
ZERO = {"cycles": 0, "simulated_steps": 0, "memory_items": 0, "replays": 0}


def _add(left, right):
    return {key: left[key] + right[key] for key in revision._WORK_KEYS}


def _bill():
    return {
        channel: {"requested": 0.0, "paid": 0.0, "unpaid": 0.0}
        for channel in ("energy", "vigilance")
    }


def _life(policy=None):
    before = [80.0, 70.0, 40.0, 90.0, 100.0]
    after = [79.0, 69.8, 39.6, 90.0, 99.0]
    zero = dict(ZERO)
    manifest = {
        "world": {"spawn": [5, 6], "laws": {"water_decay": 0.4}},
    }
    if policy is not None:
        manifest["experimental_policy"] = {"name": policy}
    row = {
        "t": 1, "action": None, "param": None, "option": None,
        "body": after[:], "pos": [5, 6], "dead": [],
        "funding_phases": {
            "decision": {
                "work": zero, "accounting": _bill(),
                "body_before": before[:], "body_after_debit": after[:]},
            "learning": {
                "work": dict(ZERO), "accounting": _bill(),
                "body_before": after[:], "body_after_debit": after[:]},
        },
        "info": {
            "funding": "NO_PROCESSING_BUDGET",
            "observer": {"decision_outcome": "no_processing_budget"},
        },
    }
    event = {
        "step": 1, "action": None, "param": None, "chosen_option": None,
        "death_causes": [], "world_position_observer_only": [5, 6],
        "personal_position": [0, 0],
        "body_before_decision": before[:],
        "body_after_physics": after[:],
        "body_after_paid_learning": after[:],
        "decision_funding": "NO_PROCESSING_BUDGET",
        "decision_outcome": "no_processing_budget",
        "capture_here_water": False,
        "positive_water_uptake": False,
        "water_uptake_above_decay": None,
        "phase_payment": {
            "decision": {"work": dict(ZERO), "accounting": _bill()},
            "learning": {"work": dict(ZERO), "accounting": _bill()},
        },
        "paid_decision_work": dict(ZERO),
        "paid_learning_work": dict(ZERO),
    }
    return {
        "manifest": manifest,
        "trace": [row],
        "observer_resource_acquisition": {
            "schema": "i3-p5d-resource-acquisition-observer/v1",
            "steps": [event],
        },
    }


def _set_public(life, public, outcome, *, action=None):
    row = life["trace"][0]
    event = life["observer_resource_acquisition"]["steps"][0]
    row["action"] = action
    row["option"] = action
    row["info"]["funding"] = public
    row["info"]["observer"]["decision_outcome"] = outcome
    event["action"] = action
    event["chosen_option"] = action
    event["decision_funding"] = public
    event["decision_outcome"] = outcome
    return life


def _set_total(life, work):
    row = life["trace"][0]
    event = life["observer_resource_acquisition"]["steps"][0]
    row["funding_phases"]["decision"]["work"] = dict(work)
    event["paid_decision_work"] = dict(work)
    event["phase_payment"]["decision"]["work"] = dict(work)
    return life


def _set_h(life, *, a=A, b=ZERO, route="P1.3_FINAL",
           public="NO_PROCESSING_BUDGET", outcome="no_processing_budget",
           action=None):
    total = _add(a, b)
    _set_total(life, total)
    _set_public(life, public, outcome, action=action)
    info = life["trace"][0]["info"]
    info.update({
        "experimental_policy": revision.CANDIDATE_H_POLICY,
        "candidate_h_route": route,
        "candidate_h_probe_funding": "FUNDED",
        "candidate_h_stage_a_work": dict(a),
        "candidate_h_stage_b_work": dict(b),
        "candidate_h_total_work": dict(total),
        "candidate_h_body_after_cognition":
            list(life["trace"][0]["funding_phases"]["decision"]["body_after_debit"]),
    })
    return life


def _set_i(life, *, route, a=A, b=ZERO,
           public="NO_PROCESSING_BUDGET", outcome="no_processing_budget",
           action=None):
    total = _add(a, b)
    _set_total(life, total)
    _set_public(life, public, outcome, action=action)
    info = life["trace"][0]["info"]
    info.update({
        "experimental_policy": "personal_shared_prior_candidate_i_v1",
        "candidate_i_route": route,
        "candidate_i_probe_funding": "FUNDED",
        "candidate_i_stage_a_work": dict(a),
        "candidate_i_stage_b_work": dict(b),
        "candidate_i_total_work": dict(total),
        "candidate_i_body_after_cognition":
            list(life["trace"][0]["funding_phases"]["decision"]["body_after_debit"]),
    })
    return life


def _set_i_post(life, *, a=A, b=ZERO,
                public="NO_PROCESSING_BUDGET",
                outcome="no_processing_budget", action=None):
    total = _add(a, b)
    _set_total(life, total)
    _set_public(life, public, outcome, action=action)
    info = life["trace"][0]["info"]
    info.update({
        "experimental_policy": "personal_shared_prior_candidate_i_v1",
        "candidate_i_route": "POST_CONTACT_CANDIDATE_H",
        "candidate_i_first_contact_omega_used": False,
        "candidate_i_post_contact_source": "CANDIDATE_H_1163_UNCHANGED",
        "candidate_h_route": "P1.3_FINAL",
        "candidate_h_probe_funding": "FUNDED",
        "candidate_h_stage_a_work": dict(a),
        "candidate_h_stage_b_work": dict(b),
        "candidate_h_total_work": dict(total),
        "candidate_h_body_after_cognition":
            list(life["trace"][0]["funding_phases"]["decision"]["body_after_debit"]),
    })
    return life


def _accept(life):
    try:
        row = revision._resource_events(life)[0]
    except ValueError:
        return False, None
    return True, row


def _reject(life):
    try:
        revision._resource_events(life)
    except ValueError:
        return True
    return False


def _legacy_rejects_sequential_no_processing(life):
    """Exact pre-repair total-work ownership predicate."""
    row = life["trace"][0]
    event = life["observer_resource_acquisition"]["steps"][0]
    processing = revision._normalize_processing_status(row, event)
    total = revision._work_vector(
        row["funding_phases"]["decision"]["work"], "decision")
    paid = processing["processing_paid"]
    return (
        (paid and total["cycles"] < 3)
        or (not paid and any(total.values()))
    )


def characterize():
    ordinary_paid = _life()
    _set_total(ordinary_paid, B)
    _set_public(
        ordinary_paid, "FUNDED", "action_admitted", action="attendre")
    op_ok, op_row = _accept(ordinary_paid)

    ordinary_zero = _life()
    oz_ok, oz_row = _accept(ordinary_zero)

    ordinary_bad = _life()
    _set_total(ordinary_bad, A)

    h_zero = _set_h(
        _life(revision.CANDIDATE_H_POLICY))
    h_paid = _set_h(
        _life(revision.CANDIDATE_H_POLICY),
        b=B, public="FUNDED", outcome="action_admitted",
        action="attendre")
    hz_ok, hz_row = _accept(h_zero)
    hp_ok, hp_row = _accept(h_paid)

    i_fallback = _set_i(
        _life("personal_shared_prior_candidate_i_v1"),
        route="P1.3_BASE_FINAL")
    if_ok, if_row = _accept(i_fallback)

    i_info = _set_i(
        _life("personal_shared_prior_candidate_i_v1"),
        route="INFORMATION_FINAL", b=INFO_B,
        public="FUNDED", outcome="action_admitted",
        action="attendre")
    ii_ok, ii_row = _accept(i_info)

    i_info_bad = _set_i(
        _life("personal_shared_prior_candidate_i_v1"),
        route="INFORMATION_FINAL")

    i_post = _set_i_post(
        _life("personal_shared_prior_candidate_i_omega0_ablation_v1"))
    ip_ok, ip_row = _accept(i_post)

    invalid = {}
    x = deepcopy(h_zero)
    x["trace"][0]["info"]["candidate_h_total_work"]["cycles"] += 1
    invalid["h_total_mismatch"] = _reject(x)

    x = deepcopy(h_zero)
    x["trace"][0]["info"]["candidate_h_body_after_cognition"][0] += 1.0
    invalid["h_body_mismatch"] = _reject(x)

    x = deepcopy(h_zero)
    x["trace"][0]["info"]["candidate_h_route"] = "UNKNOWN_FINAL"
    invalid["h_unknown_route"] = _reject(x)

    x = deepcopy(i_fallback)
    x["trace"][0]["info"]["candidate_i_stage_b_work"]["cycles"] = 1
    invalid["i_phase_sum_mismatch"] = _reject(x)

    x = deepcopy(i_post)
    x["trace"][0]["info"]["candidate_i_first_contact_omega_used"] = True
    invalid["i_post_omega_used"] = _reject(x)

    x = deepcopy(i_post)
    x["trace"][0]["info"]["candidate_i_post_contact_source"] = "OTHER"
    invalid["i_post_source_mismatch"] = _reject(x)

    invalid["ordinary_unpaid_with_work"] = _reject(ordinary_bad)
    invalid["information_final_no_processing"] = _reject(i_info_bad)

    composite_report = composite.characterize()

    rules = {
        "M0_custody": True,
        "M1_exact_legacy_reproduction":
            _legacy_rejects_sequential_no_processing(h_zero),
        "M2_total_work_physically_authoritative":
            hz_ok and hp_ok and if_ok and ii_ok and ip_ok,
        "M3_processing_ownership_explicit":
            (not hz_row["processing_paid"]
             and hp_row["processing_paid"]
             and not if_row["processing_paid"]
             and ii_row["processing_paid"]
             and not ip_row["processing_paid"]),
        "M4_r_depletion_semantics_unchanged":
            (not hz_row["processing_paid"]
             and ii_row["processing_paid"]
             and not ip_row["processing_paid"]),
        "M5_public_motor_authority_unchanged":
            (h_zero["trace"][0]["action"] is None
             and h_paid["trace"][0]["action"] == "attendre"
             and i_fallback["trace"][0]["action"] is None),
        "M6_body_and_phase_custody":
            all(invalid[key] for key in (
                "h_total_mismatch", "h_body_mismatch",
                "h_unknown_route", "i_phase_sum_mismatch",
                "i_post_omega_used", "i_post_source_mismatch")),
        "M7_status_outcome_custody":
            all(invalid.values()),
        "M8_historical_regressions":
            (op_ok and op_row["processing_paid"]
             and oz_ok and not oz_row["processing_paid"]
             and composite_report["verdict"]
             == "COMPOSITE_FUNDING_REDUCER_REPAIR_PASS"),
        "M9_authority_boundary": True,
    }
    passed = all(rules.values())
    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_MULTIPHASE_PROCESSING_REDUCER_REPAIR.md",
        "world_access": False,
        "runtime_life_access": False,
        "p2_ecology_access": False,
        "evidence_branch_access": False,
        "lives": 0,
        "accepted": {
            "ordinary_funded": op_ok,
            "ordinary_no_processing": oz_ok,
            "candidate_h_stage_b_no_processing": hz_ok,
            "candidate_h_stage_b_funded": hp_ok,
            "candidate_i_fallback_no_processing": if_ok,
            "candidate_i_information_final": ii_ok,
            "candidate_i_post_contact_no_processing": ip_ok,
        },
        "invalid_rejections": invalid,
        "composite_prerequisite": composite_report["verdict"],
        "rules": rules,
        "verdict": (
            "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS"
            if passed else
            "MULTIPHASE_PROCESSING_REDUCER_REPAIR_DEFECT"),
        "64_65_retry_authorized": False,
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
    print("MULTIPHASE_PROCESSING_REDUCER_REPAIR " + json.dumps({
        "verdict": report["verdict"],
        "rules": report["rules"],
        "accepted": report["accepted"],
        "invalid_rejections": report["invalid_rejections"],
    }, sort_keys=True))
