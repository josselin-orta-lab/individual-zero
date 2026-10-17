"""A2.30-W prospective preingestion probe adversarial non-regressions."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230w_prospective_probes import (
    experiment,validate_and_score,observation_key,digest,
)


class ProspectivePreexposureProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix="a230w-tests-")
        cls.directory=Path(cls.tmp.name)/"physical"
        cls.summary=experiment(cls.directory)
        cls.acted=json.loads(
            (cls.directory/"a230w-acted-physical-worlds.json").read_text()
        )
        cls.controls=json.loads(
            (cls.directory/"a230w-passive-positive-controls.json").read_text()
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def score(self,acted=None,controls=None):
        return validate_and_score(
            deepcopy(self.acted if acted is None else acted),
            deepcopy(self.controls if controls is None else controls),
        )

    def test_92_original_worlds_240_physical_actions_and_terminal_boundary(self):
        result=self.score()
        self.assertEqual(result["total_laboratory_world_instances"],92)
        self.assertEqual(result["physically_independent_acted_worlds"],80)
        self.assertEqual(result["passive_positive_control_worlds"],12)
        self.assertEqual(result["actually_applied_worldbody_steps"],240)
        self.assertEqual(result["physical_probe_steps"],100)
        self.assertEqual(result["physical_food_suffix_steps"],140)
        self.assertEqual(result["external_terminal_ingestions"],16)
        self.assertEqual(result["fully_committed_food_successes"],48)
        self.assertEqual(result["fully_committed_deaths"],16)
        self.assertEqual(result["fully_committed_insufficient_results"],16)
        self.assertEqual(result["new_i0_births"],0)
        self.assertEqual(result["new_i0_autonomous_steps"],0)
        self.assertFalse(result["uc_cost_evaluated"])
        self.assertFalse(result["can_deploy_predictor"])

    def test_all_blinded_pair_historical_inputs_equivalent_before_ingestion(self):
        result=self.score()
        self.assertEqual(result["preexposure_observation_equivalence_classes"],16)
        self.assertEqual(result["latent_worlds_per_first_person_class"],5)
        self.assertEqual(result["hidden_cause_pairs_same_first_person_history"],160)
        self.assertEqual(result["hidden_cause_pairs_separated_before_ingestion"],0)
        self.assertEqual(result["bounded_deterministic_policies_enumerated"],65536)
        self.assertEqual(result["zero_death_policies_in_bounded_domain"],1)
        self.assertEqual(result["zero_death_and_positive_food_policies"],0)

    def test_visible_controls_are_detectable_but_not_food_safety_labels(self):
        r=self.score()
        self.assertEqual(r["positive_visible_berry_kind_differences"],4)
        self.assertEqual(r["positive_visible_obstacle_differences"],4)
        self.assertTrue(all(x["no_food_safety_claim"] for x in self.controls))

    def test_probe_physical_cost_and_no_postterminal_lived_capture(self):
        r=self.score()
        self.assertEqual(r["probe_cost_delta_per_world"],{
            "immediate":{"energy":0.0,"food":0.0,"water":0.0,"integrity":0.0},
            "wait_twice":{"energy":-1.0,"food":-1.0,"water":-0.4,"integrity":0.0},
            "collect_first":{"energy":-0.75,"food":-0.5,
                             "water":-0.2,"integrity":0.0},
            "west_return":{"energy":-2.0,"food":-1.0,
                           "water":-0.4,"integrity":0.0},
        })
        for x in self.acted:
            self.assertFalse(x["certifies_safe_from_probe"])
            self.assertEqual(x["postterminal_lived_capture_count"],0)
            if x["latent_external_bench_only"]=="toxin_100":
                self.assertFalse(x["physically_alive_after_ingestion"])
                self.assertIsNone(x["lived_post_ingestion_if_survivor"])
                self.assertIsNotNone(
                    x["physical_terminal_step_external_only"]
                )

    def test_hidden_variant_injected_into_accessible_history_fails(self):
        examples=deepcopy(self.acted)
        examples[0]["predecision_lived_history"][0]["state"][
            "latent_external_only"
        ]="benign"
        with self.assertRaisesRegex(ValueError,"hidden"):
            self.score(acted=examples)

    def test_future_ingestion_observation_pretended_as_probe_fails(self):
        examples=deepcopy(self.acted)
        target=next(x for x in examples if
                    x["latent_external_bench_only"]=="toxin_7")
        target["predecision_lived_history"][-1]["state"]=deepcopy(
            target["lived_post_ingestion_if_survivor"]
        )
        with self.assertRaisesRegex(ValueError,"history leak"):
            self.score(acted=examples)

    def test_forged_safety_certificate_is_rejected(self):
        examples=deepcopy(self.acted)
        examples[0]["certifies_safe_from_probe"]=True
        with self.assertRaisesRegex(ValueError,"history leak"):
            self.score(acted=examples)

    def test_death_reported_as_lived_result_is_rejected(self):
        examples=deepcopy(self.acted)
        target=next(x for x in examples if
                    x["latent_external_bench_only"]=="toxin_100")
        target["lived_post_ingestion_if_survivor"]=deepcopy(
            target["physical_commands_and_receipts_external_only"]
            [-1]["after_for_external_bench"]
        )
        with self.assertRaisesRegex(ValueError,"postmortem"):
            self.score(acted=examples)

    def test_invented_world_action_after_mortality_is_rejected(self):
        examples=deepcopy(self.acted)
        target=next(x for x in examples if
                    x["latent_external_bench_only"]=="toxin_100")
        fake=deepcopy(
            target["physical_commands_and_receipts_external_only"][-1]
        )
        fake["t_monde"]+=1
        fake["terminal_external_only"]=False
        fake["sha256"]=digest({k:v for k,v in fake.items() if k!="sha256"})
        target["physical_commands_and_receipts_external_only"].append(fake)
        target["physical_total_steps"]+=1
        with self.assertRaisesRegex(ValueError,"action count"):
            self.score(acted=examples)

    def test_forged_terminal_transition_is_rejected(self):
        examples=deepcopy(self.acted)
        terminal=next(x for x in examples if
                      x["latent_external_bench_only"]=="toxin_100")
        terminal["physical_commands_and_receipts_external_only"][-1][
            "terminal_external_only"
        ]=False
        with self.assertRaisesRegex(ValueError,"physical receipts"):
            self.score(acted=examples)

    def test_blinded_hazard_effect_falsified_rejected_even_if_receipt_resigned(self):
        examples=deepcopy(self.acted)
        toxic=next(x for x in examples if
                   x["latent_external_bench_only"]=="toxin_30")
        terminal=toxic["physical_commands_and_receipts_external_only"][-1]
        terminal["after_for_external_bench"]["body"]["integrity"]+=7.0
        terminal["sha256"]=digest({k:v for k,v in terminal.items()
                                   if k!="sha256"})
        toxic["lived_post_ingestion_if_survivor"]=deepcopy(
            terminal["after_for_external_bench"]
        )
        with self.assertRaisesRegex(ValueError,"physical berry hazard"):
            self.score(acted=examples)

    def test_positive_visible_difference_erased_and_resigned_is_detected(self):
        controls=deepcopy(self.controls)
        base=next(x for x in controls if x["control"]=="resource_berry_a"
                  and x["food"]==35 and x["position"]==[5,5])
        berry=next(x for x in controls if x["control"]=="resource_berry_b"
                   and x["food"]==35 and x["position"]==[5,5])
        berry["visible_state"]=deepcopy(base["visible_state"])
        berry["visible_state_sha256"]=digest(berry["visible_state"])
        with self.assertRaisesRegex(ValueError,"visible resource"):
            self.score(controls=controls)

    def test_duplicate_world_label_is_refused(self):
        examples=deepcopy(self.acted)
        examples[1]["world_id"]=examples[0]["world_id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.score(acted=examples)

    def test_altered_physical_probe_cost_refused(self):
        examples=deepcopy(self.acted)
        row=next(x for x in examples if x["probe"]=="wait_twice")
        row["physical_probe_effect"]["food"]=0
        with self.assertRaisesRegex(ValueError,"acquisition cost"):
            self.score(acted=examples)

    def test_no_stage6_oracle_policy_calls(self):
        source=(Path(__file__).resolve().parents[1]/
            "scripts/run_stage12_issue110_b_a230w_prospective_probes.py"
        ).read_text()
        self.assertNotIn("SimulatorPlanner(",source)
        self.assertNotIn("Stage6Runtime(",source)
        self.assertNotIn("Stage12Runtime(",source)
        self.assertNotIn("import Oracle",source)
        self.assertNotIn("def predict(",source)


if __name__=="__main__":
    unittest.main()
