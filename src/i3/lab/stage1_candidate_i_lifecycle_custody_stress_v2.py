"""Candidate-I lifecycle custody stress v2.

Protocol: docs/STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2.md.

Engineering only. Replays the historical already-exposed lifecycle gate and
adds no-World production H/I sequential funding cases bridged into Stage-0.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
import sys
from types import MethodType

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    debit_cognition, transition)
from ..modules.genome import digest as genome_digest, generation_zero
from ..modules.personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind)
from ..modules.personal_shared_prior_candidate_i_mind import (
    PersonalSharedPriorCandidateIMind)
from . import stage0_revision as revision
from . import stage1_candidate_i_lifecycle_custody_stress as L
from . import stage1_multiphase_processing_reducer_repair as M

SCHEMA = "i3-candidate-i-lifecycle-custody-stress-v2/v1"
PROTOCOL = "STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2"
SYNTHETIC_BODY = (0.15, 80.0, 80.0, 80.0, 80.0)
NEXT_BODY = (80.0, 80.0, 80.0, 80.0, 80.0)
STAGE_A_WORK = CognitiveWork(cycles=5)
ZERO_WORK = CognitiveWork()
GENOME_SEED = 901


def _cap(body):
    return {
        "body": tuple(body),
        "here": (False, ()),
        "neighbors": (None, None, None, None),
        "inventory": (),
    }


def _forced_complete_fallback_probe(self, _cap, budget):
    """Spend generic Stage A, then let production H decide Stage B."""
    budget.spend(STAGE_A_WORK)
    return {
        "complete": True,
        "relevant": False,
        "classification": "FALLBACK",
        "phase": "SYNTHETIC_GENERIC_COMPLETE_STAGE_A",
        "funding": "FUNDED",
        "work": STAGE_A_WORK,
        "body_after_computation": tuple(budget.remaining),
    }


def _install_forced_probe(mind):
    mind._probe = MethodType(_forced_complete_fallback_probe, mind)


def _prime_drink_support(mind):
    mind.effects.observe(
        ("boire",), (-0.5, -0.2, 35.0, 0.0, 0.0))


def _authority_before_followup(mind):
    return {
        "last": deepcopy(mind.last),
        "pending_branch": deepcopy(mind._pending_branch),
        "settlement_start": deepcopy(mind._branch_decision_start_body),
        "settlement_work": mind._branch_decision_work,
        "pending_opportunity_presence":
            deepcopy(mind._pending_opportunity_presence),
        "pending_opportunity_commit":
            deepcopy(mind._pending_opportunity_commit),
    }


def _run_forced_decision(mind):
    _install_forced_probe(mind)
    budget = CognitiveBudget(SYNTHETIC_BODY, BodyLaws())
    action, param, work, info = mind.decide(
        _cap(SYNTHETIC_BODY), budget)
    return {
        "mind": mind,
        "action": action,
        "param": param,
        "work": work,
        "info": info,
        "budget_work": budget.work,
        "body_after_cognition": tuple(budget.remaining),
        "authority_after": _authority_before_followup(mind),
    }


def _zero_bill():
    return {
        channel: {"requested": 0.0, "paid": 0.0, "unpaid": 0.0}
        for channel in ("energy", "vigilance")
    }


def _detached_revision_join(case, policy):
    """Join the actual production info/work through Stage-0 without World."""
    laws = BodyLaws()
    work = case["work"]
    decision_after, decision_bill = debit_cognition(
        SYNTHETIC_BODY, laws, work)
    physical, dead = transition(
        SYNTHETIC_BODY, case["action"], laws, work)
    if dead:
        raise RuntimeError("generic sequential fixture unexpectedly died")

    work_dict = asdict(work)
    zero = asdict(ZERO_WORK)
    row = {
        "t": 1,
        "action": case["action"],
        "param": case["param"],
        "option": case["info"].get("option"),
        "body": list(physical),
        "pos": [0, 0],
        "dead": [],
        "funding_phases": {
            "decision": {
                "work": dict(work_dict),
                "accounting": deepcopy(decision_bill),
                "body_before": list(SYNTHETIC_BODY),
                "body_after_debit": list(decision_after),
            },
            "learning": {
                "work": dict(zero),
                "accounting": _zero_bill(),
                "body_before": list(physical),
                "body_after_debit": list(physical),
            },
        },
        "info": deepcopy(case["info"]),
    }
    event = {
        "step": 1,
        "action": case["action"],
        "param": case["param"],
        "chosen_option": case["info"].get("option"),
        "death_causes": [],
        "world_position_observer_only": [0, 0],
        "personal_position": [0, 0],
        "body_before_decision": list(SYNTHETIC_BODY),
        "body_after_physics": list(physical),
        "body_after_paid_learning": list(physical),
        "decision_funding": case["info"]["funding"],
        "decision_outcome":
            case["info"]["observer"]["decision_outcome"],
        "capture_here_water": False,
        "positive_water_uptake": False,
        "water_uptake_above_decay": None,
        "phase_payment": {
            "decision": {
                "work": dict(work_dict),
                "accounting": deepcopy(decision_bill),
            },
            "learning": {
                "work": dict(zero),
                "accounting": _zero_bill(),
            },
        },
        "paid_decision_work": dict(work_dict),
        "paid_learning_work": dict(zero),
    }
    life = {
        "manifest": {
            "world": {
                "spawn": [0, 0],
                "laws": laws.as_dict(),
            },
            "experimental_policy": {"name": policy},
        },
        "trace": [row],
        "observer_resource_acquisition": {
            "schema": "i3-p5d-resource-acquisition-observer/v1",
            "steps": [event],
        },
    }
    owner = revision._processing_work(
        life, row, work_dict)
    reduced = revision._resource_events(life)
    if len(reduced) != 1:
        raise RuntimeError("detached reducer returned wrong row count")
    return {
        "processing_owner_work": owner,
        "processing_paid": reduced[0]["processing_paid"],
        "positive_drink": reduced[0]["positive_drink"],
        "total_work": work_dict,
        "decision_after_debit": tuple(decision_after),
        "physical_body": tuple(physical),
    }


def _followup_cleanup(case):
    mind = case["mind"]
    before = _authority_before_followup(mind)
    budget = CognitiveBudget(NEXT_BODY, BodyLaws())
    action, param, work, info = mind.decide(
        _cap(NEXT_BODY), budget)
    after = _authority_before_followup(mind)
    return {
        "before_last_none": before["last"] is None,
        "before_pending_branch_none":
            before["pending_branch"] is None,
        "before_pending_opportunity_none": (
            before["pending_opportunity_presence"] is None
            and before["pending_opportunity_commit"] is None),
        "previous_settlement_bound_to_forced_body":
            before["settlement_start"] == SYNTHETIC_BODY,
        "work_matches": work == budget.work,
        "new_settlement_current": (
            after["settlement_start"] is None
            or after["settlement_start"] == NEXT_BODY),
        "stale_last_not_resurrected": (
            mind.last is None
            or tuple(mind.last[0]) != SYNTHETIC_BODY),
        "persistent_reference": (
            info.get("persistent_simulation_mode", "reference")
            == "reference"
            and info.get(
                "persistent_projection_accounting", "chunk_end")
            == "chunk_end"),
        "route": info.get(
            "candidate_i_route", info.get("candidate_h_route")),
        "action": action,
        "param": param,
    }


def _shape_h(case):
    info = case["info"]
    return {
        "route": info.get("candidate_h_route"),
        "public_funding": info.get("funding"),
        "observer_outcome":
            info.get("observer", {}).get("decision_outcome"),
        "action_none": case["action"] is None and case["param"] is None,
        "stage_a_exact":
            info.get("candidate_h_stage_a_work")
            == asdict(STAGE_A_WORK),
        "stage_b_zero":
            info.get("candidate_h_stage_b_work")
            == asdict(ZERO_WORK),
        "total_exact":
            info.get("candidate_h_total_work")
            == asdict(STAGE_A_WORK)
            == asdict(case["work"])
            == asdict(case["budget_work"]),
        "body_exact": tuple(
            info.get("candidate_h_body_after_cognition", ()))
            == case["body_after_cognition"],
        "persistent_reference": (
            info.get("persistent_simulation_mode") == "reference"
            and info.get("persistent_projection_accounting")
            == "chunk_end"),
    }


def _shape_i(case):
    info = case["info"]
    return {
        "route": info.get("candidate_i_route"),
        "nested_route": info.get("candidate_h_route"),
        "public_funding": info.get("funding"),
        "observer_outcome":
            info.get("observer", {}).get("decision_outcome"),
        "omega_unused":
            info.get("candidate_i_first_contact_omega_used") is False,
        "post_contact_source":
            info.get("candidate_i_post_contact_source"),
        "action_none": case["action"] is None and case["param"] is None,
        "stage_a_exact":
            info.get("candidate_h_stage_a_work")
            == asdict(STAGE_A_WORK),
        "stage_b_zero":
            info.get("candidate_h_stage_b_work")
            == asdict(ZERO_WORK),
        "total_exact":
            info.get("candidate_h_total_work")
            == asdict(STAGE_A_WORK)
            == asdict(case["work"])
            == asdict(case["budget_work"]),
        "body_exact": tuple(
            info.get("candidate_h_body_after_cognition", ()))
            == case["body_after_cognition"],
        "persistent_reference": (
            info.get("persistent_simulation_mode") == "reference"
            and info.get("persistent_projection_accounting")
            == "chunk_end"),
    }


def _forced_cases():
    genome = generation_zero(GENOME_SEED)
    h = PersonalRelevanceCandidateHMind(
        deepcopy(genome), 9201,
        observer_decision_diagnostics=True,
        observer_full_competition=True)
    native = PersonalSharedPriorCandidateIMind(
        deepcopy(genome), 9202,
        observer_decision_diagnostics=True,
        observer_full_competition=True)
    omega0 = PersonalSharedPriorCandidateIMind(
        deepcopy(genome), 9202,
        first_contact_omega_override=0.0,
        observer_decision_diagnostics=True,
        observer_full_competition=True)

    for mind in (native, omega0):
        _prime_drink_support(mind)

    h_case = _run_forced_decision(h)
    native_case = _run_forced_decision(native)
    omega0_case = _run_forced_decision(omega0)

    joins = {
        "h": _detached_revision_join(
            h_case, "personal_relevance_candidate_h_v1"),
        "native": _detached_revision_join(
            native_case, "personal_shared_prior_candidate_i_v1"),
        "omega0": _detached_revision_join(
            omega0_case,
            "personal_shared_prior_candidate_i_omega0_ablation_v1"),
    }
    cleanup = {
        "h": _followup_cleanup(h_case),
        "native": _followup_cleanup(native_case),
        "omega0": _followup_cleanup(omega0_case),
    }
    return {
        "genome_sha256": genome_digest(genome),
        "h": _shape_h(h_case),
        "native": _shape_i(native_case),
        "omega0": _shape_i(omega0_case),
        "joins": joins,
        "cleanup": cleanup,
        "omega0_custody": {
            "native_omega": native.first_contact_omega,
            "omega0_applied": omega0.first_contact_omega,
            "native_genome_omega": genome["genes"]["omega"],
            "same_inherited_genome":
                genome_digest(genome) == genome_digest(genome),
            "branch_memory_individual":
                native.branch_memory is not omega0.branch_memory,
            "opportunity_memory_individual":
                native.opportunity_memory is not omega0.opportunity_memory,
            "effects_individual":
                native.effects is not omega0.effects,
            "values_individual":
                native.values is not omega0.values,
        },
    }


def _geometry():
    laws = BodyLaws()
    after, _ = debit_cognition(
        SYNTHETIC_BODY, laws, STAGE_A_WORK)
    base_unfunded = False
    try:
        debit_cognition(
            after, laws, CognitiveWork(cycles=3))
    except CognitiveFundingError:
        base_unfunded = True
    return {
        "body": SYNTHETIC_BODY,
        "stage_a_work": asdict(STAGE_A_WORK),
        "body_after_stage_a": after,
        "energy_after_stage_a": after[0],
        "vigilance_after_stage_a": after[4],
        "three_cycle_base_unfunded": base_unfunded,
    }


def characterize():
    historical = L.characterize()
    reducer = M.characterize()
    geometry = _geometry()
    forced = _forced_cases()

    matrix = historical["runtime_matrix"]
    exact_old_matrix = (
        matrix["families"] == ("stable", "depletion", "pulse")
        and matrix["policies"] == (
            "personal_relevance_candidate_h_v1",
            "personal_shared_prior_candidate_i_v1",
            "personal_shared_prior_candidate_i_omega0_ablation_v1")
        and matrix["development_index"] == 0
        and matrix["world_seed"] == 2000
        and matrix["genome_seed"] == 901
        and matrix["life_seed"] == 7_490_003
        and matrix["horizon"] == 24
        and matrix["lives"] == 9
        and historical["smoke_failures"] == [])

    h = forced["h"]
    native = forced["native"]
    omega0 = forced["omega0"]
    joins = forced["joins"]
    cleanup = forced["cleanup"]
    omega = forced["omega0_custody"]

    h_ok = (
        h["route"] == "P1.3_FINAL"
        and h["public_funding"] == "NO_PROCESSING_BUDGET"
        and h["observer_outcome"] == "no_processing_budget"
        and h["action_none"]
        and h["stage_a_exact"]
        and h["stage_b_zero"]
        and h["total_exact"]
        and h["body_exact"]
        and h["persistent_reference"])

    def i_ok(row):
        return (
            row["route"] == "POST_CONTACT_CANDIDATE_H"
            and row["nested_route"] == "P1.3_FINAL"
            and row["public_funding"] == "NO_PROCESSING_BUDGET"
            and row["observer_outcome"] == "no_processing_budget"
            and row["omega_unused"]
            and row["post_contact_source"]
            == "CANDIDATE_H_1163_UNCHANGED"
            and row["action_none"]
            and row["stage_a_exact"]
            and row["stage_b_zero"]
            and row["total_exact"]
            and row["body_exact"]
            and row["persistent_reference"])

    joins_ok = all(
        row["processing_owner_work"] == asdict(ZERO_WORK)
        and row["processing_paid"] is False
        and row["positive_drink"] is False
        and row["total_work"] == asdict(STAGE_A_WORK)
        for row in joins.values())

    cleanup_ok = all(
        row["before_last_none"]
        and row["before_pending_branch_none"]
        and row["before_pending_opportunity_none"]
        and row["previous_settlement_bound_to_forced_body"]
        and row["work_matches"]
        and row["new_settlement_current"]
        and row["stale_last_not_resurrected"]
        and row["persistent_reference"]
        for row in cleanup.values())

    rules = {
        "V0_prerequisite_custody": (
            historical["verdict"]
            == "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_PASS"
            and all(historical["rules"].values())
            and reducer["verdict"]
            == "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS"
            and all(reducer["rules"].values())),
        "V1_exact_original_stress_preservation":
            exact_old_matrix,
        "V2_generic_forced_funding_geometry": (
            geometry["body"] == SYNTHETIC_BODY
            and geometry["stage_a_work"] == asdict(STAGE_A_WORK)
            and abs(geometry["energy_after_stage_a"] - 0.05) <= 1e-12
            and geometry["three_cycle_base_unfunded"]),
        "V3_actual_candidate_h_sequential_receipt":
            h_ok,
        "V4_actual_candidate_i_post_contact_receipts": (
            i_ok(native)
            and i_ok(omega0)
            and omega["omega0_applied"] == 0.0
            and omega["native_genome_omega"] != 0.0
            and omega["native_omega"]
            == omega["native_genome_omega"]
            and omega["branch_memory_individual"]
            and omega["opportunity_memory_individual"]
            and omega["effects_individual"]
            and omega["values_individual"]),
        "V5_repaired_reducer_end_to_end":
            joins_ok,
        "V6_following_decision_authority_cleanup":
            cleanup_ok,
        "V7_historical_reducer_regressions": (
            reducer["verdict"]
            == "MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS"
            and reducer["composite_prerequisite"]
            == "COMPOSITE_FUNDING_REDUCER_REPAIR_PASS"),
        "V8_authority_boundary": True,
    }
    passed = all(rules.values())
    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2.md",
        "scientific_gate": "NOT_EVALUATED",
        "fresh_development_condition_opened": False,
        "selection_validation_reserve_access": False,
        "60_61_evidence_acceptance_input": False,
        "62_63_evidence_acceptance_input": False,
        "64_65_evidence_acceptance_input": False,
        "historical_lifecycle": {
            "verdict": historical["verdict"],
            "rules": historical["rules"],
            "runtime_matrix": matrix,
            "smoke_failures": historical["smoke_failures"],
        },
        "multiphase_reducer": {
            "verdict": reducer["verdict"],
            "rules": reducer["rules"],
            "composite_prerequisite": reducer["composite_prerequisite"],
        },
        "geometry": geometry,
        "forced": forced,
        "rules": rules,
        "verdict": (
            "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_PASS"
            if passed else
            "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_DEFECT"),
        "J1_J7_verdict_authorized": False,
        "new_live_protocol_proposal_authorized": passed,
        "new_live_panel_execution_authorized": False,
        "stage2_authorized": False,
    }


def run(path):
    report = characterize()
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2 " + json.dumps({
        "verdict": report["verdict"],
        "rules": report["rules"],
        "geometry": report["geometry"],
        "forced": {
            "h": report["forced"]["h"],
            "native": report["forced"]["native"],
            "omega0": report["forced"]["omega0"],
            "joins": report["forced"]["joins"],
        },
    }, sort_keys=True))
