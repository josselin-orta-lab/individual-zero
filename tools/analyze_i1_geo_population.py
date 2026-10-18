#!/usr/bin/env python3
"""Read-only forensic audit of paired, naturally mortal I1 geography cohorts.

Accept archived GitHub artifact ZIPs OR extracted artifact directories. The
operator-only water-distance diagnostic MUST NOT enter any I1 runtime.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import io
import json
from pathlib import Path
from statistics import mean
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PROFILES = (
    (0.15, 0.35), (0.25, 0.35), (0.45, 0.35),
    (0.25, 0.75), (0.45, 0.75), (0.70, 1.00),
)
WORLDS = ("oasis", "foraging", "dry-valley")
SEEDS = (931, 932)
MAX_STEPS = 400


def _canonical(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _float_tag(obj):
    if isinstance(obj, dict) and set(obj) == {"$f64"}:
        return float.fromhex(obj["$f64"])
    if type(obj) in (float, int):
        return float(obj)
    return None


def _physical_evidence(stream, *, final_hash, expected_count, water_positions):
    """Verify each full event hash, then summarize only operator-side evidence."""
    seen_ids = set()
    previous = "0" * 64
    total = 0
    visits = []
    geo_proposals = geo_crossings = geo_cycles = 0
    geo_max_ratio = 0.0
    wake_reasons = Counter()
    applied_death = 0
    for raw in stream:
        if not raw.endswith(b"\n"):
            raise ValueError("torn causal WAL record")
        raw = raw[:-1]
        event = json.loads(raw)
        if (set(event) != {"index", "event_id", "previous_hash", "event_hash", "causal_event"}
                or _canonical(event) != raw
                or event["index"] != total
                or event["previous_hash"] != previous
                or event["event_id"] in seen_ids):
            raise ValueError("noncanonical, duplicate or reordered causal record")
        payload = _canonical({
            "event_id": event["event_id"],
            "causal_event": event["causal_event"],
        })
        new_hash = sha256(bytes.fromhex(previous) + payload).hexdigest()
        if new_hash != event["event_hash"]:
            raise ValueError("causal WAL SHA256 mismatch")
        previous = new_hash
        seen_ids.add(event["event_id"])
        total += 1
        body = event["causal_event"]
        kind = body.get("kind")
        data = body.get("data") or {}
        if kind == "stage11_geographic_visit_observed":
            loc = data.get("position")
            if (not isinstance(loc, list) or len(loc) != 2
                    or not all(type(z) is int for z in loc)):
                raise ValueError("invalid physically observed visit")
            visits.append(tuple(loc))
        if kind == "stage11_geographic_option_proposed":
            geo_proposals += 1
        if kind == "competition_cycle":
            for tr in data.get("traces", []):
                if "option:geographic:" not in str(tr.get("option_ref","")):
                    continue
                geo_cycles += 1
                geo_crossings += int(tr.get("crossed") is True)
                acc, threshold = (_float_tag(tr.get("accumulator_after")),
                                  _float_tag(tr.get("threshold")))
                if acc is not None and threshold and threshold > 0:
                    geo_max_ratio = max(geo_max_ratio, acc / threshold)
        if kind == "stage10_sleep_woke":
            wake_reasons[str(data.get("reason"))] += 1
        if kind == "individual_death_confirmed":
            applied_death += 1
    if total != expected_count or previous != final_hash:
        raise ValueError("durable WAL count or final head differs from verified report")
    if not visits:
        raise ValueError("no physical visits; cannot evaluate explored geography")
    min_water = min(
        abs(x - wx) + abs(y - wy)
        for x,y in visits for wx,wy in water_positions
    )
    return {
        "verified_wal_events": total,
        "unique_physically_visited_sites": len(set(visits)),
        "min_observed_visit_distance_to_water_operator_only": min_water,
        "physical_water_sites_reached_operator_only": sum(
            p in water_positions for p in set(visits)
        ),
        "geographic_options_proposed": geo_proposals,
        "geographic_options_competed": geo_cycles,
        "geographic_competition_crossings": geo_crossings,
        "max_geographic_accumulator_threshold_ratio": round(geo_max_ratio, 6),
        "sleep_wake_reasons": dict(wake_reasons),
        "death_seal_count": applied_death,
        "first_visited_sites": [list(p) for p in visits[:10]],
        "last_visited_sites": [list(p) for p in visits[-5:]],
    }


def _verify_report(rep, stream, expected_sha):
    if (rep.get("status") != "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
            or rep.get("source_sha") != expected_sha):
        raise ValueError("unknown report status or mixed engine SHA")
    candidate,world,seed = rep["candidate"],rep["world"],rep["seed"]
    if (type(candidate) is not int or candidate not in range(len(PROFILES))
            or world not in WORLDS or seed not in SEEDS
            or rep.get("steps_requested") != MAX_STEPS):
        raise ValueError("invalid preregistered cohort identity")
    novelty, weight = PROFILES[candidate]
    if (rep["effective_geographic_novelty"] != novelty
            or rep["effective_stage11_intrinsic_weight"] != weight
            or rep["effective_competition"] != {"threshold": 0.5, "gain": 1.0}
            or rep["birth_capability_manifest"]["effective_configuration"]["goal_manager"]["replacement_hysteresis"] != .04
            or rep["birth_capability_manifest"]["effective_configuration"]["goal_manager"]["critical_pressure"] != .35
            or rep["birth_capability_manifest"]["effective_configuration"]["toxic_berry_integrity_delta"] != -10.0):
        raise ValueError("candidate changed a nonregistered or ineffective born owner")
    if rep["birth_capability_sha256"] != rep["birth_capability_manifest"]["birth_profile_sha256"]:
        raise ValueError("birth capability attestation mismatch")
    if candidate == 0 and rep["prenatal_profile"] != {"native_unchanged":True}:
        raise ValueError("control newborn was modified")
    n = rep["observed_steps"]
    trajectory=rep["trajectory"]
    if (type(n) is not int or n < 1 or n > MAX_STEPS or len(trajectory) != n
            or rep["lifecycle"] not in ("active","dead")
            or (rep["lifecycle"] == "active" and n != MAX_STEPS)
            or trajectory[-1]["journal_head"] != rep["wal_head"]):
        raise ValueError("life is incomplete or falsely censored")
    actions = Counter(step["action"] for step in trajectory)
    if dict(actions) != rep["actions"]:
        raise ValueError("action counts differ from physical trajectory")
    zeros = {k: sum(t["body"][k] <= 0 for t in trajectory)
             for k in ("water","food","energy")}
    if zeros != rep["zero_steps"]:
        raise ValueError("bodily zero deficit accounting inconsistent")
    mean_def = mean(
        sum((100 - max(0,min(100,float(t["body"][k]))))/100
            for k in ("water","food","energy","integrity")) / 4
        for t in trajectory
    )
    score= .7*(n/MAX_STEPS)+.3*(1-mean_def)
    if abs(score-rep["external_score"])>1e-7:
        raise ValueError("operator score not reproducible from physical steps")
    path=ROOT/"src"/"i1"/"lab"/"world_presets"/(world+".json")
    world_data=json.loads(path.read_text(encoding="utf-8"))
    water={tuple(v) for v in world_data["layout"]["water_sources"]}
    if not water:
        raise ValueError("invalid control world water sources")
    evidence=_physical_evidence(stream,final_hash=rep["wal_head"],
         expected_count=rep["wal_entries"], water_positions=water)
    if (evidence["death_seal_count"] != int(rep["lifecycle"]=="dead")
            or rep["physics_digest"] != rep["birth_capability_manifest"]["effective_configuration"]["world_physics_digest"]):
        raise ValueError("death or physics evidence inconsistent")
    return {
        "candidate": candidate, "world": world, "seed": seed,
        "source_sha": expected_sha, "world_sha256":rep["world_sha256"],
        "born_physics_sha256":rep["physics_digest"],
        "born_td":rep["effective_td"],
        "born_sleep":rep["effective_sleep_version"],
        "life_id":rep["individual_id"],
        "life_steps":n, "death":rep["lifecycle"]=="dead",
        "score":round(score,9), "mean_shortage":rep["mean_shortage"],
        "actions":dict(actions), "applied_actions":rep["applied_actions"],
        "zero_steps":zeros, **evidence,
    }


def _artifact_content(path):
    """One report and one WAL per artifact; reject ambiguous partial uploads."""
    if path.suffix == ".zip":
        with ZipFile(path) as archive:
            names=archive.namelist()
            reports=[n for n in names if n.endswith("report.json")]
            journals=[n for n in names if n.endswith("life.wal")]
            if len(reports)!=1 or len(journals)!=1:
                raise ValueError("ambiguous or incomplete archived mortal life")
            report=json.loads(archive.read(reports[0]))
            with archive.open(journals[0]) as raw:
                yield report,raw
    else:
        report=json.loads(path.read_text(encoding="utf-8"))
        wal=path.with_name("life.wal")
        if not wal.exists():
            raise ValueError("missing original WAL for life")
        with wal.open("rb") as raw:
            yield report, raw


def aggregate(root, expected_sha):
    root=Path(root)
    archives=sorted(root.rglob("geo-*.zip"))
    if not archives:
        archives=sorted(root.rglob("report.json"))
    expected={(c,w,s) for c in range(len(PROFILES)) for w in WORLDS for s in SEEDS}
    if len(archives)!=len(expected):
        raise ValueError(f"missing/extra physical WALs: expected {len(expected)}, got {len(archives)}")
    lives={}
    for file in archives:
        for rep,stream in _artifact_content(file):
            outcome=_verify_report(rep,stream,expected_sha)
            key=(outcome["candidate"],outcome["world"],outcome["seed"])
            if key in lives or key not in expected:
                raise ValueError("duplicate or unregistered paired life")
            lives[key]=outcome
    if set(lives)!=expected:
        raise ValueError("not all preregistered paired lives were independently witnessed")
    for world in WORLDS:
        for seed in SEEDS:
            group=[lives[c,world,seed] for c in range(len(PROFILES))]
            for k in ("world_sha256","born_physics_sha256","born_td","born_sleep","life_id"):
                if len({json.dumps(g[k],sort_keys=True) for g in group})!=1:
                    raise ValueError("control and treatment were not physically paired: "+k)
    ranking=[]
    for cand in range(len(PROFILES)):
        group=[o for k,o in lives.items() if k[0]==cand]
        ranking.append({
            "candidate":cand,
            "preregistered_profile":(
                {"native_unchanged":True} if cand==0 else
                {"novelty":PROFILES[cand][0],"intrinsic":PROFILES[cand][1]}),
            "n":len(group), "deaths":sum(g["death"] for g in group),
            "mean_lifespan":round(mean(g["life_steps"] for g in group),2),
            "mean_score":round(mean(g["score"] for g in group),8),
            "worst_score":min(g["score"] for g in group),
            "total_drinks":sum(g["applied_actions"].get("boire",0) for g in group),
            "total_eats":sum(g["applied_actions"].get("manger",0) for g in group),
            "total_movements":sum(g["applied_actions"].get("se_deplacer",0) for g in group),
            "total_water_zero_steps":sum(g["zero_steps"]["water"] for g in group),
            "total_food_zero_steps":sum(g["zero_steps"]["food"] for g in group),
            "water_sites_reached":sum(g["physical_water_sites_reached_operator_only"]>0 for g in group),
            "geographic_competition_crossings":sum(g["geographic_competition_crossings"] for g in group),
        })
    # Descriptive sorting, NOT approval for promotion or model editing.
    ranking.sort(key=lambda v:(v["deaths"],-v["worst_score"],-v["mean_score"]))
    return {
        "status":"FULL_WAL_VERIFIED_POPULATION_OBSERVATION",
        "source_sha":expected_sha,
        "scientific_verdict":"NO_GO_PROMOTION_PENDING_REPLICATION",
        "scope":"36 newly born, independent, mortal lives",
        "operator_only_diagnostic":"water-distance labels never entered an individual",
        "candidate_summary":ranking,
        "lives":[lives[k] for k in sorted(lives)],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--sha",required=True)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    result=aggregate(args.root,args.sha)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","scientific_verdict","source_sha","candidate_summary")},indent=2))


if __name__=="__main__":
    main()
