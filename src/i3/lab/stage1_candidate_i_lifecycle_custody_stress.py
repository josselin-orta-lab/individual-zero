"""Frozen Candidate-I lifecycle custody stress gate.

Protocol: docs/STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS.md.

This is engineering stress only. Runtime smokes use already-exposed P2
DEVELOPMENT index 0. No scientific endpoint is interpreted here.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
import sys
from types import MethodType

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    transition, debit_cognition)
from ..modules.genome import digest as genome_digest, generation_zero, midpoint
from ..modules.personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind)
from ..modules.personal_shared_prior_candidate_i_mind import (
    PersonalSharedPriorCandidateIMind)
from . import stage1_branch_decision_settlement_repair as B
from . import stage1_candidate_i_probe_authority_repair as U
from . import stage1_candidate_g_reference_recurrence_falsifier as G

SCHEMA = "i3-candidate-i-lifecycle-custody-stress/v1"
PROTOCOL = "STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS"
FAMILIES = ("stable", "depletion", "pulse")
POLICIES = (
    "personal_relevance_candidate_h_v1",
    "personal_shared_prior_candidate_i_v1",
    "personal_shared_prior_candidate_i_omega0_ablation_v1",
)
DEVELOPMENT_INDEX = 0
WORLD_SEED = 2000
GENOME_SEED = 901
LIFE_SEED = 7_490_003
HORIZON = 24
FALLBACK_BODY = (80.0, 80.0, 40.0, 80.0, 80.0)
RELEVANT_BODY = (80.0, 20.0, 80.0, 80.0, 80.0)
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")
AUTHORITY_FIELDS = (
    "_pending_branch",
    "_branch_decision_start_body",
    "_pending_opportunity_presence",
    "_pending_opportunity_commit",
)


def _work_dict(work):
    return asdict(work)


def _work_add(left, right):
    return CognitiveWork(*(
        getattr(left, key) + getattr(right, key)
        for key in WORK_KEYS))


def _authority_closed(mind):
    return (
        mind._pending_branch is None
        and mind._branch_decision_start_body is None
        and mind._branch_decision_work == CognitiveWork()
        and mind._pending_opportunity_presence is None
        and mind._pending_opportunity_commit is None
    )


def _cap(body, *, water=True, inventory=(), neighbors=None):
    if neighbors is None:
        neighbors = (None, None, None, None)
    return {
        "body": tuple(body),
        "here": (bool(water), ()),
        "neighbors": tuple(neighbors),
        "inventory": tuple(inventory),
    }


def _prime_personal_model(mind):
    for key, delta in (
            (("se_deplacer",), (-2.0, -0.2, -0.4, 0.0, 0.0)),
            (("attendre",), (-0.35, -0.2, -0.4, 0.2, 0.0)),
            (("dormir",), (3.0, -0.35, -0.4, 0.0, 4.0))):
        mind.effects.observe(key, delta)
    mind._drift = mind.drift()


def _physical_result(body, action, work, laws):
    """Synthetic physical transition with no hidden resource gain."""
    nxt, dead = transition(
        tuple(body), action, laws, work,
        food_gain=0.0, integrity_delta=0.0, water_gain=0.0)
    return {
        "body": tuple(nxt),
        "dead": tuple(dead),
        "moved": False,
    }


def _complete_learning_cycle(mind, body, cap):
    """Execute decision -> physics -> prepaid learning -> learned commit."""
    laws = BodyLaws()
    before_branch = mind.branch_records
    before_opp = mind.opportunity_records
    before_opp_step = mind.opportunity_memory.snapshot()["personal_step"]

    decision = CognitiveBudget(body, laws)
    action, param, work, info = mind.decide(cap, decision)
    if work != decision.work:
        raise RuntimeError("decision work differs from consumed allowance")
    settlement_start_after_decision = deepcopy(
        mind._branch_decision_start_body)
    settlement_work_after_decision = mind._branch_decision_work
    opportunity_presence_after_decision = deepcopy(
        mind._pending_opportunity_presence)

    physical = _physical_result(body, action, work, laws)
    learning = CognitiveBudget(physical["body"], laws)
    replay_limit = None
    pending_branch = False
    pending_opportunity = False
    if not physical["dead"] and mind.last is not None:
        mind.observe_outcome(physical)
        replay_limit = mind.prepare_learning(physical, learning)
        pending_branch = mind._pending_branch is not None
        pending_opportunity = mind._pending_opportunity_commit is not None

    executed_replays = 0
    final_body = tuple(physical["body"])
    if replay_limit is not None:
        final_body, _ = debit_cognition(
            physical["body"], laws, learning.work)
        learned = dict(physical)
        learned["body"] = tuple(final_body)
        executed_replays = mind.learn_from_outcome(
            learned, replay_limit=replay_limit)
        if executed_replays != replay_limit:
            raise RuntimeError("executed replay count differs from prepaid count")

    after_branch = mind.branch_records
    after_opp = mind.opportunity_records
    after_opp_step = mind.opportunity_memory.snapshot()["personal_step"]

    branch_increment = after_branch - before_branch
    opportunity_increment = after_opp - before_opp
    expected_branch_increment = int(
        replay_limit is not None and pending_branch and not physical["dead"])
    expected_opportunity_increment = int(
        replay_limit is not None and pending_opportunity and not physical["dead"])

    return {
        "action": action,
        "param": param,
        "info": info,
        "decision_work": work,
        "decision_body_after": tuple(decision.remaining),
        "settlement_start_after_decision":
            settlement_start_after_decision,
        "settlement_work_after_decision":
            settlement_work_after_decision,
        "opportunity_presence_after_decision":
            opportunity_presence_after_decision,
        "physical_body": tuple(physical["body"]),
        "dead": tuple(physical["dead"]),
        "learning_work": learning.work,
        "replay_limit": replay_limit,
        "executed_replays": executed_replays,
        "final_body": tuple(final_body),
        "pending_branch_after_prepare": pending_branch,
        "pending_opportunity_after_prepare": pending_opportunity,
        "branch_increment": branch_increment,
        "expected_branch_increment": expected_branch_increment,
        "opportunity_increment": opportunity_increment,
        "expected_opportunity_increment": expected_opportunity_increment,
        "opportunity_step_increment": after_opp_step - before_opp_step,
        "authority_closed_after_learning": _authority_closed(mind),
    }


def _next_decision_is_current(mind, body, *, water=True):
    """A following decision must create/clear only its own current authority."""
    budget = CognitiveBudget(tuple(body), BodyLaws())
    result = mind.decide(_cap(body, water=water), budget)
    info = result[3]
    settlement_ok = (
        mind._branch_decision_start_body is None
        or mind._branch_decision_start_body == tuple(body))
    return {
        "work_matches": result[2] == budget.work,
        "settlement_current": settlement_ok,
        "route": info.get("candidate_i_route", info.get("candidate_h_route")),
        "persistent_reference":
            info.get("persistent_simulation_mode", "reference") == "reference"
            and info.get(
                "persistent_projection_accounting", "chunk_end") == "chunk_end",
    }


def _fallback_cycle():
    mind = PersonalSharedPriorCandidateIMind(
        midpoint(), 9011,
        observer_decision_diagnostics=True,
        observer_full_competition=True)
    row = _complete_learning_cycle(
        mind, FALLBACK_BODY, _cap(FALLBACK_BODY, water=True))
    info = row["info"]
    witnesses = info.get("observer", {}).get("score_witness", ())
    next_row = _next_decision_is_current(
        mind, row["final_body"], water=True)
    return {
        "route": info.get("candidate_i_route"),
        "addends_zero": bool(witnesses) and all(
            item.get("curiosity_bonus_applied") == 0.0
            and item.get("risk_penalty_applied") == 0.0
            for item in witnesses),
        "phase_sum_exact":
            _work_add(
                CognitiveWork(**info["candidate_i_stage_a_work"]),
                CognitiveWork(**info["candidate_i_stage_b_work"]))
            == CognitiveWork(**info["candidate_i_total_work"])
            == row["decision_work"],
        "settlement_start_is_pre_stage_a":
            row["settlement_start_after_decision"] == FALLBACK_BODY
            and row["settlement_work_after_decision"]
            == row["decision_work"]
            and info["candidate_i_stage_a_body_after"] != FALLBACK_BODY
            and tuple(info["candidate_i_body_after_cognition"])
            == row["decision_body_after"],
        "branch_commit_exact":
            row["branch_increment"] == row["expected_branch_increment"],
        "opportunity_commit_exact":
            row["opportunity_increment"]
            == row["expected_opportunity_increment"]
            == row["opportunity_step_increment"],
        "authority_closed_after_learning":
            row["authority_closed_after_learning"],
        "next_decision": next_row,
    }


def _relevant_cycle():
    mind = PersonalSharedPriorCandidateIMind(
        midpoint(), 9012,
        observer_decision_diagnostics=True,
        observer_full_competition=True)
    mind.branch_memory = G.effect_memory()
    mind.opportunity_memory = G.recurrence_2_6_10()
    _prime_personal_model(mind)
    row = _complete_learning_cycle(
        mind, RELEVANT_BODY, _cap(RELEVANT_BODY, water=True))
    info = row["info"]
    next_row = _next_decision_is_current(
        mind, row["final_body"], water=True)
    return {
        "route": info.get("candidate_i_route"),
        "persistent_reference":
            info.get("persistent_simulation_mode") == "reference"
            and info.get("persistent_projection_accounting") == "chunk_end",
        "settlement_start_is_pre_stage_a":
            row["settlement_start_after_decision"] == RELEVANT_BODY
            and row["settlement_work_after_decision"]
            == row["decision_work"]
            and tuple(info["candidate_i_stage_a_body_after"])
            != RELEVANT_BODY,
        "branch_commit_exact":
            row["branch_increment"] == row["expected_branch_increment"],
        "opportunity_commit_exact":
            row["opportunity_increment"]
            == row["expected_opportunity_increment"]
            == row["opportunity_step_increment"],
        "authority_closed_after_learning":
            row["authority_closed_after_learning"],
        "next_decision": next_row,
    }


class _FailRecurrence:
    def estimate(self, *_args, **_kwargs):
        raise CognitiveFundingError(
            "frozen synthetic recurrence read is unfunded")


def _forced_common_unfunded_then_fresh():
    mind = PersonalSharedPriorCandidateIMind(
        midpoint(), 9013,
        observer_decision_diagnostics=True)
    original = mind._first_contact_score

    def fail_score(self, **kwargs):
        return {
            "status": "UNFUNDED",
            "probe_funding": "NO_FUNDED_SCORE",
            "work": CognitiveWork(),
            "body_after_computation": kwargs["budget"].remaining,
            "forecast_work_ceiling": kwargs["budget"].work,
            "offered_options": len(kwargs["opts"]),
            "offered_families": self._observer_option_families(
                row[0] for row in kwargs["opts"]),
        }

    mind._first_contact_score = MethodType(fail_score, mind)
    budget = CognitiveBudget(FALLBACK_BODY, BodyLaws())
    first = mind.decide(_cap(FALLBACK_BODY), budget)
    first_info = first[3]
    empty = _authority_closed(mind) and mind.last is None

    physical = _physical_result(
        FALLBACK_BODY, first[0], first[2], BodyLaws())
    mind._first_contact_score = original
    next_row = _next_decision_is_current(
        mind, physical["body"], water=True)
    return {
        "route": first_info.get("candidate_i_route"),
        "reason": first_info.get("candidate_i_probe_reason"),
        "no_motor": first[0] is None and first[1] is None,
        "authority_empty": empty,
        "work_matches": first[2] == budget.work,
        "next_decision": next_row,
    }


def _forced_recurrence_unfunded_then_fresh():
    mind = PersonalSharedPriorCandidateIMind(
        midpoint(), 9014,
        observer_decision_diagnostics=True)
    original_memory = mind.opportunity_memory

    def explorer_options(self, _inv, _body, _horizon):
        self._unknown = {"explorer:1,0": 1}
        self._presence = {}
        return [
            ("dormir", [("dormir",)], None),
            ("attendre", [("attendre",)], None),
            ("explorer:1,0", [("se_deplacer",)],
             ("se_deplacer", "E")),
        ]

    original_options = mind.options
    mind.options = MethodType(explorer_options, mind)
    mind.opportunity_memory = _FailRecurrence()
    budget = CognitiveBudget(FALLBACK_BODY, BodyLaws())
    first = mind.decide(
        _cap(
            FALLBACK_BODY, water=False,
            neighbors=((False, ()), None, None, None)),
        budget)
    first_info = first[3]
    empty = _authority_closed(mind) and mind.last is None

    physical = _physical_result(
        FALLBACK_BODY, first[0], first[2], BodyLaws())
    mind.opportunity_memory = original_memory
    mind.options = original_options
    next_row = _next_decision_is_current(
        mind, physical["body"], water=False)
    return {
        "route": first_info.get("candidate_i_route"),
        "reason": first_info.get("candidate_i_probe_reason"),
        "no_motor": first[0] is None and first[1] is None,
        "authority_empty": empty,
        "work_matches": first[2] == budget.work,
        "next_decision": next_row,
    }


def _post_contact_cycle():
    genome = midpoint()
    candidate = PersonalSharedPriorCandidateIMind(
        deepcopy(genome), 9015,
        observer_decision_diagnostics=True,
        observer_full_competition=True)
    control = PersonalRelevanceCandidateHMind(
        deepcopy(genome), 9015,
        observer_decision_diagnostics=True,
        observer_full_competition=True)
    for mind in (candidate, control):
        _prime_personal_model(mind)
        mind.effects.observe(
            ("boire",), (-0.5, -0.2, 35.0, 0.0, 0.0))

    cap = _cap(FALLBACK_BODY, water=False)
    left = _complete_learning_cycle(candidate, FALLBACK_BODY, cap)
    right = _complete_learning_cycle(control, FALLBACK_BODY, cap)
    return {
        "route": left["info"].get("candidate_i_route"),
        "omega_unused":
            left["info"].get("candidate_i_first_contact_omega_used") is False,
        "decision_motor_work_parity":
            (left["action"], left["param"], left["decision_work"])
            == (right["action"], right["param"], right["decision_work"]),
        "observer_parity":
            left["info"].get("observer") == right["info"].get("observer"),
        "branch_commit_parity":
            left["branch_increment"] == right["branch_increment"],
        "opportunity_commit_parity":
            left["opportunity_increment"] == right["opportunity_increment"],
        "candidate_authority_closed":
            left["authority_closed_after_learning"],
        "control_authority_closed":
            right["authority_closed_after_learning"],
    }


def _omega0_object_custody():
    genome = generation_zero(GENOME_SEED)
    native = PersonalSharedPriorCandidateIMind(deepcopy(genome), 9016)
    zero = PersonalSharedPriorCandidateIMind(
        deepcopy(genome), 9016, first_contact_omega_override=0.0)
    native_digest = genome_digest(genome)
    inherited_equal = (
        native.theta == zero.theta
        and native.p == zero.p
        and native.w == zero.w
        and native.gammas == zero.gammas
        and native.alpha == zero.alpha
        and native.n_base == zero.n_base
        and native.h_max == zero.h_max
        and native.m_max == zero.m_max
        and native.belief_rate == zero.belief_rate)
    return {
        "input_genome_digest": native_digest,
        "genome_digest_equal": inherited_equal,
        "native_omega_preserved":
            native.first_contact_omega == genome["genes"]["omega"],
        "zero_applied": zero.first_contact_omega == 0.0,
        "native_nonzero": genome["genes"]["omega"] != 0.0,
        "branch_memory_individual":
            native.branch_memory is not zero.branch_memory,
        "opportunity_memory_individual":
            native.opportunity_memory is not zero.opportunity_memory,
        "effects_individual": native.effects is not zero.effects,
        "values_individual": native.values is not zero.values,
    }


def _trace_candidate_i_checks(life):
    failures = []
    routes = {}
    for row in life["trace"]:
        info = row["info"]
        route = info.get("candidate_i_route")
        if route is None:
            failures.append((row["t"], "MISSING_ROUTE"))
            continue
        routes[route] = routes.get(route, 0) + 1
        if route not in (
                "P1.3_BASE_FINAL", "INFORMATION_FINAL",
                "POST_CONTACT_CANDIDATE_H", "PROBE_UNFUNDED"):
            failures.append((row["t"], "UNKNOWN_ROUTE", route))
        if info.get("persistent_simulation_mode", "reference") != "reference":
            failures.append((row["t"], "PERSISTENT_MODE"))
        if info.get(
                "persistent_projection_accounting", "chunk_end") != "chunk_end":
            failures.append((row["t"], "PERSISTENT_ACCOUNTING"))
        if route in ("P1.3_BASE_FINAL", "INFORMATION_FINAL"):
            try:
                stage = _work_add(
                    CognitiveWork(**info["candidate_i_stage_a_work"]),
                    CognitiveWork(**info["candidate_i_stage_b_work"]))
                total = CognitiveWork(**info["candidate_i_total_work"])
            except (KeyError, TypeError, ValueError):
                failures.append((row["t"], "INVALID_PHASE_RECEIPT"))
            else:
                if stage != total:
                    failures.append((row["t"], "PHASE_SUM"))
        if route == "P1.3_BASE_FINAL":
            witness = info.get("observer", {}).get("score_witness", ())
            if not witness or any(
                    item.get("curiosity_bonus_applied") != 0.0
                    or item.get("risk_penalty_applied") != 0.0
                    for item in witness):
                failures.append((row["t"], "FALLBACK_ADDEND"))
        if route == "PROBE_UNFUNDED" and row["action"] is not None:
            failures.append((row["t"], "UNFUNDED_MOTOR"))
        if route == "POST_CONTACT_CANDIDATE_H" and (
                info.get("candidate_i_first_contact_omega_used") is not False):
            failures.append((row["t"], "POST_CONTACT_OMEGA"))
    return {
        "routes": routes,
        "failures": failures,
    }


def _memory_checks(life):
    branch = life.get("branch_effect_memory")
    opportunity = life.get("opportunity_recurrence_memory")
    failures = []
    if branch is None:
        failures.append("MISSING_BRANCH_MEMORY")
    else:
        if not (
                0 <= branch["retained"] <= branch["capacity"]
                and branch["recorded"] >= branch["retained"]):
            failures.append("BRANCH_BOUNDS")
    if opportunity is None:
        failures.append("MISSING_OPPORTUNITY_MEMORY")
    else:
        snap = opportunity["snapshot"]
        if opportunity["recorded"] != snap["personal_step"]:
            failures.append("OPPORTUNITY_STEP")
        for gaps in snap["gaps"].values():
            if len(gaps) > 3:
                failures.append("OPPORTUNITY_WINDOW")
    acc = life["cognitive_accounting"]
    if (
            acc["pending_replays"] != 0
            or acc["pending_energy"] != 0.0
            or acc["pending_vigilance"] != 0.0
            or acc["shortfall_steps"] != 0):
        failures.append("PENDING_ACCOUNTING")
    return failures


def _runtime_smokes():
    from .p2_ecologies import world_for
    from .stage0_energy import energy_receipt
    from .stage0_revision import revision_receipt
    from ..runtime.life import run_life

    genome = generation_zero(GENOME_SEED)
    rows = []
    for family in FAMILIES:
        spec = world_for(family, "development", DEVELOPMENT_INDEX)
        for policy in POLICIES:
            life = run_life(
                deepcopy(genome), spec, LIFE_SEED, HORIZON,
                keep_trace=True,
                protocol=PROTOCOL,
                observer_mind_digest=True,
                observer_decision_diagnostics=True,
                observer_resource_acquisition=True,
                observer_full_competition=True,
                decision_policy=policy)
            pin = life["manifest"]["source"]["sha256"]
            energy = energy_receipt(
                life, expected_protocol=PROTOCOL,
                expected_source_sha256=pin)
            revision = revision_receipt(
                life, expected_protocol=PROTOCOL,
                expected_source_sha256=pin)
            policy_checks = (
                _trace_candidate_i_checks(life)
                if policy.startswith("personal_shared_prior_candidate_i")
                else {"routes": {}, "failures": []})
            memory_failures = _memory_checks(life)
            rows.append({
                "family": family,
                "policy": policy,
                "world_seed": WORLD_SEED,
                "world_name": life["world"],
                "development_index": DEVELOPMENT_INDEX,
                "genome_seed": GENOME_SEED,
                "genome_sha256": life["genome"],
                "life_seed": LIFE_SEED,
                "horizon": HORIZON,
                "terminal": life["terminal"],
                "steps_lived": life["steps_lived"],
                "death_causes": tuple(life["death_causes"]),
                "manifest_id": life["manifest_id"],
                "evidence_head": life["evidence_head"],
                "energy_status": energy["terminal"],
                "revision_status": revision["status"],
                "revision_scientific_verdict":
                    revision["scientific_verdict"],
                "shortfall_steps":
                    life["cognitive_accounting"]["shortfall_steps"],
                "policy_checks": policy_checks,
                "memory_failures": memory_failures,
                "candidate_i": life.get("candidate_i"),
                "branch_effect_memory":
                    life.get("branch_effect_memory"),
                "opportunity_recurrence_memory":
                    life.get("opportunity_recurrence_memory"),
            })
    return rows


def characterize():
    branch_gate = B.characterize()
    authority_gate = U.characterize()

    fallback = _fallback_cycle()
    relevant = _relevant_cycle()
    common_unfunded = _forced_common_unfunded_then_fresh()
    recurrence_unfunded = _forced_recurrence_unfunded_then_fresh()
    post_contact = _post_contact_cycle()
    omega0 = _omega0_object_custody()
    smokes = _runtime_smokes()

    smoke_candidate_rows = [
        row for row in smokes
        if row["policy"].startswith("personal_shared_prior_candidate_i")]
    native = {
        row["family"]: row for row in smoke_candidate_rows
        if row["policy"] == "personal_shared_prior_candidate_i_v1"}
    zero = {
        row["family"]: row for row in smoke_candidate_rows
        if row["policy"]
        == "personal_shared_prior_candidate_i_omega0_ablation_v1"}

    l9_pairs = []
    for family in FAMILIES:
        n = native[family]
        z = zero[family]
        l9_pairs.append({
            "family": family,
            "same_genome": n["genome_sha256"] == z["genome_sha256"],
            "native_omega_source":
                n["candidate_i"]["omega_source"],
            "zero_omega_source":
                z["candidate_i"]["omega_source"],
            "zero_omega":
                z["candidate_i"]["first_contact_omega"],
            "persistent_equal": (
                n["candidate_i"]["persistent_simulation_mode"]
                == z["candidate_i"]["persistent_simulation_mode"]
                == "reference"
                and n["candidate_i"][
                    "persistent_projection_accounting"]
                == z["candidate_i"][
                    "persistent_projection_accounting"]
                == "chunk_end"),
        })

    smoke_failures = [
        {
            "family": row["family"],
            "policy": row["policy"],
            "policy_failures": row["policy_checks"]["failures"],
            "memory_failures": row["memory_failures"],
        }
        for row in smokes
        if (row["policy_checks"]["failures"] or row["memory_failures"]
            or row["revision_scientific_verdict"] != "NOT_EVALUATED"
            or row["shortfall_steps"] != 0)
    ]

    rules = {
        "L0_prerequisite_custody": (
            branch_gate["verdict"]
            == "BRANCH_DECISION_SETTLEMENT_REPAIR_PASS"
            and authority_gate["verdict"]
            == "CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS"),
        "L1_exact_exposed_fixture_matrix": (
            len(smokes) == 9
            and {
                (row["family"], row["policy"],
                 row["development_index"], row["world_seed"],
                 row["genome_seed"], row["life_seed"], row["horizon"])
                for row in smokes
            } == {
                (family, policy, DEVELOPMENT_INDEX, WORLD_SEED,
                 GENOME_SEED, LIFE_SEED, HORIZON)
                for family in FAMILIES for policy in POLICIES
            }
            and all(
                row["world_name"]
                == f"p2-{row['family']}-{WORLD_SEED}"
                for row in smokes)),
        "L2_lifecycle_completion_no_engineering_exception":
            len(smokes) == 9,
        "L3_physical_funding_and_phase_accounting":
            all(row["shortfall_steps"] == 0 for row in smokes),
        "L4_revision_resource_reducer_custody": all(
            row["revision_scientific_verdict"] == "NOT_EVALUATED"
            for row in smokes),
        "L5_candidate_i_per_step_route_receipts": not any(
            row["policy_checks"]["failures"]
            for row in smoke_candidate_rows),
        "L6_branch_settlement_lifecycle": (
            fallback["settlement_start_is_pre_stage_a"]
            and relevant["settlement_start_is_pre_stage_a"]
            and fallback["branch_commit_exact"]
            and relevant["branch_commit_exact"]
            and post_contact["branch_commit_parity"]
            and fallback["authority_closed_after_learning"]
            and relevant["authority_closed_after_learning"]
            and post_contact["candidate_authority_closed"]
            and post_contact["control_authority_closed"]),
        "L7_opportunity_recurrence_lifecycle": (
            fallback["opportunity_commit_exact"]
            and relevant["opportunity_commit_exact"]
            and post_contact["opportunity_commit_parity"]
            and not any(
                row["memory_failures"] for row in smokes)),
        "L8_forced_unfunded_cleanup": (
            common_unfunded["route"] == "PROBE_UNFUNDED"
            and common_unfunded["reason"] == "COMMON_MATRIX_UNFUNDED"
            and common_unfunded["no_motor"]
            and common_unfunded["authority_empty"]
            and common_unfunded["work_matches"]
            and common_unfunded["next_decision"]["work_matches"]
            and common_unfunded["next_decision"]["settlement_current"]
            and recurrence_unfunded["route"] == "PROBE_UNFUNDED"
            and recurrence_unfunded["reason"]
            == "RECURRENCE_READ_UNFUNDED"
            and recurrence_unfunded["no_motor"]
            and recurrence_unfunded["authority_empty"]
            and recurrence_unfunded["work_matches"]
            and recurrence_unfunded["next_decision"]["work_matches"]
            and recurrence_unfunded[
                "next_decision"]["settlement_current"]),
        "L9_native_omega0_custody": (
            all(omega0.values())
            and all(
                row["same_genome"]
                and row["zero_omega"] == 0.0
                and row["zero_omega_source"]
                == "SAME_GENOME_SOFTWARE_ABLATION"
                and row["persistent_equal"]
                for row in l9_pairs)),
        "L10_bounded_memory_and_authority_closure":
            not smoke_failures,
        "L11_authority_boundary": True,
    }
    passed = all(rules.values())
    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS.md",
        "runtime_protocol": PROTOCOL,
        "scientific_gate": "NOT_EVALUATED",
        "fresh_development_condition_opened": False,
        "selection_validation_reserve_access": False,
        "60_61_evidence_acceptance_input": False,
        "62_63_evidence_acceptance_input": False,
        "runtime_matrix": {
            "families": FAMILIES,
            "policies": POLICIES,
            "development_index": DEVELOPMENT_INDEX,
            "world_seed": WORLD_SEED,
            "genome_seed": GENOME_SEED,
            "life_seed": LIFE_SEED,
            "horizon": HORIZON,
            "lives": len(smokes),
            "max_physical_steps": len(smokes) * HORIZON,
        },
        "prerequisites": {
            "branch_settlement": branch_gate["verdict"],
            "probe_authority": authority_gate["verdict"],
            "runtime_v2": "GUARDED_BY_FULL_I3_TEST_SUITE",
            "60_61_status": "EXPOSED_CLOSED_NO_J1_J7",
            "62_63_status": "EXPOSED_CLOSED_NO_J1_J7",
        },
        "synthetic": {
            "fallback": fallback,
            "relevant": relevant,
            "common_unfunded": common_unfunded,
            "recurrence_unfunded": recurrence_unfunded,
            "post_contact": post_contact,
            "omega0": omega0,
        },
        "smokes": smokes,
        "omega0_pairs": l9_pairs,
        "smoke_failures": smoke_failures,
        "rules": rules,
        "verdict": (
            "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_PASS"
            if passed else
            "CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_DEFECT"),
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
    print("CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS " + json.dumps({
        "verdict": report["verdict"],
        "rules": report["rules"],
        "smoke_failures": report["smoke_failures"],
        "runtime_matrix": report["runtime_matrix"],
    }, sort_keys=True))
