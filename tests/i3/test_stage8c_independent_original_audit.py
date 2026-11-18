"""World-free falsifiers for Stage8-C independent 32,256-gzip audit."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
import inspect
import json
import math
import unittest

from i3.lab import stage8c_independent_original_audit as A


def cells(selected=210, matched=200, uniform=196):
    return {(p, arm): (7 + p % 5, round(x*144), 144)
            for p in range(32)
            for arm, x in (("selected", selected+p % 7),
                           ("matched_multiplicity", matched),
                           ("random_parent", uniform))}


class Stage8CIndependentOriginalAuditTests(unittest.TestCase):
    def test_independent_population_student_rule_and_adverse_profiles(self):
        positive = A.primary_from_population_counts(cells())
        self.assertEqual(positive["status"], A.SUCCESS)
        self.assertEqual(positive["population_units"], 32)
        self.assertEqual(positive["negative_populations"], 0)
        self.assertEqual(len(positive["effects"]), 32)
        self.assertGreater(positive["one_sided_97_5_percent_lower_bound_steps"], 0)
        negative = A.primary_from_population_counts(cells(182, 200, 190))
        self.assertEqual(negative["status"], A.NEGATIVE)
        self.assertEqual(negative["positive_populations"], 0)
        self.assertEqual(len(negative["rows"]), 32)
        zero_variance = {(p, arm): (0, 200*144, 144)
                         for p in range(32) for arm in A.ARMS}
        self.assertEqual(
            A.primary_from_population_counts(zero_variance)["status"], A.NEGATIVE)

    def test_exact_32_clusters_not_32256_pseudoreplicated_lives(self):
        d = cells()
        for bad in (
            {k: v for k,v in d.items() if k != (31, "selected")},
            {**d, (32,"selected"): (1,140*144,144)},
            {**d, (0,"selected"): (1,120,144)},
            {**d, (0,"selected"): (1,1200,143)},
            {**d, (0,"selected"): (145,200*144,144)},
            {**d, (0,"selected"): (0,float("nan"),144)},
        ):
            with self.subTest(size=len(bad)), self.assertRaises((ValueError, TypeError)):
                A.primary_from_population_counts(bad)

    def test_original_gzip_both_sha_rechecked_before_body_is_trusted(self):
        original = {"identity": {"population": 4}, "life": {"terminal": "dead"}}
        raw = A.canonical(original)
        packed = gzip.compress(raw, mtime=0)
        entry = {
            "file": "life-000.json.gz", "identity": original["identity"],
            "sha256": sha256(packed).hexdigest(),
            "uncompressed_sha256": sha256(raw).hexdigest(),
        }
        self.assertEqual(A.original_packet(packed, entry),
                         (original["identity"], original["life"]))
        with self.assertRaises(ValueError):
            A.original_packet(packed+b"x", entry)
        with self.assertRaises(ValueError):
            A.original_packet(packed, {**entry, "uncompressed_sha256": "0"*64})
        with self.assertRaises(ValueError):
            A.original_packet(packed, {**entry, "identity": {"population": 5}})
        with self.assertRaises(ValueError):
            A.original_packet(packed, {**entry, "sha256": "not-a-hash"})

    def test_parent_permutation_independent_gold_and_pop_domain(self):
        key=bytes(range(32)).hex()
        a=A.permutation(0,1,key)
        self.assertEqual(sorted(a), list(range(24)))
        self.assertEqual(
            sha256(bytes(a)).hexdigest(),
            "5f6f5301a30031f3d4e4dada40e06ef602d117836afc32f2b61cdc89106de3b4")
        self.assertNotEqual(a, A.permutation(1,1,key))
        self.assertNotEqual(a, A.permutation(0,2,key))
        with self.assertRaises(ValueError):
            A.permutation(0,1,"bad")
        with self.assertRaises(ValueError):
            A.permutation(0,3,key)

    def test_published_primary_or_any_negative_population_cannot_be_rewritten(self):
        actual=A.primary_from_population_counts(cells())
        published = {
            "schema":"i3-stage8c-new-prospective-science-original/v1",
            "scientific_admission": True,
            "status":actual["status"],
            "result":{
                "status":actual["status"],
                "primary":{
                    "population_units":32,
                    "mean_G2_S_minus_M_steps":actual["mean_G2_S_minus_M_steps"],
                    "sd_G2_S_minus_M_steps":actual["sd_G2_S_minus_M_steps"],
                    "one_sided_97_5_percent_lower_bound_steps":
                        actual["one_sided_97_5_percent_lower_bound_steps"],
                    "positive_populations":actual["positive_populations"],
                    "negative_populations":actual["negative_populations"],
                    "zero_populations":actual["zero_populations"],
                    "all_population_contrasts":actual["effects"],
                },
                "all_32_population_analyses":actual["rows"],
                "secondary_descriptive":{
                    "mean_G2_S_minus_U_steps":actual["mean_G2_S_minus_U_steps"],
                    "mean_G2_M_minus_U_steps":actual["mean_G2_M_minus_U_steps"],
                },
                "native_original_lives_rehashed":32256,
                "native_mutations_reconstructed":4608,
            },
        }
        A._confirm_publication(actual, published)
        tampered=deepcopy(published)
        tampered["result"]["primary"]["all_population_contrasts"][31]+=1
        with self.assertRaises(ValueError):
            A._confirm_publication(actual, tampered)
        tampered=deepcopy(published)
        tampered["result"]["all_32_population_analyses"][3]["G2_S_minus_M_steps"]-=10
        with self.assertRaises(ValueError):
            A._confirm_publication(actual, tampered)
        tampered=deepcopy(published)
        tampered["result"]["primary"]["one_sided_97_5_percent_lower_bound_steps"]=0
        with self.assertRaises(ValueError):
            A._confirm_publication(actual, tampered)

    def test_auditor_has_no_original_physics_or_science_reducer(self):
        src=inspect.getsource(A)
        for forbidden in (
            "from i3.lab import stage8c_prospective_science",
            "from i3.lab import stage8c_three_arm_transport",
            "run_life(", "world_for_stage6(", "reduce_primary_g2(",
            "_science_reduce(", "rehearsal_receipt(", "run_science(",
        ):
            self.assertNotIn(forbidden, src)
        self.assertEqual(A.ORIGINAL_RUN_ID, 44320492293)
        self.assertEqual(A.LIVES, 32256)
        self.assertEqual(A.MUTATIONS, 4608)
        self.assertEqual(A.T_CRIT_31, 2.0395134463964077)


if __name__ == "__main__":
    unittest.main()
