"""Independent F1L scientific cold entry: 128 originals, genuine remote claim.

Python 3.12 stdlib only. No import of F1L producer, i3 engine or World.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from tools import stage8f1l_one_shot_reservation as R
from tools import stage8f1l_one_shot_evidence as E
from tools import stage8f1l_independent_scientific_cold as Cold


def verify(input_dir, output_dir):
    receipt = R.load_receipt(input_dir / "F1L_RESERVATION.json")
    # Independent job; the claim's immutable run ID is validated below.
    claim = R.verify_remote(receipt, same_run=False)
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
               E.canonical(proof) + b"\n")
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
