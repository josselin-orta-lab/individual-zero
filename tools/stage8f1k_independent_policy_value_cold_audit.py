"""F1K cold, engine-free independent verification of P1.3 vs paid F1J.

Python stdlib only. No imports of World, Mind, BodyLaws, genome, the F1K
producer, or scientific outcome classifiers. F1C/J prior independent cold
helpers provide typed seals, native pricing and fixed-round reconstruction.
This module independently rederives policy baselines, physical effects,
source-to-fork continuity, reference early-stop rounds and prospective gates.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha1,sha256
import json
from math import isclose,sqrt,tanh
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1d_independent_next_decision_audit as D
from tools import stage8f1j_independent_fixed_round_cold_audit as J

SCHEMA="i3-stage8f1k-policy-real-cost-prospective/v0"
GRID_BLOB="bae149207c1fc41fb7fcc6fff11462e03dd17407"
PROTOCOL_BLOB="f551f751eab04e58c93f432662c3181721228b13"
PREEXPOSURE_MAIN="212d656f71ed5f4011c069575f9235b5b11d30fd"
ARMS=("reference_p13","reference_sham","fixed_round_f1j")
COINS=("energy","vigilance")
MOTOR={"se_deplacer":2.,"collecter":1.,"manger":.5,"boire":.5,"attendre":.35}
DELTA={"N":(0,-1),"E":(1,0),"S":(0,1),"W":(-1,0)}

SOURCE_BLOBS={
    "src/i3/modules/mind.py": "a77ee89dcb65ea0d841d3cd71a64e539dc9fc445",
    "src/i3/modules/body.py": "22f0920a7bbb8ea4197cb7e2020fa63d2e7aa49b",
    "src/i3/modules/world.py": "d9093953216d318c10b19c805d145dabb9c96abd",
    "src/i3/modules/genome.py": "003e923aa93b0b284a7f732fc91f3f02538dd85c",
    "tools/stage8f1j_fixed_round_paid_competition.py": "0030bc957ef53800d95adcb617a98cb4c856ee5d",
    "tools/stage8f1h_prospective_native_body_value.py": "02c5ece502729e3fa341f17cfa9cdc03e8c50bf4",
    "tools/stage8f1c_paid_postaction_learning.py": "c3d00fe078cac0ad9487ac39c2c8c7e081f32313",
    "tools/stage8f1d_next_decision_retention.py": "19f10a02b73759b52856e177ac3731f5826281c6",
}


def check(ok,msg):
    I.check(ok,"F1K COLD: "+msg)


def close(a,b):
    return I.near(a,b)


def blob_sha(raw):
    return sha1(b"blob "+str(len(raw)).encode("ascii")+bytes([0])+raw).hexdigest()


def source_guard(grid,phase,grid_bytes=None,protocol_bytes=None):
    # Hash files as plain bytes; importing the actual engine is forbidden here.
    for path,expected in SOURCE_BLOBS.items():
        check(blob_sha(Path(path).read_bytes())==expected,
              "original P1.3/F1J physiology or receipt source drift "+path)
    check(grid.get("world")=={
        "width":3,"height":3,"spawn":[1,1],
        "laws":"BodyLaws() i3-body-laws-v2","changes":[]},
        "WorldSpec geometry/laws changed")
    check(grid.get("personal_history_ticks")==4
          and grid.get("fork_tick")==5 and grid.get("arms")==list(ARMS),
          "fork/source design drift")
    roots=grid.get("origins",[])
    worlds=grid.get("ecologies",[])
    check(type(roots) is list and type(worlds) is list
          and len({r.get("seed") for r in roots})==len(roots)
          and len({r.get("id") for r in roots})==len(roots)
          and len({f.get("id") for f in worlds})==len(worlds),
          "duplicated or nonunique roots/worlds")
    if phase=="F1K_HELDOUT_RELEASE":
        check(grid_bytes is not None and protocol_bytes is not None
              and blob_sha(grid_bytes)==GRID_BLOB
              and blob_sha(protocol_bytes)==PROTOCOL_BLOB
              and json.loads(grid_bytes)==grid,
              "preexposure byte pin mismatch")
        check(grid.get("schema")=="i3-stage8f1k-preexposure-heldout-net-policy-value/v0"
              and grid.get("baseline_main")=="d727b4cbb1dc0c9490608788836d3c5c040cbae5"
              and grid.get("source_controller")=="P1.3_Mind"
              and grid.get("final_tick")==60
              and [r["id"] for r in roots]==[
                  "K"+str(i).zfill(2) for i in range(1,17)]
              and [r["seed"] for r in roots]==list(range(202611219101,202611219117))
              and len(worlds)==4
              and all(sum(r["ecology"]==f["id"] for r in roots)==4 for f in worlds)
              and grid.get("frozen_prior_results",{}).get("F1I")=="INCONCLUSIVE_COST_GATE",
              "registered heldout protocol or origins were altered")
    else:
        check(phase=="DEV_ONLY" and grid.get("schema")=="i3-stage8f1k-dev-grid/v0"
              and grid.get("phase")=="DEV_ONLY"
              and grid.get("final_tick")==9
              and len(roots)==len(worlds)==2
              and [r["seed"] for r in roots]==[202611219201,202611219202]
              and all(r["id"].startswith("DEV") for r in roots)
              and all(f["id"].startswith("DEV_") for f in worlds),
              "reserved origin in software development")
    check(all(r["ecology"] in {f["id"] for f in worlds}
              and len(r["body"])==5
              and all(type(x) in (int,float) and 0<x<=100 for x in r["body"])
              for r in roots),"body or ecology of source invalid")
    return roots


def private(sealed,expected=None):
    check(type(sealed) is dict and set(sealed)=={"data","sha256"}
          and sealed["sha256"]==I.h(sealed["data"]),
          "whole Mind private seal invalid")
    data=sealed["data"]
    check(data.get("class") in ("Mind","F1JFixedRoundMind")
          and (expected is None or data["class"]==expected)
          and type(data.get("private")) is dict
          and set(data["private"])=={"__dict__"},
          "unexpected born individual's controller or private type")
    pairs=data["private"]["__dict__"]
    check(type(pairs) is list and
          all(type(x) is list and len(x)==2 and type(x[0]) is str for x in pairs),
          "invalid typed personal brain fields")
    fields=dict(pairs)
    check(len(fields)==len(pairs)
          and {"effects","values","buffer","rng","_budget_rng",
               "acc","intention","theta","p","w","gammas",
               "n_base","h_max","inertia"}<=set(fields),
          "incomplete personally acquired brain")
    return fields


def effects(sealed):
    em=private(sealed)["effects"]
    check(type(em) is dict and set(em)=={"__effects_model__"},
          "non-native acquired EffectsModel")
    stats=dict(em["__effects_model__"]["__dict__"])["stats"]["__dict__"]
    seen={}
    for key,values in stats:
        check(type(key) is dict and set(key)=={"__tuple__"}
              and type(values) is list and len(values)==3
              and len(values[1])==5,
              "invalid acquired episodic mean entry")
        tup=tuple(key["__tuple__"])
        check(tup not in seen,"duplicate learned effect")
        seen[tup]=values
    return seen


def typed_map(field):
    check(type(field) is dict and set(field)=={"__dict__"},
          "missing typed accumulator map")
    pairs=field["__dict__"]
    out=dict(pairs)
    check(len(out)==len(pairs),"duplicate native accumulator")
    return out


def origin_world(grid,root):
    fam=next(f for f in grid["ecologies"] if f["id"]==root["ecology"])
    return {
        "t":0,"body":root["body"],"position":[1,1],"inventory":[],"dead":[],
        "water_cells":[[fam["water"],fam["water_gain"],
                        fam["water_stock"],fam["water_max_stock"],
                        fam["water_restock_every"]]],
        "food_cells":[[fam["food"],fam["token"],fam["food_quantity"],
                       fam["food_max_quantity"],fam["food_restock_every"]]],
        "hidden_effects":[[fam["token"],[fam["food_gain"],fam["integrity_delta"]]]],
        "world_spec":{"name":"F1K_ORIGIN_"+root["id"]+"_"+root["ecology"],
                      "width":3,"height":3,"spawn":[1,1],"laws":D.LAWS},
    }


def world_eq(actual,expected,msg):
    check(type(actual) is dict and type(expected) is dict
          and set(actual)==set(expected),"non-native world state "+msg)
    for field in expected:
        if field=="body":
            I.body_equal(actual[field],expected[field],msg+" body")
        else:
            check(actual[field]==expected[field],
                  "world stock, birth, position, death or causality mismatch "+msg)


def perceive(s):
    w=s["water_cells"][0]
    f=s["food_cells"][0]
    x,y=s["position"]
    def cell(p):
        if not (0<=p[0]<3 and 0<=p[1]<3):
            return None
        return [p==w[0] and w[2]>0,
                [f[1]] if p==f[0] and f[2]>0 else []]
    return {"body":s["body"],"inventory":[x for x in s["inventory"] if x[1]>0],
            "here":cell([x,y]),
            "neighbors":[cell(p) for p in
                         ([x,y-1],[x+1,y],[x,y+1],[x-1,y])]}


def physical(before,action,param,work,bill):
    check(not before["dead"],"postmortem World.step or resurrection")
    cost=I.cost(work)
    I.check_bill(bill,cost,"F1K World.step actual payment")
    e,food,water,integrity,v=before["body"]
    check(e>=cost["energy"]-1e-10 and v>=cost["vigilance"]-1e-10,
          "unfunded cognition")
    e-=cost["energy"]
    v-=cost["vigilance"]
    check(action in (None,"dormir",*MOTOR),"invented bodily command")
    if action not in (None,"dormir"):
        check(e>=MOTOR[action]-1e-10,"unfunded motor")
    out=deepcopy(before)
    out["t"]+=1
    moved=False
    f_gain=i_delta=w_gain=0.
    if action in (None,"attendre","dormir","boire"):
        check(param is None,"illegal motor parameter")
    if action=="se_deplacer":
        check(param in DELTA,"invalid self-chosen direction")
        dx,dy=DELTA[param]
        new=[out["position"][0]+dx,out["position"][1]+dy]
        check(all(0<=q<3 for q in new),"forged movement outside WorldSpec")
        out["position"]=new
        moved=True
    elif action=="collecter":
        patch=out["food_cells"][0]
        check(patch[0]==out["position"] and patch[1]==param and patch[2]>0,
              "fictitious collected food")
        patch[2]-=1
        inv=dict(out["inventory"])
        inv[param]=inv.get(param,0)+1
        out["inventory"]=sorted([[k,n] for k,n in inv.items()])
    elif action=="manger":
        inv=dict(out["inventory"])
        check(type(param) is str and inv.get(param,0)>0
              and param==out["food_cells"][0][1],"false meal")
        inv[param]-=1
        out["inventory"]=sorted([[k,n] for k,n in inv.items()])
        f_gain,i_delta=out["hidden_effects"][0][1]
    elif action=="boire":
        src=out["water_cells"][0]
        check(out["position"]==src[0] and src[2]>0,"water consumed from empty source")
        src[2]-=1
        w_gain=src[1]
    food=I.clamp(food-.2)
    water=I.clamp(water-.4)
    hydrated=water>=.05
    if action=="dormir":
        gained=min(3.,max(0.,100.-e),food/.05) if hydrated else 0.
        e+=gained
        food-=gained*.05
        v+=4.
    elif action is not None:
        e-=MOTOR[action]
    if action in ("dormir","attendre") and hydrated:
        repair=min(.2,max(0.,100.-integrity),food/.1)
        integrity+=repair
        food-=repair*.1
    if action=="manger":
        food+=f_gain
        integrity+=i_delta
    elif action=="boire":
        water+=w_gain
    out["body"]=[I.clamp(x) for x in (e,food,water,integrity,v)]
    out["dead"]=[label for label,i in (("zero_food",1),("zero_water",2),
                                      ("zero_integrity",3))
                 if out["body"][i]<=0.]
    # Native restocking follows the completed action, even on fatal ticks.
    for index in (0,):
        row=out["water_cells"][index]
        if row[4] and out["t"]%row[4]==0 and row[2] is not None:
            row[2]=min(row[3],row[2]+1)
        row=out["food_cells"][index]
        if row[4] and out["t"]%row[4]==0:
            row[2]=min(row[3],row[2]+1)
    return out,{"t":out["t"],"body":out["body"],
                "dead":out["dead"],"moved":moved}


def paid_learning(step,after_motor):
    rec=step["postaction"]
    check(rec["mind_before_outcome_observation"]==
          step["after_restoration_before_motor"],
          "learning not linked to actual chosen Mind")
    I.body_equal(rec["world_after_motor_body"],after_motor["body"],
                 "body before paid learning")
    work=rec["learn_work"]
    bill=rec["actual_paid_learning_bill"]
    state=deepcopy(after_motor)
    if bill is None:
        check(work=={"cycles":0,"simulated_steps":0,"memory_items":0,"replays":0}
              and rec["prepaid_replays"] is None
              and rec["executed_replays"]==0
              and rec["status"] in ("DEAD_NO_LEARNING",
                                   "NO_LAST_ACTION_NO_LEARNING","UNFUNDED_LEARNING"),
              "unpaid learning continued")
        I.body_equal(rec["learning_grant_remaining"],state["body"],
                     "unfunded learning grant")
        if after_motor["dead"]:
            check(rec["status"]=="DEAD_NO_LEARNING","postmortem learned knowledge")
    else:
        c=I.cost(work)
        I.check_bill(bill,c,"F1K World.pay_cognition")
        check(not after_motor["dead"] and rec["status"]=="PAID_LEARNED"
              and work["cycles"]>=2 and type(rec["prepaid_replays"]) is int
              and rec["prepaid_replays"]==rec["executed_replays"]==work["replays"],
              "learning work was not truly preauthorized")
        state["body"][0]-=c["energy"]
        state["body"][4]-=c["vigilance"]
        check(state["body"][0]>=-1e-10 and state["body"][4]>=-1e-10,
              "learning charged nonexistent reserves")
        I.body_equal(rec["learning_grant_remaining"],state["body"],
                     "learning allowance under body")
    world_eq(rec["world_after_any_learning"],state,"real paid postaction")
    I.body_equal(rec["body_after_any_learning"],state["body"],
                 "five reserves after learning")
    check(rec["mind_after_any_learning"]==step["after_paid_learning_mind"]
          and rec["learning_receipt_sha256"]==I.h({
              k:v for k,v in rec.items() if k!="learning_receipt_sha256"}),
          "post-action memory or receipt seal invalid")
    private(rec["mind_after_any_learning"])
    return rec["world_after_any_learning"],rec["mind_after_any_learning"]


def early_stopping_competition(step):
    """Cold recomputation of real P1.3 threshold break, without importing Mind."""
    obs=step["decision_info"]
    if obs.get("funding")!="FUNDED":
        return 0
    witness=obs["observer"]["competition_witness"]
    scores=obs["observer"]["score_witness"]
    prior=private(step["before_mind"],"Mind")
    options=witness["scored_order"]
    check(len(options)==len(scores)>0
          and [s["option"] for s in scores]==options
          and len(options)==len(set(options)),"scored evidence was forged")
    values=[s["total_score"] for s in scores]
    avg=sum(values)/len(values)
    sd=sqrt(sum((v-avg)**2 for v in values)/len(values))
    evidence={key:tanh((score-avg)/sd) if sd>1e-9 else 0.
              for key,score in zip(options,values)}
    initial=typed_map(prior["acc"])
    acc={x:initial.get(x,0.) for x in options}
    check(witness["accumulators_before"]==acc
          and witness["prior_intention"]==prior["intention"]
          and set(witness["normalized_evidence"])==set(options)
          and all(close(witness["normalized_evidence"][x],evidence[x])
                  for x in options),"precompetition private effects modified")
    capacity=max(1,int(round(prior["n_base"]*
                 min(1.,step["before_world"]["body"][0]/50.))))
    thresholds={
        x:1.5*(1.-prior["inertia"] if x==prior["intention"] else 1.)
        for x in options}
    check(all(close(witness["thresholds"][x],thresholds[x]) for x in options)
          and set(witness["thresholds"])==set(options),
          "P1.3 changed thresholds")
    expected_used=0
    ties=[]
    chosen_by="raw_score_fallback"
    # The simulation and memory bill was already prepaid before competition.
    # Re-evaluate each authorized P1.3 cycle against the actual initial body.
    base=step["cognitive_work"].copy()
    base["cycles"]=3
    for _ in range(capacity):
        test=base.copy()
        test["cycles"]=3+expected_used+1
        c=I.cost(test)
        body=step["before_world"]["body"]
        if c["energy"]>body[0]+1e-10 or c["vigilance"]>body[4]+1e-10:
            break
        expected_used+=1
        crossed=[]
        for x in options:
            acc[x]=max(0.,.8*acc[x]+evidence[x])
            if acc[x]>=thresholds[x]:
                crossed.append(((acc[x]-thresholds[x])/thresholds[x],x))
        if crossed:
            m=max(p for p,_ in crossed)
            # Cross-Python libm tanh can change an exact floating tie by
            # ~1e-16. Accept only a near-optimal numeric tie (1e-11), not
            # a differently ranked winner or an invented extra cycle.
            ties=sorted(x for p,x in crossed if p>=m-1e-11)
            chosen_by="threshold_crossing"
            break
    if not ties:
        best=max(values)
        ties=sorted(x for x,v in zip(options,values) if v>=best-1e-12)
    winner=witness["winner_before_control"]
    check(expected_used==witness["paid_competition_cycles"]==obs["cycles"]
          and step["cognitive_work"]["cycles"]==3+expected_used
          and witness["selection_mechanism"]==chosen_by
          and type(witness["tie_candidates"]) is list
          and bool(witness["tie_candidates"])
          and witness["tie_candidates"]==sorted(set(witness["tie_candidates"]))
          and set(witness["tie_candidates"]).issubset(set(ties))
          and winner in witness["tie_candidates"],
          "incorrect P1.3 early threshold or fictitious charged cycle: "+
          str({"expected":expected_used,
               "receipt":witness["paid_competition_cycles"],
               "info":obs["cycles"],"capacity":capacity,
               "expected_winner":ties,
               "recorded_winner":witness["winner_before_control"],
               "selection":chosen_by,
               "recorded_selection":witness["selection_mechanism"],
               "recorded_ties":witness["tie_candidates"],
               "crossed_margins":{
                   x:(acc[x]-thresholds[x])/thresholds[x]
                   for x in options if acc[x]>=thresholds[x]
               }}))
    pre=witness["accumulators_before_residual"]
    final={x:0. if x==winner else acc[x]*.5 for x in options}
    check(set(pre)==set(acc)
          and all(close(pre[x],acc[x]) for x in acc)
          and all(close(witness["accumulators_after_residual"][x],final[x])
                  for x in options),
          "P1.3 actual updated evidence not preserved")
    actual=typed_map(private(step["after_paid_learning_mind"])["acc"])
    # Learning normally preserves acc; compare chosen Mind after decision too.
    decision=typed_map(private(step["after_restoration_before_motor"])["acc"])
    check(all(close(decision[x],final[x]) for x in options)
          and witness.get("final_admitted_option")==obs["option"],
          "P1.3 native _admit or residual result falsified")
    return expected_used


def check_step(step,world,mind,policy,horizon):
    check(step["before_mind"]==mind and step["t"]==world["t"]+1
          and step["t"]<=horizon and step["no_experimental_action_override"] is True,
          "noncontiguous chronology or experimenter motor")
    world_eq(step["before_world"],world,"pre-decision")
    check(step["capture"]==perceive(world)
          and step["capture_sha256"]==I.h(step["capture"]),
          "agent's first-person capture was forged")
    check(step["readout_mode"]=="full"
          and step["temporary_prior_mean_keys"]==[]
          and step["exposed_mind_during_decision"]==step["before_mind"]
          and step["after_restoration_before_motor"]==
              step["after_decision_exposed_mind"],
          "hidden postfork memory intervention")
    private(mind,policy)
    cost=I.cost(step["cognitive_work"])
    check(step["requested_native_cost"]==cost,"wrong two-currency cognitive work")
    I.check_bill(step["native_motor"]["cognitive_accounting"],
                 cost,"real decision motor")
    remaining=list(world["body"])
    remaining[0]-=cost["energy"]
    remaining[4]-=cost["vigilance"]
    I.body_equal(step["decision_remaining"],remaining,
                 "decision budget truly charged")
    if policy=="Mind":
        rounds=early_stopping_competition(step)
    else:
        rounds=J.cold_paid_fixed_competition(step)["audited_rounds"]
    after_native,summary=physical(
        world,step["action"],step["param"],step["cognitive_work"],
        step["native_motor"]["cognitive_accounting"])
    for f in ("t","dead","moved"):
        check(step["native_motor"][f]==summary[f],"fake native motor "+f)
    I.body_equal(step["native_motor"]["body"],summary["body"],
                 "motor/death/food native body")
    world_eq(step["after_motor_world"],after_native,"after World.step")
    after_world,after_mind=paid_learning(step,after_native)
    world_eq(step["after_paid_learning_world"],after_world,
             "after genuine learning")
    check(step["receipt_sha256"]==I.h({
        k:v for k,v in step.items() if k!="receipt_sha256"}),
        "forged per-decision receipt digest")
    return after_world,after_mind,rounds


def metrics(steps,world,error,horizon):
    decisions={"energy":0.,"vigilance":0.}
    learning={"energy":0.,"vigilance":0.}
    area=[0.]*5
    for s in steps:
        for coin in COINS:
            decisions[coin]+=s["native_motor"]["cognitive_accounting"][coin]["paid"]
            bill=s["postaction"]["actual_paid_learning_bill"]
            if bill is not None:
                learning[coin]+=bill[coin]["paid"]
        for i,v in enumerate(s["postaction"]["body_after_any_learning"]):
            area[i]+=v
    return {
        "lived_ticks_t5_t60":len(steps),
        "alive_at_horizon":bool(world["t"]==horizon and not world["dead"] and error is None),
        "terminal_tick":world["t"],"terminal_dead":world["dead"],
        "terminal_body":world["body"],"terminal_position":world["position"],
        "terminal_water_stock":[[x[0],x[2]] for x in world["water_cells"]],
        "terminal_food_quantity":[[x[0],x[2]] for x in world["food_cells"]],
        "terminal_inventory":world["inventory"],
        "cumulated_body":area,
        "paid_decision":decisions,"paid_learning":learning,
        "water_drinks":sum(s["action"]=="boire" for s in steps),
        "foods_collected":sum(s["action"]=="collecter" for s in steps),
        "foods_actually_eaten":sum(s["action"]=="manger" for s in steps),
        "native_error":error,
    }


def outcome(grid,rows):
    if any(not r["comparison"]["source_valid"] for r in rows):
        return "INCONCLUSIVE_UNFUNDED_SOURCE"
    if any(a["metrics"]["native_error"] is not None for r in rows
           for a in r["arms"].values()):
        return "INCONCLUSIVE_UNFUNDED_SOURCE"
    if any(not r["comparison"]["sham_neutral"] for r in rows):
        return "INVALID_REFERENCE_SHAM"
    exposed=[r for r in rows if r["comparison"]["real_t5_surcharge"]]
    if (len(exposed)<4 or
            len({r["origin"]["ecology"] for r in exposed})<2):
        return "INCONCLUSIVE_NO_REAL_SURCHARGE"
    wins=[r for r in rows if r["comparison"]["delta_lived_ticks"]>0]
    losses=[r for r in rows if r["comparison"]["delta_lived_ticks"]<0]
    if (len(wins)>=3
            and len({r["origin"]["ecology"] for r in wins})>=2
            and not losses):
        return "LOCAL_T60_SURVIVAL_GAIN_WITH_REAL_COGNITIVE_SURCHARGE"
    if all(r["comparison"]["delta_lived_ticks"]==0 for r in rows):
        dominated=[r for r in rows if r["comparison"]["pareto"]=="FIXED_FIVE_CHANNEL_DOMINANCE"]
        adverse=[r for r in rows if r["comparison"]["pareto"]=="REFERENCE_FIVE_CHANNEL_DOMINANCE"]
        if len(dominated)>=4 and len({r["origin"]["ecology"] for r in dominated})>=2 and not adverse:
            return "LOCAL_T60_BODILY_PARETO_GAIN_NO_SURVIVAL_GAIN"
    return "NO_REPRODUCIBLE_NET_BODY_ADVANTAGE_T60"


def audit(report,grid,*,grid_bytes=None,protocol_bytes=None):
    phase=report.get("phase")
    roots=source_guard(grid,phase,grid_bytes,protocol_bytes)
    check(report.get("schema")==SCHEMA
          and report.get("origin_count")==len(roots)
          and report.get("origin_ids")==[r["id"] for r in roots]
          and report.get("worlds")==[f["id"] for f in grid["ecologies"]]
          and report.get("source_policy")=="Mind_P1.3"
          and report.get("compared_policies")==list(ARMS)
          and report.get("source_ticks")==4 and report.get("fork_tick")==5
          and report.get("final_tick")==grid["final_tick"]
          and report.get("no_motor_override") is True
          and report.get("no_run_life") is True
          and report.get("F1I_frozen")=="INCONCLUSIVE_COST_GATE"
          and report.get("F1J_frozen")=="FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL"
          and report.get("scientific_verdict") is None
          and len(report.get("rows",[]))==len(roots),
          "producer reinterpreted frozen science or used different cohort")
    if phase=="F1K_HELDOUT_RELEASE":
        check(report["frozen_preexposure_main"]==PREEXPOSURE_MAIN
              and report["grid_blob_sha"]==GRID_BLOB
              and report["protocol_blob_sha"]==PROTOCOL_BLOB,
              "release forged F1K preregistration")
    else:
        check(report["frozen_preexposure_main"] is None
              and report["grid_blob_sha"] is None
              and report["protocol_blob_sha"] is None,
              "DEV_ONLY attempted to wear a scientific source seal")
    total_steps=total_rounds=drinks=meals=0
    rows_out=[]
    for root,row in zip(roots,report["rows"]):
        check(row["origin"]==root and row["source"]["origin"]==root,
              "seed was filtered or reordered after exposure")
        source=row["source"]
        world=origin_world(grid,root)
        world_eq(source["genesis"]["world"],world,"unaltered birth")
        born=source["genesis"]["mind"]
        b=private(born,"Mind")
        check(effects(born)=={} and b["buffer"]=={"__deque__":[],"maxlen":None}
              and all(all(val==0 for val in vec) for vec in b["values"]),
              "historical or synthetic personal learning was imported")
        mind=born
        for index,step in enumerate(source["source_steps"]):
            check(index<4 and step["t"]==index+1,"source tick absent or repeated")
            world,mind,paid=check_step(step,world,mind,"Mind",4)
            total_steps+=1
            total_rounds+=paid
        world_eq(source["source_tick4_world"],world,"paid acquisition completion")
        check(source["source_tick4_mind"]==mind,"personal history was not retained")
        source_valid=(
            len(source["source_steps"])==4 and world["t"]==4
            and not world["dead"] and source["source_error"] is None
            and bool(effects(mind))
            and all(s["postaction"]["status"]=="PAID_LEARNED"
                    for s in source["source_steps"]))
        check(source["valid_paid_personal_source"] is source_valid
              and source["run_life_used"] is False
              and source["source_receipt_sha256"]==I.h({
                  k:v for k,v in source.items() if k!="source_receipt_sha256"}),
              "invalid own prepaid source or falsified receipt")
        arms=row["arms"]
        if source_valid:
            check(set(arms)==set(ARMS),"missing preregistered policy branch")
            for arm_name in ARMS:
                arm=arms[arm_name]
                check(arm["policy"]==arm_name and arm["steps"],
                      "policy fork lacks a real native T5 decision")
                expected=deepcopy(mind)
                policy="F1JFixedRoundMind" if arm_name=="fixed_round_f1j" else "Mind"
                if arm_name=="fixed_round_f1j":
                    expected=deepcopy(mind)
                    expected["data"]["class"]=policy
                    expected["sha256"]=I.h(expected["data"])
                    check(private(expected)["effects"]==private(mind)["effects"]
                          and expected["data"]["private"]==mind["data"]["private"],
                          "fork fabricated personal memory, RNG or TD")
                current=deepcopy(world)
                for step in arm["steps"]:
                    current,expected,rounds=check_step(
                        step,current,expected,policy,grid["final_tick"])
                    total_steps+=1
                    total_rounds+=rounds
                    meals+=int(step["action"]=="manger")
                    drinks+=int(step["action"]=="boire")
                world_eq(arm["last_world"],current,"final native body")
                check(arm["last_mind"]==expected
                      and (current["t"]==grid["final_tick"]
                           or current["dead"]
                           or arm["metrics"]["native_error"] is not None),
                      "unregistered early end or fabricated mind state")
                check(metrics(arm["steps"],current,
                              arm["metrics"]["native_error"],grid["final_tick"])
                      ==arm["metrics"],"incorrect native adaptive metric")
                check(arm["trajectory_sha256"]==I.h({
                    k:v for k,v in arm.items() if k!="trajectory_sha256"}),
                    "native branch receipt hash forged")
            ref,sham,fixed=(arms[k] for k in ARMS)
            neutral=all(ref[k]==sham[k] for k in
                        ("steps","last_world","last_mind","metrics"))
            valid=(neutral and all(a["metrics"]["native_error"] is None
                                   for a in arms.values()))
            a,b=ref["steps"][0],fixed["steps"][0]
            check(a["before_world"]==b["before_world"]
                  and a["before_mind"]["data"]["private"]==
                      b["before_mind"]["data"]["private"],
                  "policy not forked from exact same paid state")
            costs=(I.cost(a["cognitive_work"]),I.cost(b["cognitive_work"]))
            surcharge=(b["cognitive_work"]["cycles"]>a["cognitive_work"]["cycles"]
                       and costs[1]["energy"]>costs[0]["energy"]+1e-10
                       and costs[1]["vigilance"]>costs[0]["vigilance"]+1e-10)
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
            motor=(a["action"],a["param"])!=(b["action"],b["param"])
            expected_comparison={
                "source_valid":True,"sham_neutral":neutral,
                "real_t5_surcharge":surcharge,
                "delta_lived_ticks":delta if valid else None,
                "pareto":pareto if valid else None,
                "motor_changed":motor if valid else None,
                "arm_valid":valid,
            }
        else:
            check(arms=={},"invalid personal source was cherry-picked")
            expected_comparison={
                "source_valid":False,"sham_neutral":False,
                "real_t5_surcharge":False,"delta_lived_ticks":None,
                "pareto":None,"motor_changed":None,"arm_valid":False,
            }
        check(row["comparison"]==expected_comparison
              and row["case_sha256"]==I.h({
                  k:v for k,v in row.items() if k!="case_sha256"}),
              "post-exposure selective reclassification or source rewrite")
        rows_out.append({"root":root["id"],"ecology":root["ecology"],
                         **expected_comparison})
    chain=I.h({
        "phase":phase,"grid_blob":report["grid_blob_sha"],
        "protocol_blob":report["protocol_blob_sha"],
        "case_receipts":[r["case_sha256"] for r in report["rows"]],
    })
    check(report["provenance_sha256"]==chain,"provenance chain mismatch")
    if phase=="F1K_HELDOUT_RELEASE":
        cold_verdict=outcome(grid,report["rows"])
        check(cold_verdict==report["producer_provisional_classification"],
              "producer promoted a result not supported by cold receipts")
    else:
        cold_verdict="DEV_ONLY_NOT_SCIENTIFIC"
        check(report["producer_provisional_classification"]==cold_verdict,
              "DEV_ONLY was mislabeled as scientific evidence")
    return {
        "schema":"i3-stage8f1k-stdlib-engine-free-policy-value-cold/v0",
        "phase":phase,"original_sha256":I.h(report),
        "cold_verdict":cold_verdict,
        "preexposure_blobs_verified":phase=="F1K_HELDOUT_RELEASE",
        "native_paid_steps_verified":total_steps,
        "competition_rounds_verified":total_rounds,
        "real_meals_verified":meals,
        "real_drinks_verified":drinks,
        "all_16_origins_retained":len(roots)==16 if phase!="DEV_ONLY" else False,
        "reference_controller_unchanged":True,
        "F1I_frozen":"INCONCLUSIVE_COST_GATE",
        "per_origin":rows_out,
        "provenance_sha256":chain,
    }


def main():
    ap=argparse.ArgumentParser(description="F1K independent stdlib-only cold audit")
    ap.add_argument("original")
    ap.add_argument("grid")
    ap.add_argument("cold_output")
    ap.add_argument("--protocol",help="required for heldout source pinned original")
    args=ap.parse_args()
    raw=Path(args.original).read_bytes()
    grid_bytes=Path(args.grid).read_bytes()
    data=json.loads(raw)
    grid=json.loads(grid_bytes)
    method=Path(args.protocol).read_bytes() if args.protocol else None
    out=audit(data,grid,grid_bytes=grid_bytes,protocol_bytes=method)
    check(out["original_sha256"]==sha256(raw).hexdigest(),
          "F1K original not canonical or hashes inconsistent")
    with Path(args.cold_output).open("xb") as stream:
        stream.write(I.c(out))
    print(json.dumps({"phase":out["phase"],"verdict":out["cold_verdict"],
                      "steps":out["native_paid_steps_verified"],
                      "rounds":out["competition_rounds_verified"],
                      "sha256":I.h(out)},sort_keys=True))


if __name__=="__main__":
    main()
