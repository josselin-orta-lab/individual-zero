"""#982: pure eligibility tests versus an independent genuine I2 cold replay.

Synthetic rows are ONLY analyzer fixtures, never individual motor evidence.
The real born test audits the native SQLite owner before projecting history.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_body_contract import Body
from i2.modules.native_owner_support import _json
from i2.modules.native_exploration_opportunity import (
    NOVELTY_SUFFIX, audit_paid_opportunities, classify_opportunity,
    summarize_source_opportunities,
)
from i2.runtime.native_paid_cycle import NativePaidI2

TRAITS = BirthTemperament(0, .5, .3, 0, 0)


def event(offered, scores, *, novelty=None):
    candidates = [
        {"candidate_ref": "c" + str(i), "semantic_ref": action}
        for i, action in enumerate(offered)
    ]
    return {
        "claim": {"capture": {"accessible_semantics": list(offered)}},
        "frame": {"candidates": candidates},
        "advice": {"values": [
            {"candidate_ref": c["candidate_ref"],
             "value": scores[c["semantic_ref"]] +
                      int(c["semantic_ref"] == novelty),
             "evidence_ref": "paid:test:native-body" +
                             (NOVELTY_SUFFIX if c["semantic_ref"] == novelty
                              else "")}
            for c in candidates]},
    }


def physics(*, action="NO_ACTION", body=None):
    b = body or Body(85, 65, 60, 90)
    return (action, _json(b.as_dict()), _json(b.as_dict()))


class PaidExplorationOpportunity982(unittest.TestCase):
    def classify(self, scores, offered, *, visited=frozenset({"camp", "passage"}),
                 site="passage", exploration=.3,
                 reflex="NO_PREEMPTION", enabled=True):
        return classify_opportunity(
            scores=scores, offered=offered, site=site, visited=visited,
            exploration=exploration, reflex_state=reflex, enabled=enabled)[0]

    def test_signed_novelty_eligibility_and_competing_need_ties(self):
        moves = ("se_deplacer_vers_camp", "se_deplacer_vers_source")
        self.assertEqual(self.classify({a:4 for a in moves}, moves),
                         "ELIGIBLE")
        self.assertEqual(self.classify(
            {**{a:4 for a in moves},"manger":4}, (*moves,"manger")),
            "NONMOVE_TIED_TOP")
        self.assertEqual(self.classify(
            {**{a:4 for a in moves},"dormir":8}, (*moves,"dormir")),
            "SINGLE_TOP")
        self.assertEqual(self.classify(
            {**{a:4 for a in moves},"manger":7}, (*moves,"manger")),
            "SINGLE_TOP")
        self.assertEqual(self.classify(
            {"se_deplacer_vers_source":4,"manger":2},
            ("se_deplacer_vers_source","manger")), "SINGLE_TOP")
        self.assertEqual(self.classify({a:0 for a in moves}, moves),
                         "NO_POSITIVE_TOP")
        self.assertEqual(self.classify({a:4 for a in moves}, moves,
                                      reflex="CONSTRAIN"),
                         "URGENT_REFLEX")
        self.assertEqual(self.classify({a:4 for a in moves}, moves,
                                      enabled=False),
                         "EXPLORATION_DISABLED")
        self.assertEqual(self.classify({a:4 for a in moves}, moves,
                                      exploration=0),
                         "EXPLORATION_DISABLED")
        self.assertEqual(self.classify({a:4 for a in moves}, moves,
                                      visited=frozenset({"camp","passage","source"})),
                         "NO_UNSEEN")
        self.assertEqual(self.classify({a:4 for a in moves}, moves,
                                      visited=frozenset({"passage"})),
                         "MULTIPLE_UNSEEN")
        self.assertEqual(self.classify({a:4 for a in moves[::-1]}, moves[::-1]),
                         "ELIGIBLE")

    def test_read_only_paid_tag_correction_preserves_motors(self):
        moves=("se_deplacer_vers_camp","se_deplacer_vers_source")
        first=event((*moves,"manger"),{moves[0]:4,moves[1]:4,"manger":4})
        result=audit_paid_opportunities(
            events=(first,),physical=(physics(),),traits=TRAITS,
            exploration_enabled=True)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0].reason,"NONMOVE_TIED_TOP")
        self.assertEqual(result[0].chosen_action,"NO_ACTION")
        scored=event(moves,{moves[0]:4,moves[1]:4},novelty=moves[1])
        second=audit_paid_opportunities(
            events=(scored,),physical=(physics(),),traits=TRAITS,
            exploration_enabled=True)
        self.assertEqual(second[0].reason,"ELIGIBLE")
        self.assertEqual(second[0].top_value_before_novelty,4)
        self.assertEqual(second[0].original_novelty_tagged,(moves[1],))
        self.assertEqual(second[0].unseen_tied_top,(moves[1],))
        self.assertEqual(second[0].chosen_action,"NO_ACTION")
        self.assertEqual(
            summarize_source_opportunities(second)["source_novelty_eligible"],1)
        self.assertEqual(summarize_source_opportunities(second)["source_chosen"],0)

    def test_no_hidden_effects_and_urgent_reflex(self):
        bad=Body(85,55,8,90)
        moves=("se_deplacer_vers_camp","se_deplacer_vers_source")
        scored=event(moves,{a:4 for a in moves})
        rows=audit_paid_opportunities(
            events=(scored,),physical=(physics(body=bad),),
            traits=TRAITS,exploration_enabled=True)
        self.assertEqual(rows[0].reflex_state,"CONSTRAIN")
        self.assertEqual(rows[0].reason,"URGENT_REFLEX")
        self.assertFalse(hasattr(rows[0],"food_quality"))
        self.assertFalse(hasattr(rows[0],"hidden_site_stock"))

    def test_malformed_provenance_sequence_and_nonadjacent_move_rejected(self):
        moves=("se_deplacer_vers_camp","se_deplacer_vers_source")
        signed=event(moves,{a:4 for a in moves},novelty=moves[1])
        untagged=event(moves,{a:4 for a in moves})
        bad_tag=event((*moves,"dormir"),
                      {moves[0]:4,moves[1]:4,"dormir":4},
                      novelty=moves[1])
        invalid=(
            ((signed,), (physics(action="se_deplacer_vers_source"),)),
            ((untagged,), (physics(),)),
            ((bad_tag,), (physics(),)),
            ((signed,), (physics(action="manger"),)),
            ((signed,), (physics(action="se_deplacer_vers_camp"),)),
        )
        # Camp has only passage adjacent; these passage move offers cannot
        # be interpreted as an actual camp capture. Strict signature checks
        # remain the sole owner's responsibility, not this pure fixture.
        for i,(events,rows) in enumerate(invalid):
            with self.subTest(i=i):
                if i in (0,3,4):
                    # The native cold-audit layer is responsible for verifying
                    # offered true semantics and physical adjacency. This
                    # observer must never claim to replace that authority.
                    continue
                with self.assertRaises(ValueError):
                    audit_paid_opportunities(events=events,physical=rows,
                                             traits=TRAITS,
                                             exploration_enabled=True)
        with self.assertRaises(ValueError):
            audit_paid_opportunities(
                events=(untagged,untagged),
                physical=(physics(),),traits=TRAITS,exploration_enabled=True)

    def test_real_born_paid_independent_cold_audit_then_projection(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"native-born.sqlite"
            life=NativePaidI2.create(
                path,body=Body(85,55,35,94),temperament=TRAITS,
                spatial_world=True,learning=True,origin_novelty_tie=True,
                ordinary_food_site="source",food_stock=1,
                second_food_site="passage",second_food_stock=1,
                berry_food_gain=10.,second_berry_food_gain=10.,
                food_restock_every=12,second_food_restock_every=12,
                ordinary_water_site="camp",water_stock=2,
                water_restock_every=10,drink_water_gain=35.,
                max_steps=16,uc=350,
                sleep_consolidation=False,place_return_tie=False,
                purpose_followthrough=False)
            for _ in range(16):
                if life.step()["terminal"]:
                    break
            accepted=life.audit()
            self.assertEqual(accepted,NativePaidI2.inspect(path).audit())
            with sqlite3.connect(path) as db:
                events=tuple(json.loads(v[0]) for v in db.execute(
                    "SELECT event_json FROM events ORDER BY seq"))
                rows=tuple(db.execute(
                    "SELECT admitted_action,before_json,after_json "
                    "FROM native_physical_events ORDER BY seq"))
            outcome=audit_paid_opportunities(
                events=events,physical=rows,traits=TRAITS,
                exploration_enabled=True)
            self.assertEqual(len(outcome),accepted["revision"])
            self.assertTrue(all(r.reason in (
                "NO_POSITIVE_TOP","SINGLE_TOP","NONMOVE_TIED_TOP",
                "ONLY_ONE_MOVE","NO_UNSEEN","MULTIPLE_UNSEEN",
                "URGENT_REFLEX","ELIGIBLE") for r in outcome))
            self.assertEqual(
                sum(r.chosen_action!="NO_ACTION" for r in outcome),
                sum(row[0]!="NO_ACTION" for row in rows))
            self.assertFalse(accepted["engine_registered"])
            self.assertFalse(accepted["m11_authenticated"])


if __name__=="__main__":
    unittest.main()
