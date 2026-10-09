"""Stage-9 spontaneous causal-claim diagnostics, not scientific acceptance."""
from dataclasses import replace
import json
import unittest

from lab.stage9_spontaneous_superstition_matrix import (
    run_spontaneous_superstition_matrix,
)
from lab.stage9_random_reward_benchmark import run_random_reward_negative_control


class SpontaneousMatrixTests(unittest.TestCase):
    def test_no_bench_hypothesis_multi_seed_world_matrix(self):
        a = run_spontaneous_superstition_matrix()
        b = run_spontaneous_superstition_matrix()
        self.assertEqual(a, b)
        self.assertEqual(len(a.runs), 6)
        self.assertEqual(a.seeds, (41, 42, 43))
        self.assertEqual(len(a.world_variants), 2)
        self.assertGreaterEqual(a.physically_verified_exposures, 6)
        self.assertTrue(all(not row.bench_seeded_false_hypothesis for row in a.runs))
        self.assertTrue(all(row.scientific_gate is None for row in a.runs))
        self.assertEqual(
            a.total_lived_hydration_observations,
            a.lived_drink_observations + a.lived_wait_control_observations,
        )
        self.assertGreaterEqual(a.lived_drink_observations, 1)
        self.assertTrue(all(
            run.lived_positive_drink_observations == 0 for run in a.runs
        ))
        self.assertEqual(a.spontaneously_observed_candidates, 0)
        self.assertEqual(a.lived_positive_drink_observations, 0)
        self.assertEqual(a.runs_with_independent_positive_drinks, 0)
        self.assertEqual(a.runs_with_matched_controls, 0)
        self.assertEqual(
            a.correlation_readiness, "no_matched_positive_exposures",
        )
        self.assertIsNone(a.natural_false_rule_rate)
        self.assertEqual(a.evaluation_status, "not_evaluable")
        self.assertEqual(len(a.digest), 64)
        self.assertTrue(a.verify_digest())

    def test_matrix_digest_commits_to_results_and_physical_provenance(self):
        original = run_spontaneous_superstition_matrix(
            seeds=(41,), steps=10,
        )
        self.assertTrue(original.verify_digest())
        json_document = json.loads(original.to_json())
        digest = json_document.pop("digest")
        from lab.determinism import canonical_causal_bytes, sha256_hex
        self.assertEqual(
            sha256_hex(canonical_causal_bytes(json_document)), digest,
        )
        variants = (
            replace(original, established_false_rules=1),
            replace(original, evaluation_status="diagnostic_only"),
            replace(original, physically_verified_exposures=99),
            replace(original, runs=(
                replace(original.runs[0], drinking_commands=99),
                *original.runs[1:],
            )),
            replace(original, digest="0" * 64),
        )
        self.assertTrue(all(not item.verify_digest() for item in variants))

    def test_serialized_matrix_preserves_exact_provenance(self):
        row = run_spontaneous_superstition_matrix(seeds=(41,), steps=10)
        serialized = json.loads(row.to_json())
        self.assertEqual(serialized["digest"], row.digest)
        self.assertTrue(row.verify_digest())
        self.assertEqual(len(serialized["runs"]), 2)
        self.assertEqual(serialized["spontaneously_observed_candidates"], 0)
        self.assertIsNone(serialized["natural_false_rule_rate"])
        self.assertEqual(serialized["evaluation_status"], "not_evaluable")
        self.assertFalse(any(
            entry["bench_seeded_false_hypothesis"]
            for entry in serialized["runs"]
        ))

    def test_invalid_design_rejected(self):
        for seeds, worlds in (
            ((), ("null_water_reference",)),
            ((41, 41), ("null_water_reference",)),
            ((True,), ("null_water_reference",)),
            ((41,), ("invented_world",)),
            ((41,), ()),
        ):
            with self.subTest(seeds=seeds, worlds=worlds):
                with self.assertRaises(ValueError):
                    run_spontaneous_superstition_matrix(
                        seeds=seeds, world_variants=worlds,
                    )

    def test_physical_world_variant_preserves_non_scientific_diagnostic(self):
        row = run_random_reward_negative_control(
            campaign_seed=42, steps=14,
            world_variant="null_water_food_decay",
            bench_seed_false_hypothesis=False,
        )
        self.assertEqual(row.world_variant, "null_water_food_decay")
        self.assertFalse(row.spontaneous_candidate_refs)
        self.assertFalse(row.spontaneous_established_false_refs)
        self.assertIsNone(row.scientific_gate)
        self.assertGreaterEqual(len(row.verified_null_drink_transitions), 1)


if __name__ == "__main__":
    unittest.main()
