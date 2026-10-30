"""A2-R original-cohort archive assembler; NO births and NO GO verdict.

Takes 96 UNMODIFIED job fragments and an independently pinned origin lock,
materializes the complete, reproducible byte archive expected by the existing
i1_a2r_archive_guard, then returns the NEW manifest SHA that an independent
custodian must publish. The manifest digest calculated here is NOT an
independent external anchor. This module never accepts a subset, replacement
life, invented recovery step, or later run attempt.

All M11 source/birth/replay and motor-mediation evidence is a separate
post-flight audit. Report fields are labels, NEVER substitute for cold M11.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

from i1_a2r_archive_guard import (
    FILE_NAMES, SCHEMA_ARCHIVE, SHA40, SHA64, _directory, _read_regular,
    canonical_bytes, load_canonical_json, ordered_rows, sha256_bytes,
    validate_lock, verify_archive,
)

FRAGMENT_SCHEMA = "individual-zero-i1-a2r-original-life-fragment/1"
FRAGMENT_FIELDS = frozenset((
    "schema", "identity", "role", "seed", "mode", "horizon",
    "source_commit", "source_tree", "preset_sha256",
    "github_run_id", "github_run_attempt", "result", "generation",
    "status", "journal_head", "state_hash", "general_L3",
))
_UNVERIFIED = "NOT_ESTABLISHED"


def _parse_fragment(raw: bytes, *, row: dict, source_commit: str,
                    source_tree: str, preset: str, run_id: int):
    """Check claimed outcome labels but do NOT trust them as M11 evidence."""
    try:
        data = json.loads(raw.decode("utf-8"),
                          object_pairs_hook=_unique_pairs,
                          parse_constant=_invalid_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("A2-R original life report is malformed") from exc
    if (type(data) is not dict or
            set(data) != FRAGMENT_FIELDS or
            data.get("schema") != FRAGMENT_SCHEMA or
            data.get("horizon") != 192 or
            data.get("source_commit") != source_commit or
            data.get("source_tree") != source_tree or
            data.get("preset_sha256") != preset or
            type(data.get("github_run_id")) is not int or
            data["github_run_id"] != run_id or
            type(data.get("github_run_attempt")) is not int or
            data["github_run_attempt"] != 1 or
            data.get("general_L3") != _UNVERIFIED or
            any(data.get(k) != row[k] for k in row)):
        raise ValueError("original life has wrong birth or source/run label")
    if canonical_bytes(data) != raw:
        raise ValueError("original report not canonical; cannot reserialize evidence")
    status, result, generation = (
        data.get("status"), data.get("result"), data.get("generation"))
    if result not in ("COMPLETE", "FAILED") or type(generation) is not int:
        raise ValueError("invalid original life outcome")
    if result == "COMPLETE":
        if (not 1 <= generation <= 192 or
                status not in ("active", "dead") or
                (status == "active" and generation != 192) or
                type(data.get("journal_head")) is not str or
                not SHA64.fullmatch(data["journal_head"]) or
                type(data.get("state_hash")) is not str or
                not SHA64.fullmatch(data["state_hash"])):
            raise ValueError("claimed complete life is incomplete or not auditable")
    else:
        # Preserve a failure as a FAILED original; never normalize it to
        # COMPLETE, replace it or silently remove it from the 96 rows.
        if status not in ("technical_failure", "dead", "active"):
            raise ValueError("technical failure has an unknown status")
        if not 0 <= generation <= 192:
            raise ValueError("technical failure generation invalid")
    return data


def _unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key in original life report")
        out[key] = value
    return out


def _invalid_constant(value):
    raise ValueError("nonfinite JSON in original life report")


def _list_originals(path: Path, *, names: set[str]):
    _directory(path)
    found = set(os.listdir(path))
    if found != names:
        raise ValueError("A2-R missing or unexpected original directory/file")
    return found


def assemble_original_archive(*, spool_root, destination, external_lock_path,
                              external_lock_sha256, source_commit, source_tree,
                              preset_sha256, github_run_id):
    """Copy original bytes only once and publish a seal-ready manifest.

    The spool is a distinct immutable input. Destination MUST NOT exist,
    including an empty directory. Source/run/digest anchors come from a
    trusted independent observation, NOT the fragment report or manifest.
    Return verdict MEASUREMENT_BLOCKED until independently sealed and audited.
    """
    src = Path(spool_root)
    dst = Path(destination)
    lock_path = Path(external_lock_path)
    if (not src.is_absolute() or not dst.is_absolute() or
            not lock_path.is_absolute() or
            src.resolve() == dst.resolve() or
            dst.exists() or dst.is_symlink() or
            not dst.parent.is_dir() or
            dst.parent.is_symlink() or
            not SHA40.fullmatch(source_commit) or
            not SHA40.fullmatch(source_tree) or
            not SHA64.fullmatch(preset_sha256) or
            type(github_run_id) is not int or github_run_id < 1):
        raise ValueError("A2-R archive paths or external source lock invalid")

    expected = ordered_rows()
    _list_originals(src, names={row["identity"] for row in expected})
    lock = load_canonical_json(lock_path, expected_digest=external_lock_sha256)
    validate_lock(lock, expected_commit=source_commit,
                  expected_tree=source_tree, expected_preset=preset_sha256,
                  expected_run_id=github_run_id)
    lock_raw = _read_regular(lock_path)

    # Fail BEFORE making output, including any alias/symlink of an original.
    original_inodes = set()
    originals = []
    for row in expected:
        folder = src / row["identity"]
        _directory(folder)
        filenames = set(os.listdir(folder))
        if ("report.json" not in filenames or
                not filenames.issubset(FILE_NAMES)):
            raise ValueError("missing original report or unregistered sidecar")
        payloads = {}
        for filename in sorted(filenames):
            path = folder / filename
            item_stat = path.lstat()
            if (not stat.S_ISREG(item_stat.st_mode) or item_stat.st_nlink != 1 or
                    (item_stat.st_dev, item_stat.st_ino) in original_inodes):
                raise ValueError("original file is linked or used more than once")
            original_inodes.add((item_stat.st_dev, item_stat.st_ino))
            payloads[filename] = _read_regular(path)
        report = _parse_fragment(payloads["report.json"], row=row,
                                 source_commit=source_commit,
                                 source_tree=source_tree,
                                 preset=preset_sha256,
                                 run_id=github_run_id)
        if report["result"] == "COMPLETE" and "life.sqlite" not in payloads:
            raise ValueError("claimed complete original is missing M11 database")
        originals.append((row, report, payloads))

    # Build from precisely the immutable-checked source bytes, one copy of
    # every origin; fail/fatal rows remain in the manifest with their label.
    stage = Path(tempfile.mkdtemp(prefix=".a2r-origin-", dir=dst.parent))
    try:
        (stage / "lives").mkdir()
        (stage / "lock.json").write_bytes(lock_raw)
        entries = []
        for row, report, payloads in originals:
            folder = stage / "lives" / row["identity"]
            folder.mkdir()
            digests = {}
            for filename, payload in payloads.items():
                (folder / filename).write_bytes(payload)
                digests[filename] = sha256_bytes(payload)
            entries.append({
                **row, "run_attempt": 1,
                "source_commit": source_commit,
                "result": report["result"],
                "generation": report["generation"],
                "status": report["status"],
                "journal_head": report["journal_head"],
                "state_hash": report["state_hash"],
                "files": dict(sorted(digests.items())),
            })
        manifest = {
            "schema": SCHEMA_ARCHIVE, "lock_sha256": external_lock_sha256,
            "source_commit": source_commit, "github_run_id": github_run_id,
            "github_run_attempt": 1, "horizon": 192,
            "lives": entries, "general_L3": _UNVERIFIED,
        }
        manifest_bytes = canonical_bytes(manifest)
        (stage / "manifest.json").write_bytes(manifest_bytes)
        # Read twice and compare every original, even in the presence of
        # technical failures; a failed life remains failed.
        for row, report, payloads in originals:
            folder = stage / "lives" / row["identity"]
            for filename, payload in payloads.items():
                if _read_regular(folder / filename) != payload:
                    raise ValueError("copied A2-R original differs from spool")
        if _read_regular(stage / "lock.json") != lock_raw:
            raise ValueError("copied A2-R origin lock differs")
        if sha256_bytes(_read_regular(stage / "manifest.json")) != sha256_bytes(
                manifest_bytes):
            raise ValueError("original archive manifest changed during write")
        # The existing archive guard verifies byte completeness; it always
        # refuses a FAILED original. Do NOT suppress any audit failure to GO.
        contains_failure = any(x[1]["result"] == "FAILED" for x in originals)
        if not contains_failure:
            verify_archive(
                root=stage, expected_commit=source_commit,
                expected_tree=source_tree, expected_preset=preset_sha256,
                expected_run_id=github_run_id,
                expected_lock_sha256=external_lock_sha256,
                expected_manifest_sha256=sha256_bytes(manifest_bytes),
            )
        os.replace(stage, dst)  # destination is a previously absent name
    except BaseException:
        shutil.rmtree(stage)
        raise

    return {
        "schema": "individual-zero-i1-a2r-assembly-receipt/1",
        "original_lives": len(originals),
        "individual_failures_preserved": sum(
            x[1]["result"] == "FAILED" for x in originals),
        "lock_sha256": external_lock_sha256,
        "manifest_sha256_to_publish_independently": sha256_bytes(manifest_bytes),
        "manifest_externally_published": False,
        "external_source_runtime_verified": False,
        "m11_cold_audit_verified": False,
        "scientific_analysis_admissible": False,
        "status": "MEASUREMENT_BLOCKED",
        "general_L3": "NOT_ESTABLISHED",
    }
