"""Reduced Stage-10 sleep perception: a filtered *lived* local world capture.

The Lab supplies a single captured local state and telemetry per sleeping world
step. This filter exposes only authorized reflex geometry, nearby creatures,
and critical body changes. It never reads WorldBody, oracles, hidden maps,
technical journals, stored memories, or cognitive S_t. It does not infer a
numeric threat score: the dedicated DC-13 wake rule owns that calibration.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

from .perception import PerceptualCapture, PerceivedCell

_DIRECTIONS = frozenset(("north", "south", "east", "west"))
_BODY = frozenset(("energy", "food", "water", "integrity"))


@dataclass(frozen=True, slots=True)
class ReducedSleepObservation:
    capture: PerceptualCapture
    source_capture_ref: str
    adjacent_creature: bool
    critical_body_channels: tuple[str, ...]

    @property
    def world_step(self) -> int:
        return self.capture.t_monde


def reduced_sleep_capture(
    *, local_state: Mapping[str, object], telemetry: Mapping[str, float],
    source_capture_ref: str, world_step: int,
    critical_thresholds: Mapping[str, float],
) -> ReducedSleepObservation:
    """Filter a *single real capture*, not a reconstruction from waking memory.

    
    The caller must ensure local_state and telemetry belong to exactly the
    same physical capture at world_step. This pure function cannot attest the
    Lab's capture count or physical provenance, which is a runtime obligation.
    """
    if (type(world_step) is not int or world_step < 1
            or type(source_capture_ref) is not str or not source_capture_ref.strip()
            or not isinstance(local_state, Mapping)
            or type(local_state.get("t_monde")) is not int
            or local_state["t_monde"] != world_step
            or not isinstance(telemetry, Mapping)
            or not isinstance(critical_thresholds, Mapping)
            or not critical_thresholds or not set(critical_thresholds).issubset(_BODY)):
        raise ValueError("sleep reduction requires one versioned physical capture")
    position = local_state.get("position")
    adjacent = local_state.get("adjacent")
    if (not isinstance(position, Mapping)
            or type(position.get("x")) is not int
            or type(position.get("y")) is not int
            or not isinstance(adjacent, Sequence) or isinstance(adjacent, (str, bytes))):
        raise ValueError("invalid reduced local geometry")
    body: dict[str, float] = {}
    for key in sorted(_BODY):
        value = telemetry.get(key)
        if type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 100:
            raise ValueError("invalid physical body telemetry")
        body[key] = float(value)
    thresholds: dict[str, float] = {}
    for key, value in critical_thresholds.items():
        if (type(key) is not str or type(value) not in (int, float)
                or not isfinite(value) or not 0 <= value <= 100):
            raise ValueError("invalid versioned critical body threshold")
        thresholds[key] = float(value)

    reduced_cells: list[PerceivedCell] = []
    seen: set[str] = set()
    for raw in adjacent:
        if not isinstance(raw, Mapping):
            raise ValueError("invalid physical adjacent cell")
        direction = raw.get("direction")
        coord = raw.get("position")
        if (direction not in _DIRECTIONS or direction in seen
                or not isinstance(coord, Mapping)
                or type(coord.get("x")) is not int or type(coord.get("y")) is not int
                or type(raw.get("creature")) is not bool
                or type(raw.get("passable")) is not bool):
            raise ValueError("invalid reduced reflex geometry")
        seen.add(direction)
        reduced_cells.append(PerceivedCell(
            direction=direction,
            x=coord["x"], y=coord["y"],
            passable=raw["passable"],
            creature=raw["creature"],
            water_source=False, resources=(),
        ))
    reduced_cells.sort(key=lambda cell: (cell.direction, cell.x, cell.y))
    capture = PerceptualCapture(
        t_monde=world_step, x=position["x"], y=position["y"],
        body=body, current_water_source=False, current_resources=(),
        adjacent=tuple(reduced_cells), visible_entities=(), inventory={},
    )
    return ReducedSleepObservation(
        capture=capture, source_capture_ref=source_capture_ref,
        adjacent_creature=bool(capture.adjacent_creatures),
        critical_body_channels=tuple(sorted(
            key for key, threshold in thresholds.items()
            if body[key] <= threshold
        )),
    )
