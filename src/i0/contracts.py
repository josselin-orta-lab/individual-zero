"""Normative cognitive contracts introduced by MVP Stage 4.

These are causal data structures only. They deliberately contain no policy
logic and no Lab/runtime dependency.

Spec: 4.3, 5.2, 6.2, 7.4, 8.1-8.5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from i0.interfaces import PrimitiveCommand


@dataclass(frozen=True, slots=True)
class MotiveRef:
    type: str
    id: str


@dataclass(frozen=True, slots=True)
class GoalProposal:
    id: str
    source: str
    goal_type: str
    target: str
    base_pressure: float
    current_pressure: float
    justification_ref: str
    t_monde: int
    cycle: int
    rule_version: str

    def validate(self) -> None:
        if self.source not in {"value_needs", "prospective_memory"}:
            raise ValueError("invalid goal proposal source")
        if not 0.0 <= self.base_pressure <= 1.0:
            raise ValueError("base pressure must be in [0,1]")
        if not 0.0 <= self.current_pressure <= 1.0:
            raise ValueError("current pressure must be in [0,1]")


@dataclass(frozen=True, slots=True)
class Goal:
    id: str
    goal_type: str
    target: str
    satisfaction_condition: str
    principal_measure: str
    current_pressure: float
    state: str
    activation_t: int
    activation_cycle: int

    def validate(self) -> None:
        if self.state not in {
            "active",
            "satisfied",
            "replaced",
            "abandoned",
            "invalid",
        }:
            raise ValueError("invalid goal state")
        if not 0.0 <= self.current_pressure <= 1.0:
            raise ValueError("goal pressure must be in [0,1]")


@dataclass(frozen=True, slots=True)
class PredictedConsequence:
    variable: str
    value_or_delta: float
    precision: float


@dataclass(frozen=True, slots=True)
class PlanStep:
    index: int
    command: PrimitiveCommand
    preconditions: tuple[str, ...] = ()
    predicted_consequences: tuple[PredictedConsequence, ...] = ()
    observation_window_steps: int = 1

    def validate(self) -> None:
        if self.index < 0:
            raise ValueError("plan-step index must be non-negative")
        if self.observation_window_steps < 1:
            raise ValueError("observation window must be >= 1")


@dataclass(frozen=True, slots=True)
class Plan:
    id: str
    option_ref: str
    version: str
    steps: tuple[PlanStep, ...]
    goal_ref: str | None
    budget_used_uc: int
    status: str
    st_version: str

    def validate(self) -> None:
        if self.status not in {"valid", "to_revise", "abandoned"}:
            raise ValueError("invalid plan status")
        for step in self.steps:
            step.validate()


@dataclass(frozen=True, slots=True)
class Option:
    id: str
    version: str
    type: str
    learning_signature: str
    preconditions: tuple[str, ...]
    success_condition: str
    failure_condition: str
    invalidation_condition: str
    motive_ref: MotiveRef
    founding_st_version: str
    expires_at_step: int
    provenance: str
    grounding_contribution_refs: tuple[str, ...] = ()
    goal_ref: str | None = None
    plan_ref: str | None = None
    state: str = "proposed"

    def validate(self) -> None:
        if self.type not in {"primitive", "composite"}:
            raise ValueError("invalid option type")
        if not self.motive_ref.id or not self.motive_ref.type:
            raise ValueError("motif_ref is mandatory")
        if self.state not in {"proposed", "candidate", "engaged", "finished"}:
            raise ValueError("invalid option state")
        if self.expires_at_step < 1:
            raise ValueError("option expiry must be a positive world step")


@dataclass(frozen=True, slots=True)
class OptionProposal:
    option: Option
    plan: Plan | None
    preliminary_admissibility: str | None = None

    def validate(self) -> None:
        self.option.validate()
        if self.plan is not None:
            self.plan.validate()
            if self.plan.option_ref != self.option.id:
                raise ValueError("plan must refer to proposed option")
        if self.preliminary_admissibility not in {
            None,
            "admissible",
            "indeterminate",
        }:
            raise ValueError("invalid preliminary admissibility")


@dataclass(frozen=True, slots=True)
class Contribution:
    id: str
    schema_version: str
    type: str
    summary: str
    subject_ref: str
    emitter_module: str
    signal_family: str
    confidence: float
    urgency: float
    risk: float
    value: float
    production_t: int
    production_cycle: int
    expires_at_step: int
    payload: object
    goal_ref: str | None = None
    provenance_inputs: tuple[str, ...] = ()
    signal_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.type not in {
            "observation",
            "hypothesis",
            "alert",
            "proposed_action",
            "prediction",
            "response",
        }:
            raise ValueError("invalid contribution type")
        for name, value in (
            ("confidence", self.confidence),
            ("urgency", self.urgency),
            ("risk", self.risk),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0,1]")
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("gatekeeper value must be in [0,1]")
        if self.expires_at_step < self.production_t:
            raise ValueError("contribution cannot expire before production")


@dataclass(frozen=True, slots=True)
class STElement:
    contribution_ref: str
    summary: str
    score: float
    decomposition: Mapping[str, float]
    reliability: float
    production_t: int
    expires_at_step: int
    preempted: bool


@dataclass(frozen=True, slots=True)
class STVersion:
    individual_id: str
    version: str
    cycle: int
    t_monde: int
    fixed: Mapping[str, object]
    competitive: tuple[STElement, ...]
    requests: Mapping[str, str] = field(default_factory=dict)
    diff: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EvaluationOption:
    option_ref: str
    option_version: str
    cycle: int
    t_monde: int
    status: str
    learned_value_status: str
    learned_value: float | None
    simulated_value_status: str
    simulated_value: float | None
    intrinsic_status: str
    intrinsic_value: float | None
    risk_status: str
    risk: float | None
    safety_uncertainty: float
    protection: bool
    signal_ids: tuple[str, ...]
    producers: tuple[str, ...]

    def validate(self) -> None:
        if self.status not in {"evaluated", "not_evaluated"}:
            raise ValueError("invalid evaluation status")
        if self.learned_value_status not in {"learned", "unlearned"}:
            raise ValueError("invalid learned-value status")
        if self.simulated_value_status not in {"computed", "unavailable"}:
            raise ValueError("invalid simulated-value status")
        if self.intrinsic_status not in {"applicable", "not_applicable"}:
            raise ValueError("invalid intrinsic status")
        if self.risk_status not in {"known", "unknown"}:
            raise ValueError("invalid risk status")
        if not 0.0 <= self.safety_uncertainty <= 1.0:
            raise ValueError("safety uncertainty must be in [0,1]")


def canonical_option_order(option: Option) -> tuple[str, str]:
    return (option.learning_signature, option.id)
