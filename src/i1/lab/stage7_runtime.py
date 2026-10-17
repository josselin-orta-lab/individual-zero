"""Integrated Stage-7 memory runtime over completed Stage 6.

Memory reads only the DC-09 autobiographical projection. Stage 7 extends the
allowlist for cognitively accessible goal/S_t/comparator/memory events while
keeping technical access, rollback, hashes, budgets and oracle data excluded.

Spec: 10.1-10.5, 17.5, 20.3 Stage 7, P-34, DC-09.
"""

from __future__ import annotations

from .injected_scenario import ScenarioEvent

from dataclasses import dataclass
from typing import Mapping

from i0.equipment import EquipmentModel
from i0.modules import (
    EpisodicMemory,
    MemoryConfig,
    StaticSafetyFacts,
)
from i0.requests import Request, Response

from .journal_views import AutobiographicalPolicy
from .request_registry import RequestRegistry, RequestRegistryConfig
from .safety_protocol import SafetyProtocolConfig
from .stage2_runtime import (
    CommandExecution,
    STAGE2_AUTOBIOGRAPHICAL_POLICY,
)
from .stage6_runtime import Stage6Config, Stage6Runtime
from .world import WorldLayout, WorldPhysicsConfig


STAGE7_AUTOBIOGRAPHICAL_POLICY = AutobiographicalPolicy(
    version="stage7-autobio-v1",
    allowed_fields_by_kind={
        "command_experienced": ("t_monde", "primitive", "parameters"),
        "world_transition_experienced": (
            "t_monde",
            "position_after",
            "body_after",
            "effects",
        ),
        "active_goal_changed": ("t_monde", "cycle", "data"),
        "s_t_published": ("t_monde", "cycle", "data"),
        "agency_comparison": ("t_monde", "data"),
        "episode_closed": ("t_monde", "cycle", "data"),
        "memory_recall_proposed": ("t_monde", "cycle", "data"),
        "intention_created": ("t_monde", "cycle", "data"),
        "intention_triggered": ("t_monde", "cycle", "data"),
    },
)


_STAGE7_AUTOBIO_KINDS = frozenset(
    set(STAGE7_AUTOBIOGRAPHICAL_POLICY.allowed_fields_by_kind)
    - {"command_experienced", "world_transition_experienced"}
)


@dataclass(frozen=True, slots=True)
class Stage7Config:
    version: str
    stage6: Stage6Config
    memory: MemoryConfig

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage 7 config version must not be empty")
        self.stage6.validate()
        self.memory.validate()


class Stage7Runtime(Stage6Runtime):
    """Stage 6 cognition plus autobiographical episodic memory."""

    individual_id = "i0-stage7"

    def __init__(
        self,
        *,
        world_config: WorldPhysicsConfig,
        layout: WorldLayout,
        safety_config: SafetyProtocolConfig,
        safety_facts: StaticSafetyFacts,
        protected_integrity_threshold: float,
        config: Stage7Config,
        equipment: EquipmentModel,
        scenario_id: str | None = None,
        scenario_version: str | None = None,
        scenario_events: tuple[ScenarioEvent, ...] = (),
        autonomous_mortal: bool = False,
    ) -> None:
        config.validate()
        self._stage7_config = config
        self.memory = EpisodicMemory(config.memory)
        self.request_registry = RequestRegistry(
            RequestRegistryConfig(
                version="stage7-request-registry-v1",
                recency_window_steps=(
                    config.stage6.stage4.gatekeeper.recency_window_steps
                ),
            )
        )
        self._stage7_autobio_refs: list[tuple[str, str]] = []

        super().__init__(
            world_config=world_config,
            layout=layout,
            safety_config=safety_config,
            safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            scenario_id=scenario_id,
            scenario_version=scenario_version,
            scenario_events=scenario_events,
            autonomous_mortal=autonomous_mortal,
            config=config.stage6,
            equipment=equipment,
        )

    @property
    def causal_owners(self):
        owners = list(super().causal_owners)
        if all(owner.owner_id != self.memory.owner_id for owner in owners):
            owners.append(self.memory)
        if all(
            owner.owner_id != self.request_registry.owner_id
            for owner in owners
        ):
            owners.append(self.request_registry)
        return tuple(owners)

    def _write(
        self,
        *,
        kind: str,
        data: Mapping[str, object],
        cycle: int | None = None,
    ) -> str:
        event_id = super()._write(kind=kind, data=data, cycle=cycle)
        attempt = self.scheduler.active_attempt
        if attempt is not None and kind in _STAGE7_AUTOBIO_KINDS:
            self._stage7_autobio_refs.append(
                (attempt.attempt_ref, event_id)
            )
        return event_id

    def _request_statuses_for_st(self) -> Mapping[str, str]:
        return {
            request_ref: (
                status.response_status
                if status.state == "closed"
                and status.response_status is not None
                else status.state
            )
            for request_ref, status
            in sorted(self.request_registry.statuses.items())
        }

    def request_memory(
        self,
        request: Request,
        *,
        cycle: int,
    ) -> Response | None:
        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("memory request requires an active waking step")
        self.request_registry.register(
            request,
            t_monde=attempt.t_monde,
        )
        self._write(
            kind="request_registered",
            cycle=cycle,
            data={
                "request_ref": request.id,
                "emitter": request.emitter,
                "recipient": request.recipient,
                "question": request.question,
                "depth": request.depth,
                "deadline_value": request.deadline_value,
                "deadline_unit": request.deadline_unit,
            },
        )
        response = self.memory.respond(
            request,
            st=self.s_t.current,
            t_monde=attempt.t_monde,
        )
        delivered = self.request_registry.deliver(
            response,
            t_monde=attempt.t_monde,
        )
        self._write(
            kind="request_response",
            cycle=cycle,
            data={
                "request_ref": request.id,
                "status": (
                    "cancelled_before_delivery"
                    if delivered is None
                    else delivered.status
                ),
                "shareable": (
                    False if delivered is None else delivered.shareable
                ),
            },
        )
        return delivered

    def _autobiographical_events(self, *, cycle: int):
        events = self.stage3.substrate.views.autobiographical(
            policies={
                STAGE2_AUTOBIOGRAPHICAL_POLICY.version:
                    STAGE2_AUTOBIOGRAPHICAL_POLICY,
                STAGE7_AUTOBIOGRAPHICAL_POLICY.version:
                    STAGE7_AUTOBIOGRAPHICAL_POLICY,
            }
        )
        # Q14: access is technically logged, but the access record is not part
        # of the autobiographical projection and therefore cannot become a
        # memory merely because Memory read its source.
        self._write(
            kind="memory_autobiographical_access",
            cycle=cycle,
            data={
                "reader": "memory",
                "mode": "read_only_projection",
                "event_count": len(events),
                "policy_versions": [
                    STAGE2_AUTOBIOGRAPHICAL_POLICY.version,
                    STAGE7_AUTOBIOGRAPHICAL_POLICY.version,
                ],
            },
        )
        return events

    def _phase_hooks(
        self,
        *,
        cycle: int,
        capture,
        goal_for_planning,
        st_before_cycle,
    ):
        hooks = super()._phase_hooks(
            cycle=cycle,
            capture=capture,
            goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )

        def memory_hook(_ctx) -> None:
            autobiography = self._autobiographical_events(cycle=cycle)
            goal = self.goal_manager.active_goal
            closed = self.memory.ingest_autobiographical(
                autobiography,
                current_t_monde=capture.t_monde,
                current_goal_ref=None if goal is None else goal.id,
                current_reward=self._step_reward,
            )
            for episode in closed:
                self._write(
                    kind="episode_closed",
                    cycle=cycle,
                    data=episode.as_dict(),
                )

            for trigger in self.memory.check_intentions(
                st=st_before_cycle,
                t_monde=capture.t_monde,
                cycle=cycle,
                pressure_fn=self.goal_manager.prospective_pressure,
            ):
                if not trigger.triggered:
                    continue
                if trigger.contribution is None or trigger.goal_proposal is None:
                    raise RuntimeError("triggered intention missing outputs")
                self._publish_contribution(trigger.contribution)
                self.goal_manager.defer_proposals(
                    (trigger.goal_proposal,)
                )
                self._write(
                    kind="intention_triggered",
                    cycle=cycle,
                    data={
                        "intention_ref": trigger.intention_ref,
                        "contribution_ref": trigger.contribution.id,
                        "goal_proposal_ref": trigger.goal_proposal.id,
                        "current_pressure": (
                            trigger.goal_proposal.current_pressure
                        ),
                    },
                )

            contribution = self.memory.spontaneous_contribution(
                st=st_before_cycle,
                t_monde=capture.t_monde,
                cycle=cycle,
            )
            if contribution is not None:
                self._publish_contribution(contribution)
                self._write(
                    kind="memory_recall_proposed",
                    cycle=cycle,
                    data={
                        "episode_ref": contribution.payload["episode_ref"],
                        "subject_ref": contribution.subject_ref,
                        "contribution_ref": contribution.id,
                    },
                )

        hooks[1]["memory"] = memory_hook
        return hooks

    def _require_active_mortal_causal_step(self) -> None:
        """No out-of-step or terminal cognitive writes in an autonomous life."""
        substrate = self.stage3.substrate
        status = substrate.mortal_status
        if status is None:
            # Historical nonmortal reference fixtures retain their API.
            return
        if status.value != "active" or getattr(substrate.safety, "blocked", False):
            raise RuntimeError("terminal or safety-blocked mortal cognitive mutation")
        if self.scheduler.active_attempt is None:
            raise RuntimeError("mortal cognitive mutation requires a live world step")

    def create_intention(self, intention) -> None:
        self._require_active_mortal_causal_step()
        self.memory.create_intention(intention)
        attempt = self.scheduler.active_attempt
        if attempt is not None:
            cycle = self.compute_budget.cycle
            self._write(
                kind="intention_created",
                cycle=cycle,
                data={
                    "intention_ref": intention.id,
                    "goal_type": intention.goal_type,
                    "target": intention.target,
                    "trigger_type": intention.trigger_type,
                    "deadline_step": intention.deadline_step,
                    "base_pressure": intention.base_pressure,
                    "wake_authorized": intention.wake_authorized,
                },
            )

    @property
    def wake_deadline_index(self) -> Mapping[str, int]:
        return self.memory.wake_deadline_index

    def _current_autobiographical_refs(self) -> tuple[str, ...]:
        attempt = self.scheduler.active_attempt
        if attempt is None:
            return ()
        return tuple(
            event_ref
            for attempt_ref, event_ref in self._stage7_autobio_refs
            if attempt_ref == attempt.attempt_ref
        )

    def _dispatch_decision(
        self,
        *,
        proposal,
        prepared,
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
                autobiographical_policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
                extra_autobiographical_event_refs=(
                    self._current_autobiographical_refs()
                ),
            ),
        )
        if not isinstance(execution, CommandExecution):
            raise TypeError("unexpected Stage 7 execution result")
        if execution.status == "applied":
            self.stage3.control.mark_cognitive_step_applied(proposal)
            self.stage3.control.record_sent_prediction(
                prepared=prepared,
                t_monde=sent_t_monde,
            )
        return execution

    def run_step(self):
        self._stage7_autobio_refs = []
        return super().run_step()
