"""Prospectively frozen 58/59 DEVELOPMENT pilot for Candidate-H.

Importing this module does not import Mind, World or generate a life. It defines
only the fresh matched panel, custody reductions and frozen continuation rules.
Execution requires a separately reviewed one-shot transport.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess

IMPLEMENTATION_BASELINE = "a6f0e636022e608239daf08f3bdbeda777c06928"
PROTOCOL = "i3-stage1-candidate-h-development-58-59-v1"
FAMILIES = ("stable", "depletion", "pulse")
INDICES = (58, 59)
GENOME_SEEDS = (901, 902)
POLICIES = (
    "reference",
    "personal_recurrence_candidate_g_v1",
    "personal_relevance_candidate_h_v1",
)
REFERENCE, CANDIDATE_G, CANDIDATE_H = POLICIES
HORIZON = 400
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")
SUPPORT_PHASES = (
    "FIRST_CONTACT_PERSONAL_RECURRENCE",
    "POST_CONTACT_PERSONAL",
)


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
                life_seed = 7_470_000 + 1000 * f + 10 * w + g
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
            "FRESH_STAGE1_CANDIDATE_H_DEVELOPMENT_58_59",
        "previous_development":
            "44_57_EXPOSED_OR_CLOSED_NO_REUSE",
        "allocation_basis":
            "P2_DEVELOPMENT_COHORT_0_99_AND_REPOSITORY_COLLISION_SEARCH",
        "cases": cases,
        "scope":
            "CANDIDATE_H_LIVED_ENGINEERING_DEVELOPMENT_NOT_SCIENTIFIC_GATE",
        "failure_rule":
            "STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT",
        "observers": [
            "full_trace", "full_competition", "resource_acquisition",
            "decision_diagnostics", "mind_digest",
        ],
        "primary_question":
            "DOES_RELEVANCE_GATING_CONTRACT_SUPPORTED_BUT_IRRELEVANT_"
            "CANDIDATE_F_ACTIVATION_WITHOUT_RECREATING_FUNDING_COLLAPSE",
        "controls": {
            "reference": "P1.3_original_policy_and_cost",
            "candidate_g":
                "closed_support_gated_Candidate-G_control_on_new_opportunities",
            "candidate_h":
                "relevance_probe_then_complete_P1.3_or_Candidate-F_final",
        },
        "engineering_continuation_rules": [
            "H1_support_but_fallback_decisions_gt_0",
            "H2_candidate_f_final_decisions_gt_0",
            "H3_candidate_h_nonfunded_fraction_lt_candidate_g",
            "H4_candidate_h_processing_collapse_fraction_lt_candidate_g",
            "H5_candidate_h_paid_energy_per_lived_step_lt_candidate_g",
            "H6_candidate_h_paid_vigilance_per_lived_step_lt_candidate_g",
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
            "pilot must preserve the reviewed Candidate-H runtime implementation")


def _work(value):
    if type(value) is not dict or set(value) != set(WORK_KEYS):
        raise ValueError("complete work vector required")
    if any(type(value[key]) is not int or value[key] < 0 for key in WORK_KEYS):
        raise ValueError("nonnegative integer work required")
    return tuple(value[key] for key in WORK_KEYS)


def _work_add(left, right):
    return tuple(a + b for a, b in zip(_work(left), _work(right)))


def _funding_failure(status):
    return status != "FUNDED"


def _processing_collapse(info):
    if info.get("funding") == "NO_PROCESSING_BUDGET":
        return True
    return (
        info.get("candidate_h_route") == "PROBE_UNFUNDED"
        and info.get("candidate_h_probe_funding")
        == "NO_PROCESSING_BUDGET")


def behavioral_summary(life):
    """Reduce only original paid witnesses; never replay candidate cognition."""
    rows = life["trace"]
    events = life["observer_resource_acquisition"]["steps"]
    competition = life["observer_full_competition"]["steps"]
    if (len(rows) != life["steps_lived"] or
            len(events) != len(rows) or
            len(competition) != len(rows)):
        raise ValueError("incomplete original sidecars")

    policy = life["manifest"].get(
        "experimental_policy", {}).get("name", REFERENCE)
    funding = Counter()
    actions = Counter()
    first_failure = None
    longest = run = 0
    processing_collapse = 0

    h_routes = Counter()
    h_relevance = Counter()
    h_probe_phases = Counter()
    h_probe_funding = Counter()
    h_support_but_fallback = 0
    h_max_settlement_gap = 0.0

    g_active_trace = 0
    g_reference_trace = 0

    for row, event, comp in zip(rows, events, competition):
        info = row["info"]
        if (event["step"] != row["t"] or
                event["action"] != row["action"] or
                comp["physical_action"] != row["action"] or
                event["decision_funding"] != info["funding"] or
                comp["funding"] != info["funding"] or
                event["decision_outcome"] != comp["decision_outcome"]):
            raise ValueError("original sidecars disagree")

        status = info["funding"]
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

        processing_collapse += _processing_collapse(info)

        if policy == CANDIDATE_G:
            mode = info.get("decision_projection_mode")
            if mode == "candidate_f":
                g_active_trace += 1
            elif mode == "reference":
                g_reference_trace += 1
            else:
                raise ValueError("Candidate-G decision lacks projection mode")

        if policy == CANDIDATE_H:
            route = info.get("candidate_h_route")
            relevance = info.get("candidate_h_relevance")
            probe_phase = info.get("candidate_h_probe_phase")
            probe_funding = info.get("candidate_h_probe_funding")
            if route not in (
                    "P1.3_FINAL", "CANDIDATE_F_FINAL", "PROBE_UNFUNDED"):
                raise ValueError("invalid Candidate-H final route")
            if relevance not in (
                    "RELEVANT", "FALLBACK", "PROBE_UNFUNDED"):
                raise ValueError("invalid Candidate-H relevance status")

            h_routes[route] += 1
            h_relevance[relevance] += 1
            h_probe_phases[probe_phase] += 1
            h_probe_funding[probe_funding] += 1

            if route == "P1.3_FINAL" and probe_phase in SUPPORT_PHASES:
                h_support_but_fallback += 1

            stage_a = info.get("candidate_h_stage_a_work")
            stage_b = info.get("candidate_h_stage_b_work")
            total = info.get("candidate_h_total_work")
            if _work_add(stage_a, stage_b) != _work(total):
                raise ValueError("Candidate-H phase work does not sum")
            if _work(total) != _work(
                    row["funding_phases"]["decision"]["work"]):
                raise ValueError(
                    "Candidate-H total work differs from runtime decision bill")

            after = info.get("candidate_h_body_after_cognition")
            paid_after = row["funding_phases"]["decision"]["body_after_debit"]
            if (type(after) not in (list, tuple) or
                    len(after) != len(paid_after)):
                raise ValueError("Candidate-H body receipt missing")
            gap = max(abs(a - b) for a, b in zip(after, paid_after))
            if gap > 1e-12:
                raise ValueError("Candidate-H body settlement mismatch")
            h_max_settlement_gap = max(h_max_settlement_gap, gap)

            if (
                    info.get("persistent_simulation_mode") != "reference" or
                    info.get("persistent_projection_accounting") != "chunk_end"
                    or info.get("omega_source") != "NONE_PERSONAL_ONLY"):
                raise ValueError(
                    "Candidate-H authority or persistent projector drift")

            if route == "PROBE_UNFUNDED":
                if (status != "NO_FUNDED_RELEVANCE_PROBE" or
                        row["action"] is not None or
                        row["option"] is not None or
                        any(_work(stage_b))):
                    raise ValueError(
                        "Candidate-H unfunded probe gained Stage-B authority")
            elif route == "P1.3_FINAL":
                if info.get("decision_projection_mode") != "reference":
                    raise ValueError(
                        "Candidate-H fallback did not finish in P1.3")
            elif (
                    info.get("decision_projection_mode") != "candidate_f"):
                raise ValueError(
                    "Candidate-H relevant final lacks Candidate-F geometry")

    resource = life["observer_resource_acquisition"]["summary"]
    steps = len(rows)
    out = {
        "policy": policy,
        "funding_counts": dict(sorted(funding.items())),
        "nonfunded_decisions": sum(
            value for key, value in funding.items() if key != "FUNDED"),
        "processing_collapse_decisions": processing_collapse,
        "actions": dict(sorted(actions.items())),
        "longest_consecutive_nonfunded_steps": longest,
        "first_funding_failure": first_failure,
        "positive_water_uptakes": resource["positive_water_uptakes"],
        "positive_food_uptakes": resource["positive_food_uptakes"],
        "collected_inventory": resource["collected_inventory"],
        "consumed_inventory": resource["consumed_inventory"],
        "personally_mapped_cells": resource["new_personally_mapped_cells"],
        "inactive_fraction":
            actions["physical_inactivity"] / steps if steps else None,
        "branch_effect_memory": life.get("branch_effect_memory"),
        "opportunity_recurrence_memory":
            life.get("opportunity_recurrence_memory"),
    }

    if policy == CANDIDATE_G:
        frontier = life.get("frontier_information")
        if type(frontier) is not dict:
            raise ValueError("Candidate-G frontier summary missing")
        if frontier.get("information_active_decisions") != g_active_trace:
            raise ValueError("Candidate-G active trace mismatch")
        if frontier.get("reference_only_decisions") != g_reference_trace:
            raise ValueError("Candidate-G reference trace mismatch")
        if g_active_trace + g_reference_trace != steps:
            raise ValueError("Candidate-G projection partition incomplete")
        out["candidate_g"] = {
            "information_active_decisions": g_active_trace,
            "reference_only_decisions": g_reference_trace,
        }

    if policy == CANDIDATE_H:
        summary = life.get("candidate_h_relevance")
        if type(summary) is not dict:
            raise ValueError("Candidate-H life summary missing")
        expected = {
            "probes": steps,
            "probe_unfunded": h_routes["PROBE_UNFUNDED"],
            "candidate_f_final": h_routes["CANDIDATE_F_FINAL"],
            "p13_final": h_routes["P1.3_FINAL"],
        }
        for key, value in expected.items():
            if summary.get(key) != value:
                raise ValueError(
                    "Candidate-H trace/life summary mismatch: " + key)
        if sum(h_routes.values()) != steps:
            raise ValueError("Candidate-H final-route partition incomplete")
        out["candidate_h"] = {
            "routes": dict(sorted(h_routes.items())),
            "relevance": dict(sorted(h_relevance.items())),
            "probe_phases": dict(sorted(h_probe_phases.items())),
            "probe_funding": dict(sorted(h_probe_funding.items())),
            "support_but_fallback_decisions": h_support_but_fallback,
            "max_body_settlement_gap": h_max_settlement_gap,
        }
    return out


def _policy_rows(cases, policy):
    return [row for row in cases if row["identity"]["policy"] == policy]


def aggregate(cases):
    """Pooled engineering summaries only; no population inference."""
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
        nonfunded = processing = 0
        for row in selected:
            funding.update(row["behavior"]["funding_counts"])
            actions.update(row["behavior"]["actions"])
            nonfunded += row["behavior"]["nonfunded_decisions"]
            processing += row["behavior"]["processing_collapse_decisions"]
        decisions = sum(funding.values())
        groups[policy] = {
            "lives": len(selected),
            "censored": sum(
                row["energy"]["terminal"] == "censored"
                for row in selected),
            "dead": sum(
                row["energy"]["terminal"] == "dead"
                for row in selected),
            "lived_steps": steps,
            "decisions": decisions,
            "paid": paid,
            "paid_per_lived_step": {
                channel: paid[channel] / steps if steps else None
                for channel in paid},
            "funding_counts": dict(sorted(funding.items())),
            "nonfunded_decisions": nonfunded,
            "nonfunded_fraction":
                nonfunded / decisions if decisions else None,
            "processing_collapse_decisions": processing,
            "processing_collapse_fraction":
                processing / decisions if decisions else None,
            "actions": dict(sorted(actions.items())),
            "inactive_fraction":
                actions["physical_inactivity"] / steps if steps else None,
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

    g_rows = _policy_rows(cases, CANDIDATE_G)
    groups[CANDIDATE_G]["information_active_decisions"] = sum(
        row["behavior"]["candidate_g"]["information_active_decisions"]
        for row in g_rows)
    groups[CANDIDATE_G]["reference_only_decisions"] = sum(
        row["behavior"]["candidate_g"]["reference_only_decisions"]
        for row in g_rows)

    h_rows = _policy_rows(cases, CANDIDATE_H)
    routes = Counter()
    relevance = Counter()
    phases = Counter()
    support_but_fallback = 0
    max_gap = 0.0
    for row in h_rows:
        data = row["behavior"]["candidate_h"]
        routes.update(data["routes"])
        relevance.update(data["relevance"])
        phases.update(data["probe_phases"])
        support_but_fallback += data["support_but_fallback_decisions"]
        max_gap = max(max_gap, data["max_body_settlement_gap"])
    groups[CANDIDATE_H].update({
        "routes": dict(sorted(routes.items())),
        "relevance": dict(sorted(relevance.items())),
        "probe_phases": dict(sorted(phases.items())),
        "support_but_fallback_decisions": support_but_fallback,
        "max_body_settlement_gap": max_gap,
    })

    g = groups[CANDIDATE_G]
    h = groups[CANDIDATE_H]
    rules = {
        "H1_support_but_fallback_observed":
            h["support_but_fallback_decisions"] > 0,
        "H2_candidate_f_final_observed":
            routes["CANDIDATE_F_FINAL"] > 0,
        "H3_nonfunded_fraction_below_candidate_g":
            h["nonfunded_fraction"] < g["nonfunded_fraction"],
        "H4_processing_collapse_fraction_below_candidate_g":
            h["processing_collapse_fraction"]
            < g["processing_collapse_fraction"],
        "H5_paid_energy_rate_below_candidate_g":
            h["paid_per_lived_step"]["energy"]
            < g["paid_per_lived_step"]["energy"],
        "H6_paid_vigilance_rate_below_candidate_g":
            h["paid_per_lived_step"]["vigilance"]
            < g["paid_per_lived_step"]["vigilance"],
    }
    h["engineering_continuation_rules"] = rules
    h["engineering_continuation_rule_met"] = all(rules.values())
    groups[REFERENCE]["engineering_continuation_rule_met"] = None
    groups[CANDIDATE_G]["engineering_continuation_rule_met"] = None
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

    # Source validation above precedes engine imports and possible births.
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
                "candidate_h_route": (
                    row["behavior"].get("candidate_h", {})
                    .get("routes")),
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
            "COMPLETE_CANDIDATE_H_DEVELOPMENT_58_59_NOT_SCIENTIFIC_GATE",
        "cases": cases,
        "summary": aggregate(cases),
    }
    _write_json(output / "results.json", result)
    inventory = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(output.iterdir()) if path.is_file()
    }
    _write_json(output / "SHA256.json", inventory)
    print("CANDIDATE_H_58_59_SUMMARY " + canonical(
        result["summary"]), flush=True)
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
