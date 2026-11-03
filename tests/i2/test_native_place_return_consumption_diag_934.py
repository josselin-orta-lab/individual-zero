"""#934: native same-life diagnostic of drink-vs-move at a remembered site.

Post-hoc **instrumentation only** of the source-locked #933 useful-water
cell. Never force motors, reconfigure the birth or alter scores. The frozen
#933 scientific outcome lives in its own historical file and CI logs.
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
from i2.modules.native_physiological_needs import assess_needs
from i2.modules.native_spatial_world import BORN_SITE, destination, site_after
from i2.runtime.native_paid_cycle import NativePaidI2, PLACE_RETURN_EVIDENCE


class NativePlaceReturnConsumptionDiagnostic934(unittest.TestCase):
    def test_actual_at_site_candidate_competition_and_stocks(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "native-diagnostic.db"
            traits = BirthTemperament(0, .5, .3, 0, 0)
            life = NativePaidI2.create(
                path, body=Body(85,90,35,100), temperament=traits,
                uc=300, max_steps=24, spatial_world=True,
                ordinary_water_site="camp", place_return_tie=True,
                learning=True, evidence_tie_exploration=False,
                sleep_consolidation=False, food_stock=0, water_stock=2,
                water_restock_every=0, drink_water_gain=40.0)
            initial = life.audit()
            for _ in range(24):
                state = life.step()
                if state["terminal"]:
                    break
            state = life.audit()
            self.assertEqual(NativePaidI2.inspect(path).audit(), state)
            with sqlite3.connect(path) as conn:
                actions = list(conn.execute(
                    "SELECT admitted_action,before_json,after_json "
                    "FROM native_physical_events ORDER BY seq"))
                events = [json.loads(x[0]) for x in conn.execute(
                    "SELECT event_json FROM events ORDER BY seq")]
            site = BORN_SITE
            drunk = 0
            site_trace = []
            return_tick = None
            for tick, ((action, before_raw, after_raw), event) in enumerate(
                    zip(actions, events), 1):
                before = Body(**json.loads(before_raw))
                pressure = assess_needs(before, traits).pressures["water"]
                available = max(0, 2 - drunk)
                offered = event["claim"]["capture"]["accessible_semantics"]
                self.assertEqual(
                    "boire" in offered, site == "camp" and available > 0)
                frame, advice = event["frame"], event["advice"]
                values = {}
                if frame is not None and advice is not None:
                    semantic = {c["candidate_ref"]: c["semantic_ref"]
                                for c in frame["candidates"]}
                    values = {semantic[v["candidate_ref"]]:
                              {"value":v["value"],
                               "evidence_ref":v["evidence_ref"]}
                              for v in advice["values"]}
                dest = destination(action)
                if dest is not None:
                    next_site = site_after(site, action)
                    if next_site == "camp" and tick > 2 and return_tick is None:
                        return_tick = tick
                else:
                    next_site = site
                if site == "camp" or (dest == "camp"):
                    site_trace.append({
                        "tick":tick, "site_before":site,
                        "site_after":next_site,
                        "action":action, "water":round(before.water,3),
                        "water_need_pressure":round(pressure,6),
                        "remaining_water_stock":available,
                        "boire_offered":"boire" in offered,
                        "boire_value":values.get("boire"),
                        "move_values":{
                            key:value for key,value in values.items()
                            if key.startswith("se_deplacer_vers_")},
                        "advice_status":advice["status"] if advice else None,
                        "control_status":(event["control_review"] or {}).get("status"),
                        "memory_active":any(
                            PLACE_RETURN_EVIDENCE in v["evidence_ref"]
                            for v in values.values())})
                if action == "boire":
                    self.assertEqual(site, "camp")
                    self.assertGreater(available, 0)
                    drunk += 1
                site = next_site
            # These checks are about data provenance, not an assertion that
            # every strategy should succeed. Do not assert "no drink".
            self.assertEqual(site, state["site"])
            self.assertEqual(len(actions), state["revision"])
            self.assertGreater(len(site_trace), 0)
            print("I2_NATIVE_CAMP_DECISION_DIAG_934=" +
                  json.dumps({
                      "source":"posthoc_diagnostic_of_frozen_933_world",
                      "actual_actions":[a for a,_,_ in actions],
                      "first_return":return_tick,
                      "site_decisions":site_trace,
                      "remaining_stock":2-drunk,
                      "water_final":state["body"]["water"],
                      "uc_spent":initial["remaining_uc"] -
                                 state["remaining_uc"],
                      "cold_audit":"PASS",
                      "scientific_verdict":"NOT_ESTABLISHED",
                  },sort_keys=True,separators=(",",":")), flush=True)


if __name__ == "__main__":
    unittest.main()
