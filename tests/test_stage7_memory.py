from __future__ import annotations

import inspect
import unittest

from i0.contracts import STVersion
from i0.modules.goal_manager import GoalManager, GoalManagerConfig
from i0.modules.memory import EpisodicMemory, Intention, MemoryConfig


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

    def test_observable_zone_change_closes_episode(self) -> None:
        memory = EpisodicMemory(config(max_episode_steps=20))
        memory.ingest_autobiographical(
            [transition("z1", 1)],
            current_t_monde=2,
            current_goal_ref=None,
            current_reward=0.0,
            current_zone_ref="zone:A",
        )

        closed = memory.ingest_autobiographical(
            [transition("z1", 1), transition("z2", 2)],
            current_t_monde=3,
            current_goal_ref=None,
            current_reward=0.0,
            current_zone_ref="zone:B",
        )

        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].boundary_type, "zone_change")

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

    def test_dated_intention_uses_goal_manager_deadline_pressure(self) -> None:
        memory = EpisodicMemory(config())
        manager = GoalManager(
            GoalManagerConfig(
                version="goal-intention-test-v1",
                p_min=0.1,
                replacement_hysteresis=0.1,
                critical_pressure=0.9,
                impossible_failures_required=2,
                refractory_steps=3,
                deadline_weight=0.5,
                deadline_urgency_horizon_steps=10,
                deadline_urgency_form="linear",
            )
        )
        memory.create_intention(
            Intention(
                id="intent:drink",
                goal_type="drink",
                target="water",
                trigger_type="time",
                trigger_value=5,
                deadline_step=10,
                base_pressure=0.2,
                monitoring="strategic",
                cost_uc=1,
                wake_authorized=True,
            )
        )

        before = manager.prospective_pressure(
            base_pressure=0.2,
            remaining_steps=10,
        )
        near = manager.prospective_pressure(
            base_pressure=0.2,
            remaining_steps=1,
        )
        self.assertEqual(before, 0.2)
        self.assertGreater(near, before)

        results = memory.check_intentions(
            st=None,
            t_monde=5,
            cycle=1,
            pressure_fn=manager.prospective_pressure,
        )
        triggered = [result for result in results if result.triggered]
        self.assertEqual(len(triggered), 1)
        self.assertEqual(
            triggered[0].goal_proposal.source,
            "prospective_memory",
        )
        self.assertEqual(
            triggered[0].goal_proposal.current_pressure,
            manager.prospective_pressure(
                base_pressure=0.2,
                remaining_steps=5,
            ),
        )

    def test_intention_has_only_one_active_candidacy(self) -> None:
        memory = EpisodicMemory(config())
        memory.create_intention(
            Intention(
                id="intent:once",
                goal_type="drink",
                target="water",
                trigger_type="time",
                trigger_value=1,
                deadline_step=None,
                base_pressure=0.5,
                monitoring="spontaneous",
                cost_uc=0,
                wake_authorized=False,
            )
        )
        pressure = lambda **kwargs: kwargs["base_pressure"]

        first = memory.check_intentions(
            st=None,
            t_monde=1,
            cycle=1,
            pressure_fn=pressure,
        )
        second = memory.check_intentions(
            st=None,
            t_monde=1,
            cycle=2,
            pressure_fn=pressure,
        )

        self.assertTrue(first[0].triggered)
        self.assertFalse(second[0].triggered)

    def test_wake_index_is_derived_from_pending_dated_intentions(self) -> None:
        memory = EpisodicMemory(config())
        intention = Intention(
            id="intent:wake",
            goal_type="drink",
            target="water",
            trigger_type="time",
            trigger_value=8,
            deadline_step=8,
            base_pressure=0.3,
            monitoring="strategic",
            cost_uc=1,
            wake_authorized=True,
        )
        memory.create_intention(intention)

        self.assertEqual(memory.wake_deadline_index, {"intent:wake": 8})
        self.assertEqual(len(memory.intentions), 1)

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
