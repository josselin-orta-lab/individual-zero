"""F1K full 16-root scientific release safety tests. ZERO held-out World.step.

Mocks use fake Github Git ref API; they never create the real consumed marker.
Run the actual full T60 experiment ONLY in DEV_R via the separate CI job.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools import stage8f1k_one_shot_reservation as R
from tools import stage8f1k_one_shot_evidence as E
from tools import stage8f1k_policy_cost_value_prospective as P
from tools import stage8f1k_independent_policy_value_cold_audit as Cold

HEAD = "a"*40
ENV = {
    "GITHUB_REPOSITORY":R.REPO,
    "GITHUB_REF":"refs/heads/main",
    "GITHUB_EVENT_NAME":"workflow_dispatch",
    "GITHUB_RUN_ID":"12345678901",
    "F1K_REHEARSAL_RUN_ID":"424242424242",
    "GITHUB_RUN_ATTEMPT":"1",
    "GITHUB_SHA":HEAD,
    "F1K_APPROVED_SOURCE_SHA":HEAD,
    "F1K_CONSUME_ACK":R.ACK,
    "GITHUB_TOKEN":"TEST_FAKE_TOKEN_NEVER_USED_FOR_HTTP",
}


class FakeGitHub:
    """REST-only mock: exactly one POST refs and no deletion/overwrite."""
    def __init__(self):
        self.claim=None
        self.commit=None
        self.calls=[]

    def api(self,method,path,payload=None):
        self.calls.append((method,path))
        if method=="GET" and path=="/git/ref/heads/main":
            return {"ref":"refs/heads/main","object":{"sha":HEAD}}
        if method=="GET" and path=="/git/ref/heads/"+R.BRANCH:
            if not self.commit:
                raise R.ReservationError("F1K ONE SHOT: GitHub GET returned HTTP 404")
            return {"ref":R.CONSUMED_REF,"object":{"sha":self.commit}}
        if method=="GET" and path=="/git/commits/"+HEAD:
            return {"tree":{"sha":"b"*40}}
        if method=="GET" and path=="/git/commits/"+"e"*40:
            return {"tree":{"sha":"b"*40}}
        if method=="GET" and path=="/actions/runs/424242424242":
            return {
                "conclusion":"success","status":"completed",
                "event":"pull_request",
                "head_sha":"e"*40,
                "path":".github/workflows/i3-stage8f1k-t60-dev-rehearsal.yml",
                "repository":{"full_name":R.REPO},
            }
        if method=="POST" and path=="/git/blobs":
            self.claim=payload["content"].encode("utf-8")
            return {"sha":R.blob(self.claim)}
        if method=="POST" and path=="/git/trees":
            assert payload["tree"][0]["path"]==R.MARKER_PATH
            return {"sha":"c"*40}
        if method=="POST" and path=="/git/commits":
            assert payload["parents"]==[HEAD]
            return {"sha":"d"*40}
        if method=="POST" and path=="/git/refs":
            if self.commit is not None:
                raise R.ReservationError("F1K ONE SHOT: GitHub returned HTTP 422")
            assert payload["ref"]==R.CONSUMED_REF
            self.commit=payload["sha"]
            return {"ref":R.CONSUMED_REF,"object":{"sha":self.commit}}
        if method=="GET" and path.startswith("/contents/"+R.MARKER_PATH):
            return {
                "sha":R.blob(self.claim),
                "encoding":"base64",
                "content":base64.b64encode(self.claim).decode("ascii"),
            }
        raise AssertionError("unexpected mock API operation: "+repr((method,path)))


class F1KOneShotSafety(unittest.TestCase):
    def test_source_blobs_and_frozen_methods_never_run_a_life(self):
        pins=R.source_blobs()
        self.assertEqual(pins["src/i3/modules/mind.py"],R.ENGINE_PINS[
            "src/i3/modules/mind.py"])
        self.assertEqual(R.blob(Path(R.GRID_PATH).read_bytes()),R.GRID_BLOB)
        self.assertEqual(R.blob(Path(R.PROTOCOL_PATH).read_bytes()),R.PROTOCOL_BLOB)
        grid=P.release_grid()
        self.assertEqual(len(grid["origins"]),16)
        self.assertEqual({x["id"] for x in grid["origins"]},
                         {"K"+str(i).zfill(2) for i in range(1,17)})

    def test_dev_r_16_are_disjoint_worlds_and_seeds_with_real_T60(self):
        dev=P.validate_rehearsal(P.rehearsal_grid())
        heldout=P.release_grid()
        self.assertEqual(dev["final_tick"],60)
        self.assertEqual(len(dev["origins"]),16)
        self.assertEqual(len(dev["ecologies"]),4)
        self.assertFalse({x["seed"] for x in dev["origins"]} &
                         {x["seed"] for x in heldout["origins"]})
        self.assertFalse({x["id"] for x in dev["ecologies"]} &
                         {x["id"] for x in heldout["ecologies"]})
        self.assertEqual(Cold.source_guard(dev,"REHEARSAL_ONLY"),dev["origins"])

    def test_no_scientific_source_without_claim_even_with_old_env_value(self):
        with patch.dict(os.environ,{P.RELEASE_ENV:P.PREEXPOSURE_MAIN},clear=True):
            with patch.object(P,"new_world",side_effect=AssertionError(
                    "World.step exposure was invoked before reservation")):
                with self.assertRaises(PermissionError):
                    P.produce(P.release_grid(),"F1K_HELDOUT_RELEASE")

    def test_only_first_manual_main_commit_can_claim(self):
        with patch.dict(os.environ,ENV,clear=True), patch.object(
                R,"_current_commit",return_value=HEAD):
            self.assertEqual(R.context()["head_sha"],HEAD)
            for key,value in (
                ("F1K_REHEARSAL_RUN_ID",""),
                ("GITHUB_RUN_ATTEMPT","2"),
                ("GITHUB_REF","refs/heads/experimental"),
                ("GITHUB_EVENT_NAME","pull_request"),
                ("F1K_CONSUME_ACK","NOT_APPROVED"),
                ("F1K_APPROVED_SOURCE_SHA","f"*40),
            ):
                with patch.dict(os.environ,{key:value}):
                    with self.assertRaises(R.ReservationError):
                        R.context()

    def test_atomic_create_only_and_second_run_rejected(self):
        fake=FakeGitHub()
        with TemporaryDirectory() as td,patch.dict(os.environ,ENV,clear=True):
            with patch.object(R,"_api",side_effect=fake.api), patch.object(
                    R,"_current_commit",return_value=HEAD):
                first=R.reserve(Path(td)/"first.json")
                self.assertEqual(first["reservation_commit"],"d"*40)
                self.assertEqual(R.verify_remote(first)["root_ids"][0],"K01")
                self.assertEqual(sum(method=="POST" and path=="/git/refs"
                                     for method,path in fake.calls),1)
                with self.assertRaises(R.ReservationError):
                    R.reserve(Path(td)/"second.json")
                self.assertEqual(sum(method=="POST" and path=="/git/refs"
                                     for method,path in fake.calls),1)
                forged=deepcopy(first)
                forged["claim"]["seeds"][-1]+=999
                with self.assertRaises(R.ReservationError):
                    R.validate_receipt(forged)

    def test_failed_or_different_tree_rehearsal_refuses_before_ref_create(self):
        fake=FakeGitHub()
        def invalid(method,path,payload=None):
            if method=="GET" and path=="/git/commits/"+"e"*40:
                return {"tree":{"sha":"0"*40}}
            return fake.api(method,path,payload)
        with TemporaryDirectory() as td,patch.dict(os.environ,ENV,clear=True):
            with patch.object(R,"_api",side_effect=invalid),patch.object(
                    R,"_current_commit",return_value=HEAD):
                with self.assertRaises(R.ReservationError):
                    R.reserve(Path(td)/"none.json")
                self.assertFalse(any(m=="POST" and p=="/git/refs"
                                     for m,p in fake.calls))

    def test_permission_denied_or_ambiguous_claim_must_fail_closed(self):
        fake=FakeGitHub()
        def denied(method,path,payload=None):
            if path=="/git/ref/heads/"+R.BRANCH:
                raise R.ReservationError("HTTP 403")
            return fake.api(method,path,payload)
        with TemporaryDirectory() as td,patch.dict(os.environ,ENV,clear=True):
            with patch.object(R,"_api",side_effect=denied),patch.object(
                    R,"_current_commit",return_value=HEAD):
                with self.assertRaises(R.ReservationError):
                    R.reserve(Path(td)/"no_claim.json")
                self.assertFalse(Path(td,"no_claim.json").exists())
                self.assertFalse(any(m=="POST" and p=="/git/refs"
                                     for m,p in fake.calls))

    def test_4_original_gzips_source_and_three_arms_even_if_unfunded(self):
        origin={"id":"DEV_X","seed":202611219999,"ecology":"DEV_X"}
        source={"origin":origin,"source_receipt_sha256":"x",
                "valid_paid_personal_source":False}
        row={"origin":origin,"source":source,"arms":{},
             "comparison":{"source_valid":False}}
        row["case_sha256"]=E.digest(E.canonical(row))
        report={"schema":"DEV_FIXTURE","phase":"REHEARSAL_ONLY",
                "origin_count":1,"origin_ids":["DEV_X"],
                "worlds":["DEV_X"],"rows":[row]}
        with TemporaryDirectory() as td:
            folder=Path(td)/"archive"
            folder.mkdir()
            writer=E.CaseWriter(folder/"original_cases",["DEV_X"])
            writer(row)
            index=E.finalize(writer,report,deepcopy(report),folder)
            proof=E.verify_bundle(folder)
            self.assertEqual(proof["original_native_gzips"],4)
            self.assertTrue(proof["same_bytes_technical_reproduction"])
            self.assertEqual(index["entries"][1]["part"],"reference_p13")
            self.assertTrue((folder/"original_cases/_checkpoint_01.json").is_file())
            with (folder/"F1K_ORIGINALS_64_GZIP.tar.gz").open("wb") as stream:
                stream.write(b"altered")
            with self.assertRaises(ValueError):
                E.verify_bundle(folder)

    def test_f1k_release_native_source_can_start_only_once_without_exposure(self):
        # Nothing here calls the heldout World: abort before the source birth.
        grid=P.release_grid()
        with TemporaryDirectory() as td:
            reservation=Path(td)/"F1K_RESERVATION.json"
            reservation.write_text("{}")
            env={P.RELEASE_ENV:P.PREEXPOSURE_MAIN,
                 "I3_F1K_RESERVATION_RECEIPT":str(reservation)}
            with patch.dict(os.environ,env), patch.object(
                    R,"verify_remote",return_value={
                        "workflow_run_id":"FAKE_RUN",
                        "head_sha":"a"*40,
                    }),patch.object(P,"source",side_effect=RuntimeError(
                        "PRE_BIRTH_ABORT_NO_RESERVED_WORLDSTEP")):
                with self.assertRaisesRegex(RuntimeError,"PRE_BIRTH_ABORT"):
                    P.produce(grid,"F1K_HELDOUT_RELEASE")
                lock=reservation.with_suffix(".NATIVE_START_LOCK")
                self.assertTrue(lock.is_file())
                claim=json.loads(lock.read_bytes())
                self.assertEqual(claim["origin_ids"],
                                 ["K"+str(i).zfill(2) for i in range(1,17)])
                with self.assertRaises(FileExistsError):
                    P.produce(grid,"F1K_HELDOUT_RELEASE")

    def test_scientific_custody_can_only_read_back_originals_not_reexecute(self):
        # This is intentionally a synthetic one-row data envelope, not K.
        root={"id":"DEV_X","seed":202611219999,"ecology":"DEV_X"}
        source={"origin":root,"source_receipt_sha256":"x",
                "valid_paid_personal_source":False}
        row={"origin":root,"source":source,"arms":{},
             "comparison":{"source_valid":False}}
        row["case_sha256"]=E.digest(E.canonical(row))
        report={"schema":"SYNTHETIC_NOT_SCIENCE","phase":"F1K_HELDOUT_RELEASE",
                "origin_count":1,"origin_ids":["DEV_X"],
                "worlds":["DEV_X"],"rows":[row]}
        with TemporaryDirectory() as td:
            folder=Path(td)/"originals"
            folder.mkdir()
            writer=E.CaseWriter(folder/"original_cases",["DEV_X"])
            writer(row)
            with self.assertRaises(ValueError):
                E.finalize(writer,report,report,folder,
                           reproduction_kind="DEV_R_NATIVE_REPETITION")
            index=E.finalize(writer,report,json.loads(E.canonical(report)),folder,
                             reproduction_kind="F1K_CANONICAL_READBACK_NO_SECOND_NATIVE")
            proof=E.verify_bundle(folder)
            self.assertTrue(index["canonical_readback_byte_identical"])
            self.assertFalse(index["technical_byte_identical"])
            self.assertEqual(index["heldout_native_passes"],1)
            self.assertTrue(proof["same_bytes_canonical_readback"])
            self.assertFalse(proof["same_bytes_technical_reproduction"])
            self.assertFalse((folder/"F1K_TECHNICAL_REPRODUCTION.json.gz").exists())
            self.assertTrue((folder/"F1K_CANONICAL_READBACK.json.gz").is_file())

    def test_no_auto_science_and_no_clobber_or_retry_in_workflow(self):
        file=Path(".github/workflows/i3-stage8f1k-heldout-science-manual-once.yml")
        txt=file.read_text(encoding="utf-8")
        self.assertIn("\n  workflow_dispatch:\n",txt)
        for forbidden in ("\n  pull_request:","\n  push:","\n  schedule:",
                          "gh release upload --clobber",
                          "rerun_workflow",
                          "cancel-in-progress: true"):
            self.assertNotIn(forbidden,txt)
        for required in ("concurrency:","github.run_attempt == 1",
                         "--reserve","--release","F1K_RESERVATION.json",
                         "stage8f1k_one_shot_cold_entry",
                         "stage8f1k_one_shot_publish_status"):
            self.assertIn(required,txt)


if __name__=="__main__":
    unittest.main()
