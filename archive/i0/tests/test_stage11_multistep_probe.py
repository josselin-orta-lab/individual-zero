"""Reproducible public longitudinal Stage-11 physical and epistemic checks."""
from unittest import TestCase

from lab.stage11_multistep_probe import (
    CORRIDOR, DANGER, VARIANTS, run_public_longitudinal_corridor,
)


class PublicLongitudinalProbeTests(TestCase):
    def test_undisclosed_physical_hazard_cannot_change_initial_observation_or_decision(self):
        safe = run_public_longitudinal_corridor(variant="corridor_clear")
        hidden = run_public_longitudinal_corridor(variant="corridor_unknown_danger")
        self.assertEqual(safe.initial_canonical_danger_status, "unknown")
        self.assertEqual(hidden.initial_canonical_danger_status, "unknown")
        self.assertEqual(
            safe.initially_accessible_local_sha256,
            hidden.initially_accessible_local_sha256,
        )
        self.assertEqual(safe.first_decision, hidden.first_decision)
        self.assertEqual(safe.experienced_danger_damage_events, 0)
        self.assertEqual(safe.experienced_danger_damage_total, 0)
        for result in (safe, hidden):
            self.assertIsNone(result.scientific_verdict)
            self.assertFalse(result.heldout)
            self.assertEqual(len(result.step_trace), 8)
            self.assertEqual(len(result.physically_perceived_sites), 8)
            self.assertEqual(
                set(result.physically_perceived_sites),
                set(result.confirmed_visit_sites),
            )
            self.assertTrue(
                set(result.physically_perceived_sites) <= CORRIDOR
            )
            self.assertEqual(
                result.physically_perceived_sites[0], (2, 2),
            )
            self.assertEqual(
                sum(row["danger_zone_damage"] > 0
                    for row in result.physical_transitions),
                result.experienced_danger_damage_events,
            )
            for physical in result.physical_transitions:
                if physical["danger_zone_damage"] > 0:
                    self.assertEqual(
                        tuple(physical["position_after"]),
                        (DANGER.x, DANGER.y),
                    )

    def test_cognitive_planning_budget_zero_preserves_physics_not_intrinsic_options(self):
        denied = run_public_longitudinal_corridor(
            variant="corridor_unknown_danger_planning_0",
        )
        self.assertEqual(denied.initial_canonical_danger_status, "unknown")
        self.assertEqual(denied.accepted_planning_preflight_uc, 0)
        self.assertEqual(denied.accepted_planning_build_uc, 0)
        self.assertEqual(denied.applied_geographic_commands, 0)
        self.assertEqual(denied.remaining_offered_targets, 0)
        self.assertEqual(
            set(denied.physically_perceived_sites),
            set(denied.confirmed_visit_sites),
        )
        self.assertTrue(set(denied.physically_perceived_sites) <= CORRIDOR)

    def test_exact_reexecution_and_canonical_digests_for_each_public_condition(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                first = run_public_longitudinal_corridor(variant=variant)
                again = run_public_longitudinal_corridor(variant=variant)
                self.assertEqual(first, again)
                self.assertEqual(first.to_json(), again.to_json())
                self.assertEqual(first.classification,
                                 "development_only_not_heldout")
                print("stage11_longitudinal_public=" + first.to_json())

    def test_unregistered_inputs_are_rejected(self):
        for kwargs in (
            {"variant": "private_world"},
            {"variant": "corridor_clear", "steps": 9},
            {"variant": "corridor_clear", "steps": True},
        ):
            with self.subTest(**kwargs), self.assertRaises(ValueError):
                run_public_longitudinal_corridor(**kwargs)
