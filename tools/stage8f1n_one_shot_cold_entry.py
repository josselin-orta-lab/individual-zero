"""F1N independent immutable RAW release and 336 gzip cold audit entrypoint.

Python3.12 stdlib, no i3 engine, native producer, or Mind import.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools import stage8f1n_one_shot_reservation as R
from tools import stage8f1n_one_shot_evidence as E
from tools import stage8f1n_independent_scientific_cold as COLD

RAW_TAG = "i3-stage8f1n-t60-raw-heldout-once"


def check(ok, reason):
    if not ok:
        raise ValueError("F1N FIRST ONLY COLD: " + reason)


def verified_raw_release(receipt, input_dir):
    release = R._api("GET", "/releases/tags/" + RAW_TAG)
    check(release.get("immutable") is True and
          release.get("tag_name") == RAW_TAG and
          release.get("target_commitish") == receipt["reservation_commit"],
          "RAW Release not immutable or not targeted to scientific claim")
    paths = [input_dir/"F1N_RESERVATION.json",
             input_dir/"F1N_RESERVATION.NATIVE_START_LOCK"]
    paths += sorted((input_dir/"f1n-originals").glob("F1N_*"))
    paths += sorted((input_dir/"f1n-preservation").glob("F1N_*"))
    expected = {p.name:p for p in paths if p.is_file()}
    check(len(expected) == len(paths) and len(expected) >= 7,
          "RAW release asset missing or name collision")
    assets = release.get("assets", [])
    listed = {x["name"]:x for x in assets}
    check(len(assets) == len(listed) and set(listed) == set(expected),
          "RAW release asset list is not exact")
    for name,path in expected.items():
        check(listed[name].get("digest") == "sha256:" + E.file_digest(path) and
              listed[name].get("size") == path.stat().st_size,
              "RAW immutable release asset SHA differs: " + name)
    return {"tag":RAW_TAG,"immutable":True,
            "target":receipt["reservation_commit"],
            "asset_sha256_verified":len(expected)}


def run(input_dir, output_dir):
    input_dir = Path(input_dir)
    receipt = R.load_receipt(input_dir/"F1N_RESERVATION.json")
    claim = R.verify_remote(receipt, same_run=False)
    raw = verified_raw_release(receipt,input_dir)
    start = json.loads((input_dir/"F1N_RESERVATION.NATIVE_START_LOCK").read_bytes())
    check(start == {"schema":"i3-stage8f1n-first-native-start-lock/v0",
                    "run_id":claim["workflow_run_id"],
                    "head_sha":claim["head_sha"],
                    "root_ids":R.ROOT_IDS,
                    "one_scientific_attempt_only":True},
          "missing native START lock before the 48 original births")
    grid = COLD.science_grid()
    rows=[]
    count_steps=count_rounds=0
    def on_root(metadata,originals):
        nonlocal count_steps,count_rounds
        result,steps,rounds = COLD.cold_root(grid,metadata,originals)
        rows.append(result)
        count_steps += steps
        count_rounds += rounds
    root = input_dir/"f1n-originals"
    index,manifest,count = E.read_bundle(root,R.ROOT_IDS,on_root)
    check(count == 48 and manifest["original_part_count"] == 336 and
          index.get("schema") ==
          "i3-stage8f1n-scientific-first-only-owned-margin-native-T60/v0" and
          index.get("phase") == "F1N_HELDOUT_RELEASE" and
          index.get("preregistration_main_sha") == R.PREEXPOSURE_COMMIT and
          index.get("frozen_grid_blob") == R.GRID_BLOB and
          index.get("frozen_protocol_blob") == R.PROTOCOL_BLOB and
          index.get("source_policy") == "F1NMarginMind" and
          index.get("origin_ids") == R.ROOT_IDS and
          index.get("seeds") == R.SEEDS and
          index.get("arms") == R.ARMS and
          index.get("source_ticks") == 4 and
          index.get("confidence_record_tick") == 5 and
          index.get("paid_read_tick") == 6 and
          index.get("final_tick") == 60 and
          index.get("original_scientific_native_passes") == 1 and
          index.get("scientific_verdict") is None and
          index.get("no_motor_override") is True and
          claim["root_ids"] == index["origin_ids"] and
          manifest["reservation_sha256"] == E.digest(E.canonical(receipt)),
          "cold corpus not linked to exactly 48 one-shot claimed F1N roots")
    verdict = COLD.classify(rows)
    report = {
        "schema":"i3-stage8f1n-independent-scientific-cold-T60/v0",
        "phase":"F1N_HELDOUT_RELEASE",
        "source_preregistration_main":R.PREEXPOSURE_COMMIT,
        "source_git_commit":claim["head_sha"],
        "source_tree_sha":claim["rehearsal_verified_tree_sha"],
        "grid_git_blob":R.GRID_BLOB,"protocol_git_blob":R.PROTOCOL_BLOB,
        "scientific_run_id":claim["workflow_run_id"],
        "one_native_scientific_pass":True,
        "independent_roots_verified":count,
        "original_gzip_parts_verified":336,
        "reconstructed_World_steps":count_steps,
        "reconstructed_paid_F1J_rounds":count_rounds,
        "immutable_raw_release_custody":raw,
        "original_tar_sha256":manifest["original_tar_sha256"],
        "native_index_sha256":manifest["native_index_sha256"],
        "verdicts":verdict,"per_root":rows,
        "no_i3_World_or_Mind_import":True,
        "no_scientific_reexposure":True,
        "stage2":"NOT_ISSUED/HOLD_NO_VERDICT",
        "historical_F1L":"NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE",
        "historical_F1M":"NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE",
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    E.new_file(output_dir/"F1N_INDEPENDENT_COLD_T60.json",
               E.canonical(report) + b"\n")
    E.new_file(output_dir/"F1N_BYTE_CUSTODY_COLD.json",
               E.canonical({"schema":"i3-stage8f1n-independent-byte-custody/v0",
                            "claim_run":claim["workflow_run_id"],
                            "original_parts":336,
                            "source_not_reexecuted":True,**raw})+b"\n")
    print(json.dumps({"status":"F1N_INDEPENDENT_COLD_COMPLETE",
          "roots":count,"original_gzips":336,
          "native_steps":count_steps,"paid_rounds":count_rounds,
          "gate":verdict["status"],
          "motor":verdict.get("motor_verdict"),
          "adaptive":verdict.get("survival_verdict"),
          "body":verdict.get("body_verdict"),
          "source_not_reexecuted":True},sort_keys=True))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir",type=Path)
    parser.add_argument("output_dir",type=Path)
    args = parser.parse_args()
    run(args.input_dir,args.output_dir)


if __name__ == "__main__":
    main()