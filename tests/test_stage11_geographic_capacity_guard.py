"""Opt-in, public Stage-11 Scheduler admission guard tests.

Software bookkeeping, no free Planning/Action Control/Simulator service call,
no scientific held-out, no Golden acceptance, no safety status promotion.
"""
from dataclasses import replace
from unittest import TestCase

from lab.stage11_geographic_capacity_guard_probe import (
    LEGACY_JOURNAL_SHA256_4UC, PROTOCOL, run_public_capacity_guard,
)
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_routed_junction_probe import build_public_route_runtime


class Stage11GeographicCapacityGuardTests(TestCase):
    def test_default_is_off_and_invalid_opt_in_is_rejected(self):
        implicit = build_public_route_runtime()
        disabled = build_public_route_runtime(capacity_guard=False)
        self.assertEqual(
            implicit._stage11_config.version, disabled._stage11_config.version,
        )
        self.assertEqual(
            implicit._config.compute_budget.version,
            disabled._config.compute_budget.version,
        )
        self.assertFalse(
            implicit._stage11_config.geographic_capacity_guard_enabled,
        )
        enabled = build_public_route_runtime(capacity_guard=True)
        self.assertNotEqual(
            enabled._stage11_config.version,
            implicit._stage11_config.version,
        )
        self.assertNotEqual(
            enabled._config.compute_budget.version,
            implicit._config.compute_budget.version,
        )
        self.assertTrue(
            enabled._stage11_config.geographic_capacity_guard_enabled,
        )
        for bad in (1, 0, "true", None):
            with self.subTest(flag=bad), self.assertRaises(ValueError):
                build_public_route_runtime(capacity_guard=bad)
        cfg = build_stage11_reference_runtime(enable_geography=True)
        with self.assertRaises(ValueError):
            replace(
                cfg._stage11_config,
                geographic_capacity_guard_enabled=True,
                geographic_preflight=False,
            ).validate()
        with self.assertRaises(ValueError):
            replace(
                cfg._stage11_config,
                geographic_capacity_guard_enabled=True,
                geographic=None,
            ).validate()
        # The legacy eager preflight ablation is deliberately incompatible:
        # quoting without any observed candidate cannot become free work.
        with self.assertRaises(ValueError):
            replace(
                cfg._stage11_config,
                geographic_capacity_guard_enabled=True,
                geographic_preflight_requires_frontier=False,
            ).validate()

    def test_four_uc_hazard_and_control_need_priority_and_charges(self):
        matrix = {}
        for variant in ("control", "hidden_transient"):
            for guard in (False, True):
                with self.subTest(variant=variant, guard=guard):
                    first = run_public_capacity_guard(
                        variant=variant, planning_uc=4, exploration_uc=4,
                        capacity_guard=guard,
                    )
                    replay = run_public_capacity_guard(
                        variant=variant, planning_uc=4, exploration_uc=4,
                        capacity_guard=guard,
                    )
                    self.assertEqual(first, replay)
                    self.assertEqual(first.to_json(), replay.to_json())
                    self.assertEqual(first.protocol_version, PROTOCOL)
                    self.assertFalse(first.heldout)
                    self.assertIsNone(first.scientific_verdict)
                    self.assertEqual(first.restorations_verified, 2)
                    self.assertEqual(len(first.actions), 10)
                    self.assertEqual(len(first.captured_positions), 10)
                    self.assertEqual(
                        set(first.captured_positions),
                        set(first.credited_sites),
                    )
                    self.assertEqual(
                        tuple(s[0] for s in first.snapshot_ids_and_hashes),
                        (4, 5),
                    )
                    self.assertEqual(
                        first.hazard_active_at_snapshots,
                        (variant == "hidden_transient", False),
                    )
                    if not guard:
                        self.assertEqual(
                            first.journal_sha256_before_restore,
                            LEGACY_JOURNAL_SHA256_4UC[variant],
                        )
                        self.assertEqual(first.step5_capacity_deferrals, ())
                    else:
                        self.assertNotEqual(
                            first.journal_sha256_before_restore,
                            LEGACY_JOURNAL_SHA256_4UC[variant],
                        )
                    matrix[(variant, guard)] = first
                    print("stage11_public_capacity_guard=" + first.to_json())

        baseline = matrix[("control", False)]
        control = matrix[("control", True)]
        exposed = matrix[("hidden_transient", True)]
        exposed_old = matrix[("hidden_transient", False)]
        self.assertEqual(
            control.physical_initial_sha256, exposed.physical_initial_sha256,
        )
        self.assertEqual(control.actions[:4], exposed.actions[:4])
        self.assertEqual(control.step5_applied_action[1], "se_deplacer")
        self.assertEqual(exposed.step5_applied_action[1], "attendre")
        self.assertEqual(exposed.step5_applied_action[3], "fallback")
        self.assertEqual(
            baseline.step5_applied_action, control.step5_applied_action,
        )
        self.assertEqual(
            exposed.step5_applied_action, exposed_old.step5_applied_action,
        )
        self.assertEqual(control.step5_capacity_deferrals, ())
        self.assertGreater(control.step5_geographic_proposals, 0)
        self.assertEqual(exposed.step5_geographic_proposals, 0)
        self.assertTrue(exposed.step5_capacity_deferrals)
        for cycle, required, available, charged, consulted, safety in (
            exposed.step5_capacity_deferrals
        ):
            self.assertGreaterEqual(cycle, 1)
            self.assertEqual((required, available, charged), (3, 2, 0))
            self.assertFalse(consulted)
            self.assertIsNone(safety)
        self.assertEqual(
            sum(
                uc for _, op, uc, accepted, _ in
                exposed.step5_planning_charges
                if op == "geographic_admissibility_preflight" and accepted
            ), 0,
        )
        self.assertFalse(any(
            op == "planning_build" and not accepted
            for _, op, _, accepted, _ in exposed.step5_planning_charges
        ))
        self.assertTrue(any(
            op == "planning_build" and accepted and requested == 2
            for _, op, requested, accepted, _ in
            exposed.step5_planning_charges
        ))
        self.assertGreater(
            sum(uc for _, op, uc, accepted, _ in
                exposed_old.step5_planning_charges
                if op == "geographic_admissibility_preflight" and accepted),
            0,
        )
        self.assertTrue(any(
            op == "planning_build" and not accepted and reason == "module_envelope"
            for _, op, _, accepted, reason in
            exposed_old.step5_planning_charges
        ))

    def test_low_budget_guard_does_not_create_an_unfunded_route(self):
        for variant, planning, exploration in (
            ("control", 3, 4), ("control", 0, 0),
        ):
            with self.subTest(variant=variant, planning=planning):
                guarded = run_public_capacity_guard(
                    variant=variant, planning_uc=planning,
                    exploration_uc=exploration, capacity_guard=True,
                )
                replay = run_public_capacity_guard(
                    variant=variant, planning_uc=planning,
                    exploration_uc=exploration, capacity_guard=True,
                )
                self.assertEqual(guarded, replay)
                self.assertFalse(any(
                    "frontier_route:" in (action[2] or "")
                    and action[0] == "applied"
                    for action in guarded.actions
                ))
                self.assertEqual(guarded.restorations_verified, 2)
                self.assertEqual(
                    set(guarded.captured_positions),
                    set(guarded.credited_sites),
                )
                self.assertEqual(
                    guarded.hazard_active_at_snapshots, (False, False),
                )
                if planning == 0:
                    self.assertFalse(any(
                        operation == "geographic_admissibility_preflight"
                        and accepted
                        for _, operation, _, accepted, _ in
                        guarded.step5_planning_charges
                    ))
                print("stage11_public_capacity_guard=" + guarded.to_json())

    def test_unregistered_public_capacity_guard_cases_rejected(self):
        for args in (
            dict(variant="bad", planning_uc=4, exploration_uc=4,
                 capacity_guard=True),
            dict(variant="control", planning_uc=2, exploration_uc=4,
                 capacity_guard=True),
            dict(variant="control", planning_uc=4, exploration_uc=1,
                 capacity_guard=True),
            dict(variant="control", planning_uc=4, exploration_uc=4,
                 capacity_guard=1),
            dict(variant="control", planning_uc=True, exploration_uc=4,
                 capacity_guard=False),
            dict(variant="control", planning_uc=4, exploration_uc=0,
                 capacity_guard=True),
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                run_public_capacity_guard(**args)
