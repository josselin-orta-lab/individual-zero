"""Minimal normative Stage-4 option competition.

Stage 4 uses substitution evidence by primitive action type, no learned Q,
no simulator, no intrinsic motivation, and neutral risk/uncertainty penalties.
All numeric dynamics are explicit injected P-xx configuration.

Spec: 8.3-8.8, DC-01, DC-02, DC-10, 20.4 Stage 4.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import exp, isfinite
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


@dataclass(frozen=True, slots=True)
class AppliedMemoryIntention:
    """A remembered semantic commitment, never an engaged motor option.

    Competition owns the evidence; the next fresh perception can confirm or
    contradict an arrival. M11 persists this as ordinary Competition state.
    """
    semantic_ref: str
    source_option_ref: str
    goal_ref: str
    expected_position: tuple[int, int]
    observed_site: tuple[int, int]
    applied_step: int
    expires_at_step: int
    evidence: float
    reconsidered_step: int | None = None
    confirmed_step: int | None = None  # ONLY the next authentic Perception

    def validate(self) -> None:
        def point(value):
            return (type(value) is tuple and len(value) == 2
                    and all(type(n) is int for n in value))
        # The applied option is an immutable first-person causal reference.
        # Its canonical place, entity and first hop must agree with the
        # semantic intention and observed control result, also after M11.
        canonical = None
        if type(self.source_option_ref) is str:
            import re
            canonical = re.fullmatch(
                r"option:place-memory:place:(.+):at:(-?(?:0|[1-9][0-9]*)):"
                r"(-?(?:0|[1-9][0-9]*)):from:(-?(?:0|[1-9][0-9]*)):"
                r"(-?(?:0|[1-9][0-9]*)):via:(-?(?:0|[1-9][0-9]*)):"
                r"(-?(?:0|[1-9][0-9]*))",
                self.source_option_ref,
            )
        if (canonical is None
            or type(self.semantic_ref) is not str
            or not point(self.observed_site)
            or not point(self.expected_position)
            or canonical.group(1) != self.semantic_ref.removeprefix("memory_place_return:")
            or tuple(map(int, canonical.group(2, 3))) != self.observed_site
            or tuple(map(int, canonical.group(6, 7))) != self.expected_position
            or sum(abs(a-b) for a,b in zip(
                map(int, canonical.group(4,5)),
                map(int, canonical.group(6,7)))) != 1):
            raise ValueError("spatial intention provenance is inconsistent")
        if (type(self.semantic_ref) is not str
            or not self.semantic_ref.startswith("memory_place_return:")
            or len(self.semantic_ref) <= len("memory_place_return:")
            or type(self.source_option_ref) is not str
            or not self.source_option_ref.startswith("option:place-memory:place:")
            or type(self.goal_ref) is not str or not self.goal_ref
            or not point(self.expected_position) or not point(self.observed_site)
            or type(self.applied_step) is not int or self.applied_step < 1
            or type(self.expires_at_step) is not int
            or self.expires_at_step <= self.applied_step
            or type(self.evidence) not in (int, float)
            or not isfinite(self.evidence) or not 0.0 < self.evidence <= 1.0
            or (self.reconsidered_step is not None and
                (type(self.reconsidered_step) is not int
                 or not self.applied_step < self.reconsidered_step
                        < self.expires_at_step))
            or (self.confirmed_step is not None and (
                type(self.confirmed_step) is not int
                or self.confirmed_step != self.applied_step + 1
                or self.confirmed_step >= self.expires_at_step))
            # No M11 image may claim that an intention was reconsidered
            # before its arrival was confirmed by the next Perception.
            or (self.reconsidered_step is not None
                and (self.confirmed_step is None
                     or self.reconsidered_step < self.confirmed_step))):
            raise ValueError("invalid first-person applied memory intention")


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
        self._applied_memory_intent: AppliedMemoryIntention | None = None
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

    @property
    def applied_memory_intention(self) -> AppliedMemoryIntention | None:
        """Read-only owner state, not an option/command or fresh motor right."""
        return self._applied_memory_intent

    def record_applied_memory_intention(
        self, *, option_ref: str, verified_control_step: tuple,
        applied_step: int, expected_position: tuple[int, int],
        observed_site: tuple[int, int], fallback_used: bool,
    ) -> bool:
        """Record only a previously evaluated AND physically applied choice.

        Stage11 supplies destination and site from a frozen first-person
        Exploration offer. Action Control must have advanced the same plan.
        An unselected proposed route, refusal or fallback cannot record it.
        """
        if (type(fallback_used) is not bool
            or type(applied_step) is not int or applied_step < 1
            or type(verified_control_step) is not tuple
            or len(verified_control_step) != 3
            or type(expected_position) is not tuple
            or len(expected_position) != 2
            or any(type(x) is not int for x in expected_position)
            or type(observed_site) is not tuple
            or len(observed_site) != 2
            or any(type(x) is not int for x in observed_site)):
            raise ValueError("invalid applied intention provenance")
        current = self._registry.get(option_ref)
        if current is None or fallback_used:
            return False
        proposal = current.proposal
        opt, plan = proposal.option, proposal.plan
        if (opt.id != option_ref
            or opt.provenance != "memory"
            or opt.motive_ref.type != "place_memory"
            or opt.id != f"option:place-memory:{opt.motive_ref.id}"
            or not opt.learning_signature.startswith("memory_place_return:")
            or opt.goal_ref is None or plan is None
            or plan.goal_ref != opt.goal_ref
            or plan.id != verified_control_step[1]
            or verified_control_step != (opt.id, plan.id, 1)
            or len(plan.steps) != 1
            or plan.steps[0].command.primitive != "se_deplacer"
            or current.last_proposal_t != applied_step
            or current.accumulator < current.last_threshold
            or not isfinite(current.accumulator)
            or opt.expires_at_step <= applied_step):
            return False
        record = AppliedMemoryIntention(
            semantic_ref=opt.learning_signature,
            source_option_ref=opt.id,
            goal_ref=opt.goal_ref,
            expected_position=expected_position,
            observed_site=observed_site,
            applied_step=applied_step,
            expires_at_step=opt.expires_at_step,
            evidence=min(1.0, current.accumulator),
        )
        try:
            record.validate()
        except ValueError:
            # A mismatched current proposal/physical result is not an intent.
            return False
        self._applied_memory_intent = record
        return True

    def expire_memory_intention(self, *, world_step: int) -> bool:
        """Expire a semantic commitment by physical time, without Perception.

        Sleep never confirms a position, changes Q or grants motor admission.
        Only Competition owns this time-bound causal descriptor.
        """
        if type(world_step) is not int or world_step < 1:
            raise ValueError("invalid intention expiration clock")
        intent = self._applied_memory_intent
        if intent is None:
            return False
        if world_step < intent.applied_step:
            raise ValueError("intention clock predates application")
        if world_step < intent.expires_at_step:
            return False
        self._applied_memory_intent = None
        return True

    def observe_memory_intention(
        self, *, world_step: int, observed_position: tuple[int, int],
    ) -> str:
        """Compare the trusted last applied intention to fresh Perception.

        This does not observe WorldBody or dispatch an action. An intervening
        step never fabricates fresh continuity; it may leave the semantic
        interest suspended until expiry. GoalManager still owns which goal
        is active and Stage8/Competition still arbitrate every new command.
        """
        if (type(world_step) is not int or world_step < 1
            or type(observed_position) is not tuple
            or len(observed_position) != 2
            or any(type(n) is not int for n in observed_position)):
            raise ValueError("invalid first-person intention observation")
        intent = self._applied_memory_intent
        if intent is None:
            return "absent"
        if world_step < intent.applied_step:
            raise ValueError("memory intention cannot precede applied step")
        if world_step >= intent.expires_at_step:
            self._applied_memory_intent = None
            return "expired"
        if world_step == intent.applied_step:
            return "awaiting_new_capture"
        if world_step == intent.applied_step + 1:
            if observed_position != intent.expected_position:
                self._applied_memory_intent = None
                return "contradicted"
            if intent.confirmed_step is None:
                # Confirm the physically expected arrival in the owner only
                # AFTER the next actual first-person Perception.
                self._applied_memory_intent = replace(
                    intent, confirmed_step=world_step,
                )
            return "reconsider"
        # A late capture is NOT retroactive arrival confirmation. Without
        # a confirmed next-step observation, suspended intent is inert.
        return "suspended"

    def invalidate_contradicted_place_intention(
        self, *, semantic_ref: str, observed_site: tuple[int, int],
        contradiction_step: int,
    ) -> bool:
        """Forget an intent only when its personally observed site is disproved.

        Exploration owns the perception and its paid observation. This owner
        only invalidates the matching applied semantic commitment; it never
        erases the historical place memory, Q or a physical control command.
        """
        if (type(semantic_ref) is not str
            or not semantic_ref.startswith("memory_place_return:")
            or type(observed_site) is not tuple or len(observed_site) != 2
            or any(type(v) is not int for v in observed_site)
            or type(contradiction_step) is not int or contradiction_step < 1):
            raise ValueError("invalid first-person place contradiction")
        intent = self._applied_memory_intent
        if (intent is None or intent.semantic_ref != semantic_ref
            or intent.observed_site != observed_site
            or contradiction_step <= intent.applied_step):
            return False
        self._applied_memory_intent = None
        return True

    def drop_memory_intention(self) -> None:
        """Forget contradicting/expired evidence without moving the body."""
        self._applied_memory_intent = None

    def retain_bounded_intention_evidence(
        self, *, option_ref: str, t_monde: int,
        observed_origin: tuple[int, int], evidence: float,
    ) -> bool:
        """Reconsider one new PAID candidate, strictly below motor threshold.

        This preserves no Action Control admission, fallback engagement or Q.
        A semantic intention may remain after interruption, but cannot reuse
        motor proof after a non-consecutive step or twice in one world step.
        """
        if (type(option_ref) is not str or not option_ref
            or type(t_monde) is not int or t_monde < 2
            or type(observed_origin) is not tuple
            or len(observed_origin) != 2
            or any(type(n) is not int for n in observed_origin)
            or type(evidence) not in (float, int)
            or not isfinite(evidence) or not 0.0 < evidence <= 1.0):
            raise ValueError("invalid bounded intention evidence")
        intent = self._applied_memory_intent
        candidate = self._registry.get(option_ref)
        if (intent is None or candidate is None
            # Retention is evidence about a CONFIRMED lived hop, never
            # an inherited priority from Action Control's application.
            # Requiring the owner-side Perception confirmation closes a
            # direct API bypass even if the natural runtime calls observe
            # before retention.
            or intent.confirmed_step != t_monde
            or t_monde != intent.applied_step + 1
            or t_monde >= intent.expires_at_step
            or intent.reconsidered_step is not None
            or observed_origin != intent.expected_position
            or candidate.last_proposal_t != t_monde
            or candidate.accumulator != 0.0
            or self._engaged_option_id == option_ref):
            return False
        option, plan = candidate.proposal.option, candidate.proposal.plan
        if (option.id == intent.source_option_ref
            or option.provenance != "memory"
            or option.motive_ref.type != "place_memory"
            or option.id != f"option:place-memory:{option.motive_ref.id}"
            or option.learning_signature != intent.semantic_ref
            or not self._matches_remembered_place(option, intent)
            or option.goal_ref != intent.goal_ref
            or plan is None or plan.goal_ref != intent.goal_ref
            or len(plan.steps) != 1
            or plan.steps[0].command.primitive != "se_deplacer"):
            return False
        retained = min(float(evidence), intent.evidence,
                       candidate.last_threshold * self._config.residual)
        if not 0.0 < retained < candidate.last_threshold:
            return False
        candidate.accumulator = retained
        self._applied_memory_intent = AppliedMemoryIntention(
            semantic_ref=intent.semantic_ref,
            source_option_ref=intent.source_option_ref,
            goal_ref=intent.goal_ref,
            expected_position=intent.expected_position,
            observed_site=intent.observed_site,
            applied_step=intent.applied_step,
            expires_at_step=intent.expires_at_step,
            evidence=intent.evidence,
            reconsidered_step=t_monde,
            confirmed_step=intent.confirmed_step,
        )
        return True

    @staticmethod
    def _matches_remembered_place(option: Option, intent: AppliedMemoryIntention) -> bool:
        """The actual newly registered option must target the same lived site."""
        import re
        ref = option.motive_ref.id
        match = re.fullmatch(
            r"place:(.+):at:(-?(?:0|[1-9][0-9]*)):"
            r"(-?(?:0|[1-9][0-9]*)):from:(-?(?:0|[1-9][0-9]*)):"
            r"(-?(?:0|[1-9][0-9]*)):via:(-?(?:0|[1-9][0-9]*)):"
            r"(-?(?:0|[1-9][0-9]*))", ref,
        ) if type(ref) is str else None
        return bool(
            match is not None
            and match.group(1) == intent.semantic_ref.removeprefix("memory_place_return:")
            and tuple(map(int, match.group(2, 3))) == intent.observed_site
            and sum(abs(a-b) for a,b in zip(
                map(int,match.group(4,5)),map(int,match.group(6,7)))) == 1
        )

    def reconsider_confirmed_intention(
        self, *, option_ref: str, t_monde: int,
        observed_site: tuple[int, int], active_goal_id: str | None,
    ) -> bool:
        """Resume considering a semantic place AFTER an interruption.

        Only a newly registered, paid, independently evaluated option may be
        reconsidered. No prior accumulator, engagement, Q, UC or motor permit
        is transferred; the ordinary evaluator alone establishes its value.
        """
        if (type(option_ref) is not str or not option_ref
            or type(t_monde) is not int or t_monde < 2
            or type(observed_site) is not tuple or len(observed_site) != 2
            or any(type(x) is not int for x in observed_site)
            or (active_goal_id is not None
                and type(active_goal_id) is not str)):
            raise ValueError("invalid semantic intention reconsideration")
        intent = self._applied_memory_intent
        candidate = self._registry.get(option_ref)
        if (intent is None or intent.confirmed_step != intent.applied_step + 1
            or t_monde <= intent.confirmed_step
            or t_monde >= intent.expires_at_step
            or intent.reconsidered_step == t_monde
            or intent.goal_ref != active_goal_id
            or intent.observed_site != observed_site
            or candidate is None or candidate.last_proposal_t != t_monde
            or self._engaged_option_id == option_ref):
            return False
        option, plan = candidate.proposal.option, candidate.proposal.plan
        if (option.id == intent.source_option_ref
            or option.provenance != "memory"
            or option.motive_ref.type != "place_memory"
            or option.id != f"option:place-memory:{option.motive_ref.id}"
            or option.learning_signature != intent.semantic_ref
            or not self._matches_remembered_place(option, intent)
            or option.goal_ref != intent.goal_ref
            or plan is None or plan.goal_ref != intent.goal_ref
            or len(plan.steps) != 1
            or plan.steps[0].command.primitive != "se_deplacer"):
            return False
        # Crucially, do NOT change candidate.accumulator or last_threshold.
        self._applied_memory_intent = replace(
            intent, reconsidered_step=t_monde,
        )
        return True

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
            # A later callback cannot rewrite a candidate's already
            # authenticated proposal clock into an earlier deliberation.
            if t_monde < existing.last_proposal_t:
                return False
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
        if (self._applied_memory_intent is not None
            and t_monde >= self._applied_memory_intent.expires_at_step):
            self._applied_memory_intent = None
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

    def close_deliberation(
        self, winner: OptionProposal | None, *, adjudicated: bool = True,
    ) -> None:
        # A physically applied fallback is not an adjudicated Competition win.
        # It must not erode the evidence of unrelated still-viable options.
        # Existing validity checks, expiry and capacity constraints remain.
        if type(adjudicated) is not bool:
            raise ValueError("Competition adjudication flag must be boolean")
        if not adjudicated:
            return
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
        state = {
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
        intent = self._applied_memory_intent
        if intent is not None:
            intent.validate()
            state["applied_memory_intention"] = {
                "semantic_ref": intent.semantic_ref,
                "source_option_ref": intent.source_option_ref,
                "goal_ref": intent.goal_ref,
                "expected_position": list(intent.expected_position),
                "observed_site": list(intent.observed_site),
                "applied_step": intent.applied_step,
                "expires_at_step": intent.expires_at_step,
                "evidence": intent.evidence,
                "reconsidered_step": intent.reconsidered_step,
                **({"confirmed_step": intent.confirmed_step}
                   if intent.confirmed_step is not None else {}),
            }
        return state

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("Competition state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("Competition config version mismatch")
        required = {"config_version", "cycle", "engaged_option_id", "registry"}
        if set(state) not in (required, required | {"applied_memory_intention"}):
            raise ValueError("invalid Competition owner-image fields")
        cycle = state.get("cycle")
        if type(cycle) is not int or cycle < 0:
            raise ValueError("invalid Competition cycle")
        engaged = state.get("engaged_option_id")
        if engaged is not None and (type(engaged) is not str or not engaged):
            raise ValueError("invalid engaged option id")
        raw_registry = state.get("registry")
        if not isinstance(raw_registry, list):
            raise ValueError("invalid Competition registry")
        registry: dict[str, CandidateState] = {}
        for row in raw_registry:
            if (not isinstance(row, Mapping)
                or set(row) != {"proposal", "accumulator",
                                "last_threshold", "last_proposal_t"}):
                raise ValueError("invalid Competition candidate fields")
            proposal_raw = row["proposal"]
            if not isinstance(proposal_raw, Mapping):
                raise ValueError("invalid Competition proposal")
            proposal = decode_proposal(proposal_raw)
            proposal.validate()
            option_id = proposal.option.id
            if option_id in registry:
                # No duplicate causal candidate may silently replace another.
                raise ValueError("duplicate Competition candidate identity")
            raw_accumulator = row["accumulator"]
            raw_threshold = row["last_threshold"]
            proposal_step = row["last_proposal_t"]
            if (type(raw_accumulator) not in (int, float)
                or type(raw_threshold) not in (int, float)
                or type(proposal_step) is not int
                or proposal_step < 1
                or proposal_step >= proposal.option.expires_at_step):
                raise ValueError("invalid Competition candidate numeric provenance")
            try:
                accumulator = float(raw_accumulator)
                threshold = float(raw_threshold)
            except (OverflowError, ValueError) as error:
                raise ValueError("invalid Competition candidate numeric range") from error
            if (not isfinite(accumulator) or accumulator < 0.0
                or not isfinite(threshold)
                or not self._config.threshold_floor <= threshold <= self._config.base_threshold):
                raise ValueError("invalid Competition candidate accumulation or threshold")
            registry[option_id] = CandidateState(
                proposal=proposal, accumulator=accumulator,
                last_threshold=threshold, last_proposal_t=proposal_step,
            )
        if engaged is not None and engaged not in registry:
            raise ValueError("orphan Competition motor engagement")
        if sum(ident != "permanent:attendre" for ident in registry) > self._config.options_max:
            raise ValueError("Competition image exceeds the candidate capacity")
        raw_intent = state.get("applied_memory_intention")
        intention = None
        if raw_intent is not None:
            required = {
                "semantic_ref", "source_option_ref", "goal_ref",
                "expected_position", "observed_site", "applied_step",
                "expires_at_step", "evidence", "reconsidered_step",
            }
            if (not isinstance(raw_intent, Mapping)
                or set(raw_intent) not in (required, required | {"confirmed_step"})
                or any(type(raw_intent[k]) is not str
                       for k in ("semantic_ref", "source_option_ref", "goal_ref"))
                or any(not isinstance(raw_intent[k], (tuple, list))
                       or len(raw_intent[k]) != 2
                       for k in ("expected_position", "observed_site"))):
                raise ValueError("invalid persisted memory intention")
            intention = AppliedMemoryIntention(
                semantic_ref=raw_intent["semantic_ref"],
                source_option_ref=raw_intent["source_option_ref"],
                goal_ref=raw_intent["goal_ref"],
                expected_position=tuple(raw_intent["expected_position"]),
                observed_site=tuple(raw_intent["observed_site"]),
                applied_step=raw_intent["applied_step"],
                expires_at_step=raw_intent["expires_at_step"],
                evidence=raw_intent["evidence"],
                reconsidered_step=raw_intent["reconsidered_step"],
                confirmed_step=raw_intent.get("confirmed_step"),
            )
            intention.validate()
            if ("confirmed_step" in raw_intent
                and intention.confirmed_step is None):
                raise ValueError("invalid explicit arrival-confirmation receipt")
        self._cycle = cycle
        self._engaged_option_id = engaged
        self._registry = registry
        self._applied_memory_intent = intention
