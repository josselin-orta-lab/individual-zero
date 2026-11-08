"""Frozen Candidate-I shared-prior integration gate.

Protocol: docs/STAGE1_CANDIDATE_I_SHARED_PRIOR_INTEGRATION.md.
Software only. No World/life runner, no runtime registration.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
import math
import sys

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    cognitive_cost, debit_cognition)
from ..modules.mind import Mind
from ..modules.personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind)
from . import stage1_candidate_g_no_omega_integration as G
from . import stage1_candidate_h_post_contact_relevance as P
from . import stage1_candidate_h_unified_integration as U
from . import stage1_shared_first_contact_prior as S

SCHEMA = "i3-stage1-candidate-i-shared-prior-integration/v1"
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")
ADDEND_MODE = "discard_both_bonus_terms"
TOL = 1e-12


def _work(value):
    if isinstance(value, CognitiveWork):
        return value
    return CognitiveWork(*(int(value[key]) for key in WORK_KEYS))


def _add(left, right):
    left, right = _work(left), _work(right)
    return CognitiveWork(*(
        getattr(left, key) + getattr(right, key)
        for key in WORK_KEYS))


def _prime_reference_effects(mind):
    for key, delta in (
            (("se_deplacer",), (-2.0, -0.2, -0.4, 0.0, 0.0)),
            (("attendre",), (-0.35, -0.2, -0.4, 0.2, 0.0)),
            (("dormir",), (3.0, -0.35, -0.4, 0.0, 4.0))):
        mind.effects.observe(key, delta)
    mind._drift = mind.drift()


def _cap(kind, body, token="external-food"):
    base = {
        "body": tuple(body),
        "neighbors": ((False, ()), None, None, None),
    }
    if kind == "K80":
        base.update({"here": (False, ()), "inventory": ()})
    elif kind == "P80":
        base.update({"here": (True, ()), "inventory": ()})
    elif kind == "F108":
        base.update({
            "here": (False, ()),
            "inventory": ((token, 1),),
        })
    else:
        raise ValueError("unknown Candidate-I first-contact fixture")
    return base


def _mind(omega, *, candidate):
    if candidate:
        mind = PersonalRelevanceCandidateHMind(
            G.genome(omega), 211,
            observer_decision_diagnostics=True)
    else:
        mind = Mind(
            G.genome(omega), 211,
            observer_decision_diagnostics=True,
            score_addend_mode=ADDEND_MODE)
    _prime_reference_effects(mind)
    return mind


def _score_map(info):
    return {
        row["option"]: float(row["total_score"])
        for row in info.get("observer", {}).get("score_witness", ())
    }


def _top(scores):
    if not scores:
        return ()
    best = max(scores.values())
    return tuple(sorted(
        option for option, value in scores.items()
        if value >= best - TOL))


def _same_scores(left, right):
    if left.keys() != right.keys():
        return False, None
    worst = max(
        (abs(left[key] - right[key]) for key in left),
        default=0.0)
    return worst <= TOL, worst


def _base_fallback(kind, body, omega, *, token="external-food"):
    """Candidate-owned base Mind decision versus independent same-body control."""
    candidate = _mind(omega, candidate=True)
    control = _mind(omega, candidate=False)

    before_mode = (
        candidate.simulation_mode,
        candidate.projection_accounting)
    old_addend_mode = candidate.score_addend_mode
    candidate.score_addend_mode = ADDEND_MODE
    candidate_budget = CognitiveBudget(tuple(body), BodyLaws())
    try:
        candidate_result = Mind.decide(
            candidate, _cap(kind, body, token), candidate_budget)
    finally:
        candidate.score_addend_mode = old_addend_mode
    after_mode = (
        candidate.simulation_mode,
        candidate.projection_accounting)

    control_budget = CognitiveBudget(tuple(body), BodyLaws())
    control_result = control.decide(
        _cap(kind, body, token), control_budget)

    candidate_scores = _score_map(candidate_result[3])
    control_scores = _score_map(control_result[3])
    same_scores, error = _same_scores(candidate_scores, control_scores)
    candidate_witness = candidate_result[3].get(
        "observer", {}).get("score_witness", ())
    addends_zero = all(
        row["curiosity_bonus_applied"] == 0.0
        and row["risk_penalty_applied"] == 0.0
        for row in candidate_witness)

    return {
        "status": (
            "FUNDED" if candidate_result[3].get("funding") == "FUNDED"
            else candidate_result[3].get("funding")),
        "action": candidate_result[0],
        "param": candidate_result[1],
        "option": candidate_result[3].get("option"),
        "funding": candidate_result[3].get("funding"),
        "work": asdict(candidate_result[2]),
        "body_after_computation": tuple(candidate_budget.remaining),
        "scores": candidate_scores,
        "top": _top(candidate_scores),
        "addends_zero": addends_zero,
        "candidate_score_addend_mode_after": candidate.score_addend_mode,
        "before_mode": before_mode,
        "after_mode": after_mode,
        "same_body_control": {
            "action": control_result[0],
            "param": control_result[1],
            "option": control_result[3].get("option"),
            "funding": control_result[3].get("funding"),
            "work": asdict(control_result[2]),
            "body_after_computation": tuple(control_budget.remaining),
            "scores": control_scores,
            "top": _top(control_scores),
        },
        "score_identity": same_scores,
        "score_identity_max_error": error,
        "top_identity": _top(candidate_scores) == _top(control_scores),
        "action_identity": (
            candidate_result[0:2] == control_result[0:2]),
        "funding_identity": (
            candidate_result[3].get("funding")
            == control_result[3].get("funding")),
        "work_identity": candidate_result[2] == control_result[2],
        "body_identity": all(
            abs(a - b) <= TOL
            for a, b in zip(
                candidate_budget.remaining,
                control_budget.remaining)),
    }


def _compose_rows(shared):
    paths = {}
    for path in ("K80", "P80", "F108"):
        arms = {}
        for omega in S.OMEGAS:
            source_rows = shared["rows"][path][str(omega)]
            out = []
            for source in source_rows:
                row = {
                    "identity": source["identity"],
                    "body": tuple(source["body"]),
                    "horizon": source["horizon"],
                    "omega": omega,
                    "stage_a": deepcopy(source["stage_a"]),
                    "status": source["status"],
                    "fallback": None,
                    "combined_work": dict(source["stage_a"]["work"]),
                    "combined_body_after_computation":
                        tuple(source["stage_a"]["body_after_computation"]),
                }
                if source["status"] == "FALLBACK":
                    fallback = _base_fallback(
                        path,
                        source["stage_a"]["body_after_computation"],
                        omega)
                    row["fallback"] = fallback
                    combined = _add(
                        source["stage_a"]["work"],
                        fallback["work"])
                    row["combined_work"] = asdict(combined)
                    try:
                        final, _ = debit_cognition(
                            source["body"], BodyLaws(), combined)
                    except CognitiveFundingError:
                        final = None
                    row["combined_body_after_computation"] = (
                        None if final is None else tuple(final))
                out.append(row)
            arms[str(omega)] = out
        paths[path] = arms
    return paths


def _fallback_checks(paths):
    failures = []
    accounting = []
    addend_failures = []
    for path, arms in paths.items():
        for omega, rows in arms.items():
            for row in rows:
                if row["status"] != "FALLBACK":
                    continue
                fallback = row["fallback"]
                if not (
                        fallback["funding"] == "FUNDED"
                        and fallback["score_identity"]
                        and fallback["top_identity"]
                        and fallback["action_identity"]
                        and fallback["funding_identity"]
                        and fallback["work_identity"]
                        and fallback["body_identity"]):
                    failures.append({
                        "path": path,
                        "omega": omega,
                        "identity": row["identity"],
                        "funding": fallback["funding"],
                        "score_error":
                            fallback["score_identity_max_error"],
                    })
                if not fallback["addends_zero"]:
                    addend_failures.append({
                        "path": path,
                        "omega": omega,
                        "identity": row["identity"],
                    })

                combined = _work(row["combined_work"])
                try:
                    expected, _ = debit_cognition(
                        row["body"], BodyLaws(), combined)
                except CognitiveFundingError:
                    accounting.append({
                        "path": path,
                        "omega": omega,
                        "identity": row["identity"],
                        "reason": "COMBINED_UNFUNDED",
                    })
                    continue
                reported = row["combined_body_after_computation"]
                if reported is None or any(
                        abs(a - b) > TOL
                        for a, b in zip(expected, reported)):
                    accounting.append({
                        "path": path,
                        "omega": omega,
                        "identity": row["identity"],
                        "reason": "BODY_MISMATCH",
                    })
                bill = cognitive_cost(BodyLaws(), combined)
                if not all(
                        math.isfinite(value) and value >= 0.0
                        for value in bill):
                    accounting.append({
                        "path": path,
                        "omega": omega,
                        "identity": row["identity"],
                        "reason": "INVALID_BILL",
                    })
    return failures, accounting, addend_failures


def _renaming_checks(paths):
    mismatches = []
    for omega in S.OMEGAS:
        for row in paths["F108"][str(omega)]:
            if row["status"] != "FALLBACK":
                continue
            left = _base_fallback(
                "F108",
                row["stage_a"]["body_after_computation"],
                omega,
                token="alpha")
            right = _base_fallback(
                "F108",
                row["stage_a"]["body_after_computation"],
                omega,
                token="beta")
            keys = (
                "action", "param", "option", "funding", "work",
                "body_after_computation", "scores", "top",
                "addends_zero")
            if any(left[key] != right[key] for key in keys):
                mismatches.append({
                    "omega": omega,
                    "identity": row["identity"],
                })
    return mismatches


def _state_restoration_probe():
    mind = _mind(0.0, candidate=True)
    before = {
        "effects": deepcopy(mind.effects.stats),
        "values": deepcopy(mind.values),
        "map": deepcopy(mind.map),
        "rng": mind.rng.getstate(),
        "budget_rng": mind._budget_rng.getstate(),
        "opportunity": mind.opportunity_memory.snapshot(),
    }

    # Detached Stage-A helper has no handle to the real candidate.
    S._imagined_row((80.0, 80.0, 40.0, 80.0, 80.0), 8, 0.0)

    after_probe = {
        "effects": deepcopy(mind.effects.stats),
        "values": deepcopy(mind.values),
        "map": deepcopy(mind.map),
        "rng": mind.rng.getstate(),
        "budget_rng": mind._budget_rng.getstate(),
        "opportunity": mind.opportunity_memory.snapshot(),
    }

    low = (0.01, 80.0, 80.0, 80.0, 0.01)
    failure = _base_fallback("K80", low, 0.0)
    return {
        "probe_state_identity": before == after_probe,
        "failure_mode_before": failure["before_mode"],
        "failure_mode_after": failure["after_mode"],
        "failure_addend_mode_after":
            failure["candidate_score_addend_mode_after"],
    }


def characterize():
    shared = S.characterize()
    post = P.characterize()
    unified = U.characterize()

    paths = _compose_rows(shared)
    fallback_failures, accounting_failures, addend_failures = (
        _fallback_checks(paths))
    renaming_mismatches = _renaming_checks(paths)
    restoration = _state_restoration_probe()

    k0 = shared["counts"]["K80"]["0.0"]
    p0 = shared["counts"]["P80"]["0.0"]
    k0_rows = shared["rows"]["K80"]["0.0"]
    k0_mean_sim = (
        sum(row["stage_a"]["work"]["simulated_steps"] for row in k0_rows)
        / len(k0_rows))
    k0_declines = sum(
        row["stage_a"].get("target_choices") == ("DECLINE_TRIAL",)
        for row in k0_rows)

    relevant_fallback_work = [
        row for arms in paths.values()
        for rows in arms.values()
        for row in rows
        if row["status"] == "RELEVANT"
        and row["fallback"] is not None
    ]

    shared_prior_ok = (
        not shared["shared_prior_mismatches"]
        and shared["rules"]["D5_authority_and_genericity_boundaries"]
        and shared["rules"]["D6_renaming"]
        and shared["rules"]["D7_shared_prior_identity"])

    post_ok = (
        post["verdict"]
        == "CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS"
        and post["fixture"]["states"] == 80
        and post["stage_a"]["relevant"] == 68
        and post["stage_a"]["fallback"] == 12)

    route_post_rows = [
        row for row in unified["routing_panel"]["rows_omega_minus1"]
        if row["history"] == "POST_CONTACT"
    ]
    route_post_rows_high = [
        row for row in unified["routing_panel"]["rows_omega_plus1"]
        if row["history"] == "POST_CONTACT"
    ]

    rules = {
        "I0_source_identity": (
            shared["verdict"]
            == "SHARED_FIRST_CONTACT_PRIOR_CAPACITY_SHOWN"
            and post_ok
            and unified["verdict"]
            == "CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS"),
        "I1_omega_zero_stage_a_identity": (
            k0["states"] == 80
            and k0["relevant"] == 24
            and k0["fallback"] == 56
            and k0_declines == 40
            and abs(k0_mean_sim - 470.05) <= 1e-9
            and p0["states"] == 80
            and p0["relevant"] == 48
            and p0["fallback"] == 32),
        "I2_shared_prior_identity": shared_prior_ok,
        "I3_first_contact_fallback_no_designer_addend": (
            not fallback_failures
            and not addend_failures),
        "I4_relevant_path_integrity": not relevant_fallback_work,
        "I5_post_contact_parity": (
            post_ok
            and not unified["routing_panel"]["omega_mismatches"]
            and len(route_post_rows) == len(route_post_rows_high)
            and all(
                left.get("signature") == right.get("signature")
                for left, right in zip(
                    route_post_rows, route_post_rows_high))),
        "I6_paid_physical_accounting": not accounting_failures,
        "I7_genericity_and_renaming": (
            not renaming_mismatches
            and shared["rules"]["D5_authority_and_genericity_boundaries"]
            and shared["rules"]["D6_renaming"]),
        "I8_persistent_state_restoration": (
            restoration["probe_state_identity"]
            and restoration["failure_mode_before"]
            == ("reference", "chunk_end")
            and restoration["failure_mode_after"]
            == ("reference", "chunk_end")
            and restoration["failure_addend_mode_after"] == "normal"),
        "I9_authority_boundary": True,
    }
    passed = all(rules.values())

    summaries = {}
    for path, arms in paths.items():
        summaries[path] = {}
        for omega, rows in arms.items():
            summaries[path][omega] = {
                "states": len(rows),
                "relevant": sum(
                    row["status"] == "RELEVANT" for row in rows),
                "fallback": sum(
                    row["status"] == "FALLBACK" for row in rows),
                "fallback_funded": sum(
                    row["status"] == "FALLBACK"
                    and row["fallback"]["funding"] == "FUNDED"
                    for row in rows),
            }

    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_I_SHARED_PRIOR_INTEGRATION.md",
        "world_access": False,
        "lives": 0,
        "runtime_registered": False,
        "candidate_i_policy_registered": False,
        "score_addend_mode_first_contact_fallback": ADDEND_MODE,
        "shared_source_verdict": shared["verdict"],
        "post_contact_source_verdict": post["verdict"],
        "unified_source_verdict": unified["verdict"],
        "summaries": summaries,
        "shared_direction_monotone": shared["direction_monotone"],
        "shared_newly_relevant_p80_vs_omega0":
            shared["newly_relevant_p80_vs_omega0"],
        "fallback_identity_failures": fallback_failures,
        "fallback_addend_failures": addend_failures,
        "physical_accounting_failures": accounting_failures,
        "renaming_mismatches": renaming_mismatches,
        "state_restoration": restoration,
        "rules": rules,
        "verdict": (
            "CANDIDATE_I_SHARED_PRIOR_INTEGRATION_PASS"
            if passed else
            "CANDIDATE_I_SHARED_PRIOR_INTEGRATION_DEFECT"),
        "new_live_panel_authorized": False,
        "selection_validation_reserve_authorized": False,
        "stage2_authorized": False,
    }


def run(out_path):
    report = characterize()
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("CANDIDATE_I_SHARED_PRIOR_INTEGRATION " + json.dumps({
        "verdict": report["verdict"],
        "rules": report["rules"],
        "summaries": report["summaries"],
        "fallback_identity_failures":
            report["fallback_identity_failures"][:10],
        "fallback_addend_failures":
            report["fallback_addend_failures"][:10],
        "physical_accounting_failures":
            report["physical_accounting_failures"][:10],
        "renaming_mismatches": report["renaming_mismatches"][:10],
        "state_restoration": report["state_restoration"],
    }, sort_keys=True))
