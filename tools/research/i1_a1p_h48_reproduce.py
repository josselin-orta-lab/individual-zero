"""Fail-closed offline replay launcher for the sealed historical A1-P H48 capsule.

No I1 import or birth. The original eight mortal archives remain read-only.
The checked research capsule is external input, NOT a result or promotion to L3.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import zipfile

ORIGIN_RUN = 40938021102
SOURCE_SHA = "012ece9eb0b4531f714bd69af439eeb38d7bf701"
CAPSULE_SHA256 = "cbe306707c724b0a4c43b628076980d96f4d088092d1bb35e282c0bbf5bada2d"
ORIGINAL_SHA256 = {
    "a1-native-s1-canonical.zip": "e909d0faea78c09f5e2b4dca101caaf946c47a2a058b104bf8666bde642a03be",
    "a1-native-s1-td-read-masked.zip": "c8a19ca164593ab5c1535ab8c42b5651a34a173b832b35ea3b77d0490b505d9f",
    "a1-native-s2-canonical.zip": "0504052c11c8a551bbb67adcba059883c83bb5ae1852f7fa65daaa0fe5dafa16",
    "a1-native-s2-td-read-masked.zip": "92d90571b166b8ce95def625e22201e3ecfe9a3bfa798603d2faac8ff46a44d3",
    "a1-reversed-s1-canonical.zip": "25100c403f8676222430074da537a4b9c09842ac76b65c00a4683e6c979bbb71",
    "a1-reversed-s1-td-read-masked.zip": "c7f6931ef34b5af3badeae95b39b276dce8b72ef7de894ef5d346d4f8865bc92",
    "a1-reversed-s2-canonical.zip": "40de2ee0b1be3c4a8e9c485bb4d790eefa7f87bbb012465a0611f01c18c399e0",
    "a1-reversed-s2-td-read-masked.zip": "88ae4dc59aedabe3dc201a99eebaa7ac31159343b6259d45cf47fc9e6a974e89",
}
CAPSULE_NAMES = frozenset({
    "I1_A1P_H48_FIRST_PAID_Q_SENSITIVITY_2026-10-31.md", "README_FIRST_PAID_Q.md",
    "a1p_h48_first_paid_q_sensitivity.py", "a1p_h48_first_paid_q_sensitivity_result.json",
    "a1p_h48_instrumental_credit.py", "a1p_h48_post_credit_selection.py",
    "all_39_tests.log", "audit_h48.py", "audit_h48_independent_td.py",
    "audit_h48_motor_rank_mediation.py", "audit_h48_td_motor_closure.py",
    "audit_h48_upstream_q.py", "test_a1p_h48_first_paid_q_sensitivity.py",
    "test_a1p_h48_instrumental_credit.py", "test_a1p_h48_post_credit_selection.py",
    "test_audit_h48_independent_td.py", "test_audit_h48_motor_rank_mediation.py",
    "test_audit_h48_upstream_q.py",
})


def _regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"original or capsule is absent/linked: {path.name}")
    st = path.stat()
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        raise ValueError(f"linked or non-regular source: {path.name}")


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _check_file(path: Path, expected: str) -> None:
    _regular(path)
    if _digest(path) != expected:
        raise ValueError(f"immutable A1-P SHA-256 mismatch: {path.name}")


def _validate_capsule_members(z: zipfile.ZipFile) -> None:
    members = z.infolist()
    if len(members) != len(CAPSULE_NAMES) or {x.filename for x in members} != CAPSULE_NAMES:
        raise ValueError("capsule contains missing, repeated or unexpected files")
    if sum(x.file_size for x in members) > 1024 * 1024:
        raise ValueError("capsule uncompressed size exceeds documented limit")
    for m in members:
        mode = (m.external_attr >> 16) & 0xFFFF
        if (m.is_dir() or m.filename != Path(m.filename).name
                or m.file_size > 256 * 1024 or stat.S_ISLNK(mode)):
            raise ValueError("capsule member is linked, nested or oversized")


def verify_inputs(*, capsule: Path, originals: Path) -> dict:
    """Verify sealed bytes BEFORE unpacking any code or reading the SQLite."""
    if originals.is_symlink() or not originals.is_dir():
        raise ValueError("original archive directory absent or linked")
    _check_file(capsule, CAPSULE_SHA256)
    for name, digest in ORIGINAL_SHA256.items():
        _check_file(originals / name, digest)
    with zipfile.ZipFile(capsule) as z:
        _validate_capsule_members(z)
        if z.testzip() is not None:
            raise ValueError("corrupt capsule member")
    return {
        "scope": "I1_A1P_H48_SEALED_ARCHIVES_VERIFIED_NOT_NEW_STUDY",
        "origin_run_id": ORIGIN_RUN,
        "origin_source_commit": SOURCE_SHA,
        "capsule_sha256": CAPSULE_SHA256,
        "original_lives_sha256_verified": len(ORIGINAL_SHA256),
        "original_h48_lives_reexecuted": 0,
        "A2_R_confirmatory_lives_executed": 0,
        "motor_causal_counterfactual_proven": False,
        "adaptive_L3": "NOT_ESTABLISHED",
    }


def replay(*, capsule: Path, originals: Path, verify_only: bool = False) -> dict:
    checked = verify_inputs(capsule=capsule, originals=originals)
    if verify_only:
        return checked
    with tempfile.TemporaryDirectory(prefix="i1-a1p-h48-offline-") as temp:
        wd = Path(temp)
        with zipfile.ZipFile(capsule) as z:
            for member in z.infolist():
                # Whitelist validated. Never use extractall or trust paths.
                (wd / member.filename).write_bytes(z.read(member))
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        env["PYTHONNOUSERSITE"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["I1_A1P_ARTIFACT_DIR"] = str(originals.resolve())
        cmd = [sys.executable, "-B", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-q"]
        result = subprocess.run(cmd, cwd=wd, env=env, capture_output=True, text=True, timeout=180, check=False)
        if result.returncode or "Ran 39 tests" not in result.stderr or "OK" not in result.stderr:
            raise ValueError("pinned H48 replay tests failed or expected test count changed")
        result2 = subprocess.run([sys.executable, "-B", "a1p_h48_first_paid_q_sensitivity.py"],
                                 cwd=wd, env=env, capture_output=True, text=True, timeout=180, check=False)
        if result2.returncode:
            raise ValueError("pinned H48 sensitivity replay failed")
        summary = json.loads((wd / "a1p_h48_first_paid_q_sensitivity_result.json").read_text(encoding="utf-8"))
        if (summary.get("origin_run") != ORIGIN_RUN
                or summary.get("source_commit") != SOURCE_SHA
                or summary.get("historical_lives_verified") != 8
                or summary.get("historical_TD_updates_verified") != 188
                or summary.get("first_learned_episode_counts", {}).get("n") != 14
                or summary.get("first_learned_episode_counts", {}).get("fixed_cycle_crossing_differs") != 1
                or summary.get("adaptive_L3") != "NOT_ESTABLISHED"
                or summary.get("motor_causality_established") is not False):
            raise ValueError("H48 replay report violates pinned historical boundary")
    return {**checked, "offline_adversarial_tests_passed": 39,
            "TD_updates_replayed": 188, "first_paid_Q_episodes": 14,
            "fixed_cycle_crossing_sensitivities": 1,
            "replay_completed": True,
            "study_admissible_as_new_confirmatory_evidence": False}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capsule", required=True, type=Path)
    parser.add_argument("--originals", required=True, type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(replay(capsule=args.capsule, originals=args.originals,
                            verify_only=args.verify_only), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
