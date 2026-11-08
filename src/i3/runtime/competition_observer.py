"""External P5e full-option competition witness, never fed to Mind.

Only copies the existing funded option-score/competition evidence emitted in
the original decision loop. No replay, prediction, RNG, admission or cognition
bill is introduced by this observer.
"""
from __future__ import annotations

from math import isfinite


def _frontier_score(entry):
    """Authenticate the explicit Stage-1 frontier score schema only."""
    value = entry.get("information_value")
    if (type(value) not in (int, float) or isinstance(value, bool) or
            not isfinite(value)):
        raise RuntimeError("P5e: invalid frontier information value")
    for name in (
            "curiosity_bonus_computed", "curiosity_bonus_applied",
            "risk_penalty_computed", "risk_penalty_applied"):
        if entry.get(name) != 0.0:
            raise RuntimeError(
                "P5e: frontier score must not contain historical addends")
    return entry["base_return"] + value


def capture_competition(*, info, action, param, work, allowed, capture):
    diagnostic = info["observer"]
    witness = diagnostic["score_witness"]
    if len(witness) != diagnostic["scored_options"]:
        raise RuntimeError("P5e: count of paid scores is inconsistent")
    if work != allowed.work:
        raise RuntimeError("P5e: decision work does not match paid allowance")
    names = [entry["option"] for entry in witness]
    if len(set(names)) != len(names):
        raise RuntimeError("P5e: duplicate paid option")
    for entry in witness:
        if entry.get("score_kind") in (
                "frontier_water_expected_distress",
                "first_contact_information_expected_distress"):
            expected = _frontier_score(entry)
        else:
            # Historical P1.3 and local-information witnesses keep their
            # original identity. In particular local_information_v1 records
            # information_value as a diagnostic field while base_return is
            # already the final score, so that field must NOT be added here.
            expected = (entry["base_return"] +
                        entry["curiosity_bonus_applied"] +
                        entry["risk_penalty_applied"])
        if abs(entry["total_score"] - expected) > 1e-9:
            raise RuntimeError("P5e: forged or inconsistent paid option")
    comp = diagnostic.get("competition_witness")
    if comp is None:
        if diagnostic["decision_outcome"] not in (
                "no_processing_budget", "no_funded_score"):
            raise RuntimeError("P5e: missing competition receipt")
        if witness:
            raise RuntimeError("P5e: nonempty paid scores without competition")
    else:
        if set(comp["scored_order"]) != set(names):
            raise RuntimeError("P5e: competition did not receive paid option set")
        if comp["winner_before_control"] not in names:
            raise RuntimeError("P5e: winner was not a funded option")
        attempts = comp["control_attempts"]
        order = comp["control_order"]
        if [entry["option"] for entry in attempts] != order[:len(attempts)]:
            raise RuntimeError("P5e: control attempt ordering mismatch")
        if not order or order[0] != comp["winner_before_control"]:
            raise RuntimeError("P5e: the first control option must be the winner")
        admissions = [v for v in attempts if v["admitted"]]
        if len(admissions) > 1 or (admissions and attempts[-1] != admissions[0]):
            raise RuntimeError("P5e: controller did not stop after admission")
        if diagnostic["decision_outcome"] == "action_admitted":
            if not admissions or comp["final_admitted_option"] != admissions[0]["option"]:
                raise RuntimeError("P5e: admitted action does not match control")
            if comp["final_admitted_option"] != info["option"]:
                raise RuntimeError("P5e: admitted choice does not match decision")
            if comp["final_admitted_action"] != action:
                raise RuntimeError("P5e: admitted motor does not match decision")
        elif diagnostic["decision_outcome"] == "control_rejected":
            if admissions or comp["final_admitted_option"] is not None:
                raise RuntimeError("P5e: falsely admitted failed controls")
        else:
            raise RuntimeError("P5e: competition exists without a funded score")
        if comp["paid_competition_cycles"] > work.cycles:
            raise RuntimeError("P5e: unpriced competition")
    return {
        "step_observation": "POST_DECISION_PRE_PHYSICS",
        "body_before_decision": list(capture["body"]),
        "inventory_before_decision": [list(item) for item in capture["inventory"]],
        "funding": info["funding"],
        "decision_outcome": diagnostic["decision_outcome"],
        "offered_options": diagnostic["offered_options"],
        "scored_options": diagnostic["scored_options"],
        "offered_families": dict(diagnostic["offered_families"]),
        "scored_families": dict(diagnostic["scored_families"]),
        # Complete ORIGINAL funded set, including rest/move/explore.
        "paid_option_scores": [dict(item) for item in witness],
        "competition": comp,
        "chosen_option": info["option"],
        "physical_action": action,
        "physical_param": param,
        "paid_decision_work": {
            "cycles": work.cycles,
            "simulated_steps": work.simulated_steps,
            "memory_items": work.memory_items,
            "replays": work.replays},
    }
