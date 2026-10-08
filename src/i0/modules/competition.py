"""Minimal normative Stage-4 option competition.

Stage 4 uses substitution evidence by primitive action type, no learned Q,
no simulator, no intrinsic motivation, and neutral risk/uncertainty penalties.
All numeric dynamics are explicit injected P-xx configuration.

Spec: 8.3-8.8, DC-01, DC-02, DC-10, 20.4 Stage 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Callable, Mapping, Sequence

from i0.contracts import EvaluationOption, Option, OptionProposal, canonical_option_order


@dataclass(frozen=True, slots=True)
class CompetitionConfig:
    version: str
    c_max: int
    urgency_max: float
    urgency_scale_cycles: float
    leak: float
    noise_sigma: float
    gain: float
    base_threshold: float
    threshold_floor: float
    inertia: float
    residual: float
    options_max: int
    substitution_evidence: Mapping[str, float]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("competition config version must not be empty")
        if self.c_max < 1:
            raise ValueError("C_max must be >= 1")
        if self.urgency_max < 1.0 or self.urgency_scale_cycles <= 0:
            raise ValueError("invalid urgency parameters")
        if not 0.0 <= self.leak < 1.0:
            raise ValueError("leak must lie in [0,1[")
        if self.noise_sigma < 0 or self.gain <= 0:
            raise ValueError("invalid accumulation gain/noise")
        if self.threshold_floor <= 0:
            raise ValueError("s_min must be > 0")
        if self.base_threshold <= self.threshold_floor:
            raise ValueError("s0 must be > s_min")
        if not 0.0 <= self.inertia <= self.base_threshold - self.threshold_floor:
            raise ValueError("invalid inertia")
        if not 0.0 < self.residual < 1.0:
            raise ValueError("rho must lie in ]0,1[")
        if self.options_max < 1:
            raise ValueError("N_options_max must be >= 1")
        for primitive, evidence in self.substitution_evidence.items():
            if not -1.0 <= evidence <= 1.0:
                raise ValueError(
                    f"substitution evidence for {primitive} must be in [-1,1]"
                )


@dataclass(slots=True)
class CandidateState:
    proposal: OptionProposal
    accumulator: float
    last_threshold: float
    last_proposal_t: int


@dataclass(frozen=True, slots=True)
class CompetitionTrace:
    option_ref: str
    accumulator_before: float
    accumulator_after: float
    threshold: float
    evidence: float
    crossed: bool


@dataclass(frozen=True, slots=True)
class CompetitionCycleResult:
    winner: OptionProposal | None
    evaluations: tuple[EvaluationOption, ...]
    traces: tuple[CompetitionTrace, ...]
    cycle: int


class Competition:
    owner_id = "competition"

    def __init__(
        self,
        config: CompetitionConfig,
        *,
        noise_draw: Callable[[str, int], float] | None = None,
    ) -> None:
        config.validate()
        if config.noise_sigma > 0 and noise_draw is None:
            raise ValueError("noise_draw is required when sigma > 0")
        self._config = config
        self._noise_draw = noise_draw
        self._registry: dict[str, CandidateState] = {}
        self._engaged_option_id: str | None = None
        self._cycle = 0

    @property
    def engaged_option_id(self) -> str | None:
        return self._engaged_option_id

    @property
    def registry_size(self) -> int:
        return len(self._registry)

    def _primitive_for(self, proposal: OptionProposal) -> str:
        if proposal.plan is None or not proposal.plan.steps:
            return "attendre"
        return proposal.plan.steps[0].command.primitive

    def register(
        self,
        proposal: OptionProposal,
        *,
        active_goal_id: str | None,
        t_monde: int,
    ) -> bool:
        proposal.validate()
        option = proposal.option
        if option.goal_ref is not None and option.goal_ref != active_goal_id:
            return False
        if option.expires_at_step <= t_monde:
            return False

        existing = self._registry.get(option.id)
        if existing is not None:
            existing.proposal = proposal
            existing.last_proposal_t = t_monde
            return True

        self._registry[option.id] = CandidateState(
            proposal=proposal,
            accumulator=0.0,
            last_threshold=self._config.base_threshold,
            last_proposal_t=t_monde,
        )
        self._enforce_capacity()
        return option.id in self._registry

    def ensure_wait(self, *, t_monde: int, st_version: str) -> None:
        from i0.contracts import MotiveRef, Plan, PlanStep
        from i0.interfaces import PrimitiveCommand

        option_id = "permanent:attendre"
        if option_id in self._registry:
            return
        plan = Plan(
            id="plan:permanent:attendre",
            option_ref=option_id,
            version="1",
            steps=(PlanStep(index=0, command=PrimitiveCommand("attendre")),),
            goal_ref=None,
            budget_used_uc=1,
            status="valid",
            st_version=st_version,
        )
        option = Option(
            id=option_id,
            version="1",
            type="primitive",
            learning_signature="primitive:attendre",
            preconditions=(),
            success_condition="step_completed",
            failure_condition="command_failed",
            invalidation_condition="never",
            motive_ref=MotiveRef(type="default", id="default"),
            founding_st_version=st_version,
            expires_at_step=10**12,
            provenance="default",
            plan_ref=plan.id,
            state="candidate",
        )
        self._registry[option_id] = CandidateState(
            proposal=OptionProposal(option=option, plan=plan),
            accumulator=0.0,
            last_threshold=self._config.base_threshold,
            last_proposal_t=t_monde,
        )

    def _enforce_capacity(self) -> None:
        non_wait = [
            state
            for option_id, state in self._registry.items()
            if option_id != "permanent:attendre"
        ]
        if len(non_wait) <= self._config.options_max:
            return

        protected = self._engaged_option_id
        ranked = sorted(
            non_wait,
            key=lambda state: (
                -(
                    state.accumulator
                    / max(self._config.threshold_floor, state.last_threshold)
                ),
                -state.last_proposal_t,
                canonical_option_order(state.proposal.option),
            ),
        )
        keep_ids = {
            state.proposal.option.id
            for state in ranked[: self._config.options_max]
        }
        if protected is not None and protected in self._registry:
            keep_ids.add(protected)
            if len(keep_ids) > self._config.options_max:
                removable = [
                    state
                    for state in reversed(ranked)
                    if state.proposal.option.id != protected
                    and state.proposal.option.id in keep_ids
                ]
                if removable:
                    keep_ids.remove(removable[0].proposal.option.id)

        for option_id in list(self._registry):
            if option_id == "permanent:attendre":
                continue
            if option_id not in keep_ids:
                self._registry.pop(option_id, None)

    def open_deliberation(
        self,
        *,
        active_goal_id: str | None,
        t_monde: int,
    ) -> None:
        self._cycle = 0
        for option_id in list(self._registry):
            state = self._registry[option_id]
            option = state.proposal.option
            invalid = (
                option.expires_at_step <= t_monde
                or (
                    option.goal_ref is not None
                    and option.goal_ref != active_goal_id
                )
            )
            if invalid:
                self._registry.pop(option_id, None)
                if self._engaged_option_id == option_id:
                    self._engaged_option_id = None
                continue
            if option_id == self._engaged_option_id:
                state.accumulator = 0.0

    def urgency(self, cycle: int) -> float:
        return 1.0 + (self._config.urgency_max - 1.0) * (
            1.0 - exp(-(cycle - 1) / self._config.urgency_scale_cycles)
        )

    def evaluate(
        self,
        *,
        cycle: int,
        t_monde: int,
    ) -> CompetitionCycleResult:
        if cycle < 1:
            raise ValueError("competition cycle must be >= 1")
        self._cycle = cycle

        evaluations: list[EvaluationOption] = []
        traces: list[CompetitionTrace] = []
        crossed: list[CandidateState] = []

        for option_id in sorted(
            self._registry,
            key=lambda oid: canonical_option_order(
                self._registry[oid].proposal.option
            ),
        ):
            state = self._registry[option_id]
            primitive = self._primitive_for(state.proposal)
            evidence = self._config.substitution_evidence.get(primitive, 0.0)

            evaluation = EvaluationOption(
                option_ref=option_id,
                option_version=state.proposal.option.version,
                cycle=cycle,
                t_monde=t_monde,
                status="evaluated",
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
                producers=("stage4_substitution",),
            )
            evaluation.validate()
            evaluations.append(evaluation)

            threshold = max(
                self._config.threshold_floor,
                self._config.base_threshold
                - (
                    self._config.inertia
                    if option_id == self._engaged_option_id
                    else 0.0
                ),
            )
            before = state.accumulator
            noise = (
                0.0
                if self._noise_draw is None
                else self._noise_draw(option_id, cycle)
            )
            after = max(
                0.0,
                (1.0 - self._config.leak) * before
                + self.urgency(cycle) * self._config.gain * evidence
                + self._config.noise_sigma * noise,
            )
            state.accumulator = after
            state.last_threshold = threshold
            did_cross = after >= threshold
            traces.append(
                CompetitionTrace(
                    option_ref=option_id,
                    accumulator_before=before,
                    accumulator_after=after,
                    threshold=threshold,
                    evidence=evidence,
                    crossed=did_cross,
                )
            )
            if did_cross:
                crossed.append(state)

        winner_state: CandidateState | None = None
        if crossed:
            winner_state = sorted(
                crossed,
                key=lambda state: (
                    -(
                        (
                            state.accumulator - state.last_threshold
                        )
                        / state.last_threshold
                    ),
                    canonical_option_order(state.proposal.option),
                ),
            )[0]

        return CompetitionCycleResult(
            winner=None if winner_state is None else winner_state.proposal,
            evaluations=tuple(evaluations),
            traces=tuple(traces),
            cycle=cycle,
        )

    def close_deliberation(self, winner: OptionProposal | None) -> None:
        winner_id = None if winner is None else winner.option.id
        for option_id, state in self._registry.items():
            if option_id == winner_id:
                continue
            state.accumulator *= self._config.residual
        if winner_id is not None:
            self._engaged_option_id = winner_id

    def fallback(self) -> OptionProposal:
        if self._engaged_option_id is not None:
            engaged = self._registry.get(self._engaged_option_id)
            if engaged is not None:
                return engaged.proposal
        wait = self._registry.get("permanent:attendre")
        if wait is None:
            raise RuntimeError("permanent wait option is missing")
        return wait.proposal

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "cycle": self._cycle,
            "engaged_option_id": self._engaged_option_id,
            "registry": [
                {
                    "option_id": option_id,
                    "accumulator": state.accumulator,
                    "last_threshold": state.last_threshold,
                    "last_proposal_t": state.last_proposal_t,
                }
                for option_id, state in sorted(self._registry.items())
            ],
        }
