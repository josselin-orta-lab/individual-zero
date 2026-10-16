"""A2.30-ZH: falsify archived physical/first-person provenance offline.

One verification over original ZG and ZB artifacts. Never runs physics,
Stage6 or any I0 life. These are hard negative tests of the independent
scorer, not simulated new births.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zh_sealed_roots import (
    B_COLLECT,B_EAT,MOVE_E,
    ZG_FILES, ZB_FILES,check_state,command_key,digest,
    independently_evaluate,load_sources,read_one,
)


class ArchivedBornRootCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths={
            "zg311":Path(os.environ["A230ZH_ZG311"]),
            "zg312":Path(os.environ["A230ZH_ZG312"]),
            "zb311":Path(os.environ["A230ZH_ZB311"]),
            "zb312":Path(os.environ["A230ZH_ZB312"]),
        }
        cls.data=load_sources(
            cls.paths["zg311"],cls.paths["zg312"],
            cls.paths["zb311"],cls.paths["zb312"],
        )

    def score(self,items=None):
        return independently_evaluate(
            *(deepcopy(x) for x in (self.data if items is None else items))
        )

    def test_original_archive_recomputed_without_physics(self):
        report=self.score()
        self.assertEqual(report["real_original_I0_birth_roots"],12)
        self.assertEqual(report["real_original_autonomous_steps_read_only"],384)
        self.assertEqual(report["external_physically_applied_train_worlds_from_ZG"],6)
        self.assertEqual(report["external_physically_applied_train_steps_from_ZG"],14)
        self.assertEqual(report["physical_demonstration_example_hashes_recomputed"],14)
        self.assertEqual(report["shadow_stage6_queries_independently_scored"],24)
        self.assertEqual(report["visible_B_roots_gain_first_model_edge"],8)
        self.assertEqual(report["stage6_B_partial_substeps"],8)
        self.assertEqual(report["baseline_incomplete_with_B_visible"],8)
        self.assertEqual(report["baseline_A_partial_B_absent"],4)
        self.assertEqual(report["enriched_partial_total"],12)
        self.assertEqual(report["new_physical_worlds"],0)
        self.assertEqual(report["new_i0_births"],0)
        self.assertFalse(report["food_safety_proven"])
        self.assertFalse(report["real_i0_B_food_plan_or_action_proven"])
        self.assertFalse(report["physical_worldbody_apply_independently_proven_from_archive"])

    def test_immutable_sources_use_expected_full_hashes(self):
        for p in ("zg311","zg312"):
            for name,expected in ZG_FILES.items():
                self.assertEqual(
                    read_one(self.paths[p],name,expected),
                    read_one(self.paths["zg311"],name,expected)
                )
        for p,version in (("zb311","3.11"),("zb312","3.12")):
            self.assertEqual(
                json.loads(read_one(
                    self.paths[p],"a230zb-summary.json",ZB_FILES[version]
                ))["independent_new_I0_births"],12
            )

    def test_external_B_demonstrations_are_non_ingestive_and_consecutive(self):
        manifest,rows,summary,zb_a,zb_b=self.data
        source={e["source_world_id"]:e for e in manifest[
            "all_physical_demonstrations"
        ]}
        for profile in ("restored","sustained"):
            l=source[f"B_DEMONSTRATOR-{profile}-B_LOCAL"]
            e=source[f"B_DEMONSTRATOR-{profile}-B_EAST"]
            self.assertEqual(len(l["physical_examples"]),1)
            self.assertEqual(len(e["physical_examples"]),2)
            self.assertEqual(l["physical_examples"][0]["command"],B_COLLECT)
            self.assertEqual(e["physical_examples"][0]["command"],MOVE_E)
            self.assertEqual(e["physical_examples"][1]["command"],B_COLLECT)
            self.assertEqual(
                e["physical_examples"][0]["observed_next_state"],
                e["physical_examples"][1]["state"],
            )
            self.assertTrue(all(x["command"]!=B_EAT for x in
                l["physical_examples"]+e["physical_examples"]))
        self.assertEqual(len(rows),12)

    def test_tampering_sealed_json_hash_is_detected(self):
        file_name="a230zg-summary.json"
        raw=read_one(
            self.paths["zg311"],file_name,ZG_FILES[file_name]
        )
        with tempfile.TemporaryDirectory(prefix="zg-tamper-") as folder:
            path=Path(folder)/file_name
            path.write_bytes(raw+b"x")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                read_one(Path(folder),file_name,ZG_FILES[file_name])

    def test_fake_physical_B_collection_without_visible_B_fails(self):
        items=deepcopy(self.data)
        source=next(x for x in items[0]["all_physical_demonstrations"] if
            x["source_world_id"]=="B_DEMONSTRATOR-restored-B_LOCAL")
        source["physical_examples"][0]["state"]["current_resources"]=[]
        with self.assertRaises(ValueError):
            self.score(items)

    def test_hidden_latent_label_in_initial_input_fails(self):
        items=deepcopy(self.data)
        items[1][0]["first_person_root_state"]["B_is_safely_benign"]=True
        with self.assertRaisesRegex(ValueError,"nonperceptual"):
            self.score(items)

    def test_physically_undemonstrated_ingestion_in_corpus_fails(self):
        items=deepcopy(self.data)
        example=next(x for x in items[0]["all_physical_demonstrations"] if
            x["source_world_id"]=="B_DEMONSTRATOR-restored-B_LOCAL"
        )["physical_examples"][0]
        example["command"]=B_EAT
        with self.assertRaises(ValueError):
            self.score(items)

    def test_invented_model_first_root_known_fails(self):
        items=deepcopy(self.data)
        target=next(x for x in items[1] if x["layout"]=="B_LOCAL")
        target["baseline_stage6"]["root_available_edges"]=1
        with self.assertRaisesRegex(ValueError,"root availability"):
            self.score(items)

    def test_false_plan_found_from_partial_only_fails(self):
        items=deepcopy(self.data)
        target=next(x for x in items[1] if x["layout"]=="B_EAST")
        target["enriched_stage6"]["status"]="plan_found"
        with self.assertRaises(ValueError):
            self.score(items)

    def test_false_lived_UC_report_fails(self):
        items=deepcopy(self.data)
        items[1][0]["enriched_stage6"]["actual_i0_uc_measured"]=True
        with self.assertRaisesRegex(ValueError,"safety or UC"):
            self.score(items)

    def test_forged_safe_label_fails(self):
        items=deepcopy(self.data)
        items[1][0]["enriched_stage6"]["berry_b_safety_certified"]=True
        with self.assertRaisesRegex(ValueError,"safety or UC"):
            self.score(items)

    def test_shadow_command_marked_executed_fails(self):
        items=deepcopy(self.data)
        items[1][0]["baseline_stage6"]["no_shadow_action_dispatched"]=False
        with self.assertRaisesRegex(ValueError,"safety or UC"):
            self.score(items)

    def test_fake_firstperson_birth_identity_fails(self):
        items=deepcopy(self.data)
        items[1][0]["original_birth_id"]="i0:synthetic-life-not-born"
        with self.assertRaisesRegex(ValueError,"birth identities"):
            self.score(items)

    def test_negative_control_B_absent_fabrication_fails(self):
        items=deepcopy(self.data)
        target=next(x for x in items[1] if x["layout"]=="B_NONE")
        target["eligible_B_first_step"]=B_COLLECT
        with self.assertRaisesRegex(ValueError,"absent B"):
            self.score(items)

    def test_wrong_profile_equipment_source_fails(self):
        items=deepcopy(self.data)
        target=next(x for x in items[1] if x["profile"]=="restored")
        target["A_only_equipment_sha256"]=next(x for x in items[1]
            if x["profile"]=="sustained")["A_only_equipment_sha256"]
        with self.assertRaisesRegex(ValueError,"model"):
            self.score(items)

    def test_hidden_lethal_variant_influencing_stage6_fails(self):
        items=deepcopy(self.data)
        target=next(x for x in items[1]
            if x["layout"]=="B_EAST" and
            x["hidden_effect_for_external_stratification_only"]=="toxic_lethal")
        target["enriched_stage6"]["commands"]=[B_COLLECT]
        with self.assertRaises(ValueError):
            self.score(items)

    def test_new_cognitive_world_imports_are_forbidden(self):
        source=(Path(__file__).resolve().parents[1]/
                "scripts/audit_stage12_issue110_b_a230zh_sealed_roots.py"
               ).read_text()
        self.assertNotIn("run_stage12_issue110_b_a230zg_lived_root_shadow",source)
        self.assertNotIn("from lab.world import",source)
        self.assertNotIn("from i0.equipment import",source)
        self.assertNotIn("SimulatorPlanner(",source)
        self.assertNotIn("WorldBody(",source)
        self.assertNotIn("Stage12Runtime(",source)


if __name__=="__main__":
    unittest.main()
