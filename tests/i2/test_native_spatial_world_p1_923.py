"""P1 minimum physical space, provenance and native paid motor integration.

Physics-only route checks are NOT claimed as autonomously chosen behavior.
No site payoffs, no I1 imports, no migration of prior born research lives.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body, transition
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_spatial_world import (
    GRAPH, BORN_SITE, MOTIONS, destination, site_after, offered_moves,
    replay_site, local_evidence,
)
from i2.runtime.native_paid_cycle import NativePaidI2, NativeRefusal, NO_ACTION


class I2MinimalSpatialWorldP1(unittest.TestCase):
    TRAITS = BirthTemperament(0, 0.5, 1.0, 0, 0)
    BODY = Body(85, 90, 70, 100)

    def test_physics_only_adjacency_roundtrip_and_negative_routes(self):
        self.assertEqual(tuple(GRAPH), ("camp", "passage", "source"))
        self.assertEqual(offered_moves("camp"), ("se_deplacer_vers_passage",))
        self.assertEqual(
            offered_moves("passage"),
            ("se_deplacer_vers_camp", "se_deplacer_vers_source"))
        self.assertEqual(offered_moves("source"), ("se_deplacer_vers_passage",))
        place = BORN_SITE
        for action, expected in (
            ("se_deplacer_vers_passage", "passage"),
            ("se_deplacer_vers_source", "source"),
            ("se_deplacer_vers_passage", "passage"),
            ("se_deplacer_vers_camp", "camp"),
        ):
            place = site_after(place, action)
            self.assertEqual(place, expected)
        self.assertEqual(place, "camp")
        self.assertEqual(
            transition(self.BODY, "se_deplacer").body.energy, 83)
        for action in ("se_deplacer_vers_source", "se_deplacer_vers_camp",
                       "se_deplacer_vers_hidden", "boire"):
            with self.assertRaises(ValueError):
                site_after("camp", action)
        with self.assertRaises(ValueError):
            offered_moves("hidden")
        self.assertEqual(destination("se_deplacer_vers_source"), "source")
        self.assertIsNone(destination("manger"))
        self.assertEqual(local_evidence("camp"),
            ("evidence:i2:spatial:current:camp",
             "evidence:i2:spatial:neighbor:passage"))

    def test_unaffordable_move_is_never_offered_or_executed(self):
        # A move at energy 1 would otherwise clamp to zero and spend less
        # than its declared two-energy physical price.
        with tempfile.TemporaryDirectory() as directory:
            life = NativePaidI2.create(
                Path(directory) / "low-energy.db",
                body=Body(1.0, 90, 70, 100),
                temperament=self.TRAITS, spatial_world=True, max_steps=3,
                uc=80, learning=False, food_stock=0, water_stock=0)
            first = life.step()
            self.assertEqual(first["site"], "camp")
            with sqlite3.connect(life.path) as db:
                event = json.loads(db.execute(
                    "SELECT event_json FROM events WHERE seq=1").fetchone()[0])
                self.assertFalse(set(event["claim"]["capture"][
                    "accessible_semantics"]) & set(MOTIONS))
                self.assertEqual(db.execute(
                    "SELECT admitted_action FROM native_physical_events "
                    "WHERE seq=1").fetchone()[0] in MOTIONS, False)
            self.assertEqual(NativePaidI2.inspect(life.path).audit(),
                             life.audit())

    def test_replayed_position_is_only_from_committed_movements(self):
        rows = (
            (1, "cap1", "attendre"),
            (2, "cap2", "se_deplacer_vers_passage"),
            (3, "cap3", "dormir"),
            (4, "cap4", "se_deplacer_vers_source"),
            (5, "cap5", "se_deplacer_vers_passage"),
            (6, "cap6", "se_deplacer_vers_camp"))
        self.assertEqual(replay_site(rows, enabled=True), "camp")
        self.assertEqual(replay_site(rows[:4], enabled=True), "source")
        self.assertEqual(replay_site(rows[:1], enabled=True), "camp")
        with self.assertRaises(ValueError):
            replay_site(rows, enabled=False)
        with self.assertRaises(ValueError):
            replay_site(((1,"cap","se_deplacer_vers_source"),), enabled=True)
        with self.assertRaises(ValueError):
            replay_site((), enabled=1)

    def test_opt_in_birth_and_no_script_choices_are_paid_and_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            outcomes = {}
            for enabled in (False, True):
                path = Path(directory) / ("spatial.db" if enabled else "legacy.db")
                life = NativePaidI2.create(
                    path, body=self.BODY, temperament=self.TRAITS,
                    max_steps=12, uc=260, learning=False,
                    sleep_consolidation=False, evidence_tie_exploration=False,
                    spatial_world=enabled, water_stock=0, food_stock=0)
                before = life.audit()
                self.assertEqual(before["site"], "camp" if enabled else None)
                for _ in range(12):
                    try:
                        state = life.step()
                    except NativeRefusal:
                        break
                    if state["terminal"]:
                        break
                after = life.audit()
                self.assertEqual(NativePaidI2.inspect(path).audit(), after)
                with sqlite3.connect(path) as db:
                    physical = list(db.execute(
                        "SELECT admitted_action,before_json,after_json "
                        "FROM native_physical_events ORDER BY seq"))
                    captures = [json.loads(x[0]) for x in db.execute(
                        "SELECT event_json FROM events ORDER BY seq")]
                    value = db.execute("SELECT spatial_world FROM native_genesis").fetchone()[0]
                self.assertEqual(value, int(enabled))
                self.assertEqual(after["revision"], len(physical))
                self.assertEqual(len(captures), len(physical))
                self.assertFalse(after["engine_registered"])
                self.assertFalse(after["m11_authenticated"])
                self.assertEqual(after["scientific_verdict"], "NOT_ESTABLISHED")
                site = BORN_SITE
                moved = 0
                for i,(action,bef,aft) in enumerate(physical):
                    claim = captures[i]["claim"]
                    senses = set(claim["subjective_evidence_refs"])
                    offered = set(claim["capture"]["accessible_semantics"])
                    if enabled:
                        self.assertIn("evidence:i2:spatial:current:"+site,senses)
                        self.assertEqual(
                            offered & set(MOTIONS), set(offered_moves(site)))
                        self.assertEqual(
                            {x for x in senses if x.startswith(
                                "evidence:i2:spatial:neighbor:")},
                            {"evidence:i2:spatial:neighbor:"+n
                             for n in GRAPH[site]})
                        self.assertNotIn("evidence:i2:spatial:current:source",
                            senses if site != "source" else set())
                    else:
                        self.assertFalse(offered & set(MOTIONS))
                        self.assertFalse(any(s.startswith("evidence:i2:spatial:")
                                            for s in senses))
                    dest = destination(action)
                    if dest is not None:
                        self.assertTrue(enabled)
                        self.assertIn(dest,GRAPH[site])
                        self.assertAlmostEqual(
                            json.loads(aft)["energy"],
                            json.loads(bef)["energy"] - 2.0,places=5)
                        site=site_after(site,action)
                        moved += 1
                    elif action==NO_ACTION:
                        self.assertEqual(bef is None,False)
                self.assertEqual(after["site"], site if enabled else None)
                self.assertEqual(before["remaining_uc"]-
                                 after["remaining_uc"],
                                 260-after["remaining_uc"])
                outcomes[str(enabled)] = {"ticks":after["revision"],
                        "moves":moved,"site":after["site"],
                        "actions":[row[0] for row in physical]}
            print("I2_NATIVE_SPATIAL_P1=" +
                json.dumps(outcomes,sort_keys=True,separators=(",",":")),
                flush=True)


if __name__ == "__main__":
    unittest.main()
