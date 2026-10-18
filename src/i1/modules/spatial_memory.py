"""Entity-agnostic, first-person place recall over witnessed local edges.

No environment/world reads, no reward mapping, no motor dispatch. Every entry
is a Perception observation and every edge originates from a paid local survey.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite

from .observed_frontier_routing import ObservedSurvey, DIRECTION_BY_OFFSET


def _point(value):
    return (isinstance(value, tuple) and len(value) == 2
            and all(type(part) is int for part in value))


def _adjacent(a, b):
    return (b[0] - a[0], b[1] - a[1]) in DIRECTION_BY_OFFSET


@dataclass(frozen=True, slots=True)
class PlaceMemory:
    """Last *perceived* position, with no claim that an entity remains there."""

    observer_id: str
    entity_id: str
    entity_type: str
    position: tuple[int, int]
    observed_from: tuple[int, int]
    first_seen_step: int
    last_seen_step: int
    reached_step: int | None
    contradiction_step: int | None
    contradictions: int
    confidence: float
    provenance: str = "perceptual_capture"

    def validate(self):
        if (not isinstance(self.observer_id, str) or not self.observer_id
            or not isinstance(self.entity_id, str) or not self.entity_id
            or not isinstance(self.entity_type, str) or not self.entity_type
            or not _point(self.position) or not _point(self.observed_from)
            or (self.position != self.observed_from
                and not _adjacent(self.observed_from, self.position))
            or type(self.first_seen_step) is not int
            or type(self.last_seen_step) is not int
            or not 1 <= self.first_seen_step <= self.last_seen_step
            or (self.reached_step is not None and
                (type(self.reached_step) is not int
                 or self.reached_step < self.first_seen_step))
            or (self.contradiction_step is not None and
                (type(self.contradiction_step) is not int
                 or self.contradiction_step < self.first_seen_step))
            or type(self.contradictions) is not int
            or self.contradictions < 0
            or type(self.confidence) not in (int, float)
            or not isfinite(self.confidence)
            or not 0 <= self.confidence <= 1
            or self.provenance != "perceptual_capture"):
            raise ValueError("unfounded or malformed first-person place memory")


@dataclass(frozen=True, slots=True)
class SpatialReturnTarget:
    """One locally valid step toward a past observation, never the full route."""

    ref: str
    source_t_monde: int
    origin: tuple[int, int]
    destination: tuple[int, int]
    direction: str
    entity_id: str
    entity_type: str
    observed_position: tuple[int, int]
    visited_path: tuple[tuple[int, int], ...]
    observed_step: int
    confidence: float

    def validate(self):
        if (type(self.source_t_monde) is not int or self.source_t_monde < 1
            or type(self.observed_step) is not int
            or not 1 <= self.observed_step <= self.source_t_monde
            or not self.entity_id or not self.entity_type
            or not _point(self.origin) or not _point(self.destination)
            or not _point(self.observed_position)
            or not isinstance(self.visited_path, tuple)
            or not 2 <= len(self.visited_path) <= 9
            or self.visited_path[0] != self.origin
            or self.visited_path[1] != self.destination
            or self.visited_path[-1] != self.observed_position
            or len(set(self.visited_path)) != len(self.visited_path)
            or any(not _point(p) for p in self.visited_path)
            or any(not _adjacent(a, b) for a, b in
                   zip(self.visited_path, self.visited_path[1:]))
            or DIRECTION_BY_OFFSET.get((
                self.destination[0] - self.origin[0],
                self.destination[1] - self.origin[1],
            )) != self.direction
            or type(self.confidence) not in (int, float)
            or not isfinite(self.confidence)
            or not 0 < self.confidence <= 1):
            raise ValueError("spatial return is not a bounded witnessed route")
        canonical = (
            f"place:{self.entity_id}:at:{self.observed_position[0]}:"
            f"{self.observed_position[1]}:from:{self.origin[0]}:"
            f"{self.origin[1]}:via:{self.destination[0]}:"
            f"{self.destination[1]}"
        )
        if self.ref != canonical:
            raise ValueError("noncanonical entity-place target")


def find_spatial_returns(
    *, origin: tuple[int, int], visits: frozenset[tuple[int, int]],
    surveys: tuple[ObservedSurvey, ...],
    places: tuple[PlaceMemory, ...],
    current_free_neighbors: frozenset[tuple[int, int]],
    current_world_step: int, max_hops: int = 8, max_candidates: int = 32,
) -> tuple[SpatialReturnTarget, ...]:
    """Return bounded *alternatives*, never preselect one cognitive winner.

    All edges originate from witnessed local surveys and the first movement
    must be passable in today's actual Perception. This only ranks retrieval
    by confidence/path length. Stage8/Competition decides their usefulness.
    """
    if (not _point(origin) or not isinstance(visits, frozenset)
        or origin not in visits or len(visits) > 1024
        or any(not _point(p) for p in visits)
        or not isinstance(surveys, tuple) or len(surveys) > 1024
        or not isinstance(places, tuple) or len(places) > 1024
        or not isinstance(current_free_neighbors, frozenset)
        or any(not _point(p) or not _adjacent(origin, p)
               for p in current_free_neighbors)
        or type(current_world_step) is not int or current_world_step < 1
        or type(max_hops) is not int or not 1 <= max_hops <= 8
        or type(max_candidates) is not int or not 1 <= max_candidates <= 32):
        raise ValueError("invalid first-person route context")
    known = {}
    for survey in surveys:
        if not isinstance(survey, ObservedSurvey):
            raise ValueError("untrusted survey object")
        survey.validate()
        if (survey.world_step > current_world_step
            or survey.position not in visits
            or (survey.world_step == current_world_step
                and survey.position != origin)
            or survey.position in known):
            raise ValueError("future, duplicate or unowned route survey")
        known[survey.position] = survey
    remembered = {}
    for place in places:
        if not isinstance(place, PlaceMemory):
            raise ValueError("untrusted place memory")
        place.validate()
        if (place.last_seen_step > current_world_step
            or any(t is not None and t > current_world_step for t in
                   (place.reached_step, place.contradiction_step))
            or place.entity_id in remembered):
            raise ValueError("future or duplicate entity memory")
        remembered[place.entity_id] = place

    # Avoid a compulsory "return" when the individual already stands there.
    destinations = {}
    for place in remembered.values():
        if place.position != origin and place.confidence > 0:
            destinations.setdefault(place.position, []).append(place)

    queue = deque([(origin, (origin,))])
    seen = {origin}
    options = []
    while queue:
        node, path = queue.popleft()
        if len(path) - 1 >= max_hops:
            continue
        # The origin is always governed by CURRENT perception, not old surveys.
        edges = (current_free_neighbors if node == origin
                 else frozenset(known[node].free_neighbors)
                 if node in known else frozenset())
        for nxt in sorted(edges):
            if not _adjacent(node, nxt) or nxt in path:
                continue
            candidate_path = path + (nxt,)
            for place in destinations.get(nxt, ()):
                age = current_world_step - place.last_seen_step
                quality = (place.confidence / (1 + age / 240.0)
                           / (1 + 0.08 * (len(candidate_path) - 2)))
                if quality < 0.12:
                    continue
                direction = DIRECTION_BY_OFFSET[(
                    candidate_path[1][0] - origin[0],
                    candidate_path[1][1] - origin[1],
                )]
                target = SpatialReturnTarget(
                    ref=(f"place:{place.entity_id}:at:{nxt[0]}:{nxt[1]}:"
                         f"from:{origin[0]}:{origin[1]}:"
                         f"via:{candidate_path[1][0]}:{candidate_path[1][1]}"),
                    source_t_monde=current_world_step, origin=origin,
                    destination=candidate_path[1], direction=direction,
                    entity_id=place.entity_id, entity_type=place.entity_type,
                    observed_position=nxt, visited_path=candidate_path,
                    observed_step=place.first_seen_step, confidence=quality,
                )
                target.validate()
                options.append(target)
            if nxt in visits and nxt in known and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, candidate_path))
    # Competing *entities*, not three different ways to the same entity.
    # Otherwise a single well-connected place can monopolize the small
    # deliberation capacity before Competition sees another known site.
    selected = []
    already_seen_entities = set()
    for target in sorted(options, key=lambda target: (
        -target.confidence, len(target.visited_path),
        target.entity_type, target.entity_id, target.direction,
    )):
        if target.entity_id in already_seen_entities:
            continue
        already_seen_entities.add(target.entity_id)
        selected.append(target)
        if len(selected) >= max_candidates:
            break
    return tuple(selected)


def find_spatial_return(
    *, origin: tuple[int, int], visits: frozenset[tuple[int, int]],
    surveys: tuple[ObservedSurvey, ...],
    places: tuple[PlaceMemory, ...],
    current_free_neighbors: frozenset[tuple[int, int]],
    current_world_step: int, max_hops: int = 8,
) -> SpatialReturnTarget | None:
    """Compatibility adapter for the original one-target scientific tests."""
    candidates = find_spatial_returns(
        origin=origin, visits=visits, surveys=surveys, places=places,
        current_free_neighbors=current_free_neighbors,
        current_world_step=current_world_step, max_hops=max_hops,
        max_candidates=1,
    )
    return candidates[0] if candidates else None
