"""No-World synthetic falsifiers for Stage8-E association, never new lives."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i3.lab import stage8e_gene_associations_readonly as E
from i3.modules import genome as G


def fixture():
    means={}
    for p in range(32):
        for gen in E.GENS:
            for arm in E.ARMS:
                values = [0.5]*len(E.GENES)
                if arm=="selected":
                    values[E.GENES.index("omega")]=0.5+(p-15.5)/80
                    values[E.GENES.index("beta_u")]=0.5-(p-15.5)/80
                means[p,gen,arm]=tuple(values)
    profiles=[{"population":p,
               "G2_S_minus_M_steps":(p+1)/2
               if p not in (0,1,3,11,16,18,19,24,28,31)
               else -(p+1)/10}
              for p in range(32)]
    return profiles,means


class Stage8EGeneAssociationNoBirthTests(unittest.TestCase):
    def test_gene_list_is_full_native_v4_no_posthoc_filter(self):
        self.assertEqual(E.GENES, tuple(G.BOUNDS))
        self.assertIn("omega", E.GENES)
        self.assertIn("temperament.exploration", E.GENES)
        self.assertEqual(E.SLOTS,24)

    def test_population_means_include_all_g1_g2_and_adverse(self):
        rows,means=fixture()
        z=E.from_population_means(rows,means)
        self.assertEqual(z["population_units"],32)
        self.assertEqual(z["adverse_population_ids"],
                         [0,1,3,11,16,18,19,24,28,31])
        self.assertEqual(len(z["ranked_gene_associations"]),len(E.GENES))
        self.assertEqual(len(z["all_32_population_gene_profiles"]),32)
        self.assertEqual(set(r["gene"] for r in z["ranked_gene_associations"]),
                         set(G.BOUNDS))
        self.assertTrue(all("p_value" not in k
                            for k in z["ranked_gene_associations"][0]))
        self.assertIn("MULTIPLE_COMPARISONS", z["statistical_scope"])
        self.assertEqual(z["new_lives"],0)

    def test_missing_populations_arms_and_invalid_floats_fail_closed(self):
        rows,means=fixture()
        with self.assertRaises(ValueError):
            E.from_population_means(rows[:-1],means)
        broken=list(rows)
        broken[6]=deepcopy(broken[5])
        with self.assertRaises(ValueError):
            E.from_population_means(broken,means)
        corrupted=dict(means)
        del corrupted[11,2,"selected"]
        with self.assertRaises(ValueError):
            E.from_population_means(rows,corrupted)
        corrupted=dict(means)
        v=list(corrupted[3,1,"selected"]);v[0]=float("nan")
        corrupted[3,1,"selected"]=tuple(v)
        with self.assertRaises(ValueError):
            E.from_population_means(rows,corrupted)
        corrupted=dict(means)
        v=list(corrupted[3,1,"selected"]);v[0]=1.01
        corrupted[3,1,"selected"]=tuple(v)
        with self.assertRaises(ValueError):
            E.from_population_means(rows,corrupted)

    def test_zero_variance_correlation_stays_null_not_significant(self):
        rows,means=fixture()
        rows=[{**x,"G2_S_minus_M_steps":
               (0 if x["population"] in (2,4,5,6,7,8,9,10,12,13,14,15,17,20,21,22,23,25,26,27,29,30) else
                (-1 if x["population"] in [0,1,3,11,16,18,19,24,28,31] else 0))}
              for x in rows]
        # constant gene deltas, unlike varying outcomes
        const={k: tuple([0.5]*len(E.GENES)) for k in means}
        z=E.from_population_means(rows,const)
        self.assertTrue(all(r["G2_population_delta_vs_persistence_Pearson"] is None
                            for r in z["ranked_gene_associations"]))
        self.assertIsNone(z["ranked_gene_associations"][0][
            "leave_one_population_out_sign_agreement_fraction"])

    def test_original_audit_must_precede_any_genetic_read(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises((FileNotFoundError,ValueError)):
                E.audit_full(str(root/"missing-plan.json"),
                             str(root/"missing-originals"),
                             str(root/"missing-preverdict.json"))
            self.assertEqual(list(root.iterdir()),[])

    def test_pearson_uses_clusters_only(self):
        self.assertEqual(E._corr([1.,2.,3.],[3.,2.,1.]),-1.)
        self.assertIsNone(E._corr([1.,1.,1.],[2.,3.,4.]))
        with self.assertRaises(ValueError):
            E._corr([1.,2.],[3.,4.])


if __name__ == "__main__":
    unittest.main()
