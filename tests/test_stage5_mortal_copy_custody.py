"""Mortal Stage5 copy attempts never construct legacy Oracle/Bench children.

This intentionally fails closed until independent-birth copy custody can seed
a mortal child and its complete causal journal without historical restoration.
The historical Stage5 copy contract is unchanged for legacy fixtures.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from lab.mortal_execution import MortalStatus
from lab.stage5_reference_fixture import build_stage5_reference_runtime
from lab.stage5_runtime import Stage5Runtime
from lab.world import Command


class MortalStage5CopyCustodyTests(unittest.TestCase):
    def test_active_mortal_copy_is_refused_before_snapshot_or_legacy_birth(self):
        parent = build_stage5_reference_runtime(autonomous_mortal=True)
        self.assertIsNone(parent.bench)
        self.assertEqual(parent.stage3.substrate.mortal_status, MortalStatus.ACTIVE)
        before = parent.journal.canonical_bytes()
        with patch.object(Stage5Runtime, "__init__",
                          side_effect=AssertionError("unsafe legacy child constructed")):
            with self.assertRaisesRegex(RuntimeError, "safe birth"):
                parent.create_copy(copy_ref="development:new-identity")
        self.assertEqual(parent.journal.canonical_bytes(), before)
        self.assertEqual(parent.stage3.substrate.snapshots._snapshots, {})
        self.assertIsNone(parent.bench)

    def test_terminal_parent_cannot_publish_snapshot_or_create_a_child(self):
        parent = build_stage5_reference_runtime(autonomous_mortal=True)
        parent.world.apply_scenario_event("set_lethal_zone", {
            "position": parent.world.position.as_dict(), "active": True,
        })
        sub = parent.stage3.substrate
        sub.open_step()
        self.assertEqual(sub.execute(Command("attendre")).status, "dead")
        self.assertEqual(sub.mortal_status, MortalStatus.DEAD)
        before = parent.journal.canonical_bytes()
        with patch.object(Stage5Runtime, "__init__",
                          side_effect=AssertionError("postmortem child constructed")):
            with self.assertRaisesRegex(RuntimeError, "dead individual"):
                parent.create_copy(copy_ref="forbidden:post-death")
        self.assertEqual(parent.journal.canonical_bytes(), before)
        self.assertEqual(sub.snapshots._snapshots, {})
        self.assertTrue(parent.journal.verify())

    def test_technical_halt_cannot_publish_copy(self):
        parent = build_stage5_reference_runtime(autonomous_mortal=True)
        parent.stage3.substrate._mortal_boundary.halt(failed_step=1)
        self.assertEqual(parent.stage3.substrate.mortal_status,
                         MortalStatus.TECHNICAL_HALT)
        old = parent.journal.canonical_bytes()
        with self.assertRaisesRegex(RuntimeError, "technically halted"):
            parent.create_copy(copy_ref="forbidden:halt")
        self.assertEqual(parent.journal.canonical_bytes(), old)

    def test_legacy_copy_still_clones_into_distinct_identity(self):
        parent = build_stage5_reference_runtime()
        child, record = parent.create_copy(copy_ref="legacy:copy-unmodified")
        self.assertNotEqual(child.individual_id, parent.individual_id)
        self.assertEqual(child.lineage_parent_id, parent.individual_id)
        self.assertEqual(child.lineage_copy_point, record.id)


if __name__ == "__main__":
    unittest.main()
