"""Minimal immutable-first-person snapshot for an external distress forecast.

Stage 2.1 engineering software only. Not an engine or production price.
No full Mind copy, motor access, effects, maps, RNG state or hidden World data.
"""
from __future__ import annotations

from copy import deepcopy
from math import fsum, isfinite

from ..modules.body import (ACTION_COSTS, CognitiveBudget, CognitiveWork,
                            cognitive_cost, validate_body)
from ..modules.mind import Mind, REPLAYS_PER_SLEEP

MAX_SNAPSHOT = 512


def work_envelope(n: int, k: int = 3) -> CognitiveWork:
    """Conservative DECLARED operator categories, NOT measured host CPU cost."""
    if (type(n) is not int or type(k) is not int
            or not 0 <= k <= min(n, REPLAYS_PER_SLEEP)
            or not k <= n <= MAX_SNAPSHOT):
        raise ValueError("bounded eligible personal memory and replay count required")
    return CognitiveWork(cycles=7, memory_items=4*n+2*k, replays=k)


def preauthorize(budget: CognitiveBudget, *, n: int, k: int, action) -> bool:
    """Spend before calculation, never take energy reserved for chosen motor."""
    if not isinstance(budget, CognitiveBudget):
        raise TypeError("native cognitive allowance required")
    if action is not None and action not in ACTION_COSTS:
        raise ValueError("invalid already-chosen action")
    work = work_envelope(n, k)
    energy, vigilance = cognitive_cost(budget.laws, work)
    if (budget.remaining[0] < energy or budget.remaining[4] < vigilance
            or (action not in (None, "dormir")
                and budget.remaining[0]-energy < ACTION_COSTS[action])):
        return False
    if not budget.try_spend(work):
        raise RuntimeError("native budget refused model-admissible ticket")
    return True


class CompactPersonalDistressHead:
    """Exactly the direct-outcome #1279 regressor, with only needed state."""

    def __init__(self, source: Mind):
        if not isinstance(source, Mind):
            raise TypeError("native I3 personal Mind required")
        self.theta = tuple(source.theta)
        self.p = tuple(source.p)
        self.w = tuple(source.w)
        self.alpha = source.alpha
        self.d_max = source.d_max
        if any(type(x) not in (int, float) or not isfinite(x)
               for x in (*self.theta, *self.p, *self.w, self.alpha, self.d_max)):
            raise ValueError("nonfinite inherited personal distress parameters")
        if len(self.theta) != 5 or len(self.p) != 5 or len(self.w) != 5:
            raise ValueError("five-channel inherited readout required")
        if not (0 <= len(source.buffer) <= MAX_SNAPSHOT):
            raise ValueError("memory capacity exceeded")
        # Records are frozen copies from the pre-fork, personally lived buffer.
        self._eligible_records = tuple(deepcopy(tuple(source.buffer)))
        self.weights = [0.0] * 6
        self.training_updates = 0
        self.trained_indices = ()

    def _features(self, body):
        # Reuse the original innate Mind readout WITHOUT constructing a Mind.
        return Mind.feats(self, validate_body(body))

    def predict(self, before_body):
        phi = self._features(before_body)
        predicted = (-Mind.distress(self, phi)
                     + fsum(w*x for w, x in zip(self.weights, phi)))
        if not isfinite(predicted):
            raise RuntimeError("nonfinite compact forecast")
        return predicted

    def target_from_actual_outcome(self, after_body, dead):
        if type(dead) is not bool:
            raise TypeError("actual death flag must be boolean")
        phi = self._features(after_body)
        return -self.d_max if dead else -Mind.distress(self, phi)

    def apply(self, original_buffer, indices):
        if (type(original_buffer) not in (tuple, list)
                or tuple(original_buffer) != self._eligible_records):
            raise PermissionError("only pre-fork first-person memories permitted")
        if (type(indices) not in (tuple, list)
                or len(indices) + self.training_updates > REPLAYS_PER_SLEEP):
            raise ValueError("invalid replay count")
        if (len(set(indices)) != len(indices)
                or any(type(i) is not int or not 0 <= i < len(self._eligible_records)
                       or i in self.trained_indices for i in indices)):
            raise ValueError("duplicate, forged, or ineligible replay memory")
        # Validate all records before any learned state update.
        for i in indices:
            magnitude, before, after, dead = self._eligible_records[i]
            if type(magnitude) not in (int, float) or not isfinite(magnitude):
                raise ValueError("invalid memory priority")
            self._features(before)
            self.target_from_actual_outcome(after, dead)
        for i in indices:
            _, before, after, dead = self._eligible_records[i]
            phi = self._features(before)
            target = self.target_from_actual_outcome(after, dead)
            delta = target - self.predict(before)
            norm = fsum(x*x for x in phi)
            if not norm > 0 or not isfinite(delta):
                raise RuntimeError("invalid direct-outcome training error")
            step = self.alpha * delta / norm
            self.weights = [w + step*x for w, x in zip(self.weights, phi)]
            if any(not isfinite(w) for w in self.weights):
                raise RuntimeError("nonfinite compact learned weights")
            self.training_updates += 1
        self.trained_indices += tuple(indices)
