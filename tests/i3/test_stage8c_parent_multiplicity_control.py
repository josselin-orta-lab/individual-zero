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


    def test_control_offspring_v4_own_ancestry_and_mutation_receipts(self):
        from copy import deepcopy
        from i3.modules import genome as G

        parents = {slot: G.generation_zero(10000 + slot) for slot in range(24)}
        frozen = deepcopy(parents)
        seeds = tuple((6 << 60) + slot + 1000 for slot in range(24))
        selected = [0]*7 + [4]*5 + [17]*3 + list(range(9))
        manifest = "a" * 64
        children, receipts = C.build_matched_offspring(
            selected, parents, seeds, parent_generation_arm="shared", population=2, generation=1,
            key=KEY, prior_manifest_sha256=manifest)
        self.assertEqual(parents, frozen)
        self.assertEqual(set(children), set(range(24)))
        self.assertEqual(len(receipts), 24)
        self.assertEqual(sorted(Counter(r["parent_slot"] for r in receipts).values()),
                         sorted(Counter(selected).values()))
        for slot, claim in enumerate(receipts):
            parent_slot = claim["parent_slot"]
            self.assertEqual(claim["arm"], "matched_multiplicity")
            self.assertEqual(claim["parent_generation_arm"], "shared")
            self.assertEqual(claim["selected_reference_slots_sha256"],
                             hashlib.sha256(str(selected).replace(" ", "").encode()).hexdigest())
            self.assertEqual(claim["parent_genome_sha256"], G.digest(parents[parent_slot]))
            self.assertEqual(claim["offspring_genome_sha256"], G.digest(children[slot]))
            self.assertEqual(claim["prior_generation_manifest_sha256"], manifest)
            self.assertEqual(claim["mutation_seed"], seeds[slot])
            self.assertEqual(
                children[slot], G.mutate(parents[parent_slot], seeds[slot], scale=0.1))
        # Same sealed plan, mutation and control ancestry must reproduce bitwise.
        again, witnesses = C.build_matched_offspring(
            selected, parents, seeds, parent_generation_arm="shared", population=2, generation=1,
            key=KEY, prior_manifest_sha256=manifest)
        self.assertEqual((children, receipts), (again, witnesses))

    def test_control_offspring_rejects_bad_ancestry_before_mutation(self):
        from i3.modules import genome as G

        parents = {slot: G.generation_zero(2000 + slot) for slot in range(24)}
        seeds = tuple((6 << 60) + slot + 4000 for slot in range(24))
        inputs = ([0]*24, parents, seeds)
        opts = dict(parent_generation_arm="matched_multiplicity", population=0, generation=2, key=KEY,
                    prior_manifest_sha256="b"*64)
        failures = (
            (([0]*23, parents, seeds), opts),
            ((([0]*23)+[24], parents, seeds), opts),
            (([0]*24, {s:g for s,g in parents.items() if s != 23}, seeds), opts),
            (([0]*24, parents, seeds[:-1]), opts),
            (([0]*24, parents, seeds[:-1]+(seeds[0],)), opts),
            (([0]*24, parents, tuple([True]+list(seeds[1:]))), opts),
            (inputs, {**opts, "prior_manifest_sha256": "not-a-digest"}),
            (inputs, {**opts, "key": b"x"}),
            (inputs, {**opts, "parent_generation_arm": "selected"}),
            (inputs, {**opts, "generation": 1}),
        )
        for args, kwargs in failures:
            with self.subTest(args=str(args[0])[:28], kw=str(kwargs)[:40]):
                with self.assertRaises(ValueError):
                    C.build_matched_offspring(*args, **kwargs)
        self.assertNotIn("fitness", inspect.signature(C.build_matched_offspring).parameters)
        self.assertNotIn("score", inspect.signature(C.build_matched_offspring).parameters)



if __name__ == "__main__":
    unittest.main()
