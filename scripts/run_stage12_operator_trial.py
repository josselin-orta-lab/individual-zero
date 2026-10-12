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
from hashlib import sha1, sha256
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



def _tracked_source_fingerprint(repo: Path) -> tuple[str | None, int]:
    """Verify each Git-index blob/mode against the *actual* checkout bytes.

    Status --porcelain can hide dirty bytes behind assume-unchanged or
    skip-worktree flags, or ignore executable-bit drift if core.filemode=false.
    An independent SHA-256 tree digest is useful only after every Git-index
    tracked blob and executable mode has also been verified. Reject symlinks,
    submodule gitlinks, unmerged stages and unreadable/incomplete checkouts.
    """
    files = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--cached", "--stage", "-z"],
        capture_output=True, check=False, timeout=30,
    )
    fmt = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--show-object-format"],
        capture_output=True, check=False, timeout=5,
    )
    if files.returncode != 0 or not files.stdout or fmt.returncode != 0:
        return None, 0
    object_format = fmt.stdout.strip()
    if object_format not in (b"sha1", b"sha256"):
        return None, 0
    result = sha256()
    count = 0
    for record in files.stdout.split(b"\x00"):
        if not record:
            continue
        metadata, tab, raw = record.partition(b"\t")
        fields = metadata.split(b" ")
        if not tab or len(fields) != 3 or fields[2] != b"0":
            return None, 0
        index_mode, expected_hash = fields[:2]
        if index_mode not in (b"100644", b"100755"):
            return None, 0
        if len(expected_hash) != (40 if object_format == b"sha1" else 64):
            return None, 0
        try:
            path = Path(os.fsdecode(raw))
            if path.is_absolute() or ".." in path.parts:
                return None, 0
            local = repo / path
            if local.is_symlink() or not local.is_file():
                return None, 0
            stat = local.stat()
            actual_mode = b"100755" if stat.st_mode & 0o111 else b"100644"
            if actual_mode != index_mode:
                return None, 0
            git_blob = sha1() if object_format == b"sha1" else sha256()
            git_blob.update(b"blob " + str(stat.st_size).encode("ascii") + b"\x00")
            file_hash = sha256()
            bytes_read = 0
            with local.open("rb") as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    git_blob.update(chunk)
                    file_hash.update(chunk)
            if bytes_read != stat.st_size or git_blob.hexdigest().encode("ascii") != expected_hash:
                return None, 0
        except (OSError, UnicodeError, ValueError):
            return None, 0
        result.update(len(raw).to_bytes(8, "big"))
        result.update(raw)
        result.update(index_mode)
        result.update(file_hash.digest())
        count += 1
    return (result.hexdigest(), count) if count else (None, 0)


_REQUIRED_TRACKED_TRIAL_PATHS = (
    "scripts/run_stage12_operator_trial.py",
    "scripts/report_stage12_operator_packet.py",
    "docs/architecture/reference/en/mvp-specification-v1.3.1.md",
    "src/lab/determinism.py",
    "src/lab/stage12_runtime.py",
    "src/i0/modules/stage12_detectors.py",
    "pyproject.toml",
)

_TRIAL_IMPORT_ORIGINS = {
    "lab.journal": "src/lab/journal.py",
    "lab.determinism": "src/lab/determinism.py",
    "lab.stage12_runtime": "src/lab/stage12_runtime.py",
    "i0.modules.stage12_detectors": "src/i0/modules/stage12_detectors.py",
    "report_stage12_operator_packet": "scripts/report_stage12_operator_packet.py",
}


def _required_sources_are_git_tracked(repo: Path) -> bool:
    """Existence alone does not establish that normative/executable files are versioned."""
    files = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--cached", "-z", "--",
         *_REQUIRED_TRACKED_TRIAL_PATHS],
        capture_output=True, check=False, timeout=30,
    )
    if files.returncode != 0:
        return False
    actual = {os.fsdecode(raw) for raw in files.stdout.split(b"\x00") if raw}
    return set(_REQUIRED_TRACKED_TRIAL_PATHS).issubset(actual)


def _runtime_imports_match_checkout(repo: Path) -> bool:
    """An identified source tree is insufficient if Python imported another tree."""
    for module_name, relative in _TRIAL_IMPORT_ORIGINS.items():
        module = sys.modules.get(module_name)
        origin = getattr(module, "__file__", None)
        if not isinstance(origin, str):
            return False
        try:
            if Path(origin).resolve(strict=True) != (repo / relative).resolve(strict=True):
                return False
        except OSError:
            return False
    return True


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
        try:
            return sha256(file.read_bytes()).hexdigest()
        except OSError:
            return None

    code_commit: str | None = None
    tracked_clean: bool | None = None
    source_tree_digest: str | None = None
    source_files_count = 0
    git_root_matches_runner = False
    required_source_paths_tracked = False
    runtime_modules_from_checkout = _runtime_imports_match_checkout(repo)
    try:
        root = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False, timeout=5,
        )
        if root.returncode == 0 and root.stdout.strip():
            git_root_matches_runner = (
                Path(root.stdout.strip()).resolve() == repo
            )
        revision = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "HEAD"],
            capture_output=True, text=True, check=False, timeout=5,
        )
        if revision.returncode == 0:
            candidate = revision.stdout.strip()
            if (git_root_matches_runner
                    and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", candidate)):
                code_commit = candidate
                status = subprocess.run(
                    ["git", "-C", str(repo), "status", "--porcelain",
                     "--untracked-files=no"],
                    capture_output=True, text=True, check=False, timeout=5,
                )
                if status.returncode == 0:
                    tracked_clean = not bool(status.stdout.strip())
                    required_source_paths_tracked = (
                        _required_sources_are_git_tracked(repo)
                    )
                    source_tree_digest, source_files_count = (
                        _tracked_source_fingerprint(repo)
                    )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass

    return {
        "schema": "stage12-operator-execution-provenance-v1",
        "code_commit": code_commit,
        "git_root_matches_runner": git_root_matches_runner,
        "required_source_paths_tracked": required_source_paths_tracked,
        "runtime_modules_from_checkout": runtime_modules_from_checkout,
        "tracked_checkout_clean": tracked_clean,
        "tracked_source_tree_sha256": source_tree_digest,
        "tracked_files_count": source_files_count,
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
    # Source verification happens BEFORE birth and before allocating any
    # output folder. A dirty or unidentified checkout is not a reproducible
    # operator development fixture, even if its recorded HEAD is valid.
    before_environment = _execution_provenance()
    if (before_environment["code_commit"] is None
            or before_environment["git_root_matches_runner"] is not True
            or before_environment["required_source_paths_tracked"] is not True
            or before_environment["runtime_modules_from_checkout"] is not True
            or before_environment["tracked_checkout_clean"] is not True
            or before_environment["tracked_source_tree_sha256"] is None
            or before_environment["tracked_files_count"] < 1
            or any(before_environment[key] is None for key in (
                "normative_spec_sha256", "deterministic_engine_sha256",
                "package_manifest_sha256",
            ))):
        raise ValueError(
            "operator trial requires a clean, identified, complete Git checkout"
        )
    target = output_dir.expanduser().absolute()
    _new_exclusive_dir(target)
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
    environment_unchanged = (
        before_environment == after_environment
        and after_environment["tracked_checkout_clean"] is True
    )
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
