#!/usr/bin/env python3
"""Population research: frozen prenatal curiosity, natural I1, no in-life control.

The native arm is a completely unmodified birth. Other arms differ ONLY in
versioned Stage11 intrinsic scaling and local geographic novelty at birth.
No commands, prior resource maps, body physics or TD reward are injected.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "scripts"), str(ROOT / "src")]
from build_i1_fork import generate
from run_i1_world_preset import load_preset, _birth_parameters
from audit_i1_birth_capabilities import audit_birth

# Intentional bounded hypotheses, rather than selecting the best old seed.
# Candidate 0 is the actual untouched main constructor, NOT a synthetic copy.
PROFILES = (
    None,
    (0.20, 0.35),
    (0.30, 0.35),
    (0.20, 0.55),
    (0.30, 0.55),
    (0.45, 0.55),
)
LOW_PROFILES = (
    None,
    (0.08, 0.35),
    (0.15, 0.20),
    (0.08, 0.20),
)
WORLDS = ("oasis", "foraging", "dry-valley", "blocked-route")
POLICY = "i1-post314-spatial-natural-population-v1"


def configure_before_birth(params, candidate, *, profiles=PROFILES, policy=POLICY):
    """Return only frozen prenatal config, with canonical I1 flags untouched."""
    if type(candidate) is not int or candidate not in range(len(profiles)):
        raise ValueError("unregistered curiosity profile")
    if candidate == 0:
        return params
    from i1lab.i1_natural_runtime import GeographicExplorationConfig

    novelty, weight = profiles[candidate]
    if not (0.0 < novelty <= 1.0 and 0.0 < weight <= 1.0):
        raise ValueError("out-of-bounds exploratory configuration")
    original = params["stage11_config"]
    if original.geographic is not None:
        raise ValueError("expects unmodified reference birth input")
    # Match the exact same booleans, geometry/UC guards and capacity that the
    # default constructor installs. Only curiosity magnitude differs.
    geo = GeographicExplorationConfig(
        version="i1-firstperson-frontier-v1+" + policy + ":" + str(candidate),
        novelty_weight=novelty,
        max_distinct_sites=1024,
        max_targets_per_cycle=1,
        observe_routes=True,
        refresh_surveys=True,
        remember_entities=True,
        max_place_candidates=3,
    )
    configured = replace(
        original, version=original.version + "+" + policy + ":" + str(candidate),
        geographic=geo, intrinsic_weight=weight,
        local_threat_alerts=True,
        geographic_capacity_guard_enabled=True,
        geographic_route_enabled=True,
    )
    configured.validate()
    return {**params, "stage11_config": configured}


def study_one(*, candidate, world, seed, steps, out, study="initial"):
    if (study not in ("initial", "lowcuriosity")
            or type(candidate) is not int
            or candidate not in range(len(PROFILES if study == "initial" else LOW_PROFILES))
            or world not in WORLDS or type(seed) is not int
            or type(steps) is not int or not 1 <= steps <= 1000):
        raise ValueError("unregistered prospective study arm")
    profiles = PROFILES if study == "initial" else LOW_PROFILES
    policy = POLICY if study == "initial" else "i1-post314-low-curiosity-prenatal-v1"
    out = Path(out).resolve()
    if out.exists():
        raise FileExistsError("never overwrite a mortal life's evidence")
    out.mkdir(parents=True)
    source_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    report = {
        "status": "TECHNICAL_FAILURE", "scientific_verdict": "NOT_EVALUATED",
        "study": study,
        "source_sha": source_sha, "candidate": candidate, "world": world,
        "seed": seed, "steps_requested": steps,
        "prenatal_profile": (
            {"native_unchanged": True} if candidate == 0
            else {"geographic_novelty": profiles[candidate][0],
                  "stage11_intrinsic_weight": profiles[candidate][1]}
        ),
    }
    try:
        with TemporaryDirectory(prefix="i1-geographic-population-") as tmp:
            built = Path(tmp) / "generated"
            generate(built)
            sys.path.insert(0, str(built))
            from i1lab.i1_birth import birth_i1
            from i1lab.journal import HashChainedJournal

            preset, preset_sha = load_preset(world)
            params, _ = _birth_parameters(preset)
            native_physics = params["world_config"].digest()
            params = configure_before_birth(
                params, candidate, profiles=profiles, policy=policy)
            # Same identity within a paired world/seed set = same temperament.
            # Distinct process and unique WAL = no memory/history sharing.
            life_id = f"i1:geo-population:{world}:{seed}"
            wal = out / "life.wal"
            life = birth_i1(life_id=life_id, wal_path=str(wal), **params)
            born = audit_birth(life, expected_competition={
                "base_threshold": 0.5, "gain": 1.0,
            })
            geo = life._stage11_config.geographic
            if (geo is None or not geo.remember_entities or not geo.observe_routes
                    or not life._stage11_config.geographic_route_enabled):
                raise AssertionError("corrected natural I1 spatial capability disabled")
            expected_geo = 0.15 if candidate == 0 else profiles[candidate][0]
            expected_weight = 0.35 if candidate == 0 else profiles[candidate][1]
            if (geo.novelty_weight != expected_geo
                    or life._stage11_config.intrinsic_weight != expected_weight):
                raise AssertionError("effective exploratory birth differs from arm")
            if (life.world.config.digest() != born["effective_configuration"]["world_physics_digest"]
                    or life._stage8_config.td.version != born["effective_configuration"]["td_version"]):
                raise AssertionError("unverified birth physics/TD")
            cfg_geo = geo
            cfg_comp = life.competition._config
            cfg_goals = life.goal_manager._config
            cfg_td = life._stage8_config.td
            physics = life.world.config.digest()
            trace = []
            actions = Counter()
            applied = Counter()
            cumulative_shortage = 0.0
            for _ in range(steps):
                decision = life.run_step()
                body = dict(life.world.telemetry())
                if life.world.config.digest() != physics:
                    raise AssertionError("body physics changed within life")
                if (life._stage11_config.geographic is not cfg_geo
                        or life.competition._config is not cfg_comp
                        or life.goal_manager._config is not cfg_goals
                        or life._stage8_config.td is not cfg_td):
                    raise AssertionError("an owner was modified during life")
                action = decision.command_primitive or "NO_COMMAND"
                actions[action] += 1
                if decision.execution_status == "applied":
                    applied[action] += 1
                shortage = sum(
                    (100.0 - max(0.0, min(100.0, float(body[k])))) / 100.0
                    for k in ("water", "food", "energy", "integrity")
                ) / 4.0
                cumulative_shortage += shortage
                goal = life.goal_manager.active_goal
                trace.append({
                    "step": life.scheduler.t_monde, "body": body,
                    "action": action, "execution": decision.execution_status,
                    "goal": None if goal is None else goal.goal_type,
                    "journal_head": life.journal.head_hash,
                })
                if decision.execution_status == "dead":
                    break
            if not life.journal.verify():
                raise AssertionError("living causal journal mismatch")
            audit = HashChainedJournal.audit_durable_wal(str(wal))
            if audit["head_hash"] != life.journal.head_hash:
                raise AssertionError("durable WAL fails final hash attestation")
            # Read-only independent verifier for the sealed WAL, preserving
            # distinction between recall, proposed options and physical acts.
            from audit_i1_spatial_navigation_314 import audit as audit_spatial
            spatial = audit_spatial(wal)
            if (not spatial["independent_hash_chain_verified"]
                    or spatial["journal_head"] != audit["head_hash"]
                    or spatial["journal_entries"] != audit["verified_entries"]):
                raise AssertionError("spatial WAL attestation mismatch")
            n = len(trace)
            avg_shortage = cumulative_shortage / n
            score = 0.7 * (n / steps) + 0.3 * (1 - avg_shortage)
            report.update({
                "status": "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT",
                "individual_id": life_id, "world_sha256": preset_sha,
                "world_config_digest_before_birth": native_physics,
                "physics_digest": physics,
                "birth_capability_sha256": born["birth_profile_sha256"],
                "birth_capability_manifest": born,
                "effective_geographic_novelty": geo.novelty_weight,
                "effective_stage11_intrinsic_weight": life._stage11_config.intrinsic_weight,
                "effective_competition": {"threshold": cfg_comp.base_threshold,
                                           "gain": cfg_comp.gain},
                "effective_td": {"version": cfg_td.version, "lambda_e": cfg_td.lambda_e},
                "effective_sleep_version": life._stage10_config.sleep.version,
                "memory_sightings_final": len(life.exploration.geographic.place_memories),
                "observed_route_surveys_final": len(life.exploration.geographic.surveys),
                "goal_version": cfg_goals.version,
                "observed_steps": n,
                "lifecycle": life.stage3.substrate.mortal_status.value,
                "actions": dict(actions),
                "applied_actions": dict(applied),
                "zero_steps": {k:sum(t["body"][k] <= 0 for t in trace)
                               for k in ("water","food","energy")},
                "mean_shortage": round(avg_shortage, 9),
                "external_score": round(score, 9),
                "spatial_wal_audit": spatial,
                "wal_head": audit["head_hash"],
                "wal_entries": audit["verified_entries"],
                "trajectory": trace,
            })
    finally:
        (out / "report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--study", choices=("initial", "lowcuriosity"), default="initial")
    p.add_argument("--candidate", required=True, type=int)
    p.add_argument("--world", required=True, choices=WORLDS)
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--steps", required=True, type=int)
    p.add_argument("--output-dir", required=True, type=Path)
    a = p.parse_args()
    value = study_one(candidate=a.candidate, world=a.world,
                      seed=a.seed, steps=a.steps, out=a.output_dir, study=a.study)
    print(json.dumps({k: value[k] for k in (
        "status", "study", "candidate", "world", "seed",
        "observed_steps", "lifecycle", "actions",
        "zero_steps", "external_score",
    )}, sort_keys=True))


if __name__ == "__main__":
    main()
