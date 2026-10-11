"""Unit contracts for the opt-in, physically refreshed geographic survey owner.

No world layout, oracle or task-specific destination is accepted here.
All captures in these tests are synthetic local-Perception fixtures only.
"""
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
from unittest import TestCase

from i0.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)


def local_capture(t, *, west_creature):
    x, y = 4, 2
    directions = (("north", 0, -1), ("east", 1, 0),
                  ("south", 0, 1), ("west", -1, 0))
    return SimpleNamespace(
        t_monde=t, x=x, y=y,
        adjacent=tuple(SimpleNamespace(
            direction=name, x=x+dx, y=y+dy,
            passable=name == "west",
            creature=name == "west" and west_creature,
        ) for name, dx, dy in directions),
    )


def new_owner(*, refresh=True, routes=True):
    return GeographicExploration(GeographicExplorationConfig(
        version="p48-public-survey-refresh-unit-v1",
        novelty_weight=0.7, max_distinct_sites=10,
        max_targets_per_cycle=1, observe_routes=routes,
        refresh_surveys=refresh,
    ))


def build_refreshed_owner():
    owner = new_owner()
    for t, creature in ((1, True), (2, True), (3, False)):
        observation = local_capture(t, west_creature=creature)
        owner.observe_capture(observation)
        owner.record_survey(observation)
    return owner


class PhysicalSurveyRefreshOwnerTests(TestCase):
    def test_disabled_refresh_retains_legacy_owner_and_history(self):
        old = new_owner(refresh=False)
        first = local_capture(1, west_creature=True)
        later = local_capture(3, west_creature=False)
        old.observe_capture(first)
        self.assertTrue(old.record_survey(first))
        old.observe_capture(later)
        self.assertFalse(old.record_survey(later))
        self.assertEqual(old.surveys[0].free_neighbors, ())
        self.assertEqual(old.surveys[0].world_step, 1)
        self.assertEqual(old.export_causal_state()["schema"],
                         "geographic-exploration-v2-survey")
        self.assertEqual(old.distinct_sites, 1)

    def test_new_world_step_refreshes_topology_but_never_awards_novelty(self):
        owner = new_owner()
        first = local_capture(1, west_creature=True)
        owner.observe_capture(first)
        self.assertTrue(owner.record_survey(first))
        same = local_capture(2, west_creature=True)
        self.assertFalse(owner.observe_capture(same))
        self.assertFalse(owner.record_survey(same))
        self.assertEqual(owner.surveys[0].world_step, 1)
        opened = local_capture(3, west_creature=False)
        self.assertFalse(owner.observe_capture(opened))
        self.assertTrue(owner.record_survey(opened))
        self.assertFalse(owner.record_survey(opened))
        self.assertEqual(owner.surveys[0].world_step, 3)
        self.assertEqual(owner.surveys[0].free_neighbors, ((3, 2),))
        self.assertEqual(owner.distinct_sites, 1)
        self.assertEqual(owner.visit_count, 1)
        self.assertEqual(owner.transit_offered, ())
        self.assertEqual(owner.export_causal_state()["visits"],
                         [[4, 2, 1]])
        self.assertEqual(owner.export_causal_state()["schema"],
                         "geographic-exploration-v3-survey-refresh")

    def test_same_step_conflict_and_absent_capture_fail_closed(self):
        owner = new_owner()
        with self.assertRaises(ValueError):
            owner.record_survey(local_capture(1, west_creature=True))
        observed = local_capture(1, west_creature=True)
        owner.observe_capture(observed)
        owner.record_survey(observed)
        with self.assertRaises(ValueError):
            owner.record_survey(local_capture(1, west_creature=False))
        with self.assertRaises(ValueError):
            owner.record_survey(local_capture(2, west_creature=False))
        self.assertEqual(owner.surveys[0].free_neighbors, ())

    def test_config_and_snapshot_versions_must_not_cross(self):
        with self.assertRaises(ValueError):
            new_owner(refresh=True, routes=False)
        fresh = build_refreshed_owner()
        payload = fresh.export_causal_state()
        self.assertEqual(payload["schema"],
                         "geographic-exploration-v3-survey-refresh")
        copy = new_owner()
        copy.restore_causal_state(deepcopy(payload))
        self.assertEqual(copy.export_causal_state(), payload)
        with self.assertRaises(ValueError):
            new_owner(refresh=False).restore_causal_state(payload)
        old = new_owner(refresh=False)
        obs = local_capture(1, west_creature=True)
        old.observe_capture(obs)
        old.record_survey(obs)
        with self.assertRaises(ValueError):
            fresh.restore_causal_state(old.export_causal_state())

    def test_malformed_restores_are_atomic_even_after_a_revision(self):
        owner = build_refreshed_owner()
        expected = owner.export_causal_state()
        corruptions = []
        invalid_future = deepcopy(expected)
        invalid_future["surveys"][0]["world_step"] = 4
        corruptions.append(invalid_future)
        invalid_position = deepcopy(expected)
        invalid_position["surveys"][0]["position"] = [8, 8]
        corruptions.append(invalid_position)
        invalid_edge = deepcopy(expected)
        invalid_edge["surveys"][0]["free_neighbors"] = [[9, 9]]
        corruptions.append(invalid_edge)
        duplicate = deepcopy(expected)
        duplicate["surveys"].append(deepcopy(duplicate["surveys"][0]))
        corruptions.append(duplicate)
        wrong_schema = deepcopy(expected)
        wrong_schema["schema"] = "geographic-exploration-v2-survey"
        corruptions.append(wrong_schema)
        for bad in corruptions:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                owner.restore_causal_state(bad)
            self.assertEqual(owner.export_causal_state(), expected)
