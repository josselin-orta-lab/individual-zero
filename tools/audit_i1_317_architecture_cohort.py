#!/usr/bin/env python3
"""Issue #317: fail-closed matched I1 WAL analysis, no feedback to cognition.

The sole physical authority is independent hash-chain audit of immutable WAL.
Memory proposed/registered/crossed is not equivalent to a real movement.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import mean
from tools.audit_i1_spatial_navigation_314 import audit as audit_wal


def number(value):
    if type(value) in (int, float):
        return float(value)
    if (isinstance(value, dict) and set(value) == {"$f64"}
            and isinstance(value["$f64"], str)):
        return float.fromhex(value["$f64"])
    raise ValueError("invalid WAL floating point representation")


def cohort(root, expected_sha, worlds, seeds):
    root = Path(root)
    expected = {(w, s) for w in worlds for s in seeds}
    rows = {}
    for report_path in sorted(root.rglob("report.json")):
        report = json.loads(report_path.read_text())
        assert report["status"] == "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
        assert report["engine"] == "I1"
        assert report["run"]["git_head"] == expected_sha
        assert report["run"]["custody"] == "wal"
        assert report["run"]["requested_lives"] == 1
        assert report["run"]["requested_steps"] == 300
        assert report["old_cohorts_used_as_oracles"] is False
        assert len(report["lives"]) == 1
        w, seed = report["source"]["preset"], report["run"]["seed"]
        key = (w, seed)
        assert key in expected and key not in rows, key
        life = report["lives"][0]
        assert life["individual_id"] == f"i1:preset:{w}:{seed}:0"
        wal_path = report_path.parent / life["custody_file"]
        assert wal_path.name == "life-01.wal"
        sealed = audit_wal(wal_path)
        assert sealed["independent_hash_chain_verified"] is True
        assert life["journal_head"] == sealed["journal_head"]
        assert life["durable_entries"] == sealed["journal_entries"]
        trajectory = life["steps"]
        assert 0 < len(trajectory) <= 300
        assert trajectory[-1]["journal_head"] == life["journal_head"]
        assert life["lifecycle"] in ("active", "dead")
        assert life["lifecycle"] == "dead" or len(trajectory) == 300
        actions = Counter(s["action_primitive"] for s in trajectory)
        movement_positions = []
        for step in trajectory:
            if step["action_primitive"] == "se_deplacer":
                p = step["position"]
                movement_positions.append((p["x"], p["y"]))
        reversals = sum(
            movement_positions[i] == movement_positions[i-2]
            for i in range(2, len(movement_positions))
        )
        uc = Counter()
        crossed = Counter()
        max_memory_ratio = 0.0
        learned_memory_evaluations = 0
        kinds = Counter()
        with wal_path.open(encoding="utf-8") as stream:
            for line in stream:
                event = json.loads(line)["causal_event"]
                kind = event.get("kind")
                kinds[kind] += 1
                data = event.get("data", {})
                if not isinstance(data, dict):
                    continue
                if kind == "compute_charge" and data.get("accepted"):
                    val = data.get("requested_uc")
                    assert type(val) is int and val >= 0
                    uc[data["operation"]] += val
                elif kind == "competition_cycle":
                    for trace in data.get("traces", ()):
                        ref = str(trace.get("option_ref", ""))
                        if not ref.startswith("option:place-memory:"):
                            continue
                        threshold = number(trace["threshold"])
                        acc = number(trace["accumulator_after"])
                        assert threshold > 0 and acc >= 0
                        max_memory_ratio = max(max_memory_ratio, acc / threshold)
                        if trace.get("crossed"):
                            crossed[ref] += 1
                elif kind == "stage8_option_evaluation":
                    if (str(data.get("option_ref", "")).startswith("option:place-memory:")
                            and data.get("learned_value_status") == "learned"):
                        assert data.get("learned_value") is not None
                        learned_memory_evaluations += 1
        causal = sealed["memory_causality_317"]
        stages = sealed["stages"]
        assert sum(crossed.values()) >= stages["crossed"]
        assert stages["physically_applied"] >= causal[
            "physically_applied_unseen_multihop_first_hops"
        ]
        assert stages["physically_applied"] >= causal[
            "physically_applied_memory_actions_using_prior_td"
        ]
        rows[key] = {
            "world": w, "seed": seed, "sha": expected_sha,
            "life_id": life["individual_id"], "steps": len(trajectory),
            "lifecycle": life["lifecycle"], "journal_head": life["journal_head"],
            "verified_journal_entries": sealed["journal_entries"],
            "preset_digest": report["source"]["sha256"],
            "physics_digest": report["environment"]["world_physics_digest"],
            "initial_body": report["environment"]["initial_body"],
            "spawn": report["environment"]["spawn"],
            "actions": dict(actions), "final_body": trajectory[-1]["body"],
            "final_position": trajectory[-1]["position"],
            "memory_stages": stages, "memory_causality": causal,
            "memory_max_threshold_ratio": max_memory_ratio,
            "learned_memory_evaluations": learned_memory_evaluations,
            "accepted_uc": sum(uc.values()),
            "accepted_uc_by_operation": dict(uc),
            "consolidation_commits": kinds["stage10_consolidation_committed"],
            "immediate_movement_reversals": reversals,
            "fallback_steps": sum(bool(s["fallback_used"]) for s in trajectory),
        }
    if set(rows) != expected:
        raise ValueError(f"missing/duplicate world-seed pairs {sorted(expected-set(rows))}")
    return rows


def summary(rows):
    values = list(rows.values())
    action_totals = sum((Counter(z["actions"]) for z in values), Counter())
    stages = sum((Counter(z["memory_stages"]) for z in values), Counter())
    counts = (
        "physically_applied_unseen_multihop_first_hops",
        "physically_arrived_from_outside_current_perception",
        "physically_applied_memory_actions_using_prior_td",
        "assessments_with_prior_published_td",
        "proposed_unseen_multihop_options",
    )
    return {
        "lives": len(values), "deaths": sum(z["lifecycle"] == "dead" for z in values),
        "mean_observed_steps": mean(z["steps"] for z in values),
        "actions": dict(action_totals), "memory_stages": dict(stages),
        "advanced": {k: sum(z["memory_causality"][k] for z in values)
                     for k in counts},
        "max_accumulator_ratio": max(z["memory_max_threshold_ratio"] for z in values),
        "learned_memory_evaluations": sum(z["learned_memory_evaluations"] for z in values),
        "accepted_uc": sum(z["accepted_uc"] for z in values),
        "consolidation_commits": sum(z["consolidation_commits"] for z in values),
        "movement_reversals": sum(z["immediate_movement_reversals"] for z in values),
    }


def compare(control, treatment):
    assert set(control) == set(treatment)
    pairs = []
    for key in sorted(control):
        before, after = control[key], treatment[key]
        for attr in ("world", "seed", "life_id", "preset_digest",
                     "physics_digest", "initial_body", "spawn"):
            assert before[attr] == after[attr], (key, attr)
        pairs.append({"world": key[0], "seed": key[1],
                      "control": before, "treatment": after})
    return {
        "schema": "individual-zero-issue317-paired-wal-v2",
        "status": "PAIRED_AUTHENTICATED_NO_SCIENTIFIC_GO",
        "control_sha": next(iter(control.values()))["sha"],
        "treatment_sha": next(iter(treatment.values()))["sha"],
        "paired_lives": len(pairs),
        "summary": {"control": summary(control), "treatment": summary(treatment)},
        "pairs": pairs,
        "scientific_verdict": "NO-GO",
        "limitations": [
            "Locally visible returns do not prove remote navigation.",
            "Published TD and a later learned evaluation alone do not prove beneficial causal knowledge.",
            "Paired exploratory seeds do not replace held-out replication.",
            "No automatic survival guarantee and no forced action.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control-dir", type=Path, required=True)
    parser.add_argument("--treatment-dir", type=Path, required=True)
    parser.add_argument("--control-sha", required=True)
    parser.add_argument("--treatment-sha", required=True)
    parser.add_argument("--worlds", nargs="+", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    control = cohort(args.control_dir, args.control_sha, args.worlds, args.seeds)
    treatment = cohort(args.treatment_dir, args.treatment_sha, args.worlds, args.seeds)
    report = compare(control, treatment)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError("do not overwrite scientific evidence")
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("ISSUE317_PAIR_CUSTODY_VERIFIED")
    print(json.dumps(report["summary"], sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
