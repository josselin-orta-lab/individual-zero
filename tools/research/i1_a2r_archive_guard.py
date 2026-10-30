"""A2-R frozen 96-slot archive custody gate; NO births and NO L3 claim.

Operator-only, standard library. Requires TWO independently published SHA-256
anchors (lock and final manifest), an externally pinned git source commit, and
a complete 96-file original life ledger. A recorded failure is retained and
blocks the complete cohort; no selective replacement or second attempt.

Passing hashes does NOT prove that an I1Runtime was actually born at the
claimed commit, nor that the M11 contents have been independently replayed.
Those remain separate source/birth/M11 scientific audit obligations.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat

SCHEMA_LOCK = "individual-zero-i1-a2r-origin-lock/1"
SCHEMA_ARCHIVE = "individual-zero-i1-a2r-original-archive/1"
ROLES = ("native", "reversed")
SEEDS = tuple(range(2001, 2025))
MODES = ("CANONICAL_ABS", "RESEARCH_DEFICIT")
HORIZON = 192
MATRIX = tuple((role, seed, mode) for role in ROLES for seed in SEEDS
               for mode in MODES)
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
PREFIX = "i1:eco:a2r:reward:"
FILE_NAMES = frozenset(("life.sqlite", "life.sqlite-wal",
                        "life.sqlite-shm", "report.json"))


def _sha(value: str, *, size: int) -> str:
    if type(value) is not str or (
            SHA40 if size == 40 else SHA64).fullmatch(value) is None:
        raise ValueError(f"expected lowercase SHA-{size} provenance field")
    return value


def _identity(role: str, seed: int, mode: str) -> str:
    return PREFIX + hashlib.sha256(
        ("i1-a2r-reward-identity-v1|%s|%s|%s" %
         (role, seed, mode)).encode("ascii")
    ).hexdigest()[:24]


def ordered_rows():
    return [
        {"role": role, "seed": seed, "mode": mode,
         "identity": _identity(role, seed, mode)}
        for role, seed, mode in sorted(
            MATRIX, key=lambda row: hashlib.sha256(
                ("i1-a2r-reward-order-v1|%s|%s|%s" % row).encode("ascii")
            ).hexdigest())
    ]


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unique_dict(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key in A2-R original custody")
        result[key] = value
    return result


def _no_constants(value):
    raise ValueError("invalid nonfinite JSON constant in A2-R custody")


def load_canonical_json(path: Path, *, expected_digest: str):
    _sha(expected_digest, size=64)
    data = _read_regular(path)
    if sha256_bytes(data) != expected_digest:
        raise ValueError("independently pinned manifest/lock SHA-256 differs")
    document = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_dict,
                          parse_constant=_no_constants)
    if canonical_bytes(document) != data:
        raise ValueError("noncanonical A2-R provenance JSON")
    return document


def origin_lock(*, source_commit: str, source_tree: str,
                preset_sha256: str, run_id: int):
    """Generate a deterministic origin roster; never a self-authorizing run."""
    _sha(source_commit, size=40)
    _sha(source_tree, size=40)
    _sha(preset_sha256, size=64)
    if type(run_id) is not int or not 1 <= run_id < 2**63:
        raise ValueError("A2-R requires one positive integer GitHub run id")
    return {
        "schema": SCHEMA_LOCK,
        "source_commit": source_commit, "source_tree": source_tree,
        "preset_sha256": preset_sha256,
        "github_run_id": run_id, "github_run_attempt": 1,
        "horizon": HORIZON, "independent_seed_blocks": len(SEEDS),
        "original_individuals": len(MATRIX),
        "ordered_births": ordered_rows(),
        "authorization": "NOT_AUTHORIZED_BY_THIS_LOCK",
        "general_L3": "NOT_ESTABLISHED",
    }


def validate_lock(lock: object, *, expected_commit: str, expected_tree: str,
                  expected_preset: str, expected_run_id: int):
    if type(lock) is not dict or lock != origin_lock(
            source_commit=expected_commit, source_tree=expected_tree,
            preset_sha256=expected_preset, run_id=expected_run_id):
        raise ValueError("lock does not equal independently expected A2-R source/order")
    return True


def _read_regular(path: Path) -> bytes:
    """No symlink, hardlink, or mid-read modification, including SQLite sidecars."""
    if not path.is_absolute():
        raise ValueError("custody path must be absolute")
    try:
        before = path.lstat()
    except OSError as exc:
        raise ValueError("missing immutable original custody file") from exc
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("symlink, hardlink or nonregular custody file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if (opened.st_ino, opened.st_dev) != (before.st_ino, before.st_dev):
                raise ValueError("race in original custody path")
            data = stream.read()
            after = os.fstat(stream.fileno())
        final = path.lstat()
    except OSError as exc:
        raise ValueError("original custody read refused") from exc
    for current in (opened, after, final):
        if ((current.st_dev, current.st_ino, current.st_size,
             current.st_mtime_ns, current.st_ctime_ns) !=
            (before.st_dev, before.st_ino, before.st_size,
             before.st_mtime_ns, before.st_ctime_ns)):
            raise ValueError("original custody file changed during audit")
    return data


def _directory(path: Path):
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise ValueError("A2-R original directory missing or symlinked")
    if path.stat().st_nlink < 1:
        raise ValueError("broken archive directory")


def verify_archive(*, root: Path, expected_commit: str, expected_tree: str,
                   expected_preset: str, expected_run_id: int,
                   expected_lock_sha256: str, expected_manifest_sha256: str):
    """Verify the complete externally anchored 96-life archive, WITHOUT M11.

    A missing/crashed life is evidence of failure, never a replacement slot.
    Reject any failure even with a correctly hashed failure report.
    Inputs must be independently obtained source/run/digest attestations;
    in particular the two hashes MUST NOT be read from the same archive.
    """
    root = Path(root)
    _directory(root)
    lock = load_canonical_json(root / "lock.json",
                               expected_digest=expected_lock_sha256)
    validate_lock(lock, expected_commit=expected_commit,
                  expected_tree=expected_tree, expected_preset=expected_preset,
                  expected_run_id=expected_run_id)
    manifest = load_canonical_json(root / "manifest.json",
                                   expected_digest=expected_manifest_sha256)
    if (type(manifest) is not dict
            or set(manifest) != {"schema", "lock_sha256", "source_commit",
                                 "github_run_id", "github_run_attempt", "horizon",
                                 "lives", "general_L3"}
            or manifest["schema"] != SCHEMA_ARCHIVE
            or manifest["lock_sha256"] != expected_lock_sha256
            or manifest["source_commit"] != expected_commit
            or manifest["github_run_id"] != expected_run_id
            or type(manifest["github_run_attempt"]) is not int
            or manifest["github_run_attempt"] != 1
            or manifest["horizon"] != HORIZON
            or manifest["general_L3"] != "NOT_ESTABLISHED"):
        raise ValueError("archive deviates from independently fixed original run")
    lives = manifest["lives"]
    expected = ordered_rows()
    if type(lives) is not list or len(lives) != len(expected):
        raise ValueError("missing, substituted or extra A2-R original individuals")
    _directory(root / "lives")
    if set(os.listdir(root)) != {"lives", "lock.json", "manifest.json"}:
        raise ValueError("unaccounted A2-R archive root artifact")
    if set(os.listdir(root / "lives")) != {row["identity"] for row in expected}:
        raise ValueError("missing, duplicated or unregistered individual folder")

    seen_inode = set()
    file_count = 0
    for prescribed, life in zip(expected, lives):
        if (type(life) is not dict
                or set(life) != {"identity", "role", "seed", "mode", "run_attempt",
                                 "source_commit", "result", "generation", "status",
                                 "journal_head", "state_hash", "files"}
                or any(life.get(k) != prescribed[k] for k in prescribed)
                or type(life.get("run_attempt")) is not int
                or life["run_attempt"] != 1
                or life.get("source_commit") != expected_commit
                or life.get("result") not in ("COMPLETE", "FAILED")):
            raise ValueError("life differs from preregistered matrix, source or attempt")
        folder = root / "lives" / prescribed["identity"]
        _directory(folder)
        files = life["files"]
        if type(files) is not dict or not files or not set(files) <= FILE_NAMES:
            raise ValueError("missing or unregistered SQLite/archive file")
        if set(files) != set(os.listdir(folder)):
            raise ValueError("unaccounted original file or missing declared file")
        if life["result"] != "COMPLETE":
            raise ValueError("original technical failure: preserve, never replace")
        if "life.sqlite" not in files or "report.json" not in files:
            raise ValueError("no immutable life SQLite and birth report")
        n = life["generation"]
        status = life["status"]
        if (type(n) is not int or not 1 <= n <= HORIZON
                or status not in ("dead", "active")
                or status == "active" and n != HORIZON):
            raise ValueError("incomplete nondead A2-R original life")
        _sha(life["journal_head"], size=64)
        _sha(life["state_hash"], size=64)
        for filename, digest in sorted(files.items()):
            _sha(digest, size=64)
            path = folder / filename
            file_stat = path.lstat()
            inode = (file_stat.st_dev, file_stat.st_ino)
            if inode in seen_inode:
                raise ValueError("two claimed originals alias one physical file")
            seen_inode.add(inode)
            if sha256_bytes(_read_regular(path)) != digest:
                raise ValueError("original life / sidecar SHA-256 differs")
            file_count += 1
    return {
        "scope": "A2R_ORIGINAL_ARCHIVE_BYTE_CUSTODY_NOT_M11_NOT_L3",
        "original_lives": len(lives),
        "independent_seed_blocks": len(SEEDS),
        "original_file_count": file_count,
        "source_commit_declared_and_externally_pinned": expected_commit,
        "source_runtime_execution_attested": False,
        "full_m11_cold_audit_verified": False,
        "birth_parameters_independently_verified": False,
        "preregistered_mechanism_exposed": False,
        "study_admissible": False,
        "adaptive_learning_go": "NOT_ESTABLISHED",
        "historical_A1C": "NO_GO",
    }
