"""Stage 11 external scenario application boundary: public software tests.

No synthetic input is a lived observation or a scientific acceptance result.
External stop must preserve the WorldBody before the aborted input batch.
"""
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch

from lab.injected_scenario import ScenarioEvent, ScenarioInputRejected
from lab.stage11_routed_junction_probe import build_public_route_runtime
from lab.world import Position


def external(*, t, seq, op, x, y, **extra):
    return ScenarioEvent(
        t_monde=t, sequence=seq, operation=op,
        payload={"position": {"x": x, "y": y}, **extra},
    )


def logged(runtime, kind, *, t=None):
    return [
        entry.causal_event
        for entry in runtime.journal.entries
        if entry.causal_event.get("kind") == kind
        and (t is None or entry.causal_event.get("t_monde") == t)
    ]


def failed_batch_runner():
    events = (
        external(t=2, seq=0, op="set_danger_zone",
                 x=2, y=3, active=True),
        external(t=2, seq=1, op="set_position", x=0, y=2),
    )
    return build_public_route_runtime(
        layout_variant="junction_open",
        survey_refresh=True, scenario_events=events,
    )


class Stage11ExternalBatchFailureTests(TestCase):
    def test_multiple_inputs_revert_full_world_and_fail_stop_cleanly(self):
        runtime = failed_batch_runner()
        runtime.run_step()
        before_world = deepcopy(runtime.world.export_causal_state())
        before_others = {
            owner.owner_id: deepcopy(owner.export_causal_state())
            for owner in runtime.causal_owners
            if owner.owner_id not in {"scheduler.clock", "scenario"}
        }
        before_scenario = deepcopy(
            runtime.stage3.substrate.scenario.export_causal_state()
        )
        self.assertEqual(before_scenario["next_index"], 0)
        self.assertEqual(runtime.world.position, Position(3, 2))
        with self.assertRaises(ScenarioInputRejected):
            runtime.run_step()

        self.assertEqual(runtime.world.export_causal_state(), before_world)
        self.assertEqual(runtime.world.position, Position(3, 2))
        for owner in runtime.causal_owners:
            if owner.owner_id in before_others:
                self.assertEqual(
                    owner.export_causal_state(), before_others[owner.owner_id],
                    owner.owner_id,
                )
        self.assertEqual(runtime.scheduler.t_monde, 2)
        self.assertIsNone(runtime.scheduler.active_attempt)
        scenario = runtime.stage3.substrate.scenario
        self.assertTrue(scenario.halted)
        status = scenario.export_causal_state()
        self.assertEqual(status["next_index"], 0)
        self.assertEqual(status["rejected_event"],
                         {"t_monde": 2, "sequence": 1})

        received = logged(runtime, "external_input_received", t=2)
        applied = logged(runtime, "external_input_applied", t=2)
        rejected = logged(runtime, "external_input_rejected", t=2)
        reverted = logged(runtime, "external_input_batch_rolled_back", t=2)
        self.assertEqual([e["sequence"] for e in received], [0, 1])
        self.assertEqual([e["sequence"] for e in applied], [0])
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["sequence"], 1)
        self.assertEqual(rejected[0]["reason"], "invalid_operation_or_payload")
        self.assertEqual(rejected[0]["world_recovered"], True)
        self.assertEqual(rejected[0]["previous_inputs_reverted"], 1)
        self.assertEqual(len(reverted), 1)
        self.assertEqual(reverted[0]["previous_inputs_reverted"], 1)
        self.assertEqual(reverted[0]["world_recovered"], True)
        kinds = [e.causal_event["kind"] for e in runtime.journal.entries]
        self.assertLess(
            kinds.index("external_input_received"),
            kinds.index("external_input_applied"),
        )
        self.assertLess(
            kinds.index("external_input_applied"),
            kinds.index("external_input_rejected"),
        )
        self.assertLess(
            kinds.index("external_input_rejected"),
            kinds.index("external_input_batch_rolled_back"),
        )
        self.assertFalse(logged(runtime, "perceptual_capture", t=2))
        self.assertFalse(logged(runtime, "command_experienced", t=2))
        self.assertFalse(logged(runtime, "world_transition_experienced", t=2))
        closed = logged(runtime, "step_closed", t=2)
        self.assertEqual(len(closed), 1)
        self.assertEqual(
            closed[0]["data"],
            {"outcome": "external_stop",
             "applied_command_count": 0,
             "world_advance_count": 0},
        )
        self.assertTrue(runtime.journal.verify())

        technical_before = runtime.journal.canonical_bytes()
        with self.assertRaisesRegex(RuntimeError, "rejected external scenario"):
            runtime.run_step()
        self.assertEqual(runtime.scheduler.t_monde, 2)
        self.assertEqual(runtime.journal.canonical_bytes(), technical_before)

        # Exact owner snapshot of the *halt marker* is restorable. A
        # checkpoint predating rejection may be inspected, but resuming
        # that step requires a NEW branch and journal occurrence namespace.
        scenario.restore_causal_state(deepcopy(before_scenario))
        self.assertFalse(scenario.halted)
        scenario.restore_causal_state(deepcopy(status))
        self.assertTrue(scenario.halted)
        self.assertEqual(scenario.export_causal_state(), status)

    def test_rejected_snapshot_marker_and_cursor_must_describe_same_batch(self):
        runtime = failed_batch_runner()
        runtime.run_step()
        with self.assertRaises(ScenarioInputRejected):
            runtime.run_step()
        scenario = runtime.stage3.substrate.scenario
        frozen = deepcopy(scenario.export_causal_state())
        self.assertEqual(frozen["next_index"], 0)
        self.assertEqual(frozen["rejected_event"],
                         {"t_monde": 2, "sequence": 1})
        for index in (1, 2):
            corrupted = deepcopy(frozen)
            corrupted["next_index"] = index
            with self.subTest(next_index=index), self.assertRaisesRegex(
                ValueError, "invalid rejected scenario input marker",
            ):
                scenario.restore_causal_state(corrupted)
            self.assertEqual(scenario.export_causal_state(), frozen)
        for marker in (
            {"t_monde": 2, "sequence": 99},
            {"t_monde": 1, "sequence": 1},
        ):
            corrupted = deepcopy(frozen)
            corrupted["rejected_event"] = marker
            with self.subTest(marker=marker), self.assertRaisesRegex(
                ValueError, "invalid rejected scenario input marker",
            ):
                scenario.restore_causal_state(corrupted)
            self.assertEqual(scenario.export_causal_state(), frozen)
        scenario.restore_causal_state(deepcopy(frozen))
        self.assertTrue(scenario.halted)
        self.assertEqual(scenario.export_causal_state(), frozen)
        self.assertTrue(runtime.journal.verify())

    def test_single_rejected_input_stops_before_any_perception_or_command(self):
        runtime = build_public_route_runtime(
            scenario_events=(
                external(t=1, seq=0, op="set_position", x=0, y=2),
            ),
        )
        before = deepcopy(runtime.world.export_causal_state())
        with self.assertRaises(ScenarioInputRejected):
            runtime.run_step()
        self.assertEqual(runtime.world.export_causal_state(), before)
        self.assertFalse(logged(runtime, "external_input_applied"))
        self.assertFalse(logged(runtime, "external_input_batch_rolled_back"))
        self.assertEqual(len(logged(runtime, "external_input_rejected")), 1)
        self.assertEqual(len(logged(runtime, "external_input_received")), 1)
        self.assertFalse(logged(runtime, "perceptual_capture"))
        self.assertFalse(logged(runtime, "command_experienced"))
        self.assertIsNone(runtime.scheduler.active_attempt)
        self.assertEqual(runtime.scheduler.t_monde, 1)
        self.assertEqual(logged(runtime, "step_closed")[0]["data"]["outcome"],
                         "external_stop")
        self.assertTrue(runtime.journal.verify())

    def test_two_valid_inputs_preserve_world_step_and_logged_provenance(self):
        runner = build_public_route_runtime(
            scenario_events=(
                external(t=2, seq=0, op="set_danger_zone",
                         x=2, y=3, active=True),
                external(t=2, seq=1, op="set_position", x=4, y=2),
            ),
            survey_refresh=True,
        )
        runner.run_step()
        second = runner.run_step()
        self.assertEqual(second.execution_status, "applied")
        self.assertEqual(
            [event["sequence"] for event in logged(
                runner, "external_input_received", t=2,
            )],
            [0, 1],
        )
        self.assertEqual(
            [event["sequence"] for event in logged(
                runner, "external_input_applied", t=2,
            )],
            [0, 1],
        )
        self.assertFalse(logged(runner, "external_input_rejected"))
        self.assertFalse(logged(runner, "external_input_batch_rolled_back"))
        self.assertEqual(
            logged(runner, "perceptual_capture", t=2)[0]["data"]["position"],
            {"x": 4, "y": 2},
        )
        self.assertFalse(runner.stage3.substrate.scenario.halted)
        self.assertEqual(runner.scheduler.t_monde, 2)
        self.assertIsNone(runner.scheduler.active_attempt)
        self.assertTrue(runner.journal.verify())

    def test_rejection_recovers_even_if_failing_input_already_mutated_world(self):
        runtime = build_public_route_runtime(
            scenario_events=(
                external(t=2, seq=0, op="set_danger_zone",
                         x=2, y=3, active=True),
            ),
        )
        runtime.run_step()
        before_world = deepcopy(runtime.world.export_causal_state())
        apply_original = runtime.world.apply_scenario_event

        def broken_after_world_application(operation, payload):
            apply_original(operation, payload)
            raise ValueError("synthetic error after applying world input")

        with patch.object(
            runtime.world, "apply_scenario_event",
            side_effect=broken_after_world_application,
        ):
            with self.assertRaises(ScenarioInputRejected):
                runtime.run_step()
        self.assertEqual(runtime.world.export_causal_state(), before_world)
        self.assertEqual(runtime.scheduler.t_monde, 2)
        self.assertIsNone(runtime.scheduler.active_attempt)
        self.assertTrue(runtime.stage3.substrate.scenario.halted)
        rejected = logged(runtime, "external_input_rejected", t=2)
        self.assertEqual(len(rejected), 1)
        self.assertTrue(rejected[0]["world_recovered"])
        self.assertEqual(rejected[0]["previous_inputs_reverted"], 0)
        self.assertFalse(logged(runtime, "external_input_applied", t=2))
        self.assertFalse(logged(runtime, "perceptual_capture", t=2))
        self.assertTrue(runtime.journal.verify())

    def test_failed_world_recovery_never_claims_a_successful_rollback(self):
        runtime = build_public_route_runtime(
            scenario_events=(
                external(t=1, seq=0, op="set_position", x=0, y=2),
            ),
        )
        with patch.object(
            runtime.world, "restore_causal_state",
            side_effect=ValueError("synthetic compensation failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "WorldBody rollback failed"):
                runtime.run_step()
        rejected = logged(runtime, "external_input_rejected", t=1)
        self.assertEqual(len(rejected), 1)
        self.assertFalse(rejected[0]["world_recovered"])
        self.assertTrue(runtime.stage3.substrate.scenario.halted)
        self.assertEqual(runtime.scheduler.t_monde, 1)
        self.assertIsNone(runtime.scheduler.active_attempt)
        self.assertFalse(logged(runtime, "perceptual_capture", t=1))
        self.assertEqual(
            logged(runtime, "step_closed", t=1)[0]["data"]["outcome"],
            "external_stop",
        )
        self.assertTrue(runtime.journal.verify())

    def test_external_resource_and_body_values_do_not_coerce_types(self):
        runner = build_public_route_runtime()
        world = runner.world
        before = deepcopy(world.export_causal_state())
        position = {"x": 2, "y": 2}
        for bad_kind, bad_quantity in (
            ("wood", True), ("wood", "2"), ("wood", 1.9),
            ("wood", None), ("wood", -1), ("wood", [2]),
            (123, 2), (None, 2), ("unsupported_resource", 2),
        ):
            with self.subTest(
                kind=bad_kind, quantity=bad_quantity,
            ), self.assertRaisesRegex(ValueError, "invalid scenario resource"):
                world.apply_scenario_event("place_resource", {
                    "position": dict(position),
                    "kind": bad_kind, "quantity": bad_quantity,
                })
            self.assertEqual(world.export_causal_state(), before)

        for field, value in (
            ("energy", True), ("food", "63"), ("water", None),
            ("integrity", [98]), ("energy", float("inf")),
            ("energy", float("nan")), ("food", -1), ("water", 101.0),
        ):
            with self.subTest(
                field=field, value=value,
            ), self.assertRaises(ValueError):
                world.apply_scenario_event("set_body", {field: value})
            self.assertEqual(world.export_causal_state(), before)

        # Ordinary P-54 resource quantities and genuine numeric body values
        # still apply. They are external physical inputs, not actions.
        world.apply_scenario_event("place_resource", {
            "position": dict(position), "kind": "wood", "quantity": 2,
        })
        self.assertNotEqual(world.export_causal_state(), before)
        world.apply_scenario_event("set_body", {"food": 63, "water": 62.5})
        self.assertEqual(world.body.food, 63.0)
        self.assertEqual(world.body.water, 62.5)
        world.restore_causal_state(deepcopy(before))
        self.assertEqual(world.export_causal_state(), before)

    def test_invalid_external_physical_quantities_reject_at_step_boundary(self):
        for operation, payload in (
            ("place_resource", {
                "position": {"x": 2, "y": 2},
                "kind": "wood", "quantity": 1.9,
            }),
            ("set_body", {"integrity": True}),
        ):
            with self.subTest(operation=operation):
                runtime = build_public_route_runtime(
                    scenario_events=(ScenarioEvent(
                        t_monde=1, sequence=0, operation=operation,
                        payload=payload,
                    ),),
                )
                before = deepcopy(runtime.world.export_causal_state())
                with self.assertRaises(ScenarioInputRejected):
                    runtime.run_step()
                self.assertEqual(runtime.world.export_causal_state(), before)
                self.assertTrue(runtime.stage3.substrate.scenario.halted)
                self.assertIsNone(runtime.scheduler.active_attempt)
                self.assertEqual(runtime.scheduler.t_monde, 1)
                received = logged(runtime, "external_input_received")
                rejected = logged(runtime, "external_input_rejected")
                self.assertEqual(len(received), 1)
                self.assertEqual(received[0]["payload"], payload)
                self.assertEqual(len(rejected), 1)
                self.assertEqual(rejected[0]["world_recovered"], True)
                self.assertFalse(logged(runtime, "external_input_applied"))
                self.assertFalse(logged(runtime, "perceptual_capture"))
                self.assertFalse(logged(runtime, "command_experienced"))
                self.assertTrue(runtime.journal.verify())

    def test_independent_external_batch_failure_replays_exactly(self):
        def run():
            runner = failed_batch_runner()
            runner.run_step()
            with self.assertRaises(ScenarioInputRejected):
                runner.run_step()
            return runner

        a, b = run(), run()
        self.assertEqual(a.journal.canonical_bytes(), b.journal.canonical_bytes())
        self.assertEqual(
            {o.owner_id: o.export_causal_state() for o in a.causal_owners},
            {o.owner_id: o.export_causal_state() for o in b.causal_owners},
        )
        self.assertTrue(a.journal.verify())
        self.assertTrue(b.journal.verify())


if __name__ == "__main__":
    import unittest
    unittest.main()
