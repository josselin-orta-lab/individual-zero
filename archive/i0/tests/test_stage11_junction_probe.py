"""Public prospective Stage-11 junction negative-control tests."""
from unittest import TestCase

from lab.stage11_junction_probe import (
    ALLOWED_OPEN, ALLOWED_SEALED, VARIANTS, run_public_junction,
)


class Stage11ObservedJunctionTests(TestCase):
    def test_observed_alternative_is_not_oracle_injected(self):
        open_case = run_public_junction(variant="junction_open")
        sealed_case = run_public_junction(variant="junction_sealed")
        self.assertTrue(open_case.east_initially_passable)
        self.assertTrue(open_case.south_initially_passable)
        self.assertTrue(sealed_case.east_initially_passable)
        self.assertFalse(sealed_case.south_initially_passable)
        self.assertNotEqual(
            open_case.initial_local_sha256, sealed_case.initial_local_sha256,
        )
        for row, allowed in (
            (open_case, ALLOWED_OPEN), (sealed_case, ALLOWED_SEALED),
        ):
            self.assertEqual(row.classification, "development_only_not_heldout")
            self.assertIsNone(row.scientific_verdict)
            self.assertFalse(row.heldout)
            self.assertEqual(row.steps, 10)
            self.assertEqual(len(row.observed_positions), 10)
            self.assertTrue(set(row.observed_positions) <= allowed)
            self.assertEqual(set(row.observed_positions),
                             set(row.confirmed_visits))
            self.assertEqual(row.observed_positions[0], (2, 2))
            self.assertEqual(len(row.actions), 10)

    def test_reexecution_matches_canonical_journal_for_both_public_worlds(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                first = run_public_junction(variant=variant)
                second = run_public_junction(variant=variant)
                self.assertEqual(first, second)
                self.assertEqual(first.to_json(), second.to_json())
                print("stage11_public_junction=" + first.to_json())

    def test_unregistered_variants_and_horizons_rejected(self):
        for inputs in (
            {"variant": "hidden"},
            {"variant": "junction_open", "steps": 9},
            {"variant": "junction_open", "steps": True},
        ):
            with self.subTest(**inputs), self.assertRaises(ValueError):
                run_public_junction(**inputs)
