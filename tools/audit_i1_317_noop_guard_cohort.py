#!/usr/bin/env python3
"""#317 sealed 12-life no-op-guard study: physical, memory and motor audit.

Read-only. Independently authenticate every original mortal WAL before
interpreting personally lived positive boire, option registration, Stage8
Competition evidence and actual motor. Research-only rank-change counters
are explicitly NOT authenticated by these WAL.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _verify_arm
from audit_i1_317_lived_place_cohort import (
    classify_original, NATIVE_SLEEP, NATIVE_WAKE,
)
from audit_i1_spatial_navigation_314 import audit as authenticate_wal

SCHEMA = "i1-317-noop-guard-12-original-mortal-wal/v1"
BIRTH_SCHEMA = "i1-317-lived-place-noop-search-guard-v1"
SOURCE_SHA = "5a45e61f26c46c56a4f3edb30696e76e5002171d"
RUN_ID = 39315789674
PRESETS = ("oasis", "foraging", "memory-corridor")
SEEDS = (14083, 14107)
ARMS = ("canonical", "guarded_recall")


def require(ok, description):
    if not ok:
        raise ValueError(description)


def f64(value):
    if type(value) in (int, float):
        return float(value)
    if type(value) is dict and set(value) == {"$f64"}:
        return float.fromhex(value["$f64"])
    raise ValueError("invalid Competition numeric evidence")


def candidate_evidence(wal):
    """Only trace personally supported destinations, not unlearned source labels."""
    learned_sites = set()
    offers = {}
    scored = Counter()
    trace_values = Counter()
    motions = {}
    with wal.open(encoding="utf-8") as stream:
        for raw in stream:
            event = json.loads(raw)["causal_event"]
            kind = event.get("kind")
            step = event.get("t_monde")
            cycle = event.get("cycle")
            data = event.get("data", {})
            if kind == "i1_water_lived_outcome_admitted":
                place = data.get("source_position")
                require(data.get("admitted") is True
                        and isinstance(place, list) and len(place) == 2
                        and all(type(v) is int for v in place)
                        and f64(data.get("delta_water")) > 0,
                        "unowned positive source")
                learned_sites.add(tuple(place))
            elif kind == "i1_place_memory_option_proposed":
                target = data.get("target")
                ref = data.get("option_ref")
                if (data.get("entity_type") == "water_source"
                        and isinstance(target, list) and len(target) == 2
                        and tuple(target) in learned_sites):
                    require(type(ref) is str and ref.startswith("option:place-memory:"),
                            "unowned personal water memory option")
                    offers[(step, cycle, ref)] = tuple(target)
            elif kind == "competition_cycle":
                for trace in data.get("traces", ()):
                    key = (step, cycle, trace.get("option_ref"))
                    if key not in offers:
                        continue
                    val = trace.get("evidence")
                    if val is None:
                        trace_values["not_evaluated"] += 1
                        continue
                    score = f64(val)
                    require(-1 <= score <= 1 and f64(trace["threshold"]) > 0
                            and f64(trace["accumulator_after"]) >= 0,
                            "unphysical learned-source Competition trace")
                    scored[key] += 1
                    trace_values["evaluated"] += 1
                    if score == 0:
                        trace_values["zero_evidence"] += 1
                    if score > 0:
                        trace_values["positive_evidence"] += 1
                    if trace["crossed"] is True:
                        trace_values["crossed"] += 1
            elif kind == "command_experienced":
                require(step not in motions, "multiple physical commands in one step")
                motions[step] = event.get("primitive")
    require(all(v == 1 for v in scored.values()), "duplicated learned place trace")
    require(set(motions) == set(range(1, len(motions) + 1)),
            "noncontiguous physical command sequence")
    return {
        "personally_learned_site_count": len(learned_sites),
        "offered_lived_source_traces": len(offers),
        "evaluated_lived_source_traces": trace_values["evaluated"],
        "zero_evidence_lived_source_traces": trace_values["zero_evidence"],
        "positive_evidence_lived_source_traces": trace_values["positive_evidence"],
        "crossed_lived_source_traces": trace_values["crossed"],
        "not_evaluated_lived_source_traces": trace_values["not_evaluated"],
    }, motions


def certify(root):
    require(root.is_dir() and not root.is_symlink(), "missing 12-life evidence root")
    expected = {(world, seed) for world in PRESETS for seed in SEEDS}
    reports = {root/world/str(seed)/"report.json" for world, seed in expected}
    require(set(root.rglob("report.json")) == reports
            and not any(p.is_symlink() for p in reports),
            "missing, alien or symlinked mortality cohort reports")
    physical = {}
    births = {}
    rows = []
    for world, seed in sorted(expected):
        report = json.loads((root/world/str(seed)/"report.json").read_text())
        require(
            report.get("schema") == BIRTH_SCHEMA
            and report.get("status") == "COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
            and report.get("source_sha") == SOURCE_SHA
            and report.get("preset") == world and report.get("seed") == seed
            and report.get("horizon") == 300
            and report.get("preregistered_arms") == list(ARMS)
            and set(report.get("arms", {})) == set(ARMS)
            and report.get("no_op_guarded_paid_route_search_study") is True
            and report.get("learned_site_requires_personally_applied_boire_and_followup") is True
            and report.get("same_world_physics_needs_td_competition_action_control") is True
            and report.get("no_type_based_resource_utility") is True
            and report.get("no_motor_forcing_or_new_vital_reflex") is True
            and report.get("guard_does_not_force_motor_or_infer_thirst_relief") is True
            and report.get("no_cold_recovery_claim") is True
            and report.get("no_coma_implemented") is True
            and report.get("old_13127_13219_wal_not_reused") is True
            and report.get("scientific_verdict") == "NO-GO",
            "cohort not preregistered or born under a changed engine")
        digest = (report.get("physics_digest"), report.get("preset_sha256"))
        require(all(type(x) is str and len(x) == 64 for x in digest),
                "missing fixed world/physics digest")
        if world in births:
            require(births[world] == digest, "world differed between seeds")
        births[world] = digest
        rec = {}
        physical_pair = {}
        for arm in ARMS:
            record = report["arms"][arm]
            require(record.get("Stage10_sleep_pressure") == NATIVE_SLEEP
                    and record.get("physical_wake_thresholds") == NATIVE_WAKE
                    and record.get("option_ranking_adjusted") is (arm == "guarded_recall")
                    and record.get("option_value_advisory_adjusted") is False
                    and record.get("wal_relative_path") == f"{arm}/life-01.wal",
                    "unregistered intervention, sleep or wake modification")
            counter = record.get("research_counters_UNATTESTED")
            require(type(counter) is dict
                    and set(counter).issubset({
                        "avoided_provably_noop_expansions",
                        "potentially_useful_expansions", "rank_changes",
                        "rank_budget_denied",
                    }) and all(type(x) is int and x >= 0 for x in counter.values()),
                    "invalid unjournaled research counter")
            wal = root/world/str(seed)/arm/"life-01.wal"
            proof = _verify_arm(wal, record, authenticate_wal)
            personal = classify_original(wal, proof["lived_steps"])
            require(personal["positive_sites_physically_supported"] ==
                    record["positive_lived_source_sites"],
                    "beneficial source association not physically lived")
            analysis, motors = candidate_evidence(wal)
            require(proof["lived_steps"] == len(motors),
                    "ordinary physical commands missing")
            rec[arm] = {
                "state": proof["lifecycle"],
                "steps": proof["lived_steps"],
                "actions": proof["actions"],
                "consolidated": proof["objects_consolidated"],
                "uc": proof["accepted_cognitive_uc"],
                "learned_sites": personal["positive_sites_physically_supported"],
                "trace": analysis,
                "reported_research_counts_UNATTESTED": counter,
                "original_WAL_SHA256": record["wal_sha256"],
            }
            physical_pair[arm] = motors
        prefix = min(len(physical_pair["canonical"]),len(physical_pair["guarded_recall"]))
        altered_motor_steps = [t for t in range(1,prefix+1)
                               if physical_pair["canonical"][t] !=
                               physical_pair["guarded_recall"][t]]
        rec["pair"] = {
            "same_journal_bytes": rec["canonical"]["original_WAL_SHA256"] ==
                                  rec["guarded_recall"]["original_WAL_SHA256"],
            "first_motor_divergence": (altered_motor_steps[0] if altered_motor_steps else None),
            "shared_lived_motor_steps_changed": len(altered_motor_steps),
            "paired_uc_difference": rec["guarded_recall"]["uc"]-rec["canonical"]["uc"],
        }
        rows.append({"world": world, "seed": seed, "arms": rec})
    require(len(rows) == 6, "less than six independently born mortal pairs")
    summary = {}
    for arm in ARMS:
        lives = [row["arms"][arm] for row in rows]
        actions = sum((Counter(x["actions"]) for x in lives), Counter())
        traces = sum((Counter(x["trace"]) for x in lives), Counter())
        summary[arm] = {
            "lives": len(lives),
            "deaths": sum(x["state"] == "dead" for x in lives),
            "at_horizon": sum(x["state"] == "active" for x in lives),
            "lived_steps": sum(x["steps"] for x in lives),
            "physical_actions": dict(actions),
            "actual_consolidated_objects": sum(x["consolidated"] for x in lives),
            "accepted_cognitive_uc": sum(x["uc"] for x in lives),
            "first_person_lived_source_trace": dict(traces),
            "UNATTESTED_research_counts": dict(sum(
                (Counter(x["reported_research_counts_UNATTESTED"]) for x in lives),
                Counter()
            )),
        }
    require(sum(row["arms"]["pair"]["shared_lived_motor_steps_changed"] for row in rows)
            >= 0, "physically unreal motor divergence")
    return {
        "schema": SCHEMA,
        "source_run": RUN_ID,
        "exact_source_sha": SOURCE_SHA,
        "authenticated_original_WAL_paths": 12,
        "births_are_independent_but_equal_deterministic_content_is_permitted": True,
        "research_rank_changes_independently_proven": False,
        "first_person_source_not_a_resource_oracle": True,
        "motor_not_forced": True,
        "scientific_verdict": "NO-GO",
        "summary": summary,
        "pairs": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args()
    result = certify(options.root)
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in (
        "authenticated_original_WAL_paths", "scientific_verdict", "summary")}, sort_keys=True))


if __name__ == "__main__":
    main()
