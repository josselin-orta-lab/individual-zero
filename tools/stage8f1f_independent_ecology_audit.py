"""F1F/F1G cold, standard-library-only ecological native receipt auditor.

Standalone re-reduction of source-exact F1C, 8 fixed scheduled WorldSpecs,
actual BodyLaws v2 and cognitive costs, typed complete private Mind copies,
readout-only counterfactuals, unpaid/faked costs and honest zero outcomes.

NO Mind, World, Body, producer or code-generation imports.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1d_independent_next_decision_audit as D

F1C_SHA="e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d"
SOURCE="77c3e3395dfa379851d6192a7ec09968727c9ed9"
F1D_NEGATIVE="NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE"
F1E_NEGATIVE="NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE"
E2_NEGATIVE="STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
ECOLOGIES=(
    ("bare",None,None),
    ("water_here",(1,1),None),
    ("water_north",(1,0),None),
    ("water_east",(2,1),None),
    ("water_west",(0,1),None),
    ("food_here",None,(1,1)),
    ("food_east",None,(2,1)),
    ("mixed_here_water_east_food",(1,1),(2,1)),
)
TOKEN="f1f-neutral-food"
SLEEP=("dormir",)
GLOBAL=("*",)
ALL_TARGET=(SLEEP,GLOBAL)
MOTOR={"se_deplacer":2.0,"collecter":1.0,"manger":.5,
       "boire":.5,"attendre":.35}


def check(condition,why):
    I.check(condition,"COLD F1F/F1G: "+why)


def description(case):
    name,water,food=case
    changes=[]
    if water is not None:
        changes.append([1,"water_stock",list(water),1])
    if food is not None:
        changes.append([1,"food_quantity",list(food),1])
    return {
        "id":name,
        "water_position":list(water) if water else None,
        "food_position":list(food) if food else None,
        "water_gain":25.0 if water else None,
        "water_initial_stock":0 if water else None,
        "water_revealed_stock":1 if water else None,
        "water_max_stock":2 if water else None,
        "food_token":TOKEN if food else None,
        "food_initial_quantity":0 if food else None,
        "food_revealed_quantity":1 if food else None,
        "food_max_quantity":2 if food else None,
        "scheduled_native_changes":changes,
        "world_spec_name":"F1F_ECO_"+name,
    }


def world_expected(w,case,*,tick,body,pos,action=None,dead=()):
    name,water,food=case
    check(type(w) is dict and w.get("t")==tick and
          w.get("position")==pos and w.get("dead")==list(dead),
          "world tick, position or irreversible death was rewritten")
    I.body_equal(w.get("body"),body,"world native body")
    check(w.get("world_spec")=={
        "name":"F1F_ECO_"+name,"width":3,"height":3,
        "spawn":[1,1],"laws":D.LAWS},
          "WorldSpec body physics or original ecological context changed")
    check(w.get("hidden_effects")==[],
          "food token has unauthorized hidden physiological information")
    waters=([] if water is None else [[list(water),25.0,
                                      0 if action=="boire" else 1,2,0]])
    foods=([] if food is None else [[list(food),TOKEN,
                                      0 if action=="collecter" else 1,2,0]])
    check(w.get("water_cells")==waters and w.get("food_cells")==foods,
          "stock or food resources no longer match prescheduled native changes")
    expected_inv=([[TOKEN,1]] if action=="collecter" else [])
    check(w.get("inventory")==expected_inv,
          "invented carried food or prohibited collect")
    return True


def captured_body_and_resources(row,case,body):
    _,water,food=case
    def cell(pos):
        return [pos==water,
                [TOKEN] if pos==food else []]
    expected={
        "body":body,
        "inventory":[],
        "here":cell((1,1)),
        "neighbors":[cell(x) for x in ((1,0),(2,1),(1,2),(0,1))]
    }
    check(row==expected,"first-person tick1 capture exposes wrong resource or body")


def recompute_native_tick2(before,case,work,action,param):
    """Independent arithmetic + cell-resources; not World/Body imports."""
    native=I.cost(work)
    energy,food,water,integrity,vigilance=before
    check(energy>=native["energy"] and vigilance>=native["vigilance"],
          "not a funded first-person cognitive budget")
    energy-=native["energy"];vigilance-=native["vigilance"]
    food=I.clamp(food-.2)
    water=I.clamp(water-.4)
    hydrated=water>=.05
    name,source_water,source_food=case
    moved=False
    pos=[1,1]
    if action=="dormir":
        check(param is None,"sleep was given forbidden motor param")
        gained=(min(3.,max(0.,100.-energy),food/.05) if hydrated else 0.)
        energy+=gained
        food-=gained*.05
        vigilance+=4.
    elif action is None:
        check(param is None,"abstention must have null parameter")
    else:
        check(action in MOTOR and energy>=MOTOR[action],
              "unfunded, invented or unknown native motor choice")
        energy-=MOTOR[action]
        if action=="se_deplacer":
            check(param in {"N","E","S","W"},"bad actual native move direction")
            dx,dy={"N":(0,-1),"E":(1,0),"S":(0,1),"W":(-1,0)}[param]
            pos=[1+dx,1+dy]
            check(0<=pos[0]<3 and 0<=pos[1]<3,"native move beyond world")
            moved=True
        elif action=="boire":
            check(param is None and source_water==(1,1),
                  "drinking water not actually present under first-person capture")
            water+=25.
        elif action=="collecter":
            check(param==TOKEN and source_food==(1,1),
                  "collected nonexistent/hidden food token")
        elif action=="attendre":
            check(param is None,"wait has no parameter")
        elif action=="manger":
            check(False,"no food carried before the original second decision")
    if action in ("dormir","attendre") and hydrated:
        repair=min(.2,max(0.,100.-integrity),food/.1)
        integrity+=repair
        food-=repair*.1
    after=list(map(I.clamp,(energy,food,water,integrity,vigilance)))
    dead=[label for label,i in (("zero_food",1),("zero_water",2),("zero_integrity",3))
          if after[i]<=0]
    return after,dead,moved,pos,native


def original_boundary(row,original,case):
    prior=original["arms"]["retain"]
    check(row["context"]==description(case)
          and row["source_f1c_receipt_sha256"]==prior["receipt_sha256"]
          and row["pre_exposure_perception_sha256"]==prior["capture_sha256"]
          and row["full_retained_mind_source_sha256"]==
              prior["private_persisted_postaction"]["sha256"]
          and row["first_tick_world_steps"]==1
          and row["first_tick_free_or_forced_actions"]==0
          and row["native_first_motor"]==prior["native_motor_step"]
          and row["native_postaction_paid_learning"]==prior["paid_postaction_learning"]
          and row["native_postaction_work"]==prior["learning_work"],
          "different original F1C action, learning, bill or personal provenance")
    world_expected(row["world_at_start_of_next_decision"],
                   case,tick=1,body=prior["body_after_paid_learning"],pos=[1,1])
    check(row["source_proof_sha256"]==I.h({
          k:v for k,v in row.items() if k!="source_proof_sha256"}),
          "source/World ecological fork evidence has been tampered")


def check_readout(before,effective,mode,original):
    old=I.private_fields(original["arms"]["retain"]["private_before_postaction_learning"])
    learned=I.private_fields(original["arms"]["retain"]["private_persisted_postaction"])
    a=I.private_fields(before)
    b=I.private_fields(effective)
    check(a==learned,"before Mind not exact originally paid F1C memory")
    check(set(a)==set(b),"partial private Mind reserialized")
    differences={k for k in a if a[k]!=b[k]}
    expected={"full":set(),"sham":set(),"mask_both":{"effects"},
              "sham_state":set(),"mask_td":{"values"},
              "mask_buffer":{"buffer"}}[mode]
    check(differences==expected,
          "readout changed hidden RNG/genes or another content channel")
    if mode=="mask_both":
        orig_stats=I.observed_stats(before)
        masked_stats=I.observed_stats(effective)
        old_stats=I.observed_stats(
            original["arms"]["retain"]["private_before_postaction_learning"])
        check(set(orig_stats)==set(masked_stats)==set(old_stats)==set(ALL_TARGET),
              "invented or missing paid learned effect source")
        for k in ALL_TARGET:
            check(masked_stats[k][0]==orig_stats[k][0]
                  and masked_stats[k][2]==orig_stats[k][2]
                  and masked_stats[k][1]==old_stats[k][1],
                  "mean mask altered learned confidence/count or invented values")
    else:
        check(I.observed_stats(effective)==I.observed_stats(before),
              "TD or buffer control illegitimately altered real learned effects")
    if mode=="mask_td":
        check(b["values"]==old["values"] and a["values"]!=b["values"],
              "TD readout not exact pre-learning stored TD values")
    if mode=="mask_buffer":
        check(a["buffer"]=={"__deque__":a["buffer"]["__deque__"],"maxlen":None}
              and len(a["buffer"]["__deque__"])==1
              and b["buffer"]=={"__deque__":[None],"maxlen":None},
              "buffer mask did not preserve slot or inserted fake historical experience")


def check_arm(row,mode,origin,case,original):
    source=original["arms"]["retain"]
    check(row["mode"]==mode and
          row["real_personal_memory_restored"] is True
          and row["new_learning_performed"] is False
          and row["before_mind"]==source["private_persisted_postaction"],
          "same paid personal Mind not present at subsequent cognitive decision")
    check(row["allowed_temporary_masks"]=={
       "full":[],"sham":[],"mask_both":["effects.mean.dormir","effects.mean.*"],
       "sham_state":[],"mask_td":["values.3x6"],
       "mask_buffer":["buffer.content.one_null"]}[mode],
       "unregistered laboratory readout")
    check_readout(row["before_mind"],row["effective_readout_mind"],mode,original)
    fields_exposed=I.private_fields(row["effective_readout_mind"])
    fields_after=I.private_fields(row["post_decision_exposed_mind"])
    fields_restored=I.private_fields(row["post_decision_restored_mind"])
    check(fields_exposed["effects"]==fields_after["effects"] and
          fields_exposed["values"]==fields_after["values"] and
          fields_exposed["buffer"]==fields_after["buffer"],
          "a hidden learned update was executed during the next decision")
    check(fields_restored["effects"]==I.private_fields(
          source["private_persisted_postaction"])["effects"]
          and fields_restored["values"]==I.private_fields(
          source["private_persisted_postaction"])["values"]
          and fields_restored["buffer"]==I.private_fields(
          source["private_persisted_postaction"])["buffer"],
          "paid source personal memory was not restored")
    check(all(fields_after[k]==fields_restored[k] for k in fields_after
              if k not in {"effects","values","buffer"}),
          "lab restored non-memory private fields and overwrote decision state")
    captured_body_and_resources(row["first_person_capture"],case,
                                source["body_after_paid_learning"])
    check(row["capture_sha256"]==I.h(row["first_person_capture"]),
          "first-person capture or hash changed")
    check(row["before_world"]==origin["world_at_start_of_next_decision"],
          "different ecological physical state before second decision")
    work=row["cognitive_work"]
    native=I.cost(work)
    check(type(row["expected_native_cognitive_cost"]) is dict
          and set(row["expected_native_cognitive_cost"])==set(native)
          and all(I.near(native[k],row["expected_native_cognitive_cost"][k])
                  for k in native),
          "incorrect native two-currency cost formula")
    I.check_bill(row["native_bill"],native,"F1F/G next decision")
    left=list(source["body_after_paid_learning"])
    check(left[0]>=native["energy"] and left[4]>=native["vigilance"],
          "unfunded cognitive work")
    left[0]-=native["energy"];left[4]-=native["vigilance"]
    I.body_equal(row["prepaid_allowance_remaining"],left,"true funded allowance")
    after,dead,moved,pos,_=recompute_native_tick2(
        source["body_after_paid_learning"],case,work,
        row["action"],row["param"])
    actual=row["native_second_step"]
    check(actual["t"]==2 and actual["moved"] is moved
          and actual["dead"]==dead,"fabricated motor position or vital death")
    I.body_equal(actual["body"],after,"actual second physical body after cognition")
    world_expected(row["after_world"],case,tick=2,body=after,pos=pos,
                   action=row["action"],dead=dead)
    check(row["after_world"]["body"]==actual["body"],
          "native World after physiology not represented")
    check(type(row["decision_info"]) is dict
          and "funding" in row["decision_info"],
          "no native Mind outcome metadata")
    check(row["receipt_sha256"]==I.h({
         k:v for k,v in row.items() if k!="receipt_sha256"}),
          "post-decision original receipt SHA changed")


def gates(arms,mode):
    full,sham=arms["full"],arms["sham" if mode=="F1F" else "sham_state"]
    parity=all(all(r[k]==full[k] for k in (
       "before_world","before_mind","first_person_capture","capture_sha256",
       "cognitive_work","prepaid_allowance_remaining",
       "expected_native_cognitive_cost","native_bill")) for r in arms.values())
    neutral=all(sham[k]==full[k] for k in (
       "action","param","decision_info","cognitive_work",
       "native_bill","native_second_step","after_world",
       "post_decision_restored_mind"))
    return parity,neutral


def audit_common(report,original,*,study,expected_schema,modes,steps):
    check(type(report) is dict and report.get("schema")==expected_schema
          and report.get("source_main")==SOURCE
          and report.get("f1c_source_original_sha256")==F1C_SHA
          and report.get("f1c_original_provenance_chain_sha256")==
              original.get("provenance_chain_sha256")
          and report.get("frozen_f1d_motor_status")==F1D_NEGATIVE
          and report.get("frozen_f1e_motor_status")==F1E_NEGATIVE
          and report.get("frozen_stage8e2")==E2_NEGATIVE
          and report.get("study")==study
          and report.get("arms_per_context")==list(modes)
          and report.get("preregistered_eco_names")==[c[0] for c in ECOLOGIES]
          and report.get("per_context_native_first_step_count")==1
          and report.get("per_context_native_second_step_count")==len(modes)
          and report.get("native_step_calls")==steps
          and report.get("native_full_lives_created")==0
          and report.get("new_scientific_cohorts")==0
          and report.get("run_life_executed") is False
          and report.get("historical_G2_Mind_reconstructed") is False
          and type(report.get("contexts")) is list
          and len(report["contexts"])==len(ECOLOGIES),
          "global original source, study class or preregistered eight contexts changed")
    check(I.h(original)==F1C_SHA and
          I.audit(original,F1C_SHA)["status"]==
              "SOFTWARE_ONLY_NATIVE_POSTACTION_PAID_LEARNING_RETENTION_PASS",
          "original F1C proof not exact or never audited")
    return original["arms"]["retain"]


def audit_f1f(report,original):
    audit_common(report,original,study="F1F_MEAN_READOUT_ONLY",
                 expected_schema="i3-stage8f1f-eight-ecologies-mean-content-native-proof/v0",
                 modes=("full","sham","mask_both"),steps=32)
    valid=0
    changes=0
    for row,case in zip(report["contexts"],ECOLOGIES):
        check(row["context"]==description(case) and
              row["source"]["context"]==description(case)
              and set(row["arms"])=={"full","sham","mask_both"},
              "wrong ecology order or mode labels")
        original_boundary(row["source"],original,case)
        for mode in ("full","sham","mask_both"):
            check_arm(row["arms"][mode],mode,row["source"],case,original)
        equal,sham=gates(row["arms"],"F1F")
        eligible=equal and sham
        observed=(row["arms"]["full"]["action"],row["arms"]["full"]["param"])!=(
                  row["arms"]["mask_both"]["action"],row["arms"]["mask_both"]["param"])
        check(row["native_work_and_bills_exact_equal"] is equal
              and row["sham_neutral"] is sham
              and row["valid_equal_cost_pair"] is eligible
              and row["mean_content_motor_difference"] is (
                  observed if eligible else None),
              "an invalid cost gate or negative action was reinterpreted")
        check(row["case_sha256"]==I.h({
              k:v for k,v in row.items() if k!="case_sha256"}),
              "one ecological native case custody lost")
        valid+=int(eligible)
        changes+=int(eligible and observed)
    status=("INCONCLUSIVE_ECOLOGY_COST_GATE" if valid!=8 else
            ("NO_MEAN_CONTENT_MOTOR_EFFECT_IN_EIGHT_PREREGISTERED_ECOLOGIES"
             if changes==0 else
             "MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES"))
    check(report["eight_contexts_valid_cost_pairs"]==valid
          and report["eight_contexts_with_motor_change"]==changes
          and report["primary_verdict"]==status,
          "F1F eight-context motor decision criterion was relabelled")
    chain=I.h({
        "source_main":SOURCE,"source_f1c":F1C_SHA,
        "original_chain":original["provenance_chain_sha256"],
        "eight_cases":[row["case_sha256"] for row in report["contexts"]]
    })
    check(report["provenance_chain_sha256"]==chain,
          "original-to-ecology evidence root was fabricated")
    return {
        "schema":"i3-stage8f1f-independent-cold-eight-ecologies/v0",
        "status":"F1F_COLD_NATIVE_EIGHT_ECOLOGICAL_CONTEXTS_REDUCED",
        "source_json_sha256":I.h(report),
        "source_f1c_sha256":F1C_SHA,
        "source_root_sha256":chain,
        "preexposed_ecologies":8,
        "actual_native_original_first_step_receipts":8,
        "actual_native_second_steps_checked":24,
        "matched_cost_ecologies":valid,
        "observed_motor_changed_ecologies":changes,
        "primary_verdict":status,
        "observations":[{"context":r["context"]["id"],
                          "matched":r["valid_equal_cost_pair"],
                          "motor_changed":r["mean_content_motor_difference"],
                          "full":[r["arms"]["full"]["action"],r["arms"]["full"]["param"]],
                          "masked":[r["arms"]["mask_both"]["action"],r["arms"]["mask_both"]["param"]],
                          "work":r["arms"]["full"]["cognitive_work"],
                          "cost":r["arms"]["full"]["expected_native_cognitive_cost"]}
                         for r in report["contexts"]],
        "scientific_lives":0,"scientific_cohorts":0,
        "historical_G2_reconstructed":False,
        "stage8e2_frozen":E2_NEGATIVE
    }


def main():
    p=argparse.ArgumentParser(description="Cold stdlib native F1F eight ecological contexts")
    p.add_argument("source_f1f")
    p.add_argument("original_f1c")
    p.add_argument("output")
    a=p.parse_args()
    orig_bytes=Path(a.original_f1c).read_bytes()
    check(sha256(orig_bytes).hexdigest()==F1C_SHA,"F1C source bytes not exact")
    source_bytes=Path(a.source_f1f).read_bytes()
    report=audit_f1f(json.loads(source_bytes),json.loads(orig_bytes))
    check(report["source_json_sha256"]==sha256(source_bytes).hexdigest(),
          "producer JSON was noncanonical")
    with Path(a.output).open("xb") as fd:
        fd.write(I.c(report))
    print(json.dumps({"status":report["status"],"primary":report["primary_verdict"],
                      "valid_ecologies":report["matched_cost_ecologies"],
                      "changed_ecologies":report["observed_motor_changed_ecologies"],
                      "sha256":I.h(report)},sort_keys=True))


if __name__=="__main__":
    main()
