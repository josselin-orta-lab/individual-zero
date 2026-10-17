"""Unit-only contracts for prospective observed-site transit; not a live GO."""
from dataclasses import replace
from unittest import TestCase

from i0.modules.observed_frontier_routing import (
    ObservedSurvey, find_observed_frontier_route,
)


def history():
    # The southern branch was observed from the first real site, then
    # the agent physically visited an eastern dead end.
    return (
        ObservedSurvey((2, 2), 1, ((3, 2), (2, 3))),
        ObservedSurvey((3, 2), 2, ((2, 2), (4, 2))),
        ObservedSurvey((4, 2), 3, ((3, 2),)),
    )


def search(**kwargs):
    values = dict(
        origin=(4, 2),
        visits=frozenset({(2, 2), (3, 2), (4, 2)}),
        surveys=history(),
        current_free_neighbors=frozenset({(3, 2)}),
        current_world_step=3,
        max_transit_hops=8,
    )
    values.update(kwargs)
    return find_observed_frontier_route(**values)


class PhysicallyObservedRoutingUnitTests(TestCase):
    def test_only_seen_frontier_through_visited_sites_is_candidate(self):
        route = search()
        self.assertIsNotNone(route)
        self.assertEqual(route.next_position, (3, 2))
        self.assertEqual(route.direction, "west")
        self.assertEqual(route.visited_path,
                         ((4, 2), (3, 2), (2, 2)))
        self.assertEqual(route.observed_frontier, (2, 3))
        self.assertEqual(route.source_world_step, 1)

    def test_no_unseen_teleport_shortcut_or_unknown_frontier(self):
        self.assertIsNone(search(surveys=(
            ObservedSurvey((2, 2), 1, ((3, 2),)),
            *history()[1:],
        )))
        self.assertIsNone(search(
            visits=frozenset({(2, 2), (4, 2)}),
            surveys=(history()[0], history()[2]),
        ))
        self.assertIsNone(search(current_free_neighbors=frozenset()))

    def test_observed_new_adjacent_frontier_has_priority(self):
        self.assertIsNone(search(
            current_free_neighbors=frozenset({(3, 2), (4, 1)}),
        ))

    def test_bounded_hops_and_current_capture_freshness(self):
        self.assertIsNone(search(max_transit_hops=1))
        self.assertIsNotNone(search(max_transit_hops=2))
        with self.assertRaises(ValueError):
            search(surveys=(
                history()[0], history()[1],
                replace(history()[2], world_step=4),
            ))
        with self.assertRaises(ValueError):
            search(surveys=(
                history()[0], replace(history()[1], world_step=3),
                history()[2],
            ))

    def test_duplicate_or_forged_survey_rejected(self):
        with self.assertRaises(ValueError):
            search(surveys=history() + (history()[0],))
        with self.assertRaises(ValueError):
            search(surveys=history()[:2] + (
                ObservedSurvey((4, 2), 3, ((10, 10),)),
            ))
        with self.assertRaises(ValueError):
            search(visits=frozenset({(4, 2)}))
        with self.assertRaises(ValueError):
            search(max_transit_hops=True)

    def test_no_intrinsic_motivation_or_action_is_created_here(self):
        route = search()
        self.assertFalse(hasattr(route, "reward"))
        self.assertFalse(hasattr(route, "command"))
        self.assertFalse(hasattr(route, "safety_status"))
