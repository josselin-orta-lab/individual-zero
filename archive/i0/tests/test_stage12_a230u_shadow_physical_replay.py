"""A2.30-U physical replay: falsified world effects and terminality must fail."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from replay_stage12_issue110_b_a230u_shadow_physics import (
    read_source,replay_all,
)
from lab.determinism import canonical_causal_bytes,sha256_hex


class ExogenousPhysicsReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src=read_source(Path(os.environ["A230U_SOURCE"]))
        cls.acted=src["a230s-acted-worlds.json"]
        cls.passive=src["a230s-passive-worlds.json"]
        cls.summary=src["a230s-summary.json"]

    def audit(self,acted=None,passive=None,summary=None):
        return replay_all(
            deepcopy(self.acted if acted is None else acted),
            deepcopy(self.passive if passive is None else passive),
            deepcopy(self.summary if summary is None else summary),
        )

    def test_independent_exogenous_hazard_replay_and_mortality(self):
        a=self.audit()
        self.assertEqual(a["physical_technical_worlds_reinstantiated"],72)
        self.assertEqual(a["physical_technical_steps_replayed"],196)
        self.assertEqual(a["original_24_terminal_worlds_verified"],24)
        self.assertEqual(a["physical_replay_differences"],0)
        self.assertEqual(a["postterminal_actions"],0)
        self.assertEqual(a["new_I0_births"],0)
        self.assertEqual(a["new_independent_scientific_conditions"],0)
        self.assertTrue(a["physical_model_not_natural_world_truth"])

    def test_altered_physical_config_or_hidden_layout_fails(self):
        act=deepcopy(self.acted)
        act[0]["config_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"configuration or hidden layout"):
            self.audit(acted=act)
        act=deepcopy(self.acted)
        act[0]["layout_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"configuration or hidden layout"):
            self.audit(acted=act)

    def test_fake_integrity_outcome_even_with_new_valid_json_sha_fails(self):
        act=deepcopy(self.acted)
        entry=act[0]["physical_records"][2]
        entry["physical_example"]["observed_next_state"]["body"]["integrity"]=20.0
        entry["state_after"]["body"]["integrity"]=20.0
        entry["physical_example_sha256"]=sha256_hex(
            canonical_causal_bytes(entry["physical_example"])
        )
        with self.assertRaisesRegex(ValueError,"physical replay divergent"):
            self.audit(acted=act)

    def test_false_terminal_with_recomputed_hash_fails(self):
        act=deepcopy(self.acted)
        row=next(x for x in act if x["first_terminal_step"] is not None)
        entry=row["physical_records"][-1]
        entry["physical_example"]["terminal"]=False
        entry["terminal"]=False
        entry["physical_example_sha256"]=sha256_hex(
            canonical_causal_bytes(entry["physical_example"])
        )
        with self.assertRaisesRegex(ValueError,"physical replay divergent"):
            self.audit(acted=act)

    def test_deleted_exogenous_intervention_not_silently_explained_by_berry(self):
        act=deepcopy(self.acted)
        row=next(x for x in act if x["variant_lab_only"]=="exogenous_confounded")
        row["external_environment_interventions"]=[]
        with self.assertRaisesRegex(ValueError,"external event trace"):
            self.audit(acted=act)

    def test_command_not_produced_by_original_protocol_fails(self):
        act=deepcopy(self.acted)
        row=next(x for x in act if x["kind"]=="movement")
        row["intended_prefix"][0]["parameters"]["direction"]="west"
        with self.assertRaisesRegex(ValueError,"different commands"):
            self.audit(acted=act)

    def test_postterminal_extension_fails(self):
        act=deepcopy(self.acted)
        row=next(x for x in act if x["first_terminal_step"] is not None)
        row["physical_records"].append(deepcopy(row["physical_records"][-1]))
        row["physical_step_count"]+=1
        with self.assertRaisesRegex(ValueError,"physical death, timing"):
            self.audit(acted=act)

    def test_passive_absent_berry_cannot_be_forged_as_present(self):
        passive=deepcopy(self.passive)
        passive[0]["capture"]["current_resources"]=["berry_a"]
        with self.assertRaisesRegex(ValueError,"passive perceptual capture"):
            self.audit(passive=passive)

    def test_technical_runner_independent_from_S_and_stage6(self):
        path=(Path(__file__).resolve().parents[1]/
              "scripts/replay_stage12_issue110_b_a230u_shadow_physics.py")
        src=path.read_text()
        self.assertNotIn("from run_stage12_issue110_b_a230s_firstperson_shadow import",src)
        self.assertNotIn("EquipmentCorpusRecorder",src.split("from __future__ import annotations")[1])
        self.assertNotIn("from i0.modules.stage6_planning import",src)
        self.assertNotIn("import Oracle",src)


if __name__=="__main__":
    unittest.main()
