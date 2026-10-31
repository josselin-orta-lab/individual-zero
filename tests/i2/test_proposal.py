"""Static-only I2 proposal checks; never instantiate a living engine."""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
class TestI2Proposal(unittest.TestCase):
    def test_not_registered_or_executable(self):
        c=json.loads((ROOT/"src/i2/engine.json").read_text())
        r=json.loads((ROOT/"config/engine-registry.json").read_text())
        self.assertEqual(c["generation"],"I2")
        self.assertEqual(c["status"],"proposal")
        self.assertEqual(c["entrypoints"],{})
        self.assertEqual(c["publication_owners"],[])
        self.assertEqual(c["activation"],"NOT_REGISTERED_NOT_EXECUTABLE")
        self.assertNotIn("I2",r["generations"])
        self.assertEqual(r["active_generation"],"I1")
        self.assertEqual(c["scientific"]["gate"],"not_established")
