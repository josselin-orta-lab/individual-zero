"""Stage13 prospective protocol preflight, NOT experiments or scientific proof."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import unittest

from lab.stage13_final_preregistration import (
    REGISTRATION_SCHEMA, SPEC_PATH, preregistration_preflight,
    normative_digest,
)


def draft():
    protocols = [{
        "module_id": f"module:stage:{i:02d}",
        "stage": f"stage{i:02d}",
        "hypothesis": "H1" if i % 2 else "H2",
        "independent_observation_source": "external_sensor_and_readonly_bench",
        "measurable_claim": "observable process outcome",
        "metric": "preregistered event consistency",
        "baseline": "independent frozen baseline",
        "negative_control": "world with absent target behavior",
        "minimum_independent_runs": 3,
        "success_direction": "at_least",
        "success_threshold": 0.75,
        "failure_reporting": "report all excluded, missing and failed runs",
    } for i in range(1, 13)]
    return {
        "registration_schema": REGISTRATION_SCHEMA,
        "registration_id": "stage13-example-unsigned-draft",
        "normative_specification": SPEC_PATH,
        "normative_specification_sha256": normative_digest(),
        "implementation_commit": "a" * 40,
        "parameter_values": {
            f"P-{i:02d}": {"version": f"example-P{i:02d}", "value": 1.0}
            for i in range(1, 59)
        },
        "parameter_registry_sha256": "b" * 64,
        "world_manifest_sha256": "c" * 64,
        "equipment_manifest_sha256": "d" * 64,
        "development_seeds": [11, 12],
        "calibration_seeds": [21, 22],
        "holdout_seeds": [31, 32],
        "calibration_world_ids": ["calib:1"],
        "holdout_world_ids": ["heldout:1", "heldout:2"],
        "module_protocols": protocols,
        "hypotheses": {
            f"H{i}": f"prospective falsifiable H{i} hypothesis"
            for i in range(1, 7)
        },
        "familywise_error_control": "Holm step-down specified prospectively",
        "early_stop_rule": "stop on corrupted journal or safety block",
        "exclusion_rule": "exclude only predefined technical failures",
        "reporting_rule": "publish all favorable and unfavorable outcomes",
    }


class FinalPreregistrationPreflightTests(unittest.TestCase):
    def test_complete_draft_has_digest_but_no_operator_or_scientific_go(self):
        protocol = draft()
        receipt = preregistration_preflight(protocol)
        self.assertEqual(len(receipt.digest), 64)
        self.assertEqual(receipt.module_protocol_count, 12)
        self.assertEqual(receipt.parameter_count, 58)
        self.assertEqual(receipt.stage_coverage, tuple(
            f"stage{i:02d}" for i in range(1, 13)
        ))
        self.assertIsNone(receipt.scientific_verdict)
        self.assertFalse(receipt.campaign_started)
        self.assertTrue(receipt.operator_approval_required)

    def test_registration_digest_deterministic_under_map_reordering(self):
        a = draft()
        b = deepcopy(a)
        b["parameter_values"] = dict(reversed(list(b["parameter_values"].items())))
        b["hypotheses"] = dict(reversed(list(b["hypotheses"].items())))
        self.assertEqual(
            preregistration_preflight(a).digest,
            preregistration_preflight(b).digest,
        )
        b["module_protocols"][0]["success_threshold"] = 0.55
        self.assertNotEqual(
            preregistration_preflight(a).digest,
            preregistration_preflight(b).digest,
        )

    def test_missing_or_unversioned_calibration_never_uses_defaults(self):
        d = draft()
        d["parameter_values"].pop("P-42")
        with self.assertRaisesRegex(ValueError, "58"):
            preregistration_preflight(d)
        d = draft()
        d["parameter_values"]["P-42"]["value"] = None
        with self.assertRaisesRegex(ValueError, "nonnull"):
            preregistration_preflight(d)
        d = draft()
        d["parameter_values"]["P-42"]["value"] = float("nan")
        with self.assertRaises((TypeError, ValueError)):
            preregistration_preflight(d)

    def test_no_leakage_between_development_calibration_and_holdout(self):
        for corruption in ("seed", "world", "hypothesis", "commit", "spec"):
            d = draft()
            if corruption == "seed":
                d["holdout_seeds"].append(d["development_seeds"][0])
            elif corruption == "world":
                d["holdout_world_ids"].append("calib:1")
            elif corruption == "hypothesis":
                d["hypotheses"].pop("H6")
            elif corruption == "commit":
                d["implementation_commit"] = "a" * 7
            else:
                d["normative_specification_sha256"] = "0" * 64
            with self.subTest(corruption=corruption):
                with self.assertRaises(ValueError):
                    preregistration_preflight(d)

    def test_each_module_requires_independent_negative_control_and_threshold(self):
        for corruption in (
            "missing_stage", "duplicate_module", "no_control",
            "unverifiable_source", "unknown_threshold",
        ):
            d = draft()
            rows = d["module_protocols"]
            if corruption == "missing_stage":
                rows.pop()
            elif corruption == "duplicate_module":
                rows[1]["module_id"] = rows[0]["module_id"]
            elif corruption == "no_control":
                rows[0]["negative_control"] = ""
            elif corruption == "unverifiable_source":
                rows[0]["independent_observation_source"] = "Oracle_as_I0_input"
            else:
                rows[0]["success_threshold"] = float("inf")
            with self.subTest(corruption=corruption):
                with self.assertRaises(ValueError):
                    preregistration_preflight(d)

    def test_draft_never_creates_a_life_or_an_oracle(self):
        d = draft()
        self.assertEqual(preregistration_preflight(d).campaign_started, False)
        # Only a digest is granted: existence, chronology, source integrity
        # and actual operator-scientific approvals require separate evidence.
        self.assertNotIn("operator_signature", d)
        self.assertNotIn("scientific_verdict", d)


if __name__ == "__main__":
    unittest.main()
