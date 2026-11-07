"""Paid nested value of one trial of a personally unsupported action.

Software kernel only. It composes the zero-mean stake prior with the exact
observed-effect view. No World, action admission or motor command is involved.
"""
from __future__ import annotations

from dataclasses import asdict
from math import fsum, isfinite

from .body import CognitiveBudget, CognitiveWork, VITAL, debit_cognition
from .information_value import WORK_KEYS, _add_work, _advance
from .observed_effect_view import (
    VIEW_WORK, paid_simulate_after_observed_effect)
from .plan_information import _continuation_dict, _validate_plan
from .unknown_effect_prior import paid_zero_mean_stake_prior

SCHEMA = "i3-unknown-action-trial-value/v1"


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


def _contains_exact(plan, key):
    return any(tuple(item) == key for item in plan)


def _minimum_ceiling(model, prior_work, branches, action_key,
                     common, post, horizon, original_work):
    common_cells = len(common)
    trial_cells = len(branches) * len(post)
    plan_items = sum(len(plan) for plan in common.values())
    trial_items = len(branches) * sum(
        1 + len(plan) for plan in post.values())

    prep = CognitiveWork(
        cycles=1,
        memory_items=(
            7 * len(branches)
            + 5 * (common_cells + trial_cells)
            + 2 * (plan_items + trial_items)
            + 4))

    common_work = CognitiveWork()
    for plan in common.values():
        common_work = _add_work(
            common_work,
            _add_work(CognitiveWork(cycles=1),
                      _simulation_upper(model, plan, horizon)))

    trial_work = CognitiveWork()
    for _branch in branches:
        for plan in post.values():
            full_plan = (action_key,) + tuple(plan)
            cell = CognitiveWork(cycles=1)
            cell = _add_work(cell, VIEW_WORK)
            cell = _add_work(
                cell, _simulation_upper(model, full_plan, horizon))
            trial_work = _add_work(trial_work, cell)

    reduction = CognitiveWork(cycles=1)
    total = original_work
    for block in (prior_work, prep, common_work, trial_work, reduction):
        total = _add_work(total, block)
    return prep, total


def paid_unknown_action_trial_value(
        model, action_key, common_continuations, post_trial_continuations,
        horizon, budget: CognitiveBudget, *,
        forecast_work: CognitiveWork | None = None) -> dict:
    """Compare no trial, frozen post-trial policy and informed post-trial policy.

    The zero-mean prior supplies the possible effect of the first unsupported
    action use. Each branch then simulates a full plan whose first action is
    that trial. The exact observed delta is also used for any later exact reuse
    of the same key in that branch.

    no_trial_value:
        best continuation that never uses the unsupported exact key.

    trial_frozen_value:
        best expected trial+continuation plan when the same post-trial
        continuation must be chosen before the trial outcome is observed.

    trial_informed_value:
        expected value when the post-trial continuation may be selected after
        observing the directly sensed post-trial body.

    information_value is informed minus frozen.
    trial_advantage is informed minus no-trial.
    """
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no trial-value cognition after physical death")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer simulation horizon required")
    _validate_plan((action_key,))
    action_key = tuple(action_key)

    common = _continuation_dict(
        common_continuations, allow_empty=False)
    post = _continuation_dict(
        post_trial_continuations, allow_empty=False)
    if set(common) & set(post):
        raise ValueError("common and post-trial continuation names must differ")
    if any(_contains_exact(plan, action_key) for plan in common.values()):
        raise ValueError(
            "no-trial continuation cannot contain unsupported exact action")

    if (not hasattr(model, "theta") or not hasattr(model, "p") or
            not hasattr(model, "w") or not hasattr(model, "proj_chunks") or
            not model.proj_chunks or
            not hasattr(model, "d_max") or
            type(model.d_max) not in (int, float) or
            not isfinite(model.d_max) or
            not callable(getattr(model, "simulate", None))):
        raise ValueError("current P1.3-compatible model required")
    if forecast_work is not None and not isinstance(
            forecast_work, CognitiveWork):
        raise ValueError("forecast_work must be CognitiveWork")

    original_work = budget.work

    # The prior primitive intentionally requires a fresh allowance. Build it
    # on a detached allowance from the same phase-start body, then buy exactly
    # that declared work on the real cumulative budget.
    prior_allowance = CognitiveBudget(budget.body, budget.laws)
    prior = paid_zero_mean_stake_prior(
        budget.body, tuple(model.theta), tuple(model.p), tuple(model.w),
        prior_allowance)
    budget.spend(prior_allowance.work)
    after_prior = budget.work

    branches = tuple(prior["outcomes"])
    if not branches:
        return {
            "schema": SCHEMA,
            "status": "NO_STAKE_RELEVANT_UNCERTAINTY",
            "prior_status": prior["status"],
            "no_trial_value": None,
            "trial_frozen_value": None,
            "trial_informed_value": None,
            "information_value": 0.0,
            "trial_advantage": None,
            "work": {
                key: getattr(budget.work, key) - getattr(original_work, key)
                for key in WORK_KEYS},
            "cost_is_physical_settlement_receipt": False,
            "world_access": False,
        }

    prep, minimum = _minimum_ceiling(
        model, prior_allowance.work, branches, action_key,
        common, post, horizon, original_work)
    budget.spend(prep)
    after_prep = budget.work

    ceiling = minimum if forecast_work is None else forecast_work
    if not _leq(minimum, ceiling):
        raise ValueError(
            "common forecast cannot omit complete unknown-action matrix")
    forecast_body, _ = debit_cognition(
        budget.body, budget.laws, ceiling)

    # Anti-oracle: an observation that is identical after clipping cannot teach
    # two different exact effects. The individual has no access to unclipped
    # hidden branch identity.
    observable_effect = {}
    observed_bodies = []
    for branch in branches:
        observed = _advance(forecast_body, branch.probe_delta)
        observable = (branch.signal, observed)
        learned = tuple(branch.probe_delta)
        old = observable_effect.get(observable)
        if old is None:
            observable_effect[observable] = learned
        elif old != learned:
            raise ValueError(
                "indistinguishable trial outcomes cannot teach different effects")
        observed_bodies.append(observed)

    common_values = {}
    for name in sorted(common):
        budget.spend(CognitiveWork(cycles=1))
        value, _steps, _u = model.simulate(
            forecast_body, common[name], horizon, budget)
        if type(value) not in (int, float) or not isfinite(value):
            raise ValueError("nonfinite no-trial continuation value")
        common_values[name] = value
        if not _leq(budget.work, ceiling):
            raise RuntimeError("no-trial work exceeded funded ceiling")
    no_trial_value = max(common_values.values())
    no_trial_best = tuple(
        name for name in sorted(common)
        if common_values[name] == no_trial_value)

    trial_rows = []
    for branch in branches:
        row = {}
        for name in sorted(post):
            budget.spend(CognitiveWork(cycles=1))
            full_plan = (action_key,) + tuple(post[name])
            result = paid_simulate_after_observed_effect(
                model, forecast_body, full_plan, horizon,
                action_key, tuple(branch.probe_delta), budget)
            value = result["value"]
            if type(value) not in (int, float) or not isfinite(value):
                raise ValueError("nonfinite trial continuation value")
            row[name] = value
            if not _leq(budget.work, ceiling):
                raise RuntimeError("trial matrix work exceeded funded ceiling")
        trial_rows.append(row)

    after_cells = budget.work
    budget.spend(CognitiveWork(cycles=1))
    if not _leq(budget.work, ceiling):
        raise RuntimeError("trial reduction exceeded funded ceiling")

    frozen_means = {
        name: fsum(
            branch.probability * trial_rows[i][name]
            for i, branch in enumerate(branches))
        for name in sorted(post)
    }
    trial_frozen_value = max(frozen_means.values())
    frozen_best = tuple(
        name for name in sorted(post)
        if frozen_means[name] == trial_frozen_value)

    groups = {}
    for i, branch in enumerate(branches):
        observable = (branch.signal, observed_bodies[i])
        groups.setdefault(observable, []).append(i)

    informed_parts = []
    conditional = []
    for observable, indices in sorted(groups.items()):
        signal, observed_body = observable
        joint = {
            name: fsum(
                branches[i].probability * trial_rows[i][name]
                for i in indices)
            for name in sorted(post)
        }
        best = max(joint.values())
        informed_parts.append(best)
        conditional.append({
            "signal": signal,
            "post_trial_body": observed_body,
            "probability": fsum(
                branches[i].probability for i in indices),
            "best_post_trial_continuations": tuple(
                name for name in sorted(post) if joint[name] == best),
        })
    trial_informed_value = fsum(informed_parts)
    information_value = trial_informed_value - trial_frozen_value
    if information_value < -1e-10:
        raise RuntimeError("conditional replanning reduced information value")
    if abs(information_value) < 1e-12:
        information_value = 0.0

    actual = CognitiveWork(*(
        getattr(budget.work, key) - getattr(original_work, key)
        for key in WORK_KEYS))
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_UNKNOWN_ACTION_TRIAL_ESTIMATE_NOT_POLICY",
        "action_key": action_key,
        "prior_status": prior["status"],
        "prior_expected_external_delta": prior[
            "expected_external_delta"],
        "no_trial_value": no_trial_value,
        "no_trial_best_continuations": no_trial_best,
        "trial_frozen_value": trial_frozen_value,
        "trial_frozen_best_continuations": frozen_best,
        "trial_informed_value": trial_informed_value,
        "information_value": information_value,
        "trial_advantage": trial_informed_value - no_trial_value,
        "conditional_choices": conditional,
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


__all__ = ["SCHEMA", "paid_unknown_action_trial_value"]
