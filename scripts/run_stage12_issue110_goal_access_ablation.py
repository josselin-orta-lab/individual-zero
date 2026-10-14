"""Issue #110: unforced 2x2 goal-access ablation, preregistered before code.

Only pre-birth geographic exploration eligibility and initial water differ.
The subject chooses every physical command; audit results never feed cognition.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

from run_stage12_issue110_contrasted_science import ROOT, STEPS, run_life


PROTOCOL = "stage12-issue110-goal-access-ablation-v1"
PREREGISTRATION = (
    "docs/research/"
    "stage12-issue110-goal-access-ablation-prereg-2026-10-13.fr.md"
)


def summarize_canonical_receipts(content: bytes) -> dict[str, object]:
    """Passive post-life summary; not a goal or agency inference service."""
    if not content or not content.strip():
        raise ValueError("empty immutable life journal")
    counts: Counter[str] = Counter()
    motives: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    planned = 0
    planned_nonnull = 0
    for line in content.splitlines():
        row = json.loads(line)
        if type(row) is not dict or type(row.get("causal_event")) is not dict:
            raise ValueError("invalid canonical event representation")
        event = row["causal_event"]
        kind = event.get("kind")
        if type(kind) is not str:
            raise ValueError("canonical event type missing")
        counts[kind] += 1
        if kind == "stage6_planning_result":
            data = event.get("data")
            if not isinstance(data, dict) or "proposal_ref" not in data:
                raise ValueError("missing Stage6 planning result evidence")
            planned += 1
            proposal_ref = data["proposal_ref"]
            if proposal_ref is not None:
                if type(proposal_ref) is not str or not proposal_ref:
                    raise ValueError("invalid Stage6 planning option ref")
                planned_nonnull += 1
        elif kind == "stage12_action_motive_attested":
            data = event.get("data")
            if not isinstance(data, dict):
                raise ValueError("invalid lived motive receipt")
            motive_type = data.get("motive_type")
            if type(motive_type) is not str or not motive_type:
                raise ValueError("lived motive lacks source")
            motives[motive_type] += 1
            if (motive_type == "active_goal"
                    and data.get("goal_ref") == data.get("active_goal_ref")
                    and type(data.get("goal_ref")) is str):
                counts["matched_goal_motives"] += 1
        elif kind == "command_experienced":
            primitive = event.get("primitive")
            if type(primitive) is not str or not primitive:
                raise ValueError("lived command missing primitive")
            actions[primitive] += 1

    if planned_nonnull > planned:
        raise ValueError("planning receipts contradict")
    if sum(actions.values()) != counts["step_closed"]:
        raise ValueError("physical actions and step closure disagree")
    return {
        "schema": "stage12-independent-goal-access-counts-v1",
        "physical_steps": sum(actions.values()),
        "active_goal_changes": counts["active_goal_changed"],
        "planning_attempts": planned,
        "planning_proposals": planned_nonnull,
        "goal_motive_commands": counts["matched_goal_motives"],
        "goal_progress_precommits": counts["stage12_goal_progress_preregistered"],
        "agency_precommits": counts["stage12_goal_agency_precommitted"],
        "agency_judgements": counts["stage12_goal_agency_judgement"],
        "pairs_admitted": counts["stage12_attribution_pair_admitted"],
        "actions": dict(sorted(actions.items())),
        "motive_types": dict(sorted(motives.items())),
        "published_diagnostics": counts["stage12_lived_diagnostics_published"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=False)
    git_source = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT,
        text=True, capture_output=True, check=True,
    ).stdout.strip()
    cases = []
    for geography in (True, False):
        for water in (20.0, 35.0):
            label = f"geography-{int(geography)}-water{int(water)}"
            folder = root / label
            folder.mkdir()
            try:
                life = run_life(
                    folder, world="water_available", water=water,
                    sleep_profile="awake_ablation",
                    enable_geography=geography,
                )
                content = (folder / "canonical.jsonl").read_bytes()
                counts = summarize_canonical_receipts(content)
                if counts["physical_steps"] != life["applied_steps"]:
                    raise ValueError("goal-access count mismatches audited life")
                if life.get("audit_error"):
                    raise ValueError("life audit rejected: " + life["audit_error"])
                if counts["pairs_admitted"] != life["audits"]["pairs"]["admitted_pairs"]:
                    raise ValueError("pair count differs from independent audit")
                cases.append({
                    "case": label,
                    "geographic_exploration_enabled": geography,
                    "initial_water": water,
                    "life_sha256": hashlib.sha256(content).hexdigest(),
                    "life_head_hash": life["head_hash"],
                    "life_occurrences": life["occurrences"],
                    "life_applied_steps": life["applied_steps"],
                    "life_mortal_status": life["mortal_status"],
                    "life_failure": life["failure"],
                    "external_audit_valid": True,
                    "goal_access_counts": counts,
                    "independent_goal_progress": life["audits"]["goal"],
                    "independent_agency": life["audits"]["first_person"],
                    "independent_pairs": {
                        k: v for k, v in life["audits"]["pairs"].items()
                        if k != "diagnostic_labels"
                    },
                })
            except BaseException as error:
                failed = {
                    "case": label,
                    "geographic_exploration_enabled": geography,
                    "initial_water": water,
                    "external_audit_valid": False,
                    "error": type(error).__name__ + ": " + str(error),
                }
                cases.append(failed)
                (folder / "coverage-error.json").write_text(
                    json.dumps(failed, indent=2, sort_keys=True) + "\n",
                )
            (root / "index.json").write_text(
                json.dumps({
                    "schema": PROTOCOL, "source_sha": git_source,
                    "preregistration": PREREGISTRATION,
                    "planned_lives": 4, "completed_lives": len(cases),
                    "lives": cases,
                }, indent=2, sort_keys=True) + "\n",
            )
    valid = [life for life in cases if life.get("external_audit_valid")]
    summary = {
        "schema": PROTOCOL,
        "source_sha": git_source, "preregistration": PREREGISTRATION,
        "planned_lives": 4, "audited_lives": len(valid),
        "failed_or_unaudited_lives": 4 - len(valid),
        "actual_physical_steps": sum(
            row["goal_access_counts"]["physical_steps"] for row in valid
        ),
        "goal_planning_attempts": sum(
            row["goal_access_counts"]["planning_attempts"] for row in valid
        ),
        "goal_plans_proposed": sum(
            row["goal_access_counts"]["planning_proposals"] for row in valid
        ),
        "matched_goal_motive_commands": sum(
            row["goal_access_counts"]["goal_motive_commands"] for row in valid
        ),
        "goal_progress_precommits": sum(
            row["goal_access_counts"]["goal_progress_precommits"] for row in valid
        ),
        "agency_precommits": sum(
            row["goal_access_counts"]["agency_precommits"] for row in valid
        ),
        "admitted_pairs": sum(
            row["goal_access_counts"]["pairs_admitted"] for row in valid
        ),
        "operator_accepted": False,
        "scientific_validation": "not_performed",
        "scientific_status": "exploratory_access_ablation_only",
    }
    (root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0 if len(valid) == 4 else 2


if __name__ == "__main__":
    raise SystemExit(main())
