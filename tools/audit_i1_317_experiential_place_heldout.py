#!/usr/bin/env python3
"""#317: independently attest 32 HELD-OUT original experiential mortal WAL.

No alive actor import, motor simulation, rollback, replay, or read of unobserved
world resource state. Authenticate each real journal and mortal transition
BEFORE comparing archived Stage8 relevance, Competition, Action Control, and
first-person positive boire association. Independent deterministic births
may lawfully have identical WAL content hashes. Scientific NO-GO by design.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from math import isfinite, isclose
from pathlib import Path

from audit_i1_317_two_process_cohort import _verify_arm
from audit_i1_317_lived_place_cohort import (
    classify_original, NATIVE_SLEEP, NATIVE_WAKE,
)
from audit_i1_spatial_navigation_314 import audit as authenticate_wal

SCHEMA = "i1-317-experiential-place-heldout-32-wal/v1"
BIRTH_SCHEMA = "i1-317-experiential-place-heldout-mortal/v1"
EXACT_SHA = "4536cd2dda53e470ef577aa14ea98ab9ec05fc50"
EXACT_RUN = 39324485459
WORLDS = ("oasis", "foraging", "memory-corridor", "water-isolated-corridor")
SEEDS = (16127, 16249, 16381, 16513)
ARMS = ("guard_control", "guard_experiential")
EXPERIENTIAL_SIGNAL = "i1:personally-relieved-water:"
MAX_WATER = 30.0
MAX_BONUS = 0.45


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def number(value):
    if type(value) in (int, float):
        v = float(value)
    elif type(value) is dict and set(value) == {"$f64"}:
        v = float.fromhex(value["$f64"])
    else:
        raise ValueError("invalid canonical physical number")
    require(isfinite(v), "nonfinite WAL numeric evidence")
    return v


def point(p):
    return type(p) in (list, tuple) and len(p) == 2 and all(
        type(k) is int for k in p
    )


def inspect_wal(wal, expected_arm, world_steps):
    """Independent signals are real WAL records, not report counters."""
    require(expected_arm in ARMS, "alien arm")
    require(wal.is_file() and not wal.is_symlink(), "missing original mortal WAL")
    captures, admitted_personal, proposals = {}, {}, {}
    scores, traces, signals, command_by_step, admits = {}, {}, [], {}, {}
    uc_by_step = Counter()
    # GoalManager may legitimately change the active goal AFTER Planning
    # captured its old goal label, but BEFORE Stage8 evaluates the candidate.
    # WAL event order, not the earlier proposal annotation, is the authority.
    current_live_goal = None
    goal_transitions = set()
    goal_at_signal = {}
    with wal.open(encoding="utf-8") as stream:
        for line in stream:
            event = json.loads(line)["causal_event"]
            kind, step, cycle, data = (
                event["kind"], event.get("t_monde"),
                event.get("cycle"), event.get("data", {}),
            )
            if kind == "active_goal_changed":
                before, after = data.get("before"), data.get("after")
                require(before is None or
                        (type(before) is dict and
                         type(before.get("id")) is str and
                         type(before.get("goal_type")) is str),
                        "malformed previous GoalManager owner state")
                require(after is None or
                        (type(after) is dict and
                         type(after.get("id")) is str and
                         type(after.get("goal_type")) is str),
                        "malformed new GoalManager owner state")
                if current_live_goal is not None and before is not None:
                    require(before["id"] == current_live_goal["id"],
                            "GoalManager change breaks first-person chronology")
                current_live_goal = after
                if after is not None:
                    goal_transitions.add((step, cycle, after["id"]))
            elif kind == "perceptual_capture":
                require(type(step) is int and step not in captures,
                        "duplicate first-person capture")
                require(point((data.get("position", {}).get("x"),
                               data.get("position", {}).get("y"))),
                        "capture lacks first-person position")
                captures[step] = {
                    "position": (
                        data["position"]["x"], data["position"]["y"]),
                    "water": number(
                        data.get("dual_scope_visible_body", {}).get("water")),
                }
            elif kind == "i1_water_lived_outcome_admitted":
                site = data.get("source_position")
                require(data.get("admitted") is True and point(site)
                        and number(data.get("delta_water")) > 0
                        and type(step) is int,
                        "invalid previously lived beneficial source")
                admitted_personal.setdefault(tuple(site), []).append(step)
            elif kind == "i1_place_memory_option_proposed":
                site, ref = data.get("target"), data.get("option_ref")
                if point(site) and type(ref) is str:
                    key = (step, cycle, ref)
                    require(key not in proposals, "duplicated per-cycle place option")
                    proposals[key] = {
                        "site": tuple(site),
                        "goal": data.get("active_goal"),
                        "next": tuple(data["next"])
                            if point(data.get("next")) else None,
                        "entity_type": data.get("entity_type"),
                    }
            elif kind == "stage8_option_evaluation":
                ref = data.get("option_ref")
                key = (step, cycle, ref)
                if key in proposals:
                    require(key not in scores, "duplicate Stage8 place score")
                    scores[key] = (
                        None if data.get("evidence") is None
                        else number(data["evidence"])
                    )
            elif kind == "stage11_intrinsic_evaluation":
                active_signals = [
                    sig for sig in data.get("signal_ids", [])
                    if isinstance(sig, str)
                    and sig.startswith(EXPERIENTIAL_SIGNAL)
                ]
                if not active_signals:
                    continue
                require(expected_arm == "guard_experiential"
                        and len(active_signals) == 1
                        and "i1:conditional-lived-site-relevance" in
                        data.get("intrinsic_producers", ()),
                        "an untreated model fabricated experiential relevance")
                key = (step, cycle, data.get("option_ref"))
                require(key in proposals, "relevance without proposed place")
                site = proposals[key]["site"]
                require(active_signals[0] ==
                        f"{EXPERIENTIAL_SIGNAL}{site[0]}:{site[1]}",
                        "borrowed or mislocated first-person water signal")
                require(type(current_live_goal) is dict
                        and current_live_goal.get("goal_type") == "drink"
                        and current_live_goal.get("id", "").startswith("goal:drink:"),
                        "experimental relevance without live drink goal at Stage8")
                require(key not in goal_at_signal,
                        "duplicate same-cycle experiential signal")
                goal_at_signal[key] = dict(current_live_goal)
                signals.append(key)
            elif kind == "competition_cycle":
                for trace in data.get("traces", ()):
                    key = (step, cycle, trace.get("option_ref"))
                    if key not in proposals:
                        continue
                    require(key not in traces, "duplicate place Competition trace")
                    evidence = (
                        None if trace.get("evidence") is None
                        else number(trace["evidence"])
                    )
                    acc = number(trace.get("accumulator_after"))
                    threshold = number(trace.get("threshold"))
                    require(acc >= 0 and threshold > 0
                            and (evidence is None or -1 <= evidence <= 1)
                            and type(trace.get("crossed")) is bool,
                            "invalid place Competition margin")
                    traces[key] = {
                        "score": evidence,
                        "acc": acc,
                        "threshold": threshold,
                        "crossed": trace["crossed"],
                    }
            elif kind == "command_admitted":
                require(type(step) is int, "unindexed motor admission")
                admits.setdefault(step, []).append(data)
            elif kind == "command_experienced":
                require(type(step) is int and step not in command_by_step,
                        "duplicate physically executed motor")
                command_by_step[step] = (
                    event.get("primitive"), event.get("parameters"))
            elif kind == "compute_charge" and data.get("accepted") is True:
                require(type(step) is int and
                        type(data.get("requested_uc")) is int and
                        data["requested_uc"] >= 0, "forged UC charge")
                uc_by_step[step] += data["requested_uc"]

    require(set(command_by_step) == set(range(1, world_steps + 1)),
            "world steps not physically executed exactly once")
    acknowledged = []
    for key in signals:
        step, cycle, option_ref = key
        candidate = proposals[key]
        site = candidate["site"]
        require(site in admitted_personal
                and any(t < step for t in admitted_personal[site]),
                "relevance before admitted first-person benefit")
        capture = captures.get(step)
        require(capture is not None and
                0 <= capture["water"] <= MAX_WATER,
                "experimental relevance without currently perceived thirst")
        live_goal = goal_at_signal[key]
        stale_planning_goal = candidate["goal"] != live_goal["id"]
        if stale_planning_goal:
            require((step, cycle, live_goal["id"]) in goal_transitions,
                    "Stage8 relevance used stale goal without witnessed transition")
        score, trace = scores.get(key), traces.get(key)
        require(score is not None and trace is not None
                and trace["score"] is not None
                and score > 0 and
                isclose(score, trace["score"], abs_tol=1e-12, rel_tol=0),
                "experimental score was never used by Competition")
        require(0 < score <= 1, "invalid relevance strength")
        accepted_choice = any(
            row.get("option_ref") == option_ref and
            row.get("primitive") == "se_deplacer" and
            row.get("source") == "decision" and
            command_by_step.get(step, (None,))[0] == "se_deplacer"
            for row in admits.get(step, ())
        )
        acknowledged.append({
            "step": step, "cycle": cycle, "option_ref": option_ref,
            "site": list(site), "entity_type": candidate["entity_type"],
            "observed_water": capture["water"],
            "goal_at_planning": candidate["goal"],
            "goal_at_stage8": live_goal["id"],
            "goal_changed_after_planning_same_cycle": stale_planning_goal,
            "evidence": score, "threshold": trace["threshold"],
            "crossed": trace["crossed"],
            "option_physically_admitted": accepted_choice,
        })
    require(expected_arm != "guard_control" or not signals,
            "control arm must never add experiential signal")
    return {
        "signal_count_attested_in_wal": len(acknowledged),
        "signal_crossings": sum(x["crossed"] for x in acknowledged),
        "stage8_live_goal_transitions_verified": sum(
            x["goal_changed_after_planning_same_cycle"] for x in acknowledged),
        "signal_options_physically_admitted": sum(
            x["option_physically_admitted"] for x in acknowledged),
        "authenticated_relevance_events": acknowledged,
        "all_place_proposals": proposals,
        "competition_traces": traces,
        "physical_motors": command_by_step,
        "accepted_uc_by_step": uc_by_step,
    }


def paired_effect(control, treated):
    a, b = control["physical_motors"], treated["physical_motors"]
    common = min(len(a), len(b))
    first = next((t for t in range(1, common + 1) if a[t] != b[t]), None)
    before = (common + 1 if first is None else first)
    baseline_uc = sum(n for step, n in control["accepted_uc_by_step"].items()
                      if step < before)
    experimental_uc = sum(n for step, n in treated["accepted_uc_by_step"].items()
                          if step < before)
    require(baseline_uc == experimental_uc,
            "cognitive budget differs before first executed motor divergence")
    changed = []
    for key, extra in treated["competition_traces"].items():
        original = control["competition_traces"].get(key)
        if not original:
            continue
        if (extra["score"] is not None and original["score"] is not None
            and extra["score"] > original["score"] + 1e-12
            and key in treated["all_place_proposals"]
            and control["all_place_proposals"].get(key) ==
                treated["all_place_proposals"][key]):
            changed.append({
                "step": key[0], "cycle": key[1], "option_ref": key[2],
                "target_site": list(treated["all_place_proposals"][key]["site"]),
                "control_score": original["score"],
                "experimental_score": extra["score"],
                "new_threshold_crossing": (
                    extra["crossed"] and not original["crossed"]),
            })
    relevant_crossings = [x for x in changed if x["new_threshold_crossing"]]
    at_first = [] if first is None else [
        x for x in relevant_crossings if x["step"] == first
    ]
    return {
        "first_physical_motor_divergence": first,
        "control_motor": None if first is None else a[first],
        "treatment_motor": None if first is None else b[first],
        "accepted_uc_equal_before_first_divergence": True,
        "charged_uc_until_first_divergence_exclusive": baseline_uc,
        "comparable_place_score_increases": len(changed),
        "new_matched_place_threshold_crossings": len(relevant_crossings),
        "new_crossing_at_first_motor_change": bool(at_first),
        "first_changed_site": None if not at_first else at_first[0]["target_site"],
        "first_crossing_options": [x["option_ref"] for x in at_first],
    }



def motor_admission(wal, step):
    """Match real Action Control receipt to the physically applied motor."""
    commands=[]; admissions=[]
    with wal.open(encoding="utf-8") as stream:
        for line in stream:
            e=json.loads(line)["causal_event"]
            if e.get("t_monde")!=step:continue
            if e["kind"]=="command_experienced":commands.append(e)
            if e["kind"]=="command_admitted":admissions.append(e)
    require(len(commands)==1 and commands[0].get("emitter")=="action_control",
            "ambiguous actual motor")
    c=commands[0]
    matched=[a["data"] for a in admissions
             if a.get("attempt_ref")==c.get("attempt_ref")
             and a["data"].get("command_hash")==c.get("command_hash")
             and a["data"].get("primitive")==c.get("primitive")]
    require(len(matched)==1, "ambiguous physically matched admission")
    return {
        "option_ref": matched[0].get("option_ref"),
        "source": matched[0].get("source"),
        "primitive": c["primitive"],
    }

def certify(root):
    require(root.is_dir() and not root.is_symlink(),
            "missing original 18-life evidence")
    expected = {(world, seed) for world in WORLDS for seed in SEEDS}
    reports = {root/world/str(seed)/"report.json" for world, seed in expected}
    require(set(root.rglob("report.json")) == reports
            and not any(p.is_symlink() for p in reports),
            "incomplete, injected or redirected mortal cohort")
    birth_worlds, pairs, aggregates = {}, [], {a: Counter() for a in ARMS}
    for world, seed in sorted(expected):
        report = json.loads(
            (root/world/str(seed)/"report.json").read_text(encoding="utf-8"))
        require(
            report.get("schema") == BIRTH_SCHEMA
            and report.get("status") == "COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
            and report.get("source_sha") == EXACT_SHA
            and report.get("preset") == world and report.get("seed") == seed
            and report.get("horizon") == 300
            and report.get("preregistered_arms") == list(ARMS)
            and set(report.get("arms", {})) == set(ARMS)
            and report.get("both_arms_same_guarded_retrieval") is True
            and report.get("goal_conditioned_relevance_treatment_only") is True
            and report.get("relevance_maximum") == MAX_BONUS
            and report.get("relevance_water_gate") == MAX_WATER
            and report.get("learned_site_requires_personally_applied_boire_and_followup") is True
            and report.get("same_world_physics_needs_td_competition_action_control") is True
            and report.get("no_type_based_resource_utility") is True
            and report.get("no_motor_forcing_or_new_vital_reflex") is True
            and report.get("no_forced_motor_or_movement_water_forecast") is True
            and report.get("all_prior_seeds_excluded") is True
            and report.get("prior_source_algorithm_sha") == "43e1fa82e8034c20708d9edf380b41a5bf30502b"
            and report.get("heldout_validation_not_promotion") is True
            and report.get("water_berry_colocation_ablated_in_isolated_corridor") is True
            and report.get("no_cold_recovery_claim") is True
            and report.get("no_coma_implemented") is True
            and report.get("scientific_verdict") == "NO-GO",
            "falsified pre-registered birth specification")
        digest = (report.get("physics_digest"), report.get("preset_sha256"))
        require(all(isinstance(x, str) and len(x) == 64 for x in digest),
                "unidentified original world")
        if world in birth_worlds:
            require(birth_worlds[world] == digest, "matched world physics changed")
        birth_worlds[world] = digest
        arms = {}
        for arm in ARMS:
            rec = report["arms"][arm]
            require(
                rec.get("Stage10_sleep_pressure") == NATIVE_SLEEP
                and rec.get("physical_wake_thresholds") == NATIVE_WAKE
                and rec.get("option_ranking_adjusted") is True
                and rec.get("option_value_advisory_adjusted") is
                    (arm == "guard_experiential")
                and rec.get("wal_relative_path") == f"{arm}/life-01.wal",
                "hidden change to body, sleep, alert or cognitive arm")
            reported = rec.get("research_counters_UNATTESTED", {})
            require(type(reported) is dict and
                    set(reported).issubset({
                        "avoided_provably_noop_expansions",
                        "potentially_useful_expansions",
                        "rank_changes", "rank_budget_denied",
                        "unattested_relevance_evaluations",
                    }) and all(type(v) is int and v >= 0
                               for v in reported.values()),
                    "invalid optional lab counters")
            wal = root/world/str(seed)/arm/"life-01.wal"
            actual = _verify_arm(wal, rec, authenticate_wal)
            lived = classify_original(wal, actual["lived_steps"])
            require(lived["positive_sites_physically_supported"] ==
                    rec["positive_lived_source_sites"],
                    "wrong first-person beneficial-site count")
            evidence = inspect_wal(wal, arm, actual["lived_steps"])
            # Research counters are never the authority: WAL-only evidence
            # must independently reproduce any reported intervention count.
            if arm == "guard_experiential":
                require(
                    evidence["signal_count_attested_in_wal"] ==
                    reported.get("unattested_relevance_evaluations", 0),
                    "unattested experimental intervention was not WAL-visible")
            else:
                require(evidence["signal_count_attested_in_wal"] == 0,
                        "control arm gained experimental evidence")
            totals = aggregates[arm]
            totals["lives"] += 1
            totals["deaths"] += actual["lifecycle"] == "dead"
            totals["survive_to_horizon"] += actual["lifecycle"] == "active"
            totals["physical_steps"] += actual["lived_steps"]
            totals["physical_boire"] += actual["actions"].get("boire", 0)
            totals["physical_moves"] += actual["actions"].get("se_deplacer", 0)
            totals["objects_consolidated"] += actual["objects_consolidated"]
            totals["accepted_uc"] += actual["accepted_cognitive_uc"]
            totals["lived_beneficial_sites"] += (
                lived["positive_sites_physically_supported"])
            totals["WAL_verified_relevance_signals"] += (
                evidence["signal_count_attested_in_wal"])
            totals["WAL_verified_relevance_crossings"] += evidence["signal_crossings"]
            totals["WAL_verified_goal_switch_during_planning"] += (
                evidence["stage8_live_goal_transitions_verified"])
            arms[arm] = {"physical": actual, "wal_evidence": evidence}
        comparison = paired_effect(
            arms["guard_control"]["wal_evidence"],
            arms["guard_experiential"]["wal_evidence"],
        )
        first = comparison["first_physical_motor_divergence"]
        if first is not None:
            receipt=motor_admission(root/world/str(seed)/"guard_experiential"/"life-01.wal",first)
            comparison["physically_admitted_first_motor"] = receipt
            comparison["water_site_option_won"] = (
                "sighting:water_source:" in (receipt["option_ref"] or ""))
            comparison["berry_site_option_won"] = (
                "sighting:berry_" in (receipt["option_ref"] or ""))
        else:
            comparison["physically_admitted_first_motor"]=None
            comparison["water_site_option_won"]=False
            comparison["berry_site_option_won"]=False
        pairs.append({
            "world": world, "seed": seed,
            "physical_control": {
                k: arms["guard_control"]["physical"][k] for k in
                ("lifecycle", "lived_steps", "actions",
                 "objects_consolidated", "accepted_cognitive_uc")},
            "physical_experimental": {
                k: arms["guard_experiential"]["physical"][k] for k in
                ("lifecycle", "lived_steps", "actions",
                 "objects_consolidated", "accepted_cognitive_uc")},
            "authenticated_WAL_signal_count": arms[
                "guard_experiential"]["wal_evidence"]["signal_count_attested_in_wal"],
            "pair_comparison": comparison,
        })
    require(len(pairs) == 16 and
            all(aggregates[a]["lives"] == 16 for a in ARMS),
            "not all original mortal lives authenticated")
    by_world={}
    for world in WORLDS:
        group=[p for p in pairs if p["world"]==world]
        require(len(group)==4,"missing paired birth world")
        by_world[world]={
            "pairs":len(group),
            "pairs_with_control_applied_boire":sum(
                p["physical_control"]["actions"].get("boire",0)>0 for p in group),
            "pairs_with_treatment_applied_boire":sum(
                p["physical_experimental"]["actions"].get("boire",0)>0 for p in group),
            "first_motor_divergences":sum(
                p["pair_comparison"]["first_physical_motor_divergence"] is not None
                for p in group),
            "first_motor_water_option_won":sum(
                p["pair_comparison"]["water_site_option_won"] for p in group),
            "first_motor_berry_option_won":sum(
                p["pair_comparison"]["berry_site_option_won"] for p in group),
            "additional_applied_boire":sum(
                p["physical_experimental"]["actions"].get("boire",0)-
                p["physical_control"]["actions"].get("boire",0) for p in group),
        }
    return {
        "schema": SCHEMA,
        "status": "THIRTY_TWO_HELDOUT_MORTAL_WAL_AUDITED_NO_GLOBAL_GO",
        "source_run": EXACT_RUN, "exact_source_sha": EXACT_SHA,
        "certified_original_mortal_WAL_paths": 32,
        "same_initial_search_cost_tested_by_step": True,
        "no_new_lives_born_by_audit": True,
        "research_intervention_WAL_visible": True,
        "research_adapter_M11_cold_recovery_proven": False,
        "human_equivalence_proven": False,
        "scientific_verdict": "NO-GO",
        "by_arm": {arm: dict(counts) for arm, counts in aggregates.items()},
        "sixteen_heldout_mortal_pairs": pairs,
        "world_stratified_first_person_results": by_world,
        "first_actual_motor_option_attested": True,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    result = certify(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "scientific_verdict": result["scientific_verdict"],
        "certified_paths": result["certified_original_mortal_WAL_paths"],
        "by_arm": result["by_arm"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
