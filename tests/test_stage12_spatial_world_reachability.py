"""Issue #110: structural negative control for preknown-blocked world judgements.

This test does not assert that all possible external constraints are
unobservable. It proves that CURRENT Stage6 goal planning cannot propose a
move to a cell its very own accessible perception marks as nonpassable.
"""
import unittest

from i0.equipment import SimulationNeighbor, SimulationState
from i0.modules.stage6_planning import SimulatorPlanner


def accessible_state(east_passable: bool):
    neighbors = (
        SimulationNeighbor("north", 2, 1, True, False, (), False),
        SimulationNeighbor("south", 2, 3, True, False, (), False),
        SimulationNeighbor("east", 3, 2, east_passable, True, (), False),
        SimulationNeighbor("west", 1, 2, True, False, (), False),
    )
    return SimulationState(
        schema_version="stage12-world-reachability-test-v1",
        x=2, y=2,
        body={"energy": 50.0, "food": 70.0, "water": 20.0,
              "integrity": 100.0},
        inventory={}, current_water_source=False,
        current_resources=(), adjacent=neighbors,
        known_shelter_here=False, is_night=False,
    )


class PreknownBlockedTargetReachabilityTests(unittest.TestCase):
    def test_current_planner_filters_goal_relevant_blocked_cell(self):
        state = accessible_state(False)
        state.validate()
        options = SimulatorPlanner.candidate_commands(state)
        directions = {
            cmd.parameters["direction"] for cmd in options
            if cmd.primitive == "se_deplacer"
        }
        self.assertEqual(directions, {"north", "south", "west"})
        self.assertNotIn("east", directions)

    def test_only_changing_passability_makes_east_eligible(self):
        before = accessible_state(False)
        after = accessible_state(True)
        blocked = SimulatorPlanner.candidate_commands(before)
        passable = SimulatorPlanner.candidate_commands(after)
        self.assertFalse(any(
            c.primitive == "se_deplacer"
            and c.parameters.get("direction") == "east"
            for c in blocked
        ))
        self.assertTrue(any(
            c.primitive == "se_deplacer"
            and c.parameters.get("direction") == "east"
            for c in passable
        ))


if __name__ == "__main__":
    unittest.main()
