"""Stage-8 evidence combiner: learned Q plus Stage-6 simulation.

Spec: 8.5, 11.1, DC-01, P-13, INV-16.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import tanh

from i0.contracts import EvaluationOption, OptionProposal

from .competition import OptionEvidenceInput
from .stage6_evaluator import Stage6OptionEvaluator
from .td_values import EvaluationState, LinearTDValues


@dataclass(frozen=True, slots=True)
class Stage8EvaluationConfig:
    version: str
    n0: float
    evidence_scale: float
    extrinsic_gain: float = 1.0

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage-8 evaluation version must not be empty")
        if self.n0 <= 0:
            raise ValueError("n0 must be > 0")
        if self.evidence_scale <= 0:
            raise ValueError("evidence scale must be > 0")
        if self.extrinsic_gain <= 0:
            raise ValueError("extrinsic gain must be > 0")


class Stage8OptionEvaluator:
    def __init__(
        self,
        *,
        config: Stage8EvaluationConfig,
        stage6: Stage6OptionEvaluator,
        q_values: LinearTDValues,
    ) -> None:
        config.validate()
        self._config = config
        self._stage6 = stage6
        self._q = q_values

    @property
    def config(self) -> Stage8EvaluationConfig:
        return self._config

    def evaluate(
        self,
        *,
        proposal: OptionProposal,
        evaluation_state: EvaluationState,
        initial_state,
        cycle: int,
        t_monde: int,
    ) -> OptionEvidenceInput:
        simulated = self._stage6.evaluate(
            proposal=proposal,
            initial_state=initial_state,
            cycle=cycle,
            t_monde=t_monde,
        )
        learned = self._q.learned_value(
            evaluation_state,
            proposal.option.learning_signature,
        )

        sim_eval = simulated.evaluation
        sim_available = (
            sim_eval.status == "evaluated"
            and sim_eval.simulated_value_status == "computed"
            and sim_eval.simulated_value is not None
        )
        learned_available = (
            learned.status == "learned"
            and learned.value is not None
        )

        if not sim_available and not learned_available:
            evaluation = EvaluationOption(
                option_ref=proposal.option.id,
                option_version=proposal.option.version,
                cycle=cycle,
                t_monde=t_monde,
                status="not_evaluated",
                learned_value_status="unlearned",
                learned_value=None,
                simulated_value_status=sim_eval.simulated_value_status,
                simulated_value=None,
                intrinsic_status="not_applicable",
                intrinsic_value=None,
                risk_status=sim_eval.risk_status,
                risk=sim_eval.risk,
                safety_uncertainty=sim_eval.safety_uncertainty,
                protection=sim_eval.protection,
                signal_ids=sim_eval.signal_ids,
                producers=sim_eval.producers + ("value_needs.q_active",),
            )
            return OptionEvidenceInput(evaluation=evaluation, evidence=None)

        if learned_available and sim_available:
            weight = learned.update_count / (
                learned.update_count + self._config.n0
            )
            ext = (
                weight * float(learned.value)
                + (1.0 - weight) * float(sim_eval.simulated_value)
            )
        elif learned_available:
            ext = float(learned.value)
        else:
            ext = float(sim_eval.simulated_value)

        evidence = max(
            -1.0,
            min(
                1.0,
                self._config.extrinsic_gain
                * tanh(ext / self._config.evidence_scale),
            ),
        )
        evaluation = EvaluationOption(
            option_ref=proposal.option.id,
            option_version=proposal.option.version,
            cycle=cycle,
            t_monde=t_monde,
            status="evaluated",
            learned_value_status=(
                "learned" if learned_available else "unlearned"
            ),
            learned_value=(
                float(learned.value) if learned_available else None
            ),
            simulated_value_status=sim_eval.simulated_value_status,
            simulated_value=(
                float(sim_eval.simulated_value)
                if sim_available else None
            ),
            intrinsic_status="not_applicable",
            intrinsic_value=None,
            risk_status=sim_eval.risk_status,
            risk=sim_eval.risk,
            safety_uncertainty=sim_eval.safety_uncertainty,
            protection=sim_eval.protection,
            signal_ids=sim_eval.signal_ids,
            producers=tuple(dict.fromkeys(
                sim_eval.producers + ("value_needs.q_active",)
            )),
        )
        evaluation.validate()
        return OptionEvidenceInput(
            evaluation=evaluation,
            evidence=evidence,
        )
