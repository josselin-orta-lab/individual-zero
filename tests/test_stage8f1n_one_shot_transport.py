"""Adversarial F1N one-shot transport tests. Absolutely ZERO N01..N48 birth."""
from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os
import unittest

from tools import stage8f1n_prereg_static_guard as FROZEN
from tools import stage8f1n_one_shot_reservation as R
from tools import stage8f1n_one_shot_evidence as E
from tools import stage8f1n_scientific_native as NATIVE
from tools import stage8f1n_independent_scientific_cold as COLD
from tools import stage8f1n_one_shot_publish_status as STATUS


class TestF1NOneShotSafetyNoNewBirth(unittest.TestCase):
    def test_all_original_frozen_sources_and_future_files_pinned(self):
        FROZEN.check_files()
        pins = R.source_blobs()
        self.assertGreaterEqual(len(pins),20)
        self.assertEqual(R.PREEXPOSURE_COMMIT,
                         "253835b7baaa54e0671bcf7cd9037c0d4b7f88ca")
        self.assertEqual(R.GRID_BLOB,"c522d092cb7c1777ebb0f56c4162f61948b35653")
        self.assertEqual(R.PROTOCOL_BLOB,"ff07a8db807bee15277052ea71e1e76321286ab9")
        self.assertEqual(R.ROOT_IDS,[f"N{x:02d}" for x in range(1,49)])
        self.assertEqual(R.SEEDS,list(range(202611259801,202611259849)))
        self.assertEqual(len(E.PARTS)*len(R.ROOT_IDS),336)
        self.assertTrue(set(R.SEEDS).isdisjoint(
            {*range(202611239701,202611239733),
             *range(202611269101,202611269109),
             *range(202611269121,202611269129)}))

    def test_only_first_manual_workflow_has_any_scientific_birth_or_ref_write(self):
        for p in R.SOURCE_PATHS:
            self.assertTrue(Path(p).is_file(),p)
        script=Path(R.SCIENCE_WORKFLOW).read_text()
        self.assertIn("  workflow_dispatch:",script)
        for forbidden in ("  pull_request:","  push:","  schedule:"):
            self.assertNotIn(forbidden,script)
        self.assertIn("run_attempt == 1",script)
        self.assertIn("steps.claim.outcome == 'success'",script)
        self.assertIn("--reserve",script)
        self.assertIn("--science-only",script)
        self.assertIn("F1L_PROTECTION_AUDIT_TOKEN",script)
        self.assertIn("F1N_REHEARSAL_RUN_IDS",script)
        self.assertNotIn("N01_N48_CREATED",script)
        for p in ("tools/stage8f1n_one_shot_reservation.py",
                  "tools/stage8f1n_one_shot_evidence.py",
                  "tools/stage8f1n_scientific_native.py",
                  "tools/stage8f1n_independent_scientific_cold.py",
                  "tools/stage8f1n_one_shot_cold_entry.py",
                  "tools/stage8f1n_one_shot_publish_status.py"):
            ast.parse(Path(p).read_text(),filename=p)

    def test_context_rejects_pr_retry_replayed_science_and_whitespace(self):
        basic={"GITHUB_REPOSITORY":R.REPO,"GITHUB_REF":"refs/heads/main",
               "GITHUB_EVENT_NAME":"workflow_dispatch",
               "GITHUB_RUN_ATTEMPT":"1","GITHUB_RUN_ID":"987654",
               "GITHUB_SHA":"a"*40,"F1N_APPROVED_SOURCE_SHA":"a"*40,
               "F1N_CONSUME_ACK":R.ACK,"GITHUB_TOKEN":"test-fake",
               "F1N_REHEARSAL_RUN_IDS":"12345,12346"}
        with patch.dict(os.environ,basic,clear=True), patch.object(
                R.subprocess,"check_output",return_value="a"*40+"\n"):
            self.assertEqual(R.context()["rehearsal_run_ids"],["12345","12346"])
            for k,v in (("GITHUB_EVENT_NAME","pull_request"),
                        ("GITHUB_RUN_ATTEMPT","2"),
                        ("F1N_APPROVED_SOURCE_SHA","\t"+"a"*40),
                        ("F1N_CONSUME_ACK","CONSUME_F1M_32_ROOTS_NO_SCIENTIFIC_RETRY"),
                        ("F1N_REHEARSAL_RUN_IDS","12345,12345")):
                with self.subTest(field=k),patch.dict(os.environ,{k:v}):
                    with self.assertRaises(R.ReservationError):R.context()

    def test_ruleset_exact_no_bypass_and_create_allowed(self):
        index=[{"id":123,"target":"branch","enforcement":"active"}]
        good={"id":123,"source_type":"Repository","target":"branch",
              "enforcement":"active","bypass_actors":[],
              "conditions":{"ref_name":{"include":[R.CONSUMED_REF],"exclude":[]}},
              "rules":[{"type":"deletion"},{"type":"update"},
                       {"type":"non_fast_forward"}]}
        def verification(item):
            with patch.object(R,"_api",side_effect=[index,item]):
                return R.protected_once_ruleset()
        self.assertEqual(verification(good)["id"],123)
        for invalid in (
                {**good,"bypass_actors":[{"actor_id":5}]},
                {**good,"target":"tag"},
                {**good,"enforcement":"evaluate"},
                {**good,"rules":[{"type":"deletion"}]},
                {**good,"rules":good["rules"] + [{"type":"creation"}]},
                {**good,"conditions":{"ref_name":{
                    "include":["refs/heads/main"],"exclude":[]}}},
                {**good,"conditions":{"ref_name":{
                    "include":[R.CONSUMED_REF],"exclude":["refs/heads/other"]}}}):
            with self.subTest(invalid=invalid),self.assertRaises(R.ReservationError):
                verification(invalid)

    def test_missing_admin_read_token_rejects_immutability(self):
        with patch.dict(os.environ,{"F1L_PROTECTION_AUDIT_TOKEN":""}):
            with self.assertRaises(R.ReservationError):
                R.immutable_release_policy()

    def test_source_birth_is_impossible_without_an_actual_verified_claim(self):
        grid=NATIVE.science_grid()  # JSON, no World instantiated
        with self.assertRaises(PermissionError):
            NATIVE._new_science_world(grid,grid["origins"][0],None)
        with patch.object(R,"load_receipt",return_value={}), patch.object(
                R,"verify_remote",side_effect=R.ReservationError("NO CLAIM")):
            with self.assertRaises(R.ReservationError):
                NATIVE.produce_release("/nonexistent/F1N_RESERVATION.json",None)

    def test_frozen_science_verdicts_are_separate(self):
        def row(i):
            return {"root":f"N{i+1:02d}","ecology":f"eco{i//6}",
                    "source_valid":True,"shams_neutral":True,
                    "all_native_continuations":True,"t6_equal_paid":True,
                    "motor_changed":False,"delta_lived_ticks":0,
                    "both_alive_at_T60":True,
                    "pareto":"FIVE_CHANNELS_EQUAL_OR_TRADEOFF"}
        rows=[row(i) for i in range(48)]
        self.assertEqual(COLD.classify(rows)["motor_verdict"],
                         "NO_REPRODUCIBLE_LOCAL_T6_OWN_MARGIN_MOTOR_EFFECT")
        choices=(0,1,2,6,7,8,12,13) # 8 distinct roots in 3 ecologies
        for i in choices:rows[i]["motor_changed"]=True
        self.assertEqual(COLD.classify(rows)["motor_verdict"],
                         "REPRODUCIBLE_LOCAL_T6_OWN_MARGIN_MOTOR_EFFECT")
        for i in choices:rows[i]["delta_lived_ticks"]=1
        self.assertEqual(COLD.classify(rows)["survival_verdict"],
                         "LOCAL_T60_OWN_MARGIN_SURVIVAL_ADAPTIVE_ADVANTAGE")
        rows[21]["delta_lived_ticks"]=-1
        self.assertEqual(COLD.classify(rows)["survival_verdict"],
                         "NO_REPRODUCIBLE_LOCAL_T60_OWN_MARGIN_SURVIVAL_ADVANTAGE")
        rows[21]["t6_equal_paid"]=False
        self.assertEqual(COLD.classify(rows)["status"],
                         "INCONCLUSIVE_REAL_DECISION_COST")

    def test_body_is_secondary_and_requires_12_true_pareto_roots(self):
        rows=[{"root":f"N{i+1:02d}","ecology":f"eco{i//6}",
               "source_valid":True,"shams_neutral":True,
               "all_native_continuations":True,"t6_equal_paid":True,
               "motor_changed":False,"delta_lived_ticks":0,
               "both_alive_at_T60":True,
               "pareto":("MARGIN_FIVE_CHANNEL_DOMINANCE" if i<12 else
                         "FIVE_CHANNELS_EQUAL_OR_TRADEOFF")}
              for i in range(48)]
        self.assertNotEqual(COLD.classify(rows)["body_verdict"],
                            "BODY_ONLY_NOT_SURVIVAL_ADAPTATION")
        rows[12]["pareto"]="MARGIN_FIVE_CHANNEL_DOMINANCE"
        self.assertEqual(COLD.classify(rows)["body_verdict"],
                         "BODY_ONLY_NOT_SURVIVAL_ADAPTATION")
        rows[33]["pareto"]="MASKED_FIVE_CHANNEL_DOMINANCE"
        self.assertEqual(COLD.classify(rows)["body_verdict"],
                         "NO_REPRODUCIBLE_LOCAL_T60_OWN_MARGIN_BODY_PARETO_SUPPORT")

    def test_writer_never_drops_an_unfunded_root_or_duplicates_a_gzip(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)
            writer=E.CaseWriter(path/"parts",["N01"])
            src={"valid":False,"steps":[],"source_error":"UNFUNDED"}
            origin={"id":"N01","seed":1,"ecology":"e0","body":[1,2,3,4,5]}
            writer.part("N01","source_t1_t4",src)
            writer.finish_incomplete(origin,src,{"error":"UNFUNDED_OR_INCOMPLETE_SOURCE"})
            with self.assertRaises(RuntimeError):
                writer.part("N01","source_t1_t4",src)
            self.assertEqual(len(writer.entries),7)
            index={"rows":writer.cases}
            receipt={"stub_only":True}
            manifest=E.finish(writer,index,path,receipt)
            seen=[]
            idx,m,n=E.read_bundle(path,["N01"],lambda md,parts:seen.append(parts))
            self.assertEqual((n,len(seen),len(seen[0])),(1,1,7))
            self.assertEqual(m["original_part_count"],7)
            self.assertEqual(manifest["heldout_native_passes"],1)
            with (path/"F1N_ORIGINALS_336_GZIP.tar.gz").open("ab") as fd:
                fd.write(b"hacked")
            with self.assertRaises(ValueError):
                E.read_bundle(path,["N01"],lambda x,y:None)

    def test_cold_python_cannot_import_engine_or_science_producer(self):
        for path in ("tools/stage8f1n_independent_scientific_cold.py",
                     "tools/stage8f1n_one_shot_cold_entry.py"):
            tree=ast.parse(Path(path).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    self.assertFalse((node.module or "").startswith("i3."))
                    self.assertNotIn("stage8f1n_scientific_native",node.module or "")
                    self.assertNotIn("stage8f1n_dev_native_transport",node.module or "")
                if isinstance(node,ast.Import):
                    for value in node.names:
                        self.assertFalse(value.name.startswith("i3."))

    def test_same_tree_two_full_cold_rehearsals_required(self):
        prior={"head_sha":"a"*40,"status":"completed","conclusion":"success",
               "event":"pull_request","run_attempt":1,"path":R.DEV_WORKFLOW,
               "repository":{"full_name":R.REPO}}
        jobs={"jobs":[{"name":j,"status":"completed","conclusion":"success"}
                      for j in R.REQUIRED_DEV_JOBS]}
        commit={"tree":{"sha":"b"*40}}
        with patch.object(R,"_api",side_effect=[prior,jobs,commit]):
            self.assertEqual(R.verify_prior_rehearsal({},"b"*40,"123"),"a"*40)
        with patch.object(R,"_api",side_effect=[prior,jobs,commit]):
            with self.assertRaisesRegex(R.ReservationError,"DIFFERENT Git"):
                R.verify_prior_rehearsal({},"c"*40,"123")
        incomplete={"jobs":jobs["jobs"][:-1]}
        with patch.object(R,"_api",side_effect=[prior,incomplete]):
            with self.assertRaisesRegex(R.ReservationError,"six DEV"):
                R.verify_prior_rehearsal({},"b"*40,"123")

    def test_readonly_administrative_preflight_never_creates_a_ref(self):
        with patch.object(R,"source_blobs",return_value={}), patch.object(
                R,"protected_once_ruleset",return_value={"id":123}), patch.object(
                R,"immutable_release_policy",return_value={"enabled":True}), patch.object(
                R,"_ref_absent",return_value=None),patch.object(
                R,"_api",side_effect=R.ReservationError("GitHub GET releases/tags/ HTTP 404")) as api:
            result=R.readonly_admin_preflight()
            self.assertEqual(result["science_heldout_world_steps"],0)
            self.assertEqual(result["consumed_ref_absent"],True)
            self.assertEqual([c.args[0] for c in api.call_args_list],["GET","GET"])
        with patch.object(R,"source_blobs",return_value={}), patch.object(
                R,"protected_once_ruleset",side_effect=R.ReservationError("no ruleset")):
            with self.assertRaises(R.ReservationError):R.readonly_admin_preflight()

    def test_terminal_cold_failure_keeps_consumption_and_no_retry(self):
        with TemporaryDirectory() as path:
            report=STATUS.publish(path,"failure")
            self.assertTrue(report["one_scientific_allocation_consumed"])
            self.assertFalse(report["native_scientific_retry_permitted"])
            self.assertEqual(report["scientific_status"],
                             "INCONCLUSIVE_COLD_AUDIT_MISSING_NO_RETRY")


if __name__ == "__main__":
    unittest.main()
