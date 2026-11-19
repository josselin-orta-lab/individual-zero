"""Synthetic Stage8-E2 G0/G1/G2 genotype lineage tests, zero native lives."""
from copy import deepcopy
import unittest

from i3.lab import stage8e2_lineage_preflight as L
from i3.modules import genome as G

ROOT = "0123456789abcdef" * 4


class Stage8E2LineagePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g0 = {(p, "shared", s): G.generation_zero(100000+p*24+s)
                  for p in range(64) for s in range(24)}
        cls.f0 = {(p, "shared", s): (s % 7, 900+s)
                  for p in range(64) for s in range(24)}
        cls.g1, cls.receipts1 = L.make_descendants(
            ROOT, 1, cls.g0, cls.f0, "a"*64)
        cls.f1 = {(p, arm, s): (s % 7, 900+s)
                  for p in range(64) for arm in ("S", "M") for s in range(24)}

    def test_full_two_generation_reconstruction(self):
        a = L.audit_lineage_structure(ROOT, 1, self.g0,
                                     self.g1, self.receipts1)
        self.assertEqual(a["genomes_reconstructed"], 3072)
        self.assertTrue(a["parental_occupancy_matched"])
        self.assertFalse(a["original_gzip_audited"])
        g2, receipts = L.make_descendants(ROOT, 2, self.g1,
                                          self.f1, "b"*64)
        b = L.audit_lineage_structure(ROOT, 2, self.g1, g2, receipts)
        self.assertEqual(b["genomes_reconstructed"], 3072)
        self.assertFalse(b["scientific_claim_authorized"])

    def test_parent_fitness_coverage_is_mandatory(self):
        bad = dict(self.f0)
        bad.pop((0, "shared", 0))
        with self.assertRaises(ValueError):
            L.make_descendants(ROOT, 1, self.g0, bad, "a"*64)
        bad = dict(self.f0)
        bad[0, "shared", 0] = (7, 900)
        with self.assertRaises(ValueError):
            L.make_descendants(ROOT, 1, self.g0, bad, "a"*64)

    def test_mutation_and_parent_receipt_tampering_rejected(self):
        wrong = deepcopy(self.receipts1)
        wrong[0]["mutation_seed"] += 1
        with self.assertRaises(ValueError):
            L.audit_lineage_structure(ROOT, 1, self.g0, self.g1, wrong)
        wrong = deepcopy(self.receipts1)
        wrong[0]["parent_slot"] = (wrong[0]["parent_slot"]+1) % 24
        with self.assertRaises(ValueError):
            L.audit_lineage_structure(ROOT, 1, self.g0, self.g1, wrong)
        with self.assertRaises(ValueError):
            L.audit_lineage_structure(ROOT, 1, self.g0,
                                      self.g1, self.receipts1[:-1])

    def test_no_sealed_native_claim_from_synthetic_inputs(self):
        self.assertTrue(all(r["selection_provenance_unverified"]
                            for r in self.receipts1))
        first = L.make_descendants(ROOT, 1, self.g0, self.f0, "a"*64)
        self.assertEqual(self.receipts1, first[1])


if __name__ == "__main__":
    unittest.main()
