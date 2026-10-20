#!/usr/bin/env python3
"""#317 independent vital decision-chain audit over eight original canonical I1 WAL.

No living actor is loaded. The source SHA, mortality, physical commands,
hash chain and atomic consolidation are independently certified *before*
interpreting first-person sightings, current needs, options and Competition.

A location observed in Perception is NOT evidence that the individual
knows it is nutritious or drinkable. An experience of boire at a location
is still an association, not a universal resource oracle or safety claim.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path

from audit_i1_317_wake_recovery_cohort import (
    ARMS, BIRTH_SCHEMA, EXACT_ENGINE_SHA, PRESETS, SEEDS,
    check_birth, check_arm,
)
from audit_i1_spatial_navigation_314 import audit as audit_wal

SCHEMA = "i1-317-water-memory-decision-chain-sealed/v1"
RUN_ID = 39302574668
WATER_ALERT = 15.0
KEY_KINDS = {
    "perceptual_capture", "active_goal_changed",
    "i1_entity_place_observed", "i1_water_lived_outcome_admitted",
    "i1_water_option_proposed", "i1_place_memory_option_proposed",
    "i1_place_memory_option_registration", "competition_cycle",
    "command_admitted", "command_experienced",
    "world_transition_experienced", "stage10_sleep_woke",
    "step_closed",
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def measured(value):
    if type(value) in (float, int):
        numeric = float(value)
    elif (type(value) is dict and set(value) == {"$f64"}
          and type(value["$f64"]) is str):
        numeric = float.fromhex(value["$f64"])
    else:
        raise ValueError("invalid bodily/Competition WAL scalar")
    require(isfinite(numeric), "nonfinite WAL scalar")
    return numeric


def classify_life(events, *, physical_steps):
    """Pure first-person chronology from independently validated WAL events.

    Synthetic unit tests can call this directly; their outputs are NOT
    scientific evidence. Caller must attest every physical step separately.
    """
    require(type(physical_steps) is int and 1 <= physical_steps <= 300,
            "invalid physical life length")
    rows = defaultdict(list)
    seen_events = 0
    for event in events:
        require(type(event) is dict, "malformed event")
        kind = event.get("kind")
        if kind not in KEY_KINDS:
            continue
        step = event.get("t_monde")
        require(type(step) is int and 1 <= step <= physical_steps,
                "relevant evidence outside physically lived world steps")
        rows[step].append(event)
        seen_events += 1
    require(seen_events and len(rows) == physical_steps,
            "missing essential original physical life events")
    totals = Counter()
    examples = []
    witnessed_sources = set()
    positive_lived_sites = set()
    active_goal = None
    seen_physical_commands = {}
    for t in range(1, physical_steps + 1):
        events_this_step = rows[t]
        evidence = defaultdict(list)
        for event in events_this_step:
            evidence[event["kind"]].append(event)
        captures = evidence["perceptual_capture"]
        commands = evidence["command_experienced"]
        transitions = evidence["world_transition_experienced"]
        closures = evidence["step_closed"]
        require(len(commands) == len(transitions) == len(closures) == 1,
                "no unique physically applied command/transition/closure")
        cmd, transition, closed = commands[0], transitions[0], closures[0]
        outcome = closed["data"]
        require(outcome.get("applied_command_count") == 1
                and outcome.get("world_advance_count") == 1
                and outcome.get("outcome") in ("normal", "dead"),
                "not an independently applied world transition")
        require(t == physical_steps or outcome["outcome"] != "dead",
                "post-mortem physical continuation")
        require(cmd.get("emitter") == "action_control"
                and cmd.get("primitive") in {
                    "attendre", "dormir", "boire", "manger", "collecter",
                    "se_deplacer", "poser_une_pierre", "fabriquer_outil"},
                "unexpected command authority/primitive")
        admissions = [event for event in evidence["command_admitted"]
                      if event.get("data", {}).get("command_hash") ==
                      cmd.get("command_hash")]
        require(admissions, "physically applied command has no matched admission")
        applied = admissions[-1]["data"]
        require(applied.get("primitive") == cmd["primitive"],
                "admission primitive diverged from physical action")
        seen_physical_commands[t] = (cmd["primitive"], transition.get("effects", {}))
        # The previous current-world-step witness is not a future-world oracle.
        previously_seen_sources = set(witnessed_sources)
        previously_supported_sites = set(positive_lived_sites)
        for change in evidence["active_goal_changed"]:
            after = change["data"].get("after")
            require(after is None or type(after) is dict,
                    "invalid goal change provenance")
            active_goal = None if after is None else after.get("goal_type")
        for lived in evidence["i1_water_lived_outcome_admitted"]:
            d = lived.get("data", {})
            source = d.get("source_position")
            sent = d.get("sent_world_step")
            require(d.get("admitted") is True
                    and isinstance(source, list) and len(source) == 2
                    and all(type(n) is int for n in source)
                    and type(sent) is int and 1 <= sent < t
                    and measured(d.get("delta_water")) > 0
                    and tuple(source) in witnessed_sources
                    and seen_physical_commands.get(sent, ("",))[0] == "boire",
                    "unwitnessed or nonpositive lived water association")
            positive_lived_sites.add(tuple(source))
        for sighting in evidence["i1_entity_place_observed"]:
            d = sighting.get("data", {})
            if d.get("entity_type") != "water_source":
                continue
            position = d.get("position")
            require(d.get("source") == "perceptual_capture"
                    and isinstance(position, list) and len(position) == 2
                    and all(type(k) is int for k in position),
                    "unowned first-person water sighting")
            witnessed_sources.add(tuple(position))

        require(len(captures) <= 1, "duplicate full first-person capture")
        if not captures:
            continue
        capture = captures[0].get("data", {})
        body = capture.get("dual_scope_visible_body", {})
        require(type(body) is dict and "water" in body,
                "missing first-person water telemetry")
        water = measured(body["water"])
        require(0 <= water <= 100, "invalid seen water level")
        critical = water <= WATER_ALERT
        totals["waking_perceptual_steps"] += 1
        if not critical:
            continue
        totals["water_critical_waking_steps"] += 1
        if active_goal == "drink":
            totals["water_critical_drink_goal_active"] += 1
        if applied.get("primitive") == "dormir":
            totals["water_critical_chose_dormir"] += 1
        if applied.get("primitive") == "se_deplacer":
            totals["water_critical_chose_movement"] += 1
        if any(v.get("data", {}).get("reason") == "alert"
               for v in evidence["stage10_sleep_woke"]):
            totals["water_critical_alert_wakes"] += 1
        if previously_seen_sources:
            totals["water_critical_prior_water_place_witness"] += 1
        if previously_supported_sites:
            totals["water_critical_prior_positive_boire_association"] += 1
        if evidence["i1_water_option_proposed"]:
            totals["water_critical_proximal_water_option_proposed"] += 1

        # An ordinary local sighting of a water source is not a "benefit".
        # An ordinary memory proposal is not a motor action. Track each
        # independently all the way to an actual Competition threshold.
        memory_options = {}
        for proposed in evidence["i1_place_memory_option_proposed"]:
            d = proposed.get("data", {})
            if d.get("entity_type") != "water_source":
                continue
            ref = d.get("option_ref")
            target = d.get("target")
            nxt = d.get("next")
            require(type(ref) is str and ref.startswith("option:place-memory:")
                    and isinstance(target, list) and len(target) == 2
                    and isinstance(nxt, list) and len(nxt) == 2
                    and all(type(n) is int for n in target + nxt)
                    and tuple(target) in witnessed_sources,
                    "spatial water option has no personal-place provenance")
            # The same candidate may appear during multiple priced cycles
            # of one world step. Its identity/route must not silently change.
            if ref in memory_options:
                require(memory_options[ref] == tuple(nxt),
                        "same memory option changed motor step mid-deliberation")
            memory_options[ref] = tuple(nxt)
        if not memory_options:
            if previously_seen_sources:
                totals["water_critical_prior_seen_but_no_water_route_offered"] += 1
            continue
        totals["water_critical_water_memory_proposed_steps"] += 1
        registrations = {
            event["data"].get("option_ref") for event in
            evidence["i1_place_memory_option_registration"]
            if event.get("data", {}).get("registered") is True
        }
        registered = memory_options.keys() & registrations
        if registered:
            totals["water_critical_water_memory_registered_steps"] += 1
        crosses = set()
        best_ratio = 0.0
        for cycle in evidence["competition_cycle"]:
            for trace in cycle.get("data", {}).get("traces", ()):
                ref = trace.get("option_ref")
                if ref not in memory_options:
                    continue
                threshold = measured(trace.get("threshold"))
                acc = measured(trace.get("accumulator_after"))
                require(threshold > 0 and acc >= 0, "invalid Competition evidence")
                best_ratio = max(best_ratio, acc / threshold)
                if trace.get("crossed") is True:
                    crosses.add(ref)
        if crosses:
            require(crosses.issubset(registrations),
                    "crossed water memory option was never registered")
            totals["water_critical_water_memory_crossed_steps"] += 1
        if applied.get("option_ref") in memory_options:
            require(applied["option_ref"] in crosses,
                    "water memory option applied without Competition crossing")
            require(cmd["primitive"] == "se_deplacer"
                    and tuple(transition.get("position_after", {}).get(n, None)
                              for n in ("x", "y")) == memory_options[applied["option_ref"]],
                    "water memory motor candidate not physically realized")
            totals["water_critical_water_memory_physically_applied_steps"] += 1
        if len(examples) < 8:
            examples.append({
                "world_step": t,
                "first_person_water": round(water, 6),
                "active_goal": active_goal,
                "source_seen_before": bool(previously_seen_sources),
                "beneficial_boire_personally_experienced":
                    bool(previously_supported_sites),
                "source_return_option_count": len(memory_options),
                "maximum_accumulator_over_threshold": round(best_ratio, 6),
                "crossed": bool(crosses),
                "executed_primitive": cmd["primitive"],
            })
    return {"counters": dict(totals),
            "diagnostic_examples_only_not_evidence_of_causality": examples}


def certify(root: Path):
    require(root.is_dir() and not root.is_symlink(), "missing sealed cohort")
    reports = {root/w/str(s)/"report.json" for w in PRESETS for s in SEEDS}
    require(set(root.rglob("report.json")) == reports,
            "missing/extra physical birth groups")
    summaries = []
    world_births = {}
    hashes = set()
    for world in PRESETS:
        for seed in SEEDS:
            report = json.loads((root/world/str(seed)/"report.json").read_text())
            check_birth(report, world, seed, EXACT_ENGINE_SHA)
            physics = (report["preset_sha256"], report["physics_digest"])
            if world in world_births:
                require(world_births[world] == physics,
                        "world physics changed between locked seeds")
            world_births[world] = physics
            arm = report["arms"]["canonical"]
            wal = root/world/str(seed)/"canonical"/"life-01.wal"
            physical = check_arm(wal, arm, "canonical", audit_wal)
            require(arm["wal_sha256"] not in hashes,
                    "replayed or duplicated original canonical WAL")
            hashes.add(arm["wal_sha256"])
            with wal.open(encoding="utf-8") as stream:
                detail = classify_life(
                    (json.loads(line)["causal_event"] for line in stream),
                    physical_steps=physical["world_step_count"],
                )
            require(detail["counters"]["waking_perceptual_steps"] <=
                    physical["world_step_count"],
                    "nonphysical first-person cognitive world steps")
            summaries.append({
                "world": world, "seed": seed,
                "life_id": f"i1:preset:{world}:{seed}:0",
                "exact_source_wal_sha256": arm["wal_sha256"],
                "verified_journal_head": arm["journal_head"],
                "lifecycle": physical["lifecycle"],
                "physically_lived_steps": physical["world_step_count"],
                **detail,
            })
    require(len(summaries) == 8 and len(hashes) == 8,
            "all eight canonical lives must be unique")
    counts = sum((Counter(row["counters"]) for row in summaries), Counter())
    require(counts["water_critical_water_memory_physically_applied_steps"]
            <= counts["water_critical_water_memory_crossed_steps"]
            <= counts["water_critical_water_memory_registered_steps"]
            <= counts["water_critical_water_memory_proposed_steps"]
            <= counts["water_critical_waking_steps"],
            "option funnel is not physically and temporally ordered")
    return {
        "schema": SCHEMA,
        "status": "EIGHT_SEALED_CANONICAL_LIVES_DIAGNOSTIC_ONLY",
        "source_run": RUN_ID,
        "exact_canonical_source_sha": EXACT_ENGINE_SHA,
        "certified_unique_original_wal_lives": 8,
        "water_critical_body_threshold_from_real_perception": WATER_ALERT,
        "no_oracle_resource_knowledge": True,
        "personally_seen_does_not_prove_water_usefulness": True,
        "no_forced_action_or_new_born_life": True,
        "motor_route_utility_automatically_inferred": False,
        "scientific_verdict": "NO-GO",
        "aggregate": dict(counts),
        "individuals": summaries,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    d = certify(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": d["status"], "aggregate": d["aggregate"],
        "scientific_verdict": d["scientific_verdict"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
