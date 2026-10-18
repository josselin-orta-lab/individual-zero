"""Issue 314: first-person memory is an option, not a route oracle."""
from dataclasses import replace
from types import SimpleNamespace

import pytest

from i1.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)
from i1.modules.observed_frontier_routing import ObservedSurvey
from i1.modules.water_memory_navigation import WaterPlace, find_water_return


def site(x=1, y=0, *, step=2, confidence=0.65):
    return WaterPlace(
        observer_id="i1:test", position=(x, y), observed_from=(0, 0),
        first_seen_step=step, last_confirmed_step=step,
        reached_step=None, used_step=None, contradiction_step=None,
        contradictions=0, confidence=confidence,
    )


def survey(x, y, step, neighbors):
    return ObservedSurvey(position=(x, y), world_step=step,
                          free_neighbors=tuple(neighbors))


def route(*, places, surveys, visits, current_free, step=12, origin=(2, 0)):
    return find_water_return(
        origin=origin, visits=frozenset(visits), surveys=tuple(surveys),
        places=tuple(places), current_free_neighbors=frozenset(current_free),
        current_world_step=step,
    )


def test_no_memory_no_water_route():
    assert route(places=(), surveys=(), visits={(2, 0)},
                 current_free={(1, 0)}) is None


def test_recall_uses_real_adjacency_and_is_one_hop():
    result = route(
        places=(site(),), visits={(0, 0), (1, 0), (2, 0)},
        surveys=(survey(0, 0, 1, [(1, 0)]),
                 survey(1, 0, 2, [(0, 0), (2, 0)])),
        current_free={(1, 0)},
    )
    assert result is not None
    assert result.destination == (1, 0)
    assert result.water_position == (1, 0)
    assert result.visited_path == ((2, 0), (1, 0))


def test_unknown_intermediate_edge_never_invented():
    assert route(
        places=(site(),), visits={(0, 0), (2, 0)},
        surveys=(survey(0, 0, 1, [(1, 0)]),),
        current_free={(3, 0)},
    ) is None


def test_current_obstacle_revokes_old_first_hop():
    assert route(
        places=(site(),), visits={(0, 0), (1, 0), (2, 0)},
        surveys=(survey(2, 0, 3, [(1, 0)]),
                 survey(1, 0, 2, [(0, 0)])),
        current_free=set(),
    ) is None


def test_future_water_memory_rejected():
    with pytest.raises(ValueError, match="future"):
        route(places=(site(step=20),), surveys=(),
              visits={(2, 0)}, current_free={(1, 0)})


def test_old_memory_is_not_a_permanent_command():
    assert route(
        places=(site(step=1, confidence=0.12),), surveys=(),
        visits={(2, 0)}, current_free={(1, 0)}, step=1000,
    ) is None


def geo():
    return GeographicExploration(GeographicExplorationConfig(
        version="water-memory-test", novelty_weight=0.15,
        max_distinct_sites=10, max_targets_per_cycle=1,
        observe_routes=True, refresh_surveys=True, remember_water=True,
    ))


def capture(step, x, y, water=False, adjacent=()):
    cells = []
    for direction, dx, dy in (
        ("north", 0, -1), ("east", 1, 0),
        ("south", 0, 1), ("west", -1, 0),
    ):
        pos = (x + dx, y + dy)
        cells.append(SimpleNamespace(
            direction=direction, x=pos[0], y=pos[1],
            passable=True, creature=False,
            water_source=pos in adjacent,
        ))
    return SimpleNamespace(
        t_monde=step, x=x, y=y, current_water_source=water,
        adjacent=tuple(cells),
    )


def test_capture_memory_and_contradiction_and_restore():
    owner = geo()
    c1 = capture(1, 0, 0, adjacent=((1, 0),))
    owner.observe_capture(c1)
    owner.observe_water(c1, observer_id="i1:test")
    original = owner.water_places[0]
    assert original.position == (1, 0)
    assert original.reached_step is None
    snap = owner.export_causal_state()
    restored = geo()
    restored.restore_causal_state(snap)
    assert restored.water_places == owner.water_places
    c2 = capture(2, 0, 0)
    restored.observe_capture(c2)
    changed = restored.observe_water(c2, observer_id="i1:test")
    assert changed[0].contradictions == 1
    assert changed[0].confidence < original.confidence
    assert restored.water_places[0].position == (1, 0)


def test_duplicate_capture_does_not_invent_second_observation():
    owner = geo()
    c1 = capture(1, 0, 0, adjacent=((1, 0),))
    owner.observe_capture(c1)
    first = owner.observe_water(c1, observer_id="i1:test")[0]
    second = owner.observe_water(c1, observer_id="i1:test")[0]
    assert second.first_seen_step == first.first_seen_step
    assert second.last_confirmed_step == first.last_confirmed_step


def test_legacy_config_does_not_store_memory():
    owner = GeographicExploration(GeographicExplorationConfig(
        version="legacy", novelty_weight=0.15, max_distinct_sites=10,
        max_targets_per_cycle=1,
    ))
    c1 = capture(1, 0, 0, adjacent=((1, 0),))
    owner.observe_capture(c1)
    assert owner.observe_water(c1, observer_id="i1:test") == ()
    assert "water_places" not in owner.export_causal_state()
