"""Cold stdlib-only F1I auditor, independent of new 16-Mind producer.

Recompute from the original sixteen independently seeded origins: 4 paid
personal experience ticks, 3 identically funded fork choices, up to T30
unforced continuation, genuine token effects on native *consumption*,
energy/vigilance decision and learning debits, irreversible vital death.

No i3 engine, World/Mind/Body imports, and no producer imported.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1d_independent_next_decision_audit as D

SCHEMA="i3-stage8f1i-16-personal-paid-experiences-real-food-T30/v0"
BASE="15c6869484c5b47b14d44c9e4e77b431a80b5caa"
GRID_COMMIT="9bb5af06cc6e78f4ec86895ee57d6ccfff7f636b"
PRE_COMMIT="ff6b8b0c627797e9443ea4393e5e682e9cc07681"
T4=4
FORK=5
END=30
MODES=("full","sham","mask_owned_prior_means")
FROZEN={
 "f1f":"MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES",
 "f1g_td":"NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
 "f1g_buffer":"NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
 "f1h_survival":"NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12",
 "stage8e2":"STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
}
ECOLOGIES={
 "oasis_fruit":((1,1),25.,(1,1),"f1i-fruit",18.,2.,(20.,64.,10.,91.,96.)),
 "spring_grain":((1,0),30.,(2,1),"f1i-grain",26.,.5,(24.,58.,12.,89.,95.)),
 "patch_tuber":((2,1),18.,(1,1),"f1i-tuber",12.,3.,(18.,68.,11.,87.,94.)),
 "bitter_tradeoff":((1,1),22.,(0,1),"f1i-bitter",28.,-1.5,(22.,60.,9.5,93.,97.)),
}
MOTOR={"se_deplacer":2.,"collecter":1.,"manger":.5,
       "boire":.5,"attendre":.35}
DELTA={"N":(0,-1),"E":(1,0),"S":(0,1),"W":(-1,0)}
COINS=("energy","vigilance")


def check(test,msg):
    I.check(test,"COLD F1I: "+msg)


def body_eq(a,b,what):
    I.body_equal(a,b,"COLD F1I "+what)


def expected_cases():
    modes=[]
    roots=[]
    for i,(name,attributes) in enumerate(ECOLOGIES.items()):
        water,water_gain,food,token,gain,delta,base=attributes
        modes.append({"id":name,"water":list(water),"water_gain":water_gain,
                      "water_stock":2,"food":list(food),"token":token,
                      "food_gain":gain,"integrity_delta":delta,
                      "food_quantity":2,"food_max_quantity":2,"water_max_stock":2,
                      "water_restock_every":0,"food_restock_every":0,
                      "token_effects":[gain,delta]})
        for j in range(4):
            roots.append({"id":"R"+str(i*4+j+1).zfill(2),
                          "ecology":name,"seed":202611210101+i*4+j,
                          "body":[round(v+shift*j,3)
                                  for v,shift in zip(base,(1.25,-.8,.4,-.5,-.6))]})
    return modes,roots


def validate_grid(grid):
    modes,roots=expected_cases()
    check(type(grid) is dict
          and grid.get("schema")=="i3-stage8f1i-preregistered-grid-v0"
          and grid.get("main_before_exposure")==BASE
          and grid.get("genome")=="midpoint()"
          and grid.get("mind")=="i3.modules.mind.Mind"
          and grid.get("no_imported_prior") is True
          and grid.get("world_width")==3 and grid.get("world_height")==3
          and grid.get("spawn")==[1,1]
          and grid.get("start_tick")==0
          and grid.get("personal_acquisition_ticks")==T4
          and grid.get("first_paid_memory_anchor_tick")==1
          and grid.get("memory_readout_fork_tick")==FORK
          and grid.get("terminal_tick")==END
          and grid.get("arms")==list(MODES)
          and grid.get("modes")==modes
          and grid.get("origins")==roots,
          "preexposed origin/world/genome/food grid was altered")
    return roots


def world_start(case):
    water,water_gain,food,token,fgain,delta,_=ECOLOGIES[case["ecology"]]
    return {
        "t":0,"body":case["body"],
        "position":[1,1],"inventory":[],"dead":[],
        "water_cells":[[list(water),water_gain,2,2,0]],
        "food_cells":[[list(food),token,2,2,0]],
        "hidden_effects":[[token,[fgain,delta]]],
        "world_spec":{
           "name":"F1I_ORIGIN_"+case["id"]+"_"+case["ecology"],
           "width":3,"height":3,"spawn":[1,1],
           "laws":D.LAWS
        }
    }


def state_valid(s,case):
    start=world_start(case)
    check(s["world_spec"]==start["world_spec"]
          and s["hidden_effects"]==start["hidden_effects"]
          and len(s["position"])==2
          and 0<=s["position"][0]<3 and 0<=s["position"][1]<3,
          "WorldSpec resource effect or geography changed")
    w=s["water_cells"]
    food=s["food_cells"]
    check(len(w)==len(food)==1
          and w[0][:2]==start["water_cells"][0][:2]
          and food[0][:2]==start["food_cells"][0][:2]
          and w[0][3:]==[2,0]
          and food[0][3:]==[2,0]
          and type(w[0][2]) is int and 0<=w[0][2]<=2
          and type(food[0][2]) is int and 0<=food[0][2]<=2,
          "forged food/water stock or native source position")
    check(s["t"]>=0 and type(s["dead"]) is list
          and type(s["inventory"]) is list and len(s["body"])==5,
          "missing body or native death record")
    for token,n in s["inventory"]:
        check(token==start["food_cells"][0][1] and
              type(n) is int and 0<=n<=2,
              "invented food carried by individual")
    return s


def perceive(s):
    p=tuple(s["position"])
    water=tuple(s["water_cells"][0][0])
    food=tuple(s["food_cells"][0][0])
    token=s["food_cells"][0][1]
    stock=s["water_cells"][0][2]
    amount=s["food_cells"][0][2]
    def cell(q):
        if not 0<=q[0]<3 or not 0<=q[1]<3:
            return None
        return [q==water and stock>0,[token] if q==food and amount>0 else []]
    x,y=p
    return {"body":s["body"],
            "inventory":[v for v in s["inventory"] if v[1]>0],
            "here":cell((x,y)),
            "neighbors":[cell(z) for z in ((x,y-1),(x+1,y),(x,y+1),(x-1,y))]}


def physical(before,action,param,work,bill,case):
    """Cold World.step + BodyLaws v2: water, food, integrity, sleep, all coins."""
    state_valid(before,case)
    check(not before["dead"] and 0<=before["t"]<END,
          "action after death or unregistered horizon")
    costs=I.cost(work)
    I.check_bill(bill,costs,"F1I decision motor")
    energy,food,water,integrity,vigilance=before["body"]
    check(energy>=costs["energy"] and vigilance>=costs["vigilance"],
          "unfunded physical cognition")
    energy-=costs["energy"]
    vigilance-=costs["vigilance"]
    check(action in (None,"dormir",*MOTOR),
          "fabricated motor command or laboratory action")
    if action not in (None,"dormir"):
        check(energy>=MOTOR[action],"motor debited without physical energy")
    out=deepcopy(before)
    out["t"]+=1
    moved=False
    if action in (None,"dormir","boire","attendre"):
        check(param is None,"motor was given invalid parameter")
    food_gain=0.
    integrity_delta=0.
    water_gain=0.
    if action=="se_deplacer":
        check(param in DELTA,"not a valid self-chosen movement")
        dx,dy=DELTA[param]
        after=[out["position"][0]+dx,out["position"][1]+dy]
        check(0<=after[0]<3 and 0<=after[1]<3,"movement escaped native WorldSpec")
        out["position"]=after
        moved=True
    elif action=="collecter":
        c=out["food_cells"][0]
        check(c[0]==out["position"] and c[1]==param and c[2]>0,
              "collect without physically present food")
        c[2]-=1
        inv=dict(out["inventory"])
        inv[param]=inv.get(param,0)+1
        out["inventory"]=sorted([[k,v] for k,v in inv.items()])
    elif action=="manger":
        inv=dict(out["inventory"])
        check(type(param) is str and inv.get(param,0)>0 and
              param==out["food_cells"][0][1],
              "ate uncarried or nonphysical food")
        inv[param]-=1
        out["inventory"]=sorted([[k,v] for k,v in inv.items()])
        food_gain,integrity_delta=out["hidden_effects"][0][1]
    elif action=="boire":
        w=out["water_cells"][0]
        check(w[0]==out["position"] and w[2]>0,
              "drank nonexistent water or fabricated recharge")
        w[2]-=1
        water_gain=w[1]
    food=I.clamp(food-.2)
    water=I.clamp(water-.4)
    hydrated=water>=.05
    if action=="dormir":
        possible=min(3.,max(0.,100.-energy))
        gained=min(possible,food/.05) if hydrated else 0.
        energy+=gained
        food-=gained*.05
        vigilance+=4.
    elif action is not None:
        energy-=MOTOR[action]
    if action in ("dormir","attendre") and hydrated:
        repair=min(.2,max(0.,100.-integrity),food/.1)
        integrity+=repair
        food-=repair*.1
    if action=="manger":
        food+=food_gain
        integrity+=integrity_delta
    elif action=="boire":
        water+=water_gain
    b=list(map(I.clamp,(energy,food,water,integrity,vigilance)))
    dead=[tag for tag,i in (("zero_food",1),("zero_water",2),("zero_integrity",3))
          if b[i]<=0]
    out["body"]=b
    out["dead"]=dead
    return out,{"t":out["t"],"body":b,"dead":dead,"moved":moved}


def paid_learning(step,after_motor,post_decision_mind):
    post=step["postaction"]
    check(post["mind_before_outcome_observation"]==post_decision_mind
          and post["world_after_motor_body"]==after_motor["body"],
          "learning not attached to actual prior World.step")
    work=post["learn_work"]
    cost=I.cost(work)
    bill=post["actual_paid_learning_bill"]
    restored=deepcopy(after_motor)
    if bill is None:
        check(work=={"cycles":0,"simulated_steps":0,
                     "memory_items":0,"replays":0}
              and post["executed_replays"]==0
              and post["prepaid_replays"] is None
              and post["status"] in (
                 "DEAD_NO_LEARNING","NO_LAST_ACTION_NO_LEARNING",
                 "UNFUNDED_LEARNING"),
              "unpaid learning/replay was executed")
        check(post["learning_grant_remaining"]==after_motor["body"],
              "free learning token injected or body altered")
        if after_motor["dead"]:
            check(post["status"]=="DEAD_NO_LEARNING",
                  "postmortem memory update")
    else:
        check(not after_motor["dead"]
              and post["status"]=="PAID_LEARNED"
              and type(post["prepaid_replays"]) is int
              and post["prepaid_replays"]==post["executed_replays"]==work["replays"]
              and work["cycles"]>=2,
              "replay executed without actual prepaid native cognition")
        I.check_bill(bill,cost,"F1I own post-action learning")
        restored["body"][0]-=cost["energy"]
        restored["body"][4]-=cost["vigilance"]
        check(restored["body"][0]>=-1e-10 and restored["body"][4]>=-1e-10,
              "learning spent nonexistent energy or vigilance")
        body_eq(post["learning_grant_remaining"],restored["body"],
                "learning budget")
    check(post["world_after_any_learning"]["t"]==restored["t"]
          and post["world_after_any_learning"]["dead"]==restored["dead"]
          and post["world_after_any_learning"]["position"]==restored["position"]
          and post["world_after_any_learning"]["inventory"]==restored["inventory"]
          and post["world_after_any_learning"]["water_cells"]==restored["water_cells"]
          and post["world_after_any_learning"]["food_cells"]==restored["food_cells"]
          and post["world_after_any_learning"]["hidden_effects"]==restored["hidden_effects"],
          "pay cognition illegally reconfigured resources/death/position")
    body_eq(post["world_after_any_learning"]["body"],restored["body"],
            "genuine body after paid learning")
    body_eq(post["body_after_any_learning"],restored["body"],
            "learning debit recorded in body vector")
    check(post["learning_receipt_sha256"]==I.h({
        k:v for k,v in post.items() if k!="learning_receipt_sha256"}),
        "paid own-memory learning receipt SHA changed")
    check(I.private_fields(post["mind_after_any_learning"])
          and I.private_fields(post_decision_mind),
          "missing complete typed private memory at learning boundary")
    return post["world_after_any_learning"],post["mind_after_any_learning"]


def masked_content_ok(step,mode,t1,t4):
    before=I.private_fields(step["before_mind"])
    exposed=I.private_fields(step["exposed_mind_during_decision"])
    restored=I.private_fields(step["after_restoration_before_motor"])
    after_exposed=I.private_fields(step["after_decision_exposed_mind"])
    check(set(before)==set(exposed)==set(restored)==set(after_exposed),
          "partially serialized private Mind state")
    check(step["readout_mode"]==mode,
          "unexpected memory intervention name")
    early=I.observed_stats(t1)
    latest=I.observed_stats(t4)
    check(I.observed_stats(step["before_mind"])==latest,
          "fork does not start from own genuinely paid T4 effects")
    for field in before:
        if field!="effects":
            check(exposed[field]==before[field],
                  "mean mask touched innate genome, TD, buffer, map or RNG")
    check(I.observed_stats(step["after_restoration_before_motor"])==latest,
          "temporary readout not restored before native physics")
    if mode=="mask_owned_prior_means":
        keys=sorted(set(early)&set(latest),key=repr)
        check(step["temporary_prior_mean_keys"]==[list(k) for k in keys],
              "mask selected a favorable source key after exposure")
        seen=I.observed_stats(step["exposed_mind_during_decision"])
        check(set(seen)==set(latest),"invented or deleted learned memory key")
        for k in latest:
            target=early[k][1] if k in early else latest[k][1]
            check(seen[k][0]==latest[k][0] and seen[k][2]==latest[k][2]
                  and seen[k][1]==target,
                  "mask changed confidence/count or used fabricated first-person mean")
    else:
        check(step["temporary_prior_mean_keys"]==[]
              and I.observed_stats(step["exposed_mind_during_decision"])==latest,
              "control shams or full should read true personally learned means")
    check(I.observed_stats(step["after_decision_exposed_mind"])==
          I.observed_stats(step["exposed_mind_during_decision"]),
          "free learning was executed while mask installed")
    for fld in before:
        if fld not in ("effects","map","hist","visible","pos","tokens",
                       "external","acc","intention","last","rng","_budget_rng",
                       "_drift"):
            check(restored[fld]==before[fld],
                  "unmasked private learning or genotype changed during voluntary choice")


def verify_step(step,world,mind,case,*,mask_mode=None,t1=None,t4=None):
    check(step["t"]==world["t"]+1 and step["t"]<=END
          and step["before_world"]==world and
          step["before_mind"]==mind and
          step["no_experimental_action_override"] is True,
          "missing physical tick, forced action, bad memory continuity")
    check(step["capture"]==perceive(world)
          and step["capture_sha256"]==I.h(step["capture"]),
          "first-person agent saw hidden prior or fictitious cell")
    check(step["requested_native_cost"]==I.cost(step["cognitive_work"]),
          "wrong cognitive formula, possible unpaid work")
    bill=step["native_motor"]["cognitive_accounting"]
    I.check_bill(bill,I.cost(step["cognitive_work"]),"F1I true native World.step")
    funds=I.cost(step["cognitive_work"])
    expected_grant=list(world["body"])
    expected_grant[0]-=funds["energy"]
    expected_grant[4]-=funds["vigilance"]
    body_eq(step["decision_remaining"],expected_grant,"native work authorization")
    if mask_mode is not None:
        masked_content_ok(step,mask_mode,t1,t4)
    else:
        check(step["readout_mode"]=="full" and
              step["temporary_prior_mean_keys"]==[] and
              step["exposed_mind_during_decision"]==mind,
              "postfork motor had another forbidden memory mask")
    world_native,motor=physical(world,step["action"],step["param"],
                                step["cognitive_work"],bill,case)
    check(motor["t"]==step["native_motor"]["t"]
          and motor["dead"]==step["native_motor"]["dead"]
          and motor["moved"] is step["native_motor"]["moved"],
          "physical movement or death mismatch")
    body_eq(motor["body"],step["native_motor"]["body"],"actual food/drink/motor physiological consequence")
    check(step["after_motor_world"]==world_native,
          "native water/food stock/inventory/position differ")
    paid_world,paid_mind=paid_learning(
        step,world_native,step["after_restoration_before_motor"])
    check(step["after_paid_learning_world"]==paid_world
          and step["after_paid_learning_mind"]==paid_mind,
          "body/memory receipt after real postaction learning was altered")
    check(step["receipt_sha256"]==I.h({
        k:v for k,v in step.items() if k!="receipt_sha256"}),
        "broken per-tick custody hash")
    return paid_world,paid_mind


def metrics(steps,world,error):
    dec={"energy":0.,"vigilance":0.}
    learn={"energy":0.,"vigilance":0.}
    area=[0.]*5
    vmin=None
    drank=ate=collected=0
    for s in steps:
        for coin in COINS:
            dec[coin]+=s["native_motor"]["cognitive_accounting"][coin]["paid"]
            b=s["postaction"]["actual_paid_learning_bill"]
            if b is not None:
                learn[coin]+=b[coin]["paid"]
        ate+=int(s["action"]=="manger")
        drank+=int(s["action"]=="boire")
        collected+=int(s["action"]=="collecter")
        body=s["postaction"]["body_after_any_learning"]
        for i in range(5):
            area[i]+=body[i]
        vmin=min(vmin if vmin is not None else float("inf"),min(body[1:4]))
    return {
       "steps_t5_to_t30":len(steps),
       "alive_at_t30":bool(world["t"]==END and not world["dead"] and error is None),
       "final_tick":world["t"],"terminal_dead":world["dead"],
       "terminal_body":world["body"],"terminal_position":world["position"],
       "terminal_water_stock":[[v[0],v[2]] for v in world["water_cells"]],
       "terminal_food_quantity":[[v[0],v[2]] for v in world["food_cells"]],
       "terminal_inventory":world["inventory"],
       "cumulated_body_observed":area,"minimum_vital_reserve":vmin,
       "paid_decision":dec,"paid_learning":learn,
       "water_drinks":drank,"foods_collected":collected,"foods_actually_eaten":ate,
       "native_error":error
    }


def survival(a,b):
    if a["alive_at_t30"]!=b["alive_at_t30"]:
        return "FULL_SURVIVAL_ADVANTAGE" if a["alive_at_t30"] else "FULL_SURVIVAL_DISADVANTAGE"
    if a["steps_t5_to_t30"]!=b["steps_t5_to_t30"]:
        return "FULL_SURVIVAL_ADVANTAGE" if a["steps_t5_to_t30"]>b["steps_t5_to_t30"] else "FULL_SURVIVAL_DISADVANTAGE"
    return "NO_SURVIVAL_DIFFERENCE"


def pareto(a,b):
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


def sham_equal(full,sham):
    if (not full["steps"] or not sham["steps"] or
        len(full["steps"])!=len(sham["steps"]) or
        full["metrics"]!=sham["metrics"] or
        full["last_world"]!=sham["last_world"] or
        full["last_mind"]!=sham["last_mind"]):
        return False
    for a,b in zip(full["steps"],sham["steps"]):
        if a["t"]==FORK:
            for k in (
                "before_world","before_mind","capture","after_decision_exposed_mind",
                "after_restoration_before_motor","action","param","decision_info",
                "cognitive_work","decision_remaining","native_motor","after_motor_world",
                "postaction","after_paid_learning_mind","after_paid_learning_world"):
                if a[k]!=b[k]:
                    return False
        elif a!=b:
            return False
    return True


def gate_same_fork(full,other):
    if not full["steps"] or not other["steps"]:
        return False
    x,y=full["steps"][0],other["steps"][0]
    fields=("before_world","before_mind","capture","capture_sha256",
            "cognitive_work","decision_remaining","requested_native_cost")
    if any(x[f]!=y[f] for f in fields):
        return False
    if x["native_motor"]["cognitive_accounting"]!=y["native_motor"]["cognitive_accounting"]:
        return False
    if (x["action"],x["param"])==(y["action"],y["param"]):
        return x["native_motor"]==y["native_motor"]
    return True


def audit(report,grid):
    roots=validate_grid(grid)
    check(report.get("schema")==SCHEMA
          and report.get("source_main")==BASE
          and report.get("preexposure_grid_commit")==GRID_COMMIT
          and report.get("preexposure_protocol_commit")==PRE_COMMIT
          and report.get("personal_first_paid_tick")==1
          and report.get("acquisition_ticks")==T4
          and report.get("single_memory_readout_intervention_tick")==FORK
          and report.get("terminal_tick")==END
          and report.get("preregistered_origin_count")==16
          and report.get("preregistered_eco_names")==list(ECOLOGIES)
          and report.get("arms_per_origin")==list(MODES)
          and report.get("genome_shared_between_roots")=="midpoint()"
          and report.get("initial_personal_effects_TD_buffer_empty") is True
          and report.get("no_forced_actions") is True
          and report.get("real_world_token_effects_configured") is True
          and report.get("all_future_reads_unmodified_after_t5") is True
          and report.get("full_lives_or_run_life")==0
          and report.get("new_scientific_cohorts")==0
          and report.get("frozen_prior_studies")==FROZEN
          and type(report.get("rows")) is list and len(report["rows"])==16,
          "F1I source, science results, endpoints, horizon or population were rewritten")
    first_steps=following_steps=actual_eaten=actual_water=0
    valid_sources=valid_pairs=changed_count=wins=losses=0
    fav_ecologies=set()
    observations=[]
    for case,row in zip(roots,report["rows"]):
        check(row["origin"]==case and row["source"]["origin"]==case,
              "16 individual seeds or order selectively removed")
        source=row["source"]
        before=world_start(case)
        check(source["genesis"]["world"]==before and
              source["genesis"]["mind"]["data"]["class"]=="Mind" and
              I.observed_stats(source["genesis"]["mind"])=={},
              "created individuum with imported F1C/artificial personal knowledge")
        genesis=I.private_fields(source["genesis"]["mind"])
        check(genesis["buffer"]=={"__deque__":[],"maxlen":None}
              and all(all(v==0.0 for v in r) for r in genesis["values"]),
              "TD or buffer already contains learned lab memory at birth")
        mind=source["genesis"]["mind"]
        personal_t1=None
        for n,step in enumerate(source["source_steps"],1):
            check(n<=T4 and step["t"]==n,
                  "pre-fork lived episode illegally duplicated")
            before,mind=verify_step(step,before,mind,case)
            first_steps+=1
            if n==1:
                personal_t1=step["postaction"]["mind_after_any_learning"]
        check(source["source_tick4_world"]==before
              and source["source_tick4_mind"]==mind,
              "four source steps not retained in actual individual memory/body")
        personal_t4=mind
        if personal_t1 is None:
            check(source["paid_t1_mean_anchor"]==[],
                  "invented personal t1 effect")
        else:
            t1_stats=I.observed_stats(personal_t1)
            stored=[{"key":list(k),"stat":[v[0],v[1],v[2]]}
                    for k,v in sorted(t1_stats.items(),key=lambda x:repr(x[0]))]
            check(source["paid_t1_mean_anchor"]==stored,
                  "prior masked mean was not original personally paid tick1 observation")
        t4_stats=I.observed_stats(personal_t4)
        stored_late=[{"key":list(k),"stat":[v[0],v[1],v[2]]}
                     for k,v in sorted(t4_stats.items(),key=lambda x:repr(x[0]))]
        check(source["paid_t4_full_effects"]==stored_late,
              "learned means at t4 were posthoc refitted")
        source_valid=bool(
            len(source["source_steps"])==T4 and before["t"]==T4 and
            not before["dead"] and source["source_native_error"] is None and
            personal_t1 is not None and bool(I.observed_stats(personal_t1)) and
            source["source_steps"][0]["postaction"]["status"]=="PAID_LEARNED")
        check(source["source_valid_for_fork"] is source_valid
              and source["source_experiences_created_by_run_life"] is False
              and source["source_receipt_sha256"]==I.h({
                  k:v for k,v in source.items() if k!="source_receipt_sha256"}),
              "personal origin source state/pay gate was falsified")
        valid_sources+=int(source_valid)
        arms=row["arms"]
        if not source_valid:
            check(arms=={} and row["origin_valid"] is False
                  and row["motor_changed"] is None,
                  "skipped dead source and selected a favorable replacement")
            check(row["case_sha256"]==I.h({k:v for k,v in row.items() if k!="case_sha256"}),
                  "dead root receipt changed")
            observations.append({"id":case["id"],"source_valid":False})
            continue
        check(set(arms)==set(MODES),
              "one memory branch was selectively removed")
        for mode in MODES:
            t=arms[mode]
            current=deepcopy(before)
            private=personal_t4
            check(t["mode"]==mode and len(t["steps"])>=1
                  and t["steps"][0]["t"]==FORK,
                  "missing original fork or falsified arm")
            for ix,s in enumerate(t["steps"]):
                check(s["t"]==FORK+ix,"created hidden/missing tick")
                current,private=verify_step(
                    s,current,private,case,
                    mask_mode=mode if ix==0 else None,
                    t1=personal_t1 if ix==0 else None,
                    t4=personal_t4 if ix==0 else None
                )
                following_steps+=1
                actual_eaten+=int(s["action"]=="manger")
                actual_water+=int(s["action"]=="boire")
            check(current==t["last_world"] and private==t["last_mind"],
                  "physical or private Mind continuity lost")
            check(current["t"]==END or current["dead"] or
                  t["metrics"]["native_error"] is not None,
                  "individual retired before preregistered T30 without death/error")
            m=metrics(t["steps"],current,t["metrics"]["native_error"])
            check(t["metrics"]==m and
                  t["trajectory_sha256"]==I.h({
                      k:v for k,v in t.items() if k!="trajectory_sha256"}),
                  "native personal adaptive outcome rewritten")
        f,sham,mask=(arms[x] for x in MODES)
        equal=all(gate_same_fork(f,arms[x]) for x in MODES)
        neutral=sham_equal(f,sham)
        noerror=all(x["metrics"]["native_error"] is None for x in arms.values())
        eligible=equal and neutral and noerror
        motor=(f["steps"][0]["action"],f["steps"][0]["param"])!=(
                mask["steps"][0]["action"],mask["steps"][0]["param"])
        s=survival(f["metrics"],mask["metrics"]) if eligible else None
        d=pareto(f["metrics"],mask["metrics"]) if eligible else None
        check(row["fork_work_and_bills_equal"] is equal
              and row["sham_whole_trajectory_equal"] is neutral
              and row["origin_valid"] is eligible
              and row["motor_changed"] is (motor if eligible else None)
              and row["full_survival_advantage"]==s
              and row["terminal_five_channel_dominance"]==d
              and row["case_sha256"]==I.h({
                  k:v for k,v in row.items() if k!="case_sha256"}),
              "adaptive label or equal-cost evidence was relabelled after exposure")
        valid_pairs+=int(eligible)
        changed_count+=int(eligible and motor)
        if eligible and motor and s=="FULL_SURVIVAL_ADVANTAGE":
            wins+=1;fav_ecologies.add(case["ecology"])
        if eligible and motor and s=="FULL_SURVIVAL_DISADVANTAGE":
            losses+=1
        observations.append({
            "id":case["id"],"ecology":case["ecology"],
            "source_valid":source_valid,"valid":eligible,
            "fork_changed_motor":motor if eligible else None,
            "survival_comparison":s,"terminal_pareto":d,
            "full_terminal":f["metrics"]["terminal_body"],
            "masked_terminal":mask["metrics"]["terminal_body"],
            "full_survived":f["metrics"]["alive_at_t30"],
            "masked_survived":mask["metrics"]["alive_at_t30"],
            "full_food_eaten":f["metrics"]["foods_actually_eaten"],
            "masked_food_eaten":mask["metrics"]["foods_actually_eaten"],
            "full_water_drinks":f["metrics"]["water_drinks"],
            "masked_water_drinks":mask["metrics"]["water_drinks"],
            "full_postfork_ticks":f["metrics"]["steps_t5_to_t30"],
            "masked_postfork_ticks":mask["metrics"]["steps_t5_to_t30"],
        })
    all_sources=valid_sources==16
    costs=all(row["fork_work_and_bills_equal"] for row in report["rows"])
    shams=all(row["sham_whole_trajectory_equal"] for row in report["rows"])
    if not all_sources:
        verdict="INCONCLUSIVE_SOURCE_GATE"
    elif not costs:
        verdict="INCONCLUSIVE_COST_GATE"
    elif not shams:
        verdict="INVALID_SHAM"
    elif valid_pairs!=16:
        verdict="INCONCLUSIVE_NATIVE_OR_EVIDENCE_GATE"
    elif wins>=3 and len(fav_ecologies)>=2 and not losses:
        verdict="REPRODUCIBLE_LOCAL_T30_SURVIVAL_ADVANTAGE_OF_OWN_LEARNED_CONTENT"
    else:
        verdict="NO_REPRODUCIBLE_SURVIVAL_ADVANTAGE_T30"
    check(report["native_first_four_source_step_count"]==first_steps
          and report["native_followup_step_count"]==following_steps
          and report["valid_paid_personal_sources"]==valid_sources
          and report["valid_matched_prospective_origins"]==valid_pairs
          and report["motor_changed_origins"]==changed_count
          and report["survival_favorable_changed_origins"]==wins
          and report["survival_unfavorable_changed_origins"]==losses
          and report["favorable_ecology_count"]==len(fav_ecologies)
          and report["actual_native_food_ingestions_all_arms"]==actual_eaten
          and report["actual_native_water_drinks_all_arms"]==actual_water
          and report["strict_preexposed_primary_verdict"]==verdict,
          "F1I preregistered primary survival/motor or actual ingestion was falsely promoted")
    chain=I.h({"source_main":BASE,"grid_commit":GRID_COMMIT,
               "protocol_commit":PRE_COMMIT,
               "case_hashes":[row["case_sha256"] for row in report["rows"]]})
    check(chain==report["provenance_chain_sha256"],
          "cold original 16 personal roots SHA chain changed")
    return {
      "schema":"i3-stage8f1i-independent-cold-real-food-personal-T30/v0",
      "status":"COLD_F1I_16_FRESH_PAID_MINDS_NATIVE_RESOURCE_BODIES_REDUCED",
      "original_sha256":I.h(report),"preregistered_grid_commit":GRID_COMMIT,
      "preexposure_protocol_commit":PRE_COMMIT,
      "native_personal_origin_step_count":first_steps,
      "native_after_fork_steps_reduced":following_steps,
      "valid_paid_personal_origins":valid_sources,
      "valid_equal_cost_prospective_origins":valid_pairs,
      "changed_motor_origins":changed_count,
      "favorable_survival_with_changed_motor":wins,
      "unfavorable_survival_with_changed_motor":losses,
      "favorable_ecologies":len(fav_ecologies),
      "native_food_ingestions_verified":actual_eaten,
      "native_water_drinks_verified":actual_water,
      "primary_verdict":verdict,
      "root_provenance_sha256":chain,
      "no_original_F1F_F1G_F1H_verdict_rewritten":True,
      "living_individual_decisions_unauthorized_to_be_forced":"NATIVE_RECEIPTS_AND_SOURCE_REVIEW",
      "no_untested_scientific_cohorts":True,
      "per_origin":observations,
    }


def main():
    p=argparse.ArgumentParser(description="Engine-free real native consumption/payments T30 independent auditor")
    p.add_argument("source_f1i")
    p.add_argument("grid_preexposure")
    p.add_argument("cold_output")
    a=p.parse_args()
    original_bytes=Path(a.source_f1i).read_bytes()
    grid=json.loads(Path(a.grid_preexposure).read_bytes())
    report=audit(json.loads(original_bytes),grid)
    check(report["original_sha256"]==sha256(original_bytes).hexdigest(),
          "F1I original bytes noncanonical or changed")
    with Path(a.cold_output).open("xb") as fd:
        fd.write(I.c(report))
    print(json.dumps({
       "status":report["status"],"verdict":report["primary_verdict"],
       "valid_origins":report["valid_equal_cost_prospective_origins"],
       "changed_motor":report["changed_motor_origins"],
       "survival_favorable":report["favorable_survival_with_changed_motor"],
       "survival_unfavorable":report["unfavorable_survival_with_changed_motor"],
       "true_food_ingestions":report["native_food_ingestions_verified"],
       "true_water_drinks":report["native_water_drinks_verified"],
       "native_steps":report["native_personal_origin_step_count"]+report["native_after_fork_steps_reduced"],
       "sha256":I.h(report),
    },sort_keys=True))


if __name__=="__main__":
    main()
