"""Non-executable, never-registered engine proposal checks."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class EngineProposalTests(unittest.TestCase):
    def test_engine_is_not_activated(self):
        contract = json.loads((ROOT / "src/i3/engine.json").read_text())
        registry = json.loads((ROOT / "config/engine-registry.json").read_text())
        self.assertEqual(contract["generation"], "I3")
        self.assertEqual(contract["status"], "proposal")
        self.assertFalse(contract["entrypoints"])
        self.assertEqual(contract["activation"], "NOT_REGISTERED_NOT_EXECUTABLE")
        self.assertNotIn("I3", registry["generations"])
        self.assertEqual(contract["scientific"]["gate"], "not_established")
