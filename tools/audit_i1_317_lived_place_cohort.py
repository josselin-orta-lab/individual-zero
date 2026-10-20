#!/usr/bin/env python3
"""#317: fail-closed, read-only certification of 24 born I1 lived-place lives.

Certify actual WAL and world steps independently of the laboratory's
nonjournaled ranking/advisory counters. Preserve identical WAL hashes:
deterministic separate births can lawfully produce byte-identical journals,
so SHA inequality must NEVER be fabricated as evidence of independence.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from math import isclose, isfinite
from pathlib import Path

from audit_i1_317_two_process_cohort import _verify_arm
from audit_i1_spatial_navigation_314 import audit as authenticate_wal

EXACT_SOURCE_SHA = "5ce9604893a83615d3b84e8506709732286939c7"
EXACT_RUN_ID = 39308197811
SCHEMA = "i1-317-lived-place-24-original-wal-independent/v1"
BIRTH_SCHEMA = "i1-317-experienced-place-factorial-mortal/v1"
PRESETS = ("oasis", "foraging", "memory-corridor")
SEEDS = (13127, 13219)
ARMS = ("canonical", "recall_only", "value_only", "recall_and_value")
NATIVE_WAKE = {"energy": 10.0, "water": 15.0, "food": 10.0, "integrity": 25.0}
NATIVE_SLEEP = {
    "fatigue_gain": 0.7, "sleep_fatigue_recovery": 0.3,
    "fatigue_weight": 0.65, "consolidation_weight": 0.25,
    "night_weight": 0.2, "intrinsic_weight": 0.9,
}


def must(test, label):
    if not test:
        raise ValueError(label)


def measured(value):
    if type(value) in (int, float):
        number = float(value)
    elif isinstance(value, dict) and set(value) == {"$f64"}:
        number = float.fromhex(value["$f64"])
    else:
        raise ValueError("invalid canonical WAL floating point value")
    must(isfinite(number), "nonfinite physical/Competition value")
    return number


def _point(value):
    return ((type(value) is list or type(value) is tuple)
            and len(value) == 2 and all(type(p) is int for p in value))


def _body_water(capture):
    body = capture.get("data", {}).get("dual_scope_visible_body", {})
    must("water" in body, "first-person water was not perceived")
    water = measured(body["water"])
    must(0 <= water <= 100, "nonphysical water telemetry")
    return water


def classify_original(wal: Path, physical_steps: int):
    """Interpret first-person records only AFTER external physical verifier."""
    events_by_step = defaultdict(list)
    with wal.open(encoding="utf-8") as f:
        for line in f:
            event = json.loads(line)["causal_event"]
            t = event.get("t_monde")
            if (type(t) is int and 1 <= t <= physical_steps):
                events_by_step[t].append(event)
            elif event.get("kind") in {
                "perceptual_capture", "i1_water_lived_outcome_admitted",
                "i1_place_memory_option_proposed", "competition_cycle",
                "command_experienced", "step_closed"}:
                raise ValueError("meaningful cognition outside lived physical steps")
    must(set(events_by_step) == set(range(1,physical_steps + 1)),
         "non-contiguous original mortal events")
    details = {}
    for t in range(1,physical_steps + 1):
        seen = defaultdict(list)
        for event in events_by_step[t]:
            seen[event["kind"]].append(event)
        for kind in ("command_experienced", "world_transition_experienced",
                     "step_closed"):
            must(len(seen[kind]) == 1, "ambiguous world-step physical event")
        must(len(seen["perceptual_capture"]) <= 1,
             "multiple full first-person perception captures")
        details[t] = seen

    association_sites = set()
    totals = Counter()
    examples = []
    for t in range(1,physical_steps + 1):
        events = details[t]
        captures = events["perceptual_capture"]
        if captures:
            totals["ordinary_waking_capture_steps"] += 1
        for event in events["i1_water_lived_outcome_admitted"]:
            d = event.get("data", {})
            sent, observed = d.get("sent_world_step"), d.get("observed_world_step")
            place = d.get("source_position")
            must(d.get("admitted") is True
                 and type(sent) is int and observed == t == sent + 1
                 and sent in details and _point(place),
                 "invalid timeline for admitted personal water experiment")
            origin_capture = details[sent]["perceptual_capture"]
            followup_capture = details[t]["perceptual_capture"]
            must(len(origin_capture) == len(followup_capture) == 1,
                 "water experience requires a before and after perception")
            phys_command = details[sent]["command_experienced"][0]
            phys_transition = details[sent]["world_transition_experienced"][0]
            must(phys_command.get("primitive") == "boire"
                 and phys_transition.get("effects", {}).get("drank") is True,
                 "water learning without a physically effective boire")
            from_pos = origin_capture[0]["data"].get("position", {})
            to_pos = followup_capture[0]["data"].get("position", {})
            body_pos = phys_transition.get("position_after", {})
            must(all(isinstance(p,dict) and p.get("x")==place[0]
                     and p.get("y")==place[1]
                     for p in (from_pos,to_pos,body_pos)),
                 "learned water benefit was not seen at the same place")
            before, after = (_body_water(origin_capture[0]),
                             _body_water(followup_capture[0]))
            must(isclose(measured(d["before_water"]), before, abs_tol=1e-8)
                 and isclose(measured(d["observed_water"]), after, abs_tol=1e-8)
                 and isclose(measured(d["delta_water"]), round(after-before,8),
                             abs_tol=1e-7) and after > before,
                 "unsupported bodily improvement from an experimental water action")
            association_sites.add(tuple(place))
            totals["positive_experience_admissions"] += 1
        if not captures:
            continue
        if not association_sites:
            continue
        totals["waking_steps_after_personal_positive_water"] += 1
        memory_options = {}
        for proposed in events["i1_place_memory_option_proposed"]:
            d = proposed.get("data", {})
            target = d.get("target")
            if (d.get("entity_type") != "water_source"
                or not _point(target)
                or tuple(target) not in association_sites):
                continue
            option = d.get("option_ref")
            nxt = d.get("next")
            must(type(option) is str and option.startswith("option:place-memory:")
                 and _point(nxt),
                 "unverified memory option for lived-beneficial source")
            if option in memory_options:
                must(memory_options[option] == tuple(nxt),
                     "same memory option has inconsistent motor destination")
            memory_options[option] = tuple(nxt)
        if not memory_options:
            continue
        totals["steps_with_positively_experienced_water_route_offered"] += 1
        registered = {
            event.get("data", {}).get("option_ref")
            for event in events["i1_place_memory_option_registration"]
            if event.get("data", {}).get("registered") is True
        } & memory_options.keys()
        if registered:
            totals["steps_with_positively_experienced_water_route_registered"] += 1
        saw_score = set()
        crossed = set()
        max_accumulator_fraction = 0.0
        for cycle in events["competition_cycle"]:
            for trace in cycle.get("data", {}).get("traces", ()):
                option_ref = trace.get("option_ref")
                if option_ref not in memory_options:
                    continue
                saw_score.add(option_ref)
                if trace.get("evidence") is not None:
                    limit = measured(trace["threshold"])
                    value = measured(trace["accumulator_after"])
                    must(limit > 0 and value >= 0,
                         "invalid scored place memory accumulator")
                    max_accumulator_fraction = max(max_accumulator_fraction,
                                                   value / limit)
                if trace.get("crossed") is True:
                    crossed.add(option_ref)
        must(crossed.issubset(registered),
             "unregistered place-option threshold crossing")
        if saw_score:
            totals["steps_with_positively_experienced_water_route_scored"] += 1
        if crossed:
            totals["steps_with_positively_experienced_water_route_crossed"] += 1
        applied_ref = None
        actual_command = events["command_experienced"][0]
        for admit in events["command_admitted"]:
            d = admit.get("data", {})
            if (d.get("command_hash") == actual_command.get("command_hash")
                and d.get("option_ref") in memory_options):
                applied_ref = d["option_ref"]
        if applied_ref:
            must(applied_ref in crossed and actual_command["primitive"]=="se_deplacer",
                 "impossible physically applied memory return")
            arrived = events["world_transition_experienced"][0]["position_after"]
            must((arrived["x"],arrived["y"])==memory_options[applied_ref],
                 "memory option motor step not physically realized")
            totals["steps_with_positively_experienced_water_route_applied"] += 1
        if len(examples)<5:
            examples.append({
                "step":t, "eligible_memory_options":len(memory_options),
                "registered":bool(registered),"crossed":bool(crossed),
                "max_accumulator_fraction":round(max_accumulator_fraction,5),
                "physical_primitive":actual_command["primitive"],
            })
    return {"counters":dict(totals),
            "positive_sites_physically_supported":len(association_sites),
            "diagnostic_examples":examples}


def certify(root: Path):
    must(root.is_dir() and not root.is_symlink(),
         "missing original cohort directory")
    pairs={(w,s) for w in PRESETS for s in SEEDS}
    reports={root/w/str(s)/"report.json" for w,s in pairs}
    must(set(root.rglob("report.json"))==reports
         and not any(x.is_symlink() for x in reports),
         "incomplete/alien cohort report")
    physics={}
    lives={}
    for world,seed in sorted(pairs):
        row=json.loads((root/world/str(seed)/"report.json").read_text())
        must(row.get("schema")==BIRTH_SCHEMA
             and row.get("status")=="COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
             and row.get("source_sha")==EXACT_SOURCE_SHA
             and row.get("preset")==world and row.get("seed")==seed
             and row.get("horizon")==300
             and row.get("preregistered_arms")==list(ARMS)
             and set(row.get("arms",{}))==set(ARMS)
             and row.get("factorial_recall_and_value_independent") is True
             and row.get("learned_site_requires_personally_applied_boire_and_followup") is True
             and row.get("same_world_physics_needs_td_competition_action_control") is True
             and row.get("no_type_based_resource_utility") is True
             and row.get("no_motor_forcing_or_new_vital_reflex") is True
             and row.get("no_cold_recovery_claim") is True
             and row.get("no_coma_implemented") is True
             and row.get("scientific_verdict")=="NO-GO",
             "forged, off-design or incomplete mortal birth report")
        digest=(row.get("physics_digest"),row.get("preset_sha256"))
        must(all(type(x) is str and len(x)==64 for x in digest),
             "missing original frozen world provenance")
        if world in physics:
            must(physics[world]==digest, "world physics changed across matched seeds")
        physics[world]=digest
        for arm in ARMS:
            r=row["arms"][arm]
            do_recall=arm in ("recall_only","recall_and_value")
            do_value=arm in ("value_only","recall_and_value")
            must(r.get("option_ranking_adjusted") is do_recall
                 and r.get("option_value_advisory_adjusted") is do_value
                 and r.get("Stage10_sleep_pressure")==NATIVE_SLEEP
                 and r.get("physical_wake_thresholds")==NATIVE_WAKE
                 and r.get("wal_relative_path")==f"{arm}/life-01.wal",
                 "unregistered intervention or altered physiology")
            unproven=r.get("research_counters_UNATTESTED",{})
            must(type(unproven) is dict
                 and set(unproven).issubset({
                     "rank_changes","rank_budget_denied","value_advisories"})
                 and all(type(v) is int and v >= 0 for v in unproven.values()),
                 "untrusted experiment-only counter")
            wal=root/world/str(seed)/arm/"life-01.wal"
            physical=_verify_arm(wal,r,authenticate_wal)
            diagnostic=classify_original(wal,physical["lived_steps"])
            must(diagnostic["positive_sites_physically_supported"]==
                 r["positive_lived_source_sites"],
                 "report invents or omits personally supported water locations")
            lives[(world,seed,arm)]={
                "wal_sha256":r["wal_sha256"],"lifecycle":physical["lifecycle"],
                "steps":physical["lived_steps"],
                "actions":physical["actions"],
                "consolidated":physical["objects_consolidated"],
                "accepted_uc":physical["accepted_cognitive_uc"],
                "first_person_wal_diagnostic":diagnostic,
                "research_counter_reported_UNATTESTED":unproven,
            }
    must(len(lives)==24, "not all 24 original born lives are present")
    by_arm={}
    for arm in ARMS:
        rows=[lives[(w,s,arm)] for w,s in sorted(pairs)]
        actions=sum((Counter(x["actions"]) for x in rows),Counter())
        counts=sum((Counter(x["first_person_wal_diagnostic"]["counters"])
                    for x in rows),Counter())
        by_arm[arm]={
            "certified_existing_wal_files":6,
            "deaths":sum(x["lifecycle"]=="dead" for x in rows),
            "alive_at_horizon":sum(x["lifecycle"]=="active" for x in rows),
            "physical_world_steps":sum(x["steps"] for x in rows),
            "applied_actions":dict(actions),
            "actual_consolidated_objects":sum(x["consolidated"] for x in rows),
            "accepted_logical_uc":sum(x["accepted_uc"] for x in rows),
            "physically_supported_positive_water_sites":sum(
                x["first_person_wal_diagnostic"]["positive_sites_physically_supported"]
                for x in rows),
            "decision_chain":dict(counts),
            "unproven_research_counters_NOT_used_in_verdict":dict(sum((
                Counter(x["research_counter_reported_UNATTESTED"])
                for x in rows),Counter())),
        }
    paired=[]
    for w,s in sorted(pairs):
        base=lives[(w,s,"canonical")]
        arm_effects={}
        for a in ARMS:
            life=lives[(w,s,a)]
            arm_effects[a]={
                "same_bytes_as_canonical":life["wal_sha256"]==base["wal_sha256"],
                "lived_step_delta":life["steps"]-base["steps"],
                "consolidated_object_delta":life["consolidated"]-base["consolidated"],
                "uc_delta":life["accepted_uc"]-base["accepted_uc"],
            }
        paired.append({"world":w,"seed":s,"arms":arm_effects})
    return {
        "schema":SCHEMA,"status":"SEALED_WAL_VERIFIED_NO_INTERVENTIONAL_GO",
        "source_run":EXACT_RUN_ID,"exact_birth_source_sha":EXACT_SOURCE_SHA,
        "certified_original_wal_paths":24,
        "distinct_wal_content_sha256_count":len({x["wal_sha256"] for x in lives.values()}),
        "deterministic_equal_WAL_bytes_are_not_proof_of_reused_birth":True,
        "intervention_strength_independently_proven":False,
        "ranking_changes_UNATTESTED":True,
        "new_human_or_resource_knowledge":False,
        "cold_restore_of_research_adapter_verified":False,
        "scientific_verdict":"NO-GO",
        "by_arm":by_arm,
        "matched_pairs":paired,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=certify(a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in (
        "status","certified_original_wal_paths","scientific_verdict","by_arm")},
        sort_keys=True))


if __name__=="__main__":
    main()
