"""A2.30-J prospective physical-corpus breadth contrast for Stage6 food planning.

The only intervention occurs in detached, physically applied *prebirth*
training worlds. No target-life state, Oracle label, or journal is a training
input; the frozen exact Equipment never estimates unseen or dangerous effects.

Preregistered: docs/research/stage12-issue110-b-a230j-prebirth-coverage-prereg-2026-10-15.fr.md
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import run_stage12_issue110_b_a228_funnel as cohort
import run_stage12_issue110_first_planning_state as factory
from i0.equipment import EquipmentCorpus, train_exact_transition_table
from i0.interfaces import PrimitiveCommand
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.stage12_p48_diversity_audit import audit_stage12_p48_diversity
from lab.world import WorldBody

PROFILES = ("restored", "sustained", "episodic", "marginal")
STEPS = 32
REGISTERED_ARMS = {False: "a230j0", True: "a230j1"}
SEARCH_STATUSES = frozenset({
    "plan_found", "partial_progress", "incomplete_model",
    "not_found_within_horizon",
})


def cmd(primitive: str, direction: str | None = None) -> PrimitiveCommand:
    return PrimitiveCommand(
        primitive, {"direction": direction} if direction is not None else
        {"target": "berry_a"} if primitive in {"collecter", "manger"} else {},
    )


def recipes() -> tuple[tuple[str, tuple[PrimitiveCommand, ...]], ...]:
    """Fixed recipes: no choices from observed target-life trajectories."""
    result = []
    for command in (
        cmd("attendre"), cmd("dormir"), cmd("boire"),
        cmd("se_deplacer", "north"), cmd("se_deplacer", "south"),
        cmd("se_deplacer", "east"), cmd("se_deplacer", "west"),
    ):
        suffix = str(command.parameters.get("direction", command.primitive))
        result.append(("birth_" + suffix, (command,)))
    result.extend((
        ("wait_eight", (cmd("attendre"),) * 8),
        ("sleep_four", (cmd("dormir"),) * 4),
    ))
    for delay in (1, 2, 3):
        result.append((
            "delayed_food_" + str(delay),
            (cmd("attendre"),) * delay + (
                cmd("se_deplacer", "north"), cmd("se_deplacer", "east"),
                cmd("collecter"), cmd("manger"),
            ),
        ))
    result.extend((
        ("sleep_then_food", (
            cmd("dormir"), cmd("se_deplacer", "north"),
            cmd("se_deplacer", "east"), cmd("collecter"), cmd("manger"),
        )),
        ("spatial_loop", (
            cmd("se_deplacer", "south"), cmd("se_deplacer", "east"),
            cmd("se_deplacer", "north"), cmd("se_deplacer", "west"),
        )),
    ))
    assert len(result) == 14
    return tuple(result)


def prebirth_candidate(config, layout, original_build, *, food_target: bool,
                       extended: bool = False):
    """Train a distinct immutable physical corpus, before constructing I0.

    Returns (candidate Equipment, external proof); an OFF run uses the
    unmodified original builder directly. This function must never receive a
    living I0 instance, trajectory, experiment result or secret Oracle state.
    """
    if not food_target or extended:
        raise ValueError("A2.30-J allows only baseline food physical corpus")
    original_record = EquipmentCorpusRecorder.record_transition
    baseline_examples = []

    def tap(recorder, *, world, t_monde, family, command):
        example = original_record(
            recorder, world=world, t_monde=t_monde,
            family=family, command=command,
        )
        if (recorder._version ==
                "issue110-lived-north-east-food-physical-v1"):
            baseline_examples.append(example)
        return example

    with patch.object(EquipmentCorpusRecorder, "record_transition", tap):
        baseline = original_build(
            config, layout, food_target=food_target, extended=extended
        )
    if len(baseline_examples) != 4:
        raise AssertionError(
            "historical food examples not recovered from detached training"
        )
    extra = []
    for name, commands in recipes():
        # A new training WorldBody is born for EVERY preregistered recipe.
        # No target life's state or observations enter this loop.
        world = WorldBody(config=config, layout=layout)
        recorder = EquipmentCorpusRecorder(
            corpus_version="a230j-physical-" + name + "-v1"
        )
        for t_monde, command in enumerate(commands, start=1):
            ex = recorder.record_transition(
                world=world, t_monde=t_monde,
                family="a230j_" + name, command=command,
            )
            if ex.terminal:
                raise AssertionError("terminal prebirth training recipe")
            extra.append(ex)
    all_examples = tuple(baseline_examples + extra)
    combined = EquipmentCorpus(
        version="a230j-physical-breadth-v1", examples=all_examples,
    )
    treatment = train_exact_transition_table(
        corpus=combined, equipment_version="E-a230j-breadth-v1",
    )
    # Strict parity for every historically supported key. Equipment.version
    # differs by design; the physical predictions may not.
    for original in baseline_examples:
        a = baseline.predict(state=original.state, command=original.command)
        z = treatment.predict(state=original.state, command=original.command)
        if (a.next_state != z.next_state or a.effects != z.effects
                or a.terminal != z.terminal):
            raise AssertionError("augmented Equipment changed an old prediction")
    # Test an intentionally unobserved hazardous-resource primitive input.
    with_unknown = cmd("manger")  # Historical and expanded berry_a control.
    del with_unknown
    berry_b = PrimitiveCommand("manger", {"target": "berry_b"})
    try:
        treatment.predict(state=baseline_examples[0].state, command=berry_b)
    except LookupError:
        pass
    else:
        raise AssertionError("unseen berry_b unexpectedly became predictable")
    # Nor can food be silently ignored as part of the exact state key.
    first = baseline_examples[0].state
    unseen_body = dict(first.body)
    unseen_body["food"] = float(unseen_body["food"]) + 0.123456789
    unseen = replace(first, body=unseen_body)
    try:
        treatment.predict(state=unseen, command=baseline_examples[0].command)
    except LookupError:
        pass
    else:
        raise AssertionError("unseen bodily context was silently generalized")
    from i0.equipment import FrozenTableEquipment
    old_keys = {
        FrozenTableEquipment.input_digest(e.state, e.command)
        for e in baseline_examples
    }
    added_keys = {
        FrozenTableEquipment.input_digest(e.state, e.command) for e in extra
    }
    return treatment, {
        "baseline_equipment_sha256": baseline.artifact_digest,
        "equipment_sha256": treatment.artifact_digest,
        "historical_examples": len(baseline_examples),
        "physically_applied_extra_examples": len(extra),
        "new_unique_exact_keys": len(added_keys - old_keys),
        "unique_exact_keys_total": len(added_keys | old_keys),
        "duplicate_training_entries": len(all_examples) - len(added_keys | old_keys),
        "training_worlds_born": len(recipes()) + 1,
        "physical_training_attempts": len(all_examples),
        "physical_training_protocol": "a230j-prebirth-fixed-recipes-v1",
        "preserved_all_historical_predictions": True,
        "unseen_berry_b_unavailable": True,
        "unseen_body_input_unavailable": True,
    }


def life_runner(folder: Path, profile: str, blocked: bool, enhanced: bool):
    """Execute one autonomous birth with a frozen pre-birth-only model."""
    original_build = factory.build_prebirth_equipment
    observed_training = []

    def builder(config, layout, *, food_target, extended=False):
        if enhanced:
            model, receipt = prebirth_candidate(
                config, layout, original_build,
                food_target=food_target, extended=extended,
            )
        else:
            model = original_build(
                config, layout, food_target=food_target, extended=extended,
            )
            receipt = {
                "baseline_equipment_sha256": model.artifact_digest,
                "equipment_sha256": model.artifact_digest,
                "historical_examples": 4,
                "physically_applied_extra_examples": 0,
                "new_unique_exact_keys": 0,
                "preserved_all_historical_predictions": True,
                "unseen_berry_b_unavailable": True,
                "unseen_body_input_unavailable": True,
                "physical_training_protocol": "historical-exact-food-v1",
            }
        observed_training.append(receipt)
        return model

    original_steps = cohort.STEPS
    cohort.STEPS = STEPS
    try:
        with patch.object(
            factory, "build_prebirth_equipment", side_effect=builder
        ):
            life = cohort.run_one(
                folder, profile, blocked,
                birth_cohort=REGISTERED_ARMS[enhanced],
            )
    finally:
        cohort.STEPS = original_steps
    if len(observed_training) != 1:
        raise AssertionError("prebirth Equipment was not built exactly once")
    if not life["birth_id"].startswith(
        "i0:stage12:b:" + REGISTERED_ARMS[enhanced] + ":"
    ):
        raise AssertionError("scientific birth namespace collision")
    raw = (folder / "canonical.jsonl").read_bytes()
    physical = audit_stage12_p48_diversity(
        raw, expected_head=life["journal_head"],
        expected_count=life["journal_count"],
    )
    events = [json.loads(line)["causal_event"] for line in raw.splitlines()]
    searches = [
        e["data"]["progressive_search_diagnostic"]
        for e in events if e["kind"] == "stage6_planning_result"
    ]
    actual = [row for row in searches if row.get("status") in SEARCH_STATUSES]
    first_gaps = [
        row for row in actual
        if row.get("root_model_diagnostic") == "no_predictable_first_step"
    ]
    for diag in actual:
        if not all(k in diag for k in (
            "root_candidate_edges", "root_available_edges",
            "root_unavailable_edges", "root_model_diagnostic",
        )):
            raise AssertionError("missing A2.30-I root diagnostic in live search")
        c = diag["root_candidate_edges"]
        a = diag["root_available_edges"]
        u = diag["root_unavailable_edges"]
        if not all(type(v) is int and v >= 0 for v in (c, a, u)):
            raise AssertionError("malformed first-step diagnostic counts")
        if a + u > c:
            raise AssertionError("root diagnostic exceeds offered candidates")
    if any(
        row["status"] != "incomplete_model"
        or row["root_candidate_edges"] == 0
        or row["root_available_edges"] != 0
        or row["root_unavailable_edges"] != row["root_candidate_edges"]
        for row in first_gaps
    ):
        raise AssertionError("fabricated first-step model gap")
    if any(
        e["kind"] == "external_input_received"
        and e.get("operation") == "set_body" for e in events
    ):
        raise AssertionError("forbidden body injection")
    refused_uc = Counter(
        str(e.get("data", {}).get("operation"))
        for e in events if e["kind"] == "compute_charge"
        and e.get("data", {}).get("accepted") is False
    )
    responsibilities = Counter(
        str(e.get("data", {}).get("subjective_responsibility"))
        for e in events
        if e["kind"] == "stage12_outcome_responsibility_judgement"
    )
    if responsibilities.get("self", 0):
        raise AssertionError("unverified distal self responsibility")
    report = {
        "profile": profile, "obstacle": "A2" if blocked else "free",
        "arm": "physical_breadth" if enhanced else "historical",
        "enhanced": enhanced,
        "birth_id": life["birth_id"],
        "world_steps": life["world_steps"],
        "terminal_status": life["terminal_status"],
        "journal_head": life["journal_head"],
        "journal_sha256": life["journal_sha256"],
        "training": observed_training[0],
        "searches": len(actual),
        "stage6_statuses": dict(Counter(x["status"] for x in actual)),
        "no_predictable_first_step": len(first_gaps),
        "first_step_available_searches": sum(
            x["root_available_edges"] > 0 for x in actual
        ),
        "root_available_edge_attempts": sum(
            x["root_available_edges"] for x in actual
        ),
        "root_unavailable_edge_attempts": sum(
            x["root_unavailable_edges"] for x in actual
        ),
        "proposal_receipts": sum(
            e.get("data", {}).get("proposal_ref") is not None
            for e in events if e["kind"] == "stage6_planning_result"
        ),
        "commands": life["command_counts"],
        "food_collect_commands": life["command_counts"].get("collecter", 0),
        "food_eat_commands": life["command_counts"].get("manger", 0),
        "confirmed_ingestions": physical["physically_confirmed_eats"],
        "confirmed_food_gain_steps":
            physical["net_food_increase_steps_after_first"],
        "physically_distinct_sites": physical["physically_distinct_sites"],
        "food_captured_first_last": life["first_person_food"],
        "active_goal_motive_commands":
            life["motive_counts"].get("active_goal", 0),
        "dual_judgements": life["dual_judgements"],
        "subjective_responsibility": dict(responsibilities),
        "uc_refusals": dict(refused_uc),
        "no_oracle_injection": True,
        "fatal_transition_included_only_if_executed": True,
    }
    (folder / "a230j-measures.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print("A230J_LIFE " + json.dumps(report, sort_keys=True), flush=True)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    rows = []
    for profile in PROFILES:
        for blocked in (False, True):
            for enhanced in (False, True):
                label = (
                    profile + ("-a2" if blocked else "-free") +
                    ("-breadth" if enhanced else "-historical")
                )
                rows.append(life_runner(
                    args.output_dir / label, profile, blocked, enhanced
                ))
    paired = []
    for profile in PROFILES:
        for blocked in (False, True):
            old = next(r for r in rows if r["profile"] == profile
                       and (r["obstacle"] == "A2") == blocked
                       and not r["enhanced"])
            new = next(r for r in rows if r["profile"] == profile
                       and (r["obstacle"] == "A2") == blocked
                       and r["enhanced"])
            if (old["training"]["equipment_sha256"] !=
                    new["training"]["baseline_equipment_sha256"]):
                raise AssertionError("unmatched historical training baseline")
            if (old["training"]["equipment_sha256"] ==
                    new["training"]["equipment_sha256"]):
                raise AssertionError("unmodified candidate prebirth model")
            paired.append({
                "profile": profile, "obstacle": old["obstacle"],
                "baseline_steps": old["world_steps"],
                "enhanced_steps": new["world_steps"],
                "baseline_root_unknown": old["no_predictable_first_step"],
                "enhanced_root_unknown": new["no_predictable_first_step"],
                "baseline_root_known": old["first_step_available_searches"],
                "enhanced_root_known": new["first_step_available_searches"],
                "baseline_searches": old["searches"],
                "enhanced_searches": new["searches"],
                "baseline_ingestions": old["confirmed_ingestions"],
                "enhanced_ingestions": new["confirmed_ingestions"],
                "baseline_food_gains": old["confirmed_food_gain_steps"],
                "enhanced_food_gains": new["confirmed_food_gain_steps"],
                "baseline_dual_judgements": old["dual_judgements"],
                "enhanced_dual_judgements": new["dual_judgements"],
            })
    if len({r["birth_id"] for r in rows}) != 16:
        raise AssertionError("scientific births reused")
    summary = {
        "schema": "a230j-prebirth-physical-breadth-v1",
        "code_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "new_independent_lives": len(rows),
        "physical_world_steps": sum(x["world_steps"] for x in rows),
        "planned_max_physical_steps": 16 * STEPS,
        "terminal_statuses": dict(Counter(
            x["terminal_status"] for x in rows
        )),
        "searches": sum(x["searches"] for x in rows),
        "root_zero_known_searches": sum(
            x["no_predictable_first_step"] for x in rows
        ),
        "ingestions": sum(x["confirmed_ingestions"] for x in rows),
        "paired": paired, "lives": rows,
        "prebirth_only": True,
        "no_extrapolated_equipment": True,
        "no_operator_approval": True,
        "issue110": "OPEN", "stage12": "PARTIAL",
    }
    (args.output_dir / "a230j-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print("A230J_SUMMARY " + json.dumps(
        {k: v for k, v in summary.items() if k != "lives"},
        sort_keys=True,
    ), flush=True)
    if len(rows) != 16 or not (
        0 < summary["physical_world_steps"] <= 16 * STEPS
    ):
        raise SystemExit("A2.30-J physical cohort invalid")


if __name__ == "__main__":
    main()
