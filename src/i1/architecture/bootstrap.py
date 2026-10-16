"""Executable bootstrap for I0.

This is intentionally not a cognitive model. It validates the repository's
execution boundary: observation -> Individual -> observable state + action.

Scientific mechanisms should replace or extend this bootstrap only after a
question and experimental protocol justify them.
"""

from __future__ import annotations

from dataclasses import dataclass

from i0.interfaces import Action, Observation, StepResult


@dataclass(slots=True)
class _BootstrapState:
    seed: int = 0
    cycles_completed: int = 0
    observations_seen: int = 0
    last_observation_kind: str | None = None


class BootstrapI0:
    """Deterministic non-cognitive I0 execution scaffold."""

    def __init__(self) -> None:
        self._state = _BootstrapState()

    def reset(self, *, seed: int) -> None:
        self._state = _BootstrapState(seed=seed)

    def step(self, observation: Observation) -> StepResult:
        self._state.cycles_completed += 1
        self._state.observations_seen += 1
        self._state.last_observation_kind = observation.kind

        state = {
            "seed": self._state.seed,
            "cycles_completed": self._state.cycles_completed,
            "observations_seen": self._state.observations_seen,
            "last_observation_kind": self._state.last_observation_kind,
        }

        # The bootstrap must not invent a behavioral policy. A no-op action
        # proves the action boundary while remaining scientifically neutral.
        action = Action(
            kind="noop",
            data={"reason": "bootstrap-runtime-only"},
        )
        return StepResult(action=action, state=state)

    def snapshot(self) -> dict[str, object]:
        """Return a serializable copy of the current bootstrap state."""

        return {
            "seed": self._state.seed,
            "cycles_completed": self._state.cycles_completed,
            "observations_seen": self._state.observations_seen,
            "last_observation_kind": self._state.last_observation_kind,
        }
