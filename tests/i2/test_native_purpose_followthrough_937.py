"""P2 #937 purpose continuity: only actually paid, evidenced return handoff.

Read-only physical fixtures are NOT autonomous proof. Native local lives
choose every motor through the existing paid Competition/Action Control.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_owner_support import _json
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, PLACE_RETURN_EVIDENCE,
    PURPOSE_HANDOFF_EVIDENCE, personally_paid_arrival_purpose,
)


TRAITS = BirthTemperament(0,.5,.3,0,0)
DRINK_BEFORE = Body(85,90,35,100)
DRINK_AFTER = Body(84.5,89.8,74.6,100)
ARRIVAL_BODY = Body(82,89.5,69.4,100)


def physical(seq, action, before=DRINK_BEFORE, after=DRINK_AFTER):
    return (seq,"capture:"+str(seq),action,0.0,
            _json(before.as_dict()),_json(after.as_dict()),0)


def claim(*offered):
    return SimpleNamespace(capture=SimpleNamespace(
        accessible_semantics=tuple(offered)))


def prior_event(*, value=5, remembered=True, action="se_deplacer_vers_camp"):
    return {
        "frame":{"candidates":[
            {"candidate_ref":"chosen-move", "semantic_ref":action}]},
        "advice":{"values":[{"candidate_ref":"chosen-move",
                             "value":value,
                             "evidence_ref":("chosen:paid"+PLACE_RETURN_EVIDENCE
                              if remembered else "chosen:paid:native-body")}]},
        "control_review":{"status":"REVIEWED_NOT_ADMITTED",
                          "suggested_candidate_ref":"chosen-move"},
    }


class NativePurposeFollowthrough937(unittest.TestCase):
    SCORES={"boire":2,"se_deplacer_vers_passage":6,"attendre":1}
    HISTORY=(physical(1,"boire"),
             physical(2,"se_deplacer_vers_passage",
                      DRINK_AFTER,Body(82.5,89.6,74.2,100)),
             physical(3,"se_deplacer_vers_camp",
                      Body(82.5,89.6,69.8,100),
                      ARRIVAL_BODY))

    def handoff(self, *, rows=None, prior=None, body=ARRIVAL_BODY,
                scores=None, offered=None, learning=True, enabled=True):
        return personally_paid_arrival_purpose(
            scores if scores is not None else self.SCORES,
            claim=claim(*(offered if offered is not None
                          else ("boire","se_deplacer_vers_passage","attendre"))),
            body=body,traits=TRAITS,
            previous=self.HISTORY if rows is None else rows,
            prior_event=prior_event() if prior is None else prior,
            learning=learning,enabled=enabled)

    def test_only_committed_visited_positively_evidenced_arrival_carries(self):
        values,credited=self.handoff()
        self.assertEqual(values["boire"],5)
        self.assertEqual(values["se_deplacer_vers_passage"],6)
        self.assertEqual(credited,frozenset(("boire",)))
        # Exactly the previous paid candidate value, no new +N calibration.
        values,_=self.handoff(prior=prior_event(value=8))
        self.assertEqual(values["boire"],8)

    def test_no_transferred_goal_without_real_need_access_provenance(self):
        absent=(
            {"learning":False},{"enabled":False},
            {"body":Body(82,90,90,100)},
            {"offered":("se_deplacer_vers_passage","attendre")},
            {"prior":prior_event(remembered=False)},
            {"prior":prior_event(action="se_deplacer_vers_source")},
            {"prior":prior_event(value=0)},
            {"rows":self.HISTORY[:-1]},
            {"rows":(physical(1,"boire",DRINK_BEFORE,DRINK_BEFORE),
                     *self.HISTORY[1:])},
        )
        for kwargs in absent:
            with self.subTest(kwargs=repr(kwargs)[:140]):
                values,credited=self.handoff(**kwargs)
                self.assertEqual(values,self.SCORES)
                self.assertEqual(credited,frozenset())
        # Inactive handoff cannot self-revive on a later nonmovement cycle.
        stale=(*self.HISTORY, physical(4,"attendre",ARRIVAL_BODY,ARRIVAL_BODY))
        self.assertEqual(self.handoff(rows=stale)[1],frozenset())
        # A different preferred action still competes at the unchanged score.
        values,credited=self.handoff(scores={
            **self.SCORES,"se_deplacer_vers_passage":10})
        self.assertEqual(credited,frozenset(("boire",)))
        self.assertEqual(values["se_deplacer_vers_passage"],10)

    def test_new_birth_gate_and_no_script_native_ablation(self):
        with tempfile.TemporaryDirectory() as directory:
            outcomes={}
            for enabled in (False,True):
                for gain in (0.0,40.0):
                    name="on" if enabled else "off"
                    name+=("-useful" if gain else "-ineffective")
                    path=Path(directory)/(name+".sqlite")
                    life=NativePaidI2.create(
                        path,body=Body(85,90,35,100),
                        temperament=TRAITS,
                        uc=300,max_steps=24,spatial_world=True,
                        ordinary_water_site="camp",
                        place_return_tie=True,
                        purpose_followthrough=enabled,
                        learning=True,evidence_tie_exploration=False,
                        sleep_consolidation=False,food_stock=0,
                        water_stock=2,water_restock_every=0,
                        drink_water_gain=gain)
                    born=life.audit()
                    for _ in range(24):
                        state=life.step()
                        if state["terminal"]:
                            break
                    final=life.audit()
                    self.assertEqual(NativePaidI2.inspect(path).audit(),final)
                    with sqlite3.connect(path) as db:
                        actions=[a for (a,) in db.execute(
                            "SELECT admitted_action FROM native_physical_events "
                            "ORDER BY seq")]
                        events=[json.loads(a) for (a,) in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    credited=[]
                    for tick,event in enumerate(events,1):
                        if not event["advice"]:
                            continue
                        candidates={c["candidate_ref"]:c["semantic_ref"]
                                    for c in event["frame"]["candidates"]}
                        credited.extend((tick,candidates[v["candidate_ref"]],
                                         v["value"])
                            for v in event["advice"]["values"]
                            if PURPOSE_HANDOFF_EVIDENCE in v["evidence_ref"])
                    outcomes[name]={
                        "actions":actions,
                        "credited":credited,
                        "water":round(final["body"]["water"],4),
                        "uc_spent":born["remaining_uc"]-
                                   final["remaining_uc"],
                        "cold_audit":"PASS"}
                    self.assertEqual(final["scientific_verdict"],
                                     "NOT_ESTABLISHED")
                    if not enabled or not gain:
                        self.assertEqual(credited,[])
            with self.assertRaises(NativeRefusal):
                NativePaidI2.create(
                    Path(directory)/"illegal.sqlite",body=DRINK_BEFORE,
                    temperament=TRAITS,purpose_followthrough=True)
            print("I2_NATIVE_PURPOSE_FOLLOWTHROUGH_937="+json.dumps(
                outcomes,sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    unittest.main()
