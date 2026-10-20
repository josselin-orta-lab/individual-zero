#!/usr/bin/env python3
"""#318 matched 2x2 effect *descriptions* from 32 sealed physical WALs.

Authenticates the 32 original mortal WALs FIRST and computes within-block
descriptive factorial contrasts for a fixed 300-step horizon. Eight
world/seed blocks are NOT 32 independent replicates, no p-values or
longitudinal counterfactuals, no recalibration, no rebirth or world access.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _check
from audit_i1_318_matched_temperament_q_factorial import (
    ARMS, PRESETS, SEEDS, SOURCE_SHA, SOURCE_RUN, audit as certify,
)

SCHEMA="i1-318-matched-Q-factorial-paired-descriptive/v1"
HORIZON=300
NAMES=("neutral","rank_only","evidence_only","learned")
METRICS=("boire","dormir","consolidated","accepted_uc","local_proposals")
ARM_BY_NAME={name:arm for name,arm in zip(NAMES,ARMS)}


def paired_axes(m):
    """Return exact twice-main-effects and interaction over four arms."""
    _check(set(m)==set(NAMES),"factorial block does not contain four modes")
    a,b,c,d=(m[k] for k in NAMES)
    _check(all(type(n) is int and n>=0 for n in (a,b,c,d)),
           "invalid physical count in factorial comparison")
    return {
        # Half sum of the controlled simple effects is the main effect.
        "rank_effect_times_2":(b-a)+(d-c),
        "evidence_effect_times_2":(c-a)+(d-b),
        "interaction":d-c-b+a,
        "evidence_at_rank_off":c-a,
        "evidence_at_rank_on":d-b,
        "rank_at_evidence_off":b-a,
        "rank_at_evidence_on":d-c,
    }


def sign_summary(rows):
    return {
        "negative":sum(v<0 for v in rows),
        "zero":sum(v==0 for v in rows),
        "positive":sum(v>0 for v in rows),
        "min":min(rows),
        "max":max(rows),
        "sum":sum(rows),
    }


def _physical_commands(wal):
    counts=Counter()
    for line in wal.read_text(encoding="utf-8").splitlines():
        event=json.loads(line)["causal_event"]
        if event.get("kind")=="command_experienced":
            cmd=event.get("primitive")
            _check(type(cmd) is str, "missing authenticated physical command")
            counts[cmd]+=1
    return counts


def audit(root):
    custody=certify(root)
    _check(custody["status"]=="ORIGINAL_32_WAL_AUTHENTICATED"
           and custody["verified_WAL_count"]==32
           and custody["source_sha"]==SOURCE_SHA,
           "factorial effect analysis cannot precede original WAL custody")
    data=[]
    aggregates={key:{mode:0 for mode in NAMES} for key in METRICS}
    per_metric={key:[] for key in METRICS}
    for born in custody["pairs"]:
        world,seed=born["world"],born["seed"]
        _check(world in PRESETS and seed in SEEDS,
               "unknown pre-registered original paired world")
        row={}
        for name in NAMES:
            arm=ARM_BY_NAME[name]
            physical=born["arms"][arm]
            _check(physical["steps"]==HORIZON
                   and physical["lifecycle"]=="active",
                   "original cohort is not the declared fixed-horizon sample")
            original=root/world/str(seed)/arm/"life-01.wal"
            commands=_physical_commands(original)
            _check(sum(commands.values())==HORIZON,
                   "physical commands differ from original WAL custody")
            measures={
                "boire":commands["boire"],
                "dormir":commands["dormir"],
                "consolidated":physical["consolidated"],
                "accepted_uc":physical["accepted_uc"],
                "local_proposals":physical["local_proposals"],
            }
            _check(all(type(v) is int and v>=0 for v in measures.values()),
                   "invalid objective observed count")
            row[name]=measures
            for metric,value in measures.items():
                aggregates[metric][name]+=value
        contrasts={}
        for metric in METRICS:
            by_arm={mode:row[mode][metric] for mode in NAMES}
            result=paired_axes(by_arm)
            contrasts[metric]=result
            per_metric[metric].append(result)
        data.append({"world":world,"seed":seed,
                     "arms":row,"contrasts":contrasts})
    _check(len(data)==8 and
           {(x["world"],x["seed"]) for x in data}==
           {(w,seed) for w in PRESETS for seed in SEEDS},
           "duplicated or missing eight original factorial blocks")
    summary={}
    for metric,observations in per_metric.items():
        metric_totals=aggregates[metric]
        summary[metric]={
            "original_arm_totals":metric_totals,
            "rank_main_effect_per_life":(
                sum(x["rank_effect_times_2"] for x in observations)/16
            ),
            "evidence_main_effect_per_life":(
                sum(x["evidence_effect_times_2"] for x in observations)/16
            ),
            "interaction_per_life":(
                sum(x["interaction"] for x in observations)/8
            ),
            "paired_effect_direction_counts":{
                key:sign_summary([r[key] for r in observations])
                for key in ("rank_effect_times_2",
                            "evidence_effect_times_2",
                            "evidence_at_rank_off",
                            "evidence_at_rank_on",
                            "rank_at_evidence_off",
                            "rank_at_evidence_on",
                            "interaction")
            },
            "by_world":{
                world:{
                    "arm_totals":{
                        mode:sum(x["arms"][mode][metric]
                                 for x in data if x["world"]==world)
                        for mode in NAMES
                    },
                    "evidence_effect_times_2_sum":sum(
                        x["contrasts"][metric]["evidence_effect_times_2"]
                        for x in data if x["world"]==world
                    ),
                    "rank_effect_times_2_sum":sum(
                        x["contrasts"][metric]["rank_effect_times_2"]
                        for x in data if x["world"]==world
                    ),
                }
                for world in PRESETS
            },
        }
        certified=custody["summary"]
        for mode in NAMES:
            registered=ARM_BY_NAME[mode]
            lookup={"boire":"motor_boire","dormir":"motor_dormir",
                    "consolidated":"consolidated","accepted_uc":"UC",
                    "local_proposals":"local_proposals"}[metric]
            _check(metric_totals[mode]==certified[registered].get(lookup,0),
                   "paired counts disagree with authenticated whole-cohort summary")
    return {
        "schema":SCHEMA,
        "status":"PAIRED_DESCRIPTIVES_FROM_32_CERTIFIED_WAL",
        "source_birth_run":SOURCE_RUN,"source_sha":SOURCE_SHA,
        "WAL_authenticated":32,"blocked_four_arm_replicates":8,
        "time_horizon_steps_per_life":HORIZON,
        "sampling_limitation":"four seeds repeated in two designed worlds; not 32 independent worlds",
        "no_significance_or_causal_mediation_claim":True,
        "long_term_survival_benefit_proven":False,
        "scientific_verdict":"INCONCLUSIVE",
        "read_only":True,
        "metrics":summary,"blocks":data,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    _check(not args.output.exists(),"never overwrite original or existing report")
    report=audit(args.root)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":report["status"],"WAL_authenticated":report["WAL_authenticated"],
        "scientific_verdict":report["scientific_verdict"],
        "metrics":report["metrics"],
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
