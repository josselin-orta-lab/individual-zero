"""Prospective Stage-9 registration must not score unsealed diagnostics."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.stage9_scientific_preregistration import (
    REGISTRATION_VERSION, SPEC_PATH, load_registration,
    normative_specification_digest, preflight, validate_registration,
)


def example_draft() -> dict[str, object]:
    # Deliberately unregistered. These values are TEST FIXTURES, not
    # author-selected scientific thresholds or an approved protocol.
    return {
        "protocol_version": REGISTRATION_VERSION,
        "registration_id": "unregistered-test-fixture",
        "author": "test-only",
        "normative_specification": SPEC_PATH,
        "normative_specification_sha256": normative_specification_digest(),
        "frozen_implementation_commit": "a" * 40,
        "world_generator_version": "future-holdout-v1",
        "calibration_world_ids": ["calibration:1"],
        "holdout_world_ids": ["holdout:positive", "holdout:null"],
        "positive_world_ids": ["holdout:positive"],
        "negative_world_ids": ["holdout:null"],
        "calibration_seeds": [41, 42],
        "holdout_seeds": [1001, 1002],
        "steps_per_run": 80,
        "minimum_naturally_acquired_candidates": 10,
        "maximum_superstitious_rule_rate": 0.05,
        "minimum_known_cause_accuracy": 0.9,
        "confidence_method": "test-only-confidence-rule",
        "candidate_definition": "independent naturally acquired hypotheses",
        "ground_truth_definition": "bench-only physical effect",
        "independent_episode_definition": "distinct closed Memory episodes",
        "exclusion_rule": "test-only fixed exclusions",
        "stop_rule": "test-only fixed run count",
        "replay_rule": "identical causal state and journal",
    }


class Stage9PreregistrationTests(unittest.TestCase):
    def test_absence_means_unregistered_not_golden(self):
        result = preflight()
        self.assertEqual(result["registration_status"], "unregistered")
        self.assertFalse(result["golden_stage9_frozen"])
        self.assertIsNone(result["scientific_verdict"])
        self.assertIsNone(result["registration_digest"])

    def test_complete_draft_cannot_self_certify_scientific_acceptance(self):
        draft = example_draft()
        digest = validate_registration(draft)
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, validate_registration(deepcopy(draft)))
        result = preflight(draft)
        self.assertEqual(result["registration_digest"], digest)
        self.assertEqual(
            result["registration_status"],
            "draft_requires_independent_git_seal",
        )
        self.assertIsNone(result["scientific_verdict"])
        self.assertFalse(result["golden_stage9_frozen"])

    def test_heldout_seed_or_world_overlap_is_rejected(self):
        for key, bad in (
            ("holdout_seeds", [41, 1002]),
            ("holdout_seeds", [1001, 1001]),
            ("holdout_seeds", [True, 1001]),
            ("holdout_world_ids", ["calibration:1", "holdout:null"]),
            ("holdout_world_ids", ["holdout:positive"]),
            ("positive_world_ids", ["holdout:positive", "holdout:null"]),
            ("negative_world_ids", ["holdout:positive"]),
        ):
            with self.subTest(field=key):
                draft = example_draft()
                draft[key] = bad
                with self.assertRaises(ValueError):
                    validate_registration(draft)

    def test_invalid_thresholds_and_counts_cannot_pass(self):
        for key, bad in (
            ("steps_per_run", True),
            ("steps_per_run", 0),
            ("minimum_naturally_acquired_candidates", 0),
            ("minimum_naturally_acquired_candidates", False),
            ("maximum_superstitious_rule_rate", None),
            ("maximum_superstitious_rule_rate", float("nan")),
            ("maximum_superstitious_rule_rate", True),
            ("maximum_superstitious_rule_rate", 1.1),
            ("minimum_known_cause_accuracy", -0.1),
            ("minimum_known_cause_accuracy", float("inf")),
        ):
            with self.subTest(field=key):
                draft = example_draft()
                draft[key] = bad
                with self.assertRaises(ValueError):
                    validate_registration(draft)

    def test_fake_spec_or_implementation_or_missing_rule_is_rejected(self):
        for key, bad in (
            ("normative_specification", "reference/fr/mvp-specification-v1.2.1.md"),
            ("normative_specification_sha256", "0" * 64),
            ("frozen_implementation_commit", "b" * 39),
            ("protocol_version", "old-v1"),
            ("author", ""),
            ("replay_rule", ""),
            ("extra", "unlisted"),
        ):
            with self.subTest(field=key):
                draft = example_draft()
                draft[key] = bad
                with self.assertRaises(ValueError):
                    validate_registration(draft)

    def test_json_decoder_rejects_duplicate_fields(self):
        draft = example_draft()
        with TemporaryDirectory() as folder:
            path = Path(folder) / "draft.json"
            path.write_text(
                json.dumps(draft)[:-1]
                + ',"maximum_superstitious_rule_rate":0.99}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_registration(path)
            path.write_text(json.dumps(draft), encoding="utf-8")
            self.assertEqual(load_registration(path), draft)


if __name__ == "__main__":
    unittest.main()
