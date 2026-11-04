"""#925 P3 physical alternatives: independent food site stock/effects, no motor script.

Pure fixture checks are PHYSICS ONLY, not an autonomously chosen life.
The genuine born identity uses the unchanged paid Competition and cold replay.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, active_food_site, food_effect_here,
    old_food_available, old_food_accessible,
)

BODY = Body(85, 35, 35, 100)
TRAITS = BirthTemperament(0, .5, .3, 0, 0)


def row(action):
    return (0, "capture", action)


def meta(**updates):
    result = {
        "ordinary_food_site": "source", "food_stock": 1,
        "food_restock_every": 0,
        "second_food_site": "passage", "second_food_stock": 2,
        "second_food_restock_every": 0,
        "berry_food_gain": 30., "berry_integrity_delta": -12.,
        "second_berry_food_gain": 22., "second_berry_integrity_delta": 0.,
        "spatial_world": 1,
    }
    result.update(updates)
    return result


class NativeDualLocalFoodP3(unittest.TestCase):
    def test_two_site_stock_and_effect_never_cross_contaminate(self):
        physics = meta()
        at_camp = ()
        at_passage = (row("se_deplacer_vers_passage"),)
        at_source = at_passage + (row("se_deplacer_vers_source"),)
        self.assertIsNone(active_food_site(physics, at_camp))
        self.assertFalse(old_food_accessible(physics, at_camp))
        self.assertEqual(old_food_available(physics, at_camp), 0)
        self.assertEqual(active_food_site(physics, at_passage), "secondary")
        self.assertTrue(old_food_accessible(physics, at_passage))
        self.assertEqual(old_food_available(physics, at_passage), 2)
        self.assertEqual(food_effect_here(physics, at_passage), (22., 0.))
        after_safe_meal = at_passage + (row("manger"),)
        self.assertEqual(old_food_available(physics, after_safe_meal), 1)
        all_safe_consumed = after_safe_meal + (row("manger"),)
        self.assertEqual(old_food_available(physics, all_safe_consumed), 0)
        self.assertFalse(old_food_accessible(physics, all_safe_consumed))
        reached_source = all_safe_consumed + (row("se_deplacer_vers_source"),)
        self.assertTrue(old_food_accessible(physics, reached_source))
        self.assertEqual(old_food_available(physics, reached_source), 1)
        self.assertEqual(food_effect_here(physics, reached_source), (30., -12.))
        after_harmful_meal = reached_source + (row("manger"),)
        self.assertEqual(old_food_available(physics, after_harmful_meal), 0)
        back_to_passage = after_harmful_meal + (row("se_deplacer_vers_passage"),)
        self.assertFalse(old_food_accessible(physics, back_to_passage))
        self.assertEqual(old_food_available(physics, back_to_passage), 0)
        self.assertEqual(food_effect_here(physics, back_to_passage), (22., 0.))

    def test_independent_site_replenishment_is_not_oracular(self):
        fixture = meta(second_food_stock=0, second_food_restock_every=2,
                       food_stock=0, food_restock_every=4)
        passage = (row("se_deplacer_vers_passage"),)
        self.assertFalse(old_food_accessible(fixture, passage))
        self.assertTrue(old_food_accessible(fixture, passage +
                                           (row("attendre"),)))
        self.assertEqual(old_food_available(fixture, passage +
                                            (row("attendre"),)), 1)
        source = passage + (row("se_deplacer_vers_source"),)
        self.assertFalse(old_food_accessible(fixture, source))
        source_later = source + (row("attendre"), row("attendre"))
        self.assertTrue(old_food_accessible(fixture, source_later))
        self.assertEqual(old_food_available(fixture, source_later), 1)
        self.assertEqual(old_food_available(fixture, source_later +
                                            (row("manger"),)), 0)
        source_after = source_later + (row("manger"),
                                       row("se_deplacer_vers_passage"))
        self.assertEqual(old_food_available(fixture, source_after),
                         3)  # independent passage clock, no passage meals

    def test_legacy_single_site_projection_keeps_its_original_contract(self):
        # Old pure fixture dictionaries do not even contain v21 fields.
        legacy = {
            "ordinary_food_site": "source", "food_stock": 1,
            "food_restock_every": 0, "spatial_world": True,
            "berry_food_gain": 35., "berry_integrity_delta": -8.,
        }
        passage = (row("se_deplacer_vers_passage"),)
        source = passage + (row("se_deplacer_vers_source"),)
        self.assertFalse(old_food_accessible(legacy, passage))
        self.assertTrue(old_food_accessible(legacy, source))
        self.assertEqual(old_food_available(legacy, source), 1)
        self.assertEqual(old_food_available(legacy, source+(row("manger"),)), 0)
        self.assertEqual(food_effect_here(legacy, source), (35., -8.))

    def test_birth_lock_invalid_settings_and_cold_tamper(self):
        with tempfile.TemporaryDirectory() as root:
            baseline = dict(
                body=BODY, temperament=TRAITS, spatial_world=True,
                ordinary_food_site="source", second_food_site="passage",
                food_stock=1, food_restock_every=8,
                second_food_stock=1, second_food_restock_every=8,
                berry_food_gain=35., berry_integrity_delta=-12.,
                second_berry_food_gain=25.,
                second_berry_integrity_delta=0.,
                ordinary_water_site="camp", water_stock=2,
                water_restock_every=8, origin_novelty_tie=True,
                learning=True, max_steps=30, uc=300,
                contextual_movement_credit=True,
                sleep_consolidation=False, place_return_tie=False,
                purpose_followthrough=False,
                evidence_tie_exploration=False,
            )
            invalid = (
                {"second_food_site": "source"},
                {"second_food_site": "absent"},
                {"second_food_site": None},
                {"second_food_stock": -1},
                {"second_food_stock": 9},
                {"second_food_restock_every": True},
                {"second_food_restock_every": 33},
                {"second_berry_food_gain": -1},
                {"spatial_world": False},
                {"ordinary_food_site": None},
            )
            for i, override in enumerate(invalid):
                with self.subTest(override=override), self.assertRaises(
                        (NativeRefusal, ValueError)):
                    NativePaidI2.create(
                        Path(root) / ("invalid%d.sqlite" % i),
                        **{**baseline, **override})
            life_path = Path(root) / "dual.sqlite"
            life = NativePaidI2.create(life_path, **baseline)
            for _ in range(30):
                if life.step()["terminal"]:
                    break
            last = life.audit()
            self.assertEqual(last, NativePaidI2.inspect(life_path).audit())
            self.assertFalse(last["engine_registered"])
            self.assertFalse(last["m11_authenticated"])
            self.assertEqual(last["scientific_verdict"], "NOT_ESTABLISHED")
            with sqlite3.connect(life_path) as db:
                settings = db.execute(
                    "SELECT second_food_site,second_food_stock,"
                    "second_food_restock_every,second_berry_food_gain,"
                    "second_berry_integrity_delta FROM native_genesis").fetchone()
                self.assertEqual(settings, ("passage", 1, 8, 25., 0.))
                db.execute("UPDATE native_genesis SET "
                           "second_berry_integrity_delta=-12")
            with self.assertRaises(NativeRefusal):
                NativePaidI2.inspect(life_path)


if __name__ == "__main__":
    unittest.main()
