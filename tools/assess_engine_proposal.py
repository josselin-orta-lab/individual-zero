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
FUTURE = re.compile(r"I(?:[2-9]|[1-9][0-9]+)\Z")
SCHEMA = "individual-zero-engine-contract/v1"
OWNED_DIRS = ("lab", "modules", "runtime", "config")
OWNED_DOCS = ("STATUS.md", "ARCHITECTURE.md", "TEST_PLAN.md")


_GENERATION_NAMESPACE = re.compile(r"i(0|[1-9][0-9]*)(?:lab)?\Z", re.IGNORECASE)


def _foreign_generation_namespace(module: str, generation: str) -> bool:
    """Detect namespaces owned by a generation other than this proposal."""
    parts = module.split(".")
    if parts and parts[0] in {"src", "archive"}:
        parts = parts[1:]
    if not parts:
        return False
    match = _GENERATION_NAMESPACE.fullmatch(parts[0])
    return match is not None and int(match.group(1)) != int(generation[1:])


def _source_imports_other_generation(path: Path, generation: str) -> bool:
    """Detect explicit cross-generation and unprovable dynamic imports.

    A static checker cannot prove absence of arbitrary exec, custom loaders,
    transitive third-party imports or shared mutable services.
    """
    source = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    importlib_names: set[str] = set()
    builtins_names: set[str] = set()
    dynamic_names: set[str] = {"__import__"}
    for node in ast.walk(source):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _foreign_generation_namespace(alias.name, generation):
                    return True
                if alias.name in {"importlib", "importlib.util"}:
                    importlib_names.add(alias.asname or "importlib")
                if alias.name == "builtins":
                    builtins_names.add(alias.asname or "builtins")
        elif isinstance(node, ast.ImportFrom):
            if node.module and _foreign_generation_namespace(node.module, generation):
                return True
            # Includes from src import i1 and from .. import i0lab.
            if any(_foreign_generation_namespace(alias.name, generation)
                   for alias in node.names):
                return True
            if node.level == 0 and node.module == "importlib":
                dynamic_names.update(
                    alias.asname or alias.name for alias in node.names
                    if alias.name == "import_module"
                )
            if node.level == 0 and node.module == "builtins":
                dynamic_names.update(
                    alias.asname or alias.name for alias in node.names
                    if alias.name == "__import__"
                )
    for node in ast.walk(source):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        is_loader = (
            isinstance(fn, ast.Name) and fn.id in dynamic_names
        ) or (
            isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name)
            and ((fn.attr == "import_module" and fn.value.id in importlib_names)
                 or (fn.attr == "__import__" and fn.value.id in builtins_names))
        )
        if not is_loader:
            continue
        name = node.args[0] if node.args else next(
            (kw.value for kw in node.keywords if kw.arg == "name"), None
        )
        # A dynamic target cannot be certified independent by static review.
        if not isinstance(name, ast.Constant) or type(name.value) is not str:
            return True
        if _foreign_generation_namespace(name.value.lstrip("."), generation):
            return True
        if name.value.startswith("."):
            package = node.args[1] if len(node.args) >= 2 else next(
                (kw.value for kw in node.keywords if kw.arg == "package"), None
            )
            if (not isinstance(package, ast.Constant)
                    or type(package.value) is not str
                    or _foreign_generation_namespace(package.value, generation)):
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
        (engine / folder).is_dir()
        and not (engine / folder).is_symlink()
        and (engine / folder / "__init__.py").is_file()
        and not (engine / folder / "__init__.py").is_symlink()
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
    # Keep the existing JSON check name while enforcing ADR-0001 against
    # ALL other generations, not only the declared comparative parent.
    checks["no_parent_runtime_imports"] = bool(
        engine.is_dir() and not engine.is_symlink()
        and checks["registered_earlier_parent"]
    )
    if checks["no_parent_runtime_imports"]:
        for path in engine.rglob("*"):
            # rglob("*.py") would miss a whole symlinked prior-engine tree.
            if path.is_symlink():
                checks["no_parent_runtime_imports"] = False
                break
            if path.suffix != ".py" or not path.is_file():
                continue
            try:
                if _source_imports_other_generation(path, generation):
                    checks["no_parent_runtime_imports"] = False
                    break
            except (SyntaxError, UnicodeError, OSError):
                checks["no_parent_runtime_imports"] = False
                break
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
