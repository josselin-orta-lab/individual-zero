"""Read-only SHA-pinned reanalysis of the already sealed three-arm 64-unit lives.

No Mind, World, genotype generation, physics step or original write. The
archived source is a consumed one-shot. This verifier independently checks
every existing G original packed and unpacked SHA via two_phase_panel,
re-reduces the same original rows and reproduces all finite contrasts.
A source pin supplied by a repository is not an independent external
attestation of iid ecology, experiment independence, or scientific GO.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from . import stage2_three_arm_development as STUDY
from . import two_phase_panel as TP

SCHEMA = "i3-three-arm-64-original-read-only-reanalysis/v1"
SOURCE_SHA = "11879c46a78697aa1d3f664f1a17f489a948667d"
FINGERPRINT = "37989805cadf6502e105e500e25a656e7898e4873a21f4d51b283c42c6754327"
PLAN_SHA = "585dd83dff80bcfc9b0014db929113f84f8c8d41938749fea39f4052a61e43ae"
MANIFEST_SHA = "f493a30598c3dd82f56ab84653537286487bea61414cfc2226785209c724a50f"
UNITS = 64
LIVES = 192


def verify(archive_path) -> dict:
    root = Path(archive_path)
    if not root.is_dir() or not (root / "originals").is_dir():
        raise ValueError("missing original evidence directory; no fabricated results")
    if sha256(STUDY.PLAN.read_bytes()).hexdigest() != PLAN_SHA:
        raise ValueError("prospective frozen plan changed")
    source = json.loads((root / "SOURCE_LOCK.json").read_bytes())
    expected_lock = {
        "schema": STUDY.SCHEMA + "/source-claim",
        "status": "CONSUMED_BEFORE_FIRST_BIRTH",
        "source_sha": SOURCE_SHA,
        "source_fingerprint": FINGERPRINT,
        "plan_sha256": PLAN_SHA,
        "claim_branch": STUDY.CLAIM_BRANCH,
        "evidence_branch": STUDY.EVIDENCE_BRANCH,
        "units": UNITS, "lives": LIVES,
        "no_retry": True, "scientific_inference_authorized": False,
    }
    if source != expected_lock:
        raise ValueError("original source lock differs from consumed claim")
    raw = (root / "originals" / "MANIFEST.json").read_bytes()
    if sha256(raw).hexdigest() != MANIFEST_SHA:
        raise ValueError("historically pinned original manifest SHA mismatch")
    manifest = json.loads(raw)
    if not (manifest["status"] == "GENERATED"
            and manifest["planned"] == manifest["generated"] == LIVES
            and manifest["failure"] is None
            and len(manifest["files"]) == LIVES):
        raise ValueError("incomplete original G; no partial survival verdict")
    reported = json.loads((root / "EXECUTION_REPORT.json").read_bytes())
    if any(reported.get(k) != expected for k, expected in (
            ("status","COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY"),
            ("source_sha",SOURCE_SHA), ("source_fingerprint",FINGERPRINT),
            ("plan_sha256",PLAN_SHA), ("planned",LIVES),
            ("generated",LIVES), ("reduced",LIVES),
            ("phase_G","GENERATED"), ("phase_R","COMPLETE"),
            ("scientific_verdict","NOT_ISSUED"))):
        raise ValueError("original G/R execution report differs from frozen source")
    stored_rows = json.loads((root / "REDUCED_ROWS.json").read_bytes())
    if type(stored_rows) is not list or len(stored_rows) != LIVES:
        raise ValueError("incomplete archived Phase-R rows")
    expected_cases = STUDY.cases()
    if len(expected_cases) != LIVES:
        raise ValueError("original schedule changed")
    reconstructed = []
    # TP.load_sealed re-verifies manifest SHA, all gzip SHA-256, all
    # decompressed SHA-256 and all raw original identity records.
    for i, (identity, life) in enumerate(TP.load_sealed(root / "originals")):
        if identity != expected_cases[i] or manifest["files"][i]["identity"] != identity:
            raise ValueError("reassigned/corrupted original identity/order")
        m = life["manifest"]
        if (m["source"].get("git_head") != SOURCE_SHA or
                m["source"].get("working_tree_dirty") is not False):
            raise ValueError("original executable source not exact and clean")
        if m["world_sha256"] != life["admission_receipt"]["world_sha256"]:
            raise ValueError("source-bound original World differs")
        reconstructed.append(STUDY._reduce_row(identity, life, FINGERPRINT))
    if len(reconstructed) != LIVES or reconstructed != stored_rows:
        raise ValueError("original reductions differ from archived complete rows")
    reread = STUDY.analyze(expected_cases, reconstructed)
    if reread != reported["analysis"]:
        raise ValueError("exact archival finite result does not match original analysis")
    primary = reread["overall_contrasts"]["GATE_MINUS_RANDOM"]
    if (primary["units"] != UNITS or primary["both_survive"] != 23 or
            primary["target_only_survives"] != 4 or
            primary["comparator_only_survives"] != 4 or
            primary["neither_survives"] != 33):
        raise ValueError("canonical original GATE/RANDOM discordances changed")
    return {
        "schema": SCHEMA,
        "status": "ORIGINAL_192_OF_192_REVERIFIED_READ_ONLY",
        "source_sha": SOURCE_SHA,
        "source_fingerprint": FINGERPRINT,
        "plan_sha256": PLAN_SHA,
        "manifest_sha256": MANIFEST_SHA,
        "originals_checked": len(reconstructed),
        "matched_units": UNITS,
        "primary": "GATE_MINUS_RANDOM",
        "gate_only_survivors": 4,
        "random_only_survivors": 4,
        "both_survive": 23,
        "neither_survive": 33,
        "observed_primary_paired_risk_difference": 0.0,
        "independent_iid_verified": False,
        "survival_noninferiority_established": False,
        "scientific_verdict": "NOT_ISSUED",
        "worlds_executed_by_verifier": 0,
        "lives_executed_by_verifier": 0,
    }


def main(argv=None):
    argv = sys.argv if argv is None else argv
    if len(argv) != 2:
        raise SystemExit("usage: python -m i3.lab.stage2_three_arm_original_reanalysis ARCHIVED_EVIDENCE_DIR")
    print(json.dumps(verify(argv[1]),sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
