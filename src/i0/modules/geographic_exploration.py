"""Versioned local-frontier curiosity from one accessible Perception capture.

Stage-11 development-only slice of EN MVP v1.2.1 section 14 / INV-06,14.
No map oracle, world physics, reward, counterfactual or action sender access.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Mapping

from .observed_frontier_routing import ObservedSurvey

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

    def validate(self) -> None:
        if not isinstance(self.version, str) or not self.version:
            raise ValueError("geographic curiosity needs a version")
        if (type(self.novelty_weight) not in (int, float)
            or not isfinite(self.novelty_weight)
            or not 0 <= self.novelty_weight <= 1):
            raise ValueError("geographic P-48 interest must be bounded")
        if type(self.observe_routes) is not bool:
            raise ValueError("route survey flag must be boolean")
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

    @property
    def distinct_sites(self) -> int:
        return len(self._visits)

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
    def surveys(self) -> tuple[ObservedSurvey, ...]:
        return tuple(self._surveys[key] for key in sorted(self._surveys))

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
            return False
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

    def target_for(self, option) -> GeographicTarget | None:
        motive = getattr(option, "motive_ref", None)
        if (getattr(motive, "type", None) != "cible_exploration"
            or getattr(option, "provenance", None) != "exploration"
            or getattr(option, "goal_ref", None) is not None):
            return None
        for target in self._offered:
            if (motive.id == target.ref and option.id == (
                f"option:geographic:{target.ref}:t{target.source_t_monde}"
            ) and target.destination not in self._visits):
                return target
        return None

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": ("geographic-exploration-v2-survey"
                       if self.config.observe_routes
                       else "geographic-exploration-v1"),
            "version": self.config.version,
            "visits": [
                [x, y, count] for (x, y), count in sorted(self._visits.items())
            ],
            "last_capture": (
                None if self._last_capture is None
                else list(self._last_capture)
            ),
            "offered": [asdict(t) for t in self._offered],
            **({"surveys": [asdict(x) for x in self.surveys]}
               if self.config.observe_routes else {}),
        }

    def restore_causal_state(self, state: object) -> None:
        if (not isinstance(state, Mapping)
            or state.get("schema") != (
                "geographic-exploration-v2-survey"
                if self.config.observe_routes else "geographic-exploration-v1"
            )
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
                    or (survey.position == last[1:]
                        and survey.world_step != last[0])
                ):
                    raise ValueError("unowned or future snapshot survey")
                restored_surveys[survey.position] = survey
        elif "surveys" in state:
            raise ValueError("legacy geographic snapshot cannot contain surveys")
        self._visits = visited
        self._last_capture = last
        self._offered = tuple(offered)
        self._surveys = restored_surveys
