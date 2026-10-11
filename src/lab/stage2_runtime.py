"""Integrated scripted Stage-2 world/body/bench runtime.

This runtime uses a scripted agent, not cognition. Its purpose is to close the
tier-0 environment, oracle-isolation and terminal-mortality gates.

Spec: 18, 19, 20.3 Stage 2, INV-02, INV-27-29, INV-33, INV-39, INV-44.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .bench import EvaluationBench
from .determinism import deterministic_id
from .injected_scenario import InjectedScenario, ScenarioEvent
from .journal import HashChainedJournal
from .journal_views import (
    AutobiographicalPolicy,
    EvaluationTrace,
    JournalViews,
)
from .oracle import create_oracle
from .safety_protocol import MortalityProtocol, SafetyProtocolConfig
from .scheduler import Scheduler
from .snapshots import SnapshotManager
from .world import Command, TransitionResult, WorldBody, WorldLayout, WorldPhysicsConfig, command_digest


STAGE2_AUTOBIOGRAPHICAL_POLICY = AutobiographicalPolicy(
    version="stage2-autobio-v1",
    allowed_fields_by_kind={
        "command_experienced": ("t_monde", "primitive", "parameters"),
        "world_transition_experienced": (
            "t_monde",
            "position_after",
            "body_after",
            "effects",
        ),
    },
)


@dataclass(frozen=True, slots=True)
class CommandExecution:
    status: str  # applied | dead | safety_block
    transition: TransitionResult | None


class ScriptedStage2Runtime:
    """Environment runtime with scripted commands and no cognitive module."""

    def __init__(
        self,
        *,
        config: WorldPhysicsConfig,
        layout: WorldLayout,
        phase_component_order: Mapping[int, tuple[str, ...]],
        safety_config: SafetyProtocolConfig,
        scenario_id: str | None = None,
        scenario_version: str | None = None,
        scenario_events: tuple[ScenarioEvent, ...] = (),
    ) -> None:
        self.journal = HashChainedJournal()
        self.views = JournalViews(journal=self.journal)
        self.evaluation_trace = EvaluationTrace()
        self.world = WorldBody(config=config, layout=layout)
        self.scheduler = Scheduler(
            journal=self.journal,
            phase_component_order=phase_component_order,
        )
        self.snapshots = SnapshotManager(journal=self.journal)
        oracle, capability = create_oracle(self.world)
        self.bench = EvaluationBench(
            oracle=oracle,
            capability=capability,
            trace=self.evaluation_trace,
        )
        self.safety = MortalityProtocol(
            config=safety_config,
            scheduler=self.scheduler,
            journal=self.journal,
            bench=self.bench,
        )
        if scenario_id is None and (scenario_version is not None or scenario_events):
            raise ValueError("scenario_id is required when scenario data is supplied")
        if scenario_id is not None and scenario_version is None:
            raise ValueError("scenario_version is required with scenario_id")
        self.scenario = (
            None
            if scenario_id is None
            else InjectedScenario(
                scenario_id=scenario_id,
                version=str(scenario_version),
                events=scenario_events,
                journal=self.journal,
            )
        )

    @property
    def causal_owners(self):
        owners = [self.scheduler, self.world, self.safety]
        if self.scenario is not None:
            owners.append(self.scenario)
        return tuple(owners)

    def open_step(self) -> None:
        if self.safety.dead:
            raise RuntimeError("cannot advance a dead individual")
        if self.safety.blocked:
            raise RuntimeError("cannot advance a blocked individual")
        # A rejected external input is a stopped branch, not an omitted
        # event to be silently skipped in a later world step.
        if self.scenario is not None and self.scenario.halted:
            raise RuntimeError("cannot advance a rejected external scenario")
        attempt = self.scheduler.open_step()
        if self.scenario is not None:
            try:
                self.scenario.apply_for_step(
                    t_monde=attempt.t_monde,
                    world=self.world,
                )
            except Exception:
                # Input reception/rejection and any compensating WorldBody
                # rollback have already been technically journaled by the
                # scenario. No perception, command or world transition ran.
                self.scheduler.close_step(
                    outcome="external_stop",
                    applied_command_count=0,
                    world_advance_count=0,
                )
                raise

    def _write_command_event(self, *, command: Command, emitter: str) -> str:
        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("command requires active step")
        event_id = deterministic_id(
            "journal-event-v1",
            emitter,
            attempt.t_monde,
            attempt.attempt_ref,
            command_digest(command),
            "send",
        )
        self.journal.append(
            event_id=event_id,
            causal_event={
                "emitter": emitter,
                "kind": "command_experienced",
                "t_monde": attempt.t_monde,
                "attempt_ref": attempt.attempt_ref,
                "primitive": command.primitive,
                "parameters": dict(command.parameters),
                "command_hash": command_digest(command),
            },
        )
        return event_id

    def _write_transition_event(self, transition: TransitionResult) -> str:
        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("transition requires active step")
        event_id = deterministic_id(
            "journal-event-v1",
            "world",
            attempt.t_monde,
            attempt.attempt_ref,
            command_digest(transition.command),
            "transition",
        )
        self.journal.append(
            event_id=event_id,
            causal_event={
                "emitter": "world_and_body",
                "kind": "world_transition_experienced",
                "t_monde": attempt.t_monde,
                "attempt_ref": attempt.attempt_ref,
                "position_after": transition.position_after.as_dict(),
                "body_after": transition.body_after.as_dict(),
                "effects": dict(transition.effects),
            },
        )
        return event_id

    def send_admitted_command(
        self,
        command: Command,
        *,
        source: str,
        event_emitter: str | None = None,
        autobiographical_policy: AutobiographicalPolicy | None = None,
        extra_autobiographical_event_refs: tuple[str, ...] = (),
    ) -> CommandExecution:
        """Execute a command already admitted by the active control path.

        Stage 2's scripted agent calls this directly as an allowed stage stub.
        Stage 3+ must invoke it only through Action Control's dispatch callback.
        """

        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("open_step must be called before command send")
        if self.safety.dead:
            raise RuntimeError("dead individual cannot issue commands")
        if self.safety.blocked:
            raise RuntimeError("branch is in safety block")

        command_event = self._write_command_event(
            command=command,
            emitter=event_emitter or source,
        )
        transition = self.world.apply(command, t_monde=attempt.t_monde)

        transition_event = self._write_transition_event(transition)
        if transition.lethal:
            self.safety.confirm_death(command=command, transition=transition)
            self.scheduler.close_step(
                outcome="dead",
                applied_command_count=1,
                world_advance_count=1,
            )
            return CommandExecution(status="dead", transition=transition)

        active = self.scheduler.active_attempt
        if active is None:
            raise RuntimeError("normal transition lost active attempt")

        self.views.commit_autobiographical(
            t_monde=active.t_monde,
            attempt_ref=active.attempt_ref,
            event_refs=(
                tuple(extra_autobiographical_event_refs)
                + (command_event, transition_event)
            ),
            policy=(
                STAGE2_AUTOBIOGRAPHICAL_POLICY
                if autobiographical_policy is None
                else autobiographical_policy
            ),
        )
        self.scheduler.close_step(
            outcome="normal",
            applied_command_count=1,
            world_advance_count=1,
        )
        return CommandExecution(
            status="applied",
            transition=transition,
        )

    def execute(self, command: Command) -> CommandExecution:
        """Stage-2 scripted-agent compatibility wrapper."""

        return self.send_admitted_command(
            command,
            source="scripted_agent",
            event_emitter="stage2-scripted-agent",
        )

    def autobiographical_view(self) -> tuple[dict[str, object], ...]:
        return self.views.autobiographical(
            policies={
                STAGE2_AUTOBIOGRAPHICAL_POLICY.version:
                    STAGE2_AUTOBIOGRAPHICAL_POLICY
            }
        )

    def causal_fingerprint(self) -> dict[str, object]:
        state = {
            owner.owner_id: owner.export_causal_state()
            for owner in self.causal_owners
        }
        return state
