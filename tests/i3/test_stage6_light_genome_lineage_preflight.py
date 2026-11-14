"""Exact native-v4 genotype parity with fabricated OFFLINE lineage metadata.

These fixtures call genome generation/mutation only, never run_life, birth,
World, real seeds, real originals or parent selection from lived scores.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

from i3.lab import stage6_light_genome_lineage_preflight as v
from i3.modules import genome as native


def fake_lineage(populations=(0,)):
    founders, descendants, native_index = [], [], []
    parents = {}
    for p in populations:
        for slot in range(24):
            seed = 100000 + p*24 + slot
            value = native.generation_zero(seed)
            found = {"population": p, "slot": slot, "seed": seed,
                     "genome": value, "genome_sha256": native.digest(value)}
            founders.append(found)
            parents[p, 0, "shared", slot] = value
            native_index.append({"population": p, "generation": 0,
                                 "arm": "shared", "slot": slot,
                                 "genome_sha256": native.digest(value)})
    for gen in (1, 2):
        for p in populations:
            for arm_i, arm in enumerate(v.ARMS):
                for slot in range(24):
                    parent_slot = (slot + gen + arm_i) % 24
                    parent = parents[p, gen-1, "shared" if gen == 1 else arm,
                                     parent_slot]
                    seed = 200000 + gen*100000 + p*100 + arm_i*24 + slot
                    child = native.mutate(parent, seed, scale=0.1)
                    descendants.append({
                        "population": p, "generation": gen, "arm": arm,
                        "slot": slot, "parent_slot": parent_slot,
                        "mutation_seed": seed,
                        "parent_genome_sha256": native.digest(parent),
                        "genome": child, "genome_sha256": native.digest(child),
                    })
                    parents[p, gen, arm, slot] = child
                    native_index.append({"population": p, "generation": gen,
                                         "arm": arm, "slot": slot,
                                         "genome_sha256": native.digest(child)})
    return founders, descendants, native_index


class Stage6GenomeLineageOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = fake_lineage()

    def audit(self, sample=None, *, populations=(0,)):
        a, b, c = deepcopy(self.sample if sample is None else sample)
        return v.inspect_claimed_lineage(a, b, c,
                                         fixture_populations=populations)

    def test_reference_algorithm_parity_several_seeds_and_bounds(self):
        self.assertEqual(v.GENE_ORDER, native.GENE_ORDER)
        self.assertEqual(v.custody.BOUNDS, native.BOUNDS)
        for seed in (0, 1, 77, 100000, 2**31-1):
            parent = native.generation_zero(seed)
            self.assertEqual(v._generation_zero(seed), parent)
            self.assertEqual(v._digest(parent), native.digest(parent))
            for mut_seed in (0, 3, 2**31-1):
                offspring = native.mutate(parent, mut_seed, scale=0.1)
                self.assertEqual(v._mutate(parent, mut_seed), offspring)
                self.assertEqual(v._digest(offspring), native.digest(offspring))

    def test_complete_synthetic_single_population_not_full_pass(self):
        r = self.audit()
        self.assertEqual(r["status"], "PARTIAL_FIXTURE_MATCH_ONLY_NOT_ADMITTED")
        self.assertEqual(r["founder_genomes_checked"], 24)
        self.assertEqual(r["offspring_mutations_checked"], 96)
        self.assertEqual(r["original_genotype_claims_joined"], 120)
        self.assertFalse(r["parent_sampling_law_verified"])
        self.assertFalse(r["external_seed_allocation_verified"])
        self.assertFalse(r["native_original_bytes_read"])
        self.assertFalse(r["owner_authorization"])
        self.assertEqual(r["new_worlds_opened"], 0)
        self.assertEqual(r["new_lives_created"], 0)
        self.assertEqual(r["science_verdict"], "NOT_ISSUED")

    def test_exact_full_synthetic_shape_never_admits_science(self):
        sample = fake_lineage(tuple(range(16)))
        r = v.inspect_claimed_lineage(*sample)
        self.assertEqual(r["status"], "GENOME_CHAIN_MATCH_ONLY_NOT_ADMITTED")
        self.assertEqual((r["founder_genomes_checked"],
                          r["offspring_mutations_checked"],
                          r["original_genotype_claims_joined"]), (384, 1536, 1920))
        self.assertFalse(r["independent_source_custody_verified"])
        self.assertFalse(r["owner_authorization"])

    def test_mismatched_founder_and_self_consistent_forgery_are_rejected(self):
        sample = deepcopy(self.sample)
        sample[0][0]["genome"]["genes"]["beta_u"] = 0.4
        sample[0][0]["genome_sha256"] = native.digest(sample[0][0]["genome"])
        with self.assertRaises(ValueError):
            self.audit(sample)

    def test_parent_swap_is_not_masked_by_correct_child_hash(self):
        sample = deepcopy(self.sample)
        sample[1][0]["parent_slot"] = 23
        with self.assertRaises(ValueError):
            self.audit(sample)

    def test_wrong_mutation_seed_and_different_child_rejected(self):
        sample = deepcopy(self.sample)
        sample[1][0]["mutation_seed"] += 1
        with self.assertRaises(ValueError):
            self.audit(sample)
        sample = deepcopy(self.sample)
        sample[1][0]["genome"]["genes"]["omega"] = 0.2
        sample[1][0]["genome_sha256"] = native.digest(sample[1][0]["genome"])
        with self.assertRaises(ValueError):
            self.audit(sample)

    def test_fake_original_index_cannot_be_omitted_or_substituted(self):
        sample = deepcopy(self.sample)
        sample[2][0]["genome_sha256"] = "a"*64
        with self.assertRaises(ValueError):
            self.audit(sample)
        sample = deepcopy(self.sample)
        sample[2].pop()
        with self.assertRaises(ValueError):
            self.audit(sample)

    def test_missing_or_duplicate_founder_descendant_and_streams_fail(self):
        for section in (0, 1):
            sample = deepcopy(self.sample)
            sample[section].pop()
            with self.assertRaises(ValueError):
                self.audit(sample)
        sample = deepcopy(self.sample)
        sample[1][1]["mutation_seed"] = sample[1][0]["mutation_seed"]
        with self.assertRaises(ValueError):
            self.audit(sample)
        sample = deepcopy(self.sample)
        sample[1][1]["slot"] = sample[1][0]["slot"]
        with self.assertRaises(ValueError):
            self.audit(sample)

    def test_foreign_fields_bool_coordinates_and_false_full_pass_denied(self):
        sample = deepcopy(self.sample)
        sample[1][0]["learned_memory"] = "inherited"
        with self.assertRaises(ValueError):
            self.audit(sample)
        sample = deepcopy(self.sample)
        sample[0][0]["slot"] = True
        with self.assertRaises(ValueError):
            self.audit(sample)
        with self.assertRaises(ValueError):
            v.inspect_claimed_lineage(*self.sample)  # 1/16 cannot masquerade as full

    def test_fail_closed_method_and_no_life_methods(self):
        with patch.object(v.custody, "_assert_inert", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                self.audit()
        for action in (v.run_life, v.authorize_science):
            with self.assertRaises(PermissionError):
                action()
        path = Path(inspect.getfile(v))
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                names.append(node.module or "")
            elif isinstance(node, ast.Import):
                names.extend(a.name for a in node.names)
        self.assertFalse(any("i3.runtime" in n or "i3.modules" in n for n in names))


if __name__ == "__main__":
    unittest.main()
