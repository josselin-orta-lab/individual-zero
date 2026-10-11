"""Compact v1.3 custody proves bounded delivery without losing lived evidence.

These tests compare the same authorized world events to the historical
projection but do not interpret journal completeness as scientific proof.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from lab.compact_life_custody import BoundedLivedStream, BoundedPostCutDeltas
from lab.journal import HashChainedJournal
from lab.journal_views import JournalViews
from lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY
from lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY


def source_step(step: int, *, policy="stage2"):
    attempt = f"attempt:{step}"
    events = [
        (
            f"action:{step}",
            {
                "emitter": "stage2-scripted-agent",
                "kind": "command_experienced",
                "t_monde": step,
                "attempt_ref": attempt,
                "primitive": "attendre",
                "parameters": {},
                "oracle_canary": "never-project-me",
                "technical_secret": {"oracle_canary": "never-project-me"},
            },
        ),
        (
            f"world:{step}",
            {
                "emitter": "world_and_body",
                "kind": "world_transition_experienced",
                "t_monde": step,
                "attempt_ref": attempt,
                "position_after": {"x": 2, "y": 2},
                "body_after": {
                    "energy": 50.0, "food": 49.0,
                    "water": 50.0, "integrity": 100.0,
                },
                "effects": {"rest": "attendre"},
                "hidden_lethality_oracle": True,
            },
        ),
    ]
    if policy == "stage7":
        events.insert(0, (
            f"goal:{step}",
            {
                "emitter": "stage4-runtime",
                "kind": "active_goal_changed",
                "t_monde": step,
                "attempt_ref": attempt,
                "cycle": 1,
                "data": {"goal_type": "hydrate"},
                "ground_truth": "not-authorized",
            },
        ))
    return attempt, events


class LivedStreamTests(unittest.TestCase):
    def test_exact_authorized_projection_equals_old_journal_views(self):
        for policy_name, policy in (
            ("stage2", STAGE2_AUTOBIOGRAPHICAL_POLICY),
            ("stage7", STAGE7_AUTOBIOGRAPHICAL_POLICY),
        ):
            with self.subTest(policy=policy_name):
                attempt, raw = source_step(1, policy=policy_name)
                journal = HashChainedJournal()
                views = JournalViews(journal=journal)
                refs = []
                for event_id, event in raw:
                    journal.append(event_id=event_id, causal_event=event)
                    refs.append(event_id)
                views.commit_autobiographical(
                    t_monde=1, attempt_ref=attempt,
                    event_refs=refs, policy=policy,
                )
                legacy = views.autobiographical(
                    policies={policy.version: policy},
                )
                compact = BoundedLivedStream(
                    policy=policy, max_pending_events=6,
                )
                compact.commit_step(
                    t_monde=1, attempt_ref=attempt, experienced=raw,
                )
                result = compact.drain_for_memory()
                self.assertEqual(result, legacy)
                self.assertEqual(compact.pending_count, 0)
                self.assertNotIn("never-project-me", repr(result))
                self.assertNotIn("hidden_lethality_oracle", repr(result))
                self.assertNotIn("ground_truth", repr(result))
                self.assertNotIn("attempt_ref", repr(result))

    def test_six_hundred_accepted_step_projections_have_constant_footprint(self):
        stream = BoundedLivedStream(
            policy=STAGE2_AUTOBIOGRAPHICAL_POLICY, max_pending_events=2,
        )
        for step in range(1, 601):
            attempt, events = source_step(step)
            stream.commit_step(
                t_monde=step, attempt_ref=attempt, experienced=events,
            )
            self.assertEqual(stream.pending_count, 2)
            received = stream.drain_for_memory()
            self.assertEqual(len(received), 2)
            self.assertEqual(received[0]["t_monde"], step)
            self.assertEqual(stream.pending_count, 0)
        self.assertEqual(stream.last_step, 600)
        self.assertEqual(stream.drain_for_memory(), ())

    def test_backpressure_is_fail_closed_and_preserves_previous_events(self):
        stream = BoundedLivedStream(
            policy=STAGE2_AUTOBIOGRAPHICAL_POLICY, max_pending_events=2,
        )
        attempt, events = source_step(1)
        stream.commit_step(t_monde=1, attempt_ref=attempt, experienced=events)
        attempt2, events2 = source_step(2)
        with self.assertRaisesRegex(RuntimeError, "no silent eviction"):
            stream.commit_step(
                t_monde=2, attempt_ref=attempt2, experienced=events2,
            )
        self.assertEqual(stream.last_step, 1)
        self.assertEqual(stream.pending_count, 2)
        self.assertEqual(len(stream.drain_for_memory()), 2)
        stream.commit_step(
            t_monde=2, attempt_ref=attempt2, experienced=events2,
        )
        self.assertEqual(stream.last_step, 2)

    def test_invalid_attempt_duplicate_or_technical_event_rejects_atomically(self):
        stream = BoundedLivedStream(
            policy=STAGE2_AUTOBIOGRAPHICAL_POLICY, max_pending_events=4,
        )
        attempt, events = source_step(1)
        for invalid in (
            events + [events[0]],
            [(id, dict(event, attempt_ref="wrong")) for id, event in events],
            events + [("oracle", dict(events[0][1], kind="oracle_read"))],
            [events[0]],
        ):
            with self.subTest(reason=str(invalid[-1][0])):
                with self.assertRaises(ValueError):
                    stream.commit_step(
                        t_monde=1, attempt_ref=attempt,
                        experienced=invalid,
                    )
                self.assertEqual(stream.pending_count, 0)
                self.assertEqual(stream.last_step, 0)
        stream.commit_step(t_monde=1, attempt_ref=attempt, experienced=events)
        with self.assertRaises(ValueError):
            stream.commit_step(t_monde=1, attempt_ref=attempt, experienced=events)

    def test_peek_does_not_destroy_events_before_memory_acknowledges(self):
        stream = BoundedLivedStream(
            policy=STAGE2_AUTOBIOGRAPHICAL_POLICY, max_pending_events=2,
        )
        attempt, events = source_step(1)
        stream.commit_step(t_monde=1, attempt_ref=attempt, experienced=events)
        ready = stream.peek_for_memory()
        self.assertEqual(stream.pending_count, 2)
        ready[0]["primitive"] = "tampered"
        with self.assertRaisesRegex(ValueError, "differs from pending"):
            stream.acknowledge_memory(ready)
        self.assertEqual(stream.pending_count, 2)
        real = stream.peek_for_memory()
        self.assertEqual(real[0]["primitive"], "attendre")
        stream.acknowledge_memory(real)
        self.assertEqual(stream.pending_count, 0)
        self.assertEqual(stream.peek_for_memory(), ())

    def test_capacity_can_be_checked_before_any_world_command(self):
        stream = BoundedLivedStream(
            policy=STAGE2_AUTOBIOGRAPHICAL_POLICY, max_pending_events=2,
        )
        attempt, events = source_step(1)
        stream.commit_step(t_monde=1, attempt_ref=attempt, experienced=events)
        with self.assertRaisesRegex(RuntimeError, "no silent eviction"):
            stream.require_capacity(2)
        self.assertEqual(stream.pending_count, 2)
        self.assertEqual(stream.last_step, 1)
        stream.acknowledge_memory(stream.peek_for_memory())
        stream.require_capacity(2)

    def test_terminal_seals_without_posthumous_memory_delivery(self):
        stream = BoundedLivedStream(
            policy=STAGE2_AUTOBIOGRAPHICAL_POLICY, max_pending_events=2,
        )
        attempt, events = source_step(1)
        stream.commit_step(t_monde=1, attempt_ref=attempt, experienced=events)
        stream.seal_terminal()
        self.assertEqual(stream.pending_count, 0)
        with self.assertRaises(RuntimeError):
            stream.drain_for_memory()
        with self.assertRaises(RuntimeError):
            stream.commit_step(
                t_monde=2, attempt_ref="attempt:2",
                experienced=source_step(2)[1],
            )


class DeltaWindowTests(unittest.TestCase):
    def test_stage10_existing_publisher_kinds_map_to_actual_owners(self):
        window = BoundedPostCutDeltas(max_pending_updates=6)
        window.begin_cut(world_step=10)
        accepted = (
            ("value_needs", "td_update_published", "value_needs"),
            ("stage4-runtime", "kappa_update_published", "metacognition_health"),
            ("perception", "perceptual_precision_update_published", "perception"),
            ("stage4-runtime", "causal_safety_status_published", "causal_model"),
        )
        for n, (emitter, kind, owner) in enumerate(accepted):
            window.append_published_update(
                emitter=emitter, kind=kind, event_id=f"published:{n}",
                t_monde=10 + (n // 2),
                payload={"after": {"version": n + 1}},
            )
        frozen = window.freeze()
        self.assertEqual(
            tuple(item.owner_id for item in frozen.updates),
            tuple(x[2] for x in accepted),
        )
        self.assertEqual(frozen.cut_world_step, 10)
        self.assertEqual(window.pending_count, 4)
        window.acknowledge_published(frozen)
        self.assertEqual(window.pending_count, 0)
        window.begin_cut(world_step=12)

    def test_stale_private_rebase_cannot_consume_unseen_update(self):
        window = BoundedPostCutDeltas(max_pending_updates=3)
        window.begin_cut(world_step=5)
        window.append_published_update(
            emitter="stage4-runtime", kind="kappa_update_published",
            event_id="kappa:1", t_monde=5, payload={"after": {"kappa": 0.4}},
        )
        planned = window.freeze()
        window.append_published_update(
            emitter="value_needs", kind="td_update_published",
            event_id="td:2", t_monde=6, payload={"after": {"Q": 0.6}},
        )
        with self.assertRaisesRegex(ValueError, "changed during private"):
            window.acknowledge_published(planned)
        self.assertEqual(window.pending_count, 2)
        rebuilt = window.freeze()
        window.acknowledge_published(rebuilt)
        self.assertEqual(window.pending_count, 0)

    def test_payload_detached_and_canonical_token_detects_tampering(self):
        window = BoundedPostCutDeltas(max_pending_updates=2)
        window.begin_cut(world_step=1)
        payload = {"after": {"nested": [1, 2]}}
        window.append_published_update(
            emitter="value_needs", kind="td_update_published",
            event_id="td:1", t_monde=1, payload=payload,
        )
        payload["after"]["nested"].append(3)
        frozen = window.freeze()
        self.assertEqual(frozen.updates[0].payload["after"]["nested"], [1, 2])
        frozen.updates[0].payload["after"]["nested"].append(100)
        with self.assertRaises(ValueError):
            window.acknowledge_published(frozen)
        fresh = window.freeze()
        self.assertEqual(fresh.updates[0].payload["after"]["nested"], [1, 2])
        window.acknowledge_published(fresh)

    def test_unknown_owner_backdated_update_and_overflow_never_silently_drop(self):
        window = BoundedPostCutDeltas(max_pending_updates=1)
        window.begin_cut(world_step=5)
        with self.assertRaises(ValueError):
            window.append_published_update(
                emitter="oracle", kind="ground_truth", event_id="hidden:1",
                t_monde=5, payload={"oracle_canary": "hidden"},
            )
        with self.assertRaises(ValueError):
            window.append_published_update(
                emitter="value_needs", kind="td_update_published",
                event_id="old:1", t_monde=4, payload={},
            )
        window.append_published_update(
            emitter="value_needs", kind="td_update_published",
            event_id="ok:1", t_monde=5, payload={"after": 1},
        )
        with self.assertRaisesRegex(RuntimeError, "no silent loss"):
            window.append_published_update(
                emitter="value_needs", kind="td_update_published",
                event_id="ok:2", t_monde=5, payload={"after": 2},
            )
        self.assertEqual(window.pending_count, 1)
        self.assertEqual(window.freeze().updates[0].event_id, "ok:1")

    def test_terminal_prevents_posthumous_consolidation(self):
        window = BoundedPostCutDeltas(max_pending_updates=2)
        window.begin_cut(world_step=5)
        window.append_published_update(
            emitter="metacognition_health", kind="kappa_update_published",
            event_id="kappa:5", t_monde=5, payload={"after": 0.25},
        )
        window.seal_terminal()
        self.assertEqual(window.pending_count, 0)
        with self.assertRaises(RuntimeError):
            window.freeze()
        with self.assertRaises(RuntimeError):
            window.begin_cut(world_step=6)
        with self.assertRaises(RuntimeError):
            window.append_published_update(
                emitter="value_needs", kind="td_update_published",
                event_id="td:6", t_monde=6, payload={},
            )

    def test_independent_sequences_produce_same_digest(self):
        def run():
            window = BoundedPostCutDeltas(max_pending_updates=2)
            window.begin_cut(world_step=3)
            window.append_published_update(
                emitter="value_needs", kind="td_update_published",
                event_id="td:3", t_monde=3,
                payload={"after": {"Q": 0.7, "n": 10}},
            )
            return window.freeze().digest
        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
