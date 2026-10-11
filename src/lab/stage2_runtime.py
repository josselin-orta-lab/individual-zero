"""Integrated scripted Stage-2 world/body/bench runtime.

This runtime uses a scripted agent, not cognition. Its purpose is to close the
tier-0 environment, oracle-isolation and lethal-rollback gates.

Spec: 18, 19, 20.3 Stage 2, INV-02, INV-27-29, INV-33, INV-39, INV-44.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .determinism import deterministic_id
from .injected_scenario import InjectedScenario, ScenarioEvent
from .journal import HashChainedJournal
from .journal_views import (
    AutobiographicalPolicy,
    JournalViews,
)
from .mortal_execution import MortalStatus, MortalWorldBoundary
from .standalone_safety import StandaloneSafetyOwner
from .safety_protocol import (
    LethalHandlingResult,
    LethalSafetyProtocol,
    SafetyProtocolConfig,
)
from .scheduler import Scheduler
from .snapshots import SnapshotManager, SnapshotType
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
    status: str  # applied | dead (opt-in v1.3) | rolled_back | safety_block | masked
    transition: TransitionResult | None
    lethal_handling: LethalHandlingResult | None


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
        autonomous_mortal: bool = False,
    ) -> None:
        self.journal = HashChainedJournal()
        self.views = JournalViews(journal=self.journal)
        self.world = WorldBody(config=config, layout=layout)
        self.scheduler = Scheduler(
            journal=self.journal,
            phase_component_order=phase_component_order,
        )
        self.snapshots = SnapshotManager(journal=self.journal)
        if type(autonomous_mortal) is not bool:
            raise TypeError("autonomous_mortal must be a boolean")
        # No external Oracle/Bench modules are loaded in autonomous mode.
        self._standalone_mortal = autonomous_mortal
        if autonomous_mortal:
            self.evaluation_trace = None
            self.bench = None
            self.safety = StandaloneSafetyOwner(
                config=safety_config,
                scheduler=self.scheduler, journal=self.journal,
            )
        else:
            # Historical evaluated fixtures retain their exact default.
            from .oracle import create_oracle
            from .bench import EvaluationBench
            from .evaluation_trace import EvaluationTrace

            self.evaluation_trace = EvaluationTrace()
            oracle, capability = create_oracle(self.world)
            self.bench = EvaluationBench(
                oracle=oracle, capability=capability,
                trace=self.evaluation_trace,
            )
            self.safety = LethalSafetyProtocol(
                config=safety_config, scheduler=self.scheduler,
                snapshots=self.snapshots, journal=self.journal,
                bench=self.bench,
            )
        self._mortal_boundary: MortalWorldBoundary | None = None
        # Optional external operator control: never a cognitive or Oracle owner.
        self._operator_control = None
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
        if autonomous_mortal:
            self.enable_mortal_world()

    @property
    def causal_owners(self):
        owners = [self.scheduler, self.world, self.safety]
        if self.scenario is not None:
            owners.append(self.scenario)
        if self._operator_control is not None:
            owners.append(self._operator_control)
        return tuple(owners)

    def enable_mortal_world(self) -> None:
        """Opt into irreversible mortality before the first world step.

        Historical v1.2.1 mode stays unchanged until its regression fixtures
        have been migrated. No switching the safety contract midlife.
        """
        if (
            self._mortal_boundary is not None
            or self.scheduler.t_monde != 0
            or self.scheduler.active_attempt is not None
        ):
            raise RuntimeError("mortal runtime must be selected before birth")
        self._mortal_boundary = MortalWorldBoundary(world=self.world)
        self.snapshots.forbid_life_restoration()
        self.world.forbid_historical_restore()

    def protocol_mask_for_control(self, command: Command) -> bool:
        """Legacy rollback masks have no authority over mortal cognition.

        Actual learned vetoes and reflex safety checks stay in ActionControl.
        This adapter does not reveal hidden hazards or oracle knowledge.
        """
        if self._mortal_boundary is not None:
            return False
        return self.safety.is_masked(command)

    @property
    def mortal_status(self) -> MortalStatus | None:
        return (
            None if self._mortal_boundary is None
            else self._mortal_boundary.status
        )

    def attach_operator_control(self, control) -> None:
        """A single operator may attach only before a new mortal world step."""
        if (self._mortal_boundary is None
                or self._mortal_boundary.status is not MortalStatus.ACTIVE
                or self.scheduler.active_attempt is not None
                or self._operator_control is not None
                or getattr(control, "owner_id", None) != "operator_console"):
            raise RuntimeError("operator control requires an active mortal boundary")
        self._operator_control = control

    def open_step(self) -> None:
        if (
            self._mortal_boundary is not None
            and self._mortal_boundary.status is not MortalStatus.ACTIVE
        ):
            raise RuntimeError("dead or halted individual cannot advance")
        if self._operator_control is not None:
            self._operator_control.before_open_step()
        if self._mortal_boundary is not None and self.safety.blocked:
            raise RuntimeError("safety-blocked mortal individual cannot advance")
        # A rejected external input is a stopped branch, not an omitted
        # event to be silently skipped in a later world step.
        if self.scenario is not None and self.scenario.halted:
            raise RuntimeError("cannot advance a rejected external scenario")
        try:
            attempt = self.scheduler.open_step()
        except Exception:
            # Scheduler increments its clock before publishing step_opened.
            # A failed publication must never leave a dispatchable mortal
            # attempt lacking its opening event; do not rewind the clock.
            if self._mortal_boundary is not None:
                self._mortal_boundary.halt(failed_step=self.scheduler.t_monde)
            raise
        if self.scenario is not None:
            try:
                if self._mortal_boundary is None:
                    self.scenario.apply_for_step(
                        t_monde=attempt.t_monde, world=self.world,
                    )
                else:
                    self.scenario.apply_for_step_irreversible(
                        t_monde=attempt.t_monde, world=self.world,
                    )
            except Exception:
                if self._mortal_boundary is not None:
                    # A failed publication may already have changed the real
                    # world. Halt without restoring or retrying anything.
                    self._mortal_boundary.halt(failed_step=attempt.t_monde)
                # No individual command or cognitive cycle was dispatched.
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

    def _send_mortal_command(
        self,
        command: Command,
        *,
        source: str,
        event_emitter: str | None,
        autobiographical_policy: AutobiographicalPolicy | None,
        extra_autobiographical_event_refs: tuple[str, ...],
    ) -> CommandExecution:
        """Physically execute once, with no lethal snapshot, rewind or mask."""
        boundary = self._mortal_boundary
        attempt = self.scheduler.active_attempt
        if boundary is None or attempt is None:
            raise RuntimeError("mortal command requires active world step")
        if boundary.status is not MortalStatus.ACTIVE:
            raise RuntimeError("dead or halted individual cannot act")
        if self.safety.blocked:
            raise RuntimeError("safety-blocked mortal individual cannot act")
        try:
            command_ref = self._write_command_event(
                command=command, emitter=event_emitter or source,
            )
            physical = boundary.execute(command, t_monde=attempt.t_monde)
            physical_ref = self._write_transition_event(physical.transition)
            if physical.status == "dead":
                # I0's own exhaustive causal journal records terminal truth.
                # Neither Oracle nor Bench owns this occurrence.
                self.journal.append(
                    event_id=deterministic_id(
                        "journal-event-v1", "mortal-world",
                        attempt.t_monde, attempt.attempt_ref,
                        command_digest(command), "death-confirmed",
                    ),
                    causal_event={
                        "emitter": "world_and_body",
                        "kind": "individual_death_confirmed",
                        "t_monde": attempt.t_monde,
                        "attempt_ref": attempt.attempt_ref,
                        "command_hash": command_digest(command),
                        "reasons": list(physical.transition.lethal_reasons),
                        "position_after": physical.transition.position_after.as_dict(),
                        "body_after": physical.transition.body_after.as_dict(),
                    },
                )
                self.scheduler.close_step(
                    outcome="dead", applied_command_count=1,
                    world_advance_count=1,
                )
                # Scientific metrics are strictly optional and non-blocking.
                if self.bench is not None:
                    try:
                        self.bench.count_lethal_transition(data={
                            "t_monde": physical.transition.t_monde,
                            "command_hash": command_digest(command),
                            "reasons": list(physical.transition.lethal_reasons),
                        })
                    except Exception:
                        pass
                return CommandExecution(
                    status="dead", transition=physical.transition,
                    lethal_handling=None,
                )
            self.views.commit_autobiographical(
                t_monde=attempt.t_monde,
                attempt_ref=attempt.attempt_ref,
                event_refs=(tuple(extra_autobiographical_event_refs)
                            + (command_ref, physical_ref)),
                policy=(
                    STAGE2_AUTOBIOGRAPHICAL_POLICY
                    if autobiographical_policy is None
                    else autobiographical_policy
                ),
            )
            self.scheduler.close_step(
                outcome="normal", applied_command_count=1,
                world_advance_count=1,
            )
            return CommandExecution(
                status="applied", transition=physical.transition,
                lethal_handling=None,
            )
        except Exception:
            # A failed receipt after physical execution is uncertain: never
            # replay the command or restore the world as compensation.
            boundary.halt(failed_step=attempt.t_monde)
            raise

    def send_admitted_command(
        self,
        command: Command,
        *,
        source: str,
        event_emitter: str | None = None,
        checkpoint_owners=None,
        individual_id: str = "stage2-scripted",
        checkpoint_cycle: int = 0,
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
        if self._mortal_boundary is not None:
            return self._send_mortal_command(
                command,
                source=source,
                event_emitter=event_emitter,
                autobiographical_policy=autobiographical_policy,
                extra_autobiographical_event_refs=extra_autobiographical_event_refs,
            )

        if self.safety.blocked:
            raise RuntimeError("branch is in safety block")

        if self.safety.is_masked(command):
            self.journal.append(
                event_id=deterministic_id(
                    "journal-event-v1",
                    "safety-protocol",
                    attempt.t_monde,
                    attempt.attempt_ref,
                    command_digest(command),
                    "masked",
                ),
                causal_event={
                    "emitter": "scheduler.safety_protocol",
                    "kind": "protocol_mask_rejected_command",
                    "t_monde": attempt.t_monde,
                    "attempt_ref": attempt.attempt_ref,
                    "command_hash": command_digest(command),
                },
            )
            return CommandExecution(
                status="masked",
                transition=None,
                lethal_handling=None,
            )

        checkpoint = self.snapshots.take(
            snapshot_type=SnapshotType.LETHAL_CHECKPOINT,
            individual_id=individual_id,
            t_monde=attempt.t_monde,
            cycle=checkpoint_cycle,
            attempt_ref=attempt.attempt_ref,
            owners=(
                self.causal_owners
                if checkpoint_owners is None
                else tuple(checkpoint_owners)
            ),
            versions={
                "world_physics": self.world.config.version,
                "safety_protocol": self.safety.export_causal_state()["config_version"],
            },
            context={
                "command_source": source,
                "command_hash": command_digest(command),
                "mask": self.safety.export_causal_state()["masked_command_hashes"],
                "R_letal_consecutif": self.safety.consecutive_lethal,
            },
        )

        command_event = self._write_command_event(
            command=command,
            emitter=event_emitter or source,
        )
        transition = self.world.apply(command, t_monde=attempt.t_monde)

        if transition.lethal:
            handling = self.safety.handle_lethal(
                checkpoint_id=checkpoint.id,
                command=command,
                transition=transition,
                restore_owners=(
                    self.causal_owners
                    if checkpoint_owners is None
                    else tuple(checkpoint_owners)
                ),
            )
            if handling.blocked:
                self.scheduler.close_step(
                    outcome="blocked",
                    applied_command_count=0,
                    world_advance_count=0,
                )
                return CommandExecution(
                    status="safety_block",
                    transition=transition,
                    lethal_handling=handling,
                )
            return CommandExecution(
                status="rolled_back",
                transition=transition,
                lethal_handling=handling,
            )

        transition_event = self._write_transition_event(transition)
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
        self.safety.complete_nonlethal_step()
        self.scheduler.close_step(
            outcome="normal",
            applied_command_count=1,
            world_advance_count=1,
        )
        return CommandExecution(
            status="applied",
            transition=transition,
            lethal_handling=None,
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
