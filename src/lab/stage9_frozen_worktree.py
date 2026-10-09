"""Read-only pre-run worktree integrity check for a Stage-9 frozen commit.

Checks source bytes on disk, not just the Git commit graph. A successful check
does NOT attest actual runtime or scientific acceptance (EN v1.2.1, INV-32/33).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat

from .stage9_registration_chronology import (
    PROJECT_INSTALL_PATH, SOURCE_TREE_PATH, _check_commit, _git,
)

# Cache and packaging metadata are explicitly excluded from this preflight.
# They need separate runtime custody; all other unexpected source paths fail.
ALLOWED_GENERATED_SOURCE_DIRECTORIES = frozenset({"__pycache__"})


def verify_frozen_worktree(
    *, repository: Path, frozen_implementation_commit: str,
) -> dict[str, object]:
    """Reject modified, staged, untracked or byte-different runnable source.

    HEAD may contain later registration/evidence commits, but its src/ tree
    and pyproject.toml must remain identical to the immutable frozen commit.
    No worktree, index, source, registration or result is modified.
    """
    root = repository.resolve()
    top = Path(_git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if top != root:
        raise ValueError("source preflight requires the Git worktree root")
    _check_commit(root, frozen_implementation_commit)

    expected_tree = _git(
        root, "rev-parse", f"{frozen_implementation_commit}:{SOURCE_TREE_PATH}",
    ).strip()
    expected_package = _git(
        root, "rev-parse", f"{frozen_implementation_commit}:{PROJECT_INSTALL_PATH}",
    ).strip()
    if _git(root, "cat-file", "-t", expected_tree.decode()).strip() != b"tree":
        raise ValueError("frozen source path is not a Git tree")
    if _git(root, "cat-file", "-t", expected_package.decode()).strip() != b"blob":
        raise ValueError("frozen package manifest is not a Git blob")

    current_head = _git(root, "rev-parse", "HEAD").decode().strip()
    for path, expected, description in (
        (SOURCE_TREE_PATH, expected_tree, "source tree"),
        (PROJECT_INSTALL_PATH, expected_package, "package manifest"),
    ):
        if _git(root, "rev-parse", f"HEAD:{path}").strip() != expected:
            raise ValueError(f"current HEAD differs from frozen {description}")

    # Git porcelain catches index changes, unstaged changes, and unignored
    # untracked files. Raw blob comparisons below additionally reject bytes
    # that local clean/smudge filters might otherwise normalize away.
    if _git(
        root, "status", "--porcelain=v1", "--untracked-files=all",
        "--", SOURCE_TREE_PATH, PROJECT_INSTALL_PATH,
    ):
        raise ValueError("frozen source or package has local Git changes")

    manifest = _git(
        root, "ls-tree", "-r", "-z", frozen_implementation_commit,
        "--", SOURCE_TREE_PATH, PROJECT_INSTALL_PATH,
    )
    tracked: set[str] = set()
    for entry in manifest.split(b"\0"):
        if not entry:
            continue
        try:
            info, path = entry.split(b"\t", 1)
            mode, kind, oid = info.split(b" ")
        except ValueError as exc:
            raise ValueError("malformed frozen Git tree entry") from exc
        if kind != b"blob":
            raise ValueError("unexpected non-blob frozen source entry")
        relative = os.fsdecode(path)
        if relative in tracked:
            raise ValueError("duplicate frozen source path")
        tracked.add(relative)
        file = root / relative
        # A constant symlink can lead to mutable, untracked code outside the
        # frozen source. This strict boundary refuses source symlinks.
        if file.is_symlink() or mode == b"120000":
            raise ValueError("source checkout contains an unverified symlink")
        if not file.is_file() or mode not in (b"100644", b"100755"):
            raise ValueError("frozen tracked source missing or unsupported")
        executable = bool(file.stat().st_mode & (
            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        ))
        if executable != (mode == b"100755"):
            raise ValueError("source executable mode differs from frozen Git")
        if file.read_bytes() != _git(root, "cat-file", "blob", oid.decode()):
            raise ValueError("physical source bytes differ from frozen Git blob")

    if not any(p.startswith(SOURCE_TREE_PATH + "/") for p in tracked):
        raise ValueError("no source files verified in frozen tree")
    if PROJECT_INSTALL_PATH not in tracked:
        raise ValueError("frozen package manifest not checked")

    src = root / SOURCE_TREE_PATH
    if not src.is_dir() or src.is_symlink():
        raise ValueError("frozen source directory is absent or replaced")
    for file in src.rglob("*"):
        if file.is_symlink():
            raise ValueError("untracked source symlink in frozen checkout")
        if not file.is_file():
            continue
        relative_path = file.relative_to(root)
        if relative_path.as_posix() in tracked:
            continue
        # Git-ignored compiled caches and editable-install metadata may exist
        # after Python/import/install. These files remain UNATTESTED, and are
        # explicitly called out as such in the result and protocol. Any other
        # source-tree addition, even a shell script with no usual extension,
        # must fail instead of silently changing what the Python process uses.
        if any(
            part in ALLOWED_GENERATED_SOURCE_DIRECTORIES
            or part.endswith(".egg-info")
            for part in relative_path.parts[1:-1]
        ):
            continue
        raise ValueError("untracked source path in frozen checkout")

    return {
        "worktree_status": "frozen_tracked_code_matches_local_checkout",
        "git_head": current_head,
        "frozen_implementation_commit": frozen_implementation_commit,
        "source_tree_sha": expected_tree.decode(),
        "pyproject_blob_sha": expected_package.decode(),
        "verified_tracked_files": len(tracked),
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "outstanding": [
            "independently witness the precise checkout actually executed",
            "attest ignored compiled caches, dependencies and runtime environment",
            "audit physical worlds, raw journals, oracle and prospective registration",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage-9 local source integrity preflight, never Golden",
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--frozen-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(verify_frozen_worktree(
        repository=args.repo, frozen_implementation_commit=args.frozen_commit,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
