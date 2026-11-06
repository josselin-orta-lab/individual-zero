"""Paid empirical bodily hypotheses for Stage 1, not a live policy.

Only own applied-action outcomes enter this private bounded history. The recent
empirical window and same-key persistence are fallible modelling assumptions,
not calibrated uncertainty, hidden World effects or action admissibility.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import fsum, isfinite

from .body import (ACTIONS, CognitiveBudget, CognitiveWork, E, V, VITAL,
                   debit_cognition)
from .information_value import (PersonalProjection, SubjectiveOutcome,
                                WORK_KEYS, paid_information_value)

EffectKey = tuple[str, str | None]
Vector = tuple[float, ...]
WINDOW = 3
STORE_WORK = CognitiveWork(cycles=1, memory_items=16)


class NoPersonalSupport(ValueError):
    """No experienced outcome for this action; never a zero/favorable score."""


def _key(value: EffectKey) -> None:
    if (type(value) is not tuple or len(value) != 2 or
            type(value[0]) is not str or value[0] not in ACTIONS):
        raise ValueError("physical action and internal token key required")
    if value[0] in ("manger", "collecter"):
        if type(value[1]) is not str or not value[1]:
            raise ValueError("resource action requires a personal token identifier")
    elif value[1] is not None:
        raise ValueError("only token actions have a token identifier")


def _body(body) -> tuple:
    if (type(body) not in (tuple, list) or len(body) != 5 or
            any(type(x) not in (int, float) or not isfinite(x) or
                not 0 <= x <= 100 for x in body)):
        raise ValueError("five finite bodily channels required")
    return tuple(body)


def _alive_budget(budget: CognitiveBudget) -> None:
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0 for k in VITAL):
        raise ValueError("no personal computation after death")


@dataclass(frozen=True)
class _ExperiencedEffect:
    key: EffectKey
    delta: Vector


class PersonalOutcomes:
    """Empty at birth. Capacity must later be bound to the candidate's genome.

No old EffectsModel means are imported: they already include historical
cognitive charges and do not supply an empirical outcome distribution.
"""

    def __init__(self, capacity: int):
        if type(capacity) is not int or not 1 <= capacity <= 512:
            raise ValueError("explicit capacity in 1..512 required")
        self._samples: deque[_ExperiencedEffect] = deque(maxlen=capacity)

    def observe(self, key: EffectKey, before: Vector,
                decision_work: CognitiveWork, budget: CognitiveBudget) -> None:
        """Remember an applied outcome BEFORE learning, under a fresh allowance.

before is the personal pre-decision body; budget.body is the post-physics,
pre-learning body. decision_work is the individual's actually settled decision
work. The caller owns this binding; these inputs cannot authenticate a history.
Only that known decision debit is removed from the observed delta. This does
not undo clipping, estimate unclipped gains, or identify intrinsic causal laws.
The caller must physically settle the new learning allowance exactly once.
"""
        _key(key)
        before = _body(before)
        _alive_budget(budget)
        if budget.work != CognitiveWork() or any(before[k] <= 0 for k in VITAL):
            raise ValueError("fresh pre-learning allowance and living predecessor required")
        if not isinstance(decision_work, CognitiveWork):
            raise ValueError("actual decision work required")
        # Validate affordability from the original body, not future recovery.
        _, bill = debit_cognition(before, budget.laws, decision_work)
        budget.spend(STORE_WORK)
        delta = [after - prior for after, prior in zip(budget.body, before)]
        delta[E] += bill["energy"]["paid"]
        delta[V] += bill["vigilance"]["paid"]
        self._samples.append(_ExperiencedEffect(key, tuple(delta)))

    def _support(self, key: EffectKey) -> tuple[Vector, ...]:
        # Called only after funding a complete scan. No preference by sign,
        # current need, world name or token spelling; exact key precedes action.
        exact, same_action = deque(maxlen=WINDOW), deque(maxlen=WINDOW)
        for sample in self._samples:
            if sample.key[0] == key[0]:
                same_action.append(sample.delta)
                if sample.key == key:
                    exact.append(sample.delta)
        support = exact or same_action
        if not support:
            raise NoPersonalSupport("NO_PERSONAL_SUPPORT for action " + key[0])
        return tuple(support)

    def construct(self, probe: EffectKey,
                  continuations: tuple[tuple[str, EffectKey], ...],
                  budget: CognitiveBudget) -> tuple[SubjectiveOutcome, ...]:
        """Construct two/three hypotheses, all with a body-only observation.

Latest <=3 exact-key samples; otherwise latest <=3 same-action samples. No
cross-action/global fallback or invented newborn prior. One sample is split
into two identical half-weight branches solely for the kernel's closed API.
Repeating probe shares its hypothetical effect; other keys use their personal
mean. This persistence approximation is not a learned change detector.
"""
        _key(probe)
        _alive_budget(budget)
        if type(continuations) is not tuple or not continuations:
            raise ValueError("explicit nonempty continuation tuple required")
        names = set()
        for item in continuations:
            if type(item) is not tuple or len(item) != 2:
                raise ValueError("continuation identifier/key pair required")
            name, key = item
            if type(name) is not str or not name or name in names:
                raise ValueError("unique continuation identifiers required")
            _key(key)
            names.add(name)
        budget.spend(CognitiveWork(cycles=1, memory_items=2 + 3 * len(names)))
        keys = tuple(dict.fromkeys((probe, *(key for _, key in continuations))))
        supports = {}
        for key in keys:
            budget.spend(CognitiveWork(cycles=1, memory_items=7 * len(self._samples) + 2))
            supports[key] = self._support(key)
        count = max(2, len(supports[probe]))
        budget.spend(CognitiveWork(
            cycles=1, memory_items=5 * sum(map(len, supports.values())) +
            count * (7 + 5 * len(names))))
        means = {key: tuple(fsum(x[c] for x in rows) / len(rows) for c in range(5))
                 for key, rows in supports.items()}
        probes = supports[probe]
        if len(probes) == 1:
            probes = probes * 2
        return tuple(SubjectiveOutcome(
            1.0 / count, "body_only", delta,
            tuple((name, delta if key == probe else means[key])
                  for name, key in continuations)) for delta in probes)


def paid_personal_information(model: PersonalProjection, history: PersonalOutcomes,
                              probe: EffectKey,
                              continuations: tuple[tuple[str, EffectKey], ...],
                              budget: CognitiveBudget, *, perceive_cost: bool = True) -> dict:
    """Construct from personal history and execute the unchanged paid kernel.

No command is emitted. The diagnostic ignores only the kernel's incremental
cost: construction is prior actual spending and remains in both forecasts.
On any failure, consumed work remains in budget; no partial score is returned.
"""
    if type(perceive_cost) is not bool or not isinstance(history, PersonalOutcomes):
        raise ValueError("personal history and boolean cost flag required")
    _alive_budget(budget)
    start = budget.work
    outcomes = history.construct(probe, continuations, budget)
    built = budget.work
    result = paid_information_value(model, outcomes, budget, perceive_cost=perceive_cost)
    result["personal_outcome_model"] = "recent_empirical_same_key_persistence_v1"
    result["construction_work"] = {
        k: getattr(built, k) - getattr(start, k) for k in WORK_KEYS}
    result["total_work"] = {
        k: getattr(budget.work, k) - getattr(start, k) for k in WORK_KEYS}
    return result
