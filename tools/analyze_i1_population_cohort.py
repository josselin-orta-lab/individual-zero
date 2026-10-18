#!/usr/bin/env python3
"""Independent read-only analysis of frozen, matched I1 population life reports."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from statistics import mean

PREREGISTERED_SHA = "7839faccda89ff04545bfef94ae6f1d6115cae6c"


def _step_body(step):
    if not isinstance(step.get("body"), dict):
        raise ValueError("missing observed body")
    for k in ("water", "food", "energy", "integrity"):
        n = step["body"].get(k)
        if type(n) not in (float, int) or not 0 <= n <= 100:
            raise ValueError("unphysical or missing body observation")
    return step["body"]


def _summarize(report):
    trace = report["trajectory"]
    n = report["observed_steps"]
    if not trace or n != len(trace) or n > report["steps_requested"]:
        raise ValueError("incomplete or impossible life trajectory")
    if report["wal_entries"] < n:
        raise ValueError("not enough authenticated WAL records")
    if "journal_head" not in trace[-1] or "wal_head" not in report:
        raise ValueError("missing final WAL head in report")
    if trace[-1]["journal_head"] != report["wal_head"]:
        raise ValueError("reported WAL head differs from last observed step")
    if report["birth_capability_manifest"]["birth_profile_sha256"] != report["birth_capability_sha256"]:
        raise ValueError("birth capability hash mismatch")
    if (report["effective_goal"]["hysteresis"],
            report["effective_goal"]["critical"]) != (.04,.35):
        raise ValueError("not the calibrated canonical natural I1")
    if report["birth_capability_manifest"]["effective_configuration"]["toxic_berry_integrity_delta"] != -10:
        raise ValueError("invalid born toxic berry physics")
    if report["status"] != "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT":
        raise ValueError("incomplete individual")
    if report["lifecycle"] not in ("dead", "active"):
        raise ValueError("unknown individual lifecycle")
    body = [_step_body(step) for step in trace]
    zero = {k:sum(row[k] <= 0 for row in body) for k in ("water", "food", "energy")}
    if zero != report["zero_steps"]:
        raise ValueError("reported zero-step counts disagree with the trajectory")
    actual_score = 0.7*n/report["steps_requested"]+0.3*(1.0-
        mean(sum((100-row[k])/100 for k in ("water","food","energy","integrity"))/4
             for row in body))
    if abs(actual_score - report["score"]) > 1e-7:
        raise ValueError("externally computed score inconsistent")
    counts = Counter((step.get("action") or "NO_COMMAND") for step in trace)
    published_counts = Counter({str(k) if k is not None else "NO_COMMAND":v
                                for k,v in report["actions"].items()})
    if counts != published_counts and not (
        counts["NO_COMMAND"] == published_counts.get("null",0)
        and all(counts[k] == published_counts[k] for k in counts if k != "NO_COMMAND")
    ):
        raise ValueError("reported action counts disagree with trajectory")
    first_zero = {k:next((i+1 for i,row in enumerate(body) if row[k]<=0),None)
                  for k in ("water","food","energy","integrity")}
    return {
        "candidate":report["candidate"],
        "world":report["world"],"seed":report["seed"],
        "status":report["lifecycle"],"duration":n,
        "score":report["score"],
        "mean_shortage":report["mean_normalized_shortage"],
        "water_zero_steps":zero["water"],"food_zero_steps":zero["food"],
        "energy_zero_steps":zero["energy"],"first_zero":first_zero,
        "actions":dict(counts),
        "final_body":body[-1],"min_integrity":min(row["integrity"] for row in body),
        "goal_transitions":len(report["goal_type_transitions"]),
        "world_physics":report["effective_physics_digest"],
        "born_td":report["effective_td"],
        "born_competition":report["effective_competition"],
        "birth_capabilities":report["birth_capability_manifest"]["capabilities"],
        "identity":report["life_id"],
    }


def analyze(paths, *, expected_sha, candidates, worlds, seeds):
    candidates=set(candidates)
    worlds=set(worlds)
    seeds=set(seeds)
    if not candidates or 0 not in candidates or not worlds or not seeds:
        raise ValueError("requires a native control and explicit matched cohort")
    expected={(c,w,s) for c in candidates for w in worlds for s in seeds}
    reports={}
    for path in paths:
        r=json.loads(Path(path).read_text(encoding="utf-8"))
        if r.get("git_sha") != expected_sha:
            raise ValueError("source SHA mismatch or mixed code")
        key=(r["candidate"],r["world"],r["seed"])
        if key not in expected or key in reports:
            raise ValueError("unregistered or duplicate individual")
        reports[key]=_summarize(r)
    if set(reports)!=expected:
        raise ValueError("missing matched individuals: "+str(sorted(expected-set(reports))))
    for world in worlds:
        for seed in seeds:
            rows=[reports[c,world,seed] for c in sorted(candidates)]
            for a in rows[1:]:
                for field in ("world_physics","born_td","birth_capabilities","identity"):
                    if a[field]!=rows[0][field]:
                        raise ValueError("paired lives differ in non-treatment property: "+field)
    ranking=[]
    for candidate in sorted(candidates):
        cases=[r for (c,w,s),r in reports.items() if c==candidate]
        baseline=[reports[0,c["world"],c["seed"]] for c in cases]
        ranking.append({
            "candidate":candidate,
            "mean_score":round(mean(x["score"] for x in cases),8),
            "worst_score":round(min(x["score"] for x in cases),8),
            "mean_delta_from_native":round(mean(
                x["score"]-b["score"] for x,b in zip(cases,baseline)),8),
            "deaths":sum(x["status"]=="dead" for x in cases),
            "mean_duration":round(mean(x["duration"] for x in cases),2),
            "total_water_zero":sum(x["water_zero_steps"] for x in cases),
            "total_energy_zero":sum(x["energy_zero_steps"] for x in cases),
            "drinks":sum(x["actions"].get("boire",0) for x in cases),
            "eats":sum(x["actions"].get("manger",0) for x in cases),
            "waits":sum(x["actions"].get("attendre",0) for x in cases),
            "mean_goal_switches":round(mean(x["goal_transitions"] for x in cases),2),
        })
    ranking.sort(key=lambda x:(-x["worst_score"],-x["mean_score"]))
    world_results={}
    for world in sorted(worlds):
        rows=[x for x in reports.values() if x["world"]==world]
        world_results[world]={
            "individuals":len(rows),"deaths":sum(x["status"]=="dead" for x in rows),
            "water_zero_steps":sum(x["water_zero_steps"] for x in rows),
            "drinks":sum(x["actions"].get("boire",0) for x in rows),
            "eats":sum(x["actions"].get("manger",0) for x in rows),
            "waits":sum(x["actions"].get("attendre",0) for x in rows),
            "durations":sorted(x["duration"] for x in rows),
        }
    return {
        "status":"VERIFIED_PAIRED_REPORTS",
        "scope":"physical observables and owner-provenance from reports; WAL chain audited by source job",
        "sha":expected_sha,
        "scientific_verdict":"NO_GO_PROMOTION_UNTIL_HELDOUT",
        "ranking":ranking,
        "worlds":world_results,
        "lives":[reports[k] for k in sorted(reports)],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--sha",default=PREREGISTERED_SHA)
    p.add_argument("--candidates",type=int,nargs="+",default=list(range(6)))
    p.add_argument("--worlds",nargs="+",default=["oasis","foraging"])
    p.add_argument("--seeds",type=int,nargs="+",default=[911,912])
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    x=analyze(sorted(a.root.rglob("report.json")),expected_sha=a.sha,
              candidates=a.candidates,worlds=a.worlds,seeds=a.seeds)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:x[k] for k in ("status","scientific_verdict","ranking","worlds")},
                     indent=2))

if __name__=="__main__":
    main()
