from __future__ import annotations

import inspect
import unittest

from i0.contracts import STVersion
from i0.modules.memory import EpisodicMemory, MemoryConfig


def config(**overrides) -> MemoryConfig:
    values = dict(
        version="stage7-memory-test-v1",
        prediction_error_multiplier=2.0,
        max_episode_steps=2,
        link_delta_steps=2,
        recall_threshold=0.5,
        recall_weight_recency=1.0,
        recall_weight_importance=0.2,
        recall_weight_relevance=1.0,
        recall_recency_scale_steps=10,
        contribution_ttl_steps=4,
    )
    values.update(overrides)
    return MemoryConfig(**values)


def transition(event_id: str, t: int, water: float = 50.0):
    return {
        "event_id": event_id,
        "kind": "world_transition_experienced",
        "t_monde": t,
        "position_after": {"x": 2, "y": 2},
        "body_after": {
            "energy": 50.0,
            "food": 60.0,
            "water": water,
            "integrity": 100.0,
        },
        "effects": {},
    }


class EpisodicMemoryTests(unittest.TestCase):
    def test_max_length_closes_episode(self) -> None:
        memory = EpisodicMemory(config(max_episode_steps=2))

        first = memory.ingest_autobiographical(
            [transition("e1", 1)],
            current_t_monde=2,
            current_goal_ref="goal:drink",
            current_reward=0.0,
        )
        second = memory.ingest_autobiographical(
            [transition("e1", 1), transition("e2", 2)],
            current_t_monde=3,
            current_goal_ref="goal:drink",
            current_reward=0.5,
        )

        self.assertEqual(first, ())
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0].boundary_type, "max_length")
        self.assertEqual(second[0].event_refs, ("e1", "e2"))

    def test_large_lived_prediction_error_closes_episode(self) -> None:
        memory = EpisodicMemory(config(max_episode_steps=20))
        comparison = {
            "event_id": "cmp",
            "kind": "agency_comparison",
            "t_monde": 4,
            "data": {
                "effects": [
                    {
                        "status": "nonconforming",
                        "variable": "water",
                        "predicted": 2.0,
                        "observed": 5.0,
                        "precision": 1.0,
                    }
                ]
            },
        }

        closed = memory.ingest_autobiographical(
            [transition("e1", 3), comparison],
            current_t_monde=5,
            current_goal_ref="goal:drink",
            current_reward=0.0,
        )

        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].boundary_type, "prediction_error")
        self.assertEqual(closed[0].surprise, 3.0)

    def test_seen_autobiographical_events_are_not_ingested_twice(self) -> None:
        memory = EpisodicMemory(config(max_episode_steps=2))
        events = [transition("e1", 1)]

        memory.ingest_autobiographical(
            events,
            current_t_monde=2,
            current_goal_ref=None,
            current_reward=0.0,
        )
        memory.ingest_autobiographical(
            events,
            current_t_monde=3,
            current_goal_ref=None,
            current_reward=0.0,
        )

        state = memory.export_causal_state()
        self.assertEqual(state["open_event_refs"], ["e1"])

    def test_recall_uses_recency_importance_and_exact_goal_relevance(self) -> None:
        memory = EpisodicMemory(
            config(
                max_episode_steps=1,
                recall_threshold=0.1,
                recall_weight_recency=0.0,
                recall_weight_importance=0.0,
                recall_weight_relevance=1.0,
            )
        )
        memory.ingest_autobiographical(
            [transition("e1", 1)],
            current_t_monde=2,
            current_goal_ref="goal:drink",
            current_reward=0.0,
        )
        st = STVersion(
            individual_id="i0",
            version="S_t:test",
            cycle=1,
            t_monde=2,
            fixed={
                "active_goal": {"id": "goal:drink"},
            },
            competitive=(),
        )

        recalled = memory.recall(st=st, t_monde=2)

        self.assertEqual(len(recalled), 1)
        self.assertEqual(recalled[0].relevance, 1.0)
        self.assertEqual(recalled[0].score, 1.0)

    def test_spontaneous_recall_is_a_normal_memory_contribution(self) -> None:
        memory = EpisodicMemory(config(max_episode_steps=1, recall_threshold=0.0))
        memory.ingest_autobiographical(
            [transition("e1", 1)],
            current_t_monde=2,
            current_goal_ref=None,
            current_reward=0.0,
        )

        contribution = memory.spontaneous_contribution(
            st=None,
            t_monde=2,
            cycle=1,
        )

        self.assertIsNotNone(contribution)
        self.assertEqual(contribution.emitter_module, "memory")
        self.assertEqual(contribution.signal_family, "memory_recall")
        self.assertEqual(contribution.type, "response")

    def test_memory_module_has_no_technical_journal_or_oracle_dependency(self) -> None:
        import i0.modules.memory as module

        source = inspect.getsource(module)
        forbidden = (
            "HashChainedJournal",
            "JournalEntry",
            "EvaluationTrace",
            "lab.journal",
            "lab.oracle",
            "oracle_truth",
        )
        self.assertFalse(any(token in source for token in forbidden))


if __name__ == "__main__":
    unittest.main()
