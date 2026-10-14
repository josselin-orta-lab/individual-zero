"""Preregistered Stage12 calibration feasibility, never a forced I0 decision."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_operator_console import Stage12OperatorConsole
from run_stage12_issue110_first_planning_state import build_life

CONDITIONS = (
    ("free", False, None),
    ("fixed_obstacle", True, None),
    ("clear_at_3", True, 3),
    ("clear_at_4", True, 4),
)
MAX_STEPS = 16


def source_step_trace(raw: bytes) -> list[dict]:
    """Read-only event census, never a replacement for the independent audits.

    Missing receipts are counted as missing; no synthetic attribution or
    causal labels are constructed from the physical evaluator's knowledge.
    """
    keys = {
        "perceptual_capture": "perception",
        "stage10_reduced_capture": "sleep_reduced_capture",
        "stage10_sleep_entered": "sleep_entered",
        "stage10_sleep_woke": "sleep_woke",
        "stage12_goal_progress_preregistered": "intent",
        "stage12_goal_agency_precommitted": "agency_precommit",
        "stage12_goal_agency_judgement": "agency_judgement",
        "stage12_goal_progress_followup": "outcome",
        "stage12_attribution_pair_admitted": "pair_admitted",
        "stage12_attribution_join_deferred": "join_deferred",
        "stage12_attribution_sample_unavailable": "pair_unavailable",
        "stage12_lived_diagnostics_published": "diagnostic",
        "stage12_lived_diagnostics_deferred": "diagnostic_deferred",
        "command_experienced": "command",
        "world_transition_experienced": "physics",
        "external_input_applied": "external",
    }
    by_step: dict[int, dict] = {}
    for line in raw.splitlines():
        event = json.loads(line)["causal_event"]
        t = event.get("t_monde")
        kind = keys.get(event.get("kind"))
        if type(t) is not int or kind is None:
            continue
        row = by_step.setdefault(t, {"step": t})
        data = event.get("data", {})
        record = {"event": kind}
        if kind == "command":
            record.update(primitive=event.get("primitive"),
                          direction=event.get("parameters", {}).get("direction"))
        elif kind == "intent" and isinstance(data, dict):
            record.update(measure=data.get("measure"),
                          target_kind=data.get("target_kind"),
                          observe_world_step=data.get("observe_world_step"))
        elif kind == "agency_judgement" and isinstance(data, dict):
            record.update(agency=data.get("subjective_agency"),
                          reason=data.get("reason"))
        elif kind == "outcome" and isinstance(data, dict):
            record.update(outcome=data.get("criterion_outcome"),
                          reason=data.get("reason"))
        elif kind == "pair_admitted" and isinstance(data, dict):
            record.update(outcome=data.get("outcome"), agency=data.get("agency"))
        elif kind == "pair_unavailable" and isinstance(data, dict):
            record.update(reason=data.get("reason"),
                          due_world_step=data.get("due_world_step"))
        elif kind == "diagnostic" and isinstance(data, dict):
            record.update(pair_applied=(data.get("attribution_pair_ref") is not None),
                          verified_successes=data.get("verified_successes"),
                          verified_failures=data.get("verified_failures"),
                          attribution_bias=data.get("attribution_bias"))
        elif kind == "physics":
            record.update(position_after=event.get("position_after"),
                          movement=event.get("effects", {}).get("movement"))
        elif kind == "external":
            record.update(phase=event.get("phase", "before_step"))
        row.setdefault("receipts", []).append(record)
    return [by_step[t] for t in sorted(by_step)]


def run_one(folder: Path, name: str, obstacle: bool, clear_step: int | None,
            cohort: str) -> dict:
    folder.mkdir()
    life_id = "i0:110:calibration:" + cohort + ":" + name
    life, _, _, _ = build_life(
        "near_food_free", 70.0, "horizon_three",
        wal_path=str(folder / "life.wal"),
        birth_life_id=life_id, a2_external_obstacle=obstacle,
        a2_obstacle_clear_step=clear_step,
    )
    Stage12OperatorConsole(
        substrate=life.stage3.substrate, mode="campaign",
        policy_version="issue110-calibration-feasibility-v1",
        maximum_world_steps=MAX_STEPS,
    )
    counts = Counter()
    failure = None
    for _ in range(MAX_STEPS):
        try:
            result = life.run_step()
            if result.execution_status != "applied":
                failure = "nonapplied:" + result.execution_status
                break
            counts[result.command_primitive] += 1
        except Exception as exc:
            failure = type(exc).__name__ + ": " + str(exc)
            break
    raw = life.journal.canonical_bytes()
    (folder / "canonical.jsonl").write_bytes(raw)
    trace = source_step_trace(raw)
    (folder / "source-step-trace.json").write_text(
        json.dumps(trace, indent=2, sort_keys=True) + "\n"
    )
    anchor = dict(expected_head=life.journal.head_hash,
                  expected_count=len(life.journal.entries))
    audit_error, summary = None, {}
    try:
        durable = HashChainedJournal.audit_durable_wal(str(folder / "life.wal"))
        if (durable["head_hash"] != anchor["expected_head"] or
                durable["verified_entries"] != anchor["expected_count"]):
            raise ValueError("durable WAL diverges from journal")
        base = audit_export_bytes(raw, **anchor)
        goal = audit_stage12_goal_progress(raw, **anchor)
        agency = audit_stage12_first_person_agency(raw, **anchor)
        pair = audit_stage12_attribution_pairs(raw, **anchor)
        if base.world_steps_closed != sum(counts.values()):
            raise ValueError("steps differ from closed physics")
        # Independent pair auditor is also the source of authoritative
        # within-life 12-observation diagnostic counts.
        labels = [label for _, label in pair.diagnostic_labels if label is not None]
        rows = [json.loads(line)["causal_event"] for line in raw.splitlines()]
        inputs = [e for e in rows if e.get("kind") == "external_input_received"]
        summary = {
            "goal_criteria": goal.preregistered,
            "spatial_criteria": goal.spatial_preregistered,
            "agency_precommits": agency.precommits,
            "agency_self": agency.judgements_self,
            "agency_world": agency.judgements_world,
            "agency_unknown": agency.judgements_unknown,
            "admitted_pairs": pair.admitted_pairs,
            "applied_pairs": pair.applied_pairs,
            "applied_successes": pair.applied_successes,
            "applied_failures": pair.applied_failures,
            "applied_self": pair.applied_self,
            "applied_world": pair.applied_world,
            "bias_labels": labels,
            "min_2_success_2_failure_reached": bool(labels),
            "external_operations": [
                {"step": e["t_monde"], "phase": e.get("phase", "before_step"),
                 "operation": e.get("operation"), "payload": e.get("payload")}
                for e in inputs
            ],
        }
    except Exception as exc:
        audit_error = type(exc).__name__ + ": " + str(exc)
    result = dict(condition=name, life_id=life_id,
                  source_journal_sha256=sha256(raw).hexdigest(),
                  journal_head=anchor["expected_head"],
                  executed_physical_steps=sum(counts.values()),
                  actual_commands=dict(counts),
                  failure=failure, audit_error=audit_error,
                  source_trace=trace,
                  **summary)
    (folder / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cohort-id", type=str, required=True)
    args = parser.parse_args()
    if (not 1 <= len(args.cohort_id) <= 30 or
            not all(c.isascii() and (c.isalnum() or c in "._-")
                    for c in args.cohort_id)):
        raise ValueError("provide new unique cohort id")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    results = [run_one(args.output_dir/name, name, obstacle, clear, args.cohort_id)
               for name, obstacle, clear in CONDITIONS]
    summary = {
        "schema": "issue110-attribution-calibration-feasibility-v1",
        "source_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip(),
        "preregistration": "docs/research/stage12-issue110-attribution-calibration-prereg-2026-10-14.fr.md",
        "planned_lives": len(CONDITIONS), "executed_lives": len(results),
        "physical_steps": sum(r["executed_physical_steps"] for r in results),
        "verified_self": sum(r.get("agency_self",0) for r in results),
        "verified_world": sum(r.get("agency_world",0) for r in results),
        "applied_pairs": sum(r.get("applied_pairs",0) for r in results),
        "evaluable_lives": sum(r.get("min_2_success_2_failure_reached",False)
                               for r in results),
        "lives": results,
        "scientific_status": "exploratory_not_confirmatory",
        "operator_accepted": False,
    }
    (args.output_dir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    # Short stdout for GitHub Actions audit; full files preserved as artifact.
    print(json.dumps({k: v for k,v in summary.items() if k != "lives"},
                     sort_keys=True))
    for r in results:
        print(json.dumps({k:v for k,v in r.items()
                          if k not in ("external_operations","actual_commands","source_trace")},
                         sort_keys=True))
    return 0 if all(not r["failure"] and not r["audit_error"] for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
