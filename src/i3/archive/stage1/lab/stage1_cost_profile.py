"""Observer-side reduction of Stage-1 decision work; never a policy input.

Consumes only explicit work receipts already emitted by the opt-in development
candidate. It does not run a life, allocate cognition, infer hidden World state
or change the individual's decision.
"""
from __future__ import annotations

from collections.abc import Mapping

from i3.modules.body import BodyLaws, CognitiveWork, cognitive_cost, validate_laws

WORK = ("cycles", "simulated_steps", "memory_items", "replays")
SCHEMA = "i3-stage1-decision-cost-summary/v1"
PHASES = (
    "base_processing",
    "hypothetical_setup",
    "personal_setup",
    "personal_history_scan",
    "personal_branch_build",
    "batch_setup",
    "kernel_preparation",
    "kernel_unique_cells",
    "kernel_reduction",
    "competition",
)


def _work(value, name: str) -> CognitiveWork:
    if not isinstance(value, Mapping) or set(value) != set(WORK):
        raise ValueError("invalid work receipt: " + name)
    if any(type(value[k]) is not int or value[k] < 0 for k in WORK):
        raise ValueError("invalid work counters: " + name)
    return CognitiveWork(**{k: value[k] for k in WORK})


def _add(a: CognitiveWork, b: CognitiveWork) -> CognitiveWork:
    return CognitiveWork(*(getattr(a, k) + getattr(b, k) for k in WORK))


def _as_dict(work: CognitiveWork) -> dict:
    return {k: getattr(work, k) for k in WORK}


def summarize_decision_cost(profile: dict, laws: BodyLaws) -> dict:
    """Verify and reduce a COMPLETE decision cost profile into physical costs.

Only complete profiles are reduced: a partial funding failure remains a partial
outcome and must not be silently extrapolated. The exact phase sum must match
the decision's already-declared total CognitiveWork.
"""
    validate_laws(laws)
    if not isinstance(profile, dict) or profile.get("schema") != "i3-local-decision-cost-profile/v1":
        raise ValueError("current local decision cost profile required")
    if profile.get("status") not in ("action_admitted", "control_rejected"):
        raise ValueError("complete scored decision required")
    if type(profile.get("options")) is not list:
        raise ValueError("option receipts required")

    buckets = {name: CognitiveWork() for name in PHASES}
    buckets["base_processing"] = _work(profile.get("base_processing"), "base_processing")
    buckets["batch_setup"] = _work(profile.get("batch_setup"), "batch_setup")
    buckets["competition"] = _work(profile.get("competition"), "competition")

    for index, option in enumerate(profile["options"]):
        if not isinstance(option, dict) or option.get("phase") != "scored":
            raise ValueError(f"incomplete option receipt: {index}")
        buckets["hypothetical_setup"] = _add(
            buckets["hypothetical_setup"],
            _work(option.get("hypothetical_setup"), f"option[{index}].hypothetical_setup"),
        )
        personal = option.get("personal_construction")
        if (not isinstance(personal, dict) or
                personal.get("schema") != "i3-personal-construction-work/v1" or
                personal.get("status") != "COMPLETE"):
            raise ValueError(f"incomplete personal construction: {index}")
        for target, source in (
            ("personal_setup", "setup"),
            ("personal_history_scan", "history_scan"),
            ("personal_branch_build", "branch_build"),
        ):
            buckets[target] = _add(
                buckets[target],
                _work(personal.get(source), f"option[{index}].personal.{source}"),
            )
        kernel = option.get("kernel")
        if not isinstance(kernel, dict):
            raise ValueError(f"missing kernel receipt: {index}")
        for target, source in (
            ("kernel_preparation", "preparation"),
            ("kernel_unique_cells", "unique_cells"),
            ("kernel_reduction", "reduction"),
        ):
            buckets[target] = _add(
                buckets[target],
                _work(kernel.get(source), f"option[{index}].kernel.{source}"),
            )

    total = CognitiveWork()
    for phase in PHASES:
        total = _add(total, buckets[phase])
    declared = _work(profile.get("actual_total_work"), "actual_total_work")
    if total != declared:
        raise ValueError("phase work does not sum to declared decision work")

    physical = {}
    for phase, work in buckets.items():
        energy, vigilance = cognitive_cost(laws, work)
        physical[phase] = {
            "work": _as_dict(work),
            "energy": energy,
            "vigilance": vigilance,
        }
    energy_total, vigilance_total = cognitive_cost(laws, total)
    focus = {
        "personal_history_scan": physical["personal_history_scan"],
        "kernel_unique_cells": physical["kernel_unique_cells"],
    }
    return {
        "schema": SCHEMA,
        "phase_costs": physical,
        "total_work": _as_dict(total),
        "total_energy": energy_total,
        "total_vigilance": vigilance_total,
        "dominant_energy_phase": max(PHASES, key=lambda p: physical[p]["energy"]),
        "dominant_vigilance_phase": max(PHASES, key=lambda p: physical[p]["vigilance"]),
        "focus": focus,
    }
