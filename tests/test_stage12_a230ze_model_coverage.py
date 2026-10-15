"""A2.30-ZE preregistered Stage6 shadow capability and adversarial controls."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230ze_model_coverage import (
    run, frozen_models, decode_state, stage6_shadow, COLLECT_B,
    MOVE_E, EAT_B, EXPECTED_TRAIN_WORLDS, EXPECTED_TEST_WORLDS,
)


class Stage6PhysicallyWitnessedFirstEdgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="a230ze-lab-")
        cls.output=Path(cls.temp.name)/"study"
        cls.summary=run(cls.output)
        cls.training=json.loads(
            (cls.output/"a230ze-training-manifest.json").read_text()
        )
        cls.tests=json.loads(
            (cls.output/"a230ze-heldout-shadows.json").read_text()
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_preregistered_three_way_world_split(self):
        s=self.summary
        self.assertEqual(s["detached_worlds_total"],33)
        self.assertEqual(s["detached_physical_training_worlds"],9)
        self.assertEqual(s["detached_physical_training_steps"],13)
        self.assertEqual(s["heldout_worlds_with_no_physical_actions"],24)
        self.assertEqual(s["heldout_physical_actions"],0)
        self.assertEqual(s["new_I0_births"],0)
        self.assertEqual(s["new_I0_autonomous_world_steps"],0)
        self.assertFalse(s["Stage6_production_model_accepted"])
        self.assertFalse(s["actual_I0_food_goal_success_proven"])
        self.assertFalse(s["oracle_or_hidden_B_effect_fed_to_model"])
        self.assertEqual(len(self.training["demonstrations"]),9)
        self.assertEqual(len(self.tests),24)
        train_ids={x["source_world_id"] for x in self.training["demonstrations"]}
        test_ids={x["world_id"] for x in self.tests}
        self.assertEqual(len(train_ids),9)
        self.assertEqual(len(test_ids),24)
        self.assertFalse(train_ids & test_ids)

    def test_known_physical_prefix_yields_partial_without_eat(self):
        rows=[x for x in self.tests if
              x["cohort"]=="same_observable_input"]
        self.assertEqual(len(rows),8)
        for x in rows:
            base=x["baseline_A_only"]
            enriched=x["enriched_demonstrated_prefix"]
            self.assertEqual(base["status"],"incomplete_model")
            self.assertEqual(base["root_available_edges"],0)
            self.assertEqual(enriched["status"],"partial_progress")
            self.assertTrue(enriched["partial_progress"])
            self.assertEqual(enriched["root_available_edges"],1)
            self.assertEqual(enriched["commands"],[
                (COLLECT_B if x["layout_external_only"]=="B_LOCAL"
                 else MOVE_E).as_dict()
            ])
            self.assertFalse(enriched["has_any_ingestion_prediction"])
            self.assertIsNone(enriched["true_I0_UC_measured"])

    def test_heldout_ood_and_blocked_cases_never_invent_transition(self):
        rows=[x for x in self.tests if
              x["cohort"]!="same_observable_input"]
        self.assertEqual(len(rows),16)
        self.assertTrue(all(
            x["enriched_demonstrated_prefix"]["status"]=="incomplete_model"
            and x["enriched_demonstrated_prefix"]["root_available_edges"]==0
            and not x["enriched_demonstrated_prefix"]["commands"]
            for x in rows
        ))
        self.assertEqual(self.summary["cohorts"]["unseen_coordinates"][
            "enriched_incomplete"],8)
        self.assertEqual(self.summary["cohorts"]["unavailable_or_blocked"][
            "enriched_incomplete"],8)

    def test_training_prefix_contains_no_B_ingestion_or_terminality(self):
        items=self.training["demonstrations"]
        self.assertTrue(self.training["all_training_commands_non_ingestive"])
        self.assertEqual(sum(x["physical_steps"] for x in items),13)
        self.assertTrue(all(x["no_terminal"] for x in items))
        example_rows=[
            ex for item in items
            for ex in item["observed_physical_examples"]
        ]
        self.assertEqual(len(example_rows),13)
        self.assertFalse(any(e["terminal"] for e in example_rows))
        self.assertTrue(all(
            e["command"]["primitive"] in ("collecter","se_deplacer")
            for e in example_rows
        ))
        self.assertFalse(any(
            e["command"]==EAT_B.as_dict() for e in example_rows
        ))

    def test_hidden_effects_indistinguishable_before_exposure(self):
        groups={}
        for row in self.training["demonstrations"]:
            if row["layout_external_only"]=="A_REFERENCE":
                continue
            key=(row["layout_external_only"],
                 row["root_accessible"]["body"]["food"])
            groups.setdefault(key,[]).append(row)
        self.assertEqual(len(groups),4)
        for group in groups.values():
            self.assertEqual(len(group),2)
            self.assertEqual(
                set(x["hidden_effect_external_only"] for x in group),
                {"benign","toxic_lethal"}
            )
            self.assertEqual(group[0]["root_accessible"],
                             group[1]["root_accessible"])
            self.assertEqual(
                [x["observed_physical_examples"] for x in group[:1]][0],
                group[1]["observed_physical_examples"]
            )

    def test_model_never_certifies_safety_nor_executes_candidate(self):
        self.assertTrue(self.summary["model_contains_no_B_ingestion"])
        self.assertTrue(self.summary["model_contains_no_safety_certificate"])
        for case in self.tests:
            self.assertEqual(case["physical_steps_executed_in_heldout_world"],0)
            self.assertTrue(case["no_B_ingestion_or_test_physics"])
            self.assertTrue(case["hidden_B_effect_still_unidentified"])
            for key in ("baseline_A_only","enriched_demonstrated_prefix"):
                evidence=case[key]
                self.assertFalse(evidence["guarantees_berry_b_safe"])
                self.assertTrue(evidence["no_physical_command_dispatched"])
                self.assertFalse(evidence["has_any_ingestion_prediction"])
                self.assertIsNone(evidence["true_I0_UC_measured"])

    def test_fabricated_or_hidden_feature_cannot_enter_exact_key(self):
        row=deepcopy(self.tests[0]["first_person_state"])
        row["hidden_B_toxicity"]=-100.0
        with self.assertRaisesRegex(ValueError,"secret"):
            decode_state(row)

    def test_inadmissible_B_eating_example_rejected_from_physical_training(self):
        manifest=deepcopy(self.training["demonstrations"])
        first=next(x for x in manifest if x["layout_external_only"]=="B_LOCAL")
        poisoned=deepcopy(first["observed_physical_examples"][0])
        poisoned["command"]=EAT_B.as_dict()
        first["observed_physical_examples"].append(poisoned)
        with self.assertRaisesRegex(AssertionError,"ingestion knowledge"):
            frozen_models(manifest)

    def test_corrupted_root_after_unknown_coordinate_does_not_generalize(self):
        ood=next(x for x in self.tests if
                 x["cohort"]=="unseen_coordinates")
        self.assertEqual(ood["position"],[7,7])
        self.assertEqual(ood["enriched_demonstrated_prefix"][
            "root_available_edges"],0)
        self.assertIsInstance(ood["paired_physical_demonstrator"],str)
        self.assertTrue(ood["paired_physical_demonstrator"].startswith("ze-train-"))

    def test_prospective_learner_does_not_import_born_I0_or_oracle(self):
        path=(Path(__file__).resolve().parents[1]/
              "scripts/run_stage12_issue110_b_a230ze_model_coverage.py")
        source=path.read_text()
        self.assertNotIn("Stage12Runtime(",source)
        self.assertNotIn("build_life(",source)
        self.assertNotIn("life.run_step(",source)
        self.assertNotIn("import Oracle",source)
        self.assertNotIn("def install_B_prior(",source)


if __name__=="__main__":
    unittest.main()
