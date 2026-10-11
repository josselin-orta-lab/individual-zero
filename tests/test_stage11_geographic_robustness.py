"""Public non-held-out obstacle and physical creature geographic coverage."""
from unittest import TestCase

from lab.stage11_geographic_robustness_probe import (
    VARIANTS, run_public_layout_coverage,
)


class PublicGeographicRobustnessTests(TestCase):
    def test_four_fixed_public_layouts_keep_physical_custody_and_safety(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                row = run_public_layout_coverage(
                    variant=variant, steps=6,
                )
                self.assertEqual(row.classification,
                                 "development_only_not_heldout")
                self.assertFalse(row.heldout)
                self.assertIsNone(row.scientific_verdict)
                self.assertEqual(row.known_lethal_visits, 0)
                self.assertEqual(row.creature_occupied_visits, 0)
                self.assertGreaterEqual(row.geographic_distinct_sites, 1)
                self.assertGreaterEqual(
                    row.proposed_frontiers, row.geographic_applied_commands,
                )
                if variant != "visible_creature_north":
                    self.assertGreaterEqual(
                        row.geographic_distinct_sites,
                        row.ablation_distinct_sites,
                    )
                if variant == "east_corridor":
                    self.assertTrue(row.proposed_directions)
                    self.assertTrue(all(direction == "east"
                                        for direction in row.proposed_directions))
                if variant in ("north_obstacle", "known_lethal_north"):
                    self.assertNotEqual(row.proposed_directions[:1], ("north",))
                if variant == "known_lethal_north":
                    self.assertGreater(row.blocked_frontier_rejections, 0)
                print("stage11_public_geographic_layout=" + row.to_json())

    def test_known_creature_layout_reexecutes_identically(self):
        first = run_public_layout_coverage(
            variant="visible_creature_north", steps=6,
        )
        second = run_public_layout_coverage(
            variant="visible_creature_north", steps=6,
        )
        self.assertEqual(first, second)
        self.assertNotEqual(first.ablation_journal_sha256, "")
        self.assertNotEqual(first.geographic_journal_sha256, "")

    def test_only_declared_public_layouts_and_bounded_step_counts(self):
        for bad in (-1, 0, 3, 13, True, "6"):
            with self.subTest(steps=bad), self.assertRaises(ValueError):
                run_public_layout_coverage(
                    variant="north_obstacle", steps=bad,
                )
        with self.assertRaises(ValueError):
            run_public_layout_coverage(
                variant="private_hidden_layout", steps=6,
            )


if __name__ == "__main__":
    import unittest
    unittest.main()
