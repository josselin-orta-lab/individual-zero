"""Versioned Exploration-owned transit snapshots, unit-only observations."""
from copy import deepcopy
from types import SimpleNamespace
from unittest import TestCase

from i0.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)
from i0.modules.observed_frontier_routing import (
    GeographicTransitTarget, find_observed_frontier_route,
)


def capture(t, x, y, free):
    return SimpleNamespace(
        t_monde=t, x=x, y=y,
        adjacent=tuple(SimpleNamespace(
            direction=d, x=x+dx, y=y+dy,
            passable=(x+dx, y+dy) in free,
            creature=False,
        ) for d, dx, dy in (
            ("north", 0, -1), ("east", 1, 0),
            ("south", 0, 1), ("west", -1, 0),
        )),
    )


def owner_with_history():
    geo = GeographicExploration(GeographicExplorationConfig(
        "p48-route-transit-owner-v1", 0.7, 20, 1,
        observe_routes=True,
    ))
    for t, x, y, free in (
        (1, 2, 2, {(3, 2), (2, 3)}),
        (2, 3, 2, {(2, 2), (4, 2)}),
        (3, 4, 2, {(3, 2)}),
    ):
        obs = capture(t, x, y, free)
        geo.observe_capture(obs)
        geo.record_survey(obs)
    return geo


def target(geo):
    route = find_observed_frontier_route(
        origin=(4, 2),
        visits=frozenset((x, y) for x, y, _ in geo.export_causal_state()["visits"]),
        surveys=geo.surveys,
        current_free_neighbors=frozenset({(3, 2)}),
        current_world_step=3,
    )
    assert route is not None
    return GeographicTransitTarget(
        ref="frontier_route:2:3:via:3:2:from:4:2",
        source_t_monde=3,
        origin=(4, 2),
        destination=route.next_position,
        direction=route.direction,
        observed_frontier=route.observed_frontier,
        visited_path=route.visited_path,
        objective_observed_step=route.source_world_step,
    )


class GeographicTransitOwnerTests(TestCase):
    def test_only_paid_exploration_history_can_offer_a_transit(self):
        geo = owner_with_history()
        destination = target(geo)
        geo.freeze_transits((destination,))
        self.assertEqual(geo.transit_offered, (destination,))
        option = SimpleNamespace(
            id=f"option:geographic:{destination.ref}:t3",
            motive_ref=SimpleNamespace(type="cible_exploration", id=destination.ref),
            provenance="exploration", goal_ref=None,
        )
        self.assertEqual(geo.transit_for(option), destination)
        self.assertIsNone(geo.target_for(option))
        snapshot = geo.export_causal_state()
        copy = GeographicExploration(geo.config)
        copy.restore_causal_state(deepcopy(snapshot))
        self.assertEqual(copy.export_causal_state(), snapshot)
        self.assertEqual(copy.transit_for(option), destination)
        self.assertFalse(geo.observe_capture(capture(4, 4, 2, {(3, 2)})))
        self.assertEqual(geo.transit_offered, ())

    def test_corrupt_route_snapshot_restores_atomically(self):
        geo = owner_with_history()
        geo.freeze_transits((target(geo),))
        saved = geo.export_causal_state()
        for field, bad_value in (
            ("destination", [7, 7]),
            ("observed_frontier", [10, 10]),
            ("objective_observed_step", 44),
            ("visited_path", [[4, 2], [9, 2]]),
        ):
            state = deepcopy(saved)
            state["transit_offered"][0][field] = bad_value
            with self.subTest(field=field), self.assertRaises(ValueError):
                geo.restore_causal_state(state)
            self.assertEqual(geo.export_causal_state(), saved)

    def test_disabled_routing_cannot_offer_transit(self):
        geo = GeographicExploration(GeographicExplorationConfig(
            "p48-route-disabled-v1", 0.7, 20, 1,
        ))
        with self.assertRaises(ValueError):
            geo.freeze_transits((target(owner_with_history()),))
        self.assertNotIn("transit_offered", geo.export_causal_state())
