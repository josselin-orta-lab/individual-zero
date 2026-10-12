#!/usr/bin/env python3
"""Run one fresh mortal Stage12 *development* trial and retain its evidence.

This intentionally fixed-seed fixture is for preliminary technical operator
observations only. It does NOT test real-world deployment, sleep calibration,
scientific validity, Oracle truth or M-11 crash-resumption semantics.
Never resume this identity, even if the process exits unexpectedly.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
import os
import platform
import re
from pathlib import Path
import subprocess
import sys

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.journal import HashChainedJournal
from lab.mortal_execution import MortalStatus
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_runtime import Stage12Runtime

from report_stage12_operator_packet import evaluate_packet


def _exclusive_durable_write(path: Path, content: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(str(path), flags, 0o600)
    try:
        cursor = 0
        while cursor < len(content):
            wrote = os.write(fd, content[cursor:])
            if wrote <= 0:
                raise OSError("incomplete exclusive evidence write")
            cursor += wrote
        os.fsync(fd)
    finally:
        os.close(fd)
    directory = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def _new_exclusive_dir(path: Path) -> None:
    if not path.is_absolute() or not path.parent.is_dir():
        raise ValueError("operator output parent must exist; use a new absolute directory")
    os.mkdir(path, 0o700)
    parent = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)


def _build_trial(*, wal_path: str, steps: int) -> Stage12Runtime:
    # This fixture is intentionally aligned with the *actual* 600-step
    # integration test, not a simulated journal or manually applied action.
    stage11 = build_stage11_reference_runtime(
        enable_geography=True, autonomous_mortal=True,
    )
    stage10 = build_stage10_reference_runtime(autonomous_mortal=True)
    no_sleep = replace(
        stage10._stage10_config.sleep,
        fatigue_gain=0.0, night_weight=0.0, consolidation_weight=0.0,
    )
    stage10_config = replace(
        stage10._stage10_config,
        stage9=stage11._stage11_config.stage9, sleep=no_sleep,
    )
    individual = Stage12Runtime(
        world_config=stage11.world.config,
        layout=stage11.world._layout,
        safety_config=stage11.stage3.substrate.safety._config,
        safety_facts=stage11._canonical_safety._innate,
        protected_integrity_threshold=(
            stage11.stage3.control._config.protected_integrity_threshold
        ),
        stage11_config=stage11._stage11_config,
        stage10_config=stage10_config,
        equipment=stage11.equipment,
        autonomous_mortal=True,
        wal_path=wal_path,
        diagnostic_sample_cost_uc=1,
        module_occupancy_cost_uc=1,
        operator_alert_persistence_steps=3,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-operator-lived-dev-v1",
            window=12, stagnation_steps=4, stagnation_tolerance=0.05,
            loop_repetitions=3, loop_max_period=2,
            entropy_min_samples=4, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )
    Stage12OperatorConsole(
        substrate=individual.stage3.substrate,
        mode="campaign", policy_version="stage12-operator-trial-stop-dev-v1",
        maximum_world_steps=steps,
    )
    return individual



def _execution_provenance() -> dict[str, object]:
    """Detached operator metadata, never passed to I0's causal decisions.

    The code commit and file digests support subsequent reference replay
    review. A clean checkout is not a dependency lock or scientific proof.
    """
    repo = Path(__file__).resolve().parents[1]

    def digest(relative_path: str) -> str | None:
        file = repo / relative_path
        if not file.is_file() or file.is_symlink():
            return None
        return sha256(file.read_bytes()).hexdigest()

    code_commit: str | None = None
    tracked_clean: bool | None = None
    try:
        revision = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "HEAD"],
            capture_output=True, text=True, check=False, timeout=5,
        )
        if revision.returncode == 0:
            candidate = revision.stdout.strip()
            if re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", candidate):
                code_commit = candidate
                status = subprocess.run(
                    ["git", "-C", str(repo), "status", "--porcelain",
                     "--untracked-files=no"],
                    capture_output=True, text=True, check=False, timeout=5,
                )
                if status.returncode == 0:
                    tracked_clean = not bool(status.stdout.strip())
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass

    return {
        "schema": "stage12-operator-execution-provenance-v1",
        "code_commit": code_commit,
        "tracked_checkout_clean": tracked_clean,
        "python_implementation": platform.python_implementation(),
        "python_patch_version": platform.python_version(),
        "normative_spec_sha256": digest(
            "docs/architecture/reference/en/mvp-specification-v1.3.1.md"
        ),
        "deterministic_engine_sha256": digest("src/lab/determinism.py"),
        "package_manifest_sha256": digest("pyproject.toml"),
        # There is currently no committed, patch-exact dependency lock in
        # this repository; an exact cross-machine deterministic replay
        # claim therefore still requires a retained reference environment.
        "fully_locked_reference_environment": False,
        "human_execution_provenance_independently_attested": False,
    }


def run_trial(output_dir: Path, steps: int) -> tuple[int, dict[str, object]]:
    if type(steps) is not int or not 1 <= steps <= 600:
        raise ValueError("software trial steps must be an integer in [1,600]")
    target = output_dir.expanduser().absolute()
    _new_exclusive_dir(target)
    before_environment = _execution_provenance()
    wal = target / "individual-zero-life.wal"
    individual = _build_trial(wal_path=str(wal), steps=steps)
    actions: Counter[str] = Counter()
    failure: str | None = None
    for expected in range(1, steps + 1):
        try:
            result = individual.run_step()
            if (result.execution_status != "applied"
                    or individual.scheduler.t_monde != expected):
                raise RuntimeError(
                    f"step {expected}: physical result {result.execution_status}"
                )
            actions[result.command_primitive] += 1
        except Exception as exc:
            # The Stage11/12 mortal runtime has already fail-closed. Never
            # attempt a catch-up step, restart or rollback of this identity.
            failure = f"{type(exc).__name__}: {exc}"
            break
    complete = (
        failure is None
        and sum(actions.values()) == steps
        and individual.stage3.substrate.mortal_status
            is MortalStatus.EXPERIMENT_STOPPED
    )
    raw = individual.journal.canonical_bytes()
    export = target / "canonical-export.jsonl"
    _exclusive_durable_write(export, raw)
    tail = {"head_hash": individual.journal.head_hash,
            "occurrences": len(individual.journal.entries)}
    audit_error: str | None = None
    packet: dict[str, object] | None = None
    try:
        if not individual.journal.verify():
            raise ValueError("internal journal chain invalid")
        durable = HashChainedJournal.audit_durable_wal(str(wal))
        if (durable["head_hash"] != tail["head_hash"]
                or durable["verified_entries"] != tail["occurrences"]):
            raise ValueError("durable WAL diverges from terminal canonical export")
        if complete:
            packet = evaluate_packet(
                raw, expected_head=tail["head_hash"],
                expected_count=tail["occurrences"],
                expected_world_steps=steps, require_terminal_stop=True,
            )
    except (ValueError, RuntimeError, OSError, TypeError) as exc:
        audit_error = f"{type(exc).__name__}: {exc}"
    after_environment = _execution_provenance()
    environment_unchanged = before_environment == after_environment
    if not environment_unchanged:
        audit_error = (
            (audit_error + "; " if audit_error else "")
            + "operator checkout provenance changed during the trial"
        )
    successful = complete and audit_error is None
    manifest: dict[str, object] = {
        "schema": "stage12-retained-operator-development-trial-v1",
        "status": "complete_technically_audited" if successful else "incomplete_do_not_resume",
        "fixed_development_fixture": "stage11-geographic-and-stage10-awake-stage12-v1",
        "execution_provenance": before_environment,
        "execution_provenance_unchanged": environment_unchanged,
        "sleep_calibration_covered": False,
        "physical_truth_independently_verified": False,
        "m11_atomic_recovery_certified": False,
        "operator_accepted": False,
        "scientific_validated": False,
        "requested_world_steps": steps,
        "physically_applied_steps": sum(actions.values()),
        "world_steps_opened": individual.scheduler.t_monde,
        "mortal_status": individual.stage3.substrate.mortal_status.value,
        "actions": dict(sorted(actions.items())),
        "head_hash": tail["head_hash"],
        "occurrences": tail["occurrences"],
        "wal_filename": wal.name,
        "canonical_export_filename": export.name,
        "failure": failure,
        "audit_failure": audit_error,
        "cross_auditor_packet": packet,
        "warning": (
            "Manifest and export share local custody. Copy trusted head/count "
            "out of band; these files do not prove physical truth or M-11."
        ),
    }
    _exclusive_durable_write(
        target / "trial-manifest.json",
        (json.dumps(manifest, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"),
    )
    return (0 if successful else 2), manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=600)
    args = parser.parse_args(argv)
    try:
        exit_code, manifest = run_trial(args.output_dir, args.steps)
    except (OSError, TypeError, ValueError) as exc:
        print(f"Stage12 operator trial refused: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "status": manifest["status"], "requested": manifest["requested_world_steps"],
        "applied": manifest["physically_applied_steps"],
        "head_hash": manifest["head_hash"], "occurrences": manifest["occurrences"],
        "output_dir": str(args.output_dir.expanduser().absolute()),
        "note": "copy trusted head and count separately before operator audit",
    }, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
