"""Experimental paid information-value kernel; not a live policy or a prior.

Only caller-supplied SUBJECTIVE forecasts belong here. The caller still has to
construct them from personal experience and justify observable signal classes.
No World access, action command, curiosity addend, sampling or state learning.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import fsum, isfinite
from typing import Protocol

from .body import CognitiveBudget, CognitiveWork, VITAL, debit_cognition

Vector = tuple[float, ...]
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")


class PersonalProjection(Protocol):
    gammas: tuple[float, ...]
    proj_chunks: tuple[int, ...]
    d_max: float

    def feats(self, body): ...
    def distress(self, features): ...
    def drift(self): ...
    def project(self, body, drift, budget=None): ...
    def value(self, index, features, projection): ...


@dataclass(frozen=True)
class SubjectiveOutcome:
    probability: float
    signal: str
    probe_delta: Vector
    continuations: tuple[tuple[str, Vector], ...]


def _vector(value) -> None:
    if (type(value) is not tuple or len(value) != 5 or
            any(type(x) not in (int, float) or not isfinite(x) or
                not -100 <= x <= 100 for x in value)):
        raise ValueError("five finite predicted channel deltas in [-100,100] required")


def _validate(outcomes) -> tuple[str, ...]:
    if type(outcomes) is not tuple or len(outcomes) not in (2, 3):
        raise ValueError("two or three explicit subjective outcomes required; no default prior")
    common = None
    for branch in outcomes:
        if not isinstance(branch, SubjectiveOutcome):
            raise ValueError("SubjectiveOutcome required")
        p = branch.probability
        if type(p) not in (int, float) or not isfinite(p) or not 0 < p <= 1:
            raise ValueError("strictly positive finite probabilities required")
        if type(branch.signal) is not str or not branch.signal:
            raise ValueError("explicit observable signal class required")
        _vector(branch.probe_delta)
        if type(branch.continuations) is not tuple or not branch.continuations:
            raise ValueError("nonempty common continuations required")
        names = []
        for item in branch.continuations:
            if type(item) is not tuple or len(item) != 2:
                raise ValueError("continuation must be an identifier/delta pair")
            name, delta = item
            if type(name) is not str or not name or name in names:
                raise ValueError("unique nonempty continuation identifiers required")
            names.append(name)
            _vector(delta)
        if common is None:
            common = set(names)
        elif common != set(names):
            raise ValueError("all outcomes need the same continuation set")
    if fsum(b.probability for b in outcomes) != 1.0:
        raise ValueError("probabilities must sum to one; no hidden normalization")
    return tuple(sorted(common))


def _add_work(a: CognitiveWork, b: CognitiveWork) -> CognitiveWork:
    return CognitiveWork(*(getattr(a, k) + getattr(b, k) for k in WORK_KEYS))


def _advance(body, delta) -> tuple:
    # A predicted death is absorbing, including on the probe's first step.
    if any(body[k] <= 0 for k in VITAL):
        return tuple(body)
    return tuple(min(100.0, max(0.0, x + d)) for x, d in zip(body, delta))


def _reward(model, body) -> float:
    return (-model.d_max if any(body[k] <= 0 for k in VITAL)
            else -model.distress(model.feats(body)))


def paid_information_value(model: PersonalProjection, outcomes: tuple[SubjectiveOutcome, ...],
                           budget: CognitiveBudget, *, perceive_cost: bool = True,
                           forecast_work: CognitiveWork | None = None,
                           cell_cache: dict | None = None) -> dict:
    """Score one probe and one contingent continuation in existing value units.

Both alternatives use the SAME paid payoff matrix: sum_o max_a sum_{b in o}
P(b) G(b,a), versus max_a sum_b P(b) G(b,a). Signals include the predicted
first-person body after the probe. No branching on any other hidden identity.

Costs are quoted after a paid preparation block, then consumed BEFORE each
actual computation. Forecasts include the quoted complete cost; exact work and
remaining body must reconcile on success. Failure returns no partial score,
refunds no executed work, and never authorizes a physical command. The runtime
must settle budget.work normally; an allowance is not a World debit receipt.
"""
    names = _validate(outcomes)
    if not isinstance(budget, CognitiveBudget) or type(perceive_cost) is not bool:
        raise ValueError("CognitiveBudget and boolean perceive_cost required")
    if any(budget.remaining[k] <= 0 for k in VITAL):
        raise ValueError("no information computation after physical death")
    if (len(model.gammas) != 3 or any(type(g) not in (int, float) or
            not isfinite(g) or not 0 < g < 1 for g in model.gammas) or
            not model.proj_chunks or any(type(n) is not int or n < 1 for n in model.proj_chunks)):
        raise ValueError("current three-horizon projection contract required")
    if forecast_work is not None and (
            not isinstance(forecast_work, CognitiveWork) or not perceive_cost):
        raise ValueError("common forecast work requires an actual-cost forecast")
    if cell_cache is not None and type(cell_cache) is not dict:
        raise ValueError("decision-local cell cache must be a plain dict")
    if cell_cache is not None and forecast_work is None:
        raise ValueError("cell reuse requires an explicit common forecast work ceiling")
    original_work, original_body = budget.work, budget.remaining
    cells = len(outcomes) * len(names)
    # One preparation block; scan probe/continuation vectors and signal weights.
    prep = CognitiveWork(cycles=1, memory_items=len(outcomes) * 7 + cells * 5)
    budget.spend(prep)
    drift = model.drift()
    # A caller may reuse exact matrix cells only within one decision. The
    # common forecast body remains based on the caller's exhaustive ceiling, so
    # cheaper execution cannot make an option look better merely by predicting
    # a cheaper body. The cache key contains only bodies derived from subjective
    # deltas; no World fact or outcome label enters it.
    forecast_body = original_body
    if forecast_work is not None:
        forecast_body, _ = debit_cognition(budget.body, budget.laws, forecast_work)
    planned = []
    seen_misses = set()
    miss_count = 0
    for branch in outcomes:
        effects = dict(branch.continuations)
        row = []
        for name in names:
            first = _advance(forecast_body, branch.probe_delta)
            second = _advance(first, effects[name])
            key = (first, second)
            cached = cell_cache is not None and key in cell_cache
            if cell_cache is not None and not cached and key not in seen_misses:
                seen_misses.add(key)
                miss_count += 1
            elif cell_cache is None:
                miss_count += 1
            row.append((name, first, second, key, cached))
        planned.append(row)
    remaining_work = CognitiveWork(
        cycles=miss_count + 1,
        simulated_steps=miss_count * (2 + len(model.proj_chunks)))
    quoted_work = _add_work(budget.work, remaining_work)
    quoted_body, _ = debit_cognition(budget.body, budget.laws, quoted_work)
    if forecast_work is None:
        forecast_body = quoted_body if perceive_cost else original_body
        # No cache is allowed on this path, so planned bodies were only a work
        # count prepass. Rebuild them from the actual forecast body below.
        planned = []
        for branch in outcomes:
            effects = dict(branch.continuations)
            row = []
            for name in names:
                first = _advance(forecast_body, branch.probe_delta)
                second = _advance(first, effects[name])
                row.append((name, first, second, None, False))
            planned.append(row)
    elif any(getattr(forecast_work, k) < getattr(quoted_work, k) for k in WORK_KEYS):
        raise ValueError("common forecast cannot omit this call's actual work")
    values, groups = [], {}
    reused = 0
    for branch, planned_row in zip(outcomes, planned):
        row = []
        for name, first, second, key, cached in planned_row:
            if cached:
                value = cell_cache[key]
                reused += 1
            else:
                budget.spend(CognitiveWork(cycles=1, simulated_steps=2))
                # Still execute/pay the geometric projection for terminal
                # branches, using an absorbing forecast, never revival through
                # learned sleep.
                dead = any(second[k] <= 0 for k in VITAL)
                projection, _ = model.project(
                    second, ((0.0,) * 5, None) if dead else drift, budget)
                phi = model.feats(second)
                r_first, r_second = _reward(model, first), _reward(model, second)
                value = fsum((1 - g) * (r_first + g * (r_second + g * (
                    -model.d_max / (1 - g) if dead else model.value(k, phi, projection))))
                             for k, g in enumerate(model.gammas)) / 3
                if not isfinite(value):
                    raise ValueError("nonfinite subjective projection; no valid score")
                if cell_cache is not None:
                    cell_cache[key] = value
            row.append(value)
        values.append(row)
        # Body channels are directly perceived by current I3. An unseen latent
        # outcome index is NOT an observation; its label cannot select a plan.
        signal = (branch.signal, first)
        groups.setdefault(signal, []).append(len(values) - 1)
    budget.spend(CognitiveWork(cycles=1))
    means = [fsum(b.probability * values[i][j] for i, b in enumerate(outcomes))
             for j in range(len(names))]
    uninformed = max(means)
    informed_parts, choices = [], []
    for (signal, body), indices in sorted(groups.items()):
        joint = [fsum(outcomes[i].probability * values[i][j] for i in indices)
                 for j in range(len(names))]
        best = max(joint)
        informed_parts.append(best)
        choices.append({"signal": signal, "predicted_body": body,
                        "probability": fsum(outcomes[i].probability for i in indices),
                        "best_continuations": tuple(n for n, v in zip(names, joint) if v == best)})
    informed = fsum(informed_parts)
    if budget.work != quoted_work or budget.remaining != quoted_body:
        raise RuntimeError("executed computation differs from its funded quote")
    work = CognitiveWork(*(getattr(budget.work, k) - getattr(original_work, k) for k in WORK_KEYS))
    return {"schema": "i3-paid-information-kernel/v1", "status": "COMPLETE_SUBJECTIVE_ESTIMATE_NOT_POLICY",
            "informed_value": informed, "uninformed_value": uninformed,
            "information_value": informed - uninformed,
            "common_best_continuations": tuple(n for n, v in zip(names, means) if v == uninformed),
            "conditional_choices": choices, "continuation_order": names,
            "branch_values": values, "work": asdict(work),
            "cell_reuse": {"computed": miss_count, "reused": reused,
                           "cache_size": len(cell_cache) if cell_cache is not None else 0},
            "body_after_computation": budget.remaining, "forecast_start_body": forecast_body,
            "perceived_incremental_cost": "actual" if perceive_cost else "zero_diagnostic_still_payable",
            "cost_is_physical_settlement_receipt": False}
