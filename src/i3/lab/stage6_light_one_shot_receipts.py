"""One-shot Stage6 GitHub workflow receipts and source-exact custody bindings.

No new World, no native life and no trial selection here. This read-only
module checks output facts; it is NOT a separate permission to start research.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys

from i3.lab import stage6_light_native_gsr_transport as S


def _json_file(path: Path) -> dict:
    v = json.loads(path.read_text(encoding="utf-8"))
    if type(v) is not dict:
        raise ValueError("expected a single JSON object")
    return v


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _phase_check(root: Path, expected_sha: str) -> None:
    path = root / "PHASES.jsonl"
    lines = path.read_bytes().splitlines()
    if len(lines) != len(S.PHASES):
        raise ValueError("not exactly nine completed G/S/R phases")
    previous = None
    for i, raw in enumerate(lines):
        row = json.loads(raw)
        if (type(row) is not dict or
                set(row) != {"ordinal", "phase", "payload_sha256",
                             "previous_sha256", "chain_sha256"} or
                row["ordinal"] != i or
                row["phase"] != S.PHASES[i] or
                row["previous_sha256"] != previous):
            raise ValueError("phase order or predecessor digest differs")
        chain = row["chain_sha256"]
        if type(chain) is not str or chain != S._sha({
            k: v for k, v in row.items() if k != "chain_sha256"}):
            raise ValueError("phase chain digest failed")
        previous = chain
    if previous != expected_sha:
        raise ValueError("final stage chain head differs from native runtime receipt")


def engineering_receipt(plan_file: str, originals: str, core_file: str,
                        version: str, run_id: int) -> dict:
    p = S.verify_plan(_json_file(Path(plan_file)))
    if version not in ("3.11", "3.12"):
        raise ValueError("full engineering rehearsal must be Python 3.11/3.12")
    root = Path(originals).resolve()
    if str(root) != p["archive_root"] or not root.is_dir():
        raise ValueError("archive does not match fixed prospective path")
    if (root / "FAILURE.json").exists():
        raise ValueError("failed engineering original may not create a PASS receipt")
    output = _json_file(Path(core_file))
    report_path = root / "R_FINAL_ENGINEERING.json"
    report = _json_file(report_path)
    _phase_check(root, output["last_chain_sha256"])
    if (output.get("status") != "ENGINEERING_FULL_GSR_REHEARSAL_NO_SCIENCE"
            or output.get("allocation_sha256") != p["allocation_sha256"]
            or output.get("source_git_head") != p["source_git_head"]
            or output.get("science_admission") is not False
            or output.get("no_retry") is not True
            or output.get("lives_archived") != 11520
            or report.get("status") != output["status"]
            or report.get("original_lives") != 11520
            or report.get("scientific_admission") is not False
            or report.get("science_decision_disclosed") is not False
            or not S.G0.DIGEST.fullmatch(report.get("reduction_sha256", ""))):
        raise ValueError("incomplete or science-leaking full rehearsal")
    seals = report.get("generation_seals", [])
    if (type(seals) is not list or len(seals) != 3
            or [s["generation"] for s in seals] != [0, 1, 2]
            or [s["lives"] for s in seals] != [2304, 4608, 4608]):
        raise ValueError("missing G0/G1/G2 native original seals")
    for g in range(3):
        path = root / f"G{g}" / "MANIFEST.json"
        if not path.is_file() or _sha(path) != seals[g]["seal_sha256"]:
            raise ValueError("generation archive seal disappeared after G/S/R")
    if type(run_id) is not int or run_id <= 0:
        raise ValueError("GitHub workflow run identifier missing")
    return {
        "schema": "i3-stage6-rehearsal-receipt/v1",
        "status": output["status"], "python_version": version,
        "source_git_head": p["source_git_head"],
        "source_files_sha256": p["source_files_sha256"],
        "allocation_sha256": p["allocation_sha256"],
        "last_chain_sha256": output["last_chain_sha256"],
        "lives_archived": output["lives_archived"],
        "planned_worlds": 288, "phase_count": 9,
        "archive_sha256": _sha(report_path),
        "reduction_sha256": report["reduction_sha256"],
        "science_admission": False, "no_retry": True,
        "workflow_run_id": run_id,
        "job_name": f"engineering-{version}",
    }


def combine_rehearsal_receipts(artifacts_311: str,
                               artifacts_312: str) -> dict:
    r = {"3.11": _json_file(Path(artifacts_311)),
         "3.12": _json_file(Path(artifacts_312))}
    S._check_rehearsals(r, r["3.11"]["source_git_head"],
                        r["3.11"]["source_files_sha256"])
    return r


def science_completion(plan_file: str, originals: str,
                       core_file: str) -> dict:
    p = S.verify_science_plan(_json_file(Path(plan_file)))
    root = Path(originals).resolve()
    if str(root) != p["archive_root"] or not root.is_dir():
        raise ValueError("scientific archive must match fixed published plan")
    if (root / "FAILURE.json").exists():
        raise ValueError("failed science source cannot issue a verdict")
    core = _json_file(Path(core_file))
    final = _json_file(root / "R_FINAL_SCIENCE.json")
    _phase_check(root, core["last_chain_sha256"])
    science = final.get("frozen_analysis", {})
    if (core.get("status") not in
            ("STAGE6_LIGHT_INVALID", "STAGE6_LIGHT_SIGN_CONCORDANCE_PASS",
             "STAGE6_LIGHT_NO_SIGN_CONCORDANCE")
            or core.get("status") != final.get("status")
            or science.get("status") != final.get("status")
            or core.get("science_admission") is not True
            or core.get("allocation_sha256") != p["allocation_sha256"]
            or core.get("lives_archived") != 11520
            or final.get("original_lives") != 11520
            or final.get("scientific_admission") is not True
            or final.get("preexposure_allocation_sha256") != p["allocation_sha256"]
            or final.get("source_git_head") != p["source_git_head"]
            or science.get("threshold") != 13
            or science.get("populations") != 16):
        raise ValueError("scientific result not source/plan/analysis bound")
    contrasts = science.get("contrast", {})
    if set(contrasts) != {
        "beta_u_eff", "omega", "temperament.affiliation",
        "temperament.reward_sensitivity"}:
        raise ValueError("missing primary or negative controls")
    for item in contrasts.values():
        if (len(item["values"]) != 16 or
                sum(item[k] for k in ("plus", "minus", "zero")) != 16):
            raise ValueError("missing population contrasts or zero sign custody")
    neutral_count = sum(contrasts[k]["direction_concordant"] for k in
                        ("omega", "temperament.affiliation",
                         "temperament.reward_sensitivity"))
    if (science.get("neutral_marker_alert_count") != neutral_count or
            science.get("neutral_marker_alert") is not (neutral_count >= 1) or
            science.get("invalid_neutral_markers") is not (neutral_count >= 2) or
            science.get("two_sided_sign_null") != {
                "numerator": 1394, "denominator": 65536,
                "requires": "INDEPENDENT_SYMMETRIC_NONZERO_SIGNS_NOT_PROVEN"}):
        raise ValueError("neutral alert or frozen two-sided null was modified")
    bridge = final.get("native_original_selection_audit", {})
    if bridge.get("original_lives_structurally_checked") != 11520:
        raise ValueError("native original bridge not complete")
    return {
        "schema": "i3-stage6-light-internal-prospective-result/v1",
        "status": final["status"],
        "scientific_scope": p["science_scope"],
        "original_native_lives": 11520,
        "independent_population_units": 16,
        "source_git_head": p["source_git_head"],
        "plan_sha256": p["allocation_sha256"],
        "science_original_sha256": _sha(root / "R_FINAL_SCIENCE.json"),
        "phase_chain_sha256": core["last_chain_sha256"],
        "result": science,
        "provenance": "INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED",
        "stage2_scientific_verdict": "NOT_ISSUED",
        "all_null_and_adverse_originals_retained": True,
        "external_authentication_claimed": False,
    }


def _write_new(path: str, item: dict) -> None:
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(item, f, sort_keys=True, indent=2)
        f.write("\n")


def main() -> None:
    args = sys.argv
    if len(args) == 8 and args[1] == "rehearsal":
        _, _, plan, root, core, dest, version, run = args
        r = engineering_receipt(plan, root, core, version, int(run))
        _write_new(dest, r)
        print(json.dumps({"status": r["status"],
                          "python_version": version,
                          "lives_archived": 11520,
                          "receipt_sha256": _sha(Path(dest))}, sort_keys=True))
    elif len(args) == 5 and args[1] == "combine":
        r = combine_rehearsal_receipts(args[2], args[3])
        _write_new(args[4], r)
        print(json.dumps({"status": "TWO_FULL_REHEARSALS_VERIFIED",
                          "rehearsals_sha256": _sha(Path(args[4]))}))
    elif len(args) == 6 and args[1] == "science":
        _, _, plan, root, core, dest = args
        r = science_completion(plan, root, core)
        _write_new(dest, r)
        print(json.dumps({"status": r["status"],
                          "population_units": 16,
                          "primary_signs": {
                              k: r["result"]["contrast"]["beta_u_eff"][k]
                              for k in ("plus", "minus", "zero")},
                          "result_sha256": _sha(Path(dest))}, sort_keys=True))
    else:
        raise SystemExit("usage: rehearsal PLAN ROOT CORE OUT PYVERSION RUN_ID | combine RECEIPT311 RECEIPT312 OUT | science PLAN ROOT CORE OUT")


if __name__ == "__main__":
    main()
