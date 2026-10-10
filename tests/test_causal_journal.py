from __future__ import annotations

import unittest

from lab.determinism import canonical_causal_bytes, deterministic_id, sha256_hex
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

    def test_duplicate_event_id_rejected_without_modifying_journal(self) -> None:
        journal = self.build_journal()
        before = journal.canonical_bytes()
        original = journal.entries[0]
        with self.assertRaisesRegex(ValueError, "duplicate technical journal"):
            journal.append(
                event_id=original.event_id,
                causal_event={"kind": "unrelated-second-physical-transition"},
            )
        self.assertEqual(journal.canonical_bytes(), before)
        self.assertIs(journal.get(original.event_id), original)
        self.assertEqual(len(journal.entries), 2)
        self.assertTrue(journal.verify())

    def test_event_id_requires_a_string(self) -> None:
        journal = self.build_journal()
        before = journal.canonical_bytes()
        for invalid in (None, 123, True, ""):
            with self.subTest(event_id=invalid):
                with self.assertRaisesRegex(ValueError, "nonempty string"):
                    journal.append(
                        event_id=invalid,  # type: ignore[arg-type]
                        causal_event={"kind": "invalid_identity"},
                    )
        self.assertEqual(journal.canonical_bytes(), before)
        self.assertTrue(journal.verify())

    def test_noncanonical_unicode_event_id_is_rejected(self) -> None:
        journal = self.build_journal()
        prior = journal.canonical_bytes()
        with self.assertRaisesRegex(ValueError, "NFC-normalized"):
            journal.append(
                event_id="physical-source:e\u0301",
                causal_event={"kind": "invalid_equivalent_source_id"},
            )
        self.assertEqual(journal.canonical_bytes(), prior)
        self.assertTrue(journal.verify())

    def test_rehashed_duplicate_event_still_fails_integrity_verification(self) -> None:
        journal = self.build_journal()
        first, second = journal.entries
        forged_id = first.event_id
        # This entry has a valid SHA-256 link, but duplicates the original ID.
        forged_hash = sha256_hex(
            bytes.fromhex(first.event_hash)
            + canonical_causal_bytes({
                "event_id": forged_id,
                "causal_event": second.causal_event,
            })
        )
        journal._entries[1] = JournalEntry(
            index=1, event_id=forged_id,
            previous_hash=first.event_hash,
            event_hash=forged_hash,
            causal_event=second.causal_event,
        )
        self.assertFalse(journal.verify())

    def test_lookup_index_corruption_cannot_validate(self) -> None:
        journal = self.build_journal()
        journal._by_id.pop(journal.entries[0].event_id)
        self.assertFalse(journal.verify())

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
