"""Acceptance-report coverage: measured evidence must not become a false gate."""
import json
import unittest

from lab.stage9_acceptance_report import generate_stage9_acceptance_report
from lab.determinism import canonical_causal_bytes, sha256_hex


class Stage9AcceptanceReportTests(unittest.TestCase):
    def test_diagnostics_are_reproducible_but_never_scientific_acceptance(self):
        a = generate_stage9_acceptance_report()
        b = generate_stage9_acceptance_report()
        self.assertEqual(a, b)
        self.assertEqual(a.to_json(), b.to_json())
        data = json.loads(a.to_json())
        self.assertEqual(data["acceptance_status"], "open")
        self.assertFalse(data["golden_stage9_frozen"])
        self.assertEqual(len(data["checks"]), 7)
        checks = {row["criterion"]: row for row in data["checks"]}
        self.assertEqual(checks["known_cause_attribution"]["evidence"]["positive_ground_truth_cases"], 6)
        self.assertEqual(checks["known_cause_attribution"]["evidence"]["correct_links"], 4)
        geometric = checks["known_cause_attribution"]["evidence"]
        self.assertEqual(geometric["geometric_world_count"], 3)
        self.assertEqual(geometric["geometric_ground_truthed_cases"], 18)
        self.assertEqual(geometric["geometric_false_self_links"], 0)
        self.assertEqual(geometric["geometric_matrix_seeds"], [42, 43, 44])
        self.assertEqual(len(geometric["geometric_matrix_sha256"]), 64)
        night = checks["nighttime_attribution"]["evidence"]["scenarios"]
        self.assertEqual([v["scenario"] for v in night], [
            "creature-night-harm", "two-visible-creatures-night", "hidden-danger-harm",
        ])
        self.assertTrue(night[0]["correct_link"])
        self.assertTrue(night[1]["uncertain"])
        self.assertTrue(night[2]["uncertain"])
        superstition = checks["superstitious_rules_under_random_reward"]
        self.assertEqual(superstition["classification"], "not_evaluable")
        self.assertIsNone(superstition["evidence"]["naturally_learned_false_rule_rate"])
        self.assertIsNone(superstition["evidence"]["preregistered_maximum_false_rule_rate"])
        self.assertEqual(superstition["evidence"]["spontaneous_matrix_seeds"], [42, 43, 44])
        self.assertEqual(superstition["evidence"]["spontaneous_matrix_runs"], 6)
        self.assertEqual(len(superstition["evidence"]["spontaneous_matrix_sha256"]), 64)
        self.assertGreaterEqual(
            superstition["evidence"]["independent_lived_hydration_episodes"], 1,
        )
        self.assertEqual(superstition["evidence"]["spontaneous_candidate_count"], 0)
        self.assertEqual(
            superstition["evidence"]["spontaneous_evaluation_status"], "not_evaluable",
        )
        self.assertIsNone(superstition["evidence"]["spontaneous_diagnostic_rate"])
        self.assertEqual(
            superstition["evidence"]["spontaneous_correlation_readiness"],
            "no_matched_positive_exposures",
        )
        self.assertEqual(
            superstition["evidence"]["external_inputs_verified_seeded"], 13,
        )
        self.assertTrue(checks["causal_replay"]["evidence"]["identical"])
        self.assertEqual(
            checks["causal_replay"]["evidence"]["reference_sha256"],
            checks["causal_replay"]["evidence"]["replayed_sha256"],
        )
        self.assertTrue(all(check["outstanding"] for check in data["checks"]))
        digest = data.pop("evidence_sha256")
        self.assertEqual(len(digest), 64)
        self.assertEqual(
            digest, sha256_hex(canonical_causal_bytes(data)),
        )

    def test_spontaneous_multiworld_diagnostic_is_seeded_without_false_acceptance(self):
        one = generate_stage9_acceptance_report(
            random_reward_seed=71, random_reward_steps=10,
        ).as_dict()
        two = generate_stage9_acceptance_report(
            random_reward_seed=71, random_reward_steps=10,
        ).as_dict()
        self.assertEqual(one, two)
        evidence = next(
            check["evidence"] for check in one["checks"]
            if check["criterion"] == "superstitious_rules_under_random_reward"
        )
        self.assertEqual(evidence["spontaneous_matrix_seeds"], (71, 72, 73))
        self.assertEqual(evidence["spontaneous_matrix_runs"], 6)
        self.assertIsNone(evidence["naturally_learned_false_rule_rate"])
        self.assertIsNone(evidence["spontaneous_diagnostic_rate"])
        self.assertEqual(one["acceptance_status"], "open")
        self.assertFalse(one["golden_stage9_frozen"])

    def test_invalid_seed_and_length_cannot_be_scored(self):
        for seed, steps in ((True, 14), (-1, 14), (1, True), (1, 5)):
            with self.subTest(seed=seed, steps=steps):
                with self.assertRaises(ValueError):
                    generate_stage9_acceptance_report(
                        random_reward_seed=seed,
                        random_reward_steps=steps,
                    )


if __name__ == "__main__":
    unittest.main()
