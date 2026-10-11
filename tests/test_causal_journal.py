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

    def test_append_owns_nested_payload_after_caller_mutation(self) -> None:
        source = {
            "kind": "external_input_received",
            "data": {"position": {"x": 3, "y": 2}},
            "evidence_refs": ["source-1"],
        }
        journal = HashChainedJournal()
        event_id = deterministic_id(
            "journal-event-v1", "scenario", 1, "external-input",
        )
        entry = journal.append(event_id=event_id, causal_event=source)
        expected_bytes = journal.canonical_bytes()
        expected_hash = journal.head_hash

        source["data"]["position"]["x"] = 999
        source["evidence_refs"].append("unpublished")
        source["new_causal_key"] = "after append"

        self.assertEqual(entry.causal_event["data"]["position"],
                         {"x": 3, "y": 2})
        self.assertEqual(entry.causal_event["evidence_refs"], ["source-1"])
        self.assertIs(journal.get(event_id), entry)
        self.assertEqual(journal.canonical_bytes(), expected_bytes)
        self.assertEqual(journal.head_hash, expected_hash)
        self.assertTrue(journal.verify())

        independent = HashChainedJournal()
        independent.append(
            event_id=event_id,
            causal_event={
                "kind": "external_input_received",
                "data": {"position": {"x": 3, "y": 2}},
                "evidence_refs": ["source-1"],
            },
        )
        self.assertEqual(independent.canonical_bytes(), expected_bytes)
        self.assertEqual(independent.head_hash, expected_hash)

    def test_entry_export_cannot_mutate_nested_journal_history(self) -> None:
        journal = HashChainedJournal()
        event_id = deterministic_id(
            "journal-event-v1", "perception", 1, "capture",
        )
        entry = journal.append(
            event_id=event_id,
            causal_event={
                "kind": "perceptual_capture",
                "data": {"position": {"x": 2, "y": 3}},
                "evidence_refs": ["physical-source"],
            },
        )
        frozen_bytes = journal.canonical_bytes()
        exported = entry.as_dict()
        exported["causal_event"]["data"]["position"]["x"] = 999
        exported["causal_event"]["evidence_refs"].append("retroactive")
        exported["causal_event"]["kind"] = "fake_event"
        self.assertEqual(
            journal.get(event_id).causal_event["data"]["position"],
            {"x": 2, "y": 3},
        )
        self.assertEqual(
            journal.get(event_id).causal_event["evidence_refs"],
            ["physical-source"],
        )
        self.assertEqual(journal.canonical_bytes(), frozen_bytes)
        self.assertTrue(journal.verify())

    def test_uncanonical_nested_input_fails_before_journal_append(self) -> None:
        journal = self.build_journal()
        prior_bytes = journal.canonical_bytes()
        prior_hash = journal.head_hash
        with self.assertRaises(TypeError):
            journal.append(
                event_id=deterministic_id(
                    "journal-event-v1", "scenario", "malformed",
                ),
                causal_event={
                    "kind": "external_input_received",
                    "payload": {"invalid_set": {1, 2}},
                },
            )
        self.assertEqual(journal.canonical_bytes(), prior_bytes)
        self.assertEqual(journal.head_hash, prior_hash)
        self.assertTrue(journal.verify())

    def test_direct_entry_get_and_append_views_cannot_edit_nested_history(self) -> None:
        original = {
            "kind": "perceptual_capture",
            "data": {"position": {"x": 2, "y": 3}},
            "evidence_refs": ["physical-source"],
        }
        journal = HashChainedJournal()
        event_id = deterministic_id(
            "journal-event-v1", "perception", "direct-view-v1",
        )
        appended = journal.append(event_id=event_id, causal_event=original)
        before = journal.canonical_bytes()
        head = journal.head_hash

        # Occurrence identity, unlike the nested payload, must remain stable.
        self.assertIs(journal.get(event_id), appended)
        self.assertIs(journal.entries[0], appended)
        for view in (appended, journal.get(event_id), journal.entries[0]):
            with self.subTest(view=view.event_id):
                data = view.causal_event["data"]
                data["position"]["x"] = 999
                view.causal_event["evidence_refs"].append("fabricated")
                view.causal_event.get("data")["position"]["y"] = -1
                copied_items = dict(view.causal_event.items())
                copied_items["data"]["position"]["x"] = 404
                copied = view.causal_event.copy()
                copied["evidence_refs"].clear()
                with self.assertRaises(TypeError):
                    view.causal_event["kind"] = "tampered"
                self.assertEqual(
                    view.causal_event["data"]["position"], {"x": 2, "y": 3},
                )
                self.assertEqual(
                    view.causal_event["evidence_refs"], ["physical-source"],
                )
                self.assertEqual(journal.canonical_bytes(), before)
                self.assertEqual(journal.head_hash, head)
                self.assertTrue(journal.verify())

    def test_direct_view_preserves_list_type_and_detached_export(self) -> None:
        journal = HashChainedJournal()
        event_id = deterministic_id(
            "journal-event-v1", "autobiographical-view", "direct-view-v1",
        )
        entry = journal.append(
            event_id=event_id,
            causal_event={
                "kind": "auto_segment_commit",
                "event_refs": ["capture:1"],
                "filter_version": "autobio-v1",
                "data": {"nested": [{"count": 1}]},
            },
        )
        self.assertIsInstance(entry.causal_event["event_refs"], list)
        self.assertIsInstance(entry.causal_event.get("event_refs"), list)
        before = journal.canonical_bytes()
        for copied in (entry.as_dict(), dict(entry.causal_event)):
            payload = (
                copied["causal_event"]
                if "causal_event" in copied
                else copied
            )
            payload["event_refs"].append("fabricated")
            payload["data"]["nested"][0]["count"] = 777
        self.assertEqual(entry.causal_event["event_refs"], ["capture:1"])
        self.assertEqual(
            entry.causal_event["data"]["nested"], [{"count": 1}],
        )
        self.assertEqual(journal.canonical_bytes(), before)
        self.assertTrue(journal.verify())

    def test_manually_constructed_entry_defends_its_nested_constructor_input(self) -> None:
        source = {
            "kind": "synthetic",
            "data": {"nested": [1, 2]},
        }
        entry = JournalEntry(
            index=0, event_id="direct-view-unit",
            previous_hash=GENESIS_HASH, event_hash="1" * 64,
            causal_event=source,
        )
        source["data"]["nested"][0] = 99
        self.assertEqual(entry.causal_event["data"]["nested"], [1, 2])
        entry.causal_event["data"]["nested"][1] = 77
        self.assertEqual(entry.causal_event["data"]["nested"], [1, 2])
        self.assertEqual(
            entry.as_dict()["causal_event"]["data"]["nested"], [1, 2],
        )

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
