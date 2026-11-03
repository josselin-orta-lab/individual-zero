"""Regression: experienced ineffective water ties an untried opportunity.

The test never selects a motor action and never invents the quality of a
source that the individual has not yet visited. Source: frozen #916.
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
from i2.runtime.native_paid_cycle import NativePaidI2, NO_ACTION


class StableUnresolvedCompetition906(unittest.TestCase):
    def test_equal_positive_maxima_make_learning_arm_abstain(self):
        states = {}
        with tempfile.TemporaryDirectory() as d:
            for learning in (False, True):
                path = Path(d) / ("on" if learning else "off")
                life = NativePaidI2.create(
                    path, body=Body(85, 90, 35, 100),
                    temperament=BirthTemperament(0, .5, .3, 0, 0),
                    learning=learning, sleep_consolidation=False,
                    max_steps=24, uc=300, food_stock=0, water_stock=8,
                    water_restock_every=0, drink_water_gain=0.0,
                    discovered_water_gain=10.0)
                for _ in range(3):
                    life.step()
                self.assertEqual(NativePaidI2.inspect(path).audit(), life.audit())
                with sqlite3.connect(path) as db:
                    actions = [x[0] for x in db.execute(
                        "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
                    event = json.loads(db.execute(
                        "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
                    before = db.execute(
                        "SELECT before_json FROM native_physical_events "
                        "WHERE seq=3").fetchone()[0]
                self.assertEqual(actions[:2], ["boire", "boire"])
                meanings = {v["candidate_ref"]: v["semantic_ref"]
                            for v in event["frame"]["candidates"]}
                scores = {meanings[v["candidate_ref"]]: v["value"]
                          for v in event["advice"]["values"]}
                states[learning] = (actions, event, before, scores)
            off, on = states[False], states[True]
            self.assertEqual(off[2], on[2])
            # Independent birth refs differ, but the observable body, source
            # availability and actual first-person facts remain matched.
            self.assertEqual(
                off[1]["claim"]["subjective_evidence_refs"],
                on[1]["claim"]["subjective_evidence_refs"])
            self.assertEqual(
                off[1]["claim"]["capture"]["accessible_semantics"],
                on[1]["claim"]["capture"]["accessible_semantics"])
            self.assertEqual(off[3]["boire"], 5)
            self.assertEqual(off[0][2], "boire")
            self.assertEqual(on[3]["boire"], 3)
            self.assertEqual(on[3]["collecter"], 3)
            self.assertEqual(on[1]["advice"]["status"], "AMBIGUOUS")
            self.assertIsNone(on[1]["advice"]["suggested_candidate_ref"])
            self.assertEqual(on[0][2], NO_ACTION)


if __name__ == "__main__":
    unittest.main()
