#!/usr/bin/env python3
"""#318 first-person critical-wake/sleep reentry audit of 16 sealed native WAL.

Independently authenticate the entire original irreversible physical cohort
BEFORE counting an awake alert wake followed by a *new* decision to dormir.
This is an observed decision pathology, never a claim that thirsty individuals
must choose boire or know a previously unseen source.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from audit_i1_317_native_experiential_cohort import (
    ARMS, EXACT_RUN, EXACT_SHA, SEEDS, WORLDS, certify,
    number, require,
)

SCHEMA = "i1-318-alert-wake-new-sleep-native-original-wal/v1"


def read_one_original_wal(wal: Path):
    require(wal.is_file() and not wal.is_symlink(), "no original sealed WAL")
    wake = set()
    capture = {}
    pressure = {}
    admissions = {}
    motors = {}
    current_goal = None
    current_goal_kind = "none"
    with wal.open(encoding="utf-8") as stream:
        for raw in stream:
            ev = json.loads(raw)["causal_event"]
            kind = ev["kind"]
            step = ev.get("t_monde")
            data = ev.get("data") or {}
            if kind == "stage10_sleep_woke" and data.get("reason") == "alert":
                require(step not in wake and type(step) is int,
                        "duplicate reduced first-person alert wake")
                wake.add(step)
            elif kind == "perceptual_capture":
                body = data.get("dual_scope_visible_body", {})
                if type(body) is dict and set(body) >= {
                    "water", "energy", "food", "integrity"}:
                    require(step not in capture, "duplicate waking perception")
                    capture[step] = {
                        k: number(body[k]) for k in (
                            "water", "food", "energy", "integrity")
                    }
            elif kind == "stage10_sleep_pressure_frozen":
                if step not in pressure:
                    pressure[step] = {
                        k: number(data[k]) for k in (
                            "sleep_pressure", "fatigue", "consolidation_pressure")
                    }
            elif kind == "active_goal_changed":
                after = data.get("after")
                if after is None:
                    current_goal = None
                    current_goal_kind = "none"
                else:
                    require(type(after) is dict
                            and type(after.get("goal_type")) is str
                            and type(after.get("id")) is str,
                            "invalid logged goal transition")
                    current_goal = after["id"]
                    current_goal_kind = after["goal_type"]
            elif kind == "command_admitted":
                require(type(step) is int and step not in admissions,
                        "nonphysical multiple motor admissions")
                admissions[step] = (
                    data.get("primitive"), data.get("option_ref"),
                    current_goal, current_goal_kind,
                )
            elif kind == "command_experienced":
                require(type(step) is int and step not in motors,
                        "nonphysical multiple executed motors")
                motors[step] = ev.get("primitive")
    require(wake.issubset(admissions.keys() & motors.keys()),
            "wake alert without physically attested applied step")
    results = Counter()
    evidence = []
    for step in sorted(wake):
        primitive, option_ref, goal_id, goal_kind = admissions[step]
        require(primitive == motors[step],
                "admission not equal physically applied action")
        results["alert_wake_with_real_motor"] += 1
        if primitive != "dormir":
            results["alert_wake_accepted_other_action"] += 1
            continue
        require(type(option_ref) is str and
                option_ref.startswith("option:sleep-pressure:"),
                "alert wake sleep choice was not regular Competition sleep")
        require(step in capture and step in pressure,
                "no freshly re-perceived body or frozen sleep pressure")
        body = capture[step]
        p = pressure[step]
        results["alert_wake_chose_sleep_again"] += 1
        if body["energy"] >= 99:
            results["awake_sleep_again_energy_at_least_99"] += 1
        if body["water"] <= 15:
            results["awake_sleep_again_water_at_most_15"] += 1
        if body["water"] <= 10:
            results["awake_sleep_again_water_at_most_10"] += 1
        if body["water"] <= 0:
            results["awake_sleep_again_water_zero"] += 1
        if body["food"] <= 10:
            results["awake_sleep_again_food_at_most_10"] += 1
        if p["fatigue"] >= 0.99 and p["sleep_pressure"] >= 0.89:
            results["awake_sleep_again_high_fatigue_and_pressure"] += 1
        if goal_kind == "drink":
            results["awake_sleep_again_while_drink_goal_active"] += 1
        if goal_kind == "restore_integrity":
            results["awake_sleep_again_while_integrity_goal_active"] += 1
        # Only bounded representative evidence; original path and hashes are
        # authenticated by the independent cohort certificate above.
        if len(evidence) < 3:
            evidence.append({
                "step": step, "goal_type": goal_kind,
                "goal_ref": goal_id,
                "perceived_body": body,
                "frozen_pressure": p,
                "admitted_option_ref": option_ref,
                "physically_executed": primitive,
            })
    return {"counts": dict(results), "witnesses": evidence}


def audit(root: Path):
    certified = certify(root)
    require(
        certified["certified_original_mortal_WAL_paths"] == 16
        and certified["scientific_verdict"] == "NO-GO"
        and certified["exact_source_sha"] == EXACT_SHA
        and certified["source_run"] == EXACT_RUN,
        "cannot diagnose without fully authenticated original cohort",
    )
    rows = []
    aggregate = {arm: Counter() for arm in ARMS}
    for world in WORLDS:
        for seed in SEEDS:
            one = {}
            for arm in ARMS:
                wal = root/world/str(seed)/arm/"life-01.wal"
                result = read_one_original_wal(wal)
                one[arm] = result
                aggregate[arm].update(result["counts"])
            rows.append({"world": world, "seed": seed, "arms": one})
    return {
        "schema": SCHEMA,
        "source_run": EXACT_RUN,
        "exact_source_sha": EXACT_SHA,
        "original_WAL_paths_independently_authenticated": 16,
        "scope": "only lived own waking capture, owner goal, paid sleep option and actual motor",
        "no_motor_policy_changed": True,
        "no_rolled_back_individual": True,
        "scientific_verdict": "NO-GO",
        "by_arm": {a: dict(c) for a, c in aggregate.items()},
        "eight_matched_mortal_pairs": rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    options = p.parse_args()
    result = audit(options.root)
    options.output.parent.mkdir(parents=True, exist_ok=True)
    options.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "schema": result["schema"],
        "by_arm": result["by_arm"],
        "scientific_verdict": result["scientific_verdict"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
