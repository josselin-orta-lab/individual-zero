#!/usr/bin/env python3
"""Exact I1 generated-artifact comparison against the last pre-M11 migration.

The reference is a pinned *current* I1 software commit immediately preceding
the native M11 move, not a historical broken experimental cohort or scientific
oracle. Verify all generated Python bytes and namespace identities. The source
manifest provenance is intentionally NOT compared: that is what migration
changes. No network requests, state mutation, or older living-world replay.
"""
from __future__ import annotations

import argparse
import difflib
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def _build(root: Path, output: Path) -> dict[str, str]:
    script = root / "scripts" / "build_i1_fork.py"
    if not script.is_file():
        raise RuntimeError(f"missing independent I1 builder: {script}")
    p = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=str(root), text=True, capture_output=True, check=False,
    )
    if p.returncode:
        raise RuntimeError(
            f"I1 build failed ({root}):\n{p.stdout}\n{p.stderr}"
        )
    manifest = json.loads((output / "i1_build_manifest.json").read_text())
    observed = {}
    for rel, details in manifest["files"].items():
        path = output / rel
        if not path.is_file():
            raise AssertionError(f"manifest references missing module: {rel}")
        digest = sha256(path.read_bytes()).hexdigest()
        if digest != details["built_sha256"]:
            raise AssertionError(f"incorrect generated SHA256 for {rel}")
        observed[rel] = digest
    return observed


def verify(reference_root: Path) -> None:
    reference_root = reference_root.resolve()
    if reference_root == ROOT.resolve():
        raise ValueError("reference root must be an independent checkout")
    with TemporaryDirectory(prefix="i1-parity-") as folder:
        old_root = Path(folder) / "reference"
        new_root = Path(folder) / "native"
        old = _build(reference_root, old_root)
        new = _build(ROOT, new_root)
        missing = sorted(set(old) - set(new))
        added = sorted(set(new) - set(old))
        changed = sorted(
            rel for rel in old.keys() & new.keys() if old[rel] != new[rel]
        )
        if missing or added or changed:
            print(f"I1 byte-parity FAIL: missing={missing} added={added}"
                  f" changed={changed}", file=sys.stderr)
            for rel in changed[:3]:
                former = (old_root / rel).read_text().splitlines(keepends=True)
                native = (new_root / rel).read_text().splitlines(keepends=True)
                diff = difflib.unified_diff(
                    former, native, fromfile=f"before/{rel}",
                    tofile=f"native/{rel}", n=3,
                )
                print("".join(list(diff)[:100]), file=sys.stderr)
            raise AssertionError("native migration changed generated I1 bytes")
        print(f"I1_GENERATED_PARITY_OK: {len(new)} identical Python source files")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    args = parser.parse_args()
    verify(args.reference_root)


if __name__ == "__main__":
    main()
