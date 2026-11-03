"""Predeclared 2x2 native I2 worlds: no-learning control and empty-source negative.

Engineering cohort only.  Four steps are insufficient to infer survival or
general adaptation; this checks physical access, causal provenance, and
the *absence* of a fabricated payoff in the empty-source control.
"""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import NativePaidI2


class NativeMatchedWorldCohort(unittest.TestCase):
    BIRTH = Body(80, 60, 3, 100)
    TRAITS = BirthTemperament(0, 0.5, 0.3, 0, 0)
    FIXED_PARAMETERS = dict(
        food_stock=0, water_stock=4, drink_water_gain=0.0,
        sleep_consolidation=False, uc=80,
    )
    HORIZON = 4
    WORLD_OUTCOMES = (("empty", 0.0), ("water", 30.0))

    def test_same_physical_world_has_no_learning_dependent_affordances(self):
        with tempfile.TemporaryDirectory() as temp:
            results = {}
            for label, gain in self.WORLD_OUTCOMES:
                for learned in (False, True):
                    with self.subTest(world=label, learned=learned):
                        db_path = Path(temp) / (label + "-" + str(learned) + ".sqlite")
                        actor = NativePaidI2.create(
                            db_path, body=self.BIRTH, temperament=self.TRAITS,
                            learning=learned, discovered_water_gain=gain,
                            **self.FIXED_PARAMETERS)
                        birth = actor.audit()
                        for _ in range(self.HORIZON):
                            actor.step()
                        ending = actor.audit()
                        with sqlite3.connect(db_path) as db:
                            captures = [json.loads(row[0]) for row in db.execute(
                                "SELECT event_json FROM events ORDER BY seq")]
                            actions = [row[0] for row in db.execute(
                                "SELECT admitted_action FROM native_physical_events "
                                "ORDER BY seq")]
                            discoveries = [tuple(row) for row in db.execute(
                                "SELECT seq,found FROM native_discoveries ORDER BY seq")]
                        self.assertEqual(ending["revision"], self.HORIZON)
                        self.assertEqual(ending["m11_authenticated"], False)
                        self.assertEqual(ending["engine_registered"], False)
                        self.assertLess(ending["remaining_uc"], birth["remaining_uc"])
                        self.assertEqual(birth["body"], self.BIRTH.as_dict())
                        self.assertEqual(birth["temperament"], self.TRAITS.as_dict())
                        first = tuple(captures[0]["claim"]["capture"]["accessible_semantics"])
                        self.assertIn("collecter", first)
                        self.assertNotIn("boire_decouverte", first)
                        for seq, event in enumerate(captures, 1):
                            if "boire_decouverte" in event["claim"]["capture"]["accessible_semantics"]:
                                self.assertTrue(any(
                                    dseq < seq and found == 1 for dseq, found in discoveries))
                            if seq == 1:
                                self.assertNotIn(
                                    "evidence:i2:native:water-found:1",
                                    event["claim"]["subjective_evidence_refs"])
                        self.assertLessEqual(actions.count("collecter"), 1)
                        self.assertLessEqual(actions.count("boire_decouverte"), 1)
                        results[(label, learned)] = {
                            "first": first, "actions": actions,
                            "discovered": discoveries,
                            "ending": ending, "captured": captures,
                        }
                self.assertEqual(results[(label, False)]["first"],
                                 results[(label, True)]["first"])
                # A world outcome cannot alter the first capture of either arm.
                self.assertEqual(results[(label, False)]["first"],
                                 results[(self.WORLD_OUTCOMES[0][0], False)]["first"])

            good = results[("water", True)]
            empty = results[("empty", True)]
            fixed_good = results[("water", False)]
            fixed_empty = results[("empty", False)]

            # The exploratory action is a learned policy decision, not a
            # permission restricted by the physical world or learning flag.
            self.assertEqual(good["actions"][:2], ["boire", "boire"])
            self.assertEqual(empty["actions"][:2], ["boire", "boire"])
            self.assertIn("collecter", good["actions"])
            self.assertIn("collecter", empty["actions"])
            self.assertNotIn("collecter", fixed_good["actions"])
            self.assertNotIn("collecter", fixed_empty["actions"])
            self.assertEqual(good["discovered"], [(3, 1)])
            self.assertEqual(empty["discovered"], [(3, 0)])
            self.assertEqual(fixed_good["discovered"], [])
            self.assertEqual(fixed_empty["discovered"], [])

            # Only the physically successful discovery can restore water.
            self.assertIn("boire_decouverte", good["actions"])
            self.assertNotIn("boire_decouverte", empty["actions"])
            self.assertGreater(good["ending"]["body"]["water"],
                               empty["ending"]["body"]["water"])
            self.assertEqual(fixed_good["ending"]["body"],
                             fixed_empty["ending"]["body"])
            self.assertEqual(fixed_good["actions"], fixed_empty["actions"])
            self.assertFalse(good["ending"]["terminal"])
            self.assertFalse(empty["ending"]["terminal"])
            # No four-tick outcome establishes improved survival.  The local
            # experiment establishes a bounded decision and water difference.


if __name__ == "__main__":
    unittest.main()
