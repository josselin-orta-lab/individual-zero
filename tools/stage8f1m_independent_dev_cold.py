"""Independent F1M DEV_M cold audit, Python 3.12 stdlib, no i3 native engine.

Reconstruct T1..T60 physics, real paid decisions and learning, T5 own-history
readout and T6 accumulator-only fork. The pilot has NO scientific verdict.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import gzip
import json
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1k_independent_policy_value_cold_audit as K
from tools import stage8f1l_independent_paid_content_cold_audit as L

SCHEMA="i3-stage8f1m-development-causal-residual-actual-body/v0"
COIN=("energy","vigilance")
CONTENT=("recent","stale")
RESIDUAL=("carry","zero")
L_EXPOSED_SEEDS=set(range(202611229501,202611229533))
L_DEV_SEEDS=set(range(202611229601,202611229609))
M_DEV_SEEDS=list(range(202611239601,202611239609))


def check(ok, reason):
    if not ok:
        raise AssertionError("F1M COLD DEV: "+reason)


def cold_grid(full):
    """Independent exact DEV_M WorldSpec, separate from producer import."""
    ec=[
        {"id":"DEV_M_southwest_springs","water":[0,2],
         "water_gain":18,"water_stock":3,"water_max_stock":3,
         "water_restock_every":5,"food":[2,0],"token":"dev-m-green",
         "food_gain":20,"integrity_delta":0.8,"food_quantity":3,
         "food_max_quantity":3,"food_restock_every":4},
        {"id":"DEV_M_southeast_bitter","water":[2,2],
         "water_gain":23,"water_stock":2,"water_max_stock":2,
         "water_restock_every":6,"food":[0,0],"token":"dev-m-bitter",
         "food_gain":26,"integrity_delta":-0.8,"food_quantity":2,
         "food_max_quantity":2,"food_restock_every":5},
    ]
    origins=[]
    for i,seed in enumerate(M_DEV_SEEDS):
        j=i%4
        origins.append({"id":f"DEV_M{i+1:02d}","seed":seed,
                        "ecology":ec[i//4]["id"],
                        "body":[65+j,71-j,38+0.4*j,91-0.3*j,93-0.2*j]})
    if not full:
        origins=[origins[0],origins[4]]
    return {"schema":"i3-stage8f1m-unreleased-dev-grid/v0",
            "phase":"DEV_ONLY_NEVER_SCIENTIFIC",
            "final_tick":60,"ecologies":ec,"origins":origins,
            "arms":["recent/carry","recent/zero","stale/carry","stale/zero"],
            "source_ticks":4,"content_tick":5,"residual_fork_tick":6}


def _start_world(grid,root):
    world=K.origin_world(grid,root)
    world["world_spec"]["name"]="F1M_DEV_ORIGIN_"+root["id"]+"_"+root["ecology"]
    return world


def _reset_acc_only(sealed,mode):
    check(mode in RESIDUAL,"unregistered mediator")
    result=deepcopy(sealed)
    prv=result["data"]["private"]["__dict__"]
    matches=[v for v in prv if v[0]=="acc"]
    check(len(matches)==1,"missing/private acc mediator")
    raw=matches[0][1]
    check(set(raw)=={"__dict__"},"typed acc dictionary missing")
    pairs=raw["__dict__"]
    before=dict(pairs)
    check(len(pairs)==len(before),"duplicate residual keys")
    if mode=="zero":
        for pair in pairs:
            pair[1]=0.0
    result["sha256"]=I.h(result["data"])
    check(set(dict(pairs))==set(before),"intervention changed accumulator keys")
    return result,before,dict(pairs)


def _cold_fork(base,fork,mode):
    expected,before,after=_reset_acc_only(base,mode)
    check(fork["mode"]==mode and fork["before_mind"]==base and
          fork["after_mind"]==expected and
          fork["values_before"]==before and
          fork["values_after"]==after and
          fork["keys"]==sorted(before) and
          fork["no_action_override"] is True,"modified mediator fork")
    return expected


def _t5_equal(a,b):
    return (all(a[k]==b[k] for k in (
        "before_world","before_mind","capture",
        "cognitive_work","requested_native_cost","decision_remaining"))
        and a["native_motor"]["cognitive_accounting"]==
            b["native_motor"]["cognitive_accounting"])


def _t6_equal(a,b):
    return (all(a[k]==b[k] for k in (
        "before_world","capture","cognitive_work",
        "requested_native_cost","decision_remaining"))
        and a["native_motor"]["cognitive_accounting"]==
            b["native_motor"]["cognitive_accounting"])


def _body(a,b):
    x,y=a["metrics"],b["metrics"]
    lived=x["lived_ticks_t5_t60"]-y["lived_ticks_t5_t60"]
    delta=[v-w for v,w in zip(x["terminal_body"],y["terminal_body"])]
    pareto="NOT_COMPARABLE_HORIZON"
    if lived==0 and x["alive_at_horizon"] and y["alive_at_horizon"]:
        if all(d>=-1e-9 for d in delta) and any(d>1e-9 for d in delta):
            pareto="CARRY_FIVE_CHANNEL_DOMINANCE"
        elif all(d<=1e-9 for d in delta) and any(d < -1e-9 for d in delta):
            pareto="ZERO_FIVE_CHANNEL_DOMINANCE"
        elif all(abs(d)<=1e-9 for d in delta):
            pareto="FIVE_CHANNELS_EQUAL"
        else:
            pareto="MIXED_BODY_TRADEOFF"
    return {"delta_lived_ticks_t6_t60":lived,
            "terminal_body_delta":delta,
            "pareto":pareto,
            "carry_terminal_body":x["terminal_body"],
            "zero_terminal_body":y["terminal_body"],
            "carry_paid_decision":x["paid_decision"],
            "zero_paid_decision":y["paid_decision"],
            "carry_paid_learning":x["paid_learning"],
            "zero_paid_learning":y["paid_learning"],
            "carry_drinks":x["water_drinks"],"zero_drinks":y["water_drinks"],
            "carry_meals":x["foods_actually_eaten"],
            "zero_meals":y["foods_actually_eaten"]}


def _strip_sham(step):
    return {k:v for k,v in step.items()
            if k not in ("readout_mode","receipt_sha256")}


def _followup(rec,world,mind,arm):
    check(rec["policy"]=="DEV_M_"+arm,"unregistered arm")
    rounds=steps=0
    current,individual=deepcopy(world),deepcopy(mind)
    for tick,step in enumerate(rec["steps"],6):
        check(step["t"]==tick and tick<=60,"replayed, omitted or extra tick")
        current,individual,used=L.verify_step(
            step,current,individual,arm="full",horizon=60)
        steps+=1
        rounds+=used
    check(rec["last_mind"]==individual,"wrong T60 personal memory")
    K.world_eq(rec["last_world"],current,"F1M terminal world")
    check(rec["metrics"]==K.metrics(rec["steps"],current,
         rec["metrics"]["native_error"],60),"invented terminal body/learning")
    check(current["dead"] or current["t"]==60 or
          rec["metrics"]["native_error"] is not None,
          "truncated DEV_M continuation")
    return rec,steps,rounds


def _classification(data):
    if any(not d["source_valid"] or not d["all_continuations"] for d in data):
        return "DEV_INCONCLUSIVE_UNFUNDED_OR_INCOMPLETE_SOURCE"
    if any(not d["neutral_sham"] for d in data):
        return "DEV_INVALID_NONNEUTRAL_SHAM"
    if any(not d["t5_equal"] or not all(d[c]["t6_equal"] for c in CONTENT)
           for d in data):
        return "DEV_INCONCLUSIVE_REAL_DECISION_COST_GATE"
    motor=sum(d[c]["motor_changed"] for d in data for c in CONTENT)
    return ("DEV_ONLY_MOTOR_EFFECT_OBSERVED_NOT_SCIENCE" if motor else
            "DEV_ONLY_NO_MOTOR_EFFECT_NOT_SCIENCE")


def audit(report):
    L.source_gate()
    full=report.get("origin_count")==8
    grid=cold_grid(full)
    check(report.get("schema")==SCHEMA and
          report.get("phase")=="DEV_ONLY_NEVER_SCIENTIFIC" and
          report.get("scientific_verdict") is None and
          report.get("source_policy")=="F1JFixedRoundMind" and
          report.get("grid")==grid and
          report.get("original_protected_F1L_main")==
            "9c40f01684f5e69c893d765aa41cad1af1d33532" and
          report.get("arm_count_per_origin")==4 and
          report.get("no_imposed_motors") is True and
          report.get("no_retroactive_equalization") is True and
          report.get("f1l_scientific_roots_exposed")==0 and
          len(report.get("rows",[]))==len(grid["origins"]) and
          set(o["seed"] for o in grid["origins"]).isdisjoint(
             L_EXPOSED_SEEDS|L_DEV_SEEDS),"not exact independent DEV source")
    out=[]
    verified_steps=verified_rounds=0
    for origin,row in zip(grid["origins"],report["rows"]):
        check(row["origin"]==origin,"changed source/origin ID")
        src=row["source"]
        world=_start_world(grid,origin)
        K.world_eq(src["genesis"]["world"],world,"original DEV_M genesis")
        mind=src["genesis"]["mind"]
        p=K.private(mind,"F1JFixedRoundMind")
        check(K.effects(mind)=={} and
              p["buffer"]=={"__deque__":[],"maxlen":None} and
              all(all(z==0 for z in v) for v in p["values"]),
              "synthetic innate memories or TD")
        t1=None
        check(len(src["source_steps"])<=4,"source more than four ticks")
        for tick,step in enumerate(src["source_steps"],1):
            check(step["t"]==tick,"non-contiguous real acquisition")
            world,mind,used=L.verify_step(step,world,mind,arm="full",horizon=4)
            verified_steps+=1;verified_rounds+=used
            if tick==1:
                t1=K.effects(step["after_paid_learning_mind"])
        check(src["tick4_mind"]==mind,"acquired memory changed")
        K.world_eq(src["tick4_world"],world,"paid source body/stocks")
        own=[{"key":list(k),"stat":deepcopy(v)}
             for k,v in sorted(t1.items(),key=lambda x:repr(x[0]))] if t1 else []
        check(src["paid_t1_mean_anchor"]==own,"wrong owned T1 means")
        valid=(len(src["source_steps"])==4 and world["t"]==4 and
               not world["dead"] and t1 is not None and bool(t1) and
               src["source_error"] is None and
               all(s["postaction"]["status"]=="PAID_LEARNED"
                   for s in src["source_steps"]))
        check(src["source_valid"] is bool(valid) and
              src["source_receipt_sha256"]==I.h({
                 k:v for k,v in src.items() if k!="source_receipt_sha256"}),
              "source validity or provenance altered")
        detail={"root":origin["id"],"ecology":origin["ecology"],
                "source_valid":valid,"all_continuations":False,
                "neutral_sham":False,"t5_equal":False}
        if not valid:
            check(row["arms"]=={} and row["content_t5"]=={} and
                  row["comparison"]=={},"fabricated arms from unfunded source")
            out.append(detail);continue

        native_t5={}
        for c in CONTENT:
            step=row["content_t5"][c]
            m=deepcopy(mind);w=deepcopy(world)
            mode="full" if c=="recent" else "stale_owned_t1_means"
            w,m,used=L.verify_step(step,w,m,arm=mode,t1=t1,horizon=5)
            verified_steps+=1;verified_rounds+=used
            native_t5[c]=(w,m)
        sw,sm=deepcopy(world),deepcopy(mind)
        sham=row["shams"]["t5_recent_full_sham"]
        sw,sm,used=L.verify_step(sham,sw,sm,arm="full_sham",horizon=5)
        verified_steps+=1;verified_rounds+=used
        neutral=(sw==native_t5["recent"][0]
                 and sm==native_t5["recent"][1] and
                 _strip_sham(sham)==_strip_sham(row["content_t5"]["recent"]))
        check(neutral==row["comparison"]["t5_full_sham_neutral"],
              "original T5 sham proof modified")
        t5_equal=_t5_equal(row["content_t5"]["recent"],
                           row["content_t5"]["stale"])
        check(t5_equal==row["comparison"]["equal_t5_real_decision_cost"],
              "T5 fake real parity")
        detail["t5_equal"]=t5_equal
        control_shams=[]
        all_cont=[]
        for content in CONTENT:
            pre_world,pre_mind=native_t5[content]
            for mode in RESIDUAL:
                key=content+"/"+mode
                original=row["arms"][key]
                after=_cold_fork(pre_mind,original["fork"],mode)
                actual,steps,rounds=_followup(original["followup"],
                                              pre_world,after,key)
                verified_steps+=steps;verified_rounds+=rounds
                control=row["sham_arms"][key]
                repeated,steps,rounds=_followup(control,pre_world,after,key)
                verified_steps+=steps;verified_rounds+=rounds
                neutral=(actual["steps"]==repeated["steps"]
                         and actual["metrics"]==repeated["metrics"]
                         and actual["last_world"]==repeated["last_world"]
                         and actual["last_mind"]==repeated["last_mind"])
                check(neutral==row["shams"][key+"_neutral"],
                      "R sham claim differs from original cold")
                control_shams.append(neutral)
                all_cont.append(actual["metrics"]["native_error"] is None
                                and len(actual["steps"])>0)
            a=row["arms"][content+"/carry"]["followup"]
            b=row["arms"][content+"/zero"]["followup"]
            comp=row["comparison"][content]
            if a["steps"] and b["steps"]:
                x,y=a["steps"][0],b["steps"][0]
                real_cost=_t6_equal(x,y)
                carry_winner=x["decision_info"]["observer"]["competition_witness"]["winner_before_control"]
                zero_winner=y["decision_info"]["observer"]["competition_witness"]["winner_before_control"]
                mchange=(x["action"],x["param"])!=(y["action"],y["param"])
                wchange=(carry_winner!=zero_winner)
                check(comp["equal_t6_real_decision_cost"]==real_cost and
                      comp["winner_changed"]==wchange and
                      comp["motor_changed"]==mchange and
                      comp["carry_t6_winner"]==carry_winner and
                      comp["zero_t6_winner"]==zero_winner and
                      comp["carry_t6_motor"]==[x["action"],x["param"]] and
                      comp["zero_t6_motor"]==[y["action"],y["param"]] and
                      comp["carry_t6_work"]==x["cognitive_work"] and
                      comp["zero_t6_work"]==y["cognitive_work"] and
                      comp["carry_t6_billing"]==x["requested_native_cost"] and
                      comp["zero_t6_billing"]==y["requested_native_cost"] and
                      comp["t6_body_delta_after_paid_learning"]==[
                        v-w for v,w in zip(x["postaction"]["body_after_any_learning"],
                                           y["postaction"]["body_after_any_learning"])] and
                      comp["t6_body_delta_after_motor"]==[
                        v-w for v,w in zip(x["native_motor"]["body"],y["native_motor"]["body"])]
                      and comp["body"]==_body(a,b),
                      "predeclared motor/real body contrast not native")
                detail[content]={"t6_equal":real_cost,
                                 "winner_changed":wchange,
                                 "motor_changed":mchange,
                                 "carry_t6_motor":[x["action"],x["param"]],
                                 "zero_t6_motor":[y["action"],y["param"]],
                                 "carry_t6_winner":carry_winner,
                                 "zero_t6_winner":zero_winner,
                                 "t6_real_work":x["cognitive_work"],
                                 "t6_body_delta":comp["t6_body_delta_after_paid_learning"],
                                 "body":_body(a,b)}
            else:
                check(comp=={"error":"MISSING_NATIVE_T6"},
                      "missing original hidden")
                detail[content]={"t6_equal":False,"motor_changed":False,
                                 "winner_changed":False,
                                 "body":None}
        detail["neutral_sham"]=(neutral and all(control_shams))
        # Note: "neutral" is updated in the R loop, so T5 is checked
        # separately above by its own equality and recorded claim.
        detail["neutral_sham"]=(row["comparison"]["t5_full_sham_neutral"]
                                and all(control_shams))
        detail["all_continuations"]=all(all_cont)
        check(row["case_sha256"]==I.h({
              k:v for k,v in row.items() if k!="case_sha256"}),
              "DEV original case changed")
        out.append(detail)

    if len(out)!=len(grid["origins"]):
        raise AssertionError("source dropped")
    state=_classification(out)
    summary={
       "valid_source":sum(v["source_valid"] for v in out),
       "t5_equal_paid":sum(v["t5_equal"] for v in out),
       "t6_equal_paid":sum(v.get(c,{}).get("t6_equal",False) for v in out for c in CONTENT),
       "t6_winner_changed":sum(v.get(c,{}).get("winner_changed",False) for v in out for c in CONTENT),
       "t6_motor_changed":sum(v.get(c,{}).get("motor_changed",False) for v in out for c in CONTENT),
       "sham_valid":sum(v["neutral_sham"] for v in out),
       "t60_body_non_equal":sum(any(abs(z)>1e-9 for z in v.get(c,{}).get("body",{}).get("terminal_body_delta",[]))
                                 for v in out for c in CONTENT),
       "survival_advantage_carry":sum(v.get(c,{}).get("body",{}).get("delta_lived_ticks_t6_t60",0)>0
                                        for v in out for c in CONTENT),
       "survival_advantage_zero":sum(v.get(c,{}).get("body",{}).get("delta_lived_ticks_t6_t60",0)<0
                                       for v in out for c in CONTENT),
    }
    check(report["development_status"]==state and
          report["summary"]==summary,"producer classification disagrees with cold")
    return {
      "schema":"i3-stage8f1m-independent-dev-causal-residual-cold/v0",
      "phase":"DEV_ONLY_NEVER_SCIENTIFIC",
      "experimental_origin_count":len(out),
      "real_native_steps_independently_reconstructed":verified_steps,
      "f1j_substantive_rounds_independently_reconstructed":verified_rounds,
      "original_sha256":I.h(report),
      "source_F1L_heldouts_created":0,
      "scientific_verdict":None,
      "development_status":state,
      "summary":summary,
      "per_root":out,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("original")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    with gzip.open(args.original,"rb") as f:
        original=json.loads(f.read())
    cold=audit(original)
    with open(args.output,"x",encoding="utf-8") as out:
        json.dump(cold,out,sort_keys=True,indent=2)
        out.write("\n")
    print(json.dumps({
      "stage":"DEV_M_ONLY_COLD",
      "status":cold["development_status"],
      "roots":cold["experimental_origin_count"],
      "native_steps":cold["real_native_steps_independently_reconstructed"],
      "rounds":cold["f1j_substantive_rounds_independently_reconstructed"],
      "summary":cold["summary"],
      "F1L_new_scientific_births":0},sort_keys=True))


if __name__=="__main__":
    main()
