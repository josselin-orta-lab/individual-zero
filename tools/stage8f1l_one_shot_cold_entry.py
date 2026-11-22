"""Independent F1L scientific cold entry: 128 originals, genuine remote claim.

Python 3.12 stdlib only. No import of F1L producer, i3 engine or World.
"""
from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path

from tools import stage8f1l_one_shot_reservation as R
from tools import stage8f1l_one_shot_evidence as E
from tools import stage8f1l_independent_scientific_cold as Cold



RAW_RELEASE_TAG = "i3-stage8f1l-t60-raw-heldout-once"


def verify_immutable_raw_release(receipt, input_dir):
    """Independently compare ALL protected release asset digests with downloaded originals.

    This must run BEFORE scientific cold analysis. GitHub's immutable release
    retains the source bytes even when temporary Actions artifacts expire.
    It is GitHub-internal custody, NOT an external escrow.
    """
    claim_commit = receipt["reservation_commit"]
    release = R._api("GET", "/releases/tags/" + RAW_RELEASE_TAG)
    if (release.get("immutable") is not True
            or release.get("tag_name") != RAW_RELEASE_TAG
            or release.get("target_commitish") != claim_commit):
        raise ValueError("F1L original Release is absent, mutable or points to a different claim")
    paths = [
        input_dir / "F1L_RESERVATION.json",
        input_dir / "F1L_RESERVATION.NATIVE_START_LOCK",
    ]
    paths += sorted((input_dir / "f1l-originals").glob("F1L_*"))
    paths += sorted((input_dir / "f1l-preservation").glob("F1L_*"))
    expected = {p.name: p for p in paths if p.is_file()}
    if (len(expected) != len(paths)
            or len(expected) < 7
            or not (input_dir / "f1l-originals/F1L_ORIGINALS_128_GZIP.tar.gz").is_file()):
        raise ValueError("original raw source file missing or colliding asset names")
    assets = release.get("assets", [])
    got = {a.get("name"): a for a in assets}
    if len(assets) != len(got) or set(got) != set(expected):
        raise ValueError("immutable raw release lacks an original or contains extra evidence")
    for name, path in expected.items():
        raw = path.read_bytes()
        asset = got[name]
        if (asset.get("digest") != "sha256:" + sha256(raw).hexdigest()
                or asset.get("size") != len(raw)):
            raise ValueError("immutable release SHA256 differs from native evidence: " + name)
    return {
        "release_tag": RAW_RELEASE_TAG,
        "release_target_commit": claim_commit,
        "release_immutable": True,
        "raw_assets_byte_matched": len(expected),
        "independent_github_asset_digest_gate": True,
    }



def verify(input_dir, output_dir):
    receipt = R.load_receipt(input_dir / "F1L_RESERVATION.json")
    # Independent job; the claim's immutable run ID is validated below.
    claim = R.verify_remote(receipt, same_run=False)
    raw_release_proof = verify_immutable_raw_release(receipt, input_dir)
    lock = json.loads((input_dir / "F1L_RESERVATION.NATIVE_START_LOCK").read_bytes())
    expected = {
        "schema": "i3-stage8f1l-first-native-exposure-lock/v0",
        "reservation_run_id": claim["workflow_run_id"],
        "reserved_source_sha": claim["head_sha"],
        "origin_ids": R.ROOT_IDS,
        "no_native_second_attempt": True,
    }
    if lock != expected:
        raise ValueError("F1L original native source not locked BEFORE first birth")
    root = input_dir / "f1l-originals"
    proof = E.verify_bundle(root)
    index = json.loads((root / "F1L_CUSTODY_MANIFEST.json").read_bytes())
    if index.get("reservation_sha256") != E.digest(E.canonical(receipt)):
        raise ValueError("128 native gzip archive is detached from the first-only claim")
    if (proof["phase"] != "F1L_HELDOUT_RELEASE"
            or proof["roots"] != 32
            or proof["original_native_gzips"] != 128
            or proof["same_bytes_technical_reproduction"] is not False
            or proof["same_bytes_canonical_readback"] is not True
            or proof["heldout_native_passes"] != 1):
        raise ValueError("missing original part or second native pass concealed")
    original = gzip.decompress(
        (root / "F1L_ORIGINAL_NATIVE.json.gz").read_bytes())
    report = json.loads(original)
    cold = Cold.audit(report)
    if (cold["original_sha256"] != E.digest(original)
            or cold["phase"] != "F1L_HELDOUT_RELEASE"
            or cold["roots"] != 32
            or cold["preregistered_blobs_and_controller_verified"] is not True
            or claim["root_ids"] != report["origin_ids"]):
        raise ValueError("cold decoded originals do not match source/claim")
    output_dir.mkdir(parents=True, exist_ok=False)
    E.new_file(output_dir / "F1L_BYTE_CUSTODY_COLD.json",
               E.canonical({**proof, **raw_release_proof}) + b"\n")
    E.new_file(output_dir / "F1L_INDEPENDENT_COLD_T60.json",
               E.canonical(cold) + b"\n")
    print(json.dumps({
        "status": "F1L_FIRST_ONLY_128_GZIP_ENGINE_FREE_COLD_COMPLETE",
        "scientific_verdict": cold["cold_verdict"],
        "origins": cold["roots"],
        "native_steps": cold["native_world_steps_verified"],
        "substantive_rounds": cold["substantive_competition_rounds_verified"],
        "paid_sources": cold["personal_paid_sources_verified"],
        "equal_T5_cost": cold["T5_equal_real_decision_cost_pairs"],
        "survival_gains": cold["survival_gain_count"],
        "survival_losses": cold["survival_loss_count"],
        "original_sha256": cold["original_sha256"],
        "immutable_raw_release_assets_verified": raw_release_proof["raw_assets_byte_matched"],
    }, sort_keys=True))
    return cold


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input_dir", type=Path)
    p.add_argument("output_dir", type=Path)
    args = p.parse_args()
    verify(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
