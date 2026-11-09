"""Frozen fresh development diagnostic for the P1.3 frontier-water mechanism.

Importing this module never imports Mind/World or generates a life. This source
only defines a prospectively fixed 50/51 development panel and reductions.
Execution requires a later, separately reviewed one-shot workflow.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess

BASELINE = "ed871a04e09a386f94f739f6c0701b87776c895f"
PROTOCOL = "i3-stage1-frontier-water-development-v2"
FAMILIES = ("stable", "depletion", "pulse")
INDICES = (50, 51)
GENOME_SEEDS = (901, 902)
POLICIES = (
    "reference",
    "reference_branch_memory_v1",
    "reference_frontier_information_v1",
)
HORIZON = 400
CANDIDATE = "reference_frontier_information_v1"


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def plan():
    cases = []
    for f, family in enumerate(FAMILIES):
        for w, index in enumerate(INDICES):
            for g, genome_seed in enumerate(GENOME_SEEDS):
                block = f"{family}-{index}-g{genome_seed}"
                life_seed = 7_430_000 + 1000 * f + 10 * w + g
                for policy in POLICIES:
                    cases.append({
                        "case": block + ":" + policy,
                        "block": block,
                        "family": family,
                        "cohort": "development",
                        "index": index,
                        "genome_seed": genome_seed,
                        "life_seed": life_seed,
                        "policy": policy,
                    })
    return {
        "protocol": PROTOCOL,
        "runtime_baseline": BASELINE,
        "horizon": HORIZON,
        "maximum_steps": HORIZON * len(cases),
        "allocation_contract":
            "FRESH_STAGE1_EXTENSION_50_51_OUTSIDE_FROZEN_STAGE0_44_49",
        "previous_panel":
            "48_49_CLOSED_ENGINEERING_FAILURE_NO_REUSE",
        "allocation_basis":
            "P2_DEVELOPMENT_COHORT_0_99_AND_REPOSITORY_COLLISION_SEARCH",
        "cases": cases,
        "scope": "DESCRIPTIVE_FRONTIER_WATER_DEVELOPMENT_NOT_GATE",
        "failure_rule": "STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT",
        "observers": [
            "full_trace", "full_competition", "resource_acquisition",
            "decision_diagnostics", "mind_digest",
        ],
        "primary_question":
            "DOES_REFERENCE_FRONTIER_INFORMATION_BECOME_ONLINE_AFTER_PERSONAL_WATER_EXPERIENCE",
        "candidate_engineering_continuation_rule":
            "at_least_one_candidate_life_has_positive_frontier_information_option",
        "candidate_bootstrap_classes": [
            "NO_WATER_EXPERIENCE_BOOTSTRAP_NOT_OBSERVED",
            "WATER_EXPERIENCED_BUT_NO_ACTIONABLE_MODEL",
            "ACTIONABLE_MODEL_BUT_ZERO_INFORMATION",
            "POSITIVE_FRONTIER_INFORMATION_OBSERVED",
        ],
        "controls": {
            "reference": "P1.3_with_original_curiosity_prudence",
            "storage_only": "reference_branch_memory_v1_same_memory_cost_original_score",
            "candidate": CANDIDATE,
        },
        "frontier_scope": "one_generic_new_cell_water_only",
        "food_information": "NOT_IMPLEMENTED",
        "multi_cell_joint_outcomes": "NOT_IMPLEMENTED",
        "no_selection_validation_or_reserve": True,
    }


def _git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def validate_launch(expected_sha, expected_protocol):
    """Reject source/protocol drift before importing runtime or generating worlds."""
    if (type(expected_sha) is not str or len(expected_sha) != 40 or
            any(c not in "0123456789abcdef" for c in expected_sha) or
            _git("rev-parse", "HEAD") != expected_sha):
        raise ValueError("exact prospective source SHA required")
    if expected_protocol != digest(plan()):
        raise ValueError("prospective protocol digest mismatch")
    if _git(
            "status", "--porcelain", "--untracked-files=all", "--",
            "src/i3", "tests/i3"):
        raise ValueError("dirty I3 source")
    if _git(
            "diff", "--name-only", BASELINE, "HEAD", "--",
            "src/i3/modules", "src/i3/runtime",
            "src/i3/lab/p2_ecologies.py", "src/i3/lab/worldgen.py",
            "src/i3/lab/stage0_energy.py", "src/i3/lab/stage0_revision.py",
            "config/engine-registry.json"):
        raise ValueError(
            "diagnostic must preserve the frozen #1082 cognition and #1085 observer repair")


def bootstrap_status(behavior):
    """Prospective mechanistic classification; never a survival verdict."""
    if type(behavior) is not dict:
        raise ValueError("behavior dict required")
    water = behavior.get("positive_water_uptakes")
    frontier = behavior.get("frontier_information")
    if (type(water) is not int or water < 0 or
            type(frontier) is not dict):
        raise ValueError("complete candidate behavior required")
    actionable = frontier.get("actionable_water_queries")
    positive = frontier.get("positive_information_options")
    if (type(actionable) is not int or actionable < 0 or
            type(positive) is not int or positive < 0):
        raise ValueError("invalid frontier-information counts")
    if positive > 0:
        if actionable == 0:
            raise ValueError("positive information without actionable water")
        return "POSITIVE_FRONTIER_INFORMATION_OBSERVED"
    if actionable > 0:
        return "ACTIONABLE_MODEL_BUT_ZERO_INFORMATION"
    if water > 0:
        return "WATER_EXPERIENCED_BUT_NO_ACTIONABLE_MODEL"
    return "NO_WATER_EXPERIENCE_BOOTSTRAP_NOT_OBSERVED"


def behavioral_summary(life):
    """Reduce original paid witnesses without replaying or inferring hidden state."""
    rows = life["trace"]
    events = life["observer_resource_acquisition"]["steps"]
    competition = life["observer_full_competition"]["steps"]
    if (len(rows) != life["steps_lived"] or len(events) != len(rows) or
            len(competition) != len(rows)):
        raise ValueError("incomplete original sidecars")

    funding = Counter()
    actions = Counter()
    longest = run = 0
    first_failure = first_positive_water = first_positive_information = None
    info_options = positive_info = 0

    for row, event, comp in zip(rows, events, competition):
        if (event["step"] != row["t"] or event["action"] != row["action"] or
                comp["physical_action"] != row["action"] or
                event["decision_funding"] != row["info"]["funding"] or
                event["decision_outcome"] != comp["decision_outcome"]):
            raise ValueError("original sidecars disagree")
        status = row["info"]["funding"]
        funding[status] += 1
        actions[row["action"] or "physical_inactivity"] += 1
        if status in (
                "NO_PROCESSING_BUDGET", "NO_FUNDED_SCORE",
                "NO_FUNDED_MOTOR"):
            run += 1
            longest = max(longest, run)
            if first_failure is None:
                first_failure = {
                    "step": row["t"],
                    "funding": status,
                    "body_before":
                        row["funding_phases"]["decision"]["body_before"],
                    "work": row["funding_phases"]["decision"]["work"],
                }
        else:
            run = 0

        if first_positive_water is None and event["positive_water_uptake"]:
            first_positive_water = row["t"]

        diag = row["info"]["observer"]
        for score in diag["score_witness"]:
            if score.get("score_kind") == "frontier_water_expected_distress":
                info_options += 1
                if score.get("information_value", 0.0) > 1e-12:
                    positive_info += 1
                    if first_positive_information is None:
                        first_positive_information = row["t"]

    resource = life["observer_resource_acquisition"]["summary"]
    frontier = life.get("frontier_information")
    if frontier is not None:
        expected = {
            "frontier_options_scored": info_options,
            "positive_information_options": positive_info,
        }
        for key, value in expected.items():
            if frontier.get(key) != value:
                raise ValueError(
                    "frontier trace/output mismatch: " + key)

    steps = len(rows)
    out = {
        "funding_counts": dict(sorted(funding.items())),
        "actions": dict(sorted(actions.items())),
        "longest_consecutive_unfunded_steps": longest,
        "first_funding_failure": first_failure,
        "first_positive_water_step": first_positive_water,
        "first_positive_information_step": first_positive_information,
        "positive_water_uptakes": resource["positive_water_uptakes"],
        "positive_food_uptakes": resource["positive_food_uptakes"],
        "collected_inventory": resource["collected_inventory"],
        "consumed_inventory": resource["consumed_inventory"],
        "personally_mapped_cells": resource["new_personally_mapped_cells"],
        "paid_frontier_information_options": info_options,
        "positive_information_options": positive_info,
        "inactive_fraction":
            actions["physical_inactivity"] / steps if steps else None,
        "branch_effect_memory": life.get("branch_effect_memory"),
        "frontier_information": frontier,
    }
    if frontier is not None:
        out["bootstrap_status"] = bootstrap_status(out)
    return out


def aggregate(cases):
    """Descriptive sums across dependent lives; no population inference."""
    groups = {}
    for policy in POLICIES:
        selected = [
            row for row in cases
            if row["identity"]["policy"] == policy]
        steps = sum(row["energy"]["steps_lived"] for row in selected)
        paid = {
            channel: sum(row["energy"]["paid"][channel] for row in selected)
            for channel in ("energy", "vigilance")
        }
        funding = Counter()
        actions = Counter()
        for row in selected:
            funding.update(row["behavior"]["funding_counts"])
            actions.update(row["behavior"]["actions"])
        inactive = (
            actions["physical_inactivity"] / steps if steps else None)
        frontier_rows = [
            row["behavior"]["frontier_information"]
            for row in selected
            if row["behavior"]["frontier_information"] is not None
        ]
        statuses = Counter(
            row["behavior"].get("bootstrap_status")
            for row in selected
            if row["behavior"].get("bootstrap_status") is not None)
        groups[policy] = {
            "lives": len(selected),
            "censored": sum(
                row["energy"]["terminal"] == "censored"
                for row in selected),
            "dead": sum(
                row["energy"]["terminal"] == "dead"
                for row in selected),
            "lived_steps": steps,
            "paid": paid,
            "paid_per_lived_step": {
                channel: value / steps if steps else None
                for channel, value in paid.items()},
            "funding_counts": dict(sorted(funding.items())),
            "actions": dict(sorted(actions.items())),
            "inactive_fraction": inactive,
            "positive_water_uptakes": sum(
                row["behavior"]["positive_water_uptakes"]
                for row in selected),
            "positive_food_uptakes": sum(
                row["behavior"]["positive_food_uptakes"]
                for row in selected),
            "branch_records": sum(
                (row["behavior"]["branch_effect_memory"] or {})
                .get("recorded", 0)
                for row in selected),
            "frontier_belief_queries": sum(
                row.get("belief_queries", 0)
                for row in frontier_rows),
            "actionable_water_queries": sum(
                row.get("actionable_water_queries", 0)
                for row in frontier_rows),
            "frontier_options_scored": sum(
                row.get("frontier_options_scored", 0)
                for row in frontier_rows),
            "positive_information_options": sum(
                row.get("positive_information_options", 0)
                for row in frontier_rows),
            "bootstrap_statuses": dict(sorted(statuses.items())),
            "positive_information_lives": statuses.get(
                "POSITIVE_FRONTIER_INFORMATION_OBSERVED", 0),
            "revision_statuses": dict(Counter(
                row["revision"]["status"] for row in selected)),
            "scientific_verdict": "NOT_EVALUATED",
        }
    groups[CANDIDATE]["engineering_continuation_rule_met"] = (
        groups[CANDIDATE]["positive_information_lives"] > 0)
    groups["reference"]["engineering_continuation_rule_met"] = None
    groups["reference_branch_memory_v1"][
        "engineering_continuation_rule_met"] = None
    return groups


def _write_json(path, value):
    path.write_text(canonical(value) + "\n", encoding="utf-8")


def run(output, expected_sha, expected_protocol):
    validate_launch(expected_sha, expected_protocol)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    registration = {
        "plan": plan(),
        "protocol_sha256": digest(plan()),
        "execution_sha": expected_sha,
    }
    _write_json(output / "registration.json", registration)

    # Source validation precedes all engine imports and possible births.
    from i3.lab.p2_ecologies import world_for
    from i3.lab.stage0_energy import energy_receipt
    from i3.lab.stage0_revision import revision_receipt
    from i3.modules.genome import generation_zero
    from i3.runtime.life import run_life
    from i3.runtime.provenance import source_snapshot

    source = source_snapshot()
    if source["git_head"] != expected_sha or source["working_tree_dirty"]:
        raise ValueError(
            "source snapshot disagrees with prospective lock")
    _write_json(output / "source.json", source)

    cases = []
    for number, identity in enumerate(plan()["cases"]):
        filename = f"life-{number:02d}.json.gz"
        try:
            spec = world_for(
                identity["family"], "development", identity["index"])
            genome = generation_zero(identity["genome_seed"])
            life = run_life(
                genome, spec, identity["life_seed"], HORIZON,
                protocol=PROTOCOL,
                decision_policy=identity["policy"],
                keep_trace=True,
                observer_mind_digest=True,
                observer_decision_diagnostics=True,
                observer_resource_acquisition=True,
                observer_full_competition=True,
            )
            raw = (
                canonical({"identity": identity, "life": life}) + "\n"
            ).encode()
            compressed = gzip.compress(raw, mtime=0)
            (output / filename).write_bytes(compressed)

            energy = energy_receipt(
                life, expected_protocol=PROTOCOL,
                expected_source_sha256=source["sha256"])
            revision = revision_receipt(
                life, expected_protocol=PROTOCOL,
                expected_source_sha256=source["sha256"])
            row = {
                "identity": identity,
                "original_file": filename,
                "original_sha256": sha256(compressed).hexdigest(),
                "original_uncompressed_sha256": sha256(raw).hexdigest(),
                "energy": energy,
                "revision": revision,
                "behavior": behavioral_summary(life),
            }
            cases.append(row)
            _write_json(output / "cases.json", cases)
            print(canonical({
                "completed": number + 1,
                "case": identity["case"],
                "terminal": energy["terminal"],
                "steps": energy["steps_lived"],
                "bootstrap_status":
                    row["behavior"].get("bootstrap_status"),
            }), flush=True)
        except Exception as exc:
            failure = {
                "status": "ENGINEERING_FAILURE_NOT_A_DEATH",
                "case": identity,
                "completed": len(cases),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "no_retry": True,
            }
            _write_json(output / "failure.json", failure)
            print(canonical(failure), flush=True)
            raise

    # Reconcile equal initial opportunities inside every three-arm block.
    if len(cases) % len(POLICIES):
        raise RuntimeError("incomplete policy blocks")
    for start in range(0, len(cases), len(POLICIES)):
        block = cases[start:start + len(POLICIES)]
        if tuple(row["identity"]["policy"] for row in block) != POLICIES:
            raise ValueError("policy block order mismatch")
        if len({row["identity"]["block"] for row in block}) != 1:
            raise ValueError("opportunity block mismatch")
        first = block[0]
        for other in block[1:]:
            for field in (
                    "world_sha256", "genome_sha256",
                    "life_seed", "horizon"):
                if first["energy"][field] != other["energy"][field]:
                    raise ValueError(
                        "three-arm opportunity mismatch: " + field)

    result = {
        **registration,
        "source_sha256": source["sha256"],
        "status":
            "COMPLETE_DESCRIPTIVE_FRONTIER_WATER_DEVELOPMENT_NOT_GATE",
        "cases": cases,
        "summary": aggregate(cases),
    }
    _write_json(output / "results.json", result)
    inventory = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(output.iterdir()) if path.is_file()
    }
    _write_json(output / "SHA256.json", inventory)
    print(
        "DIAGNOSTIC_SUMMARY " + canonical(result["summary"]),
        flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--expected-sha")
    parser.add_argument("--expected-protocol")
    args = parser.parse_args()
    if args.plan:
        print(canonical({
            "plan": plan(),
            "protocol_sha256": digest(plan()),
        }))
    else:
        if not args.output:
            parser.error(
                "--output required for the frozen single execution")
        run(args.output, args.expected_sha, args.expected_protocol)
