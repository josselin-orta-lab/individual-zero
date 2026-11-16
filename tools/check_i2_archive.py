#!/usr/bin/env python3
"""Read-only, source-exact guard for the I2 research archive.

This tool neither imports I2 nor executes an engine. Git tree SHAs pin every
historical source/test byte, not merely a curated list of filenames.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "config/archives/i2-20261116.json"
ARCHIVE_DECISION = "docs/decisions/ADR-0023-i2-archived-in-place-i3-context-focus.md"
BASELINE = "9091387a24644865605520b4c42c3f997dce1e3d"
FROZEN = {
    "source": ("src/i2", "bd5d4f42832192f223531e0afdecb813e210ef05", 141),
    "tests": ("tests/i2", "e0709f39dc96f820656bf8b3d7157b0f2a6b2948", 158),
}
PINNED_BLOBS = {
    "contract": ("src/i2/engine.json", "4e04a1a89a91b617c659f9f2f3ee21d52b64b815"),
    "dated_status": ("src/i2/docs/STATUS.md", "23d6e907176bad93dcb29f45c080edb34fb6a9e0"),
}


def assess(manifest: dict, registry: dict, contract: dict,
           observed_trees: dict[str, str]) -> list[str]:
    """Compare data to immutable reviewed pins, with no source execution."""
    errors: list[str] = []
    if manifest.get("schema") != "individual-zero-archived-research-proposal/v1":
        errors.append("unknown archival manifest schema")
    if manifest.get("generation") != "I2" or manifest.get("disposition") != "ARCHIVED_IN_PLACE":
        errors.append("I2 must remain archived in place")
    if manifest.get("baseline_main_commit") != BASELINE:
        errors.append("original I2 baseline SHA was rewritten")
    if manifest.get("retained_at_original_paths") is not True:
        errors.append("archive must preserve original paths")
    if manifest.get("executable_activation") != "FORBIDDEN":
        errors.append("archive cannot permit I2 activation")
    if manifest.get("archive_entrypoint") != "archive/i2/README.md":
        errors.append("archive entrypoint was displaced")
    if manifest.get("governing_decision") != ARCHIVE_DECISION:
        errors.append("archive decision was changed without review")

    for key, (path, pinned_sha, count) in FROZEN.items():
        row = manifest.get(key)
        if not isinstance(row, dict) or (
            row.get("path"), row.get("git_tree_sha"), row.get("tracked_files")
        ) != (path, pinned_sha, count):
            errors.append(key + ": manifest pin differs from original historical tree")
        if observed_trees.get(path) != pinned_sha:
            errors.append(path + ": historical tree changed or disappeared")
    for key, (path, sha) in PINNED_BLOBS.items():
        row = manifest.get(key)
        if not isinstance(row, dict) or (row.get("path"), row.get("git_blob_sha")) != (path, sha):
            errors.append(key + ": historical blob pin changed")

    if registry.get("active_generation") != "I1":
        errors.append("archive cannot change I1 active engine")
    if registry.get("reference_generation") != "I3":
        errors.append("archive cannot displace I3 development reference")
    if "I2" in registry.get("generations", {}):
        errors.append("archived I2 cannot be silently registered")
    if contract.get("generation") != "I2" or contract.get("status") != "proposal":
        errors.append("I2 preserved proposal contract differs")
    if contract.get("entrypoints") != {} or contract.get("activation") != "NOT_REGISTERED_NOT_EXECUTABLE":
        errors.append("archived I2 cannot gain registered entrypoints")
    return errors


def git_tree(root: Path, path: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD:" + path], cwd=root,
        text=True, capture_output=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(f"cannot read original {path} tree: {result.stderr.strip()}")
    return result.stdout.strip()


def inspect(root: Path = ROOT) -> dict:
    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        registry = json.loads((root / "config/engine-registry.json").read_text(encoding="utf-8"))
        contract = json.loads((root / "src/i2/engine.json").read_text(encoding="utf-8"))
        observed = {path: git_tree(root, path) for path, _, _ in FROZEN.values()}
        errors = assess(manifest, registry, contract, observed)
        if not (root / "archive/i2/README.md").is_file():
            errors.append("missing I2 archive discovery portal")
        if not (root / ARCHIVE_DECISION).is_file():
            errors.append("missing I2 archival decision")
    except (ValueError, OSError, RuntimeError, TypeError) as exc:
        return {"status": "FAIL", "errors": ["cannot verify I2 original archive: " + str(exc)],
                "scientific_gate": "NOT_EVALUATED"}
    return {"status": "FAIL" if errors else "PASS",
            "disposition": "ARCHIVED_IN_PLACE", "baseline_sha": BASELINE,
            "trees": observed, "errors": errors, "scientific_gate": "NOT_EVALUATED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()
    result = inspect()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return int(result["status"] != "PASS")


if __name__ == "__main__":
    sys.exit(main())
