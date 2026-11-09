"""Opt-in genome-v4 omega wiring for the Stage-1 Candidate-F first-contact kernel.

This module is not a runtime policy. It does not override decide(), register an
engine, open World, or add a motor command. It only binds the inherited generic
omega gene to the already-falsified paid first-contact water kernel while
keeping the reference Mind completely omega-blind.
"""
from __future__ import annotations

from i3.modules.body import CognitiveBudget, CognitiveWork
from i3.modules.reference_memory_mind import ReferenceBranchMemoryMind
from i3.modules.water_future_opportunity import paid_water_one_future_opportunity_value

POLICY = "genomic_omega_candidate_f_first_contact_v1"


class GenomicOmegaCandidateFMind(ReferenceBranchMemoryMind):
    """Candidate F plus one inherited first-contact expectation parameter."""

    def __init__(self, genome, life_seed, **kwargs):
        if "simulation_mode" in kwargs:
            raise ValueError("simulation_mode is fixed by genomic omega candidate")
        if (kwargs.get("effect_readout", "full") != "full" or
                kwargs.get("score_addend_mode", "normal") != "normal"):
            raise ValueError(
                "genomic omega candidate rejects historical readout/score ablations")
        super().__init__(
            genome, life_seed, simulation_mode="candidate_f", **kwargs)
        self.projection_accounting = "event_local_quadratic4"
        self.first_contact_omega = genome["genes"]["omega"]

    def paid_water_first_contact(
            self, explore_plan, ordinary_continuations, horizon,
            budget: CognitiveBudget, *,
            forecast_work: CognitiveWork | None = None,
            future_opportunity_probability: float | None = None) -> dict:
        """Run the existing water first-contact kernel with inherited omega.

        The caller cannot override omega. Personal generic effect support comes
        only from this individual's own paid branch memory.
        """
        return paid_water_one_future_opportunity_value(
            self,
            self.branch_memory,
            explore_plan,
            ordinary_continuations,
            horizon,
            budget,
            forecast_work=forecast_work,
            future_opportunity_probability=future_opportunity_probability,
            omega=self.first_contact_omega,
        )


__all__ = ["GenomicOmegaCandidateFMind", "POLICY"]
