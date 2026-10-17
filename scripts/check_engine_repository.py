#!/usr/bin/env python3
"""Fail-closed, dependency-free guard of the registered engine boundaries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def check():
    errors = []
    registry = json.loads((ROOT / "config/engine-registry.json").read_text())
    manifest = json.loads((ROOT / registry["archive_manifest"]).read_text())
    if registry["schema"] != "individual-zero-engine-registry/v1":
        errors.append("unknown registry schema")
    if manifest["schema"] != "individual-zero-archived-sources/v1":
        errors.append("unknown archive schema")
    if registry["active_generation"] != "I1":
        errors.append("active generation must be I1")
    generations = registry["generations"]
    for name, entry in generations.items():
        if not (ROOT / entry["source"]).is_dir():
            errors.append(name + ": source directory missing")
    frozen = generations["I0"]
    for path, expected in (
        (frozen["source"], frozen["source_tree_sha"]),
        (frozen["lab"], frozen["lab_tree_sha"]),
    ):
        observed = git("rev-parse", "HEAD:" + path)
        if observed != expected:
            errors.append(path + ": frozen reference tree changed: " + observed)
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT
        )
        if dirty.returncode:
            errors.append(path + ": uncommitted reference modification")
    active = generations["I1"]
    if not (ROOT / active["lab"] / "__init__.py").is_file():
        errors.append("I1 must own an importable generation-scoped Lab")
    if (ROOT / "src/lab").exists():
        errors.append("unscoped shared src/lab is forbidden")
    if frozen["lab"] == active["lab"]:
        errors.append("engines cannot share one Lab")
    entries = manifest["entries"]
    if len(entries) != len({row["source"] for row in entries}):
        errors.append("duplicate archived source path")
    if len(entries) != len({row["archived"] for row in entries}):
        errors.append("duplicate archived destination path")
    counts = {
        "workflows": sum(x["source"].startswith(".github/workflows/") for x in entries),
        "tests": sum(x["source"].startswith("tests/") for x in entries),
    }
    if counts != manifest["counts"]:
        errors.append("archive counts changed")
    for item in entries:
        path = ROOT / item["archived"]
        if not path.is_file():
            errors.append("archive file missing: " + item["archived"])
            continue
        if path.stat().st_size != item["bytes"]:
            errors.append("size mismatch: " + item["archived"])
        raw = path.read_bytes()
        # Git blob identity proves content preserved byte-for-byte.
        import hashlib
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()
        if actual != item["blob_sha"]:
            errors.append("modified archived Git blob: " + item["archived"])
        if (ROOT / item["source"]).exists():
            errors.append("historical file unexpectedly active: " + item["source"])
    for key in ("lab", "overlays", "build", "tester", "ci", "frozen_reference_guard"):
        if not (ROOT / active[key]).exists():
            errors.append("I1 missing " + key + ": " + active[key])
    old = sorted((ROOT / ".github/workflows").glob("*.yml"))
    allowed = set([Path(active["ci"]).name, "i0-archive-manual.yml", "engine-structural.yml", "i1-preset-worlds.yml"])
    if Path(active["ci"]).name not in {p.name for p in old}:
        errors.append("missing active I1 workflow")
    unexpected = [x.name for x in old if not x.name.startswith("i1-") and x.name not in allowed]
    if unexpected:
        errors.append("unarchived historical workflows: " + ", ".join(unexpected))
    result = {"status": "FAIL" if errors else "PASS", "active_generation": registry["active_generation"],
              "archived": counts, "errors": errors}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = check()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
