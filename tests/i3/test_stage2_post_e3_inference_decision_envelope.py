"""Finite-data statistical nonidentifiability: no World or science births."""
from __future__ import annotations

from copy import deepcopy
import inspect
import json
from math import sqrt
from pathlib import Path
import unittest
from unittest.mock import patch

from i3.lab import stage2_post_e3_inference_decision_envelope as E
from i3.modules.world import World


class Stage2PostE3InferenceEnvelope(unittest.TestCase):
    def test_four_old_studies_have_complete_different_pair_denominators(self):
        self.assertEqual(len(E.HISTORICAL), 4)
        out = E.audit()
        self.assertEqual(out["old_studies_distinct_not_pooled"], 4)
        observed = {
            row["id"]: (row["pairs"], row["treatment_only"],
                        row["control_only"], row["both"], row["neither"])
            for row in out["history"]
        }
        self.assertEqual(observed, {
            "b1-gate-fixed-96": (96, 13, 5, 25, 53),
            "three-arm-gate-paid-random-64": (64, 4, 4, 23, 33),
            "content-priority-random-48": (48, 1, 7, 16, 24),
            "next-decision-priority-random-24": (24, 2, 3, 10, 9),
        })
        self.assertEqual(
            [x["finite_paired_risk_difference"] for x in out["history"]],
            [8 / 96, 0 / 64, -6 / 48, -1 / 24],
        )
        self.assertTrue(all(not row["extra_causal_information_control"]
                            for row in out["history"]))
        self.assertEqual(len({x["source_commit"] for x in out["history"]}), 4)
        self.assertEqual([x["treatment_survivors"] for x in out["history"]],
                         [38, 27, 17, 12])
        self.assertEqual([x["control_survivors"] for x in out["history"]],
                         [30, 27, 23, 13])

    def test_b1_conditional_numeric_ni_must_not_become_scientific_go(self):
        r = E.audit()
        x = r["history"][0]
        self.assertAlmostEqual(
            x["one_sided_95pct_lower_if_iid"],
            E.B1_PUBLISHED_CONDITIONAL_LOWER, places=10)
        self.assertGreater(
            x["one_sided_95pct_lower_if_iid"], -E.UNAPPROVED_NI_MARGIN)
        self.assertTrue(r["b1_hypothetical_5pp_NI_numerical_threshold_pass"])
        for name in (
            "b1_5pp_margin_scientifically_accepted",
            "b1_independent_iid_ecology_attested",
            "b1_independent_methods_review_pass",
            "b1_NI_scientific_claim_authorized",
        ):
            self.assertIs(r[name], False, name)
        self.assertFalse(x["confidence_valid_for_original_ecology"])
        self.assertFalse(x["scientific_NI_claim_authorized"])
        self.assertEqual(
            x["statistics_condition"], "HYPOTHETICAL_IID_PAIRED_SAMPLING_ONLY")

    def test_e3_software_fixed_two_cases_do_not_bound_general_utility(self):
        r = E.audit()
        e3, e1 = r["e3"], r["e1"]
        self.assertEqual((e3["unique_fixed_software_cases"],
                          e3["observed_event_count"]), (2, 0))
        self.assertEqual(
            e3["hypothetical_one_sided_95pct_upper_if_iid"],
            1 - sqrt(.05))
        self.assertFalse(e3["iid_source_sampling_verified"])
        self.assertFalse(e3["ecological_confidence_bound_claim"])
        self.assertEqual(e3["no_support_control"], 1)
        self.assertFalse(e3["actual_born_world_outcome"])
        self.assertEqual(r["e3_native_score_change_in_informed_fixed_shapes"], 1)
        self.assertEqual(r["e3_native_admitted_motor_changes"], 0)
        self.assertEqual(
            (e1["unique_fixed_software_cases"],
             e1["total_correlated_depth_comparisons"],
             e1["two_depth_comparisons_per_unique_case"]), (12, 24, 2))
        self.assertAlmostEqual(
            e1["hypothetical_one_sided_95pct_upper_if_iid"],
            1 - .05**(1 / 12), places=14)
        self.assertEqual(e1["changed_score_vectors"], 3)
        self.assertEqual(e1["changed_motors"], 0)
        self.assertFalse(e1["ecological_confidence_bound_claim"])
        self.assertEqual(r["next_decision_24_detached_alternate_motor"], 1)
        self.assertEqual(
            r["next_decision_24_different_alternate_motors_executed_in_World"],
            0)

    def test_new_scientific_causal_chain_is_not_synthesized_by_aggregates(self):
        r=E.audit()
        self.assertEqual(len(r["required_new_causal_evidence"]), 8)
        self.assertTrue(all(x is False for x in
                            r["required_new_causal_evidence"].values()))
        self.assertFalse(r["full_scientific_stage2_closed"])
        self.assertFalse(r["general_thinking_useful_demonstrated"])
        self.assertFalse(r["general_thinking_useless_demonstrated"])
        self.assertTrue(r["stop_this_exact_E3_candidate"])
        self.assertFalse(r["stage2_2_go"])
        self.assertFalse(r["stage2_3_go"])
        self.assertFalse(r["engine_registration"])
        self.assertEqual(r["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(r["bounded_candidate_verdict"],
                         "E3_FROZEN_CANDIDATE_NEGATIVE")
        self.assertEqual(r["methods_disposition"],
                         "NO_VERDICT_ON_GENERAL_ADAPTIVE_THINKING")
        self.assertEqual(r["total_historical_lives_reexecuted"], 0)
        self.assertEqual(r["new_Worlds"], 0)
        self.assertEqual(r["new_scientific_lives"], 0)

    def test_forged_or_partial_paired_tables_fail_closed_not_reinterpreted(self):
        bad = []
        original = E.HISTORICAL[0]
        for key, value in [
            ("pairs", 95), ("neither", 52), ("both", -1),
            ("control_survivors", 29), ("treatment_survivors", 39),
            ("treatment_only", 97), ("treatment_only", True),
            ("extra_causal_information_control", True),
            ("source_commit", "wrong"), ("source", "unsourced.csv"),
        ]:
            row=deepcopy(original)
            row[key]=value
            bad.append(row)
        missing=deepcopy(original)
        del missing["control_only"]
        bad.append(missing)
        for i, row in enumerate(bad):
            with self.subTest(case=i), self.assertRaises(ValueError):
                E._conditional_old_row(row)

    def test_hypothetical_zero_event_upper_accepts_only_zero_events(self):
        for bad in (
            dict(success_count=1,unique_cases=2,alpha=.05),
            dict(success_count=False,unique_cases=2,alpha=.05),
            dict(success_count=0,unique_cases=0,alpha=.05),
            dict(success_count=0,unique_cases=12.0,alpha=.05),
            dict(success_count=0,unique_cases=12,alpha=float("nan")),
            dict(success_count=0,unique_cases=12,alpha=0),
            dict(success_count=0,unique_cases=12,alpha=True),
        ):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                E._zero_iid_upper_sensitivity(**bad)
        self.assertTrue(
            E._zero_iid_upper_sensitivity(
                success_count=0, unique_cases=2, alpha=.05
            )["hypothetical_one_sided_95pct_upper_if_iid"] > .77
        )

    def test_no_world_import_and_manifest_authority_preserved(self):
        source=inspect.getsource(E)
        for bad in (
            "from i3.runtime", "from ..runtime", "run_life(",
            "World(", "world.step(", "newborn(", "create_world(",
        ):
            self.assertNotIn(bad, source)
        with patch.object(World, "__init__", side_effect=AssertionError(
                "Pure methods audit must never construct World"
        )):
            a=E.audit()
        self.assertEqual(a["new_Worlds"], 0)
        data=json.loads((Path(__file__).resolve().parents[2] /
                         "src/i3/ACTIVE_SURFACE.json").read_text())
        self.assertFalse(data["governance"]["fresh_lived_worlds_allowed"])
        self.assertFalse(data["governance"]["scientific_gate_authorized"])
        self.assertFalse(data["governance"]["i3_registered"])

    def test_reproducible_finite_digest_exact_source_across_interpreters(self):
        a,b=E.audit(),E.audit()
        self.assertEqual(a,b)
        self.assertEqual(len(a["aggregate_sha256"]),64)
        self.assertEqual(a["aggregate_sha256"],b["aggregate_sha256"])
        print("I3_STAGE2_POST_E3_METHODS_ENVELOPE=" + json.dumps({
            "aggregate_sha256":a["aggregate_sha256"],
            "historical_designs":a["old_studies_distinct_not_pooled"],
            "observed_finite_differences": [
                x["finite_paired_risk_difference"] for x in a["history"]],
            "b1_conditional_lower":a["history"][0][
                "one_sided_95pct_lower_if_iid"],
            "b1_NI_go":a["b1_NI_scientific_claim_authorized"],
            "hypothetical_e3_zero_of_two_upper":a["e3"][
                "hypothetical_one_sided_95pct_upper_if_iid"],
            "hypothetical_e1_zero_of_twelve_upper":a["e1"][
                "hypothetical_one_sided_95pct_upper_if_iid"],
            "bounded_candidate_verdict":a["bounded_candidate_verdict"],
            "general_science":a["scientific_verdict"],
            "new_lives":a["new_scientific_lives"],
        },sort_keys=True,separators=(",",":")))


if __name__ == "__main__":
    unittest.main()
