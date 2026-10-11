"""Public Stage-11 development controls for paid physical adjacency revision.

Compared histories start in the same world. They never inject movement,
frontier identity or hidden danger knowledge into Exploration/Planning.
"""
from unittest import TestCase

from lab.stage11_survey_refresh_probe import run_public_survey_refresh
from lab.stage11_stale_route_safety_probe import VARIANTS


def case(variant, *, refresh, exploration_uc=None):
    return run_public_survey_refresh(
        variant=variant, refresh_surveys=refresh,
        exploration_uc=exploration_uc,
    )


class Stage11PhysicalAdjacencyRefreshTests(TestCase):
    def test_reopened_neighbor_requires_new_paid_capture_and_next_step_planning(self):
        old = case("creature_removed", refresh=False)
        new = case("creature_removed", refresh=True)
        self.assertEqual(old.initial_local_sha256, new.initial_local_sha256)
        self.assertEqual(old.observed_positions[:5], new.observed_positions[:5])
        self.assertEqual(old.actions[:2], new.actions[:2])
        self.assertEqual(old.snapshot_schema, "geographic-exploration-v2-survey")
        self.assertEqual(new.snapshot_schema,
                         "geographic-exploration-v3-survey-refresh")
        self.assertFalse(old.survey_revisions)
        self.assertFalse(old.seen_return_junction_after_dead_end)
        self.assertFalse(old.captured_southern_alternative)
        self.assertEqual(len(new.survey_revisions), 1)
        revision = new.survey_revisions[0]
        self.assertEqual(
            {key: revision[key] for key in (
                "world_step", "position", "old_neighbors", "new_neighbors",
                "old_observed_step", "source",
            )},
            {
                "world_step": 5,
                "position": [4, 2],
                "old_neighbors": [],
                "new_neighbors": [[3, 2]],
                "old_observed_step": 3,
                "source": "paid_phase1_exploration_perception",
            },
        )
        # There are multiple cognitive cycles per physical step. The new
        # survey is inaccessible to *same-cycle* Planning (INV-08), but a
        # later cycle of world step 5 may legitimately use it.
        for step, cycle in new.route_candidate_step_cycles:
            if step == 5:
                self.assertGreater(cycle, revision["cycle"])
        self.assertTrue(all(t >= 5 for t in new.applied_route_steps))
        self.assertTrue(new.seen_return_junction_after_dead_end)
        self.assertTrue(new.captured_southern_alternative)
        self.assertIn((3, 2), new.observed_positions[5:])
        self.assertEqual(set(new.confirmed_visit_sites),
                         set(new.observed_positions))
        self.assertEqual(new.applied_route_into_occupied_neighbor, 0)

    def test_persistent_visible_creature_still_blocks_both_modes(self):
        old = case("creature_blocks_return", refresh=False)
        fresh = case("creature_blocks_return", refresh=True)
        for result in (old, fresh):
            self.assertFalse(result.seen_return_junction_after_dead_end)
            self.assertFalse(result.captured_southern_alternative)
            self.assertEqual(result.applied_route_steps, ())
            self.assertEqual(result.applied_route_into_occupied_neighbor, 0)
            self.assertEqual(result.danger_damage_total, 0.0)
            self.assertEqual(result.observed_positions[2:], ((4, 2),) * 8)
        self.assertEqual(fresh.survey_revisions, ())

    def test_unmodified_world_remains_equivalent_under_opt_in_refresh(self):
        old = case("unchanged_control", refresh=False)
        fresh = case("unchanged_control", refresh=True)
        self.assertEqual(old.initial_local_sha256, fresh.initial_local_sha256)
        self.assertEqual(old.observed_positions, fresh.observed_positions)
        self.assertEqual(old.actions, fresh.actions)
        self.assertEqual(fresh.survey_revisions, ())
        self.assertTrue(old.seen_return_junction_after_dead_end)
        self.assertTrue(fresh.captured_southern_alternative)
        self.assertEqual(fresh.applied_route_into_occupied_neighbor, 0)

    def test_physically_hidden_hazard_does_not_masquerade_as_adjacency_refresh(self):
        old = case("unknown_danger", refresh=False)
        fresh = case("unknown_danger", refresh=True)
        self.assertEqual(old.initial_local_sha256, fresh.initial_local_sha256)
        self.assertEqual(old.actions, fresh.actions)
        self.assertEqual(old.observed_positions, fresh.observed_positions)
        self.assertEqual(fresh.survey_revisions, ())
        self.assertEqual(fresh.danger_damage_total, 10.0)
        self.assertEqual(fresh.final_integrity, 90.0)
        self.assertEqual(fresh.applied_route_into_occupied_neighbor, 0)

    def test_zero_exploration_uc_cannot_write_paid_surveys(self):
        denied = case("creature_removed", refresh=True, exploration_uc=0)
        self.assertEqual(denied.accepted_exploration_observe_uc, 0)
        self.assertGreater(denied.rejected_exploration_observe_uc, 0)
        self.assertEqual(denied.recorded_survey_steps, ())
        self.assertEqual(denied.survey_revisions, ())
        self.assertEqual(denied.applied_route_steps, ())
        self.assertEqual(set(denied.confirmed_visit_sites),
                         set(denied.observed_positions))

    def test_all_public_variants_replay_exactly_with_independent_journal_hashes(self):
        for variant in VARIANTS:
            for refresh in (False, True):
                with self.subTest(variant=variant, refresh=refresh):
                    first = case(variant, refresh=refresh)
                    again = case(variant, refresh=refresh)
                    self.assertEqual(first, again)
                    self.assertEqual(first.to_json(), again.to_json())
                    self.assertEqual(first.classification,
                                     "public_development_only_not_heldout")
                    self.assertIsNone(first.scientific_verdict)
                    self.assertFalse(first.heldout)
                    self.assertEqual(set(first.observed_positions),
                                     set(first.confirmed_visit_sites))
                    print("stage11_public_survey_refresh=" + first.to_json())

    def test_unregistered_inputs_rejected(self):
        for bad in (
            {"variant": "secret", "refresh_surveys": True},
            {"variant": "unchanged_control", "refresh_surveys": "yes"},
            {"variant": "unchanged_control", "refresh_surveys": True,
             "exploration_uc": True},
            {"variant": "unchanged_control", "refresh_surveys": True,
             "exploration_uc": 3},
            {"variant": "unchanged_control", "refresh_surveys": True,
             "steps": 11},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                run_public_survey_refresh(**bad)
