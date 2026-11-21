"""F1H independent standard-library-only native T12 body and paid learning audit.

Never imports the policy/World/BodyLaw implementation or the F1H producer.
Cold-reduces every original F1C and F1F anchor, every future cognitive bill,
the full physical five-channel step, all water/food resources and irreversible
death; verifies chained typed private Mind receipts and prespecified endpoints.

Does NOT claim independent reimplementation of the neural TD algorithm.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1f_independent_ecology_audit as A

SCHEMA="i3-stage8f1h-prospective-t12-native-body-value/v0"
SOURCE="3ad4cb687b403214c9b9f6055b46a489dca44af4"
PREEXPOSURE="5c2abb2fc755bf0a580e2880bedf507b59a2baec"
F1C_SHA="e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d"
F1F_SHA="f620d1b46ddf269dc368dcd90ba6c93f44f0b6442f8d9e6322440de32e3fbab5"
F1F_COLD_SHA="8013f2add1f3eb0190127bb77eac588c95f153f32ba21113302bafa0292e2ac2"
F1G_SHA="a7f0782886b3d2b97cd91ea11803934f31736b91e6d659c700a3d1dd886a8376"
F1G_COLD_SHA="ec3b1c953c69d87dc042ab81da55809984e7b78c175a2697a6b3d0a24fa21310"
E2="STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
T12=12
MIXED="mixed_here_water_east_food"
MODES=("full","sham","mask_both")
MOTORS={"se_deplacer":2.,"collecter":1.,"manger":.5,
        "boire":.5,"dormir":.25,"attendre":.35}
VECTORS={"N":(0,-1),"E":(1,0),"S":(0,1),"W":(-1,0)}
CURRENCIES=("energy","vigilance")


def check(ok,what):
    I.check(ok,"COLD F1H: "+what)


def body_eq(a,b,what):
    I.body_equal(a,b,"COLD F1H "+what)


def _resources(world,case):
    _,where_water,where_food=case
    # State is checked independently after each step, including stock and
    # unchanged world laws/spec, not just the final physiological numbers.
    check(world["world_spec"]=={
        "name":"F1F_ECO_"+case[0],"width":3,"height":3,
        "spawn":[1,1],"laws":A.D.LAWS},
        "WorldSpec or BodyLaws v2 illegally changed")
    check(world["hidden_effects"]==[],"food gained hidden physiology")
    waters=world["water_cells"]
    foods=world["food_cells"]
    check(waters==([] if where_water is None else [
        [list(where_water),25.0,waters[0][2],2,0]]),
        "wrong prescheduled water placement/price")
    check(foods==([] if where_food is None else [
        [list(where_food),A.TOKEN,foods[0][2],2,0]]),
        "wrong prescheduled food placement/price")
    if waters:
        check(type(waters[0][2]) is int and 0<=waters[0][2]<=1,
              "invented water stock")
    if foods:
        check(type(foods[0][2]) is int and 0<=foods[0][2]<=1,
              "invented food stock")
    check(world["t"]>=1 and len(world["body"])==5
          and len(world["position"])==2,
          "incomplete native World snapshot")
    for token,count in world["inventory"]:
        check(token==A.TOKEN and type(count) is int and 0<=count<=1,
              "invented external inventory")
    return world


def _perception(before):
    pos=tuple(before["position"])
    waters={tuple(row[0]) for row in before["water_cells"] if row[2]>0}
    foods={tuple(row[0]):row[1] for row in before["food_cells"] if row[2]>0}
    def cell(p):
        if not 0<=p[0]<3 or not 0<=p[1]<3:
            return None
        return [p in waters, [foods[p]] if p in foods else []]
    x,y=pos
    return {
       "body":before["body"],
       "inventory":[row for row in before["inventory"] if row[1]>0],
       "here":cell((x,y)),
       "neighbors":[cell(k) for k in ((x,y-1),(x+1,y),(x,y+1),(x-1,y))]
    }


def _physical(before,action,param,work,actual_bill):
    """Reimplement native BodyLaws-v2 and World._step independent of engine."""
    check(not before["dead"] and 1<=before["t"]<T12,
          "resurrection, hidden tick, or post-T12 native World.step")
    debit=I.cost(work)
    I.check_bill(actual_bill,debit,"T12 true native motor")
    energy,food,water,integrity,vigilance=before["body"]
    check(energy>=debit["energy"] and vigilance>=debit["vigilance"],
          "actual cognitive work was underfunded")
    energy-=debit["energy"]
    vigilance-=debit["vigilance"]
    check(action in (*MOTORS,None),"unknown/prescribed physical action")
    if action is not None and action!="dormir":
        check(energy>=MOTORS[action],"native motor action unpayable")
    nxt=deepcopy(before)
    nxt["t"]+=1
    pos=nxt["position"]
    moved=False
    food_gain=0.0
    water_gain=0.0
    integrity_delta=0.0
    if action in (None,"dormir","attendre","boire"):
        check(param is None,"unexpected motor parameter")
    if action=="se_deplacer":
        check(param in VECTORS,"invalid direction")
        dx,dy=VECTORS[param]
        end=[pos[0]+dx,pos[1]+dy]
        check(0<=end[0]<3 and 0<=end[1]<3,"native step escaped bounded WorldSpec")
        nxt["position"]=end
        moved=True
    elif action=="boire":
        water_cell=next((v for v in nxt["water_cells"]
                         if v[0]==pos and v[2]>0),None)
        check(water_cell is not None,"water illegally consumed at invisible source")
        water_cell[2]-=1
        water_gain=water_cell[1]
    elif action=="collecter":
        row=next((v for v in nxt["food_cells"]
                  if v[0]==pos and v[2]>0 and v[1]==param),None)
        check(row is not None,"food collected without visible token")
        row[2]-=1
        inventory=dict((k,v) for k,v in nxt["inventory"])
        inventory[param]=inventory.get(param,0)+1
        nxt["inventory"]=sorted([[k,v] for k,v in inventory.items()])
    elif action=="manger":
        # Original F1F WorldSpec contains NO token_effects. If engine attempts
        # to eat, native step must error, never award invented free food.
        check(False,"unexpected successful eat of F1F token with no effects")
    food=I.clamp(food-.2)
    water=I.clamp(water-.4)
    hydrated=water>=.05
    if action=="dormir":
        gain=min(3.,max(0.,100.-energy),food/.05) if hydrated else 0.
        energy+=gain
        food-=gain*.05
        vigilance+=4.
    elif action is not None:
        energy-=MOTORS[action]
    if action in ("dormir","attendre") and hydrated:
        repair=min(.2,max(0.,100.-integrity),food/.1)
        integrity+=repair
        food-=repair*.1
    water+=water_gain
    food+=food_gain
    integrity+=integrity_delta
    after=list(map(I.clamp,(energy,food,water,integrity,vigilance)))
    dead=[k for k,i in (("zero_food",1),("zero_water",2),("zero_integrity",3))
          if after[i]<=0]
    nxt["body"]=after
    nxt["dead"]=dead
    return nxt,{"t":nxt["t"],"body":after,"moved":moved,"dead":dead}


def _check_learn(post,motor_world,motor_mind,raw,action,moved):
    check(post["mind_before_outcome_observation"]==motor_mind,
          "late learning did not start from real native postdecision Mind")
    check(post["world_after_motor_body"]==motor_world["body"],
          "learning starts on a fabricated bodily state")
    work=post["learn_work"]
    cost=I.cost(work)
    paid=post["actual_paid_learning_bill"]
    replays=post["prepaid_replays"]
    if paid is None:
        check(work=={"cycles":0,"simulated_steps":0,"memory_items":0,"replays":0}
              and post["executed_replays"]==0
              and replays is None and
              post["status"] in ("DEAD_NO_LEARNING",
                                 "NO_LAST_ACTION_NO_LEARNING","UNFUNDED_LEARNING"),
              "unpaid real learning or fabricated replay")
        if motor_world["dead"]:
            check(post["status"]=="DEAD_NO_LEARNING",
                  "mind learned from physically dead body")
        check(post["learning_grant_remaining"]==motor_world["body"],
              "no-cost allowance is not original body")
        expected=deepcopy(motor_world)
    else:
        check(not motor_world["dead"]
              and post["status"]=="PAID_LEARNED"
              and any(work.values())
              and type(replays) is int
              and replays==post["executed_replays"]==work["replays"],
              "learning executed without genuine prepaid replay quota")
        I.check_bill(paid,cost,"genuinely paid postaction native learning")
        expected=deepcopy(motor_world)
        expected["body"][0]-=cost["energy"]
        expected["body"][4]-=cost["vigilance"]
        check(expected["body"][0]>=0 and expected["body"][4]>=0,
              "learning repaid with negative physical reserve")
        body_eq(post["learning_grant_remaining"],expected["body"],
                "preauthorized learning reserve")
    _resources(expected,raw["case"])
    check(post["world_after_any_learning"]["t"]==expected["t"]
          and post["world_after_any_learning"]["position"]==expected["position"]
          and post["world_after_any_learning"]["inventory"]==expected["inventory"]
          and post["world_after_any_learning"]["water_cells"]==expected["water_cells"]
          and post["world_after_any_learning"]["food_cells"]==expected["food_cells"]
          and post["world_after_any_learning"]["dead"]==expected["dead"],
          "World.pay_cognition illegally rewrote world resources/tick/death")
    body_eq(post["world_after_any_learning"]["body"],expected["body"],
            "native post-learning exact body payment")
    body_eq(post["body_after_any_learning"],expected["body"],
            "body after learning")
    mind=I.private_fields(post["mind_after_any_learning"])
    before=I.private_fields(post["mind_before_outcome_observation"])
    check(set(mind)==set(before),
          "post-learning private memory was partially forged")
    check(post["learning_receipt_sha256"]==I.h({
          k:v for k,v in post.items() if k!="learning_receipt_sha256"}),
          "post-action learning SHA broken")
    return expected


def _metric(steps,end,err):
    coin_dec={"energy":0.,"vigilance":0.}
    coin_learn={"energy":0.,"vigilance":0.}
    area=[0.]*5
    v_min=None
    moves=drinks=collects=0
    for s in steps:
        bill=(s["f1f_tick2_receipt"]["native_bill"]
              if s["t"]==2 else s["native_motor_bill"])
        learning=s["postaction"]
        for coin in CURRENCIES:
            coin_dec[coin]+=bill[coin]["paid"]
            if learning["actual_paid_learning_bill"] is not None:
                coin_learn[coin]+=learning["actual_paid_learning_bill"][coin]["paid"]
        endbody=learning["body_after_any_learning"]
        for i in range(5):
            area[i]+=endbody[i]
        v_min=min(v_min if v_min is not None else float("inf"),
                  min(endbody[1:4]))
        a=(s["f1f_tick2_receipt"]["action"] if s["t"]==2 else s["chosen_action"])
        moves+=int(a=="se_deplacer");drinks+=int(a=="boire")
        collects+=int(a=="collecter")
    return {
        "steps_executed_after_f1c":len(steps),
        "alive_at_t12":bool(end["t"]==T12 and not end["dead"] and err is None),
        "final_tick":end["t"],
        "terminal_body_after_all_real_learning":end["body"],
        "terminal_position":end["position"],
        "terminal_dead_reasons":end["dead"],
        "integrated_body_reserves_unscaled":area,
        "minimum_vital_reserve_on_observed_ticks":v_min,
        "paid_cognitive_decision_total":coin_dec,
        "paid_cognitive_learning_total":coin_learn,
        "movement_count":moves,"drink_count":drinks,"collect_count":collects,
        "native_engineering_error":err
    }


def _survival(a,b):
    if a["alive_at_t12"]!=b["alive_at_t12"]:
        return "FULL_SURVIVAL_ADVANTAGE" if a["alive_at_t12"] else "FULL_SURVIVAL_DISADVANTAGE"
    if a["steps_executed_after_f1c"]!=b["steps_executed_after_f1c"]:
        return ("FULL_SURVIVAL_ADVANTAGE" if
                a["steps_executed_after_f1c"]>b["steps_executed_after_f1c"] else
                "FULL_SURVIVAL_DISADVANTAGE")
    return "NO_SURVIVAL_DIFFERENCE"


def _dominance(a,b):
    x=a["terminal_body_after_all_real_learning"]
    y=b["terminal_body_after_all_real_learning"]
    eps=1e-9
    if all(i>=j-eps for i,j in zip(x,y)) and any(i>j+eps for i,j in zip(x,y)):
        return "FULL_STRICT_FIVE_CHANNEL_PARETO_DOMINANCE"
    if all(j>=i-eps for i,j in zip(x,y)) and any(j>i+eps for i,j in zip(x,y)):
        return "MASKED_STRICT_FIVE_CHANNEL_PARETO_DOMINANCE"
    if all(abs(i-j)<=eps for i,j in zip(x,y)):
        return "FIVE_CHANNELS_IDENTICAL"
    return "MIXED_BODILY_TRADEOFF"


def _sham_equal(full,sham):
    if full["metrics"]!=sham["metrics"] or full["world_at_end"]!=sham["world_at_end"] or full["mind_at_end"]!=sham["mind_at_end"]:
        return False
    if len(full["steps"])!=len(sham["steps"]):
        return False
    for a,b in zip(full["steps"],sham["steps"]):
        if a["t"]==2:
            ca,cb=(x["f1f_tick2_receipt"] for x in (a,b))
            if any(ca[k]!=cb[k] for k in (
                "before_world","before_mind","first_person_capture",
                "post_decision_restored_mind","native_bill","native_second_step",
                "after_world","action","param","cognitive_work","decision_info")):
                return False
            if a["postaction"]!=b["postaction"]:
                return False
        elif a!=b:
            return False
    return True


def audit(report,original,f1f,f1f_cold):
    check(I.h(original)==F1C_SHA and I.h(f1f)==F1F_SHA
          and I.h(f1f_cold)==F1F_COLD_SHA,
          "F1C/F1F original source bytes or cold checksum differ")
    prior=A.audit_f1f(f1f,original)
    check(prior==f1f_cold and
          prior["primary_verdict"]==
            "MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES"
          and prior["matched_cost_ecologies"]==8
          and prior["observed_motor_changed_ecologies"]==1,
          "F1F historical causal result is not source locked")
    check(type(report) is dict and report.get("schema")==SCHEMA
          and report.get("source_main")==SOURCE
          and report.get("preregistered_preexposure_commit")==PREEXPOSURE
          and report.get("f1c_source_original_sha256")==F1C_SHA
          and report.get("f1f_source_original_sha256")==F1F_SHA
          and report.get("f1f_original_cold_sha256")==F1F_COLD_SHA
          and report.get("f1g_original_sha256_untouched")==F1G_SHA
          and report.get("f1g_cold_sha256_untouched")==F1G_COLD_SHA
          and report.get("frozen_stage8e2")==E2
          and report.get("frozen_f1d")==
            "NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE"
          and report.get("frozen_f1e")==
            "NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE"
          and report.get("frozen_f1f")==
            "MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES"
          and report.get("frozen_f1g_td")==
            "NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES"
          and report.get("frozen_f1g_buffer")==
            "NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES"
          and report.get("evidence_class")==
            "DEVELOPMENT_ONLY_NATIVE_EIGHT_SYNTHETIC_ECOLOGIES_NOT_G2"
          and report.get("study")=="F1H_T12_UNFORCED_TOTAL_MEMORY_READOUT_EFFECT"
          and report.get("preexposed_horizon_inclusive")==T12
          and report.get("conditional_preknown_f1f_motor_divergent_context")==MIXED
          and report.get("other_contexts_are_preexposed_not_selected") is True
          and report.get("preexposed_context_ids")==[c[0] for c in A.ECOLOGIES]
          and report.get("arms_per_context")==list(MODES)
          and report.get("no_policy_or_motor_override") is True
          and report.get("no_extra_content_mask_after_t2") is True
          and report.get("all_f1f_tick2_receipts_exact_archival_matches") is True
          and report.get("native_original_f1c_first_step_count")==8
          and report.get("full_lives_created")==0
          and report.get("new_scientific_cohorts")==0
          and report.get("run_life_executed") is False
          and report.get("historical_G2_private_memory_equivalence") is False
          and type(report.get("contexts")) is list
          and len(report["contexts"])==8,
          "source, strict T12 horizon or closed prior verdicts changed")
    all_cases_valid=0
    checked_steps=0
    checked_paid_learning=0
    rows_out=[]
    for original_case,case,row in zip(A.ECOLOGIES,f1f["contexts"],report["contexts"]):
        check(row["context"]==A.description(original_case)
              and row["context"]==case["context"]
              and row["source_f1f_case_sha256"]==case["case_sha256"]
              and row["source_f1f_first_paid_sha256"]==
                  case["source"]["source_proof_sha256"]
              and set(row["arms"])==set(MODES),
              "one of eight original WorldSpecs or F1F root receipts changed")
        output_rows={}
        for mode in MODES:
            t=row["arms"][mode]
            expected_f1f=case["arms"][mode]
            check(t["mode"]==mode and type(t["steps"]) is list
                  and t["steps"] and t["steps"][0]["t"]==2,
                  "wrong original memory-readout arm/tick2")
            check(t["steps"][0]["f1f_tick2_receipt"]==expected_f1f
                  and t["steps"][0]["f1f_tick2_original_receipt_sha256"]==
                      expected_f1f["receipt_sha256"],
                  "rewrote already published F1F tick2 motor/readout/native proof")
            raw=t["steps"][0]["native_motor_raw_receipt"]
            anchor={"t":2,
                    "body":expected_f1f["native_second_step"]["body"],
                    "moved":expected_f1f["native_second_step"]["moved"],
                    "dead":expected_f1f["native_second_step"]["dead"],
                    "cognitive_accounting":expected_f1f["native_bill"]}
            check(raw==anchor,"reconstructed, unpaid, or falsified F1F tick2 native receipt")
            expected_start=case["source"]["world_at_start_of_next_decision"]
            current_world=deepcopy(expected_start)
            current_mind=case["arms"][mode]["before_mind"]
            for index,step in enumerate(t["steps"]):
                check(step["t"]==2+index and step["t"]<=T12,
                      "missing/duplicate physical tick or extra trajectory extension")
                if index==0:
                    receipt=step["f1f_tick2_receipt"]
                    before=receipt["before_world"]
                    check(before==current_world,"initial F1F ecology did not match original")
                    work=receipt["cognitive_work"]
                    action,param=receipt["action"],receipt["param"]
                    actual_bill=receipt["native_bill"]
                    raw_motor=raw
                    post_mind=receipt["post_decision_restored_mind"]
                    check(I.private_fields(receipt["before_mind"])==
                          I.private_fields(current_mind),
                          "not original paid predecision private memory")
                else:
                    check(step["before_world"]==current_world,
                          "physiology after previous native learning was not retained")
                    check(step["mind_before_decision"]==current_mind,
                          "Mind private memories/RNG did not persist across ticks")
                    check(step["future_memory_content_not_masked"] is True,
                          "another illicit masked readout after tick2")
                    work=step["decision_work"]
                    action,param=step["chosen_action"],step["chosen_param"]
                    actual_bill=step["native_motor_bill"]
                    raw_motor=step["native_motor_result"]
                    post_mind=step["decision_mind_after_choice"]
                    check(I.private_fields(post_mind) and
                          "funding" in step["genuinely_computed_decision_info"],
                          "no real cognitive decision witness")
                    check(step["capture_sha256"]==I.h(step["first_person_capture"]),
                          "forged or unsealed first-person capture")
                    body_eq(step["decision_remaining"],
                            [current_world["body"][0]-I.cost(work)["energy"],
                             *current_world["body"][1:4],
                             current_world["body"][4]-I.cost(work)["vigilance"]],
                            "new post-decision grant")
                if index==0:
                    capture=receipt["first_person_capture"]
                    cap_digest=receipt["capture_sha256"]
                else:
                    capture=step["first_person_capture"]
                    cap_digest=step["capture_sha256"]
                check(cap_digest==I.h(capture)
                      and capture==_perception(current_world),
                      "individual observed hidden/fictitious ecological resources")
                _resources(current_world,original_case)
                computed,physical=_physical(current_world,action,param,work,actual_bill)
                check(raw_motor["t"]==physical["t"]
                      and raw_motor["moved"] is physical["moved"]
                      and raw_motor["dead"]==physical["dead"],
                      "native action/death/movement receipt fabricated")
                body_eq(raw_motor["body"],physical["body"],"native motor body")
                if index==0:
                    check(receipt["after_world"]==computed,
                          "frozen F1F next physical world differs")
                else:
                    check(step["world_after_motor"]==computed,
                          "postfork native world resource state incorrect")
                recorded=step["postaction"]
                expected_learning=_check_learn(
                    recorded,computed,post_mind,
                    {"case":original_case},action,physical["moved"])
                current_world=expected_learning
                current_mind=recorded["mind_after_any_learning"]
                check(step["receipt_sha256"]==I.h({
                      k:v for k,v in step.items() if k!="receipt_sha256"}),
                      "source receipt checksum corrupt")
                checked_steps+=1
                checked_paid_learning+=int(recorded["actual_paid_learning_bill"] is not None)
            check(current_world==t["world_at_end"]
                  and current_mind==t["mind_at_end"]
                  and t["trajectory_sha256"]==I.h({
                      k:v for k,v in t.items() if k!="trajectory_sha256"}),
                  "end world/Mind and original chain continuity falsified")
            met=_metric(t["steps"],current_world,t["metrics"]["native_engineering_error"])
            check(met==t["metrics"],
                  "adaptation endpoint reclassified or uncharged costs removed")
            check(current_world["t"]==T12 or current_world["dead"]
                  or t["metrics"]["native_engineering_error"] is not None,
                  "trajectory stopped before fixed T12 without death or native error")
            output_rows[mode]=met
        full,sham,masked=(row["arms"][m] for m in MODES)
        same=_sham_equal(full,sham)
        err=[m for m in MODES if row["arms"][m]["metrics"]["native_engineering_error"]]
        eligible=not err and same
        a,b=output_rows["full"],output_rows["mask_both"]
        sr=_survival(a,b) if eligible else None
        dom=(_dominance(a,b) if eligible and
             a["alive_at_t12"] and b["alive_at_t12"] else None)
        first_changed=(
            [full["steps"][0]["f1f_tick2_receipt"][x] for x in ("action","param")] !=
            [masked["steps"][0]["f1f_tick2_receipt"][x] for x in ("action","param")]
        )
        check(row["sham_entire_trajectory_neutral"] is same
              and row["native_engineering_error_arms"]==err
              and row["valid_continuation_for_value"] is eligible
              and row["observed_survival_comparison"]==sr
              and row["observed_terminal_five_channel_dominance"]==dom
              and row["initial_f1f_motor_difference"] is first_changed
              and row["case_sha256"]==I.h({
                  k:v for k,v in row.items() if k!="case_sha256"}),
              "retrospective F1H body value or sham gate falsified")
        all_cases_valid+=int(eligible)
        rows_out.append({
            "ecology":row["context"]["id"],
            "valid":eligible,"initial_motor_difference":first_changed,
            "full_survived_to_T12":a["alive_at_t12"],
            "masked_survived_to_T12":b["alive_at_t12"],
            "full_terminal_body":a["terminal_body_after_all_real_learning"],
            "masked_terminal_body":b["terminal_body_after_all_real_learning"],
            "full_terminal_position":a["terminal_position"],
            "masked_terminal_position":b["terminal_position"],
            "survival_comparison":sr,
            "five_channel_terminal_dominance":dom,
            "full_paid_decision":a["paid_cognitive_decision_total"],
            "masked_paid_decision":b["paid_cognitive_decision_total"],
            "full_paid_learning":a["paid_cognitive_learning_total"],
            "masked_paid_learning":b["paid_cognitive_learning_total"],
        })
    check(rows_out[-1]["ecology"]==MIXED
          and rows_out[-1]["initial_motor_difference"] is True
          and all(not c["initial_motor_difference"] for c in rows_out[:-1]),
          "changed pre-known F1F motor divergence context")
    overall="INCONCLUSIVE_NATIVE_CONTINUATION"
    if all_cases_valid==8:
        overall={
           "FULL_SURVIVAL_ADVANTAGE":"LOCAL_T12_SURVIVAL_ADVANTAGE_OF_MEMORY_READOUT_OBSERVED",
           "FULL_SURVIVAL_DISADVANTAGE":"LOCAL_T12_SURVIVAL_DISADVANTAGE_OF_MEMORY_READOUT_OBSERVED",
           "NO_SURVIVAL_DIFFERENCE":"NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12",
        }[rows_out[-1]["survival_comparison"]]
    check(report["valid_prospective_ecologies"]==all_cases_valid
          and report["mixed_primary_survival_verdict"]==overall
          and report["mixed_terminal_five_channel_dominance"]==
              rows_out[-1]["five_channel_terminal_dominance"]
          and report["native_followup_world_step_count"]==checked_steps,
          "primary survival endpoint or no rescue rule incorrectly reported")
    chain=I.h({
        "source_main":SOURCE,"f1c":F1C_SHA,"f1f":F1F_SHA,
        "f1f_cold":F1F_COLD_SHA,"preexposure":PREEXPOSURE,
        "contexts":[r["case_sha256"] for r in report["contexts"]]
    })
    check(report["provenance_chain_sha256"]==chain,
          "F1H evidence chain tampered")
    return {
        "schema":"i3-stage8f1h-independent-cold-body-value/v0",
        "status":"F1H_COLD_PROSPECTIVE_NATIVE_PHYSIOLOGY_AND_COSTS_AUDITED",
        "f1h_original_json_sha256":I.h(report),
        "source_f1c_sha256":F1C_SHA,
        "source_f1f_sha256":F1F_SHA,
        "source_f1f_independent_sha256":F1F_COLD_SHA,
        "root_sha256":chain,
        "preexposed_horizon_t":T12,
        "ecologies_checked":8,
        "valid_ecologies":all_cases_valid,
        "native_followup_steps_reevaluated":checked_steps,
        "native_postaction_learning_bills_checked":checked_paid_learning,
        "mixed_primary_survival_verdict":overall,
        "mixed_terminal_five_channel_dominance":rows_out[-1]["five_channel_terminal_dominance"],
        "all_tick2_actions_and_bills_match_F1F_exact_original":True,
        "all_future_motor_choices_native_receipted":True,
        "no_unpaid_learning_or_replays":True,
        "no_forced_behavior_claim":"SUPPORTED_BY_CODE_REVIEW_AND_NATIVE_RECEIPTS",
        "ecological_observations":rows_out,
        "full_native_lives":0,"new_scientific_cohorts":0,
        "frozen_causal_E2":E2
    }


def main():
    p=argparse.ArgumentParser(description="Engine-free F1H native T12 body survival/learning audit")
    p.add_argument("original_f1h")
    p.add_argument("original_f1c")
    p.add_argument("original_f1f")
    p.add_argument("cold_f1f")
    p.add_argument("output")
    args=p.parse_args()
    files=((args.original_f1h,None),(args.original_f1c,F1C_SHA),
           (args.original_f1f,F1F_SHA),(args.cold_f1f,F1F_COLD_SHA))
    objs=[]
    for path,sha in files:
        b=Path(path).read_bytes()
        if sha:
            check(sha256(b).hexdigest()==sha,
                  "original F1C/F1F bytes changed")
        objs.append(json.loads(b))
    result=audit(*objs)
    check(result["f1h_original_json_sha256"]==
          sha256(Path(args.original_f1h).read_bytes()).hexdigest(),
          "F1H source JSON not canonical")
    with Path(args.output).open("xb") as out:
        out.write(I.c(result))
    print(json.dumps({
        "status":result["status"],
        "verdict":result["mixed_primary_survival_verdict"],
        "body_dominance":result["mixed_terminal_five_channel_dominance"],
        "valid_ecologies":result["valid_ecologies"],
        "native_followup_steps":result["native_followup_steps_reevaluated"],
        "paid_postactions":result["native_postaction_learning_bills_checked"],
        "mixed":result["ecological_observations"][-1],
        "sha256":I.h(result),
    },sort_keys=True))


if __name__=="__main__":
    main()
