"""F1N terminal state: scientifically audited OR inconclusive and NO RETRY."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def publish(directory, cold_job_result):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory/"F1N_INDEPENDENT_COLD_T60.json"
    audited = cold_job_result == "success" and path.is_file()
    cold = json.loads(path.read_bytes()) if audited else None
    if cold is not None and not (
            cold.get("schema") ==
                "i3-stage8f1n-independent-scientific-cold-T60/v0" and
            cold.get("phase") == "F1N_HELDOUT_RELEASE" and
            cold.get("independent_roots_verified") == 48 and
            cold.get("original_gzip_parts_verified") == 336 and
            cold.get("one_native_scientific_pass") is True and
            cold.get("no_i3_World_or_Mind_import") is True and
            cold.get("verdicts",{}).get("status") in (
                "F1N_COMPLETE_SEPARATE_SCIENTIFIC_VERDICTS",
                "INCONCLUSIVE_PROVENANCE_OR_NATIVE_CUSTODY",
                "INCONCLUSIVE_PAID_SOURCE_OR_SHAM",
                "INCONCLUSIVE_REAL_DECISION_COST",
                "INCONCLUSIVE_INTERVENTION_SEPARATION")):
        raise ValueError("F1N cold report incomplete, invalid or unverified")
    status={
        "schema":"i3-stage8f1n-first-only-final-no-retry-status/v0",
        "one_scientific_allocation_consumed":True,
        "native_scientific_retry_permitted":False,
        "github_run_id":os.environ.get("GITHUB_RUN_ID"),
        "cold_job_result":cold_job_result,
        "scientific_status":("COLD_AUDITED_FIRST_ONLY" if audited else
                              "INCONCLUSIVE_COLD_AUDIT_MISSING_NO_RETRY"),
        "cold_verdicts":cold.get("verdicts") if audited else None,
        "F1M_immutable":"NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE",
        "F1L_immutable":"NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE",
        "stage2":"NOT_ISSUED/HOLD_NO_VERDICT",
        "i1_remains_active":True,
        "github_internal_release_not_external_escrow":True,
    }
    path=directory/"F1N_FINAL_STATUS.json"
    with path.open("xb") as output:
        output.write((json.dumps(status,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8"))
    return status


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dir",required=True)
    p.add_argument("--cold-job",required=True)
    x=p.parse_args()
    print(json.dumps(publish(x.dir,x.cold_job),sort_keys=True))


if __name__ == "__main__":
    main()
