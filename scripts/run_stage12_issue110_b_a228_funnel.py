"""A2.28: preregistered B-born autonomous goal-opportunity attrition.

No command injection, no GA06 synthetic pairs, no physical truth fed to I0.
See docs/research/stage12-issue110-b-a228-opportunity-funnel-prereg-2026-10-15.fr.md.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import run_stage12_issue110_first_planning_state as factory
from lab.journal import HashChainedJournal
from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_dual_scope_audit import audit_stage12_dual_scope
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_operator_console import Stage12OperatorConsole

PROFILES = ("restored", "sustained", "episodic", "marginal")
STEPS = 64


def _num(v):
    if type(v) in (int, float):
        return float(v)
    if type(v) is dict and set(v) == {"$f64"}:
        return float.fromhex(v["$f64"])
    return None


def new_life(folder, profile, blocked):
    identity = f"i0:stage12:b:a228:{profile}:{'A2' if blocked else 'free'}"
    original = factory.Stage12Runtime

    def born(**kwargs):
        assert kwargs["subjective_goal_agency"] is True
        assert kwargs["attribution_join"] is True
        kwargs.update(attribution_join=False, dual_scope_agency=True,
                      dual_scope_cost_uc=1)
        return original(**kwargs)

    with patch.object(factory, "Stage12Runtime", side_effect=born):
        life, config, layout, equipment = factory.build_life(
            "near_food_free", 70.0, "horizon_three",
            wal_path=str(folder / "life.wal"), birth_life_id=identity,
            a2_external_obstacle=blocked,
            a2_obstacle_clear_step=4 if blocked else None,
            calibration_food_profile=profile, planning_depth=3,
            progressive_planning=True, progressive_evaluation_prefix=True,
            progressive_revalidate_on_new_capture=True,
            instrumental_geographic_value=False,
            extrinsic_gain_override=1.6)
    if life.stage3.control.dual_scope is None:
        raise ValueError("A2.28 baby lacks born-enabled dual scope")
    if life._meta_custody.attribution_pairs is not None:
        raise ValueError("B baby cannot join legacy GA06")
    Stage12OperatorConsole(substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-b-a228-opportunity-v1",
        maximum_world_steps=STEPS)
    return life, identity


def audit_counts(events, physical_steps):
    counts = Counter(e["kind"] for e in events)
    commands = Counter(e.get("primitive") for e in events
                       if e["kind"] == "command_experienced")
    motives = Counter(e["data"]["motive_type"] for e in events
                      if e["kind"] == "stage12_action_motive_attested")
    goal_changes = [e for e in events if e["kind"] == "active_goal_changed"]
    uc = Counter((e["data"]["operation"], e["data"]["accepted"])
                 for e in events if e["kind"] == "compute_charge"
                 and e.get("data", {}).get("operation") in (
                    "goal_agency_assessment",
                    "goal_outcome_responsibility_assessment",
                    "stage12_diagnostic_sample"))
    capture_food = []
    capture_water = []
    for e in events:
        if e["kind"] != "perceptual_capture":
            continue
        observed = e.get("data", {}).get("dual_scope_visible_body", {})
        capture_food.append(_num(observed.get("food")))
        capture_water.append(_num(observed.get("water")))
    assert counts["step_closed"] == physical_steps
    assert counts["command_experienced"] == physical_steps
    assert counts["world_transition_experienced"] == physical_steps
    assert counts["stage12_action_motive_attested"] == physical_steps
    assert sum(commands.values()) == physical_steps
    assert sum(motives.values()) == physical_steps
    assert counts["stage12_outcome_responsibility_judgement"] == sum(
        n for (operation, accepted), n in uc.items()
        if operation == "goal_outcome_responsibility_assessment")
    assert counts["stage12_goal_agency_precommitted"] == counts[
        "stage12_outcome_responsibility_precommitted"]
    assert counts["stage12_goal_agency_judgement"] == counts[
        "stage12_outcome_responsibility_judgement"]
    assert not any(e["kind"] in (
        "stage12_attribution_pair_admitted",
        "stage12_attribution_pair_applied",
        "stage12_attribution_sample_unavailable")
        for e in events)
    assert not any(e["kind"] == "external_input_received"
                   and e.get("operation") == "set_body" for e in events)
    return {
        "command_counts": dict(sorted(commands.items())),
        "motive_counts": dict(sorted(motives.items())),
        "goal_activations": sum(e.get("data", {}).get("after") is not None
                                for e in goal_changes),
        "goal_deactivations": sum(e.get("data", {}).get("after") is None
                                  for e in goal_changes),
        "goal_progress_prereg": counts["stage12_goal_progress_preregistered"],
        "goal_progress_followup": counts["stage12_goal_progress_followup"],
        "proximal_precommits": counts["stage12_goal_agency_precommitted"],
        "proximal_judgements": counts["stage12_goal_agency_judgement"],
        "dual_precommits": counts["stage12_outcome_responsibility_precommitted"],
        "dual_judgements": counts["stage12_outcome_responsibility_judgement"],
        "waking_captures": counts["perceptual_capture"],
        "reduced_sleep_captures": counts["stage10_reduced_capture"],
        "sleep_wake_transitions": counts["stage10_sleep_woke"],
        "uc_debits": {
            operation: {"accepted": uc[(operation, True)],
                        "refused": uc[(operation, False)]}
            for operation in (
                "goal_agency_assessment",
                "goal_outcome_responsibility_assessment",
                "stage12_diagnostic_sample")
        },
        "first_person_food": {
            "first": next((v for v in capture_food if v is not None), None),
            "last": next((v for v in reversed(capture_food) if v is not None), None),
            "unique_values": len(set(v for v in capture_food if v is not None))
        },
        "first_person_water": {
            "first": next((v for v in capture_water if v is not None), None),
            "last": next((v for v in reversed(capture_water) if v is not None), None),
            "unique_values": len(set(v for v in capture_water if v is not None))
        }
    }


def run_one(folder, profile, blocked):
    folder.mkdir(parents=True, exist_ok=False)
    life, identity = new_life(folder, profile, blocked)
    steps = 0
    for _ in range(STEPS):
        if life.stage3.substrate.mortal_status.value != "active":
            break
        result = life.run_step()
        if result.execution_status != "applied":
            raise ValueError("non-applied autonomous step: " + result.execution_status)
        steps += 1
    raw = life.journal.canonical_bytes()
    (folder / "canonical.jsonl").write_bytes(raw)
    anchor = {"expected_head": life.journal.head_hash,
              "expected_count": len(life.journal.entries)}
    wal = HashChainedJournal.audit_durable_wal(str(folder / "life.wal"))
    if wal["head_hash"] != anchor["expected_head"] or wal["verified_entries"] != anchor["expected_count"]:
        raise ValueError("durable WAL mismatches B journal")
    base = audit_export_bytes(raw, **anchor)
    proximal = audit_stage12_first_person_agency(raw, **anchor)
    dual = audit_stage12_dual_scope(raw, **anchor)
    goal = audit_stage12_goal_progress(raw, **anchor)
    if base.world_steps_closed != steps:
        raise ValueError("B physical step count mismatch")
    events = [json.loads(line)["causal_event"] for line in raw.splitlines()]
    metrics = audit_counts(events, steps)
    if dual.precommits != metrics["dual_precommits"] or dual.judgements != metrics["dual_judgements"]:
        raise ValueError("B independent receipts mismatch")
    report = {
        "birth_id": identity, "profile": profile, "obstacle": "A2" if blocked else "free",
        "world_steps": steps, "terminal_status": life.stage3.substrate.mortal_status.value,
        "journal_head": anchor["expected_head"], "journal_count": anchor["expected_count"],
        "journal_sha256": sha256(raw).hexdigest(),
        "audited_proximal_self": proximal.judgements_self,
        "audited_proximal_world": proximal.judgements_world,
        "audited_proximal_unknown": proximal.judgements_unknown,
        "audited_proximal_unavailable": proximal.unavailable,
        "audited_dual_unavailable": dual.unavailable,
        "audited_dual_pending": dual.unresolved,
        "audited_goal_prereg": goal.preregistered,
        **metrics,
    }
    (folder / "result.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=False)
    rows = []
    for profile in PROFILES:
        for blocked in (False, True):
            label = f"{profile}-{'a2' if blocked else 'free'}"
            try:
                report = run_one(a.output_dir / label, profile, blocked)
                print("A228_LIFE " + json.dumps(report, sort_keys=True), flush=True)
                rows.append(report)
            except Exception as exc:
                error = {"profile": profile, "obstacle": "A2" if blocked else "free",
                         "error": f"{type(exc).__name__}: {exc}"}
                (a.output_dir / f"{label}-error.json").write_text(
                    json.dumps(error, sort_keys=True, indent=2) + "\n")
                print("A228_ERROR " + json.dumps(error, sort_keys=True), flush=True)
                rows.append(error)
    summary = {
        "schema": "stage12-a228-b-opportunity-funnel-v1",
        "head_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "lives_planned": 8, "lives_reported": len(rows),
        "fully_audited_lives": sum("error" not in r for r in rows),
        "physical_steps": sum(r.get("world_steps", 0) for r in rows),
        "dual_judgements": sum(r.get("dual_judgements", 0) for r in rows),
        "active_goal_motive_actions": sum(r.get("motive_counts", {}).get("active_goal", 0)
                                         for r in rows),
        "unknown_distal_only": True,
        "ga06_legacy_join": False,
        "operator_reception": False,
        "stage12": "PARTIAL",
        "lives": rows,
    }
    (a.output_dir / "a228-summary.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    print("A228_SUMMARY " + json.dumps({k:v for k,v in summary.items() if k!="lives"},
                                      sort_keys=True), flush=True)
    if summary["lives_reported"] != 8 or summary["fully_audited_lives"] != 8:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
