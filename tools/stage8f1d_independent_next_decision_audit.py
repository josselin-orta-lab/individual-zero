"""F1D cold reduction: stdlib-only, no World/Mind/decision-engine imports.

Re-check the EXACT previous F1C original, both post-learning Mind snapshots,
the two F1D native 2nd-tick bills and physical transitions, and classify
the motor effect independently. This reducer NEVER runs World.step.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import sqrt
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I

SCHEMA = "i3-stage8f1d-source-anchored-synthetic-next-decision/v0"
SOURCE = "6c4d433110f9960bd96b4b5716c214e0465f9214"
F1C_SHA = "e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d"
F1C_COLD = "754a4c06eeae546f1fe8900375323752056c1b660e1af89d6b4688419a8e1588"
NEGATIVE = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
MODES = ("retain", "discard_after_compute")
WORLD_NAME = "F1_SYNTHETIC_PAID_ONE_TICK_learned_beneficial_sleep"
# World BodyLaws v2, independently copied from frozen native source.
LAWS = {
    "food_decay": .2, "water_decay": .4,
    "sleep_energy_gain": 3., "sleep_food_cost_per_energy": .05,
    "rest_integrity_gain": .2, "rest_food_cost_per_integrity": .1,
    "min_water_for_metabolism": .05,
    "energy_per_cycle": .02, "energy_per_simulated_step": .002,
    "energy_per_memory_item": .0002, "energy_per_replay": .005,
    "vigilance_per_cycle": .05, "vigilance_per_simulated_step": .002,
    "vigilance_per_replay": .01, "sleep_vigilance_gain": 4.,
    "version": "i3-body-laws-v2",
}


def check(cond, msg):
    I.check(cond, "F1D independent audit: "+msg)


def fingerprint(x):
    return I.h(x)


def _world(w, *, tick, body, pos, dead=()):
    check(w["t"] == tick, "native time is not exactly two ticks")
    I.body_equal(w["body"], body, "body/world snapshot agreement")
    check(w["position"] == pos and w["dead"] == list(dead),
          "world position or vital death is altered")
    check(w["inventory"] == [] and w["water_cells"] == []
          and w["food_cells"] == [] and w["hidden_effects"] == [],
          "unexpected resources, stocks or private-world intervention")
    spec = w["world_spec"]
    check(spec == {"name": WORLD_NAME, "width": 3, "height": 3,
                   "spawn": [1, 1], "laws": LAWS},
          "original world physics/source changed")


def _physical_second(before, work, action, param):
    """Pure native BodyLaws-v2 arithmetic for the frozen resource-empty case."""
    bill = I.cost(work)
    energy, food, water, integrity, vigilance = before
    check(energy >= bill["energy"] and vigilance >= bill["vigilance"],
          "decision is not fully fundable in both currencies")
    energy -= bill["energy"]
    vigilance -= bill["vigilance"]
    hydrated = (water - .4) >= .05
    food = I.clamp(food - .2)
    water = I.clamp(water - .4)
    moved = False
    pos = [1, 1]
    if action == "dormir":
        check(param is None, "sleep forced a parameter")
        gain = (min(3., max(0., 100. - energy), food / .05)
                if hydrated else 0.)
        energy += gain
        food -= gain * .05
        vigilance += 4.
        if hydrated:
            repair = min(.2, max(0., 100. - integrity), food / .1)
            integrity += repair
            food -= repair * .1
    elif action == "attendre":
        check(param is None and energy >= .35, "invalid or unfunded wait")
        energy -= .35
        if hydrated:
            repair = min(.2, max(0., 100. - integrity), food / .1)
            integrity += repair
            food -= repair * .1
    elif action == "se_deplacer":
        check(param in {"N", "E", "S", "W"} and energy >= 2.,
              "invalid or unfunded move")
        energy -= 2.
        dx, dy = {"N":(0,-1),"E":(1,0),"S":(0,1),"W":(-1,0)}[param]
        pos=[1+dx,1+dy]
        check(0<=pos[0]<3 and 0<=pos[1]<3, "move exits frozen native world")
        moved=True
    else:
        check(action is None and param is None,
              "unknown/unsupported motor source in resource-empty world")
    after = list(map(I.clamp, (energy, food, water, integrity, vigilance)))
    dead = [n for n, idx in (("zero_food",1),("zero_water",2),("zero_integrity",3))
            if after[idx] <= 0.]
    return after, dead, moved, pos, bill


def _forecast(snapshot):
    stats=I.observed_stats(snapshot)
    s=stats.get(("dormir",))
    n=s[0] if s is not None else 0.
    source=None
    for key in (("dormir",),("dormir",None),("*",)):
        t=stats.get(key)
        if t and t[0] > 0:
            source=t[1]
            break
    return {"mean_delta":source or [0.]*5,
            "uncertainty":1. / sqrt(1.+n) if source else 1.}


def _receipt(row, previous, mode):
    check(row["mode"] == mode and row["next_learning_performed"] is False,
          "invalid native next-step mode or unregistered second learning")
    check(row["f1c_original_receipt_sha256"] == previous["receipt_sha256"],
          "wrong paid learning origin")
    check(row["f1c_original_persisted_mind_sha256"] ==
          previous["private_persisted_postaction"]["sha256"],
          "wrong predecision Mind origin")
    check(row["before_mind"] == previous["private_persisted_postaction"],
          "mutated original personal memory or private RNG")
    I.private_fields(row["before_mind"])
    I.private_fields(row["mind_after_decision"])
    check(row["observer_only_sleep_forecast"] == _forecast(row["before_mind"]),
          "forecast cannot be recovered from the personal learned effects")
    check(row["next_capture"]["body"] ==
          previous["body_after_paid_learning"], "different first-person body")
    check(fingerprint(row["next_capture"])==row["next_capture_sha256"],
          "first-person capture hash modified")
    check(row["next_capture"]["here"] == [False,[]]
          and row["next_capture"]["neighbors"] == [[False,[]]]*4
          and row["next_capture"]["inventory"] == [],
          "next-decision perception contains unavailable resources")
    _world(row["before_world"], tick=1, body=previous["body_after_paid_learning"],
           pos=[1,1])
    check(row["before_world"]["body"] == row["next_capture"]["body"],
          "world and first-person bodily perception differ")
    work = row["decision_work"]
    expected = I.cost(work)
    for k in ("energy","vigilance"):
        check(I.near(row["expected_native_cognitive_debit"][k], expected[k]),
              "declared cognitive computation rate changed")
    remaining = list(row["before_world"]["body"])
    remaining[0]-=expected["energy"]
    remaining[4]-=expected["vigilance"]
    I.body_equal(row["decision_allowance_remaining"],remaining,
                 "next-decision prepaid allowance")
    step = row["actual_native_step"]
    check(step["t"] == 2, "native second tick was skipped")
    I.check_bill(step["cognitive_accounting"], expected, "2nd native Mind/World bill")
    after, dead, moved, pos, _ = _physical_second(
        row["before_world"]["body"], work, row["action"], row["param"])
    I.body_equal(step["body"], after, "second funded native bodily transition")
    check(step["dead"]==dead and step["moved"] is moved,
          "new motor or death state was fabricated")
    _world(row["after_world"],tick=2,body=after,pos=pos,dead=dead)
    check(row["after_world"]["body"]==step["body"],
          "post-transition physical state not preserved")
    check(type(row["decision_info"]) is dict
          and "funding" in row["decision_info"]
          and row["decision_info"].get("option") is not False,
          "missing genuine native decision metadata")
    check(row["receipt_sha256"] == fingerprint({
          k:v for k,v in row.items() if k!="receipt_sha256"}),
          "individual native 2nd-step receipt was modified")


def classify(retain,discard):
    delta=(retain["action"],retain["param"]) != (
        discard["action"],discard["param"])
    eq_work=retain["decision_work"]==discard["decision_work"]
    eq_bill=retain["expected_native_cognitive_debit"]==discard["expected_native_cognitive_debit"]
    if not delta:
        return "NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE"
    return ("NEXT_MOTOR_DECISION_EFFECT_OBSERVED_COST_MATCHED"
            if eq_work and eq_bill else
            "NEXT_MOTOR_DECISION_DIFFERENCE_WITH_UNEQUAL_COGNITION")


def audit(report,original):
    check(type(report) is dict and report.get("schema")==SCHEMA
          and report.get("source_anchor_main_sha")==SOURCE
          and report.get("f1c_original_json_sha256")==F1C_SHA
          and report.get("f1c_independent_cold_json_sha256")==F1C_COLD
          and report.get("frozen_stage8e2")==NEGATIVE
          and report.get("evidence_class")=="SOFTWARE_ONLY_SYNTHETIC_TWO_TICKS_NO_G2_HISTORY"
          and report.get("source_case")=="learned_beneficial_sleep"
          and report.get("new_native_lives")==0
          and report.get("new_scientific_cohorts")==0
          and report.get("run_life_executed") is False
          and report.get("executed_native_world_step_calls")==4
          and report.get("historical_g2_memory_equivalence")=="NOT_DEMONSTRATED"
          and report.get("gain_in_survival_or_heritability")=="NOT_TESTED"
          and report.get("whole_life_native_custody")=="NOT_CLAIMED"
          and type(report.get("arms")) is dict
          and set(report["arms"]) == set(MODES),
          "historical source, evidence class, or no-birth status altered")
    check(I.h(original)==F1C_SHA,
          "input is not the exact original F1C JSON")
    F1C_cold=I.audit(original,F1C_SHA)
    check(F1C_cold["status"]=="SOFTWARE_ONLY_NATIVE_POSTACTION_PAID_LEARNING_RETENTION_PASS"
          and report["f1c_provenance_chain_sha256"]==original["provenance_chain_sha256"],
          "unverified F1C native memory and physical origin")
    for mode in MODES:
        _receipt(report["arms"][mode],original["arms"][mode],mode)
    a,b=(report["arms"][mode] for mode in MODES)
    check(a["before_world"]==b["before_world"]
          and a["next_capture"]==b["next_capture"]
          and a["next_capture_sha256"]==b["next_capture_sha256"]
          and report["next_step_bodies_world_capture_equal"] is True
          and report["next_decision_same_native_world_laws"] is True,
          "candidate and discard have different bodily starting conditions")
    fa=I.private_fields(a["before_mind"])
    fb=I.private_fields(b["before_mind"])
    check(set(fa)==set(fb) and {k for k in fa if fa[k]!=fb[k]}
          == {"effects","values","buffer"}
          and report["predecision_different_mind_fields"]==[
              "buffer","effects","values"],
          "unobserved intervention beyond the learned native fields")
    choice_same=a["decision_info"].get("option")==b["decision_info"].get("option")
    work_equal=a["decision_work"]==b["decision_work"]
    bill_equal=a["expected_native_cognitive_debit"]==b["expected_native_cognitive_debit"]
    status=classify(a,b)
    check(report["observed_motor_effect_classification"]==status
          and report["next_option_same"] is choice_same
          and report["next_work_exactly_equal"] is work_equal
          and report["next_native_cognitive_debit_exactly_equal"] is bill_equal,
          "posthoc rewrite of primary motor-decision criterion")
    chain=I.h({"source":SOURCE,"f1c_json":F1C_SHA,
               "f1c_chain":original["provenance_chain_sha256"],
               "next_receipts":[report["arms"][mode]["receipt_sha256"]
                                for mode in MODES]})
    check(report["provenance_chain_sha256"]==chain,
          "tampered original-to-next decision evidence chain")
    return {
        "schema":"i3-stage8f1d-independent-stdlib-next-choice-audit/v0",
        "status":"F1D_NATIVE_SYNTHETIC_SECOND_CHOICE_REDUCED",
        "source_sha256": I.h(report),
        "f1c_exact_original_sha256": F1C_SHA,
        "paired_first_person_world_states": 1,
        "native_second_world_step_receipts_verified": 2,
        "origin_first_world_step_receipts_reproduced": 2,
        "retained_learned_effect_energy": a["observer_only_sleep_forecast"]["mean_delta"][0],
        "discarded_learned_effect_energy": b["observer_only_sleep_forecast"]["mean_delta"][0],
        "next_retain_action": [a["action"],a["param"]],
        "next_discard_action":[b["action"],b["param"]],
        "next_retain_decision_work":a["decision_work"],
        "next_discard_decision_work":b["decision_work"],
        "next_work_equal":work_equal,
        "next_native_bill_equal":bill_equal,
        "next_option_equal":choice_same,
        "primary_motor_verdict":status,
        "motor_effect_proved_in_this_case":
            status=="NEXT_MOTOR_DECISION_EFFECT_OBSERVED_COST_MATCHED",
        "historical_G2_decision_effect_proved": False,
        "survival_heritability_or_gamma_causality_proved": False,
        "stage8e2": NEGATIVE,
        "native_full_lives":0, "new_scientific_cohorts":0,
    }


def main():
    p=argparse.ArgumentParser(description="Cold F1D no-World independent audit")
    p.add_argument("f1d_source")
    p.add_argument("original_f1c")
    p.add_argument("output")
    args=p.parse_args()
    raw=Path(args.original_f1c).read_bytes()
    check(sha256(raw).hexdigest()==F1C_SHA,"F1C original SHA mismatch")
    report_raw=Path(args.f1d_source).read_bytes()
    result=audit(json.loads(report_raw),json.loads(raw))
    check(result["source_sha256"]==sha256(report_raw).hexdigest(),
          "noncanonical F1D original source")
    with Path(args.output).open("xb") as out:
        out.write(I.c(result))
    print(json.dumps({"audit":result["status"],
                      "primary_motor_verdict":result["primary_motor_verdict"],
                      "no_lives":0,
                      "sha256":I.h(result)},sort_keys=True))


if __name__=="__main__":
    main()
