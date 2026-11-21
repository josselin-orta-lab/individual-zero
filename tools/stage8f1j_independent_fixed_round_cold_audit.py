"""Cold stdlib-only F1J auditor, independent of substantive fixed-round producer.

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

SCHEMA="i3-stage8f1j-fixed-substantive-rounds-equal-paid-16-origins/v0"
BASE="3745952a6c8635072828cdfbe3686229eebe50ba"
GRID_COMMIT="8f82eea7a8b08e086010dfe497099212fb35508f"
PRE_COMMIT="b90d6eb13459ddfda4f63c0828f4e39f135a376e"
T4=4
FORK=5
END=30
MODES=("full","sham","mask_owned_t1_means")
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
    I.check(test,"COLD F1J: "+msg)


def body_eq(a,b,what):
    I.body_equal(a,b,"COLD F1J "+what)


def private_fields(sealed):
    """Parse complete F1I BASE Mind, never the older PaidMicrodecisionMind."""
    check(type(sealed) is dict and set(sealed)=={"data","sha256"}
          and I.h(sealed["data"])==sealed["sha256"],
          "noncanonical or tampered full personal Mind checksum")
    rec=sealed["data"]
    check(type(rec) is dict and rec.get("class")=="F1JFixedRoundMind"
          and type(rec.get("private")) is dict
          and set(rec["private"])=={"__dict__"},
          "fresh reference Mind was replaced with a paid micro-candidate")
    pairs=rec["private"]["__dict__"]
    check(type(pairs) is list and
          all(type(row) is list and len(row)==2 and type(row[0]) is str
              for row in pairs),
          "typed private individual fields have invalid serialization")
    fields=dict(pairs)
    check(len(fields)==len(pairs) and
          {"effects","values","buffer","rng","_budget_rng","last",
           "intention","theta","p","w","gammas","map","hist"} <= set(fields),
          "incomplete private brain or forged paid memory")
    return fields


def observed_stats(sealed):
    fields=private_fields(sealed)
    effects=fields["effects"]
    check(type(effects) is dict and set(effects)=={"__effects_model__"},
          "memory effects were artificially injected")
    em=dict(effects["__effects_model__"]["__dict__"])
    check(set(em)=={"stats"},"invented EffectsModel properties")
    pairs=em["stats"]["__dict__"]
    data={}
    for key,row in pairs:
        check(type(key) is dict and set(key)=={"__tuple__"}
              and type(key["__tuple__"]) is list
              and type(row) is list and len(row)==3
              and type(row[1]) is list and len(row[1])==5,
              "invalid typed personally acquired EffectsModel mean/row")
        label=tuple(key["__tuple__"])
        check(label not in data and
              type(row[0]) in (int,float) and type(row[2]) is int,
              "duplicate or forged personal effect count")
        data[label]=row
    return data


def expected_cases():
    modes=[]
    roots=[]
    for i,(name,attributes) in enumerate(ECOLOGIES.items()):
        water,wgain,food,token,fgain,delta,base=attributes
        modes.append({
            "id":name,"water":list(water),"water_gain":wgain,
            "food":list(food),"token":token,
            "food_gain":fgain,"integrity_delta":delta,
            "water_stock":2,"food_stock":2,"restock_every":0,
        })
        for j in range(4):
            roots.append({
                "id":"J"+str(i*4+j+1).zfill(2),
                "ecology":name,"seed":202611219001+i*4+j,
                "body":[round(x+shift*(j+1),3) for x,shift
                        in zip(base,(1.1,-.45,.25,-.35,-.35))],
            })
    return modes,roots


def validate_grid(grid):
    modes,roots=expected_cases()
    check(
        type(grid) is dict
        and grid.get("schema")=="i3-stage8f1j-frozen-independent-fixed-round-v0"
        and grid.get("baseline_main")==BASE
        and grid.get("mind")=="F1JFixedRoundMind(Mind)"
        and grid.get("original_F1I_data_untouched") is True
        and grid.get("same_genome_for_all")=="midpoint()"
        and grid.get("world_width")==3 and grid.get("world_height")==3
        and grid.get("spawn")==[1,1]
        and grid.get("origin_steps")==4
        and grid.get("first_person_paid_prior_at_tick")==1
        and grid.get("fork_tick")==FORK
        and grid.get("terminal_tick")==END
        and grid.get("no_run_life") is True
        and grid.get("arms")==list(MODES)
        and grid.get("full_families")==modes
        and grid.get("origins")==roots
        and grid.get("fixed_rounds",{}).get("no_engine_patch") is True
        and grid.get("fixed_rounds",{}).get("no_padding")==
            "no synthetic equalization: every charged round must integrate all option evidence; never charge a work cycle merely for parity",
        "preexposed F1J universe, seeds or computation rule changed"
    )
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
    check(private_fields(post["mind_after_any_learning"])
          and private_fields(post_decision_mind),
          "missing complete typed private memory at learning boundary")
    return post["world_after_any_learning"],post["mind_after_any_learning"]


def masked_content_ok(step,mode,t1,t4):
    before=private_fields(step["before_mind"])
    exposed=private_fields(step["exposed_mind_during_decision"])
    restored=private_fields(step["after_restoration_before_motor"])
    after_exposed=private_fields(step["after_decision_exposed_mind"])
    check(set(before)==set(exposed)==set(restored)==set(after_exposed),
          "partially serialized private Mind state")
    check(step["readout_mode"]==mode,
          "unexpected memory intervention name")
    early=observed_stats(t1)
    latest=observed_stats(t4)
    check(observed_stats(step["before_mind"])==latest,
          "fork does not start from own genuinely paid T4 effects")
    for field in before:
        if field!="effects":
            check(exposed[field]==before[field],
                  "mean mask touched innate genome, TD, buffer, map or RNG")
    check(observed_stats(step["after_restoration_before_motor"])==latest,
          "temporary readout not restored before native physics")
    if mode=="mask_owned_prior_means":
        keys=sorted(set(early)&set(latest),key=repr)
        check(step["temporary_prior_mean_keys"]==[list(k) for k in keys],
              "mask selected a favorable source key after exposure")
        seen=observed_stats(step["exposed_mind_during_decision"])
        check(set(seen)==set(latest),"invented or deleted learned memory key")
        for k in latest:
            target=early[k][1] if k in early else latest[k][1]
            check(seen[k][0]==latest[k][0] and seen[k][2]==latest[k][2]
                  and seen[k][1]==target,
                  "mask changed confidence/count or used fabricated first-person mean")
    else:
        check(step["temporary_prior_mean_keys"]==[]
              and observed_stats(step["exposed_mind_during_decision"])==latest,
              "control shams or full should read true personally learned means")
    check(observed_stats(step["after_decision_exposed_mind"])==
          observed_stats(step["exposed_mind_during_decision"]),
          "free learning was executed while mask installed")
    # Mind.decide LEGITIMATELY changes its own map, accumulator, RNG,
    # planning and temporary decision state. Restore must preserve those
    # genuine decision results, while restoring ONLY learned effects.
    check(restored["effects"]==before["effects"]
          and after_exposed["effects"]==exposed["effects"],
          "owned learned effect model was not purely read-masked and restored")
    for fld in before:
        if fld!="effects":
            check(restored[fld]==after_exposed[fld],
                  "laboratory overwrote the genuinely chosen Mind state")
    for fld in ("values","buffer","theta","p","w","gammas"):
        check(restored[fld]==before[fld],
              "TD, episodic memory or innate genome altered at readout")


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


def _typed_mapping(record):
    check(type(record) is dict and set(record)=={"__dict__"},
          "invalid typed accumulator mapping")
    x=dict(record["__dict__"])
    check(len(x)==len(record["__dict__"]),"duplicated accumulator key")
    return x


def cold_paid_fixed_competition(step):
    """Independently reconstruct every ACTUALLY PAID evidence round and choice.

    A flat line of fabricated budget-burn rounds fails this check. No imports
    of new Mind implementation, body law, or experiment producer.
    """
    from math import sqrt,tanh,isclose
    info=step["decision_info"]
    if info["funding"]!="FUNDED":
        # Genuine no-funded-score or no-motor remains a native action outcome;
        # do not pretend an unobserved round was computed.
        return {"funding":info["funding"],"audited_rounds":0}
    observed=info["observer"]["competition_witness"]
    scored=info["observer"]["score_witness"]
    prior=private_fields(step["before_mind"])
    body=step["before_world"]["body"]
    n_base=prior["n_base"]
    capacity=max(1,int(round(n_base*min(1.,body[0]/50.))))
    check(observed["round_capacity_from_actual_body"]==capacity,
          "fixed rounds weren't determined by actual bodily capacities")
    options=observed["scored_order"]
    vals=[z["total_score"] for z in scored]
    check(len(options)==len(vals)==len(set(options)) and
          [z["option"] for z in scored]==options,
          "observer did not witness ALL paid scored options")
    mean=sum(vals)/len(vals)
    sd=sqrt(sum((v-mean)**2 for v in vals)/len(vals))
    predicted={o:(tanh((v-mean)/sd) if sd>1e-9 else 0.0)
               for o,v in zip(options,vals)}
    evidence=observed["normalized_evidence"]
    check(set(evidence)==set(options)
          and all(isclose(evidence[o],predicted[o],rel_tol=0,abs_tol=1e-11)
                  for o in options),
          "fake evidence score or inaccurate source scoring")
    first=observed["accumulators_before"]
    all_seen=_typed_mapping(prior["acc"])
    check(set(first)==set(options)
          and all(isclose(first[o],all_seen.get(o,0.),abs_tol=1e-11)
                  for o in options),
          "evidence came from invented previous accumulator")
    check(observed["prior_intention"]==prior["intention"],
          "internal personal inertia before competition changed")
    thresholds=observed["thresholds"]
    check(set(thresholds)==set(options)
          and all(isclose(thresholds[o],
                1.5*(1.-prior["inertia"] if o==prior["intention"] else 1.),
                abs_tol=1e-11) for o in options),
          "threshold or innate intention unfairly modified")
    used=observed["paid_competition_cycles"]
    trace=observed["actual_substantive_round_snapshots"]
    check(type(used) is int and 0<=used<=capacity
          and len(trace)==used
          and observed["budget_blocked_before_full_round_capacity"] is (used<capacity)
          and info["cycles"]==used
          and step["cognitive_work"]["cycles"]==3+used,
          "unpaid rounds, fake cycles or inflated competition debit")
    acc=dict(first)
    for record in trace:
        for o in options:
            acc[o]=max(0.0,.8*acc[o]+predicted[o])
        check(set(record)==set(options)
              and all(isclose(record[o],acc[o],abs_tol=1e-11)
                      for o in options),
              "fabricated no-op cognition: paid evidence round didn't integrate every option")
    check(set(observed["accumulators_before_residual"])==set(options)
          and all(isclose(observed["accumulators_before_residual"][o],acc[o],abs_tol=1e-11)
                  for o in options),
          "final evidential state is not the paid real integration")
    crossed=[((acc[o]-thresholds[o])/thresholds[o],o)
             for o in options if acc[o]>=thresholds[o]]
    if crossed:
        best=max(v for v,_ in crossed)
        tied=sorted(o for v,o in crossed if v==best)
        selection="final_round_threshold"
    else:
        maxacc=max(acc.values())
        tied=sorted(o for o,v in acc.items() if v>=maxacc-1e-12)
        if len(tied)==len(options) and max(acc.values())-min(acc.values())<=1e-12:
            ms=max(vals)
            tied=sorted(o for o,v in zip(options,vals) if v>=ms-1e-12)
            selection="all_activations_equal_raw_score_fallback"
        else:
            selection="final_round_activation"
    winner=observed["winner_before_control"]
    check(observed["selection_mechanism"]==selection
          and observed["tie_candidates"]==tied and winner in tied,
          "winner selected by laboratory rather than native competition")
    reduced={o:(0.0 if o==winner else acc[o]*.5) for o in options}
    check(set(observed["accumulators_after_residual"])==set(options)
          and all(isclose(observed["accumulators_after_residual"][o],reduced[o],abs_tol=1e-11)
                  for o in options),
          "substantive rounds weren't retained as original Mind residual")
    actual_acc=_typed_mapping(
        private_fields(step["after_restoration_before_motor"])["acc"])
    check(set(actual_acc)==set(reduced)
          and all(isclose(actual_acc[o],reduced[o],abs_tol=1e-11)
                  for o in reduced),
          "real Mind.acc differs from retrospectively claimed paid rounds")
    check(observed["final_admitted_option"]==info["option"],
          "selected action not tied to native ActionControl")
    return {"funding":"FUNDED","audited_rounds":used,
            "options_integrated_per_round":len(options),"final_winner":winner}


def audit(report,grid):
    roots=validate_grid(grid)
    previous={
        "f1i":"INCONCLUSIVE_COST_GATE",
        "f1i_unmatched_origins":["R07","R08","R10","R11"],
        "f1i_original_sha256":"e9daebdabb3b69671ecaa39c9fb48a0cc60d92d8518d42c7df1ad32ad5346f2a",
        "f1f":"MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES",
        "f1g_td":"NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
        "f1g_buffer":"NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
        "f1h":"NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12",
        "stage8e2":"STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY",
    }
    check(
        type(report) is dict
        and report.get("schema")==SCHEMA
        and report.get("reference_main_before_preexposure")==BASE
        and report.get("preexposed_grid_commit")==GRID_COMMIT
        and report.get("preexposed_protocol_commit")==PRE_COMMIT
        and report.get("study")=="F1J_FIXED_ROUND_NATIVE_PAID_COMPETITION_NEW_16_ROOTS"
        and report.get("experimental_policy")=="F1JFixedRoundMind"
        and report.get("reference_Mind_unchanged") is True
        and report.get("fixed_rounds_all_substantive_no_cost_padding") is True
        and report.get("self_chosen_native_actions_no_motor_override") is True
        and report.get("source_independent_fresh_minds") is True
        and report.get("real_food_token_effects") is True
        and report.get("preregistered_root_count")==16
        and report.get("preregistered_ecologies")==list(ECOLOGIES)
        and report.get("preregistered_root_ids")==[r["id"] for r in roots]
        and report.get("full_native_lives_run_life")==0
        and report.get("new_scientific_cohorts")==0
        and report.get("t1_personal_paid_anchor")==1
        and report.get("personal_acquisition_ticks")==4
        and report.get("one_time_readout_mask_tick")==FORK
        and report.get("terminal_tick")==END
        and report.get("sham_required_for_entire_trajectory") is True
        and report.get("no_postfork_memory_interventions") is True
        and report.get("frozen_prior_results")==previous
        and type(report.get("rows")) is list
        and len(report["rows"])==16,
        "preexposure, original F1I, funding or scientific classification changed"
    )
    personal=followup=meals=drinks=audited_rounds=0
    sources=equal_pairs=neutral_pairs=valid_pairs=changed=0
    full_wins=masked_wins=0
    rows_out=[]
    for root,row in zip(roots,report["rows"]):
        check(row["origin"]==root and row["source"]["origin"]==root,
              "root added/removed after success observed")
        source=row["source"]
        current=world_start(root)
        genesis=source["genesis"]
        check(genesis["world"]==current and
              genesis["mind"]["data"]["class"]=="F1JFixedRoundMind"
              and observed_stats(genesis["mind"])=={},
              "new Mind was preloaded with someone else's memories")
        private=private_fields(genesis["mind"])
        check(private["buffer"]=={"__deque__":[],"maxlen":None}
              and all(all(value==0.0 for value in row)
                      for row in private["values"]),
              "new Mind had artificially learned TD values/buffer")
        mind=genesis["mind"]
        t1=None
        for i,step in enumerate(source["source_steps"],1):
            check(i<=4 and step["t"]==i,
                  "personal natural source steps changed or duplicated")
            current,mind=verify_step(step,current,mind,root)
            info=cold_paid_fixed_competition(step)
            audited_rounds+=info["audited_rounds"]
            personal+=1
            if i==1:
                t1=step["postaction"]["mind_after_any_learning"]
        check(current==source["source_tick4_world"] and
              mind==source["source_tick4_mind"],
              "real own source memory did not persist")
        t4=mind
        if t1 is not None:
            p=observed_stats(t1)
            old=[{"key":list(k),"stat":deepcopy(v)}
                 for k,v in sorted(p.items(),key=lambda x:repr(x[0]))]
        else:
            old=[]
        latest=observed_stats(t4)
        stored=[{"key":list(k),"stat":deepcopy(v)}
                for k,v in sorted(latest.items(),key=lambda x:repr(x[0]))]
        check(source["paid_t1_mean_anchor"]==old
              and source["paid_t4_full_effects"]==stored,
              "old/suppressed personal means are invented or selected from later rewards")
        source_valid=(len(source["source_steps"])==4 and current["t"]==4
                      and not current["dead"] and
                      source["source_native_error"] is None
                      and t1 is not None and bool(observed_stats(t1))
                      and source["source_steps"][0]["postaction"]["status"]=="PAID_LEARNED")
        check(source["source_valid_for_fork"] is source_valid
              and source["source_experiences_created_by_run_life"] is False
              and source["source_receipt_sha256"]==I.h({
                 k:v for k,v in source.items() if k!="source_receipt_sha256"
              }), "source selection or posthoc paid source rehash")
        sources+=int(source_valid)
        arms=row["arms"]
        if not source_valid:
            check(arms=={} and row["origin_valid"] is False
                  and row["motor_changed"] is None,
                  "nonviable personal origin was substituted")
            check(row["case_sha256"]==I.h({
                k:v for k,v in row.items() if k!="case_sha256"
            }),"bad origin source receipt")
            rows_out.append({"id":root["id"],"source_valid":False})
            continue
        check(set(arms)==set(MODES),
              "F1J was missing a predefined full, sham or masked arm")
        for mode in MODES:
            arm=arms[mode]
            check(arm["mode"]==mode and arm["steps"]
                  and arm["steps"][0]["t"]==5,
                  "F1J wrong true motor branch")
            world=deepcopy(current)
            memory=t4
            for index,step in enumerate(arm["steps"]):
                check(step["t"]==5+index,
                      "hidden or extra native World step beyond preregistration")
                # The F1I native step helper labels the public J readout
                # "mask_owned_t1_means" as its internal identical semantics
                # "mask_owned_prior_means". No different masking is permitted.
                effective_mode=("mask_owned_prior_means"
                    if mode=="mask_owned_t1_means" else mode)
                world,memory=verify_step(
                    step,world,memory,root,
                    mask_mode=effective_mode if index==0 else None,
                    t1=t1 if index==0 else None,
                    t4=t4 if index==0 else None,
                )
                info=cold_paid_fixed_competition(step)
                audited_rounds+=info["audited_rounds"]
                followup+=1
                meals+=int(step["action"]=="manger")
                drinks+=int(step["action"]=="boire")
            check(arm["last_world"]==world
                  and arm["last_mind"]==memory
                  and (world["t"]==END or world["dead"]
                       or arm["metrics"]["native_error"] is not None),
                  "F1J ended early or erased the real end-state")
            check(metrics(arm["steps"],world,arm["metrics"]["native_error"])
                  ==arm["metrics"],
                  "F1J falsely scored physiological adaptive body")
            check(arm["trajectory_sha256"]==I.h({
                k:v for k,v in arm.items() if k!="trajectory_sha256"
            }),"F1J charged proof rewritten")
        full,sham,mask=(arms[m] for m in MODES)
        eq=all(gate_same_fork(full,arms[m]) for m in MODES)
        neutral=sham_equal(full,sham)
        errors=any(a["metrics"]["native_error"] is not None
                   for a in arms.values())
        valid=eq and neutral and not errors
        motor=(
            [full["steps"][0][k] for k in ("action","param")]!=
            [mask["steps"][0][k] for k in ("action","param")]
        )
        sur=survival(full["metrics"],mask["metrics"]) if valid else None
        dominance=pareto(full["metrics"],mask["metrics"]) if valid else None
        check(row["equal_full_native_work_and_paid_both_coins"] is eq
              and row["whole_trajectory_sham_neutral"] is neutral
              and row["origin_valid"] is valid
              and row["motor_changed"] is (motor if valid else None)
              and row["survival_comparison"]==sur
              and row["terminal_pareto"]==dominance
              and row["case_sha256"]==I.h({
                 k:v for k,v in row.items() if k!="case_sha256"
              }), "postexposure cost-matching or consequence recoded")
        equal_pairs+=int(eq)
        neutral_pairs+=int(neutral)
        valid_pairs+=int(valid)
        changed+=int(valid and motor)
        full_wins+=int(valid and sur=="FULL_SURVIVAL_ADVANTAGE")
        masked_wins+=int(valid and sur=="FULL_SURVIVAL_DISADVANTAGE")
        rows_out.append({
          "id":root["id"],"ecology":root["ecology"],
          "source_valid":source_valid,"fork_cost_equal":eq,
          "whole_sham_equal":neutral,"native_valid":valid,
          "changed_motor":motor if valid else None,
          "full_t5_work":full["steps"][0]["cognitive_work"],
          "masked_t5_work":mask["steps"][0]["cognitive_work"],
          "full_t5_paid":full["steps"][0]["native_motor"]["cognitive_accounting"],
          "masked_t5_paid":mask["steps"][0]["native_motor"]["cognitive_accounting"],
          "full_survives_t30":full["metrics"]["alive_at_t30"],
          "masked_survives_t30":mask["metrics"]["alive_at_t30"],
          "full_terminal":full["metrics"]["terminal_body"],
          "masked_terminal":mask["metrics"]["terminal_body"],
          "survival":sur,"pareto":dominance,
        })
    if sources!=16:
        verdict="INCONCLUSIVE_UNFUNDED_OR_SOURCE_GATE"
    elif neutral_pairs!=16:
        verdict="INVALID_SHAM"
    elif valid_pairs<equal_pairs:
        verdict="INVALID_NATIVE_AUDIT"
    elif equal_pairs!=16:
        verdict="NO_FIXED_ROUND_COST_PARITY_DEMONSTRATED"
    else:
        verdict="FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL"
    check(report["source_valid_roots"]==sources
          and report["matched_all_native_work_four_fields_and_paid_energy_vigilance_roots"]==equal_pairs
          and report["sham_neutral_roots"]==neutral_pairs
          and report["valid_prospective_roots"]==valid_pairs
          and report["motor_changed_equal_cost_roots"]==changed
          and report["full_survival_advantage_equal_cost_roots"]==full_wins
          and report["mask_survival_advantage_equal_cost_roots"]==masked_wins
          and report["real_source_native_steps"]==personal
          and report["real_followup_native_steps"]==followup
          and report["real_meals_per_all_branches"]==meals
          and report["real_drinks_per_all_branches"]==drinks
          and report["strict_preexposed_primary_verdict"]==verdict,
          "F1J preregistered parity outcome / actual native work was promoted")
    chain=I.h({
        "main":BASE,"grid_commit":GRID_COMMIT,
        "protocol_commit":PRE_COMMIT,
        "case_receipts":[r["case_sha256"] for r in report["rows"]],
    })
    check(report["provenance_sha256"]==chain,"F1J 16 roots immutable custody hashes wrong")
    return {
        "schema":"i3-stage8f1j-stdlib-engine-free-substantive-real-cost-cold/v0",
        "status":"F1J_COLD_16_REAL_NATIVE_FUNDING_AND_SUBSTANTIVE_EVIDENCE_REDUCED",
        "original_source_sha256":I.h(report),
        "grid_before_first_exposure":GRID_COMMIT,
        "hypothesis_before_first_exposure":PRE_COMMIT,
        "native_personal_source_steps":personal,
        "native_prospective_followup_steps":followup,
        "actual_substantive_competition_rounds_reduced":audited_rounds,
        "all_original_personal_sources":sources,
        "strict_t5_full_work_and_two_coins_matched":equal_pairs,
        "shams_full_trajectory_neutral":neutral_pairs,
        "valid_personal_root_comparisons":valid_pairs,
        "memory_changed_motor_at_equal_cost":changed,
        "survival_favorable_descriptive_roots":full_wins,
        "survival_unfavorable_descriptive_roots":masked_wins,
        "native_food_ingestions_verified":meals,
        "native_water_drinks_verified":drinks,
        "strict_primary_parity_verdict":verdict,
        "frozen_F1I_status":"INCONCLUSIVE_COST_GATE",
        "no_historical_cohorts_or_modified_F1I":True,
        "native_physiology_and_paid_learning_verified":True,
        "individual_actions_and_evidence_accumulators_checked":True,
        "per_origin":rows_out,
        "provenance_sha256":chain,
    }


def main():
    ap=argparse.ArgumentParser(description="stdlib-only F1J cold native fixed rounds and real body funding audit")
    ap.add_argument("original")
    ap.add_argument("frozen_grid")
    ap.add_argument("cold_output")
    args=ap.parse_args()
    b=Path(args.original).read_bytes()
    data=json.loads(b)
    grid=json.loads(Path(args.frozen_grid).read_bytes())
    report=audit(data,grid)
    check(report["original_source_sha256"]==sha256(b).hexdigest(),
          "F1J original JSON bytes had noncanonical or falsified checksum")
    with Path(args.cold_output).open("xb") as f:
        f.write(I.c(report))
    print(json.dumps({
        "status":report["status"],"verdict":report["strict_primary_parity_verdict"],
        "source_roots":report["all_original_personal_sources"],
        "equal_work_and_energy_vigilance":report["strict_t5_full_work_and_two_coins_matched"],
        "motor_effects_at_equal_cost":report["memory_changed_motor_at_equal_cost"],
        "body_steps":report["native_personal_source_steps"]+report["native_prospective_followup_steps"],
        "checked_substantive_competition_rounds":report["actual_substantive_competition_rounds_reduced"],
        "true_meals":report["native_food_ingestions_verified"],
        "true_drinks":report["native_water_drinks_verified"],
        "sha256":I.h(report),
    },sort_keys=True))


if __name__=="__main__":
    main()
