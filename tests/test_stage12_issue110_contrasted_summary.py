"""Independent GA-110 science reporter schema regression.

No autonomous transitions are fabricated or counted as experimental evidence.
"""
import unittest

from run_stage12_issue110_contrasted_science import summarize_lives


def example_life():
    return {
        "applied_steps": 5,
        "audit_error": None,
        "audits": {
            "goal": {
                "schema": "stage12-independent-goal-progress-audit-v1",
                "preregistered_one_step_criteria": 3,
                "verified_one_step_resource_gains": 1,
                "verified_one_step_no_gains": 1,
                "unavailable_next_step_observations": 1,
                "unresolved_at_terminal": 0,
            },
            "first_person": {
                "schema": "stage12-first-person-independent-technical-audit-v1",
                "precommits": 2,
                "judgements_self": 1, "judgements_world": 0,
                "judgements_unknown": 1, "unavailable": 0,
                "pending_terminal": 0, "charged_uc": 2, "refused_uc": 0,
            },
            "pairs": {
                "schema": "stage12-independent-outcome-agency-pair-audit-v1",
                "admitted_pairs": 1, "applied_pairs": 1,
                "applied_successes": 1, "applied_failures": 0,
                "applied_self": 1, "applied_world": 0,
                "missed_pairs": 0, "join_uc": 1,
                "rejected_join_uc": 0,
                "diagnostic_labels": [
                    {"world_step": 2, "attribution_bias": None},
                    {"world_step": 3, "attribution_bias": None},
                ],
            },
        },
    }


class ContrastedSummarySchemaTests(unittest.TestCase):
    def test_exact_public_schema_and_inconclusive_classification(self):
        row = example_life()
        report = summarize_lives([row], source_sha="test:fixture")
        self.assertEqual(report["verified_successes"], 1)
        self.assertEqual(report["verified_failures"], 1)
        self.assertEqual(report["agency_self"], 1)
        self.assertEqual(report["agency_unknown"], 1)
        self.assertEqual(report["agency_precommits"], 2)
        self.assertEqual(report["admitted_pairs"], 1)
        self.assertEqual(report["diagnostic_labels"], {"unavailable": 2})
        self.assertFalse(report["operator_accepted"])
        self.assertEqual(report["scientific_validation"], "not_performed")

    def test_missing_counter_refused_instead_of_silent_zero(self):
        row = example_life()
        del row["audits"]["goal"]["verified_one_step_resource_gains"]
        with self.assertRaisesRegex(ValueError, "missing or invalid"):
            summarize_lives([row], source_sha="test:fixture")

    def test_error_life_kept_in_denominator_but_not_audited(self):
        report = summarize_lives([
            example_life(), {"applied_steps": 3, "error": "safety_block"}
        ], source_sha="test:fixture")
        self.assertEqual(report["total_actual_applied_steps"], 8)
        self.assertEqual(report["audited_actual_applied_steps"], 5)
        self.assertEqual(report["failed_or_unaudited_lives"], 1)

    def test_no_pairs_is_inconclusive(self):
        row = example_life()
        pair = row["audits"]["pairs"]
        for key in ("admitted_pairs", "applied_pairs", "applied_successes",
                    "applied_self", "join_uc"):
            pair[key] = 0
        report = summarize_lives([row], source_sha="test:fixture")
        self.assertEqual(report["scientific_status"],
                         "inconclusive_no_admissible_pairs")


if __name__ == "__main__":
    unittest.main()
