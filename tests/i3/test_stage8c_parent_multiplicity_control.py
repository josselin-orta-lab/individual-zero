"""Pure, World-free Stage8-C design falsifiers, not a new cohort."""
import hashlib
import inspect
import unittest
from collections import Counter

from i3.lab import stage8c_parent_multiplicity_control as C

KEY = bytes(range(32))


class Stage8CParentMultiplicityControlTests(unittest.TestCase):
    def test_bijection_is_reproducible_and_domain_separated(self):
        a = C.blinded_permutation(population=0, generation=1, key=KEY)
        self.assertEqual(set(a), set(range(24)))
        self.assertEqual(a, C.blinded_permutation(population=0, generation=1, key=KEY))
        self.assertNotEqual(a, C.blinded_permutation(population=1, generation=1, key=KEY))
        self.assertNotEqual(a, C.blinded_permutation(population=0, generation=2, key=KEY))
        self.assertNotEqual(a, C.blinded_permutation(population=0, generation=1, key=b"!" * 32))
        self.assertEqual(hashlib.sha256(bytes(a)).hexdigest(),
                         "5f6f5301a30031f3d4e4dada40e06ef602d117836afc32f2b61cdc89106de3b4")

    def test_exact_parent_count_and_multiplicity_are_matched(self):
        draws = [0] * 7 + [4] * 5 + [17] * 3 + list(range(9))
        self.assertEqual(len(draws), 24)
        unchanged = draws[:]
        matched = C.matched_parent_draws(draws, population=0, generation=1, key=KEY)
        self.assertEqual(draws, unchanged)
        self.assertEqual(len(matched), 24)
        self.assertEqual(len(set(matched)), len(set(draws)))
        self.assertEqual(sorted(Counter(draws).values()),
                         sorted(Counter(matched).values()))

    def test_uniform_and_full_concentration_edge_cases(self):
        for draws in [list(range(24)), [3]*24]:
            matched = C.matched_parent_draws(draws, population=19, generation=2, key=KEY)
            self.assertEqual(len(set(matched)), len(set(draws)))
            self.assertEqual(sorted(Counter(matched).values()), sorted(Counter(draws).values()))

    def test_malformed_coordinates_and_incomplete_draws_fail_closed(self):
        for bad in ([0]*23, [0]*25, [0]*23 + [24], [0]*23 + [-1],
                    [0]*23 + [True], None, "0"*24):
            with self.subTest(draws=repr(bad)), self.assertRaises(ValueError):
                C.matched_parent_draws(bad, population=0, generation=1, key=KEY)
        for opts in ({"population":True, "generation":1, "key":KEY},
                     {"population":-1, "generation":1, "key":KEY},
                     {"population":0, "generation":0, "key":KEY},
                     {"population":0, "generation":3, "key":KEY},
                     {"population":0, "generation":1, "key":b"x"},
                     {"population":0, "generation":1, "key":"x"*32}):
            with self.subTest(opts=opts), self.assertRaises(ValueError):
                C.blinded_permutation(**opts)

    def test_pure_score_free_api_cannot_accept_fitness_or_world(self):
        self.assertEqual(set(inspect.signature(C.matched_parent_draws).parameters),
                         {"reference_slots", "population", "generation", "key"})
        self.assertEqual(set(inspect.signature(C.blinded_permutation).parameters),
                         {"population", "generation", "key"})


if __name__ == "__main__":
    unittest.main()
