"""A2.30-ZI independent historical data checks and meaningful tamper controls."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zi_independent import (
    read_sealed,independent_reanalysis,independently_check_world,
    independent_action,require_accessible,hash_obj,
    EAT,MOVE,COLLECT,
)


class SealedFirstPersonAlternativeReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_311=read_sealed(Path(os.environ["A230ZI_SOURCE_311"]))
        source_312=read_sealed(Path(os.environ["A230ZI_SOURCE_312"]))
        if source_311!=source_312:
            raise AssertionError("original archives not identical")
        cls.original=source_311
        cls.worlds=json.loads(source_311["a230z-physical-worlds.json"])
        cls.summary=json.loads(source_311["a230z-summary.json"])

    def audit(self,worlds=None,summary=None,allow_tamper_to_reach_scoring=False):
        worlds=deepcopy(self.worlds if worlds is None else worlds)
        summary=deepcopy(self.summary if summary is None else summary)
        if allow_tamper_to_reach_scoring:
            summary["world_data_sha256"]=hash_obj(worlds)
        return independent_reanalysis(worlds,summary)

    def test_independent_full_cohort_and_exact_stage6_root(self):
        output=self.audit()
        self.assertEqual(output["original_detached_worlds_checked"],168)
        self.assertEqual(output["original_physical_receipts_checked"],244)
        self.assertEqual(output["original_B_ingestions_recomputed"],80)
        self.assertEqual(output["original_physical_terminals_recomputed"],20)
        self.assertEqual(output["surviving_food_goals_recomputed"],40)
        self.assertEqual(output["surviving_insufficient_goals_recomputed"],20)
        self.assertEqual(output["original_no_ingestions"],88)
        self.assertEqual(output["latent_group_count"],40)
        self.assertEqual(output["risk_ambiguous_success_vs_death_groups"],20)
        self.assertEqual(output["initially_unseen_remote_resource_pair_groups"],8)
        self.assertEqual(output["remotely_discovered_by_actual_scout_pair_groups"],4)
        self.assertEqual(output["actual_stage6_algorithm_shadow_searches_checked"],80)
        self.assertEqual(output["zero_known_first_edges_independently_recomputed"],80)
        self.assertEqual(output["new_worlds"],0)
        self.assertEqual(output["new_physical_steps"],0)
        self.assertEqual(output["new_i0_births"],0)
        self.assertFalse(output["source_physics_independently_proven_from_json"])
        self.assertFalse(output["safe_food_option_certified"])

    def test_latent_label_in_first_person_input_rejected(self):
        row=deepcopy(self.worlds[0])
        row["initial_first_person"]["berry_b_is_safe"]=True
        with self.assertRaisesRegex(ValueError,"hidden, future"):
            independently_check_world(row)

    def test_future_outcome_promoted_to_initial_perception_rejected(self):
        row=deepcopy(next(x for x in self.worlds if x["ingested_berry_b_external"]))
        row["perceptual_policy_choices"][0][
            "input_accessible_state"]=deepcopy(row["post_ingestion_external_only"])
        with self.assertRaisesRegex(ValueError,"future/latent information"):
            independently_check_world(row)

    def test_fake_berry_b_initially_visible_when_remote_rejected(self):
        row=deepcopy(next(x for x in self.worlds if
            x["layout_external_only"]=="B_EAST_TWO_STEPS"))
        row["initial_first_person"]["current_resources"].append("berry_b")
        with self.assertRaisesRegex(ValueError,"initially accessible|remote or absent"):
            independently_check_world(row)

    def test_blocked_east_policy_move_forgery_rejected(self):
        row=deepcopy(next(x for x in self.worlds if
            x["layout_external_only"]=="B_EAST_BLOCKED"))
        row["perceptual_policy_choices"][0]["command"]=deepcopy(MOVE)
        with self.assertRaisesRegex(ValueError,"policy bypassed"):
            independently_check_world(row)

    def test_fabricated_safety_label_fails_before_scoring(self):
        row=deepcopy(self.worlds[0])
        row["certifies_food_safety"]=True
        with self.assertRaisesRegex(ValueError,"false safety"):
            independently_check_world(row)

    def test_tampered_physical_example_digest_rejected(self):
        row=deepcopy(next(x for x in self.worlds if
            x["physical_steps_external"]))
        row["physical_steps_external"][0]["physical_example_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"physical transition receipt"):
            independently_check_world(row)

    def test_physical_food_success_fabrication_rejected(self):
        row=deepcopy(next(x for x in self.worlds if
            x["latent_berry_effect_external_only"]=="gain_zero"
            and x["ingested_berry_b_external"]))
        row["food_success_with_survival_external"]=True
        with self.assertRaisesRegex(ValueError,"food achievement"):
            independently_check_world(row)

    def test_ghost_consumption_without_actual_inventory_rejected(self):
        row=deepcopy(next(x for x in self.worlds if
            x["layout_external_only"]=="A_ONLY"))
        row["perceptual_policy_choices"][0]["command"]=deepcopy(EAT)
        with self.assertRaisesRegex(ValueError,"policy bypassed"):
            independently_check_world(row)

    def test_postterminal_capture_falsely_lived_rejected(self):
        row=deepcopy(next(x for x in self.worlds if
            x["physical_terminal_step_external_only"] is not None))
        row["lived_states_while_alive"].append({
            "t_monde":row["physical_step_count"]+1,
            "state":deepcopy(row["physical_steps_external"][-1][
                "physical_after_external_only"]),
        })
        with self.assertRaisesRegex(ValueError,"subjective postmortem"):
            independently_check_world(row)

    def test_cross_world_or_future_stage6_example_rejected(self):
        row=deepcopy(next(x for x in self.worlds if x["stage6_shadow"]))
        row["stage6_shadow"]["own_physical_examples"].append(deepcopy(
            row["physical_steps_external"][-1]["physical_example"]
        ))
        with self.assertRaisesRegex(ValueError,"Stage6 first-person timeline"):
            independently_check_world(row)

    def test_forged_stage6_predicted_root_rejected(self):
        row=deepcopy(next(x for x in self.worlds if x["stage6_shadow"]))
        row["stage6_shadow"]["stage6_root_available_edges"]=1
        with self.assertRaisesRegex(ValueError,"Stage6 exact root coverage"):
            independently_check_world(row)

    def test_false_stage6_plan_from_unknown_root_rejected(self):
        row=deepcopy(next(x for x in self.worlds if x["stage6_shadow"]))
        row["stage6_shadow"]["stage6_status"]="plan_found"
        with self.assertRaisesRegex(ValueError,"Stage6 invented food plan"):
            independently_check_world(row)

    def test_duplicate_world_source_rejected(self):
        fake=deepcopy(self.worlds)
        fake[1]["world_id"]=fake[0]["world_id"]
        with self.assertRaisesRegex(ValueError,"identity/provenance"):
            self.audit(fake,allow_tamper_to_reach_scoring=True)

    def test_hidden_variant_dropped_from_source_rejected(self):
        fake=deepcopy(self.worlds)
        fake.pop()
        with self.assertRaisesRegex(ValueError,"world count"):
            self.audit(fake,allow_tamper_to_reach_scoring=True)

    def test_forged_aggregate_count_rejected(self):
        fake=deepcopy(self.summary)
        fake["ingestions_of_berry_b"]=168
        with self.assertRaisesRegex(ValueError,"aggregate"):
            self.audit(summary=fake)

    def test_independent_review_never_invokes_simulator_or_oracle(self):
        src=(Path(__file__).resolve().parents[1]/
             "scripts/audit_stage12_issue110_b_a230zi_independent.py").read_text()
        self.assertNotIn("from lab.world import",src)
        self.assertNotIn("from i0.modules.stage6_planning import",src)
        self.assertNotIn("from run_stage12_issue110_b_a230z_alternative_food import",src)
        self.assertNotIn("WorldBody(",src)
        self.assertNotIn("SimulatorPlanner(",src)
        self.assertNotIn("Oracle(",src)


if __name__=="__main__":
    unittest.main()
