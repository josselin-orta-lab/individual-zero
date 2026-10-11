"""Independent auditor detects buried Oracle secrets in rehashed I0 records.

A benign technical oracle_access=False fact remains legal; nested raw
oracle_canary / oracle_ground_truth keys are never legitimate lived evidence.
"""
from __future__ import annotations

import unittest

from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal


def exported_stopped_step(*, extra):
    journal = HashChainedJournal()
    journal.append(
        event_id="opened",
        causal_event={
            "emitter": "scheduler", "kind": "step_opened",
            "t_monde": 1, "attempt_ref": "attempt:1",
            "data": {"annotations": [extra]},
        },
    )
    journal.append(
        event_id="closed",
        causal_event={
            "emitter": "scheduler", "kind": "step_closed",
            "t_monde": 1, "attempt_ref": "attempt:1",
            "data": {
                "outcome": "blocked",
                "applied_command_count": 0,
                "world_advance_count": 0,
            },
        },
    )
    assert journal.verify()
    return journal.canonical_bytes()


class NestedOracleTruthAuditTests(unittest.TestCase):
    def test_buried_truth_keys_are_forbidden_with_valid_sha_chain(self):
        for hidden in ("oracle_canary", "oracle_ground_truth"):
            with self.subTest(field=hidden):
                exported = exported_stopped_step(extra={
                    "deeply_nested": {"items": [{hidden: "secret"}]},
                })
                with self.assertRaisesRegex(ValueError, "oracle"):
                    audit_export_bytes(exported)

    def test_nonsecret_negative_oracle_access_flag_is_permitted(self):
        exported = exported_stopped_step(extra={"oracle_access": False})
        result = audit_export_bytes(exported)
        self.assertEqual(result.world_steps_closed, 1)
        self.assertEqual(result.terminal_deaths, 0)


if __name__ == "__main__":
    unittest.main()
