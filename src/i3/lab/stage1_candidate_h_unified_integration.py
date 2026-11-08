"""Frozen unified Candidate-H software-integration gate.

Protocol: docs/STAGE1_CANDIDATE_H_UNIFIED_INTEGRATION.md.
No World, life, runtime registration or evidence access.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
import sys

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, debit_cognition)
from ..modules.mind import Mind
from ..modules.opportunity_recurrence import OpportunityRecurrenceMemory
from ..modules.personal_recurrence_candidate_g_mind import (
    PersonalRecurrenceCandidateGMind)
from ..modules.personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind,
    first_contact_relevant_fields,
    post_contact_relevant_scores)
from . import stage1_candidate_g_no_omega_integration as G
from . import stage1_candidate_g_reference_recurrence_falsifier as R
from . import stage1_candidate_h_relevance_fallback as H1
from . import stage1_candidate_h_post_contact_relevance as H2

SCHEMA = "i3-stage1-candidate-h-unified-integration/v1"
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")
HISTORY_MODES = ("NO_SUPPORT", "FIRST_CONTACT_SUPPORT", "POST_CONTACT")
OMEGA_ARMS = (-1.0, 1.0)


class RecurrenceReadForbidden(OpportunityRecurrenceMemory):
    """Tripwire proving post-contact routing never consults recurrence."""

    def estimate(self, *args, **kwargs):
        raise RuntimeError("POST_CONTACT_RECURRENCE_READ_FORBIDDEN")


def _work(value):
    if isinstance(value, CognitiveWork):
        return value
    return CognitiveWork(*(int(value[key]) for key in WORK_KEYS))


def _add(left, right):
    left, right = _work(left), _work(right)
    return CognitiveWork(*(
        getattr(left, key) + getattr(right, key) for key in WORK_KEYS))


def _body_grid():
    rows = []
    for channel, name in enumerate(R.CHANNEL_NAMES):
        for level in R.LEVELS:
            body = list(R.BASE_BODY)
            body[channel] = level
            rows.append({
                "channel": name,
                "channel_index": channel,
                "level": level,
                "body": tuple(body),
            })
    return tuple(rows)


def _make_mind(omega, history):
    mind = PersonalRelevanceCandidateHMind(
        G.genome(omega), 211,
        observer_decision_diagnostics=True)
    G.prime_generic(mind)
    if history == "FIRST_CONTACT_SUPPORT":
        G.prime_recurrence(mind)
    elif history == "POST_CONTACT":
        G.prime_personal_drink(mind)
        # The memory exists as an explicit tripwire. Any estimate() call fails.
        mind.opportunity_memory = RecurrenceReadForbidden()
    elif history != "NO_SUPPORT":
        raise ValueError("unknown frozen Candidate-H history mode")
    return mind


def _signature(result):
    action, param, work, info = result
    return {
        "action": action,
        "param": param,
        "work": asdict(work),
        "funding": info.get("funding"),
        "option": info.get("option"),
        "route": info.get("candidate_h_route"),
        "relevance": info.get("candidate_h_relevance"),
        "probe_phase": info.get("candidate_h_probe_phase"),
        "decision_projection_mode":
            info.get("decision_projection_mode"),
        "stage_a_work": info.get("candidate_h_stage_a_work"),
        "stage_b_work": info.get("candidate_h_stage_b_work"),
        "stage_a_body_after":
            info.get("candidate_h_stage_a_body_after"),
        "body_after": info.get("candidate_h_body_after_cognition"),
    }


def _fallback_control(omega, history, body):
    """Independently recompute Stage A then exact same-body P1.3 Stage B."""
    mind = _make_mind(omega, history)
    cap = G.cap(body)
    probe_budget = CognitiveBudget(body, BodyLaws())
    stage_a = mind._probe(cap, probe_budget)
    if not stage_a["complete"] or stage_a["relevant"]:
        return None
    post = probe_budget.remaining
    final_budget = CognitiveBudget(post, BodyLaws())
    final = Mind.decide(
        mind, mind._cap_with_body(cap, post), final_budget)
    return {
        "action": final[0],
        "param": final[1],
        "funding": final[3].get("funding"),
        "option": final[3].get("option"),
        "score_witness": final[3].get(
            "observer", {}).get("score_witness", ()),
        "work": asdict(final_budget.work),
        "body_after": final_budget.remaining,
    }


def _first_contact_parity():
    source = H1.characterize()
    mismatches = []
    relevant = fallback = 0
    for row in source["rows"]:
        probe = row["probe"]
        predicted = first_contact_relevant_fields(
            probe["target_choices"],
            probe["information_value"],
            probe["trial_advantage"])
        relevant += predicted
        fallback += not predicted
        if predicted != row["relevant"]:
            mismatches.append({
                "channel": row["channel"],
                "level": row["level"],
                "horizon": row["horizon"],
                "expected": row["relevant"],
                "observed": predicted,
            })
    return {
        "states": len(source["rows"]),
        "relevant": relevant,
        "fallback": fallback,
        "mismatches": mismatches,
        "source_verdict": source["verdict"],
    }


def _post_contact_parity():
    source = H2.characterize()
    mismatches = []
    relevant = fallback = 0
    for row in source["rows"]:
        stage = row["stage_a"]
        positive = (
            (H2.EXPLORER,)
            if stage["information"]["information_value"] > H2.TOL
            else ())
        predicted = post_contact_relevant_scores(
            stage["with_information_scores"],
            stage["without_information_scores"],
            positive)
        relevant += predicted
        fallback += not predicted
        if predicted != row["relevant"]:
            mismatches.append({
                "channel": row["channel"],
                "level": row["level"],
                "horizon": row["horizon"],
                "expected": row["relevant"],
                "observed": predicted,
            })
    return {
        "states": len(source["rows"]),
        "relevant": relevant,
        "fallback": fallback,
        "mismatches": mismatches,
        "source_verdict": source["verdict"],
    }


def _run_panel(omega):
    rows = []
    for identity in _body_grid():
        body = identity["body"]
        for history in HISTORY_MODES:
            mind = _make_mind(omega, history)
            cap = G.cap(body)
            before = (
                mind.simulation_mode, mind.projection_accounting)
            try:
                result = mind.decide(
                    cap, CognitiveBudget(body, BodyLaws()))
                error = None
            except Exception as exc:
                result = None
                error = {
                    "type": type(exc).__name__,
                    "message": str(exc),
                }
            after = (
                mind.simulation_mode, mind.projection_accounting)

            row = {
                **identity,
                "history": history,
                "omega": omega,
                "before_mode": before,
                "after_mode": after,
                "error": error,
            }
            if result is not None:
                sig = _signature(result)
                row["signature"] = sig
                row["reference_control"] = (
                    _fallback_control(omega, history, body)
                    if sig["route"] == "P1.3_FINAL"
                    else None)

                stage_a = _work(sig["stage_a_work"])
                stage_b = _work(sig["stage_b_work"])
                total = _work(sig["work"])
                row["phase_work_exact"] = (
                    _add(stage_a, stage_b) == total)
                try:
                    settled, _ = debit_cognition(
                        body, BodyLaws(), total)
                    row["body_settlement_max_abs_gap"] = max(
                        abs(a - b)
                        for a, b in zip(settled, sig["body_after"]))
                    row["body_settlement_exact"] = (
                        row["body_settlement_max_abs_gap"] <= 1e-12)
                except Exception as exc:
                    row["body_settlement_exact"] = False
                    row["settlement_error"] = (
                        type(exc).__name__ + ": " + str(exc))

                witnesses = result[3].get(
                    "observer", {}).get("score_witness", ())
                if sig["route"] == "CANDIDATE_F_FINAL":
                    row["candidate_geometry_all"] = (
                        bool(witnesses)
                        and all(
                            witness.get("decision_projection_mode")
                            == "candidate_f"
                            for witness in witnesses))
                else:
                    row["candidate_geometry_all"] = None

                control = row["reference_control"]
                if control is not None:
                    row["fallback_identity"] = (
                        sig["action"] == control["action"]
                        and sig["param"] == control["param"]
                        and sig["funding"] == control["funding"]
                        and sig["option"] == control["option"]
                        and tuple(witnesses)
                        == tuple(control["score_witness"])
                        and sig["stage_b_work"] == control["work"]
                        and tuple(sig["body_after"])
                        == tuple(control["body_after"]))
                else:
                    row["fallback_identity"] = None
            rows.append(row)
    return rows


def _panel_signature_map(rows):
    return {
        (row["channel_index"], row["level"], row["history"]):
            row.get("signature")
        for row in rows
    }


def characterize():
    first = _first_contact_parity()
    post = _post_contact_parity()
    low = _run_panel(-1.0)
    high = _run_panel(1.0)

    low_map = _panel_signature_map(low)
    high_map = _panel_signature_map(high)
    omega_mismatches = [
        {
            "channel_index": key[0],
            "level": key[1],
            "history": key[2],
        }
        for key in low_map
        if low_map[key] != high_map[key]
    ]

    complete = [row for row in low if row["error"] is None]
    errors = [row for row in low if row["error"] is not None]
    routes = {
        "NO_SUPPORT_REFERENCE": any(
            row.get("signature", {}).get("route") == "P1.3_FINAL"
            and row["history"] == "NO_SUPPORT"
            for row in complete),
        "FIRST_CONTACT_FALLBACK": any(
            row.get("signature", {}).get("route") == "P1.3_FINAL"
            and row["history"] == "FIRST_CONTACT_SUPPORT"
            for row in complete),
        "FIRST_CONTACT_RELEVANT": any(
            row.get("signature", {}).get("route") == "CANDIDATE_F_FINAL"
            and row["history"] == "FIRST_CONTACT_SUPPORT"
            for row in complete),
        "POST_CONTACT_FALLBACK": any(
            row.get("signature", {}).get("route") == "P1.3_FINAL"
            and row["history"] == "POST_CONTACT"
            for row in complete),
        "POST_CONTACT_RELEVANT": any(
            row.get("signature", {}).get("route") == "CANDIDATE_F_FINAL"
            and row["history"] == "POST_CONTACT"
            for row in complete),
    }

    fallback_rows = [
        row for row in complete
        if row.get("signature", {}).get("route") == "P1.3_FINAL"]
    relevant_rows = [
        row for row in complete
        if row.get("signature", {}).get("route")
        == "CANDIDATE_F_FINAL"]

    # Explicit forced-funding-failure restoration fixture.
    failure_body = (0.01, 80.0, 80.0, 80.0, 0.01)
    failure_mind = _make_mind(0.0, "FIRST_CONTACT_SUPPORT")
    failure_result = failure_mind.decide(
        G.cap(failure_body),
        CognitiveBudget(failure_body, BodyLaws()))
    forced_failure = {
        "funding": failure_result[3].get("funding"),
        "route": failure_result[3].get("candidate_h_route"),
        "mode_after": (
            failure_mind.simulation_mode,
            failure_mind.projection_accounting),
    }

    rules = {
        "U0_authority_boundary":
            first["source_verdict"]
            == "CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_PASS"
            and post["source_verdict"]
            == "CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS",
        "U1_first_contact_classifier_parity":
            first["states"] == 80
            and first["relevant"] == 24
            and first["fallback"] == 56
            and not first["mismatches"],
        "U2_post_contact_classifier_parity":
            post["states"] == 80
            and post["relevant"] == 68
            and post["fallback"] == 12
            and not post["mismatches"],
        "U3_fallback_final_policy_identity":
            bool(fallback_rows)
            and all(row["fallback_identity"] for row in fallback_rows),
        "U4_relevant_final_policy_integrity":
            bool(relevant_rows)
            and all(row["candidate_geometry_all"] for row in relevant_rows),
        "U5_phase_accounting":
            not errors
            and all(
                row["phase_work_exact"]
                and row["body_settlement_exact"]
                for row in complete),
        "U6_persistent_mode_restoration":
            all(
                row["before_mode"] == ("reference", "chunk_end")
                and row["after_mode"] == ("reference", "chunk_end")
                for row in complete)
            and forced_failure["mode_after"]
            == ("reference", "chunk_end"),
        "U7_information_source_and_omega_separation":
            not omega_mismatches,
        "U8_all_frozen_routes_observed":
            all(routes.values()),
        "U9_output_authority": True,
    }
    passed = all(rules.values())

    route_counts = {}
    probe_unfunded = 0
    for row in complete:
        sig = row["signature"]
        route = sig["route"]
        route_counts[route] = route_counts.get(route, 0) + 1
        probe_unfunded += route == "PROBE_UNFUNDED"

    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_H_UNIFIED_INTEGRATION.md",
        "world_access": False,
        "lives": 0,
        "evidence_branch_access": False,
        "runtime_registered": False,
        "omega_read": False,
        "first_contact_parity": first,
        "post_contact_parity": post,
        "routing_panel": {
            "decisions_per_omega": len(low),
            "history_modes": HISTORY_MODES,
            "omega_arms": OMEGA_ARMS,
            "errors": errors,
            "route_counts_omega_minus1": route_counts,
            "probe_unfunded_omega_minus1": probe_unfunded,
            "routes_observed": routes,
            "omega_mismatches": omega_mismatches,
            "rows_omega_minus1": low,
            "rows_omega_plus1": high,
        },
        "forced_failure": forced_failure,
        "rules": rules,
        "verdict": (
            "CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS"
            if passed else
            "CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_FAIL"),
        "future_development_protocol_authorized": passed,
        "runtime_registration_authorized": False,
        "new_live_panel_authorized": False,
        "selection_validation_reserve_authorized": False,
    }


def run(out_path):
    report = characterize()
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("CANDIDATE_H_UNIFIED_INTEGRATION " + json.dumps({
        "verdict": report["verdict"],
        "first_contact_parity": report["first_contact_parity"],
        "post_contact_parity": report["post_contact_parity"],
        "routing_panel": {
            "decisions_per_omega":
                report["routing_panel"]["decisions_per_omega"],
            "errors": report["routing_panel"]["errors"],
            "route_counts_omega_minus1":
                report["routing_panel"]["route_counts_omega_minus1"],
            "probe_unfunded_omega_minus1":
                report["routing_panel"]["probe_unfunded_omega_minus1"],
            "routes_observed":
                report["routing_panel"]["routes_observed"],
            "omega_mismatches":
                report["routing_panel"]["omega_mismatches"],
        },
        "forced_failure": report["forced_failure"],
        "rules": report["rules"],
    }, sort_keys=True))
