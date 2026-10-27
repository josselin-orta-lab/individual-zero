#!/usr/bin/env python3
"""Matched natural I1 newborn mortal cohort; observer-only, no policy commands."""
import argparse
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from dataclasses import replace
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "scripts"), str(ROOT / "src")]
from run_i1_world_preset import load_preset, _birth_parameters
from build_i1_fork import generate


def execute(world_name, seed, policy, steps, directory):
    if world_name not in ("oasis", "foraging"):
        raise ValueError("unregistered comparison world")
    if policy not in ("natural-004", "historical-010"):
        raise ValueError("unregistered goal policy")
    if steps < 1 or steps > 300:
        raise ValueError("invalid observation horizon")
    world, world_digest = load_preset(world_name)
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    report = {
        "status": "TECHNICAL_FAILURE", "scientific_gate": "NOT_EVALUATED",
        "source": {"world": world_name, "world_sha256": world_digest},
        "run": {"seed": seed, "policy": policy, "horizon": steps,
                "git_head": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()},
        "old_cohorts_used_as_oracles": False,
    }
    try:
        with TemporaryDirectory() as folder:
            build = Path(folder) / "generated"
            generate(build)
            sys.path.insert(0, str(build))
            from i1lab.i1_birth import birth_i1
            from i1lab.i1_natural_runtime import I1Runtime
            from i1lab.journal import HashChainedJournal

            params, _ = _birth_parameters(world)
            life_id = f"i1:goal-cohort:{world_name}:{seed}:{policy}"
            wal = directory / "life.wal"
            if policy == "natural-004":
                life = birth_i1(life_id=life_id, wal_path=str(wal), **params)
            else:
                life = I1Runtime(
                    birth_life_id=life_id, wal_path=str(wal),
                    autonomous_mortal=True, i1_goal_policy=policy,
                    diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
                    **params)
            cfg = life.goal_manager._config
            expected = (.04,.35) if policy == "natural-004" else (.10,.90)
            actual = (cfg.replacement_hysteresis, cfg.critical_pressure)
            if actual != expected:
                raise AssertionError("actual born config disagrees with declared arm")
            trace = []
            actions = Counter()
            zero_steps = Counter()
            water_gain = food_gain = 0.0
            old_body = dict(life.world.telemetry())
            for _ in range(steps):
                receipt = life.run_step()
                body = dict(life.world.telemetry())
                primitive = receipt.command_primitive
                actions[primitive or "NO_ACTION"] += 1
                for key in ("water","energy","food"):
                    if body[key] <= 0:
                        zero_steps[key] += 1
                if primitive == "boire" and receipt.execution_status == "applied":
                    water_gain += max(0.0, body["water"] - old_body["water"])
                if primitive == "manger" and receipt.execution_status == "applied":
                    food_gain += max(0.0, body["food"] - old_body["food"])
                trace.append({
                    "world_step": life.scheduler.t_monde, "body": body,
                    "action": primitive, "source": receipt.source,
                    "execution": receipt.execution_status,
                    "goal": None if life.goal_manager.active_goal is None
                             else life.goal_manager.active_goal.goal_type,
                    "journal_head": life.journal.head_hash,
                })
                old_body = body
                if life.goal_manager._config is not cfg:
                    raise AssertionError("birth goal owner changed during life")
                if receipt.execution_status == "dead":
                    break
            if not life.journal.verify():
                raise AssertionError("in-memory journal invalid")
            audit = HashChainedJournal.audit_durable_wal(str(wal))
            if audit["head_hash"] != life.journal.head_hash:
                raise AssertionError("WAL head mismatch")
            events = [e.causal_event for e in life.journal.entries_since(0)]
            report.update({
                "status": "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT",
                "identity": life_id,
                "effective_goal": {
                    "version": cfg.version, "replacement_hysteresis": actual[0],
                    "critical_pressure": actual[1]},
                "effective_td": {
                    "version": life._stage8_config.td.version,
                    "lambda_e": life._stage8_config.td.lambda_e},
                "world_physics_digest": params["world_config"].digest(),
                "lifecycle": life.stage3.substrate.mortal_status.value,
                "steps_observed": len(trace), "zero_steps": dict(zero_steps),
                "applied_drinking_water_gain": water_gain,
                "applied_eating_food_gain": food_gain,
                "actions": dict(actions),
                "journal_head": life.journal.head_hash,
                "verified_wal_entries": audit["verified_entries"],
                "goal_transition_events": [
                    e for e in events if e.get("kind") == "active_goal_changed"],
                "competition_events": [
                    e for e in events if e.get("kind") == "competition_cycle"],
                "td_events": [
                    e for e in events if "td_" in str(e.get("kind", ""))],
                "trace": trace,
            })
    finally:
        (directory / "report.json").write_text(json.dumps(report, indent=2, default=str)+"\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--world", required=True, choices=("oasis","foraging"))
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--policy", required=True, choices=("natural-004","historical-010"))
    p.add_argument("--steps", type=int, default=150)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    result = execute(args.world,args.seed,args.policy,args.steps,args.output_dir)
    print(json.dumps({k: result[k] for k in ("status","identity","steps_observed","lifecycle")}))
