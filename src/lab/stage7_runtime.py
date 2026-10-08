"""Integrated Stage-7 memory runtime over completed Stage 6.

Memory reads only the DC-09 autobiographical projection. Stage 7 extends the
allowlist for cognitively accessible goal/S_t/comparator/memory events while
keeping technical access, rollback, hashes, budgets and oracle data excluded.

Spec: 10.1-10.5, 17.5, 20.3 Stage 7, P-34, DC-09.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.equipment import EquipmentModel
from i0.modules import (
    EpisodicMemory,
    MemoryConfig,
    StaticSafetyFacts,
)

from .journal_views import AutobiographicalPolicy
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
    },
)


_STAGE7_AUTOBIO_KINDS = frozenset(
    STAGE7_AUTOBIOGRAPHICAL_POLICY.allowed_fields_by_kind
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
    ) -> None:
        config.validate()
        self._stage7_config = config
        self.memory = EpisodicMemory(config.memory)
        self._stage7_autobio_refs: list[tuple[str, str]] = []

        super().__init__(
            world_config=world_config,
            layout=layout,
            safety_config=safety_config,
            safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            config=config.stage6,
            equipment=equipment,
        )

    @property
    def causal_owners(self):
        owners = list(super().causal_owners)
        if all(owner.owner_id != self.memory.owner_id for owner in owners):
            owners.append(self.memory)
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

            contribution = self.memory.spontaneous_contribution(
                st=st_before_cycle,
                t_monde=capture.t_monde,
                cycle=cycle,
            )
            if contribution is None:
                return
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
