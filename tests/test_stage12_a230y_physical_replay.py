"""A2.30-Y: adversarial independent physical WorldBody replay of W."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from replay_stage12_issue110_b_a230y_physical_probes import (
    load_sealed,hash_object,audit_source,
)


class ProspectiveFoodProbePhysicalReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src=load_sealed(Path(os.environ["A230Y_SOURCE"]))
        cls.original_acted=src["a230w-acted-physical-worlds.json"]
        cls.original_controls=src["a230w-passive-positive-controls.json"]
        cls.original_summary=src["a230w-summary.json"]

    def verify(self,acted=None,control=None,summary=None):
        return audit_source(
            deepcopy(self.original_acted if acted is None else acted),
            deepcopy(self.original_controls if control is None else control),
            deepcopy(self.original_summary if summary is None else summary),
        )

    def test_92_detached_worlds_recreate_all_original_transitions(self):
        s=self.verify()
        self.assertEqual(s["technical_replay_worlds"],92)
        self.assertEqual(s["technical_replay_acted_worlds"],80)
        self.assertEqual(s["technical_replay_passive_controls"],12)
        self.assertEqual(s["technical_replay_physical_actions"],240)
        self.assertEqual(s["technical_replay_external_terminals"],16)
        self.assertEqual(s["technical_replay_food_goals"],48)
        self.assertEqual(s["physical_outcome_differences"],0)
        self.assertEqual(s["new_independent_scientific_conditions"],0)
        self.assertEqual(s["terminal_revivals"],0)
        self.assertEqual(s["new_i0_births"],0)
        self.assertTrue(
            s["replays_same_deterministic_worldbody_not_independent_natural_truth"]
        )

    def test_hidden_physics_config_mismatch_before_action_is_rejected(self):
        acted=deepcopy(self.original_acted)
        acted[0]["config_digest_external_only"]="0"*64
        with self.assertRaisesRegex(ValueError,"physics/layout digest"):
            self.verify(acted=acted)

    def test_layout_mismatch_before_action_is_rejected(self):
        acted=deepcopy(self.original_acted)
        acted[0]["layout_digest_external_only"]="0"*64
        with self.assertRaisesRegex(ValueError,"physics/layout digest"):
            self.verify(acted=acted)

    def test_body_after_ingestion_resigned_but_physically_false_fails(self):
        acted=deepcopy(self.original_acted)
        row=next(x for x in acted if
                 x["latent_external_bench_only"]=="toxin_30")
        event=row["physical_commands_and_receipts_external_only"][-1]
        event["after_for_external_bench"]["body"]["integrity"]+=7
        event["sha256"]=hash_object({
            k:v for k,v in event.items() if k!="sha256"
        })
        row["lived_post_ingestion_if_survivor"]=deepcopy(
            event["after_for_external_bench"]
        )
        with self.assertRaisesRegex(ValueError,"independent physical outcome"):
            self.verify(acted=acted)

    def test_forged_terminal_even_with_resigned_sha_fails(self):
        acted=deepcopy(self.original_acted)
        row=next(x for x in acted if
                 x["latent_external_bench_only"]=="toxin_100")
        e=row["physical_commands_and_receipts_external_only"][-1]
        e["terminal_external_only"]=False
        e["sha256"]=hash_object({k:v for k,v in e.items() if k!="sha256"})
        with self.assertRaisesRegex(ValueError,"independent physical outcome"):
            self.verify(acted=acted)

    def test_changed_lab_command_even_with_resigned_sha_fails(self):
        acted=deepcopy(self.original_acted)
        row=next(x for x in acted if x["probe"]=="west_return")
        e=row["physical_commands_and_receipts_external_only"][0]
        e["command"]["parameters"]["direction"]="north"
        e["sha256"]=hash_object({k:v for k,v in e.items() if k!="sha256"})
        with self.assertRaisesRegex(ValueError,"independent physical outcome"):
            self.verify(acted=acted)

    def test_first_person_observation_invented_before_ingestion_fails(self):
        acted=deepcopy(self.original_acted)
        row=next(x for x in acted if
                 x["probe"]=="wait_twice" and
                 x["latent_external_bench_only"]=="benign")
        row["predecision_lived_history"][-1]["state"]["body"]["food"]+=10
        with self.assertRaisesRegex(ValueError,"first-person timing"):
            self.verify(acted=acted)

    def test_terminal_observation_forged_as_lived_fails(self):
        acted=deepcopy(self.original_acted)
        row=next(x for x in acted if
                 x["latent_external_bench_only"]=="toxin_100")
        row["lived_post_ingestion_if_survivor"]=deepcopy(
            row["physical_commands_and_receipts_external_only"]
            [-1]["after_for_external_bench"]
        )
        with self.assertRaisesRegex(ValueError,"terminal state"):
            self.verify(acted=acted)

    def test_forged_action_beyond_mortality_is_rejected(self):
        acted=deepcopy(self.original_acted)
        row=next(x for x in acted if
                 x["latent_external_bench_only"]=="toxin_100")
        last=deepcopy(row["physical_commands_and_receipts_external_only"][-1])
        last["t_monde"]+=1
        last["sha256"]=hash_object({
            k:v for k,v in last.items() if k!="sha256"
        })
        row["physical_commands_and_receipts_external_only"].append(last)
        row["physical_total_steps"]+=1
        with self.assertRaisesRegex(ValueError,"command length"):
            self.verify(acted=acted)

    def test_physically_visible_berry_control_erasure_fails(self):
        controls=deepcopy(self.original_controls)
        prior=next(x for x in controls if
                   x["control"]=="resource_berry_a"
                   and x["food"]==35 and x["position"]==[5,5])
        altered=next(x for x in controls if
                     x["control"]=="resource_berry_b"
                     and x["food"]==35 and x["position"]==[5,5])
        altered["visible_state"]=deepcopy(prior["visible_state"])
        altered["visible_state_sha256"]=hash_object(altered["visible_state"])
        with self.assertRaisesRegex(ValueError,"physical visible control"):
            self.verify(control=controls)

    def test_source_uses_independent_fixture_builder_and_no_w_runner_import(self):
        path=(Path(__file__).resolve().parents[1] /
              "scripts/replay_stage12_issue110_b_a230y_physical_probes.py")
        script=path.read_text()
        self.assertNotIn(
            "from run_stage12_issue110_b_a230w_prospective_probes import",script)
        self.assertNotIn("EquipmentCorpusRecorder",script.split('"""',2)[2])
        self.assertNotIn("SimulatorPlanner(",script)
        self.assertNotIn("Stage12Runtime(",script)
        self.assertNotIn("import Oracle",script)


if __name__=="__main__":
    unittest.main()
