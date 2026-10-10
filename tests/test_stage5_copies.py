from __future__ import annotations

import unittest

from lab.stage5_reference_fixture import build_stage5_reference_runtime


def owner_state(runtime):
    return {
        owner.owner_id: owner.export_causal_state()
        for owner in runtime.causal_owners
    }


class Stage5CopyTests(unittest.TestCase):
    def test_copy_starts_from_complete_snapshot_with_new_identity(self) -> None:
        parent = build_stage5_reference_runtime()
        for _ in range(4):
            parent.run_step()

        parent_before = owner_state(parent)
        child, record = parent.create_copy(
            copy_ref="battery:patience:0",
            battery_copy=True,
        )

        self.assertNotEqual(child.individual_id, parent.individual_id)
        self.assertEqual(
            child.temperament_projection.parent_id,
            parent.individual_id,
        )
        self.assertEqual(
            child.temperament_projection.copy_snapshot_id,
            record.id,
        )
        self.assertEqual(
            child.temperament_projection.lineage_id,
            parent.temperament_projection.lineage_id,
        )
        self.assertTrue(child.battery_copy)
        self.assertEqual(child.scheduler.t_monde, parent.scheduler.t_monde)

        parent_after = owner_state(parent)
        self.assertEqual(parent_before, parent_after)

    def test_copy_inherits_tau_exactly_but_not_parent_identity(self) -> None:
        parent = build_stage5_reference_runtime()
        for _ in range(3):
            parent.run_step()

        child, _ = parent.create_copy(
            copy_ref="bifurcation:day30",
            battery_copy=False,
        )

        parent_state = parent.temperament_projection.export_causal_state()
        child_state = child.temperament_projection.export_causal_state()

        self.assertEqual(parent_state["tau"], child_state["tau"])
        self.assertEqual(parent_state["derived"], child_state["derived"])
        self.assertNotEqual(
            parent_state["individual_id"],
            child_state["individual_id"],
        )
        self.assertFalse(child.battery_copy)

    def test_child_can_continue_without_reinjecting_changes_into_parent(self) -> None:
        parent = build_stage5_reference_runtime()
        for _ in range(5):
            parent.run_step()

        child, _ = parent.create_copy(
            copy_ref="branch:test",
            battery_copy=False,
        )
        parent_world = parent.world.export_causal_state()
        parent_owners = owner_state(parent)

        for _ in range(3):
            child.run_step()

        self.assertEqual(
            parent.world.export_causal_state(),
            parent_world,
        )
        self.assertEqual(owner_state(parent), parent_owners)
        self.assertGreater(child.scheduler.t_monde, parent.scheduler.t_monde)

    def test_s_t_identity_is_rebound_in_copy(self) -> None:
        parent = build_stage5_reference_runtime()
        for _ in range(3):
            parent.run_step()
        self.assertIsNotNone(parent.s_t.current)

        child, _ = parent.create_copy(
            copy_ref="copy:s-t-rebind",
            battery_copy=False,
        )

        self.assertIsNotNone(child.s_t.current)
        self.assertEqual(
            child.s_t.current.individual_id,
            child.individual_id,
        )
        self.assertNotEqual(
            child.s_t.current.individual_id,
            parent.s_t.current.individual_id,
        )

    def test_copy_creation_is_logged_in_parent_and_child(self) -> None:
        parent = build_stage5_reference_runtime()
        child, record = parent.create_copy(
            copy_ref="battery:risk:1",
            battery_copy=True,
        )

        parent_events = [
            entry.causal_event
            for entry in parent.journal.entries
            if entry.causal_event.get("kind") == "copy_created"
        ]
        child_events = [
            entry.causal_event
            for entry in child.journal.entries
            if entry.causal_event.get("kind") == "copy_branch_started"
        ]

        self.assertEqual(len(parent_events), 1)
        self.assertEqual(len(child_events), 1)
        self.assertEqual(
            parent_events[0]["copy_snapshot_id"],
            record.id,
        )
        self.assertEqual(
            child_events[0]["shared_prefix_snapshot_id"],
            record.id,
        )


if __name__ == "__main__":
    unittest.main()
