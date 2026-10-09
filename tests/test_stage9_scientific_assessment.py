"""Stage-9 holdout scorer regression fixtures, NOT campaign results."""
from __future__ import annotations

from copy import deepcopy
import unittest

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage9_scientific_assessment import (
    EVIDENCE_VERSION, assess_heldout_campaign,
)
from lab.stage9_scientific_preregistration import validate_registration
from tests.test_stage9_scientific_preregistration import example_draft


def _case(world: str, seed: int) -> dict[str, str]:
    return {
        "id": "case:1", "episode_ref": f"case-episode:{world}:{seed}",
        "observation_ref": f"case-transition:{world}:{seed}",
        "ground_truth": "self", "attribution": "self_compatible",
    }


def make_report(registration: dict[str, object], *, candidates: int = 1):
    rows = []
    for world in registration["holdout_world_ids"]:
        for seed in registration["holdout_seeds"]:
            run = {
                "world_id": world,
                "world_sha256": registration["holdout_world_sha256"][world],
                "seed": seed,
                "journal_sha256": "1" * 64,
                "replay_journal_sha256": "1" * 64,
                "causal_state_sha256": "2" * 64,
                "replay_causal_state_sha256": "2" * 64,
                "known_cause_cases": [_case(world, seed)],
                "naturally_acquired_false_candidates": [],
            }
            if world in registration["negative_world_ids"]:
                run["naturally_acquired_false_candidates"] = [
                    {
                        "id": f"natural:{i}",
                        "episode_ref": f"natural-episode:{world}:{seed}:{i}",
                        "observation_ref": f"natural-transition:{world}:{seed}:{i}",
                        "causal_status": "hypothese_causale",
                    }
                    for i in range(candidates)
                ]
            rows.append(run)
    report = {
        "protocol_version": EVIDENCE_VERSION,
        "registration_digest": validate_registration(registration),
        "frozen_implementation_commit": registration["frozen_implementation_commit"],
        "runs": rows,
    }
    return sealed(report)


def sealed(report: dict[str, object]) -> dict[str, object]:
    result = deepcopy(report)
    result.pop("evidence_sha256", None)
    result["evidence_sha256"] = sha256_hex(canonical_causal_bytes(result))
    return result


class Stage9ScientificAssessmentTests(unittest.TestCase):
    def test_unregistered_and_awaiting_heldout_are_never_golden(self):
        self.assertEqual(
            assess_heldout_campaign(None, None)["assessment"], "unregistered",
        )
        with self.assertRaises(ValueError):
            assess_heldout_campaign(None, {"forged": True})
        draft = example_draft()
        pending = assess_heldout_campaign(draft, None)
        self.assertEqual(pending["assessment"], "awaiting_holdout_campaign")
        self.assertIsNone(pending["scientific_verdict"])
        self.assertFalse(pending["golden_stage9_frozen"])

    def test_zero_candidates_is_not_a_zero_percent_success(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        result = assess_heldout_campaign(draft, make_report(draft, candidates=0))
        self.assertEqual(result["assessment"], "not_evaluable")
        self.assertIsNone(result["superstitious_rule_rate"])
        self.assertIsNone(result["superstition_wilson_95"])
        self.assertFalse(result["golden_stage9_frozen"])

    def test_positive_looking_metrics_still_require_independent_review(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        draft["minimum_known_cause_accuracy"] = 0.20
        draft["maximum_superstitious_rule_rate"] = 0.80
        draft["minimum_naturally_acquired_candidates"] = 2
        result = assess_heldout_campaign(draft, make_report(draft, candidates=20))
        self.assertEqual(result["assessment"], "metrics_eligible_for_independent_review")
        self.assertEqual(result["known_cause_cases"], 4)
        self.assertEqual(result["correct_links"], 4)
        self.assertEqual(result["natural_false_candidate_count"], 40)
        self.assertEqual(result["false_established_count"], 0)
        self.assertIsNone(result["scientific_verdict"])
        self.assertFalse(result["golden_stage9_frozen"])
        self.assertGreater(len(result["outstanding"]), 0)

    def test_confidence_bounds_and_abstentions_never_become_correct(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        report = make_report(draft, candidates=10)
        report["runs"][0]["known_cause_cases"][0]["attribution"] = "uncertain"
        report["runs"][1]["known_cause_cases"][0]["ground_truth"] = "world"
        report["runs"][2]["naturally_acquired_false_candidates"][0][
            "causal_status"
        ] = "etablie"
        scored = assess_heldout_campaign(draft, sealed(report))
        self.assertEqual(scored["uncertain_links"], 1)
        self.assertEqual(scored["false_self_links"], 1)
        self.assertEqual(scored["correct_links"], 2)
        self.assertEqual(scored["false_established_count"], 1)
        self.assertEqual(scored["assessment"], "below_preregistered_confidence_threshold")

    def test_no_effect_controls_do_not_inflate_known_cause_denominator(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        draft["minimum_known_cause_accuracy"] = 0.1
        draft["maximum_superstitious_rule_rate"] = 1.0
        draft["minimum_naturally_acquired_candidates"] = 2
        report = make_report(draft, candidates=10)
        report["runs"][0]["known_cause_cases"][0].update(
            ground_truth="none", attribution="uncertain",
        )
        result = assess_heldout_campaign(draft, sealed(report))
        self.assertEqual(result["known_cause_cases"], 3)
        self.assertEqual(result["correct_links"], 3)
        self.assertEqual(result["known_cause_accuracy"], 1.0)
        self.assertEqual(result["uncertain_links"], 0)
        self.assertEqual(result["no_effect_control_cases"], 1)
        self.assertEqual(result["no_effect_control_abstentions"], 1)
        self.assertEqual(result["no_effect_control_false_attributions"], 0)

    def test_false_causation_in_no_effect_control_blocks_metric_eligibility(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        draft["minimum_known_cause_accuracy"] = 0.1
        draft["maximum_superstitious_rule_rate"] = 1.0
        draft["minimum_naturally_acquired_candidates"] = 2
        for incorrect in ("self_compatible", "world_justified"):
            with self.subTest(incorrect=incorrect):
                report = make_report(draft, candidates=10)
                report["runs"][0]["known_cause_cases"][0].update(
                    ground_truth="none", attribution=incorrect,
                )
                result = assess_heldout_campaign(draft, sealed(report))
                self.assertEqual(result["assessment"], "invalid_no_effect_attribution")
                self.assertEqual(result["no_effect_control_cases"], 1)
                self.assertEqual(result["no_effect_control_false_attributions"], 1)
                self.assertEqual(
                    result["false_self_links"], int(incorrect == "self_compatible"),
                )
                self.assertIsNone(result["scientific_verdict"])
                self.assertFalse(result["golden_stage9_frozen"])

    def test_rejects_forged_evidence_and_repeated_world_runs(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        original = make_report(draft)
        damaged = deepcopy(original)
        damaged["runs"][0]["known_cause_cases"][0]["ground_truth"] = "world"
        with self.assertRaisesRegex(ValueError, "full-report digest"):
            assess_heldout_campaign(draft, damaged)
        for label, change in (
            ("replay", lambda d: d["runs"][0].update(replay_journal_sha256="3" * 64)),
            ("duplicate", lambda d: d["runs"][1].update(
                world_id=d["runs"][0]["world_id"], seed=d["runs"][0]["seed"],
            )),
            ("world", lambda d: d["runs"][0].update(world_sha256="3" * 64)),
            ("wrong_status", lambda d: d["runs"][2][
                "naturally_acquired_false_candidates"
            ][0].update(causal_status="etabli_pour_securite")),
            ("physical_duplicate", lambda d: d["runs"][2][
                "naturally_acquired_false_candidates"
            ][0].update(
                episode_ref=d["runs"][2]["known_cause_cases"][0]["episode_ref"],
                observation_ref=d["runs"][2]["known_cause_cases"][0]["observation_ref"],
            )),
        ):
            with self.subTest(label=label):
                damaged = deepcopy(original)
                change(damaged)
                with self.assertRaises(ValueError):
                    assess_heldout_campaign(draft, sealed(damaged))

    def test_unsupported_confidence_method_cannot_implicitly_pass(self):
        draft = example_draft()
        report = make_report(draft)
        with self.assertRaisesRegex(ValueError, "confidence rule"):
            assess_heldout_campaign(draft, report)


if __name__ == "__main__":
    unittest.main()
