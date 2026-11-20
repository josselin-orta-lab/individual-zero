"""Stage8-F1, source-bound, DEVELOPMENT ONLY, matched native one-tick funding.

No run_life, no births, no historical archive access, no learning after step.
Three actual World.step calls start from identical synthetic WorldSpec/body and
three minds cloned from the very same learned predecision state. The paid
candidate and equal-paid discard are the ONLY budget-matched pair.
P1.3 reference is an unequal-cost separate negative/compatibility comparator.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost, debit_cognition,
)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.stage8f1_paid_microdecision_mind import (
    CANDIDATE, EVIDENCE, MICRO_WORK, PaidMicrodecisionMind,
    PaidMicrodecisionEqualPaidDiscardMind,
)
from i3.modules.world import WaterSource, World, WorldSpec

SCHEMA = "i3-stage8f1-development-native-matched-one-tick-evidence/v0"
F1_HEAD = "4014a59027cc53bcfb6e7a9c6e6c827e017711b9"
REFERENCE_HEAD = "03faff4b9c194a5288b92e394f6a75cbe62cd095"
FROZEN_CAUSAL = "STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0"
ARM_NAMES = ("candidate", "equal_paid_discard", "p13_reference")
STATES = (
    # name, body (E F W I V), synthetic prior own-experience observations,
    # at_water, expected candidate action, expected branch
    ("learned_beneficial_sleep", (.052, 75., 60., 90., 95.),
     ((("dormir",), (3., -.15, -.4, .2, 4.)),), False, "dormir", "F1"),
    ("learned_adverse_sleep", (.052, 75., 60., 90., 95.),
     ((("dormir",), (-.4, -.3, -4., 0., 0.)),), False, None, "F1"),
    ("no_learned_effect", (.052, 75., 60., 90., 95.),
     (), False, None, "F1"),
    ("unaffordable_micro_energy", (.03, 75., 60., 90., 95.),
     ((("dormir",), (3., -.15, -.4, .2, 4.)),), False, None, "UNFUNDED"),
    ("unaffordable_micro_vigilance", (.052, 75., 60., 90., .03),
     ((("dormir",), (3., -.15, -.4, .2, 4.)),), False, None, "UNFUNDED"),
    ("water_visible_motor_unaffordable", (.052, 75., 20., 90., 95.),
     ((("dormir",), (-.4, -.3, -4., 0., 0.)),
      (("boire",), (0., 0., 35., 0., 0.))), True, None, "F1"),
    ("terminal_food_not_rescued", (.052, .15, 60., 90., 95.),
     ((("dormir",), (3., -.15, -.4, .2, 4.)),), False, None, "F1"),
    ("reference_funded_unchanged", (85., 75., 60., 90., 95.),
     ((("dormir",), (3., -.15, -.4, .2, 4.)),), False, None, "REFERENCE"),
)


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False,
                      ensure_ascii=False).encode("utf8")


def digest(obj) -> str:
    return sha256(canonical(obj)).hexdigest()


def close(a, b) -> bool:
    return (type(a) in (float, int) and type(b) in (float, int)
            and math.isfinite(a) and math.isfinite(b)
            and math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10))


def state_witness(m: Mind) -> dict:
    """Explicit serializable private state and learned predictions BEFORE decision."""
    return {
        "gammas":list(m.gammas),"theta":list(m.theta),"p":list(m.p),"w":list(m.w),
        "effects_stats":[{"key":list(k), "v":deepcopy(v)}
                         for k,v in sorted(m.effects.stats.items(),key=lambda x:repr(x[0]))],
        "map":repr(m.map),"hist":repr(m.hist),"visible":repr(m.visible),
        "pos":list(m.pos),"tokens":repr(m.tokens),"external":repr(m.external),
        "acc":repr(m.acc),"intention":m.intention,
        "buffer":repr(list(m.buffer)),"learned_values":deepcopy(m.values),
        "rng_state":repr(m.rng.getstate()),
        "budget_rng_state":repr(m._budget_rng.getstate()),
        "last":repr(m.last),
        "body_weights":list(m.w),
    }


def make_state(case):
    name,body,experiences,at_water,_,_=case
    spec=WorldSpec(
        name="F1_SYNTHETIC_PAID_ONE_TICK_"+name,
        width=3,height=3,spawn=(1,1),body=body,
        water={(1,1):WaterSource(gain=25.,stock=2,max_stock=2)}
              if at_water else {},
        laws=BodyLaws())
    w=World(spec)
    base=Mind(midpoint(),20261120)
    for key,delta in experiences:
        base.effects.observe(key,delta)
    return w,base


def cloned_mind(cls, original):
    m=cls(midpoint(),20261120)
    m.__dict__=deepcopy(original.__dict__)
    return m


def arm_run(world: World, mind: Mind, shared_digest: str):
    cap=world.capture()
    if digest(cap)!=shared_digest:
        raise AssertionError("not the same exact first-person perceptual World state")
    b=CognitiveBudget(world.body,world.laws)
    first_person_before=digest(state_witness(mind))
    before=tuple(world.body)
    action,param,work,info=mind.decide(cap,b)
    if work!=b.work:
        raise AssertionError("decision did not report exactly the prepaid work")
    if not isinstance(work,CognitiveWork):
        raise AssertionError("non-native cognitive work")
    own_cognitive_bill=cognitive_cost(world.laws,work)
    predicted_funded, predicted_account=debit_cognition(before,world.laws,work)
    if any(not close(predicted_funded[i],b.remaining[i]) for i in range(5)):
        raise AssertionError("CognitiveBudget and genuine original-body debit disagree")
    # Real native World step, not a modeled expectation or a fabricated debit.
    result=world.step(action,param,work)
    if result["t"]!=1 or world.t!=1 or world.body!=tuple(result["body"]):
        raise AssertionError("native World did not advance exactly one real step")
    for i,k in enumerate(("energy","vigilance")):
        entry=result["cognitive_accounting"][k]
        if (not close(entry["requested"],own_cognitive_bill[i])
                or not close(entry["paid"],own_cognitive_bill[i])
                or not close(entry["unpaid"],0.0)
                or not close(predicted_account[k]["paid"],entry["paid"])):
            raise AssertionError("World.step actual native paid cognition receipt is incorrect")
    proof={
        "capture_sha256":digest(cap),
        "mind_predecision_sha256":first_person_before,
        "before_body":list(before),
        "budget_work":asdict(b.work),
        "returned_work":asdict(work),
        "paid_allowance_remaining":list(b.remaining),
        "action":action,"param":param,"option":info.get("option"),
        "funding":info.get("funding"),
        "candidate_tag":info.get("candidate"),
        "computed_discarded_option":info.get("computed_and_discarded_option"),
        "native_step_result":{
            "t":result["t"],"body":list(result["body"]),
            "moved":result["moved"],"dead":list(result["dead"]),
            "cognitive_accounting":result["cognitive_accounting"],
            "world_position":list(world.pos),
        },
        "paid_native_bills":{
            "energy":own_cognitive_bill[0],
            "vigilance":own_cognitive_bill[1],
        },
    }
    proof["receipt_sha256"]=digest(proof)
    return proof


def inspect_case(case):
    name,body,experiences,at_water,expected_action,branch=case
    base_world,base_mind=make_state(case)
    if base_world.dead:
        raise AssertionError("no synthetic case begins after death")
    prior_capture=base_world.capture()
    initial_model=state_witness(base_mind)
    shared_capture_sha=digest(prior_capture)
    private_sha=digest(initial_model)
    classes={
        "candidate":PaidMicrodecisionMind,
        "equal_paid_discard":PaidMicrodecisionEqualPaidDiscardMind,
        "p13_reference":Mind,
    }
    runs={}
    for name_arm in ARM_NAMES:
        world=deepcopy(base_world)
        mind=cloned_mind(classes[name_arm],base_mind)
        if state_witness(mind)!=initial_model or world.capture()!=prior_capture:
            raise AssertionError("matched starting private memories or first-person state mismatch")
        runs[name_arm]=arm_run(world,mind,shared_capture_sha)
    candidate,discard,reference=(runs[k] for k in ARM_NAMES)
    if (candidate["mind_predecision_sha256"]!=discard["mind_predecision_sha256"]
            or candidate["mind_predecision_sha256"]!=reference["mind_predecision_sha256"]):
        raise AssertionError("personal learned state is not exactly paired")
    if branch=="F1":
        if candidate["funding"] not in (
            "F1_PAID_SELF_SELECTED_ACTION","F1_PAID_VOLUNTARY_ABSTENTION"
        ) or discard["funding"]!="F1_EQUAL_PAID_MICRO_RESULT_DISCARDED":
            raise AssertionError("expected paid autonomous candidate + paid discard")
        if (candidate["action"]!=expected_action
                or discard["action"] is not None
                or discard["computed_discarded_option"]!=candidate["option"]
                or reference["funding"]!="NO_PROCESSING_BUDGET"):
            raise AssertionError("matched chosen/dismissed option or reference failed")
    elif branch=="UNFUNDED":
        if (candidate["funding"]!="NO_PROCESSING_BUDGET"
                or discard["funding"]!="NO_PROCESSING_BUDGET"
                or reference["funding"]!="NO_PROCESSING_BUDGET"
                or any(r["action"] is not None for r in runs.values())):
            raise AssertionError("unfunded branch must abstain without free cognition")
    elif branch=="REFERENCE":
        if (candidate["funding"]!=reference["funding"]
                or discard["funding"]!=reference["funding"]
                or candidate["action"]!=reference["action"]
                or discard["action"]!=reference["action"]
                or candidate["option"]!=reference["option"]
                or discard["option"]!=reference["option"]):
            raise AssertionError("full funded P1.3 reference behavior was unexpectedly changed")
    else:
        raise ValueError("unknown frozen synthetic case type")
    for field in ("budget_work","paid_allowance_remaining","paid_native_bills"):
        if candidate[field]!=discard[field]:
            raise AssertionError("same-thought two-currency parity failed: "+field)
    for k in ("energy","vigilance"):
        ca=candidate["native_step_result"]["cognitive_accounting"][k]
        cb=discard["native_step_result"]["cognitive_accounting"][k]
        if ca != cb:
            raise AssertionError("native World actual decision bill was not identically paid")
    if branch=="F1" and candidate["budget_work"]!=asdict(MICRO_WORK):
        raise AssertionError("positive microdecision cost not paid")
    if branch=="UNFUNDED" and candidate["budget_work"]!=asdict(CognitiveWork()):
        raise AssertionError("negative balance incorrectly allowed a cognitive action")
    if branch=="F1" and candidate["action"] is None:
        if candidate["native_step_result"]["body"]!=discard["native_step_result"]["body"]:
            raise AssertionError("abstention and equal-paid discard unexpectedly differ")
    if name=="terminal_food_not_rescued":
        if candidate["native_step_result"]["dead"]!=["zero_food"]:
            raise AssertionError("low food bodily death was bypassed")
    return {
        "case":name,
        "branch":branch,
        "synthetic_predecision_state":{
            "body":list(body),
            "capture":json.loads(canonical(prior_capture)),
            "capture_sha256":shared_capture_sha,
            "learned_effect_observations":[{"key":list(k),"delta":list(delta)}
                                            for k,delta in experiences],
            "private_mind_sha256":private_sha,
            "start_tick":0,"started_dead":False,
        },
        "runs":runs,
        "same_predecision_body_capture_private_mind":True,
        "same_native_cognitive_bill_candidate_vs_discard":True,
        "same_budget_work_and_remaining_candidate_vs_discard":True,
        "same_post_body_only_if_both_motor_none":(
            candidate["action"] is None and discard["action"] is None),
        "p13_is_NOT_cost_matched_to_micro_branch":True,
        "original_first_person_lives_created":0,
    }


def produce():
    rows=[inspect_case(case) for case in STATES]
    report={
        "schema":SCHEMA,
        "status":"DEVELOPMENT_MATCHED_NATIVE_BILL_AND_FIRST_PERSON_PROOF_PASS",
        "source_f1_baseline_head":F1_HEAD,
        "immutable_historical_p13_engine_head":REFERENCE_HEAD,
        "frozen_negative_causal_stage8e2":FROZEN_CAUSAL,
        "evidence_class":"SYNTHETIC_MATCHED_WORLD_STEP_ONE_TICK_NOT_A_LIFE",
        "full_lives_generated":0,
        "new_scientific_cohorts":0,
        "synthetic_native_world_step_calls":3*len(STATES),
        "independent_matched_cases":len(STATES),
        "brain_learning_after_native_step":"NOT_EXECUTED",
        "native_life_manifest_or_evidence_chain":"NOT_CLAIMED",
        "matched_pairs":["candidate","equal_paid_discard"],
        "reference_is_not_equal_cost_control":True,
        "scenarios":rows,
    }
    report["provenance_chain_sha256"]=digest({
        "source":F1_HEAD, "scenario_receipts":[
            [x["runs"][a]["receipt_sha256"] for a in ARM_NAMES] for x in rows]})
    return report


def main():
    p=argparse.ArgumentParser(description="No lives; synthetic one-tick native World billing")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=produce()
    path=Path(args.output)
    with path.open("xb") as f:
        f.write(canonical(result))
    print(json.dumps({
        "status":result["status"],"cases":result["independent_matched_cases"],
        "actual_native_steps":result["synthetic_native_world_step_calls"],
        "native_lives":0,"sha256":sha256(canonical(result)).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
