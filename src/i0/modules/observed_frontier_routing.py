"""Bounded observed-frontier routing, a pure Stage-11 development primitive.

This module accepts ONLY records constructed from an individual's physically
accessible Perception captures. It cannot query WorldBody or its hidden layout.
The result is a *suggestion* to the ordinary Planning/Action Control pipeline,
never an action sender or a claim of learned causation.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

DIRECTIONS = (("north", 0, -1), ("east", 1, 0),
              ("south", 0, 1), ("west", -1, 0))
DIRECTION_BY_OFFSET = {(dx, dy): direction
                       for direction, dx, dy in DIRECTIONS}


@dataclass(frozen=True, slots=True)
class ObservedSurvey:
    position: tuple[int, int]
    world_step: int
    free_neighbors: tuple[tuple[int, int], ...]

    def validate(self):
        if (type(self.world_step) is not int or self.world_step < 1
            or not _coordinate(self.position)
            or not isinstance(self.free_neighbors, tuple)
            or len(self.free_neighbors) > 4
            or len(set(self.free_neighbors)) != len(self.free_neighbors)):
            raise ValueError("invalid physical neighbor survey")
        if any(
            not _coordinate(p)
            or (p[0]-self.position[0], p[1]-self.position[1])
            not in DIRECTION_BY_OFFSET
            for p in self.free_neighbors
        ):
            raise ValueError("nonadjacent or malformed observed neighbor")


@dataclass(frozen=True, slots=True)
class FrontierRoute:
    next_position: tuple[int, int]
    direction: str
    observed_frontier: tuple[int, int]
    visited_path: tuple[tuple[int, int], ...]
    source_world_step: int

    def validate(self):
        if (not _coordinate(self.next_position)
            or not _coordinate(self.observed_frontier)
            or not isinstance(self.visited_path, tuple)
            or len(self.visited_path) < 2
            or any(not _coordinate(p) for p in self.visited_path)
            or len(set(self.visited_path)) != len(self.visited_path)
            or type(self.source_world_step) is not int
            or self.source_world_step < 1):
            raise ValueError("malformed visited-frontier route")
        first, second = self.visited_path[:2]
        delta = (second[0]-first[0], second[1]-first[1])
        if (self.next_position != second
            or DIRECTION_BY_OFFSET.get(delta) != self.direction
            or self.observed_frontier in self.visited_path):
            raise ValueError("invalid route first hop or objective")


def _coordinate(p):
    return (isinstance(p, tuple) and len(p) == 2
            and all(type(x) is int for x in p))


def find_observed_frontier_route(
    *, origin: tuple[int, int], visits: frozenset[tuple[int, int]],
    surveys: tuple[ObservedSurvey, ...],
    current_free_neighbors: frozenset[tuple[int, int]],
    current_world_step: int, max_transit_hops: int = 8,
) -> FrontierRoute | None:
    """Breadth-first traversal only across physically visited positions.

    Only survey neighbors are potential informational objectives. Transit may
    cross visited positions but *never* an unvisited or hidden-map shortcut.
    The current first hop must also be locally perceived passable right now.
    """
    if (not _coordinate(origin) or not isinstance(visits, frozenset)
        or origin not in visits
        or not visits or any(not _coordinate(v) for v in visits)
        or not isinstance(surveys, tuple)
        or not isinstance(current_free_neighbors, frozenset)
        or any(not _coordinate(p) or
               (p[0]-origin[0], p[1]-origin[1]) not in DIRECTION_BY_OFFSET
               for p in current_free_neighbors)
        or type(current_world_step) is not int or current_world_step < 1
        or type(max_transit_hops) is not int or not 1 <= max_transit_hops <= 8):
        raise ValueError("invalid physically bounded route context")
    if len(visits) > 1024 or len(surveys) > 1024:
        raise ValueError("observed history exceeds bounded routing budget")
    observed: dict[tuple[int, int], ObservedSurvey] = {}
    for survey in surveys:
        if not isinstance(survey, ObservedSurvey):
            raise ValueError("untrusted survey object")
        survey.validate()
        if (survey.position not in visits or survey.position in observed
            or survey.world_step >= current_world_step):
            raise ValueError("survey must be prior physical capture of visited site")
        observed[survey.position] = survey
    if origin not in observed:
        return None

    def ordered_neighbors(p):
        known = observed[p].free_neighbors
        return tuple(sorted(
            known, key=lambda q: (
                next(i for i, (_, dx, dy) in enumerate(DIRECTIONS)
                     if q == (p[0] + dx, p[1] + dy)), q,
            ),
        ))

    # Never route if a genuine unvisited local frontier is accessible;
    # ordinary P-48 adjacent exploration has precedence.
    if any(p not in visits for p in current_free_neighbors):
        return None
    q = deque([(origin, (origin,))])
    seen = {origin}
    while q:
        position, path = q.popleft()
        if len(path) > 1 and position in observed:
            frontiers = tuple(p for p in ordered_neighbors(position)
                              if p not in visits)
            if frontiers:
                route = FrontierRoute(
                    next_position=path[1],
                    direction=DIRECTION_BY_OFFSET[(
                        path[1][0]-origin[0], path[1][1]-origin[1]
                    )],
                    observed_frontier=frontiers[0],
                    visited_path=path,
                    source_world_step=observed[position].world_step,
                )
                route.validate()
                return route
        if len(path)-1 >= max_transit_hops:
            continue
        for neighbor in ordered_neighbors(position):
            if neighbor not in visits or neighbor in seen:
                continue
            # Revalidate the *immediate* hop against current Perception.
            if position == origin and neighbor not in current_free_neighbors:
                continue
            if neighbor not in observed:
                continue
            seen.add(neighbor)
            q.append((neighbor, path + (neighbor,)))
    return None
