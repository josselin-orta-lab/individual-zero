"""Registered public multi-step hazard/route/strict-UC software gates.

Not held-out science, not a historical Golden and not a Stage-9 GO.
All physical danger truth is inspected by Lab only, never fed to cognition.
"""
from unittest import TestCase

from lab.stage11_transient_hidden_route_probe import (
    BUDGETS, PROTOCOL, VARIANTS, run_public_transient_hidden_route,
    schedule_for,
)


class Stage11TransientHiddenRouteUCTests(TestCase):
    def test_public_budget_danger_matrix_and_independent_snapshot_replay(self):
        for planning_uc, exploration_uc in BUDGETS:
            rows = {}
            for variant in VARIANTS:
                with self.subTest(
                    planning_uc=planning_uc, exploration_uc=exploration_uc,
                    variant=variant,
                ):
                    first = run_public_transient_hidden_route(
                        variant=variant, planning_uc=planning_uc,
                        exploration_uc=exploration_uc,
                    )
                    independent = run_public_transient_hidden_route(
                        variant=variant, planning_uc=planning_uc,
                        exploration_uc=exploration_uc,
                    )
                    # Independent individuals, same physical inputs, budgets,
                    # two snapshot captures and two post-run restores.
                    self.assertEqual(first, independent)
                    self.assertEqual(first.to_json(), independent.to_json())
                    self.assertEqual(first.protocol_version, PROTOCOL)
                    self.assertFalse(first.heldout)
                    self.assertIsNone(first.scientific_verdict)
                    self.assertEqual(first.steps, 10)
                    self.assertEqual(len(first.captures), 10)
                    self.assertEqual(len(first.actions), 10)
                    self.assertEqual(
                        set(first.registered_sites), set(first.captures),
                    )
                    self.assertEqual(
                        first.external_inputs_received,
                        (
                            (3, 0, "set_danger_zone",
                             variant == "hidden_transient"),
                            (5, 0, "set_danger_zone", False),
                        ),
                    )
                    self.assertEqual(
                        first.external_inputs_applied, ((3, 0), (5, 0)),
                    )
                    self.assertEqual(
                        tuple(s.step for s in first.snapshot_evidence),
                        (4, 5),
                    )
                    self.assertEqual(
                        tuple(s.scenario_next_index
                              for s in first.snapshot_evidence),
                        (1, 2),
                    )
                    self.assertEqual(
                        tuple(s.physical_hazard_active
                              for s in first.snapshot_evidence),
                        (variant == "hidden_transient", False),
                    )
                    self.assertEqual(first.snapshot_restorations_verified, 2)
                    # Every successful restore writes an occurrence. Do not
                    # confuse the post-restore trace with the ten-step trace.
                    self.assertNotEqual(
                        first.journal_sha256_before_restore,
                        first.journal_sha256_after_restore,
                    )
                    self.assertGreaterEqual(first.danger_damage_total, 0.0)
                    self.assertGreaterEqual(first.final_integrity_before_restore, 0.0)
                    self.assertLessEqual(first.final_integrity_before_restore, 100.0)

                    if planning_uc == 0:
                        self.assertEqual(first.accepted_route_search_uc, 0)
                        self.assertEqual(first.accepted_preflight_uc, 0)
                        self.assertEqual(first.accepted_build_uc, 0)
                        self.assertEqual(first.applied_route_steps, 0)
                    if exploration_uc == 0:
                        self.assertEqual(first.accepted_exploration_observe_uc, 0)
                        self.assertEqual(first.applied_route_steps, 0)
                    # Costs for any actual funded route must be explicit.
                    self.assertGreaterEqual(first.accepted_route_search_uc, 0)
                    self.assertGreaterEqual(first.accepted_preflight_uc, 0)
                    self.assertGreaterEqual(first.accepted_build_uc, 0)
                    rows[variant] = first
                    print("stage11_public_transient_hidden_route=" + first.to_json())

            clear, hidden = rows["control"], rows["hidden_transient"]
            # Both schedules are present from birth but differ only in
            # Lab/WorldBody physical truth starting at step 3.
            self.assertEqual(
                clear.initial_local_sha256, hidden.initial_local_sha256,
            )
            self.assertEqual(clear.initial_safety_status,
                             hidden.initial_safety_status)
            self.assertEqual(clear.initial_safety_status, "unknown")
            self.assertEqual(
                clear.pre_change_perception_sha256,
                hidden.pre_change_perception_sha256,
            )
            self.assertEqual(clear.captures[:2], hidden.captures[:2])
            self.assertEqual(clear.actions[:2], hidden.actions[:2])
            # After the truth changes, *do not* force equal actions, safety
            # knowledge or learned state: body consequences may be perceived.
            # The (3,2) hazard is a Lab-only physical condition, not a
            # gifted canonical causal fact.

    def test_only_registered_conditions_and_schedule_are_accepted(self):
        for args in (
            {"variant": "unknown", "planning_uc": 4, "exploration_uc": 4},
            {"variant": "control", "planning_uc": -1, "exploration_uc": 4},
            {"variant": "control", "planning_uc": 5, "exploration_uc": 4},
            {"variant": "control", "planning_uc": True, "exploration_uc": 4},
            {"variant": "control", "planning_uc": 4, "exploration_uc": 1},
            {"variant": "control", "planning_uc": 4, "exploration_uc": True},
            {"variant": "control", "planning_uc": 3, "exploration_uc": 0},
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                run_public_transient_hidden_route(**args)
        with self.assertRaises(ValueError):
            schedule_for("unknown")
        for variant in VARIANTS:
            events = schedule_for(variant)
            self.assertEqual(
                [(e.t_monde, e.sequence, e.operation) for e in events],
                [(3, 0, "set_danger_zone"), (5, 0, "set_danger_zone")],
            )
            self.assertEqual(
                [e.payload["active"] for e in events],
                [variant == "hidden_transient", False],
            )
