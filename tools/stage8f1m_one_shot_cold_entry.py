"""F1M first-only independent cold entry: remote protected claim + immutable bytes.

ONLY Python 3.12 stdlib + engine-free verifier modules. No import of F1M
native producer, World, Mind, BodyLaws, or any scientific M source execution.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from tools import stage8f1m_one_shot_reservation as R
from tools import stage8f1m_one_shot_evidence as E
from tools import stage8f1m_independent_scientific_cold as Cold

RAW_TAG="i3-stage8f1m-t60-raw-heldout-once"


def check(ok,reason):
    if not ok:
        raise ValueError("F1M FIRST ONLY COLD: "+reason)


def verified_raw_release(receipt,input_dir):
    release=R._api("GET","/releases/tags/"+RAW_TAG)
    check(release.get("immutable") is True and
          release.get("tag_name")==RAW_TAG and
          release.get("target_commitish")==receipt["reservation_commit"],
          "original release not immutable or detached from claim")
    paths=[input_dir/"F1M_RESERVATION.json",
           input_dir/"F1M_RESERVATION.NATIVE_START_LOCK"]
    paths+=sorted((input_dir/"f1m-originals").glob("F1M_*"))
    paths+=sorted((input_dir/"f1m-emergency").glob("F1M_*"))
    expected={p.name:p for p in paths if p.is_file()}
    check(len(expected)==len(paths) and len(expected)>=7,
          "missing or duplicated raw release asset name")
    assets=release.get("assets",[])
    listed={a.get("name"):a for a in assets}
    check(len(assets)==len(listed) and set(listed)==set(expected),
          "incomplete immutable release assets")
    for name,path in expected.items():
        expected_sha=E.file_digest(path)
        if listed[name].get("digest")!="sha256:"+expected_sha:
            raise ValueError("immutable release asset differs: "+name)
        if listed[name].get("size")!=path.stat().st_size:
            raise ValueError("immutable release asset size differs: "+name)
    return {"raw_release_tag":RAW_TAG,"immutable":True,
            "github_release_asset_digests_verified":len(expected),
            "raw_release_target":receipt["reservation_commit"]}


def run(input_dir,out_dir):
    receipt=R.load_receipt(Path(input_dir)/"F1M_RESERVATION.json")
    claim=R.verify_remote(receipt,same_run=False)
    raw=verified_raw_release(receipt,Path(input_dir))
    lock=json.loads((Path(input_dir)/"F1M_RESERVATION.NATIVE_START_LOCK").read_bytes())
    expected_lock={"schema":"i3-stage8f1m-first-native-start-lock/v0",
                   "run_id":claim["workflow_run_id"],
                   "head_sha":claim["head_sha"],"root_ids":R.ROOT_IDS,
                   "one_scientific_attempt_only":True}
    check(lock==expected_lock,
          "no native start lock before even first M source birth")
    root=Path(input_dir)/"f1m-originals"
    grid=Cold.science_grid()
    verified=[];step_count=round_count=0
    def on_root(metadata,parts):
        nonlocal step_count,round_count
        row,steps,rounds=Cold.cold_root(grid,metadata,parts)
        verified.append(row)
        step_count+=steps
        round_count+=rounds
    index,manifest,count=E.read_bundle(root,R.ROOT_IDS,on_root)
    check(count==32 and manifest["original_part_count"]==384
          and index["schema"]=="i3-stage8f1m-scientific-one-shot-residual-causal-T60/v0"
          and index["phase"]=="F1M_HELDOUT_RELEASE"
          and index["source_main_prereg_commit"]==R.PREEXPOSURE
          and index["grid_blob_sha"]==R.GRID_BLOB
          and index["protocol_blob_sha"]==R.PROTOCOL_BLOB
          and index["source_policy"]=="F1JFixedRoundMind"
          and index["arms"]==R.ARMS
          and index["origin_ids"]==R.ROOT_IDS
          and index["seeds"]==R.SEEDS
          and index["scientific_verdict"] is None
          and index["original_scientific_native_passes"]==1
          and index["no_motor_override"] is True
          and manifest["reservation_sha256"]==E.digest(E.canonical(receipt))
          and claim["root_ids"]==index["origin_ids"],
          "cold report not bound to frozen 32 native M roots or first-only reservation")
    verdicts=Cold.classify(verified)
    result={"schema":"i3-stage8f1m-independent-scientific-cold-v0",
            "phase":"F1M_HELDOUT_RELEASE",
            "preexposure_grid_git_blob":R.GRID_BLOB,
            "preexposure_protocol_git_blob":R.PROTOCOL_BLOB,
            "preexposure_main_sha":R.PREEXPOSURE,
            "science_run_id":claim["workflow_run_id"],
            "source_git_commit":claim["head_sha"],
            "one_native_scientific_pass":True,
            "original_part_gzips_sha256_verified":384,
            "roots_verified":len(verified),
            "reconstructed_native_World_steps":step_count,
            "reconstructed_substantive_F1J_rounds":round_count,
            "byte_custody":raw,
            "original_tar_sha256":manifest["originals_tar_gzip_sha256"],
            "native_index_sha256":manifest["native_index_sha256"],
            "verdicts":verdicts,
            "per_root":verified,
            "no_world_or_mind_import":True,
            "stage2_status":"NOT_ISSUED/HOLD_NO_VERDICT",
            "historical_F1L":"NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE"}
    out_dir=Path(out_dir)
    out_dir.mkdir(parents=True,exist_ok=False)
    E.new_file(out_dir/"F1M_INDEPENDENT_COLD_T60.json",E.canonical(result)+b"\n")
    E.new_file(out_dir/"F1M_BYTE_CUSTODY_COLD.json",
               E.canonical({"schema":"i3-stage8f1m-independent-custody-v0",
                           "claim_run":claim["workflow_run_id"],**raw,
                           "parts":count*12,
                           "first_only":True})+b"\n")
    print(json.dumps({"status":"F1M_INDEPENDENT_COLD_COMPLETE",
          "roots":count,"original_gzips":384,
          "native_steps":step_count,"substantive_rounds":round_count,
          "gates":verdicts.get("status"),
          "motor":verdicts.get("motor_verdict"),
          "survival":verdicts.get("survival_verdict"),
          "body":verdicts.get("body_verdict"),
          "source_not_reexecuted":True},sort_keys=True))
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("input_dir",type=Path)
    parser.add_argument("output_dir",type=Path)
    args=parser.parse_args()
    run(args.input_dir,args.output_dir)


if __name__=="__main__":
    main()
