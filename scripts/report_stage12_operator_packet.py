#!/usr/bin/env python3
"""Read-only, operator-only Stage12 evidence packet for one canonical export.

Every independent audit uses the SAME trusted external tail anchors. This
program cannot resume an I0 life, query Oracle/Bench, or amend any journal.
Its assertions are technical evidence, never scientific or operator sign-off.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_alignment import evaluate_goal_action_alignment
from lab.stage12_diagnostic_audit import audit_stage12_diagnostics
from lab.stage12_occupancy_audit import audit_stage12_occupancy
from lab.stage12_operator_alert_audit import audit_stage12_operator_alerts


def evaluate_packet(
    content: bytes, *, expected_head: str, expected_count: int,
    expected_world_steps: int | None = None, require_terminal_stop: bool = False,
) -> dict[str, object]:
    if type(expected_count) is not int or expected_count < 1:
        raise ValueError("trusted occurrence count must be positive")
    if expected_world_steps is not None and (
        type(expected_world_steps) is not int or expected_world_steps < 1
    ):
        raise ValueError("world-step expectation must be positive")
    anchors = {
        "expected_head": expected_head,
        "expected_count": expected_count,
    }
    journal = audit_export_bytes(content, **anchors)
    diagnostics = audit_stage12_diagnostics(content, **anchors)
    occupancy = audit_stage12_occupancy(content, **anchors)
    alerts = audit_stage12_operator_alerts(content, **anchors)
    alignment = evaluate_goal_action_alignment(content, **anchors)
    counts = alignment.as_dict()["counts"]

    if (diagnostics.world_steps_closed != journal.world_steps_closed
            or diagnostics.head_hash != journal.head_hash
            or occupancy.head_hash != journal.head_hash
            or alerts.head_hash != journal.head_hash
            or alignment.journal_head != journal.head_hash
            or alerts.examined_samples != diagnostics.diagnostic_samples
            or alignment.as_dict()["executed_physical_actions"] >
                journal.world_steps_closed):
        raise ValueError("cross-auditor Stage12 evidence mismatch")

    if (expected_world_steps is not None
            and journal.world_steps_closed != expected_world_steps):
        raise ValueError("real executed physical-step count does not meet expectation")

    terminal_stop = False
    if require_terminal_stop:
        last = json.loads(content.split(b"\n")[-1])["causal_event"]
        terminal_stop = last.get("kind") == "experiment_stopped"
        if not terminal_stop or journal.terminal_deaths:
            raise ValueError("campaign lacks nonlethal terminal operator stop")

    return {
        "schema": "stage12-operator-evidence-packet-v1",
        "technical_validation": "passed",
        "trusted_tail_anchors_provided": True,
        "operator_stage_accepted": False,
        "final_scientific_validation": "not_performed",
        "physical_truth_independently_verified": False,
        "journal": journal.as_dict(),
        "diagnostics": diagnostics.as_dict(),
        "st_module_occupancy": occupancy.as_dict(),
        "persistent_operator_alerts": alerts.as_dict(),
        "goal_action_alignment": {
            "schema": "stage12-external-goal-action-alignment-v1",
            "executed_physical_actions": len(alignment.actions),
            "counts": counts,
            "untraceable_is_not_irrational": True,
        },
        "checks": {
            "expected_world_steps": expected_world_steps,
            "terminal_operator_stop_required": require_terminal_stop,
            "terminal_operator_stop_verified": terminal_stop,
            "diagnostic_samples_match_alert_observations": True,
        },
        "open_gates": [
            "M-11 current physical+cognitive atomic crash recovery NOT certified",
            "Stage12 lived outcome/agency attribution pairing NOT independently verified",
            "Stage12 operator sign-off NOT given",
            "Final scientific module validation NOT performed",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical_export", type=Path)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--expected-world-steps", type=int)
    parser.add_argument("--require-terminal-stop", action="store_true")
    args = parser.parse_args(argv)
    try:
        path = args.canonical_export
        if not path.is_file() or path.is_symlink():
            raise ValueError("export must be a regular nonsymlink file")
        report = evaluate_packet(
            path.read_bytes(), expected_head=args.expected_head,
            expected_count=args.expected_count,
            expected_world_steps=args.expected_world_steps,
            require_terminal_stop=args.require_terminal_stop,
        )
    except (OSError, TypeError, ValueError) as exc:
        print("Stage12 operator evidence refused: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
