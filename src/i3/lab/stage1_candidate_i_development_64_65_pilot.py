"""Frozen Candidate-I 64/65 DEVELOPMENT runner and read-only reductions.

Importing this module does not import Mind, World, runtime.life or generate a
life. Fresh 64/65 execution requires a later separately reviewed one-shot
transport after this runner is merged.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from i3.lab import stage1_candidate_i_development_64_65_plan as design

IMPLEMENTATION_BASELINE = "f64d818a80464fdb50114d0186e7fe5bd9885639"
PROTOCOL = design.PROTOCOL
POLICIES = design.POLICIES
REFERENCE = design.REFERENCE
CANDIDATE_H = design.CANDIDATE_H
CANDIDATE_I = design.CANDIDATE_I
CANDIDATE_I_OMEGA0 = design.CANDIDATE_I_OMEGA0
HORIZON = design.HORIZON
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")
FUNDING = {
    "NO_PROCESSING_BUDGET": "no_processing_budget",
    "NO_FUNDED_SCORE": "no_funded_score",
    "NO_FUNDED_MOTOR": "control_rejected",
    "FUNDED": "action_admitted",
}
COMPOSITE = "NO_FUNDED_RELEVANCE_PROBE"
INCOMPLETE_PROBE = ("NO_PROCESSING_BUDGET", "NO_FUNDED_SCORE")
FIRST_CONTACT_ROUTES = (
    "INFORMATION_FINAL", "P1.3_BASE_FINAL", "PROBE_UNFUNDED")
CAPTURE_KEYS = (
    "capture_here_water", "capture_here_food_tokens",
    "capture_neighbor_water_cells", "capture_neighbor_food_cells",
    "capture_inventory", "capture_food", "capture_water",
)


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def plan():
    return design.validate_plan()


def _git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def validate_launch(expected_sha, expected_protocol):
    """Reject source/protocol drift before importing runtime or a World."""
    if (type(expected_sha) is not str or len(expected_sha) != 40 or
            any(c not in "0123456789abcdef" for c in expected_sha) or
            _git("rev-parse", "HEAD") != expected_sha):
        raise ValueError("exact prospective source SHA required")
    if (expected_protocol != design.EXPECTED_PLAN_SHA256 or
            design.digest(plan()) != design.EXPECTED_PLAN_SHA256):
        raise ValueError("prospective protocol digest mismatch")
    try:
        _git(
            "merge-base", "--is-ancestor",
            design.REQUIRED_LIFECYCLE_STRESS_COMMIT, "HEAD")
    except subprocess.CalledProcessError as exc:
        raise ValueError(
            "execution source must descend from lifecycle-stress authority"
        ) from exc
    if _git(
            "status", "--porcelain", "--untracked-files=all", "--",
            "src/i3", "tests/i3"):
        raise ValueError("dirty I3 source")
    protected = _git(
        "diff", "--name-only", IMPLEMENTATION_BASELINE, "HEAD", "--",
        "src/i3/modules", "src/i3/runtime",
        "src/i3/lab/p2_ecologies.py", "src/i3/lab/worldgen.py",
        "src/i3/lab/stage0_energy.py", "src/i3/lab/stage0_revision.py",
        "src/i3/lab/stage1_candidate_i_lifecycle_custody_stress.py",
        "src/i3/docs/STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS.md",
        "src/i3/lab/stage1_candidate_i_development_64_65_plan.py",
        "src/i3/docs/studies/stage1-candidate-i-development-64-65/PROTOCOL.md",
        "config/engine-registry.json")
    if protected:
        raise ValueError(
            "pilot must preserve reviewed Candidate-I 64/65 implementation")


def validate_lifecycle_stress():
    """Rerun frozen L0-L11 on already-exposed fixtures before fresh birth."""
    from i3.lab import stage1_candidate_i_lifecycle_custody_stress as stress

    report = stress.characterize()
    if report["verdict"] != "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_PASS":
        raise ValueError("Candidate-I lifecycle custody stress is not PASS")
    if report["fresh_development_condition_opened"]:
        raise ValueError("lifecycle stress unexpectedly opened fresh development")
    if report["J1_J7_verdict_authorized"]:
        raise ValueError("lifecycle stress gained scientific authority")
    return report["verdict"]


def _work(value, label="work"):
    if type(value) is not dict or set(value) != set(WORK_KEYS):
        raise ValueError("complete " + label + " vector required")
    if any(
            type(value[key]) is not int or value[key] < 0
            for key in WORK_KEYS):
        raise ValueError("nonnegative integer " + label + " required")
    return tuple(value[key] for key in WORK_KEYS)


def _work_add(left, right):
    return tuple(a + b for a, b in zip(_work(left), _work(right)))


def _normalized_funding(info, event):
    public = info.get("funding")
    if event.get("decision_funding") != public:
        raise ValueError("resource processing status disagreement")
    if public in FUNDING:
        normalized = public
    elif public == COMPOSITE:
        h_nested = info.get("candidate_h_probe_funding")
        i_nested = info.get("candidate_i_probe_funding")
        if h_nested not in INCOMPLETE_PROBE:
            raise ValueError("invalid composite relevance-probe funding")
        if i_nested is not None and i_nested != h_nested:
            raise ValueError("Candidate-I composite funding witnesses disagree")
        normalized = h_nested
    else:
        raise ValueError("resource processing status disagreement")

    observer = info.get("observer")
    expected = FUNDING[normalized]
    if (type(observer) is not dict or
            event.get("decision_outcome") != expected or
            observer.get("decision_outcome") != expected):
        raise ValueError("resource processing status disagreement")
    return {
        "public": public,
        "normalized": normalized,
        "processing_paid": normalized != "NO_PROCESSING_BUDGET",
        "expected_outcome": expected,
    }


def _validate_candidate_h_row(row, info):
    route = info.get("candidate_h_route")
    if route not in ("P1.3_FINAL", "CANDIDATE_F_FINAL", "PROBE_UNFUNDED"):
        raise ValueError("invalid Candidate-H route")
    if (
            info.get("persistent_simulation_mode") != "reference" or
            info.get("persistent_projection_accounting") != "chunk_end"):
        raise ValueError("Candidate-H persistent projector drift")

    stage_a = info.get("candidate_h_stage_a_work")
    stage_b = info.get("candidate_h_stage_b_work")
    total = info.get("candidate_h_total_work")
    if _work_add(stage_a, stage_b) != _work(total):
        raise ValueError("Candidate-H phase work does not sum")
    if _work(total) != _work(
            row["funding_phases"]["decision"]["work"]):
        raise ValueError("Candidate-H total work differs from runtime bill")

    after = info.get("candidate_h_body_after_cognition")
    paid = row["funding_phases"]["decision"]["body_after_debit"]
    if (type(after) not in (list, tuple) or len(after) != len(paid) or
            max(abs(a - b) for a, b in zip(after, paid)) > 1e-12):
        raise ValueError("Candidate-H body settlement mismatch")
    return route


def _first_contact_omega_used(info):
    route = info.get("candidate_i_route")
    if route not in ("INFORMATION_FINAL", "P1.3_BASE_FINAL"):
        return False
    direct = info.get("candidate_i_direct_trial_count")
    imagined = info.get("candidate_i_imagined_trial_count")
    if (type(direct) is not int or direct < 0 or
            type(imagined) is not int or imagined < 0):
        raise ValueError("Candidate-I trial counts missing")
    return direct + imagined > 0


def _validate_candidate_i_row(row, info, policy):
    route = info.get("candidate_i_route")
    if route not in (
            "INFORMATION_FINAL", "P1.3_BASE_FINAL",
            "POST_CONTACT_CANDIDATE_H", "PROBE_UNFUNDED"):
        raise ValueError("invalid Candidate-I route")

    if (
            info.get("persistent_simulation_mode") != "reference" or
            info.get("persistent_projection_accounting") != "chunk_end"):
        raise ValueError("Candidate-I persistent projector drift")

    if route == "POST_CONTACT_CANDIDATE_H":
        if info.get("candidate_i_first_contact_omega_used") is not False:
            raise ValueError("Candidate-I post-contact read first-contact omega")
        _validate_candidate_h_row(row, info)
        return {
            "route": route,
            "omega_used": False,
            "direct_trials": 0,
            "imagined_trials": 0,
            "body_gap": 0.0,
        }

    stage_a = info.get("candidate_i_stage_a_work")
    stage_b = info.get("candidate_i_stage_b_work")
    total = info.get("candidate_i_total_work")
    if _work_add(stage_a, stage_b) != _work(total):
        raise ValueError("Candidate-I phase work does not sum")
    if _work(total) != _work(
            row["funding_phases"]["decision"]["work"]):
        raise ValueError("Candidate-I total work differs from runtime bill")

    after = info.get("candidate_i_body_after_cognition")
    paid = row["funding_phases"]["decision"]["body_after_debit"]
    if type(after) not in (list, tuple) or len(after) != len(paid):
        raise ValueError("Candidate-I body receipt missing")
    gap = max(abs(a - b) for a, b in zip(after, paid))
    if gap > 1e-12:
        raise ValueError("Candidate-I body settlement mismatch")

    source = info.get("omega_source")
    omega = info.get("first_contact_omega")
    if policy == CANDIDATE_I:
        if source != "GENOME_V4_OMEGA":
            raise ValueError("native Candidate-I did not use genome omega source")
    elif policy == CANDIDATE_I_OMEGA0:
        if source != "SOFTWARE_OMEGA_ABLATION" or omega != 0.0:
            raise ValueError("Candidate-I omega0 trace did not use zero override")

    direct = info.get("candidate_i_direct_trial_count", 0)
    imagined = info.get("candidate_i_imagined_trial_count", 0)
    if route != "PROBE_UNFUNDED":
        if (type(direct) is not int or direct < 0 or
                type(imagined) is not int or imagined < 0):
            raise ValueError("Candidate-I trial counts missing")
    else:
        direct = 0 if direct is None else direct
        imagined = 0 if imagined is None else imagined

    if route == "P1.3_BASE_FINAL":
        if (
                info.get("decision_projection_mode") != "reference" or
                info.get("candidate_i_first_contact_addend_mode")
                != "discard_both_bonus_terms"):
            raise ValueError("Candidate-I fallback geometry drift")
        observer = info.get("observer", {})
        for witness in observer.get("score_witness", ()):
            if (
                    witness.get("curiosity_bonus_applied") != 0.0 or
                    witness.get("risk_penalty_applied") != 0.0):
                raise ValueError("Candidate-I fallback applied legacy addend")
    elif route == "INFORMATION_FINAL":
        if info.get("decision_projection_mode") != "candidate_f":
            raise ValueError("Candidate-I information final geometry drift")
    elif route == "PROBE_UNFUNDED":
        if (info.get("funding") != COMPOSITE or
                row.get("action") is not None or
                row.get("option") is not None or any(_work(stage_b))):
            raise ValueError("Candidate-I unfunded probe gained final authority")

    return {
        "route": route,
        "omega_used": _first_contact_omega_used(info),
        "direct_trials": direct,
        "imagined_trials": imagined,
        "body_gap": gap,
    }


def behavioral_summary(life):
    """Reduce original paid witnesses only; never replay Candidate-I cognition."""
    rows = life["trace"]
    events = life["observer_resource_acquisition"]["steps"]
    competition = life["observer_full_competition"]["steps"]
    if (len(rows) != life["steps_lived"] or
            len(events) != len(rows) or len(competition) != len(rows)):
        raise ValueError("incomplete original sidecars")

    policy = life["manifest"].get(
        "experimental_policy", {}).get("name", REFERENCE)
    funding = Counter()
    normalized = Counter()
    actions = Counter()
    routes = Counter()
    first_failure = None
    longest = run = 0
    processing_collapse = 0
    omega_used = 0
    max_gap = 0.0
    direct_trials = imagined_trials = 0

    for row, event, comp in zip(rows, events, competition):
        info = row["info"]
        if (
                event["step"] != row["t"] or
                event["action"] != row["action"] or
                event["param"] != row["param"] or
                event["chosen_option"] != row["option"] or
                comp["physical_action"] != row["action"] or
                comp["funding"] != info["funding"]):
            raise ValueError("original sidecars disagree")

        process = _normalized_funding(info, event)
        funding[process["public"]] += 1
        normalized[process["normalized"]] += 1
        processing_collapse += (
            process["normalized"] == "NO_PROCESSING_BUDGET")
        actions[row["action"] or "physical_inactivity"] += 1

        if process["public"] != "FUNDED":
            run += 1
            longest = max(longest, run)
            if first_failure is None:
                first_failure = {
                    "step": row["t"],
                    "public_funding": process["public"],
                    "normalized_funding": process["normalized"],
                    "body_before":
                        row["funding_phases"]["decision"]["body_before"],
                    "work": row["funding_phases"]["decision"]["work"],
                }
        else:
            run = 0

        if policy == CANDIDATE_H:
            routes[_validate_candidate_h_row(row, info)] += 1
        elif policy in (CANDIDATE_I, CANDIDATE_I_OMEGA0):
            receipt = _validate_candidate_i_row(row, info, policy)
            routes[receipt["route"]] += 1
            omega_used += receipt["omega_used"]
            direct_trials += receipt["direct_trials"]
            imagined_trials += receipt["imagined_trials"]
            max_gap = max(max_gap, receipt["body_gap"])

    resource = life["observer_resource_acquisition"]["summary"]
    steps = len(rows)
    out = {
        "policy": policy,
        "funding_counts": dict(sorted(funding.items())),
        "normalized_funding_counts": dict(sorted(normalized.items())),
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

    if policy == CANDIDATE_H:
        out["candidate_h"] = {
            "routes": dict(sorted(routes.items())),
        }
    elif policy in (CANDIDATE_I, CANDIDATE_I_OMEGA0):
        summary = life.get("candidate_i")
        if type(summary) is not dict:
            raise ValueError("Candidate-I runtime summary missing")
        expected_first = (
            routes["INFORMATION_FINAL"]
            + routes["P1.3_BASE_FINAL"]
            + routes["PROBE_UNFUNDED"])
        if summary.get("first_contact_decisions") != expected_first:
            raise ValueError("Candidate-I first-contact route count mismatch")
        if summary.get("relevant_final") != routes["INFORMATION_FINAL"]:
            raise ValueError("Candidate-I information-final count mismatch")
        if summary.get("base_fallback_final") != routes["P1.3_BASE_FINAL"]:
            raise ValueError("Candidate-I fallback count mismatch")
        if summary.get("probe_unfunded") != routes["PROBE_UNFUNDED"]:
            raise ValueError("Candidate-I probe-failure count mismatch")
        if (
                summary.get("persistent_simulation_mode") != "reference" or
                summary.get("persistent_projection_accounting") != "chunk_end"):
            raise ValueError("Candidate-I runtime summary projector drift")

        native_omega = summary.get("first_contact_omega")
        if policy == CANDIDATE_I:
            if summary.get("omega_source") != "GENOME_V4_OMEGA":
                raise ValueError("native Candidate-I summary omega source drift")
            applied_omega = native_omega
            omega_source = "GENOME_V4_OMEGA"
        else:
            native_omega = summary.get("native_genome_omega")
            applied_omega = summary.get("applied_first_contact_omega")
            omega_source = summary.get("omega_source")
            if (
                    applied_omega != 0.0 or
                    summary.get("first_contact_omega") != 0.0 or
                    omega_source != "SAME_GENOME_SOFTWARE_ABLATION" or
                    summary.get("omega_ablation")
                    != "FIRST_CONTACT_ONLY_SAME_GENOME"):
                raise ValueError("omega0 runtime summary drift")

        out["candidate_i"] = {
            "routes": dict(sorted(routes.items())),
            "omega_used_decisions": omega_used,
            "direct_trials": direct_trials,
            "imagined_trials": imagined_trials,
            "native_genome_omega": native_omega,
            "applied_first_contact_omega": applied_omega,
            "omega_source": omega_source,
            "max_body_settlement_gap": max_gap,
        }
    return out


def _capture_equal(left, right):
    return all(left.get(key) == right.get(key) for key in CAPTURE_KEYS)


def _decision_signature(row):
    info = row["info"]
    return {
        "option": row["option"],
        "action": row["action"],
        "param": row["param"],
        "route": info.get("candidate_i_route"),
        "funding": info.get("funding"),
    }


def _prefix_step_equal(nrow, nevent, zrow, zevent):
    return (
        nrow["action"] == zrow["action"]
        and nrow["param"] == zrow["param"]
        and nevent["death_causes"] == zevent["death_causes"]
        and nevent["body_after_physics"] == zevent["body_after_physics"])


def paired_omega_receipt(native_life, zero_life):
    """Find the first native/omega0 decision divergence without replay."""
    if native_life["genome"] != zero_life["genome"]:
        raise ValueError("native/omega0 genome digest mismatch")
    native_summary = native_life.get("candidate_i", {})
    zero_summary = zero_life.get("candidate_i", {})
    if (
            native_summary.get("omega_source") != "GENOME_V4_OMEGA" or
            zero_summary.get("omega_source") != "SAME_GENOME_SOFTWARE_ABLATION" or
            zero_summary.get("native_genome_omega")
            != native_summary.get("first_contact_omega") or
            zero_summary.get("applied_first_contact_omega") != 0.0):
        raise ValueError("native/omega0 summary custody mismatch")

    nr = native_life["trace"]
    zr = zero_life["trace"]
    ne = native_life["observer_resource_acquisition"]["steps"]
    ze = zero_life["observer_resource_acquisition"]["steps"]
    if len(nr) != len(ne) or len(zr) != len(ze):
        raise ValueError("paired omega resource sidecar incomplete")

    prefix = 0
    divergence = None
    prefix_ok = True
    for index in range(min(len(nr), len(zr))):
        nrow, zrow = nr[index], zr[index]
        nev, zev = ne[index], ze[index]
        nsig, zsig = _decision_signature(nrow), _decision_signature(zrow)
        if nsig != zsig:
            ninfo, zinfo = nrow["info"], zrow["info"]
            common_state = (
                nev["body_before_decision"] == zev["body_before_decision"]
                and nev["personal_position"] == zev["personal_position"]
                and _capture_equal(nev, zev))
            native_omega_used = (
                _first_contact_omega_used(ninfo)
                and ninfo.get("omega_source") == "GENOME_V4_OMEGA")
            zero_omega_used = (
                _first_contact_omega_used(zinfo)
                and zinfo.get("omega_source") == "SOFTWARE_OMEGA_ABLATION"
                and zinfo.get("first_contact_omega") == 0.0)
            first_contact = (
                ninfo.get("candidate_i_route")
                in ("INFORMATION_FINAL", "P1.3_BASE_FINAL")
                and zinfo.get("candidate_i_route")
                in ("INFORMATION_FINAL", "P1.3_BASE_FINAL")
                and (
                    ninfo.get("candidate_i_direct_trial_count", 0)
                    + ninfo.get("candidate_i_imagined_trial_count", 0) > 0)
                and (
                    zinfo.get("candidate_i_direct_trial_count", 0)
                    + zinfo.get("candidate_i_imagined_trial_count", 0) > 0))
            divergence = {
                "step": nrow["t"],
                "common_predecision_state": common_state,
                "native": nsig,
                "omega0": zsig,
                "native_trace_omega": ninfo.get("first_contact_omega"),
                "omega0_trace_omega": zinfo.get("first_contact_omega"),
                "native_trace_omega_source": ninfo.get("omega_source"),
                "omega0_trace_omega_source": zinfo.get("omega_source"),
                "native_omega_used": native_omega_used,
                "omega0_override_used": zero_omega_used,
                "unsupported_first_contact": first_contact,
            }
            break
        if not _prefix_step_equal(nrow, nev, zrow, zev):
            prefix_ok = False
            break
        prefix += 1

    qualifies = bool(
        prefix_ok and divergence is not None
        and divergence["common_predecision_state"]
        and divergence["unsupported_first_contact"]
        and divergence["native_omega_used"]
        and divergence["omega0_override_used"])

    return {
        "schema": "i3-candidate-i-native-omega0-paired-divergence/v1",
        "native_genome_sha256": native_life["genome"],
        "omega0_genome_sha256": zero_life["genome"],
        "native_genome_omega": native_summary["first_contact_omega"],
        "native_applied_omega": native_summary["first_contact_omega"],
        "omega0_applied_omega": zero_summary["applied_first_contact_omega"],
        "identical_prefix_steps": prefix,
        "prefix_physics_identical": prefix_ok,
        "first_divergence_step":
            divergence["step"] if divergence is not None else None,
        "first_divergence": divergence,
        "native_steps_lived": native_life["steps_lived"],
        "omega0_steps_lived": zero_life["steps_lived"],
        "qualifies_for_J2": qualifies,
    }


def _policy_rows(cases, policy):
    return [row for row in cases if row["identity"]["policy"] == policy]


def aggregate(cases, omega_pairs):
    groups = {}
    for policy in POLICIES:
        selected = _policy_rows(cases, policy)
        steps = sum(row["energy"]["steps_lived"] for row in selected)
        paid = {
            channel: sum(row["energy"]["paid"][channel] for row in selected)
            for channel in ("energy", "vigilance")
        }
        funding = Counter()
        normalized = Counter()
        actions = Counter()
        routes = Counter()
        for row in selected:
            funding.update(row["behavior"]["funding_counts"])
            normalized.update(row["behavior"]["normalized_funding_counts"])
            actions.update(row["behavior"]["actions"])
            if "candidate_h" in row["behavior"]:
                routes.update(row["behavior"]["candidate_h"]["routes"])
            if "candidate_i" in row["behavior"]:
                routes.update(row["behavior"]["candidate_i"]["routes"])

        decisions = sum(funding.values())
        nonfunded = sum(v for k, v in funding.items() if k != "FUNDED")
        processing = normalized["NO_PROCESSING_BUDGET"]
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
            "normalized_funding_counts":
                dict(sorted(normalized.items())),
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
            "collected_inventory": sum(
                row["behavior"]["collected_inventory"]
                for row in selected),
            "consumed_inventory": sum(
                row["behavior"]["consumed_inventory"]
                for row in selected),
            "personally_mapped_cells": sum(
                row["behavior"]["personally_mapped_cells"]
                for row in selected),
            "revision_statuses": dict(Counter(
                row["revision"]["status"] for row in selected)),
            "routes": dict(sorted(routes.items())),
            "scientific_verdict": "NOT_EVALUATED",
        }

    native = groups[CANDIDATE_I]
    control = groups[CANDIDATE_H]
    native_resources = (
        native["positive_water_uptakes"] + native["positive_food_uptakes"])
    j2 = sum(pair["qualifies_for_J2"] for pair in omega_pairs)
    rules = {
        "J1_native_information_and_base_fallback_routes_both_observed":
            native["routes"].get("INFORMATION_FINAL", 0) > 0
            and native["routes"].get("P1.3_BASE_FINAL", 0) > 0,
        "J2_native_vs_omega0_common_state_first_contact_divergence_gt_0":
            j2 > 0,
        "J3_native_positive_resource_uptakes_gt_0":
            native_resources > 0,
        "J4_native_nonfunded_fraction_le_candidate_h":
            native["nonfunded_fraction"] <= control["nonfunded_fraction"],
        "J5_native_processing_collapse_fraction_le_candidate_h":
            native["processing_collapse_fraction"]
            <= control["processing_collapse_fraction"],
        "J6_native_paid_energy_per_lived_step_le_candidate_h":
            native["paid_per_lived_step"]["energy"]
            <= control["paid_per_lived_step"]["energy"],
        "J7_native_paid_vigilance_per_lived_step_le_candidate_h":
            native["paid_per_lived_step"]["vigilance"]
            <= control["paid_per_lived_step"]["vigilance"],
    }
    native["common_state_omega_divergence_blocks"] = j2
    native["engineering_continuation_rules"] = rules
    native["engineering_continuation_rule_met"] = all(rules.values())
    for policy in (REFERENCE, CANDIDATE_H, CANDIDATE_I_OMEGA0):
        groups[policy]["engineering_continuation_rule_met"] = None
    return groups


def _write_json(path, value):
    path.write_text(canonical(value) + "\n", encoding="utf-8")


def run(output, expected_sha, expected_protocol):
    validate_launch(expected_sha, expected_protocol)
    lifecycle_verdict = validate_lifecycle_stress()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)

    registration = {
        "plan": plan(),
        "protocol_sha256": design.EXPECTED_PLAN_SHA256,
        "execution_sha": expected_sha,
        "implementation_baseline": IMPLEMENTATION_BASELINE,
        "lifecycle_stress_verdict": lifecycle_verdict,
    }
    _write_json(output / "registration.json", registration)

    # All validation above precedes engine imports and possible births.
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
    omega_pairs = []
    native_life = None
    native_block = None

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

            if identity["policy"] == CANDIDATE_I:
                native_life = life
                native_block = identity["block"]
            elif identity["policy"] == CANDIDATE_I_OMEGA0:
                if native_life is None or native_block != identity["block"]:
                    raise ValueError("omega0 arm lacks matched native life")
                pair = paired_omega_receipt(native_life, life)
                pair["block"] = identity["block"]
                pair["family"] = identity["family"]
                pair["index"] = identity["index"]
                pair["genome_seed"] = identity["genome_seed"]
                pair["life_seed"] = identity["life_seed"]
                omega_pairs.append(pair)
                _write_json(output / "omega-pairs.json", omega_pairs)
                native_life = None
                native_block = None

            print(canonical({
                "completed": number + 1,
                "case": identity["case"],
                "terminal": energy["terminal"],
                "steps": energy["steps_lived"],
                "routes": row["behavior"].get(
                    "candidate_i",
                    row["behavior"].get("candidate_h", {})).get(
                        "routes"),
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

    if native_life is not None:
        raise RuntimeError("unpaired native Candidate-I life")
    if len(omega_pairs) != 12:
        raise RuntimeError("exactly 12 native/omega0 pair receipts required")
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
                        "four-arm opportunity mismatch: " + field)

    summary = aggregate(cases, omega_pairs)
    result = {
        **registration,
        "source_sha256": source["sha256"],
        "status":
            "COMPLETE_CANDIDATE_I_DEVELOPMENT_64_65_NOT_SCIENTIFIC_GATE",
        "cases": cases,
        "omega_pairs": omega_pairs,
        "summary": summary,
    }
    _write_json(output / "results.json", result)
    inventory = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(output.iterdir()) if path.is_file()
    }
    _write_json(output / "SHA256.json", inventory)
    print("CANDIDATE_I_64_65_SUMMARY " + canonical(summary), flush=True)
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
            "protocol_sha256": design.EXPECTED_PLAN_SHA256,
            "implementation_baseline": IMPLEMENTATION_BASELINE,
            "required_lifecycle_stress":
                "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_PASS",
        }))
    else:
        if not args.output:
            parser.error("--output required for frozen single execution")
        run(args.output, args.expected_sha, args.expected_protocol)
