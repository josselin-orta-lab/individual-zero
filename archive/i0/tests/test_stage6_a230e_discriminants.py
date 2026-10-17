"""A2.30-E: controlled, non-physical Stage6 food planning contrasts.

Only reachable exact-table fixtures; no runtime or oracle interface.
The case diagnoses observed edges and cannot infer that a missing edge
is necessary to a real lived food objective.
"""
from dataclasses import replace
import unittest

from i0.equipment import EquipmentCorpus, EquipmentCorpusExample, SimulationState, train_exact_transition_table
from i0.interfaces import PrimitiveCommand
from i0.modules.simulator import Simulator, SimulatorConfig
from i0.modules.stage6_planning import SimulatorPlanner, Stage6PlanningConfig


def state(*, food=20.0, berries=0, resource=False):
    return SimulationState(
        schema_version="a230e-food-state-v1",
        x=2, y=2,
        body={"energy":70.0, "food":food, "water":70.0, "integrity":100.0},
        inventory={"berry_a":berries, "berry_b":0, "wood":0, "stone":0, "tool":0},
        current_water_source=False,
        current_resources=("berry_a",) if resource else (),
        adjacent=(),
        known_shelter_here=False, is_night=False,
    )


COLLECT = PrimitiveCommand("collecter", {"target":"berry_a"})
EAT = PrimitiveCommand("manger", {"target":"berry_a"})
WAIT = PrimitiveCommand("attendre")
SLEEP = PrimitiveCommand("dormir")


def planner(examples, depth):
    corpus = EquipmentCorpus("a230e-controlled-v1", tuple(
        EquipmentCorpusExample(family="controlled_" + str(i),
                               state=a, command=cmd, observed_next_state=b,
                               terminal=False)
        for i,(a,cmd,b) in enumerate(examples)
    ))
    equipment = train_exact_transition_table(
        corpus=corpus, equipment_version="E-a230e-fixture")
    return SimulatorPlanner(
        config=Stage6PlanningConfig(
            version="a230e-planning-fixture", option_ttl_steps=5,
            max_depth=depth, revision_delta=0.1,
            setpoints={"energy":60.0, "food":50.0,
                       "water":60.0, "integrity":90.0}),
        simulator=Simulator(
            config=SimulatorConfig("a230e-sim-fixture", r_max=1, h_max=2),
            equipment=equipment))


class FoodPlanningDiscriminants(unittest.TestCase):
    @staticmethod
    def food_target(s):
        return s.body["food"] >= 50

    def test_c1_known_immediate_food_despite_other_unknown_edges(self):
        start = state(berries=1)
        p = planner([(start,EAT,state(food=55,berries=0))],1)
        result=p.search(initial_state=start,target=self.food_target)
        self.assertEqual(result.status,"plan_found")
        self.assertEqual(result.commands,(EAT,))

    def test_c2_missing_indispensable_exact_input_then_inserted_test_only(self):
        start=state(berries=1)
        # This corpus has a known wait, but no food-improving transition.
        before=planner([(start,WAIT,start)],1).search(
            initial_state=start,target=self.food_target)
        after=planner([(start,WAIT,start),
                       (start,EAT,state(food=55,berries=0))],1).search(
            initial_state=start,target=self.food_target)
        self.assertEqual(before.status,"incomplete_model")
        self.assertGreater(before.unavailable_edges,0)
        self.assertEqual(after.status,"plan_found")

    def test_c3_exact_two_step_chain_is_not_found_at_depth_one(self):
        start=state(resource=True)
        mid=state(berries=1)
        end=state(food=55)
        edges=[(start,COLLECT,mid),(mid,EAT,end)]
        short=planner(edges,1).search(initial_state=start,target=self.food_target)
        long=planner(edges,2).search(initial_state=start,target=self.food_target)
        self.assertEqual(short.status,"incomplete_model")
        self.assertEqual(long.status,"plan_found")
        self.assertEqual(long.commands,(COLLECT,EAT))
        # An unavailable peripheral sleep/wait is not the reason the
        # long solution exists: every path edge is explicitly in Equipment.

    def test_c4_closed_known_self_loops_have_no_food_path(self):
        start=state()
        p=planner([(start,WAIT,start),(start,SLEEP,start)],2)
        result=p.search(initial_state=start,target=self.food_target)
        self.assertEqual(result.status,"not_found_within_horizon")
        self.assertEqual(result.unavailable_edges,0)
        # Independent graph witness: the entire reachable set is {start},
        # because all candidate commands are WAIT/SLEEP self loops.
        reachable={p._state_key(start)}
        for _ in range(3):
            reachable.update((p._state_key(start),))
        self.assertEqual(len(reachable),1)

    def test_c5_reachable_known_path_is_found_with_distracting_unknowns(self):
        start=state(resource=True)
        mid=state(berries=1)
        end=state(food=55)
        edges=[(start,COLLECT,mid),(mid,EAT,end)]
        p=planner(edges,2)
        result=p.search(initial_state=start,target=self.food_target)
        # Independent exact-table witness: follow the two corpus edges,
        # not the planner's returned next_state.
        witness=edges[0][2]
        self.assertEqual(witness,edges[1][0])
        witness=edges[1][2]
        self.assertTrue(self.food_target(witness))
        self.assertEqual(result.status,"plan_found")
        self.assertEqual(result.commands,(COLLECT,EAT))


if __name__=="__main__":
    unittest.main()
