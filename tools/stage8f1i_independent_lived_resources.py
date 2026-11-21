"""Stage8-F1I: 16 fresh unprimed individuals, genuinely paid personal histories.

The preregistration grid and estimand existed in Git BEFORE any F1I native
steps. Each Mind starts with NO personal effects, TD content or buffer.
It learns solely from its own four native paid World.step observations.
At tick 5 a temporary readout of its OWN older (tick 1) paid means is the
only intervention; every later decision is free, native and actually paid.
Four WorldSpecs have REAL visible water and consumable food effects.
NO prior F1F/H experiment is retrained or reinterpreted, no run_life/birth.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import json

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import FoodPatch, WaterSource, World, WorldSpec
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1h_prospective_native_body_value as H

SCHEMA="i3-stage8f1i-16-personal-paid-experiences-real-food-T30/v0"
SOURCE_MAIN="15c6869484c5b47b14d44c9e4e77b431a80b5caa"
PRE_GRID_COMMIT="9bb5af06cc6e78f4ec86895ee57d6ccfff7f636b"
PRE_PROTOCOL_COMMIT="ff6b8b0c627797e9443ea4393e5e682e9cc07681"
GRID="docs/research/studies/stage8f1-paid-microdecision/STAGE8F1I_FROZEN_EXPERIMENT_GRID_2026-11-21.json"
MODES=("full","sham","mask_owned_prior_means")
T_ACQUIRE=4
T_ANCHOR=1
T_FORK=5
T_END=30
MATRIX={
    "oasis_fruit":((1,1),25.,(1,1),"f1i-fruit",18.,2.,(20.,64.,10.,91.,96.)),
    "spring_grain":((1,0),30.,(2,1),"f1i-grain",26.,.5,(24.,58.,12.,89.,95.)),
    "patch_tuber":((2,1),18.,(1,1),"f1i-tuber",12.,3.,(18.,68.,11.,87.,94.)),
    "bitter_tradeoff":((1,1),22.,(0,1),"f1i-bitter",28.,-1.5,(22.,60.,9.5,93.,97.)),
}
ECOLOGIES=tuple(MATRIX)
FROZEN_RESULTS={
 "f1f":"MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES",
 "f1g_td":"NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
 "f1g_buffer":"NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
 "f1h_survival":"NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12",
 "stage8e2":"STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
}


def exact_grid(path=GRID):
    data=json.loads(Path(path).read_text(encoding="utf8"))
    if (data.get("schema")!="i3-stage8f1i-preregistered-grid-v0"
            or data.get("main_before_exposure")!=SOURCE_MAIN
            or data.get("mind")!="i3.modules.mind.Mind"
            or data.get("genome")!="midpoint()"
            or data.get("personal_acquisition_ticks")!=T_ACQUIRE
            or data.get("first_paid_memory_anchor_tick")!=T_ANCHOR
            or data.get("memory_readout_fork_tick")!=T_FORK
            or data.get("terminal_tick")!=T_END
            or data.get("arms")!=list(MODES)
            or data.get("world_width")!=3
            or data.get("world_height")!=3
            or data.get("spawn")!=[1,1]
            or type(data.get("origins")) is not list
            or len(data["origins"])!=16 or len(data.get("modes",[]))!=4):
        raise AssertionError("changed exact preexposure geometry, roots or gates")
    expected_modes=[]
    expected_origins=[]
    for i,(name,parameter) in enumerate(MATRIX.items()):
        water,wgain,food,token,fgain,delta,base=parameter
        expected_modes.append({
            "id":name,"water":list(water),"water_gain":wgain,
            "water_stock":2,"food":list(food),"token":token,
            "food_gain":fgain,"integrity_delta":delta,
            "food_quantity":2,"food_max_quantity":2,"water_max_stock":2,
            "water_restock_every":0,"food_restock_every":0,
            "token_effects":[fgain,delta]})
        for j in range(4):
            num=i*4+j+1
            expected_origins.append({
                "id":"R"+str(num).zfill(2),
                "ecology":name,"seed":202611210101+i*4+j,
                "body":[round(x+shift*j,3) for x,shift in zip(base,(1.25,-.8,.4,-.5,-.6))]
            })
    if data["modes"]!=expected_modes or data["origins"]!=expected_origins:
        raise AssertionError("source-lock: no selection of worlds, genotypes, seeds or conditions")
    return data


def new_source_world(case):
    water,wgain,food,token,fgain,delta,_=MATRIX[case["ecology"]]
    spec=WorldSpec(
        name="F1I_ORIGIN_"+case["id"]+"_"+case["ecology"],
        width=3,height=3,spawn=(1,1),body=tuple(case["body"]),
        water={water:WaterSource(gain=wgain,stock=2,max_stock=2,restock_every=0)},
        food={food:FoodPatch(token=token,quantity=2,max_quantity=2,restock_every=0)},
        token_effects={token:(fgain,delta)},
        changes=(),laws=BodyLaws()
    )
    return World(spec)


def paid_step(world,mind,*,mask=None):
    """One native decision AND one truly funded learning on same individual."""
    if world.dead or world.t>=T_END:
        raise RuntimeError("no native decisions after death or horizon")
    before_world=D._snapshot_world(world)
    before_mind=C.seal_mind(mind)
    cap=world.capture()
    effects_orig=deepcopy(mind.effects)
    other_values=deepcopy(mind.values)
    other_buffer=deepcopy(mind.buffer)
    keys=[]
    if mask is None:
        readout_mode="full"
    elif mask=="sham":
        readout_mode="sham"
        mind.effects=deepcopy(mind.effects)
    else:
        readout_mode="mask_owned_prior_means"
        # Intersect exactly the individual's OWN legitimately paid tick-1
        # effect keys with the currently acquired tick-4 keys.
        eligible=set(mask)&set(effects_orig.stats)
        keys=sorted(eligible,key=repr)
        mind.effects=deepcopy(mind.effects)
        for k in keys:
            prior=mask[k]
            current=mind.effects.stats[k]
            if (len(prior)!=3 or len(current)!=3 or
                len(prior[1])!=5 or len(current[1])!=5):
                raise AssertionError("readout mask cannot forge missing real memories")
            current[1][:]=prior[1]
    exposed=C.seal_mind(mind)
    before_t=world.t
    budget=CognitiveBudget(world.body,world.laws)
    action,param,work,info=mind.decide(cap,budget)
    after_decide_exposed=C.seal_mind(mind)
    if world.t!=before_t or work!=budget.work:
        raise AssertionError("unfunded mind computation or hidden motor action")
    mind.effects=effects_orig
    if mind.values!=other_values or list(mind.buffer)!=list(other_buffer):
        raise AssertionError("laboratory or decision altered unmasked TD/buffer")
    after_restore=C.seal_mind(mind)
    promised=dict(zip(("energy","vigilance"),cognitive_cost(world.laws,work)))
    raw=world.step(action,param,work)
    C.paid_bill(world.laws,work,raw["cognitive_accounting"])
    after_motor=D._snapshot_world(world)
    native_motor={
        "t":raw["t"],"body":list(raw["body"]),
        "dead":list(raw["dead"]),"moved":raw["moved"],
        "cognitive_accounting":deepcopy(raw["cognitive_accounting"])
    }
    learning=H._pay_new_learning(world,mind,raw)
    step={
        "t":world.t,
        "before_world":before_world,
        "before_mind":before_mind,
        "capture":json.loads(C.canonical(cap)),
        "capture_sha256":C.digest(cap),
        "readout_mode":readout_mode,
        "temporary_prior_mean_keys":[list(k) for k in keys],
        "exposed_mind_during_decision":exposed,
        "after_decision_exposed_mind":after_decide_exposed,
        "after_restoration_before_motor":after_restore,
        "action":action,"param":param,
        "decision_info":json.loads(C.canonical(info)),
        "cognitive_work":asdict(work),
        "decision_remaining":list(budget.remaining),
        "requested_native_cost":promised,
        "native_motor":native_motor,
        "after_motor_world":after_motor,
        "postaction":learning,
        "after_paid_learning_world":D._snapshot_world(world),
        "after_paid_learning_mind":C.seal_mind(mind),
        "no_experimental_action_override":True,
    }
    step["receipt_sha256"]=C.digest(step)
    return step


def personal_source(case):
    world=new_source_world(case)
    mind=Mind(midpoint(),case["seed"])
    if (mind.effects.stats or mind.buffer or
        any(any(v!=0. for v in row) for row in mind.values) or
        world.t!=0 or world.dead):
        raise AssertionError("new roots must have no imported acquired memory")
    genesis={"world":D._snapshot_world(world),"mind":C.seal_mind(mind)}
    steps=[]
    exception=None
    owned_prior={}
    for tick in range(1,T_ACQUIRE+1):
        if world.dead:
            break
        try:
            step=paid_step(world,mind)
            steps.append(step)
            if tick==T_ANCHOR:
                owned_prior=deepcopy(mind.effects.stats)
        except (ValueError,KeyError,RuntimeError,AssertionError) as e:
            exception={"tick_attempted":tick,"type":type(e).__name__,"message":str(e)}
            break
    learned=deepcopy(mind.effects.stats)
    valid=(
        exception is None and len(steps)==T_ACQUIRE and
        world.t==T_ACQUIRE and not world.dead and
        bool(owned_prior) and steps[0]["postaction"]["status"]=="PAID_LEARNED"
    )
    row={
        "origin":case,
        "genesis":genesis,
        "source_steps":steps,
        "paid_t1_mean_anchor":[{"key":list(k),"stat":deepcopy(v)}
                               for k,v in sorted(owned_prior.items(),key=lambda x:repr(x[0]))],
        "paid_t4_full_effects":[{"key":list(k),"stat":deepcopy(v)}
                               for k,v in sorted(learned.items(),key=lambda x:repr(x[0]))],
        "source_tick4_world":D._snapshot_world(world),
        "source_tick4_mind":C.seal_mind(mind),
        "source_valid_for_fork":valid,
        "source_native_error":exception,
        "source_experiences_created_by_run_life":False
    }
    row["source_receipt_sha256"]=C.digest(row)
    return world,mind,owned_prior,row


def metric(steps,world,error):
    dec={"energy":0.,"vigilance":0.}
    learned={"energy":0.,"vigilance":0.}
    water_drinks=food_ate=food_collected=0
    area=[0.]*5
    min_vital=None
    for s in steps:
        for coin in dec:
            dec[coin]+=s["native_motor"]["cognitive_accounting"][coin]["paid"]
            b=s["postaction"]["actual_paid_learning_bill"]
            if b is not None:
                learned[coin]+=b[coin]["paid"]
        if s["action"]=="boire":water_drinks+=1
        if s["action"]=="manger":food_ate+=1
        if s["action"]=="collecter":food_collected+=1
        body=s["postaction"]["body_after_any_learning"]
        for i in range(5):
            area[i]+=body[i]
        min_vital=min(min_vital if min_vital is not None else float("inf"),
                      min(body[1:4]))
    return {
        "steps_t5_to_t30":len(steps),
        "alive_at_t30":bool(world.t==T_END and not world.dead and error is None),
        "final_tick":world.t,"terminal_dead":list(world.dead),
        "terminal_body":list(world.body),"terminal_position":list(world.pos),
        "terminal_water_stock":[[list(k),v.stock] for k,v in sorted(world.water.items())],
        "terminal_food_quantity":[[list(k),v.quantity] for k,v in sorted(world.food.items())],
        "terminal_inventory":sorted([[k,v] for k,v in world.inventory.items()]),
        "cumulated_body_observed":area,"minimum_vital_reserve":min_vital,
        "paid_decision":dec,"paid_learning":learned,
        "water_drinks":water_drinks,"foods_collected":food_collected,
        "foods_actually_eaten":food_ate,
        "native_error":error
    }


def trajectory(world,mind,mode,anchor):
    steps=[]
    error=None
    for tick in range(T_FORK,T_END+1):
        if world.dead:
            break
        try:
            intervention=(anchor if mode=="mask_owned_prior_means" and tick==T_FORK
                         else "sham" if mode=="sham" and tick==T_FORK
                         else None)
            steps.append(paid_step(world,mind,mask=intervention))
        except (ValueError,KeyError,RuntimeError,AssertionError) as e:
            error={"tick_attempted":tick,"type":type(e).__name__,"message":str(e)}
            break
    row={"mode":mode,"steps":steps,
         "last_world":D._snapshot_world(world),"last_mind":C.seal_mind(mind),
         "metrics":metric(steps,world,error)}
    row["trajectory_sha256"]=C.digest(row)
    return row


def _same_fork(a,b):
    if not a["steps"] or not b["steps"]:
        return False
    x,y=a["steps"][0],b["steps"][0]
    return all(x[k]==y[k] for k in (
        "before_world","before_mind","capture","capture_sha256",
        "cognitive_work","decision_remaining","requested_native_cost",
        "native_motor")) if (x["action"],x["param"])==(y["action"],y["param"]) else all(
        x[k]==y[k] for k in (
            "before_world","before_mind","capture","capture_sha256",
            "cognitive_work","decision_remaining","requested_native_cost",
            "native_motor") if k!="native_motor"
        ) and x["native_motor"]["cognitive_accounting"]==y["native_motor"]["cognitive_accounting"]


def _sham_equal(full,sham):
    if (not full["steps"] or not sham["steps"] or
        len(full["steps"])!=len(sham["steps"]) or
        full["metrics"]!=sham["metrics"] or
        full["last_world"]!=sham["last_world"] or
        full["last_mind"]!=sham["last_mind"]):
        return False
    for a,b in zip(full["steps"],sham["steps"]):
        if a["t"]==T_FORK:
            if any(a[k]!=b[k] for k in (
                "before_world","before_mind","capture","after_decision_exposed_mind",
                "after_restoration_before_motor","action","param","decision_info",
                "cognitive_work","decision_remaining","native_motor",
                "after_motor_world","postaction","after_paid_learning_mind",
                "after_paid_learning_world")):
                return False
        elif a!=b:
            return False
    return True


def _survival(a,b):
    if a["alive_at_t30"]!=b["alive_at_t30"]:
        return "FULL_SURVIVAL_ADVANTAGE" if a["alive_at_t30"] else "FULL_SURVIVAL_DISADVANTAGE"
    if a["steps_t5_to_t30"]!=b["steps_t5_to_t30"]:
        return "FULL_SURVIVAL_ADVANTAGE" if a["steps_t5_to_t30"]>b["steps_t5_to_t30"] else "FULL_SURVIVAL_DISADVANTAGE"
    return "NO_SURVIVAL_DIFFERENCE"


def _pareto(a,b):
    if not a["alive_at_t30"] or not b["alive_at_t30"]:
        return None
    x,y=a["terminal_body"],b["terminal_body"]
    if all(u>=v-1e-9 for u,v in zip(x,y)) and any(u>v+1e-9 for u,v in zip(x,y)):
        return "FULL_FIVE_CHANNEL_DOMINANCE"
    if all(v>=u-1e-9 for u,v in zip(x,y)) and any(v>u+1e-9 for u,v in zip(x,y)):
        return "MASKED_FIVE_CHANNEL_DOMINANCE"
    if all(abs(u-v)<=1e-9 for u,v in zip(x,y)):
        return "FIVE_CHANNELS_EQUAL"
    return "MIXED_BODILY_TRADEOFF"


def produce(grid):
    if grid!=exact_grid():
        raise AssertionError("frozen source grid changed")
    rows=[]
    for case in grid["origins"]:
        world,mind,prior,source=personal_source(case)
        if not source["source_valid_for_fork"]:
            row={"origin":case,"source":source,"arms":{},
                 "fork_work_and_bills_equal":False,"sham_whole_trajectory_equal":False,
                 "motor_changed":None,"full_survival_advantage":None,
                 "terminal_five_channel_dominance":None,
                 "origin_valid":False}
        else:
            arms={
               mode:trajectory(deepcopy(world),deepcopy(mind),mode,prior)
               for mode in MODES
            }
            base=arms["full"]
            equal=all(_same_fork(base,arms[mode]) for mode in MODES)
            sham=_sham_equal(arms["full"],arms["sham"])
            errors=any(t["metrics"]["native_error"] is not None for t in arms.values())
            valid=equal and sham and not errors
            changed=bool(
                base["steps"] and arms["mask_owned_prior_means"]["steps"] and
                (base["steps"][0]["action"],base["steps"][0]["param"])!=
                (arms["mask_owned_prior_means"]["steps"][0]["action"],
                 arms["mask_owned_prior_means"]["steps"][0]["param"]))
            f=base["metrics"]
            m=arms["mask_owned_prior_means"]["metrics"]
            row={
                "origin":case,"source":source,"arms":arms,
                "fork_work_and_bills_equal":equal,
                "sham_whole_trajectory_equal":sham,
                "motor_changed":changed if valid else None,
                "full_survival_advantage":_survival(f,m) if valid else None,
                "terminal_five_channel_dominance":_pareto(f,m) if valid else None,
                "origin_valid":valid,
            }
        row["case_sha256"]=C.digest(row)
        rows.append(row)
    all_sources=all(r["source"]["source_valid_for_fork"] for r in rows)
    costs=all(r["fork_work_and_bills_equal"] for r in rows)
    shams=all(r["sham_whole_trajectory_equal"] for r in rows)
    valid=sum(r["origin_valid"] for r in rows)
    changed=[r for r in rows if r["motor_changed"] is True]
    wins=[r for r in changed if r["full_survival_advantage"]=="FULL_SURVIVAL_ADVANTAGE"]
    losses=[r for r in changed if r["full_survival_advantage"]=="FULL_SURVIVAL_DISADVANTAGE"]
    distinct=len(set(r["origin"]["ecology"] for r in wins))
    if not all_sources:
        status="INCONCLUSIVE_SOURCE_GATE"
    elif not costs:
        status="INCONCLUSIVE_COST_GATE"
    elif not shams:
        status="INVALID_SHAM"
    elif valid!=16:
        status="INCONCLUSIVE_NATIVE_OR_EVIDENCE_GATE"
    elif len(wins)>=3 and distinct>=2 and not losses:
        status="REPRODUCIBLE_LOCAL_T30_SURVIVAL_ADVANTAGE_OF_OWN_LEARNED_CONTENT"
    else:
        status="NO_REPRODUCIBLE_SURVIVAL_ADVANTAGE_T30"
    food_eaten=sum(
        a["metrics"]["foods_actually_eaten"]
        for r in rows for a in r["arms"].values())
    water_drinks=sum(
        a["metrics"]["water_drinks"]
        for r in rows for a in r["arms"].values())
    return _final({
        "schema":SCHEMA,"source_main":SOURCE_MAIN,
        "preexposure_grid_commit":PRE_GRID_COMMIT,
        "preexposure_protocol_commit":PRE_PROTOCOL_COMMIT,
        "personal_first_paid_tick":T_ANCHOR,"acquisition_ticks":T_ACQUIRE,
        "single_memory_readout_intervention_tick":T_FORK,
        "terminal_tick":T_END,"preregistered_origin_count":16,
        "preregistered_eco_names":list(ECOLOGIES),"arms_per_origin":list(MODES),
        "genome_shared_between_roots":"midpoint()",
        "initial_personal_effects_TD_buffer_empty":True,
        "no_forced_actions":True,"real_world_token_effects_configured":True,
        "all_future_reads_unmodified_after_t5":True,
        "full_lives_or_run_life":0,"new_scientific_cohorts":0,
        "native_first_four_source_step_count":sum(len(r["source"]["source_steps"]) for r in rows),
        "native_followup_step_count":sum(len(a["steps"]) for r in rows for a in r["arms"].values()),
        "valid_paid_personal_sources":sum(r["source"]["source_valid_for_fork"] for r in rows),
        "valid_matched_prospective_origins":valid,
        "motor_changed_origins":len(changed),
        "survival_favorable_changed_origins":len(wins),
        "survival_unfavorable_changed_origins":len(losses),
        "favorable_ecology_count":distinct,
        "actual_native_food_ingestions_all_arms":food_eaten,
        "actual_native_water_drinks_all_arms":water_drinks,
        "strict_preexposed_primary_verdict":status,
        "frozen_prior_studies":FROZEN_RESULTS,
        "rows":rows,
    })


def _final(rep):
    rep["provenance_chain_sha256"]=C.digest({
       "source_main":SOURCE_MAIN,"grid_commit":PRE_GRID_COMMIT,
       "protocol_commit":PRE_PROTOCOL_COMMIT,
       "case_hashes":[r["case_sha256"] for r in rep["rows"]],
    })
    return rep


def main():
    p=argparse.ArgumentParser(description="F1I 16 unprimed and independently learned native Worlds")
    p.add_argument("--grid",default=GRID)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    grid=exact_grid(a.grid)
    report=produce(grid)
    with Path(a.output).open("xb") as fd:
        fd.write(C.canonical(report))
    print(json.dumps({
        "primary_verdict":report["strict_preexposed_primary_verdict"],
        "sources":report["valid_paid_personal_sources"],
        "valid_cost_matched_origins":report["valid_matched_prospective_origins"],
        "changed_motor_origins":report["motor_changed_origins"],
        "survival_favorable":report["survival_favorable_changed_origins"],
        "survival_unfavorable":report["survival_unfavorable_changed_origins"],
        "food_eaten":report["actual_native_food_ingestions_all_arms"],
        "water_drinks":report["actual_native_water_drinks_all_arms"],
        "source_steps":report["native_first_four_source_step_count"],
        "followup_steps":report["native_followup_step_count"],
        "sha256":C.digest(report)
    },sort_keys=True))


if __name__=="__main__":
    main()
