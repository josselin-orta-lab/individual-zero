"""Read-only raw-rank audit for carried-food information value.

This laboratory helper never changes the supplied Mind and never executes a
World step. It runs one ordinary P1.3 decision on a deep copy with existing
diagnostic witnesses enabled, then evaluates the carried-food information kernel
on that same already-perceived copy under a separate fresh allowance.

The resulting score placements are DESCRIPTIVE_NOT_COST_MATCHED:
legacy P1.3 witnesses and the Stage-1 information kernel do not yet share one
common exhaustive forecast-body ceiling.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from ..modules.carried_food_information import (
    paid_carried_unknown_food_information_value)
from ..modules.personal_outcomes import NoPersonalSupport
from ..modules.reference_memory_mind import ReferenceBranchMemoryMind

SCHEMA = "i3-carried-food-raw-rank-audit/v1"


def _inventory_count(cap, external_token):
    if type(cap) is not dict or type(cap.get("inventory")) is not tuple:
        raise ValueError("first-person capture with immutable inventory required")
    found = []
    for item in cap["inventory"]:
        if (type(item) is not tuple or len(item) != 2 or
                type(item[0]) is not str or not item[0] or
                type(item[1]) is not int or item[1] <= 0):
            raise ValueError("malformed carried inventory entry")
        if item[0] == external_token:
            found.append(item[1])
    if len(found) != 1:
        raise ValueError("external carried token must appear exactly once")
    return found[0]


def _placement(witnesses, meal_option, field, candidate_score):
    meal = next(
        (row for row in witnesses if row["option"] == meal_option), None)
    if meal is None:
        raise ValueError("reference meal option was not scored")
    reference_meal = meal.get(field)
    if (type(reference_meal) not in (int, float) or
            not isfinite(reference_meal)):
        raise ValueError("reference meal score is not finite")

    competitors = []
    for row in witnesses:
        if row["option"] == meal_option:
            continue
        value = row.get(field)
        if type(value) not in (int, float) or not isfinite(value):
            raise ValueError("reference competitor score is not finite")
        competitors.append((row["option"], float(value)))

    above = tuple(sorted(
        option for option, value in competitors
        if value > candidate_score + 1e-12))
    tied = tuple(sorted(
        option for option, value in competitors
        if abs(value - candidate_score) <= 1e-12))
    below = tuple(sorted(
        option for option, value in competitors
        if value < candidate_score - 1e-12))

    top_competitor = None
    top_score = None
    if competitors:
        top_score = max(value for _, value in competitors)
        top_competitor = tuple(sorted(
            option for option, value in competitors
            if abs(value - top_score) <= 1e-12))

    return {
        "reference_field": field,
        "reference_meal_score": float(reference_meal),
        "candidate_score": float(candidate_score),
        "candidate_minus_reference_meal": float(
            candidate_score - reference_meal),
        "competitors_strictly_above": above,
        "competitors_tied": tied,
        "competitors_strictly_below": below,
        "candidate_rank_min": 1 + len(above),
        "candidate_rank_max": 1 + len(above) + len(tied),
        "candidate_raw_top": len(above) == 0,
        "top_competitor_options": top_competitor,
        "top_competitor_score": top_score,
        "candidate_minus_top_competitor": (
            None if top_score is None
            else float(candidate_score - top_score)),
    }


def audit_carried_food_raw_rank(
        mind: ReferenceBranchMemoryMind, cap, laws: BodyLaws,
        external_token: str) -> dict:
    """Place the Stage-1 carried-food score beside actual P1.3 score witnesses.

    The reference decision is executed only on a deep copy. Its chosen action is
    observed but never returned as an authorization. The Stage-1 candidate is
    then evaluated on the same perceived copy, using a separate fresh allowance
    from the same pre-decision body.

    No Competition replay is attempted because the candidate/reference scores
    are not yet cost-matched under one common exhaustive decision ceiling.
    """
    if not isinstance(mind, ReferenceBranchMemoryMind):
        raise ValueError("ReferenceBranchMemoryMind required")
    if not isinstance(laws, BodyLaws):
        raise ValueError("BodyLaws required")
    if type(external_token) is not str or not external_token:
        raise ValueError("nonempty external carried token required")
    if type(cap) is not dict or type(cap.get("body")) not in (tuple, list):
        raise ValueError("first-person capture required")
    body = tuple(float(x) for x in cap["body"])
    count = _inventory_count(cap, external_token)

    reference = deepcopy(mind)
    reference.observer_decision_diagnostics = True
    reference_budget = CognitiveBudget(body, laws)
    ref_action, ref_param, ref_work, ref_info = reference.decide(
        cap, reference_budget)

    observer = ref_info.get("observer")
    if type(observer) is not dict:
        return {
            "schema": SCHEMA,
            "status": "REFERENCE_DECISION_NOT_OBSERVABLE",
            "reference_funding": ref_info.get("funding"),
            "comparison_status": "NOT_EVALUATED",
        }
    witnesses = observer.get("score_witness")
    if type(witnesses) is not list or not witnesses:
        return {
            "schema": SCHEMA,
            "status": "REFERENCE_MEAL_NOT_SCORED",
            "reference_funding": ref_info.get("funding"),
            "reference_decision_outcome": observer.get("decision_outcome"),
            "comparison_status": "NOT_EVALUATED",
        }

    internal_token = reference.tokens.get(external_token)
    if type(internal_token) is not str or not internal_token:
        raise RuntimeError("reference perception did not internalize carried token")
    meal_option = "manger:" + internal_token
    if not any(row.get("option") == meal_option for row in witnesses):
        return {
            "schema": SCHEMA,
            "status": "REFERENCE_MEAL_NOT_SCORED",
            "meal_option": meal_option,
            "reference_funding": ref_info.get("funding"),
            "reference_decision_outcome": observer.get("decision_outcome"),
            "comparison_status": "NOT_EVALUATED",
        }

    candidate_budget = CognitiveBudget(body, laws)
    try:
        candidate = paid_carried_unknown_food_information_value(
            reference, reference.branch_memory, internal_token, count,
            candidate_budget)
    except NoPersonalSupport:
        return {
            "schema": SCHEMA,
            "status": "CANDIDATE_NO_PERSONAL_SUPPORT",
            "meal_option": meal_option,
            "reference_funding": ref_info.get("funding"),
            "candidate_work": {
                key: getattr(candidate_budget.work, key)
                for key in ("cycles", "simulated_steps",
                            "memory_items", "replays")},
            "comparison_status": "NOT_EVALUATED",
        }
    except CognitiveFundingError:
        return {
            "schema": SCHEMA,
            "status": "CANDIDATE_UNFUNDED",
            "meal_option": meal_option,
            "reference_funding": ref_info.get("funding"),
            "candidate_work": {
                key: getattr(candidate_budget.work, key)
                for key in ("cycles", "simulated_steps",
                            "memory_items", "replays")},
            "comparison_status": "NOT_EVALUATED",
        }

    candidate_score = candidate["option_score"]
    if type(candidate_score) not in (int, float) or not isfinite(candidate_score):
        raise RuntimeError("candidate carried-food score is not finite")

    base = _placement(
        witnesses, meal_option, "base_return", float(candidate_score))
    total = _placement(
        witnesses, meal_option, "total_score", float(candidate_score))

    return {
        "schema": SCHEMA,
        "status": "COMPLETE_DESCRIPTIVE_RAW_RANK_AUDIT",
        "comparison_status": "DESCRIPTIVE_NOT_COST_MATCHED",
        "meal_option": meal_option,
        "inventory_count": count,
        "reference": {
            "funding": ref_info.get("funding"),
            "chosen_option": ref_info.get("option"),
            "chosen_action": ref_action,
            "chosen_param": ref_param,
            "work": {
                key: getattr(ref_work, key)
                for key in ("cycles", "simulated_steps",
                            "memory_items", "replays")},
            "scored_options": len(witnesses),
        },
        "candidate": {
            "score": float(candidate_score),
            "information_value": float(candidate["information_value"]),
            "support_records": candidate["support_records"],
            "subjective_branches": candidate["subjective_branches"],
            "future_repeat_units_modelled": candidate[
                "future_repeat_units_modelled"],
            "work": dict(candidate["work"]),
        },
        "placement_vs_reference_base": base,
        "placement_vs_reference_total": total,
        "cost_boundary": {
            "candidate_forecasts_its_complete_kernel_cognition": True,
            "legacy_reference_uses_same_common_exhaustive_forecast": False,
            "causal_or_cost_matched_rank_claim": False,
        },
        "competition_replayed": False,
        "control_replayed": False,
        "counterfactual_motor_command_authorized": False,
        "world_step_executed": False,
    }


__all__ = ["SCHEMA", "audit_carried_food_raw_rank"]
