"""P2 #924: read-only complete bodily consequences from committed sites.

Synthetic rows below are ONLY pure projector controls, not motor/agency
observations. The final independently born SQLite life uses ordinary paid
Competition, Control and an independent cold audit before projection.
"""
import sqlite3
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_body_contract import Body, CHANNELS, transition
from i2.modules.native_owner_support import _json
from i2.modules.native_place_experience import (
    lived_whole_body_site_consequences,
    lived_place_outcomes,
)
from i2.runtime.native_paid_cycle import NativePaidI2

TRAITS = BirthTemperament(0, .5, .3, 0, 0)


def row(seq, action, before, after):
    return (seq, "capture:" + str(seq), action, 0.0,
            _json(before.as_dict()), _json(after.as_dict()), 0)


class LivedWholeBodyPlace924(unittest.TestCase):
    def test_repeated_safe_and_harmful_meals_retain_all_body_channels(self):
        body = Body(85, 55, 50, 100)
        history = []
        def add(action, *, food=0., injury=0., drink=0.):
            nonlocal body
            physical = ("se_deplacer" if action.startswith("se_deplacer_")
                        else action)
            newer = transition(
                body, physical, berry_food_gain=food,
                berry_integrity_delta=injury, drink_water_gain=drink).body
            history.append(row(len(history)+1, action, body, newer))
            body = newer
        add("boire", drink=30.)
        add("se_deplacer_vers_passage")
        add("manger", food=12., injury=-12.)
        add("se_deplacer_vers_source")
        add("manger", food=12., injury=0.)
        add("se_deplacer_vers_passage")
        add("attendre")
        add("se_deplacer_vers_source")
        add("manger", food=0., injury=-12.)
        seen = lived_whole_body_site_consequences(
            tuple(history), traits=TRAITS, enabled=True)
        self.assertEqual(
            [(e.sequence,e.site,e.action) for e in seen],
            [(1,"camp","boire"), (3,"passage","manger"),
             (5,"source","manger"),(7,"passage","attendre"),
             (9,"source","manger")])
        injury = seen[1]
        self.assertAlmostEqual(injury.channel_effects()["food"], 11.8)
        self.assertAlmostEqual(injury.channel_effects()["integrity"], -12.)
        self.assertGreater(injury.prior_pressures[CHANNELS.index("food")], 0)
        safe = seen[2]
        self.assertEqual(safe.channel_effects()["integrity"], 0.)
        self.assertGreater(safe.channel_effects()["food"], 0)
        self.assertAlmostEqual(seen[0].channel_effects()["water"], 29.6)
        self.assertGreaterEqual(seen[3].channel_effects()["integrity"], 0)
        self.assertEqual(seen[4].channel_effects()["integrity"], -12.)
        self.assertLess(seen[4].channel_effects()["food"], 0.01)
        self.assertNotIn("hidden", {e.site for e in seen})
        with self.assertRaises(FrozenInstanceError):
            injury.site = "camp"

    def test_full_stomach_harm_preserved_even_if_old_target_only_omits(self):
        full = Body(85., 100., 90., 100.)
        harmful = transition(full, "manger", berry_food_gain=0.,
                             berry_integrity_delta=-12.).body
        hist = (row(1, "se_deplacer_vers_passage", full,
                    transition(full,"se_deplacer").body),)
        current = transition(full, "se_deplacer").body
        outcome = transition(current, "manger", berry_food_gain=0.,
                             berry_integrity_delta=-12.).body
        hist += (row(2,"manger",current,outcome),)
        records = lived_whole_body_site_consequences(
            hist, traits=TRAITS, enabled=True)
        self.assertEqual(len(records),1)
        self.assertEqual(records[0].site,"passage")
        self.assertEqual(records[0].prior_pressures[CHANNELS.index("food")],0)
        self.assertEqual(records[0].channel_effects()["integrity"],-12.)
        self.assertEqual(lived_place_outcomes(
            hist,traits=TRAITS,enabled=True),())

    def test_unknown_absence_nonspatial_no_rest_forecast(self):
        b = Body(85., 55., 50., 88.)
        self.assertEqual(lived_whole_body_site_consequences(
            (), traits=TRAITS, enabled=True), ())
        self.assertEqual(lived_whole_body_site_consequences(
            (row(1,"attendre",b,transition(b,"attendre").body),),
            traits=TRAITS,enabled=False), ())
        first = row(1,"attendre",b,transition(b,"attendre").body)
        observed = lived_whole_body_site_consequences(
            (first,), traits=TRAITS,enabled=True)
        self.assertEqual([(r.site,r.action) for r in observed],
                         [("camp","attendre")])
        self.assertGreater(observed[0].channel_effects()["integrity"],0)
        self.assertNotIn("source", [r.site for r in observed])
        with self.assertRaises(ValueError):
            lived_whole_body_site_consequences(
                (row(1, "se_deplacer_vers_passage", b,
                     transition(b,"se_deplacer").body),),
                traits=TRAITS, enabled=False)
        with self.assertRaises(ValueError):
            lived_whole_body_site_consequences(
                (row(1, "se_deplacer_vers_source", b,
                     transition(b,"se_deplacer").body),),
                traits=TRAITS, enabled=True)

    def test_invalid_rows_out_of_order_noncanonical_or_discontinuous(self):
        b = Body(85., 55., 50., 88.)
        after = transition(b,"attendre").body
        first = row(1,"attendre",b,after)
        second = row(2,"attendre",after,
                     transition(after,"attendre").body)
        invalid = [
            (row(2,"attendre",b,after),),
            (first, first),
            (first[:6],),
            (first[:2]+("unknown",)+first[3:],),
            (first[:4]+('{"food":55,"water":50,"energy":85,"integrity":88}',)+first[5:],),
            (first, row(2,"attendre",b,after)),
            (first[:1]+("",)+first[2:],),
            (first[:3]+("not-relief",)+first[4:],),
        ]
        for n,case in enumerate(invalid):
            with self.subTest(n=n), self.assertRaises(ValueError):
                lived_whole_body_site_consequences(
                    case, traits=TRAITS, enabled=True)
        self.assertEqual(len(lived_whole_body_site_consequences(
            (first,second),traits=TRAITS,enabled=True)),2)
        with self.assertRaises(ValueError):
            lived_whole_body_site_consequences(
                (first,),traits=TRAITS,enabled=1)

    def test_genuine_paid_owner_cold_replayed_before_read_only_projection(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "born-v21.db"
            life = NativePaidI2.create(
                path, body=Body(85,55,35,100), temperament=TRAITS,
                learning=True, origin_novelty_tie=True,
                spatial_world=True, ordinary_food_site="source",
                second_food_site="passage",
                berry_food_gain=12., berry_integrity_delta=-12.,
                second_berry_food_gain=12.,
                second_berry_integrity_delta=0.,
                second_food_stock=1, second_food_restock_every=8,
                food_stock=1, food_restock_every=8,
                ordinary_water_site="camp", water_stock=2,
                water_restock_every=8, drink_water_gain=40.,
                max_steps=20, uc=300)
            for _ in range(20):
                if life.step()["terminal"]:
                    break
            self.assertEqual(life.audit(),NativePaidI2.inspect(path).audit())
            with sqlite3.connect(path) as db:
                events=tuple(db.execute(
                    "SELECT e.seq,e.capture_ref,p.admitted_action,"
                    "p.net_physiological_relief,p.before_json,p.after_json,"
                    "COALESCE(d.found,0) "
                    "FROM native_physical_events p "
                    "JOIN events e ON e.seq=p.seq "
                    "LEFT JOIN native_discoveries d ON d.seq=p.seq "
                    "ORDER BY p.seq"))
            observed = lived_whole_body_site_consequences(
                events,traits=TRAITS,enabled=True)
            self.assertTrue(all(1<=e.sequence<=20 for e in observed))
            self.assertTrue(all(e.site in ("camp","passage","source")
                                for e in observed))
            self.assertTrue(all(e.action in ("manger","boire",
                           "boire_decouverte","dormir","attendre")
                                for e in observed))
            self.assertFalse(life.audit()["engine_registered"])
            self.assertFalse(life.audit()["m11_authenticated"])


if __name__=="__main__":
    unittest.main()
