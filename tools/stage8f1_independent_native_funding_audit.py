"""Independent source-and-physics verification of Stage8-F1 paired one-tick receipts.

Pure stdlib arithmetic. Never import World, Mind, the first-party reporter,
native runtime or any cohort generator. This is NOT an original-gzip audit.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

SCHEMA="i3-stage8f1-development-native-matched-one-tick-evidence/v0"
SOURCE="4014a59027cc53bcfb6e7a9c6e6c827e017711b9"
P13="03faff4b9c194a5288b92e394f6a75cbe62cd095"
NEGATIVE="STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
ARMS=("candidate","equal_paid_discard","p13_reference")
CASES=("learned_beneficial_sleep","learned_adverse_sleep",
       "no_learned_effect","unaffordable_micro_energy",
       "unaffordable_micro_vigilance","water_visible_motor_unaffordable",
       "terminal_food_not_rescued","reference_funded_unchanged")
WORK=("cycles","simulated_steps","memory_items","replays")
MICRO={"cycles":1,"simulated_steps":0,"memory_items":64,"replays":0}
TOL=1e-8


def c(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False,
                      ensure_ascii=False).encode("utf8")


def h(obj):
    return sha256(c(obj)).hexdigest()


def close(a,b):
    return (type(a) in (int,float) and type(b) in (int,float) and
            math.isfinite(a) and math.isfinite(b) and
            math.isclose(a,b,rel_tol=1e-10,abs_tol=TOL))


def eq_body(actual,expected,description):
    if len(actual)!=5 or len(expected)!=5 or any(
        not close(x,y) for x,y in zip(actual,expected)):
        raise ValueError("native physical body mismatch: "+description)


def clamp(x):
    return min(100.,max(0.,x))


def recalc_physics(before,work,action,source_visible):
    """Independent BodyLaws v2 default one-tick arithmetic from the receipt."""
    cy,ss,mi,rp=(work[k] for k in WORK)
    e_bill=cy*.02+ss*.002+mi*.0002+rp*.005
    v_bill=cy*.05+ss*.002+rp*.01
    e,f,water,i,v=before
    if e_bill>e+TOL or v_bill>v+TOL:
        raise ValueError("cognitive charge would borrow future body resources")
    e-=e_bill
    v-=v_bill
    f=clamp(f-.2)
    water=clamp(water-.4)
    hydrated=water>=.05
    if action=="dormir":
        restore=min(3.,max(0.,100.-e))
        gain=min(restore,f/.05) if hydrated else 0.
        e+=gain
        f-=gain*.05
        v+=4.
    elif action in ("se_deplacer","collecter","manger","boire","attendre"):
        e-={"se_deplacer":2.,"collecter":1.,"manger":.5,
            "boire":.5,"attendre":.35}[action]
        if e < -TOL:
            raise ValueError("unpaid physical motor debit")
    elif action is not None:
        raise ValueError("invalid native motor action")
    if action in ("attendre","dormir") and hydrated:
        repair=min(.2,max(0.,100.-i),f/.10)
        i+=repair
        f-=repair*.1
    if action=="boire":
        if not source_visible:
            raise ValueError("drinking unavailable hidden or empty water")
        water+=25.
    out=[clamp(x) for x in (e,f,water,i,v)]
    dead=[label for label,idx in (("zero_food",1),("zero_water",2),
                                 ("zero_integrity",3)) if out[idx]<=0]
    return out,dead,{"energy":e_bill,"vigilance":v_bill}


def audit(full, source_sha):
    if (type(full) is not dict or full.get("schema")!=SCHEMA
            or full.get("source_f1_baseline_head")!=SOURCE
            or full.get("immutable_historical_p13_engine_head")!=P13
            or full.get("frozen_negative_causal_stage8e2")!=NEGATIVE
            or full.get("evidence_class")!="SYNTHETIC_MATCHED_WORLD_STEP_ONE_TICK_NOT_A_LIFE"
            or full.get("full_lives_generated")!=0 or full.get("new_scientific_cohorts")!=0
            or full.get("synthetic_native_world_step_calls")!=24
            or full.get("independent_matched_cases")!=8
            or full.get("brain_learning_after_native_step")!="NOT_EXECUTED"
            or full.get("native_life_manifest_or_evidence_chain")!="NOT_CLAIMED"
            or full.get("matched_pairs")!=["candidate","equal_paid_discard"]
            or full.get("reference_is_not_equal_cost_control") is not True
            or [x["case"] for x in full.get("scenarios",[])]!=list(CASES)):
        raise ValueError("not fixed, first-person, synthetic matched native evidence")
    report={"schema":"i3-stage8f1-independent-native-physical-two-currency-audit/v0",
            "status":"ALL_MATCHED_NATIVE_RECEIPTS_INDEPENDENTLY_ACCOUNTED_SOFTWARE_ONLY",
            "report_sha256":source_sha,
            "pairs_checked":0,"native_world_step_receipts_checked":0,
            "positive_micros":0,"unaffordable_micros":0,
            "fully_funded_reference_cases":0,
            "motor_choice_agrees_with_discarded_score":0,
            "matched_positive_bill_pairs":0,
            "native_death_cases":0,
            "no_native_lives":True,
            "historical_causal_status":NEGATIVE,
            "case_results":[]}
    receipts=[]
    for row in full["scenarios"]:
        name=row["case"]
        initial=row["synthetic_predecision_state"]
        if (type(initial.get("body")) is not list or len(initial["body"])!=5
                or initial.get("start_tick")!=0 or initial.get("started_dead") is not False
                or h(initial["capture"])!=initial.get("capture_sha256")
                or initial["capture"]["body"]!=initial["body"]
                or len(initial.get("private_mind_sha256",""))!=64
                or not row.get("same_predecision_body_capture_private_mind")
                or not row.get("same_native_cognitive_bill_candidate_vs_discard")
                or not row.get("same_budget_work_and_remaining_candidate_vs_discard")
                or row.get("original_first_person_lives_created")!=0
                or row.get("p13_is_NOT_cost_matched_to_micro_branch") is not True
                or set(row.get("runs",{}))!=set(ARMS)):
            raise ValueError("incomplete shared native perception or private state")
        arm=row["runs"]
        receipts.append([])
        for arm_name in ARMS:
            r=arm[arm_name]
            proof={k:v for k,v in r.items() if k!="receipt_sha256"}
            if h(proof)!=r["receipt_sha256"]:
                raise ValueError("altered or unsealed original native one-step receipt")
            receipts[-1].append(r["receipt_sha256"])
            if (r["mind_predecision_sha256"]!=initial["private_mind_sha256"]
                    or r["capture_sha256"]!=initial["capture_sha256"]
                    or r["before_body"]!=initial["body"]):
                raise ValueError("non-matched individual mind/body/perception")
            work=r["returned_work"]
            if (set(work)!=set(WORK) or r["budget_work"]!=work
                    or any(type(v) is not int or v<0 for v in work.values())):
                raise ValueError("failed work quantity conservation")
            real=r["native_step_result"]
            if real["t"]!=1 or len(real["body"])!=5:
                raise ValueError("a postmortem or invented extra World step")
            body_calc,death,paid=recalc_physics(
                initial["body"],work,r["action"],initial["capture"]["here"][0])
            eq_body(real["body"],body_calc,name+"/"+arm_name)
            if real["dead"]!=death:
                raise ValueError("wrong actual native death or censorship")
            if real["moved"]!=(r["action"]=="se_deplacer"):
                raise ValueError("wrong actual native motor movement")
            if r["action"] is None and r["param"] is not None:
                raise ValueError("motor params present without command")
            if r["action"]=="se_deplacer":
                dxdy={"N":(0,-1),"E":(1,0),"S":(0,1),"W":(-1,0)}
                if r["param"] not in dxdy:
                    raise ValueError("non-first-person direction")
                intended=[1+dxdy[r["param"]][0],1+dxdy[r["param"]][1]]
            else:
                intended=[1,1]
            if real["world_position"]!=intended:
                raise ValueError("world motor position not conserved")
            expected_balance=list(initial["body"])
            expected_balance[0]-=paid["energy"]
            expected_balance[4]-=paid["vigilance"]
            eq_body(r["paid_allowance_remaining"],expected_balance,
                    "after genuinely charged cognition")
            for k in ("energy","vigilance"):
                a=real["cognitive_accounting"][k]
                if (set(a)!={"requested","paid","unpaid"}
                        or any(not close(a[x],paid[k]) for x in ("requested","paid"))
                        or not close(a["unpaid"],0.)
                        or not close(r["paid_native_bills"][k],paid[k])):
                    raise ValueError("World physical cognitive charge violates two-currency receipt")
            report["native_world_step_receipts_checked"]+=1
            if death:report["native_death_cases"]+=1
        a,b,r=(arm[x] for x in ARMS)
        for k in ("budget_work","paid_allowance_remaining","paid_native_bills"):
            if a[k]!=b[k]:
                raise ValueError("identical private computation not identically funded")
        if a["native_step_result"]["cognitive_accounting"]!=b["native_step_result"]["cognitive_accounting"]:
            raise ValueError("real World did not debit identical amounts in same-body pairing")
        if a["action"]!=b["action"]:
            if b["action"] is not None:
                raise ValueError("equal paid discard issued forbidden physical motor")
        if row["branch"]=="F1":
            if (a["budget_work"]!=MICRO or b["budget_work"]!=MICRO
                    or a["funding"] not in ("F1_PAID_SELF_SELECTED_ACTION",
                                           "F1_PAID_VOLUNTARY_ABSTENTION")
                    or b["funding"]!="F1_EQUAL_PAID_MICRO_RESULT_DISCARDED"
                    or b["action"] is not None
                    or b["computed_discarded_option"]!=a["option"]
                    or r["funding"]!="NO_PROCESSING_BUDGET"):
                raise ValueError("paid micro-or-discard choice not same source/controller")
            report["positive_micros"]+=1
            report["matched_positive_bill_pairs"]+=1
            report["motor_choice_agrees_with_discarded_score"]+=1
        elif row["branch"]=="UNFUNDED":
            if any(arm[x]["funding"]!="NO_PROCESSING_BUDGET"
                   or arm[x]["action"] is not None or
                   any(arm[x]["budget_work"][w] for w in WORK) for x in ARMS):
                raise ValueError("unfunded option or fake cognition")
            report["unaffordable_micros"]+=1
        elif row["branch"]=="REFERENCE":
            if (a["budget_work"]!=r["budget_work"]
                    or b["budget_work"]!=r["budget_work"]
                    or a["action"]!=r["action"] or b["action"]!=r["action"]
                    or a["funding"]!=r["funding"] or b["funding"]!=r["funding"]):
                raise ValueError("reference branch deviated under fully paid normal choice")
            report["fully_funded_reference_cases"]+=1
        else:
            raise ValueError("forbidden outcome promoted into native choice")
        report["pairs_checked"]+=1
        report["case_results"].append({
            "case":name,"branch":row["branch"],
            "candidate_action":a["action"],
            "candidate_funding":a["funding"],
            "control_action":b["action"],
            "p13_reference_action":r["action"],
            "candidate_paid_energy":a["paid_native_bills"]["energy"],
            "control_paid_energy":b["paid_native_bills"]["energy"],
            "candidate_paid_vigilance":a["paid_native_bills"]["vigilance"],
            "control_paid_vigilance":b["paid_native_bills"]["vigilance"],
            "native_body_after_action":a["native_step_result"]["body"],
            "native_body_after_discard":b["native_step_result"]["body"],
            "death_in_both_arms":(bool(a["native_step_result"]["dead"])
                                   and bool(b["native_step_result"]["dead"])),
        })
    chain=h({"source":SOURCE,"scenario_receipts":receipts})
    if chain != full.get("provenance_chain_sha256"):
        raise ValueError("complete 24-step receipt chain changed")
    if (report["pairs_checked"]!=8 or report["native_world_step_receipts_checked"]!=24
            or report["positive_micros"]!=5 or report["unaffordable_micros"]!=2
            or report["fully_funded_reference_cases"]!=1):
        raise ValueError("a preregistered synthetic case was silently removed")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("output")
    args=p.parse_args()
    raw=Path(args.input).read_bytes()
    result=audit(json.loads(raw),sha256(raw).hexdigest())
    with Path(args.output).open("xb") as f:
        f.write(c(result))
    print(json.dumps({"status":result["status"],"pairs":result["pairs_checked"],
                      "native_world_step_receipts":result["native_world_step_receipts_checked"],
                      "lives":0,"sha256":sha256(c(result)).hexdigest()},sort_keys=True))


if __name__=="__main__":
    main()
