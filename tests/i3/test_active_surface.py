"""Static guards for the I3 active-surface contract.

This test protects navigation and stage separation. It does not execute a
scientific falsifier or create any World/life.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
I3 = ROOT / "src" / "i3"
MANIFEST = I3 / "ACTIVE_SURFACE.json"


class ActiveSurfaceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text())

    def test_manifest_declares_current_governance(self):
        self.assertEqual(self.data["schema"], "i3-active-surface/v1")
        self.assertEqual(self.data["current_stage"], "2.1 replay gate")
        self.assertEqual(self.data["canonical_status"], "REPLAY_GATE_CAPACITY_SHOWN")
        self.assertFalse(self.data["governance"]["i3_registered"])
        self.assertEqual(
            self.data["governance"]["adr_0017_world_opening_moratorium"], "ACTIVE")
        self.assertFalse(self.data["governance"]["fresh_lived_worlds_allowed"])

    def test_every_declared_active_or_compatibility_path_exists(self):
        for key in ("active_science", "active_engineering", "stage1_compatibility_only"):
            for rel in self.data[key]:
                self.assertTrue((ROOT / rel).is_file(), f"missing {key}: {rel}")

    def test_active_stage2_python_does_not_import_stage1_lab_helpers(self):
        paths = [
            p for p in self.data["active_science"]
            if p.endswith(".py")
        ] + [
            p for p in self.data["active_engineering"]
            if p.endswith(".py") and p.startswith("src/i3/")
        ]
        offenders = []
        for rel in paths:
            tree = ast.parse((ROOT / rel).read_text(), filename=rel)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if "stage1_" in module:
                        offenders.append((rel, module))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if "stage1_" in alias.name:
                            offenders.append((rel, alias.name))
        self.assertEqual(offenders, [])

    def test_replay_gate_stays_unregistered_while_moratorium_is_active(self):
        runtime = (I3 / "runtime" / "life.py").read_text()
        self.assertNotIn("p13_replay_gate_v1", runtime)
        self.assertNotIn("p13_replay_gate_zero_perceived_cost_v1", runtime)

    def test_status_points_to_canonical_software_result(self):
        status = (I3 / "docs" / "STATUS.md").read_text()
        self.assertIn("REPLAY_GATE_CAPACITY_SHOWN", status)
        self.assertIn("ADR-0017 remains active", status)

    def test_stage1_compatibility_set_is_not_current_science(self):
        current = set(self.data["active_science"])
        compatibility = set(self.data["stage1_compatibility_only"])
        self.assertTrue(compatibility)
        self.assertTrue(current.isdisjoint(compatibility))


if __name__ == "__main__":
    unittest.main()
