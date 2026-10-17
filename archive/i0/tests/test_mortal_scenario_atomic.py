"""Irreversible opt-in external input batches preserve WorldBody consequences.

All scenario programs and hidden hazard truth are external Lab fixtures.
Tests never claim an individual's observations contain the batch schedule.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from lab.injected_scenario import InjectedScenario, ScenarioEvent, ScenarioInputRejected
from lab.mortal_execution import MortalStatus
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command, WorldBody


class MortalScenarioBatchTests(unittest.TestCase):
    def make_runtime(self, events):
        runtime = build_stage4_reference_runtime()
        substrate = runtime.stage3.substrate
        substrate.scenario = InjectedScenario(
            scenario_id="scenario:mortal:static",
            version="atomic-external-v1",
            events=events,
            journal=substrate.journal,
        )
        substrate.enable_mortal_world()
        return runtime

    @staticmethod
    def kinds(runtime):
        return [entry.causal_event["kind"] for entry in runtime.journal.entries]

    def test_two_valid_inputs_commit_once_with_exact_world_parity(self):
        events = (
            ScenarioEvent(1, 0, "set_danger_zone", {
                "position": {"x": 3, "y": 3}, "active": True,
            }),
            ScenarioEvent(1, 1, "place_resource", {
                "position": {"x": 2, "y": 2}, "kind": "wood",
                "quantity": 2,
            }),
        )
        runtime = self.make_runtime(events)
        comparator = WorldBody(
            config=runtime.world.config, layout=runtime.world._layout,
        )
        for event in events:
            comparator.apply_scenario_event(event.operation, event.payload)
        sub = runtime.stage3.substrate
        sub.open_step()
        self.assertEqual(
            runtime.world.export_causal_state(),
            comparator.export_causal_state(),
        )
        self.assertEqual(sub.scenario.export_causal_state()["next_index"], 2)
        kinds = self.kinds(runtime)
        self.assertEqual(kinds.count("external_input_received"), 2)
        self.assertEqual(kinds.count("external_input_applied"), 2)
        self.assertNotIn("external_input_batch_rolled_back", kinds)
        self.assertEqual(sub.execute(Command("attendre")).status, "applied")
        self.assertEqual(sub.mortal_status, MortalStatus.ACTIVE)

    def test_invalid_second_input_rejects_private_batch_without_real_rewind(self):
        events = (
            ScenarioEvent(1, 0, "set_danger_zone", {
                "position": {"x": 3, "y": 3}, "active": True,
            }),
            ScenarioEvent(1, 1, "set_body", {
                "integrity": "invalid-not-a-physical-number",
            }),
        )
        runtime = self.make_runtime(events)
        before = runtime.world.export_causal_state()
        sub = runtime.stage3.substrate
        with self.assertRaises(ScenarioInputRejected):
            sub.open_step()
        self.assertEqual(runtime.world.export_causal_state(), before)
        self.assertEqual(sub.mortal_status, MortalStatus.TECHNICAL_HALT)
        self.assertTrue(sub.scenario.halted)
        self.assertIsNone(sub.scheduler.active_attempt)
        kinds = self.kinds(runtime)
        self.assertIn("external_input_batch_halted", kinds)
        self.assertNotIn("external_input_batch_rolled_back", kinds)
        self.assertNotIn("external_input_applied", kinds)
        with self.assertRaises(RuntimeError):
            sub.open_step()

    def test_failed_applied_receipt_keeps_the_physically_published_world(self):
        event = ScenarioEvent(
            1, 0, "set_danger_zone",
            {"position": {"x": 3, "y": 3}, "active": True},
        )
        runtime = self.make_runtime((event,))
        sub = runtime.stage3.substrate
        before = runtime.world.export_causal_state()
        original_append = runtime.journal.append

        def reject_applied_receipt(*, event_id, causal_event):
            if causal_event.get("kind") == "external_input_applied":
                raise OSError("injected receipt failure after physical publication")
            return original_append(event_id=event_id, causal_event=causal_event)

        with patch.object(runtime.journal, "append", side_effect=reject_applied_receipt):
            with self.assertRaises(ScenarioInputRejected):
                sub.open_step()

        final = runtime.world.export_causal_state()
        self.assertNotEqual(final, before)
        self.assertIn({"x": 3, "y": 3}, final["danger_zones"])
        self.assertEqual(sub.mortal_status, MortalStatus.TECHNICAL_HALT)
        self.assertTrue(sub.scenario.halted)
        self.assertIsNone(sub.scheduler.active_attempt)
        kinds = self.kinds(runtime)
        self.assertIn("external_input_received", kinds)
        self.assertIn("external_input_batch_halted", kinds)
        self.assertNotIn("external_input_batch_rolled_back", kinds)
        self.assertFalse(any(
            row.causal_event["kind"] == "snapshot_restored"
            for row in runtime.journal.entries
        ))
        with self.assertRaises(RuntimeError):
            sub.open_step()
        self.assertEqual(runtime.world.export_causal_state(), final)

    def test_six_hundred_nonlethal_world_steps_keep_physics_identical(self):
        # Public development stability only: not a biological survival
        # scenario, an independent held-out or scientific acceptance.
        runtime = self.make_runtime((
            ScenarioEvent(601, 0, "set_danger_zone", {
                "position": {"x": 3, "y": 3},
            }),
        ))
        comparator = WorldBody(
            config=runtime.world.config, layout=runtime.world._layout,
        )
        sub = runtime.stage3.substrate
        for step in range(1, 601):
            sub.open_step()
            result = sub.execute(Command("attendre"))
            reference = comparator.apply(Command("attendre"), t_monde=step)
            self.assertEqual(result.status, "applied")
            self.assertEqual(result.transition.as_dict(), reference.as_dict())
        self.assertEqual(sub.mortal_status, MortalStatus.ACTIVE)
        self.assertEqual(sub.scheduler.t_monde, 600)
        self.assertEqual(
            runtime.world.export_causal_state(),
            comparator.export_causal_state(),
        )
        self.assertEqual(runtime.bench.metrics.lethal_rollbacks, 0)
        self.assertTrue(runtime.journal.verify())

    def test_no_external_event_does_not_produce_fake_receipt(self):
        runtime = self.make_runtime((
            ScenarioEvent(3, 0, "set_danger_zone", {
                "position": {"x": 3, "y": 3},
            }),
        ))
        sub = runtime.stage3.substrate
        sub.open_step()
        self.assertNotIn("external_input_received", self.kinds(runtime))
        self.assertEqual(sub.execute(Command("attendre")).status, "applied")
        self.assertEqual(sub.mortal_status, MortalStatus.ACTIVE)


if __name__ == "__main__":
    unittest.main()
