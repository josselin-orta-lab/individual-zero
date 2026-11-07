"""Three-leaf water-frontier value with an optional unsupported drink trial.

Software kernel only. It keeps the existing P1.3 explorer prefix and water
sensor/action binding, but removes any implicit "always sample unknown water"
rule. If water is revealed, the model compares declining the trial with the
expected value of one zero-mean unsupported trial followed by branch-local
replanning.

The stochastic outcome envelope is exactly the #1093 three-leaf water prior:
no water target, water+trial-positive, water+trial-negative.
"""
from __future__ import annotations

from dataclasses import asdict
from math import fsum, isfinite

from .body import CognitiveBudget, CognitiveWork, VITAL, debit_cognition
from .information_value import WORK_KEYS, _add_work
from .observed_effect_view import (
    VIEW_WORK, paid_simulate_after_observed_effect)
from .plan_information import _continuation_dict, _validate_plan
from .three_leaf_target_prior import paid_three_leaf_target_prior

SCHEMA = "i3-water-frontier-optional-trial/v1"
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


def _minimum_ceiling(
        model, explore, common, post, horizon, original_work,
        *, trial_branches):
    if trial_branches not in (0, 2):
        raise ValueError("water bootstrap has zero or two trial-effect branches")
    common_cells = len(common)
    trial_cells = trial_branches * len(post)
    common_items = sum(
        len(explore) + len(plan) for plan in common.values())
    trial_items = trial_branches * sum(
        len(explore) + 2 + len(plan) for plan in post.values())

    prep = CognitiveWork(
        cycles=1,
        memory_items=(
            (1 + trial_branches) * 7
            + 5 * (common_cells + trial_cells)
            + 2 * (common_items + trial_items)
            + 8))

    common_work = CognitiveWork()
    for plan in common.values():
        full = tuple(explore) + tuple(plan)
        common_work = _add_work(
            common_work,
            _add_work(
                CognitiveWork(cycles=1),
                _simulation_upper(model, full, horizon)))

    trial_work = CognitiveWork()
    for _ in range(trial_branches):
        for plan in post.values():
            full = tuple(explore) + (TARGET_ENTRY, DRINK) + tuple(plan)
            cell = _add_work(
                CognitiveWork(cycles=1), VIEW_WORK)
            cell = _add_work(
                cell, _simulation_upper(model, full, horizon))
            trial_work = _add_work(trial_work, cell)

    reduction = CognitiveWork(cycles=2)
    total = original_work
    for block in (prep, common_work, trial_work, reduction):
        total = _add_work(total, block)
    return prep, total


def paid_water_frontier_optional_trial_value(
        model, explore_plan, common_continuations,
        post_trial_continuations, horizon, budget: CognitiveBudget, *,
        forecast_work: CognitiveWork | None = None) -> dict:
    """Value one water-frontier option without forcing an unknown drink trial.

    All common continuations exclude the unsupported drink key. If the water
    modality is revealed, the target node chooses between that ordinary common
    value and the expected value of one drink trial. The trial itself has two
    zero-mean subjective effect leaves. After the trial, the directly sensed
    effect may change which post-trial continuation is best.

    The returned frontier value is a branch-conditioned expected bodily value,
    not an additive curiosity bonus.
    """
    _validate_explorer_prefix(explore_plan)
    common = _continuation_dict(
        common_continuations, allow_empty=False)
    post = _continuation_dict(
        post_trial_continuations, allow_empty=False)
    if set(common) & set(post):
        raise ValueError("common and post-trial continuation names must differ")
    if any(_contains(plan, DRINK) for plan in common.values()):
        raise ValueError(
            "ordinary continuation cannot contain unsupported drink trial")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer simulation horizon required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no frontier-value cognition after physical death")
    if forecast_work is not None and not isinstance(
            forecast_work, CognitiveWork):
        raise ValueError("forecast_work must be CognitiveWork")
    if (not hasattr(model, "map") or type(model.map) is not dict or
            not hasattr(model, "theta") or not hasattr(model, "p") or
            not hasattr(model, "w") or
            not hasattr(model, "proj_chunks") or not model.proj_chunks or
            not callable(getattr(model, "simulate", None)) or
            not hasattr(model, "d_max") or
            type(model.d_max) not in (int, float) or
            not isfinite(model.d_max)):
        raise ValueError("current P1.3-compatible model required")

    original_work = budget.work
    prior = paid_three_leaf_target_prior(
        model.map, budget.body, tuple(model.theta), tuple(model.p),
        tuple(model.w), "water", budget)
    after_prior = budget.work

    trial_branches = 2 if prior["leaves"] else 0
    prep, minimum = _minimum_ceiling(
        model, tuple(explore_plan), common, post, horizon, budget.work,
        trial_branches=trial_branches)
    budget.spend(prep)
    after_prep = budget.work

    ceiling = minimum if forecast_work is None else forecast_work
    if not _leq(minimum, ceiling):
        raise ValueError(
            "common forecast cannot omit complete water-frontier matrix")
    forecast_body, _ = debit_cognition(
        budget.body, budget.laws, ceiling)

    common_values = {}
    for name in sorted(common):
        budget.spend(CognitiveWork(cycles=1))
        full = tuple(explore_plan) + tuple(common[name])
        value, _steps, _uncertainty = model.simulate(
            forecast_body, full, horizon, budget)
        if type(value) not in (int, float) or not isfinite(value):
            raise ValueError("nonfinite ordinary frontier continuation value")
        common_values[name] = value
        if not _leq(budget.work, ceiling):
            raise RuntimeError("ordinary frontier work exceeded funded ceiling")

    decline_value = max(common_values.values())
    decline_best = tuple(
        name for name in sorted(common)
        if common_values[name] == decline_value)

    if not prior["leaves"]:
        after_cells = budget.work
        budget.spend(CognitiveWork(cycles=2))
        if not _leq(budget.work, ceiling):
            raise RuntimeError("flat-stake reduction exceeded funded ceiling")
        actual = CognitiveWork(*(
            getattr(budget.work, key) - getattr(original_work, key)
            for key in WORK_KEYS))
        return {
            "schema": SCHEMA,
            "status": "NO_STAKE_RELEVANT_UNCERTAINTY",
            "water_probability": prior["target_probability"],
            "ordinary_frontier_value": decline_value,
            "ordinary_best_continuations": decline_best,
            "trial_frozen_value": None,
            "trial_informed_value": None,
            "trial_information_value": 0.0,
            "trial_advantage": None,
            "target_node_best_choices": ("DECLINE_TRIAL",),
            "frontier_expected_value": decline_value,
            "water_revelation_advantage": 0.0,
            "leaf_count": 0,
            "work": asdict(actual),
            "forecast_work_ceiling": asdict(ceiling),
            "body_after_computation": budget.remaining,
            "motor_command_authorized": False,
            "world_access": False,
            "cost_is_physical_settlement_receipt": False,
        }

    if prior["leaf_count"] != 3:
        raise RuntimeError("water frontier requires exactly three prior leaves")
    no_target, plus, minus = prior["leaves"]
    p_water = prior["target_probability"]
    if not 0.0 < p_water < 1.0:
        raise RuntimeError("strict water target probability required")
    if no_target["leaf"] != "NO_TARGET_MODALITY":
        raise RuntimeError("first target-prior leaf must be no-target")
    if abs(no_target["probability"] - (1.0 - p_water)) > 1e-12:
        raise RuntimeError("no-target probability mismatch")

    plus_delta = tuple(plus["effect_delta"])
    minus_delta = tuple(minus["effect_delta"])
    if (not any(abs(x) > 1e-12 for x in plus_delta) or
            any(abs(a + b) > 1e-12
                for a, b in zip(plus_delta, minus_delta))):
        raise RuntimeError("water trial effects must be nonzero exact opposites")

    effect_leaves = (plus, minus)
    trial_rows = []
    for leaf in effect_leaves:
        row = {}
        for name in sorted(post):
            budget.spend(CognitiveWork(cycles=1))
            full = (
                tuple(explore_plan)
                + (TARGET_ENTRY, DRINK)
                + tuple(post[name]))
            result = paid_simulate_after_observed_effect(
                model, forecast_body, full, horizon,
                DRINK, tuple(leaf["effect_delta"]), budget)
            value = result["value"]
            if type(value) not in (int, float) or not isfinite(value):
                raise ValueError("nonfinite water-trial continuation value")
            row[name] = value
            if not _leq(budget.work, ceiling):
                raise RuntimeError("water trial matrix exceeded funded ceiling")
        trial_rows.append(row)

    after_cells = budget.work
    budget.spend(CognitiveWork(cycles=2))
    if not _leq(budget.work, ceiling):
        raise RuntimeError("water frontier reduction exceeded funded ceiling")

    conditional = [
        leaf["probability"] / p_water for leaf in effect_leaves]
    if abs(fsum(conditional) - 1.0) > 1e-12:
        raise RuntimeError("conditional water trial effects do not normalize")

    frozen_means = {
        name: fsum(
            conditional[i] * trial_rows[i][name]
            for i in range(2))
        for name in sorted(post)
    }
    trial_frozen_value = max(frozen_means.values())
    frozen_best = tuple(
        name for name in sorted(post)
        if frozen_means[name] == trial_frozen_value)

    branch_best = [max(row.values()) for row in trial_rows]
    trial_informed_value = fsum(
        conditional[i] * branch_best[i] for i in range(2))
    trial_information_value = trial_informed_value - trial_frozen_value
    if trial_information_value < -1e-10:
        raise RuntimeError("observed trial effect reduced information value")
    if abs(trial_information_value) < 1e-12:
        trial_information_value = 0.0

    trial_advantage = trial_informed_value - decline_value
    target_value = max(decline_value, trial_informed_value)
    target_choices = []
    if decline_value >= target_value - 1e-12:
        target_choices.append("DECLINE_TRIAL")
    if trial_informed_value >= target_value - 1e-12:
        target_choices.append("TRIAL")
    target_choices = tuple(target_choices)

    frontier_expected = (
        (1.0 - p_water) * decline_value
        + p_water * target_value)
    revelation_advantage = frontier_expected - decline_value
    if revelation_advantage < -1e-10:
        raise RuntimeError("water revelation cannot reduce optional value")
    if abs(revelation_advantage) < 1e-12:
        revelation_advantage = 0.0

    actual = CognitiveWork(*(
        getattr(budget.work, key) - getattr(original_work, key)
        for key in WORK_KEYS))
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_WATER_FRONTIER_OPTIONAL_TRIAL_ESTIMATE_NOT_POLICY",
        "water_probability": p_water,
        "non_water_probability_breakdown": dict(
            prior["non_target_probability_breakdown"]),
        "ordinary_frontier_value": decline_value,
        "ordinary_best_continuations": decline_best,
        "trial_frozen_value": trial_frozen_value,
        "trial_frozen_best_continuations": frozen_best,
        "trial_informed_value": trial_informed_value,
        "trial_information_value": trial_information_value,
        "trial_advantage": trial_advantage,
        "target_node_best_choices": target_choices,
        "frontier_expected_value": frontier_expected,
        "water_revelation_advantage": revelation_advantage,
        "effect_branch_best_values": tuple(branch_best),
        "prior_expected_external_delta": tuple(
            prior["expected_external_delta"]),
        "leaf_count": prior["leaf_count"],
        "branch_envelope": prior["branch_envelope"],
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
        "trial_is_optional": True,
        "unsupported_action": DRINK,
        "target_access_prefix": (TARGET_ENTRY,),
        "motor_command_authorized": False,
        "world_access": False,
        "cost_is_physical_settlement_receipt": False,
    }


__all__ = ["SCHEMA", "paid_water_frontier_optional_trial_value"]
