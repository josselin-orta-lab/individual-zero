"""Birth-locked, evidence-tied exploratory arbitration without motor commands.

No hypothetical discovered-resource outcome influences the first three
choices. The original archived stable-world arm keeps its born flag off.
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
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.native_owner_support import _json, current_evidence
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NO_ACTION, native_evidence_tie_exploration,
    TIE_EXPLORATION_EVIDENCE,
)


def lived_row(seq, action, before, after):
    return (seq, "capture:i2:unit:" + str(seq), action, 0.0,
            _json(before.as_dict()), _json(after.as_dict()), 0)


class EvidenceTiedExploration918(unittest.TestCase):
    TRAITS = BirthTemperament(0, .5, .3, 0, 0)

    def test_opt_in_relieves_only_lived_failures_tie(self):
        with tempfile.TemporaryDirectory() as root:
            cases = {}
            for source_gain in (0.0, 10.0):
                for enabled in (False, True):
                    key = (source_gain, enabled)
                    path = Path(root) / ("gain-%s-mode-%s.db" %
                                         (source_gain, enabled))
                    life = NativePaidI2.create(
                        path, body=Body(85,90,35,100),
                        temperament=self.TRAITS, learning=True,
                        evidence_tie_exploration=enabled,
                        sleep_consolidation=False, max_steps=24,
                        uc=300, water_stock=8, food_stock=0,
                        water_restock_every=0, drink_water_gain=0.0,
                        discovered_water_gain=source_gain)
                    for _ in range(3):
                        life.step()
                    self.assertEqual(NativePaidI2.inspect(path).audit(),
                                     life.audit())
                    with sqlite3.connect(path) as db:
                        actions = [row[0] for row in db.execute(
                            "SELECT admitted_action FROM native_physical_events "
                            "ORDER BY seq")]
                        event = json.loads(db.execute(
                            "SELECT event_json FROM events WHERE seq=3").fetchone()[0])
                        gen = db.execute(
                            "SELECT evidence_tie_exploration FROM native_genesis"
                            ).fetchone()[0]
                    self.assertEqual(gen, int(enabled))
                    self.assertEqual(actions[:2], ["boire", "boire"])
                    self.assertFalse(any("water-quality" in ref for ref
                        in event["claim"]["subjective_evidence_refs"]))
                    names = {item["candidate_ref"]: item["semantic_ref"]
                             for item in event["frame"]["candidates"]}
                    scores = {
                        names[item["candidate_ref"]]:
                        (item["value"], item["evidence_ref"])
                        for item in event["advice"]["values"]}
                    cases[key] = (actions, scores, event["advice"]["status"])
            for gain in (0.0, 10.0):
                legacy = cases[(gain, False)]
                exploratory = cases[(gain, True)]
                self.assertEqual(legacy[0][2], NO_ACTION)
                self.assertEqual(legacy[2], "AMBIGUOUS")
                self.assertEqual(exploratory[0][2], "collecter")
                self.assertEqual(exploratory[2], "ADVISORY_ONLY")
                self.assertEqual(exploratory[1]["collecter"][0], 4)
                self.assertIn(TIE_EXPLORATION_EVIDENCE,
                              exploratory[1]["collecter"][1])
            self.assertEqual(cases[(0.0,True)][0],
                             cases[(10.0,True)][0])
            self.assertEqual(cases[(0.0,True)][1]["collecter"][0],
                             cases[(10.0,True)][1]["collecter"][0])

    def test_pure_negative_gate_never_uses_hidden_world_or_clock(self):
        body = Body(85,90,35,100)
        traits = self.TRAITS
        evidence = tuple(sorted(current_evidence(body, traits)))
        claim = ObservationClaim(
            "life:i2:unit",
            FirstPersonCapture(200, "capture:i2:unit", "goal:physical-needs",
                               ("boire", "collecter", "dormir")),
            "source:i2:unit", evidence)
        before = Body(85,90,35,100)
        after = Body(84,89.8,34.6,100)
        rows = (lived_row(1,"boire",before,after),
                lived_row(2,"boire",before,after))
        tied = {"boire":3,"collecter":3,"dormir":2}
        def evaluate(scores=tied, previous=rows, learning=True,
                     enabled=True, traits=traits):
            return native_evidence_tie_exploration(
                scores, claim=claim, body=body, traits=traits,
                previous=previous, learning=learning, enabled=enabled)
        values, markers = evaluate()
        self.assertEqual(values["collecter"],4)
        self.assertEqual(markers,frozenset({"collecter"}))
        self.assertEqual(evaluate(enabled=False)[0],tied)
        self.assertEqual(evaluate(learning=False)[0],tied)
        self.assertEqual(evaluate(previous=rows[:1])[0],tied)
        self.assertEqual(evaluate(previous=rows + (
            lived_row(3,"collecter",before,after),))[0],tied)
        self.assertEqual(evaluate(scores={"boire":3,"collecter":3,
                                          "dormir":3})[0],
                         {"boire":3,"collecter":3,"dormir":3})
        self.assertEqual(evaluate(
            traits=BirthTemperament(0,.5,0,0,0))[0],tied)


if __name__ == "__main__":
    unittest.main()
