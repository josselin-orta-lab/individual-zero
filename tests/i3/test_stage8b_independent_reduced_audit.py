"""Stage8-B read-only test of frozen omnibus from published POPULATION rows.

Fixtures are synthetic summaries only. No native World, no original life
generation, no evidence of a real campaign or independent original rehash.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i3.lab import stage8b_independent_reduced_audit as V


def matrix(interaction: bool):
    return [
        {"stable": 10,
         "depletion": 10 + ((p%8)-3.5)*.7 + (18 if interaction else 0),
         "pulse": 10 + (((p*7)%13)-6)*.9 + (-16 if interaction else 0)}
        for p in range(32)
    ]


def published_primary(independent):
    return {
        "schema": V.SCHEMA_PRIMARY,
        "status": independent["status"],
        "n_populations": 32,
        "alpha_fixed": .025,
        "primary_success": independent["primary_success"],
        "covariance_identifiable": independent["covariance_identifiable"],
        "hotelling_t_squared": independent["hotelling_t_squared"],
        "f_df2_30": independent["f_df2_30"],
        "p_value_two_sided_omnibus": independent["p_value_two_sided_omnibus"],
        "family_mean_selection_advantage_steps": independent["family_means"],
        "family_positive_population_counts": independent["positive_counts"],
        "two_family_contrasts_means": {
            "depletion_minus_stable": independent["pair_contrast_means"][0],
            "pulse_minus_stable": independent["pair_contrast_means"][1],
        },
        "sample_covariance_2_by_2": independent["sample_covariance"],
        "effects_per_population": independent["effects_per_population"],
    }


class Stage8BReducedIndependentAuditTests(unittest.TestCase):
    def test_independent_Hotelling_detects_global_heterogeneity(self):
        x=V.reduce_omnibus(matrix(True))
        self.assertEqual(x["status"],V.PASS)
        self.assertLess(x["p_value_two_sided_omnibus"],.025)
        self.assertTrue(x["primary_success"])
        self.assertEqual(x["family_positive_counts"]["stable"],32)

    def test_no_heterogeneity_and_singular_covariance_never_pass(self):
        self.assertEqual(V.reduce_omnibus(matrix(False))["status"],V.NO)
        x=V.reduce_omnibus([dict(stable=7,depletion=7,pulse=7)]*32)
        self.assertEqual(x["status"],V.NO)
        self.assertIsNone(x["hotelling_t_squared"])
        self.assertEqual(x["p_value_two_sided_omnibus"],1.)

    def test_invariance_to_renaming_families(self):
        a=V.reduce_omnibus(matrix(True))
        changed=[{"stable":r["pulse"],"depletion":r["stable"],
                  "pulse":r["depletion"]} for r in matrix(True)]
        b=V.reduce_omnibus(changed)
        self.assertAlmostEqual(a["hotelling_t_squared"],b["hotelling_t_squared"])
        self.assertAlmostEqual(a["p_value_two_sided_omnibus"],b["p_value_two_sided_omnibus"])

    def test_missing_population_or_nonfinite_family_never_valid(self):
        with self.assertRaises(ValueError):
            V.reduce_omnibus(matrix(True)[:-1])
        x=matrix(True)
        del x[0]["pulse"]
        with self.assertRaises(ValueError):
            V.reduce_omnibus(x)
        x=matrix(True)
        x[0]["depletion"]=float("nan")
        with self.assertRaises(ValueError):
            V.reduce_omnibus(x)

    def test_published_primary_tampering_rejected(self):
        correct=V.reduce_omnibus(matrix(True))
        p=published_primary(correct)
        V._verify_primary(p,correct)
        for key,value in (("hotelling_t_squared",1.0),
                          ("p_value_two_sided_omnibus",.9),
                          ("primary_success",False),
                          ("alpha_fixed",.05),
                          ("n_populations",16)):
            changed=deepcopy(p)
            changed[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                V._verify_primary(changed,correct)

    def test_complete_synthetic_json_custody_and_decision_no_native_lives(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/"mock-science-originals"
            root.mkdir()
            rows=matrix(True)
            metric=V.reduce_omnibus(rows)
            primary=published_primary(metric)
            holdout=[{"population":p,"family":f,"repeat":r}
                     for p in range(32) for f in V.FAMILIES for r in (0,1)]
            method={
                "alpha_omnibus": .025,
                "n_population_units":32,
                "df1":2,"df2":30,
                "primary":"two_dimensional_population_level_Hotelling_T_squared",
                "G2_worlds_precommitted_and_blind_to_parent_fitness":True,
            }
            plan={
                "schema":V.SCHEMA_PLAN,"scientific_admission":True,
                "source_git_head":V.SOURCE_HEAD,
                "planned_lives":23040,"planned_worlds":576,
                "planned_g2_holdout_worlds":192,
                "preexposure_scientific_verdict":"NOT_ISSUED",
                "g2_holdout_reserved_worlds":holdout,
                "g2_holdout_worlds_sha256":V.hash_bytes(V.canonical(holdout)),
                "frozen_method":method,
            }
            plan["allocation_sha256"]=V.hash_bytes(V.canonical(plan))
            records=[]
            for p,row in enumerate(rows):
                records.append({
                    "population":p,
                    "G2_selected_minus_random_steps":sum(row.values())/3,
                    "G2_families_descriptive": {
                        f: {"selected_minus_random_mean_steps": row[f]}
                        for f in V.FAMILIES
                    },
                })
            final={
                "schema":V.SCHEMA_FINAL,
                "plan_sha256":plan["allocation_sha256"],
                "source_git_head":V.SOURCE_HEAD,
                "frozen_method":method,
                "original_native_lives":23040,
                "g2_holdout_worlds_sha256":plan["g2_holdout_worlds_sha256"],
                "analysis":{
                    "status":metric["status"],
                    "primary":primary,
                    "all_32_population_observed_statistics":records,
                },
            }
            final_bytes=json.dumps(final,sort_keys=True).encode()
            (root/"SCIENCE_FINAL.json").write_bytes(final_bytes)
            (root/"CLAIM.json").write_text(json.dumps({
                "allocation_sha256":plan["allocation_sha256"],
                "source_sha":V.SOURCE_HEAD,"science":True,
                "status":"CLAIMED_NO_RETRY_EVEN_IF_PARTIAL",
            }))
            report={
                "schema":V.SCHEMA_RESULT,
                "status":metric["status"],
                "science_plan_sha256":plan["allocation_sha256"],
                "source_git_head":V.SOURCE_HEAD,
                "science_original_sha256":V.hash_bytes(final_bytes),
                "population_units":32,"original_native_lives":23040,
                "primary":primary,
                "all_population_statistics":records,
            }
            plan_path=Path(tmp)/"plan.json"
            report_path=Path(tmp)/"result.json"
            plan_path.write_text(json.dumps(plan))
            report_path.write_text(json.dumps(report))
            result=V.verify_reduced_science(str(plan_path),str(root),str(report_path))
            self.assertEqual(result["status"],"READ_ONLY_REDUCED_ROWS_REPRODUCED")
            self.assertEqual(result["scientific_status"],V.PASS)
            self.assertEqual(result["original_lives_rehashed"],0)
            self.assertEqual(result["new_worlds"],0)
            self.assertEqual(result["new_lives"],0)
            report["primary"]["p_value_two_sided_omnibus"]=.5
            report_path.write_text(json.dumps(report))
            with self.assertRaises(ValueError):
                V.verify_reduced_science(str(plan_path),str(root),str(report_path))
            self.assertFalse((root/"PANEL_0").exists())


if __name__ == "__main__":
    unittest.main()
