"""A2.30-O: archive-only independent audit of preregistered A2.30-N.

NEVER imports the candidate prototype/runner, WorldBody or Oracle. Reads
unchanged original GitHub Actions artifacts from both Python versions, verifies
byte-level parity and recomputes all scores from the archived physical
examples. Cannot independently prove physics was applied from JSON alone.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from lab.determinism import canonical_causal_bytes, sha256_hex

EXPECTED_N_SHA = "d62a92d7f0a773a411de2e65ce2c2467be9efb48"
ORIGINAL_RUN = 38726664498
FILE_HASHES = {
    "a230n-training-manifest.json":
        "948dc97de8ff6fc447ea5047699d99691892e3299108ee4a21c0cdd5f6232af1",
    "a230n-heldout-physical-results.json":
        "2c40322e5b4810ccdd088ec104172a07dc2bd53d32544055d1a84a58942c8947",
    "a230n-summary.json":
        "719978de013674e3370d9fd39f9f35726888469dfd62d41575b06570d1bd0c21",
}
EXPECTED_STRATA = {
    "interpolation": 28, "hidden_lethal_move": 6,
    "hidden_toxic_food": 12, "visible_blocked_move": 4,
    "unseen_command": 4, "hidden_physics_shift": 8,
}
BODY = ("energy", "food", "water", "integrity")
INV = ("berry_a", "berry_b", "wood", "stone", "tool")
COLUMNS = (
    "dx", "dy", *(f"body.{name}" for name in BODY),
    *(f"inventory.{name}" for name in INV),
)


def canonical_sha(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def key_of(state, command):
    return canonical_sha({"state": state, "command": command})


def independent_context(state, command):
    """Alternate implementation of the published projection."""
    prim = command["primitive"]
    params = command["parameters"]
    context = {
        "is_night": bool(state["is_night"]),
        "primitive": prim,
        "parameters": params,
    }
    if prim == "se_deplacer":
        neighbor = {
            n["direction"]: n for n in state["adjacent"]
        }.get(params.get("direction"))
        if neighbor is None:
            context["visible_neighbor"] = {"present": False}
        else:
            context["visible_neighbor"] = {
                "present": True,
                "passable": bool(neighbor["passable"]),
                "creature": bool(neighbor["creature"]),
            }
    elif prim == "collecter":
        context["resource_visible_here"] = (
            params.get("target") in state["current_resources"]
        )
        context["tool_present"] = int(state["inventory"].get("tool", 0)) > 0
    elif prim == "manger":
        context["held_food_available"] = (
            int(state["inventory"].get(params.get("target"), 0)) > 0
        )
    elif prim == "boire":
        context["water_source_here"] = bool(state["current_water_source"])
    elif prim in ("attendre", "dormir"):
        context["known_shelter_here"] = bool(state["known_shelter_here"])
    else:
        context["unsupported_feature_policy"] = True
    return canonical_sha(context)


def independent_delta(state, after):
    d = {
        "dx": float(after["x"] - state["x"]),
        "dy": float(after["y"] - state["y"]),
    }
    for name in BODY:
        d["body." + name] = (
            float(after["body"][name]) - float(state["body"][name])
        )
    for name in INV:
        d["inventory." + name] = (
            float(after["inventory"].get(name, 0))
            - float(state["inventory"].get(name, 0))
        )
    if set(d) != set(COLUMNS):
        raise ValueError("unsupported hidden columns")
    return d


def harmful(state, after, terminal):
    return bool(terminal) or (
        float(after["body"]["integrity"])
        < float(state["body"]["integrity"])
    )


def check_training(training):
    examples = training["trained_target_examples"]
    provenance = training["source_provenance"]
    if len(examples) != 42 or len(provenance) != 42:
        raise ValueError("wrong number of physical training examples")
    corpus = {
        "version": "a230n-real-independent-training-physical-v1",
        "examples": examples,
    }
    if canonical_sha(corpus) != training["corpus_sha256"]:
        raise ValueError("physical training corpus SHA mismatch")
    if (training["training_worlds"] != 42
            or training["physical_training_steps"] != 54):
        raise ValueError("wrong training world or physical step count")
    exact = {}
    groups = defaultdict(list)
    IDs = set()
    count_steps = 0
    for ex, receipt in zip(examples, provenance):
        world_id = receipt["id"]
        if world_id in IDs or not world_id.startswith("train-"):
            raise ValueError("duplicate/nontraining world in source")
        IDs.add(world_id)
        if (not receipt["real_worldbody_apply"]
                or receipt["physical_example_sha256"] != canonical_sha(ex)
                or receipt["input_sha256"] != key_of(ex["state"], ex["command"])
                or receipt["terminal"] != ex["terminal"]
                or receipt["kind"] not in (
                    "wait", "sleep", "move_east", "collect_a",
                    "eat_a", "eat_b", "drink",
                )):
            raise ValueError("tampered physical training receipt")
        expected_command_steps = (
            2 if receipt["kind"] in ("eat_a", "eat_b") else 1
        )
        if receipt["physical_steps"] != expected_command_steps:
            raise ValueError("incorrect training preparatory actions")
        count_steps += expected_command_steps
        input_digest = key_of(ex["state"], ex["command"])
        if input_digest in exact and (
            exact[input_digest]["observed_next_state"] !=
                ex["observed_next_state"]
            or exact[input_digest]["terminal"] != ex["terminal"]
        ):
            raise ValueError("conflicting training exact-key outputs")
        exact[input_digest] = ex
        groups[independent_context(ex["state"], ex["command"])].append(ex)
    if count_steps != 54 or len(exact) != 42 or len(groups) != 7:
        raise ValueError("training coverage/provenance inconsistent")
    return exact, groups, IDs


def _score_one(row, exact, groups):
    if row["stratum"] not in EXPECTED_STRATA:
        raise ValueError("invalid test stratum")
    cell = row["cell"]
    truth = row["actual"]
    if not cell["real_worldbody_apply"]:
        raise ValueError("nonphysical heldout receipt")
    obs = truth["state"]
    command = truth["command"]
    after = truth["next_state"]
    terminal = truth["terminal"]
    if (
        cell["input_sha256"] != key_of(obs, command)
        or cell["terminal"] != terminal
    ):
        raise ValueError("tampered test input/terminal")
    if cell["kind"] not in (
        "wait", "sleep", "move_east", "collect_a", "eat_a",
        "eat_b", "drink", "unknown_craft",
    ):
        raise ValueError("unknown target action in heldout")
    reconstruction = {
        "family": "preregistered_target_" + cell["kind"],
        "state": obs, "command": command,
        "observed_next_state": after, "terminal": terminal,
    }
    if canonical_sha(reconstruction) != cell["physical_example_sha256"]:
        raise ValueError("tampered heldout physical consequence SHA")
    if cell["physical_steps"] != (
        2 if cell["kind"] in ("eat_a", "eat_b") else 1
    ):
        raise ValueError("incorrect actual physics steps per test world")
    delta = independent_delta(obs, after)
    if delta != truth["delta"]:
        raise ValueError("test delta contradicts actual transition")
    actually_harmful = harmful(obs, after, terminal)
    if actually_harmful != truth["observed_harm"]:
        raise ValueError("physical harm label corrupted")
    c = row["candidate"]
    if c["certifies_safe"] is not False:
        raise ValueError("prototype invented a safety guarantee")
    if row["always_abstain"] != {
        "available": False, "certifies_safe": False
    }:
        raise ValueError("all-abstain control no longer abstains")
    group_key = independent_context(obs, command)
    if c["group_key"] != group_key:
        raise ValueError("candidate group illicitly depends on test outcome")
    trained = groups.get(group_key, [])
    if trained:
        bounds = {
            axis: (
                min(independent_delta(e["state"], e["observed_next_state"])[axis]
                    for e in trained),
                max(independent_delta(e["state"], e["observed_next_state"])[axis]
                    for e in trained),
            )
            for axis in COLUMNS
        }
        lower = {name: interval[0] for name, interval in bounds.items()}
        upper = {name: interval[1] for name, interval in bounds.items()}
        expected_risk = (
            "observed_harm" if any(
                harmful(e["state"], e["observed_next_state"], e["terminal"])
                for e in trained
            ) else "unknown_hidden_risk"
        )
        terminal_set = sorted({e["terminal"] for e in trained})
        missed = [
            axis for axis in COLUMNS
            if delta[axis] < lower[axis] - 1e-8
            or delta[axis] > upper[axis] + 1e-8
        ]
        terminal_miss = terminal not in terminal_set
        width_sum = sum(upper[k] - lower[k] for k in COLUMNS)
        if (
            c["status"] != "uncertain_interval"
            or c["support_count"] != len(trained)
            or c["risk_label"] != expected_risk
            or c["lower"] != lower
            or c["upper"] != upper
            or c["observed_terminal_values"] != terminal_set
            or c["available"] is not True
            or c["all_delta_dimensions_covered"] != (not missed)
            or c["interval_miss_fields"] != missed
            or c["terminal_outside_empirical_set"] != terminal_miss
            or abs(c["empirical_interval_width_sum"] - width_sum) > 1e-8
        ):
            raise ValueError("candidate forecast/interval false or altered")
    else:
        missed = []
        terminal_miss = False
        if (
            c["status"] != "abstain_unknown_context"
            or c["support_count"] != 0
            or c["risk_label"] != "unavailable"
            or c["lower"] is not None
            or c["upper"] is not None
            or c["observed_terminal_values"] != []
            or c["available"] is not False
            or c["all_delta_dimensions_covered"] is not None
            or c["interval_miss_fields"] != []
            or c["terminal_outside_empirical_set"] is not None
            or c["empirical_interval_width_sum"] is not None
        ):
            raise ValueError("unknown-context abstention was altered")
    exact_prediction = exact.get(key_of(obs, command))
    recorded = row["exact"]
    if exact_prediction is None:
        if recorded != {
            "available": False, "nominal_model_confidence": None,
            "next_state_exact": None, "predicted_terminal": None,
            "external_naive_safe_proxy": False,
            "external_naive_false_safe_proxy": False,
        }:
            raise ValueError("exact baseline hallucinated unseen input")
        naive_false_safe = False
        exact_correct = False
    else:
        pred_after = exact_prediction["observed_next_state"]
        pred_terminal = exact_prediction["terminal"]
        exact_correct = pred_after == after and pred_terminal == terminal
        proxy = (
            not pred_terminal
            and pred_after["body"]["integrity"] >= obs["body"]["integrity"]
        )
        naive_false_safe = proxy and actually_harmful
        if recorded != {
            "available": True, "nominal_model_confidence": 1.0,
            "next_state_exact": exact_correct,
            "predicted_terminal": pred_terminal,
            "external_naive_safe_proxy": proxy,
            "external_naive_false_safe_proxy": naive_false_safe,
        }:
            raise ValueError("exact baseline and external proxy incorrectly scored")
    return {
        "stratum": row["stratum"],
        "world_id": cell["id"],
        "physical_steps": cell["physical_steps"],
        "unsafe": actually_harmful,
        "interval_available": bool(trained),
        "interval_all_covered": bool(trained) and not missed,
        "interval_miss": bool(missed),
        "integrity_miss": "body.integrity" in missed,
        "food_miss": "body.food" in missed,
        "terminal_miss": terminal_miss,
        "risk_label": c["risk_label"],
        "exact_available": exact_prediction is not None,
        "exact_correct": exact_correct,
        "proxy_false_safe": naive_false_safe,
    }


def review_sources(training, rows, summary):
    if (
        summary.get("schema") != "a230n-independent-physical-uncertain-model-v1"
        or summary.get("analysis_sha") != EXPECTED_N_SHA
        or summary.get("new_i0_lives") != 0
        or summary.get("new_i0_autonomous_steps") != 0
        or summary.get("deployable_to_i0") is not False
        or summary.get("candidate_safety_certificates") != 0
        or summary.get("oracle_to_i0_feedback") is not False
    ):
        raise ValueError("source summary is not preregistered N experiment")
    exact, groups, training_ids = check_training(training)
    if summary["training_corpus_sha256"] != training["corpus_sha256"]:
        raise ValueError("training source hash inconsistent")
    if len(rows) != 62:
        raise ValueError("not 62 separate heldout test worlds")
    recomputed = []
    test_ids = set()
    for row in rows:
        record = _score_one(row, exact, groups)
        ident = record["world_id"]
        if (ident in test_ids or ident in training_ids
                or ident.startswith("train-")):
            raise ValueError("test source contaminated by training world")
        test_ids.add(ident)
        recomputed.append(record)
    if sum(x["physical_steps"] for x in recomputed) != 82:
        raise ValueError("test physically executed step count incongruent")
    if (summary["train_worlds"],summary["train_physical_steps"],
        summary["heldout_worlds"],summary["heldout_physical_steps"]
    ) != (42,54,62,82):
        raise ValueError("source physical world/step accounting drift")
    expected_counts = {
        "candidate_available": sum(
            rec["interval_available"] for rec in recomputed
        ),
        "exact_available": sum(rec["exact_available"] for rec in recomputed),
        "candidate_interval_misses": sum(
            rec["interval_miss"] for rec in recomputed
        ),
        "candidate_terminal_set_misses": sum(
            rec["terminal_miss"] for rec in recomputed
        ),
        "exact_external_false_safe_proxy": sum(
            rec["proxy_false_safe"] for rec in recomputed
        ),
    }
    for key, actual in expected_counts.items():
        if summary[key] != actual:
            raise ValueError("source aggregate altered: " + key)
    for stratum, expected_worlds in EXPECTED_STRATA.items():
        subset = [x for x in recomputed if x["stratum"] == stratum]
        report = summary["strata"][stratum]
        audit = {
            "worlds": len(subset),
            "physically_unsafe": sum(x["unsafe"] for x in subset),
            "candidate_available": sum(
                x["interval_available"] for x in subset
            ),
            "candidate_abstained": sum(
                not x["interval_available"] for x in subset
            ),
            "candidate_all_dimensions_covered": sum(
                x["interval_all_covered"] for x in subset
            ),
            "candidate_interval_misses": sum(
                x["interval_miss"] for x in subset
            ),
            "candidate_terminal_set_misses": sum(
                x["terminal_miss"] for x in subset
            ),
            "candidate_integrity_delta_misses": sum(
                x["integrity_miss"] for x in subset
            ),
            "candidate_body_food_delta_misses": sum(
                x["food_miss"] for x in subset
            ),
            "candidate_observed_harm_labels": sum(
                x["risk_label"] == "observed_harm" for x in subset
            ),
            "candidate_unknown_risk_labels": sum(
                x["risk_label"] == "unknown_hidden_risk" for x in subset
            ),
            "candidate_safety_certificates": 0,
            "exact_available": sum(x["exact_available"] for x in subset),
            "exact_exact_outcome": sum(x["exact_correct"] for x in subset),
            "exact_external_false_safe_proxy": sum(
                x["proxy_false_safe"] for x in subset
            ),
            "always_abstain_coverage": 0,
        }
        if len(subset) != expected_worlds or audit != report:
            raise ValueError("independent test stratum counters differ: " + stratum)
    return {
        **expected_counts,
        "physical_worlds_claimed_in_source": 104,
        "physical_steps_claimed_in_source": 136,
        "training_group_count": len(groups),
        "independently_recomputed_all_62_records": True,
        "raw_physical_worldbody_execution_independently_proven": False,
        "new_lives": 0,
        "new_physical_steps": 0,
        "always_abstain_coverage": 0,
        "candidate_safety_certificates": 0,
        "stage12": "PARTIAL",
    }


def read_source(directory: Path):
    loaded = {}
    for name, sha in FILE_HASHES.items():
        hits = list(directory.rglob(name))
        if len(hits) != 1:
            raise ValueError("missing or ambiguous original archive: " + name)
        content = hits[0].read_bytes()
        if sha256(content).hexdigest() != sha:
            raise ValueError("original archive JSON digest changed: " + name)
        loaded[name] = content
    return loaded


def execute(source_a: Path, source_b: Path, output_dir: Path):
    a = read_source(source_a)
    b = read_source(source_b)
    if a != b:
        raise ValueError("Python 3.11 vs 3.12 original artifacts differ in bytes")
    result = review_sources(
        json.loads(a["a230n-training-manifest.json"]),
        json.loads(a["a230n-heldout-physical-results.json"]),
        json.loads(a["a230n-summary.json"]),
    )
    result.update({
        "schema": "stage12-a230o-independent-archive-audit-v1",
        "original_n_run": ORIGINAL_RUN,
        "source_n_sha": EXPECTED_N_SHA,
        "analysis_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "source_artifact_json_digests": FILE_HASHES,
        "python_311_312_archives_equal": True,
        "source_prototype_or_runner_imported": False,
        "conclusion": "bounded_technical_validation_only",
    })
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "a230o-summary.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    print("A230O_SUMMARY " + json.dumps(result, sort_keys=True), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-a", type=Path, required=True)
    ap.add_argument("--source-b", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    execute(args.source_a, args.source_b, args.output_dir)


if __name__ == "__main__":
    main()
