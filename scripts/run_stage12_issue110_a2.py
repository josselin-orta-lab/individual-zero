"""Prospective, four independent autonomous A2 contrasts, never forced action."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from lab.journal import HashChainedJournal
from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_spatial_cue_audit import audit_spatial_visible_cues
from lab.stage12_operator_console import Stage12OperatorConsole
from run_stage12_issue110_first_planning_state import build_life


def run_one(folder, family, intervention, cohort_id):
    folder.mkdir()
    world = "near_" + family + "_free"
    life_id = "i0:issue110:a2:" + cohort_id + ":" + family + ":" + (
        "obstacle" if intervention else "free")
    life, _, _, equipment = build_life(
        world, 70.0, "horizon_three", wal_path=str(folder / "life.wal"),
        birth_life_id=life_id, a2_external_obstacle=intervention)
    Stage12OperatorConsole(
        substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-issue110-a2-fixed-v1", maximum_world_steps=50)
    actions = Counter()
    error = None
    for _ in range(50):
        try:
            result = life.run_step()
            if result.execution_status != "applied":
                error = "nonapplied:" + result.execution_status
                break
            actions[result.command_primitive] += 1
        except Exception as exc:
            error = type(exc).__name__ + ":" + str(exc)
            break
    raw = life.journal.canonical_bytes()
    (folder / "canonical.jsonl").write_bytes(raw)
    custody = {"expected_head": life.journal.head_hash,
               "expected_count": len(life.journal.entries)}
    audits = {}
    audit_error = None
    try:
        wal = HashChainedJournal.audit_durable_wal(str(folder / "life.wal"))
        if wal["head_hash"] != custody["expected_head"] or (
                wal["verified_entries"] != custody["expected_count"]):
            raise ValueError("WAL not identical to canonical journal")
        checks = {
            "base": audit_export_bytes,
            "goal": audit_stage12_goal_progress,
            "agency": audit_stage12_first_person_agency,
            "pairs": audit_stage12_attribution_pairs,
            "cues": audit_spatial_visible_cues,
        }
        audits = {name: fn(raw, **custody).as_dict() for name, fn in checks.items()}
        if audits["base"].get("world_steps_closed") != sum(actions.values()):
            raise ValueError("actual commands and step closure differ")
    except Exception as exc:
        audit_error = type(exc).__name__ + ":" + str(exc)
    rows = [e.causal_event for e in life.journal.entries]
    external = [e for e in rows if e.get("kind") == "external_input_applied"
                and e.get("phase") == "after_admission"]
    on_step = [e for e in rows if e.get("t_monde") == 2]
    positions = {name: next((i for i,e in enumerate(on_step)
                             if e.get("kind") == name), None)
                 for name in ("command_experienced", "external_input_applied",
                              "world_transition_experienced")}
    order = (all(x is not None for x in positions.values()) and
             positions["command_experienced"] <
             positions["external_input_applied"] <
             positions["world_transition_experienced"])
    report = {
        "life_id": life_id, "family": family, "intervention": intervention,
        "executed_steps": sum(actions.values()), "actions": dict(actions),
        "error": error, "audit_error": audit_error,
        "journal_sha256": sha256(raw).hexdigest(),
        "journal_head": custody["expected_head"],
        "equipment_sha256": equipment.artifact_digest,
        "external_interventions_applied": len(external),
        "verified_post_admission_order": order if intervention else None,
        "audits": audits, "scientific_validation": "not_performed",
        "operator_accepted": False,
    }
    (folder / "result.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cohort-id", required=True)
    args = parser.parse_args()
    if (not 1 <= len(args.cohort_id) <= 32 or any(c not in
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
            for c in args.cohort_id)):
        raise ValueError("new A2 campaign needs valid unique cohort ID")
    root = args.output_dir
    root.mkdir(parents=True, exist_ok=False)
    sha = subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    records = []
    for family in ("food", "water"):
        for intervention in (False, True):
            name = family + ("_obstacle" if intervention else "_free")
            records.append(run_one(root / name, family, intervention, args.cohort_id))
    total = lambda key: sum(r.get("audits", {}).get("agency", {}).get(key, 0) for r in records)
    report = {
        "schema": "stage12-issue110-a2-autonomous-prospective-v1",
        "source_sha": sha, "preregistration":
            "docs/research/stage12-issue110-a2-prereg-2026-10-14.fr.md",
        "planned_lives": 4, "actual_lives": len(records),
        "real_physical_steps": sum(r["executed_steps"] for r in records),
        "agency_self": total("judgements_self"), "agency_world": total("judgements_world"),
        "agency_unknown": total("judgements_unknown"),
        "agency_unavailable": total("unavailable"),
        "lives": records, "operator_accepted": False,
        "scientific_validation": "not_performed",
    }
    (root / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(json.dumps(report, sort_keys=True))
    return 0 if all(not r["audit_error"] and not r["error"] and
                    (not r["intervention"] or r["verified_post_admission_order"])
                    for r in records) else 2

if __name__ == "__main__":
    raise SystemExit(main())
