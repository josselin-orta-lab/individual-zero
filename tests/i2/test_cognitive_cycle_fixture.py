"""Only one I2 SQLite contract: retired v1/v2/v3 layouts are rejected."""
from pathlib import Path
import sqlite3
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture, SCHEMA
from test_synthetic_lifecycle import (LIFE, GENESIS, Source, Values, Current,
                                      Safety, TerminalSource)


class CurrentSchemaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "single-contract.sqlite"
        self.source, self.values, self.current = Source(), Values(), Current()
        self.safety, self.terminal = Safety(), TerminalSource()
        self.ports = dict(life_ref=LIFE, observation_source=self.source,
                          valuation_source=self.values,
                          current_source=self.current, safety_source=self.safety,
                          genesis_ref=GENESIS, terminal_source=self.terminal)

    def test_only_unified_lifecycle_control_contract_exists(self):
        fixture = CognitiveCycleFixture.create(path=self.db, synthetic_uc=10,
                                              **self.ports)
        report = fixture.audit()
        self.assertEqual(report["schema"], SCHEMA)
        self.assertEqual(report["genesis_ref"], GENESIS)
        self.assertTrue(report["control_review_included"])
        self.assertEqual(report["motor_authority"], "NONE")
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute(
                "SELECT name FROM sqlite_master WHERE name='lifecycle'"
            ).fetchone()[0], "lifecycle")

    def test_missing_control_or_terminal_ports_has_no_compatibility_fallback(self):
        for missing in ("current_source", "safety_source", "genesis_ref",
                        "terminal_source"):
            with self.subTest(missing=missing):
                params = dict(self.ports)
                params.pop(missing)
                with self.assertRaises(TypeError):
                    CognitiveCycleFixture.create(
                        path=self.db, synthetic_uc=10, **params)
                self.assertFalse(self.db.exists())

    def test_legacy_schema_identifiers_cannot_be_reopened(self):
        fixture = CognitiveCycleFixture.create(path=self.db, synthetic_uc=10,
                                               **self.ports)
        for old in ("i2-unified-cognitive-cycle-fixture-v1",
                    "i2-unified-cognitive-control-fixture-v2",
                    "i2-unified-cognitive-lifecycle-fixture-v3"):
            with self.subTest(old=old):
                with sqlite3.connect(self.db) as conn:
                    conn.execute("UPDATE identity SET schema_id=? WHERE id=1", (old,))
                with self.assertRaises(ValueError):
                    CognitiveCycleFixture.reopen(path=self.db, **self.ports)
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE identity SET schema_id=? WHERE id=1", (SCHEMA,))
        self.assertEqual(fixture.audit()["committed"], 0)


if __name__ == "__main__":
    unittest.main()
