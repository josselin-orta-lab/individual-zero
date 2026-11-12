"""Real native World-paid per-step effect forecast and error ledger.

Frozen engineering-only scope in STAGE2_REAL_PAID_ERROR_LEDGER_ENGINEERING_PREFLIGHT.
The individual's Mind never sees the optional lab record or selects its purchase.
Only existing DEV Worlds may be used, NEVER scientific originals or new cohorts.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from math import fsum, isfinite

from ..modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost)
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.world import World
from .dev_worlds import dev_open_field, dev_failing_well
from .stage2_native_effect_reliability_observer import _check_paid

SCHEMA = "i3-stage2.1-real-World-paid-error-ledger-engineering/v1"
FACTORIES = (dev_open_field, dev_failing_well)
SEEDS = (840061, 840062)
HORIZON = 12
FORECAST_WORK = CognitiveWork(cycles=1, memory_items=6)
STORE_WORK = CognitiveWork(cycles=2, memory_items=12)
MODES = ("RETAIN", "PAID_DISCARD")


def _hash(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")).hexdigest()


def _can_purchase(budget, work, action=None):
    """Refuse before the optional operator, protecting the native motor."""
    if not isinstance(budget, CognitiveBudget):
        raise TypeError("native CognitiveBudget required")
    energy, vigilance = cognitive_cost(budget.laws, work)
    if (budget.remaining[0] < energy
            or budget.remaining[4] < vigilance):
        return False
    if (action not in (None, "dormir")
            and budget.remaining[0] - energy < ACTION_COSTS[action]):
        return False
    if not budget.try_spend(work):
        raise RuntimeError("budget refused after independently checked capacity")
    return True


def _record_error(ledger, action, predicted, body_before, body_after, mode):
    """Must be called only AFTER real paid STORE_WORK World receipt."""
    if mode not in MODES or type(mode) is not str:
        raise ValueError("unknown ledger control")
    if type(action) is not str or not action:
        raise ValueError("native action required")
    if not (len(predicted) == len(body_before) == len(body_after) == 5):
        raise ValueError("five-channel outcome required")
    error = fsum((a-b-p)**2 for a,b,p in zip(
        body_after, body_before, predicted)) / 5.
    if not isfinite(error) or error < 0:
        raise ValueError("invalid native prediction error")
    ledger.append((action, error))
    if mode == "PAID_DISCARD":
        if ledger.pop() != (action, error):
            raise RuntimeError("discard failed to erase just-appended record")
    return error


def _empty_receipt():
    return {c: {"requested": 0., "paid": 0., "unpaid": 0.}
            for c in ("energy", "vigilance")}


def run_arm(factory, seed, mode):
    if factory not in FACTORIES or type(seed) is not int or seed not in SEEDS:
        raise ValueError("outside fixed DEV engineering grid")
    if type(mode) is not str or mode not in MODES:
        raise ValueError("invalid retention arm")
    world = World(factory())
    mind = Mind(midpoint(), seed)
    ledger = []
    steps = []
    while world.t < HORIZON and not world.dead:
        cap = world.capture()
        before = tuple(cap["body"])
        native = CognitiveBudget(before, world.laws)
        action, param, original_work, info = mind.decide(cap, native)
        if original_work != native.work:
            raise RuntimeError("native decision work not matched to paid allowance")
        if action is not None and (mind.last is None
                                   or mind.last[2:] != (action,param)
                                   or tuple(mind.last[0]) != before):
            raise RuntimeError("motor did not come from the native Mind")
        if action is None and mind.last is not None:
            raise RuntimeError("null Mind action has invalid last action")
        key = None if action is None else tuple(mind.last[1])
        if action == "se_deplacer":
            key = ("se_deplacer",)
        predicted = None
        forecast_calls = 0
        forecast_funded = False
        if action is not None:
            forecast_funded = _can_purchase(native, FORECAST_WORK, action)
            if forecast_funded:
                predicted, uncertainty = mind.effects.predict(key)
                forecast_calls = 1
                if (len(predicted) != 5 or
                        any(not isfinite(v) for v in predicted)
                        or not isfinite(uncertainty)):
                    raise RuntimeError("nonfinite funded original forecast")
                predicted = tuple(predicted)
        work = native.work
        factual = world.step(action, param, work)
        _check_paid(world.laws, work, factual["cognitive_accounting"])
        after_motor = tuple(world.body)
        if after_motor != tuple(factual["body"]):
            raise RuntimeError("native World returned inconsistent body")

        learning_budget = CognitiveBudget(world.body, world.laws)
        learning_status = "NO_NATIVE_MOTOR" if action is None else "NO_FUNDED_LEARNING"
        learning_paid = _empty_receipt()
        actual_replays = 0
        if factual["dead"]:
            learning_status = "TERMINAL_NO_LEARNING"
        elif action is not None:
            mind.observe_outcome(factual)
            replay_limit = mind.prepare_learning(factual, learning_budget)
            if replay_limit is not None:
                learning_paid = world.pay_cognition(learning_budget.work)
                _check_paid(world.laws, learning_budget.work, learning_paid)
                factual["body"] = world.body
                actual_replays = mind.learn_from_outcome(
                    factual, replay_limit=replay_limit)
                if actual_replays != replay_limit:
                    raise RuntimeError("unmatched prepaid original replay count")
                learning_status = "PAID_LEARNING"
        if learning_status != "PAID_LEARNING":
            if learning_budget.work != CognitiveWork():
                raise RuntimeError("unfunded native learning retained a bill")
            _check_paid(world.laws, learning_budget.work, learning_paid)
        after_learning = tuple(world.body)

        storage_funded = False
        storage_paid = _empty_receipt()
        record_calls = 0
        appended = 0
        record_error = None
        # Errors may be stored only on living steps with a genuinely
        # *paid, preoutcome* point forecast, with memory billing first.
        if not factual["dead"] and forecast_funded:
            storage_budget = CognitiveBudget(world.body, world.laws)
            storage_funded = _can_purchase(storage_budget, STORE_WORK)
            if storage_funded:
                storage_paid = world.pay_cognition(storage_budget.work)
                _check_paid(world.laws, storage_budget.work, storage_paid)
                if storage_budget.work != STORE_WORK:
                    raise RuntimeError("unexpected source storage tariff")
                record_error = _record_error(
                    ledger, action, predicted, before, after_learning, mode)
                record_calls = 1
                appended = 1
            elif storage_budget.work != CognitiveWork():
                raise RuntimeError("denied source storage retained work")
        if factual["dead"] and (storage_funded or record_calls):
            raise RuntimeError("postmortem source update")
        _check_paid(world.laws, STORE_WORK if storage_funded else
                    CognitiveWork(), storage_paid)
        if len(ledger) > HORIZON:
            raise RuntimeError("unbounded personal engineering ledger")
        steps.append({
            "step": world.t, "native_action": action, "native_param": param,
            "native_option": info.get("option"), "native_funding": info.get("funding"),
            "native_decision_work": asdict(original_work),
            "total_world_decision_work": asdict(work),
            "forecast_funded": forecast_funded, "forecast_calls": forecast_calls,
            "forecast_key": key, "preoutcome_point_forecast": predicted,
            "world_decision_receipt": factual["cognitive_accounting"],
            "post_world_body": after_motor,
            "learning_status": learning_status,
            "native_learning_work": asdict(learning_budget.work),
            "native_learning_receipt": learning_paid,
            "actual_native_replays": actual_replays,
            "post_native_learning_body": after_learning,
            "storage_funded": storage_funded, "storage_receipt": storage_paid,
            "storage_compute_calls": record_calls,
            "storage_initial_appends": appended,
            "post_real_storage_body": tuple(world.body),
            "record_error": record_error,
            "lab_ledger_records": len(ledger),
            "terminal": bool(factual["dead"]),
        })
    if any((x["forecast_calls"] != int(x["forecast_funded"])
            or x["storage_compute_calls"] != int(x["storage_funded"])
            or x["storage_initial_appends"] != int(x["storage_funded"]))
           for x in steps):
        raise RuntimeError("optional operators not paid before execution")
    return {
        "world": world.spec.name, "seed": seed, "mode": mode,
        "steps_lived": len(steps), "terminal": bool(world.dead),
        "final_body": tuple(world.body), "lab_ledger_count": len(ledger),
        "laboratory_ledger_not_consumed_by_Mind": True,
        "world_calls": len(steps), "scientific_lives": 0,
        "steps": steps,
    }


def audit():
    rows = []
    for factory in FACTORIES:
        for seed in SEEDS:
            left = run_arm(factory, seed, "RETAIN")
            right = run_arm(factory, seed, "PAID_DISCARD")
            if left["steps_lived"] != right["steps_lived"]:
                raise RuntimeError("retention altered native life length")
            if (left["final_body"] != right["final_body"]
                    or left["terminal"] != right["terminal"]):
                raise RuntimeError("external ledger leaked into native physiology")
            for a,b in zip(left["steps"], right["steps"]):
                # Every native and paid fact must match. Only the external
                # retained record count may differ by design.
                if any(a[k] != b[k] for k in a
                       if k != "lab_ledger_records"):
                    raise RuntimeError("lab retention changed native motor or costs")
            rows.append({"world": left["world"], "seed": seed,
                         "retain": left, "discard": right})
    counts = {
        "engineering_worlds": 8,
        "engineering_world_steps": sum(
            row[mode]["steps_lived"] for row in rows for mode in
            ("retain", "discard")),
        "funded_forecasts_per_arm": sum(
            sum(s["forecast_calls"] for s in row["retain"]["steps"])
            for row in rows),
        "funded_stores_per_arm": sum(
            sum(s["storage_compute_calls"] for s in row["retain"]["steps"])
            for row in rows),
        "refused_forecasts_per_arm": sum(
            sum(s["native_action"] is not None and not s["forecast_funded"]
                for s in row["retain"]["steps"]) for row in rows),
        "refused_stores_per_arm": sum(
            sum(s["forecast_funded"] and not s["terminal"] and
                not s["storage_funded"] for s in row["retain"]["steps"])
            for row in rows),
        "null_decisions_per_arm": sum(
            sum(s["native_action"] is None for s in row["retain"]["steps"])
            for row in rows),
    }
    return {
        "schema": SCHEMA,
        "status": ("ACTUAL_PAID_LEDGER_ENGINEERING_PASS"
                   if counts["funded_stores_per_arm"]
                   else "NO_ACTUAL_STORE_OBSERVED"),
        "source_kind": "EXPOSED_DEV_ENGINEERING_WORLDS_ONLY",
        "horizon": HORIZON, "seeds": list(SEEDS),
        "source_worlds": [f().name for f in FACTORIES],
        "world_paid_preoutcome_prediction_and_postlearning_storage": True,
        "equal_model_work_and_factual_native_motors": True,
        "external_lab_retention_never_read_by_Mind": True,
        "full_host_CPU_cost_equal": False,
        "individually_chosen_additional_computation": False,
        "new_scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False, **counts,
        "deterministic_aggregate_sha256": _hash(rows),
        "rows": rows,
    }


if __name__ == "__main__":
    r = audit()
    print("I3_REAL_PAID_ERROR_LEDGER=" + json.dumps(
        {k:v for k,v in r.items() if k!="rows"}, sort_keys=True))
