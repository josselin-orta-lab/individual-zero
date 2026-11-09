#!/usr/bin/env python3
"""One-time archival migration of closed I3 Stage-1 candidate implementations.

Repoints retained tests and historical opt-in runtime paths. Never changes a
World, an experimental result, an action token, or a scientific verdict.
"""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
I3 = ROOT / "src/i3"
LAB, MODULES = I3 / "lab", I3 / "modules"
TARGET = I3 / "archive/stage1"
TESTS = ROOT / "tests/i3"

MOVE_LAB = sorted([*LAB.glob("stage1_*.py"),
                   *LAB.glob("projection_candidate_[ef]*.py")])
MOVE_MODULES = sorted([*MODULES.glob("candidate_f_*.py"),
                       *(MODULES / name for name in (
                           "genomic_omega_candidate_f.py",
                           "genomic_omega_frontier_information_mind.py",
                           "personal_recurrence_candidate_g_mind.py",
                           "personal_relevance_candidate_h_mind.py",
                           "personal_shared_prior_candidate_i_mind.py"))])
MOVED = MOVE_LAB + MOVE_MODULES
assert len(MOVE_LAB) == 22 and len(MOVE_MODULES) == 8
assert all(p.is_file() for p in MOVED)
RELOCATED = {
    "i3." + p.parent.name + "." + p.stem:
    "i3.archive.stage1." + p.parent.name + "." + p.stem
    for p in MOVED
}
FROM = re.compile(r"^(\s*)from\s+(\.*[A-Za-z0-9_.]+)\s+import\s+(.*)$")


def source_package(path: Path) -> str:
    if path.is_relative_to(I3):
        return "i3." + ".".join(path.relative_to(I3).parts[:-1])
    return ""


def package_import_target(base: str, rest: str) -> str | None:
    if base not in ("i3.lab", "i3.modules"):
        return None
    names = re.split(r"\s*,\s*", rest.split("#", 1)[0].strip())
    if len(names) == 1 and "(" not in rest:
        new = RELOCATED.get(base + "." + names[0].split()[0])
        if new:
            return new.rsplit(".", 1)[0]
    if any(RELOCATED.get(base + "." + n.split()[0]) for n in names):
        raise RuntimeError("Mixed or multiline candidate import: " + base + " " + rest)
    return None


def rewrite(source: str, path: Path, moving: bool) -> str:
    current_package = source_package(path)
    out = []
    for line in source.splitlines(keepends=True):
        matched = FROM.match(line)
        if matched:
            leader, spec, rest = matched.groups()
            full = (importlib.util.resolve_name(spec, current_package)
                    if spec.startswith(".") else spec)
            updated = RELOCATED.get(full) or package_import_target(full, rest)
            if updated is not None or (moving and spec.startswith(".")):
                line = (f"{leader}from {updated or full} import {rest}"
                        + ("\n" if line.endswith("\n") else ""))
        for old, new in sorted(RELOCATED.items(), key=lambda kv: -len(kv[0])):
            line = re.sub(r"(?<![\w.])" + re.escape(old) + r"(?![\w])", new, line)
        out.append(line)
    return "".join(out)


for path in sorted([*I3.rglob("*.py"), *TESTS.rglob("*.py")]):
    if path in MOVED:
        continue
    old = path.read_text()
    new = rewrite(old, path, False)
    if new != old:
        path.write_text(new)

for path in MOVED:
    dest = TARGET / path.parent.name / path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rewrite(path.read_text(), path, True))
    path.unlink()

for path in (I3 / "archive/__init__.py", TARGET / "__init__.py",
             TARGET / "lab/__init__.py", TARGET / "modules/__init__.py"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '"""Retained closed Stage-1 compatibility code, not active science."""\n'
    )

manifest_path = I3 / "ACTIVE_SURFACE.json"
manifest = json.loads(manifest_path.read_text())
compat = {
    "src/i3/archive/stage1/" + Path(old).parent.name + "/" + Path(old).name
    if ("i3." + Path(old).parent.name + "." + Path(old).stem) in RELOCATED
    else old for old in manifest["stage1_compatibility_only"]
}
compat.update(str((TARGET / p.parent.name / p.name).relative_to(ROOT))
              for p in MOVED)
manifest["stage1_compatibility_only"] = sorted(compat)
manifest["historical_roots"] = sorted(set(
    manifest["historical_roots"] + ["src/i3/archive/stage1/"]))
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

for path in (I3 / "AGENTS.md", I3 / "docs/ACTIVE_SURFACE.md",
             I3 / "docs/README.md", LAB / "README.md"):
    old = path.read_text()
    new = old.replace(
        "Stage-1 files still present under `lab/`",
        "Stage-1 candidate modules archived under `archive/stage1/`")
    new = new.replace(
        "Some Stage-1 source still exists under `src/i3/lab/` only because retained\n"
        "compatibility tests or engineering regression tools import it.",
        "Stage-1 candidate implementations are under `src/i3/archive/stage1/`;\n"
        "retained tests and historical opt-in runtime paths import this package.")
    new = new.replace(
        "Several Stage-1 lab modules remain under `src/i3/lab/` because retained tests,\n"
        "runtime compatibility paths or ADR-0017 regression tooling still import them.",
        "Stage-1 candidate code is archived under `src/i3/archive/stage1/`\n"
        "for retained compatibility tests and regression tooling.")
    for before, after in RELOCATED.items():
        new = new.replace(
            "src/" + before.replace(".", "/") + ".py",
            "src/" + after.replace(".", "/") + ".py")
    if new != old:
        path.write_text(new)

readme = TARGET / "README.md"
readme.write_text(
    "# Closed Stage-1 candidate implementations\n\n"
    "Stage 1 closed negative under ADR-0018. These modules are retained solely\n"
    "for historical opt-in runtime compatibility, regression tests and sealed\n"
    "engineering checks. They are **not** active Stage-2 science.\n\n"
    "Historical tests remain under `tests/i3/` and import this archive.\n"
    "The original scientific evidence, World indices, experimental verdicts,\n"
    "fixtures, action identifiers, and behavior contracts are unchanged.\n\n"
    "## Former module import paths\n\n" +
    "\n".join(f"- `{old}` -> `{new}`"
              for old, new in sorted(RELOCATED.items())) + "\n"
)

for path in sorted([*I3.rglob("*.py"), *TESTS.rglob("*.py")]):
    source = path.read_text()
    ast.parse(source, filename=str(path))
    if path.parent in (LAB, MODULES) and (
        path.name.startswith("stage1_") or
        re.match(r"projection_candidate_[ef]|candidate_f_|"
                 r"personal_.*_candidate_[ghi]_mind|"
                 r"genomic_omega_(candidate_f|frontier_information_mind)",
                 path.name)):
        raise RuntimeError("Candidate still in active package: " + str(path))
    for old in RELOCATED:
        if re.search(r"(?<![\w.])" + re.escape(old) + r"(?![\w])", source):
            raise RuntimeError("Stale candidate import: " + str(path) + ": " + old)

print(f"I3_STAGE1_ARCHIVE_PASS moved={len(MOVED)} "
      f"compatibility_paths={len(manifest['stage1_compatibility_only'])}")
