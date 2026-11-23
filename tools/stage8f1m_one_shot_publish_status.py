"""Terminal status for the F1M one-shot, including inconclusive no-retry."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def publish(directory,cold_job_result):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    source=directory/"F1M_INDEPENDENT_COLD_T60.json"
    verified=cold_job_result=="success" and source.is_file()
    cold=json.loads(source.read_bytes()) if verified else None
    if cold is not None and (
            cold.get("phase")!="F1M_HELDOUT_RELEASE"
            or cold.get("roots_verified")!=32
            or cold.get("original_part_gzips_sha256_verified")!=384
            or cold.get("one_native_scientific_pass") is not True
            or cold.get("no_world_or_mind_import") is not True
            or cold.get("verdicts",{}).get("status") not in (
                "F1M_COMPLETE_SEPARATE_SCIENTIFIC_VERDICTS",
                "INCONCLUSIVE_PROVENANCE_OR_NATIVE_CUSTODY",
                "INCONCLUSIVE_PAID_SOURCE_OR_SHAM",
                "INCONCLUSIVE_REAL_DECISION_COST")):
        raise ValueError("unverified or incomplete F1M cold verdict")
    verdict=cold.get("verdicts") if verified else None
    status={
        "schema":"i3-stage8f1m-first-only-final-no-retry-status/v0",
        "one_scientific_allocation_consumed":True,
        "native_scientific_retry_permitted":False,
        "github_run_id":os.environ.get("GITHUB_RUN_ID"),
        "cold_job_result":cold_job_result,
        "scientific_status":("COLD_AUDITED_FIRST_ONLY" if verified
                             else "INCONCLUSIVE_COLD_AUDIT_MISSING_NO_RETRY"),
        "cold_verdicts":verdict,
        "F1L_immutable":"NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE",
        "stage2":"NOT_ISSUED/HOLD_NO_VERDICT",
        "i1_remains_active":True,
        "github_internal_release_not_external_escrow":True,
    }
    with (directory/"F1M_FINAL_STATUS.json").open("xb") as out:
        out.write((json.dumps(status,sort_keys=True,
                              separators=(",",":"))+"\n").encode("utf-8"))
    return status


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dir",type=Path,required=True)
    p.add_argument("--cold-job",required=True)
    a=p.parse_args()
    print(json.dumps(publish(a.dir,a.cold_job),sort_keys=True))


if __name__=="__main__":
    main()
