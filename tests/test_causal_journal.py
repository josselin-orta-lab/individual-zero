from __future__ import annotations

import unittest

from lab.determinism import deterministic_id
from lab.journal import GENESIS_HASH, HashChainedJournal, JournalEntry


class HashChainedJournalTests(unittest.TestCase):
    def build_journal(self) -> HashChainedJournal:
        journal = HashChainedJournal()
        journal.append(
            event_id=deterministic_id("journal-event-v1", "scheduler", 1),
            causal_event={"kind": "step_opened", "t_monde": 1},
        )
        journal.append(
            event_id=deterministic_id("journal-event-v1", "scheduler", 2),
            causal_event={"kind": "cycle_opened", "t_monde": 1, "cycle": 1},
        )
        return journal

    def test_genesis_hash_is_32_zero_bytes_in_hex(self) -> None:
        self.assertEqual(GENESIS_HASH, "0" * 64)

    def test_chain_verifies_after_append(self) -> None:
        journal = self.build_journal()

        self.assertTrue(journal.verify())
        self.assertEqual(len(journal.entries), 2)
        self.assertEqual(journal.entries[0].previous_hash, GENESIS_HASH)
        self.assertEqual(journal.entries[1].previous_hash, journal.entries[0].event_hash)

    def test_same_events_produce_byte_identical_journal(self) -> None:
        first = self.build_journal()
        second = self.build_journal()

        self.assertEqual(first.canonical_bytes(), second.canonical_bytes())
        self.assertEqual(first.head_hash, second.head_hash)

    def test_noncausal_metadata_does_not_change_causal_hash(self) -> None:
        event_id = deterministic_id("journal-event-v1", "scheduler", 1)

        first = HashChainedJournal()
        first.append(
            event_id=event_id,
            causal_event={"kind": "step_opened", "t_monde": 1},
            noncausal_metadata={"t_systeme": "2026-10-08T10:00:00Z"},
        )

        second = HashChainedJournal()
        second.append(
            event_id=event_id,
            causal_event={"kind": "step_opened", "t_monde": 1},
            noncausal_metadata={"t_systeme": "different"},
        )

        self.assertEqual(first.head_hash, second.head_hash)
        self.assertEqual(first.canonical_bytes(), second.canonical_bytes())

    def test_event_identity_is_part_of_hash_chain(self) -> None:
        first = HashChainedJournal()
        first.append(
            event_id="a" * 64,
            causal_event={"kind": "same"},
        )

        second = HashChainedJournal()
        second.append(
            event_id="b" * 64,
            causal_event={"kind": "same"},
        )

        self.assertNotEqual(first.head_hash, second.head_hash)

    def test_mutated_entry_is_detected(self) -> None:
        journal = self.build_journal()
        original = journal.entries[0]

        journal._entries[0] = JournalEntry(  # noqa: SLF001 - deliberate tamper fixture
            index=original.index,
            event_id=original.event_id,
            previous_hash=original.previous_hash,
            event_hash=original.event_hash,
            causal_event={"kind": "tampered", "t_monde": 1},
        )

        self.assertFalse(journal.verify())


if __name__ == "__main__":
    unittest.main()
