"""Prospective Stage-9 registration must not score unsealed diagnostics."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from lab.stage9_scientific_preregistration import (
    REGISTRATION_VERSION, SPEC_PATH, load_registration,
    normative_specification_digest, preflight, validate_registration,
)
from lab import stage9_scientific_preregistration as registration_module
from lab import stage9_secure_file_read as guarded


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
        "world_generator_sha256": "d" * 64,
        "equipment_sha256": "e" * 64,
        "parameter_registry_sha256": "f" * 64,
        "ontology_sha256": "0" * 64,
        "calibration_world_sha256": {"calibration:1": "a" * 64},
        "holdout_world_sha256": {
            "holdout:positive": "b" * 64,
            "holdout:null": "c" * 64,
        },
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
        "confidence_method": "wilson_95",
        "candidate_definition": "independent naturally acquired hypotheses",
        "ground_truth_definition": "bench-only physical effect",
        "independent_episode_definition": "distinct closed Memory episodes",
        "exclusion_rule": "test-only fixed exclusions",
        "stop_rule": "test-only fixed run count",
        "replay_rule": "identical causal state and journal",
    }


class Stage9PreregistrationTests(unittest.TestCase):

    def test_normative_digest_refuses_symlinked_file_and_parent(self):
        # The normative English source itself may not be silently redirected
        # by a link, even if the linked file contains byte-identical text.
        for part in ("leaf", "parent"):
            with self.subTest(part=part):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    target = root / SPEC_PATH
                    target.parent.mkdir(parents=True)
                    target.write_bytes(b"synthetic-normative-specification")
                    fake_module = root / "src" / "lab" / "module.py"
                    with patch.object(registration_module, "__file__", str(fake_module)):
                        self.assertEqual(len(normative_specification_digest()), 64)
                        if part == "leaf":
                            relocated = root / "relocated-normative.md"
                            target.rename(relocated)
                            target.symlink_to(relocated)
                        else:
                            relocated = root / "relocated-en"
                            target.parent.rename(relocated)
                            target.parent.symlink_to(
                                relocated, target_is_directory=True,
                            )
                        with self.assertRaisesRegex(ValueError, "symlink"):
                            normative_specification_digest()

    def test_normative_digest_detects_mutation_during_descriptor_read(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / SPEC_PATH
            target.parent.mkdir(parents=True)
            target.write_bytes(b"synthetic-normative-specification")
            fake_module = root / "src" / "lab" / "module.py"
            before = target.stat()
            original = target.read_bytes()
            real_fdopen = guarded.os.fdopen
            mutated = False

            def rewrite_after_open(fd, mode):
                nonlocal mutated
                stream = real_fdopen(fd, mode)
                if not mutated:
                    mutated = True
                    target.write_bytes(b"X" + original[1:])
                    os.utime(target, ns=(
                        before.st_atime_ns, before.st_mtime_ns + 2_000_000_000,
                    ))
                return stream

            with patch.object(registration_module, "__file__", str(fake_module)):
                with patch.object(
                    guarded.os, "fdopen", side_effect=rewrite_after_open,
                ):
                    with self.assertRaisesRegex(
                        ValueError, "changed during descriptor read",
                    ):
                        normative_specification_digest()
            self.assertTrue(mutated)

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

    def test_registration_preflight_never_authorizes_heldout_exposure(self):
        # Even a complete, syntactically valid prospective draft does not
        # witness custody or independent roles, and cannot be a campaign GO.
        for draft in (None, example_draft()):
            with self.subTest(manifest_supplied=draft is not None):
                result = preflight(draft)
                self.assertIs(result["launch_authorized_by_preflight"], False)
                self.assertIs(
                    result["independent_heldout_custody_attested_by_preflight"],
                    False,
                )
                self.assertIs(
                    result["independent_evaluator_approved_by_preflight"],
                    False,
                )
                self.assertIn(
                    "sealed custody of plaintext held-out seeds and world manifests",
                    result["outstanding"],
                )
                self.assertIn(
                    "named operator and independent evaluator with conflict review",
                    result["outstanding"],
                )
                self.assertIn(
                    "prospective human approval and explicit release-to-run decision",
                    result["outstanding"],
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

    def test_world_hashes_reject_relabeling_and_calibration_reuse(self):
        for label, edit in (
            ("same_holdout_physics", ("holdout:null", "b" * 64)),
            ("calibration_reused", ("holdout:positive", "a" * 64)),
            ("invalid_world_digest", ("holdout:null", "not-a-digest")),
            ("missing_world_digest", ("holdout:null", None)),
        ):
            with self.subTest(label=label):
                draft = example_draft()
                key, digest = edit
                if digest is None:
                    draft["holdout_world_sha256"].pop(key)
                else:
                    draft["holdout_world_sha256"][key] = digest
                with self.assertRaises(ValueError):
                    validate_registration(draft)

        draft = example_draft()
        draft["calibration_world_sha256"]["alias:extra"] = "1" * 64
        with self.assertRaises(ValueError):
            validate_registration(draft)
        draft = example_draft()
        draft["parameter_registry_sha256"] = "0" * 63
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
            ("confidence_method", "unsupported-test-method"),
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
            for malformed in ("NaN", "Infinity", "-Infinity"):
                with self.subTest(value=malformed):
                    raw = json.dumps(draft).replace(
                        '"maximum_superstitious_rule_rate": 0.05',
                        '"maximum_superstitious_rule_rate": ' + malformed,
                        1,
                    )
                    path.write_text(raw, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "non-finite registration"):
                        load_registration(path)
            path.write_text(json.dumps(draft), encoding="utf-8")
            self.assertEqual(load_registration(path), draft)


if __name__ == "__main__":
    unittest.main()
