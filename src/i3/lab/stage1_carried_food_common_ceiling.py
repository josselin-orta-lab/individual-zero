"""Cost-comparable raw-score audit for one carried unknown-food option.

Laboratory helper only. It never executes Competition, Action Control or a World
step. A deep-copied P1.3 reference repertoire and the Stage-1 carried-food
information kernel share one conservative complete-work forecast body.

Historical curiosity/prudence are intentionally excluded from this comparison:
Stage 1 asks whether information value can replace those additive terms in the
same predicted-distress score units.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork, VITAL,
    capacities, debit_cognition)
from ..modules.carried_food_information import (
    _minimum_ceiling as _food_minimum_ceiling,
    paid_carried_unknown_food_information_value)
from ..modules.information_value import WORK_KEYS, _add_work
from ..modules.forecast_work import projection_simulated_steps_ceiling
from ..modules.personal_outcomes import NoPersonalSupport
from ..modules.reference_memory_mind import ReferenceBranchMemoryMind

SCHEMA = "i3-carried-food-common-ceiling-audit/v1"
MAX_SUPPORT_BRANCHES = 3


def _work_delta(after, before):
    return CognitiveWork(*(
        getattr(after, key) - getattr(before, key)
        for key in WORK_KEYS))


def _leq(a, b):
    return all(getattr(a, key) <= getattr(b, key) for key in WORK_KEYS)


def _simulation_upper(model, plan, horizon):
    i = steps = 0
    while i < len(plan) and steps < horizon:
        key = plan[i]
        run = 1
        if key[0] == "se_deplacer":
            while (i + run < len(plan) and plan[i + run] == key and
                   run < horizon):
                run += 1
        i += run
        steps += 1
    return CognitiveWork(
        simulated_steps=steps + projection_simulated_steps_ceiling(model))


def _inventory_count(cap, external_token):
    if type(cap) is not dict or type(cap.get("inventory")) is not tuple:
        raise ValueError("first-person capture with immutable inventory required")
    matches = []
    for item in cap["inventory"]:
        if (type(item) is not tuple or len(item) != 2 or
                type(item[0]) is not str or not item[0] or
                type(item[1]) is not int or item[1] <= 0):
            raise ValueError("malformed carried inventory entry")
        if item[0] == external_token:
            matches.append(item[1])
    if len(matches) != 1:
        raise ValueError("external carried token must appear exactly once")
    return matches[0]


def _setup_work(mind, cap):
    return CognitiveWork(
        cycles=3,
        memory_items=(
            len(mind.buffer) + 2 * len(mind.map) + len(mind.effects.stats)
            + len(mind.tokens) + len(mind.external) + len(mind.acc)
            + sum(len(v) for v in mind.values) + 12
            + len(cap["inventory"])
            + sum(len(cell[1]) for cell in (cap["here"], *cap["neighbors"])
                  if cell is not None)))


def _ordinary_quote(model, opts, horizon):
    work = CognitiveWork()
    for oid, plan, _first in opts:
        work = _add_work(work, _simulation_upper(model, plan, horizon))
        if oid in model._presence:
            _pr, travel = model._presence[oid]
            work = _add_work(
                work, _simulation_upper(model, travel, horizon))
    return work


def _score_ordinary(model, opts, forecast_body, horizon, budget, ceiling):
    rows = []
    for oid, plan, _first in opts:
        value, _steps, uncertainty = model.simulate(
            forecast_body, plan, horizon, budget)
        if oid in model._presence:
            pr, travel = model._presence[oid]
            failed, _failed_steps, _ = model.simulate(
                forecast_body, travel, horizon, budget)
            value = pr * value + (1.0 - pr) * failed
        if type(value) not in (int, float) or not isfinite(value):
            raise RuntimeError("nonfinite ordinary option score")
        if not _leq(budget.work, ceiling):
            raise RuntimeError("ordinary scoring exceeded common ceiling")
        rows.append({
            "option": oid,
            "base_score": float(value),
            "uncertainty": float(uncertainty),
        })
    return rows


def _winners(rows, *, field):
    best = max(row[field] for row in rows)
    return best, tuple(sorted(
        row["option"] for row in rows
        if abs(row[field] - best) <= 1e-12))


def audit_carried_food_common_ceiling(
        mind: ReferenceBranchMemoryMind, cap, laws: BodyLaws,
        external_token: str) -> dict:
    """Compare ordinary P1.3 base options and the information meal fairly.

    The supplied Mind is never mutated. One deep copy performs first-person
    perception and constructs the unchanged P1.3 option repertoire.

    A single conservative ceiling includes ordinary setup work, every ordinary
    rollout, a direct branch-memory scan and a maximum three-branch food matrix.
    Every score is forecast from the body after that same complete ceiling.
    """
    if not isinstance(mind, ReferenceBranchMemoryMind):
        raise ValueError("ReferenceBranchMemoryMind required")
    if not isinstance(laws, BodyLaws):
        raise ValueError("BodyLaws required")
    if type(external_token) is not str or not external_token:
        raise ValueError("nonempty external carried token required")
    if type(cap) is not dict or type(cap.get("body")) not in (tuple, list):
        raise ValueError("first-person capture required")
    body = tuple(float(x) for x in cap["body"])
    count = _inventory_count(cap, external_token)

    model = deepcopy(mind)
    budget = CognitiveBudget(body, laws)
    if any(budget.body[k] <= 0.0 for k in VITAL):
        raise ValueError("no audit cognition after physical death")

    setup = _setup_work(model, cap)
    budget.spend(setup)
    after_setup = budget.work

    cycles, horizon, miss = capacities(body, model.n_base, model.h_max)
    del cycles
    inv = model.perceive(cap, miss)
    opts = tuple(model.options(inv, body, horizon))
    model._drift = model.drift()

    internal_token = model.tokens.get(external_token)
    if type(internal_token) is not str or not internal_token:
        raise RuntimeError("perception did not internalize carried token")
    meal_option = "manger:" + internal_token
    if not any(oid == meal_option for oid, _plan, _first in opts):
        return {
            "schema": SCHEMA,
            "status": "REFERENCE_MEAL_NOT_OFFERED",
            "comparison_status": "NOT_EVALUATED",
            "meal_option": meal_option,
        }

    ordinary_quote = _ordinary_quote(model, opts, horizon)
    support_quote = CognitiveWork(
        cycles=1,
        memory_items=7 * len(model.branch_memory._samples) + 2)

    before_candidate_remainder = _add_work(
        _add_work(after_setup, ordinary_quote), support_quote)
    _prep, candidate_cumulative = _food_minimum_ceiling(
        model, MAX_SUPPORT_BRANCHES, count >= 2,
        before_candidate_remainder)
    candidate_remainder = _work_delta(
        candidate_cumulative, before_candidate_remainder)

    ceiling = after_setup
    for block in (ordinary_quote, support_quote, candidate_remainder):
        ceiling = _add_work(ceiling, block)

    try:
        forecast_body, _audit = debit_cognition(body, laws, ceiling)
    except CognitiveFundingError:
        return {
            "schema": SCHEMA,
            "status": "COMMON_CEILING_UNFUNDED",
            "comparison_status": "NOT_EVALUATED",
            "meal_option": meal_option,
            "common_forecast_work_ceiling": {
                key: getattr(ceiling, key) for key in WORK_KEYS},
        }

    ordinary = _score_ordinary(
        model, opts, forecast_body, horizon, budget, ceiling)
    after_ordinary = budget.work

    try:
        candidate = paid_carried_unknown_food_information_value(
            model, model.branch_memory, internal_token, count, budget,
            forecast_work=ceiling)
    except NoPersonalSupport:
        return {
            "schema": SCHEMA,
            "status": "CANDIDATE_NO_PERSONAL_SUPPORT",
            "comparison_status": "NOT_EVALUATED",
            "meal_option": meal_option,
        }
    except CognitiveFundingError as exc:
        raise RuntimeError(
            "common ceiling failed to fund quoted food kernel") from exc

    if not _leq(budget.work, ceiling):
        raise RuntimeError("actual common-ceiling audit work exceeded quote")

    original_meal = next(
        row for row in ordinary if row["option"] == meal_option)
    reference_best, reference_winners = _winners(
        ordinary, field="base_score")

    candidate_rows = []
    for row in ordinary:
        item = dict(row)
        item["candidate_score"] = (
            float(candidate["option_score"])
            if row["option"] == meal_option else row["base_score"])
        candidate_rows.append(item)
    candidate_best, candidate_winners = _winners(
        candidate_rows, field="candidate_score")

    meal_candidate = float(candidate["option_score"])

    return {
        "schema": SCHEMA,
        "status": "COMPLETE_COMMON_CEILING_RAW_SCORE_AUDIT",
        "comparison_status": "COST_COMPARABLE_FORECAST_BODY_NOT_POLICY",
        "meal_option": meal_option,
        "inventory_count": count,
        "horizon": horizon,
        "offered_options": len(opts),
        "forecast_start_body": tuple(forecast_body),
        "common_forecast_work_ceiling": {
            key: getattr(ceiling, key) for key in WORK_KEYS},
        "actual_work": {
            key: getattr(budget.work, key) for key in WORK_KEYS},
        "work_blocks": {
            "setup": {
                key: getattr(after_setup, key) for key in WORK_KEYS},
            "ordinary_quote": {
                key: getattr(ordinary_quote, key) for key in WORK_KEYS},
            "support_quote": {
                key: getattr(support_quote, key) for key in WORK_KEYS},
            "candidate_remainder_quote": {
                key: getattr(candidate_remainder, key) for key in WORK_KEYS},
            "ordinary_actual_after_setup": {
                key: getattr(after_ordinary, key) - getattr(after_setup, key)
                for key in WORK_KEYS},
        },
        "reference_base": {
            "best_score": float(reference_best),
            "raw_winners": reference_winners,
            "meal_score": float(original_meal["base_score"]),
            "meal_raw_top": meal_option in reference_winners,
        },
        "candidate_base": {
            "best_score": float(candidate_best),
            "raw_winners": candidate_winners,
            "meal_score": meal_candidate,
            "meal_minus_reference_meal": float(
                meal_candidate - original_meal["base_score"]),
            "meal_raw_top": meal_option in candidate_winners,
            "winner_set_changed": reference_winners != candidate_winners,
            "information_value": float(candidate["information_value"]),
            "support_records": candidate["support_records"],
            "subjective_branches": candidate["subjective_branches"],
        },
        "ordinary_scores": tuple(ordinary),
        "candidate_score_rows": tuple(candidate_rows),
        "curiosity_prudence_included": False,
        "competition_replayed": False,
        "control_replayed": False,
        "motor_command_authorized": False,
        "world_step_executed": False,
        "original_mind_mutated": False,
        "cost_is_physical_settlement_receipt": False,
    }


__all__ = ["SCHEMA", "audit_carried_food_common_ceiling"]
