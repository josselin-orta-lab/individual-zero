"""Paid information value for one carried unknown-food trial.

Software kernel only. A carried token is already a first-person action
opportunity, so no World/source-persistence model is needed.

Effect hypotheses come only from existing paid ReferenceBranchMemory:
exact-token support first, otherwise the existing same-action "manger"
fallback. The kernel compares one trial with optional further carried units:
by default one repeat (#1102); opt-in `max_future_repeats` represents up to
that many further carried units as first-person future uses (characterization
STAGE1_CARRIED_FOOD_REUSE_CHARACTERIZATION.md).

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
        model, branches, repeats, original_work):
    cells_per_branch = repeats + 1
    cells = branches * cells_per_branch
    plan_items = branches * (repeats + 1) * (repeats + 2) // 2
    prep = CognitiveWork(
        cycles=1,
        memory_items=branches * 7 + cells * 5 + 2 * plan_items + 6)

    matrix = CognitiveWork()
    stop = (("manger", "_placeholder"),)
    for _ in range(branches):
        for units in range(1, repeats + 2):
            plan = stop * units
            cell = _add_work(CognitiveWork(cycles=1), VIEW_WORK)
            cell = _add_work(cell, _simulation_upper(model, plan))
            matrix = _add_work(matrix, cell)

    reduction = CognitiveWork(cycles=1)
    total = original_work
    for block in (prep, matrix, reduction):
        total = _add_work(total, block)
    return prep, total


def _plan_name(units):
    if units == 1:
        return "STOP_AFTER_TRIAL"
    if units == 2:
        return "REPEAT_ONCE"
    return f"REPEAT_{units - 1}_TIMES"


def paid_carried_unknown_food_information_value(
        model, memory: ReferenceBranchMemory, token, inventory_count,
        budget: CognitiveBudget, *,
        support_index=None,
        forecast_work: CognitiveWork | None = None,
        max_future_repeats: int = 1) -> dict:
    """Value learning one carried token's effect over carried future uses.

    inventory_count is the individual's current carried count for this internal
    token. One unit is the trial. Each further carried unit is a certain
    first-person future matching opportunity. At most
    `r = min(max_future_repeats, inventory_count - 1)` further units are
    represented; the default (1) is exactly the bounded #1102 kernel.
    Outcome branches stay the two or three personal effect rows; the r + 1
    plans per branch are all simulated and paid before comparison.
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
    if type(max_future_repeats) is not int or max_future_repeats < 1:
        raise ValueError("max_future_repeats must be a positive integer")
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
    repeats = min(max_future_repeats, inventory_count - 1)

    prep, minimum = _minimum_ceiling(
        model, branch_count, repeats, budget.work)
    budget.spend(prep)
    after_prep = budget.work

    ceiling = minimum if forecast_work is None else forecast_work
    if not _leq(minimum, ceiling):
        raise ValueError(
            "common forecast cannot omit complete carried-food matrix")
    forecast_body, _ = debit_cognition(
        budget.body, budget.laws, ceiling)

    plan_values = []          # plan_values[i][j]: eat j + 1 units, branch i
    for effect_delta in deltas:
        row = []
        for units in range(1, repeats + 2):
            budget.spend(CognitiveWork(cycles=1))
            result = paid_simulate_after_observed_effect(
                model, forecast_body, (key,) * units, units,
                key, effect_delta, budget)
            row.append(result["value"])
        plan_values.append(row)
        if not _leq(budget.work, ceiling):
            raise RuntimeError("carried-food matrix exceeded funded ceiling")

    after_cells = budget.work
    budget.spend(CognitiveWork(cycles=1))
    if not _leq(budget.work, ceiling):
        raise RuntimeError("carried-food reduction exceeded funded ceiling")

    plan_expected = tuple(
        fsum(p * row[j] for p, row in zip(probabilities, plan_values))
        for j in range(repeats + 1))
    stop_expected = plan_expected[0]
    repeat_expected = plan_expected[1] if repeats >= 1 else None
    frozen = max(plan_expected)
    informed = fsum(
        p * max(row) for p, row in zip(probabilities, plan_values))
    choices = []
    for p, row, delta in zip(probabilities, plan_values, deltas):
        best = max(row)
        choices.append({
            "effect_delta": delta,
            "probability": p,
            "stop_value": row[0],
            "repeat_value": row[1] if repeats >= 1 else None,
            "plan_values": tuple(row),
            "best_choices": tuple(
                _plan_name(j + 1) for j, value in enumerate(row)
                if value >= best - 1e-12),
        })
    choices = tuple(choices)

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
        "max_future_repeats": max_future_repeats,
        "future_repeat_units_modelled": repeats,
        "additional_units_ignored_by_stage1_bound": max(
            0, inventory_count - 1 - repeats),
        "support_records": len(support),
        "subjective_branches": branch_count,
        "support_access": support_receipt.get("access"),
        "stop_expected_value": stop_expected,
        "repeat_expected_value": repeat_expected,
        "plan_expected_values": plan_expected,
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
