"""Stage11 bounded physical visits and routed dead-end saturation tests.

Only publicly fixed Lab worlds and isolated synthetic owner unit inputs.
No scientific or hidden-world data is inferred.
"""
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
from unittest import TestCase

from i0.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)
from i0.modules.observed_frontier_routing import GeographicTransitTarget
from lab.stage11_routed_capacity_probe import (
    run_public_routed_capacity, CAPS,
)


def capture(t, x, y, *, free):
    directions = (
        ("north", 0, -1), ("east", 1, 0),
        ("south", 0, 1), ("west", -1, 0),
    )
    return SimpleNamespace(
        t_monde=t, x=x, y=y,
        adjacent=tuple(
            SimpleNamespace(
                direction=direction, x=x+dx, y=y+dy,
                passable=direction in free, creature=False,
            )
            for direction, dx, dy in directions
        ),
    )


class OwnerCapacityAtomicityTests(TestCase):
    def test_failed_novel_capture_preserves_pending_transit_and_snapshot(self):
        owner = GeographicExploration(GeographicExplorationConfig(
            version="p48-public-capacity-owner-test-v1",
            novelty_weight=0.7,
            max_distinct_sites=2, max_targets_per_cycle=1,
            observe_routes=True, refresh_surveys=True,
        ))
        origin = capture(1, 2, 2, free={"east", "south"})
        corridor = capture(2, 3, 2, free={"west"})
        self.assertTrue(owner.observe_capture(origin))
        self.assertTrue(owner.record_survey(origin))
        self.assertTrue(owner.observe_capture(corridor))
        self.assertTrue(owner.record_survey(corridor))
        # The observation at the earlier junction witnesses a southern
        # frontier; the only possible transit is over already visited sites.
        pending = GeographicTransitTarget(
            ref="frontier_route:2:3:via:2:2:from:3:2",
            source_t_monde=2,
            origin=(3, 2), destination=(2, 2), direction="west",
            observed_frontier=(2, 3),
            visited_path=((3, 2), (2, 2)),
            objective_observed_step=1,
        )
        owner.freeze_transits((pending,))
        before = deepcopy(owner.export_causal_state())
        self.assertEqual(owner.transit_offered, (pending,))
        # A new physical capture is a true input, NOT an inferred site.
        # The bounded owner must reject overflow with no partial mutation.
        with self.assertRaisesRegex(ValueError, "capacity exhausted"):
            owner.observe_capture(capture(3, 4, 2, free=set()))
        self.assertEqual(owner.export_causal_state(), before)
        self.assertEqual(owner.transit_offered, (pending,))
        self.assertEqual(owner.distinct_sites, 2)
        self.assertFalse(owner.observe_capture(corridor))
        self.assertEqual(owner.export_causal_state(), before)

    def test_invalid_owner_cap_cannot_be_used_as_unbounded_mode(self):
        config = GeographicExplorationConfig(
            version="p48-public-capacity-owner-test-v1",
            novelty_weight=0.7, max_distinct_sites=2,
            max_targets_per_cycle=1, observe_routes=True,
            refresh_surveys=True,
        )
        for bad in (0, -1, True, "2"):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                GeographicExploration(replace(
                    config, max_distinct_sites=bad,
                ))


class PublicRoutedCapacityTests(TestCase):
    def test_saturation_stops_unproductive_return_routes_without_ghost_visits(self):
        capped = run_public_routed_capacity(site_cap=3)
        control = run_public_routed_capacity(site_cap=4)
        self.assertFalse(capped.heldout)
        self.assertIsNone(capped.scientific_verdict)
        self.assertEqual(capped.classification,
                         "public_development_only_not_heldout")
        self.assertEqual(capped.steps, control.steps)
        self.assertNotEqual(capped.input_sha256, control.input_sha256)
        self.assertEqual(capped.captured_positions[:3],
                         control.captured_positions[:3])
        self.assertEqual(capped.distinct_captured_sites, 3)
        self.assertEqual(capped.owner_distinct_sites, 3)
        self.assertEqual(capped.capped_world_steps[0], 3)
        self.assertTrue(capped.capacity_stop_world_steps)
        self.assertEqual(capped.accepted_route_search_uc_at_cap, 0)
        self.assertEqual(capped.route_search_events_at_cap, 0)
        self.assertEqual(capped.applied_transit_steps_at_cap, ())
        self.assertFalse(capped.observed_southern_alternative)
        self.assertEqual(
            capped.distinct_captured_sites, capped.owner_distinct_sites,
        )
        self.assertEqual(
            control.distinct_captured_sites, control.owner_distinct_sites,
        )
        self.assertEqual(control.distinct_captured_sites, 4)
        self.assertTrue(control.observed_southern_alternative)
        self.assertGreater(control.accepted_route_search_uc, 0)
        self.assertEqual(control.accepted_route_search_uc_at_cap, 0)
        self.assertEqual(control.applied_transit_steps_at_cap, ())
        self.assertIn("+route-site-cap-stop-v1", capped.budget_version)
        print("stage11_public_routed_capacity=" + capped.to_json())
        print("stage11_public_routed_capacity=" + control.to_json())

    def test_cap_controls_replay_with_exact_journals(self):
        for cap in CAPS:
            with self.subTest(cap=cap):
                first = run_public_routed_capacity(site_cap=cap)
                repeat = run_public_routed_capacity(site_cap=cap)
                self.assertEqual(first, repeat)
                self.assertEqual(first.to_json(), repeat.to_json())
                self.assertEqual(
                    first.owner_distinct_sites,
                    first.distinct_captured_sites,
                )
                self.assertLessEqual(first.owner_distinct_sites, cap)
                self.assertEqual(first.accepted_route_search_uc_at_cap, 0)
                self.assertEqual(first.route_search_events_at_cap, 0)
                self.assertEqual(first.applied_transit_steps_at_cap, ())

    def test_rejects_unregistered_caps_and_windows(self):
        for kwargs in (
            {"site_cap": 2},
            {"site_cap": 5},
            {"site_cap": True},
            {"site_cap": "3"},
            {"site_cap": 3, "steps": 9},
            {"site_cap": 3, "steps": True},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                run_public_routed_capacity(**kwargs)


if __name__ == "__main__":
    import unittest
    unittest.main()
