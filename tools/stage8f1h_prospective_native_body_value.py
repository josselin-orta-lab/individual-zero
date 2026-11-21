"""F1H: preexposed T12 BODY consequences of F1F's autonomous motor fork.

Source-exact F1C and F1F, 8 frozen ecologies, 3 arms; native paid F1C and
identical archived F1F tick-2 decision receipts. Only tick-2 effect-model mean
readout is briefly masked, then ALL trajectories autonomously choose and
pay cognition and post-action learning until tick 12 or irreversible death.

Research scope: conditional, synthetic policy-READOUT total effect, not a
forced E-vs-N intervention, not real G2 descendants or generalized survival.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path

from i3.modules.body import CognitiveBudget, CognitiveWork, cognitive_cost
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1f_ecological_mean_readout as F
from tools import stage8f1f_independent_ecology_audit as A
from tools import stage8f1f_native_ecological_contexts as X

SCHEMA="i3-stage8f1h-prospective-t12-native-body-value/v0"
SOURCE_MAIN="3ad4cb687b403214c9b9f6055b46a489dca44af4"
F1C_SHA=D.F1C_ORIGINAL_SHA
F1F_SHA="f620d1b46ddf269dc368dcd90ba6c93f44f0b6442f8d9e6322440de32e3fbab5"
F1F_COLD_SHA="8013f2add1f3eb0190127bb77eac588c95f153f32ba21113302bafa0292e2ac2"
F1G_SHA="a7f0782886b3d2b97cd91ea11803934f31736b91e6d659c700a3d1dd886a8376"
F1G_COLD_SHA="ec3b1c953c69d87dc042ab81da55809984e7b78c175a2697a6b3d0a24fa21310"
PREEXPOSURE_COMMIT="5c2abb2fc755bf0a580e2880bedf507b59a2baec"
MODES=("full","sham","mask_both")
T12=12
MIXED="mixed_here_water_east_food"
FROZEN_E2=C.NEGATIVE


def load_source(path, expected):
    raw=Path(path).read_bytes()
    import hashlib
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise AssertionError("byte-exact original source SHA mismatch: "+str(path))
    return json.loads(raw)


def _native_second(world,mind,mode,original,reference,expected):
    """Recompute the whole native F1F receipt EXACTLY, retaining raw World.step."""
    if mode not in MODES:
        raise ValueError("non-preregistered original F1F comparator")
    src=original["arms"]["retain"]
    pre=C.seal_mind(mind)
    if pre!=src["private_persisted_postaction"] or world.t!=1 or world.dead:
        raise AssertionError("original paid F1C memory missing at fork")
    old_stats,new_stats,old_values,new_values=reference
    before_world=D._snapshot_world(world)
    cap=world.capture()
    orig_effects=deepcopy(mind.effects)
    orig_values=deepcopy(mind.values)
    orig_buffer=deepcopy(mind.buffer)
    exposed_effects=deepcopy(orig_effects)
    exposed_values=deepcopy(orig_values)
    exposed_buffer=deepcopy(orig_buffer)
    masks=[]
    if mode=="mask_both":
        for key in F.TARGET_KEYS:
            exposed_effects.stats[key][1][:]=old_stats[key][1]
            masks.append("effects.mean."+key[0])
    if mode!="full":
        mind.effects=exposed_effects
        mind.values=exposed_values
        mind.buffer=exposed_buffer
    during=C.seal_mind(mind)
    budget=CognitiveBudget(world.body,world.laws)
    action,param,work,info=mind.decide(cap,budget)
    after_decide=C.seal_mind(mind)
    if budget.work!=work or world.t!=1:
        raise AssertionError("unpaid/hidden second decision")
    mind.effects=orig_effects
    mind.values=orig_values
    mind.buffer=orig_buffer
    restored=C.seal_mind(mind)
    if (I.observed_stats(restored)!=new_stats or mind.values!=new_values or
            list(mind.buffer)!=list(orig_buffer)):
        raise AssertionError("native decision did not restore earned memory")
    energy,vigilance=cognitive_cost(world.laws,work)
    native=world.step(action,param,work)
    if native["t"]!=2 or world.t!=2:
        raise AssertionError("not the genuine archived tick2 physics")
    for k,v in (("energy",energy),("vigilance",vigilance)):
        bill=native["cognitive_accounting"][k]
        if abs(bill["paid"]-v)>1e-10 or bill["unpaid"]!=0.:
            raise AssertionError("tick2 World.step did not pay earned cognitive work")
    rec={
        "mode":mode,"allowed_temporary_masks":masks,
        "before_world":before_world,"before_mind":pre,
        "first_person_capture":json.loads(C.canonical(cap)),
        "capture_sha256":C.digest(cap),
        "effective_readout_mind":during,
        "post_decision_exposed_mind":after_decide,
        "post_decision_restored_mind":restored,
        "action":action,"param":param,
        "decision_info":json.loads(C.canonical(info)),
        "cognitive_work":asdict(work),
        "prepaid_allowance_remaining":list(budget.remaining),
        "native_bill":deepcopy(native["cognitive_accounting"]),
        "expected_native_cognitive_cost":{"energy":energy,"vigilance":vigilance},
        "native_second_step":{
            "t":native["t"],"body":list(native["body"]),
            "moved":native["moved"],"dead":list(native["dead"]),
        },
        "after_world":D._snapshot_world(world),
        "real_personal_memory_restored":True,
        "new_learning_performed":False,
    }
    rec["receipt_sha256"]=C.digest(rec)
    if rec!=expected:
        raise AssertionError("INVALID_F1F_TICK2_ANCHOR: exact archived native F1F decision receipt differs")
    # Raw native result (not inferred/forged) is carried to paid post-step
    # learning on THIS same Mind. No action is ever read from the archive and
    # imposed on the engine. The Mind itself chose and paid above.
    return rec,native


def _pay_new_learning(world,mind,raw):
    """Native continuation order: observe, authorize, debit, learn. No free replay."""
    before=C.seal_mind(mind)
    after_step_body=list(world.body)
    status="DEAD_NO_LEARNING" if world.dead else "NO_NEW_LEARNING"
    work=CognitiveWork()
    remaining=after_step_body
    replays=None
    paid=None
    executed=0
    if not world.dead and mind.last is not None:
        mind.observe_outcome(raw)
        grant=CognitiveBudget(world.body,world.laws)
        replays=mind.prepare_learning(raw,grant)
        work=grant.work
        remaining=list(grant.remaining)
        if replays is None:
            if work!=CognitiveWork():
                raise AssertionError("unfunded learning retained paid work")
            status="UNFUNDED_LEARNING"
        else:
            if work==CognitiveWork():
                raise AssertionError("unpaid learning wrongly authorized")
            paid=world.pay_cognition(work)
            C.paid_bill(world.laws,work,paid)
            raw["body"]=world.body   # EXACT native runtime convention
            executed=mind.learn_from_outcome(raw,replay_limit=replays)
            if executed!=replays:
                raise AssertionError("learning computed more/less replays than already paid")
            status="PAID_LEARNED"
    elif not world.dead:
        status="NO_LAST_ACTION_NO_LEARNING"
    record={
        "status":status,
        "mind_before_outcome_observation":before,
        "world_after_motor_body":after_step_body,
        "learn_work":asdict(work),
        "learning_grant_remaining":remaining,
        "prepaid_replays":replays,
        "actual_paid_learning_bill":paid,
        "executed_replays":executed,
        "body_after_any_learning":list(world.body),
        "world_after_any_learning":D._snapshot_world(world),
        "mind_after_any_learning":C.seal_mind(mind),
    }
    record["learning_receipt_sha256"]=C.digest(record)
    return record


def _native_followup_step(world,mind):
    if world.dead or not 3<=world.t+1<=T12:
        raise AssertionError("post-death or over-horizon native decision")
    before_world=D._snapshot_world(world)
    before_mind=C.seal_mind(mind)
    cap=world.capture()
    budget=CognitiveBudget(world.body,world.laws)
    action,param,work,info=mind.decide(cap,budget)
    if work!=budget.work or world.t!=before_world["t"]:
        raise AssertionError("world advanced during unforced thought")
    after_decision=C.seal_mind(mind)
    energy,vigilance=cognitive_cost(world.laws,work)
    raw=world.step(action,param,work)
    for coin,value in (("energy",energy),("vigilance",vigilance)):
        bill=raw["cognitive_accounting"][coin]
        if (abs(bill["paid"]-value)>1e-10 or
                abs(bill["requested"]-value)>1e-10 or
                bill["unpaid"]!=0.0):
            raise AssertionError("postfork cognition had unpaid or forged physical bill")
    out={
        "t":raw["t"],"before_world":before_world,
        "mind_before_decision":before_mind,
        "first_person_capture":json.loads(C.canonical(cap)),
        "capture_sha256":C.digest(cap),
        "chosen_action":action,"chosen_param":param,
        "genuinely_computed_decision_info":json.loads(C.canonical(info)),
        "decision_work":asdict(work),
        "decision_remaining":list(budget.remaining),
        "decision_mind_after_choice":after_decision,
        "native_motor_bill":deepcopy(raw["cognitive_accounting"]),
        "native_motor_result":{
            "t":raw["t"],"body":list(raw["body"]),
            "moved":raw["moved"],"dead":list(raw["dead"])},
        "world_after_motor":D._snapshot_world(world),
        "future_memory_content_not_masked":True,
    }
    out["postaction"]=_pay_new_learning(world,mind,raw)
    out["receipt_sha256"]=C.digest(out)
    return out


def _metric(steps,world, error):
    """Prespecified descriptive metrics, never an after-the-fact scalar reward."""
    paid_decision={k:0.0 for k in ("energy","vigilance")}
    paid_learning={k:0.0 for k in ("energy","vigilance")}
    area=[0.0]*5
    vital_min=None
    movements=0
    drank=0
    collected=0
    for item in steps:
        dec_bill=(item["f1f_tick2_receipt"]["native_bill"]
                  if item["t"]==2 else item["native_motor_bill"])
        post=item["postaction"]
        for coin in paid_decision:
            paid_decision[coin]+=dec_bill[coin]["paid"]
            if post["actual_paid_learning_bill"] is not None:
                paid_learning[coin]+=post["actual_paid_learning_bill"][coin]["paid"]
        end=post["body_after_any_learning"]
        for i,val in enumerate(end):
            area[i]+=val
        vital_min=min(vital_min if vital_min is not None else float("inf"),
                      min(end[1],end[2],end[3]))
        action=(item["f1f_tick2_receipt"]["action"] if item["t"]==2
                else item["chosen_action"])
        movements+=int(action=="se_deplacer")
        drank+=int(action=="boire")
        collected+=int(action=="collecter")
    return {
        "steps_executed_after_f1c":len(steps),
        "alive_at_t12":bool(world.t==T12 and not world.dead and error is None),
        "final_tick":world.t,
        "terminal_body_after_all_real_learning":list(world.body),
        "terminal_position":list(world.pos),
        "terminal_dead_reasons":list(world.dead),
        "integrated_body_reserves_unscaled":area,
        "minimum_vital_reserve_on_observed_ticks":vital_min,
        "paid_cognitive_decision_total":paid_decision,
        "paid_cognitive_learning_total":paid_learning,
        "movement_count":movements,
        "drink_count":drank,
        "collect_count":collected,
        "native_engineering_error":error,
    }


def _trajectory(world,mind,mode,original,ref,expected):
    orig_tick2,raw=_native_second(world,mind,mode,original,ref,expected)
    step={
        "t":2,"f1f_tick2_original_receipt_sha256":orig_tick2["receipt_sha256"],
        "f1f_tick2_receipt":orig_tick2,
        "native_motor_raw_receipt":json.loads(C.canonical(raw)),
        "postaction":_pay_new_learning(world,mind,raw),
    }
    step["receipt_sha256"]=C.digest(step)
    steps=[step]
    error=None
    while world.t<T12 and not world.dead:
        try:
            steps.append(_native_followup_step(world,mind))
        except KeyError as exc:
            # The original F1F food token explicitly has NO token_effects.
            # No fabricated benefit or rescue; report a native model gap.
            error={"t_attempted":world.t+1,"kind":"UNDEFINED_F1F_TOKEN_EFFECT",
                   "message":str(exc)}
            break
    return {
        "mode":mode,
        "steps":steps,
        "world_at_end":D._snapshot_world(world),
        "mind_at_end":C.seal_mind(mind),
        "metrics":_metric(steps,world,error),
    }


def _dominance(a,b):
    av=a["terminal_body_after_all_real_learning"]
    bv=b["terminal_body_after_all_real_learning"]
    eps=1e-9
    if all(x>=y-eps for x,y in zip(av,bv)) and any(x>y+eps for x,y in zip(av,bv)):
        return "FULL_STRICT_FIVE_CHANNEL_PARETO_DOMINANCE"
    if all(y>=x-eps for x,y in zip(av,bv)) and any(y>x+eps for x,y in zip(av,bv)):
        return "MASKED_STRICT_FIVE_CHANNEL_PARETO_DOMINANCE"
    if all(abs(x-y)<=eps for x,y in zip(av,bv)):
        return "FIVE_CHANNELS_IDENTICAL"
    return "MIXED_BODILY_TRADEOFF"


def _rank_survival(a,b):
    # Alive at T12 has priority over equal 11-step count with death ON T12.
    if a["alive_at_t12"]!=b["alive_at_t12"]:
        return "FULL_SURVIVAL_ADVANTAGE" if a["alive_at_t12"] else "FULL_SURVIVAL_DISADVANTAGE"
    if a["steps_executed_after_f1c"]>b["steps_executed_after_f1c"]:
        return "FULL_SURVIVAL_ADVANTAGE"
    if a["steps_executed_after_f1c"]<b["steps_executed_after_f1c"]:
        return "FULL_SURVIVAL_DISADVANTAGE"
    return "NO_SURVIVAL_DIFFERENCE"


def _sham_equivalence(x,y):
    # Complete future physical/memory trajectory must be identical to the
    # identical-content sham, never just the first motor action.
    if len(x["steps"])!=len(y["steps"]):
        return False
    if (x["metrics"]!=y["metrics"] or
            x["world_at_end"]!=y["world_at_end"] or
            x["mind_at_end"]!=y["mind_at_end"]):
        return False
    for a,b in zip(x["steps"],y["steps"]):
        if a["t"]==2:
            ca,cb=a["f1f_tick2_receipt"],b["f1f_tick2_receipt"]
            fields=("before_world","before_mind","first_person_capture",
                    "post_decision_restored_mind","native_bill","native_second_step",
                    "after_world","action","param","cognitive_work","decision_info")
            if any(ca[k]!=cb[k] for k in fields):
                return False
            if a["postaction"]!=b["postaction"]:
                return False
        elif a!=b:
            return False
    return True


def produce(original,f1f,previous_cold):
    ref=F.authentic_reference(original)
    if C.digest(original)!=F1C_SHA or C.digest(f1f)!=F1F_SHA:
        raise AssertionError("F1H received noncanonical original F1C/F1F source")
    cold=A.audit_f1f(f1f,original)
    if (C.digest(previous_cold)!=F1F_COLD_SHA or
            C.canonical(cold)!=C.canonical(previous_cold) or
            f1f["eight_contexts_valid_cost_pairs"]!=8 or
            f1f["eight_contexts_with_motor_change"]!=1):
        raise AssertionError("F1F historical independent verdict was changed")
    cases=[]
    for case,f1f_case in zip(X.ECOLOGIES,f1f["contexts"]):
        if f1f_case["context"]!=X.describe(case):
            raise AssertionError("nonpreregistered ecological fork or ordering")
        start_world,start_mind,origin=X.native_original_paid_source(original,case)
        if origin!=f1f_case["source"]:
            raise AssertionError("F1F source original post-paid learning changed")
        arms={}
        for mode in MODES:
            arms[mode]=_trajectory(
                deepcopy(start_world),deepcopy(start_mind),mode,
                original,ref,f1f_case["arms"][mode])
            arms[mode]["trajectory_sha256"]=C.digest(arms[mode])
        full,sham,masked=(arms[m] for m in MODES)
        neutral=_sham_equivalence(full,sham)
        errors=[m for m in MODES if arms[m]["metrics"]["native_engineering_error"]]
        full_m=full["metrics"];masked_m=masked["metrics"]
        comparable=not errors and neutral
        row={
            "context":X.describe(case),
            "source_f1f_case_sha256":f1f_case["case_sha256"],
            "source_f1f_first_paid_sha256":origin["source_proof_sha256"],
            "arms":arms,
            "sham_entire_trajectory_neutral":neutral,
            "native_engineering_error_arms":errors,
            "valid_continuation_for_value":comparable,
            "observed_survival_comparison":(
                _rank_survival(full_m,masked_m) if comparable else None),
            "observed_terminal_five_channel_dominance":(
                _dominance(full_m,masked_m) if comparable and
                full_m["alive_at_t12"] and masked_m["alive_at_t12"] else None),
            "initial_f1f_motor_difference":(
                [full["steps"][0]["f1f_tick2_receipt"]["action"],
                 full["steps"][0]["f1f_tick2_receipt"]["param"]]!=
                [masked["steps"][0]["f1f_tick2_receipt"]["action"],
                 masked["steps"][0]["f1f_tick2_receipt"]["param"]]),
        }
        row["case_sha256"]=C.digest(row)
        cases.append(row)
    mix=cases[-1]
    if (mix["context"]["id"]!=MIXED or
            not mix["initial_f1f_motor_difference"] or
            any(c["initial_f1f_motor_difference"] for c in cases[:-1])):
        raise AssertionError("F1F motor difference precondition no longer exactly 1/8")
    all_valid=all(c["valid_continuation_for_value"] for c in cases)
    if not all_valid:
        verdict="INCONCLUSIVE_NATIVE_CONTINUATION"
    else:
        direction=mix["observed_survival_comparison"]
        verdict={
            "FULL_SURVIVAL_ADVANTAGE":"LOCAL_T12_SURVIVAL_ADVANTAGE_OF_MEMORY_READOUT_OBSERVED",
            "FULL_SURVIVAL_DISADVANTAGE":"LOCAL_T12_SURVIVAL_DISADVANTAGE_OF_MEMORY_READOUT_OBSERVED",
            "NO_SURVIVAL_DIFFERENCE":"NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12"
        }[direction]
    report={
        "schema":SCHEMA,
        "source_main":SOURCE_MAIN,
        "preregistered_preexposure_commit":PREEXPOSURE_COMMIT,
        "f1c_source_original_sha256":F1C_SHA,
        "f1f_source_original_sha256":F1F_SHA,
        "f1f_original_cold_sha256":F1F_COLD_SHA,
        "f1g_original_sha256_untouched":F1G_SHA,
        "f1g_cold_sha256_untouched":F1G_COLD_SHA,
        "frozen_stage8e2":FROZEN_E2,
        "frozen_f1d":"NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE",
        "frozen_f1e":"NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE",
        "frozen_f1f":"MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES",
        "frozen_f1g_td":"NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
        "frozen_f1g_buffer":"NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
        "evidence_class":"DEVELOPMENT_ONLY_NATIVE_EIGHT_SYNTHETIC_ECOLOGIES_NOT_G2",
        "study":"F1H_T12_UNFORCED_TOTAL_MEMORY_READOUT_EFFECT",
        "preexposed_horizon_inclusive":T12,
        "conditional_preknown_f1f_motor_divergent_context":MIXED,
        "other_contexts_are_preexposed_not_selected":True,
        "preexposed_context_ids":[x[0] for x in X.ECOLOGIES],
        "arms_per_context":list(MODES),
        "no_policy_or_motor_override":True,
        "no_extra_content_mask_after_t2":True,
        "all_f1f_tick2_receipts_exact_archival_matches":True,
        "native_original_f1c_first_step_count":8,
        "native_followup_world_step_count":sum(
            len(a["steps"]) for c in cases for a in c["arms"].values()),
        "full_lives_created":0,
        "new_scientific_cohorts":0,
        "run_life_executed":False,
        "historical_G2_private_memory_equivalence":False,
        "valid_prospective_ecologies":sum(c["valid_continuation_for_value"] for c in cases),
        "mixed_primary_survival_verdict":verdict,
        "mixed_terminal_five_channel_dominance":mix["observed_terminal_five_channel_dominance"],
        "contexts":cases,
    }
    report["provenance_chain_sha256"]=C.digest({
        "source_main":SOURCE_MAIN,"f1c":F1C_SHA,"f1f":F1F_SHA,
        "f1f_cold":F1F_COLD_SHA,"preexposure":PREEXPOSURE_COMMIT,
        "contexts":[c["case_sha256"] for c in cases],
    })
    return report


def main():
    p=argparse.ArgumentParser(description="F1H native T12 prospective, no action forcing or new lives")
    p.add_argument("--f1c-original",required=True)
    p.add_argument("--f1f-original",required=True)
    p.add_argument("--f1f-cold",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    src=load_source(a.f1c_original,F1C_SHA)
    prior=load_source(a.f1f_original,F1F_SHA)
    prior_cold=load_source(a.f1f_cold,F1F_COLD_SHA)
    report=produce(src,prior,prior_cold)
    with Path(a.output).open("xb") as fd:
        fd.write(C.canonical(report))
    print(json.dumps({
        "status":report["mixed_primary_survival_verdict"],
        "valid_ecologies":report["valid_prospective_ecologies"],
        "next_native_steps":report["native_followup_world_step_count"],
        "original_tick2_archival_matches":report["all_f1f_tick2_receipts_exact_archival_matches"],
        "mixed":[
            {k:v for k,v in c["arms"][mode]["metrics"].items()
             if k in ("steps_executed_after_f1c","alive_at_t12",
                       "terminal_body_after_all_real_learning","terminal_position",
                       "native_engineering_error")}
            for c in report["contexts"] if c["context"]["id"]==MIXED
            for mode in ("full","mask_both")],
        "sha256":C.digest(report),
    },sort_keys=True))


if __name__=="__main__":
    main()
