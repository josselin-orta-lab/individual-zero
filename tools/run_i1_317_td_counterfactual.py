#!/usr/bin/env python3
"""#317 operator-only counterfactual: remove one *action* TD eligibility credit.

No production I1 file, physical law, reward, decision, Competition threshold,
Action Control, or existing WAL is edited. Two separate irreversible mortal
births share the same initial code, identity, parameters and world. An instance
hook removes only one named memory-signature weight update at one witnessed TD
publication. This tests the role of learned *action* value, not the causal
benefit of the corresponding entity. Diagnostic seeds are not held-out GO.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from math import isclose, isfinite
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from run_i1_world_preset import _birth_parameters, _wal_life, load_preset


def num(value):
    if type(value) in (int, float):
        result = float(value)
    elif isinstance(value, dict) and set(value) == {"$f64"}:
        result = float.fromhex(value["$f64"])
    else:
        raise ValueError("missing or invalid WAL numerical value")
    if not isfinite(result):
        raise ValueError("non-finite WAL numerical value")
    return result


class SingleTDMemoryCreditAblation:
    """Instance-local, single-use filter around TD update_segment.

    A targeted *prior* eligibility trace is temporarily removed from the
    update iterator, then restored at precisely the natural decay. No reward
    is changed; all other signatures get normal updates. The single published
    WAL TD update visibly omits the target signature in the ablation arm.
    """

    def __init__(self, model, *, decision_step, target, previous, following):
        if (type(decision_step) is not int or decision_step < 2
            or not target.startswith("memory_place_return:")
            or not previous or not following):
            raise ValueError("invalid researcher ablation target")
        self.model = model
        self.decision_step = decision_step
        self.target = target
        self.previous = previous
        self.following = following
        self.original = model.update_segment
        self.records = []

    def install(self):
        model = self.model

        def hook(**kwargs):
            pending = model.pending_segment
            rewards = kwargs.get("rewards")
            step = (pending.decision_t_monde + len(rewards)
                    if pending is not None and rewards is not None else None)
            if step != self.decision_step:
                return self.original(**kwargs)
            if (self.records or len(rewards) != 1
                or pending.signature != self.previous
                or kwargs.get("previous_signature") != self.previous
                or kwargs.get("next_signature") != self.following):
                raise RuntimeError("expected lived TD credit context was not present")
            old_trace = model._traces.get(self.target)
            if (not isinstance(old_trace, list) or not old_trace
                or not any(old_trace)
                or not all(isfinite(float(v)) for v in old_trace)):
                raise RuntimeError("target memory eligibility was absent")
            preserved_trace = list(old_trace)
            old_weights = tuple(model._weights.get(self.target, ()))
            old_count = model._update_counts.get(self.target, 0)
            del model._traces[self.target]
            # Fail closed on exceptions; restoring a live trace is not a
            # rollback of the individual's action or physical environment.
            try:
                update = self.original(**kwargs)
            finally:
                decay = (
                    model.config.beta * model.config.lambda_e
                ) ** len(rewards)
                model._traces[self.target] = [
                    value * decay for value in preserved_trace
                ]
            if (self.target in update.updated_signatures
                or tuple(model._weights.get(self.target, ())) != old_weights
                or model._update_counts.get(self.target, 0) != old_count
                or not isclose(update.return_g, float(rewards[0]),
                               rel_tol=1e-12, abs_tol=1e-12)):
                raise RuntimeError("TD credit ablation altered the wrong state")
            self.records.append({
                "world_step": step,
                "suppressed_memory_action_signature": self.target,
                "previous_signature": update.previous_signature,
                "next_signature": update.next_signature,
                "return_g": update.return_g,
                "delta": update.delta,
                "remaining_updated_signatures": list(update.updated_signatures),
                "original_trace_decay_preserved": True,
                "reward_or_action_modified": False,
                "entity_affordance_inferred": False,
            })
            return update

        model.update_segment = hook


def load_events(path):
    return [json.loads(line)["causal_event"] for line in path.read_bytes().splitlines()]


def unique_td(events, step, previous):
    rows = [e["data"] for e in events
            if e.get("t_monde") == step
            and e.get("kind") == "td_update_published"
            and isinstance(e.get("data"), dict)
            and e["data"].get("previous_signature") == previous]
    if len(rows) != 1:
        raise ValueError("expected exactly one first-person TD update")
    return rows[0]


def memory_evaluation(events, step, signature):
    results = [e["data"] for e in events
               if e.get("t_monde") == step
               and e.get("kind") == "stage8_option_evaluation"
               and isinstance(e.get("data"), dict)
               and e["data"].get("learning_signature") == signature]
    if not results:
        return None
    record = results[-1]
    return {
        "option_ref": record.get("option_ref"),
        "learned_status": record.get("learned_value_status"),
        "learned_q": (None if record.get("learned_value") is None
                      else num(record["learned_value"])),
        "intrinsic_value": (None if record.get("intrinsic_value") is None
                            else num(record["intrinsic_value"])),
        "evidence": (None if record.get("evidence") is None
                     else num(record["evidence"])),
    }


def physical_memory_decision(events, step, option):
    if not isinstance(option, str) or not option:
        return None
    crossed = []
    for e in events:
        if e.get("t_monde") == step and e.get("kind") == "competition_cycle":
            d = e.get("data")
            if isinstance(d, dict):
                for trace in d.get("traces", ()):
                    if (isinstance(trace, dict)
                        and trace.get("option_ref") == option
                        and trace.get("crossed") is True):
                        crossed.append({
                            "before": num(trace["accumulator_before"]),
                            "after": num(trace["accumulator_after"]),
                            "threshold": num(trace["threshold"]),
                            "evidence": num(trace["evidence"]),
                        })
    admissions = [
        e for e in events
        if e.get("t_monde") == step and e.get("kind") == "command_admitted"
        and isinstance(e.get("data"), dict)
        and e["data"].get("option_ref") == option
        and e["data"].get("primitive") == "se_deplacer"]
    certified = False
    for admitted in admissions:
        attempt = admitted.get("attempt_ref")
        command_hash = admitted["data"].get("command_hash")
        commands = [
            e for e in events
            if e.get("t_monde") == step
            and e.get("attempt_ref") == attempt
            and e.get("kind") == "command_experienced"
            and e.get("primitive") == "se_deplacer"
            and e.get("command_hash") == command_hash]
        transitions = [
            e for e in events
            if e.get("t_monde") == step
            and e.get("attempt_ref") == attempt
            and e.get("kind") == "world_transition_experienced"
            and e.get("effects") == {"movement": "moved"}]
        closures = [
            e for e in events
            if e.get("t_monde") == step
            and e.get("attempt_ref") == attempt
            and e.get("kind") == "step_closed"
            and isinstance(e.get("data"), dict)
            and e["data"].get("outcome") == "normal"
            and e["data"].get("applied_command_count") == 1
            and e["data"].get("world_advance_count") == 1]
        if len(commands) == len(transitions) == len(closures) == 1:
            certified = True
    return {
        "crossed_competition": bool(crossed),
        "crossings": crossed,
        "admitted_by_action_control": bool(admissions),
        "physically_applied_same_option": bool(crossed and certified),
    }


def run(*, output_dir, preset, seed, steps, credit_step, signature,
        previous, following, check_step, expected_control_head=None,
        inspect_signature=None):
    output_dir = output_dir.resolve()
    if (output_dir.exists()
        or type(seed) is not int or not 0 <= seed <= 2**32 - 1
        or type(steps) is not int or not 2 <= steps <= 300
        or type(credit_step) is not int or not 2 <= credit_step < steps
        or type(check_step) is not int or not credit_step < check_step <= steps):
        raise ValueError("unsafe or overwriting experiment parameters")
    inspect_signature = (signature if inspect_signature is None
                         else inspect_signature)
    if not inspect_signature.startswith("memory_place_return:"):
        raise ValueError("decision inspection must target a memory signature")
    preset_data, digest = load_preset(preset)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.strip()
    report = {
        "schema": "i1-317-operator-td-counterfactual-v1",
        "code_sha": sha, "preset": preset, "preset_sha256": digest,
        "seed": seed, "horizon": steps,
        "memory_signature": signature,
        "decision_inspected_signature": inspect_signature,
        "targeted_td_step": credit_step,
        "later_decision_step": check_step,
        "only_intervention": "one prior memory-action eligibility credit",
        "canonical_engine_modules_modified": False,
        "reward_or_physics_modified": False,
        "population_go": False,
        "entity_causality_proven": False,
        "status": "NOT_STARTED",
    }
    output_dir.mkdir(parents=True, exist_ok=False)
    try:
        with TemporaryDirectory(prefix="i1-317-paired-td-build-") as tmp:
            from build_i1_fork import generate
            build = Path(tmp) / "generated"
            generate(build)
            sys.path.insert(0, str(build))
            from i1lab.i1_birth import birth_i1
            from audit_i1_spatial_navigation_314 import audit as independent_audit

            params, _ = _birth_parameters(preset_data)
            report["physics_digest"] = params["world_config"].digest()
            report["stage11_config"] = params["stage11_config"].version
            report["td_config"] = params["stage11_config"].stage9.stage8.td.version
            arms = {}
            life_id = f"i1:preset:{preset}:{seed}:0"
            for arm in ("control", "memory-credit-ablated"):
                directory = output_dir / arm
                directory.mkdir()
                wal = directory / "life-01.wal"
                gates = []

                def born(**birth_kwargs):
                    individual = birth_i1(**birth_kwargs)
                    if arm == "memory-credit-ablated":
                        gate = SingleTDMemoryCreditAblation(
                            individual.q_active, decision_step=credit_step,
                            target=signature, previous=previous,
                            following=following)
                        gate.install()
                        gates.append(gate)
                    return individual

                life = _wal_life(
                    birth=born, params=params, life_id=life_id,
                    path=wal, steps=steps)
                if arm == "memory-credit-ablated" and (
                    len(gates) != 1 or len(gates[0].records) != 1):
                    raise RuntimeError("ablation must execute once, physically")
                proof = independent_audit(wal)
                if (proof["independent_hash_chain_verified"] is not True
                    or proof["journal_head"] != life["journal_head"]
                    or proof["journal_entries"] != life["durable_entries"]):
                    raise RuntimeError("independent WAL custody mismatch")
                events = load_events(wal)
                td = unique_td(events, credit_step, previous)
                arms[arm] = {
                    "trajectory": life["steps"],
                    "events": events,
                    "td": td,
                    "public": {
                        "wal_file": f"{arm}/life-01.wal",
                        "wal_sha256": sha256(wal.read_bytes()).hexdigest(),
                        "journal_head": life["journal_head"],
                        "journal_entries": life["durable_entries"],
                        "lifecycle": life["lifecycle"],
                        "steps_lived": len(life["steps"]),
                        "final_body": life["steps"][-1]["body"],
                        "final_position": life["steps"][-1]["position"],
                        "actions": dict(Counter(
                            s["action_primitive"] for s in life["steps"])),
                        "td_at_credit_step": {
                            "previous_signature": td["previous_signature"],
                            "next_signature": td["next_signature"],
                            "return_g": num(td["return_g"]),
                            "delta": num(td["delta"]),
                            "updated_signatures": td["updated_signatures"],
                        },
                        "gate": [] if not gates else gates[0].records,
                    },
                }
        control, ablated = (arms["control"], arms["memory-credit-ablated"])
        if (len(control["trajectory"]) < check_step
            or len(ablated["trajectory"]) < credit_step):
            raise RuntimeError("insufficient mortal physical experience")
        for t in range(credit_step-1):
            a, b = control["trajectory"][t], ablated["trajectory"][t]
            if any(a[k] != b[k] for k in (
                "journal_head", "position", "body", "action_primitive",
                "execution", "action_source", "fallback_used")):
                raise RuntimeError(f"births diverged before target TD step {t+1}")
        report["identical_world_steps_before_credit"] = credit_step-1
        report["identical_precredit_journal_head"] = (
            control["trajectory"][credit_step-2]["journal_head"])
        if (expected_control_head is not None
            and control["public"]["journal_head"] != expected_control_head):
            raise RuntimeError("baseline differs from pinned authentic historical WAL")
        td_a = control["public"]["td_at_credit_step"]
        td_b = ablated["public"]["td_at_credit_step"]
        if (signature not in td_a["updated_signatures"]
            or signature in td_b["updated_signatures"]
            or td_a["previous_signature"] != previous
            or td_b["previous_signature"] != previous
            or td_a["next_signature"] != following
            or td_b["next_signature"] != following
            or td_a["return_g"] != td_b["return_g"]
            or td_a["delta"] != td_b["delta"]
            or sorted(v for v in td_a["updated_signatures"] if v != signature)
              != sorted(td_b["updated_signatures"])):
            raise RuntimeError("ablation not isolated to one memory TD update")
        tmax = min(len(control["trajectory"]), len(ablated["trajectory"]))
        divergence = next((
            t+1 for t in range(tmax)
            if any(control["trajectory"][t][key] != ablated["trajectory"][t][key]
                   for key in ("position", "body", "action_primitive",
                               "execution", "action_source", "fallback_used"))
        ), None)
        ev_a = memory_evaluation(
            control["events"], check_step, inspect_signature)
        ev_b = memory_evaluation(
            ablated["events"], check_step, inspect_signature)
        if ev_a is None:
            raise RuntimeError("pinned baseline memory Q evaluation missing")
        comparison = {
            "first_physical_divergence_step": divergence,
            "evaluations": {
                "control": ev_a, "memory-credit-ablated": ev_b},
            "physical_decisions": {
                "control": physical_memory_decision(
                    control["events"], check_step, ev_a["option_ref"]),
                "memory-credit-ablated": (
                    None if ev_b is None else physical_memory_decision(
                        ablated["events"], check_step, ev_b["option_ref"])),
            },
            "causal_scope": "single witnessed TD eligibility credit only",
            "whole_life_policy_effect_is_empirically_observed_not_assumed": True,
            "entity_affordance_not_inferred": True,
        }
        report["arms"] = {name: d["public"] for name, d in arms.items()}
        report["comparison"] = comparison
        report["status"] = "COMPLETED_DIAGNOSTIC_NO_GLOBAL_GO"
    except Exception as exc:
        report["status"] = "TECHNICAL_FAILURE"
        report["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        (output_dir / "report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "code_sha": sha,
        "first_physical_divergence_step": (
            report["comparison"]["first_physical_divergence_step"]),
        "evaluations": report["comparison"]["evaluations"],
        "physical_decisions": report["comparison"]["physical_decisions"],
        "lifecycle": {
            name: row["lifecycle"] for name, row in report["arms"].items()},
    }, sort_keys=True, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--credit-step", type=int, required=True)
    parser.add_argument("--memory-signature", required=True)
    parser.add_argument("--previous-signature", required=True)
    parser.add_argument("--next-signature", required=True)
    parser.add_argument("--check-step", type=int, required=True)
    parser.add_argument("--expected-control-head")
    parser.add_argument("--inspect-signature", help=(
        "Optional separate memory signature for later-decision negative control; "
        "defaults to the ablated signature. This never affects the birth."))
    args = parser.parse_args()
    run(output_dir=args.output_dir, preset=args.preset, seed=args.seed,
        steps=args.steps, credit_step=args.credit_step,
        signature=args.memory_signature, previous=args.previous_signature,
        following=args.next_signature, check_step=args.check_step,
        expected_control_head=args.expected_control_head,
        inspect_signature=args.inspect_signature)


if __name__ == "__main__":
    main()
