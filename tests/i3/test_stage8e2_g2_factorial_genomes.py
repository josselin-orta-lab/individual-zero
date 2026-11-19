"""Pure native-v4 Stage8-E2 G2 factorial genome contract tests."""
from copy import deepcopy
import unittest

from i3.lab import stage8e2_g2_factorial_genomes as F
from i3.modules import genome as G


def input_pairs():
    return {(p, s): {"S": G.generation_zero(100000 + p*24 + s),
                      "M": G.generation_zero(200000 + p*24 + s)}
            for p in range(64) for s in range(24)}


class Stage8E2FactorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pairs = input_pairs()
        cls.offspring = F.assemble_g2(cls.pairs)

    def test_four_arm_complete_and_reaudited(self):
        report = F.independent_genotype_audit(self.pairs, self.offspring)
        self.assertEqual(report["g2_genome_copies"], 6144)
        self.assertEqual(report["g2_planned_lives"], 36864)
        self.assertFalse(report["original_gzip_audited"])
        self.assertFalse(report["scientific_claim_authorized"])

    def test_reject_missing_pair_and_foreign_arm(self):
        p = dict(self.pairs)
        del p[0, 0]
        with self.assertRaises(ValueError):
            F.assemble_g2(p)
        broken = dict(self.offspring)
        del broken[0, "S_sham", 0]
        with self.assertRaises(ValueError):
            F.independent_genotype_audit(self.pairs, broken)

    def test_falsify_non_gamma_mutation_and_partial_swap(self):
        broken = dict(self.offspring)
        gene = "omega"
        changed = deepcopy(broken[0, "S_swap", 0])
        changed["genes"][gene] = self.pairs[0, 0]["M"]["genes"][gene]
        # Force a detectable non-gamma change even if parental alleles match.
        if changed["genes"][gene] == self.pairs[0, 0]["S"]["genes"][gene]:
            changed["genes"][gene] += 0.01
        broken[0, "S_swap", 0] = changed
        with self.assertRaises(ValueError):
            F.independent_genotype_audit(self.pairs, broken)
        partial = dict(self.offspring)
        changed = deepcopy(partial[0, "S_swap", 0])
        changed["genes"]["gamma3"] = self.pairs[0, 0]["S"]["genes"]["gamma3"]
        partial[0, "S_swap", 0] = changed
        if self.pairs[0, 0]["S"]["genes"]["gamma3"] != self.pairs[0, 0]["M"]["genes"]["gamma3"]:
            with self.assertRaises(ValueError):
                F.independent_genotype_audit(self.pairs, partial)


if __name__ == "__main__":
    unittest.main()
