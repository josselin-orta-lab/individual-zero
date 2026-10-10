"""I0-vNext Stage-11 opt-in episode length boundary, not historical Stage-9.

A max-length cut must not put command_experienced and its physical
world_transition_experienced from one world step into different episodes.
DC-09 causal evidence gates remain intact.
"""
from dataclasses import replace
from unittest import TestCase

from i0.modules.memory import EpisodicMemory
from lab.stage7_reference_fixture import build_stage7_reference_runtime
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime


def events():
    return [
        {"event_id": "step1:marker", "kind": "memory_marker", "t_monde": 1},
        {"event_id": "step2:command", "kind": "command_experienced",
         "t_monde": 2, "primitive": "boire", "parameters": {}},
        {"event_id": "step2:transition", "kind": "world_transition_experienced",
         "t_monde": 2},
    ]


def memory(atomic):
    base = build_stage7_reference_runtime().memory._config
    return EpisodicMemory(
        replace(base, version="test-memory-step-boundary-v1"),
        atomic_world_step_length_boundary=atomic,
    )


def ingest(memory_owner):
    return memory_owner.ingest_autobiographical(
        events(), current_t_monde=2,
        current_goal_ref=None, current_reward=0.0,
    )


class StepAtomicMemoryTests(TestCase):
    def test_length_closure_keeps_same_world_step_together(self):
        vnext = memory(True)
        closed = ingest(vnext)
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].boundary_type, "max_length")
        self.assertEqual(closed[0].end_t_monde, 2)
        self.assertIn("step2:command", closed[0].event_refs)
        self.assertIn("step2:transition", closed[0].event_refs)
        self.assertEqual(len(set(closed[0].event_refs)), 3)
        self.assertEqual(vnext.export_causal_state()["open_event_refs"], [])

    def test_historical_mode_stays_event_granular(self):
        legacy = memory(False)
        closed = ingest(legacy)
        self.assertEqual(len(closed), 1)
        self.assertIn("step2:command", closed[0].event_refs)
        self.assertNotIn("step2:transition", closed[0].event_refs)
        self.assertEqual(legacy.export_causal_state()["open_event_refs"],
                         ["step2:transition"])
        self.assertNotIn("boundary_semantics", legacy.export_causal_state())

    def test_atomic_snapshot_version_and_replay_mode_are_checked(self):
        source = memory(True)
        ingest(source)
        state = source.export_causal_state()
        self.assertEqual(state["boundary_semantics"],
                         "atomic-world-step-length-v1")
        mirror = memory(True)
        mirror.restore_causal_state(state)
        self.assertEqual(mirror.export_causal_state(), state)
        baseline = memory(False)
        with self.assertRaises(ValueError):
            baseline.restore_causal_state(state)
        invalid = dict(state)
        invalid["boundary_semantics"] = "untrusted"
        with self.assertRaises(ValueError):
            mirror.restore_causal_state(invalid)
        self.assertEqual(mirror.export_causal_state(), state)

    def test_mode_ownership_is_versioned_stage11_only(self):
        vnext = build_stage11_reference_runtime()
        baseline = build_stage9_reference_runtime()
        self.assertEqual(vnext.memory.export_causal_state()[
            "boundary_semantics"
        ], "atomic-world-step-length-v1")
        self.assertIn("atomic-world-step-length-v1",
                      vnext.memory._config.version)
        self.assertNotIn("boundary_semantics",
                         baseline.memory.export_causal_state())
        self.assertNotIn("atomic-world-step-length-v1",
                         baseline.memory._config.version)
        owners = [owner.owner_id for owner in vnext.causal_owners]
        self.assertEqual(owners.count("memory"), 1)
        self.assertEqual(len(owners), len(set(owners)))

    def test_public_stage11_executes_and_verifies_journal(self):
        vnext = build_stage11_reference_runtime()
        for _ in range(3):
            self.assertEqual(vnext.run_step().execution_status, "applied")
        self.assertTrue(vnext.journal.verify())


if __name__ == "__main__":
    import unittest
    unittest.main()
