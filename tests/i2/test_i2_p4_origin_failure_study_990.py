"""#990 pure study-contract tests. Absolutely no real born-life cohort in CI."""
from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.i2_p4_origin_failure_study_990 import (
    ARMS, MAX_STEPS, WORLD_HARMS, frozen_cells,
    frozen_birth_kwargs, first_matched_factor_divergence,
    classify_protocol_exposure, run_study, verify_custody_receipt,
)


def frame(action, *, before=None, after=None, site="camp", offers=None,
          factor_tagged=False, chosen_motor_credited=False,
          subjective_context=None):
    body = before or {"energy": 78.0, "food": 46.0,
                      "water": 44.0, "integrity": 94.0}
    return {
        "action": action, "before": body, "after": after or body,
        "site_before": site, "site_after": site,
        "offered": offers or ["attendre", "se_deplacer_vers_passage"],
        "factor_tagged": factor_tagged,
        "factor_credited_chosen_motor": chosen_motor_credited,
        "subjective_context": (
            {"goal": "goal:physical-needs",
             "evidence": ["local:camp"], "contradicted": []}
            if subjective_context is None else subjective_context),
    }


def diagnose(*failed_ticks):
    return {"ticks": [{"failed_channels": ["food"] if tick in failed_ticks
                       else []} for tick in range(5)]}


class P4OriginFailure990Contract(unittest.TestCase):
    def test_exact_six_prospectively_frozen_birth_cells(self):
        cells = frozen_cells()
        self.assertEqual(len(cells), 6)
        self.assertEqual(len(set(cells)), 6)
        self.assertEqual(len(ARMS), 3)
        self.assertEqual(len(WORLD_HARMS), 2)
        for cell in cells:
            world, harm, arm, learning, factor = cell
            law = frozen_birth_kwargs(cell)
            self.assertEqual(law["max_steps"], MAX_STEPS)
            self.assertEqual(MAX_STEPS, 128)
            self.assertEqual(law["uc"], 1000)
            self.assertEqual(law["ordinary_food_site"], "camp")
            self.assertEqual(law["second_food_site"], "passage")
            self.assertEqual(law["food_stock"], 1)
            self.assertEqual(law["second_food_stock"], 1)
            self.assertEqual(law["berry_food_gain"], 0.0)
            self.assertEqual(law["second_berry_food_gain"], 20.0)
            self.assertEqual(law["food_restock_every"], 8)
            self.assertEqual(law["second_food_restock_every"], 8)
            self.assertEqual(law["water_restock_every"], 10)
            self.assertEqual(law["ordinary_water_site"], "camp")
            self.assertFalse(law["origin_novelty_tie"])
            self.assertEqual(law["learning"], learning)
            self.assertEqual(law["need_failure_exploration"], factor)
            self.assertEqual(law["second_berry_integrity_delta"], harm)
            self.assertEqual(law["body"].as_dict(),
                             {"energy": 78, "food": 46,
                              "water": 44, "integrity": 94})
            self.assertEqual(law["temperament"].as_dict(), {
                "reward_sensitivity": 0, "threat_sensitivity": .5,
                "exploration": .3, "goal_protection": 0,
                "affiliation": 0,
            })
        self.assertEqual(
            {frozen_birth_kwargs(c)["second_berry_integrity_delta"]
             for c in cells}, {0.0, -12.0})

    def test_undeclared_cell_rejected(self):
        with self.assertRaises(ValueError):
            frozen_birth_kwargs(("favorable", 0, "factor", True, True))

    @patch("tools.i2_p4_origin_failure_study_990.NativePaidI2.create")
    def test_dry_run_refuses_before_birth_or_output(self, birth):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "cohort"
            with self.assertRaisesRegex(ValueError, "explicit"):
                run_study(destination, execute=False, expected_head="0" * 40)
            self.assertFalse(destination.exists())
        birth.assert_not_called()

    @patch("tools.i2_p4_origin_failure_study_990.NativePaidI2.create")
    def test_bad_head_refused_before_birth(self, birth):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "clean source-locked"):
                with patch("tools.i2_p4_origin_failure_study_990._require_exact_clean_checkout",
                           side_effect=ValueError("exact clean source-locked")):
                    run_study(Path(folder) / "study", execute=True,
                              expected_head="1" * 40)
        birth.assert_not_called()

    def test_off_factor_motors_do_not_create_divergence(self):
        arms = [frame("attendre"), frame("attendre")]
        outcome = first_matched_factor_divergence(
            arms, arms, diagnose(1), diagnose(1))
        self.assertEqual(outcome["classification"], "NO_MOTOR_DIVERGENCE")

    def test_genuine_matched_first_divergence_after_failed_food(self):
        common = [frame("manger"), frame("manger")]
        off = common + [frame("attendre")]
        on = common + [frame("se_deplacer_vers_passage",
                             factor_tagged=True, chosen_motor_credited=True)]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_AFTER_MATCHED_FAILURE_WITH_FACTOR_CREDIT")
        self.assertTrue(result["factor_tagged_at_divergence"])
        self.assertTrue(result["chosen_motor_factor_credited"])
        self.assertEqual(result["first_motor_divergence_tick"], 3)
        self.assertTrue(result["same_prehistory"])

    def test_factor_on_unchosen_candidate_is_not_chosen_motor_credit(self):
        common = [frame("manger"), frame("manger")]
        off = common + [frame("attendre")]
        on = common + [frame("se_deplacer_vers_passage",
                             factor_tagged=True,
                             chosen_motor_credited=False)]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(
            result["classification"],
            "DIVERGENCE_AFTER_MATCHED_FAILURE_NO_FACTOR_CREDIT",
        )
        self.assertTrue(result["factor_tagged_at_divergence"])
        self.assertFalse(result["chosen_motor_factor_credited"])

    def test_matched_postfailure_divergence_without_tag_not_credited(self):
        common = [frame("manger"), frame("manger")]
        off = common + [frame("attendre")]
        on = common + [frame("se_deplacer_vers_passage")]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_AFTER_MATCHED_FAILURE_NO_FACTOR_CREDIT")
        self.assertFalse(result["factor_tagged_at_divergence"])

    def test_passage_failures_do_not_count_as_origin_exposure(self):
        common = [frame("manger", site="passage"),
                  frame("manger", site="passage")]
        off = common + [frame("attendre", site="passage")]
        on = common + [frame("se_deplacer_vers_camp",
                             site="passage", factor_tagged=True,
                             chosen_motor_credited=True)]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(
            result["classification"],
            "DIVERGENCE_WITHOUT_TWO_FAILED_ORIGIN_MEALS")
        self.assertTrue(result["same_prehistory"])

    def test_prior_different_local_offers_block_matched_history(self):
        normal = ["attendre", "manger", "se_deplacer_vers_passage"]
        hidden = ["attendre", "manger"]
        off = [frame("manger", offers=normal),
               frame("manger", offers=normal),
               frame("attendre")]
        on = [frame("manger", offers=hidden),
              frame("manger", offers=normal),
              frame("se_deplacer_vers_passage",
                    factor_tagged=True, chosen_motor_credited=True)]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_WITH_UNMATCHED_HISTORY")
        self.assertFalse(result["same_prehistory"])

    def test_prior_different_subjective_claim_blocks_matched_history(self):
        changed = {"goal": "goal:physical-last-resort",
                   "evidence": ["local:camp"], "contradicted": []}
        off = [frame("manger"), frame("manger"), frame("attendre")]
        on = [frame("manger", subjective_context=changed),
              frame("manger"),
              frame("se_deplacer_vers_passage",
                    factor_tagged=True, chosen_motor_credited=True)]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_WITH_UNMATCHED_HISTORY")
        self.assertFalse(result["same_prehistory"])

    def test_current_different_subjective_evidence_blocks_attribution(self):
        changed = {"goal": "goal:physical-needs",
                   "evidence": ["local:camp", "new:personal"], "contradicted": []}
        common = [frame("manger"), frame("manger")]
        off = common + [frame("attendre")]
        on = common + [frame("se_deplacer_vers_passage",
                             factor_tagged=True, chosen_motor_credited=True,
                             subjective_context=changed)]
        result = first_matched_factor_divergence(
            off, on, diagnose(2), diagnose(2))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_WITH_UNMATCHED_HISTORY")
        self.assertFalse(result["same_prehistory"])

    def test_no_origin_exposure_and_factor_inactive_are_separate(self):
        trace = [dict(frame("attendre"), tick=1)]
        diag = {"ticks": [{"tick": 1, "failed_channels": [],
                           "unknown_offered": [], "reason": "NO_FAILED_CURRENT_NEED"}]}
        report = classify_protocol_exposure(
            trace, diag, factor_enabled=True)
        self.assertIn("NO_DOUBLE_FAILURE_EXPOSURE", report["labels"])
        self.assertIn("FACTOR_INACTIVE", report["labels"])
        self.assertIn("NO_SAFE_RECOVERY", report["labels"])
        self.assertNotIn("NO_SCORE_ELIGIBILITY", report["labels"])

    def test_food_failure_without_unseen_offer_is_not_ineligible_score(self):
        trace = [dict(frame("manger"), tick=1),
                 dict(frame("manger"), tick=2),
                 dict(frame("attendre"), tick=3)]
        diag = {"ticks": [
            {"tick": 1, "failed_channels": [],
             "unknown_offered": [], "reason": "NO_FAILED_CURRENT_NEED"},
            {"tick": 2, "failed_channels": [],
             "unknown_offered": [], "reason": "NO_FAILED_CURRENT_NEED"},
            {"tick": 3, "failed_channels": ["food"],
             "unknown_offered": [], "reason": "NO_UNSEEN_OFFERED_MOVE"}]}
        report = classify_protocol_exposure(
            trace, diag, factor_enabled=False)
        self.assertEqual(report["first_origin_double_failure_predecision_tick"], 3)
        self.assertIn("NO_ADMISSIBLE_ALTERNATIVE", report["labels"])
        self.assertNotIn("NO_SCORE_ELIGIBILITY", report["labels"])

    def test_offered_unknown_with_nonpositive_score_is_separate(self):
        trace = [dict(frame("manger"), tick=1),
                 dict(frame("manger"), tick=2),
                 dict(frame("attendre"), tick=3)]
        diag = {"ticks": [
            {"tick": 1, "failed_channels": [],
             "unknown_offered": [], "reason": "NO_FAILED_CURRENT_NEED"},
            {"tick": 2, "failed_channels": [],
             "unknown_offered": [], "reason": "NO_FAILED_CURRENT_NEED"},
            {"tick": 3, "failed_channels": ["food"],
             "unknown_offered": ["se_deplacer_vers_passage"],
             "reason": "NONPOSITIVE_SCORE"}]}
        report = classify_protocol_exposure(
            trace, diag, factor_enabled=True)
        self.assertIn("NO_SCORE_ELIGIBILITY", report["labels"])
        self.assertIn("FACTOR_INACTIVE", report["labels"])
        self.assertNotIn("NO_ADMISSIBLE_ALTERNATIVE", report["labels"])

    def test_visit_without_eating_retains_negative_outcome(self):
        trace = [dict(frame("se_deplacer_vers_passage",
                            site="camp"), tick=1, site_after="passage"),
                 dict(frame("attendre", site="passage"), tick=2)]
        diag = {"ticks": [
            {"tick": 1, "failed_channels": [], "unknown_offered": [],
             "reason": "NO_FAILED_CURRENT_NEED"},
            {"tick": 2, "failed_channels": [], "unknown_offered": [],
             "reason": "NO_FAILED_CURRENT_NEED"}]}
        report = classify_protocol_exposure(
            trace, diag, factor_enabled=False)
        self.assertIn("VISIT_WITHOUT_MEAL", report["labels"])
        self.assertIn("NO_SAFE_RECOVERY", report["labels"])
        self.assertEqual(report["passage_meal_ticks"], [])

    def test_observer_refuses_unaligned_tick_history(self):
        trace = [dict(frame("attendre"), tick=2)]
        diag = {"ticks": [{"tick": 1, "failed_channels": [],
                           "unknown_offered": [], "reason": "NO_FAILED_CURRENT_NEED"}]}
        with self.assertRaisesRegex(ValueError, "unaligned"):
            classify_protocol_exposure(trace, diag, factor_enabled=True)

    def test_retained_archive_receipt_rejects_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "original.sqlite"
            archive = Path(folder) / "archive.sqlite"
            archive.write_bytes(b"original-archive")
            end = dict(revision=3, max_steps=3, terminal=False,
                       remaining_uc=50, site="camp", body={"food": 30})
            receipt = dict(
                source=str(source), archive=str(archive), cold_audit="PASS",
                revision=3, max_steps=3, biological_terminal=False,
                right_censored=True, remaining_uc=50, site="camp",
                body=end["body"],
                archive_sha256=sha256(archive.read_bytes()).hexdigest())
            self.assertTrue(verify_custody_receipt(
                source, archive, receipt, end))
            archive.write_bytes(b"replaced-archive")
            with self.assertRaisesRegex(ValueError, "digest"):
                verify_custody_receipt(source, archive, receipt, end)
            archive.write_bytes(b"original-archive")
            with self.assertRaisesRegex(ValueError, "not bound"):
                verify_custody_receipt(
                    source, archive, dict(receipt, remaining_uc=49), end)

    def test_pre_failure_divergence_not_credited_to_lived_failure(self):
        common = [frame("attendre")]
        result = first_matched_factor_divergence(
            common + [frame("attendre")],
            common + [frame("se_deplacer_vers_passage")],
            diagnose(), diagnose())
        self.assertEqual(result["classification"],
                         "DIVERGENCE_BEFORE_PERSONAL_DOUBLE_FAILURE")

    def test_different_current_body_prevents_clean_attribution(self):
        off = [frame("manger")] + [
            frame("attendre", before={"energy": 70., "food": 44.,
                                     "water": 42., "integrity": 94.})]
        on = [frame("manger")] + [
            frame("se_deplacer_vers_passage",
                  before={"energy": 69., "food": 43.,
                          "water": 42., "integrity": 94.})]
        result = first_matched_factor_divergence(
            off, on, diagnose(1), diagnose(1))
        self.assertEqual(result["classification"],
                         "DIVERGENCE_WITH_UNMATCHED_HISTORY")
        self.assertFalse(result["same_prehistory"])

    def test_identical_motors_different_body_are_not_matched_lives(self):
        a = [frame("attendre")]
        b = [frame("attendre", after={
            "energy": 77.0, "food": 46.0, "water": 44.0,
            "integrity": 94.0,
        })]
        result = first_matched_factor_divergence(a, b, diagnose(), diagnose())
        self.assertEqual(
            result["classification"],
            "NO_MOTOR_DIVERGENCE_BUT_PHYSICS_UNMATCHED",
        )
        self.assertFalse(result["same_prehistory"])

    def test_different_lengths_are_not_a_matching_effect(self):
        result = first_matched_factor_divergence(
            [frame("manger")], [frame("manger"), frame("attendre")],
            diagnose(), diagnose())
        self.assertEqual(result["classification"],
                         "DIFFERENT_OBSERVED_LIFE_LENGTHS")


if __name__ == "__main__":
    unittest.main()
