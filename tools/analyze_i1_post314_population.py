#!/usr/bin/env python3
"""Fail-closed external comparison of full post-314 newborn population reports."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import mean

CANDIDATES = range(6)
WORLDS = ("oasis", "foraging", "dry-valley")
SEEDS = (1041, 1042)
HORIZON = 400


def aggregate(paths, sha, *, study='initial'):
    if not sha or len(sha) != 40:
        raise ValueError("pin one full git SHA")
    if study not in ('initial','lowcuriosity'):
        raise ValueError('unregistered study')
    candidates = range(6) if study=='initial' else range(4)
    worlds = WORLDS if study=='initial' else ('oasis','foraging','dry-valley','blocked-route')
    seeds = SEEDS if study=='initial' else (1141,1142)
    horizon = HORIZON if study=='initial' else 450
    expected={(c,w,seed) for c in candidates for w in worlds for seed in seeds}
    reports={}
    for p in paths:
        data=json.loads(Path(p).read_text(encoding="utf-8"))
        key=(data.get("candidate"),data.get("world"),data.get("seed"))
        if key in reports or key not in expected:
            raise ValueError("duplicate/foreign candidate, world or seed")
        if (data.get('study', 'initial') != study or
            data.get("status")!="COMPLETED_WITHOUT_SCIENTIFIC_VERDICT" or data.get("source_sha")!=sha):
            raise ValueError("incomplete life or mixed engine SHA")
        n=data.get("observed_steps")
        trace=data.get("trajectory")
        if (type(n) is not int or not 1<=n<=horizon or
            not isinstance(trace,list) or len(trace)!=n or
            data.get("steps_requested")!=horizon):
            raise ValueError("impossible lifespan or missing step trace")
        born=data["birth_capability_manifest"]
        active=born["capabilities"]
        if (born["birth_profile_sha256"]!=data["birth_capability_sha256"] or
            active["stage11.geographic_route_search"]!="active" or
            active["stage11.geographic_route_survey"]!="active" or
            active["stage11.first_person_place_memory"]!="conditional" or
            born["effective_configuration"]["goal_manager"]["replacement_hysteresis"]!=.04 or
            born["effective_configuration"]["goal_manager"]["critical_pressure"]!=.35 or
            born["effective_configuration"]["toxic_berry_integrity_delta"]!=-10):
            raise ValueError("wrong corrected I1 born configuration")
        if (data["wal_entries"] < n or data["wal_head"]!=trace[-1]["journal_head"]):
            raise ValueError("incomplete physical WAL attestation")
        if (data["lifecycle"]=="dead")!=(n < horizon):
            # Death *can* occur on the last step and must remain terminal.
            if not (data["lifecycle"]=="dead" and n==horizon):
                raise ValueError("death incorrectly censored")
        if data["lifecycle"] not in ("active","dead"):
            raise ValueError("invalid mortal status")
        counts=Counter(s["action"] for s in trace)
        if dict(counts)!=data["actions"]:
            raise ValueError("action trace/count contradiction")
        report_score=.7*n/horizon + .3*(1-mean(
          sum((100-max(0,min(100,float(x["body"][k]))))/100
              for k in ("water","food","energy","integrity"))/4 for x in trace
        ))
        if abs(report_score-data["external_score"])>1e-7:
            raise ValueError("score inconsistent with bodily trajectory")
        reports[key]=data
    if set(reports)!=expected:
        raise ValueError(f"missing paired lives: {len(expected-set(reports))}")
    for world in worlds:
        for seed in seeds:
            group=[reports[c,world,seed] for c in candidates]
            for k in ("world_sha256","physics_digest","effective_td","effective_sleep_version","individual_id"):
                if len({json.dumps(row[k],sort_keys=True) for row in group})!=1:
                    raise ValueError("mismatched paired life provenance: "+k)
    candidates=[]
    for cand in candidates:
        lives=[r for (c,w,s),r in reports.items() if c==cand]
        candidates.append({
            "candidate":cand, "n":len(lives),
            "deaths":sum(x["lifecycle"]=="dead" for x in lives),
            "mean_lifespan":round(mean(x["observed_steps"] for x in lives),3),
            "mean_score":round(mean(x["external_score"] for x in lives),8),
            "worst_score":min(x["external_score"] for x in lives),
            "drinks":sum(x["applied_actions"].get("boire",0) for x in lives),
            "eats":sum(x["applied_actions"].get("manger",0) for x in lives),
            "moves":sum(x["applied_actions"].get("se_deplacer",0) for x in lives),
            "memory_sightings":sum(x["memory_sightings_final"] for x in lives),
            "memory_options_proposed":sum(x['spatial_wal_audit']['stages']['proposed'] for x in lives),
            "memory_options_crossed":sum(x['spatial_wal_audit']['stages']['crossed'] for x in lives),
            "memory_physical_returns":sum(x['spatial_wal_audit']['stages']['applied_with_prior_personal_sighting'] for x in lives),
            "memory_destinations_reached":sum(x['spatial_wal_audit']['stages']['arrived_at_previously_seen_site'] for x in lives),
            "route_surveys":sum(x["observed_route_surveys_final"] for x in lives),
            "water_zero_steps":sum(x["zero_steps"]["water"] for x in lives),
        })
    candidates.sort(key=lambda x:(x["deaths"],-x["worst_score"],-x["mean_score"]))
    return {"status":"VERIFIED_PAIRED_POST314_PHYSICAL_REPORTS",
            "scientific_verdict":"NO_GO_PROMOTION_PENDING_FRESH_HELDOUT_AND_SPATIAL_WAL_CAUSAL_PROOF",
            "source_sha":sha,"study":study,"n":len(reports),
            "ranking":candidates}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--study', choices=('initial','lowcuriosity'), default='initial')
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--sha",required=True)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=aggregate(sorted(a.root.rglob("report.json")),a.sha,study=a.study)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
