"""Publish an explicit F1K cold status, including failures, without re-running K."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def publish(directory: Path, cold_job_result: str):
    directory.mkdir(parents=True, exist_ok=True)
    proof = directory / "F1K_INDEPENDENT_COLD_T60.json"
    passed = cold_job_result == "success" and proof.is_file()
    cold = json.loads(proof.read_bytes()) if passed else None
    if cold is not None and (cold["phase"] != "F1K_HELDOUT_RELEASE"
                             or cold["all_16_origins_retained"] is not True):
        raise ValueError("cannot label incomplete cold result verified")
    status = {
        "schema": "i3-stage8f1k-final-no-retry-status/v0",
        "original_scientific_allocation_consumed": True,
        "native_repeat_after_run_permitted": False,
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "cold_job_result": cold_job_result,
        "scientific_status": ("COLD_AUDITED_LOCAL_RESULT"
                              if passed else
                              "INCONCLUSIVE_COLD_AUDIT_MISSING_NO_RETRY"),
        "cold_verdict": cold["cold_verdict"] if passed else None,
        "historical_f1i": "INCONCLUSIVE_COST_GATE",
        "historical_f1j": "FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL",
        "stage2": "NOT_ISSUED/HOLD_NO_VERDICT",
        "i1_remains_active": True,
        "no_claim_of_external_custody": True,
    }
    out = directory / "F1K_FINAL_STATUS.json"
    with out.open("xb") as stream:
        stream.write((json.dumps(status,sort_keys=True,
                                 separators=(",",":"))+"\n").encode("utf-8"))
    return status


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir",type=Path,required=True)
    ap.add_argument("--cold-job",required=True)
    args=ap.parse_args()
    print(json.dumps(publish(args.dir,args.cold_job),sort_keys=True))


if __name__=="__main__":
    main()
