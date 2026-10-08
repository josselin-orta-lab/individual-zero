"""Stage-3 symbolic perception without noise.

This module consumes only the local capture and authorized body telemetry.
It never imports or accesses the world, oracle, bench, or technical journal.

Spec: 6.1, 9.2, 20.3 Stage 3, DC-11, INV-02, INV-45.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class PerceivedCell:
    direction: str
    x: int
    y: int
    passable: bool
    water_source: bool
    resources: tuple[str, ...]
    creature: bool


@dataclass(frozen=True, slots=True)
class PerceptualCapture:
    t_monde: int
    x: int
    y: int
    body: Mapping[str, float]
    current_water_source: bool
    current_resources: tuple[str, ...]
    adjacent: tuple[PerceivedCell, ...]

    @property
    def adjacent_creatures(self) -> tuple[PerceivedCell, ...]:
        return tuple(cell for cell in self.adjacent if cell.creature)

    @property
    def passable_moves(self) -> tuple[PerceivedCell, ...]:
        return tuple(cell for cell in self.adjacent if cell.passable)


class SymbolicPerception:
    """Deterministic Stage-3 perception stub with no learned state or noise."""

    def capture(
        self,
        *,
        local_state: Mapping[str, object],
        telemetry: Mapping[str, float],
    ) -> PerceptualCapture:
        position = local_state.get("position")
        adjacent = local_state.get("adjacent")
        if not isinstance(position, Mapping) or not isinstance(adjacent, Sequence):
            raise ValueError("invalid local-state capture")

        perceived_cells: list[PerceivedCell] = []
        for raw in adjacent:
            if not isinstance(raw, Mapping):
                raise ValueError("invalid adjacent local cell")
            raw_position = raw.get("position")
            resources = raw.get("resources")
            if not isinstance(raw_position, Mapping) or not isinstance(resources, Sequence):
                raise ValueError("invalid adjacent cell payload")
            perceived_cells.append(
                PerceivedCell(
                    direction=str(raw["direction"]),
                    x=int(raw_position["x"]),
                    y=int(raw_position["y"]),
                    passable=bool(raw["passable"]),
                    water_source=bool(raw["water_source"]),
                    resources=tuple(str(item) for item in resources),
                    creature=bool(raw["creature"]),
                )
            )

        body = {
            key: float(telemetry[key])
            for key in ("energy", "food", "water", "integrity")
        }
        return PerceptualCapture(
            t_monde=int(local_state["t_monde"]),
            x=int(position["x"]),
            y=int(position["y"]),
            body=body,
            current_water_source=bool(local_state["current_water_source"]),
            current_resources=tuple(
                str(item)
                for item in local_state["current_resources"]  # type: ignore[index]
            ),
            adjacent=tuple(perceived_cells),
        )
