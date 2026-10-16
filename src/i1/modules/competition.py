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
from i0.serde import decode_proposal, encode_proposal


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
    evidence: float | None
    crossed: bool


@dataclass(frozen=True, slots=True)
class OptionEvidenceInput:
    evaluation: EvaluationOption
    evidence: float | None

    def validate(self) -> None:
        self.evaluation.validate()
        if self.evaluation.status == "evaluated":
            if self.evidence is None:
                raise ValueError("evaluated option requires evidence")
            if not -1.0 <= self.evidence <= 1.0:
                raise ValueError("option evidence must lie in [-1,1]")
        elif self.evidence is not None:
            raise ValueError("not_evaluated option cannot carry evidence")


@dataclass(frozen=True, slots=True)
class CompetitionCycleResult:
    winner: OptionProposal | None
    crossed_ranked: tuple[OptionProposal, ...]
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

    @property
    def candidate_proposals(self) -> tuple[OptionProposal, ...]:
        return tuple(
            self._registry[option_id].proposal
            for option_id in sorted(
                self._registry,
                key=lambda oid: canonical_option_order(
                    self._registry[oid].proposal.option
                ),
            )
        )

    def _primitive_for(self, proposal: OptionProposal) -> str:
        if proposal.plan is None or not proposal.plan.steps:
            return "attendre"
        return proposal.plan.steps[0].command.primitive

    @staticmethod
    def _plan_semantics(proposal: OptionProposal) -> object:
        plan = proposal.plan
        if plan is None:
            return None
        return (
            tuple(
                (
                    step.command.as_dict(),
                    tuple(step.preconditions),
                    tuple(
                        (
                            consequence.variable,
                            consequence.value_or_delta,
                            consequence.precision,
                        )
                        for consequence in step.predicted_consequences
                    ),
                    step.observation_window_steps,
                )
                for step in plan.steps
            ),
            plan.goal_ref,
        )

    @classmethod
    def material_plan_change(
        cls,
        before: OptionProposal,
        after: OptionProposal,
    ) -> bool:
        return cls._plan_semantics(before) != cls._plan_semantics(after)

    def proposal_for(self, option_ref: str) -> OptionProposal | None:
        state = self._registry.get(option_ref)
        return None if state is None else state.proposal

    def accumulator_for(self, option_ref: str) -> float | None:
        state = self._registry.get(option_ref)
        return None if state is None else state.accumulator

    def is_engaged(self, option_ref: str) -> bool:
        return self._engaged_option_id == option_ref

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
            material_change = self.material_plan_change(
                existing.proposal,
                proposal,
            )
            if material_change and option.id != self._engaged_option_id:
                # DC-17: evidence accumulated for a different realization of
                # a non-engaged option never transfers to the revised plan.
                existing.accumulator = 0.0
                existing.last_threshold = self._config.base_threshold
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
        evidence_inputs: Mapping[str, OptionEvidenceInput] | None = None,
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
            if evidence_inputs is None:
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
            else:
                supplied = evidence_inputs.get(option_id)
                if supplied is None:
                    raise ValueError(
                        f"missing Stage-6 evidence input for option {option_id}"
                    )
                supplied.validate()
                evaluation = supplied.evaluation
                evidence = supplied.evidence

            evaluation.validate()
            evaluations.append(evaluation)

            if evaluation.status == "not_evaluated":
                before = state.accumulator
                traces.append(
                    CompetitionTrace(
                        option_ref=option_id,
                        accumulator_before=before,
                        accumulator_after=before,
                        threshold=state.last_threshold,
                        evidence=None,
                        crossed=False,
                    )
                )
                continue

            if evidence is None:
                raise ValueError("evaluated option unexpectedly lacks evidence")

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

        crossed_ranked = tuple(
            state.proposal
            for state in sorted(
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
            )
        )

        return CompetitionCycleResult(
            winner=None if not crossed_ranked else crossed_ranked[0],
            crossed_ranked=crossed_ranked,
            evaluations=tuple(evaluations),
            traces=tuple(traces),
            cycle=cycle,
        )

    def prune_invalid(
        self,
        *,
        active_goal_id: str | None,
        t_monde: int,
    ) -> None:
        for option_id in list(self._registry):
            state = self._registry[option_id]
            option = state.proposal.option
            if option_id == "permanent:attendre":
                continue
            if (
                option.expires_at_step <= t_monde
                or (
                    option.goal_ref is not None
                    and option.goal_ref != active_goal_id
                )
            ):
                self.invalidate_candidate(option_id)

    def invalidate_candidate(self, option_ref: str) -> None:
        self._registry.pop(option_ref, None)
        if self._engaged_option_id == option_ref:
            self._engaged_option_id = None

    def close_deliberation(self, winner: OptionProposal | None) -> None:
        winner_id = None if winner is None else winner.option.id
        for option_id, state in self._registry.items():
            if option_id == winner_id:
                continue
            state.accumulator *= self._config.residual
        if winner_id is not None:
            self._engaged_option_id = winner_id

    def fallback_candidates(self) -> tuple[OptionProposal, ...]:
        candidates: list[OptionProposal] = []
        if self._engaged_option_id is not None:
            engaged = self._registry.get(self._engaged_option_id)
            if engaged is not None:
                candidates.append(engaged.proposal)
        wait = self._registry.get("permanent:attendre")
        if wait is not None and (
            not candidates or candidates[0].option.id != wait.proposal.option.id
        ):
            candidates.append(wait.proposal)
        return tuple(candidates)

    def fallback(self) -> OptionProposal:
        candidates = self.fallback_candidates()
        if not candidates:
            raise RuntimeError("permanent wait option is missing")
        return candidates[0]

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "cycle": self._cycle,
            "engaged_option_id": self._engaged_option_id,
            "registry": [
                {
                    "proposal": encode_proposal(state.proposal),
                    "accumulator": state.accumulator,
                    "last_threshold": state.last_threshold,
                    "last_proposal_t": state.last_proposal_t,
                }
                for _, state in sorted(self._registry.items())
            ],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("Competition state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("Competition config version mismatch")
        cycle = state.get("cycle")
        if not isinstance(cycle, int) or cycle < 0:
            raise ValueError("invalid Competition cycle")
        engaged = state.get("engaged_option_id")
        if engaged is not None and not isinstance(engaged, str):
            raise ValueError("invalid engaged option id")
        raw_registry = state.get("registry")
        if not isinstance(raw_registry, list):
            raise ValueError("invalid Competition registry")
        registry: dict[str, CandidateState] = {}
        for row in raw_registry:
            if not isinstance(row, Mapping):
                raise ValueError("invalid Competition candidate")
            proposal_raw = row.get("proposal")
            if not isinstance(proposal_raw, Mapping):
                raise ValueError("invalid Competition proposal")
            proposal = decode_proposal(proposal_raw)
            registry[proposal.option.id] = CandidateState(
                proposal=proposal,
                accumulator=float(row["accumulator"]),
                last_threshold=float(row["last_threshold"]),
                last_proposal_t=int(row["last_proposal_t"]),
            )
        self._cycle = cycle
        self._engaged_option_id = engaged
        self._registry = registry
