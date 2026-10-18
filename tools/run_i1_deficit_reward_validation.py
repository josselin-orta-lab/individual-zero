#!/usr/bin/env python3
"""Predeclared matched mortal I1 reward experiment, with no policy interventions."""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "scripts"), str(ROOT / "src")]
from run_i1_world_preset import load_preset, _birth_parameters
from build_i1_fork import generate

REWARDS = ("absolute", "deficit-only-v1")
WORLDS = ("oasis", "foraging")


def execute(*, world, seed, reward, steps, output_dir):
    if world not in WORLDS or reward not in REWARDS or type(seed) is not int:
        raise ValueError("unregistered experimental arm")
    if not 1 <= steps <= 300:
        raise ValueError("unregistered step horizon")
    preset, digest = load_preset(world)
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "status": "TECHNICAL_FAILURE", "scientific_gate": "NOT_EVALUATED",
        "world": world, "world_sha256": digest, "seed": seed,
        "reward": reward, "requested_steps": steps,
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    try:
        with TemporaryDirectory() as tmp:
            build = Path(tmp) / "generated"
            generate(build)
            sys.path.insert(0, str(build))
            from i1lab.i1_birth import birth_i1
            from i1lab.journal import HashChainedJournal
            from i1.modules.value_needs import ValueAndNeeds, BODY_VARIABLES

            params, _ = _birth_parameters(preset)
            # Both arms share the same life identity and temperament, but never
            # run simultaneously and never share state, WAL, Q or memory.
            identity = f"i1:reward-study:{world}:{seed}"
            if reward == "deficit-only-v1":
                old = ValueAndNeeds.reward_between
                def deficit_reward(self, before, after):
                    cfg = self.config
                    return sum(
                        cfg.weights[k] * (
                            max(0.0, cfg.setpoints[k] - float(before[k]))
                            - max(0.0, cfg.setpoints[k] - float(after[k]))
                        ) for k in BODY_VARIABLES
                    )
                ValueAndNeeds.reward_between = deficit_reward
                # Research branch: policy is verified as effective before any
                # live step; no ordinary runtime module is modified.
                if ValueAndNeeds.reward_between is old:
                    raise AssertionError("reward arm not installed")
            wal = output / "life.wal"
            life = birth_i1(life_id=identity, wal_path=str(wal), **params)
            assert life.goal_manager._config.replacement_hysteresis == .04
            assert life.goal_manager._config.critical_pressure == .35
            assert life._stage8_config.td.lambda_e == .8
            assert life.value_needs.reward_between.__func__ is ValueAndNeeds.reward_between
            before = dict(life.world.telemetry())
            transitions = []
            totals = Counter()
            for _ in range(steps):
                receipt = life.run_step()
                after = dict(life.world.telemetry())
                action = receipt.command_primitive
                totals[action or "NO_ACTION"] += 1
                transitions.append({
                    "t": life.scheduler.t_monde, "before": before,
                    "after": after, "action": action,
                    "execution": receipt.execution_status,
                    "source": receipt.source,
                    "goal": None if life.goal_manager.active_goal is None
                        else life.goal_manager.active_goal.goal_type,
                    "experienced_reward": life.value_needs.reward_between(before, after),
                    "head": life.journal.head_hash,
                })
                before = after
                if receipt.execution_status == "dead":
                    break
            if not life.journal.verify():
                raise RuntimeError("live journal invalid")
            audit = HashChainedJournal.audit_durable_wal(str(wal))
            if (audit["head_hash"] != life.journal.head_hash
                    or audit["verified_entries"] != life.journal.entry_count):
                raise RuntimeError("durable WAL mismatch")
            events = [e.causal_event for e in life.journal.entries_since(0)]
            kinds = Counter(e.get("kind") for e in events)
            report.update({
                "status": "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT",
                "identity": identity,
                "born_goal": {"version": life.goal_manager._config.version,
                              "hysteresis": .04, "critical": .35},
                "effective_reward": reward,
                "effective_td_lambda": life._stage8_config.td.lambda_e,
                "lifecycle": life.stage3.substrate.mortal_status.value,
                "observed_steps": len(transitions), "actions": dict(totals),
                "zero_steps": {key: sum(t["after"][key] <= 0 for t in transitions)
                               for key in ("food", "water", "energy")},
                "drinks_applied": sum(t["action"] == "boire" and t["execution"] == "applied"
                                      for t in transitions),
                "eats_applied": sum(t["action"] == "manger" and t["execution"] == "applied"
                                    for t in transitions),
                "journal_head": life.journal.head_hash,
                "journal_entries": audit["verified_entries"],
                "event_counts": dict(kinds),
                "goal_events": [e for e in events if e.get("kind") == "active_goal_changed"],
                "competition_events": [e for e in events if e.get("kind") == "competition_cycle"],
                "td_events": [e for e in events if "td" in str(e.get("kind", ""))],
                "trajectory": transitions,
            })
    finally:
        (output / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--world", required=True, choices=WORLDS)
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--reward", required=True, choices=REWARDS)
    p.add_argument("--steps", type=int, default=300)
    p.add_argument("--output-dir", required=True)
    a = p.parse_args()
    x = execute(world=a.world, seed=a.seed, reward=a.reward,
                steps=a.steps, output_dir=a.output_dir)
    print(json.dumps({k: x[k] for k in
                      ("status", "identity", "lifecycle", "observed_steps",
                       "zero_steps", "drinks_applied", "eats_applied")}))
