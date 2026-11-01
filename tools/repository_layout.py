#!/usr/bin/env python3
"""Read-only directory inventory for agents. Never runs engines or tests."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", "reports"}
# These root-level I1 tests predate generation-owned test directories. A new
# I1/I2 test belongs under tests/i1/ or tests/i2/, not alongside infra tests.
LEGACY_ROOT_GENERATION_TESTS = frozenset({
    "test_i1_a235_lived_recall.py", "test_i1_a235_m11_cold_recall.py",
    "test_i1_a235_m11_recall_contract.py", "test_i1_a235_physical_witness.py",
    "test_i1_a235_runtime_birth.py", "test_i1_a236_combined_m11_cold.py",
    "test_i1_a236_combined_m11_water.py", "test_i1_a237_d2_no_geography.py",
    "test_i1_a238_factorial_smoke.py", "test_i1_active_birth.py",
    "test_i1_decision_witness.py", "test_i1_first_physical_step.py",
    "test_i1_issue136_d1_learning.py", "test_i1_issue136_water_readiness.py",
    "test_i1_m11_cold_recovery.py", "test_i1_model_m11_contract.py",
})
HISTORICAL_RESEARCH_MANIFEST = "docs/research/studies/HISTORICAL_ROOT_FILES.md"


def check_research_root_placement(root: Path) -> list[str]:
    """Do not add root-level studies or silently remove historical source paths."""
    manifest = root / HISTORICAL_RESEARCH_MANIFEST
    if not manifest.is_file() or manifest.is_symlink():
        return ["missing or unsafe historical research placement baseline"]
    expected = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.startswith("- `") and line.endswith("`"):
            expected.add(line[3:-1])
    if not expected or "README.md" not in expected:
        return ["empty or invalid historical research baseline"]
    folder = root / "docs/research"
    actual = {p.name for p in folder.glob("*.md") if p.is_file() and not p.is_symlink()}
    new = sorted(actual - expected)
    removed = sorted(expected - actual)
    return ([f"new root-level research Markdown: {n}; use docs/research/studies/<study-id>/" for n in new]
            + [f"historical research path missing: {n}; audit provenance before moving" for n in removed])


ENTRYPOINTS = (
    "archive/README.md", "tests/TEST_LAYOUT.md", "docs/README.md",
    "docs/research/README.md", "docs/research/studies/README.md",
    "docs/engineering/AGENT_NAVIGATION.md",
)


def paths(root: Path = ROOT) -> list[str]:
    """Return physical files, without generated reports or Git objects."""
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*")
                  if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(root).parts))


def bucket(kind: str, path: str) -> str | None:
    """Classify a path's *location*, never its scientific authority."""
    if kind == "archives":
        if path.startswith("archive/i0/"):
            return "i0-frozen"
        if path.startswith("docs/research/archive/"):
            return "research-historical"
        if path.startswith("docs/architecture/reference/"):
            return "architecture-versioned"
        if path in ("src/i1/docs/STATUS_HISTORY.md", "src/i2/docs/STATUS_HISTORY.md"):
            return "generation-status-history"
    elif kind == "tests":
        if not (path.endswith(".py") and path.rsplit("/", 1)[-1].startswith("test_")):
            return None
        for prefix, role in (
            ("archive/i0/tests/", "i0-frozen"),
            ("tests/i1/", "i1"), ("tests/i2/", "i2"),
            ("tests/infra/", "infrastructure"),
            ("tests/research/a1p/", "a1p-tooling"),
            ("tests/research/a1c/", "a1c-tooling"),
            ("tests/research/a2r/", "a2r-tooling"),
            ("tests/", "root-legacy-and-infrastructure"),
            ("tools/research/tests/", "research-tooling"),
            ("tools/a1c_tests/", "a1c-tooling"),
            ("tools/a2r_tests/", "a2r-tooling"),
        ):
            if path.startswith(prefix):
                return role
        return "unclassified-test"
    elif kind == "docs":
        if not path.endswith(".md"):
            return None
        for prefix, role in (
            ("src/i1/docs/", "i1-owned"), ("src/i2/docs/", "i2-owned"),
            ("docs/research/audits/", "research-audits"),
            ("docs/research/studies/", "research-studies"),
            ("docs/research/archive/", "research-historical"),
            ("docs/research/", "research-records-and-methods"),
            ("docs/architecture/reference/", "architecture-versioned"),
            ("docs/architecture/proposals/", "architecture-proposals"),
            ("docs/architecture/", "architecture-current-and-historical"),
            ("docs/decisions/", "accepted-decisions"),
            ("docs/engineering/", "engineering"),
            ("docs/presentation/", "onboarding"),
            ("docs/governance/", "governance"),
            ("docs/operations/", "historical-operations"),
            ("archive/i0/", "i0-frozen"),
        ):
            if path.startswith(prefix):
                return role
        if path == "docs/README.md":
            return "documentation-portal"
    return None


def inventory(root: Path = ROOT, kind: str = "docs", match: str = "", limit: int = 30) -> dict:
    grouped: dict[str, list[str]] = {}
    for path in paths(root):
        group = bucket(kind, path)
        if group is not None:
            grouped.setdefault(group, []).append(path)
    selected = sorted((group, path) for group, records in grouped.items()
                      for path in records if match.lower() in path.lower())
    return {
        "kind": kind, "match": match,
        "groups": {name: len(grouped[name]) for name in sorted(grouped)},
        "matched": len(selected), "showing": min(limit, len(selected)),
        "paths": [{"group": group, "path": path} for group, path in selected[:limit]],
        "truncated": len(selected) > limit,
        "scientific_verdict": "NOT_EVALUATED",
    }


def audit(root: Path = ROOT) -> dict:
    listing = paths(root)
    return {
        "status": "INVENTORY_ONLY",
        "research_documents_at_directory_root": sum(
            p.startswith("docs/research/") and p.count("/") == 2 and p.endswith(".md")
            for p in listing),
        "tests_at_directory_root": sorted(
            p for p in listing if p.startswith("tests/test_") and p.count("/") == 1
            and p.endswith(".py")),
        "embedded_tool_tests": sum(
            bucket("tests", p) in {"research-tooling", "a1c-tooling", "a2r-tooling"}
            for p in listing),
        "frozen_i0_files": sum(p.startswith("archive/i0/") for p in listing),
        "scientific_verdict": "NOT_EVALUATED",
    }


def check(root: Path = ROOT) -> dict:
    errors = [f"missing navigation entrypoint: {path}" for path in ENTRYPOINTS
              if not (root / path).is_file()]
    errors.extend(check_research_root_placement(root))
    for deprecated in ("tools/research/tests", "tools/a1c_tests", "tools/a2r_tests"):
        folder = root / deprecated
        if folder.is_dir() and any(folder.rglob("test_*.py")):
            errors.append(f"tests returned to deprecated location: {deprecated}; use tests/research/")
    for p in (root / "tests").glob("test_i[0-9]*.py"):
        if p.name not in LEGACY_ROOT_GENERATION_TESTS:
            errors.append(f"new generation test at root: {p.relative_to(root)} (use tests/iN/)")
    return {"status": "PASS" if not errors else "FAIL", "errors": sorted(errors),
            "scientific_verdict": "NOT_EVALUATED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inventory", "audit", "check"))
    parser.add_argument("--kind", choices=("archives", "tests", "docs"), default="docs")
    parser.add_argument("--match", default="", help="Case-insensitive substring in the repository path")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be nonnegative")
    data = (inventory(kind=args.kind, match=args.match, limit=args.limit)
            if args.command == "inventory" else audit() if args.command == "audit" else check())
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.command == "inventory":
        print(f"{args.kind}: {data['matched']} matching paths ({data['showing']} shown)")
        for name, count in data["groups"].items():
            print(f"  {name}: {count}")
        for item in data["paths"]:
            print(f"{item['group']}: {item['path']}")
        if data["truncated"]:
            print("Use --match and --limit for more precise navigation.")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 1 if args.command == "check" and data["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
