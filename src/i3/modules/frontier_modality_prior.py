"""Paid first-person prior over what resource modality a frontier may reveal.

This primitive predicts observation classes only. It assigns no bodily effect,
utility or action value. It extends P1.3's existing Laplace resource-presence
rate with a symmetric two-modality Laplace prior over water versus token
incidence in the individual's own perceived map.
"""
from __future__ import annotations

from .body import CognitiveBudget, CognitiveWork, VITAL

SCHEMA = "i3-frontier-modality-prior/v1"


def paid_frontier_modality_prior(
        personal_map, budget: CognitiveBudget, *,
        work_receipt: dict | None = None) -> dict:
    if type(personal_map) is not dict:
        raise ValueError("plain first-person map required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0.0 for k in VITAL):
        raise ValueError("no modality cognition after physical death")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    before = budget.work
    budget.spend(CognitiveWork(
        cycles=1, memory_items=2 * len(personal_map) + 8))

    seen = []
    for cell in personal_map.values():
        if cell is None:
            continue
        if (type(cell) is not tuple or len(cell) != 2 or
                type(cell[0]) is not bool or type(cell[1]) is not tuple):
            raise ValueError("malformed first-person map cell")
        seen.append(cell)

    resource_cells = sum(
        1 for water, tokens in seen if water or tokens)
    water_incidences = sum(
        1 for water, _tokens in seen if water)
    token_incidences = sum(
        1 for _water, tokens in seen if tokens)

    p_resource = (resource_cells + 1.0) / (len(seen) + 2.0)
    modality_denominator = water_incidences + token_incidences + 2.0
    q_water = (water_incidences + 1.0) / modality_denominator
    q_token = (token_incidences + 1.0) / modality_denominator

    branches = (
        {"signal": "NO_RESOURCE",
         "probability": 1.0 - p_resource},
        {"signal": "WATER_MODALITY",
         "probability": p_resource * q_water},
        {"signal": "TOKEN_MODALITY",
         "probability": p_resource * q_token},
    )
    total = sum(row["probability"] for row in branches)
    if abs(total - 1.0) > 1e-12:
        raise RuntimeError("frontier modality probabilities do not normalize")

    work = {
        key: getattr(budget.work, key) - getattr(before, key)
        for key in ("cycles", "simulated_steps", "memory_items", "replays")
    }
    result = {
        "schema": SCHEMA,
        "status": "COMPLETE_FIRST_PERSON_MODALITY_PRIOR",
        "resource_base_rate": p_resource,
        "conditional_modality": {
            "water": q_water,
            "token": q_token,
        },
        "personal_counts": {
            "seen_passable_cells": len(seen),
            "resource_cells": resource_cells,
            "water_incidences": water_incidences,
            "token_incidences": token_incidences,
        },
        "branches": branches,
        "mixed_cell_semantics": (
            "ONE_INCIDENCE_PER_MODALITY_THEN_NORMALIZED_NO_SEPARATE_MIXED_BRANCH"),
        "newborn_semantics": (
            "SYMMETRIC_BETA_RESOURCE_AND_DIRICHLET_MODALITY_PRIOR"),
        "body_input": False,
        "action_effect_input": False,
        "token_identity_input": False,
        "world_access": False,
        "work": work,
        "cost_is_physical_settlement_receipt": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-frontier-modality-prior-work/v1",
            "status": result["status"],
            "work": dict(work),
        })
    return result


__all__ = ["SCHEMA", "paid_frontier_modality_prior"]
