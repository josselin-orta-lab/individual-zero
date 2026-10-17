#!/usr/bin/env python3
"""Read-only pre-registration readiness review for a future engine.

This is *not* an activation tool and not a scientific GO gate. No imports of
candidate code, runtime birth, registry mutation, or test execution occur.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FUTURE = re.compile(r"I[2-9][0-9]*\Z")
SCHEMA = "individual-zero-engine-contract/v1"
OWNED_DIRS = ("lab", "modules", "runtime", "config")
OWNED_DOCS = ("STATUS.md", "ARCHITECTURE.md", "TEST_PLAN.md")


def _source_imports_parent(path: Path, parent: str) -> bool:
    source = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    parent_prefix = parent.lower()
    for node in ast.walk(source):
        modules = []
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                modules = [node.module or ""]
        if any(module == parent_prefix or
               module.startswith(parent_prefix + ".") or
               module == parent_prefix + "lab" or
               module.startswith(parent_prefix + "lab.")
               for module in modules):
            return True
    return False


def inspect_proposal(generation: str, *, root: Path = ROOT) -> dict:
    if not FUTURE.fullmatch(generation):
        raise ValueError("inspection requires future I2+ generation name")
    root = root.resolve()
    stem = generation.lower()
    engine = root / "src" / stem
    tests = root / "tests" / stem
    docs = engine / "docs"
    checks = {}

    try:
        registry = json.loads(
            (root / "config" / "engine-registry.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as exc:
        raise ValueError("unreadable engine registry") from exc
    registered = registry.get("generations", {})
    checks["not_registered"] = generation not in registered
    checks["not_active"] = registry.get("active_generation") != generation
    checks["no_legacy_shared_lab"] = not (root / "src/lab").exists()
    checks["owned_paths_exist"] = all(
        path.is_dir() and not path.is_symlink()
        for path in (engine, tests, docs)
    )
    checks["isolated_lab_layout"] = engine.is_dir() and all(
        (engine / folder / "__init__.py").is_file()
        for folder in OWNED_DIRS
    )
    checks["documentation_present"] = docs.is_dir() and all(
        (docs / filename).is_file() for filename in OWNED_DOCS
    )
    contract = None
    try:
        contract = json.loads((engine / "engine.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    if not isinstance(contract, dict):
        contract = {}
    parent = contract.get("parent")
    checks["contract_is_proposal"] = (
        contract.get("schema") == SCHEMA
        and contract.get("generation") == generation
        and contract.get("status") == "proposal"
        and contract.get("activation") == "NOT_REGISTERED_NOT_EXECUTABLE"
        and contract.get("entrypoints") == {}
        and contract.get("scientific", {}).get("gate") == "not_established"
    )
    checks["registered_earlier_parent"] = (
        isinstance(parent, str)
        and bool(re.fullmatch(r"I[1-9][0-9]*", parent))
        and int(parent[1:]) < int(generation[1:])
        and parent in registered
    )
    checks["owned_paths_declared"] = contract.get("paths") == {
        "engine": f"src/{stem}",
        "lab": f"src/{stem}/lab",
        "runtime": f"src/{stem}/runtime",
        "tests": f"tests/{stem}",
        "documentation": f"src/{stem}/docs",
    }
    flags = contract.get("constraints", {})
    checks["life_safety_declared"] = (
        isinstance(flags, dict)
        and flags.get("mortality_irreversible") is True
        and flags.get("first_person_observations_only") is True
        and flags.get("uc_billed_cognition") is True
        and flags.get("live_state_rollback") is False
        and flags.get("hidden_oracle_input") is False
        and flags.get("legacy_h1_h2_default") is False
        and contract.get("persistence", {}).get("no_postmortem_recovery") is True
    )
    # A template-only module is NOT proof of independent implementation.
    checks["lab_implementation_present"] = (engine / "lab").is_dir() and any(
        p.name != "__init__.py" and p.suffix == ".py"
        for p in (engine / "lab").rglob("*.py")
    )
    checks["runtime_implementation_present"] = (engine / "runtime").is_dir() and any(
        p.name != "__init__.py" and p.suffix == ".py"
        for p in (engine / "runtime").rglob("*.py")
    )
    checks["cognition_implementation_present"] = (engine / "modules").is_dir() and any(
        p.name != "__init__.py" and p.suffix == ".py"
        for p in (engine / "modules").rglob("*.py")
    )
    checks["independent_tests_present"] = tests.is_dir() and any(
        p.name.startswith("test_") and p.name != "test_proposal.py"
        for p in tests.glob("test_*.py")
    )
    checks["no_parent_runtime_imports"] = True
    if engine.is_dir() and checks["registered_earlier_parent"]:
        for path in engine.rglob("*.py"):
            if path.is_symlink():
                checks["no_parent_runtime_imports"] = False
                break
            try:
                if _source_imports_parent(path, parent):
                    checks["no_parent_runtime_imports"] = False
                    break
            except (SyntaxError, UnicodeError, OSError):
                checks["no_parent_runtime_imports"] = False
                break
    else:
        checks["no_parent_runtime_imports"] = False
    blocked = sorted(key for key, passed in checks.items() if not passed)
    return {
        "schema": "individual-zero-engine-proposal-assessment/v1",
        "generation": generation,
        "status": "BLOCKED" if blocked else "STRUCTURE_PRESENT_REVIEW_REQUIRED",
        "checks": checks,
        "blocked_by": blocked,
        "test_execution": "NOT_PERFORMED",
        "scientific_evidence": "NOT_EVALUATED",
        "activation": "FORBIDDEN",
        "registration": "FORBIDDEN",
        "human_review_required": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    try:
        report = inspect_proposal(args.generation)
    except ValueError as exc:
        print(f"proposal assessment refused: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(args.generation + ": " + report["status"])
        for key in report["blocked_by"]:
            print(" - " + key)
    if args.strict and report["blocked_by"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
