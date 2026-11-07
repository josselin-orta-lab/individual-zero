"""Paid information value for one carried unknown-food trial.

Software kernel only. A carried token is already a first-person action
opportunity, so no World/source-persistence model is needed.

Effect hypotheses come only from existing paid ReferenceBranchMemory:
exact-token support first, otherwise the existing same-action "manger"
fallback. The kernel compares one trial with an optional second carried unit.

It emits a score, never a motor command.
"""
from __future__ import annotations

from dataclasses import asdict
from math import fsum, isfinite

from .body import CognitiveBudget, CognitiveWork, VITAL, debit_cognition
from .information_value import WORK_KEYS, _add_work
from .observed_effect_view import (
    VIEW_WORK, paid_simulate_after_observed_effect)
from .reference_branches import ReferenceBranchMemory

SCHEMA = "i3-carried-unknown-food-information/v1"


def _leq(a, b):
    return all(getattr(a, key) <= getattr(b, key) for key in WORK_KEYS)


def _key(token):
    if type(token) is not str or not token:
        raise ValueError("nonempty internal carried-token identifier required")
    return ("manger", token)


def _simulation_upper(model, plan):
    return CognitiveWork(
        simulated_steps=len(plan) + len(model.proj_chunks))


def _minimum_ceiling(
        model, branches, repeat_available, original_work):
    cells_per_branch = 2 if repeat_available else 1
    cells = branches * cells_per_branch
    plan_items = branches * (1 + (2 if repeat_available else 0))
    prep = CognitiveWork(
        cycles=1,
        memory_items=branches * 7 + cells * 5 + 2 * plan_items + 6)

    matrix = CognitiveWork()
    stop = (("manger", "_placeholder"),)
    repeat = stop + stop
    for _ in range(branches):
        plans = (stop, repeat) if repeat_available else (stop,)
        for plan in plans:
            cell = _add_work(CognitiveWork(cycles=1), VIEW_WORK)
            cell = _add_work(cell, _simulation_upper(model, plan))
            matrix = _add_work(matrix, cell)

    reduction = CognitiveWork(cycles=1)
    total = original_work
    for block in (prep, matrix, reduction):
        total = _add_work(total, block)
    return prep, total


def paid_carried_unknown_food_information_value(
        model, memory: ReferenceBranchMemory, token, inventory_count,
        budget: CognitiveBudget, *,
        support_index=None,
        forecast_work: CognitiveWork | None = None) -> dict:
    """Value learning one carried token's effect with at most one repeat.

    inventory_count is the individual's current carried count for this internal
    token. One unit is the trial. If at least two units are carried, a second
    unit is a certain first-person future matching opportunity.

    More than two units do not create additional repeats in this bounded Stage-1
    kernel.
    """
    key = _key(token)
    if type(inventory_count) is not int or inventory_count < 1:
        raise ValueError("positive integer carried inventory_count required")
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no food-information cognition after physical death")
    if forecast_work is not None and not isinstance(
            forecast_work, CognitiveWork):
        raise ValueError("forecast_work must be CognitiveWork")
    if (not callable(getattr(model, "simulate", None)) or
            not hasattr(model, "proj_chunks") or not model.proj_chunks or
            not hasattr(model, "d_max") or
            type(model.d_max) not in (int, float) or
            not isfinite(model.d_max)):
        raise ValueError("current P1.3-compatible model required")

    original_work = budget.work
    support_receipt = {}
    support = memory.branches(
        key, budget, support_index=support_index,
        work_receipt=support_receipt)
    after_support = budget.work

    if len(support) not in (1, 2, 3):
        raise RuntimeError("personal food support must contain one to three rows")
    deltas = tuple(tuple(float(x) for x in row) for row in support)
    if len(deltas) == 1:
        deltas = deltas * 2
    branch_count = len(deltas)
    probabilities = tuple(1.0 / branch_count for _ in deltas)
    repeat_available = inventory_count >= 2

    prep, minimum = _minimum_ceiling(
        model, branch_count, repeat_available, budget.work)
    budget.spend(prep)
    after_prep = budget.work

    ceiling = minimum if forecast_work is None else forecast_work
    if not _leq(minimum, ceiling):
        raise ValueError(
            "common forecast cannot omit complete carried-food matrix")
    forecast_body, _ = debit_cognition(
        budget.body, budget.laws, ceiling)

    stop_values = []
    repeat_values = []
    for effect_delta in deltas:
        budget.spend(CognitiveWork(cycles=1))
        stop_result = paid_simulate_after_observed_effect(
            model, forecast_body, (key,), 1,
            key, effect_delta, budget)
        stop_values.append(stop_result["value"])
        if repeat_available:
            budget.spend(CognitiveWork(cycles=1))
            repeat_result = paid_simulate_after_observed_effect(
                model, forecast_body, (key, key), 2,
                key, effect_delta, budget)
            repeat_values.append(repeat_result["value"])
        if not _leq(budget.work, ceiling):
            raise RuntimeError("carried-food matrix exceeded funded ceiling")

    after_cells = budget.work
    budget.spend(CognitiveWork(cycles=1))
    if not _leq(budget.work, ceiling):
        raise RuntimeError("carried-food reduction exceeded funded ceiling")

    stop_expected = fsum(
        p * value for p, value in zip(probabilities, stop_values))
    if repeat_available:
        repeat_expected = fsum(
            p * value for p, value in zip(probabilities, repeat_values))
        frozen = max(stop_expected, repeat_expected)
        informed_parts = []
        choices = []
        for p, stop, repeat, delta in zip(
                probabilities, stop_values, repeat_values, deltas):
            best = max(stop, repeat)
            informed_parts.append(p * best)
            choices.append({
                "effect_delta": delta,
                "probability": p,
                "stop_value": stop,
                "repeat_value": repeat,
                "best_choices": tuple(
                    name for name, value in (
                        ("STOP_AFTER_TRIAL", stop),
                        ("REPEAT_ONCE", repeat))
                    if value >= best - 1e-12),
            })
        informed = fsum(informed_parts)
    else:
        repeat_expected = None
        frozen = stop_expected
        informed = stop_expected
        choices = tuple({
            "effect_delta": delta,
            "probability": p,
            "stop_value": stop,
            "repeat_value": None,
            "best_choices": ("STOP_AFTER_TRIAL",),
        } for p, stop, delta in zip(
            probabilities, stop_values, deltas))

    information = informed - frozen
    if information < -1e-10:
        raise RuntimeError("carried-food information reduced expected value")
    if abs(information) < 1e-12:
        information = 0.0

    actual = CognitiveWork(*(
        getattr(budget.work, key_name) - getattr(original_work, key_name)
        for key_name in WORK_KEYS))
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_CARRIED_UNKNOWN_FOOD_ESTIMATE_NOT_POLICY",
        "token": token,
        "inventory_count": inventory_count,
        "trial_units": 1,
        "future_repeat_units_modelled": 1 if repeat_available else 0,
        "additional_units_ignored_by_stage1_bound": max(
            0, inventory_count - 2),
        "support_records": len(support),
        "subjective_branches": branch_count,
        "support_access": support_receipt.get("access"),
        "stop_expected_value": stop_expected,
        "repeat_expected_value": repeat_expected,
        "frozen_value": frozen,
        "informed_value": informed,
        "information_value": information,
        "conditional_choices": tuple(choices),
        "option_score": informed,
        "score_units": "P1.3_NORMALIZED_PREDICTED_DISTRESS_RETURN",
        "trial_forced": False,
        "motor_command_authorized": False,
        "world_access": False,
        "work": asdict(actual),
        "work_breakdown": {
            "support_read": {
                key_name: getattr(after_support, key_name)
                - getattr(original_work, key_name)
                for key_name in WORK_KEYS},
            "preparation": {
                key_name: getattr(after_prep, key_name)
                - getattr(after_support, key_name)
                for key_name in WORK_KEYS},
            "matrix": {
                key_name: getattr(after_cells, key_name)
                - getattr(after_prep, key_name)
                for key_name in WORK_KEYS},
            "reduction": {
                key_name: getattr(budget.work, key_name)
                - getattr(after_cells, key_name)
                for key_name in WORK_KEYS},
            "total": asdict(actual),
        },
        "minimum_complete_forecast_work": asdict(minimum),
        "forecast_work_ceiling": asdict(ceiling),
        "forecast_start_body": forecast_body,
        "body_after_computation": budget.remaining,
        "cost_is_physical_settlement_receipt": False,
    }


__all__ = ["SCHEMA", "paid_carried_unknown_food_information_value"]
