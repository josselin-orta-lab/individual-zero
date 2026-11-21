"""F1E: causal mean-content readout intervention with exactly matched native costs.

All five experimental readouts start as deep copies of the SAME authentic
F1C retained, physically paid one-tick Mind/World. During the subsequent
native Mind.decide ONLY, a detached EffectsModel copy may expose the
pre-F1C personal means of ('dormir',) and/or ('*',) while preserving the
actual trained counts, data-shape, buffer, TD values and all other state.
The real learned EffectsModel is restored immediately after decision.
NO rule decides or overrides a motor action for the organism.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import json

from i3.modules.body import CognitiveBudget, CognitiveWork, cognitive_cost
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1d_next_decision_retention as D

SCHEMA = "i3-stage8f1e-native-equal-cost-content-readout/v0"
SOURCE = "3dd12c94843ca2cadf1af5c885b9eb215db31553"
F1C_ORIGINAL_SHA256 = D.F1C_ORIGINAL_SHA
F1D_NEGATIVE = "NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE"
STAGE8E2_NEGATIVE = C.NEGATIVE
MODES = ("full", "sham", "mask_both", "mask_sleep_only", "mask_global_only")
TARGET_KEYS = (("dormir",), ("*",))
KEYS_BY_MODE = {
    "full": (), "sham": (), "mask_both": TARGET_KEYS,
    "mask_sleep_only": (("dormir",),),
    "mask_global_only": (("*",),),
}


def old_and_new(original):
    """Only observed real F1C private snapshots supply either set of means."""
    retain = original["arms"]["retain"]
    prior = I.observed_stats(retain["private_before_postaction_learning"])
    learned = I.observed_stats(retain["private_persisted_postaction"])
    if set(prior) != set(learned) or set(prior) != set(TARGET_KEYS):
        raise AssertionError("changed F1C learned-effect keys")
    for key in TARGET_KEYS:
        n,m,c = prior[key]
        nn,mm,cc = learned[key]
        if (len(m)!=5 or len(mm)!=5 or n != 1 or c != 1 or
                nn != 2 or cc != 2 or m == mm):
            raise AssertionError("not an authentic changed two-observation F1C mean")
    return prior,learned


def _readout(world,mind,mode,prior,learned,original):
    if mode not in MODES:
        raise ValueError("non-predeclared readout mode")
    src=original["arms"]["retain"]
    pre=C.seal_mind(mind)
    if pre != src["private_persisted_postaction"]:
        raise AssertionError("counterfactual started from non-F1C trained private Mind")
    if list(world.body) != src["body_after_paid_learning"] or world.t!=1 or world.dead:
        raise AssertionError("not exact native F1C post-paid-learning body and tick")
    begin_world=D._snapshot_world(world)
    captured=world.capture()
    baseline=deepcopy(mind.effects)
    if baseline.stats != {k: deepcopy(v) for k,v in learned.items()}:
        raise AssertionError("native model differs from archived paid F1C evidence")
    # This is an observer intervention, not a computational shortcut or
    # replacement motor policy. Same stat KEYS/COUNTS/capacity/uncertainty.
    overlay=deepcopy(baseline)
    for key in KEYS_BY_MODE[mode]:
        overlay.stats[key][1][:] = prior[key][1]
    if mode == "sham":
        # Pass through the same isolated-copy branch with unchanged content.
        for key in TARGET_KEYS:
            overlay.stats[key][1][:] = learned[key][1]
    # Full is the unaltered native model; sham is an identity-valued clone.
    mind.effects = baseline if mode == "full" else overlay
    effective=C.seal_mind(mind)
    if dict(effective["data"]["private"]["__dict__"]) != {
            **dict(pre["data"]["private"]["__dict__"]),
            "effects": dict(effective["data"]["private"]["__dict__"])["effects"]}:
        raise AssertionError("content intervention affected fields outside model")
    active_stats=I.observed_stats(effective)
    for key in TARGET_KEYS:
        before=learned[key]
        during=active_stats[key]
        if during[0] != before[0] or during[2] != before[2]:
            raise AssertionError("the learned counts or confidence were altered")
        expected=prior[key][1] if key in KEYS_BY_MODE[mode] else learned[key][1]
        if during[1] != expected:
            raise AssertionError("unregistered mean-content replacement")

    grant=CognitiveBudget(world.body,world.laws)
    action,param,work,info=mind.decide(captured,grant)
    if work != grant.work or world.t!=1:
        raise AssertionError("unfunded decision or hidden motor tick")
    after_readout=C.seal_mind(mind)
    if I.observed_stats(after_readout) != active_stats:
        raise AssertionError("individual mutated effects during otherwise read-only decision")
    mind.effects=baseline
    restored=C.seal_mind(mind)
    if I.observed_stats(restored) != learned:
        raise AssertionError("the trained F1C memory was not restored after readout")
    expected_cost=cognitive_cost(world.laws,work)
    outcome=world.step(action,param,work)
    if world.t!=2:
        raise AssertionError("native paid second tick is missing")
    for name,expected in zip(("energy","vigilance"),expected_cost):
        row=outcome["cognitive_accounting"][name]
        if (abs(row["requested"]-expected)>1e-10
                or abs(row["paid"]-expected)>1e-10
                or row["unpaid"] != 0.0):
            raise AssertionError("native World did not debit the two-currency work")
    if I.observed_stats(C.seal_mind(mind)) != learned:
        raise AssertionError("a decision or motor outcome modified authentic F1C learning")
    record={
        "mode":mode,
        "source_f1c_retain_receipt_sha256":src["receipt_sha256"],
        "source_trained_mind_sha256":src["private_persisted_postaction"]["sha256"],
        "before_world":begin_world,
        "before_mind":pre,
        "next_capture":json.loads(C.canonical(captured)),
        "capture_sha256":C.digest(captured),
        "effective_readout_mind":effective,
        "mean_only_intervention_keys":[list(k) for k in KEYS_BY_MODE[mode]],
        "post_decision_before_restore":after_readout,
        "post_decision_restored_mind":restored,
        "actual_action":action,"actual_param":param,
        "actual_decision_info":json.loads(C.canonical(info)),
        "actual_decision_work":asdict(work),
        "actual_native_bill":deepcopy(outcome["cognitive_accounting"]),
        "expected_cost":{"energy":expected_cost[0],"vigilance":expected_cost[1]},
        "remaining_after_paid_budget":list(grant.remaining),
        "native_second_step":{
            "t":outcome["t"],"body":list(outcome["body"]),
            "moved":outcome["moved"],"dead":list(outcome["dead"])
        },
        "after_world":D._snapshot_world(world),
        "original_trained_effect_model_restored":True,
        "second_learning_executed":False,
    }
    record["receipt_sha256"]=C.digest(record)
    return record


def classification(a,b):
    if (a["actual_action"],a["actual_param"]) == (
            b["actual_action"],b["actual_param"]):
        return "NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE"
    return "EQUAL_COST_CONTENT_CAUSES_DIFFERENT_NEXT_MOTOR_COMMAND_IN_THIS_CASE"


def produce(original):
    # One F1C native World.step and paid postaction learning reconstructed,
    # then FIVE detached copies for pre-declared one-tick choice probes.
    world,mind=D._matched_state("retain",original)
    prior,learned=old_and_new(original)
    rows={}
    for mode in MODES:
        rows[mode]=_readout(deepcopy(world),deepcopy(mind),mode,prior,learned,original)
    full=rows["full"]
    for mode in MODES:
        row=rows[mode]
        for attr in ("before_world","before_mind","next_capture","capture_sha256",
                     "source_trained_mind_sha256","actual_decision_work","actual_native_bill",
                     "expected_cost","remaining_after_paid_budget"):
            if row[attr]!=full[attr]:
                raise AssertionError("equal-cost or same-world pairing failed: "+mode+"/"+attr)
        if row["before_mind"]!=original["arms"]["retain"]["private_persisted_postaction"]:
            raise AssertionError("F1C learned memory not preserved")
    if (rows["sham"]["effective_readout_mind"]!=rows["full"]["effective_readout_mind"]
            or rows["sham"]["actual_action"]!=rows["full"]["actual_action"]
            or rows["sham"]["actual_param"]!=rows["full"]["actual_param"]
            or rows["sham"]["post_decision_restored_mind"]!=rows["full"]["post_decision_restored_mind"]
            or rows["sham"]["native_second_step"]!=rows["full"]["native_second_step"]):
        raise AssertionError("INVALID_SHAM_NEUTRALITY")
    if rows["mask_both"]["effective_readout_mind"]==rows["full"]["effective_readout_mind"]:
        raise AssertionError("masked source means not actually changed")
    # Predeclared negative verdict is allowed; no search for favourable cases.
    verdict=classification(full,rows["mask_both"])
    report={
        "schema":SCHEMA,
        "source_main_sha256":SOURCE,
        "evidence_class":"SOFTWARE_ONLY_SYNTHETIC_EQUAL_COST_READOUT_NOT_G2",
        "f1c_original_json_sha256":F1C_ORIGINAL_SHA256,
        "f1c_original_provenance_chain_sha256":original["provenance_chain_sha256"],
        "f1d_original_primary_motor_verdict_unchanged":F1D_NEGATIVE,
        "stage8e2_frozen_causal_status":STAGE8E2_NEGATIVE,
        "preexposed_conditions":list(MODES),
        "source_case":"learned_beneficial_sleep",
        "intervention":"counterfactual_personal_mean_readout_only_same_learned_counts_and_memory",
        "original_f1c_native_world_step_reconstructions":1,
        "new_native_world_step_calls":len(MODES),
        "new_native_full_lives":0,
        "new_scientific_cohorts":0,
        "run_life_executed":False,
        "historical_g2_memory_equivalence":"NOT_DEMONSTRATED",
        "future_survival_or_heritability_effect":"NOT_TESTED",
        "full_native_life_chain":"NOT_CLAIMED",
        "all_next_decision_work_exact_equal":True,
        "all_native_two_currency_bills_exact_equal":True,
        "all_arms_source_memory_truly_paid_and_retained":True,
        "native_motor_effect_primary":verdict,
        "sham_control_neutral":True,
        "arms":rows,
    }
    report["provenance_chain_sha256"]=C.digest({
        "source":SOURCE,
        "f1c_source":F1C_ORIGINAL_SHA256,
        "f1c_proof_chain":original["provenance_chain_sha256"],
        "receipts":[rows[m]["receipt_sha256"] for m in MODES]
    })
    return report


def main():
    parser=argparse.ArgumentParser(description="F1E original F1C equal-cost memory readout, no new lives")
    parser.add_argument("--f1c-original",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    original=D.read_f1c_exact(args.f1c_original)
    result=produce(original)
    with Path(args.output).open("xb") as stream:
        stream.write(C.canonical(result))
    print(json.dumps({
        "status":result["native_motor_effect_primary"],
        "actual_native_steps":result["original_f1c_native_world_step_reconstructions"]+result["new_native_world_step_calls"],
        "next_native_bill":result["arms"]["full"]["expected_cost"],
        "next_actions":{m:[result["arms"][m]["actual_action"],result["arms"][m]["actual_param"]] for m in MODES},
        "no_lives":result["new_native_full_lives"],
        "sha256":C.digest(result),
    },sort_keys=True))


if __name__=="__main__":
    main()
