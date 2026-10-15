"""A2.30-K: independent read-only archive audit of physical J contrasts.

No new I0 birth, no world step, no oracle feedback. Revalidates old WAL and
canonical events before contrasting acts, food, search, UC and B judgements.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_dual_scope_audit import audit_stage12_dual_scope
from lab.stage12_p48_diversity_audit import audit_stage12_p48_diversity

RUN_ID = 38720764403
EXPECTED_SHA = "73d04843735bdfd60ddbf40ae064057847b614fb"
PROFILES = ("restored", "sustained", "episodic", "marginal")
SEARCH_STATUSES = {
    "plan_found", "partial_progress", "incomplete_model",
    "not_found_within_horizon",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def compare_by_step(first: dict[int, list], second: dict[int, list]):
    """The earliest *physical world step* with unequal public projections."""
    for world_step in sorted(set(first) | set(second)):
        if first.get(world_step, ()) != second.get(world_step, ()):
            return world_step
    return None


def by_step(events: list[dict], kind: str, extract):
    found = defaultdict(list)
    for e in events:
        if e.get("kind") == kind:
            found[e["t_monde"]].append(extract(e))
    return dict(found)


def passive_projections(events: list[dict]) -> dict[str, dict[int, list]]:
    def plan(e):
        data = e["data"]
        diag = data.get("progressive_search_diagnostic") or {}
        return {
            "search_status": diag.get("status"),
            "expanded": diag.get("expanded_states"),
            "unavailable": diag.get("unavailable_edges"),
            "root_candidates": diag.get("root_candidate_edges"),
            "root_known": diag.get("root_available_edges"),
            "root_unknown": diag.get("root_unavailable_edges"),
            "root_label": diag.get("root_model_diagnostic"),
            "proposal_created": data.get("proposal_ref") is not None,
        }
    return {
        "commands": by_step(
            events, "command_experienced",
            lambda e: {
                "primitive": e.get("primitive"),
                "parameters": e.get("parameters"),
            },
        ),
        "capture": by_step(
            events, "perceptual_capture",
            lambda e: {
                "position": e.get("data", {}).get("position"),
                "food": e.get("data", {}).get(
                    "dual_scope_visible_body", {}
                ).get("food"),
                "inventory": e.get("data", {}).get(
                    "agency_visible_inventory"
                ),
            },
        ),
        "planning": by_step(events, "stage6_planning_result", plan),
        "dual_scope": by_step(
            events, "stage12_outcome_responsibility_judgement",
            lambda e: {
                "observed_outcome": e["data"].get("observed_outcome"),
                "subjective_responsibility":
                    e["data"].get("subjective_responsibility"),
                "reason": e["data"].get("reason"),
            },
        ),
    }


def validate_source(folder: Path, profile: str, blocked: bool, enriched: bool):
    mode = "breadth" if enriched else "historical"
    label = profile + ("-a2" if blocked else "-free") + "-" + mode
    base = folder / label
    if not base.is_dir():
        raise ValueError("missing immutable A2.30-J life folder: " + label)
    measures = read_json(base / "a230j-measures.json")
    life = read_json(base / "result.json")
    birth = "i0:stage12:b:" + ("a230j1:" if enriched else "a230j0:")
    birth += profile + (":A2" if blocked else ":free")
    if life["birth_id"] != birth or measures["birth_id"] != birth:
        raise ValueError("wrong or repeated scientific birth")
    if measures["arm"] != ("physical_breadth" if enriched else "historical"):
        raise ValueError("unknown treatment arm in source archive")

    raw = (base / "canonical.jsonl").read_bytes()
    if sha256(raw).hexdigest() != measures["journal_sha256"]:
        raise ValueError("journal SHA mismatch with measurement receipt")
    if life["journal_sha256"] != measures["journal_sha256"]:
        raise ValueError("journal SHA mismatch with independent life report")
    anchor = {
        "expected_head": life["journal_head"],
        "expected_count": life["journal_count"],
    }
    external = audit_export_bytes(raw, **anchor)
    wal = HashChainedJournal.audit_durable_wal(str(base / "life.wal"))
    if (wal["head_hash"] != anchor["expected_head"] or
            wal["verified_entries"] != anchor["expected_count"]):
        raise ValueError("M11 durable WAL head/count diverge")
    if external.world_steps_closed != life["world_steps"]:
        raise ValueError("physical world-step count diverges")
    dual = audit_stage12_dual_scope(raw, **anchor)
    goal = audit_stage12_goal_progress(raw, **anchor)
    physical = audit_stage12_p48_diversity(raw, **anchor)
    if (
        dual.judgements != measures["dual_judgements"]
        or physical["physically_confirmed_eats"]
        != measures["confirmed_ingestions"]
        or physical["net_food_increase_steps_after_first"]
        != measures["confirmed_food_gain_steps"]
        or physical["physically_distinct_sites"]
        != measures["physically_distinct_sites"]
    ):
        raise ValueError("independent observer disagrees with study receipt")
    events = [json.loads(line)["causal_event"] for line in raw.splitlines()]
    kinds = Counter(e["kind"] for e in events)
    if (kinds["command_experienced"] != measures["world_steps"]
            or kinds["world_transition_experienced"] != measures["world_steps"]
            or kinds["step_closed"] != measures["world_steps"]):
        raise ValueError("canonical physical receipts incomplete")
    statuses = Counter()
    root_gaps = 0
    root_known = 0
    for e in events:
        if e["kind"] != "stage6_planning_result":
            continue
        diag = e.get("data", {}).get("progressive_search_diagnostic")
        if not isinstance(diag, dict):
            raise ValueError("missing search diagnostic from immutable J life")
        if diag.get("status") in SEARCH_STATUSES:
            statuses[diag["status"]] += 1
            root_gaps += diag.get("root_model_diagnostic") == (
                "no_predictable_first_step"
            )
            root_known += diag.get("root_available_edges", 0) > 0
    if (sum(statuses.values()) != measures["searches"]
        or dict(statuses) != measures["stage6_statuses"]
        or root_gaps != measures["no_predictable_first_step"]
        or root_known != measures["first_step_available_searches"]):
        raise ValueError("Stage6 measured-search counts disagree with journal")
    uc_refusals = Counter(
        str(e.get("data", {}).get("operation"))
        for e in events if e["kind"] == "compute_charge"
        and e.get("data", {}).get("accepted") is False
    )
    if dict(uc_refusals) != measures["uc_refusals"]:
        raise ValueError("UC refusal audit diverges")
    measured_primitives = Counter(e.get("primitive") for e in events
                                 if e["kind"] == "command_experienced")
    if dict(measured_primitives) != measures["commands"]:
        raise ValueError("motor command count disagrees with receipt")
    recorded_responsibility = Counter(
        str(e.get("data", {}).get("subjective_responsibility"))
        for e in events
        if e["kind"] == "stage12_outcome_responsibility_judgement"
    )
    if dict(recorded_responsibility) != measures["subjective_responsibility"]:
        raise ValueError("dual-scope judgement counts differ")
    if recorded_responsibility.get("self", 0):
        raise ValueError("false distal self agency in original J archive")
    if kinds["active_goal_changed"] != life["goal_change_receipts"]:
        raise ValueError("goal activation/update receipts incomplete")
    training = measures["training"]
    if not (
        training["preserved_all_historical_predictions"] is True
        and training["unseen_body_input_unavailable"] is True
        and training["unseen_berry_b_unavailable"] is True
    ):
        raise ValueError("missing Equipment abstention and compatibility witness")
    if enriched:
        if (training["historical_examples"] != 4
            or training["physically_applied_extra_examples"] != 46
            or training["training_worlds_born"] != 15
            or training["new_unique_exact_keys"] < 1):
            raise ValueError("treatment is not the pre-registered physical corpus")
        if training["equipment_sha256"] == training["baseline_equipment_sha256"]:
            raise ValueError("treatment Equipment hash not distinct")
    else:
        if (training["historical_examples"] != 4
            or training["physically_applied_extra_examples"] != 0):
            raise ValueError("control Equipment was altered")
    return {
        "label": label,
        "life": life,
        "measures": measures,
        "events": events,
        "projections": passive_projections(events),
        "positions": physical["positions"],
        "P48": physical,
        "WAL_verified": True,
        "dual_verified": dual.judgements,
        "goal_progress_audited": goal.preregistered,
    }


def compare_pair(control: dict, experimental: dict) -> dict:
    x = control["measures"]
    y = experimental["measures"]
    a = control["projections"]
    b = experimental["projections"]
    train0 = x["training"]
    train1 = y["training"]
    if train0["equipment_sha256"] != train1["baseline_equipment_sha256"]:
        raise ValueError("treatment not paired with exact control model")
    if x["world_steps"] != 32 or y["world_steps"] != 32:
        raise ValueError("unexpected early life stop in J original study")
    first_diffs = {
        item: compare_by_step(a[item], b[item]) for item in a
    }
    # Physical frames may be richer than just commands. An unequal frame
    # cannot be dismissed even when the same action primitive was chosen.
    physical_trace_match = (control["positions"] == experimental["positions"])
    return {
        "profile": x["profile"],
        "obstacle": x["obstacle"],
        "historical_equipment_sha256": train0["equipment_sha256"],
        "treatment_equipment_sha256": train1["equipment_sha256"],
        "new_exact_training_keys": train1["new_unique_exact_keys"],
        "added_physical_prebirth_examples":
            train1["physically_applied_extra_examples"],
        "first_different_world_step": first_diffs,
        "physically_observed_positions_identical": physical_trace_match,
        "site_counts": [
            x["physically_distinct_sites"], y["physically_distinct_sites"]
        ],
        "root_known_searches": [
            x["first_step_available_searches"],
            y["first_step_available_searches"],
        ],
        "root_unknown_searches": [
            x["no_predictable_first_step"],
            y["no_predictable_first_step"],
        ],
        "searches": [x["searches"], y["searches"]],
        "confirmed_ingestions": [
            x["confirmed_ingestions"], y["confirmed_ingestions"]
        ],
        "confirmed_food_gains": [
            x["confirmed_food_gain_steps"],
            y["confirmed_food_gain_steps"]
        ],
        "UC_refusals": [x["uc_refusals"], y["uc_refusals"]],
        "distal_judgements": [
            x["subjective_responsibility"],
            y["subjective_responsibility"]
        ],
        "dual_judgement_counts": [
            x["dual_judgements"], y["dual_judgements"]
        ],
    }


def execute(source_dir: Path, output_dir: Path):
    found = list(source_dir.rglob("a230j-summary.json"))
    if len(found) != 1:
        raise ValueError("original J summary must be unique in immutable ZIP")
    root = found[0].parent
    source = read_json(found[0])
    if (
        source.get("schema") != "a230j-prebirth-physical-breadth-v1"
        or source.get("code_sha") != EXPECTED_SHA
        or source.get("new_independent_lives") != 16
        or source.get("physical_world_steps") != 512
        or source.get("searches") != 370
        or source.get("root_zero_known_searches") != 327
        or source.get("ingestions") != 8
    ):
        raise ValueError("wrong preregistered source run or cohort")
    output_dir.mkdir(parents=True, exist_ok=False)
    results = []
    original_ids = set()
    births = 0
    for profile in PROFILES:
        for blocked in (False, True):
            a = validate_source(root, profile, blocked, False)
            b = validate_source(root, profile, blocked, True)
            for life in (a, b):
                identifier = life["measures"]["birth_id"]
                if identifier in original_ids:
                    raise ValueError("duplicate original scientific life ID")
                original_ids.add(identifier)
                births += 1
            paired = compare_pair(a, b)
            results.append(paired)
            (output_dir / (
                profile + ("-a2" if blocked else "-free") +
                "-impact.json"
            )).write_text(json.dumps(paired, indent=2, sort_keys=True) + "\n")
            print("A230K_PAIR " + json.dumps(paired, sort_keys=True), flush=True)
    if births != 16:
        raise ValueError("not exactly sixteen original lives")
    summary = {
        "schema": "stage12-a230k-readonly-paired-impact-v1",
        "source_original_action_run": RUN_ID,
        "source_original_code_sha": EXPECTED_SHA,
        "analysis_code_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "original_lives_audited": births,
        "original_physical_steps_reanalysed": 512,
        "new_independent_births": 0,
        "new_physical_steps": 0,
        "physical_disagreement_pairs": sum(
            not p["physically_observed_positions_identical"] for p in results
        ),
        "different_command_pairs": sum(
            p["first_different_world_step"]["commands"] is not None
            for p in results
        ),
        "different_plan_receipt_pairs": sum(
            p["first_different_world_step"]["planning"] is not None
            for p in results
        ),
        "different_perceived_food_position_pairs": sum(
            p["first_different_world_step"]["capture"] is not None
            for p in results
        ),
        "different_B_judgement_pairs": sum(
            p["first_different_world_step"]["dual_scope"] is not None
            for p in results
        ),
        "UC_refusal_difference_pairs": sum(
            p["UC_refusals"][0] != p["UC_refusals"][1] for p in results
        ),
        "added_prebirth_examples_each_treatment": 46,
        "paired_root_gap_total": [
            sum(p["root_unknown_searches"][0] for p in results),
            sum(p["root_unknown_searches"][1] for p in results),
        ],
        "paired_ingestions_total": [
            sum(p["confirmed_ingestions"][0] for p in results),
            sum(p["confirmed_ingestions"][1] for p in results),
        ],
        "physical_impossibility_proven": False,
        "causal_generalization_proven": False,
        "model_deployed_to_main": False,
        "stage12": "PARTIAL",
        "pairs": results,
    }
    (output_dir / "a230k-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print("A230K_SUMMARY " + json.dumps(
        {k: v for k, v in summary.items() if k != "pairs"},
        sort_keys=True,
    ), flush=True)
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    execute(args.source_dir, args.output_dir)


if __name__ == "__main__":
    main()
