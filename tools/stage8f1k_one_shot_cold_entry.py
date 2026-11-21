"""F1K independent cold entrypoint. Python 3.12 stdlib only; no native engine."""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from tools import stage8f1k_one_shot_reservation as R
from tools import stage8f1k_one_shot_evidence as E
from tools import stage8f1k_independent_policy_value_cold_audit as C
from tools import stage8f1c_independent_postaction_audit as I

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input_dir",type=Path)
    ap.add_argument("output_dir",type=Path)
    args=ap.parse_args()
    # This is the ACTUAL remote GitHub ref and immutable-intent source SHA,
    # not only a locally copied claim or a self-signed report.
    receipt=R.load_receipt(args.input_dir/"F1K_RESERVATION.json")
    claim=R.verify_remote(receipt)
    root=args.input_dir/"f1k-originals"
    proof=E.verify_bundle(root)
    case_index=json.loads((root/"F1K_CUSTODY_MANIFEST.json").read_bytes())
    if case_index.get("reservation_sha256")!=E.digest(E.canonical(receipt)):
        raise ValueError("raw native custody is not bound to the original pre-step GitHub claim")
    if (proof["phase"]!="F1K_HELDOUT_RELEASE" or
            proof["roots"]!=16 or proof["original_native_gzips"]!=64):
        raise ValueError("scientific release incomplete despite source consumption")
    original=gzip.decompress((root/"F1K_ORIGINAL_NATIVE.json.gz").read_bytes())
    report=json.loads(original)
    grid_bytes=Path(R.GRID_PATH).read_bytes()
    protocol_bytes=Path(R.PROTOCOL_PATH).read_bytes()
    cold=C.audit(report,json.loads(grid_bytes),
                 grid_bytes=grid_bytes,protocol_bytes=protocol_bytes)
    if (cold["original_sha256"]!=E.digest(original)
            or cold["phase"]!="F1K_HELDOUT_RELEASE"
            or cold["all_16_origins_retained"] is not True
            or cold["preexposure_blobs_verified"] is not True
            or claim["head_sha"]!=receipt["claim"]["head_sha"]):
        raise ValueError("cold native proof and original reservation do not reconcile")
    args.output_dir.mkdir(parents=True,exist_ok=False)
    E.new_file(args.output_dir/"F1K_BYTE_CUSTODY_COLD.json",E.canonical(proof)+b"\n")
    E.new_file(args.output_dir/"F1K_INDEPENDENT_COLD_T60.json",I.c(cold))
    print(json.dumps({
        "status":"F1K_COLD_INDEPENDENT_SIXTEEN_GZIP_PASS",
        "verdict":cold["cold_verdict"],"original":cold["original_sha256"],
        "paid_native_steps":cold["native_paid_steps_verified"],
        "native_rounds":cold["competition_rounds_verified"],
        "not_a_stage2_promotion":True,
    },sort_keys=True))

if __name__=="__main__":
    main()
