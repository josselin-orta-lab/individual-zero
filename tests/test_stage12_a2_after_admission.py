"""A2 physical/cognitive tests: these fixtures are NOT autonomous science."""
from dataclasses import replace
import unittest
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.world import WorldBody, Position
from lab.injected_scenario import InjectedScenario, ScenarioEvent
from lab.journal import HashChainedJournal
from lab.stage11_reference_fixture import build_stage11_reference_runtime


class A2AfterAdmissionTests(unittest.TestCase):
    def setUp(self):
        baseline = build_stage11_reference_runtime()
        self.start = baseline.world.position
        self.target = Position(self.start.x + 1, self.start.y)
        self.world = WorldBody(
            config=baseline.world.config,
            layout=replace(baseline.world._layout,
                obstacles=frozenset(), water_sources=frozenset({self.target})),
        )
        self.perception = SymbolicPerception()
        self.pre = self.sense(1)
        self.command = PrimitiveCommand("se_deplacer", {"direction": "east"})

    def sense(self, t):
        return self.perception.capture(
            local_state=self.world.capture_local(t_monde=t).as_dict(),
            telemetry=self.world.telemetry())

    def assess(self, post):
        svc = GoalAgencyService()
        svc.preregister(
            assessment_ref="a", intent_ref="i", life_id="life:a",
            goal_ref="g", option_ref="o", command_hash="c",
            world_step=1, measure="spatial_distance",
            command=self.command, capture=self.pre,
            spatial_target=(self.target.x, self.target.y, "water"),
        )
        return svc.evaluate(capture=post, world_step=2, cue_ref="capture:2", paid=True)

    def test_actual_after_admission_obstacle_yields_world_cue(self):
        self.assertTrue(next(c.passable for c in self.pre.adjacent if c.direction == "east"))
        self.world.forbid_historical_restore()
        journal = HashChainedJournal()
        scenario = InjectedScenario(scenario_id="a2", version="v1",
            events=(ScenarioEvent(t_monde=1, sequence=0, operation="set_obstacle",
                payload={"position": self.target.as_dict(), "active": True},
                phase="after_admission"),), journal=journal)
        self.assertEqual(scenario.apply_for_step_irreversible(
            t_monde=1, world=self.world, phase="before_step"), ())
        # This fixture models an already admitted command. The live runtime
        # owns that gate, and no fixture may count as autonomous evidence.
        scenario.apply_for_step_irreversible(
            t_monde=1, world=self.world, phase="after_admission")
        movement = self.world.apply(self.command, t_monde=1)
        self.assertEqual(movement.effects["movement"], "blocked")
        self.assertEqual(self.assess(self.sense(2)).subjective_agency, "world")
        self.assertEqual(
            [entry.causal_event["phase"] for entry in journal.entries],
            ["after_admission", "after_admission"])
        self.assertTrue(journal.verify())

    def test_unchanged_world_with_forced_motion_failure_remains_unknown(self):
        self.world.apply_scenario_event("set_action_failure_schedule",
            {"primitive": "se_deplacer", "schedule": [True]})
        self.world.apply(self.command, t_monde=1)
        self.assertEqual(self.assess(self.sense(2)).subjective_agency, "unknown")

    def test_free_world_has_self_cue(self):
        self.world.apply(self.command, t_monde=1)
        self.assertEqual(self.assess(self.sense(2)).subjective_agency, "self")

    def test_new_obstruction_without_command_is_not_a_valid_attribution(self):
        self.world.apply_scenario_event("set_obstacle",
            {"position": self.target.as_dict(), "active": True})
        # The judgement policy has a prior commitment; runtime refuses to
        # create one without an actually admitted and dispatched motor event.
        self.assertFalse(next(c.passable for c in self.sense(2).adjacent
                              if c.direction == "east"))


if __name__ == "__main__":
    unittest.main()
