"""Source-frozen native-choice cost-only bridge, no scientific life.

See STAGE2_NATIVE_CHOICE_COST_BRIDGE_PREFLIGHT_2026-11-12.md.
The individual controls only its native motor selection. The laboratory
requests an optional readout after that choice, and always discards it.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.world import World, WorldSpec
from . import stage2_readout_learning_affordability as SOURCE
from .stage2_action_conditional_existing_effects import passive_readouts
from .stage2_actual_learning_settlement_engineering import _assert_paid

SCHEMA = "i3-stage2.1-native-choice-cost-bridge-engineering/v1"
GENOME_SEED = 100061


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False, default=str).encode()).hexdigest()


def run_arm(case, body, *, request_optional):
    if type(case) is not str or case not in dict(SOURCE.CASES):
        raise ValueError("unknown frozen engineering case")
    if tuple(body) != dict(SOURCE.CASES)[case]:
        raise PermissionError("changed body from predeclared case")
    if type(request_optional) is not bool:
        raise TypeError("optional request flag must be boolean")
    world = World(WorldSpec(
        name="engineering-native-choice-cost-" + case,
        width=1, height=1, spawn=(0, 0), body=tuple(body),
        laws=BodyLaws()))
    mind = Mind(midpoint(), GENOME_SEED)
    budget = CognitiveBudget(world.body, world.laws)
    cap = world.capture()
    action, param, work, info = mind.decide(cap, budget)
    if work != budget.work:
        raise RuntimeError("native decision declared work not authorized")
    if (action is None) != (mind.last is None):
        raise RuntimeError("native null choice has inconsistent first-person history")
    if action is not None and (tuple(mind.last[0]) != cap["body"]
                              or mind.last[2:] != (action, param)):
        raise RuntimeError("native motor not owned by original Mind")
    # This seal includes both RNGs. Optional measurement must not update
    # memory, values, intentions or stochastic control.
    pre_optional_source = SOURCE._source_seal(mind)
    native_work = work
    extra_paid = False
    readouts_executed = 0
    optional_status = "NOT_REQUESTED"
    if request_optional:
        if action is None:
            optional_status = "NO_NATIVE_MOTOR"
        elif SOURCE._authorize_optional(
                budget, action=action, n=len(mind.buffer)):
            optional_status = "OPTIONAL_PAID_AND_DISCARDED"
            extra_paid = True
            # The actual host readout is executed *after* the model
            # permission, then discarded. It never controls the motor.
            discarded = passive_readouts(mind, cap["body"], action)
            if not discarded["scalar_forecasts"]:
                raise RuntimeError("funded additional readout not executed")
            readouts_executed = 1
        else:
            optional_status = "OPTIONAL_DENIED"
    if SOURCE._source_seal(mind) != pre_optional_source:
        raise RuntimeError("extra readout mutated the decision maker or RNG")
    if not extra_paid and budget.work != native_work:
        raise RuntimeError("denied optional work incurred phantom bill")
    if extra_paid and budget.work == native_work:
        raise RuntimeError("optional readout performed without additional work")
    if action is None and readouts_executed:
        raise RuntimeError("null motor cannot acquire action-specific readout")

    result = world.step(action, param, budget.work)
    decision_paid = _assert_paid(
        budget.work, world.laws, result["cognitive_accounting"])
    immediate = tuple(world.body)
    if tuple(result["body"]) != immediate:
        raise RuntimeError("World returned a body different from its own")
    learning = CognitiveBudget(immediate, world.laws)
    learning_status = "NO_NATIVE_MOTOR"
    learned = False
    if result["dead"]:
        learning_status = "TERMINAL_NO_LEARNING"
    elif mind.last is not None:
        mind.observe_outcome(result)
        replay_limit = mind.prepare_learning(result, learning)
        if replay_limit is not None:
            paid = world.pay_cognition(learning.work)
            _assert_paid(learning.work, world.laws, paid)
            result["body"] = world.body
            executed = mind.learn_from_outcome(
                result, replay_limit=replay_limit)
            if executed != replay_limit:
                raise RuntimeError("native replay count mismatched prepaid count")
            learning_status = "PAID_LEARNING"
            learned = True
        else:
            learning_status = "NO_FUNDED_LEARNING"
    if not learned:
        if learning.work != CognitiveWork() or tuple(world.body) != immediate:
            raise RuntimeError("unfunded learning changed body or work")
        paid = {c: {"requested": 0.0, "paid": 0.0, "unpaid": 0.0}
                for c in ("energy", "vigilance")}
    _assert_paid(learning.work, world.laws, paid)
    if world.t != 1:
        raise RuntimeError("multiple World steps on one-step bridge")
    return {
        "case": case,
        "request_optional": request_optional,
        "native_motor": action,
        "native_param": param,
        "native_funding": info["funding"],
        "native_pre_optional_work": asdict(native_work),
        "native_selected_option": info.get("option"),
        "original_mind_last_before_optional": action is not None,
        "optional_status": optional_status,
        "optional_readouts_executed": readouts_executed,
        "optional_paid": extra_paid,
        "pre_optional_source_unchanged": True,
        "cumulative_decision_work": asdict(budget.work),
        "actual_decision_model_energy": decision_paid[0],
        "actual_decision_model_vigilance": decision_paid[1],
        "world_decision_receipt": result["cognitive_accounting"],
        "immediate_post_world_body": immediate,
        "native_outcome_terminal": bool(result["dead"]),
        "learning_status": learning_status,
        "actual_native_learning_executed": learned,
        "native_learning_work": asdict(learning.work),
        "native_learning_receipt": paid,
        "post_paid_learning_body": tuple(world.body),
        "world_steps": world.t,
        "host_joules_calibrated": False,
    }


def audit():
    rows = []
    for case, body in SOURCE.CASES:
        baseline = run_arm(case, body, request_optional=False)
        optional = run_arm(case, body, request_optional=True)
        for key in ("native_motor", "native_param", "native_funding",
                    "native_pre_optional_work", "native_selected_option",
                    "original_mind_last_before_optional"):
            if baseline[key] != optional[key]:
                raise RuntimeError("two matched arms changed native pre-cost decision")
        if (optional["optional_status"] in ("OPTIONAL_DENIED", "NO_NATIVE_MOTOR")
                and (baseline["immediate_post_world_body"] !=
                     optional["immediate_post_world_body"]
                     or baseline["post_paid_learning_body"] !=
                        optional["post_paid_learning_body"])):
            raise RuntimeError("unfunded optional request changed actual World path")
        rows.append({"case": case, "reference": baseline, "optional": optional})

    status_counts = {
        s: sum(r["optional"]["optional_status"] == s for r in rows)
        for s in ("NO_NATIVE_MOTOR", "OPTIONAL_DENIED",
                  "OPTIONAL_PAID_AND_DISCARDED")}
    lost = [r["case"] for r in rows
            if r["reference"]["learning_status"] == "PAID_LEARNING"
            and r["optional"]["learning_status"] == "NO_FUNDED_LEARNING"]
    return {
        "schema": SCHEMA,
        "status": "NATIVE_CHOICE_COST_BRIDGE_PASS",
        "action_mediation": "NO_ACTION_MEDIATION_OBSERVED",
        "native_choice_source": "ORIGINAL_MIND_DECIDE_ON_EACH_ARM",
        "additional_computation_is_laboratory_requested": True,
        "actual_optional_readouts_delivered_to_policy": 0,
        "frozen_body_cases": len(SOURCE.CASES),
        "engineering_Worlds_constructed": 8,
        "engineering_World_steps": 8,
        "science_lives": 0,
        "optional_status_counts": status_counts,
        "lost_native_learning_allocations": lost,
        "original_native_motor_pair_parity": True,
        "original_decision_model_cost_pair_parity": True,
        "host_CPU_joule_calibration": False,
        "scientific_verdict": "NOT_ISSUED",
        "deterministic_aggregate_sha256": _digest(rows),
        "rows": rows,
    }


if __name__ == "__main__":
    print("I3_NATIVE_CHOICE_COST_BRIDGE="+json.dumps(
        audit(), sort_keys=True, separators=(",", ":")))
