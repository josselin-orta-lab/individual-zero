"""F1F preregistered ecological content experiment, native equal-cost gates.

The remembered F1C first-person action and the actual post-action cognition
bill are reconstructed WITHOUT forcing behavior. Eight WORLDS expose
resources through native WorldSpec.changes at tick 1. Each runs three
separate genuine Mind.decide -> World.step interventions at tick 2.

This source also provides the shared, predeclared content readout mechanism
for the future DISTINCT Stage8-F1G TD/buffer audit (not run by F1F).
"""
from __future__ import annotations

import argparse
from collections import deque
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path

from i3.modules.body import CognitiveBudget, cognitive_cost
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1f_native_ecological_contexts as X

SCHEMA = "i3-stage8f1f-eight-ecologies-mean-content-native-proof/v0"
SOURCE_MAIN = "77c3e3395dfa379851d6192a7ec09968727c9ed9"
SOURCE_F1C_SHA = D.F1C_ORIGINAL_SHA
MODES_F1F = ("full", "sham", "mask_both")
MODES_F1G = ("full", "sham_state", "mask_td", "mask_buffer")
ALL_MODES = MODES_F1F + ("sham_state", "mask_td", "mask_buffer")
TARGET_KEYS = (("dormir",), ("*",))
STAGE8E2_NEGATIVE = C.NEGATIVE
F1E_NEGATIVE = "NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE"
F1D_NEGATIVE = "NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE"


def authentic_reference(original):
    receipt=original["arms"]["retain"]
    old = I.observed_stats(receipt["private_before_postaction_learning"])
    learned = I.observed_stats(receipt["private_persisted_postaction"])
    if (set(old)!=set(learned) or set(old)!=set(TARGET_KEYS)
            or any(old[key][0]!=old[key][2] or
                   learned[key][0]!=learned[key][2] or
                   old[key][0]!=1. or learned[key][0]!=2. or
                   old[key][1]==learned[key][1] for key in TARGET_KEYS)):
        raise AssertionError("expected original personally acquired F1C effect means")
    private_old=I.private_fields(receipt["private_before_postaction_learning"])
    private_new=I.private_fields(receipt["private_persisted_postaction"])
    if (len(private_old["values"])!=3 or
            len(private_new["values"])!=3 or
            any(len(row)!=6 for row in private_old["values"]+private_new["values"])):
        raise AssertionError("no source-locked 3x6 TD value control")
    if not any(x != y for x,y in zip(private_old["values"],private_new["values"])):
        raise AssertionError("TD content was not actually learned in original F1C")
    if private_old["buffer"] != {"__deque__":[],"maxlen":None}:
        raise AssertionError("historical pre-learning episodic buffer was not empty")
    if (private_new["buffer"]["maxlen"] is not None or
            len(private_new["buffer"]["__deque__"])!=1):
        raise AssertionError("cannot isolate single personal remembered episode")
    return old,learned,private_old["values"],private_new["values"]


def actual_paid_second_choice(world,mind,mode,original,reference=None):
    """Run a decision without replacing its outcome, costs or the genuine Mind."""
    if mode not in ALL_MODES:
        raise ValueError("unregistered experimental intervention")
    src=original["arms"]["retain"]
    before=C.seal_mind(mind)
    if before!=src["private_persisted_postaction"] or world.t!=1 or world.dead:
        raise AssertionError("not exact F1C-paid and retained personal Mind")
    prior_stats,learned_stats,prior_values,learned_values=(
        reference if reference is not None else authentic_reference(original))
    before_world=D._snapshot_world(world)
    cap=world.capture()
    original_effects=deepcopy(mind.effects)
    original_values=deepcopy(mind.values)
    original_buffer=deepcopy(mind.buffer)
    if (I.observed_stats(before) != learned_stats
            or original_values != learned_values
            or len(original_buffer)!=1):
        raise AssertionError("private Mind already changed before intervention")
    # Temporary EXPOSURE ONLY. All three original learned objects survive.
    exposed_effects=deepcopy(original_effects)
    exposed_values=deepcopy(original_values)
    exposed_buffer=deepcopy(original_buffer)
    masks=[]
    if mode == "mask_both":
        for key in TARGET_KEYS:
            exposed_effects.stats[key][1][:] = prior_stats[key][1]
            masks.append("effects.mean."+key[0])
    if mode == "mask_td":
        exposed_values=deepcopy(prior_values)
        masks.append("values.3x6")
    if mode == "mask_buffer":
        # Non-factual sentinel, not a fabricated episode. This is a READ
        # mask and must never execute learning/replay while installed.
        exposed_buffer=deque([None],maxlen=original_buffer.maxlen)
        masks.append("buffer.content.one_null")
    # For sham, sham_state: exact copies; for full: original object paths.
    if mode!="full":
        mind.effects=exposed_effects
        mind.values=exposed_values
        mind.buffer=exposed_buffer
    exposed=C.seal_mind(mind)
    original_fields=I.private_fields(before)
    during_fields=I.private_fields(exposed)
    changed={field for field in original_fields if original_fields[field]!=during_fields[field]}
    expected={
        "full":set(),"sham":set(),"mask_both":{"effects"},
        "sham_state":set(),"mask_td":{"values"},"mask_buffer":{"buffer"},
    }[mode]
    if changed!=expected:
        raise AssertionError("temporary readout modified an unregistered private field")
    if mode=="mask_both":
        masked=I.observed_stats(exposed)
        if any(masked[key][0]!=learned_stats[key][0] or
               masked[key][2]!=learned_stats[key][2] or
               masked[key][1]!=prior_stats[key][1] for key in TARGET_KEYS):
            raise AssertionError("mean readout changed count or used invented prior")
    decision=CognitiveBudget(world.body,world.laws)
    action,param,work,info=mind.decide(cap,decision)
    after_read=C.seal_mind(mind)
    if (decision.work!=work or world.t!=1 or
            I.observed_stats(after_read)!=I.observed_stats(exposed)):
        raise AssertionError("decision escaped its real prepaid memory readout")
    if (mind.values!=exposed_values or
            list(mind.buffer)!=list(exposed_buffer)):
        raise AssertionError("decision unexpectedly mutated TD/buffer readout")
    mind.effects=original_effects
    mind.values=original_values
    mind.buffer=original_buffer
    after_restore=C.seal_mind(mind)
    if (I.observed_stats(after_restore)!=learned_stats or
            mind.values!=learned_values or
            len(mind.buffer)!=1 or list(mind.buffer)!=list(original_buffer)):
        raise AssertionError("learned F1C content was not restored in living Mind")
    energy,vigilance=cognitive_cost(world.laws,work)
    native=world.step(action,param,work)
    if world.t!=2 or (list(native["body"])!=list(world.body)):
        raise AssertionError("not a real native second step")
    for coin,value in (("energy",energy),("vigilance",vigilance)):
        bill=native["cognitive_accounting"][coin]
        if (abs(bill["paid"]-value)>1e-10 or
                abs(bill["requested"]-value)>1e-10 or bill["unpaid"]!=0):
            raise AssertionError("native two-currency decision was not fully paid")
    if (mind.effects.stats!=original_effects.stats or
            mind.values!=learned_values or list(mind.buffer)!=list(original_buffer)):
        raise AssertionError("physical World.step rewrote genuine learned Mind")
    return {
        "mode":mode,"allowed_temporary_masks":masks,
        "before_world":before_world,
        "before_mind":before,
        "first_person_capture":json.loads(C.canonical(cap)),
        "capture_sha256":C.digest(cap),
        "effective_readout_mind":exposed,
        "post_decision_exposed_mind":after_read,
        "post_decision_restored_mind":after_restore,
        "action":action,"param":param,
        "decision_info":json.loads(C.canonical(info)),
        "cognitive_work":asdict(work),
        "prepaid_allowance_remaining":list(decision.remaining),
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


def finish_receipt(row):
    row["receipt_sha256"]=C.digest(row)
    return row


def case_gate(rows):
    full=rows["full"];sham=rows["sham"]
    parity=all(
       all(row[attr]==full[attr] for attr in (
           "before_world","before_mind","first_person_capture","capture_sha256",
           "cognitive_work","prepaid_allowance_remaining",
           "expected_native_cognitive_cost","native_bill"))
       for row in rows.values())
    sham_neutral=all(sham[key]==full[key] for key in (
        "action","param","decision_info","cognitive_work",
        "native_bill","native_second_step","after_world",
        "post_decision_restored_mind"))
    return parity,sham_neutral


def produce(original):
    reference=authentic_reference(original)
    cases=[]
    for case in X.ECOLOGIES:
        world,mind,origin=X.native_original_paid_source(original,case)
        rows={}
        for mode in MODES_F1F:
            rows[mode]=finish_receipt(actual_paid_second_choice(
               deepcopy(world),deepcopy(mind),mode,original,reference))
        parity,sham=case_gate(rows)
        changed=(rows["full"]["action"],rows["full"]["param"])!=(
            rows["mask_both"]["action"],rows["mask_both"]["param"])
        row={
            "context":X.describe(case),
            "source":origin,
            "arms":rows,
            "native_work_and_bills_exact_equal":parity,
            "sham_neutral":sham,
            "valid_equal_cost_pair":bool(parity and sham),
            "mean_content_motor_difference":changed if parity and sham else None,
        }
        row["case_sha256"]=C.digest(row)
        cases.append(row)
    valid=sum(row["valid_equal_cost_pair"] for row in cases)
    changed=sum(row["mean_content_motor_difference"] is True for row in cases)
    verdict=("INCONCLUSIVE_ECOLOGY_COST_GATE" if valid!=len(X.ECOLOGIES)
             else ("NO_MEAN_CONTENT_MOTOR_EFFECT_IN_EIGHT_PREREGISTERED_ECOLOGIES"
                   if changed==0 else
                   "MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES"))
    report={
        "schema":SCHEMA,"source_main":SOURCE_MAIN,
        "f1c_source_original_sha256":SOURCE_F1C_SHA,
        "f1c_original_provenance_chain_sha256":original["provenance_chain_sha256"],
        "evidence_class":"SYNTHETIC_PREREGISTERED_EIGHT_ECOLOGICAL_WORLDS_NOT_G2",
        "study":"F1F_MEAN_READOUT_ONLY",
        "frozen_f1d_motor_status":F1D_NEGATIVE,
        "frozen_f1e_motor_status":F1E_NEGATIVE,
        "frozen_stage8e2":STAGE8E2_NEGATIVE,
        "preregistered_eco_names":[c[0] for c in X.ECOLOGIES],
        "arms_per_context":list(MODES_F1F),
        "per_context_native_first_step_count":1,
        "per_context_native_second_step_count":len(MODES_F1F),
        "native_step_calls":len(X.ECOLOGIES)*(1+len(MODES_F1F)),
        "native_full_lives_created":0,"new_scientific_cohorts":0,
        "run_life_executed":False,"historical_G2_Mind_reconstructed":False,
        "eight_contexts_valid_cost_pairs":valid,
        "eight_contexts_with_motor_change":changed,
        "primary_verdict":verdict,
        "contexts":cases,
    }
    report["provenance_chain_sha256"]=C.digest({
        "source_main":SOURCE_MAIN,
        "source_f1c":SOURCE_F1C_SHA,
        "original_chain":original["provenance_chain_sha256"],
        "eight_cases":[row["case_sha256"] for row in cases]
    })
    return report


def main():
    p=argparse.ArgumentParser(description="F1F original F1C across eight ecologies, no births")
    p.add_argument("--f1c-original",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    original=D.read_f1c_exact(args.f1c_original)
    r=produce(original)
    with Path(args.output).open("xb") as out:
        out.write(C.canonical(r))
    print(json.dumps({
        "primary_verdict":r["primary_verdict"],
        "valid_equal_cost_ecologies":r["eight_contexts_valid_cost_pairs"],
        "motor_changed_ecologies":r["eight_contexts_with_motor_change"],
        "native_world_steps":r["native_step_calls"],
        "actions":{x["context"]["id"]:{
            m:[x["arms"][m]["action"],x["arms"][m]["param"]] for m in MODES_F1F
        } for x in r["contexts"]},
        "sha256":C.digest(r),
    },sort_keys=True))


if __name__=="__main__":
    main()
