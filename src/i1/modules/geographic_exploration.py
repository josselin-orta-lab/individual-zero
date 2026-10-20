"""Versioned local-frontier curiosity from one accessible Perception capture.

Stage-11 development-only slice of EN MVP v1.2.1 section 14 / INV-06,14.
No map oracle, world physics, reward, counterfactual or action sender access.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from math import isfinite
from typing import Mapping

from .observed_frontier_routing import ObservedSurvey, GeographicTransitTarget
from .spatial_memory import PlaceMemory, SpatialReturnTarget, EntityMotionDiagnosis

DIRECTION_DELTAS = {"north": (0, -1), "east": (1, 0),
                    "south": (0, 1), "west": (-1, 0)}
DIRECTION_ORDER = tuple(DIRECTION_DELTAS)


@dataclass(frozen=True, slots=True)
class GeographicExplorationConfig:
    version: str
    novelty_weight: float
    max_distinct_sites: int
    max_targets_per_cycle: int
    observe_routes: bool = False
    refresh_surveys: bool = False
    remember_entities: bool = False
    max_place_candidates: int = 1

    def validate(self) -> None:
        if not isinstance(self.version, str) or not self.version:
            raise ValueError("geographic curiosity needs a version")
        if (type(self.novelty_weight) not in (int, float)
            or not isfinite(self.novelty_weight)
            or not 0 <= self.novelty_weight <= 1):
            raise ValueError("geographic P-48 interest must be bounded")
        if type(self.observe_routes) is not bool:
            raise ValueError("route survey flag must be boolean")
        if type(self.refresh_surveys) is not bool:
            raise ValueError("survey refresh flag must be boolean")
        if (type(self.max_place_candidates) is not int
            or not 1 <= self.max_place_candidates <= 4):
            raise ValueError("invalid bounded place candidate count")
        if type(self.remember_entities) is not bool:
            raise ValueError("entity-place flag must be boolean")
        if self.remember_entities and not self.observe_routes:
            raise ValueError("entity-place recall requires paid route observations")
        if self.refresh_surveys and not self.observe_routes:
            raise ValueError("survey refresh requires opted-in route observations")
        if (type(self.max_distinct_sites) is not int or self.max_distinct_sites < 1
            or type(self.max_targets_per_cycle) is not int
            or not 1 <= self.max_targets_per_cycle <= 4):
            raise ValueError("invalid geographic capacity")


@dataclass(frozen=True, slots=True)
class GeographicTarget:
    ref: str
    source_t_monde: int
    origin: tuple[int, int]
    destination: tuple[int, int]
    direction: str

    def validate(self) -> None:
        if (not self.ref or type(self.source_t_monde) is not int
            or self.source_t_monde < 1 or self.direction not in DIRECTION_DELTAS
            or not isinstance(self.origin, tuple) or len(self.origin) != 2
            or not isinstance(self.destination, tuple) or len(self.destination) != 2
            or any(type(x) is not int for x in (*self.origin, *self.destination))):
            raise ValueError("invalid local frontier target")
        dx, dy = DIRECTION_DELTAS[self.direction]
        if self.destination != (self.origin[0] + dx, self.origin[1] + dy):
            raise ValueError("target is not an adjacent geographic destination")
        if self.ref != (
            f"frontier:{self.destination[0]}:{self.destination[1]}:"
            f"from:{self.origin[0]}:{self.origin[1]}"
        ):
            raise ValueError("invalid canonical geographic target reference")


class GeographicExploration:
    """Private state of the canonical Exploration owner, not a second owner."""

    def __init__(self, config: GeographicExplorationConfig) -> None:
        config.validate()
        self.config = config
        self._visits: dict[tuple[int, int], int] = {}
        self._last_capture: tuple[int, int, int] | None = None
        self._offered: tuple[GeographicTarget, ...] = ()
        self._surveys: dict[tuple[int, int], ObservedSurvey] = {}
        self._transit_offered: tuple[GeographicTransitTarget, ...] = ()
        self._places: dict[str, PlaceMemory] = {}
        self._place_observer_id: str | None = None
        self._place_offered: tuple[SpatialReturnTarget, ...] = ()
        self._motion: dict[str, EntityMotionDiagnosis] = {}
        self._motion_updates: tuple[EntityMotionDiagnosis, ...] = ()

    def _snapshot_schema(self) -> str:
        if self.config.remember_entities:
            return "geographic-exploration-v5-entity-motion"
        if self.config.refresh_surveys:
            return "geographic-exploration-v3-survey-refresh"
        if self.config.observe_routes:
            return "geographic-exploration-v2-survey"
        return "geographic-exploration-v1"

    @property
    def place_memories(self) -> tuple[PlaceMemory, ...]:
        """First-person last sightings, never a hidden world map."""
        return tuple(self._places[key] for key in sorted(self._places))

    @property
    def motion_diagnoses(self) -> tuple[EntityMotionDiagnosis, ...]:
        return tuple(self._motion[k] for k in sorted(self._motion))

    @property
    def motion_updates(self) -> tuple[EntityMotionDiagnosis, ...]:
        return self._motion_updates

    def _observe_motion(self, *, capture, observer_id: str, visible: dict) -> None:
        """Only unique sightings in uninterrupted physical captures are linked.

        Multiple same-kind entities, gaps and unobserved replacements break
        the tentative link. No use of the raw sensor label as an identity.
        """
        counts = {}
        for kind, position in visible:
            counts.setdefault(kind, []).append(position)
        updated = []
        active = {}
        for kind, positions in sorted(counts.items()):
            if len(positions) != 1:
                continue
            point = positions[0]
            previous = self._motion.get(kind)
            if (previous is not None
                and previous.last_seen_step == capture.t_monde):
                active[kind] = previous
                continue
            if (previous is not None
                and previous.last_seen_step == capture.t_monde - 1):
                moved = point != previous.last_position
                record = replace(
                    previous, last_seen_step=capture.t_monde,
                    last_position=point,
                    observations=previous.observations + 1,
                    observed_moves=previous.observed_moves + int(moved),
                    observed_stays=previous.observed_stays + int(not moved),
                )
            else:
                record = EntityMotionDiagnosis(
                    observer_id=observer_id,
                    trace_ref=f"motion:{kind}:{capture.t_monde}:{point[0]}:{point[1]}",
                    entity_type=kind, first_seen_step=capture.t_monde,
                    last_seen_step=capture.t_monde,
                    first_position=point, last_position=point,
                    observations=1, observed_moves=0, observed_stays=0,
                )
            record.validate()
            active[kind] = record
            updated.append(record)
        self._motion = active
        self._motion_updates = tuple(updated)

    def observe_entities(self, capture, *, observer_id: str) -> tuple[PlaceMemory, ...]:
        """Store only witnessed visible_entities, with repeat-step idempotence.

        Re-observing a known site updates its confidence; a fully visible but
        missing entity weakens confidence. Remote absence does not.
        """
        if not self.config.remember_entities:
            return ()
        if (not isinstance(observer_id, str) or not observer_id
            or self._last_capture !=
                (capture.t_monde, capture.x, capture.y)
            or (self._place_observer_id is not None
                and self._place_observer_id != observer_id)):
            raise ValueError("entity memory must belong to this physical life")
        visible = {}
        for entity in capture.visible_entities:
            position = (entity.x, entity.y)
            if (not isinstance(entity.entity_id, str) or not entity.entity_id
                or not isinstance(entity.entity_type, str) or not entity.entity_type
                or (position != (capture.x, capture.y)
                    and (position[0]-capture.x, position[1]-capture.y)
                    not in DIRECTION_DELTAS.values())
                or (entity.entity_type, position) in visible):
                raise ValueError("invalid or duplicated first-person entity")
            visible[(entity.entity_type, position)] = entity
        self._place_observer_id = observer_id
        self._observe_motion(capture=capture, observer_id=observer_id, visible=visible)
        updates = []
        for (kind, position), entity in sorted(visible.items()):
            key = f"sighting:{kind}:{position[0]}:{position[1]}"
            old = self._places.get(key)
            if old is None and len(self._places) >= self.config.max_distinct_sites:
                continue
            if old is not None and old.last_seen_step == capture.t_monde:
                if old.position != (entity.x, entity.y):
                    raise ValueError("same-step entity location contradiction")
                continue
            if old is not None and old.entity_type != entity.entity_type:
                raise ValueError("entity type cannot silently change for one ID")
            position = (entity.x, entity.y)
            reached = (
                capture.t_monde if position == (capture.x, capture.y) else
                old.reached_step if old is not None and old.position == position
                else None
            )
            memory = PlaceMemory(
                observer_id=observer_id, entity_id=key,
                entity_type=entity.entity_type, position=position,
                observed_from=(capture.x, capture.y),
                first_seen_step=(capture.t_monde if old is None
                                 else old.first_seen_step),
                last_seen_step=capture.t_monde,
                reached_step=reached,
                contradiction_step=None if old is None else old.contradiction_step,
                contradictions=0 if old is None else old.contradictions,
                confidence=min(0.9, 0.55 if old is None
                               else old.confidence + 0.15),
                perceived_entity_id=entity.entity_id,
            )
            memory.validate()
            self._places[key] = memory
            updates.append(memory)
        local_positions = {(capture.x, capture.y)}
        local_positions.update((cell.x, cell.y) for cell in capture.adjacent)
        for key, old in tuple(self._places.items()):
            if ((old.entity_type, old.position) in visible
                or old.last_seen_step == capture.t_monde
                or old.position not in local_positions
                or old.contradiction_step == capture.t_monde):
                continue
            # A missing entity at its last *currently sensed* position might
            # have disappeared or moved, not proof the whole type is absent.
            memory = replace(old,
                contradiction_step=capture.t_monde,
                contradictions=old.contradictions + 1,
                confidence=old.confidence * 0.25,
            )
            memory.validate()
            self._places[key] = memory
            updates.append(memory)
        return tuple(updates)

    def freeze_places(self, targets: tuple[SpatialReturnTarget, ...]) -> None:
        """Only unchanged, physically grounded candidates survive Phase-1."""
        if not isinstance(targets, tuple) or len(targets) > self.config.max_place_candidates:
            raise ValueError("invalid offered place targets")
        accepted = []
        for target in targets:
            target.validate()
            memory = self._places.get(target.entity_id)
            if (not self.config.remember_entities or memory is None
                or target.observed_position != memory.position
                or target.entity_type != memory.entity_type
                or target.observed_step != memory.first_seen_step
                or self._last_capture is None
                or target.origin != self._last_capture[1:]
                or target.source_t_monde != self._last_capture[0]
                or any(point not in self._visits
                       for point in target.visited_path[:-1])
                or any(a not in self._surveys
                       or b not in self._surveys[a].free_neighbors
                       for a, b in zip(
                           target.visited_path[1:-1],
                           target.visited_path[2:]))
                or target.confidence > memory.confidence):
                # A new perception can contradict the Phase-0 frozen memory.
                # Discard this proposal, never crash the living individual.
                continue
            accepted.append(target)
        if len({t.ref for t in accepted}) != len(accepted):
            raise ValueError("duplicate place offer")
        self._place_offered = tuple(accepted)

    def freeze_place(self, target: SpatialReturnTarget | None) -> None:
        """Backwards-compatible one-target interface."""
        self.freeze_places(() if target is None else (target,))

    @property
    def place_offered(self) -> tuple[SpatialReturnTarget, ...]:
        return self._place_offered

    def place_for(self, option) -> SpatialReturnTarget | None:
        """Read only the currently offered, funded and goal-linked option."""
        motive = getattr(option, "motive_ref", None)
        if (getattr(motive, "type", None) != "place_memory"
            or getattr(option, "provenance", None) != "memory"):
            return None
        for target in self._place_offered:
            if (motive.id == target.ref
                and option.id ==
                    f"option:place-memory:{target.ref}"):
                return target
        return None

    @property
    def distinct_sites(self) -> int:
        return len(self._visits)

    def has_recorded_site(self, position: tuple[int, int]) -> bool:
        """Read the individual's own observed visit ledger in O(1).

        A check here neither inspects terrain nor creates a visit. The same
        private dictionary remains the authoritative source for observations.
        """
        if (type(position) is not tuple or len(position) != 2
                or any(type(v) is not int for v in position)):
            raise ValueError("observed geographic coordinates must be integers")
        return position in self._visits

    @property
    def visit_count(self) -> int:
        return sum(self._visits.values())

    @property
    def offered(self) -> tuple[GeographicTarget, ...]:
        return self._offered

    def observe_capture(self, capture) -> bool:
        """Only a *new* world-step Perception position counts as a visit.

        Staying in place for many steps does not fabricate new locations;
        duplicate deliberation cycles within one step are idempotent.
        """
        t, x, y = capture.t_monde, capture.x, capture.y
        if (any(type(v) is not int for v in (t, x, y)) or t < 1):
            raise ValueError("geographic visits require real world-step coordinates")
        if self._last_capture is not None:
            old_t, old_x, old_y = self._last_capture
            if t < old_t or (t == old_t and (x, y) != (old_x, old_y)):
                raise ValueError("contradictory/retrograde physical capture")
            if ((x, y) not in self._visits
                and len(self._visits) >= self.config.max_distinct_sites):
                raise ValueError("geographic visit register capacity exhausted")
            if t > old_t:
                self._transit_offered = ()
                self._place_offered = ()
            if t == old_t or (x, y) == (old_x, old_y):
                self._last_capture = (t, x, y)
                return False
        if (x, y) not in self._visits and len(self._visits) >= self.config.max_distinct_sites:
            # Fail closed, never evict a known site and rediscover it for reward.
            raise ValueError("geographic visit register capacity exhausted")
        self._visits[(x, y)] = self._visits.get((x, y), 0) + 1
        self._last_capture = (t, x, y)
        return True

    @property
    def transit_offered(self) -> tuple[GeographicTransitTarget, ...]:
        return self._transit_offered

    @property
    def surveys(self) -> tuple[ObservedSurvey, ...]:
        return tuple(self._surveys[key] for key in sorted(self._surveys))

    def phase_observation_fixed_fields(self):
        """Snapshot the immutable geographic fields of a paid Phase-1 pass.

        The visit counters and survey dictionary are intentionally omitted:
        their only mutations in Stage11's paid hook have explicit boolean
        results. The captured tuple fields are frozen and never changed in
        place. This is NOT a replacement for the full M11 causal export.
        """
        return (
            self._last_capture,
            self._offered,
            self._transit_offered,
        )

    def observed_survey_at(
        self, position: tuple[int, int],
    ) -> ObservedSurvey | None:
        """Read a witnessed local survey without sorting every known survey."""
        if (type(position) is not tuple or len(position) != 2
                or any(type(v) is not int for v in position)):
            raise ValueError("survey coordinates must be real observations")
        return self._surveys.get(position)

    def record_survey(self, capture) -> bool:
        """Only an accepted Exploration observation may store local topology.

        The owner never consumes a world layout or a future observation.
        A second cognitive cycle in the same world step is idempotent.
        """
        if not self.config.observe_routes:
            return False
        position = (capture.x, capture.y)
        if position not in self._visits or self._last_capture != (
            capture.t_monde, capture.x, capture.y,
        ):
            raise ValueError("survey requires actual current physical visit")
        cells = tuple(capture.adjacent)
        if (len(cells) != 4
            or {cell.direction for cell in cells} != set(DIRECTION_DELTAS)):
            raise ValueError("incomplete local survey is not route evidence")
        for cell in cells:
            dx, dy = DIRECTION_DELTAS[cell.direction]
            if (cell.x, cell.y) != (capture.x + dx, capture.y + dy):
                raise ValueError("survey neighbor coordinate mismatch")
            if type(cell.passable) is not bool or type(cell.creature) is not bool:
                raise ValueError("unknown passability is not a free neighbor")
        record = ObservedSurvey(
            position=position, world_step=capture.t_monde,
            free_neighbors=tuple(sorted(
                (c.x, c.y) for c in cells
                if c.passable is True and c.creature is False
            )),
        )
        record.validate()
        old = self._surveys.get(position)
        if old is not None:
            if not self.config.refresh_surveys:
                return False
            if record.world_step < old.world_step:
                raise ValueError("retrograde survey revision")
            if record.world_step == old.world_step:
                if record.free_neighbors != old.free_neighbors:
                    raise ValueError("conflicting same-world-step physical survey")
                return False
            if record.free_neighbors == old.free_neighbors:
                return False
            # Replace only the *current* local physical adjacency after a
            # new world-step capture and accepted Exploration observation.
            # The visit ledger and its novelty count are never rewritten.
            self._surveys[position] = record
            return True
        if len(self._surveys) >= self.config.max_distinct_sites:
            raise ValueError("route survey capacity exceeded")
        self._surveys[position] = record
        return True

    def cibles(
        self, capture, *, degraded: bool = False,
        inadmissible_directions: frozenset[str] = frozenset(),
        candidate_limit: int | None = None,
    ) -> tuple[GeographicTarget, ...]:
        """Bound the visible frontier after the read-only Action Control veto.

        The caller supplies only directions that Action Control explicitly
        marked INADMISSIBLE for this captured context. Unknown directions
        must NOT enter this set. No private safety cache is created here:
        the canonical policy can change on a later decision or world step.
        """
        if (
            not isinstance(inadmissible_directions, frozenset)
            or not inadmissible_directions <= set(DIRECTION_DELTAS)
        ):
            raise ValueError("invalid Action Control excluded directions")
        if (
            candidate_limit is not None
            and (
                type(candidate_limit) is not int
                or not 1 <= candidate_limit <= len(DIRECTION_DELTAS)
            )
        ):
            raise ValueError("raw frontier limit must be 1..4")
        if degraded or self.config.novelty_weight == 0:
            return ()
        t, x, y = capture.t_monde, capture.x, capture.y
        if (any(type(v) is not int for v in (t, x, y)) or t < 1):
            raise ValueError("geographic targets require an accessible capture")
        if len(self._visits) >= self.config.max_distinct_sites:
            return ()
        seen = set()
        candidates = []
        for cell in capture.adjacent:
            direction = cell.direction
            if direction not in DIRECTION_DELTAS or direction in seen:
                raise ValueError("noncanonical or duplicate Perception neighbor")
            seen.add(direction)
            dx, dy = DIRECTION_DELTAS[direction]
            destination = (x + dx, y + dy)
            if (type(cell.x) is not int or type(cell.y) is not int
                or (cell.x, cell.y) != destination):
                raise ValueError("Perception neighbor position mismatch")
            if (
                cell.passable is not True or cell.creature is True
                or destination in self._visits
                or direction in inadmissible_directions
            ):
                continue
            target = GeographicTarget(
                ref=f"frontier:{destination[0]}:{destination[1]}:from:{x}:{y}",
                source_t_monde=t, origin=(x, y),
                destination=destination, direction=direction,
            )
            target.validate()
            candidates.append(target)
        return tuple(sorted(
            candidates, key=lambda q: (DIRECTION_ORDER.index(q.direction), q.ref)
        )[:(
            self.config.max_targets_per_cycle
            if candidate_limit is None else candidate_limit
        )])

    def freeze_targets(self, targets: tuple[GeographicTarget, ...]) -> None:
        """Accept pre-phase-grounded targets through the phase-3 service.

        Only Planning's funded, filtered options may be offered for intrinsic
        evaluation. This owner never invents a destination from the plan.
        """
        if (not isinstance(targets, tuple)
            or len(targets) > self.config.max_targets_per_cycle):
            raise ValueError("invalid offered frontier count")
        for target in targets:
            target.validate()
            if target.destination in self._visits:
                raise ValueError("cannot offer an already visited destination")
            if self._last_capture is not None and (
                target.source_t_monde != self._last_capture[0]
                or target.origin != self._last_capture[1:]
            ):
                raise ValueError("offered target mismatches current physical capture")
        if len({t.ref for t in targets}) != len(targets):
            raise ValueError("duplicate geographic target")
        self._offered = targets

    def freeze_transits(
        self, targets: tuple[GeographicTransitTarget, ...],
    ) -> None:
        """Freeze only funded transit options tied to witnessed topology.

        A transit is NOT a novel visit. Its objective must remain unvisited,
        and every intermediate hop must already have a physical survey.
        """
        if (not isinstance(targets, tuple)
            or len(targets) > 1
            or len(targets) > self.config.max_targets_per_cycle
            or (targets and not self.config.observe_routes)):
            raise ValueError("invalid offered geographic transit count")
        for target in targets:
            if not isinstance(target, GeographicTransitTarget):
                raise ValueError("not a canonical route target")
            target.validate()
            if (self._last_capture is None
                or target.source_t_monde != self._last_capture[0]
                or target.origin != self._last_capture[1:]
                or target.observed_frontier in self._visits
                or target.destination not in self._visits
                # The route is validated to contain at most nine typed
                # coordinates. Probe the existing ledger, never rebuild it.
                or any(site not in self._visits
                       for site in target.visited_path)):
                raise ValueError("route transit not tied to physical visit ledger")
            for a, b in zip(target.visited_path, target.visited_path[1:]):
                if a not in self._surveys or b not in self._surveys[a].free_neighbors:
                    raise ValueError("route crosses a non-observed transit edge")
            objective_source = self._surveys.get(target.visited_path[-1])
            if (objective_source is None
                or target.observed_frontier not in objective_source.free_neighbors
                or target.objective_observed_step != objective_source.world_step):
                raise ValueError("route objective not witnessed at physical site")
        self._transit_offered = targets

    def transit_for(self, option) -> GeographicTransitTarget | None:
        motive = getattr(option, "motive_ref", None)
        if (getattr(motive, "type", None) != "cible_exploration"
            or getattr(option, "provenance", None) != "exploration"
            or getattr(option, "goal_ref", None) is not None):
            return None
        for target in self._transit_offered:
            if (motive.id == target.ref
                and option.id == (
                    f"option:geographic:{target.ref}"
                )
                and target.observed_frontier not in self._visits
                and target.destination in self._visits):
                return target
        return None

    def target_for(self, option) -> GeographicTarget | None:
        motive = getattr(option, "motive_ref", None)
        if (getattr(motive, "type", None) != "cible_exploration"
            or getattr(option, "provenance", None) != "exploration"
            or getattr(option, "goal_ref", None) is not None):
            return None
        for target in self._offered:
            if (motive.id == target.ref and option.id == (
                f"option:geographic:{target.ref}"
            ) and target.destination not in self._visits):
                return target
        return None

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self._snapshot_schema(),
            "version": self.config.version,
            "visits": [
                [x, y, count] for (x, y), count in sorted(self._visits.items())
            ],
            "last_capture": (
                None if self._last_capture is None
                else list(self._last_capture)
            ),
            "offered": [asdict(t) for t in self._offered],
            **({"entity_places": [asdict(x) for x in self.place_memories],
                "place_observer_id": self._place_observer_id,
                "place_offered": [asdict(x) for x in self._place_offered],
                "motion_diagnoses": [asdict(x) for x in self.motion_diagnoses],
            } if self.config.remember_entities else {}),
            **({
                "surveys": [asdict(x) for x in self.surveys],
                "transit_offered": [asdict(x) for x in self._transit_offered],
            } if self.config.observe_routes else {}),
        }

    def restore_causal_state(self, state: object) -> None:
        if (not isinstance(state, Mapping)
            or state.get("schema") != self._snapshot_schema()
            or state.get("version") != self.config.version
            or not isinstance(state.get("visits"), list)
            or not isinstance(state.get("offered"), list)):
            raise ValueError("incompatible geographical snapshot")
        visited = {}
        for raw in state["visits"]:
            if (not isinstance(raw, (tuple, list)) or len(raw) != 3
                or any(type(v) is not int for v in raw)
                or raw[2] < 1 or (raw[0], raw[1]) in visited):
                raise ValueError("corrupt geographic visit counter")
            visited[(raw[0], raw[1])] = raw[2]
        if len(visited) > self.config.max_distinct_sites:
            raise ValueError("geographic visit capacity exceeded")
        raw_last = state.get("last_capture")
        if raw_last is None:
            last = None
        else:
            if (not isinstance(raw_last, (tuple, list)) or len(raw_last) != 3
                or any(type(v) is not int for v in raw_last)
                or raw_last[0] < 1
                or (raw_last[1], raw_last[2]) not in visited):
                raise ValueError("invalid last geographic capture")
            last = tuple(raw_last)
        # Real owner exports always pair an observed visit ledger with its
        # latest physical Perception capture. A nonempty visit history with
        # no last capture is not an alternate empty state: accepting it
        # silently breaks replay chronology, especially at cold import.
        # Reject before assigning any restored owner fields (atomic failure).
        if (last is None) != (not visited):
            raise ValueError("visit ledger and last physical capture disagree")
        offered = []
        for raw in state["offered"]:
            if not isinstance(raw, Mapping) or set(raw) != {
                "ref", "source_t_monde", "origin", "destination", "direction"
            }:
                raise ValueError("corrupt offered geographic target")
            target = GeographicTarget(
                ref=raw["ref"], source_t_monde=raw["source_t_monde"],
                origin=tuple(raw["origin"]),
                destination=tuple(raw["destination"]),
                direction=raw["direction"],
            )
            target.validate()
            if (last is None or target.source_t_monde != last[0]
                or target.origin != last[1:]
                or target.destination in visited):
                raise ValueError("stale geographic target in snapshot")
            offered.append(target)
        if len(offered) > self.config.max_targets_per_cycle or len({
            target.ref for target in offered
        }) != len(offered):
            raise ValueError("invalid offered target counts")
        restored_surveys = {}
        if self.config.observe_routes:
            raw_surveys = state.get("surveys")
            if not isinstance(raw_surveys, list) or len(raw_surveys) > len(visited):
                raise ValueError("corrupt route-survey snapshot")
            for row in raw_surveys:
                if not isinstance(row, Mapping) or set(row) != {
                    "position", "world_step", "free_neighbors",
                }:
                    raise ValueError("malformed snapshot survey")
                survey = ObservedSurvey(
                    position=tuple(row["position"]),
                    world_step=row["world_step"],
                    free_neighbors=tuple(
                        tuple(p) for p in row["free_neighbors"]
                    ),
                )
                survey.validate()
                if (
                    survey.position not in visited
                    or survey.position in restored_surveys
                    or last is None or survey.world_step > last[0]
                ):
                    raise ValueError("unowned or future snapshot survey")
                restored_surveys[survey.position] = survey
        elif "surveys" in state or "transit_offered" in state:
            raise ValueError("legacy geographic snapshot cannot contain routing")
        restored_transits = ()
        if self.config.observe_routes:
            raw_transits = state.get("transit_offered")
            if not isinstance(raw_transits, list) or len(raw_transits) > 1:
                raise ValueError("invalid routed target snapshot")
            transits = []
            for row in raw_transits:
                if not isinstance(row, Mapping) or set(row) != {
                    "ref", "source_t_monde", "origin", "destination",
                    "direction", "observed_frontier", "visited_path",
                    "objective_observed_step",
                }:
                    raise ValueError("invalid routed target snapshot fields")
                transit = GeographicTransitTarget(
                    ref=row["ref"], source_t_monde=row["source_t_monde"],
                    origin=tuple(row["origin"]),
                    destination=tuple(row["destination"]),
                    direction=row["direction"],
                    observed_frontier=tuple(row["observed_frontier"]),
                    visited_path=tuple(tuple(p) for p in row["visited_path"]),
                    objective_observed_step=row["objective_observed_step"],
                )
                transit.validate()
                transits.append(transit)
            # Validate the complete prospective owner before any mutation.
            trial = GeographicExploration(self.config)
            trial._visits = visited
            trial._last_capture = last
            trial._surveys = restored_surveys
            trial.freeze_transits(tuple(transits))
            restored_transits = trial.transit_offered
        places = {}
        place_observer = None
        place_offered = ()
        if self.config.remember_entities:
            raw_places = state.get("entity_places")
            place_observer = state.get("place_observer_id")
            if (not isinstance(raw_places, list)
                or len(raw_places) > self.config.max_distinct_sites
                or (place_observer is not None and
                    (not isinstance(place_observer, str) or not place_observer))
                or (bool(raw_places) and place_observer is None)):
                raise ValueError("invalid entity-place memory snapshot")
            for row in raw_places:
                if (not isinstance(row, Mapping)
                    or set(row) != set(PlaceMemory.__dataclass_fields__)):
                    raise ValueError("malformed entity-place snapshot")
                place = PlaceMemory(**{
                    **row, "position": tuple(row["position"]),
                    "observed_from": tuple(row["observed_from"]),
                })
                place.validate()
                if (place.entity_id in places or place.observer_id != place_observer
                    or last is None or place.last_seen_step > last[0]
                    or any(t is not None and t > last[0] for t in
                           (place.reached_step, place.contradiction_step))):
                    raise ValueError("future, duplicate or alien entity-place memory")
                places[place.entity_id] = place
            raw_offered = state.get("place_offered")
            if not isinstance(raw_offered, list) or len(raw_offered) > self.config.max_place_candidates:
                raise ValueError("invalid offered entity-place snapshot")
            place_targets = []
            for row in raw_offered:
                if (not isinstance(row, Mapping)
                    or set(row) != set(SpatialReturnTarget.__dataclass_fields__)):
                    raise ValueError("invalid entity-place target fields")
                target = SpatialReturnTarget(**{
                    **row, "origin": tuple(row["origin"]),
                    "destination": tuple(row["destination"]),
                    "observed_position": tuple(row["observed_position"]),
                    "visited_path": tuple(tuple(p) for p in row["visited_path"]),
                })
                target.validate()
                site = places.get(target.entity_id)
                if (site is None or last is None
                    or target.source_t_monde != last[0]
                    or target.origin != last[1:]
                    or target.observed_position != site.position
                    or target.entity_type != site.entity_type
                    or target.observed_step != site.first_seen_step
                    or target.confidence > site.confidence
                    or any(point not in visited for point in
                           target.visited_path[:-1])):
                    raise ValueError("stale entity-place snapshot target")
                place_targets.append(target)
            place_offered = tuple(place_targets)
        elif any(key in state for key in
                 ("entity_places", "place_offered", "place_observer_id")):
            raise ValueError("unexpected place memory in legacy snapshot")
        restored_motion = {}
        if self.config.remember_entities:
            raw_motion = state.get("motion_diagnoses")
            if (not isinstance(raw_motion, list)
                or len(raw_motion) > self.config.max_distinct_sites):
                raise ValueError("invalid motion snapshot")
            for row in raw_motion:
                if (not isinstance(row, Mapping)
                    or set(row) != set(EntityMotionDiagnosis.__dataclass_fields__)):
                    raise ValueError("malformed motion diagnosis")
                record = EntityMotionDiagnosis(**{
                    **row, "first_position": tuple(row["first_position"]),
                    "last_position": tuple(row["last_position"]),
                })
                record.validate()
                if (last is None or record.last_seen_step > last[0]
                    or record.observer_id != place_observer
                    or record.entity_type in restored_motion):
                    raise ValueError("foreign or future motion diagnosis")
                restored_motion[record.entity_type] = record
        elif "motion_diagnoses" in state:
            raise ValueError("unexpected motion diagnosis")
        self._motion = restored_motion
        self._motion_updates = ()
        self._places = places
        self._place_observer_id = place_observer
        self._place_offered = place_offered
        self._visits = visited
        self._last_capture = last
        self._offered = tuple(offered)
        self._surveys = restored_surveys
        self._transit_offered = restored_transits
