#!/usr/bin/env python3
"""#317 independent prospective sleep cohort audit: SEALED WAL, never replay.

Reads all 8 preregistered world/seed triplets from run #39297909539.
Reports alone are not evidence: independently verify each original WAL hash
chain, physical transitions, consolidation publications, accepted UCs and
body-state outcome. This tool never imports or dispatches a living actor.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from math import isclose, isfinite
from pathlib import Path

from run_i1_317_two_process_sleep import ARMS, HORIZON, PRESETS, PROFILES, SEEDS

SCHEMA = "i1-317-two-process-sealed-cohort/v1"
BIRTH_SCHEMA = "i1-317-two-process-sleep-mortal-pairs/v1"
BASE_SLEEP = {
    "fatigue_gain": 0.7, "sleep_fatigue_recovery": 0.3,
    "fatigue_weight": 0.65, "consolidation_weight": 0.25,
    "night_weight": 0.2, "intrinsic_weight": 0.9,
}
# Verified canonical I1 Stage4 fixture: day=300, night=[201,300].
NIGHT_START = 201


def _check(condition, message):
    if not condition:
        raise ValueError(message)


def _hex(value, length):
    return (type(value) is str and len(value) == length
            and all(c in "0123456789abcdef" for c in value))


def _number(value):
    if type(value) in (int, float):
        return float(value)
    if isinstance(value, dict) and set(value) == {"$f64"}:
        return float.fromhex(value["$f64"])
    raise ValueError("unrecognized WAL body number")


def _same(x, y):
    return isfinite(x) and isfinite(y) and isclose(x, y, abs_tol=1e-8, rel_tol=1e-10)


def _scan_physical_wal(path):
    """Cross-check the summarizer with a separate event/attempt scan."""
    commands, transitions, closures = {}, {}, {}
    counts = Counter()
    accepted_uc = 0
    episode_refs, consolidated_refs = set(), set()
    wakes = set()
    last_body = last_position = None
    with path.open(encoding="utf-8") as stream:
        for index, line in enumerate(stream):
            event = json.loads(line)["causal_event"]
            kind, t, data = event["kind"], event.get("t_monde"), event.get("data", {})
            counts[kind] += 1
            if kind in {"command_experienced", "world_transition_experienced", "step_closed"}:
                _check(type(t) is int and 1 <= t <= HORIZON, "invalid physical step index")
                target = {"command_experienced": commands,
                          "world_transition_experienced": transitions,
                          "step_closed": closures}[kind]
                _check(t not in target, "duplicated physical event at world step")
                target[t] = (index, event)
            if kind == "compute_charge" and data.get("accepted") is True:
                value = data.get("requested_uc")
                _check(type(value) is int and value >= 0, "invalid accepted UC")
                accepted_uc += value
            if kind == "episode_closed":
                ref = data.get("id")
                _check(isinstance(ref, str) and ref not in episode_refs,
                       "duplicated or absent lived episode reference")
                episode_refs.add(ref)
            if kind == "stage10_consolidation_version_activated":
                refs = data.get("batch")
                _check(isinstance(refs, list) and bool(refs),
                       "consolidation publication with empty batch")
                for ref in refs:
                    _check(isinstance(ref, str) and ref not in consolidated_refs,
                           "duplicated/invented consolidated reference")
                    consolidated_refs.add(ref)
            if kind == "stage10_sleep_woke" and data.get("reason") == "alert":
                _check(t not in wakes, "duplicate critical alert wake")
                wakes.add(t)
    n = len(closures)
    _check(1 <= n <= HORIZON and set(closures) == set(range(1, n + 1)),
           "non-contiguous physically closed life")
    _check(set(commands) == set(closures) == set(transitions),
           "missing command, body transition or closure")
    physically_applied = {}
    for t in range(1, n + 1):
        i, cmd = commands[t]
        j, transition = transitions[t]
        k, close = closures[t]
        _check(i < j < k and
               cmd.get("attempt_ref") == transition.get("attempt_ref") ==
               close.get("attempt_ref"), "not one ordered physical attempt")
        closure = close["data"]
        _check(closure.get("applied_command_count") == 1
               and closure.get("world_advance_count") == 1
               and closure.get("outcome") in {"normal", "dead"}
               and cmd.get("emitter") == "action_control",
               "unapplied command counted as lived physical action")
        _check(t == n or closure["outcome"] != "dead",
               "physical action after irreversible death")
        primitive = cmd.get("primitive")
        _check(isinstance(primitive, str) and primitive, "invalid physical primitive")
        physically_applied[t] = primitive
        last_body = transition["body_after"]
        last_position = transition["position_after"]
    _check(consolidated_refs.issubset(episode_refs),
           "publication references an episode not lived")
    _check(counts["stage10_consolidation_committed"]
           == counts["stage10_consolidation_version_activated"],
           "unmatched atomic consolidation commitment")
    _check(all(type(t) is int and 1 <= t <= n for t in wakes),
           "alert after terminal physical step")
    sleep = [physically_applied[t] == "dormir" for t in range(1, n + 1)]
    night = [NIGHT_START <= t <= 300 for t in range(1, n + 1)]
    lengths, streak = [], 0
    for s in sleep + [False]:
        if s:
            streak += 1
        elif streak:
            lengths.append(streak)
            streak = 0
    return {
        "lived_steps": n,
        "lifecycle": "dead" if closures[n][1]["data"]["outcome"] == "dead" else "active",
        "actions": dict(Counter(physically_applied.values())),
        "sleep_fraction": sum(sleep) / n,
        "day_observed_steps": n - sum(night),
        "night_observed_steps": sum(night),
        "day_sleep_fraction": sum(s and not is_night for s, is_night in zip(sleep, night))
                              / (n - sum(night)) if n != sum(night) else None,
        "night_sleep_fraction": sum(s and is_night for s, is_night in zip(sleep, night))
                                / sum(night) if any(night) else None,
        "physical_sleep_bouts": len(lengths),
        "maximum_sleep_bout_steps": max(lengths, default=0),
        "alert_wakes": len(wakes),
        "alert_wakes_followed_by_sleep": sum(physically_applied[t] == "dormir" for t in wakes),
        "consolidation_commits": counts["stage10_consolidation_committed"],
        "objects_consolidated": len(consolidated_refs),
        "episode_objects_closed": len(episode_refs),
        "pending_episode_objects": len(episode_refs) - len(consolidated_refs),
        "accepted_cognitive_uc": accepted_uc,
        "final_body": {k: _number(v) for k, v in last_body.items()},
        "final_position": last_position,
    }


def _verify_arm(wal, record, verifier):
    _check(wal.is_file() and not wal.is_symlink(), "WAL missing or symlink")
    _check(_hex(record.get("wal_sha256"), 64)
           and sha256(wal.read_bytes()).hexdigest() == record["wal_sha256"],
           "original WAL checksum mismatch")
    proof = verifier(wal)
    _check(proof["independent_hash_chain_verified"] is True
           and proof["journal_head"] == record["journal_head"]
           and proof["journal_entries"] == record["verified_journal_entries"],
           "independent WAL authenticity failed")
    scan = _scan_physical_wal(wal)
    for field in ("lived_steps", "lifecycle", "physical_sleep_bouts",
                  "maximum_sleep_bout_steps", "alert_wakes",
                  "alert_wakes_followed_by_sleep", "consolidation_commits",
                  "objects_consolidated", "episode_objects_closed",
                  "pending_episode_objects", "accepted_cognitive_uc",
                  "day_observed_steps", "night_observed_steps"):
        _check(scan[field] == record.get(field),
               "report/WAL contradiction: " + field)
    _check(scan["actions"] == record.get("action_counts"),
           "report/WAL physical action distribution differs")
    for field in ("sleep_fraction", "day_sleep_fraction", "night_sleep_fraction"):
        a, b = scan[field], record.get(field)
        _check((a is None and b is None)
               or (type(b) is float and _same(a, b)),
               "report/WAL phase distribution differs: " + field)
    _check(scan["final_position"] == record.get("final_position"),
           "final position not physically observed")
    _check(scan["final_body"].keys() == record.get("final_body", {}).keys(),
           "terminal bodily telemetry fields mismatch")
    for key, value in scan["final_body"].items():
        _check(_same(value, float(record["final_body"][key])),
               "terminal physical body mismatch: " + key)
    _check(scan["lifecycle"] == "dead" or scan["lived_steps"] == HORIZON,
           "non-dead life censored before its authorized horizon")
    return scan


def analyse(root, expected_sha, *, verifier=None):
    _check(_hex(expected_sha, 40), "exact cohort engine SHA required")
    _check(root.is_dir() and not root.is_symlink(), "missing cohort directory")
    if verifier is None:
        from audit_i1_spatial_navigation_314 import audit
        verifier = audit
    expected = {(w, s) for w in PRESETS for s in SEEDS}
    found = {}
    expected_reports = {root / w / str(seed) / "report.json" for w, seed in expected}
    actual_reports = set(root.rglob("report.json"))
    _check(actual_reports == expected_reports and not any(p.is_symlink() for p in actual_reports),
           "missing, duplicate or alien birth reports")
    for world, seed in sorted(expected):
        report = json.loads((root / world / str(seed) / "report.json").read_text())
        _check(report.get("schema") == BIRTH_SCHEMA
               and report.get("status") == "COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
               and report.get("source_sha") == expected_sha
               and report.get("preset") == world and report.get("seed") == seed
               and report.get("horizon") == HORIZON
               and report.get("preregistered_arms") == list(ARMS)
               and set(report.get("arms", {})) == set(ARMS)
               and report.get("no_sleep_or_motor_forcing") is True
               and report.get("same_world_needs_rewards_td_competition_action_control") is True
               and report.get("ordinary_wake_thresholds_unchanged") is True
               and report.get("all_born_independently_and_irreversibly") is True
               and report.get("no_coma_implemented") is True
               and report.get("scientific_verdict") == "NO-GO"
               and _hex(report.get("physics_digest"), 64)
               and _hex(report.get("preset_sha256"), 64),
               "invalid pre-registered birth provenance")
        for arm in ARMS:
            record = report["arms"][arm]
            expected_params = BASE_SLEEP if arm == "canonical" else PROFILES[arm]
            _check(all(record.get("Stage10_sleep_pressure", {}).get(key) == val
                       for key, val in expected_params.items()
                       if key in BASE_SLEEP),
                   "incorrect frozen experimental sleep policy")
            _check(record.get("physical_wake_thresholds") ==
                   {"water": 15.0, "food": 10.0, "integrity": 25.0,
                    "energy": 10.0}, "first-person wake rule changed")
            _check(record.get("wal_relative_path") == arm + "/life-01.wal",
                   "WAL path replaced")
            observed = _verify_arm(root / world / str(seed) / arm / "life-01.wal",
                                   record, verifier)
            found[(world, seed, arm)] = observed
    _check(len(found) == 24, "not the 24 pre-registered mortal lives")
    summary = {}
    for arm in ARMS:
        rows = [found[(world, seed, arm)] for world, seed in sorted(expected)]
        total_steps = sum(r["lived_steps"] for r in rows)
        actions = sum((Counter(r["actions"]) for r in rows), Counter())
        _check(sum(actions.values()) == total_steps, "unaccounted physical actions")
        summary[arm] = {
            "lives": len(rows),
            "deaths": sum(r["lifecycle"] == "dead" for r in rows),
            "alive_at_horizon": sum(r["lifecycle"] == "active" for r in rows),
            "physically_lived_steps": total_steps,
            "actions": dict(actions),
            "physical_sleep_fraction": actions["dormir"] / total_steps,
            "night_exposed_lives": sum(r["night_observed_steps"] > 0 for r in rows),
            "physically_observed_night_steps": sum(r["night_observed_steps"] for r in rows),
            "consolidation_commits": sum(r["consolidation_commits"] for r in rows),
            "actual_consolidated_objects": sum(r["objects_consolidated"] for r in rows),
            "closed_episodes": sum(r["episode_objects_closed"] for r in rows),
            "accepted_uc": sum(r["accepted_cognitive_uc"] for r in rows),
            "accepted_uc_per_lived_step": sum(r["accepted_cognitive_uc"] for r in rows) / total_steps,
            "critical_alert_wakes": sum(r["alert_wakes"] for r in rows),
            "alert_wakes_followed_by_sleep": sum(r["alert_wakes_followed_by_sleep"] for r in rows),
        }
    comparisons = []
    for world, seed in sorted(expected):
        baseline = found[(world, seed, "canonical")]
        comparisons.append({
            "world": world, "seed": seed,
            "arms": {a: {k: found[(world, seed, a)][k] for k in (
                "lifecycle", "lived_steps", "actions", "objects_consolidated",
                "accepted_cognitive_uc", "night_observed_steps",
                "alert_wakes_followed_by_sleep")}
                for a in ARMS},
            "homeostatic_minus_canonical_lived_steps":
                found[(world, seed, "homeostatic")]["lived_steps"]-baseline["lived_steps"],
            "circadian_minus_canonical_lived_steps":
                found[(world, seed, "circadian")]["lived_steps"]-baseline["lived_steps"],
        })
    return {
        "schema": SCHEMA,
        "status": "SEALED_PROSPECTIVE_SLEEP_COHORT_NO_GLOBAL_GO",
        "source_run": 39297909539,
        "exact_engine_sha": expected_sha,
        "exact_births": len(found),
        "no_prior_life_replayed": True,
        "scientific_verdict": "NO-GO",
        "circadian_effect_isolated": False,
        "circadian_caveat": (
            "The circadian candidate also changes fatigue and consolidation "
            "parameters, so even exposed nights cannot identify night weighting alone."
        ),
        "coma_tested": False,
        "summary": summary,
        "matched_triplets": comparisons,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = analyse(args.root, args.expected_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in (
        "status", "exact_births", "scientific_verdict", "summary")}, indent=2))


if __name__ == "__main__":
    main()
