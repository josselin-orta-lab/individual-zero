"""Synthetic, pure Stage8-B independent original-level reduction tests.

No native physics, motor, World, genome, mutation or new life is executed.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from i3.lab import stage8b_independent_original_audit as V
from i3.lab import stage8b_independent_reduced_audit as R


def fake_data():
    all_totals={}
    family_totals={}
    report=[]
    for p in range(32):
        all_totals[p,0,"shared"]={"lives":144,"steps":144*200,"censored":0}
        for g in (1,2):
            for arm in V.ARMS:
                all_totals[p,g,arm]={"lives":144,"steps":144*200,"censored":0}
        # selected has modest improvement for stable/depletion and a
        # deterioration for pulse. Integral native steps, no fake World calls.
        family_steps={
            "stable":(210,200),
            "depletion":(208,200),
            "pulse":(199,200),
        }
        for f,(s,r) in family_steps.items():
            family_totals[p,"selected",f]=[48,48*s,0]
            family_totals[p,"random_parent",f]=[48,48*r,0]
        s2=sum(family_totals[p,"selected",f][1] for f in V.FAMILIES)
        r2=sum(family_totals[p,"random_parent",f][1] for f in V.FAMILIES)
        all_totals[p,2,"selected"]["steps"]=s2
        all_totals[p,2,"random_parent"]["steps"]=r2
        report.append({
            "population":p,"panel":p//16,
            "G0_mean_steps":200.,
            "G1_selected_mean_steps":200.,
            "G1_random_mean_steps":200.,
            "G2_selected_mean_steps":s2/144,
            "G2_random_mean_steps":r2/144,
            "G1_selected_minus_random_steps":0.,
            "G2_selected_minus_random_steps":(s2-r2)/144,
            "G2_selected_horizon_survival":0.,
            "G2_random_horizon_survival":0.,
            "G2_families_descriptive":{
                f:{
                    "selected_minus_random_mean_steps":(s-r),
                    "selected_horizon_fraction":0.,
                    "random_horizon_fraction":0.,
                } for f,(s,r) in family_steps.items()
            },
        })
    return all_totals,family_totals,report


class Stage8BIndependentOriginalAuditPureTests(unittest.TestCase):
    def test_all_32_population_family_original_totals_are_retained(self):
        counts,families,rows=fake_data()
        recomputed=V.from_original_counts(counts,families,rows)
        self.assertEqual(len(recomputed),32)
        self.assertEqual(recomputed[0],{"stable":10.,"depletion":8.,"pulse":-1.})
        x=R.reduce_omnibus(recomputed)
        # Equal effects in all 32 populations => singular covariance, no GO.
        self.assertEqual(x["status"],R.NO)
        self.assertEqual(x["p_value_two_sided_omnibus"],1.)

    def test_any_fraudulent_published_family_effect_is_rejected(self):
        counts,families,rows=fake_data()
        mutated=deepcopy(rows)
        mutated[11]["G2_families_descriptive"]["pulse"][
            "selected_minus_random_mean_steps"]=14.
        with self.assertRaises(ValueError):
            V.from_original_counts(counts,families,mutated)
        mutated=deepcopy(rows)
        mutated[15]["G2_selected_minus_random_steps"]=42.
        with self.assertRaises(ValueError):
            V.from_original_counts(counts,families,mutated)

    def test_original_counts_cannot_be_partial_or_misindexed(self):
        counts,families,rows=fake_data()
        with self.assertRaises(ValueError):
            V.from_original_counts(counts,families,rows[:-1])
        mutated=deepcopy(rows)
        mutated[20]["panel"]=0
        with self.assertRaises(ValueError):
            V.from_original_counts(counts,families,mutated)
        del counts[1,2,"selected"]
        with self.assertRaises((ValueError,KeyError)):
            V.from_original_counts(counts,families,rows)

    def test_foreign_or_mutated_science_plan_sha_rejected(self):
        plan={"schema":V.SCHEMA_SCIENCE,"scientific_admission":True}
        plan["allocation_sha256"]=V._digest_plan(plan)
        self.assertIs(V._assert_plan(plan,V.SCHEMA_SCIENCE),plan)
        modified=dict(plan)
        modified["scientific_admission"]=False
        with self.assertRaises(ValueError):
            V._assert_plan(modified,V.SCHEMA_SCIENCE)
        with self.assertRaises(ValueError):
            V._assert_plan(plan,"i3-stage8a-mean-persistence-science-plan/v1")

    def test_missing_scientific_originals_must_not_create_lives(self):
        with TemporaryDirectory() as tmp:
            science=Path(tmp)/"never-born"
            with self.assertRaises(FileNotFoundError):
                V.audit_full(str(Path(tmp)/"absent-plan.json"),
                             str(science),
                             str(Path(tmp)/"absent-result.json"))
            self.assertFalse(science.exists())


if __name__ == "__main__":
    unittest.main()
