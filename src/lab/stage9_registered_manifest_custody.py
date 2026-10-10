"""Read-only byte custody for preregistered Stage-9 physical manifests.

The external bench supplies its original world+layout+scenario manifests, plus
the world generator, equipment, parameter registry and ontology manifests.
This audit compares *file bytes* to immutable digests declared prospectively.
It never certifies generator semantics, physical independence, access to
unseen outcomes, actual executable provenance, INV-25 or a Golden.

Normative context: EN MVP v1.2.1 §§13.2, 19.5 and 20.3, INV-25/32/33.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex
from .stage9_scientific_preregistration import (
    load_registration, validate_registration,
)


INDEX_VERSION = "stage9-registered-physical-manifest-index-v1"
INDEX_FIELDS = frozenset({
    "protocol_version", "registration_digest", "frozen_manifests",
    "calibration_worlds", "holdout_worlds",
})
FROZEN_MANIFEST_DIGESTS = {
    "world_generator": "world_generator_sha256",
    "equipment": "equipment_sha256",
    "parameter_registry": "parameter_registry_sha256",
    "ontology": "ontology_sha256",
}


def _reject_duplicate_manifest_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    values: dict[str, object] = {}
    for key, value in pairs:
        if key in values:
            raise ValueError(f"duplicate physical manifest index JSON key: {key}")
        values[key] = value
    return values


def _reject_nonfinite_manifest_constant(value: str) -> None:
    raise ValueError(f"non-finite physical manifest index JSON constant: {value}")


def load_manifest_index(path: Path) -> dict[str, object]:
    """Reject duplicate keys/nonfinite JSON before any file access."""
    index = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_manifest_keys,
        parse_constant=_reject_nonfinite_manifest_constant,
    )
    if not isinstance(index, dict):
        raise ValueError("physical manifest index must be a JSON object")
    return index


def _root_without_aliases(path: Path) -> Path:
    absolute = path.absolute()
    if any(part.is_symlink() for part in (absolute, *absolute.parents)):
        raise ValueError("physical manifest custody root may not be a symlink")
    resolved = absolute.resolve()
    if not resolved.is_dir():
        raise ValueError("physical manifest custody root must be a directory")
    return resolved


def _file_without_aliases(root: Path, supplied: object) -> Path:
    if not isinstance(supplied, str) or not supplied.strip():
        raise ValueError("physical manifest path must be a nonempty string")
    # '.' and '..' are forbidden before Path normalizes them away.
    if (
        supplied.startswith("/")
        or any(part in {"", ".", ".."} for part in supplied.split("/"))
    ):
        raise ValueError("physical manifest path must be traversal-free and relative")
    relative = Path(supplied)
    if relative.is_absolute() or not relative.parts:
        raise ValueError("physical manifest path must be relative")
    candidate = root
    for part in relative.parts:
        candidate /= part
        if candidate.is_symlink():
            raise ValueError("physical manifest path may not traverse symlinks")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("physical manifest path escapes the custody root") from exc
    if not resolved.is_file():
        raise ValueError("missing physical manifest file")
    return resolved


def _hash_bytes(path: Path) -> tuple[str, int]:
    """Hash a regular file through no-follow directory and file descriptors.

    Checking is_symlink() only before Path.open() leaves a TOCTOU gap: an
    attacker can replace the leaf or a parent with a symlink just before the
    actual open. Open every directory component relative to its already-open
    parent, with O_NOFOLLOW, and check the leaf with fstat. This remains only
    a local filesystem check, never a signature or external custody witness.
    """
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("physical manifest custody requires no-follow file opens")
    absolute = path.absolute()
    parts = absolute.parts
    if len(parts) < 2:
        raise ValueError("physical manifest path must identify a regular file")
    directory_flags = (
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        | getattr(os, "O_CLOEXEC", 0)
    )
    file_flags = (
        os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    directory_fd = None
    file_fd = None
    try:
        directory_fd = os.open(parts[0], directory_flags)
        for part in parts[1:-1]:
            nested_fd = os.open(part, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = nested_fd
        file_fd = os.open(parts[-1], file_flags, dir_fd=directory_fd)
        opened = os.fstat(file_fd)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("physical manifest is not a regular file")
        current = path.lstat()
        if (
            not stat.S_ISREG(current.st_mode)
            or (current.st_dev, current.st_ino)
            != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError("physical manifest changed during descriptor open")
        digest = sha256()
        size = 0
        with os.fdopen(file_fd, "rb") as stream:
            file_fd = None
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                digest.update(chunk)
            if os.fstat(stream.fileno()).st_size != size:
                raise ValueError("physical manifest size changed while reading")
        if not size:
            raise ValueError("empty physical manifest cannot establish file custody")
        return digest.hexdigest(), size
    except OSError as exc:
        raise ValueError("physical manifest path changed or traversed a symlink") from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if directory_fd is not None:
            os.close(directory_fd)


def audit_registered_manifest_files(
    *, registration: Mapping[str, object],
    index: Mapping[str, object],
    artifact_root: Path,
) -> dict[str, object]:
    """Check every declared frozen and physical-world file against its digest.

    This is necessary but not sufficient evidence of a legitimate prospective
    heldout design. File names, manifests, digests, and a local filesystem can
    all be fabricated by an actor who controls the experiment.
    """
    digest = validate_registration(registration)
    if not isinstance(index, dict) or set(index) != INDEX_FIELDS:
        raise ValueError("physical manifest index has missing or extra fields")
    if index["protocol_version"] != INDEX_VERSION:
        raise ValueError("physical manifest index version mismatch")
    if index["registration_digest"] != digest:
        raise ValueError("physical manifest index differs from registration")
    frozen = index["frozen_manifests"]
    calibration = index["calibration_worlds"]
    holdout = index["holdout_worlds"]
    if not isinstance(frozen, dict) or set(frozen) != set(FROZEN_MANIFEST_DIGESTS):
        raise ValueError("frozen manifest paths must cover exact registered roles")
    if (
        not isinstance(calibration, dict)
        or set(calibration) != set(registration["calibration_world_ids"])
        or not isinstance(holdout, dict)
        or set(holdout) != set(registration["holdout_world_ids"])
    ):
        raise ValueError("world manifest paths must cover each registered world")

    root = _root_without_aliases(artifact_root)
    filenames: set[Path] = set()
    inodes: set[tuple[int, int]] = set()
    pinned: list[tuple[str, Path, tuple[int, int], str]] = []
    total_bytes = 0
    count = 0

    for group, files, digests in (
        ("frozen", frozen, {
            role: registration[registration_key]
            for role, registration_key in FROZEN_MANIFEST_DIGESTS.items()
        }),
        ("calibration", calibration, registration["calibration_world_sha256"]),
        ("holdout", holdout, registration["holdout_world_sha256"]),
    ):
        for label in sorted(files):
            source = _file_without_aliases(root, files[label])
            metadata = source.stat()
            inode = (metadata.st_dev, metadata.st_ino)
            if source in filenames or inode in inodes:
                raise ValueError(
                    "physical manifest reused across registered worlds or roles"
                )
            filenames.add(source)
            inodes.add(inode)
            observed, size = _hash_bytes(source)
            if observed != digests[label]:
                raise ValueError(
                    f"{group} physical manifest digest mismatch: {label}"
                )
            pinned.append((files[label], source, inode, observed))
            total_bytes += size
            count += 1

    # Rehash after the complete sweep: a file replaced mid-audit must not
    # silently pass merely because its first read preceded the replacement.
    # This is not a filesystem signature or evidence of external custody.
    for relative, original_path, inode, expected in pinned:
        # Revalidate the *declared* path, not just the original inode.
        # Moving a file and replacing its old name with a symlink to that
        # same inode preserves stat() and SHA-256 but violates file custody.
        current_path = _file_without_aliases(root, relative)
        meta = current_path.stat()
        if (
            current_path != original_path
            or (meta.st_dev, meta.st_ino) != inode
            or _hash_bytes(current_path)[0] != expected
        ):
            raise ValueError("physical manifest changed during custody audit")

    return {
        "manifest_custody_status":
            "registered_manifest_bytes_match_requires_independent_review",
        "registration_digest": digest,
        "manifest_index_sha256": sha256_hex(canonical_causal_bytes(index)),
        "frozen_manifests_checked": len(FROZEN_MANIFEST_DIGESTS),
        "calibration_worlds_checked": len(calibration),
        "holdout_worlds_checked": len(holdout),
        "total_manifest_files_checked": count,
        "total_manifest_bytes_checked": total_bytes,
        "physical_world_semantics_attested": False,
        "world_generation_independence_attested": False,
        "heldout_seed_custody_attested": False,
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "outstanding": [
            "external review of the physical world, layout and scenario semantics",
            "independent custody and prospective selection of heldout seeds",
            "execute frozen code and verify real-world journal/Memory provenance",
            "review preregistration Git chronology and INV-25 independently",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare Stage-9 physical manifest bytes; never a Golden gate",
    )
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        audit_registered_manifest_files(
            registration=load_registration(args.registration),
            index=load_manifest_index(args.index),
            artifact_root=args.artifact_root,
        ),
        sort_keys=True, indent=2,
    ))


if __name__ == "__main__":
    main()
