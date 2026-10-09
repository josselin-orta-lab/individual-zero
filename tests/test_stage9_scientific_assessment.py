"""Stage-9 holdout scorer regression fixtures, NOT campaign results."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage9_scientific_assessment import (
    EVIDENCE_VERSION, assess_heldout_campaign, load_heldout_evidence,
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
                        "contingency_ref": f"causal:natural:{i}",
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

    def test_distinct_physical_cases_can_share_one_closed_memory_episode(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        report = make_report(draft, candidates=5)
        first = deepcopy(report["runs"][0]["known_cause_cases"][0])
        second = deepcopy(first)
        second["id"] = "case:2"
        second["observation_ref"] = "distinct-world-transition"
        report["runs"][0]["known_cause_cases"].append(second)
        scored = assess_heldout_campaign(draft, sealed(report))
        self.assertEqual(scored["known_cause_cases"], 5)
        self.assertEqual(scored["correct_links"], 5)
        self.assertIsNone(scored["scientific_verdict"])
        self.assertFalse(scored["golden_stage9_frozen"])

    def test_distinct_physical_candidates_can_share_an_episode(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        report = make_report(draft, candidates=5)
        null_run = report["runs"][2]
        candidates = null_run["naturally_acquired_false_candidates"]
        candidates[1]["episode_ref"] = candidates[0]["episode_ref"]
        candidates[2]["episode_ref"] = null_run["known_cause_cases"][0]["episode_ref"]
        scored = assess_heldout_campaign(draft, sealed(report))
        self.assertEqual(scored["natural_false_candidate_count"], 10)
        self.assertIsNone(scored["scientific_verdict"])

    def test_repeated_canonical_rule_cannot_inflate_false_rule_denominator(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        report = make_report(draft, candidates=5)
        natural = report["runs"][2]["naturally_acquired_false_candidates"]
        # Independent event, independent episode and candidate alias still
        # refer to the same canonical hypothesis and must count once.
        natural[1]["contingency_ref"] = natural[0]["contingency_ref"]
        with self.assertRaisesRegex(ValueError, "reused canonical false-rule"):
            assess_heldout_campaign(draft, sealed(report))

    def test_canonical_rules_are_run_scoped_for_independent_world_seeds(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        report = make_report(draft, candidates=5)
        # The same ontology-level contingency can be learned independently
        # by two different individuals in distinct world/seed runs.
        rows = [row for row in report["runs"] if row["naturally_acquired_false_candidates"]]
        self.assertEqual(
            rows[0]["naturally_acquired_false_candidates"][0]["contingency_ref"],
            rows[1]["naturally_acquired_false_candidates"][0]["contingency_ref"],
        )
        scored = assess_heldout_campaign(draft, sealed(report))
        self.assertEqual(scored["natural_false_candidate_count"], 10)
        self.assertFalse(scored["golden_stage9_frozen"])

    def test_obsolete_evidence_schema_cannot_be_treated_as_current(self):
        draft = example_draft()
        report = make_report(draft, candidates=5)
        report["protocol_version"] = "stage9-heldout-evidence-v1"
        with self.assertRaisesRegex(ValueError, "heldout evidence version mismatch"):
            assess_heldout_campaign(draft, sealed(report))

    def test_one_physical_transition_never_counts_twice_with_episode_alias(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        for kind in ("known_cause", "natural_candidate", "cross_category"):
            with self.subTest(kind=kind):
                report = make_report(draft, candidates=5)
                run = report["runs"][2]
                cases = run["known_cause_cases"]
                candidates = run["naturally_acquired_false_candidates"]
                if kind == "known_cause":
                    alias = deepcopy(cases[0])
                    alias["id"] = "case:physical-alias"
                    alias["episode_ref"] = "different-memory-episode"
                    cases.append(alias)
                elif kind == "natural_candidate":
                    candidates[1]["observation_ref"] = candidates[0]["observation_ref"]
                    candidates[1]["episode_ref"] = "different-memory-episode"
                else:
                    candidates[0]["observation_ref"] = cases[0]["observation_ref"]
                    candidates[0]["episode_ref"] = "different-memory-episode"
                with self.assertRaisesRegex(ValueError, "reused physical"):
                    assess_heldout_campaign(draft, sealed(report))

    def test_physical_refs_are_scoped_to_world_seed_run(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        report = make_report(draft, candidates=5)
        # Each world/seed run has an independent physical event namespace.
        report["runs"][1]["known_cause_cases"][0]["observation_ref"] = (
            report["runs"][0]["known_cause_cases"][0]["observation_ref"]
        )
        scored = assess_heldout_campaign(draft, sealed(report))
        self.assertEqual(scored["known_cause_cases"], 4)
        self.assertFalse(scored["golden_stage9_frozen"])

    def test_distinct_episodes_remain_evaluable_without_golden_approval(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        draft["minimum_known_cause_accuracy"] = 0.20
        draft["maximum_superstitious_rule_rate"] = 0.80
        draft["minimum_naturally_acquired_candidates"] = 2
        scored = assess_heldout_campaign(draft, make_report(draft, candidates=20))
        self.assertEqual(scored["natural_false_candidate_count"], 40)
        self.assertEqual(scored["assessment"], "metrics_eligible_for_independent_review")
        self.assertIsNone(scored["scientific_verdict"])
        self.assertFalse(scored["golden_stage9_frozen"])

    def test_holdout_json_loader_rejects_ambiguous_or_nonfinite_reports(self):
        draft = example_draft()
        draft["confidence_method"] = "wilson_95"
        report = make_report(draft, candidates=5)
        encoded = json.dumps(report)
        self.assertIn('"ground_truth": "self"', encoded)
        duplicated = encoded.replace(
            '"ground_truth": "self"',
            '"ground_truth": "world", "ground_truth": "self"',
            1,
        )
        with TemporaryDirectory() as folder:
            path = Path(folder) / "heldout.json"
            for label, raw in (
                ("duplicate_nested_key", duplicated),
                ("nonfinite_literal", encoded.replace('"seed": 1001', '"seed": NaN', 1)),
                ("root_not_object", '[]'),
            ):
                with self.subTest(label=label):
                    path.write_text(raw, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_heldout_evidence(path)
            path.write_text(encoded, encoding="utf-8")
            self.assertEqual(load_heldout_evidence(path), report)
            self.assertFalse(
                assess_heldout_campaign(draft, load_heldout_evidence(path))[
                    "golden_stage9_frozen"
                ]
            )

    def test_unsupported_confidence_method_cannot_implicitly_pass(self):
        draft = example_draft()
        report = make_report(draft)
        with self.assertRaisesRegex(ValueError, "confidence rule"):
            assess_heldout_campaign(draft, report)


if __name__ == "__main__":
    unittest.main()
