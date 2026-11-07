"""Paid information value over explicit P1.3 continuation plans; not a policy.

The caller supplies every subjective probe outcome and every continuation plan.
This module never invents an exploration outcome, reads World, changes a map or
chooses an action. It only asks whether an observed bodily outcome would change
which already-specified P1.3 plan minimizes predicted personal distress.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import fsum, isfinite

from .body import ACTIONS, CognitiveBudget, CognitiveWork, VITAL, debit_cognition
from .information_value import WORK_KEYS, _add_work, _advance

Vector = tuple[float, ...]


@dataclass(frozen=True)
class PlanSubjectiveOutcome:
    probability: float
    signal: str
    probe_delta: Vector


def _validate_delta(value) -> None:
    if (type(value) is not tuple or len(value) != 5 or
            any(type(x) not in (int, float) or not isfinite(x) or
                not -100 <= x <= 100 for x in value)):
        raise ValueError("five finite predicted channel deltas in [-100,100] required")


def _validate_plan(plan) -> None:
    if type(plan) is not tuple or not plan:
        raise ValueError("nonempty immutable P1.3 continuation plan required")
    for key in plan:
        if (type(key) is not tuple or len(key) not in (1, 2) or
                type(key[0]) is not str or key[0] not in ACTIONS):
            raise ValueError("plan action key required")
        if len(key) == 2 and (type(key[1]) is not str or not key[1]):
            raise ValueError("nonempty internal token required")
        if len(key) == 1 and key[0] in ("manger", "collecter"):
            raise ValueError("resource plan action requires internal token")
        if len(key) == 2 and key[0] not in ("manger", "collecter"):
            raise ValueError("only resource actions carry an internal token")


def _validate(outcomes, continuations, horizon):
    if type(outcomes) is not tuple or len(outcomes) not in (2, 3):
        raise ValueError("two or three explicit subjective outcomes required")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer simulation horizon required")
    for branch in outcomes:
        if not isinstance(branch, PlanSubjectiveOutcome):
            raise ValueError("PlanSubjectiveOutcome required")
        if (type(branch.probability) not in (int, float) or
                not isfinite(branch.probability) or
                not 0 < branch.probability <= 1):
            raise ValueError("strictly positive finite probability required")
        if type(branch.signal) is not str or not branch.signal:
            raise ValueError("explicit observable signal class required")
        _validate_delta(branch.probe_delta)
    if fsum(b.probability for b in outcomes) != 1.0:
        raise ValueError("probabilities must sum to one; no hidden normalization")
    if type(continuations) is not tuple or not continuations:
        raise ValueError("explicit continuation plans required")
    names = []
    plans = {}
    for item in continuations:
        if type(item) is not tuple or len(item) != 2:
            raise ValueError("continuation identifier/plan pair required")
        name, plan = item
        if type(name) is not str or not name or name in names:
            raise ValueError("unique nonempty continuation identifier required")
        _validate_plan(plan)
        names.append(name)
        plans[name] = plan
    return tuple(sorted(names)), plans


def _minimum_ceiling(model, outcomes, plans, horizon, original_work):
    """Conservative full-matrix work bound, not a Stage-2 budget choice."""
    cells = len(outcomes) * len(plans)
    plan_items = sum(len(plan) for plan in plans.values())
    prep = CognitiveWork(
        cycles=1,
        memory_items=len(outcomes) * 7 + cells * 5 + 2 * plan_items)
    # Mind.simulate spends at most one simulated unit per explicit plan item
    # before its geometric projection. Consecutive moves may cost less, and
    # predicted death may skip projection; the common forecast never relies on
    # those favorable early exits.
    per_branch_sim = sum(
        min(len(plan), horizon) + len(model.proj_chunks)
        for plan in plans.values())
    remainder = CognitiveWork(
        cycles=cells + 1,
        simulated_steps=len(outcomes) * per_branch_sim)
    return prep, _add_work(original_work, _add_work(prep, remainder))


def paid_plan_information_value(model, outcomes, continuations, horizon,
                                budget: CognitiveBudget, *,
                                forecast_work: CognitiveWork | None = None) -> dict:
    """Evaluate contingent re-planning over explicit existing P1.3 plans.

Every branch-plan cell is actually executed through model.simulate unless the
subjective probe body is already dead, which is absorbing. All cells share one
conservative forecast body based on the complete matrix ceiling. The
calculation cannot stop early because one branch/plan looks favorable.

forecast_work is an optional cumulative common decision-work ceiling. A caller
comparing several probes can provide one larger shared ceiling; it may not
understate this call's complete matrix bound.
"""
    names, plans = _validate(outcomes, continuations, horizon)
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0 for k in VITAL):
        raise ValueError("no information computation after physical death")
    if (not hasattr(model, "simulate") or not hasattr(model, "proj_chunks") or
            not model.proj_chunks or
            any(type(n) is not int or n < 1 for n in model.proj_chunks) or
            not hasattr(model, "d_max") or not isfinite(model.d_max)):
        raise ValueError("current P1.3 simulation model required")
    if forecast_work is not None and not isinstance(forecast_work, CognitiveWork):
        raise ValueError("forecast_work must be CognitiveWork")

    original_work = budget.work
    prep, minimum = _minimum_ceiling(
        model, outcomes, plans, horizon, original_work)
    budget.spend(prep)
    after_prep = budget.work

    ceiling = minimum if forecast_work is None else forecast_work
    if any(getattr(ceiling, k) < getattr(minimum, k) for k in WORK_KEYS):
        raise ValueError("common forecast cannot omit complete plan-matrix work")
    forecast_body, _ = debit_cognition(budget.body, budget.laws, ceiling)

    values = []
    groups = {}
    for branch in outcomes:
        first = _advance(forecast_body, branch.probe_delta)
        row = []
        for name in names:
            budget.spend(CognitiveWork(cycles=1))
            if any(first[k] <= 0 for k in VITAL):
                value = -model.d_max
            else:
                value, _, _ = model.simulate(
                    first, plans[name], horizon, budget)
            if type(value) not in (int, float) or not isfinite(value):
                raise ValueError("nonfinite subjective plan value")
            row.append(value)
            if any(getattr(budget.work, k) > getattr(ceiling, k)
                   for k in WORK_KEYS):
                raise RuntimeError("plan information work exceeded its funded ceiling")
        values.append(row)
        groups.setdefault((branch.signal, first), []).append(len(values) - 1)

    after_cells = budget.work
    budget.spend(CognitiveWork(cycles=1))
    if any(getattr(budget.work, k) > getattr(ceiling, k) for k in WORK_KEYS):
        raise RuntimeError("plan information reduction exceeded its funded ceiling")

    means = [
        fsum(branch.probability * values[i][j]
             for i, branch in enumerate(outcomes))
        for j in range(len(names))
    ]
    uninformed = max(means)
    informed_parts = []
    choices = []
    for (signal, body), indices in sorted(groups.items()):
        joint = [
            fsum(outcomes[i].probability * values[i][j] for i in indices)
            for j in range(len(names))
        ]
        best = max(joint)
        informed_parts.append(best)
        choices.append({
            "signal": signal,
            "predicted_body": body,
            "probability": fsum(outcomes[i].probability for i in indices),
            "best_continuations": tuple(
                name for name, value in zip(names, joint) if value == best),
        })
    informed = fsum(informed_parts)

    def delta(after, before):
        return {k: getattr(after, k) - getattr(before, k) for k in WORK_KEYS}

    actual = CognitiveWork(*(
        getattr(budget.work, k) - getattr(original_work, k)
        for k in WORK_KEYS))
    return {
        "schema": "i3-paid-plan-information/v1",
        "status": "COMPLETE_SUBJECTIVE_ESTIMATE_NOT_POLICY",
        "informed_value": informed,
        "uninformed_value": uninformed,
        "information_value": informed - uninformed,
        "common_best_continuations": tuple(
            name for name, value in zip(names, means) if value == uninformed),
        "conditional_choices": choices,
        "continuation_order": names,
        "branch_values": values,
        "work": asdict(actual),
        "work_breakdown": {
            "preparation": delta(after_prep, original_work),
            "plan_matrix": delta(after_cells, after_prep),
            "reduction": delta(budget.work, after_cells),
            "total": asdict(actual),
        },
        "minimum_complete_forecast_work": asdict(minimum),
        "forecast_work_ceiling": asdict(ceiling),
        "forecast_start_body": forecast_body,
        "body_after_computation": budget.remaining,
        "cost_is_physical_settlement_receipt": False,
        "outcome_generation": "CALLER_SUPPLIED_PERSONAL_BELIEFS_ONLY",
    }


@dataclass(frozen=True)
class RevealedPlanOutcome:
    """Subjective probe outcome plus plans exposed by that observable result."""
    probability: float
    signal: str
    probe_delta: Vector
    revealed_continuations: tuple = ()


def _continuation_dict(items, *, allow_empty):
    if type(items) is not tuple or (not allow_empty and not items):
        raise ValueError("explicit immutable continuation tuple required")
    names = []
    plans = {}
    for item in items:
        if type(item) is not tuple or len(item) != 2:
            raise ValueError("continuation identifier/plan pair required")
        name, plan = item
        if type(name) is not str or not name or name in names:
            raise ValueError("unique nonempty continuation identifier required")
        _validate_plan(plan)
        names.append(name)
        plans[name] = plan
    return plans


def _validate_revealed(outcomes, common_continuations, horizon):
    if type(outcomes) is not tuple or len(outcomes) not in (2, 3):
        raise ValueError("two or three explicit subjective outcomes required")
    if type(horizon) is not int or horizon < 1:
        raise ValueError("positive integer simulation horizon required")
    common = _continuation_dict(common_continuations, allow_empty=False)
    revealed = []
    total = 0.0
    for branch in outcomes:
        if not isinstance(branch, RevealedPlanOutcome):
            raise ValueError("RevealedPlanOutcome required")
        if (type(branch.probability) not in (int, float) or
                not isfinite(branch.probability) or
                not 0 < branch.probability <= 1):
            raise ValueError("strictly positive finite probability required")
        if type(branch.signal) is not str or not branch.signal:
            raise ValueError("explicit observable signal class required")
        _validate_delta(branch.probe_delta)
        plans = _continuation_dict(
            branch.revealed_continuations, allow_empty=True)
        if set(plans) & set(common):
            raise ValueError("revealed continuation cannot shadow a common plan")
        revealed.append(plans)
        total += branch.probability
    if abs(total - 1.0) > 1e-12:
        raise ValueError("probabilities must sum to one; no hidden normalization")
    return common, tuple(revealed)


def _revealed_minimum_ceiling(
        model, outcomes, common, revealed, horizon, original_work):
    cells = 0
    plan_items = 0
    simulated = 0
    for plans in revealed:
        available = {**common, **plans}
        cells += len(available)
        plan_items += sum(len(plan) for plan in available.values())
        simulated += sum(
            min(len(plan), horizon) + len(model.proj_chunks)
            for plan in available.values())
    prep = CognitiveWork(
        cycles=1,
        memory_items=len(outcomes) * 7 + cells * 5 + 2 * plan_items)
    remainder = CognitiveWork(
        cycles=cells + 1,
        simulated_steps=simulated)
    return prep, _add_work(original_work, _add_work(prep, remainder))


def paid_revealed_plan_information_value(
        model, outcomes, common_continuations, horizon,
        budget: CognitiveBudget, *,
        forecast_work: CognitiveWork | None = None) -> dict:
    """Value information that can reveal new P1.3 continuation plans.

    The uninformed comparator can choose only from common_continuations.
    After an observable result, the informed comparator can choose from those
    common plans plus the plans explicitly revealed by that result.

    Hidden branch identity never grants a plan. If two outcomes collapse to the
    same observable (signal, predicted body), their available plan dictionaries
    must be identical or the calculation fails closed.

    The complete branch-specific matrix is conservatively quoted before any
    plan cell executes. There is no early stop and no value-of-computation rule.
    """
    common, revealed = _validate_revealed(
        outcomes, common_continuations, horizon)
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0 for k in VITAL):
        raise ValueError("no information computation after physical death")
    if (not hasattr(model, "simulate") or not hasattr(model, "proj_chunks") or
            not model.proj_chunks or
            any(type(n) is not int or n < 1 for n in model.proj_chunks) or
            not hasattr(model, "d_max") or not isfinite(model.d_max)):
        raise ValueError("current P1.3 simulation model required")
    if forecast_work is not None and not isinstance(forecast_work, CognitiveWork):
        raise ValueError("forecast_work must be CognitiveWork")

    original_work = budget.work
    prep, minimum = _revealed_minimum_ceiling(
        model, outcomes, common, revealed, horizon, original_work)
    budget.spend(prep)
    after_prep = budget.work

    ceiling = minimum if forecast_work is None else forecast_work
    if any(getattr(ceiling, k) < getattr(minimum, k) for k in WORK_KEYS):
        raise ValueError("common forecast cannot omit complete revealed-plan matrix")
    forecast_body, _ = debit_cognition(budget.body, budget.laws, ceiling)

    prepared = []
    observable_plans = {}
    for branch, extra in zip(outcomes, revealed):
        first = _advance(forecast_body, branch.probe_delta)
        available = {**common, **extra}
        canonical = tuple(sorted(available.items()))
        observable = (branch.signal, first)
        old = observable_plans.get(observable)
        if old is None:
            observable_plans[observable] = canonical
        elif old != canonical:
            raise ValueError(
                "indistinguishable outcomes cannot reveal different plans")
        prepared.append((first, available, observable))

    rows = []
    groups = {}
    for index, (branch, prepared_row) in enumerate(zip(outcomes, prepared)):
        first, available, observable = prepared_row
        row = {}
        for name in sorted(available):
            plan = available[name]
            budget.spend(CognitiveWork(cycles=1))
            if any(first[k] <= 0 for k in VITAL):
                value = -model.d_max
            else:
                value, _, _ = model.simulate(
                    first, plan, horizon, budget)
            if type(value) not in (int, float) or not isfinite(value):
                raise ValueError("nonfinite subjective plan value")
            row[name] = value
            if any(getattr(budget.work, k) > getattr(ceiling, k)
                   for k in WORK_KEYS):
                raise RuntimeError(
                    "revealed-plan information work exceeded funded ceiling")
        rows.append(row)
        groups.setdefault(observable, []).append(index)

    after_cells = budget.work
    budget.spend(CognitiveWork(cycles=1))
    if any(getattr(budget.work, k) > getattr(ceiling, k)
           for k in WORK_KEYS):
        raise RuntimeError(
            "revealed-plan reduction exceeded its funded ceiling")

    common_names = tuple(sorted(common))
    common_means = {
        name: fsum(
            branch.probability * rows[i][name]
            for i, branch in enumerate(outcomes))
        for name in common_names
    }
    uninformed = max(common_means.values())
    common_best = tuple(
        name for name in common_names if common_means[name] == uninformed)

    informed_parts = []
    choices = []
    for observable, indices in sorted(groups.items()):
        signal, body = observable
        names = tuple(name for name, _ in observable_plans[observable])
        joint = {
            name: fsum(
                outcomes[i].probability * rows[i][name]
                for i in indices)
            for name in names
        }
        best = max(joint.values())
        informed_parts.append(best)
        choices.append({
            "signal": signal,
            "predicted_body": body,
            "probability": fsum(outcomes[i].probability for i in indices),
            "available_continuations": names,
            "best_continuations": tuple(
                name for name in names if joint[name] == best),
        })
    informed = fsum(informed_parts)

    def delta(after, before):
        return {k: getattr(after, k) - getattr(before, k) for k in WORK_KEYS}

    actual = CognitiveWork(*(
        getattr(budget.work, k) - getattr(original_work, k)
        for k in WORK_KEYS))
    return {
        "schema": "i3-paid-revealed-plan-information/v1",
        "status": "COMPLETE_SUBJECTIVE_ESTIMATE_NOT_POLICY",
        "informed_value": informed,
        "uninformed_value": uninformed,
        "information_value": informed - uninformed,
        "common_best_continuations": common_best,
        "conditional_choices": choices,
        "common_continuation_order": common_names,
        "branch_values": tuple(
            tuple(sorted(row.items())) for row in rows),
        "work": asdict(actual),
        "work_breakdown": {
            "preparation": delta(after_prep, original_work),
            "plan_matrix": delta(after_cells, after_prep),
            "reduction": delta(budget.work, after_cells),
            "total": asdict(actual),
        },
        "minimum_complete_forecast_work": asdict(minimum),
        "forecast_work_ceiling": asdict(ceiling),
        "forecast_start_body": forecast_body,
        "body_after_computation": budget.remaining,
        "cost_is_physical_settlement_receipt": False,
        "outcome_generation": "CALLER_SUPPLIED_PERSONAL_BELIEFS_ONLY",
        "revealed_plan_semantics": "OBSERVABLE_GROUP_ONLY",
    }
