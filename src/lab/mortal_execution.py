"""One-way physical death boundary for the future I0 v1.3 runtime.

This is a standalone migration seam, NOT yet wired to Stage2/Stage10.
WorldBody remains the sole physics authority; no checkpoint, protocol mask,
rollback, technical event archive or oracle read is introduced here.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .world import (
    BodyState, Command, Position, TransitionResult, WorldBody,
    command_digest, validate_command,
)


class MortalStatus(str, Enum):
    ACTIVE = "active"
    DEAD = "dead"
    TECHNICAL_HALT = "technical_halt"
    EXPERIMENT_STOPPED = "experiment_stopped"


@dataclass(frozen=True, slots=True)
class TerminalDeath:
    """External terminal fact, not a cognitive experience or reward."""

    world_step: int
    command_hash: str
    reasons: tuple[str, ...]
    position: Position
    body: BodyState


@dataclass(frozen=True, slots=True)
class MortalStepResult:
    """The actual, once-applied physical transition."""

    status: str  # applied | dead
    transition: TransitionResult


class MortalWorldBoundary:
    """External exactly-once world-step execution with irreversible mortality.

    The caller remains responsible for Action Control admission, scheduling,
    ordinary lived-event publication and nonlethal learning. This boundary
    owns *only* the terminal lifetime gate and the physical dispatch itself.

    It does not expose a restore/revive method. On a WorldBody exception the
    world may already have mutated, so it fails closed to technical_halt
    without trying to restore or compensate prior effects.
    """

    def __init__(self, *, world: WorldBody) -> None:
        if not isinstance(world, WorldBody):
            raise TypeError("mortality boundary requires the real WorldBody")
        # A snapshot owner might otherwise call WorldBody.restore_causal_state
        # directly, bypassing the SnapshotManager's ban on life restoration.
        world.forbid_historical_restore()
        self._world = world
        self._world_dispatch_key = world._install_mortal_dispatch_authority()
        self._status = MortalStatus.ACTIVE
        self._last_world_step = 0
        self._death: TerminalDeath | None = None
        self._failed_step: int | None = None

    @property
    def status(self) -> MortalStatus:
        return self._status

    @property
    def last_world_step(self) -> int:
        return self._last_world_step

    @property
    def terminal_death(self) -> TerminalDeath | None:
        return self._death

    @property
    def failed_step(self) -> int | None:
        return self._failed_step

    def halt(self, *, failed_step: int | None = None) -> None:
        """Permanently fail closed after an uncertain external commit.

        A confirmed death stays a death; this function never restores state.
        """
        if self._status is not MortalStatus.ACTIVE:
            return
        self._world.freeze_terminal_state()
        self._status = MortalStatus.TECHNICAL_HALT
        if failed_step is not None:
            self._failed_step = failed_step

    def stop_experiment(self) -> None:
        """Externally stop this test identity, permanently, without death.

        A stopped simulation never becomes the same individual's restarted
        life; it may be inspected only as an immutable completed trajectory.
        """
        if self._status is not MortalStatus.ACTIVE:
            raise RuntimeError("only a living individual may be stopped by an operator")
        self._world.freeze_terminal_state()
        self._status = MortalStatus.EXPERIMENT_STOPPED

    def acknowledge_nonphysical_step(self, *, t_monde: int) -> None:
        """Account for one verified, closed blocked attempt with NO world effect.

        The external Scheduler/Operator must attest a unique, hash-chained
        `step_closed` with zero command and world advances before invoking.
        No physics, clock rewind, WorldBody command or cognitive result is
        synthesized here. This makes a diagnostic nonlethal block resumable
        at the next original Scheduler time without rewriting prior steps.
        """
        if (self._status is not MortalStatus.ACTIVE
                or type(t_monde) is not int
                or t_monde != self._last_world_step + 1):
            raise RuntimeError("nonphysical step acknowledgement is not consecutive")
        self._last_world_step = t_monde

    def execute(self, command: Command, *, t_monde: int) -> MortalStepResult:
        if self._status is not MortalStatus.ACTIVE:
            raise RuntimeError("dead or halted individual cannot execute")
        if type(t_monde) is not int or t_monde != self._last_world_step + 1:
            raise ValueError("physical world steps must be consecutive integers")
        # Refuse malformed commands before touching physics. This does not
        # classify hidden world hazards or invent an oracle-informed veto.
        validate_command(command)
        try:
            # No direct WorldBody.apply is permitted on a mortal world.
            # The physical authority is scoped to this one boundary call.
            with self._world._admit_mortal_dispatch(self._world_dispatch_key):
                result = self._world.apply(command, t_monde=t_monde)
            if (
                not isinstance(result, TransitionResult)
                or result.t_monde != t_monde
                or result.command != command
            ):
                raise RuntimeError("physical world produced an invalid receipt")
        except Exception:
            # No world state is restored, even if its mutation was partial.
            # Caller must not continue from uncertain state or mutate it
            # through another WorldBody API entry point.
            self._world.freeze_terminal_state()
            self._failed_step = t_monde
            self._status = MortalStatus.TECHNICAL_HALT
            raise

        self._last_world_step = t_monde
        if not result.lethal:
            return MortalStepResult(status="applied", transition=result)

        self._death = TerminalDeath(
            world_step=t_monde,
            command_hash=command_digest(command),
            reasons=tuple(result.lethal_reasons),
            position=result.position_after,
            body=result.body_after,
        )
        self._world.freeze_terminal_state()
        self._status = MortalStatus.DEAD
        return MortalStepResult(status="dead", transition=result)
