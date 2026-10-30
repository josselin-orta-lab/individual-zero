"""Reserve ONE A2-R original slot, preserving failures without starting I1.

A slot is claimed exclusively BEFORE any potential birth. It starts with a
PENDING report rejected by the existing 96-slot archive assembler. A single
terminal transition may seal COMPLETE or FAILED, but never convert a failure
to a successful replacement. If interrupted while PENDING, the run is blocked:
NEVER retry a mortal life. No cohort launch, M11 cold proof, external run
attestation, or permission to execute is granted by this module.

This module deliberately has no call to birth_i1_m11 or run_step.
"""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import stat
import tempfile

from i1_a2r_archive_guard import (
    MATRIX, SHA40, SHA64, _identity, _read_regular, canonical_bytes,
)
from i1_a2r_archive_assembly import FRAGMENT_SCHEMA, FRAGMENT_FIELDS

_SCOPE = "A2R_ORIGINAL_SLOT_CUSTODY_NO_BIRTH_NO_L3"
_GATE_SCOPE = "A2R_RUN_CONTEXT_PREFLIGHT_NOT_EXTERNAL_ATTESTATION_NOT_L3"
_HORIZON = 192
_PENDING = "PENDING"

_CONTEXT_FIELDS = frozenset((
    "scope", "role", "seed", "mode", "identity", "source_commit",
    "source_tree", "preset_sha256", "github_run_id", "github_run_attempt",
    "external_lock_sha256_claimed", "external_run_event_independently_verified",
    "protected_environment_review_independently_verified",
    "cohort_launch_authorized_by_this_module", "general_L3",
))


def _context(ctx):
    """Validate a claimed context again; not evidence of external approval."""
    if (type(ctx) is not dict or set(ctx) != _CONTEXT_FIELDS
            or ctx["scope"] != _GATE_SCOPE
            or type(ctx["role"]) is not str
            or type(ctx["seed"]) is not int
            or type(ctx["mode"]) is not str
            or (ctx["role"], ctx["seed"], ctx["mode"]) not in MATRIX
            or ctx["identity"] != _identity(
                ctx["role"], ctx["seed"], ctx["mode"])
            or type(ctx["source_commit"]) is not str
            or SHA40.fullmatch(ctx["source_commit"]) is None
            or type(ctx["source_tree"]) is not str
            or SHA40.fullmatch(ctx["source_tree"]) is None
            or type(ctx["preset_sha256"]) is not str
            or SHA64.fullmatch(ctx["preset_sha256"]) is None
            or type(ctx["github_run_id"]) is not int
            or not 1 <= ctx["github_run_id"] < 2**63
            or type(ctx["github_run_attempt"]) is not int
            or ctx["github_run_attempt"] != 1
            or type(ctx["external_lock_sha256_claimed"]) is not str
            or SHA64.fullmatch(ctx["external_lock_sha256_claimed"]) is None
            or ctx["external_run_event_independently_verified"] is not False
            or ctx["protected_environment_review_independently_verified"] is not False
            or ctx["cohort_launch_authorized_by_this_module"] is not False
            or ctx["general_L3"] != "NOT_ESTABLISHED"):
        raise ValueError("A2-R slot requires an unchanged non-authorizing gate context")
    return ctx


def _root(spool_root):
    path = Path(spool_root)
    if (not path.is_absolute() or path.is_symlink()
            or not path.is_dir() or path.resolve() != path):
        raise ValueError("original spool root must preexist without symlinks")
    return path


def _report(ctx, *, result, status, generation, head, state_hash):
    return {
        "schema": FRAGMENT_SCHEMA,
        "identity": ctx["identity"], "role": ctx["role"],
        "seed": ctx["seed"], "mode": ctx["mode"],
        "horizon": _HORIZON, "source_commit": ctx["source_commit"],
        "source_tree": ctx["source_tree"],
        "preset_sha256": ctx["preset_sha256"],
        "github_run_id": ctx["github_run_id"],
        "github_run_attempt": ctx["github_run_attempt"],
        "result": result, "generation": generation, "status": status,
        "journal_head": head, "state_hash": state_hash,
        "general_L3": "NOT_ESTABLISHED",
    }


def _sync_dir(path):
    handle = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(handle)
    finally:
        os.close(handle)


def reserve_original_slot(*, spool_root, context):
    """Atomically claim one ID: crash leaves a permanently unusable PENDING slot.

    An existing slot, even empty or with a failed report, is NEVER reused.
    The caller MUST NOT interpret reservation as permission to run a life.
    """
    ctx = _context(context)
    root = _root(spool_root)
    slot = root / ctx["identity"]
    try:
        slot.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise ValueError("original mortal identity already reserved; no retry") from exc
    # Do not remove the slot if anything below fails; a partial claim is fatal.
    report = _report(ctx, result=_PENDING, status="technical_failure",
                     generation=0, head=None, state_hash=None)
    data = canonical_bytes(report)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW
    fd = os.open(slot / "report.json", flags, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())
    _sync_dir(slot)
    _sync_dir(root)
    return {
        "scope": _SCOPE, "identity": ctx["identity"],
        "slot_path": str(slot), "original_reserved": True,
        "born_or_run_step_executed": False, "launch_authorized": False,
        "archive_admissible": False, "general_L3": "NOT_ESTABLISHED",
    }


def _outcome(result, receipt):
    if result not in ("COMPLETE", "FAILED"):
        raise ValueError("only terminal original outcomes may be sealed")
    if type(receipt) is not dict or set(receipt) != {
            "generation", "status", "journal_head", "state_hash"}:
        raise ValueError("terminal receipt must have the exact M11 outcome fields")
    n, status, head, state = (receipt["generation"], receipt["status"],
                              receipt["journal_head"], receipt["state_hash"])
    if type(n) is not int or not 0 <= n <= _HORIZON:
        raise ValueError("invalid M11 generation")
    if result == "COMPLETE":
        if (not 1 <= n <= _HORIZON or status not in ("dead", "active")
                or (status == "active" and n != _HORIZON)
                or type(head) is not str or SHA64.fullmatch(head) is None
                or type(state) is not str or SHA64.fullmatch(state) is None):
            raise ValueError("incomplete, unsealed or forged complete original")
    elif status not in ("technical_failure", "dead", "active"):
        raise ValueError("invalid original technical failure status")
    if result == "FAILED":
        for label, value in (("journal_head", head), ("state_hash", state)):
            if value is not None and (type(value) is not str
                                      or SHA64.fullmatch(value) is None):
                raise ValueError("invalid failure " + label)
    return n, status, head, state


def finalize_original_slot(*, spool_root, context, result, receipt):
    """One irreversible PENDING -> COMPLETE/FAILED receipt transition.

    COMPLETE is a syntactic outcome assertion, NOT cold M11 authenticity:
    the existing independent archive/M11 postflight must verify SQLite,
    constructor provenance and the true run event. FAILURES stay FAILED.
    """
    ctx = _context(context)
    root = _root(spool_root)
    slot = root / ctx["identity"]
    if not slot.is_dir() or slot.is_symlink() or slot.resolve() != slot:
        raise ValueError("original slot missing, linked or replaced")
    n, status, head, state = _outcome(result, receipt)
    # A directory flock survives report replacement and serializes concurrent
    # terminal writers without adding an unregistered lock file to the archive.
    lockfd = os.open(slot, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(lockfd, fcntl.LOCK_EX)
        pending = _report(ctx, result=_PENDING, status="technical_failure",
                          generation=0, head=None, state_hash=None)
        if _read_regular(slot / "report.json") != canonical_bytes(pending):
            raise ValueError("original already finalized or pending provenance changed")
        allowed = {"report.json", "life.sqlite", "life.sqlite-wal", "life.sqlite-shm"}
        found = set(os.listdir(slot))
        if not {"report.json"} <= found or not found <= allowed:
            raise ValueError("unaccounted original custody sidecar")
        if result == "COMPLETE":
            sqlite = slot / "life.sqlite"
            if not sqlite.is_file() or sqlite.is_symlink():
                raise ValueError("claimed complete original lacks unlinked M11 SQLite")
            st = sqlite.lstat()
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                raise ValueError("claimed original M11 SQLite is not unique")
        for name in found - {"report.json"}:
            s = (slot / name).lstat()
            if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1:
                raise ValueError("original custody sidecar has an alias")
        final = _report(ctx, result=result, status=status,
                        generation=n, head=head, state_hash=state)
        if set(final) != FRAGMENT_FIELDS:
            raise ValueError("original terminal schema mismatch")
        # A temporary file is never silently reused. If interrupted, extras
        # fail the downstream archive guard instead of replacing a life.
        fd, temp = tempfile.mkstemp(prefix=".terminal-", dir=slot)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(canonical_bytes(final))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, slot / "report.json")
            _sync_dir(slot)
        except BaseException:
            # Failure to finalize preserves the existing pending or terminal
            # original, and no second birth is possible.
            if os.path.exists(temp):
                os.unlink(temp)
            raise
    finally:
        os.close(lockfd)
    return {
        "scope": _SCOPE, "identity": ctx["identity"],
        "result": result, "generation": n, "status": status,
        "bytes_from_M11_independently_verified": False,
        "external_run_attested": False,
        "study_admissible": False, "general_L3": "NOT_ESTABLISHED",
    }
