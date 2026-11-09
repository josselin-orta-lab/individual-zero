"""Prospectively frozen 56/57 development pilot for no-omega Candidate-G.

Importing this module does not import Mind, World or generate a life. It defines
only the fresh matched panel and read-only reductions. Execution requires a
later separately reviewed one-shot workflow.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess

IMPLEMENTATION_BASELINE = "b9acb61a26be6d9ddcbe4dee2d0f5218cca5ccaf"
PROTOCOL = "i3-stage1-candidate-g-development-56-57-v1"
FAMILIES = ("stable", "depletion", "pulse")
INDICES = (56, 57)
GENOME_SEEDS = (901, 902)
POLICIES = (
    "reference",
    "personal_recurrence_candidate_g_v1",
    "genomic_omega_frontier_information_v1",
)
REFERENCE, CANDIDATE, COST_ANCHOR = POLICIES
HORIZON = 400
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")


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
                life_seed = 7_460_000 + 1000 * f + 10 * w + g
                for policy in POLICIES:
                    cases.append({
                        "case": block + ":" + policy,
                        "block": block,
                        "family": family,
                        "cohort": "development",
                        "index": index,
                        "world_seed": 2000 + index,
                        "genome_seed": genome_seed,
                        "life_seed": life_seed,
                        "policy": policy,
                    })
    return {
        "protocol": PROTOCOL,
        "horizon": HORIZON,
        "maximum_steps": HORIZON * len(cases),
        "allocation_contract":
            "FRESH_STAGE1_CANDIDATE_G_DEVELOPMENT_56_57",
        "previous_development":
            "44_55_EXPOSED_OR_CLOSED_NO_REUSE",
        "allocation_basis":
            "P2_DEVELOPMENT_COHORT_0_99_AND_REPOSITORY_COLLISION_SEARCH",
        "cases": cases,
        "scope":
            "DESCRIPTIVE_CANDIDATE_G_DEVELOPMENT_PILOT_NOT_GATE",
        "failure_rule":
            "STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT",
        "observers": [
            "full_trace", "full_competition", "resource_acquisition",
            "decision_diagnostics", "mind_digest",
        ],
        "primary_question":
            "DOES_PERSONALLY_SUPPORTED_INTERMITTENT_CANDIDATE_F_PROJECTION_"
            "REDUCE_REALIZED_COGNITIVE_COLLAPSE",
        "controls": {
            "reference": "P1.3_original_policy_and_cost",
            "candidate":
                "personal_recurrence_candidate_g_v1_no_genomic_omega",
            "cost_anchor":
                "rejected_genomic_omega_candidate_f_same_opportunities",
        },
        "engineering_continuation_rules": [
            "candidate_information_active_decisions_gt_0",
            "candidate_reference_only_decisions_gt_0",
            "candidate_paid_energy_per_lived_step_lt_cost_anchor",
            "candidate_paid_vigilance_per_lived_step_lt_cost_anchor",
            "candidate_no_processing_budget_fraction_lt_cost_anchor",
        ],
        "survival_is_not_a_continuation_rule": True,
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
            "diff", "--name-only", IMPLEMENTATION_BASELINE, "HEAD", "--",
            "src/i3/modules", "src/i3/runtime",
            "src/i3/lab/p2_ecologies.py", "src/i3/lab/worldgen.py",
            "src/i3/lab/stage0_energy.py", "src/i3/lab/stage0_revision.py",
            "config/engine-registry.json"):
        raise ValueError(
            "pilot must preserve the reviewed Candidate-G runtime implementation")


def _funding_failure(status):
    return status in (
        "NO_PROCESSING_BUDGET", "NO_FUNDED_SCORE", "NO_FUNDED_MOTOR")


def behavioral_summary(life):
    """Reduce original paid witnesses only; never replay cognition."""
    rows = life["trace"]
    events = life["observer_resource_acquisition"]["steps"]
    competition = life["observer_full_competition"]["steps"]
    if (len(rows) != life["steps_lived"] or
            len(events) != len(rows) or len(competition) != len(rows)):
        raise ValueError("incomplete original sidecars")

    funding = Counter()
    actions = Counter()
    longest = run = 0
    first_failure = first_water = None

    active_trace = 0
    reference_trace = 0
    recurrence_supported_trace = 0
    frontier_trace = 0
    positive_info_trace = 0

    for row, event, comp in zip(rows, events, competition):
        if (event["step"] != row["t"] or
                event["action"] != row["action"] or
                comp["physical_action"] != row["action"] or
                event["decision_funding"] != row["info"]["funding"] or
                event["decision_outcome"] != comp["decision_outcome"]):
            raise ValueError("original sidecars disagree")

        status = row["info"]["funding"]
        funding[status] += 1
        actions[row["action"] or "physical_inactivity"] += 1
        if _funding_failure(status):
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

        if first_water is None and event["positive_water_uptake"]:
            first_water = row["t"]

        info = row["info"]
        mode = info.get("decision_projection_mode")
        if mode == "candidate_f":
            active_trace += 1
        elif mode == "reference":
            reference_trace += 1
        elif life["manifest"].get("experimental_policy", {}).get("name") == CANDIDATE:
            raise ValueError("Candidate-G decision lacks projection-mode witness")

        if info.get("frontier_phase") == "FIRST_CONTACT_PERSONAL_RECURRENCE":
            recurrence_supported_trace += 1

        observer = info.get("observer")
        if observer is not None:
            for score in observer["score_witness"]:
                if score.get("score_kind") == "frontier_water_expected_distress":
                    frontier_trace += 1
                    if score.get("information_value", 0.0) > 1e-12:
                        positive_info_trace += 1

    resource = life["observer_resource_acquisition"]["summary"]
    frontier = life.get("frontier_information")
    recurrence = life.get("opportunity_recurrence_memory")
    policy = life["manifest"].get("experimental_policy", {}).get(
        "name", REFERENCE)

    if policy == CANDIDATE:
        if "first_contact_omega" in canonical(life):
            raise ValueError("Candidate-G evidence contains first_contact_omega")
        if type(frontier) is not dict or type(recurrence) is not dict:
            raise ValueError("Candidate-G runtime summaries missing")
        if frontier.get("omega_source") != "NONE_PERSONAL_RECURRENCE_ONLY":
            raise ValueError("Candidate-G omega authority drift")
        if (
                frontier.get("persistent_simulation_mode") != "reference" or
                frontier.get("persistent_projection_accounting") != "chunk_end"):
            raise ValueError("Candidate-G persistent projector leaked")
        if frontier.get("information_active_decisions") != active_trace:
            raise ValueError("Candidate-G active-decision trace mismatch")
        if frontier.get("reference_only_decisions") != reference_trace:
            raise ValueError("Candidate-G reference-decision trace mismatch")
        if active_trace + reference_trace != len(rows):
            raise ValueError("Candidate-G decision-mode partition incomplete")
        if (
                frontier.get("recurrence_supported_decisions") !=
                recurrence_supported_trace):
            raise ValueError("Candidate-G recurrence trace mismatch")
        if frontier.get("frontier_options_scored") != frontier_trace:
            raise ValueError("Candidate-G frontier score trace mismatch")
        if frontier.get("positive_information_options") != positive_info_trace:
            raise ValueError("Candidate-G positive-information trace mismatch")
        if recurrence.get("recorded") != (
                recurrence.get("snapshot", {}).get("observations")):
            # Snapshot implementations may expose richer structure but the
            # top-level observation count must remain custody-consistent.
            snapshot = recurrence.get("snapshot", {})
            if "observations" in snapshot:
                raise ValueError("Candidate-G recurrence custody mismatch")

    steps = len(rows)
    return {
        "policy": policy,
        "funding_counts": dict(sorted(funding.items())),
        "actions": dict(sorted(actions.items())),
        "longest_consecutive_unfunded_steps": longest,
        "first_funding_failure": first_failure,
        "first_positive_water_step": first_water,
        "positive_water_uptakes": resource["positive_water_uptakes"],
        "positive_food_uptakes": resource["positive_food_uptakes"],
        "collected_inventory": resource["collected_inventory"],
        "consumed_inventory": resource["consumed_inventory"],
        "personally_mapped_cells": resource["new_personally_mapped_cells"],
        "inactive_fraction":
            actions["physical_inactivity"] / steps if steps else None,
        "branch_effect_memory": life.get("branch_effect_memory"),
        "opportunity_recurrence_memory": recurrence,
        "frontier_information": frontier,
        "trace_candidate_f_projection_decisions": active_trace,
        "trace_reference_projection_decisions": reference_trace,
        "trace_recurrence_supported_decisions": recurrence_supported_trace,
        "trace_frontier_options_scored": frontier_trace,
        "trace_positive_information_options": positive_info_trace,
    }


def _policy_rows(cases, policy):
    return [row for row in cases if row["identity"]["policy"] == policy]


def aggregate(cases):
    """Descriptive pooled engineering summaries; no population inference."""
    groups = {}
    for policy in POLICIES:
        selected = _policy_rows(cases, policy)
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
        total_decisions = sum(funding.values())
        no_processing = funding["NO_PROCESSING_BUDGET"]
        frontier_rows = [
            row["behavior"]["frontier_information"]
            for row in selected
            if row["behavior"]["frontier_information"] is not None
        ]
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
                channel: paid[channel] / steps if steps else None
                for channel in paid},
            "funding_counts": dict(sorted(funding.items())),
            "no_processing_budget_fraction": (
                no_processing / total_decisions if total_decisions else None),
            "actions": dict(sorted(actions.items())),
            "inactive_fraction": (
                actions["physical_inactivity"] / steps if steps else None),
            "positive_water_uptakes": sum(
                row["behavior"]["positive_water_uptakes"]
                for row in selected),
            "positive_food_uptakes": sum(
                row["behavior"]["positive_food_uptakes"]
                for row in selected),
            "revision_statuses": dict(Counter(
                row["revision"]["status"] for row in selected)),
            "scientific_verdict": "NOT_EVALUATED",
        }
        if policy == CANDIDATE:
            groups[policy].update({
                "information_active_decisions": sum(
                    x.get("information_active_decisions", 0)
                    for x in frontier_rows),
                "reference_only_decisions": sum(
                    x.get("reference_only_decisions", 0)
                    for x in frontier_rows),
                "recurrence_supported_decisions": sum(
                    x.get("recurrence_supported_decisions", 0)
                    for x in frontier_rows),
                "frontier_options_scored": sum(
                    x.get("frontier_options_scored", 0)
                    for x in frontier_rows),
                "positive_information_options": sum(
                    x.get("positive_information_options", 0)
                    for x in frontier_rows),
                "opportunity_records": sum(
                    (row["behavior"]["opportunity_recurrence_memory"] or {})
                    .get("recorded", 0)
                    for row in selected),
            })

    candidate = groups[CANDIDATE]
    anchor = groups[COST_ANCHOR]
    rules = {
        "R1_candidate_information_active_observed":
            candidate["information_active_decisions"] > 0,
        "R2_candidate_reference_only_observed":
            candidate["reference_only_decisions"] > 0,
        "R3_candidate_energy_rate_below_cost_anchor":
            candidate["paid_per_lived_step"]["energy"]
            < anchor["paid_per_lived_step"]["energy"],
        "R4_candidate_vigilance_rate_below_cost_anchor":
            candidate["paid_per_lived_step"]["vigilance"]
            < anchor["paid_per_lived_step"]["vigilance"],
        "R5_candidate_no_processing_fraction_below_cost_anchor":
            candidate["no_processing_budget_fraction"]
            < anchor["no_processing_budget_fraction"],
    }
    candidate["engineering_continuation_rules"] = rules
    candidate["engineering_continuation_rule_met"] = all(rules.values())
    groups[REFERENCE]["engineering_continuation_rule_met"] = None
    groups[COST_ANCHOR]["engineering_continuation_rule_met"] = None
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

    # All source validation above precedes engine imports and possible births.
    from i3.lab.p2_ecologies import world_for
    from i3.lab.stage0_energy import energy_receipt
    from i3.lab.stage0_revision import revision_receipt
    from i3.modules.genome import generation_zero
    from i3.runtime.life import run_life
    from i3.runtime.provenance import source_snapshot

    source = source_snapshot()
    if source["git_head"] != expected_sha or source["working_tree_dirty"]:
        raise ValueError("source snapshot disagrees with prospective lock")
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
                "candidate_active_decisions":
                    row["behavior"]["trace_candidate_f_projection_decisions"],
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
            "COMPLETE_DESCRIPTIVE_CANDIDATE_G_DEVELOPMENT_PILOT_NOT_GATE",
        "cases": cases,
        "summary": aggregate(cases),
    }
    _write_json(output / "results.json", result)
    inventory = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(output.iterdir()) if path.is_file()
    }
    _write_json(output / "SHA256.json", inventory)
    print("PILOT_SUMMARY " + canonical(result["summary"]), flush=True)
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
            parser.error("--output required for frozen single execution")
        run(args.output, args.expected_sha, args.expected_protocol)
