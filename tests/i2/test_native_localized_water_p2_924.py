"""P2 boundary: resource position is physical access, NOT a learned site reward.

The path prefixes here are physics-only replays, not motor commands or
claims that an autonomous individual chose to navigate to the source.
"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_spatial_world import GRAPH
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, old_water_accessible, genesis_digest,
)


class LocalizedWaterP2(unittest.TestCase):
    BODY = Body(85, 90, 35, 100)
    TRAITS = BirthTemperament(0, .5, .3, 0, 0)

    def test_remote_water_requires_physical_arrival_and_supply(self):
        # Only previously admitted actions can define the current site.
        base = {"water_stock":2, "water_restock_every":0,
                "spatial_world":1, "ordinary_water_site":"source"}
        empty = []
        passage = [(1,"cap","se_deplacer_vers_passage")]
        arrived = passage + [(2,"cap","se_deplacer_vers_source")]
        consumed = arrived + [(3,"cap","boire")]
        self.assertFalse(old_water_accessible(base, empty))
        self.assertFalse(old_water_accessible(base, passage))
        self.assertTrue(old_water_accessible(base, arrived))
        self.assertTrue(old_water_accessible(base, consumed))
        exhausted = consumed + [(4,"cap","boire")]
        self.assertFalse(old_water_accessible(base, exhausted))
        self.assertFalse(old_water_accessible(
            {**base, "water_stock":0}, arrived))
        self.assertTrue(old_water_accessible(
            {**base, "ordinary_water_site":None}, empty))
        self.assertTrue(old_water_accessible(
            {**base, "ordinary_water_site":"camp"}, empty))

    def test_birth_validates_site_and_capture_has_no_remote_water(self):
        with tempfile.TemporaryDirectory() as root:
            for bad_site, spatial in (
                ("not-a-site",True), ("source",False),
                (1,True), ("source",0)):
                with self.subTest(site=bad_site,spatial=spatial):
                    with self.assertRaises(NativeRefusal):
                        NativePaidI2.create(
                            Path(root) / ("invalid-"+str(bad_site)+"-"+str(spatial)),
                            body=self.BODY, temperament=self.TRAITS,
                            spatial_world=spatial,
                            ordinary_water_site=bad_site)
            path=Path(root)/"local.db"
            life=NativePaidI2.create(
                path, body=self.BODY, temperament=self.TRAITS,
                spatial_world=True, ordinary_water_site="source",
                water_stock=2, food_stock=0, max_steps=4,
                uc=110, learning=False)
            with life._connect() as db:
                meta=life._meta(db)
                snap=__import__(
                    "i2.runtime.native_physiology_journal",fromlist=["native_snapshot"]
                ).native_snapshot(db)
                claim=life._claim(snap,meta,life._rows(db))
                self.assertEqual(meta["ordinary_water_site"],"source")
                self.assertNotIn("boire",claim.capture.accessible_semantics)
                self.assertNotIn(
                    "evidence:i2:spatial:current:source",
                    claim.subjective_evidence_refs)
                self.assertNotIn(
                    "evidence:i2:spatial:neighbor:source",
                    claim.subjective_evidence_refs)
            self.assertEqual(NativePaidI2.inspect(path).audit(),life.audit())
            with sqlite3.connect(path) as db:
                db.execute(
                    "UPDATE native_genesis SET ordinary_water_site='camp' WHERE id=1")
            with self.assertRaises(NativeRefusal):
                life.audit()

    def test_legacy_global_water_and_empty_supply_remain_stable(self):
        with tempfile.TemporaryDirectory() as root:
            for spatial in (False,True):
                for stock in (0,1):
                    path=Path(root)/("test-"+str(spatial)+"-"+str(stock))
                    life=NativePaidI2.create(
                        path, body=self.BODY, temperament=self.TRAITS,
                        spatial_world=spatial, water_stock=stock,
                        food_stock=0, max_steps=2, uc=80)
                    with life._connect() as db:
                        meta=life._meta(db)
                        snap=__import__(
                          "i2.runtime.native_physiology_journal",
                          fromlist=["native_snapshot"]
                        ).native_snapshot(db)
                        claim=life._claim(snap,meta,life._rows(db))
                    self.assertEqual("boire" in
                        claim.capture.accessible_semantics,bool(stock))
                    self.assertEqual(NativePaidI2.inspect(path).audit(),life.audit())


if __name__ == "__main__":
    unittest.main()
