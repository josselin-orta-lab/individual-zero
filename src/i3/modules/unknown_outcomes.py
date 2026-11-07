"""Paid first-person belief over actionable outcomes of an unseen frontier.

This is not a decision policy and does not manufacture a bodily-effect prior.
It reuses P1.3's existing Laplace resource base rate and only turns resource
mass into actionable water/food hypotheses when the individual has personally
learned a beneficial effect for that modality and retains paid empirical
effect branches. Unsupported mass stays non-actionable.
"""
from __future__ import annotations

from math import isfinite

from .body import CognitiveBudget, CognitiveWork, F, VITAL, W
from .information_value import WORK_KEYS
from .personal_outcomes import NoPersonalSupport
from .reference_branches import ReferenceBranchMemory

SCHEMA = "i3-frontier-actionable-belief/v1"
_GENERIC_FOOD_KEY = ("manger", "__stage1_unknown_food__")


def _delta(after, before):
    return {k: getattr(after, k) - getattr(before, k) for k in WORK_KEYS}


def _living_budget(budget):
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if any(budget.remaining[k] <= 0 for k in VITAL):
        raise ValueError("no frontier belief computation after physical death")


def _personal_state(mind):
    if not hasattr(mind, "map") or type(mind.map) is not dict:
        raise ValueError("personal map required")
    effects = getattr(mind, "effects", None)
    if effects is None or type(getattr(effects, "stats", None)) is not dict:
        raise ValueError("personal EffectsModel state required")
    return effects


def paid_frontier_actionable_belief(
        mind, branch_memory: ReferenceBranchMemory,
        budget: CognitiveBudget, *, work_receipt: dict | None = None) -> dict:
    """Build a conservative 2/3-way actionable frontier belief.

    The structural resource probability is exactly P1.3's existing
    (resource_cells + 1)/(seen_cells + 2). Conditional water-vs-token
    modality weights come from personal map incidences only. A mixed observed
    cell contributes one incidence to each modality.

    A modality is actionable only when:
      1. the individual's EffectsModel has personally learned a positive
         bodily consequence for that generic action class; and
      2. the paid recent branch memory can supply empirical effect samples.

    Any probability mass that lacks those two conditions is folded into
    NO_ACTIONABLE_PERSONAL_MODEL. It is never converted into a zero-delta
    or favorable hidden consequence.
    """
    _living_budget(budget)
    effects = _personal_state(mind)
    if not isinstance(branch_memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    start = budget.work
    scan = CognitiveWork(
        cycles=1,
        memory_items=2 * len(mind.map) + 3 * len(effects.stats) + 4)
    budget.spend(scan)
    after_scan = budget.work

    seen = [cell for cell in mind.map.values() if cell is not None]
    if any(type(cell) is not tuple or len(cell) != 2 for cell in seen):
        raise ValueError("malformed personal map cell")
    if any(type(cell[0]) is not bool or type(cell[1]) is not tuple for cell in seen):
        raise ValueError("malformed personal map sensor record")

    resource_cells = sum(bool(water or tokens) for water, tokens in seen)
    water_cells = sum(bool(water) for water, _ in seen)
    token_cells = sum(bool(tokens) for _, tokens in seen)
    p_resource = (resource_cells + 1.0) / (len(seen) + 2.0)
    if not 0.0 < p_resource < 1.0 or not isfinite(p_resource):
        raise RuntimeError("invalid P1.3 resource base rate")

    modalities = water_cells + token_cells
    q_water = water_cells / modalities if modalities else 0.0
    q_food = token_cells / modalities if modalities else 0.0

    water_positive = effects.known_positive(("boire",), W)
    food_positive = any(
        type(key) is tuple and len(key) > 1 and key[0] == "manger" and
        key[1] is not None and st[2] > 0 and st[1][F] > 0
        for key, st in effects.stats.items())

    support_index = branch_memory.begin_support_index()
    water_effects = ()
    food_effects = ()
    support = {
        "water": "NO_PERSONAL_POSITIVE_EFFECT" if not water_positive
                 else "NO_EMPIRICAL_BRANCH_SUPPORT",
        "food": "NO_PERSONAL_POSITIVE_EFFECT" if not food_positive
                else "NO_EMPIRICAL_BRANCH_SUPPORT",
    }

    if q_water > 0.0 and water_positive:
        try:
            water_effects = branch_memory.branches(
                ("boire", None), budget, support_index=support_index)
            support["water"] = "SUPPORTED"
        except NoPersonalSupport:
            pass
    if q_food > 0.0 and food_positive:
        try:
            food_effects = branch_memory.branches(
                _GENERIC_FOOD_KEY, budget, support_index=support_index)
            support["food"] = "SUPPORTED"
        except NoPersonalSupport:
            pass

    p_water = p_resource * q_water if water_effects else 0.0
    p_food = p_resource * q_food if food_effects else 0.0
    p_none = 1.0 - p_water - p_food
    if min(p_none, p_water, p_food) < -1e-12:
        raise RuntimeError("actionable frontier probabilities do not normalize")
    p_none = max(0.0, p_none)

    branches = []
    if water_effects or food_effects:
        branches.append({
            "signal": "NO_ACTIONABLE_PERSONAL_MODEL",
            "probability": p_none,
            "resource_effects": (),
        })
        if water_effects:
            branches.append({
                "signal": "ACTIONABLE_WATER",
                "probability": p_water,
                "resource_effects": tuple(tuple(x) for x in water_effects),
            })
        if food_effects:
            branches.append({
                "signal": "ACTIONABLE_FOOD_TOKEN",
                "probability": p_food,
                "resource_effects": tuple(tuple(x) for x in food_effects),
            })

    if branches:
        total = sum(row["probability"] for row in branches)
        if abs(total - 1.0) > 1e-12 or not 2 <= len(branches) <= 3:
            raise RuntimeError("frontier branch contract violated")

    result = {
        "schema": SCHEMA,
        "status": ("COMPLETE_ACTIONABLE_PERSONAL_BELIEF"
                   if branches else "NO_ACTIONABLE_PERSONAL_MODEL"),
        "resource_base_rate": p_resource,
        "personal_counts": {
            "seen_cells": len(seen),
            "resource_cells": resource_cells,
            "water_cells": water_cells,
            "token_cells": token_cells,
        },
        "conditional_modality": {
            "water": q_water,
            "food_token": q_food,
        },
        "support": support,
        "branches": tuple(branches),
        "unknown_semantics": (
            "UNSUPPORTED_RESOURCE_MASS_COLLAPSES_TO_NO_ACTIONABLE_PERSONAL_MODEL"),
        "newborn_semantics": (
            "STRUCTURAL_RESOURCE_PRIOR_ONLY_UNTIL_PERSONAL_ACTIONABLE_SUPPORT"),
        "world_access": False,
        "work": _delta(budget.work, start),
        "work_breakdown": {
            "personal_state_scan": _delta(after_scan, start),
            "empirical_support_reads": _delta(budget.work, after_scan),
            "total": _delta(budget.work, start),
        },
        "cost_is_physical_settlement_receipt": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-frontier-actionable-belief-work/v1",
            "status": result["status"],
            "work": dict(result["work"]),
        })
    return result


__all__ = ["SCHEMA", "paid_frontier_actionable_belief"]
