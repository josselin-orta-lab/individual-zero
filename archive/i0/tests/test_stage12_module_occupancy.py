"""Stage12 occupancy entropy measures module slots, not repeated contexts."""
import unittest
from i0.modules.stage12_occupancy import module_occupancy_entropy


class ModuleOccupancyTests(unittest.TestCase):
    def test_empty_current_st_is_unknown(self):
        x = module_occupancy_entropy({}, warning_fraction=0.2, module_universe_size=4)
        self.assertIsNone(x.low_entropy)
        self.assertIsNone(x.normalized_entropy)
        self.assertEqual(x.status, "unavailable_empty_st")

    def test_one_dominant_module_and_balanced_modules(self):
        concentrated = module_occupancy_entropy(
            {"perception": 4, "planning": 0}, warning_fraction=0.25,
            module_universe_size=4,
        )
        self.assertEqual(concentrated.normalized_entropy, 0.0)
        self.assertTrue(concentrated.low_entropy)
        balanced = module_occupancy_entropy(
            {"perception": 1, "planning": 1, "memory": 1, "value_needs": 1},
            warning_fraction=0.25, module_universe_size=4,
        )
        self.assertEqual(balanced.normalized_entropy, 1.0)
        self.assertFalse(balanced.low_entropy)
        self.assertEqual(balanced.occupied_slots, 4)

    def test_fixed_universe_prevents_false_normalization(self):
        partial = module_occupancy_entropy(
            {"planning": 1, "perception": 1},
            warning_fraction=0.55, module_universe_size=4,
        )
        self.assertAlmostEqual(partial.normalized_entropy, 0.5)
        self.assertTrue(partial.low_entropy)

    def test_rejects_ambiguous_or_fabricated_occupancy(self):
        for counts in ({"planning": -1}, {"planning": True}, {"": 1},
                       {"a": 1, "b": 1, "c": 1}):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                module_occupancy_entropy(
                    counts, warning_fraction=0.25, module_universe_size=2,
                )
        for ratio in (-0.1, 1.1, float("nan"), True):
            with self.subTest(ratio=ratio), self.assertRaises(ValueError):
                module_occupancy_entropy(
                    {"planning": 1}, warning_fraction=ratio,
                    module_universe_size=4,
                )


if __name__ == "__main__":
    unittest.main()
