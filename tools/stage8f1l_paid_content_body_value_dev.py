"""F1L DEV_ONLY native prototype: paid personal-content contrast at T5.

This file has NO scientific-release function. L01..L32 are never instantiated
here. F1L heldouts are reserved by preexposure documents, not by this tool.
No changes to Mind P1.3, F1JFixedRoundMind or BodyLaws.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha1
import json
from pathlib import Path

from i3.modules.body import BodyLaws, CognitiveBudget, cognitive_cost
from i3.modules.genome import midpoint
from i3.modules.world import World, WorldSpec, WaterSource, FoodPatch
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1h_prospective_native_body_value as H
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind

SCHEMA = "i3-stage8f1l-development-only-personal-content-T60/v0"
GRID_PATH = ("docs/research/studies/stage8f1-paid-microdecision/"
             "STAGE8F1L_HELDOUT_EQUAL_PAID_MEMORY_CONTENT_GRID_2026-11-22.json")
PROTOCOL_PATH = ("docs/research/studies/stage8f1-paid-microdecision/"
                 "STAGE8F1L_EQUAL_PAID_CONTENT_BODY_VALUE_PREEXPOSURE_2026-11-22.md")
GRID_BLOB = "e336c12640a9143f026afafd8de44af6a46c4c97"
PROTOCOL_BLOB = "4c89ced38db82b8edf688c44bccd81601abda057"
PREREG_MAIN = "620e58a6b149ccb8169463a33eee9bd81d4ebd22"
ARMS = ("full", "full_sham", "stale_owned_t1_means")
RESERVED_SEEDS = frozenset(range(202611229501, 202611229533))
DEVELOPMENT_SEEDS = frozenset(range(202611229601, 202611229609))
T_SOURCE, T_FORK, T_END = 4, 5, 60

SOURCE_BLOBS = {
    "src/i3/modules/mind.py": "a77ee89dcb65ea0d841d3cd71a64e539dc9fc445",
    "src/i3/modules/body.py": "22f0920a7bbb8ea4197cb7e2020fa63d2e7aa49b",
    "src/i3/modules/world.py": "d9093953216d318c10b19c805d145dabb9c96abd",
    "src/i3/modules/genome.py": "003e923aa93b0b284a7f732fc91f3f02538dd85c",
    "tools/stage8f1j_fixed_round_paid_competition.py":
        "0030bc957ef53800d95adcb617a98cb4c856ee5d",
    "tools/stage8f1h_prospective_native_body_value.py":
        "02c5ece502729e3fa341f17cfa9cdc03e8c50bf4",
    "tools/stage8f1c_paid_postaction_learning.py":
        "c3d00fe078cac0ad9487ac39c2c8c7e081f32313",
    "tools/stage8f1d_next_decision_retention.py":
        "19f10a02b73759b52856e177ac3731f5826281c6",
}


def git_blob(data):
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_readonly_prereg():
    """Verify frozen L origins and reference sources, WITHOUT instantiating one."""
    for path, expected in SOURCE_BLOBS.items():
        if git_blob(Path(path).read_bytes()) != expected:
            raise ValueError("F1L reference-source SHA drift: " + path)
    if (git_blob(Path(GRID_PATH).read_bytes()) != GRID_BLOB or
            git_blob(Path(PROTOCOL_PATH).read_bytes()) != PROTOCOL_BLOB):
        raise ValueError("F1L FROZEN GRID/PROTOCOL DRIFT")
    grid = json.loads(Path(GRID_PATH).read_bytes())
    if (grid.get("schema") !=
            "i3-stage8f1l-heldout-personal-content-net-body-value/v0" or
            grid.get("phase") != "PREEXPOSURE_ONLY_NO_WORLD_STEP" or
            grid.get("scientific_exposure_authorized") is not False or
            grid.get("personal_history_ticks") != T_SOURCE or
            grid.get("fork_tick") != T_FORK or
            grid.get("final_tick") != T_END or
            grid.get("arms") != list(ARMS) or
            grid.get("frozen_prior_results", {}).get("F1K") !=
            "INCONCLUSIVE_NO_REAL_SURCHARGE" or
            grid.get("source_policy") !=
            "tools.stage8f1j_fixed_round_paid_competition.F1JFixedRoundMind"):
        raise ValueError("F1L preregistered design drift")
    origins = grid.get("origins", [])
    ecologies = grid.get("ecologies", [])
    if (len(origins) != 32 or len(ecologies) != 8 or
            [r.get("id") for r in origins] !=
            ["L%02d" % i for i in range(1, 33)] or
            [r.get("seed") for r in origins] !=
            list(range(202611229501, 202611229533)) or
            any(sum(r["ecology"] == e["id"] for r in origins) != 4
                for e in ecologies)):
        raise ValueError("F1L reserve or ecology changed")
    return grid


def dev_grid(full=False):
    """Disjoint alternative ecologies; short smoke or 8-root T60 rehearsal."""
    ecologies = [
        {"id": "DEV_L_west_springs", "water": [0, 1], "water_gain": 17,
         "water_stock": 3, "water_max_stock": 3, "water_restock_every": 4,
         "food": [2, 2], "token": "dev-f1l-cress", "food_gain": 16,
         "integrity_delta": 1.25, "food_quantity": 3,
         "food_max_quantity": 3, "food_restock_every": 5},
        {"id": "DEV_L_east_tuber", "water": [2, 1], "water_gain": 25,
         "water_stock": 2, "water_max_stock": 2, "water_restock_every": 3,
         "food": [0, 2], "token": "dev-f1l-tuber", "food_gain": 29,
         "integrity_delta": -0.75, "food_quantity": 2,
         "food_max_quantity": 2, "food_restock_every": 6},
    ]
    origins = []
    for i in range(8):
        j = i % 4
        origins.append({
            "id": "DEV_L%02d" % (i + 1),
            "ecology": ecologies[i // 4]["id"],
            "seed": 202611229601 + i,
            "body": [60 + j, 69 - j, 34 + j * 0.5,
                     93 - j * 0.3, 96 - j * 0.2],
        })
    if not full:
        origins = [origins[0], origins[4]]
    return {
        "schema": "i3-stage8f1l-dev-%s/v0" %
                  ("t60" if full else "smoke"),
        "phase": "DEV_ONLY", "world": {"width": 3, "height": 3,
        "spawn": [1, 1], "laws": "BodyLaws() i3-body-laws-v2",
        "changes": []},
        "ecologies": ecologies, "origins": origins,
        "personal_history_ticks": T_SOURCE, "fork_tick": T_FORK,
        "final_tick": 60 if full else 9, "arms": list(ARMS),
    }


def validate_dev(grid):
    if grid not in (dev_grid(), dev_grid(full=True)):
        raise ValueError("F1L DEV_ONLY accepts only fixed disjoint fixtures")
    reserved = verify_readonly_prereg()
    if (any(r["seed"] in RESERVED_SEEDS or
            r["seed"] not in DEVELOPMENT_SEEDS or
            not r["id"].startswith("DEV_L") for r in grid["origins"]) or
            {e["id"] for e in grid["ecologies"]} &
            {e["id"] for e in reserved["ecologies"]} or
            any(e["water"] in ([1, 1], [0, 0])
                for e in grid["ecologies"])):
        raise ValueError("F1L reserve/DEV contamination")
    return grid


def new_world(grid, origin):
    """Creation restricted to development roots even if called directly."""
    if (origin not in grid["origins"] or
            origin["seed"] not in DEVELOPMENT_SEEDS or
            not origin["id"].startswith("DEV_L")):
        raise PermissionError("F1L L01..L32 may NOT be instantiated by DEV")
    ecology = next(e for e in grid["ecologies"]
                   if e["id"] == origin["ecology"])
    spec = grid["world"]
    return World(WorldSpec(
        name="F1L_DEV_ORIGIN_" + origin["id"] + "_" + ecology["id"],
        width=spec["width"], height=spec["height"],
        spawn=tuple(spec["spawn"]), body=tuple(origin["body"]),
        water={tuple(ecology["water"]): WaterSource(
            gain=ecology["water_gain"], stock=ecology["water_stock"],
            max_stock=ecology["water_max_stock"],
            restock_every=ecology["water_restock_every"])},
        food={tuple(ecology["food"]): FoodPatch(
            token=ecology["token"], quantity=ecology["food_quantity"],
            max_quantity=ecology["food_max_quantity"],
            restock_every=ecology["food_restock_every"])},
        token_effects={ecology["token"]:
                       (ecology["food_gain"], ecology["integrity_delta"])},
        changes=(), laws=BodyLaws(),
    ))


def paid_step(world, mind, mode="full", t1_stats=None):
    """Charge every native thought, then pay real post-action learning."""
    if world.dead:
        raise RuntimeError("no decision after irreversible death")
    if mode not in ARMS:
        raise ValueError("non-preregistered memory arm")
    before_world = D._snapshot_world(world)
    before_mind = C.seal_mind(mind)
    cap = world.capture()
    effects_owned = deepcopy(mind.effects)
    td_owned = deepcopy(mind.values)
    buffer_owned = deepcopy(mind.buffer)
    keys = []
    if mode == "full_sham":
        mind.effects = deepcopy(mind.effects)
    elif mode == "stale_owned_t1_means":
        if t1_stats is None or not t1_stats:
            raise ValueError("T1 personal paid memory is required")
        eligible = set(t1_stats) & set(effects_owned.stats)
        keys = sorted(eligible, key=repr)
        mind.effects = deepcopy(mind.effects)
        for key in keys:
            past, current = t1_stats[key], mind.effects.stats[key]
            if (len(past) != 3 or len(current) != 3 or
                    len(past[1]) != 5 or len(current[1]) != 5):
                raise ValueError("non-native personal mean key")
            current[1][:] = past[1]
    exposed = C.seal_mind(mind)
    budget = CognitiveBudget(world.body, world.laws)
    action, param, work, info = mind.decide(cap, budget)
    after_decide = C.seal_mind(mind)
    if world.t != before_world["t"] or work != budget.work:
        raise AssertionError("unpaid decision or hidden World.step")
    mind.effects = effects_owned
    if mind.values != td_owned or list(mind.buffer) != list(buffer_owned):
        raise AssertionError("F1L cannot interfere with TD or buffer")
    after_restore = C.seal_mind(mind)
    promised = dict(zip(("energy", "vigilance"),
                        cognitive_cost(world.laws, work)))
    raw = world.step(action, param, work)
    C.paid_bill(world.laws, work, raw["cognitive_accounting"])
    native = {"t": raw["t"], "body": list(raw["body"]),
              "dead": list(raw["dead"]), "moved": raw["moved"],
              "cognitive_accounting": deepcopy(raw["cognitive_accounting"])}
    after_motor = D._snapshot_world(world)
    post = H._pay_new_learning(world, mind, raw)
    row = {
        "t": world.t, "before_world": before_world,
        "before_mind": before_mind,
        "capture": json.loads(C.canonical(cap)),
        "capture_sha256": C.digest(cap),
        "readout_mode": mode,
        "temporary_prior_mean_keys": [list(key) for key in keys],
        "exposed_mind_during_decision": exposed,
        "after_decision_exposed_mind": after_decide,
        "after_restoration_before_motor": after_restore,
        "action": action, "param": param,
        "decision_info": json.loads(C.canonical(info)),
        "cognitive_work": asdict(work),
        "decision_remaining": list(budget.remaining),
        "requested_native_cost": promised,
        "native_motor": native, "after_motor_world": after_motor,
        "postaction": post,
        "after_paid_learning_world": D._snapshot_world(world),
        "after_paid_learning_mind": C.seal_mind(mind),
        "no_experimental_action_override": True,
    }
    row["receipt_sha256"] = C.digest(row)
    return row


def source(grid, origin):
    world = new_world(grid, origin)
    mind = F1JFixedRoundMind(midpoint(), origin["seed"])
    if (mind.effects.stats or mind.buffer or
            any(any(v != 0. for v in row) for row in mind.values) or
            world.t != 0 or world.dead):
        raise AssertionError("DEV birth with synthetic personal memory")
    genesis = {"world": D._snapshot_world(world),
               "mind": C.seal_mind(mind)}
    steps, error, t1_stats = [], None, {}
    for tick in range(1, T_SOURCE + 1):
        if world.dead:
            break
        try:
            steps.append(paid_step(world, mind))
            if tick == 1:
                t1_stats = deepcopy(mind.effects.stats)
        except (ValueError, KeyError, RuntimeError, AssertionError) as exc:
            error = {"attempted_tick": tick, "type": type(exc).__name__,
                     "message": str(exc)}
            break
    valid = (error is None and len(steps) == T_SOURCE and
             world.t == T_SOURCE and not world.dead and
             bool(t1_stats) and
             all(s["postaction"]["status"] == "PAID_LEARNED"
                 for s in steps))
    rec = {
        "origin": origin, "genesis": genesis, "source_steps": steps,
        "paid_t1_mean_anchor": [
            {"key": list(k), "stat": deepcopy(v)}
            for k, v in sorted(t1_stats.items(), key=lambda x: repr(x[0]))
        ],
        "source_tick4_world": D._snapshot_world(world),
        "source_tick4_mind": C.seal_mind(mind),
        "valid_paid_personal_source": valid, "source_error": error,
        "run_life_used": False,
    }
    rec["source_receipt_sha256"] = C.digest(rec)
    return world, mind, t1_stats, rec


def followup(world, mind, mode, t1_stats, horizon):
    steps, error = [], None
    while not world.dead and world.t < horizon:
        try:
            readout = mode if world.t == T_SOURCE else "full"
            steps.append(paid_step(
                world, mind, readout,
                t1_stats if readout == "stale_owned_t1_means" else None,
            ))
        except (ValueError, KeyError, RuntimeError, AssertionError) as exc:
            error = {"attempted_tick": world.t + 1,
                     "type": type(exc).__name__, "message": str(exc)}
            break
    coins = ("energy", "vigilance")
    decision = {coin: 0. for coin in coins}
    learning = {coin: 0. for coin in coins}
    body_integral = [0.] * 5
    for s in steps:
        for coin in coins:
            decision[coin] += s["native_motor"]["cognitive_accounting"][coin]["paid"]
            bill = s["postaction"]["actual_paid_learning_bill"]
            if bill is not None:
                learning[coin] += bill[coin]["paid"]
        for i, v in enumerate(s["postaction"]["body_after_any_learning"]):
            body_integral[i] += v
    metrics = {
        "lived_ticks_t5_t60": len(steps),
        "alive_at_horizon": (world.t == horizon and not world.dead and
                             error is None),
        "terminal_tick": world.t, "terminal_dead": list(world.dead),
        "terminal_body": list(world.body),
        "terminal_position": list(world.pos),
        "terminal_water_stock":
            sorted([[list(k), v.stock] for k, v in world.water.items()]),
        "terminal_food_quantity":
            sorted([[list(k), v.quantity] for k, v in world.food.items()]),
        "terminal_inventory":
            sorted([[k, v] for k, v in world.inventory.items()]),
        "cumulated_body": body_integral,
        "paid_decision": decision, "paid_learning": learning,
        "water_drinks": sum(s["action"] == "boire" for s in steps),
        "foods_collected": sum(s["action"] == "collecter" for s in steps),
        "foods_actually_eaten": sum(s["action"] == "manger" for s in steps),
        "native_error": error,
    }
    rec = {"policy": mode, "steps": steps,
           "last_world": D._snapshot_world(world),
           "last_mind": C.seal_mind(mind), "metrics": metrics}
    rec["trajectory_sha256"] = C.digest(rec)
    return rec


def semantic_sham_step(step):
    """Do not mistake expected sham labels for physical differences."""
    return {k: v for k, v in step.items() if
            k not in ("readout_mode", "receipt_sha256")}


def compare(arms, source_valid):
    if not source_valid:
        return {"source_valid": False, "sham_neutral": False,
                "equal_t5_decision_cost": False, "motor_changed": None,
                "delta_lived_ticks": None, "pareto": None,
                "arm_valid": False}
    full, sham, stale = (arms[p] for p in ARMS)
    neutral = (full["metrics"] == sham["metrics"] and
               full["last_world"] == sham["last_world"] and
               full["last_mind"] == sham["last_mind"] and
               len(full["steps"]) == len(sham["steps"]) and
               all(semantic_sham_step(a) == semantic_sham_step(b)
                   for a, b in zip(full["steps"], sham["steps"])))
    valid = neutral and all(arm["metrics"]["native_error"] is None and
                            arm["steps"] for arm in arms.values())
    if not valid:
        return {"source_valid": True, "sham_neutral": neutral,
                "equal_t5_decision_cost": False, "motor_changed": None,
                "delta_lived_ticks": None, "pareto": None,
                "arm_valid": False}
    left, right = full["steps"][0], stale["steps"][0]
    equal = all(left[k] == right[k] for k in (
        "before_world", "before_mind", "capture", "capture_sha256",
        "cognitive_work", "requested_native_cost", "decision_remaining",
    )) and (left["native_motor"]["cognitive_accounting"] ==
            right["native_motor"]["cognitive_accounting"])
    delta = (full["metrics"]["lived_ticks_t5_t60"] -
             stale["metrics"]["lived_ticks_t5_t60"])
    pareto = "NOT_EQUAL_SURVIVAL"
    if (delta == 0 and full["metrics"]["alive_at_horizon"] and
            stale["metrics"]["alive_at_horizon"]):
        x = full["metrics"]["terminal_body"]
        y = stale["metrics"]["terminal_body"]
        if all(a >= b - 1e-9 for a, b in zip(x, y)) and any(
                a > b + 1e-9 for a, b in zip(x, y)):
            pareto = "FULL_FIVE_CHANNEL_DOMINANCE"
        elif all(b >= a - 1e-9 for a, b in zip(x, y)) and any(
                b > a + 1e-9 for a, b in zip(x, y)):
            pareto = "STALE_FIVE_CHANNEL_DOMINANCE"
        elif all(abs(a - b) <= 1e-9 for a, b in zip(x, y)):
            pareto = "FIVE_CHANNELS_EQUAL"
        else:
            pareto = "MIXED_BODILY_TRADEOFF"
    return {
        "source_valid": True, "sham_neutral": neutral,
        "equal_t5_decision_cost": equal,
        "motor_changed": (left["action"], left["param"]) !=
                         (right["action"], right["param"]),
        "delta_lived_ticks": delta, "pareto": pareto,
        "arm_valid": True,
    }


def produce(grid, phase="DEV_ONLY", on_case=None):
    """Only DEV fixtures. There is deliberately no F1L scientific release."""
    if phase != "DEV_ONLY":
        raise PermissionError("F1L HELDOUT_UNEXPOSED: no one-shot authority exists")
    validate_dev(grid)
    rows = []
    for origin in grid["origins"]:
        world, mind, t1_stats, source_receipt = source(grid, origin)
        arms = {}
        if source_receipt["valid_paid_personal_source"]:
            arms = {
                policy: followup(
                    deepcopy(world), deepcopy(mind), policy,
                    t1_stats, grid["final_tick"])
                for policy in ARMS
            }
        comparison = compare(arms, source_receipt["valid_paid_personal_source"])
        case = {"origin": origin, "source": source_receipt,
                "arms": arms, "comparison": comparison}
        case["case_sha256"] = C.digest(case)
        rows.append(case)
        if on_case is not None:
            on_case(case)
    report = {
        "schema": SCHEMA, "phase": phase,
        "preregistered_main": PREREG_MAIN,
        "grid_blob_sha": GRID_BLOB, "protocol_blob_sha": PROTOCOL_BLOB,
        "origin_count": len(rows),
        "origin_ids": [r["id"] for r in grid["origins"]],
        "source_policy": "F1JFixedRoundMind",
        "arms": list(ARMS), "source_ticks": T_SOURCE,
        "fork_tick": T_FORK, "final_tick": grid["final_tick"],
        "no_motor_override": True, "run_life_used": False,
        "scientific_verdict": None,
        "producer_only_status": "DEV_ONLY_NOT_SCIENTIFIC",
        "historical_F1K": "INCONCLUSIVE_NO_REAL_SURCHARGE",
        "rows": rows,
    }
    report["provenance_sha256"] = C.digest({
        "phase": phase,
        "grid_blob_sha": GRID_BLOB, "protocol_blob_sha": PROTOCOL_BLOB,
        "cases": [r["case_sha256"] for r in rows],
    })
    return report


def main():
    ap = argparse.ArgumentParser(description="F1L DEV-only, no L01..L32")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--full-rehearsal", action="store_true")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    grid = dev_grid(full=args.full_rehearsal)
    result = produce(grid)
    with Path(args.output).open("xb") as out:
        out.write(C.canonical(result))
    print(json.dumps({
        "phase": "DEV_ONLY", "origins": result["origin_count"],
        "status": result["producer_only_status"],
        "source_valid": sum(r["source"]["valid_paid_personal_source"]
                            for r in result["rows"]),
        "sham_neutral": sum(r["comparison"]["sham_neutral"]
                            for r in result["rows"]),
        "equal_t5_decision_cost": sum(
            r["comparison"]["equal_t5_decision_cost"]
            for r in result["rows"]),
        "L_holdouts_exposed": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
