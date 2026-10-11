"""External Bench audits copied journal bytes without any live I0 or Oracle."""
from __future__ import annotations

import unittest

from lab.bench import EvaluationBench
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.journal_views import EvaluationTrace


class IndependentBenchExportTests(unittest.TestCase):
    def test_bench_without_oracle_audits_detached_export_without_mutation(self):
        journal = HashChainedJournal()
        journal.append(
            event_id="event:1",
            causal_event={
                "emitter": "fixture", "kind": "technical_statement",
                "t_monde": 0, "data": {"visible_to_individual": False},
            },
        )
        original = journal.canonical_bytes()
        head = journal.head_hash
        trace = EvaluationTrace()
        bench = EvaluationBench(trace=trace)
        result = bench.verify_exported_journal(
            original, expected_head=head, expected_count=1,
        )
        self.assertEqual(result.occurrences, 1)
        self.assertEqual(result.world_steps_closed, 0)
        self.assertFalse(result.as_dict()["physical_truth_verified"])
        self.assertEqual(journal.canonical_bytes(), original)
        self.assertEqual(journal.head_hash, head)
        self.assertTrue(journal.verify())
        self.assertEqual(len(trace.records), 1)
        self.assertEqual(trace.records[0].kind, "journal_export_verified")
        self.assertFalse(trace.records[0].data["physical_truth_verified"])
        self.assertEqual(bench.metrics.lethal_transitions, 0)
        self.assertEqual(bench.metrics.safety_blocks, 0)

    def test_false_export_does_not_create_verified_trace(self):
        journal = HashChainedJournal()
        journal.append(event_id="event:1", causal_event={
            "kind": "technical_statement", "t_monde": 0,
        })
        original = journal.canonical_bytes()
        invalid = original.replace(b"technical_statement", b"technical_falsehood")
        trace = EvaluationTrace()
        bench = EvaluationBench(trace=trace)
        with self.assertRaises(ValueError):
            bench.verify_exported_journal(
                invalid, expected_head=journal.head_hash,
                expected_count=1,
            )
        self.assertEqual(trace.records, ())
        self.assertEqual(journal.canonical_bytes(), original)

    def test_bench_journal_verification_is_oracle_independent(self):
        journal = HashChainedJournal()
        journal.append(event_id="event:1", causal_event={
            "kind": "technical_statement", "t_monde": 0,
        })
        result = EvaluationBench(trace=EvaluationTrace()).verify_exported_journal(
            journal.canonical_bytes(),
            expected_head=journal.head_hash,
            expected_count=len(journal.entries),
        )
        self.assertEqual(
            result.head_hash,
            audit_export_bytes(journal.canonical_bytes()).head_hash,
        )


if __name__ == "__main__":
    unittest.main()
