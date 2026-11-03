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
    NativePaidI2, PRIORS, NO_ACTION, RESOURCE_FAILURE_EVIDENCE,
    consecutive_personal_need_failures, innate_adjustment,
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
                    path, body=Body(85, 90, 50, 100),
                    temperament=self.TRAITS, learning=learning,
                    sleep_consolidation=False, water_stock=4,
                    food_stock=0, drink_water_gain=0.0)
                actor.step()  # native birth chooses an actual, paid drink
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
            self.assertIn(RESOURCE_FAILURE_EVIDENCE,
                          learned["boire"]["evidence_ref"])
            self.assertNotIn(RESOURCE_FAILURE_EVIDENCE,
                             innate["boire"]["evidence_ref"])

    def test_failure_streak_is_resource_specific_bounded_and_reversible(self):
        water = Body(85, 90, 50, 100)
        dry = Body(84.5, 89.8, 49.6, 100)
        restoring = Body(84, 89.6, 59.2, 100)
        wrong_need = Body(85, 90, 90, 100)
        not_needed = Body(84.5, 89.8, 89.6, 100)
        failed = (_row(1, "boire", water, dry),)
        self.assertEqual(consecutive_personal_need_failures(
            previous=failed, action="boire", traits=self.TRAITS), 1)
        self.assertEqual(consecutive_personal_need_failures(
            previous=failed, action="manger", traits=self.TRAITS), 0)
        self.assertEqual(consecutive_personal_need_failures(
            previous=failed, action="boire_decouverte",
            traits=self.TRAITS), 0)
        failure_again = failed + (_row(2, NO_ACTION, dry, dry),
                                  _row(3, "boire", dry, Body(84, 89.6, 49.2, 100)))
        self.assertEqual(consecutive_personal_need_failures(
            previous=failure_again, action="boire", traits=self.TRAITS), 2)
        succeeded = failure_again + (_row(4, "boire", dry, restoring),)
        self.assertEqual(consecutive_personal_need_failures(
            previous=succeeded, action="boire", traits=self.TRAITS), 0)
        self.assertEqual(consecutive_personal_need_failures(
            previous=(_row(1, "boire", wrong_need, not_needed),),
            action="boire", traits=self.TRAITS), 0)
        many = tuple(_row(i, "boire", water, dry) for i in range(1, 91))
        self.assertEqual(consecutive_personal_need_failures(
            previous=many, action="boire", traits=self.TRAITS), 64)

    def test_nonrestoration_is_not_a_failed_unrelated_need(self):
        hungry = Body(85, 40, 80, 100)
        hungry_after_drink = Body(84.5, 39.8, 79.6, 100)
        self.assertEqual(consecutive_personal_need_failures(
            previous=(_row(1, "boire", hungry, hungry_after_drink),),
            action="boire", traits=self.TRAITS), 0)
        self.assertEqual(consecutive_personal_need_failures(
            previous=(_row(1, "manger", hungry, hungry_after_drink),),
            action="manger", traits=self.TRAITS), 1)


if __name__ == "__main__":
    unittest.main()
