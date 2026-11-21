"""Cold F1E independent stdlib-only proof of exactly equal cognitive cost.

NO engine, Mind, World, or producer imports. Re-read original F1C bytes and
recalculate native physical receipts, prepaid two-currency bills, and exactly
which original personal mean-values reached the decision readout.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1d_independent_next_decision_audit as D

SCHEMA="i3-stage8f1e-native-equal-cost-content-readout/v0"
SOURCE="3dd12c94843ca2cadf1af5c885b9eb215db31553"
F1C_SHA="e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d"
F1D_NEGATIVE="NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE"
NEGATIVE="STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
MODES=("full","sham","mask_both","mask_sleep_only","mask_global_only")
TARGET=(("dormir",),("*",))
KEYS={
    "full":(),"sham":(),
    "mask_both":TARGET,
    "mask_sleep_only":(("dormir",),),
    "mask_global_only":(("*",),),
}


def check(condition,reason):
    I.check(condition,"F1E COLD: "+reason)


def same_model_content_and_counts(original, effective, prior,learned,mode):
    """Nothing except the expressly masked mean values may be different."""
    base=I.private_fields(original)
    altered=I.private_fields(effective)
    check(base.keys()==altered.keys()
          and all(base[k]==altered[k] for k in base if k!="effects"),
          "readout changed RNG, buffer, TD values, genome or other private state")
    predicted=I.observed_stats(effective)
    check(set(predicted)==set(TARGET) and set(learned)==set(TARGET)
          and set(prior)==set(TARGET),"unknown or invented private effects keys")
    for key in TARGET:
        check(predicted[key][0] == learned[key][0]
              and predicted[key][2] == learned[key][2],
              "readout changed learned sample count or uncertainty")
        baseline=prior[key][1] if key in KEYS[mode] else learned[key][1]
        check(predicted[key][1] == baseline,
              "masked personal mean is not from the archived F1C first-person source")
    return predicted


def audit_one(row,mode,original,prior,learned):
    source=original["arms"]["retain"]
    check(row["mode"]==mode
          and row["source_f1c_retain_receipt_sha256"]==source["receipt_sha256"]
          and row["source_trained_mind_sha256"]==
              source["private_persisted_postaction"]["sha256"]
          and row["original_trained_effect_model_restored"] is True
          and row["second_learning_executed"] is False,
          "wrong original paid personal source, or unauthorized post-second learning")
    check(row["before_mind"]==source["private_persisted_postaction"],
          "one arm did not start with fully retained, PAID F1C history")
    baseline=I.observed_stats(row["before_mind"])
    check(baseline==learned,"actual trained effects were not shared by all arms")
    check(row["mean_only_intervention_keys"]==[list(k) for k in KEYS[mode]],
          "unregistered action mean mask")
    effective=I.observed_stats(row["effective_readout_mind"])
    same_model_content_and_counts(row["before_mind"],row["effective_readout_mind"],
                                  prior,learned,mode)
    post_mask=I.observed_stats(row["post_decision_before_restore"])
    check(post_mask==effective,"decision modified effects of temporary readout")
    actual_restored=I.observed_stats(row["post_decision_restored_mind"])
    check(actual_restored==learned,"counterfactual write escaped and modified real trained memory")
    first=I.private_fields(row["post_decision_before_restore"])
    second=I.private_fields(row["post_decision_restored_mind"])
    check(all(first[k]==second[k] for k in first if k!="effects"),
          "restoration rewrote non-effect Mind private state")
    check(row["next_capture"]["body"] == source["body_after_paid_learning"]
          and I.h(row["next_capture"])==row["capture_sha256"],
          "body/capture or first-person image differs from verified source")
    check(row["next_capture"]["here"]==[False,[]]
          and row["next_capture"]["neighbors"]==[[False,[]]]*4
          and row["next_capture"]["inventory"]==[],
          "unavailable world resources were injected")
    D._world(row["before_world"],tick=1,
             body=source["body_after_paid_learning"],pos=[1,1])
    check(row["before_world"]["body"]==row["next_capture"]["body"],
          "native World body differs from first-person body")
    work=row["actual_decision_work"]
    native_cost=I.cost(work)
    check(set(row["expected_cost"])=={"energy","vigilance"}
          and all(I.near(row["expected_cost"][coin],native_cost[coin])
                  for coin in native_cost),
          "non-native billing or false cognitive unit price")
    remaining=list(row["before_world"]["body"])
    remaining[0]-=native_cost["energy"]
    remaining[4]-=native_cost["vigilance"]
    check(remaining[0]>=0 and remaining[4]>=0,"cognitive debt or free energy")
    I.body_equal(row["remaining_after_paid_budget"],remaining,
                 "prepaid thought allowance")
    I.check_bill(row["actual_native_bill"],native_cost,
                 "next World.step exactly equal two-currency bill")
    second_world,death,moved,pos,_=D._physical_second(
        row["before_world"]["body"],work,row["actual_action"],row["actual_param"])
    step=row["native_second_step"]
    check(step["t"]==2 and step["moved"] is moved
          and step["dead"]==death,"World.step motor outcome/death fabricated")
    I.body_equal(step["body"],second_world,"native post-motor physiological result")
    D._world(row["after_world"],tick=2,body=second_world,pos=pos,dead=death)
    check(row["after_world"]["body"]==step["body"],
          "native world after the second tick falsified")
    check(type(row["actual_decision_info"]) is dict
          and row["actual_decision_info"].get("funding") is not None
          and row["actual_decision_info"].get("option") is not False,
          "not a genuine native decision-info receipt")
    check(row["receipt_sha256"]==I.h({
          k:v for k,v in row.items() if k!="receipt_sha256"}),
          "hash of true native evidence receipt changed")
    return native_cost


def classification(a,b):
    if [a["actual_action"],a["actual_param"]]==[
            b["actual_action"],b["actual_param"]]:
        return "NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE"
    return "EQUAL_COST_CONTENT_CAUSES_DIFFERENT_NEXT_MOTOR_COMMAND_IN_THIS_CASE"


def audit(report,original):
    check(type(report) is dict and report.get("schema")==SCHEMA
          and report.get("source_main_sha256")==SOURCE
          and report.get("evidence_class")=="SOFTWARE_ONLY_SYNTHETIC_EQUAL_COST_READOUT_NOT_G2"
          and report.get("f1c_original_json_sha256")==F1C_SHA
          and report.get("f1c_original_provenance_chain_sha256")==
              original.get("provenance_chain_sha256")
          and report.get("f1d_original_primary_motor_verdict_unchanged")==F1D_NEGATIVE
          and report.get("stage8e2_frozen_causal_status")==NEGATIVE
          and report.get("source_case")=="learned_beneficial_sleep"
          and report.get("preexposed_conditions")==list(MODES)
          and report.get("original_f1c_native_world_step_reconstructions")==1
          and report.get("new_native_world_step_calls")==len(MODES)
          and report.get("new_native_full_lives")==0
          and report.get("new_scientific_cohorts")==0
          and report.get("run_life_executed") is False
          and report.get("historical_g2_memory_equivalence")=="NOT_DEMONSTRATED"
          and report.get("full_native_life_chain")=="NOT_CLAIMED"
          and report.get("future_survival_or_heritability_effect")=="NOT_TESTED"
          and report.get("intervention")==
              "counterfactual_personal_mean_readout_only_same_learned_counts_and_memory"
          and type(report.get("arms")) is dict
          and set(report["arms"])==set(MODES),
          "wrong preexposure source, F1C original, policy limits or arm count")
    check(I.h(original)==F1C_SHA,"wrong original F1C JSON bytes or contents")
    reduced=I.audit(original,F1C_SHA)
    check(reduced["status"]=="SOFTWARE_ONLY_NATIVE_POSTACTION_PAID_LEARNING_RETENTION_PASS",
          "original source never passed F1C cold physical audit")
    source=original["arms"]["retain"]
    prior=I.observed_stats(source["private_before_postaction_learning"])
    learned=I.observed_stats(source["private_persisted_postaction"])
    check(set(prior)==set(learned)==set(TARGET)
          and all(prior[k][0]==prior[k][2]==1 and
                  learned[k][0]==learned[k][2]==2 and
                  prior[k][1] != learned[k][1] for k in TARGET),
          "there is no original F1C personal numeric learned difference to isolate")
    costs={}
    for mode in MODES:
        costs[mode]=audit_one(report["arms"][mode],mode,original,prior,learned)
    full=report["arms"]["full"]
    for mode in MODES:
        x=report["arms"][mode]
        for name in ("before_world","before_mind","next_capture","capture_sha256",
                     "source_trained_mind_sha256","actual_decision_work",
                     "actual_native_bill","expected_cost","remaining_after_paid_budget"):
            check(x[name]==full[name],"world or exact paid work differs across arms: "+mode+"/"+name)
    check(report["all_next_decision_work_exact_equal"] is True
          and report["all_native_two_currency_bills_exact_equal"] is True
          and report["all_arms_source_memory_truly_paid_and_retained"] is True,
          "paid cognition parity flag is false")
    sham=report["arms"]["sham"]
    check(report["sham_control_neutral"] is True
          and sham["effective_readout_mind"]==full["effective_readout_mind"]
          and sham["actual_action"]==full["actual_action"]
          and sham["actual_param"]==full["actual_param"]
          and sham["post_decision_restored_mind"]==full["post_decision_restored_mind"]
          and sham["native_second_step"]==full["native_second_step"],
          "sham readout incorrectly changed real decision or body")
    masked=report["arms"]["mask_both"]
    check(masked["effective_readout_mind"]!=full["effective_readout_mind"],
          "content intervention was not actually exposed to the decision")
    primary=classification(full,masked)
    check(report["native_motor_effect_primary"]==primary,
          "retrospective promotion of an unchanged motor command")
    chain=I.h({"source":SOURCE,"f1c_source":F1C_SHA,
               "f1c_proof_chain":original["provenance_chain_sha256"],
               "receipts":[report["arms"][mode]["receipt_sha256"] for mode in MODES]})
    check(report["provenance_chain_sha256"]==chain,
          "source-to-decision chain has been changed")

    return {
        "schema":"i3-stage8f1e-cold-independent-equal-cost-content-audit/v0",
        "status":"F1E_NATIVE_EQUAL_COST_CONTENT_READOUT_COLD_AUDITED",
        "source_original_sha256":I.h(report),
        "exact_f1c_original_sha256":F1C_SHA,
        "source_case":"learned_beneficial_sleep",
        "number_of_preexposed_readouts":len(MODES),
        "native_second_step_receipts_verified":len(MODES),
        "original_paid_F1C_event_reconstructed":1,
        "next_work_all_exactly_equal":True,
        "next_native_energy_paid_each":costs["full"]["energy"],
        "next_native_vigilance_paid_each":costs["full"]["vigilance"],
        "original_f1c_learned_personal_sleep_energy_mean":learned[("dormir",)][1][0],
        "prior_personal_sleep_energy_mean":prior[("dormir",)][1][0],
        "true_content_next_motor":[full["actual_action"],full["actual_param"]],
        "masked_content_next_motor":[masked["actual_action"],masked["actual_param"]],
        "sham_native_decision_neutral":True,
        "primary_verdict":primary,
        "motor_content_effect_at_equal_cost_in_single_case":
            primary=="EQUAL_COST_CONTENT_CAUSES_DIFFERENT_NEXT_MOTOR_COMMAND_IN_THIS_CASE",
        "decision_option_by_readout":{
            mode:report["arms"][mode]["actual_decision_info"].get("option") for mode in MODES},
        "body_and_first_person_equal":True,
        "historical_G2_equivalence":False,
        "scientific_lives":0,"scientific_cohorts":0,
        "stage8e2_causal_verdict_unchanged":NEGATIVE
    }


def main():
    p=argparse.ArgumentParser(description="Stdlib-only F1E independent cold audit, no Mind/World imports")
    p.add_argument("source_json")
    p.add_argument("original_f1c_json")
    p.add_argument("result_json")
    args=p.parse_args()
    raw=Path(args.source_json).read_bytes()
    old_raw=Path(args.original_f1c_json).read_bytes()
    check(sha256(old_raw).hexdigest()==F1C_SHA,"F1C original exact bytes unavailable")
    result=audit(json.loads(raw),json.loads(old_raw))
    check(result["source_original_sha256"]==sha256(raw).hexdigest(),
          "F1E source original had noncanonical bytes")
    with Path(args.result_json).open("xb") as target:
        target.write(I.c(result))
    print(json.dumps({"status":result["status"],
                      "primary":result["primary_verdict"],
                      "five_native_second_receipts":result["native_second_step_receipts_verified"],
                      "energy_paid_each":result["next_native_energy_paid_each"],
                      "sha256":I.h(result)},sort_keys=True))


if __name__=="__main__":
    main()
