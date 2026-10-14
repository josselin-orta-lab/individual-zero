"""Preregistered Stage12 A2.6: six genuine mortal lives, up to 600 steps each.

Never force a decision or create synthetic step/pair evidence. All per-step
physical checkpoints and summaries are offline, after the run, from WAL-
anchored immutable event receipts. Honor death, halt and safety block.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from run_stage12_issue110_first_planning_state import build_life
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_a2_causal_audit import audit_stage12_a2_causal_link
from lab.stage12_p48_diversity_audit import audit_stage12_p48_diversity

MAX_STEPS = 600
PAIRS = (("restored", False), ("restored", True), ("sustained", False))
MILESTONES = (100, 300, 600)
PREREG = (
    "docs/research/stage12-issue110-a26-long-horizon-prereg-2026-10-14.fr.md"
)


def _snapshot(physical: dict, events: list[dict], horizon: int) -> dict | None:
    """Read-only snapshot at a genuinely closed physical-step milestone."""
    if physical["world_steps"] < horizon:
        return None
    path = physical["positions"][:horizon]
    sites = {(x["x"], x["y"]) for x in path}
    # Include the genuine pre-step perceptual origin, not invented metadata.
    first = next((
        e.get("data", {}).get("position")
        for e in events
        if e.get("kind") == "perceptual_capture" and e.get("t_monde") == 1
    ), None)
    if isinstance(first, dict) and set(first) == {"x", "y"}:
        sites.add((first["x"], first["y"]))
    cmds = Counter(x["command"] for x in path)
    judgements = Counter(
        e.get("data", {}).get("subjective_agency")
        for e in events
        if e.get("kind") == "stage12_goal_agency_judgement"
        and e.get("t_monde", 0) <= horizon
    )
    eaten = sum(
        e.get("kind") == "world_transition_experienced"
        and e.get("t_monde", 0) <= horizon
        and e.get("effects", {}).get("ate") in ("berry_a", "berry_b")
        for e in events
    )
    food_increases = sum(
        path[i]["food_after"] > path[i-1]["food_after"]
        for i in range(1, len(path))
    )
    return {
        "step": horizon, "physically_distinct_sites": len(sites),
        "moves": cmds.get("se_deplacer", 0),
        "confirmed_moves": sum(
            x["movement"] == "moved" for x in path
        ), "blocked_moves": sum(x["movement"] == "blocked" for x in path),
        "sleep": cmds.get("dormir", 0), "wait": cmds.get("attendre", 0),
        "eaten": eaten, "food_increase_steps": food_increases,
        "food_last": path[-1]["food_after"],
        "active_goal_motives": sum(
            e.get("kind") == "stage12_action_motive_attested"
            and e.get("t_monde", 0) <= horizon
            and e.get("data", {}).get("motive_type") == "active_goal"
            for e in events
        ),
        "agency_self": judgements.get("self", 0),
        "agency_world": judgements.get("world", 0),
        "agency_unknown": judgements.get("unknown", 0),
        "attribution_pairs_consumed": sum(
            e.get("kind") == "stage12_lived_diagnostics_published"
            and e.get("t_monde", 0) <= horizon
            and e.get("data", {}).get("attribution_pair_ref") is not None
            for e in events
        ),
    }


def run_one(root: Path, cohort: str, profile: str, obstacle: bool,
            instrumental: bool) -> dict:
    name = (
        ("instrumental_" if instrumental else "control_") + profile
        + ("_a2" if obstacle else "_free")
    )
    folder = root / name
    folder.mkdir()
    birth = "i0:110:a26:" + cohort + ":" + name
    life, config, layout, equipment = build_life(
        "near_food_free", 70.0, "horizon_three",
        birth_life_id=birth, wal_path=str(folder / "life.wal"),
        a2_external_obstacle=obstacle,
        a2_obstacle_clear_step=(4 if obstacle else None),
        calibration_food_profile=profile, progressive_planning=True,
        progressive_evaluation_prefix=True,
        instrumental_geographic_value=instrumental,
    )
    console = Stage12OperatorConsole(
        substrate=life.stage3.substrate, mode="campaign",
        policy_version="issue110-a26-longitudinal-prereg-v1",
        maximum_world_steps=MAX_STEPS,
    )
    actions = Counter()
    problem = None
    ending = "uncertain"
    for t in range(1, MAX_STEPS + 1):
        current = life.stage3.substrate.mortal_status.value
        if current != "active":
            ending = current
            break
        try:
            step = life.run_step()
            if step.execution_status != "applied":
                ending = "nonapplied:" + step.execution_status
                break
            actions[step.command_primitive] += 1
        except Exception as exc:
            problem = type(exc).__name__ + ": " + str(exc)
            ending = life.stage3.substrate.mortal_status.value
            break
        if t % 100 == 0:
            print("A26_PROGRESS " + json.dumps(
                {"condition": name, "step": t,
                 "status": life.stage3.substrate.mortal_status.value,
                 "commands": dict(actions)}, sort_keys=True),
                flush=True,
            )
    if len(actions) and sum(actions.values()) == MAX_STEPS:
        ending = "experiment_stop_at_600"
        if life.stage3.substrate.mortal_status.value == "active":
            # The operator ends this experiment externally; this is not death
            # and does not advance the world by even one additional step.
            console.arreter(reason="world_step_cap_reached")
        else:
            ending = life.stage3.substrate.mortal_status.value
    elif ending == "uncertain":
        ending = life.stage3.substrate.mortal_status.value
    raw = life.journal.canonical_bytes()
    (folder / "canonical.jsonl").write_bytes(raw)
    report = {
        "condition": name, "profile": profile, "a2": obstacle,
        "instrumental": instrumental, "life_id": birth,
        "config_sha256": config.digest(),
        "equipment_sha256": equipment.artifact_digest,
        "journal_sha256": sha256(raw).hexdigest(),
        "world_steps": sum(actions.values()),
        "commands": dict(actions), "terminal_status": ending,
        "runtime_exception": problem, "audit_error": None,
    }
    try:
        anchors = dict(expected_head=life.journal.head_hash,
                       expected_count=len(life.journal.entries))
        durable = HashChainedJournal.audit_durable_wal(
            str(folder / "life.wal"))
        if (durable["head_hash"] != anchors["expected_head"]
                or durable["verified_entries"] != anchors["expected_count"]):
            raise ValueError("WAL and physical journal custody mismatch")
        base = audit_export_bytes(raw, **anchors)
        goal = audit_stage12_goal_progress(raw, **anchors)
        agency = audit_stage12_first_person_agency(raw, **anchors)
        pairs = audit_stage12_attribution_pairs(raw, **anchors)
        p48 = audit_stage12_p48_diversity(raw, **anchors)
        if base.world_steps_closed != report["world_steps"]:
            raise ValueError("real physical closure count mismatch")
        if obstacle:
            a2 = audit_stage12_a2_causal_link(
                raw, expected_interventions=((2, 3, 1),),
                **anchors)
            report["independent_a2_world_judgements"] = (
                a2.verified_a2_subjective_world_judgements)
        events = [json.loads(line)["causal_event"]
                  for line in raw.splitlines()]
        milestones = {
            str(n): _snapshot(p48, events, n) for n in MILESTONES
        }
        report.update(
            physical_census={
                k: v for k, v in p48.items()
                if k not in ("positions", "cross_option_shared_signals")
            },
            milestones=milestones,
            goal_criteria=goal.preregistered,
            agency_self=agency.judgements_self,
            agency_world=agency.judgements_world,
            agency_unknown=agency.judgements_unknown,
            pairs_applied=pairs.applied_pairs,
            applied_successes=pairs.applied_successes,
            applied_failures=pairs.applied_failures,
            evaluable=any(
                label is not None for _, label in pairs.diagnostic_labels
            ),
        )
        (folder / "a26-milestones.json").write_text(
            json.dumps(milestones, sort_keys=True, indent=2) + "\n")
    except Exception as exc:
        report["audit_error"] = type(exc).__name__ + ": " + str(exc)
    (folder / "a26-result.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n")
    print("A26_LIFE " + json.dumps(report, sort_keys=True), flush=True)
    return report


def _paired(lives: list[dict]) -> list[dict]:
    by_key = {(v["profile"], v["a2"], v["instrumental"]): v
              for v in lives}
    results = []
    for profile, a2 in PAIRS:
        control = by_key[(profile, a2, False)]
        instrumental = by_key[(profile, a2, True)]
        comparison = {
            "profile": profile, "a2": a2,
            "control_world_steps": control["world_steps"],
            "instrumental_world_steps": instrumental["world_steps"],
            "control_terminal": control["terminal_status"],
            "instrumental_terminal": instrumental["terminal_status"],
        }
        for n in MILESTONES:
            off = (control.get("milestones") or {}).get(str(n))
            on = (instrumental.get("milestones") or {}).get(str(n))
            comparison[str(n)] = (
                {"sites_off": off["physically_distinct_sites"],
                 "sites_on": on["physically_distinct_sites"],
                 "preserved_80pct": (
                     on["physically_distinct_sites"] * 5
                     >= off["physically_distinct_sites"] * 4),
                 "eaten_off": off["eaten"],
                 "eaten_on": on["eaten"],
                 "food_off": off["food_last"],
                 "food_on": on["food_last"],
                 "attribution_pairs_off": off["attribution_pairs_consumed"],
                 "attribution_pairs_on": on["attribution_pairs_consumed"]}
                if off is not None and on is not None else None
            )
        results.append(comparison)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cohort-id", required=True)
    args = parser.parse_args()
    if (not 1 <= len(args.cohort_id) <= 32
            or not all(c.isascii() and (c.isalnum() or c in "._-")
                       for c in args.cohort_id)):
        parser.error("unique ASCII cohort ID required, maximum 32 chars")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    lives = []
    for instrumental in (False, True):
        for profile, a2 in PAIRS:
            try:
                lives.append(run_one(
                    args.output_dir, args.cohort_id, profile, a2,
                    instrumental))
            except Exception as exc:
                # Do not fabricate a sixth life or conceal earlier WALs.
                lives.append({
                    "profile": profile, "a2": a2,
                    "instrumental": instrumental, "world_steps": 0,
                    "terminal_status": "failed",
                    "runtime_exception": type(exc).__name__ + ": " + str(exc),
                    "audit_error": "no complete independent audit",
                })
    overview = {
        "schema": "stage12-a26-long-horizon-v1",
        "preregistration": PREREG,
        "source_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip(),
        "cohort": args.cohort_id,
        "lives": lives,
        "planned_lives": 6,
        "actual_lives": len(lives),
        "actual_world_steps": sum(v["world_steps"] for v in lives),
        "completed_600": sum(
            v["world_steps"] == MAX_STEPS for v in lives),
        "physical_deaths": sum(
            v["terminal_status"] == "dead" for v in lives),
        "audit_or_runtime_failures": sum(
            bool(v.get("audit_error") or v.get("runtime_exception"))
            for v in lives),
        "evaluable_attribution_lives": sum(
            bool(v.get("evaluable")) for v in lives),
        "paired": _paired(lives),
        "operator_accepted": False,
        "scientific_validation_claimed": False,
    }
    (args.output_dir / "a26-summary.json").write_text(
        json.dumps(overview, indent=2, sort_keys=True) + "\n")
    print("A26_SUMMARY " + json.dumps({
        k: v for k, v in overview.items() if k != "lives"
    }, sort_keys=True), flush=True)
    return 0 if overview["audit_or_runtime_failures"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
