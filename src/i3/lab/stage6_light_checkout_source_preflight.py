"""Read-only checkout/source pin verifier for *unexecuted* Stage-6-light.

No I3/runtime imports, Worlds, genomes, allocation, or automatic admission.
The caller must provide externally fixed expected hashes. Equal self-declared
hashes alone are not proof of an independent timestamp or owner permission.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

METHOD = (Path(__file__).resolve().parents[1] / "docs/studies/"
          "stage6-light-preparation/STAGE6_LIGHT_PROTOCOL_METHOD_V1.json")
SOURCE_ROOT = "src/i3"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
DENIED = (
    "worlds_allowed", "cohorts_allowed", "engineering_rehearsal_allowed",
    "science_admission_allowed", "auto_start_allowed", "adr0017_lineage_exception_accepted",
)
UNASSIGNED = (
    "owner_decision_sha", "owner_authorized_world_indices",
    "assigned_world_seeds", "assigned_founder_seeds", "execution_source_sha",
    "execution_transport_fingerprint", "independent_allocation_manifest_sha256",
    "full_scale_python311_rehearsal_sha", "full_scale_python312_rehearsal_sha",
)


def _is_hex(value: object, length: int) -> bool:
    return type(value) is str and (HEX40 if length == 40 else HEX64).fullmatch(value) is not None


def _canonical_digest(obj: object) -> str:
    # Exact canonicalization from i3.runtime.provenance.digest; independently
    # implemented here to avoid importing the live runtime.
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return sha256(raw).hexdigest()


def _check_method(method: dict) -> None:
    if (type(method) is not dict or
            method.get("schema") != "i3-stage6-light-method-preauth/v1" or
            method.get("protocol_id") != "I3_STAGE6_LIGHT_METHOD_V1" or
            method.get("status") != "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE" or
            method.get("phase") != "design_only" or
            method.get("scientific_verdict") != "NOT_ISSUED"):
        raise PermissionError("method is not the non-executable Stage-6-light v1")
    auth = method.get("authorization")
    if (type(auth) is not dict or set(auth) != set(DENIED + UNASSIGNED) or
            any(auth[key] is not False for key in DENIED) or
            any(auth[key] is not None for key in UNASSIGNED)):
        raise PermissionError("method must deny every owner, index and World grant")
    custody = method.get("custody")
    if (type(custody) is not dict or
            custody.get("scientific_worlds_and_lives_now_allowed") is not False or
            custody.get("rehearsal_worlds_and_lives_now_allowed") is not False or
            custody.get("per_generation_selection_requires_separate_adr0017_acceptance") is not True):
        raise PermissionError("live lineage G/S/R not admitted by ADR-0017")


def _git(root: Path, *args: str) -> bytes:
    try:
        proc = subprocess.run(("git", "-C", str(root), *args), capture_output=True,
                              timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("git evidence unavailable") from exc
    if proc.returncode != 0:
        raise ValueError("git evidence command failed")
    return proc.stdout


def _safe_source_path(name: object) -> bool:
    if type(name) is not str or not name or "\\" in name or "\x00" in name:
        return False
    p = PurePosixPath(name)
    return (not p.is_absolute() and not any(part in ("", ".", "..") for part in name.split("/"))
            and p.suffix == ".py" and not any(part.startswith(".") for part in p.parts)
            and p.as_posix() == name)


def verify_checkout_source(*, checkout_root: str | Path, source_record: dict,
                           expected_git_head: str, expected_source_sha256: str,
                           expected_method_sha256: str,
                           method_path: str | Path = METHOD) -> dict:
    """Bind one *claimed* run_life.source_snapshot to committed checkout bytes.

    External pins must be supplied separately from the record being checked.
    Checks all .py files under src/i3, Git HEAD tree and the unmodified checkout.
    It does not run life, attest a timestamp, certify World independence or grant
    authorization. Method bytes are pinned before any source-tree access.
    """
    for name, val, size in (
        ("git HEAD", expected_git_head, 40),
        ("source", expected_source_sha256, 64),
        ("method", expected_method_sha256, 64),
    ):
        if not _is_hex(val, size):
            raise ValueError(f"external {name} pin required")
    method_file = Path(method_path)
    if not method_file.is_file() or method_file.is_symlink():
        raise PermissionError("method file must be a local regular file")
    method_bytes = method_file.read_bytes()
    if sha256(method_bytes).hexdigest() != expected_method_sha256:
        raise PermissionError("externally pinned method bytes do not match")
    try:
        method = json.loads(method_bytes)
    except (ValueError, UnicodeError) as exc:
        raise PermissionError("unreadable pinned method") from exc
    _check_method(method)

    if (type(source_record) is not dict or
            set(source_record) != {"files", "sha256", "git_head", "working_tree_dirty"} or
            source_record["sha256"] != expected_source_sha256 or
            source_record["git_head"] != expected_git_head or
            source_record["working_tree_dirty"] is not False):
        raise ValueError("claimed native source does not match external pins")
    declared = source_record["files"]
    if (type(declared) is not dict or not declared or
            any(not _safe_source_path(k) or not _is_hex(v, 64)
                for k, v in declared.items()) or
            _canonical_digest(declared) != expected_source_sha256):
        raise ValueError("source manifest is incomplete, unsafe or self-inconsistent")

    root = Path(checkout_root).resolve(strict=True)
    source = root / SOURCE_ROOT
    if not source.is_dir() or source.is_symlink():
        raise ValueError("expected source directory absent or redirected")
    if _git(root, "rev-parse", "--show-toplevel").decode().strip() != str(root):
        raise ValueError("source is not the expected Git repository root")
    if _git(root, "rev-parse", "HEAD").decode().strip() != expected_git_head:
        raise ValueError("checkout HEAD differs from external prospective pin")
    if _git(root, "status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("checkout is not clean, including untracked sources")

    present: dict[str, str] = {}
    for file in source.rglob("*.py"):
        if file.is_symlink() or any(parent.is_symlink() for parent in file.parents if parent != root):
            raise ValueError("Python source symlink is not a fixed source byte sequence")
        if not file.is_file():
            raise ValueError("nonregular Python source")
        name = file.relative_to(source).as_posix()
        if not _safe_source_path(name):
            raise ValueError("unsafe Python module name")
        content = file.read_bytes()
        present[name] = sha256(content).hexdigest()
        if declared.get(name) != present[name]:
            raise ValueError("checkout file differs from native source claim")
        # Verify Git HEAD actually owns these exact bytes, not just a local
        # self-consistent checksum or a path marked assume-unchanged.
        git_bytes = _git(root, "show", f"HEAD:{SOURCE_ROOT}/{name}")
        if git_bytes != content:
            raise ValueError("Git HEAD source differs from current bytes")
    if present != declared:
        raise ValueError("native manifest omits a Python file or adds a phantom file")
    if _canonical_digest(present) != expected_source_sha256:
        raise ValueError("native source root digest differs from the external pin")
    return {
        "status": "CHECKOUT_BYTES_MATCH_EXTERNAL_PINS_PREAUTH_ONLY",
        "source_file_count": len(present),
        "git_head": expected_git_head,
        "source_sha256": expected_source_sha256,
        "method_sha256": expected_method_sha256,
        "source_bytes_against_checkout_verified": True,
        "git_head_tree_bytes_verified": True,
        "external_pre_execution_timestamp_attested": False,
        "source_or_method_independently_authenticated": False,
        "owner_authorization": False,
        "worlds_opened": 0,
        "lives_executed": 0,
        "scientific_verdict": "NOT_ISSUED",
    }


def run_life(*_args, **_kwargs):
    raise PermissionError("source preflight cannot run any life")


def open_world(*_args, **_kwargs):
    raise PermissionError("source preflight cannot open a World")


def authorize_science(*_args, **_kwargs):
    raise PermissionError("source preflight cannot grant Stage-6 admission")
