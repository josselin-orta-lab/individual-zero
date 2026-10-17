"""Structural contract checks, including meaningful failure injection."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_engine_contracts import inspect, valid_publication_owners


class VersionedEngineContractTests(unittest.TestCase):
    def test_current_registry_matches_engine_contract(self):
        result = inspect(ROOT)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["checked"], ["I1"])

    def test_registry_mismatch_fails_closed(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "config").mkdir()
            (path / "src/i1").mkdir(parents=True)
            (path / "src/i1/lab").mkdir()
            (path / "src/i1/runtime").mkdir()
            (path / "tests/i1").mkdir(parents=True)
            (path / "docs/engines/i1").mkdir(parents=True)
            registry = json.loads((ROOT / "config/engine-registry.json").read_text())
            (path / "config/engine-registry.json").write_text(json.dumps(registry))
            contract = json.loads((ROOT / "src/i1/engine.json").read_text())
            contract["entrypoints"]["birth"] = "i1lab.unapproved.create"
            (path / "src/i1/engine.json").write_text(json.dumps(contract))
            report = inspect(path)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("registered birth differs" in x for x in report["errors"]))

    def test_future_engines_do_not_inherit_i1_four_owner_roster(self):
        self.assertTrue(valid_publication_owners("I2", ["sensor", "motivation"]))
        self.assertTrue(valid_publication_owners("I2", []))
        self.assertFalse(valid_publication_owners("I2", ["duplicated", "duplicated"]))
        self.assertFalse(valid_publication_owners("I2", ["sensor", None]))
        self.assertFalse(valid_publication_owners("I1", ["sensor", "motivation"]))
        self.assertTrue(valid_publication_owners(
            "I1", ["value_and_needs", "causal_model",
                   "perception", "metacognition_health"]
        ))

    def test_forbidden_shared_lab_fails_closed(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "config").mkdir()
            (path / "src/i1/lab").mkdir(parents=True)
            (path / "src/i1/runtime").mkdir()
            (path / "src/lab").mkdir()
            (path / "tests/i1").mkdir(parents=True)
            (path / "docs/engines/i1").mkdir(parents=True)
            (path / "config/engine-registry.json").write_bytes(
                (ROOT / "config/engine-registry.json").read_bytes())
            (path / "src/i1/engine.json").write_bytes(
                (ROOT / "src/i1/engine.json").read_bytes())
            report = inspect(path)
            self.assertTrue(any("shared src/lab" in x for x in report["errors"]))


if __name__ == "__main__":
    unittest.main()
