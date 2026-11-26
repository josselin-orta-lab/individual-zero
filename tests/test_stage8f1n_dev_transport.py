"""Adversarial F1N development only: funded margin and native sham contracts."""
from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
import unittest

from i3.modules.body import BodyLaws,CognitiveBudget,CognitiveWork,CognitiveFundingError
from i3.modules.genome import midpoint
from tools import stage8f1n_dev_native_transport as P
from tools import stage8f1n_independent_dev_cold as COLD
from tools import stage8f1l_paid_content_body_value_dev as L
from tools.stage8f1n_paid_margin_mind import F1NMarginMind


class TestPaidOwnMarginDEV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        g=P.dev_grid("A",False)
        cls.grid=g
        origin=g["origins"][0]
        world=P.dev_world(g,origin)
        mind=F1NMarginMind(midpoint(),origin["seed"])
        for _ in range(4):
            L.paid_step(world,mind)
        cls.t5=P.t5(world,mind)
        cls.t5_world=deepcopy(world)
        cls.t5_mind=deepcopy(mind)
        P.fork(mind,"margin")
        cls.t6=L.paid_step(world,mind)

    def test_heldout_identity_disallowed_without_scientific_gate(self):
        bad=deepcopy(self.grid["origins"][0])
        bad["id"]="N01"
        bad["seed"]=202611259801
        with self.assertRaises(PermissionError):
            P.dev_world(self.grid,bad)
        with self.assertRaises(PermissionError):
            P.dev_source_gate({**self.grid,"origins":[bad]})

    def test_two_disjoint_development_cohorts_and_prereg_grid_intact(self):
        a=P.dev_grid("A")
        b=P.dev_grid("B")
        self.assertEqual(len(a["origins"]),len(b["origins"]))
        self.assertEqual(len(a["origins"]),8)
        self.assertFalse(set(x["seed"] for x in a["origins"]) &
                         set(x["seed"] for x in b["origins"]))
        self.assertFalse(set(x["seed"] for x in a["origins"]) &
                         set(range(202611259801,202611259849)))

    def test_own_margin_real_postaction_memory_write(self):
        w=self.t5["write"]
        self.assertEqual(w["genuinely_executed_work"]["memory_items"],1)
        self.assertEqual(w["actual_paid_memory_bill"]["energy"]["paid"],0.0002)
        self.assertEqual(w["actual_paid_memory_bill"]["energy"]["unpaid"],0.)
        self.assertEqual(w["world_before_write"]["t"],5)
        COLD.verified_paid_t5_write(w,self.t5["step"])

    def test_t6_real_memory_read_paid_and_source_unmodified(self):
        witness=self.t6["decision_info"]["observer"]["competition_witness"]
        self.assertTrue(witness["f1n_margin_read"]["memory_read_paid"])
        self.assertEqual(witness["f1n_margin_read"]["mode"],"margin")
        self.assertGreater(self.t6["cognitive_work"]["memory_items"],0)
        self.assertGreater(self.t5["write"]["own_final_q"],0)
        COLD._actual_t6_competition(self.t6,"margin")

    def test_second_paid_read_forbidden_after_one_competition(self):
        mind=F1NMarginMind(midpoint(),202611269101)
        mind.f1n_owned_margin={"source_tick":5,"key":"a","q":0.5}
        mind.arm_paid_t6_read("margin")
        grant=CognitiveBudget((70,70,40,95,95),BodyLaws())
        mind._compete([("a",1.),("b",0.)],5,grant)
        self.assertEqual(grant.work.memory_items,1)
        self.assertTrue(mind.f1n_read_used)
        with self.assertRaises(ValueError):
            mind.arm_paid_t6_read("masked")

    def test_masked_and_margin_equal_real_cost_no_fake_cycles(self):
        mind=F1NMarginMind(midpoint(),202611269101)
        mind.f1n_owned_margin={"source_tick":5,"key":"a","q":0.5}
        masked=deepcopy(mind)
        mind.arm_paid_t6_read("margin")
        masked.arm_paid_t6_read("masked")
        left=CognitiveBudget((70,70,40,95,95),BodyLaws())
        right=CognitiveBudget((70,70,40,95,95),BodyLaws())
        mind._compete([("a",1.),("b",0.)],5,left)
        masked._compete([("a",1.),("b",0.)],5,right)
        self.assertEqual(left.work,right.work)
        self.assertEqual(left.remaining,right.remaining)
        self.assertEqual(left.work.memory_items,1)
        l=mind._observer_competition["thresholds"]
        r=masked._observer_competition["thresholds"]
        self.assertAlmostEqual(l["a"],r["a"]*.75)
        self.assertEqual(l["b"],r["b"])

    def test_unfunded_t6_read_fails_before_using_margin(self):
        m=F1NMarginMind(midpoint(),202611269101)
        m.f1n_owned_margin={"source_tick":5,"key":"a","q":0.5}
        m.arm_paid_t6_read("margin")
        grant=CognitiveBudget((0.,70.,40.,90.,90.),BodyLaws())
        with self.assertRaises(CognitiveFundingError):
            m._compete([("a",1.),("b",0.)],5,grant)
        self.assertEqual(grant.work,CognitiveWork())

    def test_tampering_with_threshold_rejected_by_independent_cold(self):
        altered=deepcopy(self.t6)
        witness=altered["decision_info"]["observer"]["competition_witness"]
        winner=witness["winner_before_control"]
        witness["thresholds"][winner]+=0.01
        with self.assertRaisesRegex(AssertionError,"threshold"):
            COLD._actual_t6_competition(altered,"margin")

    def test_tampering_with_memory_write_debit_rejected(self):
        altered=deepcopy(self.t5["write"])
        altered["actual_paid_memory_bill"]["energy"]["paid"]=0.0
        with self.assertRaises((ValueError,AssertionError)):
            COLD.verified_paid_t5_write(altered,self.t5["step"])

    def test_tampering_with_stored_q_rejected(self):
        altered=deepcopy(self.t5["write"])
        altered["own_final_q"]=0.0
        with self.assertRaises(AssertionError):
            COLD.verified_paid_t5_write(altered,self.t5["step"])

    def test_cold_module_has_no_engine_or_producer_import(self):
        src=Path(COLD.__file__).read_text()
        tree=ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom):
                self.assertFalse((node.module or "").startswith(("i3", "src.i3")))
                self.assertFalse((node.module or "").startswith(
                    "tools.stage8f1n_dev_native_transport"))
            elif isinstance(node,ast.Import):
                for alias in node.names:
                    self.assertFalse(alias.name.startswith(("i3", "src.i3")))
        self.assertFalse(any(isinstance(n,ast.Call) and
            isinstance(n.func,ast.Attribute) and n.func.attr=="step"
            for n in ast.walk(tree)))


if __name__=="__main__":
    unittest.main()