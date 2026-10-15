"""A2.30-H offline census of exact-key divergence at the Stage6 search root.

Uses A2.30-E original, independently authenticated archives; no new lives,
no cognitive feedback, no prediction fallback and no assumed physical cause.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from audit_stage12_issue110_b_a230g_graph_witness import (
    EXPECTED_INCOMPLETE,
    RUN_ID,
    EXPECTED_SHA,
    validate_archives,
)
from lab.determinism import canonical_causal_bytes, sha256_hex

FIELDS = (
    "schema_version", "x", "y", "body", "inventory",
    "current_water_source", "current_resources", "adjacent",
    "known_shelter_here", "is_night",
)


def hashed_input(state: dict, command: dict) -> str:
    """Exact serialization contract of FrozenTableEquipment, not physics."""
    return sha256_hex(canonical_causal_bytes({
        "state": state, "command": command,
    }))


def field_difference(a: dict, b: dict) -> tuple[str, ...]:
    return tuple(name for name in FIELDS if a[name] != b[name])


def expanded_field_difference(a: dict, b: dict) -> tuple[str, ...]:
    """Descriptive feature mismatch, never a licensed generalization key."""
    features: set[str] = set()
    for key in FIELDS:
        if a[key] == b[key]:
            continue
        if key in ("body", "inventory"):
            for subkey in set(a[key]) | set(b[key]):
                if a[key].get(subkey) != b[key].get(subkey):
                    features.add(f"{key}.{subkey}")
        elif key == "adjacent":
            aa = {c["direction"]: c for c in a["adjacent"]}
            bb = {c["direction"]: c for c in b["adjacent"]}
            for direction in sorted(set(aa) | set(bb)):
                if direction not in aa or direction not in bb:
                    features.add(f"adjacent.{direction}.presence")
                    continue
                for prop in set(aa[direction]) | set(bb[direction]):
                    if aa[direction].get(prop) != bb[direction].get(prop):
                        features.add(f"adjacent.{direction}.{prop}")
        else:
            features.add(key)
    return tuple(sorted(features))


def categorize_root_edge(edge: dict, initial_state: dict,
                         training: list[dict]) -> dict:
    """Recheck E's edge reason and original exact-key membership."""
    if edge["state_sha256"] != sha256_hex(
        canonical_causal_bytes(initial_state)
    ):
        raise ValueError("root state SHA is inconsistent with observed input")
    cmd = edge["command"]
    actual = hashed_input(initial_state, cmd)
    if actual != edge["input_sha256"]:
        raise ValueError("root command/input key is not reproducible")
    if edge["complete"]:
        raise ValueError("this H audit expects the root unknown-only subset")
    if edge["reason"] != "equipment_input_unseen":
        return {
            "category": "other_unavailability",
            "reason": edge["reason"],
            "command": cmd,
            "differences": (),
            "top_fields": (),
        }

    training_hashes = {t["input_sha256"] for t in training}
    if actual in training_hashes:
        raise ValueError("trained original input refused by Equipment")
    examples = [t for t in training if t["command"] == cmd]
    if not examples:
        if edge["category"] != "unseen_command":
            raise ValueError("actual command-coverage category mismatch")
        return {
            "category": "unseen_command",
            "reason": edge["reason"],
            "command": cmd,
            "differences": (),
            "top_fields": (),
        }

    closest = min(
        examples,
        key=lambda t: (
            len(field_difference(initial_state, t["state"])),
            field_difference(initial_state, t["state"]),
            t["input_sha256"],
        ),
    )
    top_fields = field_difference(initial_state, closest["state"])
    if not top_fields:
        raise ValueError("identical trained command state was rejected")
    if (
        edge["category"] != "unseen_state_for_known_command"
        or tuple(edge["nearest_differing_fields"]) != top_fields
    ):
        raise ValueError("nearest input mismatch classification changed")
    return {
        "category": "unseen_state_for_known_command",
        "reason": edge["reason"],
        "command": cmd,
        "differences": expanded_field_difference(
            initial_state, closest["state"]
        ),
        "top_fields": top_fields,
    }


def examine_life(detail: dict, life: dict) -> dict:
    training = detail["prebirth_training"]
    for t in training:
        if hashed_input(t["state"], t["command"]) != t["input_sha256"]:
            raise ValueError("physical prebirth training key mismatch")
    rows = []
    categories = Counter()
    reasons = Counter()
    primitives = Counter()
    fields = Counter()
    top_fields = Counter()
    timesteps = Counter()
    measures = Counter()
    samples_with_food_action = 0
    root_attempts = 0
    for search in detail["searches"]:
        if search["status"] != "incomplete_model":
            continue
        root = search["initial_state_sha256"]
        init = search["initial_accessible_state"]
        if sha256_hex(canonical_causal_bytes(init)) != root:
            raise ValueError("first-person root state hash mismatch")
        root_edges = [e for e in search["edges"]
                      if e["state_sha256"] == root]
        if not root_edges:
            raise ValueError("no initial command candidates observed")
        if any(e["complete"] for e in root_edges):
            raise ValueError("A2.30-G zero-known-root result contradicted")
        if len(root_edges) != len(search["candidate_states"][0][
                "candidate_commands"]):
            raise ValueError("truncated action candidates at root")
        root_attempts += len(root_edges)
        has_food = False
        for edge in root_edges:
            classifier = categorize_root_edge(edge, init, training)
            category = classifier["category"]
            primitive = edge["command"]["primitive"]
            has_food |= primitive in ("collecter", "manger")
            categories[category] += 1
            reasons[classifier["reason"]] += 1
            primitives[primitive] += 1
            fields.update(classifier["differences"])
            top_fields.update(classifier["top_fields"])
        samples_with_food_action += bool(has_food)
        timesteps[str(search["step_attempt"])] += 1
        measures[str(search["progress_measure"])] += 1
        rows.append({
            "search_ordinal": search["ordinal"],
            "step_attempt": search["step_attempt"],
            "progress_measure": search["progress_measure"],
            "root_food": init["body"]["food"],
            "root_water": init["body"]["water"],
            "root_energy": init["body"]["energy"],
            "root_position": [init["x"], init["y"]],
            "first_step_candidate_count": len(root_edges),
            "has_food_candidate": has_food,
            "root_unavailable_by_command": dict(
                Counter(e["command"]["primitive"] for e in root_edges)
            ),
            "root_coverage_category": dict(Counter(
                categorize_root_edge(e, init, training)["category"]
                for e in root_edges
            )),
        })
    return {
        "birth_id": life["birth_id"],
        "original_world_steps": life["world_steps"],
        "incomplete_searches": len(rows),
        "root_unavailable_attempts": root_attempts,
        "root_unavailability_reasons": dict(reasons),
        "root_coverage_categories": dict(categories),
        "root_unavailable_primitives": dict(primitives),
        "closest_training_top_differing_fields": dict(top_fields),
        "closest_training_nested_differences": dict(fields),
        "searches_with_food_command_candidate": samples_with_food_action,
        "searches_without_food_command_candidate":
            len(rows) - samples_with_food_action,
        "incomplete_by_world_step": dict(timesteps),
        "progress_measures": dict(measures),
        "search_roots": rows,
        "causal_necessity_of_any_one_differing_field_proven": False,
        "physical_impossibility_proven": False,
    }


def execute(source_dir: Path, output_dir: Path) -> dict:
    source, lives = validate_archives(source_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    rows = []
    for label, detail, life in lives:
        row = examine_life(detail, life)
        row["label"] = label
        rows.append(row)
        (output_dir / (label + "-root-state.json")).write_text(
            json.dumps(row, indent=2, sort_keys=True) + "\n"
        )
        print("A230H_LIFE " + json.dumps({
            k: v for k, v in row.items() if k not in (
                "search_roots", "incomplete_by_world_step"
            )
        }, sort_keys=True), flush=True)
    def total_of(field):
        return dict(sum((Counter(row[field]) for row in rows), Counter()))
    result = {
        "schema": "stage12-a230h-root-key-mismatch-v1",
        "source_action_run": RUN_ID,
        "original_physical_steps_reanalysed": source["physical_steps"],
        "original_births_reanalysed": len(rows),
        "new_lives": 0,
        "new_physical_steps": 0,
        "source_sha": EXPECTED_SHA,
        "analysis_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "incomplete_searches": sum(r["incomplete_searches"] for r in rows),
        "root_unavailable_attempts": sum(
            r["root_unavailable_attempts"] for r in rows
        ),
        "root_coverage_categories": total_of("root_coverage_categories"),
        "root_unavailability_reasons": total_of("root_unavailability_reasons"),
        "root_unavailable_primitives": total_of("root_unavailable_primitives"),
        "closest_training_top_differing_fields":
            total_of("closest_training_top_differing_fields"),
        "closest_training_nested_differences":
            total_of("closest_training_nested_differences"),
        "searches_with_food_command_candidate": sum(
            r["searches_with_food_command_candidate"] for r in rows
        ),
        "searches_without_food_command_candidate": sum(
            r["searches_without_food_command_candidate"] for r in rows
        ),
        "incomplete_by_world_step": total_of("incomplete_by_world_step"),
        "progress_measures": total_of("progress_measures"),
        "causal_source_of_state_divergence": "undetermined",
        "field_relevance_or_safe_generalization_proven": False,
        "runtime_change": False,
        "stage12": "PARTIAL",
        "rows": [{k: v for k, v in r.items() if k not in (
            "search_roots", "incomplete_by_world_step"
        )} for r in rows],
    }
    if (
        result["incomplete_searches"] != EXPECTED_INCOMPLETE
        or result["root_unavailable_attempts"] != sum(
            result["root_coverage_categories"].values()
        )
        or result["searches_with_food_command_candidate"]
        + result["searches_without_food_command_candidate"]
        != EXPECTED_INCOMPLETE
    ):
        raise ValueError("inconsistent model-root key totals")
    (output_dir / "a230h-summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print("A230H_SUMMARY " + json.dumps(
        {k: v for k, v in result.items() if k not in (
            "rows", "incomplete_by_world_step"
        )}, sort_keys=True
    ), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    execute(args.source_dir, args.output_dir)


if __name__ == "__main__":
    main()
