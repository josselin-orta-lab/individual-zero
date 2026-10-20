#!/usr/bin/env python3
"""Issue #317: sealed observational capacity and throughput audit for Stage10.

This audit DOES NOT create coma, alter sleep, infer resource utility or
replace physical actions. Capacity crossings are shadow observations,
not intervention outcomes. Every living episode and published batch
is independently witnessed in the original mortal hash-chained WAL.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
from tempfile import TemporaryDirectory

from audit_i1_spatial_navigation_314 import audit as verify_wal
from audit_i1_317_fresh_population import FRESH_SEEDS, PRESETS, design

SCHEMA = "i1-317-consolidation-capacity-shadow/v1"
CAPACITIES = (16, 32, 64, 128)
ENGINE = "28dfa62d6cf05ebecd1d2767769aa6ae53224616"


def finite(raw):
    if type(raw) in (float, int):
        result = float(raw)
    elif isinstance(raw, dict) and set(raw) == {"$f64"}:
        result = float.fromhex(raw["$f64"])
    else:
        raise ValueError("body value not physically witnessed")
    if not isfinite(result) or not 0 <= result <= 100:
        raise ValueError("non-physical body value")
    return result


def info(e):
    value = e.get("data")
    return value if isinstance(value, dict) else {}


def classify(events, steps):
    """Pure classifier. Caller must independently authenticate complete WAL."""
    if type(steps) is not int or not 1 <= steps <= 300:
        raise ValueError("invalid physically lived horizon")
    groups = defaultdict(list)
    for e in events:
        t = e.get("t_monde")
        if type(t) is int and t >= 1:
            if t > steps:
                raise ValueError("WAL event after death/horizon")
            groups[t].append(e)
    created, committed = set(), set()
    last_commit = None
    batches = 0
    histories = []
    for t in range(1, steps+1):
        rows = groups[t]
        closed = [e for e in rows if e.get("kind") == "step_closed"]
        transitions = [e for e in rows
                       if e.get("kind") == "world_transition_experienced"]
        if len(closed) != 1 or len(transitions) != 1:
            raise ValueError("missing/duplicate physically completed world step")
        closure = info(closed[0])
        if (closure.get("outcome") not in ("normal", "dead")
            or (closure.get("outcome") == "dead" and t != steps)
            or closure.get("world_advance_count") != 1
            or closure.get("applied_command_count") != 1):
            raise ValueError("unapplied/unsafe physical action")
        body = transitions[0].get("body_after")
        if not isinstance(body, dict):
            raise ValueError("missing physical body")
        physiological = {
            k: finite(body[k]) for k in ("water", "food", "integrity", "energy")
        }
        published = []
        receipt = []
        new_episodes = 0
        for e in rows:
            kind = e.get("kind")
            if kind == "episode_closed":
                eid = info(e).get("id")
                if not isinstance(eid, str) or not eid or eid in created:
                    raise ValueError("invented/repeated episode closure")
                created.add(eid)
                new_episodes += 1
            elif kind == "stage10_consolidation_version_activated":
                pub = info(e)
                refs = pub.get("batch")
                if (type(refs) is not list or not refs
                    or any(type(x) is not str or x not in created
                           or x in committed for x in refs)
                    or len(set(refs)) != len(refs)):
                    raise ValueError("unlived or duplicated consolidated object")
                published.append(pub)
                committed.update(refs)
            elif kind == "stage10_consolidation_committed":
                receipt.append(info(e))
        if len(published) != len(receipt) or len(published) > 1:
            raise ValueError("unmatched/broken consolidation transaction")
        if published:
            if (published[0].get("consolidation_id") !=
                    receipt[0].get("consolidation_id")
                or published[0].get("new_history_version") !=
                    receipt[0].get("new_history_version")
                or receipt[0].get("world_step") != t):
                raise ValueError("unmatched atomic consolidation publication")
            last_commit = t
            batches += 1
        pending = len(created)-len(committed)
        if pending < 0:
            raise ValueError("impossible pending consolidation backlog")
        histories.append({
            "world_step": t, "pending": pending,
            "water": physiological["water"], "food": physiological["food"],
            "integrity": physiological["integrity"],
            "energy": physiological["energy"],
            "episode_closures": new_episodes,
            "episode_objects_consolidated": (
                len(published[0]["batch"]) if published else 0
            ),
        })
    probes = {}
    for n in CAPACITIES:
        first = next((h for h in histories if h["pending"] >= n), None)
        if first is None:
            probes[str(n)] = {
                "crossed": False, "first_step": None,
                "body_at_first_crossing": None,
                "physically_witnessed_recovery_to_half": False,
            }
            continue
        recovered = any(
            h["pending"] <= n//2 and h["world_step"] > first["world_step"]
            for h in histories)
        probes[str(n)] = {
            "crossed": True, "first_step": first["world_step"],
            "pending_at_first_crossing": first["pending"],
            "body_at_first_crossing": {
                k: first[k] for k in ("water", "food", "integrity", "energy")
            },
            "physically_witnessed_recovery_to_half": recovered,
            "remaining_backlog_at_horizon": histories[-1]["pending"],
            "coma_not_tested": True,
        }
    return {
        "episodes_closed": len(created),
        "episode_objects_consolidated": len(committed),
        "consolidation_batches": batches,
        "final_pending": histories[-1]["pending"],
        "maximum_pending": max(x["pending"] for x in histories),
        "last_consolidation_step": last_commit,
        "unconsolidated_steps_since_last_batch": (
            None if last_commit is None else steps - last_commit),
        "probes": probes,
        "actual_coma_events": 0,
        "capacity_is_shadow_not_a_policy": True,
    }


def _sealed(path, expected_sha, expected_head, expected_events):
    if not path.is_file() or path.is_symlink():
        raise ValueError("WAL not regular and accessible")
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected_sha:
        raise ValueError("wrong original WAL digest")
    with TemporaryDirectory(prefix="i1-317-capacity-evidence-") as temp:
        copy = Path(temp) / "sealed.wal"
        copy.write_bytes(raw)
        certified = verify_wal(copy)
    if (certified["independent_hash_chain_verified"] is not True
        or certified["journal_head"] != expected_head
        or certified["journal_entries"] != expected_events):
        raise ValueError("independent WAL custody mismatch")
    events = [json.loads(line)["causal_event"] for line in raw.splitlines()]
    if len(events) != expected_events:
        raise ValueError("WAL custody changed during classification")
    return events


def analyse(root, report_path):
    manifest_bytes = report_path.read_bytes()
    report = json.loads(manifest_bytes)
    pre = report.get("preregistered_design", {})
    if (report.get("schema") != "i1-317-fresh-current-model-population/v1"
        or report.get("status") !=
           "SEALED_OBSERVATIONAL_POPULATION_NO_SCIENTIFIC_GO"
        or report.get("scientific_verdict") != "NO-GO"
        or pre.get("engine_sha") != ENGINE):
        raise ValueError("wrong or mutable preregistered science")
    people = report["individuals"]
    expected = design(PRESETS, FRESH_SEEDS)
    if (len(people) != len(expected)
        or {(p["world"], p["seed"]) for p in people} != set(expected)):
        raise ValueError("missing/duplicated predeclared birth")
    lives = []
    for p in sorted(people, key=lambda x: (x["world"], x["seed"])):
        wal = root / p["world"] / str(p["seed"]) / "life-01.wal"
        events = _sealed(wal, p["source_wal_sha256"],
                         p["journal_head"], p["verified_journal_entries"])
        a = classify(events, p["physically_lived_steps"])
        if a["consolidation_batches"] != p["sleep_consolidation_commits"]:
            raise ValueError("consolidation count contradicts published life")
        a.update({"world": p["world"], "seed": p["seed"],
                  "lifecycle": p["lifecycle"], "life_id": p["life_id"],
                  "wal_sha256": p["source_wal_sha256"],
                  "physically_lived_steps": p["physically_lived_steps"]})
        lives.append(a)
    return {
        "schema": SCHEMA,
        "source_manifest_sha256": sha256(manifest_bytes).hexdigest(),
        "source_engine": ENGINE, "births": len(lives),
        "deaths": sum(x["lifecycle"] == "dead" for x in lives),
        "total_episodes_closed": sum(x["episodes_closed"] for x in lives),
        "total_consolidated": sum(
            x["episode_objects_consolidated"] for x in lives),
        "total_pending_at_horizons": sum(x["final_pending"] for x in lives),
        "candidate_capacity_shadow": {
            str(n): {
                "crossed_by_lives": sum(
                    x["probes"][str(n)]["crossed"] for x in lives),
                "first_crossing_at_water_10_or_lower": sum(
                    x["probes"][str(n)]["crossed"]
                    and x["probes"][str(n)]
                        ["body_at_first_crossing"]["water"] <= 10
                    for x in lives),
                "recovered_to_half_in_observed_trajectory": sum(
                    x["probes"][str(n)]
                     ["physically_witnessed_recovery_to_half"] for x in lives),
            } for n in CAPACITIES
        },
        "lives": lives,
        "coma_physically_tested": False,
        "survival_under_coma_proven": False,
        "scientific_verdict": "NO-GO",
        "interpretation": "Shadow capacity crossings do not simulate coma, "
                          "causal recovery, or survival. No individual altered.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--population-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("never overwrite historical science report")
    result = analyse(args.root, args.population_report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({
        k: result[k] for k in (
            "births", "deaths", "total_episodes_closed",
            "total_consolidated", "total_pending_at_horizons",
            "candidate_capacity_shadow", "coma_physically_tested",
            "scientific_verdict")
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
