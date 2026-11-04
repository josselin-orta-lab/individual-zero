"""P2 v22: pure need-conditioned multi-channel tie and real paid life tests.

Pure examples are not motor decisions or evidence of adaptation. The born
cohort is exploratory, source-frozen, never tuned after reading the result.
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
from i2.modules.native_place_experience import LivedWholeBodySiteConsequence
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal,
    whole_body_site_relevance, whole_body_site_tie_scores,
)

TRAITS = BirthTemperament(0, .5, .3, 0, 0)
MOTION = {"toward_a": "passage", "toward_b": "source"}
TIED = {"toward_a": 4, "toward_b": 4, "sleep": 2}


def lived(site, *, food, integrity, seq):
    return LivedWholeBodySiteConsequence(
        seq, site, "manger", (80., 55., 65., 90.),
        (79.5, 55. + food, 64.6, 90. + integrity),
        (-.5, food, -.4, integrity), (.0, .2, .1, .1))


class WholeBodyPlaceTieV22(unittest.TestCase):
    def test_multichannel_effect_changes_with_current_need(self):
        evidence = (lived("passage", food=12., integrity=-12., seq=2),
                    lived("source", food=12., integrity=0., seq=5))
        hungry = whole_body_site_relevance(
            evidence, body=Body(85., 40., 65., 100.), traits=TRAITS)
        fragile = whole_body_site_relevance(
            evidence, body=Body(85., 95., 65., 55.), traits=TRAITS)
        self.assertGreater(hungry["source"], hungry["passage"])
        self.assertGreater(fragile["source"], fragile["passage"])
        self.assertGreater(hungry["passage"], fragile["passage"])
        self.assertGreater(hungry["source"], fragile["source"])
        self.assertEqual(set(hungry), {"passage", "source"})
        self.assertEqual(whole_body_site_relevance(
            (), body=Body(85.,40.,65.,55.),traits=TRAITS), {})

    def test_pure_tie_is_name_symmetric_and_does_not_force_motor(self):
        effects = {"passage": 2., "source": 5.}
        got, evidence = whole_body_site_tie_scores(
            TIED, offered=tuple(TIED), destinations=MOTION,
            effects=effects, reflex_state="NO_PREEMPTION", enabled=True)
        self.assertEqual(got, {"toward_a":4,"toward_b":5,"sleep":2})
        self.assertEqual(evidence, frozenset({"toward_b"}))
        rotated, credited = whole_body_site_tie_scores(
            TIED, offered=tuple(TIED),
            destinations={"toward_a":"source","toward_b":"passage"},
            effects=effects, reflex_state="NO_PREEMPTION", enabled=True)
        self.assertEqual(rotated, {"toward_a":5,"toward_b":4,"sleep":2})
        self.assertEqual(credited, frozenset({"toward_a"}))
        for reflex in ("CONSTRAIN","PREEMPT"):
            self.assertEqual(whole_body_site_tie_scores(
                TIED, offered=tuple(TIED), destinations=MOTION, effects=effects,
                reflex_state=reflex, enabled=True), (TIED, frozenset()))
        self.assertEqual(whole_body_site_tie_scores(
            TIED, offered=tuple(TIED), destinations=MOTION, effects=effects,
            reflex_state="NO_PREEMPTION", enabled=False), (TIED, frozenset()))

    def test_unknown_negative_equal_and_without_top_tie(self):
        variants = (
            ({}, TIED),
            ({"source":-1., "passage":-2.}, TIED),
            ({"source":1., "passage":1.}, TIED),
            ({"source":2.}, {"toward_a":2,"toward_b":1,"sleep":3}),
            ({"source":5.}, {"toward_a":0,"toward_b":0,"sleep":0}),
        )
        for effects,scores in variants:
            with self.subTest(effects=effects,scores=scores):
                self.assertEqual(whole_body_site_tie_scores(
                    scores, offered=tuple(scores), destinations=MOTION,
                    effects=effects, reflex_state="NO_PREEMPTION",
                    enabled=True),(scores,frozenset()))
        with self.assertRaises(NativeRefusal):
            whole_body_site_tie_scores(
                TIED, offered=tuple(TIED), destinations=MOTION,
                effects={"source":1.},reflex_state="NO_PREEMPTION",enabled=1)

    def test_born_flag_exact_and_immutable_cold_tamper(self):
        with tempfile.TemporaryDirectory() as root:
            base=dict(body=Body(85,55,35,100),temperament=TRAITS,
                      learning=True,spatial_world=True,
                      place_return_tie=True,whole_body_place_tie=True,
                      purpose_followthrough=False,max_steps=3,uc=100)
            invalid=(
                {"whole_body_place_tie":1},
                {"whole_body_place_tie":"true"},
                {"learning":False},
                {"spatial_world":False},
                {"place_return_tie":False},
                {"purpose_followthrough":True},
            )
            for i,override in enumerate(invalid):
                with self.subTest(case=i),self.assertRaises(NativeRefusal):
                    NativePaidI2.create(
                        Path(root)/("invalid"+str(i)+".sqlite"),
                        **{**base,**override})
            path=Path(root)/"valid.sqlite"
            life=NativePaidI2.create(path,**base)
            for _ in range(3):
                if life.step()["terminal"]:
                    break
            self.assertEqual(life.audit(),NativePaidI2.inspect(path).audit())
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute(
                    "SELECT whole_body_place_tie FROM native_genesis"
                ).fetchone(), (1,))
                db.execute("UPDATE native_genesis SET whole_body_place_tie=0")
            with self.assertRaises(NativeRefusal):
                NativePaidI2.inspect(path)

    def test_separate_born_paid_learning_lives_not_pure_motor_fixtures(self):
        report={}
        with tempfile.TemporaryDirectory() as root:
            for injury_site in ("passage","source"):
                for enabled in (False,True):
                    key=injury_site+("-whole" if enabled else "-target")
                    path=Path(root)/(key+".sqlite")
                    life=NativePaidI2.create(
                        path,body=Body(85,55,35,100),temperament=TRAITS,
                        learning=True,spatial_world=True,
                        place_return_tie=True,whole_body_place_tie=enabled,
                        origin_novelty_tie=True,
                        purpose_followthrough=False,
                        contextual_movement_credit=True,
                        target_food_credit_enabled=False,
                        evidence_tie_exploration=False,
                        sleep_consolidation=False,
                        ordinary_food_site="source",
                        second_food_site="passage",
                        berry_food_gain=12.,
                        berry_integrity_delta=(-12. if injury_site=="source" else 0.),
                        second_berry_food_gain=12.,
                        second_berry_integrity_delta=(-12. if injury_site=="passage" else 0.),
                        food_stock=1,second_food_stock=1,
                        food_restock_every=8,second_food_restock_every=8,
                        ordinary_water_site="camp",water_stock=2,
                        water_restock_every=8,drink_water_gain=40.,
                        max_steps=64,uc=850)
                    begin=life.audit()
                    for _ in range(64):
                        if life.step()["terminal"]:
                            break
                    finish=life.audit()
                    self.assertEqual(finish,NativePaidI2.inspect(path).audit())
                    with sqlite3.connect(path) as db:
                        events=[json.loads(row[0]) for row in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                        actions=[row[0] for row in db.execute(
                            "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
                    self.assertEqual(len(actions),finish["revision"])
                    tags=[i+1 for i,e in enumerate(events)
                          if any(":lived-whole-body-site-need-relevance" in
                                 v["evidence_ref"] for v in
                                 (e.get("advice") or {}).get("values",()))]
                    if not enabled:
                        self.assertEqual(tags,[])
                    report[key]={
                        "revision":finish["revision"],
                        "terminal":finish["terminal"],
                        "right_censored":finish["revision"]==64
                                        and not finish["terminal"],
                        "body":finish["body"],"site":finish["site"],
                        "uc_spent":begin["remaining_uc"]-finish["remaining_uc"],
                        "actions":actions,"whole_body_evidence_ticks":tags,
                        "cold_audit":"PASS"}
            for site in ("passage","source"):
                off,on=report[site+"-target"],report[site+"-whole"]
                first=next((i+1 for i,(a,b) in enumerate(
                    zip(off["actions"],on["actions"])) if a!=b),None)
                report[site+"-comparison"]={"first_motor_divergence":first}
            print("I2_P2_WHOLE_BODY_SITE_TIE_V22="+json.dumps(
                report,sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    unittest.main()
