"""Isolated, inactive bounded continuation evidence for issue #326 / #346.

Never creates an option, registers a Competition candidate or grants motor
authority. Every new action still needs independent arbitration.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class IntentEvidence:
    semantic_ref: str
    last_applied_step: int
    observed_destination: tuple[int, int]
    accumulated: float


def _coordinate(value):
    return (type(value) is tuple and len(value) == 2
            and all(type(item) is int for item in value))


def _unit(value):
    return (type(value) in (int, float) and isfinite(value)
            and 0 < value <= 1)


def bounded_continuation(prior: IntentEvidence, *, intended_ref: str,
                         now_step: int, observed_origin: tuple[int, int],
                         ceiling: float, residual: float, applied: bool) -> float | None:
    """Bound evidence only when the previous hop was personally applied."""
    if type(prior) is not IntentEvidence:
        raise TypeError("invalid previous intention")
    if (type(now_step) is not int or now_step < 2
            or type(prior.last_applied_step) is not int
            or prior.last_applied_step < 1
            or type(prior.semantic_ref) is not str or not prior.semantic_ref
            or type(intended_ref) is not str or not intended_ref
            or not _coordinate(observed_origin)
            or not _coordinate(prior.observed_destination)
            or type(applied) is not bool
            or not _unit(ceiling) or not _unit(residual)
            or residual >= 1
            or not _unit(prior.accumulated)):
        raise ValueError("invalid bounded continuation evidence")
    if (not applied or now_step != prior.last_applied_step + 1
            or prior.semantic_ref != intended_ref
            or prior.observed_destination != observed_origin):
        return None
    return min(float(prior.accumulated), float(ceiling) * float(residual))
