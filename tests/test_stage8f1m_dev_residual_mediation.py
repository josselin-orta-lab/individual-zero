"""Safety tests for F1M DEV-only mediator design; NO World.step in this suite."""
from __future__ import annotations

from copy import deepcopy
import unittest

from tools import stage8f1m_dev_residual_mediation as M


class DummyMind:
    def __init__(self):
        self.acc={"drink":1.5,"eat":0.4}
        self.intention="drink"
        self.values=[[0.0,0.0]]
        self.buffer=[]


class TestStage8F1MNoBirthSafety(unittest.TestCase):
    def test_dev_only_grid_and_unique_future_seeds(self):
        small,big=M.dev_grid(),M.dev_grid(full=True)
        self.assertEqual(len(small["origins"]),2)
        self.assertEqual(len(big["origins"]),8)
        self.assertEqual([o["id"] for o in big["origins"]],
                         [f"DEV_M{i:02d}" for i in range(1,9)])
        self.assertEqual({o["seed"] for o in big["origins"]},set(M.DEV_ONLY_SEEDS))
        self.assertFalse(set(M.DEV_ONLY_SEEDS)&(M.RESERVED_L|M.DEV_L))
        self.assertNotIn("workflow_dispatch",M.SCHEMA)
        M.source_gate(small)
        M.source_gate(big)

    def test_malformed_science_grid_refused_before_world(self):
        grid=deepcopy(M.dev_grid())
        grid["origins"][0]["seed"]=next(iter(M.RESERVED_L))
        with self.assertRaises(PermissionError):
            M.source_gate(grid)
        grid=M.dev_grid()
        grid["phase"]="SCIENTIFIC"
        with self.assertRaises(PermissionError):
            M.source_gate(grid)

    def test_carry_no_change_zero_values_only_and_no_action(self):
        mind=DummyMind()
        before=deepcopy(mind)
        carry=M.residual_intervention(mind,"carry")
        self.assertEqual(carry["before_mind"],carry["after_mind"])
        self.assertEqual(before.__dict__,mind.__dict__)
        fresh=DummyMind()
        zero=M.residual_intervention(fresh,"zero")
        self.assertEqual(zero["keys"],["drink","eat"])
        self.assertEqual(fresh.acc,{"drink":0.0,"eat":0.0})
        self.assertEqual(fresh.intention,before.intention)
        self.assertEqual(fresh.values,before.values)
        self.assertEqual(fresh.buffer,before.buffer)
        self.assertTrue(zero["no_action_override"])
        self.assertNotEqual(zero["before_mind"],zero["after_mind"])
        with self.assertRaises(ValueError):
            M.residual_intervention(DummyMind(),"unregistered")

    def test_cost_gate_rejects_fake_equalization(self):
        a={"before_world":"same","before_mind":"same","capture":"same",
           "cognitive_work":{"cycles":7,"simulated_steps":13,"memory_items":5,"replays":0},
           "requested_native_cost":{"energy":0.16,"vigilance":0.38},
           "decision_remaining":[10,10,10,10,10],
           "native_motor":{"cognitive_accounting":"actually paid"}}
        b=deepcopy(a)
        self.assertTrue(M.t5_pair_cost(a,b))
        self.assertTrue(M.t6_pair_cost(a,b))
        b["cognitive_work"]["cycles"]=8
        self.assertFalse(M.t5_pair_cost(a,b))
        self.assertFalse(M.t6_pair_cost(a,b))
        b=deepcopy(a)
        b["native_motor"]["cognitive_accounting"]="unpaid"
        self.assertFalse(M.t6_pair_cost(a,b))
        b=deepcopy(a)
        b["before_mind"]="diff-residual"
        self.assertFalse(M.t5_pair_cost(a,b))
        self.assertTrue(M.t6_pair_cost(a,b))

    def test_corporeal_positive_tradeoff_and_survival_not_conflated(self):
        def arm(lived,body):
            return {"metrics":{"lived_ticks_t5_t60":lived,
                 "terminal_body":body,"alive_at_horizon":True,
                 "paid_decision":{},"paid_learning":{},"water_drinks":0,
                 "foods_actually_eaten":0}}
        x=arm(55,[3,4,5,6,7])
        y=arm(55,[2,4,5,6,7])
        result=M.body_comparison(x,y)
        self.assertEqual(result["pareto"],"CARRY_FIVE_CHANNEL_DOMINANCE")
        self.assertEqual(result["delta_lived_ticks_t6_t60"],0)
        z=arm(55,[2,4,5,7,7])
        self.assertEqual(M.body_comparison(x,z)["pareto"],"MIXED_BODY_TRADEOFF")
        z=arm(54,[2,4,5,6,7])
        self.assertEqual(M.body_comparison(x,z)["pareto"],"NOT_COMPARABLE_HORIZON")
        self.assertEqual(M.body_comparison(x,z)["delta_lived_ticks_t6_t60"],1)


if __name__=="__main__":
    unittest.main()
