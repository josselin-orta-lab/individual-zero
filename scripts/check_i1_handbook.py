#!/usr/bin/env python3
"""Validate I1 handbook links, file references and registered engine paths.

Static integrity checking only: never execute a documented command or infer
scientific evidence. Standard-library-only on Python 3.11 and 3.12.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE = re.compile(r"`([^`\n]+)`")
PATH = re.compile(r"^(?:src/i1/|src/i0/|archive/i0/|tests/|scripts/|tools/|config/|docs/|\.github/|runtime/|modules/|lab/|\.\./|\.\./\.\./|\.\./\.\./\.\./)[^\s]+$")
SUFFIX = (".py", ".json", ".md", ".yml", ".yaml")
REQUIRED = ("README.md", "THEORY.md", "COGNITIVE_FLOW.md",
            "EVIDENCE_MATRIX.md", "DEVELOPMENT_PLAYBOOK.md",
            "OBSERVABILITY.md", "ARCHITECTURE.md", "STATUS.md",
            "TEST_PLAN.md", "WORLD_PRESETS.md", "NEEDS_AND_ACTION.md",
            "MEMORY_AND_LEARNING.md", "CONSOLIDATION_AND_PUBLICATION.md",
            "MORTALITY_AND_M11.md", "EXPERIMENT_PROTOCOL.md",
            "UC_AND_SCHEDULING.md")


def inspect(root: Path = ROOT) -> dict:
    root = root.resolve()
    docs = root / "src/i1/docs"
    errors: list[str] = []
    checks = 0
    try:
        contract = json.loads((root / "src/i1/engine.json").read_text(encoding="utf-8"))
        registry = json.loads((root / "config/engine-registry.json").read_text(encoding="utf-8"))
        if contract["generation"] != "I1" or contract["paths"]["documentation"] != "src/i1/docs":
            errors.append("I1 contract points outside canonical documents")
        if contract["scientific"]["evidence_index"] != "src/i1/docs/EVIDENCE_MATRIX.md":
            errors.append("I1 evidence index diverges")
        if registry["active_generation"] != "I1":
            errors.append("registry active generation differs from I1")
        checks += 3
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append("engine contract unreadable: " + str(exc))
    start = docs / "README.md"
    index = start.read_text(encoding="utf-8") if start.is_file() else ""
    for name in REQUIRED:
        p = docs / name
        checks += 2
        if not p.is_file():
            errors.append("missing canonical document: " + name)
        if name != "README.md" and f"]({name})" not in index:
            errors.append("handbook index missing link: " + name)
    for file in sorted(docs.glob("*.md")):
        data = file.read_text(encoding="utf-8")
        for target in LINK.findall(data):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            checks += 1
            dest = (file.parent / target).resolve()
            if not dest.is_relative_to(root) or not dest.exists():
                errors.append(f"{file.relative_to(root)}: broken link {target}")
        for raw in CODE.findall(data):
            raw = raw.split("::", 1)[0]
            if not (raw.endswith(SUFFIX) or raw.endswith("/")):
                continue
            if not PATH.fullmatch(raw):
                continue
            checks += 1
            if raw.startswith(("runtime/", "modules/", "lab/")):
                dest = root / "src/i1" / raw
            elif raw.startswith("../"):
                dest = file.parent / raw
            else:
                dest = root / raw
            dest = dest.resolve()
            if not dest.is_relative_to(root) or not dest.exists():
                errors.append(f"{file.relative_to(root)}: missing source path {raw}")
    return {"status": "PASS" if not errors else "FAIL",
            "documents": len(list(docs.glob("*.md"))),
            "checks": checks, "errors": sorted(set(errors)),
            "scientific_gate": "NOT_EVALUATED"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = inspect()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["status"], result["checks"], "checks")
        for error in result["errors"]:
            print(error)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
