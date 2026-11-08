"""Stage-1 water information using personally learned opportunity recurrence.

Software composition only. A paid OpportunityRecurrenceMemory supplies the
future matching-water availability scalar. No recurrence support means the
information trial is not evaluated; no numeric substitute is invented.
"""
from __future__ import annotations

from dataclasses import asdict

from .body import CognitiveBudget, CognitiveWork, VITAL
from .information_value import WORK_KEYS
from .opportunity_recurrence import OpportunityRecurrenceMemory
from .reference_branches import ReferenceBranchMemory
from .water_future_opportunity import paid_water_one_future_opportunity_value

SCHEMA = "i3-water-personal-recurrence-opportunity-value/v1"


def paid_water_personal_recurrence_value(
        model, memory: ReferenceBranchMemory,
        recurrence: OpportunityRecurrenceMemory,
        explore_plan, ordinary_continuations, horizon,
        budget: CognitiveBudget, *, omega: float = 0.0) -> dict:
    """Use paid personal recurrence as future water-opportunity availability."""
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if not isinstance(recurrence, OpportunityRecurrenceMemory):
        raise ValueError("OpportunityRecurrenceMemory required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no recurrence information cognition after death")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer planning horizon required")

    original_work = budget.work
    recurrence_result = recurrence.estimate("water", horizon, budget)
    after_recurrence = budget.work

    if recurrence_result["status"] == "NO_PERSONAL_RECURRENCE_SUPPORT":
        actual = CognitiveWork(*(
            getattr(budget.work, key) - getattr(original_work, key)
            for key in WORK_KEYS))
        return {
            "schema": SCHEMA,
            "status": "NO_PERSONAL_FUTURE_OPPORTUNITY_SUPPORT",
            "recurrence": recurrence_result,
            "future_water_opportunity_probability": None,
            "trial_evaluated": False,
            "trial_information_value": None,
            "trial_advantage": None,
            "target_node_best_choices": (),
            "work": asdict(actual),
            "work_breakdown": {
                "recurrence": asdict(actual),
                "stage1_kernel": asdict(CognitiveWork()),
                "total": asdict(actual),
            },
            "world_access": False,
            "motor_command_authorized": False,
            "cost_is_physical_settlement_receipt": False,
        }

    p_future = recurrence_result[
        "future_matching_opportunity_probability"]
    if p_future is None:
        raise RuntimeError("complete recurrence estimate lacks probability")

    inner = paid_water_one_future_opportunity_value(
        model, memory, explore_plan, ordinary_continuations, horizon, budget,
        future_opportunity_probability=p_future, omega=omega)

    total = CognitiveWork(*(
        getattr(budget.work, key) - getattr(original_work, key)
        for key in WORK_KEYS))
    kernel_work = CognitiveWork(*(
        getattr(budget.work, key) - getattr(after_recurrence, key)
        for key in WORK_KEYS))

    result = dict(inner)
    result.update({
        "schema": SCHEMA,
        "status": (
            "COMPLETE_PERSONAL_RECURRENCE_STAGE1_ESTIMATE_NOT_POLICY"
            if inner["status"] ==
            "COMPLETE_ONE_FUTURE_OPPORTUNITY_ESTIMATE_NOT_POLICY"
            else inner["status"]),
        "recurrence": recurrence_result,
        "future_water_opportunity_probability": p_future,
        "future_opportunity_probability_source":
            "PAID_PERSONAL_ONSET_RECURRENCE",
        "trial_evaluated": inner["trial_frozen_value"] is not None,
        "work": asdict(total),
        "work_breakdown": {
            "recurrence": {
                key: getattr(after_recurrence, key)
                - getattr(original_work, key)
                for key in WORK_KEYS},
            "stage1_kernel": asdict(kernel_work),
            "total": asdict(total),
        },
    })
    return result


__all__ = ["SCHEMA", "paid_water_personal_recurrence_value"]
