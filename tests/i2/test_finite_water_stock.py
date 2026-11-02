"""Finite water is owned by the paid action journal and disappears at depletion."""
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2,SCENARIOS,DRINK,PrototypeRefusal,
)

class FiniteWaterStockTests(unittest.TestCase):
    def test_one_use_consumes_stock_and_next_capture_has_no_drink(self):
        with tempfile.TemporaryDirectory() as directory:
            life=IsolatedI2.create(
                Path(directory)/"finite.sqlite",learning=True,
                impulses=SCENARIOS["adverse"],initial_energy=6,
                restorative_water_study=True,finite_water_capacity=1,
                deadline_aware=True)
            life.run_world(ticks=4)
            rows=life.decision_evidence()
            self.assertEqual(rows[0]["chosen"],DRINK)
            self.assertIn(DRINK,rows[0]["visible"])
            self.assertEqual(len(rows),2)
            self.assertNotIn(DRINK,rows[1]["visible"])
            self.assertEqual(life.audit()["water_remaining"],0)
            self.assertEqual(rows[0]["energy_after"],8)
            self.assertEqual(
                IsolatedI2.inspect(life.path).audit()["water_remaining"],0)
            self.assertEqual(life.audit()["science"],"NOT_ESTABLISHED")
            self.assertFalse(life.audit()["m11_authenticated"])

    def test_existing_unlimited_and_inert_water_worlds_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            for water in (False,True):
                life=IsolatedI2.create(
                    Path(directory)/(str(water)+".sqlite"),learning=True,
                    impulses=SCENARIOS["adverse"],initial_energy=20,
                    restorative_water_study=water,deadline_aware=True)
                life.run_world(ticks=4)
                self.assertIsNone(life.audit()["water_remaining"])
                self.assertIn(DRINK,life.decision_evidence()[1]["visible"])

    def test_invalid_stock_refused_at_genesis(self):
        with tempfile.TemporaryDirectory() as directory:
            for bad in (-1,9,True,1.0):
                with self.subTest(bad=bad),self.assertRaises(PrototypeRefusal):
                    IsolatedI2.create(Path(directory)/"bad.sqlite",learning=True,
                       impulses=SCENARIOS["adverse"],
                       restorative_water_study=True,finite_water_capacity=bad)
            with self.assertRaises(PrototypeRefusal):
                IsolatedI2.create(Path(directory)/"inert.sqlite",learning=True,
                    impulses=SCENARIOS["adverse"],finite_water_capacity=1)

if __name__=="__main__":
    unittest.main()
