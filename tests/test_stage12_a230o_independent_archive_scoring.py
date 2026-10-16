"""Negative controls for archive-only A2.30-O independent reviewer."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_stage12_issue110_b_a230o_independent_scoring import (
    read_source, review_sources,
)


class AdversarialArchiveVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original = read_source(Path(os.environ["A230O_SOURCE_A"]))
        other = read_source(Path(os.environ["A230O_SOURCE_B"]))
        if original != other:
            raise AssertionError("original Python versions disagree")
        cls.original = original
        cls.training = json.loads(original["a230n-training-manifest.json"])
        cls.heldout = json.loads(original["a230n-heldout-physical-results.json"])
        cls.summary = json.loads(original["a230n-summary.json"])

    def review(self, *, training=None, heldout=None, summary=None):
        return review_sources(
            deepcopy(self.training if training is None else training),
            deepcopy(self.heldout if heldout is None else heldout),
            deepcopy(self.summary if summary is None else summary),
        )

    def test_independent_reconstruction_of_all_records(self):
        report = self.review()
        self.assertTrue(report["independently_recomputed_all_62_records"])
        self.assertEqual(report["candidate_available"], 54)
        self.assertEqual(report["exact_available"], 18)
        self.assertEqual(report["candidate_interval_misses"], 20)
        self.assertEqual(report["candidate_terminal_set_misses"], 12)
        self.assertEqual(report["exact_external_false_safe_proxy"], 18)
        self.assertEqual(report["candidate_safety_certificates"], 0)
        self.assertEqual(report["new_lives"], 0)
        self.assertFalse(
            report["raw_physical_worldbody_execution_independently_proven"]
        )

    def test_tampered_accessible_input_digest_fails(self):
        altered = deepcopy(self.heldout)
        altered[0]["cell"]["input_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "test input"):
            self.review(heldout=altered)

    def test_contradictory_terminal_outcome_fails(self):
        altered = deepcopy(self.heldout)
        row = next(
            x for x in altered if x["stratum"] == "hidden_lethal_move"
        )
        row["actual"]["terminal"] = False
        with self.assertRaisesRegex(ValueError, "terminal"):
            self.review(heldout=altered)

    def test_unjustified_safety_certificate_fails(self):
        altered = deepcopy(self.heldout)
        altered[0]["candidate"]["certifies_safe"] = True
        with self.assertRaisesRegex(ValueError, "safety guarantee"):
            self.review(heldout=altered)

    def test_inverted_forecast_range_fails(self):
        altered = deepcopy(self.heldout)
        row = next(x for x in altered if x["candidate"]["available"])
        row["candidate"]["lower"]["body.food"] = 9000
        with self.assertRaisesRegex(ValueError, "forecast/interval"):
            self.review(heldout=altered)

    def test_untrained_primitive_cannot_claim_known_interval(self):
        altered = deepcopy(self.heldout)
        row = next(x for x in altered if x["stratum"] == "unseen_command")
        row["candidate"]["status"] = "uncertain_interval"
        with self.assertRaisesRegex(ValueError, "abstention"):
            self.review(heldout=altered)

    def test_holdout_inserted_into_training_is_rejected(self):
        altered = deepcopy(self.training)
        ex = altered["trained_target_examples"][0]
        altered["trained_target_examples"].append(ex)
        with self.assertRaisesRegex(ValueError, "training examples"):
            self.review(training=altered)

    def test_fake_physical_training_example_is_rejected(self):
        altered = deepcopy(self.training)
        altered["trained_target_examples"][0]["terminal"] = True
        with self.assertRaisesRegex(ValueError, "corpus SHA"):
            self.review(training=altered)

    def test_wrong_aggregate_count_fails(self):
        altered = deepcopy(self.summary)
        altered["candidate_available"] = 62
        with self.assertRaisesRegex(ValueError, "aggregate"):
            self.review(summary=altered)

    def test_independent_reviewer_does_not_import_predictor_or_simulator(self):
        auditor = (
            Path(__file__).resolve().parents[1]
            / "scripts/audit_stage12_issue110_b_a230o_independent_scoring.py"
        ).read_text()
        self.assertNotIn(
            "from audit_stage12_issue110_b_a230n_uncertain_predictor import",
            auditor
        )
        self.assertNotIn("from lab.world import", auditor)
        self.assertNotIn("import Simulator", auditor)
        self.assertNotIn("def predict(", auditor)


if __name__ == "__main__":
    unittest.main()
