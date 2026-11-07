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


class _DecisionSupportIndex:
    """Ephemeral same-decision history index, invalidated by any new sample."""

    __slots__ = ("owner", "version", "exact", "same_action", "built")

    def __init__(self, owner: int, version: int):
        self.owner = owner
        self.version = version
        self.exact = {}
        self.same_action = {}
        self.built = False


class PersonalOutcomes:
    """Empty at birth. Capacity must later be bound to the candidate's genome.

No old EffectsModel means are imported: they already include historical
cognitive charges and do not supply an empirical outcome distribution.
"""

    def __init__(self, capacity: int):
        if type(capacity) is not int or not 1 <= capacity <= 512:
            raise ValueError("explicit capacity in 1..512 required")
        self._samples: deque[_ExperiencedEffect] = deque(maxlen=capacity)
        self._version = 0

    def begin_support_index(self):
        """Create an empty ephemeral index token; no history work happens here."""
        return _DecisionSupportIndex(id(self), self._version)

    def _check_support_index(self, index) -> None:
        if not isinstance(index, _DecisionSupportIndex):
            raise ValueError("decision support index required")
        if index.owner != id(self):
            raise ValueError("support index belongs to another personal history")
        if index.version != self._version:
            raise ValueError("stale decision support index")

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
        self._version += 1

    def _missing_support(self, key: EffectKey) -> tuple[Vector, ...]:
        raise NoPersonalSupport("NO_PERSONAL_SUPPORT for action " + key[0])

    def _supports(self, keys: tuple[EffectKey, ...]) -> dict[EffectKey, tuple[Vector, ...]]:
        """Resolve many keys from one history pass, preserving old precedence/order."""
        if type(keys) is not tuple or not keys:
            raise ValueError("nonempty effect-key tuple required")
        for key in keys:
            _key(key)
        exact = {key: deque(maxlen=WINDOW) for key in keys}
        actions = {key[0] for key in keys}
        same_action = {action: deque(maxlen=WINDOW) for action in actions}
        for sample in self._samples:
            if sample.key[0] in same_action:
                same_action[sample.key[0]].append(sample.delta)
            if sample.key in exact:
                exact[sample.key].append(sample.delta)
        result = {}
        for key in keys:
            support = exact[key] or same_action[key[0]]
            result[key] = tuple(support) if support else self._missing_support(key)
        return result

    def _build_support_index(self, index: _DecisionSupportIndex) -> None:
        self._check_support_index(index)
        exact, same_action = {}, {}
        for sample in self._samples:
            exact.setdefault(sample.key, deque(maxlen=WINDOW)).append(sample.delta)
            same_action.setdefault(sample.key[0], deque(maxlen=WINDOW)).append(sample.delta)
        index.exact = {key: tuple(rows) for key, rows in exact.items()}
        index.same_action = {key: tuple(rows) for key, rows in same_action.items()}
        index.built = True

    def _indexed_supports(self, keys: tuple[EffectKey, ...],
                          index: _DecisionSupportIndex) -> dict[EffectKey, tuple[Vector, ...]]:
        self._check_support_index(index)
        if not index.built:
            raise ValueError("support index has not been paid and built")
        result = {}
        for key in keys:
            _key(key)
            support = index.exact.get(key) or index.same_action.get(key[0])
            result[key] = support if support else self._missing_support(key)
        return result

    def _support(self, key: EffectKey) -> tuple[Vector, ...]:
        return self._supports((key,))[key]

    def construct(self, probe: EffectKey,
                  continuations: tuple[tuple[str, EffectKey], ...],
                  budget: CognitiveBudget, *,
                  work_receipt: dict | None = None,
                  support_index=None) -> tuple[SubjectiveOutcome, ...]:
        """Construct two/three hypotheses, all with a body-only observation.

Latest <=3 exact-key samples; otherwise latest <=3 same-action samples. No
cross-action/global fallback or invented newborn prior. One sample is split
into two identical half-weight branches solely for the kernel's closed API.
Repeating probe shares its hypothetical effect; other keys use their personal
mean. This persistence approximation is not a learned change detector.
"""
        _key(probe)
        _alive_budget(budget)
        if work_receipt is not None and type(work_receipt) is not dict:
            raise ValueError("work_receipt must be a plain dict")
        if support_index is not None:
            self._check_support_index(support_index)
        zero_work = {k: 0 for k in WORK_KEYS}
        start_work = budget.work
        if work_receipt is not None:
            work_receipt.clear()
            work_receipt.update({
                "schema": "i3-personal-construction-work/v1",
                "status": "STARTED",
                "phase": "validate",
                "setup": dict(zero_work),
                "history_scan": dict(zero_work),
                "history_access": "unstarted",
                "branch_build": dict(zero_work),
                "total": dict(zero_work),
            })
        def delta(after, before):
            return {k: getattr(after, k) - getattr(before, k) for k in WORK_KEYS}
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
        if work_receipt is not None:
            work_receipt["phase"] = "setup"
        before = budget.work
        budget.spend(CognitiveWork(cycles=1, memory_items=2 + 3 * len(names)))
        if work_receipt is not None:
            work_receipt["setup"] = delta(budget.work, before)
            work_receipt["total"] = delta(budget.work, start_work)
            work_receipt["phase"] = "history_scan"
        keys = tuple(dict.fromkeys((probe, *(key for _, key in continuations))))
        scan_start = budget.work
        if support_index is None:
            budget.spend(CognitiveWork(
                cycles=1, memory_items=7 * len(self._samples) + 2 * len(keys)))
            supports = self._supports(keys)
            access = "direct_scan"
        elif not support_index.built:
            budget.spend(CognitiveWork(
                cycles=1, memory_items=7 * len(self._samples) + 2 * len(keys)))
            self._build_support_index(support_index)
            supports = self._indexed_supports(keys, support_index)
            access = "shared_scan"
        else:
            # Lookup is still explicit paid work; only the repeated history
            # traversal is reused. No free query or cross-decision persistence.
            budget.spend(CognitiveWork(cycles=1, memory_items=2 * len(keys)))
            supports = self._indexed_supports(keys, support_index)
            access = "indexed_lookup"
        if work_receipt is not None:
            work_receipt["history_scan"] = delta(budget.work, scan_start)
            work_receipt["history_access"] = access
            work_receipt["total"] = delta(budget.work, start_work)
        count = max(2, len(supports[probe]))
        if work_receipt is not None:
            work_receipt["phase"] = "branch_build"
        before = budget.work
        budget.spend(CognitiveWork(
            cycles=1, memory_items=5 * sum(map(len, supports.values())) +
            count * (7 + 5 * len(names))))
        if work_receipt is not None:
            work_receipt["branch_build"] = delta(budget.work, before)
            work_receipt["total"] = delta(budget.work, start_work)
        means = {key: tuple(fsum(x[c] for x in rows) / len(rows) for c in range(5))
                 for key, rows in supports.items()}
        probes = supports[probe]
        if len(probes) == 1:
            probes = probes * 2
        result = tuple(SubjectiveOutcome(
            1.0 / count, "body_only", delta,
            tuple((name, delta if key == probe else means[key])
                  for name, key in continuations)) for delta in probes)
        if work_receipt is not None:
            work_receipt["status"] = "COMPLETE"
            work_receipt["phase"] = "complete"
            work_receipt["total"] = delta(budget.work, start_work)
        return result


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
