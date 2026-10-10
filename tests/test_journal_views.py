from __future__ import annotations

import unittest

from lab.determinism import deterministic_id
from lab.journal import HashChainedJournal
from lab.journal_views import (
    AutobiographicalPolicy,
    EvaluationTrace,
    JournalViews,
)


class JournalViewsTests(unittest.TestCase):
    def append_event(
        self,
        journal: HashChainedJournal,
        *,
        kind: str,
        attempt_ref: str,
        sequence: int,
        extra: dict[str, object] | None = None,
    ) -> str:
        event_id = deterministic_id(
            "journal-event-v1",
            "fixture",
            attempt_ref,
            sequence,
            kind,
        )
        payload = {
            "kind": kind,
            "attempt_ref": attempt_ref,
            "t_monde": 1,
            "perceptible": f"value-{sequence}",
            "technical_counter": sequence,
        }
        payload.update(extra or {})
        journal.append(event_id=event_id, causal_event=payload)
        return event_id

    def policy(self) -> AutobiographicalPolicy:
        return AutobiographicalPolicy(
            version="autobio-v1",
            allowed_fields_by_kind={
                "observation_perceived": ("t_monde", "perceptible"),
                "command_experienced": ("t_monde", "perceptible"),
            },
        )

    def test_commit_projects_only_explicitly_allowed_fields(self) -> None:
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        event_ref = self.append_event(
            journal,
            kind="observation_perceived",
            attempt_ref="attempt-1",
            sequence=0,
        )

        views.commit_autobiographical(
            t_monde=1,
            attempt_ref="attempt-1",
            event_refs=(event_ref,),
            policy=self.policy(),
        )

        projected = views.autobiographical(
            policies={"autobio-v1": self.policy()},
        )

        self.assertEqual(
            projected,
            (
                {
                    "event_id": event_ref,
                    "kind": "observation_perceived",
                    "t_monde": 1,
                    "perceptible": "value-0",
                },
            ),
        )
        self.assertNotIn("attempt_ref", projected[0])
        self.assertNotIn("technical_counter", projected[0])

    def test_lethal_or_other_unlisted_event_cannot_be_committed(self) -> None:
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        lethal_ref = self.append_event(
            journal,
            kind="lethal_transition",
            attempt_ref="attempt-1",
            sequence=0,
        )

        with self.assertRaises(ValueError):
            views.commit_autobiographical(
                t_monde=1,
                attempt_ref="attempt-1",
                event_refs=(lethal_ref,),
                policy=self.policy(),
            )

    def test_commit_cannot_cross_attempts(self) -> None:
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        event_ref = self.append_event(
            journal,
            kind="observation_perceived",
            attempt_ref="attempt-1",
            sequence=0,
        )

        with self.assertRaises(ValueError):
            views.commit_autobiographical(
                t_monde=1,
                attempt_ref="attempt-2",
                event_refs=(event_ref,),
                policy=self.policy(),
            )

    def test_uncommitted_allowed_event_is_not_autobiographical(self) -> None:
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        self.append_event(
            journal,
            kind="observation_perceived",
            attempt_ref="attempt-cancelled",
            sequence=0,
        )

        self.assertEqual(
            views.autobiographical(
                policies={"autobio-v1": self.policy()},
            ),
            (),
        )

    def test_new_event_type_is_excluded_by_default(self) -> None:
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        event_ref = self.append_event(
            journal,
            kind="brand_new_event_type",
            attempt_ref="attempt-1",
            sequence=0,
        )

        with self.assertRaises(ValueError):
            views.commit_autobiographical(
                t_monde=1,
                attempt_ref="attempt-1",
                event_refs=(event_ref,),
                policy=self.policy(),
            )

    def test_technical_view_is_complete_and_append_only(self) -> None:
        journal = HashChainedJournal()
        views = JournalViews(journal=journal)
        first = self.append_event(
            journal,
            kind="observation_perceived",
            attempt_ref="attempt-1",
            sequence=0,
        )
        second = self.append_event(
            journal,
            kind="lethal_transition",
            attempt_ref="attempt-1",
            sequence=1,
        )

        self.assertEqual(
            tuple(entry.event_id for entry in views.technical()),
            (first, second),
        )
        self.assertTrue(journal.verify())

    def test_policy_cannot_expose_attempt_ref(self) -> None:
        policy = AutobiographicalPolicy(
            version="bad-v1",
            allowed_fields_by_kind={
                "observation_perceived": ("attempt_ref",),
            },
        )

        with self.assertRaises(ValueError):
            policy.validate()


class EvaluationTraceTests(unittest.TestCase):
    def test_evaluation_trace_is_separate_from_technical_journal(self) -> None:
        journal = HashChainedJournal()
        trace = EvaluationTrace()

        trace.append(kind="oracle_annotation", data={"truth": 1})

        self.assertEqual(len(trace.records), 1)
        self.assertEqual(journal.entries, ())


if __name__ == "__main__":
    unittest.main()
