"""Actual mortal Stage-10 sleeping steps drive six semantic passes and h."""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
import unittest

from i0.modules.consolidation_batch import BatchSelectionPolicy
from i0.modules.consolidation_budget import ConsolidationBudgetConfig
from i0.modules.consolidation_replay_agenda import ReplayAgendaPolicy
from i0.modules.consolidation_semantics import SemanticPassPolicy
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage10_runtime import Stage10Runtime


def configured_runtime(*, maximum_passes_per_sleep_step=1):
    base = build_stage10_reference_runtime(autonomous_mortal=True)
    original = base._stage10_config
    selection = BatchSelectionPolicy(
        version="stage10-live-selection-dev-v1",
        maximum_episodes=1, consequence_reference=1.0,
        surprise_reference=1.0, recency_window_steps=8,
        repetition_reference=1,
        weight_consequence=1.0, weight_surprise=1.0,
        weight_recency=1.0, weight_repetition=1.0,
        ageing_gain_per_step=0.1, scan_uc_per_episode=1,
    )
    semantic = SemanticPassPolicy(
        version="stage10-live-sixpass-dev-v1",
        replay=ReplayAgendaPolicy(
            version="stage10-live-replay-dev-v1",
            recent_window_steps=3, start_with_recent=True,
        ),
        skill_success_threshold=2, nearby_context_radius=1,
        rule_expiry_steps=20,
    )
    budget = ConsolidationBudgetConfig(
        version="stage10-live-p42-dev-v1",
        period_capacity_uc=600, step_slot_uc=100,
        operation_costs={
            "semantic_plan_build": 1,
            "replay_agenda_scan": 1,
            "episode_scan": 1, "episode_replay": 1,
            "rule_extraction": 1, "skill_compilation": 1,
            "kappa_recalibration": 1, "index_maintenance": 1,
            "pass_prepare": 1, "pass_validate": 1,
        },
    )
    config = replace(
        original,
        sleep=replace(
            original.sleep,
            # Force genuine waking autobiographical episodes before the
            # explicitly injected fatigue stress. This is a versioned software
            # integration fixture, not a normative sleep calibration.
            fatigue_gain=0.0,
            night_weight=0.0,
            consolidation_weight=0.0,
            max_consecutive_sleep_steps=18,
            natural_wake_threshold=0.000001,
        ),
        sleep_work=budget, selection_policy=selection,
        semantic_policy=semantic, p_cons_min=0.0,
        maximum_passes_per_sleep_step=maximum_passes_per_sleep_step,
    )
    runtime = Stage10Runtime(
        world_config=base.world.config,
        layout=base.world._layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=(
            base.stage3.control._config.protected_integrity_threshold
        ),
        config=config, equipment=base.equipment,
        autonomous_mortal=True,
    )
    return runtime


class LiveConsolidationRuntimeTests(unittest.TestCase):
    def test_causal_six_passes_run_in_real_sleep_and_commit_unproven_h(self):
        runtime = configured_runtime()
        self.assertIsNone(runtime.stage3.substrate.bench)
        self.assertIsNone(runtime.stage3.substrate.evaluation_trace)
        initial_h = runtime.slow_history.current_version

        # Every episode must originate in an applied physical waking life.
        waking_trace = []
        for _ in range(12):
            if runtime.memory.episodes:
                break
            result = runtime.run_step()
            waking_trace.append((result.source, result.command_primitive))
            self.assertEqual(result.execution_status, "applied")
        self.assertTrue(
            runtime.memory.episodes,
            f"no lived episode after waking trace {waking_trace}; "
            f"auto commits={sum(e.causal_event['kind'] == 'auto_segment_commit' for e in runtime.journal.entries)}",
        )

        # Physical sleep must first win Competition and Action Control.
        state = runtime.sleep_health.export_causal_state()
        state["fatigue"] = 1.0
        runtime.sleep_health.restore_causal_state(state)
        if runtime.sleep_session.mode == "awake":
            for _ in range(10):
                result = runtime.run_step()
                self.assertEqual(result.execution_status, "applied")
                if result.command_primitive == "dormir":
                    break
            else:
                self.fail("sleep was not selected by real waking cognition")

        for _ in range(18):
            runtime.run_step()
            if runtime.slow_history.current_version != initial_h:
                break
        self.assertNotEqual(runtime.slow_history.current_version, initial_h)
        self.assertIsNone(runtime.consolidation.current)
        history = runtime.slow_history.read_committed()
        self.assertTrue(history["consolidated_episode_refs"])
        self.assertTrue(all(
            row["status"] == "hypothese_causale"
            and row["validated_for_safety"] is False
            for row in history["hypotheses"]
        ))
        kinds = [
            event.causal_event["kind"] for event in runtime.journal.entries
        ]
        self.assertEqual(
            kinds.count("stage10_consolidation_pass_checkpointed"), 6,
        )
        self.assertEqual(
            kinds.count("stage10_consolidation_version_activated"), 1,
        )
        self.assertTrue(runtime.journal.verify())
        self.assertEqual(runtime.bench, None)

    def test_bounded_paid_multipass_preserves_order_and_budget(self):
        runtime = configured_runtime(maximum_passes_per_sleep_step=3)
        for _ in range(12):
            if runtime.memory.episodes:
                break
            self.assertEqual(runtime.run_step().execution_status, "applied")
        self.assertTrue(runtime.memory.episodes)
        state = runtime.sleep_health.export_causal_state()
        state["fatigue"] = 1.0
        runtime.sleep_health.restore_causal_state(state)
        for _ in range(35):
            self.assertEqual(runtime.run_step().execution_status, "applied")
            kinds = [e.causal_event["kind"] for e in runtime.journal.entries]
            if "stage10_consolidation_version_activated" in kinds:
                break
        else:
            self.fail("three-pass bounded sleep never published h")
        checkpoints = [
            e.causal_event for e in runtime.journal.entries
            if e.causal_event["kind"] == "stage10_consolidation_pass_checkpointed"
        ]
        counts = Counter(e["data"]["world_step"] for e in checkpoints)
        self.assertTrue(counts)
        self.assertGreater(max(counts.values()), 1)
        self.assertLessEqual(max(counts.values()), 3)
        self.assertTrue(all(
            0 <= e["data"]["consumed_step_uc"] <= 100
            and 0 <= e["data"]["consumed_period_uc"] <= 600
            for e in checkpoints
        ))
        publications = [
            e.causal_event for e in runtime.journal.entries
            if e.causal_event["kind"] == "stage10_consolidation_version_activated"
        ]
        self.assertEqual(len(publications), 1)
        self.assertEqual(
            [e["data"]["pass"] for e in checkpoints[:6]],
            ["episode_selection", "interleaved_replay",
             "hypothesis_extraction", "procedural_compilation",
             "kappa_recalibration", "index_maintenance"],
        )
        self.assertTrue(runtime.journal.verify())
        self.assertIsNone(runtime.stage3.substrate.bench)

    def test_multipass_configuration_requires_integral_bounded_count(self):
        config = configured_runtime()._stage10_config
        for invalid in (0, 7, True, 1.5, -1):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    replace(config, maximum_passes_per_sleep_step=invalid).validate()

    def test_live_custody_cannot_activate_in_legacy_or_without_prices(self):
        base = build_stage10_reference_runtime()
        policy = BatchSelectionPolicy(
            version="x", maximum_episodes=1,
            consequence_reference=1.0, surprise_reference=1.0,
            recency_window_steps=2, repetition_reference=1,
            weight_consequence=1.0, weight_surprise=1.0,
            weight_recency=1.0, weight_repetition=1.0,
            ageing_gain_per_step=0.1, scan_uc_per_episode=1,
        )
        with self.assertRaises(ValueError):
            replace(base._stage10_config, selection_policy=policy).validate()


if __name__ == "__main__":
    unittest.main()
