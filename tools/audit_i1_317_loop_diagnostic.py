#!/usr/bin/env python3
"""Issue #317: read-only causal diagnosis of local memory oscillations.

Operates ONLY on sealed WALs and external, passive physical life reports.
Does not infer entity affordances, inject actions, or modify causal state.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from math import isfinite
import json
from pathlib import Path

from audit_i1_spatial_navigation_314 import _position, audit as verify_wal

SEEDS = (3011, 3023, 3041, 3067, 3083, 3109, 3121, 3137)


def motor_cycles(trajectory, spawn):
    """Physical A-B-A reversals; report speed separately from magnitude."""
    moves = []
    original = tuple(spawn)
    sites = {original}
    for row in trajectory:
        point = _position(row.get("position"))
        if point is None:
            raise ValueError("malformed passive physical position")
        sites.add(point)
        step = row["world_step"]
        if row.get("action_primitive") == "se_deplacer":
            moves.append((step, point))
    reentries = []
    max_streak = streak = 0
    for i in range(2, len(moves)):
        a, b, c = moves[i-2:i+1]
        if a[1] == c[1] and a[1] != b[1]:
            reentries.append((a[0],c[0]))
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return {
        "moves": len(moves),
        "physical_unique_sites": len(sites),
        "max_manhattan_distance_from_spawn": max(
            abs(x-original[0])+abs(y-original[1]) for x,y in sites
        ),
        "reversals_among_successive_movement_actions": len(reentries),
        "reversals_within_8_world_steps": sum(
            last-first <= 8 for first,last in reentries
        ),
        "max_consecutive_reversal_run": max_streak,
        "note": ("A reversal is defined on successive MOVEMENT actions; "
                 "sleep or eating between them does not erase prior displacement."),
    }


def remembered_options(events):
    """Count which formerly seen targets were even afforded a chance to compete."""
    captures = {}
    proposed = {}
    registrations = set()
    crosses = set()
    learned = set()
    for idx, event in enumerate(events):
        key = (event.get("t_monde"), event.get("attempt_ref"))
        t, attempt = key
        if type(t) is not int or not isinstance(attempt,str):
            continue
        data = event.get("data", {})
        if not isinstance(data,dict):
            continue
        kind = event.get("kind")
        if kind == "perceptual_capture":
            here = _position(data.get("position"))
            adjacent = data.get("agency_visible_adjacent")
            if (here is not None and isinstance(adjacent,list)
                and all(isinstance(x,dict) and
                        _position(x) is not None for x in adjacent)):
                captures[key] = (idx, frozenset(
                    [here] + [_position(x) for x in adjacent]
                ))
        elif kind == "i1_place_memory_option_proposed":
            opt = data.get("option_ref")
            if isinstance(opt,str) and opt.startswith("option:place-memory:"):
                proposed[(key,opt)] = (idx,data)
        elif kind == "i1_place_memory_option_registration" and data.get("registered") is True:
            registrations.add((key, data.get("option_ref")))
        elif kind == "competition_cycle":
            for trace in data.get("traces",()):
                if isinstance(trace,dict) and trace.get("crossed") is True:
                    crosses.add((key,trace.get("option_ref")))
        elif kind == "stage8_option_evaluation" and data.get("learned_value_status") == "learned":
            learned.add((key,data.get("option_ref")))
    tallies = Counter()
    locations = set()
    remote_examples = []
    for (key,ref),(idx,p) in proposed.items():
        cap = captures.get(key)
        target = _position(p.get("target"))
        next_hop = _position(p.get("next"))
        if cap is None or cap[0]>=idx or target is None or next_hop is None:
            tallies["unclassifiable_proposal"]+=1
            continue
        tallies["classifiable_proposals"]+=1
        if target in cap[1]:
            tallies["visible_target_proposals"]+=1
        else:
            tallies["outside_perception_proposals"]+=1
            if target!=next_hop:
                tallies["unseen_multihop_proposals"]+=1
                locations.add((key[0], target))
                if len(remote_examples)<4:
                    remote_examples.append({
                        "t_monde":key[0],"target":list(target),
                        "next_hop":list(next_hop),"entity_id":p.get("entity_id"),
                        "registered":(key,ref) in registrations,
                        "crossed":(key,ref) in crosses,
                        "learned_evaluated":(key,ref) in learned,
                    })
                if (key,ref) in registrations:
                    tallies["unseen_multihop_registered"]+=1
                if (key,ref) in crosses:
                    tallies["unseen_multihop_crossed"]+=1
                if (key,ref) in learned:
                    tallies["unseen_multihop_learned"]+=1
    return {
        **{name:tallies[name] for name in (
            "classifiable_proposals", "unclassifiable_proposal",
            "visible_target_proposals", "outside_perception_proposals",
            "unseen_multihop_proposals", "unseen_multihop_registered",
            "unseen_multihop_crossed", "unseen_multihop_learned",
        )},
        "distinct_unseen_target_world_steps":len(locations),
        "sample_unseen_offers":remote_examples,
    }



def _wal_numeric(value):
    """Decode one journal canonical numeric value without inventing zeros."""
    if type(value) in (float, int):
        result = float(value)
    elif (type(value) is dict and set(value) == {"$f64"}
          and type(value["$f64"]) is str):
        result = float.fromhex(value["$f64"])
    else:
        raise ValueError("unreadable WAL TD or body value")
    if not isfinite(result):
        raise ValueError("non-finite WAL TD or body value")
    return result


def audit_memory_td_credit(events, trajectory, initial_body):
    """Certify TD *action* credit, never infer entity affordances.

    The calling cohort reader authenticates the sealed WAL first. The
    additional checks here match a committed Action Control command, a
    World/Body transition, and scheduler closure to the passive physical
    trajectory. A TD update alone cannot certify an entity was useful.
    """
    seen_steps = {}
    for row in trajectory:
        step = row.get("world_step")
        if type(step) is not int or step < 1 or step in seen_steps:
            raise ValueError("invalid passive world-step sequence")
        seen_steps[step] = row
    if sorted(seen_steps) != list(range(1, len(seen_steps) + 1)):
        raise ValueError("incomplete passive world-step sequence")
    if (type(initial_body) is not dict
            or set(("energy", "food", "water", "integrity")) - set(initial_body)):
        raise ValueError("missing witnessed starting physiology")

    by_step_attempt = defaultdict(list)
    updates = []
    for index, event in enumerate(events):
        step, attempt = event.get("t_monde"), event.get("attempt_ref")
        if type(step) is not int or not isinstance(attempt, str):
            continue
        by_step_attempt[(step, attempt)].append((index, event))
        data = event.get("data")
        if (event.get("kind") == "td_update_published"
                and type(data) is dict
                and isinstance(data.get("previous_signature"), str)
                and data["previous_signature"].startswith("memory_place_return:")):
            updates.append((index, step, data))

    totals = Counter()
    examples = []
    for publication_index, published_step, data in updates:
        totals["memory_td_updates"] += 1
        length = data.get("segment_length")
        signature = data["previous_signature"]
        if type(length) is not int or length < 1:
            totals["unattributable_memory_td_updates"] += 1
            continue
        start = published_step - length
        positive = _wal_numeric(data.get("return_g")) > 0
        if positive:
            totals["positive_memory_td_updates"] += 1
        if length > 1:
            totals["multistep_td_segments"] += 1
        entity = signature[len("memory_place_return:"):]
        matches = []
        for (step, attempt), rows in by_step_attempt.items():
            if step != start:
                continue
            admissions = [(i, e) for i, e in rows
                          if e.get("kind") == "command_admitted"
                          and type(e.get("data")) is dict
                          and e["data"].get("primitive") == "se_deplacer"
                          and isinstance(e["data"].get("option_ref"), str)
                          and e["data"]["option_ref"].startswith(
                              "option:place-memory:place:" + entity + ":at:")]
            if len(admissions) != 1:
                continue
            admitted_index, admitted = admissions[0]
            command_hash = admitted["data"].get("command_hash")
            commands = [(i, e) for i, e in rows
                        if e.get("kind") == "command_experienced"
                        and e.get("primitive") == "se_deplacer"
                        and e.get("command_hash") == command_hash]
            transitions = [(i, e) for i, e in rows
                           if e.get("kind") == "world_transition_experienced"]
            closures = [(i, e) for i, e in rows
                        if e.get("kind") == "step_closed"
                        and type(e.get("data")) is dict
                        and e["data"].get("outcome") == "normal"
                        and e["data"].get("applied_command_count") == 1
                        and e["data"].get("world_advance_count") == 1]
            if (len(commands) == len(transitions) == len(closures) == 1
                    and admitted_index < commands[0][0] < transitions[0][0]
                    < closures[0][0] < publication_index):
                matches.append(transitions[0][1])

        row = seen_steps.get(start)
        before = initial_body if start == 1 else seen_steps.get(start-1, {}).get("body")
        if len(matches) != 1 or row is None or before is None:
            totals["unattributable_memory_td_updates"] += 1
            continue
        transition = matches[0]
        after = row.get("body")
        position = row.get("position")
        physical_position = transition.get("position_after")
        physical_body = transition.get("body_after")
        if (row.get("execution") != "applied"
                or row.get("action_primitive") != "se_deplacer"
                or type(after) is not dict or type(before) is not dict
                or type(physical_body) is not dict
                or type(position) is not dict or type(physical_position) is not dict
                or any(position.get(k) != physical_position.get(k) for k in ("x", "y"))
                or any(k not in after or k not in before or k not in physical_body
                       or abs(_wal_numeric(after[k]) - _wal_numeric(physical_body[k])) > 1e-8
                       for k in ("energy", "food", "water", "integrity"))):
            totals["unattributable_memory_td_updates"] += 1
            continue

        totals["physically_attributed_memory_td_updates"] += 1
        effects = transition.get("effects")
        movement_only = (length == 1 and effects == {"movement": "moved"})
        if positive and movement_only:
            totals["positive_one_step_movement_only_td"] += 1
            if all(_wal_numeric(after[k]) <= _wal_numeric(before[k])
                   for k in ("energy", "food", "water", "integrity")):
                totals["positive_without_increased_body_variable"] += 1
        updated = data.get("updated_signatures")
        if isinstance(updated, list):
            totals["non_memory_trace_updates"] += sum(
                isinstance(s, str) and not s.startswith("memory_place_return:")
                for s in updated)
        if len(examples) < 12:
            examples.append({
                "executed_step": start, "published_step": published_step,
                "signature": signature, "segment_length": length,
                "return_g": _wal_numeric(data["return_g"]),
                "physical_effects": effects,
                "body_delta": {
                    k: round(_wal_numeric(after[k]) - _wal_numeric(before[k]), 8)
                    for k in ("energy", "food", "water", "integrity")
                },
                "entity_causality": "not_established_from_td_action_credit",
            })
    return {
        **{key: totals[key] for key in (
            "memory_td_updates", "physically_attributed_memory_td_updates",
            "unattributable_memory_td_updates", "positive_memory_td_updates",
            "positive_one_step_movement_only_td",
            "positive_without_increased_body_variable",
            "multistep_td_segments", "non_memory_trace_updates")},
        "certification": "physical_action_credit_only_not_entity_causality",
        "examples": examples,
    }

def read_cohort(root, exact_sha):
    results={}
    for path in sorted(Path(root).rglob("report.json")):
        report=json.loads(path.read_text())
        if (report.get("engine")!="I1"
            or report["run"]["git_head"]!=exact_sha
            or report["source"]["preset"]!="memory-corridor"
            or report["run"]["custody"]!="wal"
            or report["run"]["requested_steps"]!=300
            or report["run"]["requested_lives"]!=1
            or report["old_cohorts_used_as_oracles"] is not False):
            raise ValueError("untrusted cohort provenance")
        seed=report["run"]["seed"]
        if type(seed) is not int or seed not in SEEDS or seed in results:
            raise ValueError("unregistered, duplicate or missing seed")
        life=report["lives"]
        if len(life)!=1 or life[0]["custody_file"]!="life-01.wal":
            raise ValueError("one immutable WAL required for each individual")
        life=life[0]
        wal=path.parent/"life-01.wal"
        proof=verify_wal(wal)
        if (proof["independent_hash_chain_verified"] is not True
            or proof["journal_head"]!=life["journal_head"]
            or proof["journal_entries"]!=life["durable_entries"]):
            raise ValueError("WAL authentication failed")
        events=[]
        with wal.open(encoding="utf-8") as stream:
            for line in stream:
                events.append(json.loads(line)["causal_event"])
        steps=life["steps"]
        if (not steps or steps[-1]["journal_head"]!=life["journal_head"]
            or not 1<=len(steps)<=300
            or (life["lifecycle"]=="active" and len(steps)!=300)):
            raise ValueError("invalid simulated physical life")
        result={
            "seed":seed,
            "code_sha":exact_sha,
            "preset_digest":report["source"]["sha256"],
            "physics_digest":report["environment"]["world_physics_digest"],
            "initial_body":report["environment"]["initial_body"],
            "life_id":life["individual_id"],
            "status":life["lifecycle"],
            "world_steps":len(steps),
            "physical":motor_cycles(steps,report["environment"]["spawn"]),
            "memory":remembered_options(events),
            "td_credit":audit_memory_td_credit(events,steps,report["environment"]["initial_body"]),
            "certified_memory_steps":proof["stages"]["physically_applied"],
            "certified_unseen_multihop_first_hops":proof[
                "memory_causality_317"]["physically_applied_unseen_multihop_first_hops"],
            "certified_completed_remote_returns":proof[
                "memory_causality_317"]["completed_remote_multihop_returns"],
        }
        results[seed]=result
    if set(results)!=set(SEEDS):
        raise ValueError(f"incomplete cohort: {sorted(results)}")
    return results


def compare(a,b):
    if set(a)!=set(b):
        raise ValueError("cohorts do not have identical registered seeds")
    for seed in SEEDS:
        for k in ("preset_digest","physics_digest","initial_body","life_id"):
            if a[seed][k]!=b[seed][k]:
                raise ValueError(f"unmatched actual birth {seed} {k}")
    def summary(c):
        rows=list(c.values())
        def total(path,key):
            return sum(x[path][key] for x in rows)
        return {
            "deaths":sum(x["status"]=="dead" for x in rows),
            "mean_world_steps":sum(x["world_steps"] for x in rows)/len(rows),
            "moves":total("physical","moves"),
            "reversals_among_moves":total("physical","reversals_among_successive_movement_actions"),
            "reversals_within_8_steps":total("physical","reversals_within_8_world_steps"),
            "unique_sites_per_life":[x["physical"]["physical_unique_sites"] for x in rows],
            "unseen_multihop_proposals":total("memory","unseen_multihop_proposals"),
            "unseen_multihop_registered":total("memory","unseen_multihop_registered"),
            "unseen_multihop_crossed":total("memory","unseen_multihop_crossed"),
            "unseen_multihop_learned":total("memory","unseen_multihop_learned"),
            "physical_memory_actions":sum(x["certified_memory_steps"] for x in rows),
            "memory_td_updates":total("td_credit","memory_td_updates"),
            "memory_td_physically_attributed":total("td_credit","physically_attributed_memory_td_updates"),
            "memory_td_unattributable":total("td_credit","unattributable_memory_td_updates"),
            "memory_td_positive_movement_only":total("td_credit","positive_one_step_movement_only_td"),
            "memory_td_positive_without_increased_body_variable":total("td_credit","positive_without_increased_body_variable"),
            "remote_first_hops":sum(x["certified_unseen_multihop_first_hops"] for x in rows),
            "completed_remote_returns":sum(x["certified_completed_remote_returns"] for x in rows),
        }
    return {
        "schema":"i1-issue317-independent-oscillation-recall-diagnostic-v1",
        "authority":"immutable_WAL_plus_external_physical_observer",
        "status":"VERIFIED_CAUSAL_DIAGNOSTIC_NOT_LEARNED_AFFORDANCE",
        "summary":{"baseline":summary(a),"interruption_aware":summary(b)},
        "pairs":[{"seed":s,"baseline":a[s],"interruption_aware":b[s]}
                 for s in SEEDS],
        "scientific_verdict":"NO-GO",
        "limitations":[
            "Physical A-B-A reversal is not by itself evidence of pathology or a cause of death.",
            "A remembered entity is not known to satisfy any need merely because it was revisited.",
            "No change to thresholds, TD, physics or option competition was applied.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",type=Path,required=True)
    p.add_argument("--interrupted",type=Path,required=True)
    p.add_argument("--baseline-sha",required=True)
    p.add_argument("--interrupted-sha",required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    results=compare(read_cohort(a.baseline,a.baseline_sha),
                    read_cohort(a.interrupted,a.interrupted_sha))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.output.exists():
        raise FileExistsError("refusing to overwrite scientific result")
    a.output.write_text(json.dumps(results,sort_keys=True,indent=2)+"\n")
    print("ISSUE317_AUTHENTICATED_LOOP_DIAGNOSTIC")
    print(json.dumps(results["summary"],sort_keys=True,indent=2))


if __name__=="__main__":
    main()
