"""Pure causal-locus operator tests; no engine, World, life or cohort."""
from copy import deepcopy
import unittest

from i3.lab import stage8e_reciprocal_locus_swap as C
from i3.modules import genome as G


def pair():
    s=G.midpoint()
    m=G.midpoint()
    s["genes"]["omega"]=0.8
    m["genes"]["omega"]=-0.3
    s["genes"]["beta_u"]=1.2
    m["genes"]["beta_u"]=0.7
    G.validate(s);G.validate(m)
    return s,m


class Stage8ESingleLocusSwapTests(unittest.TestCase):
    def test_one_gene_reciprocal_swap_without_mutating_input(self):
        s,m=pair()
        before_s, before_m = deepcopy(s),deepcopy(m)
        r=C.reciprocal_allele_swap(s,m,gene="omega")
        self.assertEqual((s,m),(before_s,before_m))
        self.assertEqual(r["S_sham"],s)
        self.assertEqual(r["M_sham"],m)
        self.assertEqual(r["S_swap"]["genes"]["omega"],-0.3)
        self.assertEqual(r["M_swap"]["genes"]["omega"],0.8)
        self.assertEqual(r["S_swap"]["genes"]["beta_u"],1.2)
        self.assertEqual(r["M_swap"]["genes"]["beta_u"],0.7)
        self.assertEqual(r["sha256"]["S_sham"],G.digest(s))
        for k in ("S_sham","M_sham","S_swap","M_swap"):
            G.validate(r[k])
            self.assertEqual(r["sha256"][k],G.digest(r[k]))
        self.assertTrue(r["no_births"])

    def test_swap_is_reversible_involution(self):
        s,m=pair()
        x=C.reciprocal_allele_swap(s,m,gene="omega")
        y=C.reciprocal_allele_swap(x["S_swap"],x["M_swap"],gene="omega")
        self.assertEqual(y["S_swap"],s)
        self.assertEqual(y["M_swap"],m)

    def test_refuses_order_coupled_gamma_and_unknown_loci(self):
        s,m=pair()
        self.assertNotIn("gamma1",C.eligible_genes())
        for gene in ("gamma1","gamma2","gamma3","non_gene",None,0):
            with self.subTest(gene=gene),self.assertRaises(ValueError):
                C.reciprocal_allele_swap(s,m,gene=gene)

    def test_refuses_invalid_v4_genomes_no_partial_changes(self):
        s,m=pair()
        invalid=deepcopy(m)
        invalid["genes"]["omega"]=3.
        with self.assertRaises(ValueError):
            C.reciprocal_allele_swap(s,invalid,gene="omega")
        self.assertEqual(s["genes"]["omega"],0.8)
        old=deepcopy(s)
        bad=deepcopy(s)
        del bad["genes"]["beta_u"]
        with self.assertRaises(ValueError):
            C.reciprocal_allele_swap(bad,m,gene="omega")
        self.assertEqual(s,old)

    def test_gamma_horizon_block_is_valid_and_preserves_all_other_loci(self):
        s=G.generation_zero(72001)
        m=G.generation_zero(72002)
        old_s,old_m=deepcopy(s),deepcopy(m)
        r=C.reciprocal_gamma_horizon_block_swap(s,m)
        self.assertEqual((s,m),(old_s,old_m))
        self.assertEqual(r["loci_jointly_intervened"],["gamma1","gamma2","gamma3"])
        self.assertEqual(r["S_sham"],s)
        self.assertEqual(r["M_sham"],m)
        for k in G.GENE_ORDER:
            if k in C.GAMMA_HORIZONS:
                self.assertEqual(r["S_swap"]["genes"][k],m["genes"][k])
                self.assertEqual(r["M_swap"]["genes"][k],s["genes"][k])
            else:
                self.assertEqual(r["S_swap"]["genes"][k],s["genes"][k])
                self.assertEqual(r["M_swap"]["genes"][k],m["genes"][k])
        for arm in ("S_sham","M_sham","S_swap","M_swap"):
            G.validate(r[arm])
            self.assertEqual(G.digest(r[arm]),r["sha256"][arm])
        self.assertTrue(r["no_births"])

    def test_gamma_horizon_block_swap_is_reversible_and_ordered(self):
        s=G.generation_zero(7915)
        m=G.generation_zero(7916)
        a=C.reciprocal_gamma_horizon_block_swap(s,m)
        b=C.reciprocal_gamma_horizon_block_swap(a["S_swap"],a["M_swap"])
        self.assertEqual(b["S_swap"],s)
        self.assertEqual(b["M_swap"],m)
        self.assertEqual(C.GAMMA_HORIZONS,("gamma1","gamma2","gamma3"))

    def test_gamma_horizon_block_refuses_invalid_v4(self):
        s,m=pair()
        bad=deepcopy(s)
        bad["genes"]["gamma3"]=bad["genes"]["gamma1"]-0.01
        with self.assertRaises(ValueError):
            C.reciprocal_gamma_horizon_block_swap(bad,m)
        self.assertEqual(s["genes"]["omega"],0.8)

    def test_no_fabricated_replacement_when_equal_alleles(self):
        s=G.midpoint()
        m=deepcopy(s)
        r=C.reciprocal_allele_swap(s,m,gene="omega")
        self.assertEqual(r["S_sham"],r["S_swap"])
        self.assertEqual(r["M_sham"],r["M_swap"])


if __name__ == "__main__":
    unittest.main()
