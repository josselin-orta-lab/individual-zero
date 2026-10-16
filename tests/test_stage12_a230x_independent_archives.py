"""A2.30-X: adversarial independent audit of original sealed W receipts."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230x_sealed_probes import (
    from_sealed_zip_extract,rebuild,hash_object,
)


class IndependentProspectiveWArchiveAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        left=from_sealed_zip_extract(Path(os.environ["A230X_SOURCE_311"]))
        right=from_sealed_zip_extract(Path(os.environ["A230X_SOURCE_312"]))
        if left!=right:
            raise AssertionError("original physical W artifacts differ")
        cls.acted=json.loads(left["a230w-acted-physical-worlds.json"])
        cls.control=json.loads(left["a230w-passive-positive-controls.json"])
        cls.summary=json.loads(left["a230w-summary.json"])

    def review(self,acted=None,control=None,summary=None):
        return rebuild(
            deepcopy(self.acted if acted is None else acted),
            deepcopy(self.control if control is None else control),
            deepcopy(self.summary if summary is None else summary),
        )

    def test_reconstructed_physical_first_person_and_positive_controls(self):
        audit=self.review()
        self.assertEqual(audit["original_acted_worlds"],80)
        self.assertEqual(audit["original_passive_visible_worlds"],12)
        self.assertEqual(audit["sealed_physical_actions_checked"],240)
        self.assertEqual(audit["recomputed_observation_classes"],16)
        self.assertEqual(audit["recomputed_indistinguishable_hidden_pairs"],160)
        self.assertEqual(audit["external_deaths_checked"],16)
        self.assertEqual(audit["surviving_food_goals_checked"],48)
        self.assertEqual(audit["surviving_insufficient_food_checked"],16)
        self.assertEqual(audit["positive_visible_species_differences"],4)
        self.assertEqual(audit["positive_visible_obstacle_differences"],4)
        self.assertEqual(audit["finite_deterministic_policies"],65536)
        self.assertEqual(audit["finite_zero_death_policies"],1)
        self.assertEqual(audit["finite_zero_death_and_food_policies"],0)
        self.assertEqual(audit["new_physical_steps_executed"],0)
        self.assertFalse(audit["physical_application_proven_from_archives_alone"])

    def test_injected_latent_feature_in_lived_input_fails(self):
        acted=deepcopy(self.acted)
        acted[0]["predecision_lived_history"][0]["state"][
            "latent_external_only"
        ]="benign"
        with self.assertRaisesRegex(ValueError,"non-first-person"):
            self.review(acted=acted)

    def test_borrowed_future_ingestion_capture_fails(self):
        acted=deepcopy(self.acted)
        row=next(x for x in acted if x["probe"]=="collect_first"
                 and x["latent_external_bench_only"]=="benign")
        row["predecision_lived_history"][-1]["state"]=deepcopy(
            row["lived_post_ingestion_if_survivor"]
        )
        with self.assertRaisesRegex(ValueError,"foreign future"):
            self.review(acted=acted)

    def test_unfounded_safe_claim_rejected(self):
        acted=deepcopy(self.acted)
        acted[0]["certifies_safe_from_probe"]=True
        with self.assertRaisesRegex(ValueError,"fake safety"):
            self.review(acted=acted)

    def test_hash_of_physical_receipt_tampered_rejected(self):
        acted=deepcopy(self.acted)
        acted[0]["physical_commands_and_receipts_external_only"][0][
            "sha256"
        ]="0"*64
        with self.assertRaisesRegex(ValueError,"physical world receipt"):
            self.review(acted=acted)

    def test_fake_integrity_effect_even_with_resigned_receipt_rejected(self):
        acted=deepcopy(self.acted)
        row=next(x for x in acted if x["latent_external_bench_only"]=="toxin_30")
        receipt=row["physical_commands_and_receipts_external_only"][-1]
        receipt["after_for_external_bench"]["body"]["integrity"]+=7.0
        receipt["sha256"]=hash_object({
            k:v for k,v in receipt.items() if k!="sha256"
        })
        row["lived_post_ingestion_if_survivor"]=deepcopy(
            receipt["after_for_external_bench"]
        )
        with self.assertRaisesRegex(ValueError,"hidden effect"):
            self.review(acted=acted)

    def test_forged_postmortem_lived_result_rejected(self):
        acted=deepcopy(self.acted)
        row=next(x for x in acted if x["latent_external_bench_only"]=="toxin_100")
        row["lived_post_ingestion_if_survivor"]=deepcopy(
            row["physical_commands_and_receipts_external_only"][-1][
                "after_for_external_bench"
            ]
        )
        with self.assertRaisesRegex(ValueError,"mortality"):
            self.review(acted=acted)

    def test_postterminal_extra_action_rejected(self):
        acted=deepcopy(self.acted)
        row=next(x for x in acted if x["latent_external_bench_only"]=="toxin_100")
        extra=deepcopy(row["physical_commands_and_receipts_external_only"][-1])
        extra["t_monde"]+=1
        extra["terminal_external_only"]=False
        extra["sha256"]=hash_object({k:v for k,v in extra.items()
                                    if k!="sha256"})
        row["physical_commands_and_receipts_external_only"].append(extra)
        row["physical_total_steps"]+=1
        with self.assertRaisesRegex(ValueError,"chronology"):
            self.review(acted=acted)

    def test_destroy_visible_control_but_resign_passive_fails(self):
        control=deepcopy(self.control)
        ref=next(x for x in control if x["control"]=="resource_berry_a"
                 and x["food"]==35 and x["position"]==[5,5])
        fake=next(x for x in control if x["control"]=="resource_berry_b"
                  and x["food"]==35 and x["position"]==[5,5])
        fake["visible_state"]=deepcopy(ref["visible_state"])
        fake["visible_state_sha256"]=hash_object(fake["visible_state"])
        with self.assertRaisesRegex(ValueError,"positive resource"):
            self.review(control=control)

    def test_duplicate_world_id_detected(self):
        acted=deepcopy(self.acted)
        acted[1]["world_id"]=acted[0]["world_id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.review(acted=acted)

    def test_probe_bodily_cost_manipulated_fails(self):
        acted=deepcopy(self.acted)
        row=next(x for x in acted if x["probe"]=="wait_twice")
        row["physical_probe_effect"]["food"]=0.0
        with self.assertRaisesRegex(ValueError,"bodily"):
            self.review(acted=acted)

    def test_altered_external_summary_does_not_pass_recalculation(self):
        summary=deepcopy(self.summary)
        summary["external_terminal_ingestions"]=0
        with self.assertRaisesRegex(ValueError,"aggregate source"):
            self.review(summary=summary)

    def test_analyst_does_not_import_original_runner_or_world(self):
        code=(Path(__file__).resolve().parents[1]/
              "scripts/audit_stage12_issue110_b_a230x_sealed_probes.py"
        ).read_text()
        for disallowed in (
            "from run_stage12_issue110_b_a230w_prospective_probes import",
            "from lab.world import","WorldBody(","Stage6Runtime(",
            "SimulatorPlanner(","import Oracle",
        ):
            self.assertNotIn(disallowed,code)


if __name__=="__main__":
    unittest.main()
