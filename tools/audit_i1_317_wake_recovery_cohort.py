#!/usr/bin/env python3
"""Issue #317: independent, fail-closed 32-life recovered-wake WAL audit.

Verify each actual physical transition, hash chain, provenance, bodily ending,
consolidation publication, and waking reason. No living runtime is imported
or stepped. Experimental pressure scalar was never journaled by the
research-only wrapper, so its exact value is explicitly NOT certified here.
This does not promote new natural-sleep policy or claim scientific GO.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _verify_arm
from audit_i1_spatial_navigation_314 import audit as audit_wal

SCHEMA = "i1-317-wake-recovery-32-sealed-wal/v1"
BIRTH_SCHEMA = "i1-317-wake-recovery-factorial-mortal/v1"
RUN_ID = 39302574668
EXACT_ENGINE_SHA = "9f19100e276a16edaefd17e26a1092ef98391c38"
PRESETS = ("oasis", "foraging", "dry-valley", "memory-corridor")
SEEDS = (11117, 11239)
ARMS = ("canonical", "recovered_fatigue",
        "natural_threshold", "recovered_and_threshold")
BASE_SLEEP = {
    "fatigue_gain": 0.7, "sleep_fatigue_recovery": 0.3,
    "fatigue_weight": 0.65, "consolidation_weight": 0.25,
    "night_weight": 0.2, "intrinsic_weight": 0.9,
}
WAKE_THRESHOLDS = {
    "water": 15.0, "food": 10.0, "integrity": 25.0,
    "energy": 10.0,
}
ALLOWED_WAKE_REASONS = {
    "reflex", "alert", "dated_intention", "maximum_duration", "natural_end",
}
HORIZON = 300


def require(ok, label):
    if not ok:
        raise ValueError(label)


def flags(arm):
    require(arm in ARMS, "alien intervention arm")
    return (arm in ("recovered_fatigue", "recovered_and_threshold"),
            arm in ("natural_threshold", "recovered_and_threshold"))


def _hex(value, size):
    return (type(value) is str and len(value) == size
            and all(c in "0123456789abcdef" for c in value))


def _wake_events(wal):
    """Independent passive wake statistics from the original WAL events."""
    counter = Counter()
    reduced = 0
    entered = 0
    woke_steps = set()
    with wal.open(encoding="utf-8") as stream:
        for raw in stream:
            event = json.loads(raw)["causal_event"]
            kind = event.get("kind")
            if kind == "stage10_sleep_woke":
                step = event.get("t_monde")
                reason = event.get("data", {}).get("reason")
                require(type(step) is int and 1 <= step <= HORIZON
                        and step not in woke_steps
                        and reason in ALLOWED_WAKE_REASONS,
                        "invalid/duplicated authenticated wake event")
                woke_steps.add(step)
                counter[reason] += 1
            elif kind == "stage10_reduced_capture":
                reduced += 1
                require(event.get("data", {}).get("full_cognitive_perception") is False,
                        "unobserved ordinary cognition during sleeping capture")
            elif kind == "stage10_sleep_entered":
                entered += 1
                require(event.get("data", {}).get("from_applied_dormir") is True,
                        "sleep entry not claimed from an applied command")
    require(0 <= entered - len(woke_steps) <= 1,
            "impossible sleep entry/wake cardinality")
    require(reduced >= len(woke_steps), "wake without reduced perception")
    return {"reasons": dict(counter), "reduced_captures": reduced,
            "sleep_entries": entered, "wake_count": len(woke_steps)}


def check_birth(report, world, seed, expected_sha):
    """Check every preregistered identity before any comparison."""
    require(
        report.get("schema") == BIRTH_SCHEMA
        and report.get("status") == "COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
        and report.get("source_sha") == expected_sha
        and report.get("preset") == world
        and report.get("seed") == seed
        and report.get("horizon") == HORIZON
        and report.get("preregistered_arms") == list(ARMS)
        and report.get("factorial_dimensions") == {
            "recovery_update": [False, True],
            "natural_wake_threshold": [0.1, 0.35]}
        and set(report.get("arms", {})) == set(ARMS)
        and report.get("no_sleep_or_motor_forcing") is True
        and report.get("same_world_needs_rewards_td_competition_action_control") is True
        and report.get("ordinary_wake_thresholds_unchanged") is True
        and report.get("only_natural_wake_pressure_and_threshold_intervened") is True
        and report.get("all_born_independently_and_irreversibly") is True
        and report.get("pre_registered_factorial") is True
        and report.get("no_coma_implemented") is True
        and report.get("human_equivalence_proven") is False
        and report.get("scientific_verdict") == "NO-GO"
        and _hex(report.get("physics_digest"), 64)
        and _hex(report.get("preset_sha256"), 64),
        "forged/unregistered cohort birth"
    )


def check_arm(wal, record, arm, verifier):
    """Cross-check independently authenticated WAL versus birth report."""
    recovered, raised = flags(arm)
    require(record.get("Stage10_sleep_pressure") == BASE_SLEEP,
            "stage10 weights drifted across factorial arms")
    require(record.get("physical_wake_thresholds") == WAKE_THRESHOLDS,
            "vital wake protections weakened")
    require(record.get("experimental_recovery_adjustment") is recovered
            and record.get("natural_wake_threshold") == (0.35 if raised else 0.1),
            "incorrect intervention or natural threshold")
    require(record.get("wal_relative_path") == f"{arm}/life-01.wal"
            and _hex(record.get("wal_sha256"), 64)
            and _hex(record.get("journal_head"), 64),
            "WAL identity replaced")
    physically_lived = _verify_arm(wal, record, verifier)
    wakes = _wake_events(wal)
    require(wakes["reasons"] == record.get("wake_reasons"),
            "wake reason report differs from authenticated WAL")
    require(wakes["reasons"].get("alert", 0) == physically_lived["alert_wakes"],
            "unmatched alert wakes")
    observed_evaluations = record.get("recomputed_wake_evaluations")
    reported_adjustments = record.get("pressure_adjusted_evaluations")
    require(type(observed_evaluations) is int
            and type(reported_adjustments) is int
            and 0 <= reported_adjustments <= observed_evaluations,
            "invalid non-WAL research pressure counters")
    require((observed_evaluations == wakes["reduced_captures"]) if recovered
            else (observed_evaluations == 0 and reported_adjustments == 0),
            "research wake evaluator must not skip physical reduced captures")
    require(physically_lived["lifecycle"] in {"active", "dead"},
            "not a genuine mortal outcome")
    return {
        "world_step_count": physically_lived["lived_steps"],
        "lifecycle": physically_lived["lifecycle"],
        "physical_actions": physically_lived["actions"],
        "actual_consolidated_objects": physically_lived["objects_consolidated"],
        "episode_objects_closed": physically_lived["episode_objects_closed"],
        "accepted_uc": physically_lived["accepted_cognitive_uc"],
        "night_exposure": physically_lived["night_observed_steps"],
        "wake_reasons": wakes["reasons"],
        "sleep_entries": wakes["sleep_entries"],
        "reduced_sleep_captures": wakes["reduced_captures"],
        "reported_pressure_adjusted_evaluations_UNATTESTED":
            reported_adjustments,
        "wal_sha256": record["wal_sha256"],
        "journal_head": record["journal_head"],
    }


def analyse(root, expected_sha=EXACT_ENGINE_SHA, verifier=audit_wal):
    require(expected_sha == EXACT_ENGINE_SHA, "must pin original source SHA")
    require(root.is_dir() and not root.is_symlink(), "missing sealed WAL root")
    expected_pairs = {(world, seed) for world in PRESETS for seed in SEEDS}
    actual_reports = set(root.rglob("report.json"))
    expected_reports = {root/world/str(seed)/"report.json"
                        for world, seed in expected_pairs}
    require(actual_reports == expected_reports
            and not any(p.is_symlink() for p in actual_reports),
            "missing, duplicate or alien report")
    data = {}
    hashes = set()
    pairs = {}
    for world, seed in sorted(expected_pairs):
        path = root / world / str(seed) / "report.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        check_birth(report, world, seed, expected_sha)
        pair_identity = (report["physics_digest"], report["preset_sha256"])
        if world in pairs:
            require(pairs[world] == pair_identity, "mismatched fixed world/physics")
        pairs[world] = pair_identity
        for arm in ARMS:
            record = report["arms"][arm]
            wal = root / world / str(seed) / arm / "life-01.wal"
            result = check_arm(wal, record, arm, verifier)
            require(result["wal_sha256"] not in hashes, "replayed/duplicated WAL")
            hashes.add(result["wal_sha256"])
            data[(world, seed, arm)] = result
    require(len(data) == 32 and len(hashes) == 32, "incomplete factorial")
    aggregate = {}
    for arm in ARMS:
        items = [data[(w, s, arm)] for w, s in sorted(expected_pairs)]
        actions = sum((Counter(x["physical_actions"]) for x in items), Counter())
        wakes = sum((Counter(x["wake_reasons"]) for x in items), Counter())
        steps = sum(x["world_step_count"] for x in items)
        require(sum(actions.values()) == steps, "lived physical actions lost")
        aggregate[arm] = {
            "independent_lives": len(items),
            "deaths": sum(x["lifecycle"] == "dead" for x in items),
            "survivors_at_horizon": sum(x["lifecycle"] == "active" for x in items),
            "physically_lived_steps": steps,
            "physical_sleep_steps": actions["dormir"],
            "physical_awake_actions": steps - actions["dormir"],
            "physical_actions": dict(actions),
            "wake_reasons": dict(wakes),
            "physically_consolidated_objects": sum(
                x["actual_consolidated_objects"] for x in items),
            "closed_episode_objects": sum(x["episode_objects_closed"] for x in items),
            "accepted_uc": sum(x["accepted_uc"] for x in items),
            "actual_night_exposure_steps": sum(x["night_exposure"] for x in items),
        }
    # Exact paired effects are descriptive; n=8 is not promotion evidence.
    matched = []
    for world, seed in sorted(expected_pairs):
        baseline = data[(world, seed, "canonical")]
        matched.append({
            "world": world, "seed": seed,
            "deaths": {a: data[(world, seed, a)]["lifecycle"]
                       for a in ARMS},
            "lived_step_difference_from_canonical": {
                a: data[(world, seed, a)]["world_step_count"]
                - baseline["world_step_count"] for a in ARMS if a != "canonical"},
            "consolidation_difference_from_canonical": {
                a: data[(world, seed, a)]["actual_consolidated_objects"]
                - baseline["actual_consolidated_objects"]
                for a in ARMS if a != "canonical"},
        })
    return {
        "schema": SCHEMA,
        "status": "INDEPENDENTLY_CERTIFIED_FACTORIAL_NO_SCIENTIFIC_GO",
        "exact_engine_sha": expected_sha,
        "source_run_id": RUN_ID,
        "verified_lives": len(data),
        "verified_distinct_original_wal_sha256": len(hashes),
        "motor_commands_forced": False,
        "experimental_recovery_scalar_itself_WAL_proven": False,
        "note": "The nonpersistent research wrapper did not journal each recomputed wake scalar; only real physical outcomes and wake reasons are independently certified.",
        "cold_recovery_of_experimental_adapter_verified": False,
        "coma_implemented_or_tested": False,
        "human_equivalence_proven": False,
        "scientific_verdict": "NO-GO",
        "by_arm": aggregate,
        "matched_triplets": matched,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--expected-sha", default=EXACT_ENGINE_SHA)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = analyse(args.root, args.expected_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in
        ("status", "verified_lives", "scientific_verdict", "by_arm")},
        sort_keys=True))


if __name__ == "__main__":
    main()
