"""State custody for a Candidate-F cost-only shadow across real P1.3 history.

Experimental apparatus only. The Candidate-F shadow has no motor authority.
Before each shadow decision its common first-person state is replaced by a deep
copy of the state actually retained by the plain P1.3 controller. Candidate-
specific architecture state, especially omega and paid branch memory, persists.

After the P1.3 action is physically applied, one extra branch-memory record may
be prepaid from the real learning allowance and committed from that actually
lived outcome. The shadow action is never learned.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .body import CognitiveBudget, CognitiveWork
from .personal_outcomes import STORE_WORK

if TYPE_CHECKING:
    from .genomic_omega_frontier_information_mind import (
        GenomicOmegaFrontierInformationMind)
    from .mind import Mind

SCHEMA = "i3-candidate-f-shadow-state-custody/v1"


@dataclass(frozen=True, slots=True)
class PendingActualBranch:
    key: tuple[str, str | None]
    before: tuple[float, ...]
    reference_decision_work: CognitiveWork
    physical_body: tuple[float, ...]
    laws: object


def _validate_types(reference, candidate):
    from .genomic_omega_frontier_information_mind import (
        GenomicOmegaFrontierInformationMind)
    from .mind import Mind

    if type(reference) is not Mind:
        raise ValueError("exact plain P1.3 Mind required")
    if not isinstance(candidate, GenomicOmegaFrontierInformationMind):
        raise ValueError("Candidate-F omega shadow required")
    if reference is candidate:
        raise ValueError("reference and shadow must be distinct minds")
    if reference.simulation_mode != "reference":
        raise ValueError("reference simulation mode drift")
    if reference.projection_accounting != "chunk_end":
        raise ValueError("reference projection accounting drift")
    if candidate.simulation_mode != "candidate_f":
        raise ValueError("candidate simulation mode drift")
    if candidate.projection_accounting != "event_local_quadratic4":
        raise ValueError("candidate projection accounting drift")


def _common_inherited(mind):
    return (
        tuple(mind.theta), tuple(mind.p), tuple(mind.w),
        tuple(mind.gammas), mind.alpha, mind.beta_u, mind.lambda_r,
        mind.kappa0, mind.inertia, mind.n_base, mind.h_max, mind.m_max,
        mind.belief_rate, mind.effect_readout, mind.score_addend_mode,
    )


def synchronize_candidate_shadow(
        reference: "Mind",
        candidate: "GenomicOmegaFrontierInformationMind") -> dict:
    """Deep-copy common lived state into the non-motor Candidate-F shadow.

    This copy is experimental counterfactual bookkeeping, not cognition of the
    control individual. The actual Candidate-F shadow computation remains paid
    by the separate upper-cost decision primitive.
    """
    _validate_types(reference, candidate)
    if _common_inherited(reference) != _common_inherited(candidate):
        raise ValueError("reference/candidate inherited common state mismatch")

    private_memory = candidate.branch_memory
    private_records = candidate.branch_records
    private_omega = candidate.first_contact_omega

    candidate.effects = deepcopy(reference.effects)
    candidate.map = deepcopy(reference.map)
    candidate.hist = deepcopy(reference.hist)
    candidate.visible = deepcopy(reference.visible)
    candidate.pos = tuple(reference.pos)
    candidate.tokens = deepcopy(reference.tokens)
    candidate.external = deepcopy(reference.external)
    candidate.values = deepcopy(reference.values)
    candidate.buffer = deepcopy(reference.buffer)
    candidate.last = deepcopy(reference.last)
    candidate.acc = deepcopy(reference.acc)
    candidate.intention = reference.intention
    candidate.rng.setstate(reference.rng.getstate())
    candidate._budget_rng.setstate(reference._budget_rng.getstate())

    candidate._pending_branch = None
    candidate._branch_decision_work = CognitiveWork()
    candidate._observer_first_forecast = None
    candidate._observer_competition = None

    if candidate.branch_memory is not private_memory:
        raise RuntimeError("candidate private branch memory was replaced")
    if candidate.branch_records != private_records:
        raise RuntimeError("candidate private branch count changed")
    if candidate.first_contact_omega != private_omega:
        raise RuntimeError("candidate omega changed during alignment")

    from .candidate_f_cost_control import _validate_pair
    _validate_pair(reference, candidate)

    return {
        "schema": SCHEMA,
        "status": "COMMON_FIRST_PERSON_STATE_ALIGNED",
        "alignment_scope": "EXPERIMENTAL_SHADOW_BOOKKEEPING_NOT_COGNITION",
        "candidate_branch_records_preserved": private_records,
        "candidate_omega_preserved": private_omega,
        "world_access": False,
        "motor_authority": False,
    }


def prepay_actual_reference_branch(
        reference: "Mind",
        candidate: "GenomicOmegaFrontierInformationMind",
        result: dict,
        reference_decision_work: CognitiveWork,
        learning_budget: CognitiveBudget,
        *,
        reference_learning_funded: bool) -> PendingActualBranch | None:
    """Prepay one shadow-private branch record from the real P1.3 outcome.

    Call only after the ordinary P1.3 learning plan has already consumed its
    work from learning_budget. Storage is additional and cannot steal a
    reference replay. The branch uses the action actually authorized by P1.3,
    never the Candidate-F shadow choice.

    The stored before-body is the body P1.3 actually saw after shadow cognition.
    Therefore only the P1.3 decision bill is removed from the observed delta.
    Candidate shadow cognition happened before this body and is not double
    corrected.
    """
    _validate_types(reference, candidate)
    if type(reference_learning_funded) is not bool:
        raise TypeError("reference_learning_funded must be boolean")
    if not isinstance(reference_decision_work, CognitiveWork):
        raise ValueError("actual P1.3 decision work required")
    if not isinstance(result, dict) or "body" not in result or "dead" not in result:
        raise ValueError("physical outcome result required")
    if not isinstance(learning_budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if tuple(result["body"]) != learning_budget.body:
        raise ValueError("learning allowance must start from post-physics body")
    if result["dead"] or reference.last is None or not reference_learning_funded:
        return None

    before, key, action, _param = reference.last
    if action is None:
        return None
    branch_key = (
        action,
        key[1] if action in ("manger", "collecter") else None,
    )

    if not learning_budget.try_spend(STORE_WORK):
        return None

    return PendingActualBranch(
        branch_key, tuple(before), reference_decision_work,
        tuple(result["body"]), learning_budget.laws)


def commit_actual_reference_branch(
        candidate: "GenomicOmegaFrontierInformationMind",
        pending: PendingActualBranch | None) -> bool:
    """Commit one prepaid actual-action sample to shadow branch memory."""
    from .genomic_omega_frontier_information_mind import (
        GenomicOmegaFrontierInformationMind)
    if not isinstance(candidate, GenomicOmegaFrontierInformationMind):
        raise ValueError("Candidate-F omega shadow required")
    if pending is None:
        return False
    if not isinstance(pending, PendingActualBranch):
        raise ValueError("PendingActualBranch required")

    sub = CognitiveBudget(pending.physical_body, pending.laws)
    candidate.branch_memory.observe(
        pending.key, pending.before, pending.reference_decision_work, sub)
    if sub.work != STORE_WORK:
        raise RuntimeError("candidate branch storage exceeded prepaid block")
    candidate.branch_records += 1
    return True


__all__ = [
    "PendingActualBranch", "SCHEMA", "commit_actual_reference_branch",
    "prepay_actual_reference_branch", "synchronize_candidate_shadow",
]
