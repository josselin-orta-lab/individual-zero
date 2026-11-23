"""F1M first-only transport abuse tests. NEVER instantiates M01..M32."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import ast
import json
import os
import unittest

from tools import stage8f1m_prereg_static_guard as G
from tools import stage8f1m_one_shot_reservation as R
from tools import stage8f1m_one_shot_evidence as E
from tools import stage8f1m_independent_scientific_cold as COLD
from tools import stage8f1m_one_shot_publish_status as STATUS


class TestF1MOneShotTransportNoNativeBirth(unittest.TestCase):
    def test_prereg_source_matches_git_and_no_heldout_birth(self):
        self.assertEqual(G.check_files()["science_births_created"],0)
        pins=R.source_blobs()
        self.assertGreaterEqual(len(pins),19)
        self.assertEqual(R.ROOT_IDS,[f"M{i:02d}" for i in range(1,33)])
        self.assertEqual(R.SEEDS,list(G.SEEDS))
        self.assertEqual(R.GRID_BLOB,G.GRID_BLOB)
        self.assertEqual(R.PROTOCOL_BLOB,G.PROTOCOL_BLOB)
        self.assertEqual(R.PREEXPOSURE,"d79eb0712daccab2dad0839d5c9a6eaa717eef9f")
        self.assertEqual(R.CONSUMED_REF,
                         "refs/heads/i3-stage8-f1m-heldout-consumed-once")
        self.assertEqual(len(E.PARTS),12)
        self.assertEqual(len(E.PARTS)*len(R.ROOT_IDS),384)

    def test_all_scientific_sources_parse_and_manual_only_trigger(self):
        for path in (
          "tools/stage8f1m_one_shot_reservation.py",
          "tools/stage8f1m_scientific_native.py",
          "tools/stage8f1m_one_shot_evidence.py",
          "tools/stage8f1m_independent_scientific_cold.py",
          "tools/stage8f1m_one_shot_cold_entry.py",
          "tools/stage8f1m_one_shot_publish_status.py"):
            ast.parse(Path(path).read_text(encoding="utf8"),filename=path)
        workflow=Path(".github/workflows/i3-stage8f1m-heldout-science-manual-once.yml").read_text()
        self.assertIn("  workflow_dispatch:",workflow)
        self.assertNotIn("  push:",workflow)
        self.assertNotIn("  pull_request:",workflow)
        self.assertNotIn("  schedule:",workflow)
        self.assertIn("run_attempt == 1",workflow)
        self.assertIn("steps.claim.outcome == 'success'",workflow)
        self.assertIn("--science-only --reservation",workflow)
        self.assertIn("F1L_PROTECTION_AUDIT_TOKEN",workflow)
        self.assertIn("F1M_REHEARSAL_RUN_IDS",workflow)

    def test_prereg_is_not_science_authority(self):
        with patch.dict(os.environ,{"GITHUB_REPOSITORY":R.REPO,
                 "GITHUB_EVENT_NAME":"pull_request","GITHUB_REF":"refs/heads/main",
                 "GITHUB_RUN_ATTEMPT":"1","GITHUB_RUN_ID":"42"},
                 clear=True):
            with self.assertRaises(R.ReservationError):
                R.context()
        with patch.dict(os.environ,{"GITHUB_REPOSITORY":R.REPO,
                 "GITHUB_EVENT_NAME":"workflow_dispatch","GITHUB_REF":"refs/heads/main",
                 "GITHUB_RUN_ATTEMPT":"2","GITHUB_RUN_ID":"42"},
                 clear=True):
            with self.assertRaises(R.ReservationError):
                R.context()

    def test_repository_ruleset_has_to_be_exact_no_bypass(self):
        index=[{"id":278,"enforcement":"active","target":"branch"}]
        good={"id":278,"source_type":"Repository","enforcement":"active",
              "target":"branch",
              "conditions":{"ref_name":{"include":[R.CONSUMED_REF],"exclude":[]}},
              "rules":[{"type":"deletion"},{"type":"update"},{"type":"non_fast_forward"}],
              "bypass_actors":[]}
        def verify(doc):
            with patch.object(R,"_api",side_effect=[index,doc]):
                return R.protected_once_ruleset()
        self.assertEqual(verify(good)["id"],278)
        for mutant in [
                {**good,"bypass_actors":[{"actor_id":5}]},
                {**good,"enforcement":"evaluate"},
                {**good,"rules":[{"type":"deletion"}]},
                {**good,"conditions":{"ref_name":{"include":["refs/heads/main"],
                                                  "exclude":[]}}},
                {**good,"conditions":{"ref_name":{"include":[R.CONSUMED_REF],
                                                  "exclude":["refs/heads/other"]}}}
                ]:
            with self.assertRaises(R.ReservationError):
                verify(mutant)

    def test_missing_admin_token_fails_closed_before_source_birth(self):
        with patch.dict(os.environ,{"F1L_PROTECTION_AUDIT_TOKEN":""}):
            with self.assertRaises(R.ReservationError):
                R.immutable_release_policy()

    def test_streamed_original_parts_sha_and_incremental_checkpoints(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            writer=E.CaseWriter(root/"parts",["M01"])
            src={"source_valid":False,"source_receipt_sha256":"unfunded-0"}
            row={"origin":{"id":"M01"},"source":src,"arms":{},"shams":{},
                 "sham_arms":{},"content_t5":{},"comparison":{},
                 "case_sha256":"fixture-not-science"}
            writer.part("M01","source",src)
            writer.finalize_case(row)
            self.assertEqual(len(writer.entries),12)
            index={"rows":[{"origin":row["origin"],"case_sha256":row["case_sha256"]}]}
            claim={"fixture":"reservation only, no GitHub POST"}
            manifest=E.finish(writer,index,root,claim)
            observed=[]
            header,idx,n=E.read_bundle(root,["M01"],
                lambda meta,parts:observed.append((meta,parts)))
            self.assertEqual((n,len(observed),len(observed[0][1])),(1,1,12))
            self.assertEqual(E.digest(E.canonical(header)),idx["native_index_sha256"])
            self.assertEqual(manifest["heldout_native_passes"],1)
            with (root/"F1M_CUSTODY_MANIFEST.json").open("ab") as corrupted:
                corrupted.write(b"garbage")
            # JSON manifest malformed or stale SHA never verifies as genuine.
            with self.assertRaises((ValueError,json.JSONDecodeError)):
                E.read_bundle(root,["M01"],lambda meta,parts:None)

    def test_motor_adaptation_and_body_are_three_distinct_metrics(self):
        def source(i):
            eco=f"eco{i//4}"
            base={"pareto":"FIVE_CHANNELS_EQUAL","delta_lived_ticks_t6_t60":0}
            return {"root":f"M{i+1:02d}","ecology":eco,
                    "source_valid":True,"all_shams_neutral":True,
                    "all_native_continuations":True,"t5_equal_paid":True,
                    "recent":{"cost_equal":True,"motor_changed":False,
                       "winner_changed":False,"delta_lived_ticks":0,"body":deepcopy(base)},
                    "stale":{"cost_equal":True,"motor_changed":False,
                       "winner_changed":False,"delta_lived_ticks":0,"body":deepcopy(base)}}
        roots=[source(i) for i in range(32)]
        for i in (0,1,4,5,8,9):
            roots[i]["recent"]["motor_changed"]=True
        verdict=COLD.classify(roots)
        self.assertEqual(verdict["motor_verdict"],
                         "REPRODUCIBLE_LOCAL_T6_RESIDUAL_MOTOR_EFFECT")
        self.assertEqual(verdict["survival_verdict"],
                         "NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE")
        for i in (0,1,4,5,8,9):
            roots[i]["recent"]["delta_lived_ticks"]=1
            roots[i]["recent"]["body"]["delta_lived_ticks_t6_t60"]=1
        verdict=COLD.classify(roots)
        self.assertEqual(verdict["survival_verdict"],
                         "LOCAL_T60_SURVIVAL_ADAPTIVE_ADVANTAGE")
        roots[15]["stale"]["delta_lived_ticks"]=-1
        self.assertEqual(COLD.classify(roots)["survival_verdict"],
                         "NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE")
        roots[15]["stale"]["cost_equal"]=False
        self.assertEqual(COLD.classify(roots)["status"],
                         "INCONCLUSIVE_REAL_DECISION_COST")

    def test_terminal_no_retry_without_cold_never_claims_science_success(self):
        with TemporaryDirectory() as tmp:
            out=STATUS.publish(tmp,"failure")
            self.assertTrue(out["one_scientific_allocation_consumed"])
            self.assertFalse(out["native_scientific_retry_permitted"])
            self.assertEqual(out["scientific_status"],
                             "INCONCLUSIVE_COLD_AUDIT_MISSING_NO_RETRY")


if __name__=="__main__":
    unittest.main()
