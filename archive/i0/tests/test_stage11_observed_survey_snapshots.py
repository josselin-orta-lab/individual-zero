"""Opt-in Exploration survey snapshot tests; unit-only physical inputs."""
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
from unittest import TestCase

from i0.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)


def capture(t, x, y):
    directions = (("north", 0, -1), ("east", 1, 0),
                  ("south", 0, 1), ("west", -1, 0))
    return SimpleNamespace(
        t_monde=t, x=x, y=y,
        adjacent=tuple(
            SimpleNamespace(
                direction=name, x=x+dx, y=y+dy,
                passable=(name in ("east", "west", "south")),
                creature=False,
            ) for name, dx, dy in directions
        ),
    )


class ObservedSurveySnapshotTests(TestCase):
    def make_owner(self, enabled=True):
        return GeographicExploration(GeographicExplorationConfig(
            version="p48-public-survey-unit-v1",
            novelty_weight=0.7, max_distinct_sites=20,
            max_targets_per_cycle=1, observe_routes=enabled,
        ))

    def test_disabled_mode_has_original_snapshot_shape(self):
        geo = self.make_owner(enabled=False)
        geo.observe_capture(capture(1, 2, 2))
        self.assertFalse(geo.record_survey(capture(1, 2, 2)))
        state = geo.export_causal_state()
        self.assertEqual(state["schema"], "geographic-exploration-v1")
        self.assertNotIn("surveys", state)

    def test_only_physical_owner_capture_can_store_survey(self):
        geo = self.make_owner()
        source = capture(1, 2, 2)
        with self.assertRaises(ValueError):
            geo.record_survey(source)
        self.assertTrue(geo.observe_capture(source))
        self.assertTrue(geo.record_survey(source))
        self.assertFalse(geo.record_survey(source))
        self.assertEqual(len(geo.surveys), 1)
        self.assertEqual(geo.surveys[0].world_step, 1)
        self.assertEqual(geo.surveys[0].position, (2, 2))
        with self.assertRaises(ValueError):
            geo.record_survey(capture(2, 2, 2))

    def test_versioned_snapshot_replay_and_atomic_rejection(self):
        geo = self.make_owner()
        geo.observe_capture(capture(1, 2, 2))
        geo.record_survey(capture(1, 2, 2))
        geo.observe_capture(capture(2, 3, 2))
        geo.record_survey(capture(2, 3, 2))
        state = geo.export_causal_state()
        self.assertEqual(state["schema"], "geographic-exploration-v2-survey")
        restored = self.make_owner()
        restored.restore_causal_state(deepcopy(state))
        self.assertEqual(restored.export_causal_state(), state)
        for key, corrupted in (
            ("position", (9, 9)),
            ("world_step", 99),
            ("free_neighbors", ((9, 9),)),
        ):
            invalid = deepcopy(state)
            invalid["surveys"][0][key] = corrupted
            with self.subTest(key=key), self.assertRaises(ValueError):
                restored.restore_causal_state(invalid)
            self.assertEqual(restored.export_causal_state(), state)

    def test_revisit_preserves_prior_survey(self):
        geo = self.make_owner()
        for step, position in enumerate(((2, 2), (3, 2), (2, 2)), 1):
            obs = capture(step, *position)
            geo.observe_capture(obs)
            geo.record_survey(obs)
        self.assertEqual(len(geo.surveys), 2)
        state = geo.export_causal_state()
        restored = self.make_owner()
        restored.restore_causal_state(deepcopy(state))
        self.assertEqual(restored.export_causal_state(), state)
