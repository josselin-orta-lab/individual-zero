#!/usr/bin/env python3
"""Read-only audit of capabilities on a REAL, newly born canonical I1.

This tool does not configure, execute, heal, reset or teach the individual.
An "active" capability is wired at birth, not proof that it will be exercised.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "individual-zero-i1-effective-birth-capabilities/v1"

# This is an explicit natural-I1 contract, not "enable every code path".
# Any intentional change to the default phenotype requires a reviewed edit.
EXPECTED = {
    "stage4.value_needs": "active",
    "stage4.goal_manager": "active",
    "stage4.competition": "active",
    "stage4.gatekeeper": "active",
    "stage5.temperament_projection": "active",
    "stage6.progressive_planning": "active",
    "stage7.episodic_memory": "active",
    "stage8.td_learning": "active",
    "stage9.causal_model": "active",
    "stage10.sleep_pressure": "conditional",
    "stage10.consolidation": "conditional",
    "stage11.exploration": "conditional",
    "stage11.global_modulation": "active",
    "stage11.geographic_exploration": "conditional",
    "stage11.local_threat_alerts": "active",
    "stage11.geographic_route_search": "disabled",
    "stage11.geographic_route_survey": "disabled",
    "stage11.instrumental_geographic_value": "disabled",
    "stage11.prospective_water_predictor": "disabled",
    "stage12.lived_diagnostics": "conditional",
    "stage12.subjective_goal_agency": "active",
    "stage12.dual_scope_agency": "active",
    "stage12.spatial_goal_progress": "active",
    "stage12.attribution_join": "disabled",
    "i1.unknown_affordance_consideration": "active",
    "i1.first_person_water_probing": "active",
    "i1.first_person_water_learning": "active",
    "i1.external_predictor": "disabled",
    "i1.external_lived_recall": "disabled",
    "i1.d2_movement_prudence": "disabled",
    "i1.private_consolidated_recall": "conditional",
    "i1.h1_h2_ablation": "disabled",
    "i1.toxic_berry_minus_10": "active",
    "world.mortal": "active",
    "world.operator_bench": "disabled",
    "world.hidden_evaluation_trace": "disabled",
}


def _mode(enabled: bool, conditional: bool = False) -> str:
    if not enabled:
        return "disabled"
    return "conditional" if conditional else "active"


def _stage4(stages):
    return stages.stage9.stage8.stage7.stage6.stage4


def _canonical(data) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def enforce_manifest(manifest, *, expected_competition=None):
    """Fail closed on any unexplained natural birth capability drift."""
    if manifest.get("schema") != SCHEMA:
        raise AssertionError("unknown capability manifest version")
    modes = manifest.get("capabilities")
    if not isinstance(modes, dict) or modes != EXPECTED:
        changed = {
            key: {"expected": EXPECTED.get(key), "actual": modes.get(key)}
            for key in sorted(set(EXPECTED) | set(modes or {}))
            if EXPECTED.get(key) != (modes or {}).get(key)
        }
        raise AssertionError("natural birth capability drift: " + str(changed))
    if set(manifest.get("stage_configs", {})) != {
        "4", "5", "6", "7", "8", "9", "10", "11", "12"
    }:
        raise AssertionError("incomplete Stage4-12 birth evidence")
    goal = manifest["effective_configuration"]["goal_manager"]
    if (goal["replacement_hysteresis"], goal["critical_pressure"]) != (.04, .35):
        raise AssertionError("natural GoalManager birth calibration is not 0.04/0.35")
    if manifest["effective_configuration"]["toxic_berry_integrity_delta"] != -10.0:
        raise AssertionError("natural toxic berry integrity is not -10")
    if expected_competition is not None:
        observed = manifest["effective_configuration"]["competition"]
        if (observed["base_threshold"], observed["gain"]) != (
            expected_competition["base_threshold"], expected_competition["gain"]
        ):
            raise AssertionError("competition candidate did not reach born owner")
    if not manifest["invariants"]["stage4_10_11_owner_consistency"]:
        raise AssertionError("different GoalManager/Competition/TD owners across stages")
    if not manifest["invariants"]["unique_causal_owner_ids"]:
        raise AssertionError("duplicate causal owner")
    if not manifest["invariants"]["unstarted_without_observer_effect"]:
        raise AssertionError("birth observer advanced or modified the individual")
    return manifest


def audit_birth(life, *, expected_competition=None):
    """Read actual born owners without advancing time, rewards or journal."""
    if (type(life).__name__ != "I1Runtime"
            or not type(life).__module__.startswith("i1lab.")):
        raise AssertionError("audit requires canonical generated I1Runtime")
    before = (
        life.scheduler.t_monde, life.journal.entry_count,
        dict(life.world.body.as_dict()),
        life.world.config.digest(),
    )
    s11, s10 = life._stage11_config, life._stage10_config
    s9, s8, s7, s6 = (life._stage9_config, life._stage8_config,
                        life._stage7_config, life._stage6_config)
    c4 = life._config
    c4_11 = _stage4(s11)
    c4_10 = _stage4(s10)
    goals = life.goal_manager._config
    competition = life.competition._config
    world = life.world.config
    geo = s11.geographic
    owner_ids = [owner.owner_id for owner in life.causal_owners]
    stages = {
        "4": c4.version,
        "5": "projected-in-stage11:" + s11.version,
        "6": s6.version,
        "7": s7.version,
        "8": s8.version,
        "9": s9.version,
        "10": s10.version,
        "11": s11.version,
        "12": life._stage12_detector_policy.version,
    }
    capabilities = {
        "stage4.value_needs": _mode(life.value_needs is not None),
        "stage4.goal_manager": _mode(life.goal_manager is not None),
        "stage4.competition": _mode(life.competition is not None),
        "stage4.gatekeeper": _mode(life.gatekeeper is not None),
        "stage5.temperament_projection": _mode(s11.temperament_parameters is not None),
        "stage6.progressive_planning": _mode(
            life.planning is not None and s6.planning.progressive_subgoals),
        "stage7.episodic_memory": _mode(life.memory is not None),
        "stage8.td_learning": _mode(life.q_active is not None),
        "stage9.causal_model": _mode(life.causal_model is not None),
        "stage10.sleep_pressure": _mode(
            life.sleep_health is not None and s10.sleep.fatigue_weight > 0,
            conditional=True),
        "stage10.consolidation": _mode(
            life.consolidation is not None and life.consolidation_scan is not None
            and s10.selection_policy is not None
            and s10.semantic_policy is not None, conditional=True),
        "stage11.exploration": _mode(life.exploration is not None, conditional=True),
        "stage11.global_modulation": _mode(life.modulation is not None),
        "stage11.geographic_exploration": _mode(
            geo is not None and life.exploration.geographic is not None,
            conditional=True),
        "stage11.local_threat_alerts": _mode(s11.local_threat_alerts),
        "stage11.geographic_route_search": _mode(s11.geographic_route_enabled),
        "stage11.geographic_route_survey": _mode(
            geo is not None and geo.observe_routes),
        "stage11.instrumental_geographic_value": _mode(
            s11.instrumental_geographic_value),
        "stage11.prospective_water_predictor": _mode(
            s11.prospective_water is not None
            and life.lived_water_predictor is not None),
        "stage12.lived_diagnostics": _mode(
            life._stage12_detectors is not None, conditional=True),
        "stage12.subjective_goal_agency": _mode(life._goal_agency_enabled),
        "stage12.dual_scope_agency": _mode(life._dual_scope_enabled),
        "stage12.spatial_goal_progress": _mode(life._spatial_goal_enabled),
        "stage12.attribution_join": _mode(life._attribution_join_enabled),
        "i1.unknown_affordance_consideration": _mode(
            life._i1_unknown_action_enabled),
        "i1.first_person_water_probing": _mode(life._i1_water_probe_enabled),
        "i1.first_person_water_learning": _mode(life._i1_water_learning_enabled),
        "i1.external_predictor": _mode(life._i1_enabled),
        "i1.external_lived_recall": _mode(life._i1_lived_recall_enabled),
        "i1.d2_movement_prudence": _mode(life._d2_prudence),
        "i1.private_consolidated_recall": _mode(
            "i1_private_procedure_recall" in c4.compute_budget.operation_costs,
            conditional=True),
        "i1.h1_h2_ablation": _mode(any(
            "I1A238" in cls.__name__ or "I1A239" in cls.__name__
            for cls in type(life).__mro__)),
        "i1.toxic_berry_minus_10": _mode(
            world.berry_effects["berry_b"].integrity_delta == -10.0),
        "world.mortal": _mode(
            life.stage3.substrate.mortal_status is not None),
        "world.operator_bench": _mode(life.stage3.substrate.bench is not None),
        "world.hidden_evaluation_trace": _mode(
            life.stage3.substrate.evaluation_trace is not None),
    }
    owner_consistency = (
        goals == c4.goals == c4_11.goals == c4_10.goals
        and competition == c4.competition == c4_11.competition
        == c4_10.competition
        and s8.td == s11.stage9.stage8.td == s10.stage9.stage8.td
        and life.value_needs.config == c4.value_needs
    )
    manifest = {
        "schema": SCHEMA,
        "individual_id": life.individual_id,
        "runtime_class": type(life).__module__ + "." + type(life).__name__,
        "stage_configs": stages,
        "capabilities": capabilities,
        "effective_configuration": {
            "goal_manager": {
                "version": goals.version,
                "replacement_hysteresis": goals.replacement_hysteresis,
                "critical_pressure": goals.critical_pressure,
            },
            "competition": {
                "version": competition.version,
                "base_threshold": competition.base_threshold,
                "gain": competition.gain,
            },
            "td_version": s8.td.version,
            "sleep_version": s10.sleep.version,
            "consolidation_policy_version": (
                None if s10.semantic_policy is None
                else s10.semantic_policy.version),
            "world_physics_version": world.version,
            "world_physics_digest": world.digest(),
            "toxic_berry_integrity_delta": (
                world.berry_effects["berry_b"].integrity_delta),
        },
        "causal_owner_ids": sorted(owner_ids),
        "invariants": {
            "stage4_10_11_owner_consistency": owner_consistency,
            "unique_causal_owner_ids": len(owner_ids) == len(set(owner_ids)),
            "unstarted_without_observer_effect": False,
        },
    }
    after = (
        life.scheduler.t_monde, life.journal.entry_count,
        dict(life.world.body.as_dict()),
        life.world.config.digest(),
    )
    manifest["invariants"]["unstarted_without_observer_effect"] = (
        before == after and life.scheduler.t_monde == 0
    )
    enforce_manifest(manifest, expected_competition=expected_competition)
    manifest["birth_profile_sha256"] = sha256(_canonical(manifest)).hexdigest()
    return manifest


def run_cli(*, preset, output):
    # Build a disposable I1 module; never modify an installed or born actor.
    sys.path[:0] = [
        str(ROOT / "tools"), str(ROOT / "scripts"), str(ROOT / "src")
    ]
    from build_i1_fork import generate
    from run_i1_world_preset import load_preset, _birth_parameters
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("refusing to overwrite a prior birth audit")
    with TemporaryDirectory(prefix="i1-birth-capability-audit-") as scratch:
        workspace = Path(scratch)
        generated = workspace / "generated"
        generate(generated)
        sys.path.insert(0, str(generated))
        from i1lab.i1_birth import birth_i1
        world, world_sha = load_preset(preset)
        params, _ = _birth_parameters(world)
        life = birth_i1(
            life_id="i1:audit:" + preset + ":20261018",
            wal_path=str(workspace / "unstarted.wal"), **params,
        )
        manifest = audit_birth(life)
        manifest["environment"] = {"preset": preset, "sha256": world_sha}
        git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                             check=False, capture_output=True, text=True)
        manifest["git_sha"] = git.stdout.strip() if git.returncode == 0 else None
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + chr(10),
                      encoding="utf-8")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preset", choices=("oasis", "foraging"), required=True)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    value = run_cli(preset=a.preset, output=a.output)
    print(json.dumps({"status": "PASS", "sha256": value["birth_profile_sha256"],
                      "preset": a.preset, "stages": sorted(value["stage_configs"]),
                      "capabilities": value["capabilities"]}, sort_keys=True))
