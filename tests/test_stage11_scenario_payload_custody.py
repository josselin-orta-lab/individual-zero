"""Stage11 external scenario nested-payload ownership, public unit-only."""
from copy import deepcopy
from unittest import TestCase

from lab.injected_scenario import InjectedScenario, ScenarioEvent
from lab.journal import HashChainedJournal
from lab.stage11_routed_junction_probe import build_public_route_runtime
from lab.world import Position


def event(*, position=None):
    if position is None:
        position = {"x": 4, "y": 2}
    return ScenarioEvent(
        t_monde=2, sequence=0, operation="set_position",
        payload={"position": position},
    )


class Stage11ScenarioPayloadCustodyTests(TestCase):
    def test_caller_and_export_cannot_rewrite_future_physical_input(self):
        caller_position = {"x": 4, "y": 2}
        original_event = event(position=caller_position)
        runtime = build_public_route_runtime(
            survey_refresh=True, scenario_events=(original_event,),
        )
        scenario = runtime.stage3.substrate.scenario
        expected_program = deepcopy(scenario.export_causal_state())

        # The caller controls these Python dictionaries, but not the
        # registered, versioned external program stored in the runtime.
        caller_position["x"] = 0
        original_event.payload["position"]["y"] = 99
        self.assertEqual(scenario.export_causal_state(), expected_program)

        exported = scenario.export_causal_state()
        exported["events"][0]["payload"]["position"]["x"] = 0
        exported["events"][0]["payload"]["position"]["y"] = -1
        self.assertEqual(scenario.export_causal_state(), expected_program)

        runtime.run_step()
        runtime.run_step()
        # The external arrival is verified at the true physical Perception
        # boundary. After that capture, a legitimately selected autonomous
        # command may move the body again in the very same world step.
        captured = [
            row.causal_event for row in runtime.journal.entries
            if row.causal_event.get("kind") == "perceptual_capture"
            and row.causal_event.get("t_monde") == 2
        ]
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0]["data"]["position"], {"x": 4, "y": 2})
        actual = [
            row.causal_event for row in runtime.journal.entries
            if row.causal_event.get("kind") == "external_input_received"
        ]
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0]["payload"]["position"], {"x": 4, "y": 2})
        self.assertEqual(scenario.export_causal_state()["events"],
                         expected_program["events"])
        self.assertTrue(runtime.journal.verify())

    def test_returned_applied_events_cannot_rewrite_custody_or_journal(self):
        runtime = build_public_route_runtime()
        journal = HashChainedJournal()
        engine = InjectedScenario(
            scenario_id="stage11-custody-unit",
            version="nested-v1",
            events=(ScenarioEvent(
                t_monde=1, sequence=0, operation="set_position",
                payload={"position": {"x": 4, "y": 2}},
            ),),
            journal=journal,
        )
        applied = engine.apply_for_step(t_monde=1, world=runtime.world)
        self.assertEqual(len(applied), 1)
        self.assertEqual(runtime.world.position, Position(4, 2))
        owner_snapshot = deepcopy(engine.export_causal_state())
        journal_bytes = journal.canonical_bytes()
        applied[0].payload["position"]["x"] = 0
        applied[0].payload["position"]["y"] = 999

        self.assertEqual(engine.export_causal_state(), owner_snapshot)
        self.assertEqual(journal.canonical_bytes(), journal_bytes)
        self.assertTrue(journal.verify())
        self.assertFalse(engine.halted)

    def test_independent_unmodified_programs_replay_exactly(self):
        def run():
            runner = build_public_route_runtime(
                survey_refresh=True, scenario_events=(event(),),
            )
            runner.run_step()
            runner.run_step()
            self.assertTrue(runner.journal.verify())
            return runner

        a, b = run(), run()
        self.assertEqual(a.journal.canonical_bytes(), b.journal.canonical_bytes())
        self.assertEqual(
            {owner.owner_id: owner.export_causal_state() for owner in a.causal_owners},
            {owner.owner_id: owner.export_causal_state() for owner in b.causal_owners},
        )


if __name__ == "__main__":
    import unittest
    unittest.main()
