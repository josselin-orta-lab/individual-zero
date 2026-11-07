"""Paid counterfactual simulation after one explicitly observed action effect.

Software primitive only. The real Mind is never mutated. One exact action key
may read one explicitly observed five-channel delta with zero uncertainty inside
the counterfactual branch; all other prediction reads delegate to the unchanged
owner model.

This deliberately does not emulate the whole P1.3 learning pipeline. In
particular it does not update action-level/global fallbacks, TD values, replay
memory, map state or any other action.
"""
from __future__ import annotations

from math import isfinite

from .body import CognitiveBudget, CognitiveWork, VITAL, validate_body
from .information_value import WORK_KEYS
from .plan_information import _validate_delta, _validate_plan

SCHEMA = "i3-observed-effect-view/v1"
VIEW_WORK = CognitiveWork(cycles=1, memory_items=7)


def _work_delta(after, before):
    return {
        key: getattr(after, key) - getattr(before, key)
        for key in WORK_KEYS
    }


class _ObservedEffectView:
    __slots__ = (
        "_owner", "_effect_key", "_effect_delta",
        "observer_decision_diagnostics", "_observer_first_forecast",
    )

    def __init__(self, owner, effect_key, effect_delta):
        self._owner = owner
        self._effect_key = effect_key
        self._effect_delta = effect_delta
        self.observer_decision_diagnostics = bool(
            getattr(owner, "observer_decision_diagnostics", False))
        self._observer_first_forecast = None

    def __getattr__(self, name):
        return getattr(self._owner, name)

    def _read_plan_prediction(self, key):
        if tuple(key) == self._effect_key:
            return self._effect_delta, 0.0
        return self._owner._read_plan_prediction(key)

    def _simulate_candidate_f(self, body, plan, horizon, budget):
        """Preserve this proxy through Candidate F helper dispatch."""
        helper = getattr(self._owner, "_simulate_candidate_f", None)
        function = getattr(helper, "__func__", None)
        if not callable(function):
            raise ValueError("candidate_f helper unavailable on owner model")
        return function(self, body, plan, horizon, budget)


def paid_simulate_after_observed_effect(
        model, body, plan, horizon, effect_key, effect_delta,
        budget: CognitiveBudget, *, work_receipt: dict | None = None) -> dict:
    """Run the existing simulator through one exact observed-effect view.

    The caller must already have obtained effect_delta from an observable
    subjective branch. This helper does not generate an effect and cannot use a
    hidden branch identity.

    VIEW_WORK pays construction/readout of the exact key+delta view.
    Subsequent simulation work is whatever the existing model simulator really
    spends. A future comparison must include both in its common forecast
    ceiling; this helper does not create that ceiling itself.
    """
    predicted_body = validate_body(body)
    if any(predicted_body[k] <= 0.0 for k in VITAL):
        raise ValueError("no continuation simulation after predicted death")
    _validate_plan(plan)
    _validate_plan((effect_key,))
    _validate_delta(effect_delta)
    effect_key = tuple(effect_key)
    effect_delta = tuple(float(x) for x in effect_delta)

    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer simulation horizon required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no counterfactual cognition after physical death")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    simulator = getattr(model, "simulate", None)
    read_prediction = getattr(model, "_read_plan_prediction", None)
    if (not callable(simulator) or
            not callable(getattr(simulator, "__func__", None)) or
            not callable(read_prediction)):
        raise ValueError("current P1.3-compatible simulator required")
    if (not hasattr(model, "proj_chunks") or not model.proj_chunks or
            not hasattr(model, "d_max") or
            type(model.d_max) not in (int, float) or
            not isfinite(model.d_max)):
        raise ValueError("complete P1.3-compatible model state required")

    before = budget.work
    budget.spend(VIEW_WORK)
    after_view = budget.work

    view = _ObservedEffectView(model, effect_key, effect_delta)
    value, steps, uncertainty = simulator.__func__(
        view, predicted_body, plan, horizon, budget)

    if (type(value) not in (int, float) or not isfinite(value) or
            type(steps) is not int or steps < 0 or
            type(uncertainty) not in (int, float) or
            not isfinite(uncertainty)):
        raise ValueError("invalid counterfactual simulation result")

    result = {
        "schema": SCHEMA,
        "status": "COMPLETE_EXACT_OBSERVED_EFFECT_VIEW",
        "effect_key": effect_key,
        "effect_delta": effect_delta,
        "value": value,
        "simulated_plan_steps": steps,
        "max_uncertainty": uncertainty,
        "first_forecast": (
            view._observer_first_forecast
            if view.observer_decision_diagnostics else None),
        "work": _work_delta(budget.work, before),
        "work_breakdown": {
            "view": _work_delta(after_view, before),
            "simulation": _work_delta(budget.work, after_view),
            "total": _work_delta(budget.work, before),
        },
        "model_mutation_authorized": False,
        "cross_action_transfer": False,
        "world_access": False,
        "cost_is_physical_settlement_receipt": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-observed-effect-view-work/v1",
            "status": result["status"],
            "work": dict(result["work"]),
        })
    return result


__all__ = [
    "SCHEMA", "VIEW_WORK", "paid_simulate_after_observed_effect",
]
