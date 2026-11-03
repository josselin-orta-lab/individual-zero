"""Prospectively frozen #924 independent born-life spatial return falsifier.

No scripted motor, hidden gains, retrospective score tuning, or
premature scientific claim from a candidate-value change.
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
from i2.modules.native_spatial_world import BORN_SITE, destination, site_after
from i2.runtime.native_paid_cycle import (
    NativePaidI2, PLACE_RETURN_EVIDENCE, NO_ACTION
)


class LivedPlaceReturnCohort924(unittest.TestCase):
    TICKS = 24
    TRAITS = BirthTemperament(0,.5,.3,0,0)

    def test_same_life_visited_source_return_or_report_falsifier(self):
        results = {}
        histories = {}
        with tempfile.TemporaryDirectory() as tmp:
            for gain in (0.0,40.0):
                for enabled in (False,True):
                    key = ("beneficial" if gain else "ineffective") + (
                        ":remembered" if enabled else ":baseline")
                    with self.subTest(cell=key):
                        path = Path(tmp)/(key.replace(":","-")+".sqlite")
                        life = NativePaidI2.create(
                            path, body=Body(85,90,35,100),
                            temperament=self.TRAITS, uc=300,
                            max_steps=self.TICKS, spatial_world=True,
                            ordinary_water_site="camp",
                            place_return_tie=enabled, learning=True,
                            evidence_tie_exploration=False,
                            sleep_consolidation=False,
                            food_stock=0, water_stock=2,
                            water_restock_every=0,
                            drink_water_gain=gain)
                        born = life.audit()
                        for _ in range(self.TICKS):
                            state = life.step()
                            if state["terminal"]:
                                break
                        final = life.audit()
                        self.assertEqual(NativePaidI2.inspect(path).audit(),final)
                        self.assertFalse(final["engine_registered"])
                        self.assertFalse(final["m11_authenticated"])
                        self.assertEqual(final["scientific_verdict"],"NOT_ESTABLISHED")
                        with sqlite3.connect(path) as db:
                            phys = list(db.execute(
                                "SELECT admitted_action,before_json,after_json "
                                "FROM native_physical_events ORDER BY seq"))
                            events = [json.loads(t[0]) for t in db.execute(
                                "SELECT event_json FROM events ORDER BY seq")]
                        self.assertEqual(len(phys),final["revision"])
                        self.assertEqual(len(events),final["revision"])
                        site = BORN_SITE
                        initial_contact = None
                        first_departure = None
                        first_return = None
                        had_satisfied_water = False
                        thirst_recurred_at = None
                        records = []
                        for tick,((action,bef,aft),event) in enumerate(
                                zip(phys,events),start=1):
                            pre_site = site
                            before,after=json.loads(bef),json.loads(aft)
                            claims=set(event["claim"]["subjective_evidence_refs"])
                            offers=set(event["claim"]["capture"][
                                "accessible_semantics"])
                            self.assertIn(
                                "evidence:i2:spatial:current:"+site,claims)
                            self.assertEqual("boire" in offers,
                                site=="camp" and
                                sum(a=="boire" for a,_,_ in phys[:tick-1])<2)
                            if action=="boire":
                                self.assertEqual(site,"camp")
                                self.assertAlmostEqual(after["water"],
                                    min(100,max(0,before["water"]-.4)+gain))
                                if initial_contact is None:
                                    initial_contact=tick
                            if before["water"]>=70:
                                had_satisfied_water=True
                            if (had_satisfied_water and before["water"]<70
                                    and thirst_recurred_at is None):
                                thirst_recurred_at=tick
                            dst=destination(action)
                            if dst is not None:
                                if (site=="camp" and
                                        first_departure is None):
                                    first_departure=tick
                                if (dst=="camp" and
                                        first_departure is not None and
                                        first_return is None):
                                    first_return=tick
                                site=site_after(site,action)
                            advice=event["advice"]
                            frame=event["frame"]
                            value={}
                            if advice is not None and frame is not None:
                                ids={c["candidate_ref"]:c["semantic_ref"]
                                     for c in frame["candidates"]}
                                value={ids[v["candidate_ref"]]:
                                    {"value":v["value"],
                                     "provenance":v["evidence_ref"]}
                                    for v in advice["values"]}
                            records.append({
                                "tick":tick,"site_before":pre_site,
                                "action":action,"water_before":before["water"],
                                "water_after":after["water"],
                                "scores":value,
                                "subjective":sorted(claims)})
                        self.assertEqual(site,final["site"])
                        histories[(gain,enabled)]=(phys,events,records)
                        genuine_return = bool(
                            gain > 0 and initial_contact is not None and
                            first_departure is not None and
                            first_return is not None and
                            thirst_recurred_at is not None and
                            initial_contact < first_departure <
                            thirst_recurred_at <= first_return and
                            records[first_return-1]["site_before"]=="passage" and
                            records[first_return-1]["water_before"] < 70 and
                            any(a=="boire" and json.loads(aft)["water"] >
                                json.loads(bef)["water"]
                                for a,bef,aft in phys[:initial_contact]))
                        # Do not label an unexposed bodily/locomotion
                        # prerequisite as a failed *learned decision*.
                        if initial_contact is None:
                            eligible="NO_PERSONAL_RESOURCE_CONTACT"
                        elif gain > 0 and not any(
                                a=="boire" and json.loads(aft)["water"] >
                                json.loads(bef)["water"]
                                for a,bef,aft in phys[:initial_contact]):
                            eligible="NO_PERSONAL_RESTORATION"
                        elif first_departure is None:
                            eligible="NO_DEPARTURE_FROM_KNOWN_SITE"
                        elif thirst_recurred_at is None:
                            eligible="NEED_NOT_RECURRED_AT_HORIZON"
                        elif first_return is None:
                            eligible="RECURRED_NEED_NO_PHYSICAL_RETURN"
                        elif genuine_return:
                            eligible="PAID_RETURN_AFTER_RECURRENT_NEED"
                        else:
                            eligible="RETURN_WITHOUT_REQUIRED_NEED_ORDER"
                        results[key]={
                            "exposure_class":eligible,
                            "genuine_need_return":genuine_return,
                            "ticks":final["revision"],
                            "censor":"TERMINAL" if final["terminal"] else
                                     "HORIZON_CENSORED",
                            "first_contact":initial_contact,
                            "first_departure":first_departure,
                            "first_return":first_return,
                            "thirst_recurred_at":thirst_recurred_at,
                            "water_final":round(final["body"]["water"],4),
                            "uc_spent":born["remaining_uc"]-
                                       final["remaining_uc"],
                            "actions":[r[0] for r in phys],
                            "place_memory_used":any(
                                PLACE_RETURN_EVIDENCE in v["provenance"]
                                for row in records for v in row["scores"].values()),
                            "memory_provenance_events":[{
                                "tick":row["tick"],
                                "site":row["site_before"],
                                "chosen":row["action"],
                                "remembered_scores":{
                                    name:value["value"]
                                    for name,value in row["scores"].items()
                                    if PLACE_RETURN_EVIDENCE in value["provenance"]}}
                                for row in records if any(
                                PLACE_RETURN_EVIDENCE in v["provenance"]
                                for v in row["scores"].values())],
                            "cold_audit":"PASS"}
            for enabled in (False,True):
                bad=histories[(0.0,enabled)]
                good=histories[(40.0,enabled)]
                before_contact=0
                for x,y in zip(bad[0],good[0]):
                    if x!=y:
                        break
                    before_contact+=1
                if before_contact < min(len(bad[0]),len(good[0])):
                    self.assertEqual(bad[0][before_contact][0],"boire")
                    self.assertEqual(good[0][before_contact][0],"boire")
                results[":quality-identifiability:"+str(enabled)]={
                    "same_physical_prefix":before_contact,
                    "first_quality_exposure":(
                        before_contact+1 if before_contact<
                        min(len(bad[0]),len(good[0])) else None)}
            for gain in (0.0,40.0):
                innate=histories[(gain,False)]
                learned=histories[(gain,True)]
                prefix=0
                for a,b in zip(innate[0],learned[0]):
                    if a!=b:
                        break
                    prefix+=1
                diverged=(prefix<min(len(innate[0]),len(learned[0])))
                if diverged:
                    left,right=innate[1][prefix],learned[1][prefix]
                    self.assertEqual(
                        left["claim"]["subjective_evidence_refs"],
                        right["claim"]["subjective_evidence_refs"])
                    self.assertEqual(
                        left["claim"]["capture"]["accessible_semantics"],
                        right["claim"]["capture"]["accessible_semantics"])
                    self.assertEqual(
                        innate[0][prefix][1],learned[0][prefix][1])
                results[":learning-difference:"+str(gain)]={
                    "first_motor_or_physical_difference":prefix+1 if diverged else None,
                    "matched_physical_prefix":prefix,
                    "interpretation":"NO_DIFFERENCE" if not diverged else
                        "DIVERGENT_CHOICE_CAUSAL_REVIEW_REQUIRED"}
            print("I2_NATIVE_PLACE_RETURN_P2_924="+json.dumps(
                results,sort_keys=True,separators=(",",":")),flush=True)


if __name__ == "__main__":
    unittest.main()
