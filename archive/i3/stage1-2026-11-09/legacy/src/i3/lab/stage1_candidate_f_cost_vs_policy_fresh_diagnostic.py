"""Prospectively frozen development falsifier for Candidate-F cost vs policy.

Importing this module does not import Mind, World or run a life. It defines the
fresh 54/55 three-arm panel and read-only reductions. Execution is authorized
only by a later separately reviewed one-shot workflow after this protocol merges.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess

BASELINE = "954ea5f312024fb902dd43a6845341adc3f88f0f"
PROTOCOL = "i3-stage1-candidate-f-cost-vs-policy-development-v2"
FAMILIES = ("stable", "depletion", "pulse")
INDICES = (54, 55)
GENOME_SEEDS = (901, 902)
POLICIES = (
    "reference",
    "genomic_omega_frontier_information_v1",
    "candidate_f_shadow_upper_cost_reference_controller_v1",
)
REFERENCE = POLICIES[0]
CANDIDATE = POLICIES[1]
UPPER_COST = POLICIES[2]
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
                life_seed = 7_450_000 + 1000 * f + 10 * w + g
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
            "FRESH_STAGE1_COST_VS_POLICY_EXTENSION_54_55",
        "previous_development":
            "44_53_EXPOSED_OR_CLOSED_NO_REUSE",
        "allocation_basis":
            "P2_DEVELOPMENT_COHORT_0_99_AND_REPOSITORY_COLLISION_SEARCH",
        "cases": cases,
        "scope":
            "DESCRIPTIVE_CAUSAL_FALSIFIER_DEVELOPMENT_NOT_GATE",
        "failure_rule":
            "STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT",
        "observers": [
            "full_trace", "full_competition", "resource_acquisition",
            "decision_diagnostics", "mind_digest",
        ],
        "primary_question":
            "CAN_P13_MOTOR_POLICY_RETAIN_SURVIVAL_WHILE_REAL_"
            "CANDIDATE_F_SHADOW_COGNITION_IS_PAID",
        "candidate_f_policy": CANDIDATE,
        "upper_cost_policy": UPPER_COST,
        "engineering_continuation_rule":
            "at_least_one_UPPER_SURVIVES_CANDIDATE_DIES_block",
        "paired_classes": [
            "UPPER_SURVIVES_CANDIDATE_DIES",
            "CANDIDATE_SURVIVES_UPPER_DIES",
            "BOTH_SURVIVE",
            "BOTH_DIE",
        ],
        "controls": {
            "reference":
                "P1.3_original_policy_and_cost",
            "candidate":
                "Candidate-F_plus_genomic_omega_motor_policy",
            "upper_cost":
                "P1.3_motor_policy_after_paid_Candidate-F_shadow_plus_"
                "P1.3_choice",
        },
        "cost_claim":
            "UPPER_COST_NOT_EXACT_MATCH_OR_MEDIATION",
        "no_selection_validation_or_reserve": True,
    }


def _git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def validate_launch(expected_sha, expected_protocol):
    """Reject any runtime/cognition/physics drift before first 54/55 birth."""
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
            "diagnostic must preserve the frozen cost-vs-policy runtime")


def _work_add(a, b):
    return {key: a[key] + b[key] for key in WORK_KEYS}


def audit_upper_cost_trace(life):
    """Authenticate every upper-cost decision without replaying cognition."""
    rows = life["trace"]
    if life.get("candidate_f_cost_control") is None:
        raise ValueError("upper-cost life summary required")
    if life["candidate_f_cost_control"]["decisions"] != len(rows):
        raise ValueError("upper-cost decision count mismatch")

    shadow = {key: 0 for key in WORK_KEYS}
    reference = {key: 0 for key in WORK_KEYS}
    total = {key: 0 for key in WORK_KEYS}
    max_gap = 0.0
    shadow_action_differs = 0

    for row in rows:
        cc = row.get("info", {}).get("cost_control")
        if type(cc) is not dict:
            raise ValueError("missing per-step upper-cost receipt")
        if (cc.get("motor_authority") != "P1.3_REFERENCE_ONLY" or
                cc.get("candidate_motor_authority") is not False):
            raise ValueError("shadow gained motor authority")
        if cc.get("cost_matching_claim") != "UPPER_COST_NOT_EXACT_MATCH":
            raise ValueError("upper-cost claim drift")
        if cc.get("settlement_authority") != "CUMULATIVE_V2_PHASE_START_BODY":
            raise ValueError("cumulative v2 settlement authority drift")

        sw = cc.get("candidate_shadow_work")
        rw = cc.get("reference_choice_work")
        tw = cc.get("total_work")
        dw = row["funding_phases"]["decision"]["work"]
        if any(
                type(v) is not int or v < 0
                for work in (sw, rw, tw, dw)
                for key, v in work.items()
                if key in WORK_KEYS):
            raise ValueError("invalid upper-cost work receipt")
        if any(set(work) != set(WORK_KEYS) for work in (sw, rw, tw, dw)):
            raise ValueError("incomplete upper-cost work vector")
        if _work_add(sw, rw) != tw or tw != dw:
            raise ValueError("upper-cost decision bill is not exact sum")

        gap = cc.get("sequential_settlement_max_abs_gap")
        if type(gap) not in (int, float) or gap < 0 or gap > 1e-12:
            raise ValueError("upper-cost settlement audit gap")
        max_gap = max(max_gap, float(gap))

        if list(cc.get("body_before", ())) != list(
                row["funding_phases"]["decision"]["body_before"]):
            raise ValueError("upper-cost phase-start body mismatch")
        if list(cc.get("body_after_reference_choice", ())) != list(
                row["funding_phases"]["decision"]["body_after_debit"]):
            raise ValueError("upper-cost final decision body mismatch")

        shadow = _work_add(shadow, sw)
        reference = _work_add(reference, rw)
        total = _work_add(total, tw)
        if cc.get("candidate_shadow_action") != row["action"]:
            shadow_action_differs += 1

    memory = life.get("branch_effect_memory")
    summary = life["candidate_f_cost_control"]
    if type(memory) is not dict:
        raise ValueError("upper-cost branch memory receipt required")
    if (summary.get("shadow_branch_commits") != memory.get("recorded") or
            summary.get("shadow_branch_retained") != memory.get("retained")):
        raise ValueError("upper-cost private memory custody mismatch")
    return {
        "status": "AUTHENTICATED_UPPER_COST_P1.3_MOTOR",
        "decisions": len(rows),
        "candidate_shadow_work": shadow,
        "reference_choice_work": reference,
        "total_decision_work": total,
        "max_sequential_settlement_gap": max_gap,
        "shadow_action_differs_from_actual": shadow_action_differs,
        "shadow_branch_commits": summary["shadow_branch_commits"],
        "shadow_branch_retained": summary["shadow_branch_retained"],
        "shadow_first_contact_omega": summary["shadow_first_contact_omega"],
        "shadow_first_contact_queries":
            summary["shadow_first_contact_queries"],
        "shadow_frontier_options_scored":
            summary["shadow_frontier_options_scored"],
        "shadow_positive_information_options":
            summary["shadow_positive_information_options"],
    }


def behavioral_summary(life):
    """Reduce only original paid witnesses; never replay or infer hidden state."""
    rows = life["trace"]
    events = life["observer_resource_acquisition"]["steps"]
    competition = life["observer_full_competition"]["steps"]
    if (len(rows) != life["steps_lived"] or len(events) != len(rows) or
            len(competition) != len(rows)):
        raise ValueError("incomplete original sidecars")

    funding = Counter()
    actions = Counter()
    first_failure = first_water = None
    longest = run = 0
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
        if first_water is None and event["positive_water_uptake"]:
            first_water = row["t"]

    resource = life["observer_resource_acquisition"]["summary"]
    upper = (
        audit_upper_cost_trace(life)
        if life.get("candidate_f_cost_control") is not None else None)
    frontier = life.get("frontier_information")
    steps = len(rows)
    return {
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
        "frontier_information": frontier,
        "upper_cost_control": upper,
    }


def paired_class(candidate_terminal, upper_terminal):
    if candidate_terminal not in ("dead", "censored"):
        raise ValueError("invalid Candidate-F terminal")
    if upper_terminal not in ("dead", "censored"):
        raise ValueError("invalid upper-cost terminal")
    candidate_survives = candidate_terminal == "censored"
    upper_survives = upper_terminal == "censored"
    if upper_survives and not candidate_survives:
        return "UPPER_SURVIVES_CANDIDATE_DIES"
    if candidate_survives and not upper_survives:
        return "CANDIDATE_SURVIVES_UPPER_DIES"
    if candidate_survives:
        return "BOTH_SURVIVE"
    return "BOTH_DIE"


def aggregate(cases):
    """Descriptive arm totals plus paired logical counterexamples."""
    groups = {}
    for policy in POLICIES:
        selected = [
            row for row in cases
            if row["identity"]["policy"] == policy]
        steps = sum(row["energy"]["steps_lived"] for row in selected)
        paid = {
            channel: sum(
                row["energy"]["paid"][channel] for row in selected)
            for channel in ("energy", "vigilance")
        }
        funding = Counter()
        actions = Counter()
        revision = Counter()
        for row in selected:
            funding.update(row["behavior"]["funding_counts"])
            actions.update(row["behavior"]["actions"])
            revision[row["revision"]["status"]] += 1
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
            "inactive_fraction": (
                actions["physical_inactivity"] / steps
                if steps else None),
            "positive_water_uptakes": sum(
                row["behavior"]["positive_water_uptakes"]
                for row in selected),
            "positive_food_uptakes": sum(
                row["behavior"]["positive_food_uptakes"]
                for row in selected),
            "revision_statuses": dict(sorted(revision.items())),
            "scientific_verdict": "NOT_EVALUATED",
        }

    by_block = {}
    for row in cases:
        block = row["identity"]["block"]
        policy = row["identity"]["policy"]
        if policy in by_block.setdefault(block, {}):
            raise ValueError("duplicate policy inside opportunity block")
        by_block[block][policy] = row
    if len(by_block) != 12:
        raise ValueError("exactly twelve paired opportunity blocks required")

    paired = []
    classes = Counter()
    upper_vs_candidate = Counter()
    upper_vs_reference = Counter()
    for block in sorted(by_block):
        arms = by_block[block]
        if set(arms) != set(POLICIES):
            raise ValueError("incomplete three-arm opportunity block")
        ref = arms[REFERENCE]
        cand = arms[CANDIDATE]
        upper = arms[UPPER_COST]
        cls = paired_class(
            cand["energy"]["terminal"], upper["energy"]["terminal"])
        classes[cls] += 1

        def compare(a, b):
            return "win" if a > b else "loss" if a < b else "tie"

        cand_steps = cand["energy"]["steps_lived"]
        upper_steps = upper["energy"]["steps_lived"]
        ref_steps = ref["energy"]["steps_lived"]
        upper_vs_candidate[compare(upper_steps, cand_steps)] += 1
        upper_vs_reference[compare(upper_steps, ref_steps)] += 1
        paired.append({
            "block": block,
            "classification": cls,
            "reference_terminal": ref["energy"]["terminal"],
            "candidate_terminal": cand["energy"]["terminal"],
            "upper_cost_terminal": upper["energy"]["terminal"],
            "reference_steps": ref_steps,
            "candidate_steps": cand_steps,
            "upper_cost_steps": upper_steps,
            "upper_minus_candidate_steps": upper_steps - cand_steps,
            "upper_minus_reference_steps": upper_steps - ref_steps,
        })

    strict = classes["UPPER_SURVIVES_CANDIDATE_DIES"]
    return {
        "arms": groups,
        "paired_blocks": paired,
        "paired_classes": dict(sorted(classes.items())),
        "upper_lifespan_vs_candidate": dict(sorted(
            upper_vs_candidate.items())),
        "upper_lifespan_vs_reference": dict(sorted(
            upper_vs_reference.items())),
        "strict_cost_only_counterexample_blocks": strict,
        "engineering_continuation_rule_met": strict > 0,
        "causal_interpretation": (
            "STRICT_COUNTEREXAMPLE_TO_UNIVERSAL_COST_SUFFICIENCY"
            if strict > 0 else
            "NO_STRICT_COUNTEREXAMPLE_IN_SMALL_OVERCHARGED_PANEL"),
        "cost_matching_claim":
            "UPPER_COST_NOT_EXACT_MATCH_OR_MEDIATION",
        "analysis_unit":
            "TWELVE_MATCHED_DEVELOPMENT_OPPORTUNITIES_NOT_INDEPENDENT_POPULATIONS",
        "scientific_verdict": "NOT_EVALUATED",
    }


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

    # All source locks pass before these imports can construct a World.
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
                "upper_cost_authenticated": (
                    row["behavior"]["upper_cost_control"] is not None),
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
            "COMPLETE_DESCRIPTIVE_COST_VS_POLICY_DEVELOPMENT_NOT_GATE",
        "cases": cases,
        "summary": aggregate(cases),
    }
    _write_json(output / "results.json", result)
    inventory = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(output.iterdir()) if path.is_file()
    }
    _write_json(output / "SHA256.json", inventory)
    print("DIAGNOSTIC_SUMMARY " + canonical(result["summary"]), flush=True)
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
            parser.error("--output required for the frozen single execution")
        run(args.output, args.expected_sha, args.expected_protocol)
