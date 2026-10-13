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
    verified = [
        life for life in lives
        if not life.get("audit_error") and "error" not in life
        and life.get("audits")
    ]
    summary = {
        "schema": "issue110-contrasted-ga-summary-v1",
        "source_sha": source_sha, "planned_lives": 12,
        "independently_audited_lives": len(verified),
        "total_actual_applied_steps": sum(
            life.get("applied_steps", 0) for life in lives
        ),
        "audited_actual_applied_steps": sum(
            life["applied_steps"] for life in verified
        ),
        "verified_successes": sum(
            life["audits"]["goal"]["verified_strict_gains"] for life in verified
        ),
        "verified_failures": sum(
            life["audits"]["goal"]["verified_no_gains"] for life in verified
        ),
        "agency_self": sum(
            life["audits"]["first_person"]["judgements_self"] for life in verified
        ),
        "agency_world": sum(
            life["audits"]["first_person"]["judgements_world"] for life in verified
        ),
        "agency_unknown": sum(
            life["audits"]["first_person"]["judgements_unknown"] for life in verified
        ),
        "admitted_pairs": sum(
            life["audits"]["pairs"]["admitted_pairs"] for life in verified
        ),
        "applied_pairs": sum(
            life["audits"]["pairs"]["applied_pairs"] for life in verified
        ),
        "operator_accepted": False,
        "scientific_validation": "not_performed",
        "scientific_status": "exploratory_only_no_general_claim",
    }
    (root / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0 if len(verified) == 12 else 2


if __name__ == "__main__":
    raise SystemExit(main())
