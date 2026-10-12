"""Operator development campaign for SQLite-owned Stage10/11 mortal lives.

Use only fresh disposable individuals and real, committed physical steps.
Each life is split across independently spawned Python processes so the
resumption API must restore the sole latest committed generation. This
campaign cannot certify Stage12, external physical truth or operator signoff.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from lab.sqlite_life_store import SQLiteLifeLedger

ROOT = Path(__file__).resolve().parents[1]
TRIAL = ROOT / "scripts" / "run_m11_transactional_trial.py"
AUDIT = ROOT / "scripts" / "audit_i0_sqlite.py"
STAGES = ("stage10", "stage11")


def _process(script: Path, args: list[str], timeout_seconds: int) -> dict:
    child = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT, capture_output=True, text=True,
        timeout=timeout_seconds, check=False,
    )
    if child.returncode != 0:
        raise RuntimeError(
            f"{script.name} exited {child.returncode}: "
            f"{child.stderr[-1500:]} {child.stdout[-300:]}"
        )
    try:
        data = json.loads(child.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{script.name}: invalid JSON receipt") from exc
    if type(data) is not dict:
        raise RuntimeError(f"{script.name}: unexpected receipt type")
    return data


def _save_report(path: Path, report: dict) -> None:
    source = dict(report)
    source.pop("evidence_sha256", None)
    raw = json.dumps(
        source, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    payload = dict(source)
    payload["evidence_sha256"] = hashlib.sha256(raw).hexdigest()
    partial = path.with_suffix(".tmp")
    with partial.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    partial.replace(path)


def _git_head() -> str:
    command = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT,
        text=True, capture_output=True, check=True, timeout=20,
    )
    return command.stdout.strip()


def run_campaign(*, output: Path, total: int, per_life: int,
                 batch: int, max_births: int) -> dict:
    if total < 2 or total % len(STAGES):
        raise ValueError("target steps must be a positive even integer")
    if not 1 <= batch <= per_life <= 600:
        raise ValueError("invalid batch or per-life physical-step cap")
    if max_births < 1:
        raise ValueError("positive birth bound required")
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    lives_dir = output / "lives"
    lives_dir.mkdir()
    report_path = output / "manifest.json"
    report = {
        "schema": "m11-sqlite-operator-development-campaign-v1",
        "source_sha": _git_head(),
        "python_version": platform.python_version(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "software_development_hypothesis_only",
        "normative_target": "mvp-specification-v1.3.1/M-11",
        "supported_runtimes": list(STAGES),
        "stage12_atomic_recovery_certified": False,
        "operator_acceptance": None,
        "scientific_validation": None,
        "requested_physical_steps": total,
        "physical_steps": 0,
        "by_runtime": {name: 0 for name in STAGES},
        "births": 0,
        "terminal_deaths": 0,
        "cold_process_resumptions": 0,
        "lives": [],
        "errors": [],
    }
    started = time.monotonic()
    _save_report(report_path, report)
    target_per_stage = total // len(STAGES)
    try:
        for stage in STAGES:
            stage_births = 0
            while report["by_runtime"][stage] < target_per_stage:
                stage_births += 1
                if stage_births > max_births:
                    raise RuntimeError(f"{stage}: birth cap before 600-step quota")
                name = f"{stage}-{stage_births:03d}"
                db = lives_dir / f"{name}.sqlite"
                identity = None
                completed = 0
                last_count = 0
                last_head = None
                record = {
                    "name": name, "runtime": stage,
                    "database": str(db.relative_to(output)),
                    "batches": [], "status": "not_started",
                }
                report["lives"].append(record)
                report["births"] += 1
                while (completed < per_life
                       and report["by_runtime"][stage] < target_per_stage):
                    wanted = min(
                        batch, per_life - completed,
                        target_per_stage - report["by_runtime"][stage],
                    )
                    args = [
                        "--db", str(db), "--runtime", stage,
                        "--steps", str(wanted),
                    ]
                    if identity is not None:
                        args += ["--resume", "--identity", identity]
                        report["cold_process_resumptions"] += 1
                    received = _process(TRIAL, args, 600)
                    if identity is None:
                        identity = received.get("individual_id")
                        if type(identity) is not str or not identity:
                            raise RuntimeError("birth did not return durable identity")
                    elif received.get("individual_id") != identity:
                        raise RuntimeError("identity changed on cold process resume")
                    physical = received.get("executed_steps")
                    generation = received.get("generation")
                    world_step = received.get("last_world_step")
                    status = received.get("status")
                    count = received.get("journal_count")
                    head = received.get("journal_head")
                    if (type(physical) is not int or physical < 1
                            or physical > wanted or type(generation) is not int
                            or generation != completed + physical
                            or type(world_step) is not int
                            or world_step != completed + physical
                            or type(count) is not int or count <= last_count
                            or type(head) is not str or head == last_head
                            or status not in ("active", "dead")
                            or received.get("pending_intent") is not False
                            or received.get("operator_acceptance") is not None
                            or received.get("scientific_validation") is not None):
                        raise RuntimeError(
                            f"{name}: unproven physical steps or bad current receipt"
                        )
                    audited = _process(
                        AUDIT,
                        ["--db", str(db), "--identity", identity,
                         "--expect-generation", str(generation),
                         "--expect-head", head],
                        240,
                    )
                    if (audited.get("generation") != generation
                            or audited.get("journal_count") != count
                            or audited.get("journal_head") != head
                            or audited.get("pending_intent") is not False
                            or audited.get("may_recover") is not (status == "active")
                            or audited.get("runtime_recovery_certified") is not False):
                        raise RuntimeError(f"{name}: independent current audit differs")
                    record["batches"].append({
                        "requested_steps": wanted,
                        "applied_physical_steps": physical,
                        "generation": generation,
                        "world_step": world_step,
                        "journal_count": count,
                        "journal_head": head,
                        "lifecycle": status,
                    })
                    completed += physical
                    last_count, last_head = count, head
                    report["by_runtime"][stage] += physical
                    report["physical_steps"] += physical
                    record["status"] = status
                    _save_report(report_path, report)
                    if status == "dead":
                        report["terminal_deaths"] += 1
                        break

                # Export and retain the complete canonical journal for independent
                # postrun audit even if this disposable test life has died.
                with SQLiteLifeLedger.open_existing(
                    path=str(db), expected_individual_id=identity,
                ) as ledger:
                    audited = ledger.audit()
                    stream = ledger.export_canonical_journal()
                    if (audited.generation != completed
                            or audited.journal_count != last_count
                            or audited.journal_head != last_head
                            or len(stream.splitlines()) != last_count):
                        raise RuntimeError(f"{name}: loss or truncation of full journal")
                journal_file = lives_dir / f"{name}.jsonl"
                journal_file.write_bytes(stream + (b"\n" if stream else b""))
                record["applied_physical_steps"] = completed
                record["identity"] = identity
                record["journal_bytes"] = len(stream)
                record["journal_sha256"] = hashlib.sha256(stream).hexdigest()
                record["journal"] = str(journal_file.relative_to(output))
                record["sqlite_bytes"] = db.stat().st_size
                _save_report(report_path, report)

        if (report["physical_steps"] != total
                or any(report["by_runtime"][s] != target_per_stage for s in STAGES)
                or report["cold_process_resumptions"] < len(STAGES)):
            raise RuntimeError("full physical quota or actual cold resumes not proven")
        report["result"] = "software_gate_pass_not_m11_operator_acceptance"
    except BaseException as exc:
        report["result"] = "fail_or_incomplete"
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        raise
    finally:
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
        _save_report(report_path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target-steps", type=int, default=600)
    parser.add_argument("--max-steps-per-life", type=int, default=50)
    parser.add_argument("--batch-steps", type=int, default=25)
    parser.add_argument("--max-births-per-runtime", type=int, default=40)
    args = parser.parse_args()
    try:
        summary = run_campaign(
            output=args.output_dir.resolve(),
            total=args.target_steps,
            per_life=args.max_steps_per_life,
            batch=args.batch_steps,
            max_births=args.max_births_per_runtime,
        )
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"M11_CAMPAIGN_FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "source_sha": summary["source_sha"],
        "result": summary["result"],
        "actual_world_steps": summary["physical_steps"],
        "by_runtime": summary["by_runtime"],
        "births": summary["births"],
        "deaths": summary["terminal_deaths"],
        "cold_process_resumptions": summary["cold_process_resumptions"],
        "elapsed_seconds": summary["elapsed_seconds"],
        "scientific_validation": None,
        "operator_acceptance": None,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
