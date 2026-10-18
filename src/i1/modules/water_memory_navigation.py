"""First-person water-place recall and bounded observed-edge return (I1 only).

Pure Stage-11 reasoning: never reads WorldBody, hidden layouts, or operator maps.
The live owner of WaterPlace and its publication is GeographicExploration.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite

from .observed_frontier_routing import ObservedSurvey, DIRECTION_BY_OFFSET


def _point(value):
    return (isinstance(value, tuple) and len(value) == 2
            and all(type(v) is int for v in value))


def _adjacent(a, b):
    return ((b[0] - a[0], b[1] - a[1]) in DIRECTION_BY_OFFSET)


@dataclass(frozen=True, slots=True)
class WaterPlace:
    observer_id: str
    position: tuple[int, int]
    observed_from: tuple[int, int]
    first_seen_step: int
    last_confirmed_step: int
    reached_step: int | None
    used_step: int | None
    contradiction_step: int | None
    contradictions: int
    confidence: float
    source: str = "perceptual_capture"

    def validate(self):
        if (not self.observer_id or not _point(self.position)
            or not _point(self.observed_from)
            or (self.position != self.observed_from
                and not _adjacent(self.observed_from, self.position))
            or type(self.first_seen_step) is not int
            or type(self.last_confirmed_step) is not int
            or not 1 <= self.first_seen_step <= self.last_confirmed_step
            or any(v is not None and (type(v) is not int or v < self.first_seen_step)
                   for v in (self.reached_step, self.used_step, self.contradiction_step))
            or type(self.contradictions) is not int or self.contradictions < 0
            or not isfinite(self.confidence) or not 0 <= self.confidence <= 1
            or self.source != "perceptual_capture"):
            raise ValueError("unfounded or malformed personal water memory")
        if (self.used_step is not None and self.reached_step is None):
            raise ValueError("water use requires physically reached place")


@dataclass(frozen=True, slots=True)
class WaterReturnTarget:
    ref: str
    source_t_monde: int
    origin: tuple[int, int]
    destination: tuple[int, int]
    direction: str
    water_position: tuple[int, int]
    visited_path: tuple[tuple[int, int], ...]
    observed_step: int
    confidence: float

    def validate(self):
        if (type(self.source_t_monde) is not int or self.source_t_monde < 1
            or type(self.observed_step) is not int
            or not 1 <= self.observed_step <= self.source_t_monde
            or not _point(self.origin) or not _point(self.destination)
            or not _point(self.water_position)
            or not isinstance(self.visited_path, tuple)
            or not 2 <= len(self.visited_path) <= 9
            or self.visited_path[0] != self.origin
            or self.visited_path[1] != self.destination
            or self.visited_path[-1] != self.water_position
            or len(set(self.visited_path)) != len(self.visited_path)
            or any(not _point(p) for p in self.visited_path)
            or any(not _adjacent(a, b) for a, b in
                   zip(self.visited_path, self.visited_path[1:]))
            or DIRECTION_BY_OFFSET.get((
                self.destination[0] - self.origin[0],
                self.destination[1] - self.origin[1],
            )) != self.direction
            or not isfinite(self.confidence) or not 0 < self.confidence <= 1):
            raise ValueError("water return is not a bounded observed route")
        expected = (
            f"water:{self.water_position[0]}:{self.water_position[1]}:"
            f"from:{self.origin[0]}:{self.origin[1]}:"
            f"via:{self.destination[0]}:{self.destination[1]}"
        )
        if self.ref != expected:
            raise ValueError("noncanonical water recall ref")


def find_water_return(*, origin: tuple[int, int],
                      visits: frozenset[tuple[int, int]],
                      surveys: tuple[ObservedSurvey, ...],
                      places: tuple[WaterPlace, ...],
                      current_free_neighbors: frozenset[tuple[int, int]],
                      current_world_step: int,
                      max_hops: int = 8) -> WaterReturnTarget | None:
    """Only visited survey edges or the *current* first-person edge are usable.

    Memory of an unseen destination is not memory of a traversable itinerary.
    A final unvisited site is permitted solely if its adjacent edge was
    physically surveyed from a visited site; only the next hop is proposed.
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
        or type(max_hops) is not int or not 1 <= max_hops <= 8):
        raise ValueError("invalid personal-route search input")
    known = {}
    for survey in surveys:
        if not isinstance(survey, ObservedSurvey):
            raise ValueError("untrusted route survey")
        survey.validate()
        if (survey.world_step > current_world_step
            or survey.position not in visits or survey.position in known):
            raise ValueError("future or unowned route survey")
        known[survey.position] = survey
    water = {}
    for site in places:
        if not isinstance(site, WaterPlace):
            raise ValueError("untrusted water-place memory")
        site.validate()
        if (site.first_seen_step > current_world_step
            or site.last_confirmed_step > current_world_step
            or any(step is not None and step > current_world_step
                   for step in (site.reached_step, site.used_step,
                                site.contradiction_step))
            or site.position in water):
            raise ValueError("future or duplicate water-place memory")
        if site.position != origin:
            water[site.position] = site

    # Every intermediate transit site was actually visited; the first hop is
    # independently verified against this step's actual local Perception.
    queue = deque([(origin, (origin,))])
    seen = {origin}
    candidates = []
    while queue:
        node, path = queue.popleft()
        if len(path) - 1 >= max_hops:
            continue
        edges = (
            current_free_neighbors if node == origin
            else frozenset(known[node].free_neighbors) if node in known
            else frozenset()
        )
        if node == origin and node in known:
            # An old survey cannot override a new local obstruction.
            edges = current_free_neighbors
        for nxt in sorted(edges):
            if not _adjacent(node, nxt) or nxt == origin:
                continue
            candidate_path = path + (nxt,)
            site = water.get(nxt)
            if site is not None and nxt not in path:
                age = current_world_step - site.last_confirmed_step
                quality = site.confidence / (1 + age / 240.0)
                quality /= (1 + 0.08 * (len(candidate_path) - 2))
                if quality >= 0.12:
                    direction = DIRECTION_BY_OFFSET[(
                        candidate_path[1][0] - origin[0],
                        candidate_path[1][1] - origin[1],
                    )]
                    target = WaterReturnTarget(
                        ref=(f"water:{nxt[0]}:{nxt[1]}:"
                             f"from:{origin[0]}:{origin[1]}:"
                             f"via:{candidate_path[1][0]}:{candidate_path[1][1]}"),
                        source_t_monde=current_world_step, origin=origin,
                        destination=candidate_path[1], direction=direction,
                        water_position=nxt, visited_path=candidate_path,
                        observed_step=site.first_seen_step,
                        confidence=quality,
                    )
                    target.validate()
                    candidates.append(target)
            if nxt in visits and nxt not in seen and nxt in known:
                seen.add(nxt)
                queue.append((nxt, candidate_path))
    if not candidates:
        return None
    return min(candidates, key=lambda t: (
        -t.confidence, len(t.visited_path), t.water_position, t.direction,
    ))
