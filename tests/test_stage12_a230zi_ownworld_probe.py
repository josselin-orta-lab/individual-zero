"""A2.30-ZI: adversarial verification on ONE preregistered lab cohort.

Unit tests consume the already-generated sixty-four physical trial worlds
and two physically applied A prebirth references. They never re-run physics.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230zi_ownworld_probe import (
    B_COLLECT, MOVE_E, EAT_B, HIDDEN_B, HIDDEN_EAST,LAYOUTS,PROFILES,PROTOCOLS,
    assert_visible, fixed_perceptual_probe, score_worlds,
    one_sided_lethal_control, digest,
)
from run_stage12_issue110_b_a230zg_lived_root_shadow import (
    verify_original_birth_sources,
)


class FirstPersonOwnWorldMotorProbeSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=Path(os.environ["A230ZI_OUTPUT"])
        cls.summary=json.loads((p/"a230zi-summary.json").read_text())
        cls.worlds=json.loads((p/"a230zi-ownworld-tests.json").read_text())
        cls.manifest=json.loads((p/"a230zi-A-physical-source.json").read_text())
        roots=verify_original_birth_sources(
            Path(os.environ["A230ZI_ORIGINAL_311"]),
            Path(os.environ["A230ZI_ORIGINAL_312"]),
        )
        cls.roots={
            (x["profile"],x["layout"],x["hidden_B_external_only"]):
                x["initial_accessible_projection"]
            for x in roots
        }

    def score(self,worlds=None):
        return score_worlds(
            deepcopy(self.worlds if worlds is None else worlds),
            {
                "detached_A_reference_worlds":2,
                "real_physical_A_reference_steps":8,
                "models_originate_from_reference_A_worlds":True,
            },
            self.roots,
        )

    def test_preregistered_66_worlds_28_real_actions_80_shadows(self):
        s=self.score()
        self.assertEqual(s["independent_total_worlds"],66)
        self.assertEqual(s["independent_test_worlds"],64)
        self.assertEqual(s["independent_A_prebirth_reference_worlds"],2)
        self.assertEqual(s["actual_A_reference_physical_steps"],8)
        self.assertEqual(s["real_test_physical_steps"],20)
        self.assertEqual(s["total_new_physical_steps"],28)
        self.assertEqual(s["physical_terminal_worlds"],4)
        self.assertEqual(s["worlds_with_initial_motor_probe"],16)
        self.assertEqual(s["worlds_surviving_motor_probe"],12)
        self.assertEqual(s["worlds_without_motor_probe"],48)
        self.assertEqual(s["real_Stage6_shadow_searches"],80)
        self.assertEqual(s["postfirst_living_stage6_searches"],12)
        self.assertEqual(s["postsecond_living_stage6_searches"],4)
        self.assertEqual(s["paired_observationally_identical_hidden_motor_deaths"],4)
        self.assertEqual(s["firstperson_initial_root_matches_historical_I0"],48)
        self.assertEqual(s["new_I0_births"],0)
        self.assertFalse(s["I0_UC_measured"])
        self.assertEqual(s["cognitive_deployment"],"NO-GO")

    def test_all_factor_cells_and_fixed_non_ingestive_commands(self):
        self.assertEqual(len(self.worlds),64)
        self.assertEqual(len({r["world_id"] for r in self.worlds}),64)
        cases={
            (r["profile"],r["layout_external_only"],r["hidden_B_external_only"],
             r["hidden_lethal_zone_external_only"],
             r["protocol_frozen_before_physics"])
            for r in self.worlds
        }
        self.assertEqual(len(cases),2*4*2*2*2)
        for r in self.worlds:
            arm=r["layout_external_only"]
            history=r["real_physical_lab_receipts"]
            commands=[row["command"] for row in history]
            if r["protocol_frozen_before_physics"]=="ABSTAIN" or arm in (
                "B_NONE","B_EAST_BLOCKED",
            ):
                self.assertEqual(commands,[])
            elif arm=="B_LOCAL":
                self.assertEqual(commands,[B_COLLECT.as_dict()])
            else:
                self.assertEqual(commands,(
                    [MOVE_E.as_dict()] if r[
                        "hidden_lethal_zone_external_only"]=="east_hidden_lethal"
                    else [MOVE_E.as_dict(),B_COLLECT.as_dict()]
                ))
            self.assertNotIn(EAT_B.as_dict(),commands)
            self.assertTrue(r["no_berry_B_ingestion"])
            self.assertFalse(r["berry_B_safety_certified"])
            self.assertIsNone(r["postterminal_firstperson_capture"])
            self.assertEqual(r["i0_births"],0)
            self.assertEqual(r["i0_autonomous_steps"],0)

    def test_own_memory_is_never_postterminal_or_a_foreign_world(self):
        for r in self.worlds:
            receipts=r["real_physical_lab_receipts"]
            shadows=r["stage6_shadow_queries"]
            choices=r["lab_perceptual_choices"]
            if r["physically_terminal_step_external_only"] is not None:
                self.assertTrue(receipts[-1]["terminal_external_only"])
                self.assertEqual(len(shadows),1)
                self.assertEqual(len(r["firstperson_history_while_alive"]),1)
                self.assertEqual(r["own_world_prior_examples_for_final_living_state"],0)
            else:
                self.assertEqual(
                    r["own_world_prior_examples_for_final_living_state"],
                    len(receipts),
                )
            self.assertEqual(
                [s["own_living_prior_examples"] for s in shadows],
                list(range(len(shadows))),
            )
            self.assertTrue(all(s["no_shadow_dispatch"] for s in shadows))
            self.assertTrue(all(not s["planner"]["berry_b_safety_certified"]
                                for s in shadows))
            self.assertTrue(all(
                x["not_issued_as_current_firstperson_prediction"]
                for x in r["past_edges_known_only_retrospectively"]
            ))
            self.assertTrue(all(not s["lab_next_command_known_in_frozen_exact_model"]
                                for s in shadows))

    def test_original_I0_roots_not_mutated_or_reborn(self):
        for row in self.worlds:
            if row["layout_external_only"]=="B_EAST_BLOCKED":
                continue
            key=(
                row["profile"],row["layout_external_only"],
                row["hidden_B_external_only"],
            )
            self.assertEqual(row["firstperson_birth_state"],self.roots[key])

    def test_hidden_berry_effect_does_not_change_non_ingestive_physics(self):
        pairs=defaultdict(list)
        for r in self.worlds:
            k=(r["profile"],r["layout_external_only"],
               r["hidden_lethal_zone_external_only"],
               r["protocol_frozen_before_physics"])
            pairs[k].append(r)
        self.assertEqual(len(pairs),32)
        for pair in pairs.values():
            self.assertEqual(len(pair),2)
            self.assertEqual(pair[0]["firstperson_birth_state"],
                             pair[1]["firstperson_birth_state"])
            self.assertEqual(
                [x["command"] for x in pair[0]["real_physical_lab_receipts"]],
                [x["command"] for x in pair[1]["real_physical_lab_receipts"]],
            )
            self.assertEqual(pair[0]["physically_terminal_step_external_only"],
                             pair[1]["physically_terminal_step_external_only"])

    def test_hidden_lethal_east_contradiction_is_not_safe_inference(self):
        pairs=defaultdict(list)
        for row in self.worlds:
            if (row["layout_external_only"]=="B_EAST" and
                row["protocol_frozen_before_physics"]=="VISIBLE_PROBE"):
                pairs[(row["profile"],row["hidden_B_external_only"])].append(row)
        self.assertEqual(len(pairs),4)
        for pair in pairs.values():
            self.assertEqual(len(pair),2)
            safe=next(x for x in pair if
                x["hidden_lethal_zone_external_only"]=="east_clear")
            death=next(x for x in pair if
                x["hidden_lethal_zone_external_only"]=="east_hidden_lethal")
            self.assertEqual(safe["firstperson_birth_state"],
                             death["firstperson_birth_state"])
            self.assertEqual(
                safe["real_physical_lab_receipts"][0]["command"],
                death["real_physical_lab_receipts"][0]["command"],
            )
            self.assertIsNone(safe["physically_terminal_step_external_only"])
            self.assertEqual(death["physically_terminal_step_external_only"],1)
            self.assertEqual(len(death["stage6_shadow_queries"]),1)
        controls=self.manifest["exact_mortal_counterfactual_controls"]
        self.assertEqual(len(controls),4)
        self.assertTrue(all(x["predicted_terminal"] is False and
                            x["physically_terminal_external"] is True
                            for x in controls))
        self.assertTrue(all(x["nominal_exact_table_confidence"]==1.0
                            for x in controls))
        self.assertTrue(all(not x["safety_calibration_inferred"]
                            for x in controls))

    def test_external_A_source_is_physically_authentic_per_profile(self):
        src=self.manifest["A_reference_worlds"]
        self.assertEqual(len(src),2)
        for item in src:
            self.assertEqual(len(item["physical_examples"]),4)
            self.assertEqual(len(item["physical_example_sha256"]),4)
            for source,d in zip(item["physical_examples"],
                                item["physical_example_sha256"]):
                self.assertEqual(digest(source),d)
                self.assertFalse(source["terminal"])
        self.assertEqual(
            set(self.manifest["A_model_digest_by_profile"]),
            set(PROFILES),
        )

    def test_fake_future_or_hidden_feature_in_decision_is_rejected(self):
        row=deepcopy(self.worlds[0]["firstperson_birth_state"])
        row["hidden_zone_is_lethal"]=True
        with self.assertRaisesRegex(ValueError,"hidden or future"):
            fixed_perceptual_probe(row,"VISIBLE_PROBE",())

    def test_invented_B_ghost_proposal_is_rejected(self):
        altered=deepcopy(self.worlds)
        target=next(x for x in altered if x["layout_external_only"]=="B_NONE")
        target["lab_perceptual_choices"][0][
            "preregistered_external_lab_proposal"]=B_COLLECT.as_dict()
        with self.assertRaisesRegex(ValueError,"frozen first-person probe"):
            self.score(altered)

    def test_blocked_east_move_is_rejected(self):
        altered=deepcopy(self.worlds)
        target=next(x for x in altered if
            x["layout_external_only"]=="B_EAST_BLOCKED")
        target["lab_perceptual_choices"][0][
            "preregistered_external_lab_proposal"]=MOVE_E.as_dict()
        with self.assertRaisesRegex(ValueError,"frozen first-person probe"):
            self.score(altered)

    def test_false_safe_label_rejected(self):
        altered=deepcopy(self.worlds)
        altered[0]["berry_B_safety_certified"]=True
        with self.assertRaisesRegex(ValueError,"safety or UC"):
            self.score(altered)

    def test_false_real_I0_UC_charge_rejected(self):
        altered=deepcopy(self.worlds)
        altered[0]["lived_i0_UC_cost"]=1
        with self.assertRaisesRegex(ValueError,"safety or UC"):
            self.score(altered)

    def test_postmortem_firstperson_capture_rejected(self):
        altered=deepcopy(self.worlds)
        dead=next(x for x in altered if
            x["physically_terminal_step_external_only"] is not None)
        dead["postterminal_firstperson_capture"]={
            "fabricated_after_death":True
        }
        with self.assertRaisesRegex(ValueError,"safety or UC"):
            self.score(altered)

    def test_terminal_example_learned_after_death_rejected(self):
        altered=deepcopy(self.worlds)
        dead=next(x for x in altered if
            x["physically_terminal_step_external_only"] is not None)
        dead["own_world_prior_examples_for_final_living_state"]=1
        with self.assertRaisesRegex(ValueError,"timeline"):
            self.score(altered)

    def test_shadow_motor_execution_fabrication_rejected(self):
        altered=deepcopy(self.worlds)
        altered[0]["stage6_shadow_queries"][0]["no_shadow_dispatch"]=False
        with self.assertRaisesRegex(ValueError,"shadow leaked"):
            self.score(altered)

    def test_physical_step_sha_corruption_rejected(self):
        altered=deepcopy(self.worlds)
        active=next(x for x in altered if x["real_physical_lab_receipts"])
        active["real_physical_lab_receipts"][0][
            "physical_example_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"physical action receipt"):
            self.score(altered)

    def test_food_ingestion_forgery_rejected(self):
        altered=deepcopy(self.worlds)
        active=next(x for x in altered if x["real_physical_lab_receipts"])
        active["real_physical_lab_receipts"][0][
            "physical_example"]["command"]=EAT_B.as_dict()
        with self.assertRaisesRegex(ValueError,"physical action receipt"):
            self.score(altered)

    def test_foreign_world_experience_count_rejected(self):
        altered=deepcopy(self.worlds)
        active=next(x for x in altered if
            x["own_world_prior_examples_for_final_living_state"]>0)
        active["own_world_prior_examples_for_final_living_state"]=99
        with self.assertRaisesRegex(ValueError,"timeline"):
            self.score(altered)

    def test_hidden_motor_risk_forged_visible_rejected(self):
        altered=deepcopy(self.worlds)
        altered[0]["firstperson_birth_state"]["known_lethal_east"]=True
        with self.assertRaisesRegex(ValueError,"hidden or future"):
            self.score(altered)

    def test_missing_physical_terminal_receipt_rejected(self):
        altered=deepcopy(self.worlds)
        lethal=next(x for x in altered if
            x["physically_terminal_step_external_only"] is not None)
        lethal["physically_terminal_step_external_only"]=None
        with self.assertRaisesRegex(ValueError,"spurious external death"):
            self.score(altered)

    def test_duplicate_physical_world_id_rejected(self):
        altered=deepcopy(self.worlds)
        altered[0]["world_id"]=altered[1]["world_id"]
        with self.assertRaisesRegex(ValueError,"factorial|population"):
            self.score(altered)

    def test_no_new_I0_oracle_runtime_or_prediction_installation(self):
        source=(
            Path(__file__).resolve().parents[1]/
            "scripts/run_stage12_issue110_b_a230zi_ownworld_probe.py"
        ).read_text()
        self.assertNotIn("life.run_step(",source)
        self.assertNotIn("Stage12Runtime(",source)
        self.assertNotIn("from lab.oracle import",source)
        self.assertNotIn("install_model(",source)
        self.assertNotIn("def guarantee_berry_b_safe",source)
        self.assertNotIn("stage3.control.dispatch(",source)


if __name__=="__main__":
    unittest.main()
