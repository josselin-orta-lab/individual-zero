"""F1J 16 independent personal paid histories under true fixed-round choice.

First F1J native step MUST follow frozen grid and protocol git commits.
Never force an action, prefill an EffectsModel or pad CognitiveWork.
Original Mind P1.3, previously closed Stage8-F1I, and BodyLaws unchanged.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

from i3.modules.genome import midpoint
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1d_next_decision_retention as D
from tools import stage8f1i_independent_lived_resources as F1I
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind

SCHEMA="i3-stage8f1j-fixed-substantive-rounds-equal-paid-16-origins/v0"
BASE="3745952a6c8635072828cdfbe3686229eebe50ba"
GRID_PREEXPOSURE_COMMIT="8f82eea7a8b08e086010dfe497099212fb35508f"
PREEXPOSURE_COMMIT="b90d6eb13459ddfda4f63c0828f4e39f135a376e"
GRID_PATH=("docs/research/studies/stage8f1-paid-microdecision/"
           "STAGE8F1J_FROZEN_FIXED_ROUND_NATIVE_EQUAL_COST_GRID_2026-11-21.json")
ARMS=("full","sham","mask_owned_t1_means")
ORIGINS=16
T_ACQUIRE=4
T_FORK=5
T_END=30
PRIOR_RESULTS={
 "f1i":"INCONCLUSIVE_COST_GATE",
 "f1i_unmatched_origins":["R07","R08","R10","R11"],
 "f1i_original_sha256":"e9daebdabb3b69671ecaa39c9fb48a0cc60d92d8518d42c7df1ad32ad5346f2a",
 "f1f":"MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES",
 "f1g_td":"NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
 "f1g_buffer":"NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES",
 "f1h":"NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12",
 "stage8e2":"STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY"
}


def exact_grid(path=GRID_PATH):
    data=json.loads(Path(path).read_bytes())
    if (data.get("schema")!="i3-stage8f1j-frozen-independent-fixed-round-v0"
            or data.get("baseline_main")!=BASE
            or data.get("mind")!="F1JFixedRoundMind(Mind)"
            or data.get("same_genome_for_all")!="midpoint()"
            or data.get("origin_steps")!=T_ACQUIRE
            or data.get("first_person_paid_prior_at_tick")!=1
            or data.get("fork_tick")!=T_FORK
            or data.get("terminal_tick")!=T_END
            or data.get("arms")!=list(ARMS)
            or data.get("world_width")!=3
            or data.get("world_height")!=3
            or data.get("spawn")!=[1,1]
            or data.get("original_F1I_data_untouched") is not True):
        raise AssertionError("F1J changed preregistered population or stopping rule")
    matrix=F1I.MATRIX
    modes=[]
    roots=[]
    for i,(name,params) in enumerate(matrix.items()):
        water,wgain,food,token,fgain,delta,base=params
        modes.append({
            "id":name,"water":list(water),"water_gain":wgain,
            "food":list(food),"token":token,"food_gain":fgain,
            "integrity_delta":delta,"water_stock":2,"food_stock":2,
            "restock_every":0,
        })
        for j in range(4):
            roots.append({
                "id":"J"+str(i*4+j+1).zfill(2),
                "ecology":name,
                "seed":202611219001+i*4+j,
                "body":[round(x+shift*(j+1),3) for x,shift in
                        zip(base,(1.1,-.45,.25,-.35,-.35))],
            })
    if data.get("full_families")!=modes or data.get("origins")!=roots:
        raise AssertionError("F1J attempted source-selected seed/ecology/body")
    fixed=data.get("fixed_rounds",{})
    if not (fixed.get("no_padding")=="no synthetic equalization: every charged round must integrate all option evidence; never charge a work cycle merely for parity"
            and fixed.get("no_engine_patch") is True
            and data.get("no_run_life") is True):
        raise AssertionError("source-lock failure: F1J calculation and autonomy")
    return data


def personal_source(case):
    world=F1I.new_source_world(case)
    mind=F1JFixedRoundMind(midpoint(),case["seed"])
    if (mind.effects.stats or mind.buffer or
        any(any(v!=0.0 for v in row) for row in mind.values)
        or world.t!=0 or world.dead):
        raise AssertionError("fresh origin must have no synthetic personal memory")
    genesis={"world":D._snapshot_world(world),"mind":C.seal_mind(mind)}
    steps=[]
    error=None
    owned_at_t1={}
    for tick in range(1,T_ACQUIRE+1):
        if world.dead:
            break
        try:
            step=F1I.paid_step(world,mind)
            steps.append(step)
            if tick==1:
                owned_at_t1=deepcopy(mind.effects.stats)
        except (ValueError,KeyError,RuntimeError,AssertionError) as exc:
            error={"tick_attempted":tick,"type":type(exc).__name__,"message":str(exc)}
            break
    learned=deepcopy(mind.effects.stats)
    valid=(error is None and len(steps)==T_ACQUIRE
           and world.t==T_ACQUIRE and not world.dead
           and bool(owned_at_t1)
           and steps[0]["postaction"]["status"]=="PAID_LEARNED")
    row={
        "origin":case,"genesis":genesis,
        "source_steps":steps,
        "paid_t1_mean_anchor":[{"key":list(k),"stat":deepcopy(v)}
                               for k,v in sorted(owned_at_t1.items(),key=lambda x:repr(x[0]))],
        "paid_t4_full_effects":[{"key":list(k),"stat":deepcopy(v)}
                               for k,v in sorted(learned.items(),key=lambda x:repr(x[0]))],
        "source_tick4_world":D._snapshot_world(world),
        "source_tick4_mind":C.seal_mind(mind),
        "source_valid_for_fork":valid,
        "source_native_error":error,
        "source_experiences_created_by_run_life":False,
    }
    row["source_receipt_sha256"]=C.digest(row)
    return world,mind,owned_at_t1,row


def followup(world,mind,mode,t1_stats):
    original_mode=("mask_owned_prior_means"
                   if mode=="mask_owned_t1_means" else mode)
    result=F1I.trajectory(world,mind,original_mode,t1_stats)
    result["mode"]=mode
    result["trajectory_sha256"]=C.digest({
        k:v for k,v in result.items() if k!="trajectory_sha256"
    })
    return result


def same_fork(full,other):
    return F1I._same_fork(full,other)


def produce(grid):
    if grid!=exact_grid():
        raise AssertionError("preregistered F1J roots mutated")
    rows=[]
    for root in grid["origins"]:
        world,mind,t1,source=personal_source(root)
        if not source["source_valid_for_fork"]:
            row={
              "origin":root,"source":source,"arms":{},
              "equal_full_native_work_and_paid_both_coins":False,
              "whole_trajectory_sham_neutral":False,
              "origin_valid":False,"motor_changed":None,
              "survival_comparison":None,"terminal_pareto":None,
            }
        else:
            arms={
                mode:followup(
                    deepcopy(world),deepcopy(mind),mode,t1
                ) for mode in ARMS
            }
            full,sham,masked=(arms[m] for m in ARMS)
            equal=all(same_fork(full,arms[m]) for m in ARMS)
            neutral=F1I._sham_equal(full,sham)
            errors=any(a["metrics"]["native_error"] is not None
                       for a in arms.values())
            valid=equal and neutral and not errors
            motor=bool(
                full["steps"] and masked["steps"] and
                (full["steps"][0]["action"],full["steps"][0]["param"])!=
                (masked["steps"][0]["action"],masked["steps"][0]["param"])
            )
            row={
                "origin":root,"source":source,"arms":arms,
                "equal_full_native_work_and_paid_both_coins":equal,
                "whole_trajectory_sham_neutral":neutral,
                "origin_valid":valid,
                "motor_changed":motor if valid else None,
                "survival_comparison":(
                    F1I._survival(full["metrics"],masked["metrics"])
                    if valid else None
                ),
                "terminal_pareto":(
                    F1I._pareto(full["metrics"],masked["metrics"])
                    if valid else None
                ),
            }
        row["case_sha256"]=C.digest(row)
        rows.append(row)
    sources=sum(int(r["source"]["source_valid_for_fork"]) for r in rows)
    equal=sum(int(r["equal_full_native_work_and_paid_both_coins"]) for r in rows)
    neutral=sum(int(r["whole_trajectory_sham_neutral"]) for r in rows)
    valid=sum(int(r["origin_valid"]) for r in rows)
    if sources!=ORIGINS:
        verdict="INCONCLUSIVE_UNFUNDED_OR_SOURCE_GATE"
    elif neutral!=ORIGINS:
        verdict="INVALID_SHAM"
    elif any(a["metrics"]["native_error"] is not None for r in rows
             for a in r["arms"].values()) or valid<equal:
        verdict="INVALID_NATIVE_AUDIT"
    elif equal!=ORIGINS:
        verdict="NO_FIXED_ROUND_COST_PARITY_DEMONSTRATED"
    else:
        verdict="FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL"
    result={
        "schema":SCHEMA,
        "reference_main_before_preexposure":BASE,
        "preexposed_grid_commit":GRID_PREEXPOSURE_COMMIT,
        "preexposed_protocol_commit":PREEXPOSURE_COMMIT,
        "study":"F1J_FIXED_ROUND_NATIVE_PAID_COMPETITION_NEW_16_ROOTS",
        "experimental_policy":"F1JFixedRoundMind",
        "reference_Mind_unchanged":True,
        "fixed_rounds_all_substantive_no_cost_padding":True,
        "self_chosen_native_actions_no_motor_override":True,
        "source_independent_fresh_minds":True,
        "real_food_token_effects":True,
        "preregistered_root_count":ORIGINS,
        "preregistered_ecologies":list(F1I.MATRIX),
        "preregistered_root_ids":[r["id"] for r in grid["origins"]],
        "full_native_lives_run_life":0,
        "new_scientific_cohorts":0,
        "t1_personal_paid_anchor":1,
        "personal_acquisition_ticks":T_ACQUIRE,
        "one_time_readout_mask_tick":T_FORK,
        "terminal_tick":T_END,
        "sham_required_for_entire_trajectory":True,
        "no_postfork_memory_interventions":True,
        "source_valid_roots":sources,
        "matched_all_native_work_four_fields_and_paid_energy_vigilance_roots":equal,
        "sham_neutral_roots":neutral,
        "valid_prospective_roots":valid,
        "motor_changed_equal_cost_roots":sum(r["motor_changed"] is True for r in rows),
        "full_survival_advantage_equal_cost_roots":sum(
            r["survival_comparison"]=="FULL_SURVIVAL_ADVANTAGE" for r in rows),
        "mask_survival_advantage_equal_cost_roots":sum(
            r["survival_comparison"]=="FULL_SURVIVAL_DISADVANTAGE" for r in rows),
        "real_meals_per_all_branches":sum(
            a["metrics"]["foods_actually_eaten"] for r in rows for a in r["arms"].values()),
        "real_drinks_per_all_branches":sum(
            a["metrics"]["water_drinks"] for r in rows for a in r["arms"].values()),
        "real_source_native_steps":sum(len(r["source"]["source_steps"]) for r in rows),
        "real_followup_native_steps":sum(
            len(a["steps"]) for r in rows for a in r["arms"].values()),
        "strict_preexposed_primary_verdict":verdict,
        "frozen_prior_results":PRIOR_RESULTS,
        "rows":rows,
    }
    result["provenance_sha256"]=C.digest({
        "main":BASE,"grid_commit":GRID_PREEXPOSURE_COMMIT,
        "protocol_commit":PREEXPOSURE_COMMIT,
        "case_receipts":[r["case_sha256"] for r in rows],
    })
    return result


def main():
    ap=argparse.ArgumentParser(description="F1J genuinely paid fixed-round evidence integrator")
    ap.add_argument("--grid",default=GRID_PATH)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    report=produce(exact_grid(args.grid))
    with Path(args.output).open("xb") as f:
        f.write(C.canonical(report))
    print(json.dumps({
        "status":report["strict_preexposed_primary_verdict"],
        "paid_sources":report["source_valid_roots"],
        "equal_real_work_and_two_currency_paid":report["matched_all_native_work_four_fields_and_paid_energy_vigilance_roots"],
        "neutral_shams":report["sham_neutral_roots"],
        "motor_changed":report["motor_changed_equal_cost_roots"],
        "true_meals":report["real_meals_per_all_branches"],
        "true_drinks":report["real_drinks_per_all_branches"],
        "source_native_steps":report["real_source_native_steps"],
        "followup_native_steps":report["real_followup_native_steps"],
        "sha256":C.digest(report),
    },sort_keys=True))


if __name__=="__main__":
    main()
