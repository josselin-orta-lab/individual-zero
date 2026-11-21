"""F1G separate pre-exposed causal TD and episodic-buffer readout controls.

Eight ecological WorldSpecs fixed BEFORE results F1F, same F1C original Mind
and genuinely funded post-action outcome update. Each context has ONE
independent full, sham, TD readout and episodic-buffer content mask.
No selective focus on the positive F1F ecology, no motor action forced, no
new life, no imagined G2 private checkpoint.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1f_ecological_mean_readout as F
from tools import stage8f1f_native_ecological_contexts as X

SCHEMA="i3-stage8f1g-eight-ecologies-separate-td-buffer-native-proof/v0"
SOURCE_MAIN=F.SOURCE_MAIN
IMPLEMENTATION_BASE="f6c86019df2800e5584f1b047746e093c4d17abe"
F1F_FIXED_ORIGINAL_SHA256="f620d1b46ddf269dc368dcd90ba6c93f44f0b6442f8d9e6322440de32e3fbab5"
F1F_FIXED_COLD_SHA256="8013f2add1f3eb0190127bb77eac588c95f153f32ba21113302bafa0292e2ac2"
F1F_FIXED_K=1
SOURCE_F1C_SHA=D.F1C_ORIGINAL_SHA
MODES=F.MODES_F1G
CONTROLS=("mask_td","mask_buffer")
E2=F.STAGE8E2_NEGATIVE


def gate(arms):
    full,sham=(arms[x] for x in ("full","sham_state"))
    comparable_fields=(
        "before_world","before_mind","first_person_capture","capture_sha256",
        "cognitive_work","prepaid_allowance_remaining",
        "native_bill","expected_native_cognitive_cost"
    )
    same_work_and_currency=all(
        all(row[f]==full[f] for f in comparable_fields)
        for row in arms.values())
    sham_neutral=all(sham[f]==full[f] for f in (
        "action","param","decision_info","cognitive_work","native_bill",
        "native_second_step","after_world","post_decision_restored_mind"))
    return same_work_and_currency,sham_neutral


def produce(original):
    ref=F.authentic_reference(original)
    cases=[]
    for case in X.ECOLOGIES:
        world,mind,source=X.native_original_paid_source(original,case)
        arms={}
        for mode in MODES:
            arms[mode]=F.finish_receipt(F.actual_paid_second_choice(
                deepcopy(world),deepcopy(mind),mode,original,ref))
        work_equal,sham=gate(arms)
        eligible=bool(work_equal and sham)
        delta_td=(arms["full"]["action"],arms["full"]["param"])!=(
            arms["mask_td"]["action"],arms["mask_td"]["param"])
        delta_buf=(arms["full"]["action"],arms["full"]["param"])!=(
            arms["mask_buffer"]["action"],arms["mask_buffer"]["param"])
        case_row={
            "context":X.describe(case),
            "source":source,
            "arms":arms,
            "same_work_and_two_currencies_across_all_four_arms":work_equal,
            "identity_sham_neutral":sham,
            "all_four_arms_matched_valid":eligible,
            "td_content_motor_changed":delta_td if eligible else None,
            "buffer_content_motor_changed":delta_buf if eligible else None,
        }
        case_row["case_sha256"]=C.digest(case_row)
        cases.append(case_row)
    valid=sum(x["all_four_arms_matched_valid"] for x in cases)
    k_td=sum(x["td_content_motor_changed"] is True for x in cases)
    k_buffer=sum(x["buffer_content_motor_changed"] is True for x in cases)
    if valid!=len(X.ECOLOGIES):
        result="INCONCLUSIVE_TD_OR_BUFFER_COST_GATE"
        td_status=buffer_status=result
    else:
        result="TWO_SEPARATE_TD_BUFFER_CONTENT_COST_GATES_EVALUATED"
        td_status=("TD_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_ECOLOGIES"
                   if k_td else "NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES")
        buffer_status=("BUFFER_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_ECOLOGIES"
                       if k_buffer else "NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES")
    report={
        "schema":SCHEMA,
        "source_main":SOURCE_MAIN,
        "f1g_implementation_base":IMPLEMENTATION_BASE,
        "f1g_preexposure_document_commit":
            "82d3dc015b5d89ce52b1abc632e7a6a1a52d01b7",
        "f1c_source_original_sha256":SOURCE_F1C_SHA,
        "f1c_original_provenance_chain_sha256":original["provenance_chain_sha256"],
        "f1f_fixed_original_sha256":F1F_FIXED_ORIGINAL_SHA256,
        "f1f_fixed_cold_sha256":F1F_FIXED_COLD_SHA256,
        "f1f_previous_observed_motor_change_count":F1F_FIXED_K,
        "evidence_class":"SYNTHETIC_SEPARATE_TD_BUFFER_EIGHT_ECOLOGIES_NOT_G2",
        "study":"F1G_SEPARATE_TD_AND_BUFFER",
        "frozen_f1d_motor_status":F.F1D_NEGATIVE,
        "frozen_f1e_motor_status":F.F1E_NEGATIVE,
        "frozen_stage8e2":E2,
        "preregistered_eco_names":[v[0] for v in X.ECOLOGIES],
        "arms_per_context":list(MODES),
        "per_context_native_first_step_count":1,
        "per_context_native_second_step_count":len(MODES),
        "native_step_calls":len(X.ECOLOGIES)*(1+len(MODES)),
        "native_full_lives_created":0,
        "new_scientific_cohorts":0,
        "run_life_executed":False,
        "historical_G2_Mind_reconstructed":False,
        "valid_equal_cost_ecologies":valid,
        "td_content_motor_changed_ecologies":k_td,
        "buffer_content_motor_changed_ecologies":k_buffer,
        "primary_gate_status":result,
        "td_primary_verdict":td_status,
        "buffer_primary_verdict":buffer_status,
        "contexts":cases,
    }
    report["provenance_chain_sha256"]=C.digest({
        "study":SCHEMA,
        "source_main":SOURCE_MAIN,
        "implementation_base":IMPLEMENTATION_BASE,
        "source_f1c":SOURCE_F1C_SHA,
        "source_f1f":F1F_FIXED_ORIGINAL_SHA256,
        "original_chain":original["provenance_chain_sha256"],
        "eight_cases":[row["case_sha256"] for row in cases],
    })
    return report


def main():
    p=argparse.ArgumentParser(description="F1G separated TD and buffer native eight-ecology control")
    p.add_argument("--f1c-original",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    original=D.read_f1c_exact(args.f1c_original)
    result=produce(original)
    with Path(args.output).open("xb") as out:
        out.write(C.canonical(result))
    print(json.dumps({
        "primary_gate":result["primary_gate_status"],
        "td_verdict":result["td_primary_verdict"],
        "buffer_verdict":result["buffer_primary_verdict"],
        "equal_cost_ecologies":result["valid_equal_cost_ecologies"],
        "td_motor_changes":result["td_content_motor_changed_ecologies"],
        "buffer_motor_changes":result["buffer_content_motor_changed_ecologies"],
        "native_world_steps":result["native_step_calls"],
        "actions":{
            x["context"]["id"]:{
                m:[x["arms"][m]["action"],x["arms"][m]["param"]]
                for m in MODES}
            for x in result["contexts"]},
        "sha256":C.digest(result),
    },sort_keys=True))


if __name__=="__main__":
    main()
