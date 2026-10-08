from __future__ import annotations

import unittest

from lab.determinism import RandomStreamRegistry, deterministic_id
from lab.journal import HashChainedJournal
from lab.snapshots import SnapshotManager, SnapshotType


class FakeOwner:
    def __init__(self, owner_id: str, value: int) -> None:
        self._owner_id = owner_id
        self.value = value

    @property
    def owner_id(self) -> str:
        return self._owner_id

    def export_causal_state(self) -> object:
        return {"value": self.value}

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, dict):
            raise ValueError("invalid fake owner state")
        self.value = int(state["value"])


class SnapshotManagerTests(unittest.TestCase):
    def make_manager(self) -> tuple[SnapshotManager, HashChainedJournal]:
        journal = HashChainedJournal()
        return SnapshotManager(journal=journal), journal

    def test_exactly_four_life_snapshot_types_exist(self) -> None:
        self.assertEqual(
            {snapshot_type.value for snapshot_type in SnapshotType},
            {"birth", "periodic", "lethal_checkpoint", "copy"},
        )

    def test_snapshot_restores_each_owner_through_its_interface(self) -> None:
        manager, _ = self.make_manager()
        first = FakeOwner("first", 10)
        second = FakeOwner("second", 20)

        record = manager.take(
            snapshot_type=SnapshotType.PERIODIC,
            individual_id="i0-1",
            t_monde=4,
            cycle=0,
            attempt_ref=None,
            owners=(second, first),
            versions={"ontology": "v1"},
        )

        first.value = 99
        second.value = 88
        manager.restore(record.id, owners=(first, second))

        self.assertEqual(first.value, 10)
        self.assertEqual(second.value, 20)

    def test_rng_state_continuation_is_restored_exactly(self) -> None:
        manager, _ = self.make_manager()
        rng = RandomStreamRegistry(campaign_seed=42)
        world = rng.stream("world")
        world.random()

        record = manager.take(
            snapshot_type=SnapshotType.PERIODIC,
            individual_id="i0-1",
            t_monde=5,
            cycle=0,
            attempt_ref=None,
            owners=(rng,),
            versions={"runtime": "mvp-v1.2.1"},
        )

        expected = [world.random() for _ in range(5)]
        for _ in range(7):
            rng.stream("world").random()

        manager.restore(record.id, owners=(rng,))
        actual = [rng.stream("world").random() for _ in range(5)]

        self.assertEqual(actual, expected)

    def test_restore_does_not_rewind_technical_journal(self) -> None:
        manager, journal = self.make_manager()
        owner = FakeOwner("state", 1)

        record = manager.take(
            snapshot_type=SnapshotType.LETHAL_CHECKPOINT,
            individual_id="i0-1",
            t_monde=2,
            cycle=3,
            attempt_ref="attempt-a",
            owners=(owner,),
            versions={"runtime": "mvp-v1.2.1"},
            context={
                "command_source": "decision",
                "mask": [],
                "R_letal_consecutif": 0,
            },
        )
        length_after_checkpoint = len(journal.entries)

        journal.append(
            event_id=deterministic_id("journal-event-v1", "world", "lethal"),
            causal_event={"kind": "lethal_transition"},
        )
        length_before_restore = len(journal.entries)

        owner.value = 999
        manager.restore(record.id, owners=(owner,))

        self.assertEqual(owner.value, 1)
        self.assertGreater(len(journal.entries), length_before_restore)
        self.assertGreater(len(journal.entries), length_after_checkpoint)
        self.assertTrue(journal.verify())

    def test_snapshot_hash_tampering_is_detected(self) -> None:
        manager, _ = self.make_manager()
        owner = FakeOwner("state", 7)

        record = manager.take(
            snapshot_type=SnapshotType.BIRTH,
            individual_id="i0-1",
            t_monde=0,
            cycle=0,
            attempt_ref=None,
            owners=(owner,),
            versions={"runtime": "mvp-v1.2.1"},
        )

        manager._snapshots[record.id].payload["t_monde"] = 999  # deliberate tamper

        self.assertFalse(manager.verify(record.id))
        with self.assertRaises(ValueError):
            manager.restore(record.id, owners=(owner,))

    def test_lethal_checkpoint_requires_attempt_ref(self) -> None:
        manager, _ = self.make_manager()
        owner = FakeOwner("state", 1)

        with self.assertRaises(ValueError):
            manager.take(
                snapshot_type=SnapshotType.LETHAL_CHECKPOINT,
                individual_id="i0-1",
                t_monde=1,
                cycle=1,
                attempt_ref=None,
                owners=(owner,),
                versions={},
            )

    def test_restore_requires_exact_owner_set(self) -> None:
        manager, _ = self.make_manager()
        owner = FakeOwner("state", 1)

        record = manager.take(
            snapshot_type=SnapshotType.COPY,
            individual_id="i0-1",
            t_monde=8,
            cycle=0,
            attempt_ref=None,
            owners=(owner,),
            versions={"runtime": "mvp-v1.2.1"},
        )

        with self.assertRaises(ValueError):
            manager.restore(
                record.id,
                owners=(owner, FakeOwner("unexpected", 2)),
            )

    def test_snapshot_identity_is_independent_of_owner_argument_order(self) -> None:
        def take(order: tuple[str, str]):
            manager, _ = self.make_manager()
            owners = {
                "a": FakeOwner("a", 1),
                "b": FakeOwner("b", 2),
            }
            return manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id="i0-1",
                t_monde=3,
                cycle=0,
                attempt_ref=None,
                owners=tuple(owners[key] for key in order),
                versions={"runtime": "mvp-v1.2.1"},
            )

        first = take(("a", "b"))
        second = take(("b", "a"))

        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.id, second.id)


if __name__ == "__main__":
    unittest.main()
