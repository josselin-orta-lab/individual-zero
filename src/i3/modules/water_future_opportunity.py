"""Paid water-frontier value with one future matching opportunity.

Software kernel only. It never assumes that the currently revealed source
persists after the first drink trial.

The initial frontier has at most three subjective leaves:
    no water target;
    water + RMS-positive unsupported drink effect;
    water + RMS-negative unsupported drink effect.

Conditional on learning the drink effect, the model additionally represents one
future generic water opportunity with the current first-person water-modality
probability. That future availability is analytically marginalized, not added
as a new simulated subjective outcome branch.

Every ordinary and future-reuse plan cell is still explicitly simulated and
paid before values are compared.
"""
from __future__ import annotations

from dataclasses import asdict
from math import fsum, isfinite

from .body import CognitiveBudget, CognitiveWork, VITAL, debit_cognition
from .information_value import WORK_KEYS, _add_work
from .observed_effect_view import (
    VIEW_WORK, paid_simulate_after_observed_effect)
from .plan_information import _validate_plan
from .reference_branches import ReferenceBranchMemory
from .rms_three_leaf_target_prior import paid_rms_three_leaf_target_prior

SCHEMA = "i3-water-one-future-opportunity-value/v1"
DRINK = ("boire",)
TARGET_ENTRY = ("se_deplacer",)


def _leq(a, b):
    return all(getattr(a, key) <= getattr(b, key) for key in WORK_KEYS)


def _simulation_upper(model, plan, horizon):
    i = steps = 0
    while i < len(plan) and steps < horizon:
        key = plan[i]
        run = 1
        if key[0] == "se_deplacer":
            while (i + run < len(plan) and plan[i + run] == key and
                   run < horizon):
                run += 1
        i += run
        steps += 1
    return CognitiveWork(
        simulated_steps=steps + len(model.proj_chunks))


def _contains(plan, key):
    return any(tuple(item) == key for item in plan)


def _validate_explorer_prefix(plan):
    _validate_plan(plan)
    if any(tuple(key) != TARGET_ENTRY for key in plan):
        raise ValueError("existing P1.3 explorer prefix must contain moves only")




def _ordinary_continuation_dict(items):
    """Named suffixes; empty tuple means stop/bootstrap after explorer prefix."""
    if type(items) is not tuple or not items:
        raise ValueError("nonempty named ordinary continuation set required")
    out = {}
    for item in items:
        if type(item) is not tuple or len(item) != 2:
            raise ValueError("continuation identifier/plan pair required")
        name, plan = item
        if type(name) is not str or not name or name in out:
            raise ValueError("unique nonempty continuation identifier required")
        if type(plan) is not tuple:
            raise ValueError("immutable continuation plan required")
        if plan:
            _validate_plan(plan)
        out[name] = plan
    return out


def _future_opportunity_reduction(
        conditional, ordinary_rows, reuse_rows, p_future):
    """Reduce two learned-effect branches and one observable availability event.

    Availability itself is not a simulated outcome branch. When absent, only
    ordinary plans exist. When present, a matching-action reuse plan is also
    available. The informed policy knows the learned effect branch; the frozen
    comparator does not, while both may condition on observed availability.
    """
    if (type(conditional) is not tuple or len(conditional) != 2 or
            any(type(q) not in (int, float) or not isfinite(q) or q <= 0.0
                for q in conditional) or
            abs(fsum(conditional) - 1.0) > 1e-12):
        raise ValueError("two normalized positive effect probabilities required")
    if (type(p_future) not in (int, float) or not isfinite(p_future) or
            not 0.0 <= p_future <= 1.0):
        raise ValueError("future opportunity probability must be in [0,1]")
    if (type(ordinary_rows) is not tuple or type(reuse_rows) is not tuple or
            len(ordinary_rows) != 2 or len(reuse_rows) != 2):
        raise ValueError("two ordinary/reuse effect rows required")
    names = tuple(sorted(ordinary_rows[0]))
    if not names:
        raise ValueError("nonempty continuation rows required")
    for rows in (ordinary_rows, reuse_rows):
        for row in rows:
            if type(row) is not dict or tuple(sorted(row)) != names:
                raise ValueError("continuation rows must share names")
            if any(type(v) not in (int, float) or not isfinite(v)
                   for v in row.values()):
                raise ValueError("finite continuation values required")

    informed_parts = []
    branch_choices = []
    for i in range(2):
        best_o = max(ordinary_rows[i].values())
        best_r = max(reuse_rows[i].values())
        present = max(best_o, best_r)
        informed_branch = (
            (1.0 - p_future) * best_o
            + p_future * present)
        informed_parts.append(
            conditional[i] * informed_branch)
        branch_choices.append({
            "best_without_future_opportunity": tuple(
                name for name in names
                if ordinary_rows[i][name] == best_o),
            "best_reuse_continuations_if_available": tuple(
                name for name in names
                if reuse_rows[i][name] == best_r),
            "future_opportunity_choice": (
                "REUSE" if best_r > best_o + 1e-12
                else "DECLINE_REUSE" if best_o > best_r + 1e-12
                else "TIE"),
        })
    informed = fsum(informed_parts)

    mean_o = {
        name: fsum(
            conditional[i] * ordinary_rows[i][name]
            for i in range(2))
        for name in names
    }
    mean_r = {
        name: fsum(
            conditional[i] * reuse_rows[i][name]
            for i in range(2))
        for name in names
    }
    frozen_absent = max(mean_o.values())
    frozen_present = max(
        max(mean_o.values()), max(mean_r.values()))
    frozen = (
        (1.0 - p_future) * frozen_absent
        + p_future * frozen_present)

    information = informed - frozen
    if information < -1e-10:
        raise RuntimeError("effect information reduced expected value")
    if abs(information) < 1e-12:
        information = 0.0
    return {
        "informed_value": informed,
        "frozen_value": frozen,
        "information_value": information,
        "branch_choices": tuple(branch_choices),
    }


def _minimum_ceiling(
        model, explore, ordinary, horizon, original_work, *,
        effect_branches):
    if effect_branches not in (0, 2):
        raise ValueError("future-opportunity model has zero or two effect branches")

    decline_cells = len(ordinary)
    # Per effect branch, evaluate every ordinary continuation twice:
    # current-trial-only O_ij and one-future-opportunity reuse R_ij.
    trial_cells = effect_branches * 2 * len(ordinary)

    decline_items = sum(
        len(explore) + len(plan)
        for plan in ordinary.values())
    trial_items = effect_branches * sum(
        (len(explore) + 2 + len(plan))
        + (len(explore) + 4 + len(plan))
        for plan in ordinary.values())

    prep = CognitiveWork(
        cycles=1,
        memory_items=(
            (1 + effect_branches) * 7
            + 5 * (decline_cells + trial_cells)
            + 2 * (decline_items + trial_items)
            + 12))

    decline_work = CognitiveWork()
    for plan in ordinary.values():
        full = tuple(explore) + tuple(plan)
        decline_work = _add_work(
            decline_work,
            _add_work(
                CognitiveWork(cycles=1),
                _simulation_upper(model, full, horizon)))

    trial_work = CognitiveWork()
    for _ in range(effect_branches):
        for plan in ordinary.values():
            current_trial = (
                tuple(explore)
                + (TARGET_ENTRY, DRINK)
                + tuple(plan))
            future_reuse = (
                tuple(explore)
                + (TARGET_ENTRY, DRINK, TARGET_ENTRY, DRINK)
                + tuple(plan))
            for full in (current_trial, future_reuse):
                cell = _add_work(
                    CognitiveWork(cycles=1), VIEW_WORK)
                cell = _add_work(
                    cell, _simulation_upper(model, full, horizon))
                trial_work = _add_work(trial_work, cell)

    reduction = CognitiveWork(cycles=2)
    total = original_work
    for block in (prep, decline_work, trial_work, reduction):
        total = _add_work(total, block)
    return prep, total


def paid_water_one_future_opportunity_value(
        model, memory: ReferenceBranchMemory, explore_plan,
        ordinary_continuations, horizon, budget: CognitiveBudget, *,
        forecast_work: CognitiveWork | None = None,
        future_opportunity_probability: float | None = None) -> dict:
    """Value a current unknown drink trial plus one generic future opportunity.

    The future opportunity is not the persistence of the current source.
    It is one generic future water-modality opportunity after one generic
    movement, weighted by the current first-person water-modality probability.

    Conditional on an effect branch i:
      O_ij = current trial + ordinary continuation j
      R_ij = current trial + one generic future move/drink + continuation j

    Future opportunity availability is observable when it occurs. Therefore the
    informed policy can choose between O and R after both effect learning and
    availability observation. The frozen comparator may condition on
    availability but not on the unknown drink effect.

    No availability branch is simulated. The Bernoulli event is marginalized
    analytically while every O/R plan cell is genuinely simulated and paid.
    """
    _validate_explorer_prefix(explore_plan)
    ordinary = _ordinary_continuation_dict(ordinary_continuations)
    if any(_contains(plan, DRINK) for plan in ordinary.values()):
        raise ValueError(
            "ordinary continuation cannot contain unsupported drink")
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer simulation horizon required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no future-opportunity cognition after physical death")
    if forecast_work is not None and not isinstance(
            forecast_work, CognitiveWork):
        raise ValueError("forecast_work must be CognitiveWork")
    if (future_opportunity_probability is not None and
            (type(future_opportunity_probability) not in (int, float) or
             not isfinite(future_opportunity_probability) or
             not 0.0 <= future_opportunity_probability <= 1.0)):
        raise ValueError(
            "future_opportunity_probability must be finite in [0,1]")
    if (not hasattr(model, "map") or type(model.map) is not dict or
            not hasattr(model, "proj_chunks") or not model.proj_chunks or
            not callable(getattr(model, "simulate", None)) or
            not hasattr(model, "d_max") or
            type(model.d_max) not in (int, float) or
            not isfinite(model.d_max)):
        raise ValueError("current P1.3-compatible model required")

    original_work = budget.work
    prior = paid_rms_three_leaf_target_prior(
        model.map, memory, "water", budget)
    after_prior = budget.work

    effect_branches = 2 if prior["leaves"] else 0
    prep, minimum = _minimum_ceiling(
        model, tuple(explore_plan), ordinary, horizon, budget.work,
        effect_branches=effect_branches)
    budget.spend(prep)
    after_prep = budget.work

    ceiling = minimum if forecast_work is None else forecast_work
    if not _leq(minimum, ceiling):
        raise ValueError(
            "common forecast cannot omit complete future-opportunity matrix")
    forecast_body, _ = debit_cognition(
        budget.body, budget.laws, ceiling)

    decline_values = {}
    for name in sorted(ordinary):
        budget.spend(CognitiveWork(cycles=1))
        full = tuple(explore_plan) + tuple(ordinary[name])
        value, _steps, _uncertainty = model.simulate(
            forecast_body, full, horizon, budget)
        if type(value) not in (int, float) or not isfinite(value):
            raise ValueError("nonfinite decline continuation value")
        decline_values[name] = value
        if not _leq(budget.work, ceiling):
            raise RuntimeError("decline work exceeded funded ceiling")

    decline_value = max(decline_values.values())
    decline_best = tuple(
        name for name in sorted(ordinary)
        if decline_values[name] == decline_value)

    if not prior["leaves"]:
        after_cells = budget.work
        budget.spend(CognitiveWork(cycles=2))
        if not _leq(budget.work, ceiling):
            raise RuntimeError("no-support reduction exceeded funded ceiling")
        actual = CognitiveWork(*(
            getattr(budget.work, key) - getattr(original_work, key)
            for key in WORK_KEYS))
        return {
            "schema": SCHEMA,
            "status": prior["status"],
            "water_probability": prior["target_probability"],
            "future_water_opportunity_probability": (
                prior["target_probability"]
                if future_opportunity_probability is None
                else float(future_opportunity_probability)),
            "future_opportunity_probability_source": (
                "CURRENT_FIRST_PERSON_MODALITY_PROXY"
                if future_opportunity_probability is None
                else "EXPLICIT_PERSONAL_RECURRENCE"),
            "decline_value": decline_value,
            "decline_best_continuations": decline_best,
            "trial_frozen_value": None,
            "trial_informed_value": None,
            "trial_information_value": 0.0,
            "trial_advantage": None,
            "target_node_best_choices": ("DECLINE_TRIAL",),
            "frontier_expected_value": decline_value,
            "water_revelation_advantage": 0.0,
            "subjective_leaf_count": 0,
            "work": asdict(actual),
            "forecast_work_ceiling": asdict(ceiling),
            "body_after_computation": budget.remaining,
            "world_access": False,
            "motor_command_authorized": False,
            "cost_is_physical_settlement_receipt": False,
        }

    if prior["leaf_count"] != 3:
        raise RuntimeError("RMS water prior must have exactly three leaves")
    no_target, positive, negative = prior["leaves"]
    p_initial = prior["target_probability"]
    p_future = (
        p_initial if future_opportunity_probability is None
        else float(future_opportunity_probability))
    if not 0.0 < p_initial < 1.0:
        raise RuntimeError("strict water probability required")
    if no_target["leaf"] != "NO_TARGET_MODALITY":
        raise RuntimeError("first RMS target leaf must be no-target")

    effect_leaves = (positive, negative)
    conditional = [
        leaf["probability"] / p_initial
        for leaf in effect_leaves]
    if abs(fsum(conditional) - 1.0) > 1e-12:
        raise RuntimeError("conditional RMS effects do not normalize")

    ordinary_rows = []
    reuse_rows = []
    for leaf in effect_leaves:
        ordinary_row = {}
        reuse_row = {}
        effect_delta = tuple(leaf["effect_delta"])
        for name in sorted(ordinary):
            current_trial = (
                tuple(explore_plan)
                + (TARGET_ENTRY, DRINK)
                + tuple(ordinary[name]))
            future_reuse = (
                tuple(explore_plan)
                + (TARGET_ENTRY, DRINK, TARGET_ENTRY, DRINK)
                + tuple(ordinary[name]))
            budget.spend(CognitiveWork(cycles=1))
            o = paid_simulate_after_observed_effect(
                model, forecast_body, current_trial, horizon,
                DRINK, effect_delta, budget)
            budget.spend(CognitiveWork(cycles=1))
            r = paid_simulate_after_observed_effect(
                model, forecast_body, future_reuse, horizon,
                DRINK, effect_delta, budget)
            ordinary_row[name] = o["value"]
            reuse_row[name] = r["value"]
            if not _leq(budget.work, ceiling):
                raise RuntimeError(
                    "future-opportunity plan matrix exceeded funded ceiling")
        ordinary_rows.append(ordinary_row)
        reuse_rows.append(reuse_row)

    after_cells = budget.work
    budget.spend(CognitiveWork(cycles=2))
    if not _leq(budget.work, ceiling):
        raise RuntimeError(
            "future-opportunity reduction exceeded funded ceiling")

    reduced = _future_opportunity_reduction(
        tuple(conditional), tuple(ordinary_rows), tuple(reuse_rows), p_future)
    informed = reduced["informed_value"]
    frozen = reduced["frozen_value"]
    information = reduced["information_value"]
    branch_choices = []
    for leaf, row in zip(effect_leaves, reduced["branch_choices"]):
        item = dict(row)
        item["effect_delta"] = tuple(leaf["effect_delta"])
        branch_choices.append(item)

    trial_advantage = informed - decline_value
    target_value = max(decline_value, informed)
    target_choices = []
    if decline_value >= target_value - 1e-12:
        target_choices.append("DECLINE_TRIAL")
    if informed >= target_value - 1e-12:
        target_choices.append("TRIAL")
    target_choices = tuple(target_choices)

    frontier_expected = (
        (1.0 - p_initial) * decline_value
        + p_initial * target_value)
    revelation_advantage = frontier_expected - decline_value
    if revelation_advantage < -1e-10:
        raise RuntimeError("optional water revelation reduced expected value")
    if abs(revelation_advantage) < 1e-12:
        revelation_advantage = 0.0

    actual = CognitiveWork(*(
        getattr(budget.work, key) - getattr(original_work, key)
        for key in WORK_KEYS))
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_ONE_FUTURE_OPPORTUNITY_ESTIMATE_NOT_POLICY",
        "water_probability": p_initial,
        "future_water_opportunity_probability": p_future,
        "future_opportunity_probability_source": (
            "CURRENT_FIRST_PERSON_MODALITY_PROXY"
            if future_opportunity_probability is None
            else "EXPLICIT_PERSONAL_RECURRENCE"),
        "future_opportunity_semantics": (
            "ONE_GENERIC_FUTURE_ONE_CELL_WATER_OPPORTUNITY_"
            "NOT_CURRENT_SOURCE_PERSISTENCE"),
        "decline_value": decline_value,
        "decline_best_continuations": decline_best,
        "trial_frozen_value": frozen,
        "trial_informed_value": informed,
        "trial_information_value": information,
        "trial_advantage": trial_advantage,
        "target_node_best_choices": target_choices,
        "frontier_expected_value": frontier_expected,
        "water_revelation_advantage": revelation_advantage,
        "effect_branch_choices": tuple(branch_choices),
        "prior_expected_external_delta": tuple(
            prior["expected_external_delta"]),
        "subjective_leaf_count": prior["leaf_count"],
        "future_availability_marginalized": True,
        "future_availability_simulated_as_extra_branch": False,
        "cross_channel_approximation": prior[
            "cross_channel_approximation"],
        "work": asdict(actual),
        "work_breakdown": {
            "prior": {
                key: getattr(after_prior, key) - getattr(original_work, key)
                for key in WORK_KEYS},
            "preparation": {
                key: getattr(after_prep, key) - getattr(after_prior, key)
                for key in WORK_KEYS},
            "matrix": {
                key: getattr(after_cells, key) - getattr(after_prep, key)
                for key in WORK_KEYS},
            "reduction": {
                key: getattr(budget.work, key) - getattr(after_cells, key)
                for key in WORK_KEYS},
            "total": asdict(actual),
        },
        "minimum_complete_forecast_work": asdict(minimum),
        "forecast_work_ceiling": asdict(ceiling),
        "forecast_start_body": forecast_body,
        "body_after_computation": budget.remaining,
        "world_access": False,
        "motor_command_authorized": False,
        "cost_is_physical_settlement_receipt": False,
    }


__all__ = ["SCHEMA", "paid_water_one_future_opportunity_value"]
