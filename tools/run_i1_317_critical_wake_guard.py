#!/usr/bin/env python3
"""Issue 317/292: paired *operator-only* test of critical-body sleep arbitration.

Ordinary I1 already WAKES at <= food10, water15, integrity25. Its waking
Competition may immediately choose sleep again. The research arm only removes
the *intrinsic* sleep bonus while a current first-person capture witnesses
water, food or integrity <=10 on the actual body scale (0..100). Learned
Q(dormir), intrinsic fatigue owner state, memory, world, rewards, physics,
Competition thresholds, Action Control and actual wake rules are untouched.

This is a falsification experiment, not a new production coma policy, not an
ordered move/drink/eat, not proof of long-term biological safety.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
CRITICAL = ("water", "food", "integrity")
EXPERIMENTAL_LIMIT = 10.0
PREDECLARED_WORLDS = ("oasis", "foraging", "memory-corridor")
PREDECLARED_SEEDS = (9601, 9631)
HORIZON = 300


def witnessed_critical_channels(body: Mapping[str, float],
                                threshold: float = EXPERIMENTAL_LIMIT):
    """Only direct body telemetry, no inferred resource nor world knowledge."""
    if (not isinstance(body, Mapping)
        or type(threshold) not in (int, float)
        or not isfinite(threshold) or not 0 < threshold <= 100):
        raise ValueError("invalid first-person critical observation")
    for name in (*CRITICAL, "energy"):
        value = body.get(name)
        if (type(value) not in (float, int)
            or not isfinite(value) or not 0 <= value <= 100):
            raise ValueError("absent/nonphysical first-person body channel")
    return tuple(name for name in CRITICAL
                 if body[name] <= threshold)


class CriticalWakeDriveGuard:
    """An in-memory research-only witness and one-cycle evidence modifier."""

    def __init__(self, actor):
        self.actor = actor
        self.original = actor._evaluate_competition_cycle
        self.affected_steps = set()
        self.cycles = 0
        self.saw_waking_critical = False

    def install(self):
        actor = self.actor

        def evaluate(*, capture, cycle):
            critical = witnessed_critical_channels(capture.body)
            if not critical:
                return self.original(capture=capture, cycle=cycle)
            original_config = actor._stage10_config
            if original_config.intrinsic_weight < 0:
                raise RuntimeError("invalid native sleep intrinsic weight")
            self.saw_waking_critical = True
            self.affected_steps.add(capture.t_monde)
            self.cycles += 1
            # No Q/TD weight is touched, and the original freeze of actual
            # fatigue and pending consolidation remains fully intact.
            # Competition sees the same candidate, learned Q and threshold,
            # but not the positive *intrinsic* sleep contribution for this
            # physically urgent waking deliberation.
            actor._stage10_config = replace(
                original_config, intrinsic_weight=0.0)
            try:
                return self.original(capture=capture, cycle=cycle)
            finally:
                actor._stage10_config = original_config

        actor._evaluate_competition_cycle = evaluate


def _events(path: Path):
    return [json.loads(line)["causal_event"]
            for line in path.read_bytes().splitlines()]


def _summarize_life(life, *, wal, published):
    events = _events(wal)
    alerts = sorted({
        x["t_monde"] for x in events
        if x.get("kind") == "stage10_sleep_woke"
        and isinstance(x.get("data"), dict)
        and x["data"].get("reason") == "alert"
    })
    steps = life["steps"]
    resleep = [t for t in alerts
               if t <= len(steps)
               and steps[t-1]["action_primitive"] == "dormir"]
    commits = [x for x in events
               if x.get("kind") == "stage10_consolidation_committed"]
    accepted = sum(
        x["data"]["requested_uc"]
        for x in events if x.get("kind") == "compute_charge"
        and isinstance(x.get("data"), dict)
        and x["data"].get("accepted") is True)
    return {
        "lifecycle": life["lifecycle"],
        "physically_lived_steps": len(steps),
        "last_body": steps[-1]["body"],
        "last_position": steps[-1]["position"],
        "action_counts": dict(Counter(
            row["action_primitive"] for row in steps)),
        "alert_wakes": len(alerts),
        "alert_wakes_followed_by_sleep_same_step": len(resleep),
        "committed_consolidation_batches": len(commits),
        "accepted_cognitive_uc": accepted,
        "wal_sha256": sha256(wal.read_bytes()).hexdigest(),
        "wal_head": life["journal_head"],
        "verified_events": life["durable_entries"],
        "actual_thresholds": published,
    }


def experiment(*, world: str, seed: int, out: Path):
    if (world not in PREDECLARED_WORLDS or type(seed) is not int
        or seed not in PREDECLARED_SEEDS
        or out.exists()):
        raise ValueError("unpreregistered world/seed or unsafe overwrite")
    out = out.resolve()
    from run_i1_world_preset import _birth_parameters, _wal_life, load_preset
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True,
            text=True, cwd=ROOT).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("unavailable exact source SHA") from exc
    preset, preset_sha = load_preset(world)
    report = {
        "schema": "i1-317-critical-body-intrinsic-sleep-guard/paired-v1",
        "source_sha": sha,
        "birth_preset": world,
        "preset_sha256": preset_sha,
        "seed": seed,
        "horizon": HORIZON,
        "critical_body_percentage": EXPERIMENTAL_LIMIT,
        "three_channels": list(CRITICAL),
        "ordinary_wake_rules_unchanged": True,
        "no_motor_orders_or_sleep_ban": True,
        "no_reward_or_q_change": True,
        "no_coma_implemented": True,
        "physiological_safety_proven": False,
        "entity_causal_learning_proven": False,
        "scientific_verdict": "NO-GO",
        "status": "NOT_STARTED",
    }
    out.mkdir(parents=True, exist_ok=False)
    try:
        with TemporaryDirectory(prefix="i1-317-critical-guard-") as temp:
            from build_i1_fork import generate
            generated = Path(temp) / "generated"
            generate(generated)
            sys.path.insert(0, str(generated))
            from i1lab.i1_birth import birth_i1
            from audit_i1_spatial_navigation_314 import audit as verify_wal
            params, _ = _birth_parameters(preset)
            report["physics_digest"] = params["world_config"].digest()
            arms = {}
            life_id = f"i1:preset:{world}:{seed}:0"
            for arm in ("canonical", "critical-intrinsic-guard"):
                folder = out / arm
                folder.mkdir()
                path = folder / "life-01.wal"
                interventions = []
                births = []

                def birth(**kwargs):
                    individual = birth_i1(**kwargs)
                    births.append(individual)
                    if arm == "critical-intrinsic-guard":
                        hook = CriticalWakeDriveGuard(individual)
                        hook.install()
                        interventions.append(hook)
                    return individual

                lived = _wal_life(
                    birth=birth, params=params, life_id=life_id,
                    path=path, steps=HORIZON)
                if len(births) != 1 or (arm != "canonical"
                                        and len(interventions) != 1):
                    raise RuntimeError("not one unique and mortal I1 birth")
                proof = verify_wal(path)
                if (proof["independent_hash_chain_verified"] is not True
                    or proof["journal_head"] != lived["journal_head"]
                    or proof["journal_entries"] != lived["durable_entries"]):
                    raise RuntimeError("not a cryptographically verified birth")
                config = births[0]._stage10_config
                threshold = dict(config.critical_body_thresholds)
                if (threshold.get("water", 0) < 15
                    or threshold.get("integrity", 0) < 25
                    or threshold.get("food", 0) < 10):
                    raise RuntimeError("canonical protective wake thresholds weakened")
                if config.intrinsic_weight <= 0:
                    raise RuntimeError("permanent modification of sleep motivation")
                pub = _summarize_life(lived, wal=path, published=threshold)
                pub["wal_relative_path"] = f"{arm}/life-01.wal"
                pub["operator_intervention"] = {
                    "intrinsic_only_current_critical_waking_cycle": arm != "canonical",
                    "waking_cycles_at_verified_critical_body": (
                        0 if not interventions else interventions[0].cycles),
                    "affected_world_steps": (
                        [] if not interventions else sorted(
                            interventions[0].affected_steps)),
                    "changed_memory_or_world_owners": False,
                }
                arms[arm] = {"lived": lived, "public": pub}
        control = arms["canonical"]["lived"]["steps"]
        alternate = arms["critical-intrinsic-guard"]["lived"]["steps"]
        affected = arms["critical-intrinsic-guard"]["public"][
            "operator_intervention"]["affected_world_steps"]
        first_effect = min(affected) if affected else None
        if first_effect is not None:
            prefix = min(first_effect - 1, len(control), len(alternate))
            for t in range(prefix):
                if any(control[t][k] != alternate[t][k] for k in (
                    "journal_head", "body", "position", "action_primitive",
                    "execution", "action_source", "fallback_used")):
                    raise RuntimeError(
                        "noncausal divergence before any first-person critical guard")
        first_action_divergence = next((
            t + 1 for t, (a,b) in enumerate(zip(control, alternate))
            if any(a[k] != b[k] for k in (
                "body", "position", "action_primitive", "execution",
                "action_source", "fallback_used"))
        ), None)
        if (first_effect is not None and first_action_divergence is not None
            and first_action_divergence < first_effect):
            raise RuntimeError("physical divergence predates intervention")
        report["arms"] = {k: v["public"] for k,v in arms.items()}
        report["first_guarded_first_person_world_step"] = first_effect
        report["first_physical_action_divergence"] = first_action_divergence
        report["status"] = "PAIRED_MORTAL_DIAGNOSTIC_COMPLETE"
    except Exception as exc:
        report["status"] = "TECHNICAL_FAILURE"
        report["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        (out / "report.json").write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n",
            encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "preset": world, "seed": seed,
        "first_guarded": report["first_guarded_first_person_world_step"],
        "first_motor_divergence": report["first_physical_action_divergence"],
        "outcomes": {
            name: {
                "lifecycle": case["lifecycle"],
                "steps": case["physically_lived_steps"],
                "alert_to_sleep": case["alert_wakes_followed_by_sleep_same_step"],
                "actions": case["action_counts"],
                "consolidation": case["committed_consolidation_batches"],
                "accepted_uc": case["accepted_cognitive_uc"],
            } for name, case in report["arms"].items()
        },
        "scientific_verdict": "NO-GO",
    }, indent=2, sort_keys=True))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preset",required=True)
    p.add_argument("--seed",type=int,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    x=p.parse_args()
    experiment(world=x.preset,seed=x.seed,out=x.output_dir)


if __name__=="__main__":
    main()
