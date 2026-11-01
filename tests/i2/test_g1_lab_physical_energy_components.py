"""ADR-0006 measurement-only: audit physical decomposition, never aversion.

Frozen before implementation in issue #662 comment 6560542329.
No policy, experimenter-initiated action, or living motor authority.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from i2.lab.integrated_loop import (  # noqa: E402
    IntegratedLab, REGIMES, EAT, LabRefusal,
)
from i2.modules.cognitive_cycle_fixture import FaultInjected  # noqa: E402


class BodyEnergyComponentAccounting(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.path=Path(self.t.name)/"owner.sqlite"

    def create(self, **kwargs):
        return IntegratedLab.create(
            self.path,life_ref="lab:components:one",
            genesis_ref="lab:components:genesis",learning=True,
            deltas=REGIMES["adverse"],initial_energy=24,**kwargs,
        )

    def rows(self):
        with sqlite3.connect(self.path) as db:
            return db.execute(
                "SELECT action_ref,before_energy,metabolic_debit,"
                "food_energy_impulse,net,energy,uc_remaining "
                "FROM g1_lab_steps ORDER BY seq"
            ).fetchall()

    def test_one_chosen_food_negative_impulse_and_cost(self):
        lab=self.create()
        first=lab.step()
        second=lab.step()
        self.assertEqual(second.chosen,EAT)
        rows=self.rows()
        self.assertEqual([r[2] for r in rows],[2,2])
        self.assertEqual([r[3] for r in rows],[0,-8])
        for action,before,cost,food,net,after,uc in rows:
            self.assertEqual(max(0,min(100,before-cost+food))-before,net)
            self.assertEqual(after-before,net)
            self.assertGreaterEqual(uc,0)
        self.assertEqual(lab.audit()["revision"],2)
        self.assertEqual(first.motor_authority,"NONE")

    def test_historical_metabolic_and_food_component_forgery_refused(self):
        for field in ("metabolic_debit","food_energy_impulse"):
            with self.subTest(field=field):
                if self.path.exists():
                    self.path.unlink()
                lab=self.create()
                lab.step();lab.step()
                with sqlite3.connect(self.path) as db:
                    db.execute(f"UPDATE g1_lab_steps SET {field}={field}+1 WHERE seq=2")
                with self.assertRaisesRegex(LabRefusal,"cannot replay"):
                    lab.audit()
                with self.assertRaises(LabRefusal):
                    lab.step()

    def test_body_and_components_rollback_with_cognition(self):
        lab=self.create()
        before=lab.audit()
        with self.assertRaises(FaultInjected):
            lab.step(fault="before_commit")
        self.assertEqual(lab.audit(),before)
        self.assertEqual(self.rows(),[])

    def test_aversive_valence_not_invented_from_nutrition(self):
        with sqlite3.connect(self.path) as db:
            pass
        lab=self.create()
        lab.step()
        with sqlite3.connect(self.path) as db:
            columns={r[1] for r in db.execute("PRAGMA table_info(g1_lab_steps)")}
        self.assertIn("food_energy_impulse",columns)
        self.assertIn("metabolic_debit",columns)
        self.assertNotIn("sensory_aversion",columns)
        self.assertNotIn("subjective_pain",columns)
        self.assertFalse(lab.audit()["m11_authenticated"])


if __name__=="__main__":
    unittest.main()
