"""A2.30-ZR: meaningful independent physical replay and falsification tests."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from replay_stage12_issue110_b_a230zr_pure_physics import (
    read_original, repeat_all, physical_replay_one, digest,
)


class FrozenProspectivePhysicsReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sealed=read_original(Path(os.environ["A230ZR_SOURCE"]))
        cls.original=cls.sealed["a230z-physical-worlds.json"]

    def pick(self,criteria):
        return deepcopy(next(item for item in self.original if criteria(item)))

    def test_replay_all_168_physical_worlds_no_postterminal(self):
        result=repeat_all(self.sealed)
        self.assertEqual(result["technical_new_worldbody_instances"],168)
        self.assertEqual(result["technical_repeated_worldbody_applications"],244)
        self.assertEqual(result["technical_terminal_transitions"],20)
        self.assertEqual(result["technical_reproduced_food_successes"],40)
        self.assertEqual(result["technical_physical_receipt_discrepancies"],0)
        self.assertEqual(result["postterminal_actions_attempted"],0)
        self.assertEqual(result["new_independent_scientific_conditions"],0)
        self.assertEqual(result["new_I0_births"],0)
        self.assertFalse(result["real_I0_UC_cost_measured"])
        self.assertFalse(result["model_deployed_to_I0"])

    def test_forged_physics_config_digest_rejected(self):
        row=self.pick(lambda r:r["physical_step_count"]>0)
        row["config_sha256_external_only"]="0"*64
        with self.assertRaisesRegex(ValueError,"configuration/layout"):
            physical_replay_one(row)

    def test_forged_obstacle_layout_digest_rejected(self):
        row=self.pick(lambda r:r["layout_external_only"]=="B_EAST_BLOCKED")
        row["layout_sha256_external_only"]="0"*64
        with self.assertRaisesRegex(ValueError,"configuration/layout"):
            physical_replay_one(row)

    def test_same_visible_species_hidden_effect_changed_rejected(self):
        row=self.pick(lambda r:r["layout_external_only"]=="B_LOCAL"
                      and r["latent_berry_effect_external_only"]=="benign")
        row["latent_berry_effect_external_only"]="toxin_100"
        row["world_id"]=row["world_id"].replace("benign","toxin_100")
        with self.assertRaisesRegex(ValueError,"configuration/layout"):
            physical_replay_one(row)

    def test_false_body_result_even_with_fresh_sha_is_rejected(self):
        row=self.pick(lambda r:r["ingested_berry_b_external"]
                      and r["latent_berry_effect_external_only"]=="benign")
        step=row["physical_steps_external"][-1]
        step["physical_after_external_only"]["body"]["food"]+=2
        step["physical_example"]["observed_next_state"]["body"]["food"]+=2
        step["physical_example_sha256"]=digest(step["physical_example"])
        row["post_ingestion_external_only"]["body"]["food"]+=2
        with self.assertRaisesRegex(ValueError,"WorldBody.apply replay contradicts"):
            physical_replay_one(row)

    def test_false_terminal_after_ingestion_with_recomputed_sha_rejected(self):
        row=self.pick(lambda r:r["physical_terminal_step_external_only"] is not None)
        step=row["physical_steps_external"][-1]
        step["terminal_external_only"]=False
        step["physical_example"]["terminal"]=False
        step["physical_example_sha256"]=digest(step["physical_example"])
        with self.assertRaisesRegex(ValueError,"WorldBody.apply replay contradicts"):
            physical_replay_one(row)

    def test_blocked_obstacle_bypass_rejected(self):
        row=self.pick(lambda r:r["layout_external_only"]=="B_EAST_BLOCKED")
        row["perceptual_policy_choices"][0]["command"]={
            "primitive":"se_deplacer",
            "parameters":{"direction":"east"},
        }
        with self.assertRaisesRegex(ValueError,"first-person physical command"):
            physical_replay_one(row)

    def test_hidden_remote_resource_prematurely_visible_rejected(self):
        row=self.pick(lambda r:r["layout_external_only"]=="B_EAST_TWO_STEPS")
        row["initial_first_person"]["current_resources"].append("berry_b")
        row["initial_first_person_sha256"]=digest(row["initial_first_person"])
        with self.assertRaisesRegex(ValueError,"initial perception mismatch"):
            physical_replay_one(row)

    def test_action_appended_after_terminal_rejected(self):
        row=self.pick(lambda r:r["physical_terminal_step_external_only"] is not None)
        fake=deepcopy(row["physical_steps_external"][-1])
        fake["t_monde"]+=1
        row["physical_steps_external"].append(fake)
        row["physical_step_count"]+=1
        with self.assertRaisesRegex(ValueError,"wrong replay lifetime"):
            physical_replay_one(row)

    def test_postmortem_experience_fabricated_rejected(self):
        row=self.pick(lambda r:r["physical_terminal_step_external_only"] is not None)
        row["lived_states_while_alive"].append({
            "t_monde":row["physical_step_count"]+1,
            "state":deepcopy(row["physical_steps_external"][-1][
                "physical_after_external_only"]),
        })
        with self.assertRaisesRegex(ValueError,"wrong replay lifetime"):
            physical_replay_one(row)

    def test_claim_of_food_goal_without_physical_gain_rejected(self):
        row=self.pick(lambda r:r["latent_berry_effect_external_only"]=="gain_zero"
                      and r["ingested_berry_b_external"])
        row["food_success_with_survival_external"]=True
        with self.assertRaisesRegex(ValueError,"false physical food-goal"):
            physical_replay_one(row)

    def test_no_runtime_or_original_runner_dependency(self):
        code=(Path(__file__).resolve().parents[1]/
              "scripts/replay_stage12_issue110_b_a230zr_pure_physics.py"
        ).read_text()
        self.assertNotIn("from run_stage12_issue110_b_a230z_alternative_food import",code)
        self.assertNotIn("EquipmentCorpusRecorder(",code)
        self.assertNotIn("from i0.modules.stage6_planning import",code)
        self.assertNotIn("SimulatorPlanner(",code)
        self.assertNotIn("Oracle(",code)


if __name__=="__main__":
    unittest.main()
