"""Isolated, non-activated review prototype for #326; no motor authority."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IntentEvidence:
    semantic_ref: str
    last_applied_step: int
    observed_destination: tuple[int, int]
    accumulated: float

def bounded_continuation(prior: IntentEvidence, *, intended_ref: str,
                         now_step: int, observed_origin: tuple[int, int],
                         ceiling: float, residual: float, applied: bool) -> float | None:
    """Transfer only information after independently verified motor application.

    No motor decision, Competition registration, or memory owner is created.
    """
    if not isinstance(prior, IntentEvidence):
        raise TypeError("invalid previous intention")
    if (type(now_step) is not int or now_step < 2
        or type(prior.last_applied_step) is not int
        or type(prior.semantic_ref) is not str
        or type(intended_ref) is not str
        or not isinstance(observed_origin, tuple)
        or len(observed_origin) != 2
        or any(type(v) is not int for v in observed_origin)
        or type(prior.observed_destination) is not tuple
        or any(type(v) is not int for v in prior.observed_destination)
        or type(applied) is not bool
        or type(ceiling) not in (int, float)
        or type(residual) not in (int, float)
        or type(prior.accumulated) not in (int, float)
        or not 0 < residual < 1 or not 0 < ceiling <= 1
        or not 0 < prior.accumulated <= 1):
        raise ValueError("invalid bounded continuation input")
    if (not applied or now_step != prior.last_applied_step + 1
        or prior.semantic_ref != intended_ref
        or prior.observed_destination != observed_origin):
        return None
    return min(float(prior.accumulated), float(ceiling) * float(residual))
