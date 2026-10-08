"""Stage-6 simulated option evidence.

This module replaces Stage 4's substitution evidence with E_a^sim while learned
Q remains unavailable and intrinsic motivation remains non-applicable.

Spec: 7.1, 8.5, 12.4, DC-01, 20.3 Stage 6.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import tanh

from i0.contracts import EvaluationOption, OptionProposal
from i0.equipment import SimulationState

from .competition import OptionEvidenceInput
from .simulator import Simulator
from .value_needs import ValueNeedsConfig


@dataclass(frozen=True, slots=True)
class Stage6EvaluationConfig:
    version: str
    evidence_scale: float
    beta: float
    r_eff: int
    h_eff: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage-6 evaluation config version must not be empty")
        if self.evidence_scale <= 0:
            raise ValueError("E_ech must be > 0")
        if not 0.0 < self.beta < 1.0:
            raise ValueError("beta must lie in ]0,1[")
        if self.r_eff < 1 or self.h_eff < 1:
            raise ValueError("effective simulation budgets must be >= 1")


@dataclass(frozen=True, slots=True)
class PlanRevisionComparison:
    status: str  # improved | not_improved | unavailable
    old_value: float | None
    new_value: float | None
    delta: float | None
    required_delta: float
    r_eff: int
    h_eff: int


class Stage6OptionEvaluator:
    def __init__(
        self,
        *,
        config: Stage6EvaluationConfig,
        simulator: Simulator,
        needs_config: ValueNeedsConfig,
    ) -> None:
        config.validate()
        needs_config.validate()
        self._config = config
        self._simulator = simulator
        self._needs = needs_config

    @property
    def config(self) -> Stage6EvaluationConfig:
        return self._config

    def _deviation(self, body) -> float:
        return sum(
            self._needs.weights[name]
            * abs(float(body[name]) - self._needs.setpoints[name])
            for name in ("energy", "food", "water", "integrity")
        )

    def evaluate(
        self,
        *,
        proposal: OptionProposal,
        initial_state: SimulationState,
        cycle: int,
        t_monde: int,
    ) -> OptionEvidenceInput:
        proposal.validate()
        if proposal.plan is None or not proposal.plan.steps:
            raise ValueError("Stage-6 evaluation requires an executable plan")

        commands = tuple(step.command for step in proposal.plan.steps)
        result = self._simulator.rollout(
            initial_state=initial_state,
            commands=commands,
            r_eff=self._config.r_eff,
            h_eff=self._config.h_eff,
        )

        if not result.complete:
            evaluation = EvaluationOption(
                option_ref=proposal.option.id,
                option_version=proposal.option.version,
                cycle=cycle,
                t_monde=t_monde,
                status="not_evaluated",
                learned_value_status="unlearned",
                learned_value=None,
                simulated_value_status="unavailable",
                simulated_value=None,
                intrinsic_status="not_applicable",
                intrinsic_value=None,
                risk_status="unknown",
                risk=None,
                safety_uncertainty=0.0,
                protection=False,
                signal_ids=(),
                producers=(
                    f"equipment:{result.equipment_version}",
                    "stage6_simulator",
                ),
            )
            return OptionEvidenceInput(
                evaluation=evaluation,
                evidence=None,
            )

        if not result.completed_rollouts:
            raise RuntimeError("complete simulation has no rollout")

        # Deterministic equipment computes one unique rollout even when R_eff
        # announces several identical rollouts. Its value is therefore also the
        # average over the deduplicated identical set.
        rollout = result.completed_rollouts[0]
        previous_body = initial_state.body
        simulated_value = 0.0
        for k, prediction in enumerate(rollout.predictions):
            next_body = prediction.next_state.body
            reward = self._deviation(previous_body) - self._deviation(next_body)
            simulated_value += (self._config.beta ** k) * reward
            previous_body = next_body

        evidence = tanh(simulated_value / self._config.evidence_scale)
        evaluation = EvaluationOption(
            option_ref=proposal.option.id,
            option_version=proposal.option.version,
            cycle=cycle,
            t_monde=t_monde,
            status="evaluated",
            learned_value_status="unlearned",
            learned_value=None,
            simulated_value_status="computed",
            simulated_value=simulated_value,
            intrinsic_status="not_applicable",
            intrinsic_value=None,
            risk_status="unknown",
            risk=None,
            safety_uncertainty=0.0,
            protection=False,
            signal_ids=(),
            producers=(
                f"equipment:{result.equipment_version}",
                "stage6_simulator",
                "value_needs",
            ),
        )
        return OptionEvidenceInput(
            evaluation=evaluation,
            evidence=evidence,
        )

    def compare_revised_plans(
        self,
        *,
        old_proposal: OptionProposal,
        new_proposal: OptionProposal,
        initial_state: SimulationState,
        delta_plan: float,
        cycle: int,
        t_monde: int,
    ) -> PlanRevisionComparison:
        if delta_plan < 0.0:
            raise ValueError("Delta_plan must be non-negative")

        old = self.evaluate(
            proposal=old_proposal,
            initial_state=initial_state,
            cycle=cycle,
            t_monde=t_monde,
        ).evaluation
        new = self.evaluate(
            proposal=new_proposal,
            initial_state=initial_state,
            cycle=cycle,
            t_monde=t_monde,
        ).evaluation

        if (
            old.simulated_value_status != "computed"
            or new.simulated_value_status != "computed"
            or old.simulated_value is None
            or new.simulated_value is None
        ):
            return PlanRevisionComparison(
                status="unavailable",
                old_value=old.simulated_value,
                new_value=new.simulated_value,
                delta=None,
                required_delta=delta_plan,
                r_eff=self._config.r_eff,
                h_eff=self._config.h_eff,
            )

        delta = new.simulated_value - old.simulated_value
        return PlanRevisionComparison(
            status="improved" if delta >= delta_plan else "not_improved",
            old_value=old.simulated_value,
            new_value=new.simulated_value,
            delta=delta,
            required_delta=delta_plan,
            r_eff=self._config.r_eff,
            h_eff=self._config.h_eff,
        )
