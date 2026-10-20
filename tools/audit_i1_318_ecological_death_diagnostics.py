#!/usr/bin/env python3
"""#318 read-only failure-mode census of 24 separately certified mortal WALs.

The new-world result 12/12 deaths in both arms is a failure of *ecological
generalization* at this horizon, not a software test failure. Never re-birth.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _check, _number
from audit_i1_318_long_horizon_evidence import (
    ARMS, PRESETS, SEEDS, SOURCE_SHA, audit as certify,
)

SCHEMA="i1-318-ecological-24-physical-failure-diagnostics/v1"
FIELDS=("water","food","energy","integrity")


def analyse(root):
    custody=certify(root)
    _check(custody["verified_WAL_count"]==24
           and custody["source_sha"]==SOURCE_SHA
           and custody["original_WAL_untouched"] is True,
           "original mortal custody must precede diagnosis")
    summary={}
    pairs=[]
    for world in PRESETS:
        summary[world]={}
        for arm in ARMS:
            summary[world][arm]=Counter()
        for seed in SEEDS:
            one={"world":world,"seed":seed,"arms":{}}
            for arm in ARMS:
                p=root/world/str(seed)/arm/"life-01.wal"
                events=[json.loads(line)["causal_event"] for line in p.read_text().splitlines()]
                physical=[e for e in events if e.get("kind")=="world_transition_experienced"]
                commands=[e for e in events if e.get("kind")=="command_experienced"]
                receptions=[e for e in events if e.get("kind")=="i1_local_opportunity_proposed"]
                _check(len(physical)==len(commands)>0,
                       "physical event discontinuity in certified mortal WAL")
                last=physical[-1].get("body_after")
                _check(type(last) is dict and all(field in last for field in FIELDS),
                       "last witnessed body is unavailable")
                terminal={field:_number(last[field]) for field in FIELDS}
                counts=Counter(e.get("primitive") for e in commands)
                first_local=min((e.get("t_monde") for e in receptions),default=None)
                record={
                    "steps":len(commands),
                    "end_body_observed":terminal,
                    "first_local_proposal_step":first_local,
                    "physical_actions":dict(counts),
                    "local_proposal_count":len(receptions),
                    "last_action":commands[-1].get("primitive"),
                    # The terminal limiting need is descriptive, not a
                    # physical cause-of-death statement without owner proof.
                    "lowest_terminal_need":min(FIELDS,key=lambda f:terminal[f]),
                    "specific_death_cause_proven":False,
                }
                one["arms"][arm]=record
                total=summary[world][arm]
                total["lives"]+=1
                total["physical_steps"]+=len(commands)
                total["local_proposals"]+=len(receptions)
                total["zero_local_opportunity_lives"]+=int(not receptions)
                total["physical_drink_commands"]+=counts["boire"]
                total["physical_sleep_commands"]+=counts["dormir"]
                for field,val in terminal.items():
                    total[field+"_at_or_below_zero"]+=int(val<=0)
            pairs.append(one)
    return {
        "schema":SCHEMA,"status":"READ_ONLY_CERTIFIED_DEATH_DIAGNOSTICS",
        "scientific_verdict":"INCONCLUSIVE",
        "source_sha":SOURCE_SHA,"authenticated_original_WAL":24,
        "no_rebirth_or_replay":True,"no_primitive_specific_rule":True,
        "no_hidden_lethal_zone_cause_inferred":True,
        "world_totals":{
            world:{arm:dict(counts) for arm,counts in perarm.items()}
            for world,perarm in summary.items()},
        "pairs":pairs,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    _check(not args.output.exists(),"do not overwrite scientific report")
    d=analyse(args.root)
    args.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":d["status"],"scientific_verdict":d["scientific_verdict"],
        "world_totals":d["world_totals"]},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
