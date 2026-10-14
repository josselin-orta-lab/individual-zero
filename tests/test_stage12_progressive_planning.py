"""Opt-in Stage6 progressive planning: never changes legacy baseline policy."""
from dataclasses import replace
import unittest
from i0.modules.stage6_planning import Stage6PlanningConfig, SimulatorPlanner
from i0.modules.simulator import Simulator, SimulatorConfig
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_stage6_planning import shelter_planner


class ProgressivePlanningContracts(unittest.TestCase):
    def test_flag_off_is_historically_default(self):
        planner, state = shelter_planner()
        self.assertFalse(planner._config.progressive_subgoals)
        baseline = planner.plan_target(initial_state=state, target="shelter_here")
        self.assertEqual(baseline.status, "plan_found")
        self.assertEqual(len(baseline.commands), 4)

    def test_opt_in_preserves_complete_goal_plan(self):
        planner, state = shelter_planner()
        planner._config = replace(planner._config, progressive_subgoals=True)
        result = planner.plan_target(initial_state=state, target="shelter_here")
        self.assertEqual(result.status, "plan_found")
        self.assertFalse(result.partial_progress)
        self.assertEqual(len(result.commands), 4)

    def test_config_validates_flag_type(self):
        planner, _ = shelter_planner()
        with self.assertRaises(ValueError):
            replace(planner._config, progressive_subgoals=1).validate()

    def test_no_invented_progress_if_no_predictive_edge(self):
        planner, state = shelter_planner()
        planner._config = replace(planner._config, max_depth=1,
                                  progressive_subgoals=True)
        result = planner.search(initial_state=state, target=lambda _: False)
        self.assertEqual(result.status, "incomplete_model")
        self.assertEqual(result.commands, ())


if __name__ == "__main__":
    unittest.main()
