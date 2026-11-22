"""F1L terminal no-retry publication status, even on cold/native failure."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def publish(directory, cold_job_result):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    source = directory / "F1L_INDEPENDENT_COLD_T60.json"
    verified = cold_job_result == "success" and source.is_file()
    cold = json.loads(source.read_bytes()) if verified else None
    if cold is not None and (
            cold.get("phase") != "F1L_HELDOUT_RELEASE"
            or cold.get("roots") != 32
            or cold.get("cold_status") != "COLD_VERIFIED_32_FIRST_ONLY"):
        raise ValueError("cannot publish a truncated cold result as verified")
    result = {
        "schema": "i3-stage8f1l-final-no-scientific-retry-status/v0",
        "one_scientific_allocation_consumed": True,
        "scientific_native_retry_permitted": False,
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "cold_job_result": cold_job_result,
        "scientific_status": (
            "COLD_AUDITED_LOCAL_RESULT" if verified
            else "INCONCLUSIVE_COLD_AUDIT_MISSING_NO_RETRY"),
        "cold_verdict": cold["cold_verdict"] if verified else None,
        "F1I_immutable": "INCONCLUSIVE_COST_GATE",
        "F1K_immutable": "INCONCLUSIVE_NO_REAL_SURCHARGE",
        "stage2": "NOT_ISSUED/HOLD_NO_VERDICT",
        "i1_remains_active": True,
        "github_release_not_external_escrow": True,
    }
    with (directory / "F1L_FINAL_STATUS.json").open("xb") as out:
        out.write((json.dumps(result, sort_keys=True,
                              separators=(",", ":")) + "\n").encode("utf-8"))
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", type=Path, required=True)
    p.add_argument("--cold-job", required=True)
    args = p.parse_args()
    print(json.dumps(publish(args.dir, args.cold_job), sort_keys=True))


if __name__ == "__main__":
    main()
