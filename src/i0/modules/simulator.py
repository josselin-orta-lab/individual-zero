"""Stage-6 deterministic simulation service.

The simulator consumes only an explicit accessible SimulationState and a frozen
EquipmentModel. It does not read world, oracle, temperament, values, goals or
competition state directly.

Spec: 8.4, 12.2-12.4, DC-01, 20.3 Stage 6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .causal_corrections import (
    EstablishedCorrectionSource, CausalCorrectionConflict,
    correct_equipment_prediction,
)

from i0.equipment import (
    EquipmentModel,
    EquipmentPrediction,
    SimulationNeighbor,
    SimulationState,
)
from i0.interfaces import PrimitiveCommand

from .perception import PerceptualCapture


@dataclass(frozen=True, slots=True)
class SimulatorConfig:
    version: str
    r_max: int
    h_max: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("simulator config version must not be empty")
        if self.r_max < 1 or self.h_max < 1:
            raise ValueError("R_max and H_max must be >= 1")


@dataclass(frozen=True, slots=True)
class SimulationRollout:
    predictions: tuple[EquipmentPrediction, ...]
    horizon_reached: int
    terminal: bool


@dataclass(frozen=True, slots=True)
class SimulationResult:
    status: str  # complete | unavailable
    equipment_version: str
    requested_rollouts: int
    effective_rollouts: int
    requested_horizon: int
    completed_rollouts: tuple[SimulationRollout, ...]
    partial_rollout: SimulationRollout | None
    reason: str | None

    @property
    def complete(self) -> bool:
        return self.status == "complete"


def state_from_capture(
    *,
    capture: PerceptualCapture,
    is_night: bool,
) -> SimulationState:
    shelters_here = any(
        entity.entity_type == "shelter"
        and entity.x == capture.x
        and entity.y == capture.y
        for entity in capture.visible_entities
    )
    state = SimulationState(
        schema_version="stage6-simulation-state-v1",
        x=capture.x,
        y=capture.y,
        body=dict(capture.body),
        inventory=dict(capture.inventory),
        current_water_source=capture.current_water_source,
        current_resources=tuple(capture.current_resources),
        adjacent=tuple(
            SimulationNeighbor(
                direction=cell.direction,
                x=cell.x,
                y=cell.y,
                passable=cell.passable,
                water_source=cell.water_source,
                resources=tuple(cell.resources),
                creature=cell.creature,
            )
            for cell in capture.adjacent
        ),
        known_shelter_here=shelters_here,
        is_night=is_night,
    )
    state.validate()
    return state


class Simulator:
    """Budgeted rollout service over immutable equipment."""

    def __init__(
        self,
        *,
        config: SimulatorConfig,
        equipment: EquipmentModel,
        corrections: EstablishedCorrectionSource | None = None,
    ) -> None:
        config.validate()
        self._config = config
        self._equipment = equipment
        self._corrections = corrections

    @property
    def equipment_version(self) -> str:
        return self._equipment.version

    def rollout(
        self,
        *,
        initial_state: SimulationState,
        commands: Sequence[PrimitiveCommand],
        r_eff: int,
        h_eff: int,
    ) -> SimulationResult:
        initial_state.validate()
        if r_eff < 1 or r_eff > self._config.r_max:
            raise ValueError("R_eff outside configured bounds")
        if h_eff < 1 or h_eff > self._config.h_max:
            raise ValueError("H_eff outside configured bounds")
        if not commands:
            raise ValueError("simulation requires at least one command")

        # The current reference equipment is deterministic. S-09.2 forbids
        # repeating an identical rollout; R_eff is therefore announced and
        # logged while only one unique trajectory is computed.
        predictions: list[EquipmentPrediction] = []
        state = initial_state
        terminal = False

        horizon_target = min(h_eff, len(commands))
        for index in range(horizon_target):
            command = commands[index]
            try:
                prediction = self._equipment.predict(
                    state=state,
                    command=command,
                )
            except LookupError:
                partial = SimulationRollout(
                    predictions=tuple(predictions),
                    horizon_reached=len(predictions),
                    terminal=terminal,
                )
                return SimulationResult(
                    status="unavailable",
                    equipment_version=self._equipment.version,
                    requested_rollouts=r_eff,
                    effective_rollouts=1,
                    requested_horizon=h_eff,
                    completed_rollouts=(),
                    partial_rollout=partial,
                    reason="equipment_input_unseen",
                )

            if self._corrections is not None:
                try:
                    prediction, _ = correct_equipment_prediction(
                        source=self._corrections,
                        command=command,
                        state=state,
                        prediction=prediction,
                    )
                except CausalCorrectionConflict:
                    partial = SimulationRollout(
                        predictions=tuple(predictions),
                        horizon_reached=len(predictions),
                        terminal=terminal,
                    )
                    return SimulationResult(
                        status="unavailable",
                        equipment_version=self._equipment.version,
                        requested_rollouts=r_eff,
                        effective_rollouts=1,
                        requested_horizon=h_eff,
                        completed_rollouts=(),
                        partial_rollout=partial,
                        reason="unresolved_causal_correction_conflict",
                    )

            predictions.append(prediction)
            state = prediction.next_state
            terminal = prediction.terminal
            if terminal:
                break

        rollout = SimulationRollout(
            predictions=tuple(predictions),
            horizon_reached=len(predictions),
            terminal=terminal,
        )

        # A terminal state legitimately closes the rollout early. Otherwise the
        # announced horizon must have been completed for the available command
        # sequence. Planning may request a shorter plan than H_eff; that plan
        # endpoint is a complete trajectory, not an interrupted computation.
        if not terminal and len(predictions) < horizon_target:
            return SimulationResult(
                status="unavailable",
                equipment_version=self._equipment.version,
                requested_rollouts=r_eff,
                effective_rollouts=1,
                requested_horizon=h_eff,
                completed_rollouts=(),
                partial_rollout=rollout,
                reason="announced_horizon_incomplete",
            )

        return SimulationResult(
            status="complete",
            equipment_version=self._equipment.version,
            requested_rollouts=r_eff,
            effective_rollouts=1,
            requested_horizon=h_eff,
            completed_rollouts=(rollout,),
            partial_rollout=None,
            reason=None,
        )
