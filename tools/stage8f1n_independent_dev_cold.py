"""F1N DEV_N: independent Python-stdlib cold audit of native T1..T60 originals.

NEVER imports i3, Mind, World, the F1N producer or its decision subclass.
Verifies 7 separately hash-stamped gzip parts per DEV_N root, the exact paid
T5 own-memory write and genuinely paid T6 margin/masked read, every substantive
F1J accumulation round, original physics, personal learning, shams and survival.
This is a SOFTWARE-ONLY rehearsed contract, never a scientific F1N verdict.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from math import isclose,sqrt,tanh
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1j_independent_fixed_round_cold_audit as J
from tools import stage8f1k_independent_policy_value_cold_audit as K
from tools import stage8f1n_prereg_static_guard as N

SCHEMA="i3-stage8f1n-dev-owned-margin-native-T60/v0"
PART_SCHEMA="i3-stage8f1n-native-incremental-receipt/v0"
PHASE="DEV_ONLY_NEVER_F1N_SCIENTIFIC"
PARTS=("source_t1_t4","self_paid_t5","self_paid_t5_sham",
       "margin_t6_t60","margin_t6_t60_sham",
       "masked_t6_t60","masked_t6_t60_sham")
DEV_A_SEEDS=tuple(range(202611269101,202611269109))
DEV_B_SEEDS=tuple(range(202611269121,202611269129))


def check(cond,why):
    if not cond:
        raise AssertionError("F1N COLD DEV: "+why)


def close(a,b):
    return isclose(a,b,rel_tol=0,abs_tol=1e-10)


def digest(raw):
    return sha256(raw).hexdigest()


def cold_grid(cohort,full):
    check(cohort in ("A","B") and type(full) is bool,"invalid DEV cohort")
    ec=[
        {"id":"DEV_N_spring_south", "water":[0,2], "water_gain":19,
         "water_stock":3, "water_max_stock":3, "water_restock_every":6,
         "food":[2,0], "token":"dev-n-tuber", "food_gain":22,
         "integrity_delta":0.8, "food_quantity":3,
         "food_max_quantity":3, "food_restock_every":5},
        {"id":"DEV_N_bitter_pond", "water":[2,2], "water_gain":23,
         "water_stock":2, "water_max_stock":2, "water_restock_every":5,
         "food":[0,0], "token":"dev-n-bitter", "food_gain":26,
         "integrity_delta":-0.8, "food_quantity":2,
         "food_max_quantity":2, "food_restock_every":6},
    ]
    seeds=DEV_A_SEEDS if cohort=="A" else DEV_B_SEEDS
    origins=[]
    for i,seed in enumerate(seeds):
        j=i%4
        origins.append({"id":f"DEV_N{cohort}{i+1:02d}",
                        "ecology":ec[i//4]["id"],"seed":seed,
                        "body":[66+j,72-j,42+.4*j,92-.3*j,94-.2*j]})
    if not full:
        origins=[origins[0],origins[4]]
    return {"schema":"i3-stage8f1n-dev-grid/v0","phase":PHASE,
            "cohort":cohort,"origin_count":len(origins),
            "world":{"width":3,"height":3,"spawn":[1,1],
                     "laws":"BodyLaws() i3-body-laws-v2","changes":[]},
            "ecologies":ec,"origins":origins,"final_tick":60,
            "source_ticks":4,"t5_tick":5,"t6_margin_fork":6,
            "arms":["margin","masked"]}


def origin_world(grid,origin):
    world=K.origin_world(grid,origin)
    world["world_spec"]["name"]="F1N_DEV_ORIGIN_"+origin["id"]+"_"+origin["ecology"]
    return world


def fields(sealed):
    check(type(sealed) is dict and set(sealed)=={"data","sha256"}
          and sealed["sha256"]==I.h(sealed["data"]),"sealed Mind SHA wrong")
    raw=sealed["data"]
    check(raw.get("class")=="F1NMarginMind"
          and set(raw.get("private",{}))=={"__dict__"},
          "F1N native subclass secretly replaced")
    entries=raw["private"]["__dict__"]
    check(type(entries) is list and all(type(v) is list and
          len(v)==2 and type(v[0]) is str for v in entries),
          "untyped F1N brain private fields")
    result=dict(entries)
    check(len(result)==len(entries) and
          {"effects","values","buffer","acc","rng","_budget_rng",
           "last","intention","inertia","n_base","f1n_owned_margin",
           "f1n_pending_margin","f1n_mode","f1n_read_used"}<=set(result),
          "fictitious F1N personal memory fields")
    return result


def typed_map(obj):
    check(type(obj) is dict and set(obj)=={"__dict__"},"typed map invalid")
    pairs=obj["__dict__"]
    v=dict(pairs)
    check(len(v)==len(pairs),"duplicate typed map key")
    return v


def map_val(v):
    return None if v is None else typed_map(v)


def _normalized_seal(seal):
    # One detached, O(1) structural operation; never recurse into enormous
    # private brain dictionaries. Its original SHA was already authenticated.
    res=deepcopy(seal)
    if res["data"]["class"] == "F1NMarginMind":
        res["data"]["class"] = "F1JFixedRoundMind"
        res["sha256"] = I.h(res["data"])
    return res


def _normalize(obj):
    """Detached exact F1N-to-F1J class normalization for generic cold helpers.

    The F1N-only threshold logic and funding are separately independently
    audited on the UNMODIFIED signed witness by _actual_t6_competition.
    No native engine modules are imported or executed.
    """
    if type(obj) is dict and set(obj)=={"data","sha256"}:
        return _normalized_seal(obj)
    step=deepcopy(obj)
    for key in ("before_mind","exposed_mind_during_decision",
                "after_decision_exposed_mind","after_restoration_before_motor",
                "after_paid_learning_mind"):
        step[key]=_normalized_seal(step[key])
    po=step["postaction"]
    for key in ("mind_before_outcome_observation","mind_after_any_learning"):
        po[key]=_normalized_seal(po[key])
    po["learning_receipt_sha256"]=I.h({
        k:v for k,v in po.items() if k!="learning_receipt_sha256"})
    step["receipt_sha256"]=I.h({k:v for k,v in step.items()
                                  if k!="receipt_sha256"})
    return step


def _expected_paid_winner_margin(step):
    witness=step["decision_info"]["observer"]["competition_witness"]
    final=witness["accumulators_before_residual"]
    threshold=witness["thresholds"]
    w=witness["winner_before_control"]
    others=[(final[k]-threshold[k])/threshold[k] for k in final if k!=w]
    crossed=bool(others and final[w]>=threshold[w])
    gap=(final[w]-threshold[w])/threshold[w]-max(others) if crossed else 0.
    q=float(min(1.,max(0.,gap)))
    return {"key":w,"q":q,"crossed":crossed,
            "paid_rounds":witness["paid_competition_cycles"]}


def _actual_t6_competition(step,mode):
    """Independent F1J equations with ONLY preregistered paid F1N threshold read."""
    check(mode in ("margin","masked"),"unregistered T6 modality")
    info=step["decision_info"]
    check(info.get("funding")=="FUNDED","unfunded T6 cannot pass DEV parity")
    obs=info["observer"]["competition_witness"]
    before=fields(step["before_mind"])
    after=fields(step["after_restoration_before_motor"])
    check(before["f1n_mode"]==mode and after["f1n_mode"]=="off"
          and before["f1n_read_used"] is False and after["f1n_read_used"] is True,
          "T6 readout was not one-tick only")
    owned=map_val(before["f1n_owned_margin"])
    check(type(owned) is dict and set(owned)=={"key","q","source_tick"}
          and owned["source_tick"]==5 and type(owned["q"]) is float
          and 0.<=owned["q"]<=1.,"missing paid source margin")
    rd=obs["f1n_margin_read"]
    effect=owned["q"] if mode=="margin" else 0.
    check(rd=={"mode":mode,"own_key":owned["key"],
               "own_q":owned["q"],"applied_q":effect,
               "own_key_scored":owned["key"] in obs["scored_order"],
               "memory_read_paid":True},"fake F1N readout of owned q")
    check(step["cognitive_work"]["memory_items"]>=1,
          "F1N T6 memory item free")
    scored=info["observer"]["score_witness"]
    options=obs["scored_order"]
    check([v["option"] for v in scored]==options and
          len(options)>0 and len(set(options))==len(options),
          "invented paid-scored options")
    vals=[o["total_score"] for o in scored]
    avg=sum(vals)/len(vals)
    sd=sqrt(sum((x-avg)**2 for x in vals)/len(vals))
    evidence={o:(tanh((score-avg)/sd) if sd>1e-9 else 0.)
              for o,score in zip(options,vals)}
    check(set(obs["normalized_evidence"])==set(options)
          and all(close(obs["normalized_evidence"][o],evidence[o]) for o in options),
          "fake T6 scored evidence")
    initial=typed_map(before["acc"])
    first={k:initial.get(k,0.) for k in options}
    check(obs["accumulators_before"]==first and
          obs["prior_intention"]==before["intention"],
          "made-up F1N own previous accumulation")
    expected={k:1.5*(1.-before["inertia"] if k==before["intention"] else 1.)
              for k in options}
    if owned["key"] in expected:
        expected[owned["key"]]*=(1.-.5*effect)
    check(set(obs["thresholds"])==set(expected)
          and all(close(obs["thresholds"][k],expected[k]) for k in expected),
          "invented F1N T6 threshold or wrong kappa")
    cap=max(1,int(round(before["n_base"]*min(1.,step["before_world"]["body"][0]/50.))))
    check(obs["round_capacity_from_actual_body"]==cap,"false corporal round limit")
    used=obs["paid_competition_cycles"]
    trace=obs["actual_substantive_round_snapshots"]
    check(type(used) is int and used>=0 and used<=cap
          and len(trace)==used and
          obs["budget_blocked_before_full_round_capacity"] is (used<cap)
          and info["cycles"]==used
          and step["cognitive_work"]["cycles"]==3+used,
          "synthetic or unpaid F1N decision round")
    result=dict(first)
    for snap in trace:
        for k in options:
            result[k]=max(0.,.8*result[k]+evidence[k])
        check(set(snap)==set(options)
              and all(close(snap[k],result[k]) for k in options),
              "forged substantive F1N round")
    check(set(obs["accumulators_before_residual"])==set(result)
          and all(close(obs["accumulators_before_residual"][k],result[k])
                  for k in result),"wrong final paid F1N activation")
    crossed=[((result[k]-expected[k])/expected[k],k)
             for k in result if result[k]>=expected[k]]
    if crossed:
        best=max(v for v,k in crossed)
        tied=sorted(k for v,k in crossed if v==best)
        selection="final_round_threshold"
    else:
        vmax=max(result.values())
        tied=sorted(k for k,v in result.items() if v>=vmax-1e-12)
        if len(tied)==len(options) and max(result.values())-min(result.values())<=1e-12:
            high=max(vals)
            tied=sorted(k for k,v in zip(options,vals) if v>=high-1e-12)
            selection="all_activations_equal_raw_score_fallback"
        else:
            selection="final_round_activation"
    winner=obs["winner_before_control"]
    check(obs["selection_mechanism"]==selection
          and obs["tie_candidates"]==tied and winner in tied,
          "F1N laboratory chose a different competition winner")
    reduction={k:0. if k==winner else result[k]*.5 for k in result}
    check(set(obs["accumulators_after_residual"])==set(result)
          and all(close(obs["accumulators_after_residual"][k],reduction[k])
                  for k in result),"wrong native F1N residual update")
    new_acc=typed_map(after["acc"])
    check(set(new_acc)==set(reduction)
          and all(close(new_acc[k],reduction[k]) for k in reduction),
          "F1N brain after decision not matching computed residual")
    check(before["f1n_owned_margin"]==after["f1n_owned_margin"],
          "readout modified paid stored q")
    check(map_val(after["f1n_pending_margin"])==_expected_paid_winner_margin(step),
          "F1N own pending margin not derived from paid final round")
    check(obs["final_admitted_option"]==info["option"],
          "F1N native Action Control override")
    return used


def verify_step(step,world,mind,tick,mode="off",sham=False):
    """Reconstruct physics and personal learning without native code imports."""
    check(step["t"]==tick==world["t"]+1 and tick<=60
          and not world["dead"] and step["before_mind"]==mind
          and step["no_experimental_action_override"] is True,
          "unlinked native F1N step or imposed action")
    K.world_eq(step["before_world"],world,"pre-F1N decision")
    pre=fields(mind)
    check(pre["f1n_mode"]==mode,"readout mode without authorized F1N fork")
    check(pre["f1n_read_used"] is (tick>=7),"unpaid repeat/omitted T6 memory read")
    check(step["capture"]==K.perceive(world)
          and step["capture_sha256"]==I.h(step["capture"]),
          "fake first-person capture")
    check(step["readout_mode"]==("full_sham" if sham else "full")
          and step["temporary_prior_mean_keys"]==[]
          and step["exposed_mind_during_decision"]==mind
          and step["after_restoration_before_motor"]==
                 step["after_decision_exposed_mind"],
          "attempted to hide an additional memory content intervention")
    info=step["decision_info"]
    out=fields(step["after_restoration_before_motor"])
    check(out["f1n_owned_margin"]==pre["f1n_owned_margin"]
          and out["f1n_read_used"] is (tick>=6),
          "surreptitious personal memory edit during thought")
    if info.get("funding")=="FUNDED":
        check(type(out["last"]) is dict and out["last"].get("__tuple__",[None]*4)[2:]==
              [step["action"],step["param"]],
              "unpaid or injected motor")
        witness=info["observer"]["competition_witness"]
        check(witness["final_admitted_option"]==info["option"]
              and witness["final_admitted_action"]==step["action"]
              and witness["status"]=="ACTION_ADMITTED",
              "native ActionControl does not match receipt")
        if tick!=6:
            check(witness["f1n_margin_read"]=={
                "mode":"off","own_key":None,"own_q":None,
                "applied_q":0.0,"own_key_scored":False,
                "memory_read_paid":False},
                "F1N paid margin used outside prereg T6")
            check(map_val(out["f1n_pending_margin"])==
                  _expected_paid_winner_margin(step),
                  "unpaid or forged native final q pending")
    else:
        check(step["action"] is None and step["param"] is None,
              "unfunded action was imposed")
    cost=I.cost(step["cognitive_work"])
    check(cost==step["requested_native_cost"],"decision invoice does not add up")
    I.check_bill(step["native_motor"]["cognitive_accounting"],cost,
                 "F1N original native World.step")
    remaining=list(world["body"])
    remaining[0]-=cost["energy"]
    remaining[4]-=cost["vigilance"]
    I.body_equal(step["decision_remaining"],remaining,"F1N paid decision allowance")
    norm=_normalize(step)
    check(norm["after_restoration_before_motor"]==
          norm["after_decision_exposed_mind"],"normalized original brain mismatch")
    if tick==6:
        used=_actual_t6_competition(step,mode)
    else:
        used=J.cold_paid_fixed_competition(norm)["audited_rounds"]
    state,summary=K.physical(world,step["action"],step["param"],
                             step["cognitive_work"],
                             step["native_motor"]["cognitive_accounting"])
    for k in ("t","dead","moved"):
        check(step["native_motor"][k]==summary[k],"not an original real motor: "+k)
    I.body_equal(step["native_motor"]["body"],summary["body"],
                 "wrong body after actual real motor")
    K.world_eq(step["after_motor_world"],state,"after paid F1N motor")
    nextworld,_=K.paid_learning(norm,state)
    K.verify_paid_personal_learning(norm)
    K.world_eq(step["after_paid_learning_world"],nextworld,"after real F1N learning")
    check(step["postaction"]["mind_after_any_learning"]==
          step["after_paid_learning_mind"],"invalid F1N learned mind seal")
    check(step["postaction"]["learning_receipt_sha256"]==I.h({
        k:v for k,v in step["postaction"].items()
        if k!="learning_receipt_sha256"}),"forged F1N learning receipt")
    check(step["receipt_sha256"]==I.h({k:v for k,v in step.items()
                                       if k!="receipt_sha256"}),
          "forged F1N native step SHA")
    return nextworld,step["after_paid_learning_mind"],used


def verified_paid_t5_write(write,step):
    """Independently verify the memory is only created after real T5 action."""
    check(write["world_before_write"]==step["after_paid_learning_world"]
          and write["mind_before_write"]==step["after_paid_learning_mind"]
          and write["no_world_step_during_write"] is True
          and write["no_observer_to_policy"] is True,
          "T5 own margin was fabricated before native paid learning")
    prev=fields(write["mind_before_write"])
    nxt=fields(write["mind_after_write"])
    check(prev["f1n_owned_margin"] is None
          and nxt["f1n_pending_margin"] is None,
          "not exactly one private paid margin record")
    pend=map_val(prev["f1n_pending_margin"])
    check(pend==_expected_paid_winner_margin(step),
          "own margin differs from genuine computed native T5 final score")
    info=step["decision_info"]
    permitted=(info["option"]==pend["key"]
               and step["action"] is not None and
               info["observer"]["competition_witness"]
                   ["winner_before_control"]==pend["key"])
    q=float(pend["q"] if permitted and pend["crossed"] else 0.)
    check(write["authentic_admitted_winner"] is permitted
          and close(write["own_final_q"],q)
          and write["own_final_key"]==pend["key"],
          "recorded own margin was not self selected or admitted")
    expected=deepcopy(prev)
    expected["f1n_owned_margin"]={"__dict__":[
        ["key",pend["key"]],["q",q],["source_tick",5]]}
    expected["f1n_pending_margin"]=None
    check(nxt==expected,"free hidden edit to nonmargin private state")
    cost=I.cost(write["genuinely_executed_work"])
    check(write["genuinely_executed_work"]=={
        "cycles":0,"simulated_steps":0,"memory_items":1,"replays":0},
        "F1N writing personal item was free")
    I.check_bill(write["actual_paid_memory_bill"],cost,"F1N own T5 memory write")
    start=write["world_before_write"]
    end=deepcopy(start)
    end["body"][0]-=cost["energy"]
    end["body"][4]-=cost["vigilance"]
    K.world_eq(end,write["world_after_write"],"actual T5 memory expenditure")
    I.body_equal(write["memory_budget_remaining"],end["body"],
                 "memory bill actually authorized and paid")
    check(write["sha256"]==I.h({k:v for k,v in write.items() if k!="sha256"}),
          "F1N own T5 memory-write receipt SHA invalid")
    return end,write["mind_after_write"]


def verify_followup(rec,origin_world,origin_mind,mode):
    check(rec["policy"]=="F1N_DEV_"+mode,"wrong fork original policy")
    world,mind=deepcopy(origin_world),deepcopy(origin_mind)
    used=0
    for tick,step in enumerate(rec["steps"],6):
        check(tick<=60 and step["t"]==tick,"T6-T60 missing/reordered original")
        world,mind,rounds=verify_step(step,world,mind,tick,
                                      mode if tick==6 else "off")
        used+=rounds
    check(rec["last_mind"]==mind,"F1N original last brain not reached")
    K.world_eq(rec["last_world"],world,"F1N real terminal world")
    check(rec["metrics"]==K.metrics(rec["steps"],world,
                                    rec["metrics"]["native_error"],60),
          "invented F1N terminal body or bill")
    check(world["dead"] or world["t"]==60 or
          rec["metrics"]["native_error"] is not None,
          "DEV_N omitted a surviving native continuation")
    check(rec["trajectory_sha256"]==I.h({
        k:v for k,v in rec.items() if k!="trajectory_sha256"}),
        "changed original F1N trajectory SHA")
    return world,mind,used


def verify_fork(fork,base,mode):
    check(fork["mode"]==mode and fork["before_mind"]==base
          and fork["no_motor_override"] is True
          and fork["keys_and_scores_untouched"] is True,
          "fork altered original personal T5 state")
    expected=deepcopy(base)
    fields_expected=expected["data"]["private"]["__dict__"]
    matches=[v for v in fields_expected if v[0]=="f1n_mode"]
    check(len(matches)==1 and matches[0][1]=="off" and fields(base)["f1n_read_used"] is False,
          "private mode has already been spent")
    matches[0][1]=mode
    expected["sha256"]=I.h(expected["data"])
    check(expected==fork["after_mind"],"fork secretly changed bodily policy")
    before=fields(base)
    check(map_val(before["f1n_owned_margin"])==
          fork["same_original_personal_record"],
          "fork reconstituted an alternate personal memory")
    return expected


def read_originals(directory):
    base=Path(directory)
    report=json.loads((base/"F1N_DEV_NATIVE_INDEX.json").read_bytes())
    grid=report["grid"]
    expected=cold_grid(grid["cohort"],grid["origin_count"]==8)
    check(grid==expected and report["schema"]==SCHEMA
          and report["phase"]==PHASE and report["scientific_verdict"] is None
          and report["source_single_native_pass"] is True
          and report["f1n_heldout_world_steps_created"]==0
          and report["no_imposed_motor"] is True
          and report["no_retroactive_cost_padding"] is True,
          "unregistered DEV_N origins or forged scientific status")
    check(report["case_count"]==len(grid["origins"])
          and report["original_parts"]==len(grid["origins"])*7
          and report["parts_per_root"]==7
          and report["parts"]==list(PARTS)
          and len(report["entries"])==len(grid["origins"])*7,
          "missing original gzip parts")
    origin_ids=[o["id"] for o in grid["origins"]]
    check(set(origin_ids).isdisjoint(N.ROOT_IDS)
          and set(o["seed"] for o in grid["origins"]).isdisjoint(N.SEEDS)
          and all(s in DEV_A_SEEDS+DEV_B_SEEDS for s in
                  (o["seed"] for o in grid["origins"])),
          "F1N heldout scientific source leaked into development")
    entries=report["entries"]
    check(len({e["path"] for e in entries})==len(entries),
          "duplicate native source path in index")
    for k in range(1,len(origin_ids)+1):
        ck=json.loads((base/f"_checkpoint_{k:02d}.json").read_bytes())
        check(ck["completed"]==k and ck["roots"]==origin_ids[:k]
              and ck["entries"]==entries[:k*7],
              "original incremental F1N native checkpoint mismatch")
    return grid,report


def iter_originals(directory, report):
    """One-root bounded-memory reading, SHA-checking every original part."""
    base=Path(directory)
    entries=report["entries"]
    for i,origin in enumerate(report["grid"]["origins"]):
        root=origin["id"]
        parts={}
        for j,part in enumerate(PARTS):
            entry=entries[i*7+j]
            rel=f"{root}/{part}.json.gz"
            check(entry["path"]==rel and entry["id"]==root
                  and entry["part"]==part and rel not in parts,
                  "duplicated, missing or out-of-order F1N gzip")
            gz=(base/rel).read_bytes()
            check(len(gz)==entry["gzip_bytes"] and
                  digest(gz)==entry["gzip_sha256"],
                  "mutable or forged compressed native original")
            raw=gzip.decompress(gz)
            check(len(raw)==entry["raw_bytes"] and
                  digest(raw)==entry["raw_sha256"],
                  "decoded original not the hash-stamped native receipt")
            obj=json.loads(raw)
            check(obj["schema"]==PART_SCHEMA and obj["id"]==root
                  and obj["part"]==part and I.h(obj)==entry["raw_sha256"],
                  "wrong per-root per-part source identity")
            parts[rel]=obj["native"]
        yield root,parts


def audit(directory):
    N.check_files()
    grid,report=read_originals(directory)
    detailed=[]
    totals={"source_valid":0,"t5_sham_neutral":0,"t6_equal_cost":0,
            "long_shams_neutral":0,"real_t5_margin_writes":0,
            "real_t6_margin_reads":0,"real_t6_masked_reads":0,
            "motor_changed":0,"paid_rounds":0,"world_steps":0}
    for (origin,index),(root,parts) in zip(
            zip(grid["origins"],report["cases"]),
            iter_originals(directory,report)):
        check(root==origin["id"],"mismatched streamed native root")
        check(index["origin"]==origin,"altered case source identity")
        src=parts[f"{root}/source_t1_t4.json.gz"]
        world=origin_world(grid,origin)
        K.world_eq(src["genesis"]["world"],world,"authentic fresh DEV_N birth")
        mind=src["genesis"]["mind"]
        born=fields(mind)
        check(born["f1n_owned_margin"] is None
              and born["f1n_pending_margin"] is None
              and born["f1n_mode"]=="off" and born["f1n_read_used"] is False
              and K.effects(_normalize(mind))=={}
              and born["buffer"]=={"__deque__":[],"maxlen":None}
              and all(all(z==0 for z in row) for row in born["values"]),
              "individual was born with alien memory")
        check(len(src["steps"])==4,"invalid genuine T1..T4 lifetime")
        for tick,step in enumerate(src["steps"],1):
            world,mind,used=verify_step(step,world,mind,tick)
            totals["world_steps"]+=1;totals["paid_rounds"]+=used
        check(src["valid"] is True and src["error"] is None
              and src["world_t4"]==world and src["mind_t4"]==mind
              and world["t"]==4 and not world["dead"] and
              all(x["postaction"]["status"]=="PAID_LEARNED"
                  for x in src["steps"]),
              "unfunded or invented T1..T4 autobiographical source")
        totals["source_valid"]+=1
        t5={}
        for suffix,sham in (("self_paid_t5",False),("self_paid_t5_sham",True)):
            doc=parts[f"{root}/{suffix}.json.gz"]
            step=doc["step"]
            w,m,used=verify_step(step,world,mind,5,sham=sham)
            totals["world_steps"]+=1;totals["paid_rounds"]+=used
            w,m=verified_paid_t5_write(doc["write"],step)
            check(doc["t5_world"]==w and doc["t5_mind"]==m,
                  "paid T5 margin write not actually retained by same individual")
            t5[suffix]=doc
            totals["real_t5_margin_writes"]+=1
        first,sham=t5["self_paid_t5"],t5["self_paid_t5_sham"]
        neutral=(first["write"]==sham["write"] and
                 first["t5_world"]==sham["t5_world"] and
                 first["t5_mind"]==sham["t5_mind"] and
                 {k:v for k,v in first["step"].items()
                  if k not in ("readout_mode","receipt_sha256")}==
                 {k:v for k,v in sham["step"].items()
                  if k not in ("readout_mode","receipt_sha256")})
        check(neutral,"T5 native sham altered own paid personal margin")
        totals["t5_sham_neutral"]+=1
        state=first["t5_world"]
        person=first["t5_mind"]
        arms={}
        sham_arms={}
        for mode in ("margin","masked"):
            original=parts[f"{root}/{mode}_t6_t60.json.gz"]
            control=parts[f"{root}/{mode}_t6_t60_sham.json.gz"]
            changed=verify_fork(original["fork"],person,mode)
            same=verify_fork(control["fork"],person,mode)
            check(changed==same,"fork shams diverged before memory access")
            last,m,rounds=verify_followup(original["followup"],state,changed,mode)
            totals["world_steps"]+=len(original["followup"]["steps"])
            totals["paid_rounds"]+=rounds
            last_s,m_s,rounds_s=verify_followup(control["followup"],state,same,mode)
            totals["world_steps"]+=len(control["followup"]["steps"])
            totals["paid_rounds"]+=rounds_s
            sham_equal=(original==control and last==last_s and m==m_s)
            check(sham_equal,"T6..T60 native sham is not neutral")
            arms[mode]=original
            sham_arms[mode]=control
            if mode=="margin":totals["real_t6_margin_reads"]+=1
            else:totals["real_t6_masked_reads"]+=1
        totals["long_shams_neutral"]+=2
        a=arms["margin"]["followup"]["steps"]
        b=arms["masked"]["followup"]["steps"]
        check(a and b,"no native T6 in one of the arms")
        ax,bx=a[0],b[0]
        check(ax["before_world"]==bx["before_world"]
              and ax["capture"]==bx["capture"]
              and ax["cognitive_work"]==bx["cognitive_work"]
              and ax["requested_native_cost"]==bx["requested_native_cost"]
              and ax["decision_remaining"]==bx["decision_remaining"]
              and ax["native_motor"]["cognitive_accounting"]==
                  bx["native_motor"]["cognitive_accounting"]
              and all(q["paid"]==q["requested"] and q["unpaid"]==0.0
                      for st in (ax,bx) for q in
                      st["native_motor"]["cognitive_accounting"].values()),
              "unequal REAL cognitive T6 funding, no fictitious padding")
        totals["t6_equal_cost"]+=1
        diff=(ax["action"],ax["param"])!=(bx["action"],bx["param"])
        totals["motor_changed"]+=int(diff)
        # The developer's aggregate has no authority without this cold computation.
        cmp=index["comparison"]
        check(cmp["equal_t6_real_decision_cost"] is True
              and cmp["motor_changed"] is diff
              and cmp["delta_lived_ticks"]==len(a)-len(b)
              and cmp["delta_body"]==[
                 x-y for x,y in zip(arms["margin"]["followup"]["metrics"]["terminal_body"],
                                    arms["masked"]["followup"]["metrics"]["terminal_body"])],
              "producer silently reclassified physical outcomes")
        check(index["source_valid"] is True and index["shams_neutral"] is True,
              "producer claimed invalid paid source/shams")
        detailed.append({"root":root,"seed":origin["seed"],"source_valid":True,
                         "t5_sham_neutral":True,"t6_real_cost_equal":True,
                         "sham_long_controls":2,"motor_changed":diff,
                         "delta_lived_ticks":len(a)-len(b),
                         "q":map_val(fields(person)["f1n_owned_margin"])["q"],
                         "reused_scored_key":ax["decision_info"]["observer"]
                             ["competition_witness"]["f1n_margin_read"]
                             ["own_key_scored"]})
    check(report["summary"]["source_valid"]==totals["source_valid"]
          and report["summary"]["shams_neutral"]==len(detailed)
          and report["summary"]["t6_equal_cost"]==totals["t6_equal_cost"]
          and report["summary"]["motor_changed"]==totals["motor_changed"],
          "aggregated DEV_N source of truth differs from cold evidence")
    complete=(len(detailed)==len(grid["origins"]) and
              totals["source_valid"]==len(detailed) and
              totals["t5_sham_neutral"]==len(detailed) and
              totals["t6_equal_cost"]==len(detailed) and
              totals["long_shams_neutral"]==2*len(detailed))
    check(complete,"inconclusive DEV_N native paid/sham gates")
    return {"schema":"i3-stage8f1n-independent-dev-cold-T60/v0",
            "phase":PHASE,"cohort":grid["cohort"],
            "source_policy":"F1NMarginMind (opt-in DEV-only)",
            "cold_python_standard_library_only":True,
            "engine_or_native_producer_imported":False,
            "original_parts_verified":len(report["entries"]),
            "roots":len(detailed),"seed_set":[o["seed"] for o in grid["origins"]],
            "per_root":detailed,"summary":totals,
            "DEV_only_technical_result":"DEV_N_COLD_VALID_BUT_NOT_SCIENTIFIC",
            "f1n_scientific_heldouts_exposed":0,
            "scientific_verdict":None}


def main():
    parser=argparse.ArgumentParser(description="Independent no-engine F1N DEV audit")
    parser.add_argument("--original-dir",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    result=audit(args.original_dir)
    out=Path(args.output)
    with out.open("xb") as fp:
        fp.write(json.dumps(result,sort_keys=True,ensure_ascii=False,
                            separators=(",",":"),allow_nan=False).encode()+b"\n")
    print(json.dumps({"phase":result["phase"],"cohort":result["cohort"],
                      "result":result["DEV_only_technical_result"],
                      "summary":result["summary"],
                      "f1n_sci_born":0},sort_keys=True))


if __name__=="__main__":
    main()