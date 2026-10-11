"""Stage-10 waking-health integration invariants, no sleep/consolidation.

A named opt-in Stage-10 runtime adds only Metacognition-owned fatigue and
step-frozen pressure. Stage-9 reference remains semantically unmodified.
"""
import unittest
from copy import deepcopy

from i0.modules.metacognition import MinimalMetacognition
from i0.modules.sleep_health import SleepHealth
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage10_health_reference_fixture import (
    build_stage10_health_reference_runtime,
)


def health():
    return build_stage10_health_reference_runtime().sleep_health


class SleepHealthUnitTests(unittest.TestCase):
    def test_frozen_pressure_cannot_learn_from_same_step_computation(self):
        model = health()
        first = model.begin_waking_step(
            world_step=1, unconsolidated_episodes=0,
            memory_occupancy=0.0, is_night=False,
        )
        self.assertEqual(first.fatigue, 0)
        initial = first.sleep_pressure
        model.close_waking_cycle(
            world_step=1, cycle=1, consumed_uc=40,
            cycle_ceiling=100, c_max=4,
        )
        second = model.begin_waking_step(
            world_step=1, unconsolidated_episodes=100,
            memory_occupancy=1.0, is_night=True,
        )
        self.assertEqual(second, first)
        self.assertEqual(model.frozen.sleep_pressure, initial)
        self.assertGreater(model.fatigue, first.fatigue)
        future = model.begin_waking_step(
            world_step=2, unconsolidated_episodes=0,
            memory_occupancy=0.0, is_night=False,
        )
        self.assertGreater(future.sleep_pressure, initial)
        self.assertEqual(future.fatigue, model.fatigue)

    def test_counts_only_real_uc_once_per_distinct_cycle(self):
        model = health()
        model.begin_waking_step(
            world_step=2, unconsolidated_episodes=0,
            memory_occupancy=0, is_night=False,
        )
        model.close_waking_cycle(
            world_step=2, cycle=1, consumed_uc=20,
            cycle_ceiling=100, c_max=4,
        )
        after = model.fatigue
        with self.assertRaises(ValueError):
            model.close_waking_cycle(
                world_step=2, cycle=1, consumed_uc=20,
                cycle_ceiling=100, c_max=4,
            )
        self.assertEqual(after, model.fatigue)
        model.close_waking_cycle(
            world_step=2, cycle=2, consumed_uc=20,
            cycle_ceiling=100, c_max=4,
        )
        self.assertGreater(model.fatigue, after)
        with self.assertRaises(ValueError):
            model.close_waking_cycle(
                world_step=1, cycle=3, consumed_uc=2,
                cycle_ceiling=100, c_max=4,
            )

    def test_snapshot_roundtrip_and_atomic_corruption_rejection(self):
        model = health()
        model.begin_waking_step(
            world_step=2, unconsolidated_episodes=1,
            memory_occupancy=0.25, is_night=True,
        )
        model.close_waking_cycle(
            world_step=2, cycle=1, consumed_uc=30,
            cycle_ceiling=100, c_max=4,
        )
        state = model.export_causal_state()
        other = health()
        other.restore_causal_state(state)
        self.assertEqual(other.export_causal_state(), state)
        for kind in ("fatigue_nan", "bad_version", "corrupt_pressure",
                     "bad_clock", "duplicate_extra_key"):
            bad = deepcopy(state)
            if kind == "fatigue_nan":
                bad["fatigue"] = float("nan")
            elif kind == "bad_version":
                bad["config_version"] = "forged"
            elif kind == "corrupt_pressure":
                bad["frozen"]["intrinsic_value"] = 1.0
            elif kind == "bad_clock":
                bad["last_cycle"] = (3, 1)
            else:
                bad["injected"] = 1
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):
                    other.restore_causal_state(bad)
                self.assertEqual(other.export_causal_state(), state)

    def test_legacy_metacognition_without_opt_in_has_identical_snapshot(self):
        legacy = MinimalMetacognition()
        self.assertIsNone(legacy.sleep_health)
        self.assertEqual(
            legacy.export_causal_state(),
            {"f_cog_uc_counter": 0, "last_cycle_uc": 0, "budget_state": "normal"},
        )
        with self.assertRaises(ValueError):
            legacy.restore_causal_state({
                **legacy.export_causal_state(),
                "sleep_health": health().export_causal_state(),
            })
        self.assertIsNone(legacy.sleep_health)

    def test_single_metacognition_owner_restores_full_sleep_state(self):
        m = MinimalMetacognition()
        cfg = health().rules.config
        m.attach_sleep_health(cfg)
        with self.assertRaises(ValueError):
            m.attach_sleep_health(cfg)
        m.sleep_health.begin_waking_step(
            world_step=1, unconsolidated_episodes=2,
            memory_occupancy=0.5, is_night=True,
        )
        before = m.export_causal_state()
        with self.assertRaises(ValueError):
            m.restore_causal_state({
                **before,
                "sleep_health": {
                    **before["sleep_health"],
                    "fatigue": float("nan"),
                },
            })
        self.assertEqual(m.export_causal_state(), before)
        n = MinimalMetacognition()
        n.attach_sleep_health(cfg)
        n.restore_causal_state(before)
        self.assertEqual(n.export_causal_state(), before)


class Stage10WakingHealthRuntimeTests(unittest.TestCase):
    def test_stage10_attaches_to_existing_owner_once(self):
        runtime = build_stage10_health_reference_runtime()
        ids = [owner.owner_id for owner in runtime.causal_owners]
        self.assertEqual(ids.count("metacognition_health"), 1)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIs(runtime.metacognition.sleep_health, runtime.sleep_health)
        self.assertIsNone(runtime.sleep_health.frozen)
        result = runtime.run_step()
        self.assertEqual(result.execution_status, "applied")
        frozen = runtime.sleep_health.frozen
        self.assertEqual(runtime.sleep_health.frozen_world_step, 1)
        self.assertIsNotNone(frozen)
        self.assertEqual(frozen.fatigue, 0.0)
        self.assertGreater(runtime.sleep_health.fatigue, 0.0)
        self.assertEqual(
            runtime.s_t.current.fixed["sleep_readiness"]["sleep_pressure"],
            frozen.sleep_pressure,
        )
        self.assertFalse(
            runtime.s_t.current.fixed["sleep_readiness"]["enabled_for_action"]
        )
        self.assertTrue(runtime.journal.verify())

    def test_same_step_pressure_never_changes_across_cycles(self):
        runtime = build_stage10_health_reference_runtime()
        for _ in range(3):
            result = runtime.run_step()
            self.assertEqual(result.execution_status, "applied")
            self.assertTrue(runtime.journal.verify())
        frozen = [
            item.causal_event["data"]
            for item in runtime.journal.entries
            if item.causal_event.get("kind") == "stage10_sleep_pressure_frozen"
        ]
        charged = [
            item.causal_event["data"]
            for item in runtime.journal.entries
            if item.causal_event.get("kind") == "stage10_fatigue_cycle_closed"
        ]
        self.assertEqual(len(frozen), 3)
        self.assertGreaterEqual(len(charged), 3)
        self.assertEqual(
            sorted(set(item["world_step"] for item in frozen)), [1, 2, 3],
        )
        self.assertTrue(all(0 <= item["f_cog_after"] <= 1 for item in charged))
        self.assertTrue(all(
            item["logical_uc"] <= item["cycle_budget_uc"] for item in charged
        ))

    def test_reference_stage9_no_sleep_side_effects(self):
        original = build_stage9_reference_runtime()
        new = build_stage10_health_reference_runtime()
        self.assertNotIn("sleep_health", original.metacognition.export_causal_state())
        for _ in range(3):
            a, b = original.run_step(), new.run_step()
            self.assertEqual(
                (a.execution_status, a.command_primitive, a.source),
                (b.execution_status, b.command_primitive, b.source),
            )
        self.assertNotIn("sleep_readiness", original.s_t.current.fixed)
        self.assertIn("sleep_readiness", new.s_t.current.fixed)
        self.assertTrue(original.journal.verify())
        self.assertTrue(new.journal.verify())

    def test_reexecution_is_exact_for_metacognition_snapshot_and_journal(self):
        a, b = build_stage10_health_reference_runtime(), build_stage10_health_reference_runtime()
        for rt in (a, b):
            for _ in range(3):
                self.assertEqual(rt.run_step().execution_status, "applied")
        self.assertEqual(
            a.metacognition.export_causal_state(),
            b.metacognition.export_causal_state(),
        )
        self.assertEqual(a.journal.canonical_bytes(), b.journal.canonical_bytes())


if __name__ == "__main__":
    unittest.main()
