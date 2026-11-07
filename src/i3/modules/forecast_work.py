"""Shared conservative projection-work quotes for I3 forecast ceilings.

These are pre-computation funding ceilings, not physical work receipts.
Executed cognition is still charged from the actual CognitiveBudget work.
"""
from __future__ import annotations


_REFERENCE_ACCOUNTING = ("chunk_end", "trapezoid")
_CANDIDATE_F_ACCOUNTING = "event_local_quadratic4"
_UNQUOTED_REJECTED_ACCOUNTING = ("event_quadratic", "event_quartic")


def projection_simulated_steps_ceiling(model) -> int:
    """Return a complete conservative projection reward-evaluation ceiling."""
    chunks = getattr(model, "proj_chunks", None)
    if (type(chunks) is not tuple or not chunks or
            any(type(run) is not int or run < 1 for run in chunks)):
        raise ValueError("positive immutable projection chunks required")

    simulation_mode = getattr(model, "simulation_mode", "reference")
    if simulation_mode not in ("reference", "candidate_f"):
        raise ValueError("unknown simulation mode for forecast quote")

    accounting = getattr(model, "projection_accounting", "chunk_end")
    if simulation_mode == "candidate_f" and accounting != _CANDIDATE_F_ACCOUNTING:
        raise ValueError(
            "candidate_f forecast requires event_local_quadratic4 projection")

    if accounting in _REFERENCE_ACCOUNTING:
        return len(chunks)
    if accounting == _CANDIDATE_F_ACCOUNTING:
        # One paid starting reward plus at most one new paid reward evaluation
        # per projected discrete step. Blocks of 3/4 steps pay only 2.
        return 1 + sum(chunks)
    if accounting in _UNQUOTED_REJECTED_ACCOUNTING:
        raise ValueError(
            "rejected dynamic projection mode has no Stage-1 forecast ceiling")
    raise ValueError("unknown projection accounting for forecast quote")
