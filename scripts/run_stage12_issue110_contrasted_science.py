"""Preregistered issue-110 GA contrasted 12-life physical experiment.

See docs/research/stage12-issue110-ga-contrasted-prereg-2026-10-13.fr.md.
This runner does not decide whether any autonomous belief is correct.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_runtime import Stage12Runtime
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_diagnostic_audit import audit_stage12_diagnostics
from lab.world import Position

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ("path_obstructed", "reference", "water_available")
WATERS = (20.0, 35.0)
SLEEP = ("awake_ablation", "sleep_reference")
STEPS = 50


def run_life(directory: Path, *, world: str, water: float, sleep_profile: str) -> dict:
    baseline11 = build_stage11_reference_runtime(
        enable_geography=True, autonomous_mortal=True,
    )
    baseline10 = build_stage10_reference_runtime(autonomous_mortal=True)
    config = replace(
        baseline11.world.config,
        version="stage12-issue110-contrasted-physical-v1",
        initial_body=replace(baseline11.world.config.initial_body, water=water),
    )
    layout = baseline11.world._layout
    if world == "water_available":
        layout = replace(
            layout,
            water_sources=layout.water_sources | frozenset({Position(2, 2)}),
            resources=layout.resources + ((Position(2, 2), "berry_a", 2),),
        )
    elif world == "path_obstructed":
        layout = replace(
            layout, obstacles=layout.obstacles | frozenset({Position(3, 2)}),
        )
    elif world != "reference":
        raise ValueError("unregistered physical world")
    layout.validate(config)
    sleep = baseline10._stage10_config.sleep
    if sleep_profile == "awake_ablation":
        sleep = replace(
            sleep, fatigue_gain=0.0, night_weight=0.0,
            consolidation_weight=0.0,
        )
    elif sleep_profile != "sleep_reference":
        raise ValueError("unregistered sleep profile")
    combined = replace(
        baseline10._stage10_config,
        stage9=baseline11._stage11_config.stage9,
        sleep=sleep,
    )
    life = Stage12Runtime(
        world_config=config, layout=layout,
        safety_config=baseline11.stage3.substrate.safety._config,
        safety_facts=baseline11._canonical_safety._innate,
        protected_integrity_threshold=(
            baseline11.stage3.control._config.protected_integrity_threshold
        ),
        stage11_config=baseline11._stage11_config,
        stage10_config=combined,
        equipment=baseline11.equipment, autonomous_mortal=True,
        wal_path=str(directory / "life.wal"),
        subjective_goal_agency=True, goal_agency_cost_uc=1,
        attribution_join=True, attribution_join_cost_uc=1,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-issue110-ga-contrasted-v1",
            window=12, stagnation_steps=4, stagnation_tolerance=0.05,
            loop_repetitions=3, loop_max_period=2,
            entropy_min_samples=4, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )
    Stage12OperatorConsole(
        substrate=life.stage3.substrate, mode="campaign",
        policy_version="issue110-contrasted-external-stop-v1",
        maximum_world_steps=STEPS,
    )
    actions = Counter()
    failure = None
    for _ in range(STEPS):
        try:
            result = life.run_step()
            if result.execution_status != "applied":
                failure = "nonapplied:" + result.execution_status
                break
            actions[result.command_primitive] += 1
        except Exception as exc:
            failure = type(exc).__name__ + ": " + str(exc)
            break
    raw = life.journal.canonical_bytes()
    (directory / "canonical.jsonl").write_bytes(raw)
    anchors = dict(
        expected_head=life.journal.head_hash,
        expected_count=len(life.journal.entries),
    )
    audit_error = None
    reports = {}
    try:
        durable = HashChainedJournal.audit_durable_wal(
            str(directory / "life.wal"),
        )
        if (durable["head_hash"] != anchors["expected_head"]
                or durable["verified_entries"] != anchors["expected_count"]):
            raise ValueError("durable WAL disagrees with canonical export")
        if not life.journal.verify():
            raise ValueError("invalid internal life journal")
        base = audit_export_bytes(raw, **anchors)
        if base.world_steps_closed != sum(actions.values()):
            raise ValueError("closed world steps differ from applied actions")
        goal = audit_stage12_goal_progress(raw, **anchors)
        agency = audit_stage12_first_person_agency(raw, **anchors)
        pairs = audit_stage12_attribution_pairs(raw, **anchors)
        diag = audit_stage12_diagnostics(raw, **anchors)
        labels = Counter(
            "unavailable" if label is None else label
            for _, label in pairs.diagnostic_labels
        )
        reports = {
            "journal": base.as_dict(),
            "goal": goal.as_dict(),
            "first_person": agency.as_dict(),
            "pairs": pairs.as_dict(),
            "diagnostics": diag.as_dict(),
            "attribution_diagnostic_labels": dict(sorted(labels.items())),
        }
    except Exception as exc:
        audit_error = type(exc).__name__ + ": " + str(exc)
    result = {
        "schema": "issue110-contrasted-ga-physical-v1",
        "world": world, "initial_water": water,
        "sleep_profile": sleep_profile,
        "world_sha256": sha256_hex(canonical_causal_bytes(config.as_dict())),
        "layout_sha256": sha256_hex(canonical_causal_bytes(layout.as_dict())),
        "requested_steps": STEPS, "applied_steps": sum(actions.values()),
        "mortal_status": life.stage3.substrate.mortal_status.value,
        "actions": dict(sorted(actions.items())),
        "journal_sha256": sha256(raw).hexdigest(),
        "head_hash": anchors["expected_head"],
        "occurrences": anchors["expected_count"],
        "failure": failure, "audit_error": audit_error,
        "audits": reports,
        "operator_accepted": False,
        "scientific_validated": False,
        "physical_truth_independently_verified": False,
    }
    (directory / "life-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )
    return result


def summarize_lives(lives: list[dict], *, source_sha: str) -> dict:
    """Summarize exact *public audit report schema*, not Python dataclass names.

    Reject missing/invalid audit keys: a malformed report must not be counted
    as zero scientific evidence. The on-disk index keeps every failed life.
    """
    audited = [
        life for life in lives
        if life.get("audit_error") is None and "error" not in life
        and bool(life.get("audits"))
    ]
    expected_schemas = {
        "goal": "stage12-independent-goal-progress-audit-v1",
        "first_person": "stage12-first-person-independent-technical-audit-v1",
        "pairs": "stage12-independent-outcome-agency-pair-audit-v1",
    }
    for life in audited:
        for section, schema in expected_schemas.items():
            data = life["audits"].get(section)
            if not isinstance(data, dict) or data.get("schema") != schema:
                raise ValueError("unexpected issue110 " + section + " audit schema")
    def count(section: str, key: str) -> int:
        values = []
        for life in audited:
            value = life["audits"][section].get(key)
            if type(value) is not int or value < 0:
                raise ValueError(f"missing or invalid {section}.{key} audit counter")
            values.append(value)
        return sum(values)

    labels: Counter[str] = Counter()
    for life in audited:
        for row in life["audits"]["pairs"].get("diagnostic_labels", []):
            if not isinstance(row, dict) or row.get("attribution_bias") not in (
                None, "self_serving_pattern", "self_blame_pattern",
                "no_detected_pattern",
            ):
                raise ValueError("unexpected first-person diagnostic label")
            name = "unavailable" if row["attribution_bias"] is None else row["attribution_bias"]
            labels[name] += 1

    total_steps = sum(life.get("applied_steps", 0) for life in lives)
    pairs = count("pairs", "applied_pairs")
    return {
        "schema": "issue110-contrasted-ga-summary-v2",
        "source_sha": source_sha, "planned_lives": len(WORLDS) * len(WATERS) * len(SLEEP),
        "completed_lives": len(lives),
        "independently_audited_lives": len(audited),
        "failed_or_unaudited_lives": len(lives) - len(audited),
        "total_actual_applied_steps": total_steps,
        "audited_actual_applied_steps": sum(life["applied_steps"] for life in audited),
        "lives_with_fewer_than_50_steps": sum(
            life.get("applied_steps", 0) < STEPS for life in lives
        ),
        "goal_preregistered": count("goal", "preregistered_one_step_criteria"),
        "verified_successes": count("goal", "verified_one_step_resource_gains"),
        "verified_failures": count("goal", "verified_one_step_no_gains"),
        "unknown_goal_outcomes": count("goal", "unavailable_next_step_observations"),
        "unresolved_goal_outcomes_at_terminal": count("goal", "unresolved_at_terminal"),
        "agency_precommits": count("first_person", "precommits"),
        "agency_self": count("first_person", "judgements_self"),
        "agency_world": count("first_person", "judgements_world"),
        "agency_unknown": count("first_person", "judgements_unknown"),
        "agency_unavailable": count("first_person", "unavailable"),
        "agency_pending_at_terminal": count("first_person", "pending_terminal"),
        "agency_uc_charged": count("first_person", "charged_uc"),
        "agency_uc_refused": count("first_person", "refused_uc"),
        "admitted_pairs": count("pairs", "admitted_pairs"),
        "applied_pairs": pairs,
        "applied_successes": count("pairs", "applied_successes"),
        "applied_failures": count("pairs", "applied_failures"),
        "applied_self": count("pairs", "applied_self"),
        "applied_world": count("pairs", "applied_world"),
        "missed_pairs": count("pairs", "missed_pairs"),
        "join_uc_charged": count("pairs", "join_uc"),
        "join_uc_refused": count("pairs", "rejected_join_uc"),
        "diagnostic_labels": dict(sorted(labels.items())),
        "operator_accepted": False,
        "scientific_validation": "not_performed",
        "scientific_status": (
            "inconclusive_no_admissible_pairs" if pairs == 0
            else "exploratory_pairs_observed_final_validation_pending"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=False)
    source_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    lives = []
    for world in WORLDS:
        for water in WATERS:
            for sleep in SLEEP:
                label = f"{world}-water{int(water)}-{sleep}"
                folder = root / label
                folder.mkdir()
                try:
                    lives.append(run_life(
                        folder, world=world, water=water,
                        sleep_profile=sleep,
                    ))
                except BaseException as exc:
                    record = {
                        "world": world, "initial_water": water,
                        "sleep_profile": sleep, "applied_steps": 0,
                        "error": type(exc).__name__ + ": " + str(exc),
                    }
                    lives.append(record)
                    (folder / "runner-error.json").write_text(
                        json.dumps(record, indent=2) + "\n",
                    )
                (root / "index.json").write_text(json.dumps({
                    "source_sha": source_sha,
                    "preregistration": "docs/research/stage12-issue110-ga-contrasted-prereg-2026-10-13.fr.md",
                    "completed_lives": len(lives),
                    "planned_lives": 12,
                    "lives": lives,
                }, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
    summary = summarize_lives(lives, source_sha=source_sha)
    (root / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["independently_audited_lives"] == 12 else 2


if __name__ == "__main__":
    raise SystemExit(main())
