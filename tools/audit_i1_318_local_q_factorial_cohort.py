#!/usr/bin/env python3
"""Read-only certificate for the 32 original I1 #318 factorial mortal WALs.

Strict original source SHA and hash-chain custody precede any interpretation.
The auditor never instantiates, resumes, or duplicates a living individual.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _verify_arm, _check, _hex
from audit_i1_spatial_navigation_314 import audit as audit_wal
from audit_i1_318_local_q_ablation_cohort import classify_arm, compare_pair

SCHEMA="i1-318-Q-factorial-32-original-WAL-certificate/v1"
BIRTH_SCHEMA="i1-318-local-Q-factorial-mortal/v1"
SOURCE_SHA="0b727273ff748c7919cebb8420dc99a39f2580f6"
SOURCE_RUN=39405862547
ARMS=("local_q_neutral","local_q_rank_only","local_q_evidence_only","local_q_learned")
PRESETS=("memory-corridor","water-isolated-corridor")
SEEDS=(23111,23239,23357,23473)
POLICY="i1-local-interaction-goal-independent-v2"


def audit(root):
    _check(root.is_dir() and not root.is_symlink(),"original cohort directory absent")
    pairs={(w,s) for w in PRESETS for s in SEEDS}
    expected={root/w/str(s)/"report.json" for w,s in pairs}
    _check(set(root.rglob("report.json"))==expected
           and all(p.is_file() and not p.is_symlink() for p in expected),
           "report set is missing, altered or injected")
    overall={arm:Counter() for arm in ARMS}
    out=[]
    for w,seed in sorted(pairs):
        report=json.loads((root/w/str(seed)/"report.json").read_text())
        _check(report.get("schema")==BIRTH_SCHEMA
               and report.get("source_sha")==SOURCE_SHA
               and report.get("status")=="COMPLETE_FACTORIAL_PHYSICAL_DIAGNOSTIC"
               and report.get("preset")==w
               and report.get("seed")==seed
               and report.get("horizon")==300
               and report.get("preregistered_arms")==list(ARMS)
               and set(report.get("arms",{}))==set(ARMS)
               and report.get("only_local_Q_exposure_changed") is True
               and report.get("all_lives_distinct_and_mortal") is True
               and report.get("fixed_local_opportunity_contract")==POLICY
               and report.get("same_world_physics_needs_td_competition_action_control") is True
               and report.get("no_motor_forcing_or_new_vital_reflex") is True
               and report.get("scientific_verdict")=="NO-GO"
               and _hex(report.get("physics_digest"),64)
               and _hex(report.get("preset_sha256"),64),
               "broken preregistered 2x2 protocol")
        verified={}
        chains={}
        for arm in ARMS:
            r=report["arms"][arm]
            exposure=arm.removeprefix("local_q_")
            _check(r.get("local_q_exposure")==exposure
                   and r.get("cross_goal_local_opportunities_opt_in") is True
                   and r.get("native_stage8_opt_in") is False
                   and r.get("critical_alert_sleep_guard_opt_in") is False
                   and r.get("option_ranking_adjusted") is True
                   and r.get("option_value_advisory_adjusted") is False
                   and r.get("wal_relative_path")==arm+"/life-01.wal",
                   "arm has an altered cognitive or physical selector")
            p=root/w/str(seed)/arm/"life-01.wal"
            _check(p.is_file() and not p.is_symlink(),"absent immutable WAL")
            _check(sha256(p.read_bytes()).hexdigest()==r.get("wal_sha256"),
                   "WAL digest mismatch")
            v=_verify_arm(p,r,audit_wal)
            events=[json.loads(row)["causal_event"] for row in p.read_text().splitlines()]
            # The older classifier only accepts 'neutral'/'learned' and is
            # purposely not used to validate intermediate modes. Instead
            # inspect their own birth-sealed Q selector on every local proposal.
            motors={}
            local=0
            for event in events:
                k=event.get("kind")
                if k=="command_experienced":
                    t=event.get("t_monde")
                    _check(t not in motors,"duplicate original motor")
                    motors[t]=(event.get("primitive"),event.get("parameters"))
                if k=="i1_local_opportunity_proposed":
                    d=event.get("data",{})
                    _check(d.get("q_exposure")==exposure
                           and d.get("goal_ref") is None
                           and d.get("forced_motor") is False
                           and d.get("physical_outcome_known") is False
                           and d.get("q_used_for_candidate_rank") == (exposure in ("rank_only","learned"))
                           and d.get("q_used_for_competition_evidence") == (exposure in ("evidence_only","learned")),
                           "factorial source not independently attested")
                    local+=1
            _check(len(motors)==v["lived_steps"],"original physical timeline gap")
            chains[arm]=motors
            verified[arm]={"lifecycle":v["lifecycle"],"steps":v["lived_steps"],
                            "consolidated":v["objects_consolidated"],
                            "accepted_uc":v["accepted_cognitive_uc"],
                            "local_proposals":local,"WAL_sha256":r["wal_sha256"]}
            total=overall[arm]
            total["lives"]+=1
            total["deaths"]+=int(v["lifecycle"]=="dead")
            total["steps"]+=v["lived_steps"]
            total["consolidated"]+=v["objects_consolidated"]
            total["UC"]+=v["accepted_cognitive_uc"]
            total["local_proposals"]+=local
            for name,count in v["actions"].items():
                total["motor_"+name]+=count
        # Different later histories are not comparable as equal treatment
        # effects. Only the first actual motor fork is reliable here.
        common=min(map(len,chains.values()))
        fork=next((t for t in range(1,common+1)
                   if len({json.dumps(chains[a][t],sort_keys=True)
                           for a in ARMS})>1),None)
        out.append({"world":w,"seed":seed,"first_motor_divergence":fork,
                    "first_motor_by_arm":({a:chains[a][fork][0] for a in ARMS}
                                          if fork is not None else {}),
                    "arms":verified})
    _check(len(out)==8 and all(overall[a]["lives"]==8 for a in ARMS),
           "not thirty-two independent authenticated WALs")
    return {"schema":SCHEMA,"status":"ORIGINAL_32_WAL_AUTHENTICATED",
            "scientific_verdict":"INCONCLUSIVE","source_sha":SOURCE_SHA,
            "birth_run_id":SOURCE_RUN,"verified_WAL_count":32,
            "original_WAL_untouched":True,"no_replay_resurrection":True,
            "summary":{a:dict(overall[a]) for a in ARMS},"pairs":out}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    _check(not args.output.exists(),"never overwrite original evidence")
    result=audit(args.root)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],
                      "verified_WAL_count":result["verified_WAL_count"],
                      "summary":result["summary"]},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
