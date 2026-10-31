"""I2 must have one v4 synthetic cognitive transaction, not legacy owners."""
from pathlib import Path
import ast
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules import cognitive_cycle_fixture as current


class SoleOwnerTests(unittest.TestCase):
    def test_single_transaction_owner_and_no_obsolete_imports(self):
        obsolete = {
            "intention_atomic_fixture",
            "competition_transaction_fixture",
            "action_control_custody_fixture",
        }
        package = ROOT / "src" / "i2" / "modules"
        for name in obsolete:
            self.assertFalse((package / (name + ".py")).exists())
        source = (package / "cognitive_cycle_fixture.py").read_text()
        parsed = ast.parse(source)
        imported = set()
        for node in ast.walk(parsed):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[-1])
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[-1] for alias in node.names)
        self.assertFalse(obsolete & imported)
        self.assertEqual(current.SCHEMA,
                         "i2-unified-cognitive-lifecycle-fixture-v4")

    def test_no_second_sqlite_owner_in_i2_modules(self):
        package = ROOT / "src" / "i2" / "modules"
        for path in package.glob("*.py"):
            if path.name == "cognitive_cycle_fixture.py":
                continue
            with self.subTest(module=path.name):
                parsed = ast.parse(path.read_text())
                imported = set()
                for node in ast.walk(parsed):
                    if isinstance(node, ast.Import):
                        imported.update(alias.name.split(".")[0] for alias in node.names)
                    if isinstance(node, ast.ImportFrom) and node.module:
                        imported.add(node.module.split(".")[0])
                self.assertNotIn("sqlite3", imported)
                self.assertNotIn("apsw", imported)
                self.assertNotIn("pysqlite3", imported)

    def test_retired_docs_and_unused_workflow_are_absent(self):
        docs = ROOT / "src" / "i2" / "docs"
        self.assertFalse((docs / "COGNITIVE_CYCLE_FIXTURE.md").exists())
        self.assertFalse((docs / "CI_WORKFLOW_TEMPLATE.yml").exists())
        current_docs = (docs / "COGNITIVE_CONTROL_UNIFIED.md").read_text()
        self.assertIn(current.SCHEMA, current_docs)

    def test_v4_still_owns_necessary_serialization_and_replay(self):
        for name in (
            "_claim_map", "_parse_claim", "_request", "_frame_map",
            "_advice_map", "_PublishedValues", "_AcceptFrame",
            "_ControlLedger", "_RecordedSafety", "_CaptureSafety",
            "_AcceptedCurrent",
        ):
            with self.subTest(name=name):
                self.assertTrue(hasattr(current, name))
        self.assertEqual(current.CycleReceipt.__dataclass_fields__["motor_authority"].default,
                         "NONE")


if __name__ == "__main__":
    unittest.main()
