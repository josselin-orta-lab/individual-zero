"""Grid world and body physics for normative MVP Stage 2.

The physics is deterministic. Numerical costs, gains, damages, layouts and
world-specific contingencies are explicit preregistered configuration inputs.

Spec: 4.1, 7.1, 18.3, 19.5, 20.3 Stage 2, P-52, P-53.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from i1.interfaces import PrimitiveCommand

from .determinism import canonical_causal_bytes, sha256_hex


PRIMITIVE_ACTIONS = frozenset(
    {
        "se_deplacer",
        "collecter",
        "manger",
        "boire",
        "poser_une_pierre",
        "fabriquer_outil",
        "dormir",
        "attendre",
    }
)
DIRECTIONS = {
    "north": (0, -1),
    "south": (0, 1),
    "east": (1, 0),
    "west": (-1, 0),
}
RESOURCE_KINDS = frozenset({"berry_a", "berry_b", "wood", "stone"})


@dataclass(frozen=True, order=True, slots=True)
class Position:
    x: int
    y: int

    def moved(self, direction: str) -> "Position":
        try:
            dx, dy = DIRECTIONS[direction]
        except KeyError as exc:
            raise ValueError(f"unknown movement direction: {direction}") from exc
        return Position(self.x + dx, self.y + dy)

    def manhattan(self, other: "Position") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def as_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y}


@dataclass(frozen=True, slots=True)
class BodyState:
    energy: float
    food: float
    water: float
    integrity: float

    def validate(self) -> None:
        for name, value in (
            ("energy", self.energy),
            ("food", self.food),
            ("water", self.water),
            ("integrity", self.integrity),
        ):
            if not 0.0 <= value <= 100.0:
                raise ValueError(f"{name} must be in [0,100]")

    def as_dict(self) -> dict[str, float]:
        return {
            "energy": self.energy,
            "food": self.food,
            "water": self.water,
            "integrity": self.integrity,
        }


@dataclass(frozen=True, slots=True)
class BerryEffect:
    food_gain: float
    integrity_delta: float

    def validate(self) -> None:
        if self.food_gain < 0:
            raise ValueError("berry food gain must be non-negative")

    def as_dict(self) -> dict[str, float]:
        return {
            "food_gain": self.food_gain,
            "integrity_delta": self.integrity_delta,
        }


@dataclass(frozen=True, slots=True)
class ToolRecipe:
    wood_required: int
    stone_required: int
    collection_gain: int

    def validate(self) -> None:
        if self.wood_required < 0 or self.stone_required < 0:
            raise ValueError("tool recipe quantities must be non-negative")
        if self.collection_gain < 1:
            raise ValueError("tool collection gain must be >= 1")

    def as_dict(self) -> dict[str, int]:
        return {
            "wood_required": self.wood_required,
            "stone_required": self.stone_required,
            "collection_gain": self.collection_gain,
        }


@dataclass(frozen=True, slots=True)
class WorldPhysicsConfig:
    """Preregistered Stage-2 physics, carrying P-52 and P-53 values."""

    version: str
    width: int
    height: int
    day_steps: int
    night_steps: int
    night_start_step: int
    initial_body: BodyState
    initial_position: Position
    food_decay_per_step: float
    water_decay_per_step: float
    action_energy_costs: Mapping[str, float]
    sleep_energy_gain: float
    rest_integrity_gain: float
    drink_water_gain: float
    berry_effects: Mapping[str, BerryEffect]
    creature_damage: float
    danger_zone_damage: float
    tool_recipe: ToolRecipe
    shelter_stones_required: int = 4
    starvation_integrity_damage_per_step: float = 0.0
    dehydration_integrity_damage_per_step: float = 0.0

    def validate(self) -> None:
        if not self.version:
            raise ValueError("world physics version must not be empty")
        if (self.width, self.height) != (32, 32):
            raise ValueError("normative MVP grid is exactly 32 x 32")
        if self.day_steps != 300 or self.night_steps != 100:
            raise ValueError("normative MVP day is 300 steps including 100 night steps")
        if not 0 <= self.night_start_step < self.day_steps:
            raise ValueError("night_start_step must be inside the simulated day")
        if self.night_start_step + self.night_steps > self.day_steps:
            raise ValueError("night interval must fit within one simulated day")
        self.initial_body.validate()
        self._validate_interior(self.initial_position)
        if self.food_decay_per_step < 0 or self.water_decay_per_step < 0:
            raise ValueError("continuous body decay must be non-negative")
        if self.sleep_energy_gain < 0 or self.rest_integrity_gain < 0:
            raise ValueError("rest gains must be non-negative")
        if (
            self.drink_water_gain < 0
            or self.creature_damage < 0
            or self.danger_zone_damage < 0
        ):
            raise ValueError("world gains and damages must be non-negative")
        if set(self.action_energy_costs) != PRIMITIVE_ACTIONS:
            raise ValueError("energy cost must be declared for every primitive action")
        if any(cost < 0 for cost in self.action_energy_costs.values()):
            raise ValueError("action energy costs must be non-negative")
        if set(self.berry_effects) != {"berry_a", "berry_b"}:
            raise ValueError("the MVP contains exactly two berry species")
        for effect in self.berry_effects.values():
            effect.validate()
        for damage in (self.starvation_integrity_damage_per_step,
                       self.dehydration_integrity_damage_per_step):
            if not 0.0 <= damage <= 100.0 or damage != damage:
                raise ValueError('I1 deprivation rates must be finite in [0,100]')
        self.tool_recipe.validate()
        if self.shelter_stones_required != 4:
            raise ValueError("normative MVP shelter is formed from exactly 4 stones")

    def _validate_interior(self, position: Position) -> None:
        if not (1 <= position.x < self.width - 1 and 1 <= position.y < self.height - 1):
            raise ValueError("position must lie inside impassable borders")

    def is_night(self, t_monde: int) -> bool:
        if t_monde < 1:
            raise ValueError("world step must be >= 1")
        step_in_day = (t_monde - 1) % self.day_steps
        return self.night_start_step <= step_in_day < self.night_start_step + self.night_steps

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "width": self.width,
            "height": self.height,
            "day_steps": self.day_steps,
            "night_steps": self.night_steps,
            "night_start_step": self.night_start_step,
            "initial_body": self.initial_body.as_dict(),
            "initial_position": self.initial_position.as_dict(),
            "food_decay_per_step": self.food_decay_per_step,
            "water_decay_per_step": self.water_decay_per_step,
            "action_energy_costs": dict(self.action_energy_costs),
            "sleep_energy_gain": self.sleep_energy_gain,
            "rest_integrity_gain": self.rest_integrity_gain,
            "drink_water_gain": self.drink_water_gain,
            "berry_effects": {
                name: effect.as_dict()
                for name, effect in sorted(self.berry_effects.items())
            },
            "creature_damage": self.creature_damage,
            "danger_zone_damage": self.danger_zone_damage,
            "tool_recipe": self.tool_recipe.as_dict(),
            "shelter_stones_required": self.shelter_stones_required,
            "starvation_integrity_damage_per_step": self.starvation_integrity_damage_per_step,
            "dehydration_integrity_damage_per_step": self.dehydration_integrity_damage_per_step,
        }

    def digest(self) -> str:
        self.validate()
        return sha256_hex(canonical_causal_bytes(self.as_dict()))


@dataclass(frozen=True, slots=True)
class WorldLayout:
    """Complete preregistered starting layout for one world instance."""

    obstacles: frozenset[Position] = frozenset()
    water_sources: frozenset[Position] = frozenset()
    resources: tuple[tuple[Position, str, int], ...] = ()
    creatures: frozenset[Position] = frozenset()
    danger_zones: frozenset[Position] = frozenset()
    lethal_zones: frozenset[Position] = frozenset()
    oracle_canary: str = ""

    def validate(self, config: WorldPhysicsConfig) -> None:
        config.validate()
        for position in (
            set(self.obstacles)
            | set(self.water_sources)
            | set(self.creatures)
            | set(self.danger_zones)
            | set(self.lethal_zones)
        ):
            config._validate_interior(position)
        seen_resource_cells: set[tuple[Position, str]] = set()
        for position, kind, quantity in self.resources:
            config._validate_interior(position)
            if kind not in RESOURCE_KINDS:
                raise ValueError(f"unknown resource kind: {kind}")
            if quantity < 0:
                raise ValueError("resource quantity must be non-negative")
            key = (position, kind)
            if key in seen_resource_cells:
                raise ValueError("duplicate resource kind at same cell")
            seen_resource_cells.add(key)

    def as_dict(self) -> dict[str, object]:
        return {
            "obstacles": [p.as_dict() for p in sorted(self.obstacles)],
            "water_sources": [p.as_dict() for p in sorted(self.water_sources)],
            "resources": [
                {"position": p.as_dict(), "kind": kind, "quantity": quantity}
                for p, kind, quantity in sorted(
                    self.resources,
                    key=lambda row: (row[0].x, row[0].y, row[1]),
                )
            ],
            "creatures": [p.as_dict() for p in sorted(self.creatures)],
            "danger_zones": [p.as_dict() for p in sorted(self.danger_zones)],
            "lethal_zones": [p.as_dict() for p in sorted(self.lethal_zones)],
            "oracle_canary": self.oracle_canary,
        }


Command = PrimitiveCommand


@dataclass(frozen=True, slots=True)
class LocalCell:
    direction: str
    position: Position
    passable: bool
    water_source: bool
    resources: tuple[str, ...]
    creature: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "direction": self.direction,
            "position": self.position.as_dict(),
            "passable": self.passable,
            "water_source": self.water_source,
            "resources": list(self.resources),
            "creature": self.creature,
        }


@dataclass(frozen=True, slots=True)
class VisibleEntity:
    entity_id: str
    entity_type: str
    position: Position
    properties: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "position": self.position.as_dict(),
            "properties": dict(self.properties),
        }


@dataclass(frozen=True, slots=True)
class LocalWorldState:
    t_monde: int
    position: Position
    current_water_source: bool
    current_resources: tuple[str, ...]
    adjacent: tuple[LocalCell, ...]
    visible_entities: tuple[VisibleEntity, ...] = ()
    inventory: Mapping[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "t_monde": self.t_monde,
            "position": self.position.as_dict(),
            "current_water_source": self.current_water_source,
            "current_resources": list(self.current_resources),
            "adjacent": [cell.as_dict() for cell in self.adjacent],
            "visible_entities": [
                entity.as_dict() for entity in self.visible_entities
            ],
            "inventory": dict(sorted(self.inventory.items())),
        }


@dataclass(frozen=True, slots=True)
class TransitionResult:
    command: Command
    t_monde: int
    position_before: Position
    position_after: Position
    body_before: BodyState
    body_after: BodyState
    lethal: bool
    lethal_reasons: tuple[str, ...]
    effects: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "command": self.command.as_dict(),
            "t_monde": self.t_monde,
            "position_before": self.position_before.as_dict(),
            "position_after": self.position_after.as_dict(),
            "body_before": self.body_before.as_dict(),
            "body_after": self.body_after.as_dict(),
            "lethal": self.lethal,
            "lethal_reasons": list(self.lethal_reasons),
            "effects": dict(self.effects),
        }


def validate_command(command: PrimitiveCommand) -> None:
    if command.primitive not in PRIMITIVE_ACTIONS:
        raise ValueError(f"unknown primitive action: {command.primitive}")
    if command.primitive == "se_deplacer":
        direction = command.parameters.get("direction")
        if direction not in DIRECTIONS:
            raise ValueError("movement command requires a canonical direction")
    if command.primitive in {"collecter", "manger"}:
        target = command.parameters.get("target")
        if target not in RESOURCE_KINDS:
            raise ValueError(f"{command.primitive} requires a resource target")
    unknown = set(command.parameters)
    allowed = {
        "se_deplacer": {"direction"},
        "collecter": {"target"},
        "manger": {"target"},
    }.get(command.primitive, set())
    if unknown - allowed:
        raise ValueError(
            f"unsupported parameters for {command.primitive}: "
            + ", ".join(sorted(unknown - allowed))
        )


def command_digest(command: PrimitiveCommand) -> str:
    validate_command(command)
    return sha256_hex(canonical_causal_bytes(command.as_dict()))


class WorldBody:
    """Single owner of simulated real world and body causal state."""

    owner_id = "world_and_body"
    # Only mutable physical state advances when an externally prepared batch
    # is committed. Immutable physics/configuration objects retain identity.
    _SCENARIO_MUTABLE_FIELDS = (
        "_position", "_body", "_inventory", "_resources", "_placed_stones",
        "_shelters", "_obstacles", "_water_sources", "_creatures",
        "_danger_zones", "_lethal_zones", "_action_failure_schedules",
        "_action_failure_indices",
    )

    def __init__(
        self,
        *,
        config: WorldPhysicsConfig,
        layout: WorldLayout,
    ) -> None:
        config.validate()
        layout.validate(config)
        if config.initial_position in layout.obstacles:
            raise ValueError("initial position cannot be an obstacle")
        self._config = config
        self._layout = layout
        self._position = config.initial_position
        self._body = config.initial_body
        self._inventory: dict[str, int] = {
            "berry_a": 0,
            "berry_b": 0,
            "wood": 0,
            "stone": 0,
            "tool": 0,
        }
        self._resources: dict[tuple[Position, str], int] = {
            (position, kind): quantity
            for position, kind, quantity in layout.resources
        }
        self._placed_stones: dict[Position, int] = {}
        self._shelters: set[Position] = set()
        self._obstacles = set(layout.obstacles)
        self._water_sources = set(layout.water_sources)
        self._creatures = set(layout.creatures)
        self._danger_zones = set(layout.danger_zones)
        self._lethal_zones = set(layout.lethal_zones)
        # Empty outside an injected battery scenario, so historical causal
        # encodings remain unchanged. P-54 supplies primitive + schedule.
        self._action_failure_schedules: dict[str, tuple[bool, ...]] = {}
        self._action_failure_indices: dict[str, int] = {}
        # Monotonic custody bit: not part of the individual's physical or
        # cognitive state; a detached copy has a different identity.
        self._historical_restore_forbidden = False
        # Monotonic runtime guard, deliberately excluded from causal state.
        # A terminal individual's physical consequences cannot be changed
        # through the public WorldBody mutation API.
        self._terminal_frozen = False
        # Direct WorldBody.apply would otherwise bypass Action Control,
        # the once-only mortal boundary and its causal journal receipts.
        self._mortal_dispatch_key: object | None = None
        self._mortal_dispatch_active = False

    def _install_mortal_dispatch_authority(self) -> object:
        """Bind exactly one forward-only physical dispatcher to this world."""
        if self._mortal_dispatch_key is not None:
            raise RuntimeError("mortal WorldBody already has a physical owner")
        key = object()
        self._mortal_dispatch_key = key
        return key

    @contextmanager
    def _admit_mortal_dispatch(self, key: object):
        """Authorize one synchronous boundary-owned WorldBody.apply call."""
        self._require_mutable_world()
        if key is not self._mortal_dispatch_key or self._mortal_dispatch_active:
            raise RuntimeError("unauthorized or reentrant mortal world dispatch")
        self._mortal_dispatch_active = True
        try:
            yield
        finally:
            self._mortal_dispatch_active = False

    def freeze_terminal_state(self) -> None:
        """Forbid further physical and scenario mutation on this world owner."""
        self._terminal_frozen = True

    def _require_mutable_world(self) -> None:
        if self._terminal_frozen:
            raise RuntimeError("terminal or halted WorldBody cannot be mutated")

    def forbid_historical_restore(self) -> None:
        """Permanently forbid changing this living world's past via import."""
        self._historical_restore_forbidden = True

    def apply_scenario_batch_atomically(
        self, operations: Sequence[tuple[str, Mapping[str, object]]],
    ) -> None:
        """Commit only forward external operations prepared on a private copy.

        An invalid later operation has no effect on the actual world. Only
        after the entire private batch succeeds do we replace all mutable
        physical fields with ONE dictionary publication. There is no saved
        public state to restore and no retroactive compensation on error.
        """
        self._require_mutable_world()
        if not self._historical_restore_forbidden:
            raise RuntimeError("forward batch requires mortal-world custody")
        if not operations:
            return
        candidate = deepcopy(self)
        for operation, payload in operations:
            candidate.apply_scenario_event(operation, deepcopy(dict(payload)))
        # No operation that can fail occurs after publication begins.
        replacement = dict(self.__dict__)
        for name in self._SCENARIO_MUTABLE_FIELDS:
            replacement[name] = getattr(candidate, name)
        self.__dict__ = replacement

    @property
    def position(self) -> Position:
        return self._position

    @property
    def body(self) -> BodyState:
        return self._body

    @property
    def config(self) -> WorldPhysicsConfig:
        return self._config

    def inventory(self) -> Mapping[str, int]:
        return dict(self._inventory)

    def telemetry(self) -> Mapping[str, float]:
        return self._body.as_dict()

    def capture_local(self, *, t_monde: int) -> LocalWorldState:
        """Return the minimal Stage-3 local symbolic state.

        Hidden danger/lethality classifications are deliberately absent.
        """

        if t_monde < 1:
            raise ValueError("t_monde must be >= 1")

        # Stage-3 only sees the current cell and four cardinal neighbors.
        # Inspect every resource once rather than re-scanning the entire world
        # for each of those cells. This lookup is ephemeral observation work:
        # it is never retained by the individual or populated from Oracle data.
        local_positions = {self._position}
        local_positions.update(
            self._position.moved(direction)
            for direction in ("north", "south", "east", "west")
        )
        local_resource_rows: dict[Position, list[tuple[str, int]]] = {}
        for (position, kind), quantity in self._resources.items():
            if position in local_positions and quantity > 0:
                local_resource_rows.setdefault(position, []).append((kind, quantity))

        def resource_kinds(position: Position) -> tuple[str, ...]:
            return tuple(sorted(kind for kind, _ in local_resource_rows.get(position, ())))

        adjacent: list[LocalCell] = []
        for direction in ("north", "south", "east", "west"):
            position = self._position.moved(direction)
            passable = self._is_interior(position) and position not in self._obstacles
            adjacent.append(
                LocalCell(
                    direction=direction,
                    position=position,
                    passable=passable,
                    water_source=position in self._water_sources,
                    resources=resource_kinds(position),
                    creature=position in self._creatures,
                )
            )

        visible_entities: list[VisibleEntity] = []
        for index, position in enumerate(sorted(self._water_sources)):
            visible_entities.append(
                VisibleEntity(
                    entity_id=f"water_source:{index}",
                    entity_type="water_source",
                    position=position,
                    properties={},
                )
            )
        # Visible resources already belong to the local field. Their final
        # entity order is established below by (entity_type, entity_id), so
        # sorting remote resource cells cannot influence the capture.
        for position, resources in local_resource_rows.items():
            for kind, quantity in resources:
                visible_entities.append(
                    VisibleEntity(
                        entity_id=f"{kind}:{position.x}:{position.y}",
                        entity_type=kind,
                        position=position,
                        properties={"quantity": quantity},
                    )
                )
        for index, position in enumerate(sorted(self._creatures)):
            visible_entities.append(
                VisibleEntity(
                    entity_id=f"creature:{index}",
                    entity_type="creature",
                    position=position,
                    properties={},
                )
            )
        for index, position in enumerate(sorted(self._shelters)):
            visible_entities.append(
                VisibleEntity(
                    entity_id=f"shelter:{index}",
                    entity_type="shelter",
                    position=position,
                    properties={},
                )
            )

        # Only the physical cell and its four cardinal neighbors are in the
        # local symbolic field. Full remote entity lists belong to WorldBody
        # and the external observer, never the individual's Perception.
        visible_entities = [
            entity for entity in visible_entities
            if (abs(entity.position.x - self._position.x)
                + abs(entity.position.y - self._position.y)) <= 1
        ]

        return LocalWorldState(
            t_monde=t_monde,
            position=self._position,
            current_water_source=self._position in self._water_sources,
            current_resources=resource_kinds(self._position),
            adjacent=tuple(adjacent),
            visible_entities=tuple(
                sorted(
                    visible_entities,
                    key=lambda entity: (
                        entity.entity_type,
                        entity.entity_id,
                    ),
                )
            ),
            inventory=dict(sorted(self._inventory.items())),
        )

    def is_night(self, t_monde: int) -> bool:
        return self._config.is_night(t_monde)

    def ground_truth(self) -> Mapping[str, object]:
        """Complete state for oracle/bench only. Never hand this to the individual."""

        return {
            "position": self._position.as_dict(),
            "body": self._body.as_dict(),
            "inventory": dict(sorted(self._inventory.items())),
            "resources": [
                {
                    "position": position.as_dict(),
                    "kind": kind,
                    "quantity": quantity,
                }
                for (position, kind), quantity in sorted(
                    self._resources.items(),
                    key=lambda row: (row[0][0].x, row[0][0].y, row[0][1]),
                )
            ],
            "obstacles": [p.as_dict() for p in sorted(self._obstacles)],
            "water_sources": [p.as_dict() for p in sorted(self._water_sources)],
            "creatures": [p.as_dict() for p in sorted(self._creatures)],
            "danger_zones": [p.as_dict() for p in sorted(self._danger_zones)],
            "lethal_zones": [p.as_dict() for p in sorted(self._lethal_zones)],
            "placed_stones": [
                {"position": p.as_dict(), "count": count}
                for p, count in sorted(self._placed_stones.items())
            ],
            "shelters": [p.as_dict() for p in sorted(self._shelters)],
            "oracle_canary": self._layout.oracle_canary,
            "physics_version": self._config.version,
        }

    def capture_operator_world_frame(self, *, t_monde: int) -> dict[str, object]:
        """Capture actual engine state for an operator-owned 2D export.

        This is a read-only capture, NOT an I0 observation, an Oracle result,
        a journal commit, or proof that a step boundary was committed. The
        caller must attest the corresponding durable closure separately.
        """
        if type(t_monde) is not int or t_monde < 1:
            raise ValueError("operator frame requires a positive world step")
        entities: list[dict[str, object]] = []

        def add(kind: str, position: Position, suffix: str = "") -> None:
            entities.append({
                "id": f"{kind}:{position.x}:{position.y}{suffix}",
                "kind": kind,
                "position": position.as_dict(),
            })

        for kind, positions in (
            ("obstacle", self._obstacles),
            ("water", self._water_sources),
            ("creature", self._creatures),
            ("danger", self._danger_zones),
            ("lethal", self._lethal_zones),
            ("shelter", self._shelters),
        ):
            for position in sorted(positions):
                add(kind, position)
        for (position, kind), quantity in sorted(self._resources.items()):
            if quantity > 0:
                add("resource", position, ":" + kind)
        for position, count in sorted(self._placed_stones.items()):
            if count > 0:
                add("stone", position)
        entities.sort(key=lambda item: item["id"])
        return {
            "t_monde": t_monde,
            "individual_pose": self._position.as_dict(),
            "entities": entities,
        }

    def operator_world_geometry(self) -> dict[str, object]:
        """Read-only engine geometry, never a cognition-facing observation."""
        return {
            "coordinate_system": "grid-xy-top-left",
            "width": self._config.width,
            "height": self._config.height,
        }

    def export_causal_state(self) -> object:
        truth = dict(self.ground_truth())
        truth.pop("oracle_canary", None)
        if self._action_failure_schedules:
            truth["scenario_action_failures"] = [
                {
                    "primitive": primitive,
                    "schedule": list(self._action_failure_schedules[primitive]),
                    "next_index": self._action_failure_indices.get(primitive, 0),
                }
                for primitive in sorted(self._action_failure_schedules)
            ]
        return truth

    def restore_causal_state(self, state: object) -> None:
        """Import an independent historical fixture, never rewind live I0."""
        if self._historical_restore_forbidden:
            raise RuntimeError("historical WorldBody restoration is forbidden")
        if not isinstance(state, Mapping):
            raise ValueError("world/body state must be a mapping")
        if state.get("physics_version") != self._config.version:
            raise ValueError("world physics version mismatch")

        def read_position(raw: object, label: str) -> Position:
            if (
                not isinstance(raw, Mapping)
                or set(raw) != {"x", "y"}
                or type(raw["x"]) is not int
                or type(raw["y"]) is not int
            ):
                raise ValueError(f"invalid {label} position")
            result = Position(raw["x"], raw["y"])
            self._config._validate_interior(result)
            return result

        position = read_position(state.get("position"), "world")
        raw_body = state.get("body")
        body_fields = ("energy", "food", "water", "integrity")
        if (
            not isinstance(raw_body, Mapping)
            or set(raw_body) != set(body_fields)
            or any(type(raw_body[name]) not in (int, float)
                   for name in body_fields)
        ):
            raise ValueError("invalid world/body snapshot body")
        restored_body = BodyState(**{
            name: float(raw_body[name]) for name in body_fields
        })
        restored_body.validate()

        raw_inventory = state.get("inventory")
        if (
            not isinstance(raw_inventory, Mapping)
            or set(raw_inventory) != RESOURCE_KINDS | {"tool"}
            or any(type(quantity) is not int or quantity < 0
                   for quantity in raw_inventory.values())
        ):
            raise ValueError("invalid world inventory snapshot")
        inventory = dict(raw_inventory)

        raw_resources = state.get("resources")
        if not isinstance(raw_resources, list):
            raise ValueError("world/body snapshot is missing resources")
        resources: dict[tuple[Position, str], int] = {}
        for row in raw_resources:
            if not isinstance(row, Mapping) or set(row) != {
                "position", "kind", "quantity"
            }:
                raise ValueError("malformed resource row")
            location = read_position(row["position"], "resource")
            kind, quantity = row["kind"], row["quantity"]
            if (
                type(kind) is not str or kind not in RESOURCE_KINDS
                or type(quantity) is not int or quantity < 0
                or (location, kind) in resources
            ):
                raise ValueError("invalid or duplicate snapshot resource")
            resources[(location, kind)] = quantity

        def positions(name: str) -> set[Position]:
            raw = state.get(name)
            if not isinstance(raw, list):
                raise ValueError(f"missing {name} state")
            result: set[Position] = set()
            for row in raw:
                location = read_position(row, name)
                if location in result:
                    raise ValueError(f"duplicate {name} position")
                result.add(location)
            return result

        obstacles = positions("obstacles")
        water_sources = positions("water_sources")
        creatures = positions("creatures")
        danger_zones = positions("danger_zones")
        lethal_zones = positions("lethal_zones")
        shelters = positions("shelters")
        if position in obstacles:
            raise ValueError("world/body snapshot position is obstructed")

        raw_stones = state.get("placed_stones")
        if not isinstance(raw_stones, list):
            raise ValueError("missing placed stone state")
        placed_stones: dict[Position, int] = {}
        for row in raw_stones:
            if not isinstance(row, Mapping) or set(row) != {
                "position", "count"
            }:
                raise ValueError("malformed placed stone state")
            location = read_position(row["position"], "placed stone")
            count = row["count"]
            if (
                type(count) is not int or count < 1
                or location in placed_stones
            ):
                raise ValueError("invalid or duplicate placed stone count")
            placed_stones[location] = count

        raw_failures = state.get("scenario_action_failures", [])
        if not isinstance(raw_failures, list):
            raise ValueError("malformed scenario action-failure state")
        failure_schedules: dict[str, tuple[bool, ...]] = {}
        failure_indices: dict[str, int] = {}
        for row in raw_failures:
            if not isinstance(row, Mapping) or set(row) != {
                "primitive", "schedule", "next_index"
            }:
                raise ValueError("malformed scenario action-failure row")
            primitive = row["primitive"]
            schedule = row["schedule"]
            next_index = row["next_index"]
            if (
                type(primitive) is not str
                or primitive not in PRIMITIVE_ACTIONS
                or primitive in failure_schedules
                or not isinstance(schedule, list) or not schedule
                or any(type(value) is not bool for value in schedule)
                or type(next_index) is not int
                or not 0 <= next_index <= len(schedule)
            ):
                raise ValueError("invalid scenario action-failure program")
            failure_schedules[primitive] = tuple(schedule)
            failure_indices[primitive] = next_index

        # No validation or coercion occurs after the first assignment.
        # Owner snapshots, journal hashes and replay data remain unchanged
        # for states that WorldBody can actually export.
        self._position = position
        self._body = restored_body
        self._inventory = inventory
        self._resources = resources
        self._obstacles = obstacles
        self._water_sources = water_sources
        self._creatures = creatures
        self._danger_zones = danger_zones
        self._lethal_zones = lethal_zones
        self._shelters = shelters
        self._placed_stones = placed_stones
        self._action_failure_schedules = failure_schedules
        self._action_failure_indices = failure_indices

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, value))

    def _is_interior(self, position: Position) -> bool:
        return (
            1 <= position.x < self._config.width - 1
            and 1 <= position.y < self._config.height - 1
        )

    def _body_after_continuous_dynamics(
        self,
        *,
        command: Command,
        body: BodyState,
    ) -> BodyState:
        energy = body.energy
        if command.primitive == "dormir":
            energy += self._config.sleep_energy_gain
        else:
            energy -= self._config.action_energy_costs[command.primitive]

        integrity = body.integrity
        if command.primitive in {"attendre", "dormir"}:
            integrity += self._config.rest_integrity_gain

        return BodyState(
            energy=self._clamp(energy),
            food=self._clamp(body.food - self._config.food_decay_per_step),
            water=self._clamp(body.water - self._config.water_decay_per_step),
            integrity=self._clamp(integrity),
        )

    def _consume_action_failure_program(
        self,
        primitive: str,
    ) -> tuple[int, bool] | None:
        schedule = self._action_failure_schedules.get(primitive)
        if schedule is None:
            return None
        index = self._action_failure_indices.get(primitive, 0)
        if index >= len(schedule):
            return None
        forced = schedule[index]
        self._action_failure_indices[primitive] = index + 1
        return index, forced

    def apply(self, command: Command, *, t_monde: int) -> TransitionResult:
        """Apply one primitive command and detect lethality before continuation."""

        self._require_mutable_world()
        if self._mortal_dispatch_key is not None and not self._mortal_dispatch_active:
            raise RuntimeError("mortal world transitions require Action Control dispatch")
        validate_command(command)
        if t_monde < 1:
            raise ValueError("t_monde must be >= 1")

        before_position = self._position
        before_body = self._body
        position = before_position
        body = self._body_after_continuous_dynamics(command=command, body=before_body)
        effects: dict[str, object] = {}

        programmed_failure = self._consume_action_failure_program(
            command.primitive
        )
        forced_failure = False
        if programmed_failure is not None:
            attempt_index, forced_failure = programmed_failure
            effects["scenario_failure_attempt"] = {
                "primitive": command.primitive,
                "attempt_index": attempt_index,
                "forced": forced_failure,
            }

        if forced_failure:
            # The attempt consumes normal continuous body dynamics and world
            # time, but its primitive-specific intended effect is suppressed.
            # Hazards below still apply because general physics is unchanged.
            effects["scenario_forced_failure"] = command.primitive

        elif command.primitive == "se_deplacer":
            target = position.moved(str(command.parameters["direction"]))
            if self._is_interior(target) and target not in self._obstacles:
                position = target
                effects["movement"] = "moved"
            else:
                effects["movement"] = "blocked"

        elif command.primitive == "collecter":
            target = str(command.parameters["target"])
            key = (position, target)
            available = self._resources.get(key, 0)
            if available > 0:
                gain = self._config.tool_recipe.collection_gain if self._inventory["tool"] > 0 else 1
                collected = min(available, gain)
                self._resources[key] = available - collected
                self._inventory[target] += collected
                effects["collected"] = {"kind": target, "quantity": collected}
            else:
                effects["collected"] = {"kind": target, "quantity": 0}

        elif command.primitive == "manger":
            target = str(command.parameters["target"])
            if target not in {"berry_a", "berry_b"}:
                raise ValueError("only berries may be eaten in the MVP")
            if self._inventory[target] > 0:
                self._inventory[target] -= 1
                effect = self._config.berry_effects[target]
                body = BodyState(
                    energy=body.energy,
                    food=self._clamp(body.food + effect.food_gain),
                    water=body.water,
                    integrity=self._clamp(body.integrity + effect.integrity_delta),
                )
                effects["ate"] = target
            else:
                effects["ate"] = "unavailable"

        elif command.primitive == "boire":
            if position in self._water_sources:
                body = BodyState(
                    energy=body.energy,
                    food=body.food,
                    water=self._clamp(body.water + self._config.drink_water_gain),
                    integrity=body.integrity,
                )
                effects["drank"] = True
            else:
                effects["drank"] = False

        elif command.primitive == "poser_une_pierre":
            if self._inventory["stone"] > 0:
                self._inventory["stone"] -= 1
                count = self._placed_stones.get(position, 0) + 1
                self._placed_stones[position] = count
                effects["placed_stone_count"] = count
                if count >= self._config.shelter_stones_required:
                    self._shelters.add(position)
                    effects["shelter_formed"] = True
            else:
                effects["placed_stone_count"] = 0

        elif command.primitive == "fabriquer_outil":
            recipe = self._config.tool_recipe
            if (
                self._inventory["wood"] >= recipe.wood_required
                and self._inventory["stone"] >= recipe.stone_required
            ):
                self._inventory["wood"] -= recipe.wood_required
                self._inventory["stone"] -= recipe.stone_required
                self._inventory["tool"] += 1
                effects["tool_crafted"] = True
            else:
                effects["tool_crafted"] = False

        elif command.primitive in {"dormir", "attendre"}:
            effects["rest"] = command.primitive

        if self._config.is_night(t_monde):
            adjacent = [
                creature
                for creature in sorted(self._creatures)
                if position.manhattan(creature) <= 1
            ]
            if adjacent:
                body = BodyState(
                    energy=body.energy,
                    food=body.food,
                    water=body.water,
                    integrity=self._clamp(body.integrity - self._config.creature_damage),
                )
                effects["creature_damage"] = self._config.creature_damage

        if position in self._danger_zones:
            body = BodyState(
                energy=body.energy,
                food=body.food,
                water=body.water,
                integrity=self._clamp(
                    body.integrity - self._config.danger_zone_damage
                ),
            )
            effects["danger_zone_damage"] = self._config.danger_zone_damage

        # #231: apply *after* the actual action. Successful eating or
        # drinking prevents same-step deprivation. Rest, a failed
        # action, and physical hazards do not suspend metabolism.
        starvation = (self._config.starvation_integrity_damage_per_step
                      if body.food <= 0.0 else 0.0)
        dehydration = (self._config.dehydration_integrity_damage_per_step
                       if body.water <= 0.0 else 0.0)
        if starvation or dehydration:
            integrity_before = body.integrity
            body = BodyState(
                energy=body.energy, food=body.food, water=body.water,
                integrity=self._clamp(integrity_before - starvation - dehydration),
            )
            effects['deprivation_integrity_damage'] = {
                'starvation': starvation, 'dehydration': dehydration,
                'actual_integrity_loss': integrity_before - body.integrity,
            }
        lethal_reasons: list[str] = []
        if position in self._lethal_zones:
            lethal_reasons.append("lethal_zone")
        if body.integrity <= 0.0:
            lethal_reasons.append("zero_integrity")

        self._position = position
        self._body = body

        return TransitionResult(
            command=command,
            t_monde=t_monde,
            position_before=before_position,
            position_after=position,
            body_before=before_body,
            body_after=body,
            lethal=bool(lethal_reasons),
            lethal_reasons=tuple(lethal_reasons),
            effects=effects,
        )

    def apply_scenario_event(self, operation: str, payload: Mapping[str, object]) -> None:
        """Apply a logged external scenario input to world/body only."""

        self._require_mutable_world()
        def position_from_payload() -> Position:
            raw = payload.get("position")
            if (
                not isinstance(raw, Mapping)
                or set(raw) != {"x", "y"}
                or any(type(raw[name]) is not int for name in ("x", "y"))
            ):
                raise ValueError(
                    "scenario event requires exact integer x,y position"
                )
            position = Position(raw["x"], raw["y"])
            self._config._validate_interior(position)
            return position

        if operation == "set_obstacle":
            # A2: real environmental geometry change. Physical ownership
            # remains with WorldBody, never the cognition or evaluator.
            if set(payload) != {"position", "active"}:
                raise ValueError("obstacle intervention requires position and active")
            position = position_from_payload()
            active = payload["active"]
            if type(active) is not bool:
                raise ValueError("obstacle active must be a boolean")
            # An external obstacle may block the individual's *destination*,
            # but it cannot materialize under the current physical body.
            if active and position == self._position:
                raise ValueError("obstacle cannot occupy the current body cell")
            if active:
                self._obstacles.add(position)
            else:
                self._obstacles.discard(position)
            return

        if operation in {"set_danger_zone", "set_lethal_zone"}:
            position = position_from_payload()
            active = payload.get("active", True)
            if type(active) is not bool:
                raise ValueError("scenario zone active must be a boolean")
            target = (
                self._danger_zones
                if operation == "set_danger_zone"
                else self._lethal_zones
            )
            if active:
                target.add(position)
            else:
                target.discard(position)
            return

        if operation == "place_creature":
            self._creatures.add(position_from_payload())
            return

        if operation == "remove_creature":
            self._creatures.discard(position_from_payload())
            return

        if operation == "place_resource":
            position = position_from_payload()
            kind = payload.get("kind")
            quantity = payload.get("quantity", 0)
            # The literal external quantities must survive the logged
            # input interface unchanged. int(1.9), int(True), and int("2")
            # would silently assert different physical evidence.
            if (
                type(kind) is not str or kind not in RESOURCE_KINDS
                or type(quantity) is not int or quantity < 0
            ):
                raise ValueError("invalid scenario resource")
            self._resources[(position, kind)] = quantity
            return

        if operation == "set_position":
            # External world intervention, never an individual movement command.
            # Grid coordinates are discrete; silently coercing a fractional,
            # Boolean or string input could relocate the body to a different
            # location than the actual logged external scenario command.
            raw = payload.get("position")
            if (
                not isinstance(raw, Mapping)
                or set(raw) != {"x", "y"}
                or any(type(raw[k]) is not int for k in ("x", "y"))
            ):
                raise ValueError("scenario set_position requires exact integer x,y")
            position = position_from_payload()
            if position in self._obstacles:
                raise ValueError("scenario position is obstructed")
            self._position = position
            return

        if operation == "set_body":
            updates = dict(self._body.as_dict())
            for key in ("energy", "food", "water", "integrity"):
                if key in payload:
                    value = payload[key]
                    if type(value) not in (int, float):
                        raise ValueError(
                            "scenario body value must be a number, not a coercion"
                        )
                    updates[key] = float(value)
            body = BodyState(**updates)
            body.validate()
            self._body = body
            return

        if operation == "set_action_failure_schedule":
            primitive = str(payload.get("primitive"))
            raw_schedule = payload.get("schedule")
            if primitive not in PRIMITIVE_ACTIONS:
                raise ValueError("action-failure scenario requires known primitive")
            if not isinstance(raw_schedule, list) or not raw_schedule:
                raise ValueError("action-failure schedule must be a non-empty list")
            if any(type(value) is not bool for value in raw_schedule):
                raise ValueError("action-failure schedule values must be booleans")
            self._action_failure_schedules[primitive] = tuple(raw_schedule)
            self._action_failure_indices[primitive] = 0
            return

        raise ValueError(f"unsupported scenario operation: {operation}")
