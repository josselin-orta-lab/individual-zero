from __future__ import annotations

import unittest

from i0.config import (
    MVP_PHASE1_PRODUCER_ORDER,
    build_ontology_registry,
    build_schema_registry,
)
from lab.bus import InMemoryBus, ProducerBuffer
from lab.journal import HashChainedJournal


def journal_event_payload() -> dict[str, object]:
    return {
        "n": 1,
        "type": "fixture",
        "charge": {},
        "provenance": [],
        "emp_prec": "0" * 64,
        "emp": "1" * 64,
    }


class InMemoryBusTests(unittest.TestCase):
    def make_bus(self) -> tuple[InMemoryBus, HashChainedJournal]:
        journal = HashChainedJournal()
        bus = InMemoryBus(
            schemas=build_schema_registry(),
            ontology=build_ontology_registry(),
            producer_order=MVP_PHASE1_PRODUCER_ORDER,
            journal=journal,
        )
        return bus, journal

    def test_canonical_pour_is_independent_of_buffer_argument_order(self) -> None:
        def run(reverse: bool) -> tuple[tuple[str, ...], bytes]:
            bus, journal = self.make_bus()
            perception = ProducerBuffer("perception")
            planning = ProducerBuffer("planning")

            perception.publish(
                schema_name="JournalEvent",
                schema_version="1.0",
                payload=journal_event_payload(),
                semantic_terms=("individual",),
            )
            planning.publish(
                schema_name="JournalEvent",
                schema_version="1.0",
                payload=journal_event_payload(),
                semantic_terms=("tool",),
            )

            buffers = [perception, planning]
            if reverse:
                buffers.reverse()

            bus.pour(
                buffers=buffers,
                t_monde=1,
                cycle=1,
                attempt_ref="attempt-1",
            )
            return (
                tuple(message.producer for message in bus.available),
                journal.canonical_bytes(),
            )

        producers_a, journal_a = run(False)
        producers_b, journal_b = run(True)

        self.assertEqual(producers_a, ("perception", "planning"))
        self.assertEqual(producers_a, producers_b)
        self.assertEqual(journal_a, journal_b)

    def test_unknown_semantic_term_is_rejected_and_logged(self) -> None:
        bus, journal = self.make_bus()
        buffer = ProducerBuffer("perception")
        buffer.publish(
            schema_name="JournalEvent",
            schema_version="1.0",
            payload=journal_event_payload(),
            semantic_terms=("term_that_does_not_exist",),
        )

        results = bus.pour(
            buffers=(buffer,),
            t_monde=1,
            cycle=1,
            attempt_ref="attempt-1",
        )

        self.assertFalse(results[0].accepted)
        self.assertEqual(results[0].violation.code, "unknown_semantic_term")
        self.assertEqual(bus.available, ())
        self.assertTrue(journal.verify())
        self.assertEqual(
            journal.entries[-1].causal_event["kind"],
            "bus_message_rejected",
        )

    def test_unknown_major_schema_version_is_rejected_and_logged(self) -> None:
        bus, journal = self.make_bus()
        buffer = ProducerBuffer("perception")
        buffer.publish(
            schema_name="JournalEvent",
            schema_version="2.0",
            payload=journal_event_payload(),
            semantic_terms=("individual",),
        )

        results = bus.pour(
            buffers=(buffer,),
            t_monde=1,
            cycle=1,
            attempt_ref="attempt-1",
        )

        self.assertFalse(results[0].accepted)
        self.assertEqual(results[0].violation.code, "unknown_major_version")
        self.assertEqual(
            journal.entries[-1].causal_event["kind"],
            "bus_message_rejected",
        )

    def test_unknown_causal_field_is_rejected_and_logged(self) -> None:
        bus, journal = self.make_bus()
        buffer = ProducerBuffer("planning")
        payload = journal_event_payload()
        payload["hidden_input"] = "not-declared"
        buffer.publish(
            schema_name="JournalEvent",
            schema_version="1.0",
            payload=payload,
            semantic_terms=("tool",),
        )

        results = bus.pour(
            buffers=(buffer,),
            t_monde=1,
            cycle=1,
            attempt_ref="attempt-1",
        )

        self.assertFalse(results[0].accepted)
        self.assertEqual(results[0].violation.code, "unknown_causal_field")
        self.assertTrue(journal.verify())

    def test_local_order_within_one_producer_is_preserved(self) -> None:
        bus, _ = self.make_bus()
        buffer = ProducerBuffer("perception")
        first = journal_event_payload()
        first["n"] = 1
        second = journal_event_payload()
        second["n"] = 2

        buffer.publish(
            schema_name="JournalEvent",
            schema_version="1.0",
            payload=first,
            semantic_terms=("individual",),
        )
        buffer.publish(
            schema_name="JournalEvent",
            schema_version="1.0",
            payload=second,
            semantic_terms=("individual",),
        )

        bus.pour(
            buffers=(buffer,),
            t_monde=1,
            cycle=1,
            attempt_ref="attempt-1",
        )

        self.assertEqual(
            tuple(message.local_sequence for message in bus.available),
            (0, 1),
        )
        self.assertEqual(
            tuple(message.payload["n"] for message in bus.available),
            (1, 2),
        )

    def test_drain_returns_immutable_snapshot_and_clears_bus_storage(self) -> None:
        bus, _ = self.make_bus()
        buffer = ProducerBuffer("perception")
        buffer.publish(
            schema_name="JournalEvent",
            schema_version="1.0",
            payload=journal_event_payload(),
            semantic_terms=("individual",),
        )
        bus.pour(
            buffers=(buffer,),
            t_monde=1,
            cycle=1,
            attempt_ref="attempt-1",
        )

        drained = bus.drain_available()

        self.assertEqual(len(drained), 1)
        self.assertEqual(bus.available, ())


if __name__ == "__main__":
    unittest.main()
