"""A2.30-I behavioral parity after adding Stage6 diagnostic fields.

Deterministic *technical replay* of old A2.30-E births (same identities).
Compares original canonical archives against new physically executed lives.
Technical replays are NOT new independent scientific samples. Journal hashes
are expected to change due to additive, versioned diagnostic data.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

import run_stage12_issue110_b_a228_funnel as cohort
from audit_stage12_issue110_b_a230g_graph_witness import (
    validate_archives, EXPECTED_PROFILES, RUN_ID, EXPECTED_SHA,
)

STEPS = 24
ORIGINAL_DIAGNOSTIC_FIELDS = (
    "status", "expanded_states", "unavailable_edges", "partial_progress",
)


def records(raw: bytes) -> list[dict]:
    return [json.loads(line)["causal_event"]
            for line in raw.splitlines()]


def projection(events: list[dict]) -> dict:
    def of_kind(kind):
        return [e for e in events if e.get("kind") == kind]

    def body_capture(e):
        data = e.get("data", {})
        return {
            "world_step": e.get("t_monde"),
            "position": data.get("position"),
            "visible_body": data.get("dual_scope_visible_body"),
            "visible_inventory": data.get("agency_visible_inventory"),
        }

    search = []
    for e in of_kind("stage6_planning_result"):
        data = e["data"]
        diag = data.get("progressive_search_diagnostic")
        search.append({
            "world_step": e.get("t_monde"),
            "proposal_exists": data.get("proposal_ref") is not None,
            "goal_exists": data.get("goal_ref") is not None,
            "planning_version": data.get("planning_version"),
            "equipment_version": data.get("equipment_version"),
            "diagnostic": (
                None if not isinstance(diag, dict)
                else {k: diag.get(k) for k in ORIGINAL_DIAGNOSTIC_FIELDS}
            ),
        })
    return {
        "event_count": len(events),
        "event_kinds": dict(Counter(e.get("kind") for e in events)),
        "commands": [
            {
                "world_step": e.get("t_monde"),
                "primitive": e.get("primitive"),
                "parameters": e.get("parameters"),
            }
            for e in of_kind("command_experienced")
        ],
        "perceptual_captures": [
            body_capture(e) for e in of_kind("perceptual_capture")
        ],
        "stage6_search_receipts": search,
        "proximal_agency_judgements": [
            (e.get("t_monde"), e["data"].get("subjective_agency"))
            for e in of_kind("stage12_goal_agency_judgement")
        ],
        "distal_responsibility_judgements": [
            (
                e.get("t_monde"),
                e["data"].get("observed_outcome"),
                e["data"].get("subjective_responsibility"),
            )
            for e in of_kind("stage12_outcome_responsibility_judgement")
        ],
    }


def verify_additive_only(old: list[dict], new: list[dict]) -> dict:
    a = projection(old)
    z = projection(new)
    for name in a:
        if a[name] != z[name]:
            raise AssertionError(
                "Stage6 diagnostic-only change modified " + name
                + f" (before {str(a[name])[:400]}, after {str(z[name])[:400]})"
            )
    prev = [
        e for e in old if e["kind"] == "stage6_planning_result"
        and isinstance(e.get("data", {}).get("progressive_search_diagnostic"), dict)
    ]
    curr = [
        e for e in new if e["kind"] == "stage6_planning_result"
        and isinstance(e.get("data", {}).get("progressive_search_diagnostic"), dict)
    ]
    if len(prev) != len(curr):
        raise AssertionError("new diagnostic changed number of planning receipts")
    new_counts = Counter()
    for old_e, new_e in zip(prev, curr):
        old_diag = old_e["data"]["progressive_search_diagnostic"]
        new_diag = new_e["data"]["progressive_search_diagnostic"]
        if all(k in old_diag for k in ORIGINAL_DIAGNOSTIC_FIELDS):
            for f in ("root_candidate_edges", "root_available_edges",
                      "root_unavailable_edges", "root_model_diagnostic"):
                if f not in new_diag:
                    raise AssertionError("missing new additive root diagnostic")
            c = new_diag["root_candidate_edges"]
            known = new_diag["root_available_edges"]
            unknown = new_diag["root_unavailable_edges"]
            if not all(type(v) is int and v >= 0 for v in (c, known, unknown)):
                raise AssertionError("malformed root edge counts")
            if known + unknown > c:
                raise AssertionError("root attempts exceed candidates")
            root_reason = new_diag["root_model_diagnostic"]
            if root_reason == "no_predictable_first_step":
                if not (new_diag["status"] == "incomplete_model"
                        and c > 0 and known == 0 and unknown == c):
                    raise AssertionError("incorrect first-step gap classification")
            elif root_reason not in (
                "at_least_one_predictable_first_step", "not_classified"
            ):
                raise AssertionError("new unrecognized model diagnostic")
            new_counts[root_reason] += 1
    return {
        "physical_commands_compared": len(a["commands"]),
        "perceptual_captures_compared": len(a["perceptual_captures"]),
        "stage6_receipts_compared": len(a["stage6_search_receipts"]),
        "proximal_judgements_compared": len(a["proximal_agency_judgements"]),
        "distal_judgements_compared":
            len(a["distal_responsibility_judgements"]),
        "new_diagnostic_counts": dict(new_counts),
        "semantic_parity": True,
    }


def execute(source_dir: Path, output_dir: Path):
    source_summary, old_lives = validate_archives(source_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    old_steps = cohort.STEPS
    cohort.STEPS = STEPS
    try:
        results = []
        for name, _, original in old_lives:
            profile = name.split("-")[0]
            obstacle = name.endswith("-a2")
            run_dir = output_dir / name
            new = cohort.run_one(
                run_dir, profile, obstacle, birth_cohort="a230e"
            )
            if new["birth_id"] != original["birth_id"]:
                raise ValueError("technical replay changed source birth identity")
            before_path = (source_dir / "a230e-summary.json").parent
            # Artifact uploader may wrap source files in one directory.
            hits = list(source_dir.rglob(
                "a230e-summary.json"
            ))
            if len(hits) != 1:
                raise AssertionError("source original artifact ambiguous")
            before_path = hits[0].parent / name / "canonical.jsonl"
            original_raw = before_path.read_bytes()
            new_raw = (run_dir / "canonical.jsonl").read_bytes()
            before = records(original_raw)
            after = records(new_raw)
            result = verify_additive_only(before, after)
            if new["world_steps"] != STEPS or original["world_steps"] != STEPS:
                raise AssertionError("technical replay did not complete 24 steps")
            result.update({
                "profile": profile,
                "obstacle": obstacle,
                "birth_id": new["birth_id"],
                "technical_replay_steps": new["world_steps"],
                "original_canonical_head": original["journal_head"],
                "new_canonical_head": new["journal_head"],
                "same_journal_hash_claimed": False,
            })
            results.append(result)
            print("A230I_PARITY_LIFE " + json.dumps(
                result, sort_keys=True
            ), flush=True)
    finally:
        cohort.STEPS = old_steps
    totals = {
        "schema": "stage6-a230i-behavioral-parity-v1",
        "source_immutable_run": RUN_ID,
        "source_code_sha": EXPECTED_SHA,
        "new_code_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "original_independent_lives_compared": len(results),
        "technical_replay_steps": sum(
            x["technical_replay_steps"] for x in results
        ),
        "new_independent_scientific_births": 0,
        "new_independent_scientific_steps": 0,
        "commands_compared": sum(
            x["physical_commands_compared"] for x in results
        ),
        "semantic_decision_parity": True,
        "journal_hash_parity_not_expected": True,
        "stage12": "PARTIAL",
        "model_predictive_coverage_changed": False,
        "world_physics_changed": False,
        "results": results,
    }
    if len(results) != 8 or totals["technical_replay_steps"] != 192:
        raise AssertionError("missing technical parity replay")
    (output_dir / "a230i-parity-summary.json").write_text(
        json.dumps(totals, indent=2, sort_keys=True) + "\n"
    )
    print("A230I_PARITY_SUMMARY " + json.dumps({
        k: v for k, v in totals.items() if k != "results"
    }, sort_keys=True), flush=True)
    return totals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    execute(args.source_dir, args.output_dir)


if __name__ == "__main__":
    main()
