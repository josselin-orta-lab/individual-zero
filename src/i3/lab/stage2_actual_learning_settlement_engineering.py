"""Actual one-step native World and outcome-learning cost settlement.

SOURCE-FROZEN engineering-only experiment, see
STAGE2_ACTUAL_LEARNING_SETTLEMENT_PREFLIGHT_2026-11-12.md.
No individual autonomously chooses the fixed action in this test.
No scientific lives, no historical indices, no change to Mind or BodyLaws.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost, validate_body)
from ..modules.world import World, WorldSpec
from . import stage2_readout_learning_affordability as ORIGINAL
from .stage2_action_conditional_existing_effects import passive_readouts
from .stage2_action_phase_readout_budget import proposed_readout_work

SCHEMA = "i3-stage2.1-actual-World-next-learning-settlement-engineering/v1"
CURRENCIES = ("energy", "vigilance")


def _sha(value):
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()


def _assert_paid(work, laws, accounting):
    expected = cognitive_cost(laws, work)
    for name, price in zip(CURRENCIES, expected):
        actual = accounting.get(name)
        if (not isinstance(actual, dict)
                or abs(actual.get("requested", -999.)-price) > 1e-10
                or abs(actual.get("paid", -999.)-price) > 1e-10
                or actual.get("unpaid") != 0.):
            raise RuntimeError("forged or unpaid native two-currency receipt")
    return expected


def settle_one(name, body, *, extra_requested):
    """One explicitly fixed engineering action, no autonomous motor claim."""
    if type(name) is not str or name not in dict(ORIGINAL.CASES):
        raise ValueError("case outside predeclared fixture set")
    if tuple(body) != dict(ORIGINAL.CASES)[name]:
        raise PermissionError("cannot retune body for an old frozen case")
    if type(extra_requested) is not bool:
        raise TypeError("explicit native readout request required")
    initial = validate_body(body)
    spec = WorldSpec(
        name="engineering-learning-settlement-" + name,
        width=1, height=1, spawn=(0, 0), body=initial,
        laws=BodyLaws())
    world = World(spec)
    mind = ORIGINAL._original_mind(initial)
    budget = CognitiveBudget(world.body, world.laws)
    if not budget.try_spend(ORIGINAL.DECISION):
        raise RuntimeError("fixed base decision bill unavailable")

    baseline = budget.work
    extra = proposed_readout_work(len(mind.buffer))
    source_sha_before = ORIGINAL._source_seal(mind)
    granted = False
    readouts_executed = 0
    if extra_requested:
        granted = ORIGINAL._authorize_optional(
            budget, action=ORIGINAL.ACTION, n=len(mind.buffer))
        if granted:
            # The resulting forecast is deliberately not delivered to
            # any controller. This is an actual computed-and-discarded arm.
            _ignored = passive_readouts(mind, initial, ORIGINAL.ACTION)
            if not _ignored["scalar_forecasts"]:
                raise RuntimeError("paid readout did not execute")
            readouts_executed += 1
        elif budget.work != baseline:
            raise RuntimeError("denied work changed allowance")
    if ORIGINAL._source_seal(mind) != source_sha_before:
        raise RuntimeError("optional computation mutated source or RNG")
    decision_bill = budget.work
    expected_bill = CognitiveWork(
        cycles=baseline.cycles+(extra.cycles if granted else 0),
        simulated_steps=baseline.simulated_steps,
        memory_items=baseline.memory_items+
                     (extra.memory_items if granted else 0),
        replays=baseline.replays)
    if decision_bill != expected_bill:
        raise RuntimeError("actual optional budget differs from preflight")
    result = world.step(ORIGINAL.ACTION, ORIGINAL.PARAM, decision_bill)
    decision_prices = _assert_paid(
        decision_bill, world.laws, result["cognitive_accounting"])
    immediate = tuple(world.body)
    if immediate != tuple(result["body"]) or result["dead"]:
        raise RuntimeError("predeclared nonterminal step did not settle")

    mind.observe_outcome(result)
    learning = CognitiveBudget(immediate, world.laws)
    replay_limit = mind.prepare_learning(result, learning)
    learned = replay_limit is not None
    # The actual World learning payment occurs before trained state updates.
    if learned:
        learning_account = world.pay_cognition(learning.work)
        _assert_paid(learning.work, world.laws, learning_account)
        result["body"] = world.body
        replay_actual = mind.learn_from_outcome(
            result, replay_limit=replay_limit)
        if replay_actual != replay_limit:
            raise RuntimeError("actual replay exceeded prepaid count")
    else:
        if learning.work != CognitiveWork():
            raise RuntimeError("denied learning retained a phantom charge")
        learning_account = {
            c: {"requested": 0., "paid": 0., "unpaid": 0.}
            for c in CURRENCIES}
        replay_actual = 0
    post = tuple(world.body)
    _assert_paid(learning.work, world.laws, learning_account)

    # Compare against existing pure-contract projections for the identical
    # precommitted case. No new synthetic body is tuned to an observed result.
    projection = ORIGINAL.examine(initial, extra_requested=extra_requested)
    if (projection["optional_status"] !=
            ("NOT_REQUESTED" if not extra_requested else
             "MODEL_AUTHORIZED" if granted else "NO_FUNDED_READOUT")
            or projection["cumulative_decision_work"] != asdict(decision_bill)
            or tuple(projection["post_action_body"]) != immediate
            or projection["next_base_learning_model_authorized"] != learned
            or projection["next_base_learning_work"] != asdict(learning.work)):
        raise RuntimeError("actual World disproved existing pure model contract")
    projected_post = projection["next_learning_pure_projected_body"]
    if projected_post is not None and tuple(projected_post) != post:
        raise RuntimeError("actual native learning settlement differs from projection")
    if not learned and post != immediate:
        raise RuntimeError("unfunded learning changed body")
    if world.t != 1:
        raise RuntimeError("engineering World unexpectedly ran extra steps")

    return {
        "case": name, "optional_requested": extra_requested,
        "optional_funded": granted, "optional_readouts_executed": readouts_executed,
        "model_price_is_not_host_cpu_joules": True,
        "motor_source": "FIXED_ENGINEERING_COMMAND_NOT_NATIVE_DECISION",
        "factual_motor": ORIGINAL.ACTION,
        "initial_body": initial, "immediate_post_world_body": immediate,
        "post_paid_learning_body": post,
        "decision_work": asdict(decision_bill),
        "decision_energy_vigilance": dict(zip(CURRENCIES, decision_prices)),
        "world_decision_accounting": result["cognitive_accounting"],
        "learning_status": "PAID_LEARNING" if learned else "NO_FUNDED_LEARNING",
        "learning_work": asdict(learning.work),
        "world_learning_accounting": learning_account,
        "actual_learn_from_outcome_executed": learned,
        "actual_replays_executed": replay_actual,
        "world_steps": world.t,
        "source_unchanged_before_outcome": True,
        "pure_contract_matches_actual_world": True,
    }


def audit():
    rows = []
    for name, body in ORIGINAL.CASES:
        rows.append({
            "case": name,
            "baseline": settle_one(name, body, extra_requested=False),
            "optional": settle_one(name, body, extra_requested=True),
        })
    by = {row["case"]: row for row in rows}
    loss = []
    for name in ("energy_boundary", "vigilance_boundary"):
        pair = by[name]
        if (pair["baseline"]["learning_status"] != "PAID_LEARNING"
                or pair["optional"]["learning_status"] != "NO_FUNDED_LEARNING"
                or pair["optional"]["optional_readouts_executed"] != 1):
            raise RuntimeError("declared lost-learning falsifier failed")
        loss.append(name)
    both = by["both_funded"]
    if any(both[mode]["learning_status"] != "PAID_LEARNING"
           for mode in ("baseline", "optional")):
        raise RuntimeError("both-funded control failed")
    denied = by["optional_denied"]
    if (denied["optional"]["optional_funded"]
            or denied["optional"]["optional_readouts_executed"]
            or denied["baseline"]["immediate_post_world_body"] !=
               denied["optional"]["immediate_post_world_body"]
            or denied["baseline"]["post_paid_learning_body"] !=
               denied["optional"]["post_paid_learning_body"]):
        raise RuntimeError("denied optional work changed physical body")
    deterministic = [{
        "case": row["case"],
        "baseline": row["baseline"],
        "optional": row["optional"],
    } for row in rows]
    return {
        "schema": SCHEMA,
        "status": "ACTUAL_WORLD_LEARNING_SETTLEMENT_PASS",
        "frozen_cases": len(rows), "engineering_Worlds_constructed": 8,
        "engineering_World_steps_executed": 8,
        "optional_actual_readouts_executed": sum(
            x["optional"]["optional_readouts_executed"] for x in rows),
        "actual_lost_learning_opportunities": loss,
        "actual_native_world_step_and_learning_payment": True,
        "actual_native_outcome_learning_executed_only_if_funded": True,
        "baseline_action_selected_by_Mind": False,
        "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
        "deterministic_aggregate_sha256": _sha(deterministic),
        "rows": rows,
    }


if __name__ == "__main__":
    print("I3_STAGE2_ACTUAL_LEARNING_SETTLEMENT=" +
          json.dumps(audit(), sort_keys=True, separators=(",", ":")))
