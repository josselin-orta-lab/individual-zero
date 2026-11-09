"""ADR-0017 two-phase panel execution and sealed rehearsal.

Phase G generates every planned life, in the frozen order, and archives each
original immediately (deterministic gzip and SHA-256). Nothing is reduced,
aggregated or ruled on during G. A generation exception is an engineering
failure: stop, archive, no retry.

Phase R then reads only the sealed originals, after re-verifying every digest.
A reduction exception yields `REDUCTION_DEFECT_PENDING_REPAIR`: the panel is
not closed and no partial result is returned. The failure receipt is
structural only.

A sealed rehearsal runs the same G and R on engineering worlds and returns
pipeline status, counts, digests, invariants and time per step. It never
returns the reduced rows.
"""
from __future__ import annotations

import gzip
from hashlib import sha256
import json
from pathlib import Path
import tempfile

SCHEMA = "i3-two-phase-panel/v1"


def _dump(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def generate(cases, run_case, archive_dir) -> dict:
    """Phase G. Returns the sealed manifest, also written to MANIFEST.json."""
    root = Path(archive_dir)
    root.mkdir(parents=True, exist_ok=True)
    files, status, failure = [], "GENERATED", None
    for i, case in enumerate(cases):
        try:
            life = run_case(case)
        except Exception as exc:
            status = "ENGINEERING_FAILURE_NOT_A_DEATH"
            failure = {"case_index": i, "case": case,
                       "error_type": type(exc).__name__, "error": str(exc),
                       "completed": i, "no_retry": True}
            break
        raw = _dump({"identity": case, "life": life})
        packed = gzip.compress(raw, mtime=0)
        name = f"life-{i:03d}.json.gz"
        (root / name).write_bytes(packed)
        files.append({"file": name, "sha256": sha256(packed).hexdigest(),
                      "uncompressed_sha256": sha256(raw).hexdigest(),
                      "identity": case})
    manifest = {"schema": SCHEMA, "status": status, "planned": len(cases),
                "generated": len(files), "files": files, "failure": failure}
    body = _dump(manifest)
    (root / "MANIFEST.json").write_bytes(body)
    (root / "MANIFEST.sha256").write_text(sha256(body).hexdigest() + "\n")
    return manifest


def load_sealed(archive_dir):
    """Re-verify the manifest and every original; yield (identity, life)."""
    root = Path(archive_dir)
    body = (root / "MANIFEST.json").read_bytes()
    if sha256(body).hexdigest() != (root / "MANIFEST.sha256").read_text().strip():
        raise ValueError("sealed manifest digest mismatch")
    manifest = json.loads(body)
    if manifest["status"] != "GENERATED" or manifest["generated"] != manifest["planned"]:
        raise ValueError("phase G did not complete; nothing may be reduced")
    for row in manifest["files"]:
        packed = (root / row["file"]).read_bytes()
        if sha256(packed).hexdigest() != row["sha256"]:
            raise ValueError(f"original digest mismatch: {row['file']}")
        raw = gzip.decompress(packed)
        if sha256(raw).hexdigest() != row["uncompressed_sha256"]:
            raise ValueError(f"uncompressed digest mismatch: {row['file']}")
        payload = json.loads(raw)
        if payload["identity"] != row["identity"]:
            raise ValueError(f"identity mismatch: {row['file']}")
        yield payload["identity"], payload["life"]


def reduce(archive_dir, reducer) -> dict:
    """Phase R. All rows, or a structural repair receipt and no rows."""
    rows = []
    for i, (identity, life) in enumerate(load_sealed(archive_dir)):
        try:
            rows.append(reducer(identity, life))
        except Exception as exc:
            return {"status": "REDUCTION_DEFECT_PENDING_REPAIR",
                    "failure": {"record_index": i,
                                "error_type": type(exc).__name__,
                                "error": str(exc)}}
    return {"status": "COMPLETE", "rows": rows}


def sealed_rehearsal(cases, run_case, reducer, invariants) -> dict:
    """Run G and R on engineering cases; return pipeline facts only."""
    with tempfile.TemporaryDirectory() as tmp:
        g = generate(cases, run_case, tmp)
        report = {"schema": SCHEMA + "/sealed-rehearsal", "planned": len(cases),
                  "phase_G": g["status"], "generated": g["generated"],
                  "generation_failure": (
                      {k: g["failure"][k] for k in ("case_index", "error_type", "error")}
                      if g["failure"] else None)}
        if g["status"] != "GENERATED":
            report.update(phase_R=None, reduced=0, status="FAIL")
            return report
        r = reduce(tmp, reducer)
        failures, step_ms = {}, []
        for identity, life in load_sealed(tmp):
            for name, ok in invariants(identity, life).items():
                failures[name] = failures.get(name, 0) + (not ok)
            step_ms.append(life.get("mean_step_ms", 0.0))
        manifest_sha = (Path(tmp) / "MANIFEST.sha256").read_text().strip()
        report.update(
            phase_R=r["status"],
            reduced=len(r.get("rows", [])),
            reduction_failure=r.get("failure"),
            invariant_failures=failures,
            manifest_sha256=manifest_sha,
            mean_step_ms=(sum(step_ms) / len(step_ms)) if step_ms else None,
            status=("PASS" if r["status"] == "COMPLETE"
                    and not any(failures.values()) else "FAIL"))
        return report
