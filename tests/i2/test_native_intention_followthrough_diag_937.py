"""#937: read-only audit of real native semantic intent after a learned return.

This test does not modify scores, re-open intent, command motor or claim
memory-enabled ecological benefit. It exposes existing committed owner state.
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
from i2.runtime.native_paid_cycle import NativePaidI2


class NativeIntentionFollowthroughDiagnostic937(unittest.TestCase):
    def test_same_born_physics_and_intention_owner_timeline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"native-intent.db"
            life = NativePaidI2.create(
                path, body=Body(85,90,35,100),
                temperament=BirthTemperament(0,.5,.3,0,0),
                uc=300, max_steps=24, spatial_world=True,
                ordinary_water_site="camp", place_return_tie=True,
                learning=True, evidence_tie_exploration=False,
                sleep_consolidation=False, food_stock=0,
                water_stock=2, water_restock_every=0,
                drink_water_gain=40.0)
            born = life.audit()
            for _ in range(24):
                state = life.step()
                if state["terminal"]:
                    break
            final = life.audit()
            self.assertEqual(NativePaidI2.inspect(path).audit(), final)
            with sqlite3.connect(path) as db:
                chosen = [r[0] for r in db.execute(
                    "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
                data = [json.loads(r[0]) for r in db.execute(
                    "SELECT event_json FROM events ORDER BY seq")]
            self.assertEqual(len(data),len(chosen))
            site=BORN_SITE
            timeline=[]
            for tick,(action,event) in enumerate(zip(chosen,data),1):
                pre=site
                current=event["owner_snapshot"]["current"]
                owner=event["owner_snapshot"]
                cap=event["claim"]["capture"]
                frame=event["frame"] or {}
                advice=event["advice"] or {}
                semantics={x["candidate_ref"]:x["semantic_ref"]
                           for x in frame.get("candidates",[])}
                candidate_values={
                    semantics[v["candidate_ref"]]:v["value"]
                    for v in advice.get("values",[])}
                if destination(action) is not None:
                    site=site_after(site,action)
                timeline.append({
                    "tick":tick,
                    "capture_step":cap["step"],
                    "pre_site":pre,"post_site":site,
                    "intent_transition":event["intention_kind"],
                    "semantic":current["semantic_ref"] if current else None,
                    "intent_goal":current["goal_ref"] if current else None,
                    "intent_status":current["status"] if current else None,
                    "expiry":current["expires_at_step"] if current else None,
                    "water_offered":"boire" in cap["accessible_semantics"],
                    "drink_score":candidate_values.get("boire"),
                    "movement_scores":{
                        k:v for k,v in candidate_values.items()
                        if k.startswith("se_deplacer_vers_")},
                    "choice":action,
                })
                self.assertEqual(owner["last_step"],cap["step"])
            self.assertEqual(site,final["site"])
            self.assertEqual(timeline[0]["semantic"],"boire")
            self.assertEqual(timeline[0]["intent_transition"],"opened")
            self.assertEqual(timeline[0]["expiry"],74)
            # A fixed semantic-ref with a short TTL is not an enduring
            # bodily-purpose plan. Claiming it persists at returned camp
            # would be a false scientific diagnosis.
            self.assertIsNone(timeline[13]["semantic"])
            self.assertIsNone(timeline[14]["semantic"])
            self.assertTrue(timeline[14]["water_offered"])
            self.assertEqual(timeline[14]["choice"],"se_deplacer_vers_passage")
            self.assertEqual(timeline[14]["drink_score"],2)
            self.assertEqual(
                timeline[14]["movement_scores"]["se_deplacer_vers_passage"],6)
            self.assertEqual(
                [x["tick"] for x in timeline if x["intent_transition"]=="expired"],
                [9])
            self.assertEqual(final["scientific_verdict"],"NOT_ESTABLISHED")
            print("I2_NATIVE_INTENT_FOLLOWTHROUGH_937="+json.dumps({
                "born_config":"same as frozen useful-water ON arm of #933",
                "initial_expiry_capture_step":74,
                "first_intent_expiry_tick":9,
                "returned_camp_tick":14,
                "post_return_competition_tick":15,
                "semantic_at_return":timeline[13]["semantic"],
                "semantic_at_camp":timeline[14]["semantic"],
                "timeline":timeline,
                "uc_spent":born["remaining_uc"]-final["remaining_uc"],
                "water_final":final["body"]["water"],
                "cold_audit":"PASS",
                "scientific_verdict":"NOT_ESTABLISHED",
            },sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    unittest.main()
