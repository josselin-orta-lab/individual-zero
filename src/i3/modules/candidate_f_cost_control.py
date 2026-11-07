"""Paid Candidate-F shadow cognition followed by a P1.3 reference choice.

Software falsifier only. This is deliberately an upper-cost control, not an
exact cost-matched arm: it pays a complete Candidate-F decision computation and
then also pays the ordinary P1.3 decision from the resulting bodily state.

Only the P1.3 action has motor authority.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from .body import CognitiveBudget, CognitiveWork, VITAL

if TYPE_CHECKING:
    from .genomic_omega_frontier_information_mind import (
        GenomicOmegaFrontierInformationMind)
    from .mind import Mind

SCHEMA = "i3-candidate-f-shadow-cost-reference-choice/v1"


def _common_inherited_state(mind):
    return (
        tuple(mind.theta), tuple(mind.p), tuple(mind.w),
        tuple(mind.gammas), mind.alpha, mind.beta_u, mind.lambda_r,
        mind.kappa0, mind.inertia, mind.n_base, mind.h_max, mind.m_max,
        mind.belief_rate,
    )


def _common_first_person_state(mind):
    return (
        mind.effects.stats,
        mind.map,
        mind.hist,
        mind.visible,
        mind.pos,
        mind.tokens,
        mind.external,
        mind.values,
        tuple(mind.buffer),
        mind.last,
    )


def _validate_pair(reference, candidate):
    # Keep this utility import-detached from World/runtime until actually used.
    # Mind itself imports DIRECTIONS from modules.world, so top-level imports
    # here would make a pure software-control module look World-coupled.
    from .genomic_omega_frontier_information_mind import (
        GenomicOmegaFrontierInformationMind)
    from .mind import Mind

    if type(reference) is not Mind:
        raise ValueError("exact plain P1.3 Mind required for reference choice")
    if not isinstance(candidate, GenomicOmegaFrontierInformationMind):
        raise ValueError("GenomicOmegaFrontierInformationMind shadow required")
    if reference is candidate:
        raise ValueError("reference and candidate shadow must be distinct minds")
    if reference.simulation_mode != "reference":
        raise ValueError("reference simulation mode drift")
    if reference.projection_accounting != "chunk_end":
        raise ValueError("reference projection accounting drift")
    if candidate.simulation_mode != "candidate_f":
        raise ValueError("candidate simulation mode drift")
    if candidate.projection_accounting != "event_local_quadratic4":
        raise ValueError("candidate projection accounting drift")
    if _common_inherited_state(reference) != _common_inherited_state(candidate):
        raise ValueError("reference/candidate inherited common state mismatch")
    if _common_first_person_state(reference) != _common_first_person_state(candidate):
        raise ValueError("reference/candidate learned first-person state mismatch")
    if reference.rng.getstate() != candidate.rng.getstate():
        raise ValueError("reference/candidate perception RNG state mismatch")
    if reference._budget_rng.getstate() != candidate._budget_rng.getstate():
        raise ValueError("reference/candidate budget-order RNG state mismatch")
    if reference.acc != candidate.acc or reference.intention != candidate.intention:
        raise ValueError("reference/candidate control state mismatch")


def paid_candidate_f_shadow_then_reference_choice(
        reference: "Mind",
        candidate: "GenomicOmegaFrontierInformationMind",
        capture: dict,
        budget: CognitiveBudget) -> tuple:
    """Pay Candidate-F cognition first, then let plain P1.3 choose.

    The candidate shadow receives the original first-person capture and has no
    motor authority. Its actually consumed work is immediately settled against
    the cumulative budget.

    The plain P1.3 mind then receives the same non-body capture fields but the
    post-shadow bodily state. Its decision is actually executed and paid.

    This control is intentionally conservative: total work is shadow candidate
    work plus reference decision work. It can falsify "cost alone is sufficient"
    if a later integrated arm survives despite this over-cost, but a collapse
    would not by itself quantify cost mediation.
    """
    if not isinstance(capture, dict) or "body" not in capture:
        raise ValueError("first-person capture with body required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if budget.work != CognitiveWork():
        raise ValueError("fresh cumulative decision allowance required")
    if tuple(capture["body"]) != budget.body:
        raise ValueError("capture body must match cumulative allowance")
    if any(budget.body[k] <= 0.0 for k in VITAL):
        raise ValueError("no decision computation after physical death")
    _validate_pair(reference, candidate)

    initial_body = tuple(budget.body)

    candidate_budget = CognitiveBudget(initial_body, budget.laws)
    candidate_action, candidate_param, candidate_work, candidate_info = (
        candidate.decide(capture, candidate_budget))
    if candidate_work != candidate_budget.work:
        raise RuntimeError("candidate shadow declared work mismatch")
    budget.spend(candidate_work)
    body_after_shadow = tuple(budget.remaining)

    reference_capture = dict(capture)
    reference_capture["body"] = body_after_shadow
    reference_budget = CognitiveBudget(body_after_shadow, budget.laws)
    action, param, reference_work, info = reference.decide(
        reference_capture, reference_budget)
    if reference_work != reference_budget.work:
        raise RuntimeError("reference declared work mismatch")
    budget.spend(reference_work)

    # CognitiveBudget's canonical v2 settlement recomputes the cumulative bill
    # from the phase-start body. The detached reference allowance subtracts the
    # same linear bill from the already debited post-shadow body. These are
    # mathematically identical but may differ by floating-point association.
    sequential_body = tuple(reference_budget.remaining)
    settlement_gap = max(
        abs(a - b) for a, b in zip(budget.remaining, sequential_body))
    if settlement_gap > 1e-12:
        raise RuntimeError("sequential cognition settlement body mismatch")

    out = dict(info)
    out["experimental_policy"] = SCHEMA
    out["cost_control"] = {
        "schema": SCHEMA,
        "scope": "SOFTWARE_ONE_DECISION_UPPER_COST_NOT_RUNTIME",
        "motor_authority": "P1.3_REFERENCE_ONLY",
        "candidate_shadow_action": candidate_action,
        "candidate_shadow_param": candidate_param,
        "candidate_shadow_option": candidate_info.get("option"),
        "candidate_shadow_funding": candidate_info.get("funding"),
        "candidate_shadow_work": asdict(candidate_work),
        "reference_choice_work": asdict(reference_work),
        "total_work": asdict(budget.work),
        "body_before": initial_body,
        "body_after_candidate_shadow": body_after_shadow,
        "body_after_reference_choice": tuple(budget.remaining),
        "sequential_reference_body": sequential_body,
        "sequential_settlement_max_abs_gap": settlement_gap,
        "settlement_authority": "CUMULATIVE_V2_PHASE_START_BODY",
        "cost_matching_claim": "UPPER_COST_NOT_EXACT_MATCH",
        "world_access": False,
        "candidate_motor_authority": False,
    }
    return action, param, budget.work, out


__all__ = [
    "SCHEMA", "paid_candidate_f_shadow_then_reference_choice",
]
