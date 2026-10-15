"""A2.30-E prospective, external-only census of *actual* Stage6 search edges.

Pre-registered before instrumentation in
docs/research/stage12-issue110-b-a230-edge-necessity-prereg-2026-10-15.fr.md.

The probe delegates each original call exactly once, returning its original
result. Corpus membership and field comparisons live solely in the laboratory.
I0 never receives the audit, an alternate prediction, or an oracle label.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import run_stage12_issue110_b_a228_funnel as cohort
import run_stage12_issue110_first_planning_state as factory
from i0.equipment import FrozenTableEquipment
from i0.modules.simulator import Simulator
from i0.modules.stage6_planning import SimulatorPlanner
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.determinism import canonical_causal_bytes, sha256_hex

PROFILES = ("restored", "sustained", "episodic", "marginal")
STEPS = 24
STATE_FIELDS = (
    "schema_version", "x", "y", "body", "inventory", "current_water_source",
    "current_resources", "adjacent", "known_shelter_here", "is_night",
)


def state_hash(state):
    return sha256_hex(canonical_causal_bytes(state.as_dict()))


class EdgeProbe:
    """A passive observer, neither a cognitive owner nor a model provider."""

    def __init__(self):
        self.world_step = 0
        self.searches = []
        self.current_search = None
        self.training = {}
        self.training_examples = []

    def record_example(self, recorder, example):
        # The factory also constructs Stage10/11 reference training data.
        # Only this life's independently applied prebirth food table counts.
        if not str(getattr(recorder, "_version", "")).startswith(
            "issue110-lived-north-east-food-physical-v1"
        ):
            return
        key = FrozenTableEquipment.input_digest(example.state, example.command)
        entry = {
            "input_sha256": key,
            "command": example.command.as_dict(),
            "state": example.state.as_dict(),
            "family": example.family,
        }
        self.training_examples.append(entry)
        self.training[key] = entry

    def closest_training(self, state, command):
        encoded = command.as_dict()
        similar = [ex for ex in self.training_examples
                   if ex["command"] == encoded]
        if not similar:
            return {
                "category": "unseen_command",
                "same_command_training_examples": 0,
                "nearest_differing_fields": list(STATE_FIELDS),
            }
        before = state.as_dict()
        diffs = [
            tuple(name for name in STATE_FIELDS if before[name] != ex["state"][name])
            for ex in similar
        ]
        best = min(diffs, key=lambda fields: (len(fields), fields))
        if not best:
            raise AssertionError("available training key was marked as absent")
        return {
            "category": "unseen_state_for_known_command",
            "same_command_training_examples": len(similar),
            "nearest_differing_fields": list(best),
        }

    @contextmanager
    def observe(self):
        original_record = EquipmentCorpusRecorder.record_transition
        original_search = SimulatorPlanner.search
        original_candidates = SimulatorPlanner.candidate_commands
        original_rollout = Simulator.rollout
        original_step = factory.Stage12Runtime.run_step
        probe = self

        def record_wrapper(recorder, *args, **kwargs):
            example = original_record(recorder, *args, **kwargs)
            probe.record_example(recorder, example)
            return example

        def step_wrapper(runtime, *args, **kwargs):
            probe.world_step += 1
            return original_step(runtime, *args, **kwargs)

        def candidate_wrapper(cls, state):
            commands = original_candidates(state)
            ctx = probe.current_search
            if ctx is not None:
                ctx["candidate_states"].append({
                    "state_sha256": state_hash(state),
                    "depth": ctx["state_depth"].get(state_hash(state)),
                    "candidate_commands": [cmd.as_dict() for cmd in commands],
                    "current_resources": list(state.current_resources),
                    "berry_inventory": {
                        berry: int(state.inventory.get(berry, 0))
                        for berry in ("berry_a", "berry_b")
                    },
                    "passable_adjacent": sum(x.passable for x in state.adjacent),
                })
            return commands

        def rollout_wrapper(simulator, *, initial_state, commands, r_eff, h_eff):
            # No replay and no fallback: the unmodified simulator is the sole
            # source of the prediction and of the reason for unavailability.
            result = original_rollout(
                simulator, initial_state=initial_state, commands=commands,
                r_eff=r_eff, h_eff=h_eff,
            )
            ctx = probe.current_search
            if ctx is None:
                return result
            if len(commands) != 1 or r_eff != 1 or h_eff != 1:
                raise AssertionError("unexpected Stage6 search rollout contract")
            command = commands[0]
            input_sha = FrozenTableEquipment.input_digest(initial_state, command)
            known_exact = input_sha in probe.training
            row = {
                "input_sha256": input_sha,
                "state_sha256": state_hash(initial_state),
                "command": command.as_dict(),
                "parent_depth": ctx["state_depth"].get(state_hash(initial_state)),
                "known_exact_in_prebirth_corpus": known_exact,
                "complete": result.complete,
                "status": result.status,
                "reason": result.reason,
                "terminal": None,
                "next_state_sha256": None,
            }
            if result.complete:
                if not result.completed_rollouts:
                    raise AssertionError("complete rollout without predictions")
                predictions = result.completed_rollouts[0].predictions
                if len(predictions) != 1:
                    raise AssertionError("wrong Stage6 edge horizon")
                next_state = predictions[0].next_state
                row["next_state_sha256"] = state_hash(next_state)
                row["terminal"] = bool(predictions[0].terminal)
                if row["parent_depth"] is not None:
                    ctx["state_depth"].setdefault(
                        row["next_state_sha256"], row["parent_depth"] + 1
                    )
            elif result.reason == "equipment_input_unseen":
                if known_exact:
                    raise AssertionError("trained exact Equipment input refused")
                row.update(probe.closest_training(initial_state, command))
            else:
                row["category"] = "other_unavailability"
            ctx["edges"].append(row)
            return result

        def search_wrapper(planner, *, initial_state, target,
                           progress_measure=None):
            if probe.current_search is not None:
                raise AssertionError("unexpected nested planning search")
            first_sha = state_hash(initial_state)
            ctx = {
                "step_attempt": probe.world_step,
                "ordinal": len(probe.searches) + 1,
                "initial_accessible_state": initial_state.as_dict(),
                "initial_state_sha256": first_sha,
                "progress_measure": progress_measure,
                "depth_limit": planner._config.max_depth,
                "model_version": planner._simulator.equipment_version,
                "state_depth": {first_sha: 0},
                "candidate_states": [],
                "edges": [],
            }
            probe.current_search = ctx
            try:
                result = original_search(
                    planner, initial_state=initial_state, target=target,
                    progress_measure=progress_measure,
                )
                ctx["status"] = result.status
                ctx["expanded_states"] = result.expanded_states
                ctx["unavailable_edges"] = result.unavailable_edges
                ctx["commands"] = [cmd.as_dict() for cmd in result.commands]
                ctx["predicted_target_from_model"] = result.status == "plan_found"
                ctx["partial_progress"] = result.partial_progress
                counted_unavailable = sum(
                    not e["complete"] for e in ctx["edges"]
                )
                if counted_unavailable != result.unavailable_edges:
                    raise AssertionError(
                        f"search counter mismatch: {counted_unavailable} != "
                        f"{result.unavailable_edges}"
                    )
                if len(ctx["candidate_states"]) != result.expanded_states:
                    raise AssertionError(
                        "observed candidate nodes do not match expanded_states"
                    )
                probe.searches.append(ctx)
                return result
            finally:
                probe.current_search = None

        # Everything below exists only inside this external experiment.
        with patch.object(EquipmentCorpusRecorder, "record_transition", record_wrapper), \
             patch.object(factory.Stage12Runtime, "run_step", step_wrapper), \
             patch.object(SimulatorPlanner, "candidate_commands",
                          classmethod(candidate_wrapper)), \
             patch.object(SimulatorPlanner, "search", search_wrapper), \
             patch.object(Simulator, "rollout", rollout_wrapper):
            yield


def run_life(folder, profile, blocked, *, observed):
    previous_steps = cohort.STEPS
    cohort.STEPS = STEPS
    probe = EdgeProbe() if observed else None
    try:
        if probe is None:
            life = cohort.run_one(
                folder, profile, blocked, birth_cohort="a230e"
            )
        else:
            with probe.observe():
                life = cohort.run_one(
                    folder, profile, blocked, birth_cohort="a230e"
                )
    finally:
        cohort.STEPS = previous_steps
    return life, probe


def audit_life(folder, life, probe):
    events = [
        json.loads(line)["causal_event"]
        for line in (folder / "canonical.jsonl").read_bytes().splitlines()
    ]
    stage6 = [
        e for e in events if e.get("kind") == "stage6_planning_result"
    ]
    actual_by_step = defaultdict(Counter)
    receipts = Counter()
    for event in stage6:
        diag = event.get("data", {}).get("progressive_search_diagnostic")
        if not isinstance(diag, dict):
            raise AssertionError("missing canonical Stage6 diagnostic")
        status = diag.get("status")
        receipts[status] += 1
        if status in (
            "plan_found", "partial_progress", "incomplete_model",
            "not_found_within_horizon"
        ):
            actual_by_step[event["t_monde"]][status] += 1
    observed_by_step = defaultdict(Counter)
    for search in probe.searches:
        observed_by_step[search["step_attempt"]][search["status"]] += 1
    if dict(actual_by_step) != dict(observed_by_step):
        raise AssertionError(
            "physical-step search statuses mismatch canonical receipts: "
            f"{dict(actual_by_step)} != {dict(observed_by_step)}"
        )
    if len(probe.training_examples) != 4:
        raise AssertionError(
            f"unexpected prebirth food corpus {len(probe.training_examples)}"
        )
    all_edges = [edge for s in probe.searches for edge in s["edges"]]
    incomplete = [s for s in probe.searches
                  if s["status"] == "incomplete_model"]
    unavailable = [e for e in all_edges if not e["complete"]]
    missing = [e for e in unavailable
               if e["reason"] == "equipment_input_unseen"]
    other = [e for e in unavailable
             if e["reason"] != "equipment_input_unseen"]
    if any(e.get("known_exact_in_prebirth_corpus") for e in missing):
        raise AssertionError("known corpus key misclassified as unseen")
    if len(probe.searches) != sum(actual_by_step[t].total()
                                 for t in actual_by_step):
        raise AssertionError("search/receipt one-to-one mapping failed")
    counts = {
        "searches": len(probe.searches),
        "canonical_search_statuses": dict(receipts),
        "actual_rollout_edges": len(all_edges),
        "available_edges": len(all_edges) - len(unavailable),
        "unavailable_edges": len(unavailable),
        "missing_exact_inputs": len(missing),
        "other_unavailability": len(other),
        "unknown_command": sum(e.get("category") == "unseen_command"
                               for e in missing),
        "known_command_unseen_state": sum(
            e.get("category") == "unseen_state_for_known_command"
            for e in missing
        ),
        "unknown_causes": dict(Counter(e.get("reason") for e in other)),
        "missing_commands": dict(Counter(
            e["command"]["primitive"] for e in missing
        )),
        "nearest_differing_fields": dict(Counter(
            field for e in missing
            for field in e.get("nearest_differing_fields", ())
        )),
        "incomplete_searches": len(incomplete),
        "incomplete_with_unavailable_food_command": sum(
            any(e["command"]["primitive"] in ("collecter", "manger")
                and not e["complete"] for e in s["edges"])
            for s in incomplete
        ),
        "incomplete_without_unavailable_food_command": sum(
            not any(e["command"]["primitive"] in ("collecter", "manger")
                    and not e["complete"] for e in s["edges"])
            for s in incomplete
        ),
        "no_path_proven_by_unknown_edge": True,
        "necessary_missing_edge_proven": False,
    }
    detailed = {
        "schema": "a230e-real-search-inputs-laboratory-only-v1",
        "birth_id": life["birth_id"],
        "journal_sha256": sha256(
            (folder / "canonical.jsonl").read_bytes()
        ).hexdigest(),
        "prebirth_training": probe.training_examples,
        "searches": probe.searches,
        "counts": counts,
        "epistemic_limit": (
            "Unknown attempted edges are observed. Their necessity for "
            "food-goal achievement has not been independently established."
        ),
    }
    (folder / "a230e-real-search-edges.json").write_text(
        json.dumps(detailed, indent=2, sort_keys=True) + "\n"
    )
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)

    # One deterministic replay control with the SAME artificial identity,
    # never counted as a ninth independent scientific birth.
    replay_folder = args.output_dir / "_technical_replay_control"
    control, _ = run_life(replay_folder, "restored", False, observed=False)
    rows = []
    for profile in PROFILES:
        for blocked in (False, True):
            name = profile + ("-a2" if blocked else "-free")
            path = args.output_dir / name
            life, probe = run_life(path, profile, blocked, observed=True)
            counts = audit_life(path, life, probe)
            row = {
                "profile": profile,
                "obstacle": "A2" if blocked else "free",
                "birth_id": life["birth_id"],
                "physical_steps": life["world_steps"],
                "terminal_status": life["terminal_status"],
                "journal_head": life["journal_head"],
                "dual_judgements": life["dual_judgements"],
                **counts,
            }
            if profile == "restored" and not blocked:
                original = (replay_folder / "canonical.jsonl").read_bytes()
                measured = (path / "canonical.jsonl").read_bytes()
                if original != measured:
                    raise AssertionError(
                        "read-only probe changed deterministic canonical life"
                    )
                if (control["world_steps"] != life["world_steps"] or
                    control["journal_head"] != life["journal_head"]):
                    raise AssertionError("same-identity technical replay diverged")
            rows.append(row)
            print("A230E_LIFE " + json.dumps(row, sort_keys=True),
                  flush=True)

    report = {
        "schema": "stage12-a230e-prospective-edge-census-v1",
        "code_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "lives": len(rows),
        "physical_steps": sum(x["physical_steps"] for x in rows),
        "replay_control_steps_excluded": control["world_steps"],
        "deterministic_replay_byte_identical": True,
        "searches": sum(x["searches"] for x in rows),
        "incomplete_searches": sum(x["incomplete_searches"] for x in rows),
        "missing_exact_inputs": sum(x["missing_exact_inputs"] for x in rows),
        "unknown_command": sum(x["unknown_command"] for x in rows),
        "known_command_unseen_state": sum(
            x["known_command_unseen_state"] for x in rows
        ),
        "actual_edges": sum(x["actual_rollout_edges"] for x in rows),
        "unavailability_by_command": dict(sum(
            (Counter(x["missing_commands"]) for x in rows), Counter()
        )),
        "rows": rows,
        "root_cause": "undetermined_without_necessary-edge-proof",
        "operator_validated": False,
        "stage12": "PARTIAL",
        "norm_changed": False,
    }
    (args.output_dir / "a230e-summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print("A230E_SUMMARY " + json.dumps(
        {k: v for k, v in report.items() if k != "rows"},
        sort_keys=True,
    ), flush=True)
    if len(rows) != 8 or report["physical_steps"] != STEPS * len(rows):
        raise SystemExit("incomplete physically executed scientific cohort")


if __name__ == "__main__":
    main()
