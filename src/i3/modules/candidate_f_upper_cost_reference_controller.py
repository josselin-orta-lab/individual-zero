"""Multi-step software controller for the Candidate-F upper-cost falsifier.

There are two internal minds but only the plain P1.3 reference has motor
authority and owns the common lived history. Before every decision, the
Candidate-F shadow is realigned to that actual history while preserving only
its candidate-private branch memory and omega state.

This module is not registered in runtime.life and opens no World by itself.
"""
from __future__ import annotations

from .body import CognitiveBudget, CognitiveWork
from .candidate_f_cost_control import (
    SCHEMA as DECISION_SCHEMA,
    paid_candidate_f_shadow_then_reference_choice)
from .candidate_f_shadow_state import (
    SCHEMA as STATE_SCHEMA,
    commit_actual_reference_branch,
    prepay_actual_reference_branch,
    synchronize_candidate_shadow)

POLICY = "candidate_f_shadow_upper_cost_reference_controller_v1"


class CandidateFUpperCostReferenceController:
    """Candidate-F cognition cost with P1.3 motor choice and lived history."""

    def __init__(self, genome, life_seed, **kwargs):
        from .genomic_omega_frontier_information_mind import (
            GenomicOmegaFrontierInformationMind)
        from .mind import Mind

        self.reference = Mind(genome, life_seed, **kwargs)
        self.shadow = GenomicOmegaFrontierInformationMind(
            genome, life_seed, **kwargs)
        self._pending_shadow_branch = None
        self._last_reference_decision_work = CognitiveWork()
        self._last_total_decision_work = CognitiveWork()
        self._last_alignment = None
        self.decisions = 0
        self.shadow_branch_commits = 0

    def __getattr__(self, name):
        # Runtime observers/readers see the actual actor's first-person state.
        return getattr(self.reference, name)

    @property
    def branch_memory(self):
        return self.shadow.branch_memory

    @property
    def branch_records(self):
        return self.shadow.branch_records

    @property
    def first_contact_omega(self):
        return self.shadow.first_contact_omega

    def decide(self, capture, budget: CognitiveBudget):
        self._pending_shadow_branch = None
        alignment = synchronize_candidate_shadow(
            self.reference, self.shadow)
        action, param, work, info = (
            paid_candidate_f_shadow_then_reference_choice(
                self.reference, self.shadow, capture, budget))

        control = info["cost_control"]
        self._last_reference_decision_work = CognitiveWork(
            **control["reference_choice_work"])
        self._last_total_decision_work = work
        self._last_alignment = alignment
        self.decisions += 1

        info["experimental_policy"] = POLICY
        control["decision_primitive_schema"] = DECISION_SCHEMA
        control["state_custody_schema"] = STATE_SCHEMA
        control["alignment"] = dict(alignment)
        control["controller_decision_index"] = self.decisions
        return action, param, work, info

    def observe_outcome(self, result):
        """Only the real P1.3 actor receives the paid orientation update."""
        return self.reference.observe_outcome(result)

    def prepare_learning(self, result, budget: CognitiveBudget):
        """Buy normal P1.3 learning, then optional shadow-private storage."""
        self._pending_shadow_branch = None
        replay_limit = self.reference.prepare_learning(result, budget)
        self._pending_shadow_branch = prepay_actual_reference_branch(
            self.reference, self.shadow, result,
            self._last_reference_decision_work, budget,
            reference_learning_funded=(replay_limit is not None))
        return replay_limit

    def learn_from_outcome(
            self, result, *, replay_limit=0, replay_retention=True):
        """Commit P1.3 learning, then the already-prepaid actual-action sample."""
        pending, self._pending_shadow_branch = (
            self._pending_shadow_branch, None)
        replays = self.reference.learn_from_outcome(
            result, replay_limit=replay_limit,
            replay_retention=replay_retention)
        if commit_actual_reference_branch(self.shadow, pending):
            self.shadow_branch_commits += 1
        return replays

    def custody_summary(self) -> dict:
        return {
            "schema": POLICY,
            "motor_authority": "P1.3_REFERENCE_ONLY",
            "decision_cost": (
                "CANDIDATE_F_SHADOW_PLUS_P1.3_REFERENCE"),
            "learning_cost": (
                "P1.3_REFERENCE_PLUS_CANDIDATE_PRIVATE_STORE_IF_FUNDED"),
            "decisions": self.decisions,
            "shadow_branch_commits": self.shadow_branch_commits,
            "shadow_branch_retained": len(self.shadow.branch_memory._samples),
            "shadow_first_contact_omega": self.shadow.first_contact_omega,
            "last_total_decision_work": {
                "cycles": self._last_total_decision_work.cycles,
                "simulated_steps": self._last_total_decision_work.simulated_steps,
                "memory_items": self._last_total_decision_work.memory_items,
                "replays": self._last_total_decision_work.replays,
            },
            "world_access": False,
            "runtime_registered": False,
        }


__all__ = ["CandidateFUpperCostReferenceController", "POLICY"]
