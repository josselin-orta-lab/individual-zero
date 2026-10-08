"""Integrated Stage-4 minimal cognitive runtime.

This is the first loop that traverses the reference architecture:
world -> perception -> contributions -> Gatekeeper -> S_t -> Planning ->
Competition -> Action Control -> world.

No Stage-5+ mechanism is introduced here.

Spec: 3.3-3.8, 6, 7, 8, 9, 20.3 Stage 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.config import (
    MVP_CYCLE_PHASE_COMPONENT_ORDER,
    MVP_PHASE1_PRODUCER_ORDER,
    build_ontology_registry,
    build_schema_registry,
)
from i0.contracts import Contribution, Goal, OptionProposal
from i0.modules import (
    Competition,
    CompetitionConfig,
    CognitiveSpace,
    Gatekeeper,
    GatekeeperConfig,
    GoalManager,
    GoalManagerConfig,
    GreedyPlannerE0,
    MinimalMetacognition,
    PlanningConfig,
    PreparedCommand,
    StaticSafetyFacts,
    ValueAndNeeds,
    ValueNeedsConfig,
)
from i0.serde import encode_proposal

from .bus import InMemoryBus, ProducerBuffer
from .compute_budget import ComputeBudgetConfig, CycleComputeBudget
from .determinism import canonical_causal_bytes, deterministic_id, sha256_hex
from .safety_protocol import SafetyProtocolConfig
from .scheduler import CyclePhase, PhaseContext
from .stage2_runtime import CommandExecution
from .stage3_runtime import Stage3Runtime
from .world import WorldLayout, WorldPhysicsConfig, command_digest


@dataclass(frozen=True, slots=True)
class Stage4Config:
    version: str
    perception_ttl_steps: int
    value_needs: ValueNeedsConfig
    goals: GoalManagerConfig
    gatekeeper: GatekeeperConfig
    planning: PlanningConfig
    competition: CompetitionConfig
    compute_budget: ComputeBudgetConfig

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage 4 config version must not be empty")
        if self.perception_ttl_steps < 1:
            raise ValueError("perception TTL must be >= 1")
        self.value_needs.validate()
        self.goals.validate()
        self.gatekeeper.validate()
        self.planning.validate()
        self.competition.validate()
        self.compute_budget.validate()


@dataclass(frozen=True, slots=True)
class Stage4StepResult:
    source: str
    execution_status: str
    command_primitive: str | None
    option_ref: str | None
    st_version: str | None
    cycles_used: int
    reflex_triggered: bool
    fallback_used: bool


class Stage4Runtime:
    """Normative minimal cognitive system with explicit injected parameters."""

    individual_id = "i0-stage4"

    def __init__(
        self,
        *,
        world_config: WorldPhysicsConfig,
        layout: WorldLayout,
        safety_config: SafetyProtocolConfig,
        safety_facts: StaticSafetyFacts,
        protected_integrity_threshold: float,
        config: Stage4Config,
    ) -> None:
        config.validate()
        self._config = config

        self.stage3 = Stage3Runtime(
            config=world_config,
            layout=layout,
            phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
            safety_config=safety_config,
            safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
        )
        self.value_needs = ValueAndNeeds(config.value_needs)
        self.goal_manager = GoalManager(config.goals)
        self.gatekeeper = Gatekeeper(config.gatekeeper)
        self.s_t = CognitiveSpace(individual_id=self.individual_id)
        self.planning = GreedyPlannerE0(config.planning)
        self.competition = Competition(config.competition)
        self.compute_budget = CycleComputeBudget(config=config.compute_budget)
        self.metacognition = MinimalMetacognition()

        self._ontology = build_ontology_registry()
        self._schemas = build_schema_registry()
        self._buffers = {
            producer: ProducerBuffer(producer)
            for producer in MVP_PHASE1_PRODUCER_ORDER
        }
        self.bus = InMemoryBus(
            schemas=self._schemas,
            ontology=self._ontology,
            producer_order=MVP_PHASE1_PRODUCER_ORDER,
            journal=self.stage3.journal,
        )

        self._event_sequence = 0
        self._step_need_state = None
        self._step_reward = 0.0
        self._admitted_contributions: tuple[Contribution, ...] = ()
        self._pending_contributions: dict[str, Contribution] = {}
        self._proposal_this_cycle: OptionProposal | None = None
        self._cycle_result = None
        self._admitted_decision = None
        self._fallback_used_this_cycle = False
        self._safety_block_after_cycle = False
        self._cycle_degraded = False

    @property
    def journal(self):
        return self.stage3.journal

    @property
    def world(self):
        return self.stage3.world

    @property
    def scheduler(self):
        return self.stage3.scheduler

    @property
    def bench(self):
        return self.stage3.bench

    @property
    def causal_owners(self):
        owners = list(self.stage3.substrate.causal_owners)
        owners.extend(
            [
                self.stage3.perception,
                self.stage3.control,
                self.value_needs,
                self.goal_manager,
                self.gatekeeper,
                self.s_t,
                self.planning,
                self.competition,
                self.compute_budget,
                self.metacognition,
                self.bus,
            ]
        )
        owners.extend(self._buffers[producer] for producer in MVP_PHASE1_PRODUCER_ORDER)

        seen: set[str] = set()
        unique = []
        for owner in owners:
            owner_id = owner.owner_id
            if owner_id in seen:
                continue
            seen.add(owner_id)
            unique.append(owner)
        return tuple(unique)

    def _write(
        self,
        *,
        kind: str,
        data: Mapping[str, object],
        cycle: int | None = None,
    ) -> None:
        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("Stage 4 journal event requires active step")
        event_id = deterministic_id(
            "journal-event-v1",
            "stage4-runtime",
            attempt.t_monde,
            cycle,
            attempt.attempt_ref,
            self._event_sequence,
            kind,
        )
        self._event_sequence += 1
        event = {
            "emitter": "stage4-runtime",
            "kind": kind,
            "t_monde": attempt.t_monde,
            "attempt_ref": attempt.attempt_ref,
            "data": dict(data),
        }
        if cycle is not None:
            event["cycle"] = cycle
        self.journal.append(
            event_id=event_id,
            causal_event=event,
        )

    def _charge(
        self,
        *,
        module: str,
        operation: str,
        count: int = 1,
        protected: bool = False,
    ) -> bool:
        charge = self.compute_budget.charge(
            module=module,
            operation=operation,
            count=count,
        )
        self._write(
            kind="compute_charge",
            cycle=self.compute_budget.cycle,
            data={
                "module": module,
                "operation": operation,
                "count": count,
                "requested_uc": charge.requested_uc,
                "accepted": charge.accepted,
                "reason": charge.reason,
            },
        )
        if charge.accepted:
            return True
        self._cycle_degraded = True
        if protected:
            raise RuntimeError(
                f"protected compute path exceeded P-43 budget: {module}/{operation}"
            )
        return False

    @staticmethod
    def _comparison_as_dict(comparison) -> object:
        if comparison is None:
            return None
        return {
            "option_ref": comparison.option_ref,
            "sent_t_monde": comparison.sent_t_monde,
            "observed_t_monde": comparison.observed_t_monde,
            "status": comparison.status,
            "attribution": comparison.attribution,
            "effects": list(comparison.effects),
        }

    @staticmethod
    def _goal_as_dict(goal: Goal | None) -> object:
        if goal is None:
            return None
        return {
            "id": goal.id,
            "goal_type": goal.goal_type,
            "target": goal.target,
            "satisfaction_condition": goal.satisfaction_condition,
            "principal_measure": goal.principal_measure,
            "current_pressure": goal.current_pressure,
            "state": goal.state,
            "activation_t": goal.activation_t,
            "activation_cycle": goal.activation_cycle,
            "justification_ref": goal.justification_ref,
        }

    def _goal_satisfied(self) -> bool:
        goal = self.goal_manager.active_goal
        state = self._step_need_state
        if goal is None or state is None:
            return False
        target = goal.target
        if target not in state.deficits:
            return False
        return state.deficits[target] <= 0.0

    @staticmethod
    def _semantic_terms(contribution: Contribution) -> tuple[str, ...]:
        terms: list[str] = []
        payload = contribution.payload
        if isinstance(payload, Mapping):
            entity_type = payload.get("entity_type")
            if isinstance(entity_type, str):
                terms.append(
                    "berry"
                    if entity_type in {"berry_a", "berry_b"}
                    else entity_type
                )
            target = payload.get("target")
            if isinstance(target, str) and target in {
                "energy",
                "food",
                "water",
                "integrity",
            }:
                terms.append(target)
        if contribution.subject_ref.startswith("body:"):
            term = contribution.subject_ref.split(":", 1)[1]
            if term in {"energy", "food", "water", "integrity"}:
                terms.append(term)
        return tuple(sorted(set(terms)))

    def _publish_contribution(self, contribution: Contribution) -> None:
        contribution.validate()
        payload = {
            "id": contribution.id,
            "version_schema": contribution.schema_version,
            "type": contribution.type,
            "resume": contribution.summary,
            "charge": (
                encode_proposal(contribution.payload)
                if isinstance(contribution.payload, OptionProposal)
                else contribution.payload
            ),
            "subject_ref": contribution.subject_ref,
            "references_secondaires": [],
            "confiance": {
                "conf": contribution.confidence,
                "methode": "declaree",
            },
            "urgence": {"niveau": contribution.urgency},
            "risque": {
                "niveau": contribution.risk,
                "irreversible": False,
            },
            "valeur": {
                "estimation": contribution.value,
                "cible": "but" if contribution.goal_ref is not None else "besoin",
                "incertitude": 0.0,
            },
            "cout": {"engage_UC": 0},
            "provenance": {
                "individu": self.individual_id,
                "module": contribution.emitter_module,
                "version_module": self._config.version,
                "entrees": list(contribution.provenance_inputs),
                "signal_ids": list(contribution.signal_ids),
            },
            "horodatage": {
                "t_monde": contribution.production_t,
                "cycle": contribution.production_cycle,
                "t_systeme": None,
            },
            "validite": {
                "expire_a": {
                    "value": contribution.expires_at_step,
                    "unit": "pas",
                }
            },
            "liens": {},
            "degrade": False,
            "empreinte": sha256_hex(
                canonical_causal_bytes(
                    {
                        "id": contribution.id,
                        "payload": (
                            encode_proposal(contribution.payload)
                            if isinstance(contribution.payload, OptionProposal)
                            else contribution.payload
                        ),
                    }
                )
            ),
        }
        self._buffers[contribution.emitter_module].publish(
            schema_name="Contribution",
            schema_version="1.0",
            payload=payload,
            semantic_terms=self._semantic_terms(contribution),
        )
        self._pending_contributions[contribution.id] = contribution

    def _planning_contribution(
        self,
        proposal: OptionProposal,
        *,
        t_monde: int,
        cycle: int,
    ) -> Contribution:
        goal = self.goal_manager.active_goal
        urgency = 0.0 if goal is None else goal.current_pressure
        contribution = Contribution(
            id=f"action-proposal:{proposal.option.id}:{t_monde}:{cycle}",
            schema_version="mvp-v1.2.1",
            type="proposed_action",
            summary=f"proposed option {proposal.option.learning_signature}",
            subject_ref=f"option:{proposal.option.id}",
            emitter_module="planning",
            signal_family="planning",
            confidence=1.0,
            urgency=urgency,
            risk=0.0,
            value=0.0,
            production_t=t_monde,
            production_cycle=cycle,
            expires_at_step=proposal.option.expires_at_step,
            payload=proposal,
            goal_ref=proposal.option.goal_ref,
        )
        contribution.validate()
        return contribution

    def _propose_for_cycle(
        self,
        *,
        capture,
        goal_for_planning: Goal,
        st_before_cycle,
        cycle: int,
    ) -> OptionProposal | None:
        """Stage-specific planning seam. Stage 4 keeps greedy E-0 exactly."""
        return self.planning.propose(
            goal=goal_for_planning,
            st_version=st_before_cycle.version,
            position=(capture.x, capture.y),
            known_entities=self.stage3.perception.known_entities,
            observation_ref_by_entity=(
                self.stage3.perception.observation_ref_by_entity
            ),
            retained_contribution_refs=frozenset(
                element.contribution_ref
                for element in st_before_cycle.competitive
            ),
            t_monde=capture.t_monde,
            cycle=cycle,
        )

    def _register_option_proposal(
        self,
        *,
        proposal: OptionProposal,
        active_goal_id: str | None,
        t_monde: int,
        cycle: int,
    ) -> bool:
        """Stage-specific registration seam; Stage 4 keeps exact semantics."""
        del cycle
        return self.competition.register(
            proposal,
            active_goal_id=active_goal_id,
            t_monde=t_monde,
        )

    def _evaluate_competition_cycle(
        self,
        *,
        capture,
        cycle: int,
    ):
        """Stage-specific evidence seam. Stage 4 keeps substitution evidence."""
        return self.competition.evaluate(
            cycle=cycle,
            t_monde=capture.t_monde,
        )

    def _phase_hooks(
        self,
        *,
        cycle: int,
        capture,
        goal_for_planning: Goal | None,
        st_before_cycle,
    ):
        def no_op(_ctx: PhaseContext) -> None:
            return None

        def modulation_hook(_ctx: PhaseContext) -> None:
            self.compute_budget.open_cycle(cycle)
            self._cycle_degraded = False

        def perception_hook(_ctx: PhaseContext) -> None:
            if cycle != 1:
                return
            if not self._charge(
                module="perception",
                operation="perception_publish",
                count=max(1, len(capture.visible_entities)),
            ):
                return
            for contribution in self.stage3.perception.publish_capture(
                capture=capture,
                cycle=cycle,
                ttl_steps=self._config.perception_ttl_steps,
            ):
                self._publish_contribution(contribution)

        def value_needs_hook(_ctx: PhaseContext) -> None:
            if not self._charge(
                module="value_needs",
                operation="value_needs_cycle",
            ):
                self.goal_manager.defer_proposals(())
                return
            alerts, proposals = self.value_needs.produce(
                state=self._step_need_state,
                t_monde=capture.t_monde,
                cycle=cycle,
            )
            for alert in alerts:
                self._publish_contribution(alert)
            self.goal_manager.defer_proposals(proposals)

        def goal_hook(_ctx: PhaseContext) -> None:
            if not self._charge(
                module="goal_manager",
                operation="goal_arbitrate",
            ):
                return
            before = self.goal_manager.active_goal
            after = self.goal_manager.arbitrate(
                self.goal_manager.visible_proposals,
                t_monde=capture.t_monde,
                cycle=cycle,
                satisfied=self._goal_satisfied(),
            )
            if before != after:
                old_proposal = self.planning.current_proposal
                self._write(
                    kind="active_goal_changed",
                    cycle=cycle,
                    data={
                        "before": self._goal_as_dict(before),
                        "after": self._goal_as_dict(after),
                    },
                )
                if before is not None and (
                    after is None or after.id != before.id
                ):
                    if old_proposal is not None:
                        self.competition.invalidate_candidate(
                            old_proposal.option.id
                        )
                        self.stage3.control.clear_option_step(
                            old_proposal.option.id
                        )
                    self.planning.invalidate_current()

        def planning_hook(_ctx: PhaseContext) -> None:
            self._proposal_this_cycle = None
            if goal_for_planning is None or st_before_cycle is None:
                return
            if not self._charge(
                module="planning",
                operation="planning_build",
            ):
                return
            proposal = self._propose_for_cycle(
                capture=capture,
                goal_for_planning=goal_for_planning,
                st_before_cycle=st_before_cycle,
                cycle=cycle,
            )
            if proposal is None:
                return
            self._proposal_this_cycle = proposal
            self._publish_contribution(
                self._planning_contribution(
                    proposal,
                    t_monde=capture.t_monde,
                    cycle=cycle,
                )
            )

        def bus_hook(ctx: PhaseContext) -> None:
            self._charge(
                module="bus",
                operation="bus_pour",
                protected=True,
            )
            results = self.bus.pour(
                buffers=[
                    self._buffers[p]
                    for p in MVP_PHASE1_PRODUCER_ORDER
                ],
                t_monde=ctx.t_monde,
                cycle=ctx.cycle,
                attempt_ref=ctx.attempt_ref,
            )
            admitted: list[Contribution] = []
            for result in results:
                if not result.accepted or result.message is None:
                    continue
                contribution_id = str(result.message.payload["id"])
                contribution = self._pending_contributions.get(contribution_id)
                if contribution is not None:
                    admitted.append(contribution)
            self._admitted_contributions = tuple(admitted)
            self._pending_contributions.clear()
            self.bus.drain_available()

        def gatekeeper_hook(_ctx: PhaseContext) -> None:
            self._charge(
                module="gatekeeper",
                operation="gatekeeper_select",
                protected=True,
            )
            selection = self.gatekeeper.select(
                self._admitted_contributions,
                active_goal=self.goal_manager.active_goal,
                t_monde=capture.t_monde,
            )
            current_step = self.stage3.control.current_step
            version = self.s_t.publish(
                cycle=cycle,
                t_monde=capture.t_monde,
                fixed={
                    "body": dict(capture.body),
                    "active_goal": self._goal_as_dict(
                        self.goal_manager.active_goal
                    ),
                    "plan_step": {
                        "option_ref": current_step[0],
                        "plan_ref": current_step[1],
                        "step_index": current_step[2],
                    },
                    "profile": {"name": "normal"},
                    "budget": {
                        "state": (
                            "degraded"
                            if self._cycle_degraded
                            else self.metacognition.state.budget_state
                        )
                    },
                    "last_action": self._comparison_as_dict(
                        self.stage3.control.last_comparison
                    ),
                },
                competitive=selection.elements,
                diff={
                    "feedback": [
                        {
                            "contribution_ref": feedback.contribution_ref,
                            "status": feedback.status,
                            "score": feedback.score,
                            "reason": feedback.reason,
                        }
                        for feedback in selection.feedback
                    ]
                },
            )
            self._write(
                kind="s_t_published",
                cycle=cycle,
                data={
                    "version": version.version,
                    "competitive_refs": [
                        element.contribution_ref
                        for element in version.competitive
                    ],
                },
            )

        def competition_registration_hook(_ctx: PhaseContext) -> None:
            current = self.s_t.current
            if current is None:
                raise RuntimeError("Competition requires a published S_t")
            self.competition.ensure_wait(
                t_monde=capture.t_monde,
                st_version=current.version,
            )
            if not self._charge(
                module="competition",
                operation="competition_register",
            ):
                return
            self.competition.prune_invalid(
                active_goal_id=(
                    None
                    if self.goal_manager.active_goal is None
                    else self.goal_manager.active_goal.id
                ),
                t_monde=capture.t_monde,
            )
            if self._proposal_this_cycle is not None:
                registered = self._register_option_proposal(
                    proposal=self._proposal_this_cycle,
                    active_goal_id=(
                        None
                        if self.goal_manager.active_goal is None
                        else self.goal_manager.active_goal.id
                    ),
                    t_monde=capture.t_monde,
                    cycle=cycle,
                )
                self._write(
                    kind="option_registration",
                    cycle=cycle,
                    data={
                        "option_ref": self._proposal_this_cycle.option.id,
                        "registered": registered,
                    },
                )

        def competition_decision_hook(_ctx: PhaseContext) -> None:
            if not self._charge(
                module="competition",
                operation="competition_evaluate",
                count=max(1, self.competition.registry_size),
            ):
                self._cycle_result = None
                return
            self._cycle_result = self._evaluate_competition_cycle(
                capture=capture,
                cycle=cycle,
            )
            self._write(
                kind="competition_cycle",
                cycle=cycle,
                data={
                    "traces": [
                        {
                            "option_ref": trace.option_ref,
                            "accumulator_before": trace.accumulator_before,
                            "accumulator_after": trace.accumulator_after,
                            "threshold": trace.threshold,
                            "evidence": trace.evidence,
                            "crossed": trace.crossed,
                        }
                        for trace in self._cycle_result.traces
                    ]
                },
            )

        def control_hook(_ctx: PhaseContext) -> None:
            self._admitted_decision = None
            self._fallback_used_this_cycle = False
            self._safety_block_after_cycle = False

            if self._cycle_result is not None:
                for proposal in self._cycle_result.crossed_ranked:
                    if not self._charge(
                        module="action_control",
                        operation="control_admit",
                        protected=True,
                    ):
                        return
                    prepared = self.stage3.control.prepare_option_step(proposal)
                    admission = self.stage3.control.admit(
                        capture=capture,
                        prepared=prepared,
                    )
                    self.stage3.record_admission(
                        prepared=prepared,
                        admission=admission,
                    )
                    if admission.ok:
                        self._admitted_decision = (
                            proposal,
                            prepared,
                            admission,
                        )
                        return
                    if admission.scope == "option":
                        self.competition.invalidate_candidate(proposal.option.id)
                        self.planning.invalidate_current()
                        self.stage3.control.clear_option_step(
                            proposal.option.id
                        )

            if cycle != self._config.competition.c_max:
                return

            for proposal in self.competition.fallback_candidates():
                self._charge(
                    module="action_control",
                    operation="control_admit",
                    protected=True,
                )
                prepared = self.stage3.control.prepare_option_step(proposal)
                admission = self.stage3.control.admit(
                    capture=capture,
                    prepared=prepared,
                )
                self.stage3.record_admission(
                    prepared=prepared,
                    admission=admission,
                )
                if admission.ok:
                    self._admitted_decision = (
                        proposal,
                        prepared,
                        admission,
                    )
                    self._fallback_used_this_cycle = True
                    return
                if admission.scope == "option":
                    self.competition.invalidate_candidate(proposal.option.id)

            self._safety_block_after_cycle = True

        def metacognition_hook(_ctx: PhaseContext) -> None:
            self.metacognition.close_cycle(
                consumed_uc=self.compute_budget.consumed_cycle_uc,
                cycle_ceiling=self._config.compute_budget.cycle_ceiling,
                degraded=self._cycle_degraded,
                protected_capacity=self._config.compute_budget.protected_capacity,
            )

        return {
            CyclePhase.FREEZE: {
                "global_modulation": modulation_hook,
            },
            CyclePhase.PRODUCTION: {
                "perception": perception_hook,
                "value_needs": value_needs_hook,
                "memory": no_op,
                "goal_manager": goal_hook,
                "causal_model": no_op,
                "exploration": no_op,
                "planning": planning_hook,
                "metacognition_health": no_op,
                "bus": bus_hook,
            },
            CyclePhase.SELECTION: {
                "gatekeeper": gatekeeper_hook,
            },
            CyclePhase.EVALUATION: {
                "competition": competition_registration_hook,
            },
            CyclePhase.ACCUMULATION_DECISION: {
                "competition": competition_decision_hook,
                "action_control": control_hook,
            },
            CyclePhase.CLOSURE: {
                "metacognition_health": metacognition_hook,
                "causal_model": no_op,
                "perception": no_op,
                "journal": no_op,
            },
        }

    def _dispatch_decision(
        self,
        *,
        proposal: OptionProposal,
        prepared: PreparedCommand,
        admission,
        cycle: int,
        sent_t_monde: int,
    ) -> CommandExecution:
        execution = self.stage3.control.dispatch_prechecked(
            admission=admission,
            sender=lambda command: self.stage3.substrate.send_admitted_command(
                command,
                source="action_control",
                checkpoint_owners=self.causal_owners,
                individual_id=self.individual_id,
                checkpoint_cycle=cycle,
            ),
        )
        if not isinstance(execution, CommandExecution):
            raise TypeError("unexpected Stage 4 execution result")
        if execution.status == "applied":
            self.stage3.control.mark_cognitive_step_applied(proposal)
            self.stage3.control.record_sent_prediction(
                prepared=prepared,
                t_monde=sent_t_monde,
            )
        return execution

    def _handle_agency_comparison(
        self,
        *,
        capture,
        comparison,
    ) -> None:
        """Stage-specific comparison seam; Stage 4 keeps its exact behavior."""
        self._write(
            kind="agency_comparison",
            data=self._comparison_as_dict(comparison),
        )
        if (
            comparison.status == "nonconforming"
            and comparison.option_ref is not None
        ):
            self.competition.invalidate_candidate(comparison.option_ref)
            self.stage3.control.clear_option_step(comparison.option_ref)
            self.planning.invalidate_current()

    def run_step(self) -> Stage4StepResult:
        capture = self.stage3.open_step()
        comparison = self.stage3.control.compare_capture(capture)
        if comparison is not None:
            self._handle_agency_comparison(
                capture=capture,
                comparison=comparison,
            )

        self._step_need_state = self.value_needs.assess(capture.body)
        self._step_reward = self.value_needs.reward_for(self._step_need_state)

        reflex, reflex_admission, reflex_execution = self.stage3.attempt_reflex(
            checkpoint_owners=self.causal_owners,
            individual_id=self.individual_id,
        )
        if (
            reflex is not None
            and reflex_admission is not None
            and reflex_admission.ok
            and reflex_execution is not None
            and reflex_execution.status in {"applied", "safety_block"}
        ):
            self.stage3._capture = None
            return Stage4StepResult(
                source="reflex",
                execution_status=reflex_execution.status,
                command_primitive=reflex.prepared.command.primitive,
                option_ref=None,
                st_version=(
                    None if self.s_t.current is None else self.s_t.current.version
                ),
                cycles_used=0,
                reflex_triggered=True,
                fallback_used=False,
            )

        active_goal_id = (
            None
            if self.goal_manager.active_goal is None
            else self.goal_manager.active_goal.id
        )
        self.competition.open_deliberation(
            active_goal_id=active_goal_id,
            t_monde=capture.t_monde,
        )

        start_cycle = 1
        for cycle in range(start_cycle, self._config.competition.c_max + 1):
            self._admitted_decision = None
            self._fallback_used_this_cycle = False
            self._safety_block_after_cycle = False
            self._proposal_this_cycle = None
            goal_for_planning = self.goal_manager.active_goal
            st_before_cycle = self.s_t.current

            self.scheduler.run_cycle(
                cycle=cycle,
                hooks=self._phase_hooks(
                    cycle=cycle,
                    capture=capture,
                    goal_for_planning=goal_for_planning,
                    st_before_cycle=st_before_cycle,
                ),
            )
            self.goal_manager.close_cycle_inputs()

            if self._safety_block_after_cycle:
                self.stage3.substrate.safety.enter_safety_block(
                    reason="no_admissible_safe_command",
                )
                self.scheduler.close_step(
                    outcome="blocked",
                    applied_command_count=0,
                    world_advance_count=0,
                )
                self.stage3._capture = None
                return Stage4StepResult(
                    source="fallback",
                    execution_status="safety_block",
                    command_primitive=None,
                    option_ref=None,
                    st_version=(
                        None
                        if self.s_t.current is None
                        else self.s_t.current.version
                    ),
                    cycles_used=cycle,
                    reflex_triggered=reflex is not None,
                    fallback_used=True,
                )

            if self._admitted_decision is None:
                continue

            proposal, prepared, admission = self._admitted_decision
            execution = self._dispatch_decision(
                proposal=proposal,
                prepared=prepared,
                admission=admission,
                cycle=cycle,
                sent_t_monde=capture.t_monde,
            )
            if execution.status == "rolled_back":
                # The cognitive checkpoint restored all causal owners, while
                # the technical journal remained append-only. Continue with
                # the next cycle under the rollback protocol mask.
                continue

            if execution.status == "applied":
                self.competition.close_deliberation(proposal)
            self.stage3._capture = None
            return Stage4StepResult(
                source=(
                    "fallback"
                    if self._fallback_used_this_cycle
                    else "decision"
                ),
                execution_status=execution.status,
                command_primitive=prepared.command.primitive,
                option_ref=proposal.option.id,
                st_version=(
                    None if self.s_t.current is None else self.s_t.current.version
                ),
                cycles_used=cycle,
                reflex_triggered=reflex is not None,
                fallback_used=self._fallback_used_this_cycle,
            )

        raise RuntimeError("Stage 4 deliberation exited without decision or block")
