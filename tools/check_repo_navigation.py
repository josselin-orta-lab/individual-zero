#!/usr/bin/env python3
"""Static, read-only sanity check for agent-facing repository entrypoints.

Never executes the engine or scientific experiments. Standard library only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = (
    "README.md", "AGENTS.md", "CONTRIBUTING.md", "RESEARCH_MAP.md",
    "docs/README.md", "docs/engineering/AGENT_NAVIGATION.md",
    "docs/engineering/START_HERE.md", "docs/architecture/README.md",
    "docs/architecture/ENGINE_GENERATIONS.md",
    "docs/presentation/01-project-overview.md",
    "docs/presentation/02-repository-tour.md",
    "docs/presentation/04-contributor-first-hour.md",
    "docs/research/README.md", "src/i1/AGENTS.md",
    "src/i1/README.md", "src/i1/docs/README.md", "src/i1/docs/STATUS.md",
    "src/i2/AGENTS.md", "src/i2/README.md",
    "src/i2/docs/README.md", "src/i2/docs/STATUS.md",
    "src/i2/docs/ARCHITECTURE.md", ".github/PULL_REQUEST_TEMPLATE.md",
)
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
NO_LAB = ("src/lab/",)
STALE = ("Experimental code may remain experimental until results justify integration into I0.",
         "No scientific question is formally registered yet.",
         "Lab observes. Adapters connect. I0 operates.")


def inspect(root: Path = ROOT, scope: str = "entrypoints") -> dict:
    root = root.resolve()
    errors = []
    checked = 0
    registry_path = root / "config/engine-registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if registry["active_generation"] != "I1":
            errors.append("active generation differs from I1; update checker assumptions")
        if "I2" in registry.get("generations", {}):
            errors.append("I2 unexpectedly registered")
        for generation in ("i1", "i2"):
            contract = json.loads((root / f"src/{generation}/engine.json").read_text(encoding="utf-8"))
            if contract.get("paths", {}).get("documentation") != f"src/{generation}/docs":
                errors.append(f"{generation}: wrong documentation owner in engine contract")
            if generation == "i2" and contract.get("entrypoints"):
                errors.append("I2 proposal unexpectedly declares execution entrypoints")
        checked += 3
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"cannot read registry/contracts: {exc}")

    paths = ENTRYPOINTS
    if scope == "all":
        paths = tuple(sorted(p.relative_to(root).as_posix()
                             for base in ("docs", "src/i1/docs", "src/i2/docs")
                             for p in (root / base).rglob("*.md"))) + ENTRYPOINTS
    for relative in sorted(set(paths)):
        path = root / relative
        if not path.is_file():
            errors.append(f"missing entrypoint: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        checked += 1
        if scope == "entrypoints" and relative in (
                "CONTRIBUTING.md", "docs/presentation/04-contributor-first-hour.md"):
            for phrase in STALE:
                if phrase in content:
                    errors.append(f"{relative}: stale instruction: {phrase}")
            if "src/lab/" in content and "no active" not in content.lower():
                errors.append(f"{relative}: obsolete shared Lab destination")
        for found in LINK.finditer(content):
            href = found.group(1).strip().strip("<>")
            if href.startswith(("https://", "http://", "mailto:", "data:", "/")):
                continue
            target = href.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(root):
                errors.append(f"{relative}: link escapes repository: {href}")
            elif not resolved.exists():
                errors.append(f"{relative}: broken local link: {href}")
            checked += 1
    for generation in ("i1", "i2"):
        current = root / f"src/{generation}/docs/STATUS.md"
        history = root / f"src/{generation}/docs/STATUS_HISTORY.md"
        if not history.is_file():
            errors.append(f"{generation}: missing preserved historical status")
        if current.is_file() and len(current.read_text(encoding="utf-8").splitlines()) > 100:
            errors.append(f"{generation}: current STATUS.md should be a short routing surface")
    return {"status": "PASS" if not errors else "FAIL",
            "scope": scope, "checks": checked, "errors": sorted(set(errors)),
            "scientific_gate": "NOT_EVALUATED"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("entrypoints", "all"), default="entrypoints")
    args = parser.parse_args()
    result = inspect(scope=args.scope)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
