"""F1F/F1G preregistered eight ecological WorldSpecs at native tick 1.

Resources are physically DORMANT at tick 0; World._apply_changes reveals
them only after the individual's authentic, pre-paid F1C first action.
This preserves the exact F1C first-person Mind/source receipt and creates
eight ecological decision contexts with real World.capture/World.step.
No new life, no genomic intervention, no action imposed.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.world import World, WorldSpec, WaterSource, FoodPatch
from i3.modules.stage8f1_paid_microdecision_mind import (
    MICRO_WORK, PaidMicrodecisionMind,
)
from tools import stage8f1_matched_native_funding as B
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D

# Immutable source/specification, not selected from observed experimental data.
ECOLOGIES = (
    ("bare", None, None),
    ("water_here", (1, 1), None),
    ("water_north", (1, 0), None),
    ("water_east", (2, 1), None),
    ("water_west", (0, 1), None),
    ("food_here", None, (1, 1)),
    ("food_east", None, (2, 1)),
    ("mixed_here_water_east_food", (1, 1), (2, 1)),
)
TOKEN = "f1f-neutral-food"
SOURCE_ECO = "learned_beneficial_sleep"


def named_context(name):
    for case in ECOLOGIES:
        if case[0] == name:
            return case
    raise ValueError("ecology not named in preexposure")


def describe(case):
    name, water, food = case
    changes = []
    if water is not None:
        changes.append((1, "water_stock", water, 1))
    if food is not None:
        changes.append((1, "food_quantity", food, 1))
    return {
        "id": name,
        "water_position": list(water) if water else None,
        "food_position": list(food) if food else None,
        "water_gain": 25.0 if water else None,
        "water_initial_stock": 0 if water else None,
        "water_revealed_stock": 1 if water else None,
        "water_max_stock": 2 if water else None,
        "food_token": TOKEN if food else None,
        "food_initial_quantity": 0 if food else None,
        "food_revealed_quantity": 1 if food else None,
        "food_max_quantity": 2 if food else None,
        "scheduled_native_changes": [
            [step,kind,list(location),value]
            for step,kind,location,value in changes
        ],
        "world_spec_name": "F1F_ECO_"+name,
    }


def new_world(case):
    name, water, food = case
    spec = WorldSpec(
        name="F1F_ECO_"+name, width=3, height=3, spawn=(1,1),
        body=B.STATES[0][1], laws=BodyLaws(),
        water=({water: WaterSource(gain=25., stock=0, max_stock=2)}
               if water is not None else {}),
        food=({food: FoodPatch(token=TOKEN,quantity=0,max_quantity=2)}
              if food is not None else {}),
        changes=tuple((step,kind,tuple(pos),value)
                      for step,kind,pos,value in (
                        ([(1,"water_stock",water,1)] if water is not None else [])
                        + ([(1,"food_quantity",food,1)] if food is not None else []))),
    )
    return World(spec)


def native_original_paid_source(original, case):
    """One genuine first step per ecological spec, byte-matched F1C Mind."""
    src = original["arms"]["retain"]
    base_world, base_mind = B.make_state(B.STATES[0])
    world = new_world(case)
    mind = B.cloned_mind(PaidMicrodecisionMind,base_mind)
    cap = world.capture()
    if (C.seal_mind(mind) != src["private_before_decision"] or
            C.digest(cap) != src["capture_sha256"] or
            C.canonical(cap) != C.canonical(src["capture"])):
        raise AssertionError("ecological source changed original F1C first perception/Mind")
    authorized = CognitiveBudget(world.body, world.laws)
    action, param, work, info = mind.decide(cap,authorized)
    if (action != src["action"] or param != src["param"] or
            work != MICRO_WORK or work != authorized.work or
            asdict(work) != src["decision_work"] or
            info["funding"] != src["decision_funding"]):
        raise AssertionError("laboratory overrode original voluntary first action")
    native = world.step(action,param,work)
    if (world.t != 1 or native["dead"] or
            list(native["body"]) != src["native_motor_step"]["body"] or
            native["cognitive_accounting"] != src["native_motor_step"]["cognitive_accounting"] or
            native["moved"] != src["native_motor_step"]["moved"]):
        raise AssertionError("the first real native F1C bodily receipt changed")
    mind.observe_outcome(native)
    if C.seal_mind(mind) != src["private_before_postaction_learning"]:
        raise AssertionError("ecology caused extra pre-learning private Mind work")
    learning = CognitiveBudget(world.body, world.laws)
    replays = mind.prepare_learning(native,learning)
    if (replays != src["prepaid_replays"] or
            asdict(learning.work) != src["learning_work"]):
        raise AssertionError("F1C learning authorization has changed")
    debit = world.pay_cognition(learning.work)
    if (debit != src["paid_postaction_learning"] or
            list(world.body) != src["body_after_paid_learning"]):
        raise AssertionError("real postaction funding altered by ecological schedule")
    native["body"] = world.body
    executed = mind.learn_from_outcome(native,replay_limit=replays)
    if (executed != src["executed_replays"] or
            C.seal_mind(mind) != src["private_persisted_postaction"]):
        raise AssertionError("ecological source is not the original PAID acquired memory")
    if world.t != 1 or world.dead or world.capture()["body"] != world.body:
        raise AssertionError("no living matched next decision in ecological native World")
    # Three names, physics and private memory are evidence of the source
    # boundary, not powers given to the living Mind.
    evidence = {
        "context": describe(case),
        "source_f1c_receipt_sha256": src["receipt_sha256"],
        "pre_exposure_perception_sha256": src["capture_sha256"],
        "native_first_motor": {
            "t": native["t"], "body": src["native_motor_step"]["body"],
            "dead": list(native["dead"]), "moved": native["moved"],
            "cognitive_accounting": native["cognitive_accounting"]
        },
        "native_postaction_paid_learning": debit,
        "native_postaction_work": asdict(learning.work),
        "full_retained_mind_source_sha256":
            src["private_persisted_postaction"]["sha256"],
        "world_at_start_of_next_decision": D._snapshot_world(world),
        "first_tick_world_steps": 1,
        "first_tick_free_or_forced_actions": 0,
    }
    evidence["source_proof_sha256"] = C.digest(evidence)
    return world,mind,evidence
