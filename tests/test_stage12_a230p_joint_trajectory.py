"""A2.30-P: technical controls for preregistered non-exhaustive joint witness model."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230p_joint_prefix_experiment import evaluate
from audit_stage12_issue110_b_a230p_joint_trajectories import (
    JointStep, PhysicalPrefixWitness,
)


class JointTrajectorySafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="a230p-unit-")
        cls.output=Path(cls.temp.name)/"experiment"
        cls.summary=evaluate(cls.output)
        cls.train=json.loads(
            (cls.output/"a230p-training-manifest.json").read_text()
        )
        cls.tests=json.loads(
            (cls.output/"a230p-heldout-physical-results.json").read_text()
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_physical_world_accounting_and_strict_train_test_disjointness(self):
        a=self.summary
        self.assertEqual(a["training_physical_worlds"],48)
        self.assertEqual(a["training_physical_steps"],132)
        self.assertEqual(a["heldout_physical_worlds"],80)
        self.assertEqual(a["heldout_physical_steps"],220)
        self.assertEqual(a["physical_worlds_total"],128)
        self.assertEqual(a["physical_steps_total"],352)
        self.assertEqual(a["new_i0_births"],0)
        self.assertEqual(a["new_autonomous_i0_steps"],0)
        self.assertTrue(a["models_frozen_before_any_test_world"])
        self.assertFalse(a["oracle_feedback_to_i0"])
        self.assertFalse(a["deployable_to_i0"])
        ids={item["world_id"] for item in self.train["training_witnesses"]}
        ids_test={item["world_id"] for item in self.tests}
        self.assertEqual(len(ids),48)
        self.assertEqual(len(ids_test),80)
        self.assertFalse(ids.intersection(ids_test))
        self.assertEqual(
            self.train["training_witness_corpus_sha256"],
            a["training_witness_corpus_sha256"]
        )

    def test_id_joint_continuations_and_terminal_step_witnessed(self):
        subset=[x for x in self.tests if x["stage"]=="heldout_ID"]
        self.assertEqual(len(subset),48)
        self.assertTrue(all(x["result"]["covered"] for x in subset))
        self.assertTrue(all(
            x["result"]["joint_branch_witnessed"] is True
            and x["result"]["terminal_step_in_empirical_set"] is True
            for x in subset
        ))
        self.assertEqual(
            self.summary["strata"]["heldout_ID"]["joint_matches"],48
        )

    def test_model_expresses_delayed_terminal_not_seen_on_first_step(self):
        late=[x for x in self.tests if x["stage"]=="heldout_ID"
              and x["family"] in ("WAIT","EAT")
              and x["result"]["first_terminal_step"] in (2,3)]
        self.assertEqual(len(late),8)
        self.assertTrue(all(
            x["model"]["single_step_baseline_witnessed_terminal"] is False
            and x["result"]["observed_possible_late_terminal"] is True
            and x["model"]["risk_label"]=="observed_terminal_possible"
            for x in late
        ))
        self.assertEqual(
            self.summary["strata"]["heldout_ID"]
            ["late_terminal_absent_from_first_step_witness"],8
        )

    def test_hidden_ood_cannot_claim_complete_joint_behavior(self):
        subset=[x for x in self.tests if x["stage"]=="heldout_hidden_OOD"]
        self.assertEqual(len(subset),24)
        self.assertTrue(all(
            x["result"]["covered"] is True
            and x["result"]["novel_joint_branch"] is True
            for x in subset
        ))
        self.assertEqual(
            self.summary["strata"]["heldout_hidden_OOD"]["novel_branches"],24
        )
        self.assertTrue(any(
            x["result"]["first_terminal_step"]==2
            and x["result"]["terminal_step_in_empirical_set"] is False
            for x in subset
        ))

    def test_visible_unseen_context_and_prefix_return_pure_abstention(self):
        subset=[
            x for x in self.tests
            if x["stage"]=="heldout_unknown_context"
        ]
        self.assertEqual(len(subset),8)
        self.assertTrue(all(
            x["model"]["status"]=="abstain_unknown_context"
            and x["model"]["supported_physical_worlds"]==0
            and x["model"]["empirical_branches"]==[]
            and x["result"]["covered"] is False
            for x in subset
        ))

    def test_terminal_worlds_never_continue_and_safety_never_certified(self):
        self.assertTrue(all(
            not x["model"]["certifies_safe"]
            and x["model"]["unseen_hidden_hazard_not_excluded"]
            and x["model"]["risk_label"] in (
                "observed_terminal_possible","observed_harm_possible",
                "unknown_hidden_risk","unavailable"
            )
            for x in self.tests
        ))
        for row in self.tests:
            w=row["witness"]
            physical=row["source_lab_physics"]
            terminal=w["first_terminal_step"]
            self.assertEqual(len(w["steps"]),row["physical_steps"])
            self.assertEqual(len(physical["observed_physical_examples"]),
                             row["physical_steps"])
            if terminal is not None:
                self.assertEqual(terminal,len(w["steps"]))
                self.assertTrue(w["steps"][-1]["terminal"])
                self.assertTrue(all(
                    not step["terminal"] for step in w["steps"][:-1]
                ))
            else:
                self.assertEqual(len(w["steps"]),3)
                self.assertFalse(any(x["terminal"] for x in w["steps"]))

    def test_adversarial_post_terminal_extension_is_invalid(self):
        original=next(
            x for x in self.tests
            if x["result"]["first_terminal_step"] is not None
        )
        from i0.equipment import SimulationState, SimulationNeighbor
        from i0.interfaces import PrimitiveCommand
        # Validate that a terminal step cannot be followed by another step:
        # use an authentic training state/step shape, no invented world event.
        from run_stage12_issue110_b_a230p_joint_prefix_experiment import (
            run_physical_world,
        )
        witness,_=run_physical_world(
            stage="unit_negative",family="MOV",variant="lethal_east",
            food=30.0,position=(2,2),
        )
        forged=replace(witness,steps=witness.steps+(
            JointStep(
                cumulative_delta=dict(witness.steps[0].cumulative_delta),
                terminal=False,
            ),
        ))
        with self.assertRaisesRegex(ValueError,"postterminal"):
            forged.validate()

    def test_forecast_model_cannot_see_external_world_or_oracle(self):
        source=(Path(__file__).resolve().parents[1]/
                "scripts/audit_stage12_issue110_b_a230p_joint_trajectories.py").read_text()
        self.assertNotIn("from lab.world import",source)
        self.assertNotIn("def predict(",source)
        self.assertNotIn("Stage6Runtime",source)
        self.assertNotIn('risk_label="safe"',source)
        self.assertNotIn("import Oracle",source)


if __name__=="__main__":
    unittest.main()
