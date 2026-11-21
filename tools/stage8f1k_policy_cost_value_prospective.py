"""Stage8-F1K prospective policy comparison: P1.3 vs substantive paid F1J.

No holdout exposure is performed on import or in DEV_ONLY tests. The historical
P1.3 controller, F1J, F1I and all prior scientific files remain untouched.
A separate cold auditor, not this module, is authoritative for native evidence.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha1
import json
import os
from pathlib import Path

from i3.modules.body import BodyLaws, CognitiveBudget, cognitive_cost
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import World, WorldSpec, WaterSource, FoodPatch
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1h_prospective_native_body_value as H
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind

SCHEMA = "i3-stage8f1k-policy-real-cost-prospective/v0"
GRID = "docs/research/studies/stage8f1-paid-microdecision/STAGE8F1K_HELDOUT_POLICY_VALUE_GRID_2026-11-21.json"
PROTOCOL = "docs/research/studies/stage8f1-paid-microdecision/STAGE8F1K_HELDOUT_POLICY_VALUE_PREEXPOSURE_2026-11-21.md"
PREEXPOSURE_MAIN = "212d656f71ed5f4011c069575f9235b5b11d30fd"
SOURCE_MAIN = "d727b4cbb1dc0c9490608788836d3c5c040cbae5"
GRID_BLOB = "bae149207c1fc41fb7fcc6fff11462e03dd17407"
PROTOCOL_BLOB = "f551f751eab04e58c93f432662c3181721228b13"
ARMS = ("reference_p13", "reference_sham", "fixed_round_f1j")
T_SOURCE, T_FORK, T_END = 4, 5, 60
RELEASE_ENV = "I3_F1K_ONE_SHOT_HOLDOUT_RELEASE"


def git_blob_sha(payload: bytes) -> str:
    """Calculate actual git blob identity, not a checksum of parsed JSON."""
    return sha1(b"blob " + str(len(payload)).encode("ascii") + b"\\0" + payload).hexdigest()


def release_grid(path=GRID, protocol=PROTOCOL):
    source = Path(path).read_bytes()
    method = Path(protocol).read_bytes()
    if (git_blob_sha(source) != GRID_BLOB
            or git_blob_sha(method) != PROTOCOL_BLOB):
        raise ValueError("F1K PREEXPOSURE_DRIFT: frozen blobs changed")
    grid = json.loads(source)
    if (grid.get("schema") != "i3-stage8f1k-preexposure-heldout-net-policy-value/v0"
            or grid.get("baseline_main") != SOURCE_MAIN
            or grid.get("phase") != "PREEXPOSURE_ONLY_NO_NATIVE_STEPS_AUTHORIZED_BY_THIS_DOCUMENT"
            or grid.get("source_controller") != "P1.3_Mind"
            or grid.get("reference_controller") != "i3.modules.mind.Mind (P1.3 funded-v2, exactly baseline)"
            or grid.get("competing_controller") != "tools.stage8f1j_fixed_round_paid_competition.F1JFixedRoundMind (exact baseline)"
            or grid.get("world",{}).get("laws") != "BodyLaws() i3-body-laws-v2"
            or grid.get("same_genome") != "midpoint()"
            or grid.get("personal_history_ticks") != T_SOURCE
            or grid.get("fork_tick") != T_FORK
            or grid.get("final_tick") != T_END
            or grid.get("arms") != list(ARMS)
            or grid.get("frozen_prior_results",{}).get("F1I") != "INCONCLUSIVE_COST_GATE"
            or grid.get("frozen_prior_results",{}).get("stage2") != "NOT_ISSUED/HOLD_NO_VERDICT"):
        raise ValueError("F1K preregistered authority/contrast drift")
    if ([r.get("id") for r in grid.get("origins",[])] !=
            ["K"+str(i).zfill(2) for i in range(1,17)]
            or [r.get("seed") for r in grid["origins"]] !=
            list(range(202611219101,202611219117))
            or len(grid.get("ecologies",[])) != 4
            or any(len([r for r in grid["origins"]
                        if r["ecology"]==f["id"]]) != 4
                   for f in grid["ecologies"])):
        raise ValueError("F1K original 16 reserved sources changed")
    return grid


def dev_grid():
    """Explicitly disjoint technical fixtures; NEVER substitute for K01..K16."""
    families = [
        {"id":"DEV_corner_supplies","water":[1,1],"water_gain":12,
         "water_stock":3,"water_max_stock":3,"water_restock_every":0,
         "food":[1,1],"token":"f1k-dev-apple","food_gain":19,
         "integrity_delta":1,"food_quantity":3,"food_max_quantity":3,
         "food_restock_every":0},
        {"id":"DEV_distant_well","water":[0,1],"water_gain":15,
         "water_stock":2,"water_max_stock":2,"water_restock_every":3,
         "food":[1,2],"token":"f1k-dev-berry","food_gain":16,
         "integrity_delta":-0.25,"food_quantity":2,
         "food_max_quantity":2,"food_restock_every":4},
    ]
    return {
        "schema":"i3-stage8f1k-dev-grid/v0",
        "phase":"DEV_ONLY",
        "world":{"width":3,"height":3,"spawn":[1,1],
                 "laws":"BodyLaws() i3-body-laws-v2","changes":[]},
        "ecologies":families,
        "origins":[
            {"id":"DEV01","ecology":families[0]["id"],"seed":202611219201,
             "body":[55.,69.,11.,90.,95.]},
            {"id":"DEV02","ecology":families[1]["id"],"seed":202611219202,
             "body":[53.,62.,10.,91.,94.]},
        ],
        "personal_history_ticks":4,"fork_tick":5,
        "final_tick":9,"arms":list(ARMS),
    }


def validate_dev(grid):
    if grid != dev_grid() or grid["phase"] != "DEV_ONLY":
        raise ValueError("F1K dev test must use the fixed separate DEV_ONLY fixtures")
    if any(r["id"].startswith("K") or
           202611219101 <= r["seed"] <= 202611219116
           for r in grid["origins"]):
        raise ValueError("holdout root accidentally entered DEV_ONLY")
    return grid


def new_world(grid, origin):
    if origin not in grid["origins"]:
        raise ValueError("source not allocated")
    family = next(f for f in grid["ecologies"] if f["id"] == origin["ecology"])
    spec = grid["world"]
    return World(WorldSpec(
        name="F1K_ORIGIN_"+origin["id"]+"_"+origin["ecology"],
        width=spec["width"],height=spec["height"],spawn=tuple(spec["spawn"]),
        body=tuple(origin["body"]),
        water={tuple(family["water"]):WaterSource(
            gain=family["water_gain"],stock=family["water_stock"],
            max_stock=family["water_max_stock"],
            restock_every=family["water_restock_every"])},
        food={tuple(family["food"]):FoodPatch(
            token=family["token"],quantity=family["food_quantity"],
            max_quantity=family["food_max_quantity"],
            restock_every=family["food_restock_every"])},
        token_effects={family["token"]:(
            family["food_gain"],family["integrity_delta"])},
        changes=(),laws=BodyLaws()
    ))


def paid_step(world, mind):
    """One voluntarily decided native action followed by genuinely prepaid learning."""
    if world.dead:
        raise RuntimeError("death is irreversible, no postmortem decision")
    before_world = D._snapshot_world(world)
    before_mind = C.seal_mind(mind)
    capture = world.capture()
    budget = CognitiveBudget(world.body,world.laws)
    action,param,work,info = mind.decide(capture,budget)
    after_choice = C.seal_mind(mind)
    if work != budget.work or world.t != before_world["t"]:
        raise AssertionError("cognitive work or motor was not native")
    promised = dict(zip(("energy","vigilance"),cognitive_cost(world.laws,work)))
    raw = world.step(action,param,work)
    C.paid_bill(world.laws,work,raw["cognitive_accounting"])
    motor = {
        "t":raw["t"],"body":list(raw["body"]),
        "dead":list(raw["dead"]),"moved":raw["moved"],
        "cognitive_accounting":deepcopy(raw["cognitive_accounting"]),
    }
    after_motor = D._snapshot_world(world)
    post = H._pay_new_learning(world,mind,raw)
    receipt = {
        "t":world.t,"before_world":before_world,"before_mind":before_mind,
        "capture":json.loads(C.canonical(capture)),
        "capture_sha256":C.digest(capture),
        "readout_mode":"full","temporary_prior_mean_keys":[],
        "exposed_mind_during_decision":before_mind,
        "after_decision_exposed_mind":after_choice,
        "after_restoration_before_motor":after_choice,
        "action":action,"param":param,
        "decision_info":json.loads(C.canonical(info)),
        "cognitive_work":asdict(work),
        "decision_remaining":list(budget.remaining),
        "requested_native_cost":promised,
        "native_motor":motor,"after_motor_world":after_motor,
        "postaction":post,
        "after_paid_learning_world":D._snapshot_world(world),
        "after_paid_learning_mind":C.seal_mind(mind),
        "no_experimental_action_override":True,
    }
    receipt["receipt_sha256"] = C.digest(receipt)
    return receipt


def source(grid, root):
    world = new_world(grid,root)
    mind = Mind(midpoint(),root["seed"],observer_full_competition=True)
    if (mind.effects.stats or mind.buffer
            or any(any(val != 0 for val in vec) for vec in mind.values)
            or world.t != 0 or world.dead):
        raise AssertionError("birth must begin without acquired memory")
    genesis = {"world":D._snapshot_world(world),"mind":C.seal_mind(mind)}
    steps, error = [], None
    for tick in range(1,T_SOURCE+1):
        if world.dead:
            break
        try:
            steps.append(paid_step(world,mind))
        except (ValueError,KeyError,RuntimeError,AssertionError) as exc:
            error = {"attempted_tick":tick,"type":type(exc).__name__,
                     "message":str(exc)}
            break
    valid = (len(steps)==T_SOURCE and world.t==T_SOURCE
             and not world.dead and error is None
             and bool(mind.effects.stats)
             and all(s["postaction"]["status"]=="PAID_LEARNED" for s in steps))
    receipt = {
        "origin":root,"genesis":genesis,"source_steps":steps,
        "source_tick4_world":D._snapshot_world(world),
        "source_tick4_mind":C.seal_mind(mind),
        "valid_paid_personal_source":valid,
        "source_error":error,
        "run_life_used":False,
    }
    receipt["source_receipt_sha256"] = C.digest(receipt)
    return world,mind,receipt


def fork_owned_mind(mind,policy):
    clone = deepcopy(mind)
    if policy=="fixed_round_f1j":
        # No constructor, genome or RNG reset; change ONLY the _compete dispatch.
        if type(clone) is not Mind:
            raise AssertionError("P1.3 personal source was replaced")
        clone.__class__ = F1JFixedRoundMind
        before,after = C.seal_mind(mind),C.seal_mind(clone)
        if before["data"]["private"] != after["data"]["private"]:
            raise AssertionError("policy switch secretly changed acquired memory")
    elif policy not in ("reference_p13","reference_sham"):
        raise ValueError("unregistered policy arm")
    return clone


def followup(world,mind,policy,horizon):
    steps,error = [],None
    while not world.dead and world.t < horizon:
        try:
            steps.append(paid_step(world,mind))
        except (ValueError,KeyError,RuntimeError,AssertionError) as exc:
            error={"attempted_tick":world.t+1,"type":type(exc).__name__,
                   "message":str(exc)}
            break
    decision = {"energy":0.,"vigilance":0.}
    learning = {"energy":0.,"vigilance":0.}
    area = [0.]*5
    for s in steps:
        for coin in decision:
            decision[coin]+=s["native_motor"]["cognitive_accounting"][coin]["paid"]
            if s["postaction"]["actual_paid_learning_bill"] is not None:
                learning[coin]+=s["postaction"]["actual_paid_learning_bill"][coin]["paid"]
        for i,b in enumerate(s["postaction"]["body_after_any_learning"]):
            area[i]+=b
    metrics = {
        "lived_ticks_t5_t60":len(steps),
        "alive_at_horizon":bool(world.t==horizon and not world.dead and error is None),
        "terminal_tick":world.t,"terminal_dead":list(world.dead),
        "terminal_body":list(world.body),
        "terminal_position":list(world.pos),
        "terminal_water_stock":sorted([[list(k),v.stock] for k,v in world.water.items()]),
        "terminal_food_quantity":sorted([[list(k),v.quantity] for k,v in world.food.items()]),
        "terminal_inventory":sorted([[k,v] for k,v in world.inventory.items()]),
        "cumulated_body":area,
        "paid_decision":decision,"paid_learning":learning,
        "water_drinks":sum(s["action"]=="boire" for s in steps),
        "foods_collected":sum(s["action"]=="collecter" for s in steps),
        "foods_actually_eaten":sum(s["action"]=="manger" for s in steps),
        "native_error":error,
    }
    result={"policy":policy,"steps":steps,
            "last_world":D._snapshot_world(world),
            "last_mind":C.seal_mind(mind),"metrics":metrics}
    result["trajectory_sha256"]=C.digest(result)
    return result


def compare(root, arms, source_valid):
    if not source_valid:
        return {"source_valid":False,"sham_neutral":False,
                "real_t5_surcharge":False,"delta_lived_ticks":None,
                "pareto":None,"motor_changed":None,"arm_valid":False}
    ref,sham,fixed=(arms[k] for k in ARMS)
    neutral=all(ref[key]==sham[key] for key in ("steps","last_world","last_mind","metrics"))
    valid=(neutral and all(a["metrics"]["native_error"] is None for a in arms.values())
           and all(bool(a["steps"]) for a in arms.values()))
    first,other=ref["steps"][0],fixed["steps"][0]
    a,b=first["cognitive_work"],other["cognitive_work"]
    ac,bc=first["requested_native_cost"],other["requested_native_cost"]
    surcharge=(b["cycles"]>a["cycles"] and
               ac["energy"] < bc["energy"]-1e-10 and
               ac["vigilance"] < bc["vigilance"]-1e-10)
    delta=fixed["metrics"]["lived_ticks_t5_t60"]-ref["metrics"]["lived_ticks_t5_t60"]
    pareto="NOT_EQUAL_SURVIVAL"
    if delta==0 and ref["metrics"]["alive_at_horizon"] and fixed["metrics"]["alive_at_horizon"]:
        x,y=fixed["metrics"]["terminal_body"],ref["metrics"]["terminal_body"]
        if all(u>=v-1e-9 for u,v in zip(x,y)) and any(u>v+1e-9 for u,v in zip(x,y)):
            pareto="FIXED_FIVE_CHANNEL_DOMINANCE"
        elif all(v>=u-1e-9 for u,v in zip(x,y)) and any(v>u+1e-9 for u,v in zip(x,y)):
            pareto="REFERENCE_FIVE_CHANNEL_DOMINANCE"
        elif all(abs(u-v)<=1e-9 for u,v in zip(x,y)):
            pareto="FIVE_CHANNELS_EQUAL"
        else:
            pareto="MIXED_BODILY_TRADEOFF"
    return {
        "source_valid":True,"sham_neutral":neutral,
        "real_t5_surcharge":surcharge,
        "delta_lived_ticks":delta if valid else None,"pareto":pareto if valid else None,
        "motor_changed":bool((first["action"],first["param"])!=
                             (other["action"],other["param"])) if valid else None,
        "arm_valid":valid,
    }


def classify(grid,rows,phase):
    if any(not row["comparison"]["source_valid"] for row in rows):
        return "INCONCLUSIVE_UNFUNDED_SOURCE"
    if any(any(a["metrics"]["native_error"] is not None for a in row["arms"].values())
           for row in rows):
        return "INCONCLUSIVE_UNFUNDED_SOURCE"
    if any(not row["comparison"]["sham_neutral"] for row in rows):
        return "INVALID_REFERENCE_SHAM"
    ecologies={r["origin"]["ecology"] for r in rows
               if r["comparison"]["real_t5_surcharge"]}
    exposed=sum(r["comparison"]["real_t5_surcharge"] for r in rows)
    if exposed<grid.get("success_criteria",{}).get("cost_exposure_min_roots",4) or len(ecologies)<2:
        return "INCONCLUSIVE_NO_REAL_SURCHARGE"
    diffs=[r["comparison"]["delta_lived_ticks"] for r in rows]
    wins=[r for r in rows if r["comparison"]["delta_lived_ticks"]>0]
    losses=[r for r in rows if r["comparison"]["delta_lived_ticks"]<0]
    if len(wins)>=3 and len({r["origin"]["ecology"] for r in wins})>=2 and not losses:
        return "LOCAL_T60_SURVIVAL_GAIN_WITH_REAL_COGNITIVE_SURCHARGE"
    if all(x==0 for x in diffs):
        d=[r for r in rows if r["comparison"]["pareto"]=="FIXED_FIVE_CHANNEL_DOMINANCE"]
        adverse=[r for r in rows if r["comparison"]["pareto"]=="REFERENCE_FIVE_CHANNEL_DOMINANCE"]
        if len(d)>=4 and len({r["origin"]["ecology"] for r in d})>=2 and not adverse:
            return "LOCAL_T60_BODILY_PARETO_GAIN_NO_SURVIVAL_GAIN"
    return "NO_REPRODUCIBLE_NET_BODY_ADVANTAGE_T60"


def produce(grid,phase="DEV_ONLY"):
    if phase=="DEV_ONLY":
        validate_dev(grid)
    elif phase=="F1K_HELDOUT_RELEASE":
        if grid!=release_grid():
            raise ValueError("science grid not byte-identical to frozen sources")
        if os.environ.get(RELEASE_ENV)!=PREEXPOSURE_MAIN:
            raise PermissionError("F1K holdout release needs distinct one-shot authority")
    else:
        raise ValueError("unknown prospective population phase")
    rows=[]
    for root in grid["origins"]:
        world,mind,personal=source(grid,root)
        arms={}
        if personal["valid_paid_personal_source"]:
            arms={p:followup(deepcopy(world),fork_owned_mind(mind,p),
                             p,grid["final_tick"]) for p in ARMS}
        comparison=compare(root,arms,personal["valid_paid_personal_source"])
        row={"origin":root,"source":personal,"arms":arms,"comparison":comparison}
        row["case_sha256"]=C.digest(row)
        rows.append(row)
    producer_estimate=classify(grid,rows,phase)
    result={
        "schema":SCHEMA,"phase":phase,
        "frozen_preexposure_main":PREEXPOSURE_MAIN if phase!="DEV_ONLY" else None,
        "grid_blob_sha":GRID_BLOB if phase!="DEV_ONLY" else None,
        "protocol_blob_sha":PROTOCOL_BLOB if phase!="DEV_ONLY" else None,
        "origin_count":len(grid["origins"]),
        "origin_ids":[r["id"] for r in grid["origins"]],
        "worlds":[e["id"] for e in grid["ecologies"]],
        "source_policy":"Mind_P1.3","compared_policies":list(ARMS),
        "source_ticks":T_SOURCE,"fork_tick":T_FORK,
        "final_tick":grid["final_tick"],
        "no_motor_override":True,"no_run_life":True,
        "F1I_frozen":"INCONCLUSIVE_COST_GATE",
        "F1J_frozen":"FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL",
        "scientific_verdict":None,
        "producer_provisional_classification":(
            producer_estimate if phase!="DEV_ONLY" else "DEV_ONLY_NOT_SCIENTIFIC"),
        "rows":rows,
    }
    result["provenance_sha256"]=C.digest({
        "phase":phase,"grid_blob":result["grid_blob_sha"],
        "protocol_blob":result["protocol_blob_sha"],
        "case_receipts":[r["case_sha256"] for r in rows],
    })
    return result


def main():
    ap=argparse.ArgumentParser(description="F1K native comparator; dev-only by default")
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dev",action="store_true",help="two disjoint DEV_ONLY fixtures")
    mode.add_argument("--release",action="store_true",help="requires source seal and one-shot gate")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    phase="F1K_HELDOUT_RELEASE" if args.release else "DEV_ONLY"
    grid=release_grid() if args.release else dev_grid()
    report=produce(grid,phase)
    with Path(args.output).open("xb") as stream:
        stream.write(C.canonical(report))
    print(json.dumps({
        "phase":phase,"roots":report["origin_count"],
        "producer_only":report["producer_provisional_classification"],
        "sha256":C.digest(report),"scientific_verdict":None,
    },sort_keys=True))


if __name__=="__main__":
    main()
