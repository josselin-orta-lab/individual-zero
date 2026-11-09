"""Software-only proposed Stage-2.1 random control. Never runs a World."""
from fractions import Fraction
import random
import unittest
from i3.lab import stage2_random_equal_mean as C


class RandomEqualMeanTests(unittest.TestCase):
    def test_exact_development_mean(self):
        self.assertEqual(C.TARGET_MEAN, Fraction(5532, 867))
        self.assertEqual(C.TARGET_MEAN, Fraction(1844, 289))
        self.assertEqual((C.LOW, C.HIGH, C.HIGH_TICKETS, C.TICKETS), (6, 7, 110, 289))
        self.assertEqual(Fraction(179 * 6 + 110 * 7, 289), C.TARGET_MEAN)

    def test_reproducible_bounded_independent(self):
        first = [C.scheduled_replays(7540000, i) for i in range(100)]
        self.assertEqual(first, [C.scheduled_replays(7540000, i) for i in range(100)])
        self.assertEqual(set(first), {6, 7})
        self.assertNotEqual(first, [C.scheduled_replays(7540001, i) for i in range(100)])
        self.assertNotEqual(first, [C.scheduled_replays(7540000, i + 1) for i in range(100)])

    def test_invalid_inputs_fail_closed(self):
        for bad in (True, -1, 1.0, "1", None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                C.scheduled_replays(bad, 0)
            with self.subTest(ordinal=bad), self.assertRaises(ValueError):
                C.scheduled_replays(1, bad)

    def test_does_not_use_global_rng(self):
        random.seed(88)
        before = random.getstate()
        C.scheduled_replays(987, 11)
        self.assertEqual(random.getstate(), before)


if __name__ == "__main__":
    unittest.main()
