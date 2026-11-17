"""Pure synthetic tests of POSTHOC independent Stage8-A archive reduction.

There are NO native World, motor, mutation, run_life or seed allocation calls.
Success of these tests is NEVER an independent archive result in itself.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i3.lab import stage8a_independent_original_audit as A


class Stage8AIndependentNoBirthTests(unittest.TestCase):

    def test_23_positive_9_negative_can_pass_mean_criterion(self):
        x=A._mean_primary([15.0]*23 + [-5.0]*9)
        self.assertEqual(x["status"], A.POSITIVE)
        self.assertEqual(x["positive"], 23)
        self.assertEqual(x["negative"], 9)
        self.assertGreater(x["lower"],0)
        self.assertGreater(x["mean"],0)

    def test_positive_mean_can_still_fail_Student_bound(self):
        x=A._mean_primary([100.0]*4 + [-10.0]*28)
        self.assertGreater(x["mean"],0)
        self.assertLessEqual(x["lower"],0)
        self.assertEqual(x["status"],A.NEGATIVE)

    def test_null_negative_and_missing_population_fail(self):
        for z in ([0.0]*32,[-5.0]*32,[3.0]*32):
            observed=A._mean_primary(z)
            self.assertFalse(observed["positive_lower_bound"])
            self.assertEqual(observed["status"],A.NEGATIVE)
        for z in ([1.0]*31,[1.0]*33,
                  [float("nan")]+[1.0]*31):
            with self.assertRaises(ValueError):
                A._mean_primary(z)

    def test_altered_or_missing_science_plan_sha_fails_before_birth(self):
        plan={"schema":"test","frozen":True}
        plan["allocation_sha256"]=A.A.digest(A.A.canonical(plan))
        self.assertEqual(A._digest_and_assert(plan),plan)
        corrupted=deepcopy(plan)
        corrupted["frozen"]=False
        with self.assertRaises(ValueError):
            A._digest_and_assert(corrupted)
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/"never-open"
            with self.assertRaises(FileNotFoundError):
                A.audit_full(str(root/"SCIENCE_PLAN.json"),
                             str(root), str(root/"SCIENCE_RESULT.json"))
            self.assertFalse(root.exists())

    def test_report_values_cannot_be_overwritten_by_a_later_decision(self):
        observed=A._mean_primary([15.0]*23+[-5.0]*9)
        report_primary={
            "status":observed["status"],
            "n_populations":32,
            "mean_difference_steps":observed["mean"],
            "sample_sd_between_populations":observed["sd"],
            "standard_error":observed["se"],
            "one_sided_97_5_percent_lower_bound_steps":observed["lower"],
            "t_critical_df31_one_sided_975":A.TCRIT,
            "positive":observed["positive"],
            "negative":observed["negative"],
            "zero":observed["zero"],
            "primary_success":True,
            "population_contrasts_steps":observed["contrasts"],
        }
        final={
            "schema":A.FINAL_SCHEMA,
            "source_git_head":A.SOURCE_HEAD,
            "result":{
                "status":observed["status"],
                "primary":report_primary,
                "all_population_statistics":[],
            },
        }
        report={
            "schema":A.RESULT_SCHEMA,"status":observed["status"],
            "source_git_head":A.SOURCE_HEAD,
            "population_units":32,
            "original_native_lives":23040,
            "primary":report_primary,
            "all_population_statistics":[],
        }
        self.assertTrue(A._assert_original_reducer_match(
            final,report,observed))
        changed=deepcopy(report)
        changed["primary"]["mean_difference_steps"]-=1
        with self.assertRaises(ValueError):
            A._assert_original_reducer_match(final,changed,observed)
        changed=deepcopy(report)
        changed["primary"]["positive"]=32
        with self.assertRaises(ValueError):
            A._assert_original_reducer_match(final,changed,observed)
        changed=deepcopy(report)
        changed["primary"]["population_contrasts_steps"][0]=-99.0
        with self.assertRaises(ValueError):
            A._assert_original_reducer_match(final,changed,observed)

    def test_source_pins_and_import_are_inert(self):
        self.assertEqual(A.RUN_ID,43950098410)
        self.assertEqual(A.SOURCE_HEAD,
                         "ac353a9c4206ee3ecfd90bb101e26d092103958b")
        self.assertEqual(A.SCIENCE_PLAN_SHA,
                         "dcd93550453541273c940f78fc459dd3f4deaa807911cb89992c4d1eb7d3b660")
        self.assertEqual(A.POP,32)
        self.assertEqual(A.LIVES_TOTAL,23040)
        self.assertEqual(A.TCRIT,2.0395134463964077)


if __name__=="__main__":
    unittest.main()
