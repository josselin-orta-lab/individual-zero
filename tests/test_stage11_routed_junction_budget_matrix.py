"""Public, deterministic route budget matrix; no scientific Golden claims."""
from unittest import TestCase

from lab.stage11_routed_junction_probe import (
    CONDITIONS, build_public_route_runtime, run_public_routed_junction,
)


class PublicRoutedJunctionBudgetTests(TestCase):
    def test_validated_matched_open_junction_route(self):
        row = run_public_routed_junction()
        self.assertEqual(row.steps, 10)
        self.assertEqual(row.observed_positions[:7], (
            (2, 2), (3, 2), (4, 2), (3, 2), (2, 2), (2, 3), (2, 4),
        ))
        self.assertTrue(row.returned_to_junction)
        self.assertTrue(row.observed_alternate_branch)
        self.assertEqual(row.applied_route_steps, 2)
        self.assertEqual(len(set(row.observed_positions)),
                         len(row.confirmed_visit_sites))
        self.assertEqual(row.rejected_route_search_uc, 0)

    def test_budget_denials_are_not_fictional_transits(self):
        for budget in (0, 1, 2, 3):
            with self.subTest(planning_uc=budget):
                row = run_public_routed_junction(planning_uc=budget)
                self.assertEqual(row.applied_route_steps, 0)
                self.assertEqual(row.offered_transits_remaining, 0)
                self.assertEqual(row.accepted_route_search_uc, 0)
                self.assertFalse(row.observed_alternate_branch)
        # 4 UC is the registered lower bound to pay search, preflight
        # and one 2-UC build, not a promise that Competition selects it.
        row = run_public_routed_junction(planning_uc=4)
        self.assertGreaterEqual(row.accepted_route_search_uc, 0)
        self.assertEqual(row.rejected_route_search_uc, 0)

    def test_sealed_control_does_not_fabricate_alternate_branch(self):
        row = run_public_routed_junction(layout_variant="junction_sealed")
        self.assertFalse(row.observed_alternate_branch)
        self.assertTrue(set(row.observed_positions) <= {
            (2, 2), (3, 2), (4, 2),
        })

    def test_canonical_replay_and_provenance(self):
        for variant, budget in CONDITIONS:
            with self.subTest(variant=variant, budget=budget):
                first = run_public_routed_junction(
                    layout_variant=variant, planning_uc=budget,
                )
                second = run_public_routed_junction(
                    layout_variant=variant, planning_uc=budget,
                )
                self.assertEqual(first, second)
                self.assertEqual(first.to_json(), second.to_json())
                self.assertFalse(first.heldout)
                self.assertIsNone(first.scientific_verdict)
                print("stage11_public_routed_evidence=" + first.to_json())

    def test_invalid_conditions_fail_closed(self):
        for args in (
            {"layout_variant": "unknown"},
            {"planning_uc": -1},
            {"planning_uc": 5},
            {"planning_uc": True},
        ):
            with self.subTest(**args), self.assertRaises(ValueError):
                build_public_route_runtime(**args)
        with self.assertRaises(ValueError):
            run_public_routed_junction(steps=11)
