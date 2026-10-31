#!/usr/bin/env python3
"""Static, read-only sanity check for agent-facing repository entrypoints.

Never executes the engine or scientific experiments. Standard library only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = (
    "README.md", "AGENTS.md", "CONTRIBUTING.md", "RESEARCH_MAP.md",
    "docs/README.md", "docs/engineering/AGENT_NAVIGATION.md",
    "docs/engineering/START_HERE.md", "docs/architecture/README.md",
    "docs/architecture/ENGINE_GENERATIONS.md",
    "docs/architecture/ATLAS.md",
    "docs/architecture/proposals/README.md",
    "docs/presentation/01-project-overview.md",
    "docs/presentation/02-repository-tour.md",
    "docs/presentation/04-contributor-first-hour.md",
    "docs/research/README.md", "src/i1/AGENTS.md",
    "src/i1/README.md", "src/i1/docs/README.md", "src/i1/docs/STATUS.md",
    "src/i2/AGENTS.md", "src/i2/README.md",
    "src/i2/docs/README.md", "src/i2/docs/STATUS.md",
    "src/i2/docs/ARCHITECTURE.md", ".github/PULL_REQUEST_TEMPLATE.md",
)
CURRENT_EXTRA = (
    "docs/architecture/reference/README.md",
    "docs/architecture/reference/en/README.md",
    "docs/architecture/reference/fr/README.md",
    "docs/research/experiment-lifecycle.md",
    "docs/research/experiments-vs-tests.md",
    "docs/research/glossary.md", "docs/research/rai.md",
    "docs/research/reproducibility.md", "docs/research/results-guidance.md",
    "src/i1/architecture/README.md", "src/i1/config/README.md",
    "src/i1/interfaces/README.md", "src/i1/lab/README.md",
    "src/i1/modules/README.md",
    "src/adapters/README.md", "observer/README.md",
)
CURRENT_DIRS = (
    "docs/presentation", "docs/engineering", "docs/governance",
    "docs/decisions", "examples", "src/i1/docs", "src/i2/docs",
)
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
NO_LAB = ("src/lab/",)
STALE = ("Experimental code may remain experimental until results justify integration into I0.",
         "No scientific question is formally registered yet.",
         "Lab observes. Adapters connect. I0 operates.")


def is_historical(path: str) -> bool:
    # The proposals/ index is a current route; its dated proposals are archival.
    if path == "docs/architecture/proposals/README.md":
        return False
    if path.startswith(("archive/", "src/i0/", "docs/operations/",
                        "docs/architecture/proposals/")):
        return True
    if path.startswith(("docs/architecture/IMPLEMENTATION_MAP",
                        "docs/architecture/TECHNICAL_DECISIONS")):
        return True
    if path in ("docs/architecture/I0_OVERVIEW.md",
                "docs/architecture/BOOTSTRAP_RUNTIME.md"):
        return True
    if path.startswith("docs/architecture/reference/") and path.endswith(".md"):
        return path not in CURRENT_EXTRA
    if path.startswith("docs/research/"):
        return path not in CURRENT_EXTRA and path != "docs/research/README.md"
    if path.startswith("src/i1/docs/"):
        name = path.removeprefix("src/i1/docs/")
        return name.startswith(("STATUS_HISTORY", "EXPERIMENT_", "ISSUE_",
                                "I1_ECO_", "SCIENTIFIC_LEARNING_AUDIT",
                                "STAGE10_PAID_", "I1_WAKE_CUE_", "research/"))
    return path == "src/i2/docs/STATUS_HISTORY.md"


def source_paths(root: Path, scope: str) -> tuple[str, ...]:
    if scope == "entrypoints":
        return ENTRYPOINTS
    if scope == "all":
        return tuple(sorted({*ENTRYPOINTS,
                             *(p.relative_to(root).as_posix()
                               for p in root.rglob("*.md") if ".git" not in p.parts)}))
    found = set(ENTRYPOINTS) | set(CURRENT_EXTRA)
    for dirname in CURRENT_DIRS:
        found.update(p.relative_to(root).as_posix()
                     for p in (root / dirname).rglob("*.md")
                     if not is_historical(p.relative_to(root).as_posix()))
    return tuple(sorted(found))


def inspect(root: Path = ROOT, scope: str = "entrypoints", strict_historical: bool = False) -> dict:
    root = root.resolve()
    errors = []
    warnings = []
    checked = 0
    registry_path = root / "config/engine-registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if registry["active_generation"] not in registry["generations"]:
            errors.append("active generation absent from engine registry")
        for generation in ("i1", "i2"):
            contract = json.loads((root / f"src/{generation}/engine.json").read_text(encoding="utf-8"))
            if contract.get("paths", {}).get("documentation") != f"src/{generation}/docs":
                errors.append(f"{generation}: wrong documentation owner in engine contract")
            if contract.get("status") == "proposal" and contract.get("entrypoints"):
                errors.append(f"{generation}: proposal unexpectedly declares execution entrypoints")
            if (contract.get("status") == "proposal"
                    and contract.get("generation") in registry.get("generations", {})):
                errors.append(f"{generation}: inactive proposal unexpectedly registered")
        checked += 3
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"cannot read registry/contracts: {exc}")

    paths = source_paths(root, scope)
    for relative in sorted(set(paths)):
        path = root / relative
        target_errors = warnings if is_historical(relative) and not strict_historical else errors
        if not path.is_file():
            target_errors.append(f"missing entrypoint: {relative}")
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
        clean = re.sub(r"(?ms)^\s*(?:\x60){3,}[^\n]*\n.*?^\s*(?:\x60){3,}[^\n]*\n",
                       "", content)
        for found in LINK.finditer(clean):
            href = found.group(1).strip().strip("<>")
            if href.startswith(("https://", "http://", "mailto:", "data:", "/")):
                continue
            target = unquote(href.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(root):
                target_errors.append(f"{relative}: link escapes repository: {href}")
            elif not resolved.exists():
                target_errors.append(f"{relative}: broken local link: {href}")
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
            "warnings": sorted(set(warnings)),
            "scientific_gate": "NOT_EVALUATED"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("entrypoints", "current", "all"), default="entrypoints")
    parser.add_argument("--strict-historical", action="store_true")
    args = parser.parse_args()
    result = inspect(scope=args.scope, strict_historical=args.strict_historical)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
