"""#986 pure, no-born-life, no-physics-tuning adversarial opportunity checks."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_need_failure_opportunity_audit import (
    audit_need_failure_opportunities, report_need_failure_opportunities,
)

TRAITS = BirthTemperament(0, .5, .3, 0, 0)
BODY = {"energy": 78.0, "food": 46.0, "water": 44.0, "integrity": 94.0}
FAIL = ":personal-need-failure-adjacent-exploration"
OLD = ":visited-versus-unvisited-adjacent-tie"


def canon(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def make_event(offered, scores=None, tags=None):
    capture = {"accessible_semantics": sorted(offered)}
    if scores is None:
        return {"claim": {"capture": capture}, "frame": None, "advice": None}
    tags = tags or {}
    return {
        "claim": {"capture": capture},
        "frame": {"candidates": [
            {"candidate_ref": "r:"+name, "semantic_ref": name}
            for name in sorted(offered)]},
        "advice": {"values": [
            {"candidate_ref": "r:"+name, "value": scores[name],
             "evidence_ref": "signed"+tags.get(name, "")}
            for name in sorted(offered)]},
    }


def make_effect(action, before=BODY, after=None):
    return (action, canon(before), canon(before if after is None else after))


def records(*, meal_count=2, restore=False, move=True, scores=None,
            tags=None, before=BODY, offered=None, action="NO_ACTION",
            first_meal_body=None):
    events, effects = [], []
    body = dict(first_meal_body or BODY)
    if move:
        events.append(make_event(["se_deplacer_vers_passage"],
                                 {"se_deplacer_vers_passage": 5}))
        effects.append(make_effect("se_deplacer_vers_passage", body))
    for i in range(meal_count):
        events.append(make_event(["manger", "attendre"],
                                 {"manger": 6, "attendre": 1}))
        next_body = dict(body)
        if restore and i == meal_count - 1:
            next_body["food"] += 5
        else:
            next_body["food"] -= .2
        effects.append(make_effect("manger", body, next_body))
        body = next_body
    if before is not BODY:
        body = dict(before)
        if effects:
            # The malformed-history test intentionally breaks continuity.
            pass
    offered = offered or (["attendre", "se_deplacer_vers_source"]
                          if move else ["attendre", "se_deplacer_vers_passage"])
    scores = scores or {name: 5 if name == "attendre" else 3 for name in offered}
    events.append(make_event(offered, scores, tags))
    effects.append(make_effect(action, body))
    return events, effects


def classify(**kwargs):
    events, physical = records(**kwargs)
    return audit_need_failure_opportunities(
        events=events, physical=physical, traits=TRAITS, factor_enabled=True)


class NeedFailureOpportunityAudit986(unittest.TestCase):
    def test_two_observed_failures_and_paid_gap(self):
        rows = classify(meal_count=2)
        self.assertEqual(rows[-1].reason, "ELIGIBLE_BUT_NOT_CREDITED")
        self.assertEqual(rows[-1].failed_channels, ("food",))
        self.assertEqual(rows[-1].score_gap, 2)
        result = report_need_failure_opportunities(
            events=records(meal_count=2)[0],
            physical=records(meal_count=2)[1],
            traits=TRAITS, factor_enabled=False)
        self.assertEqual(result["summary"]["factor_tags"], 0)
        self.assertTrue(result["summary"]["diagnostic_only"])
        self.assertFalse(result["summary"]["preboost_score_imputed"])
        self.assertEqual(result["summary"]["first_double_failure_tick"], 4)
        self.assertEqual(
            result["summary"]["first_unique_unseen_and_double_failure_tick"], 4)
        self.assertIsNone(result["summary"]["first_factor_tag_tick"])
        self.assertEqual(result["summary"]["no_movement_offered_ticks"], 2)
        self.assertEqual(result["summary"]["only_visited_moves_offered_ticks"], 0)
        self.assertEqual(result["summary"]["positive_bounded_score_opportunity_ticks"], 1)
        self.assertEqual(result["summary"]["eligible_but_not_credited_on_ticks"], 0)
        enabled = report_need_failure_opportunities(
            events=records(meal_count=2)[0],
            physical=records(meal_count=2)[1],
            traits=TRAITS, factor_enabled=True)
        self.assertEqual(enabled["summary"]["eligible_but_not_credited_on_ticks"], 1)
        # Synthetic history intentionally has an unexplained ON non-credit.
        # The real native cold audit must reject an impossible signed event.
        self.assertEqual(enabled["ticks"][-1]["reason"], "ELIGIBLE_BUT_NOT_CREDITED")

    def test_no_or_one_failed_attempt_and_later_success(self):
        for count in (0, 1):
            self.assertEqual(classify(meal_count=count)[-1].reason,
                             "NO_FAILED_CURRENT_NEED")
        self.assertEqual(classify(meal_count=2, restore=True)[-1].reason,
                         "NO_FAILED_CURRENT_NEED")

    def test_no_current_need_and_urgent_reflex(self):
        full = dict(BODY, food=72.0)
        self.assertEqual(classify(meal_count=2, first_meal_body=full)[-1].reason,
                         "NO_FAILED_CURRENT_NEED")
        urgent = dict(BODY, water=9.0)
        self.assertEqual(classify(meal_count=2, first_meal_body=urgent)[-1].reason,
                         "URGENT_REFLEX")

    def test_known_destination_and_empty_unknown_set(self):
        rows = classify(move=True, meal_count=2,
                        offered=["attendre", "se_deplacer_vers_camp"])
        self.assertEqual(rows[-1].reason, "NO_UNSEEN_OFFERED_MOVE")
        # Only personally committed movement produces the visited set.
        self.assertEqual(rows[-1].visited_before, ("camp", "passage"))

    def test_old_novelty_cannot_stack_and_new_tag_preboost_unknown(self):
        offered = ["attendre", "se_deplacer_vers_source"]
        scores = {"attendre": 5, "se_deplacer_vers_source": 6}
        rows = classify(scores=scores, tags={"se_deplacer_vers_source": OLD})
        self.assertEqual(rows[-1].reason, "ORIGIN_NOVELTY_ALREADY_CREDITED")
        rows = classify(scores=scores, tags={"se_deplacer_vers_source": FAIL})
        self.assertEqual(rows[-1].reason, "UNOBSERVABLE_PREBOOST_SCORE")
        self.assertIsNone(rows[-1].score_gap)

    def test_bad_score_gap_and_nonpositive(self):
        offered = ["attendre", "se_deplacer_vers_source"]
        self.assertEqual(classify(scores={"attendre": 9,
                          "se_deplacer_vers_source": 3})[-1].reason,
                         "SCORE_GAP_GT_FOUR")
        self.assertEqual(classify(scores={"attendre": 5,
                          "se_deplacer_vers_source": 0})[-1].reason,
                         "NONPOSITIVE_SCORE")

    def test_unsigned_score_bad_offer_and_physical_discontinuity(self):
        es, ps = records()
        es[-1]["advice"]["values"].pop()
        with self.assertRaises(ValueError):
            audit_need_failure_opportunities(
                events=es, physical=ps, traits=TRAITS, factor_enabled=True)
        es, ps = records()
        es[-1]["claim"]["capture"]["accessible_semantics"] = [
            "attendre", "se_deplacer_vers_camp"]
        with self.assertRaises(ValueError):
            audit_need_failure_opportunities(
                events=es, physical=ps, traits=TRAITS, factor_enabled=True)
        es, ps = records(before=dict(BODY, food=20))
        with self.assertRaises(ValueError):
            audit_need_failure_opportunities(
                events=es, physical=ps, traits=TRAITS, factor_enabled=True)

    def test_incorrect_disabled_tag_and_impossible_activation(self):
        es, ps = records(tags={"se_deplacer_vers_source": FAIL})
        with self.assertRaises(ValueError):
            audit_need_failure_opportunities(
                events=es, physical=ps, traits=TRAITS, factor_enabled=False)
        es, ps = records(meal_count=0,
                         tags={"se_deplacer_vers_source": FAIL})
        with self.assertRaises(ValueError):
            audit_need_failure_opportunities(
                events=es, physical=ps, traits=TRAITS, factor_enabled=True)

    def test_no_paid_frame_is_not_an_invented_decision(self):
        e = make_event(["attendre"])
        rows = audit_need_failure_opportunities(
            events=[e], physical=[make_effect("NO_ACTION")],
            traits=TRAITS, factor_enabled=True)
        self.assertEqual(rows[0].reason, "NO_PAID_FRAME")
        with self.assertRaises(ValueError):
            audit_need_failure_opportunities(
                events=[e], physical=[make_effect("attendre")],
                traits=TRAITS, factor_enabled=True)


if __name__ == "__main__":
    unittest.main()
