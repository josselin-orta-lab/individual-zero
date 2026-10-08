"""Stage-3 symbolic perception without noise.

This module consumes only the local capture and authorized body telemetry.
It never imports or accesses the world, oracle, bench, or technical journal.

Spec: 6.1, 9.2, 20.3 Stage 3, DC-11, INV-02, INV-45.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from i0.contracts import Contribution


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
class PerceivedEntity:
    entity_id: str
    entity_type: str
    x: int
    y: int
    properties: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class PerceptualCapture:
    t_monde: int
    x: int
    y: int
    body: Mapping[str, float]
    current_water_source: bool
    current_resources: tuple[str, ...]
    adjacent: tuple[PerceivedCell, ...]
    visible_entities: tuple[PerceivedEntity, ...] = ()

    @property
    def adjacent_creatures(self) -> tuple[PerceivedCell, ...]:
        return tuple(cell for cell in self.adjacent if cell.creature)

    @property
    def passable_moves(self) -> tuple[PerceivedCell, ...]:
        return tuple(cell for cell in self.adjacent if cell.passable)


class SymbolicPerception:
    """Deterministic symbolic perception with Stage-4 exact known-map state."""

    owner_id = "perception"

    def __init__(self) -> None:
        self._known_entities: dict[str, PerceivedEntity] = {}
        self._observation_ref_by_entity: dict[str, str] = {}

    @property
    def known_entities(self) -> Mapping[str, PerceivedEntity]:
        return dict(self._known_entities)

    @property
    def observation_ref_by_entity(self) -> Mapping[str, str]:
        return dict(self._observation_ref_by_entity)

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

        raw_entities = local_state.get("visible_entities", ())
        if not isinstance(raw_entities, Sequence):
            raise ValueError("invalid visible-entity payload")
        perceived_entities: list[PerceivedEntity] = []
        for raw in raw_entities:
            if not isinstance(raw, Mapping):
                raise ValueError("invalid visible entity")
            raw_position = raw.get("position")
            properties = raw.get("properties", {})
            if not isinstance(raw_position, Mapping) or not isinstance(properties, Mapping):
                raise ValueError("invalid visible entity payload")
            entity = PerceivedEntity(
                entity_id=str(raw["entity_id"]),
                entity_type=str(raw["entity_type"]),
                x=int(raw_position["x"]),
                y=int(raw_position["y"]),
                properties=dict(properties),
            )
            perceived_entities.append(entity)
            self._known_entities[entity.entity_id] = entity

        refs = state.get("observation_ref_by_entity", {})
        if not isinstance(refs, Mapping):
            raise ValueError("invalid Perception observation-ref state")
        self._observation_ref_by_entity = {
            str(entity_id): str(ref)
            for entity_id, ref in refs.items()
        }

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
            visible_entities=tuple(perceived_entities),
        )

    def publish_capture(
        self,
        *,
        capture: PerceptualCapture,
        cycle: int,
        ttl_steps: int,
    ) -> tuple[Contribution, ...]:
        if ttl_steps < 1:
            raise ValueError("perception contribution TTL must be >= 1")

        contributions: list[Contribution] = []
        for entity in sorted(
            capture.visible_entities,
            key=lambda item: (item.entity_type, item.entity_id),
        ):
            contribution = Contribution(
                id=f"observation:{entity.entity_id}:{capture.t_monde}:{cycle}",
                schema_version="mvp-v1.2.1",
                type="observation",
                summary=(
                    f"{entity.entity_type} at ({entity.x},{entity.y})"
                ),
                subject_ref=f"entity:{entity.entity_id}",
                emitter_module="perception",
                signal_family="world_symbolic",
                confidence=1.0,
                urgency=0.0,
                risk=0.0,
                value=0.0,
                production_t=capture.t_monde,
                production_cycle=cycle,
                expires_at_step=capture.t_monde + ttl_steps,
                payload={
                    "entity_ref": entity.entity_id,
                    "entity_type": entity.entity_type,
                    "attribute": "position",
                    "value": {"x": entity.x, "y": entity.y},
                    "uncertainty": 0.0,
                    "channel": "symbolic_world",
                    "anchor": "world",
                    "properties": dict(entity.properties),
                },
                signal_ids=(
                    f"world-capture:{capture.t_monde}:{entity.entity_id}",
                ),
            )
            contribution.validate()
            self._observation_ref_by_entity[entity.entity_id] = contribution.id
            contributions.append(contribution)
        return tuple(contributions)

    def export_causal_state(self) -> object:
        return {
            "known_entities": [
                {
                    "entity_id": entity.entity_id,
                    "entity_type": entity.entity_type,
                    "x": entity.x,
                    "y": entity.y,
                    "properties": dict(entity.properties),
                }
                for entity in sorted(
                    self._known_entities.values(),
                    key=lambda item: item.entity_id,
                )
            ],
            "observation_ref_by_entity": dict(
                sorted(self._observation_ref_by_entity.items())
            ),
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("Perception state must be a mapping")
        raw = state.get("known_entities")
        if not isinstance(raw, list):
            raise ValueError("Perception known_entities must be a list")
        self._known_entities = {}
        for row in raw:
            if not isinstance(row, Mapping):
                raise ValueError("invalid known entity state")
            entity = PerceivedEntity(
                entity_id=str(row["entity_id"]),
                entity_type=str(row["entity_type"]),
                x=int(row["x"]),
                y=int(row["y"]),
                properties=dict(row.get("properties", {})),
            )
            self._known_entities[entity.entity_id] = entity
