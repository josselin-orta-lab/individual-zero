"""Stage8-F1M DEV_ONLY: intervene on persistent residual accumulators, not actions.

This is a development pilot on NEVER-F1L DEV_M roots only.
- T1..T4: self-acquired, real paid memory.
- T5: native recent vs own T1 mean readout; no prescribed motor.
- AFTER real T5 action + real paid learning, clone each identical state.
- Prior to T6, carry accumulator values or zero *values only*, same keys.
- T6..T60: real autonomous motor, genuine costs, physical transitions.
No import of F1L scientific producer, no historical seed, no manual dispatch,
no heldout F1M scientific source and no scientific verdict.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import gzip
import json
from pathlib import Path

from i3.modules.body import BodyLaws
from i3.modules.genome import midpoint
from i3.modules.world import World, WorldSpec, WaterSource, FoodPatch
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D0
from tools import stage8f1l_paid_content_body_value_dev as L
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind

SCHEMA = "i3-stage8f1m-development-causal-residual-actual-body/v0"
DEV_ONLY_SEEDS = tuple(range(202611239601, 202611239609))
DEV_REPLICA2_SEEDS = tuple(range(202611239611, 202611239619))
RESERVED_L = frozenset(range(202611229501, 202611229533))
DEV_L = frozenset(range(202611229601, 202611229609))
END_TICK = 60
CONTENT = ("recent", "stale")
RESIDUAL = ("carry", "zero")
SHAM = ("original", "sham")


def dev_grid(full=False):
    """Development-only ecologies disjoint from F1L scientific and DEV_L worlds."""
    eco = [
        {"id": "DEV_M_southwest_springs", "water": [0, 2],
         "water_gain": 18, "water_stock": 3, "water_max_stock": 3,
         "water_restock_every": 5, "food": [2, 0],
         "token": "dev-m-green", "food_gain": 20,
         "integrity_delta": 0.8, "food_quantity": 3,
         "food_max_quantity": 3, "food_restock_every": 4},
        {"id": "DEV_M_southeast_bitter", "water": [2, 2],
         "water_gain": 23, "water_stock": 2, "water_max_stock": 2,
         "water_restock_every": 6, "food": [0, 0],
         "token": "dev-m-bitter", "food_gain": 26,
         "integrity_delta": -0.8, "food_quantity": 2,
         "food_max_quantity": 2, "food_restock_every": 5},
    ]
    origins = []
    for i, seed in enumerate(DEV_ONLY_SEEDS):
        j = i % 4
        origins.append({
            "id": "DEV_M%02d" % (i + 1),
            "seed": seed, "ecology": eco[i // 4]["id"],
            "body": [65+j, 71-j, 38+0.4*j, 91-0.3*j, 93-0.2*j],
        })
    if not full:
        origins = (origins[0], origins[4])
    return {"schema":"i3-stage8f1m-unreleased-dev-grid/v0",
            "phase":"DEV_ONLY_NEVER_SCIENTIFIC",
            "final_tick":END_TICK,
            "ecologies":eco,"origins":list(origins),
            "arms":["recent/carry", "recent/zero",
                    "stale/carry", "stale/zero"],
            "source_ticks":4,"content_tick":5,"residual_fork_tick":6}


def dev_replica2_grid(full=False):
    """Independent DEV_M second technical source set, no heldout M births."""
    result=deepcopy(dev_grid(full))
    result["schema"]="i3-stage8f1m-unreleased-dev-replica2-grid/v0"
    for origin in result["origins"]:
        index=int(origin["id"][5:])-1
        origin["id"]="DEV_MR%02d" % (index+1)
        origin["seed"]=DEV_REPLICA2_SEEDS[index]
    return result


def source_gate(grid):
    L.verify_readonly_prereg()   # validates frozen reference SHA without L World.step
    official = dev_grid(full=len(grid["origins"]) == 8)
    alternative=dev_replica2_grid(full=len(grid["origins"])==8)
    if grid!=official and grid!=alternative:
        raise PermissionError("DEV_M accepts only two disjoint fixed DEV source sets")
    seeds = [o["seed"] for o in grid["origins"]]
    if (not set(seeds).issubset(set(DEV_ONLY_SEEDS)|set(DEV_REPLICA2_SEEDS))
            or set(seeds) & (RESERVED_L | DEV_L | set(range(202611239701,202611239733)))
            or any(not x["id"].startswith("DEV_M") for x in grid["origins"])
            or any(e["water"] in ([1,1],[0,0],[0,1],[2,1]) for e in grid["ecologies"])
            or any(not e["id"].startswith("DEV_M") for e in grid["ecologies"])):
        raise PermissionError("scientific F1L or historical dev seed contamination")
    return True


def _new_dev_world(grid, origin):
    if (origin not in grid["origins"] or
            origin["seed"] not in (*DEV_ONLY_SEEDS,*DEV_REPLICA2_SEEDS) or
            not origin["id"].startswith("DEV_M")):
        raise PermissionError("F1M DEV only accepts DEV_M origins")
    ec = next(x for x in grid["ecologies"] if x["id"] == origin["ecology"])
    return World(WorldSpec(
        name="F1M_DEV_ORIGIN_"+origin["id"]+"_"+ec["id"],
        width=3,height=3,spawn=(1,1),body=tuple(origin["body"]),
        water={tuple(ec["water"]):WaterSource(gain=ec["water_gain"],
               stock=ec["water_stock"],max_stock=ec["water_max_stock"],
               restock_every=ec["water_restock_every"])},
        food={tuple(ec["food"]):FoodPatch(token=ec["token"],
              quantity=ec["food_quantity"],max_quantity=ec["food_max_quantity"],
              restock_every=ec["food_restock_every"])},
        token_effects={ec["token"]:(ec["food_gain"],ec["integrity_delta"])},
        changes=(),laws=BodyLaws()))


def _source(grid, origin):
    world = _new_dev_world(grid, origin)
    mind = F1JFixedRoundMind(midpoint(), origin["seed"])
    if (world.t != 0 or world.dead or mind.effects.stats or mind.buffer
            or any(any(x != 0 for x in row) for row in mind.values)):
        raise AssertionError("non-native or prelearned DEV_M birth")
    genesis={"world":D0._snapshot_world(world),"mind":C.seal_mind(mind)}
    steps, t1_stats, error = [], {}, None
    for tick in range(1,5):
        if world.dead:
            break
        try:
            steps.append(L.paid_step(world,mind))
            if tick==1:
                t1_stats=deepcopy(mind.effects.stats)
        except (ValueError,KeyError,RuntimeError,AssertionError) as e:
            error={"tick":tick,"type":type(e).__name__,"message":str(e)}
            break
    valid=(error is None and len(steps)==4 and world.t==4 and
           not world.dead and bool(t1_stats) and
           all(s["postaction"]["status"]=="PAID_LEARNED" for s in steps))
    rec={"genesis":genesis,"source_steps":steps,
         "paid_t1_mean_anchor":[{"key":list(k),"stat":deepcopy(v)}
              for k,v in sorted(t1_stats.items(),key=lambda x:repr(x[0]))],
         "source_valid":valid,"source_error":error,
         "tick4_world":D0._snapshot_world(world),
         "tick4_mind":C.seal_mind(mind)}
    rec["source_receipt_sha256"]=C.digest(rec)
    return world,mind,t1_stats,rec


def residual_intervention(mind, mode):
    """Only residual *values* in a cloned mind can differ after native T5."""
    if mode not in RESIDUAL:
        raise ValueError("invalid DEV residual mode")
    before=C.seal_mind(mind)
    original=deepcopy(mind.acc)
    if mode=="carry":
        mind.acc=deepcopy(original)
    else:
        mind.acc={key:0.0 for key in original}
    if set(mind.acc)!=set(original) or any(
            type(v) is not float for v in mind.acc.values()):
        raise AssertionError("accumulator key or value class changed")
    after=C.seal_mind(mind)
    except_acc=deepcopy(mind)
    except_acc.acc=deepcopy(original)
    if C.seal_mind(except_acc)!=before:
        raise AssertionError("residual fork altered another private mind field")
    if mode=="carry" and after!=before:
        raise AssertionError("carry control changed mind state")
    return {"mode":mode,"keys":sorted(original),
            "values_before":original,
            "values_after":dict(mind.acc),
            "before_mind":before,"after_mind":after,
            "no_action_override":True}


def t5_pair_cost(left,right):
    return (all(left[x]==right[x] for x in (
        "before_world","before_mind","capture",
        "cognitive_work","requested_native_cost","decision_remaining"))
        and left["native_motor"]["cognitive_accounting"]==
        right["native_motor"]["cognitive_accounting"])


def t6_pair_cost(left,right):
    """Never correct inequality; report and fail the scientific parity gate."""
    return (all(left[x]==right[x] for x in (
        "before_world","capture","cognitive_work",
        "requested_native_cost","decision_remaining"))
        and left["native_motor"]["cognitive_accounting"]==
        right["native_motor"]["cognitive_accounting"])


def body_comparison(x,y):
    a,b=x["metrics"],y["metrics"]
    survival=a["lived_ticks_t5_t60"]-b["lived_ticks_t5_t60"]
    delta=[v-w for v,w in zip(a["terminal_body"],b["terminal_body"])]
    rank="NOT_COMPARABLE_HORIZON"
    if (survival==0 and a["alive_at_horizon"] and b["alive_at_horizon"]):
        if all(d>=-1e-9 for d in delta) and any(d>1e-9 for d in delta):
            rank="CARRY_FIVE_CHANNEL_DOMINANCE"
        elif all(d<=1e-9 for d in delta) and any(d < -1e-9 for d in delta):
            rank="ZERO_FIVE_CHANNEL_DOMINANCE"
        elif all(abs(d)<=1e-9 for d in delta):
            rank="FIVE_CHANNELS_EQUAL"
        else:
            rank="MIXED_BODY_TRADEOFF"
    return {
        "delta_lived_ticks_t6_t60":survival,"terminal_body_delta":delta,
        "pareto":rank, "carry_terminal_body":a["terminal_body"],
        "zero_terminal_body":b["terminal_body"],
        "carry_paid_decision":a["paid_decision"],
        "zero_paid_decision":b["paid_decision"],
        "carry_paid_learning":a["paid_learning"],
        "zero_paid_learning":b["paid_learning"],
        "carry_drinks":a["water_drinks"],"zero_drinks":b["water_drinks"],
        "carry_meals":a["foods_actually_eaten"],"zero_meals":b["foods_actually_eaten"]}


def _followup(world,mind,mode,horizon):
    out=L.followup(world,mind,"full",None,horizon)
    out["policy"]="DEV_M_"+mode
    return out


def _one(grid,origin):
    world,mind,t1,source=_source(grid,origin)
    row={"origin":origin,"source":source,"content_t5":{},
         "arms":{},"shams":{},"sham_arms":{},"comparison":{}}
    if not source["source_valid"]:
        return row
    t5_states={}
    for content in CONTENT:
        w,m=deepcopy(world),deepcopy(mind)
        mode="full" if content=="recent" else "stale_owned_t1_means"
        t5=L.paid_step(w,m,mode,t1 if content=="stale" else None)
        row["content_t5"][content]=t5
        t5_states[content]=(w,m)
    sham_w,sham_m=deepcopy(world),deepcopy(mind)
    sham_t5=L.paid_step(sham_w,sham_m,"full_sham")
    row["shams"]["t5_recent_full_sham"]=sham_t5
    row["comparison"]["t5_full_sham_neutral"]=(L.semantic_sham_step(sham_t5)==
                             L.semantic_sham_step(row["content_t5"]["recent"]))
    row["comparison"]["equal_t5_real_decision_cost"]=t5_pair_cost(
         row["content_t5"]["recent"],row["content_t5"]["stale"])
    for content in CONTENT:
        a_world,a_mind=t5_states[content]
        for mode in RESIDUAL:
            key=content+"/"+mode
            world_i,mind_i=deepcopy(a_world),deepcopy(a_mind)
            fork=residual_intervention(mind_i,mode)
            row["arms"][key]={"fork":fork,
                   "followup":_followup(world_i,mind_i,key,grid["final_tick"])}
            # Repeat the SAME nonmotor operation, with a freshly cloned native
            # T5 state. No fictitious CognitiveWork or physics, no seeded L life.
            world_s,mind_s=deepcopy(a_world),deepcopy(a_mind)
            fork_sham=residual_intervention(mind_s,mode)
            same=(fork==fork_sham)
            sham=_followup(world_s,mind_s,key,grid["final_tick"])
            ref=row["arms"][key]["followup"]
            row["sham_arms"][key]=sham
            same=(same and sham["steps"]==ref["steps"]
                  and sham["last_world"]==ref["last_world"]
                  and sham["last_mind"]==ref["last_mind"]
                  and sham["metrics"]==ref["metrics"])
            row["shams"][key+"_neutral"]=same
        carry=row["arms"][content+"/carry"]["followup"]
        zero=row["arms"][content+"/zero"]["followup"]
        if carry["steps"] and zero["steps"]:
            x,y=carry["steps"][0],zero["steps"][0]
            row["comparison"][content]={
              "equal_t6_real_decision_cost":t6_pair_cost(x,y),
              "winner_changed":(
                x["decision_info"]["observer"]["competition_witness"]["winner_before_control"]!=
                y["decision_info"]["observer"]["competition_witness"]["winner_before_control"]),
              "motor_changed":(x["action"],x["param"])!=(y["action"],y["param"]),
              "carry_t6_motor":[x["action"],x["param"]],
              "zero_t6_motor":[y["action"],y["param"]],
              "carry_t6_winner":x["decision_info"]["observer"]["competition_witness"]["winner_before_control"],
              "zero_t6_winner":y["decision_info"]["observer"]["competition_witness"]["winner_before_control"],
              "carry_t6_work":x["cognitive_work"],"zero_t6_work":y["cognitive_work"],
              "carry_t6_billing":x["requested_native_cost"],
              "zero_t6_billing":y["requested_native_cost"],
              "t6_body_delta_after_paid_learning":[
                  v-w for v,w in zip(x["postaction"]["body_after_any_learning"],
                                     y["postaction"]["body_after_any_learning"])],
              "t6_body_delta_after_motor":[
                  v-w for v,w in zip(x["native_motor"]["body"],
                                     y["native_motor"]["body"])],
              "body":body_comparison(carry,zero),
            }
        else:
            row["comparison"][content]={"error":"MISSING_NATIVE_T6"}
    row["case_sha256"]=C.digest({k:v for k,v in row.items()
                                  if k!="case_sha256"})
    return row


def classify(rows):
    if any(not r["source"]["source_valid"] or
       any(not r["arms"][k]["followup"]["steps"] or
               r["arms"][k]["followup"]["metrics"]["native_error"] is not None
               for k in r["arms"]) or len(r["arms"])!=4
           for r in rows):
        return "DEV_INCONCLUSIVE_UNFUNDED_OR_INCOMPLETE_SOURCE"
    if any(not r["comparison"]["t5_full_sham_neutral"] or
           not all(r["shams"][k+"_neutral"] for k in r["arms"])
           for r in rows):
        return "DEV_INVALID_NONNEUTRAL_SHAM"
    if any(not r["comparison"]["equal_t5_real_decision_cost"] or
           any(not r["comparison"][c]["equal_t6_real_decision_cost"]
               for c in CONTENT)
           for r in rows):
        return "DEV_INCONCLUSIVE_REAL_DECISION_COST_GATE"
    changed=sum(r["comparison"][c]["motor_changed"]
                for r in rows for c in CONTENT)
    return ("DEV_ONLY_MOTOR_EFFECT_OBSERVED_NOT_SCIENCE" if changed else
            "DEV_ONLY_NO_MOTOR_EFFECT_NOT_SCIENCE")


def produce(full=False,replica2=False):
    grid=dev_replica2_grid(full) if replica2 else dev_grid(full)
    source_gate(grid)
    rows=[_one(grid,origin) for origin in grid["origins"]]
    status=classify(rows)
    return {
       "schema":SCHEMA,"phase":"DEV_ONLY_NEVER_SCIENTIFIC",
       "design":"two-factor memory-readout at T5 x native residual carry/zero at pre-T6",
       "source_policy":"F1JFixedRoundMind",
       "original_protected_F1L_main":"9c40f01684f5e69c893d765aa41cad1af1d33532",
       "scientific_verdict":None,
       "development_status":status,
       "origin_count":len(rows),"arm_count_per_origin":4,
       "grid":grid,"rows":rows,
       "f1l_scientific_roots_exposed":0,
       "no_imposed_motors":True,
       "no_retroactive_equalization":True,
       "summary":{
          "valid_source":sum(r["source"]["source_valid"] for r in rows),
          "t5_equal_paid":sum(r["comparison"].get("equal_t5_real_decision_cost",False) for r in rows),
          "t6_equal_paid":sum(r["comparison"].get(c,{}).get("equal_t6_real_decision_cost",False) for r in rows for c in CONTENT),
          "t6_winner_changed":sum(r["comparison"].get(c,{}).get("winner_changed",False) for r in rows for c in CONTENT),
          "t6_motor_changed":sum(r["comparison"].get(c,{}).get("motor_changed",False) for r in rows for c in CONTENT),
          "sham_valid":sum(r["comparison"].get("t5_full_sham_neutral",False) and
             all(r["shams"][k+"_neutral"] for k in r["arms"]) for r in rows),
          "t60_body_non_equal":sum(any(abs(v)>1e-9 for v in r["comparison"].get(c,{}).get("body",{}).get("terminal_body_delta",[])) for r in rows for c in CONTENT),
          "survival_advantage_carry":sum(r["comparison"].get(c,{}).get("body",{}).get("delta_lived_ticks_t6_t60",0)>0 for r in rows for c in CONTENT),
          "survival_advantage_zero":sum(r["comparison"].get(c,{}).get("body",{}).get("delta_lived_ticks_t6_t60",0)<0 for r in rows for c in CONTENT),
       }}


def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--smoke",action="store_true")
    g.add_argument("--full",action="store_true")
    g.add_argument("--full-replica2",action="store_true")
    p.add_argument("--output",required=True)
    x=p.parse_args()
    report=produce(x.full or x.full_replica2,replica2=x.full_replica2)
    with open(x.output,"xb") as fd:
        with gzip.GzipFile(fileobj=fd,mode="wb",filename="",mtime=0) as out:
            out.write(C.canonical(report))
    print(json.dumps({"phase":report["phase"],"diagnostic":report["development_status"],
                      "roots":report["origin_count"],"summary":report["summary"]},sort_keys=True))


if __name__=="__main__":
    main()
