"""Prospectively locked GA-08 autonomous free/blocked/absent spatial trials.

No forced choice. Prebirth Equipment observations come from a DIFFERENT
WorldBody, and never confer agency labels on the born individual.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.equipment import train_exact_transition_table
from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_runtime import Stage12Runtime
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_diagnostic_audit import audit_stage12_diagnostics
from lab.stage12_spatial_provenance_audit import audit_stage12_spatial_provenance
from lab.world import WorldBody, Position, BerryEffect

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "stage12-ga08-autonomous-physical-6life-prereg-v1"
PREREG = "docs/research/stage12-issue110-ga08-spatial-prereg-2026-10-14.fr.md"
CASES = ("water_free", "water_blocked", "water_absent",
         "food_free", "food_blocked", "food_absent")
MAX_STEPS = 50


def prebirth_equipment(config, layout, *, kind: str, label: str):
    """Laboratory training *before birth*: no oracle labels or live edits."""
    world = WorldBody(config=config, layout=layout)
    recorder = EquipmentCorpusRecorder(
        corpus_version="stage12-ga08-physical-prebirth-" + label + "-v1",
    )
    commands = [("movement_free", PrimitiveCommand(
        "se_deplacer", {"direction": "east"}
    ))]
    if kind == "water":
        commands.append(("drinking", PrimitiveCommand("boire")))
    else:
        commands.extend((
            ("collection_without_tool", PrimitiveCommand(
                "collecter", {"target": "berry_a"}
            )),
            ("resource_consumption", PrimitiveCommand(
                "manger", {"target": "berry_a"}
            )),
        ))
    for t, (family, command) in enumerate(commands, 1):
        recorder.record_transition(
            world=world, t_monde=t, family=family, command=command,
        )
    return train_exact_transition_table(
        corpus=recorder.build(),
        equipment_version="E-stage12-ga08-prebirth-" + label + "-v1",
    )


def run_life(folder: Path, *, label: str) -> dict:
    if label not in CASES:
        raise ValueError("unregistered GA08 spatial context")
    kind, condition = label.split("_")
    blocked = condition == "blocked"
    exists = condition != "absent"
    baseline11 = build_stage11_reference_runtime(
        enable_geography=True, autonomous_mortal=True,
    )
    baseline10 = build_stage10_reference_runtime(autonomous_mortal=True)
    old_config = baseline11.world.config
    config = replace(
        old_config, version="stage12-ga08-physical-" + label + "-v1",
        initial_body=replace(
            old_config.initial_body,
            energy=50.0, integrity=100.0,
            food=35.0 if kind == "food" else 75.0,
            water=20.0 if kind == "water" else 75.0,
        ),
        berry_effects={
            **old_config.berry_effects,
            "berry_a": BerryEffect(food_gain=30.0, integrity_delta=0.0),
        },
    )
    target = Position(3, 2)
    layout = replace(
        baseline11.world._layout,
        obstacles=frozenset({target}) if blocked else frozenset(),
        water_sources=(frozenset({target})
                       if exists and kind == "water" else frozenset()),
        resources=(((target, "berry_a", 2),)
                   if exists and kind == "food" else ()),
        creatures=frozenset(), danger_zones=frozenset(),
        lethal_zones=frozenset(),
    )
    layout.validate(config)
    sleep = replace(
        baseline10._stage10_config.sleep,
        version="stage12-ga08-physical-sleep-dev-v1",
        consolidation_weight=0.0,
    )
    stage11 = baseline11._stage11_config
    c9 = stage11.stage9
    c8 = c9.stage8
    c7 = c8.stage7
    c6 = c7.stage6
    stage6 = replace(
        c6,
        simulator=replace(c6.simulator, h_max=3,
                          version="stage12-ga08-physical-sim-v1"),
        planning=replace(c6.planning, max_depth=3,
                         version="stage12-ga08-physical-plan-v1"),
        evaluation=replace(c6.evaluation, h_eff=3,
                           version="stage12-ga08-physical-eval-v1"),
    )
    stage11 = replace(stage11, stage9=replace(
        c9, stage8=replace(c8, stage7=replace(c7, stage6=stage6)),
    ))
    combined = replace(
        baseline10._stage10_config,
        stage9=stage11.stage9, sleep=sleep,
    )
    equipment = prebirth_equipment(config, layout, kind=kind, label=label)
    life = Stage12Runtime(
        world_config=config, layout=layout,
        safety_config=baseline11.stage3.substrate.safety._config,
        safety_facts=baseline11._canonical_safety._innate,
        protected_integrity_threshold=(
            baseline11.stage3.control._config.protected_integrity_threshold
        ),
        stage11_config=stage11, stage10_config=combined,
        equipment=equipment, autonomous_mortal=True,
        wal_path=str(folder / "life.wal"),
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        subjective_goal_agency=True, goal_agency_cost_uc=1,
        attribution_join=True, attribution_join_cost_uc=1,
        spatial_goal_agency=True, spatial_progress_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-ga08-physical-detection-prereg-v1",
            window=12, stagnation_steps=4, stagnation_tolerance=0.05,
            loop_repetitions=3, loop_max_period=2,
            entropy_min_samples=4, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )
    Stage12OperatorConsole(
        substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-ga08-operator-50-v1",
        maximum_world_steps=MAX_STEPS,
    )
    actions = Counter()
    technical_failure = None
    for _ in range(MAX_STEPS):
        try:
            result = life.run_step()
            if result.execution_status != "applied":
                technical_failure = "not_applied:" + result.execution_status
                break
            actions[result.command_primitive] += 1
        except Exception as exc:
            technical_failure = type(exc).__name__ + ": " + str(exc)
            break
    raw = life.journal.canonical_bytes()
    (folder / "canonical.jsonl").write_bytes(raw)
    anchor = {
        "expected_head": life.journal.head_hash,
        "expected_count": len(life.journal.entries),
    }
    audit_error = None
    analyses = {}
    try:
        durable = HashChainedJournal.audit_durable_wal(
            str(folder / "life.wal")
        )
        if (durable["head_hash"] != anchor["expected_head"]
                or durable["verified_entries"] != anchor["expected_count"]):
            raise ValueError("M11 WAL differs from canonical RAM ledger")
        if not life.journal.verify():
            raise ValueError("bad immutable causal journal")
        base = audit_export_bytes(raw, **anchor)
        if base.world_steps_closed != sum(actions.values()):
            raise ValueError("physical step accounting inconsistent")
        spatial = audit_stage12_spatial_provenance(raw, **anchor)
        goal = audit_stage12_goal_progress(raw, **anchor)
        agency = audit_stage12_first_person_agency(raw, **anchor)
        pairs = audit_stage12_attribution_pairs(raw, **anchor)
        diagnostic = audit_stage12_diagnostics(raw, **anchor)
        analyses = {
            "spatial": spatial.as_dict(),
            "goal": goal.as_dict(),
            "agency": agency.as_dict(),
            "pairs": pairs.as_dict(),
            "diagnostics": diagnostic.as_dict(),
            "physical_steps_closed": base.world_steps_closed,
            "perceptual_events": sum(
                e.causal_event["kind"] == "perceptual_capture"
                for e in life.journal.entries
            ),
            "planning_proposals": sum(
                e.causal_event.get("kind") == "stage6_planning_result"
                and e.causal_event.get("data", {}).get("proposal_ref") is not None
                for e in life.journal.entries
            ),
        }
    except Exception as exc:
        audit_error = type(exc).__name__ + ": " + str(exc)
    row = {
        "schema": PROTOCOL,
        "case": label, "target_kind": kind, "target_visible": exists,
        "destination_blocked": blocked,
        "physical_steps": sum(actions.values()),
        "actions": dict(sorted(actions.items())),
        "failure": technical_failure,
        "audit_error": audit_error,
        "mortal_status": life.stage3.substrate.mortal_status.value,
        "journal_sha256": sha256(raw).hexdigest(),
        "head_hash": anchor["expected_head"],
        "occurrences": anchor["expected_count"],
        "world_sha256": sha256_hex(canonical_causal_bytes(config.as_dict())),
        "layout_sha256": sha256_hex(canonical_causal_bytes(layout.as_dict())),
        "equipment_sha256": equipment.artifact_digest,
        "audits": analyses,
        "operator_accepted": False,
        "scientific_status": "exploratory_only_not_validated",
    }
    (folder / "life-result.json").write_text(
        json.dumps(row, indent=2, sort_keys=True) + "\n",
    )
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    code_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    rows = []
    for label in CASES:
        folder = root / label
        folder.mkdir()
        try:
            row = run_life(folder, label=label)
        except BaseException as exc:
            row = {
                "case": label, "failure": type(exc).__name__ + ": " + str(exc),
                "audit_error": "runner_interrupted",
                "physical_steps": 0,
            }
            (folder / "runner-error.json").write_text(
                json.dumps(row, indent=2, sort_keys=True) + "\n",
            )
        rows.append(row)
        (root / "index.json").write_text(
            json.dumps({
                "schema": PROTOCOL, "source_sha": code_sha,
                "preregistration": PREREG, "planned_lives": len(CASES),
                "completed_lives": len(rows), "lives": rows,
                "scientific_validation": "not_performed",
                "operator_accepted": False,
            }, indent=2, sort_keys=True) + "\n",
        )
    valid = [r for r in rows if (
        r.get("audit_error") is None and r.get("failure") is None
        and bool(r.get("audits"))
    )]
    def count(section, key):
        return sum(r["audits"][section][key] for r in valid)
    summary = {
        "schema": PROTOCOL, "source_sha": code_sha,
        "preregistration": PREREG,
        "planned_lives": len(CASES), "audited_lives": len(valid),
        "failed_or_unverified_lives": len(CASES) - len(valid),
        "physical_steps": sum(r["physical_steps"] for r in valid),
        "spatial_preregistered": count("spatial", "preregistered"),
        "spatial_successes": count("spatial", "verified_successes"),
        "spatial_failures": count("spatial", "verified_failures"),
        "spatial_unknown": count("spatial", "unknown_outcomes"),
        "agency_self": count("spatial", "judgements_self"),
        "agency_world": count("spatial", "judgements_world"),
        "agency_unknown": count("spatial", "judgements_unknown"),
        "agency_uc": count("spatial", "charged_agency_uc"),
        "pairs_admitted": count("pairs", "admitted_pairs"),
        "pairs_applied": count("pairs", "applied_pairs"),
        "bias_labels": dict(Counter(
            str(record["attribution_bias"])
            for r in valid for record in r["audits"]["pairs"]["diagnostic_labels"]
        )),
        "operator_accepted": False,
        "scientific_validation": "not_performed",
        "scientific_status": "exploratory_no_general_causality_claim",
    }
    (root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
    )
    print("issue110_ga08_physical_summary=" + json.dumps(summary, sort_keys=True))
    return 0 if len(valid) == len(CASES) else 2


if __name__ == "__main__":
    raise SystemExit(main())
