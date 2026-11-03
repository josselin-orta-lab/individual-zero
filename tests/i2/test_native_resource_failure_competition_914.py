"""Resource-specific personal learning must affect paid Competition
before critical thirst, without changing motor permissions or innate control.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_owner_support import _json
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NO_ACTION, RESOURCE_OUTCOME_EVIDENCE,
    personally_observed_resource_outcomes,
)


def _row(step, action, before, after):
    return (step, "capture:i2:test:" + str(step), action, 0.0,
            _json(before.as_dict()), _json(after.as_dict()), 0)


def _scores(event):
    frame, advice = event["frame"], event["advice"]
    if frame is None or advice is None:
        return {}
    names = {c["candidate_ref"]: c["semantic_ref"]
             for c in frame["candidates"]}
    return {names[v["candidate_ref"]]: v
            for v in advice["values"]}


class ResourceNeedFailureCompetition914(unittest.TestCase):
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)

    def test_one_failed_drink_devalues_paid_advice_above_critical_water(self):
        with tempfile.TemporaryDirectory() as directory:
            observations = {}
            for learning in (False, True):
                path = Path(directory) / ("learned" if learning else "innate")
                actor = NativePaidI2.create(
                    path, body=Body(85, 90, 15, 100),
                    temperament=self.TRAITS, learning=learning,
                    sleep_consolidation=False, water_stock=4,
                    food_stock=0, drink_water_gain=0.0)
                actor.step()  # autonomous choice at a noncritical water need
                actor.step()  # later capture may reassess that experience
                with sqlite3.connect(path) as db:
                    first = db.execute(
                        "SELECT admitted_action,before_json,after_json "
                        "FROM native_physical_events WHERE seq=1").fetchone()
                    event = json.loads(db.execute(
                        "SELECT event_json FROM events WHERE seq=2").fetchone()[0])
                self.assertEqual(first[0], "boire")
                self.assertLessEqual(json.loads(first[2])["water"],
                                     json.loads(first[1])["water"])
                self.assertIn("evidence:i2:native:outcome:1",
                              event["claim"]["subjective_evidence_refs"])
                self.assertEqual(
                    event["claim"]["capture"]["goal_ref"],
                    "goal:physical-needs")  # not the crisis mechanism
                self.assertEqual(NativePaidI2.inspect(path).audit(),
                                 actor.audit())
                observations[learning] = (_scores(event), first)
            learned, first_on = observations[True]
            innate, first_off = observations[False]
            self.assertEqual(first_on, first_off)
            self.assertIn("boire", learned)
            self.assertIn("boire", innate)
            # The learned individual has EXACTLY the same bodily need and
            # physical offers; only *its lived failed action* lowers advice.
            self.assertEqual(
                learned["boire"]["value"], innate["boire"]["value"] - 1)
            self.assertIn(RESOURCE_OUTCOME_EVIDENCE,
                          learned["boire"]["evidence_ref"])
            self.assertNotIn(RESOURCE_OUTCOME_EVIDENCE,
                             innate["boire"]["evidence_ref"])

    def test_history_retains_conflicting_outcomes_and_no_clock_inference(self):
        water = Body(85, 90, 50, 100)
        dry = Body(84.5, 89.8, 49.6, 100)
        restore = Body(84.5, 89.8, 59.6, 100)
        failed = tuple(_row(i, "boire", water, dry)
                       for i in range(1, 43))
        counts = personally_observed_resource_outcomes(
            previous=failed, traits=self.TRAITS)
        self.assertEqual(counts["boire"], (0, 42))
        # A surprising restoration is only one piece of new evidence.
        one_recovery = failed + (_row(43, "boire", water, restore),)
        counts = personally_observed_resource_outcomes(
            previous=one_recovery, traits=self.TRAITS)
        self.assertEqual(counts["boire"], (1, 42))
        # Unchosen waiting/sleep does NOT make adverse evidence expire
        # or predict the hidden resource has recovered.
        waiting = one_recovery + tuple(
            _row(i, NO_ACTION, water, dry) for i in range(44, 121))
        self.assertEqual(personally_observed_resource_outcomes(
            previous=waiting, traits=self.TRAITS)["boire"], (1, 42))
        # Associations are read from the bounded born owner's FULL journal,
        # not just its latest 64 unrelated general chosen outcomes.
        self.assertEqual(len(waiting), 120)
        self.assertEqual(
            personally_observed_resource_outcomes(
                previous=waiting, traits=self.TRAITS)["manger"], (0, 0))

    def test_experienced_success_and_failure_are_symmetric_and_specific(self):
        water = Body(85, 90, 50, 100)
        dry = Body(84.5, 89.8, 49.6, 100)
        restore = Body(84.5, 89.8, 59.6, 100)
        history = (_row(1, "boire", water, restore),
                   _row(2, "boire", water, restore),
                   _row(3, "boire", water, dry))
        counts = personally_observed_resource_outcomes(
            previous=history, traits=self.TRAITS)
        self.assertEqual(counts["boire"], (2, 1))
        self.assertEqual(counts["boire_decouverte"], (0, 0))
        self.assertEqual(counts["manger"], (0, 0))
        history += (_row(4, "boire", water, dry),)
        self.assertEqual(personally_observed_resource_outcomes(
            previous=history, traits=self.TRAITS)["boire"], (2, 2))
        # No synthetic failure when the reserve already exceeded setpoint.
        satiated = Body(85, 90, 90, 100)
        after = Body(84.5, 89.8, 89.6, 100)
        self.assertEqual(personally_observed_resource_outcomes(
            previous=(_row(1, "boire", satiated, after),),
            traits=self.TRAITS)["boire"], (0, 0))

    def test_no_success_is_inferred_from_the_wrong_need(self):
        hungry = Body(85, 40, 80, 100)
        hungry_after_drink = Body(84.5, 39.8, 79.6, 100)
        counts = personally_observed_resource_outcomes(
            previous=(_row(1, "boire", hungry, hungry_after_drink),),
            traits=self.TRAITS)
        self.assertEqual(counts["boire"], (0, 0))
        counts = personally_observed_resource_outcomes(
            previous=(_row(1, "manger", hungry, hungry_after_drink),),
            traits=self.TRAITS)
        self.assertEqual(counts["manger"], (0, 1))

    def test_one_positive_exposure_does_not_erase_forty_two_negative_ones(self):
        from i2.runtime.native_paid_cycle import personally_nonrestoring_scores
        from i2.modules.intention_continuity import FirstPersonCapture
        from i2.modules.intention_ingress import ObservationClaim
        from i2.modules.native_owner_support import current_evidence
        water = Body(85, 90, 50, 100)
        dry = Body(84.5, 89.8, 49.6, 100)
        restorative = Body(84.5, 89.8, 59.6, 100)
        previous = tuple(_row(i, "boire", water, dry)
                         for i in range(1, 43))
        evidence = current_evidence(water, self.TRAITS)
        claim = ObservationClaim(
            "life:i2:unit",
            FirstPersonCapture(400, "capture:i2:unit", "goal:physical-needs",
                               ("boire", "collecter", "dormir")),
            "source:i2:unit", tuple(sorted(evidence)))
        innate = {"boire": 7, "collecter": 3, "dormir": 2}
        scores, _, associated = personally_nonrestoring_scores(
            innate, claim=claim, body=water, traits=self.TRAITS,
            previous=previous, learning=True)
        self.assertIn("boire", associated)
        from i2.runtime.native_paid_cycle import PRIORS, innate_adjustment
        reference = innate_adjustment(PRIORS, water, self.TRAITS)["boire"]
        self.assertEqual(scores["boire"], reference - 42)
        previous += (_row(43, "boire", water, restorative),)
        recovered, _, associated = personally_nonrestoring_scores(
            innate, claim=claim, body=water, traits=self.TRAITS,
            previous=previous, learning=True)
        self.assertEqual(recovered["boire"], reference + 1 - 42)
        nolearning, _, refs = personally_nonrestoring_scores(
            innate, claim=claim, body=water, traits=self.TRAITS,
            previous=previous, learning=False)
        self.assertEqual(nolearning, innate)
        self.assertFalse(refs)


if __name__ == "__main__":
    unittest.main()
