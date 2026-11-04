"""#969: isolated origin novelty controls and paid P3 falsifier, research only."""
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
    NativePaidI2, NativeRefusal, origin_novelty_tie_scores,
)

BODY = Body(85, 35, 35, 100)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)


def tie(scores, destinations, visited, *, exploration=.3,
        reflex="NO_PREEMPTION", enabled=True):
    return origin_novelty_tie_scores(
        scores, offered=tuple(scores), destinations=destinations,
        visited=visited, exploration=exploration,
        reflex_state=reflex, enabled=enabled)


class OriginNovelty969(unittest.TestCase):
    def test_pure_positive_tie_nonoracle_and_symmetric_renaming(self):
        scores = {"left": 4, "right": 4, "sleep": 2}
        a = {"left": "known", "right": "unknown"}
        self.assertEqual(tie(scores, a, {"known"}),
                         ({**scores, "right": 5}, frozenset({"right"})))
        b = {"left": "unknown", "right": "known"}
        self.assertEqual(tie(scores, b, {"known"}),
                         ({**scores, "left": 5}, frozenset({"left"})))
        for seen in (set(), {"known", "unknown"}):
            self.assertEqual(tie(scores, a, seen), (scores, frozenset()))
        for kw in ({"enabled": False}, {"exploration": 0},
                   {"exploration": -.1}, {"reflex": "CONSTRAIN"},
                   {"reflex": "PREEMPT"}):
            self.assertEqual(tie(scores, a, {"known"}, **kw),
                             (scores, frozenset()))
        for other in ({"left": 4, "right": 4, "sleep": 4},
                      {"left": 3, "right": 4, "sleep": 5},
                      {"left": 0, "right": 0, "sleep": 0}):
            self.assertEqual(tie(other, a, {"known"}),
                             (other, frozenset()))
        many = {"left": 4, "right": 4}
        self.assertEqual(tie(many, {"left": "u1", "right": "u2"},
                             {"known"}), (many, frozenset()))
        with self.assertRaises(NativeRefusal):
            tie(scores, a, {"known"}, enabled=1)

    def test_exact_born_flag_and_independent_cold_tamper(self):
        with tempfile.TemporaryDirectory() as root:
            base = dict(body=BODY, temperament=TRAITS,
                        spatial_world=True, ordinary_food_site="source",
                        ordinary_water_site="camp", uc=120, max_steps=3)
            for i, bad in enumerate((1, 0, "true", None)):
                with self.subTest(bad=bad), self.assertRaises(NativeRefusal):
                    NativePaidI2.create(Path(root) / ("bad%d.db" % i),
                                        **base, origin_novelty_tie=bad)
            with self.assertRaises(NativeRefusal):
                NativePaidI2.create(Path(root) / "nonspatial.db",
                                    body=BODY, temperament=TRAITS,
                                    origin_novelty_tie=True)
            path = Path(root) / "verified.db"
            life = NativePaidI2.create(path, **base, origin_novelty_tie=True)
            for _ in range(3):
                life.step()
            self.assertEqual(life.audit(), NativePaidI2.inspect(path).audit())
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute(
                    "SELECT origin_novelty_tie FROM native_genesis").fetchone(),
                    (1,))
                db.execute("UPDATE native_genesis SET origin_novelty_tie=0")
            with self.assertRaises(NativeRefusal):
                life.audit()

    def test_new_unforced_64_step_p3_pair(self):
        """New exploratory worlds, never reinterpret old #947/968 outcomes."""
        output = {}
        with tempfile.TemporaryDirectory() as root:
            for enabled in (False, True):
                name = "on" if enabled else "off"
                path = Path(root) / (name + ".sqlite")
                life = NativePaidI2.create(
                    path, body=BODY, temperament=TRAITS, learning=False,
                    spatial_world=True, ordinary_food_site="source",
                    ordinary_water_site="camp", food_stock=1, water_stock=2,
                    food_restock_every=8, water_restock_every=8,
                    uc=850, max_steps=64, drink_water_gain=40.,
                    berry_food_gain=35., origin_novelty_tie=enabled,
                    evidence_tie_exploration=False,
                    sleep_consolidation=False, place_return_tie=False,
                    purpose_followthrough=False,
                    contextual_movement_credit=False)
                start = life.audit()
                for _ in range(64):
                    if life.step()["terminal"]:
                        break
                final = life.audit()
                self.assertEqual(final, NativePaidI2.inspect(path).audit())
                with sqlite3.connect(path) as db:
                    actions = [r[0] for r in db.execute(
                        "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
                    events = [json.loads(r[0]) for r in db.execute(
                        "SELECT event_json FROM events ORDER BY seq")]
                sites, site = [BORN_SITE], BORN_SITE
                for action in actions:
                    if destination(action) is not None:
                        site = site_after(site, action)
                    sites.append(site)
                self.assertEqual(site, final["site"])
                novelty, meals = [], []
                for tick, event in enumerate(events, 1):
                    for v in (event.get("advice") or {}).get("values", ()):
                        if ":visited-versus-unvisited-adjacent-tie" in v["evidence_ref"]:
                            novelty.append(tick)
                    if actions[tick-1] == "manger":
                        self.assertEqual(sites[tick-1], "source")
                        self.assertIn("manger", event["claim"]["capture"]["accessible_semantics"])
                        meals.append(tick)
                if not enabled:
                    self.assertEqual(novelty, [])
                output[name] = {
                    "actions": actions, "sites": sites,
                    "novelty_paid_ticks": novelty, "meal_ticks": meals,
                    "terminal": final["terminal"], "steps": final["revision"],
                    "body": final["body"], "uc": start["remaining_uc"]-final["remaining_uc"],
                    "cold_audit": "PASS"}
            print("I2_ORIGIN_NOVELTY_969=" + json.dumps(
                output, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
