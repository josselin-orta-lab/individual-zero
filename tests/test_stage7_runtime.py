from __future__ import annotations

import unittest

from i0.modules import StaticSafetyFacts
from i0.modules.memory import MemoryConfig
from lab.stage6_reference_fixture import build_stage6_reference_runtime
from lab.stage7_reference_fixture import build_stage7_reference_runtime
from lab.stage7_runtime import (
    STAGE7_AUTOBIOGRAPHICAL_POLICY,
    Stage7Config,
    Stage7Runtime,
)
from lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY
from lab.world import Position, WorldLayout


def autobiography(runtime):
    return runtime.stage3.substrate.views.autobiographical(
        policies={
            STAGE2_AUTOBIOGRAPHICAL_POLICY.version:
                STAGE2_AUTOBIOGRAPHICAL_POLICY,
            STAGE7_AUTOBIOGRAPHICAL_POLICY.version:
                STAGE7_AUTOBIOGRAPHICAL_POLICY,
        }
    )


class Stage7RuntimeTests(unittest.TestCase):
    def test_memory_reads_only_committed_autobiographical_events(self) -> None:
        runtime = build_stage7_reference_runtime()
        for _ in range(4):
            runtime.run_step()

        visible = autobiography(runtime)
        visible_ids = {event["event_id"] for event in visible}

        self.assertGreater(len(runtime.memory.episodes), 0)
        for episode in runtime.memory.episodes:
            self.assertTrue(set(episode.event_refs).issubset(visible_ids))

        technical_access = [
            entry.causal_event
            for entry in runtime.journal.entries
            if entry.causal_event.get("kind") == "memory_autobiographical_access"
        ]
        self.assertGreater(len(technical_access), 0)
        self.assertFalse(
            any(
                event.get("kind") == "memory_autobiographical_access"
                for event in visible
            )
        )

    def test_closed_episode_becomes_recall_candidate_through_memory_contribution(self) -> None:
        runtime = build_stage7_reference_runtime()
        for _ in range(5):
            runtime.run_step()

        recalls = [
            entry.causal_event
            for entry in runtime.journal.entries
            if entry.causal_event.get("kind") == "memory_recall_proposed"
        ]
        self.assertGreater(len(runtime.memory.episodes), 0)
        self.assertGreater(len(recalls), 0)

        admitted_memory_messages = [
            entry.causal_event
            for entry in runtime.journal.entries
            if entry.causal_event.get("kind") == "bus_message_admitted"
            and entry.causal_event.get("data", {})
            .get("message", {})
            .get("producer") == "memory"
        ]
        self.assertGreater(len(admitted_memory_messages), 0)

    def test_extended_autobiography_contains_goal_and_s_t_but_not_budget_or_hashes(self) -> None:
        runtime = build_stage7_reference_runtime()
        for _ in range(3):
            runtime.run_step()

        visible = autobiography(runtime)
        kinds = {event["kind"] for event in visible}
        encoded = repr(visible)

        self.assertIn("s_t_published", kinds)
        self.assertIn("active_goal_changed", kinds)
        self.assertNotIn("compute_charge", kinds)
        self.assertNotIn("memory_autobiographical_access", kinds)
        self.assertNotIn("attempt_ref", encoded)
        self.assertNotIn("event_hash", encoded)
        self.assertNotIn("previous_hash", encoded)

    def test_lethal_cancelled_branch_never_enters_memory(self) -> None:
        stage6 = build_stage6_reference_runtime()
        lethal_layout = WorldLayout(
            water_sources=frozenset({Position(2, 2)}),
            lethal_zones=frozenset({Position(2, 2)}),
        )
        runtime = Stage7Runtime(
            world_config=stage6.world.config,
            layout=lethal_layout,
            safety_config=stage6.stage3.substrate.safety._config,
            safety_facts=StaticSafetyFacts(),
            protected_integrity_threshold=20.0,
            config=Stage7Config(
                version="stage7-lethal-test-v1",
                stage6=stage6.stage6_config,
                memory=MemoryConfig(
                    version="p34-lethal-test-v1",
                    prediction_error_multiplier=2.0,
                    max_episode_steps=2,
                    link_delta_steps=2,
                    recall_threshold=0.25,
                    recall_weight_recency=0.5,
                    recall_weight_importance=0.25,
                    recall_weight_relevance=1.0,
                    recall_recency_scale_steps=20,
                    contribution_ttl_steps=4,
                ),
            ),
            equipment=stage6.equipment,
        )

        result = runtime.run_step()

        technical_kinds = [
            entry.causal_event.get("kind")
            for entry in runtime.journal.entries
        ]
        self.assertIn("lethal_transition_detected", technical_kinds)
        self.assertIn(result.execution_status, {"applied", "safety_block"})
        visible = autobiography(runtime)
        self.assertFalse(
            any("lethal" in str(event.get("kind", "")) for event in visible)
        )
        self.assertFalse(
            any(
                "lethal" in repr(episode.as_dict()).lower()
                for episode in runtime.memory.episodes
            )
        )

    def test_stage7_reference_execution_is_deterministic(self) -> None:
        def execute():
            runtime = build_stage7_reference_runtime()
            for _ in range(8):
                runtime.run_step()
            return (
                runtime.journal.canonical_bytes(),
                {
                    owner.owner_id: owner.export_causal_state()
                    for owner in runtime.causal_owners
                },
            )

        journal_a, state_a = execute()
        journal_b, state_b = execute()

        self.assertEqual(journal_a, journal_b)
        self.assertEqual(state_a, state_b)


if __name__ == "__main__":
    unittest.main()
