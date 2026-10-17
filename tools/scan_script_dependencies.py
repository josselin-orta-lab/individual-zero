#!/usr/bin/env python3
"""Static script custody audit; historical scripts are NEVER imported/executed.

A namespace import is not engine ownership or evidence of scientific validity.
Dynamic and subprocess dependencies cannot be fully determined by this audit.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCOPE_ROOTS = frozenset({"i0", "i1", "i1lab", "lab"})
SCHEMA = "individual-zero-script-custody/v1"



def _literal_targets(node: ast.AST, modules: set[str],
                     bindings: dict[str, set[str]]) -> set[str]:
    """Infer ONLY exact checked-in script filenames from literal expressions."""
    hits = set()
    for item in ast.walk(node):
        if isinstance(item, ast.Name):
            hits.update(bindings.get(item.id, set()))
        elif isinstance(item, ast.Constant) and isinstance(item.value, str):
            value = item.value.replace("\\", "/")
            if value.startswith("scripts/") and value.endswith(".py"):
                stem = value[len("scripts/"):-3]
                if stem in modules and "/" not in stem:
                    hits.add("scripts/" + stem + ".py")
        elif (isinstance(item, ast.Call)
              and isinstance(item.func, ast.Attribute)
              and item.func.attr == "with_name" and len(item.args) == 1
              and isinstance(item.args[0], ast.Constant)
              and isinstance(item.args[0].value, str)):
            name = item.args[0].value
            if name.endswith(".py") and name[:-3] in modules:
                hits.add("scripts/" + name)
        elif isinstance(item, ast.BinOp) and isinstance(item.op, ast.Div):
            fragments = []
            current = item
            while isinstance(current, ast.BinOp) and isinstance(current.op, ast.Div):
                if isinstance(current.right, ast.Constant) and isinstance(current.right.value, str):
                    fragments.insert(0, current.right.value)
                else:
                    break
                current = current.left
            if len(fragments) >= 2 and fragments[-2] == "scripts":
                last = fragments[-1]
                if last.endswith(".py") and last[:-3] in modules:
                    hits.add("scripts/" + last)
    return hits


def _launch_api(node: ast.Call) -> str | None:
    f = node.func
    if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
            and f.value.id == "subprocess"
            and f.attr in {"run", "Popen", "check_call", "check_output", "call"}):
        return "subprocess." + f.attr
    if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
            and f.value.id == "os" and f.attr in {"system", "popen"}):
        return "os." + f.attr
    return None


def _static_execution_and_file_evidence(source: ast.AST,
                                        modules: set[str]) -> tuple:
    """Observe explicit launch targets and path literals; do not run commands.

    All dynamic subprocess calls remain unresolved even when some literal
    path is observed. File literals record references, not actual I/O.
    """
    bindings: dict[str, set[str]] = {}
    for item in ast.walk(source):
        if isinstance(item, (ast.Assign, ast.AnnAssign)):
            target = item.targets[0] if isinstance(item, ast.Assign) and len(item.targets) == 1 else (
                item.target if isinstance(item, ast.AnnAssign) else None)
            if isinstance(target, ast.Name) and item.value is not None:
                found = _literal_targets(item.value, modules, bindings)
                if found:
                    bindings[target.id] = found
    calls = []
    file_literals = set()
    for item in ast.walk(source):
        if not isinstance(item, ast.Call):
            continue
        api = _launch_api(item)
        if api:
            hits = sorted(_literal_targets(item, modules, bindings))
            calls.append({
                "api": api, "line": item.lineno,
                "resolved_script_targets": hits,
                "dependency_resolution": ("LITERAL_TARGETS_ONLY" if hits
                                          else "UNRESOLVED_DYNAMIC_OR_NON_SCRIPT"),
            })
        f = item.func
        path_api = (
            isinstance(f, ast.Name) and f.id in {"Path", "PurePath", "open"}
            or isinstance(f, ast.Attribute) and
            f.attr in {"with_name", "joinpath", "open"}
        )
        if path_api:
            for argument in item.args:
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    value = argument.value
                    if value.endswith((".json", ".jsonl", ".yaml", ".yml",
                                       ".py", ".md", ".toml", ".sqlite", ".wal",
                                       ".csv", ".parquet", ".txt")):
                        file_literals.add((item.lineno, value))
    dependencies = set()
    for entry in calls:
        dependencies.update(entry["resolved_script_targets"])
    return (
        sorted(calls, key=lambda item: (item["line"], item["api"])),
        sorted(dependencies),
        [{"line": line, "literal": name}
         for line, name in sorted(file_literals)],
    )


def _inspect_script(path: Path, modules: set[str]) -> dict:
    raw = path.read_bytes()
    imports, dependencies, evidence, uncertainties = set(), set(), [], []
    process_calls, launched_scripts, path_literals = [], [], []
    parse_error = None
    try:
        source = ast.parse(raw.decode("utf-8-sig"), filename=str(path))
    except (UnicodeError, SyntaxError) as exc:
        parse_error = "%s at line %s" % (
            type(exc).__name__, getattr(exc, "lineno", None))
    else:
        process_calls, launched_scripts, path_literals = (
            _static_execution_and_file_evidence(source, modules)
        )
        for node in ast.walk(source):
            targets = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    uncertainties.append(node.lineno)
                else:
                    targets = [node.module] if node.module else []
                    if node.module == "scripts":
                        targets.extend("scripts." + x.name for x in node.names)
            elif isinstance(node, ast.Call):
                f = node.func
                if (isinstance(f, ast.Name) and f.id == "__import__"
                        or isinstance(f, ast.Attribute) and
                        f.attr == "import_module"):
                    uncertainties.append(node.lineno)
            for module in targets:
                if not module:
                    continue
                imports.add(module)
                parts = module.split(".")
                if parts[0] in SCOPE_ROOTS:
                    evidence.append({"module": module, "line": node.lineno,
                                     "namespace": parts[0]})
                local = (parts[1] if parts[0] == "scripts" and len(parts) > 1
                         else parts[0] if len(parts) == 1 else None)
                if local in modules and local != path.stem:
                    dependencies.add("scripts/" + local + ".py")
    return {
        "source_sha256": sha256(raw).hexdigest(),
        "imports": sorted(imports),
        "script_dependencies": sorted(dependencies),
        "subprocess_calls": process_calls,
        "resolved_subprocess_script_dependencies": launched_scripts,
        "literal_file_references": path_literals,
        "namespace_evidence": sorted(
            evidence, key=lambda x: (x["line"], x["module"])),
        "dynamic_or_relative_import_lines": sorted(set(uncertainties)),
        "parse_error": parse_error,
    }


def _scope(evidence: list[dict]) -> str:
    roots = {x["namespace"] for x in evidence}
    i0 = bool(roots & {"i0", "lab"})
    i1 = bool(roots & {"i1", "i1lab"})
    if i0 and i1:
        return "MIXED_I0_I1_IMPORTS_NOT_OWNERSHIP"
    if i0:
        return "I0_OR_LEGACY_LAB_IMPORTS_NOT_OWNERSHIP"
    if i1:
        return "I1_IMPORTS_NOT_OWNERSHIP"
    return "UNDETERMINED_FROM_STATIC_IMPORTS"


def _reachable(start: str, scripts: dict) -> set[str]:
    visited, pending = set(), (list(scripts[start]["script_dependencies"])
                             + list(scripts[start]["resolved_subprocess_script_dependencies"]))
    while pending:
        item = pending.pop()
        if item in visited:
            continue
        visited.add(item)
        pending.extend(scripts[item]["script_dependencies"])
        pending.extend(scripts[item]["resolved_subprocess_script_dependencies"])
    return visited


def analyze(root: Path = ROOT) -> dict:
    root = root.resolve()
    inventory = json.loads((root / "config/tool-inventory.json").read_text())
    custody = json.loads((root / "config/script-custody.json").read_text())
    active = set(inventory["active_ci_scripts"])
    pending = set(inventory["research_or_legacy_review"])
    reviewed = custody.get("reviewed", {})
    errors = []
    if custody.get("schema") != SCHEMA:
        errors.append("unsupported custody schema")
    if not isinstance(reviewed, dict):
        raise ValueError("reviewed custody must be a JSON object")
    paths = sorted(p.relative_to(root).as_posix()
                   for p in (root / "scripts").glob("*.py") if p.is_file())
    if active & pending or active | pending != set(paths):
        errors.append("script inventory has unknown or duplicated paths")
    modules = {Path(path).stem for path in paths}
    scripts = {}
    for path in paths:
        item = _inspect_script(root / path, modules)
        item["declared_role"] = "CURRENT_CI_TOOL" if path in active else "REVIEW_REQUIRED"
        item["import_scope_observation"] = _scope(item["namespace_evidence"])
        scripts[path] = item
        if item["parse_error"] and path in active:
            errors.append(path + ": active script cannot be parsed")
    for path in sorted(active):
        if path not in scripts:
            errors.append("missing active script " + path)
            continue
        reach = _reachable(path, scripts)
        crossed = sorted(reach & pending)
        if crossed:
            errors.append(path + ": imports or launches unreviewed scripts: " + ", ".join(crossed))
        scripts[path]["transitive_script_dependencies"] = sorted(reach)
        scripts[path]["dependency_completeness"] = (
            "INCOMPLETE_DYNAMIC_IMPORTS_OR_SUBPROCESSES"
            if (scripts[path]["dynamic_or_relative_import_lines"]
                or any(x["dependency_resolution"] != "LITERAL_TARGETS_ONLY"
                       for x in scripts[path]["subprocess_calls"]))
            else "STATIC_IMPORTS_AND_LITERAL_SUBPROCESSES_ONLY"
        )
    for path, claim in sorted(reviewed.items()):
        if path not in pending:
            errors.append(path + ": only nonactive scripts can be reviewed")
            continue
        if (not isinstance(claim, dict)
                or claim.get("context") not in {"archived_i0_lab_compatibility",
                                                 "historical_i1_experiment_review"}
                or claim.get("verified_import") not in scripts[path]["imports"]
                or claim.get("scientific_oracle") is not False):
            errors.append(path + ": review import evidence not verified")
        else:
            scripts[path]["reviewed_custody"] = claim
    scope_counts = dict(sorted(Counter(
        scripts[p]["import_scope_observation"] for p in sorted(pending)
    ).items()))
    return {
        "schema": "individual-zero-script-dependencies/v1",
        "status": "FAIL" if errors else "PASS_WITH_REVIEW",
        "analysis": "AST_IMPORTS_ONLY_DOES_NOT_EXECUTE_HISTORICAL_SCRIPTS",
        "active_scripts": len(active),
        "review_pending": len(pending),
        "reviewed_with_import_evidence": len(reviewed),
        "candidate_scope_counts": scope_counts,
        "subprocess_calls_observed": sum(len(x["subprocess_calls"]) for x in scripts.values()),
        "literal_child_scripts_observed": sum(len(x["resolved_subprocess_script_dependencies"]) for x in scripts.values()),
        "errors": errors,
        "scripts": scripts,
        "scientific_conclusion": "NOT_EVALUATED",
    }


def markdown(report: dict) -> str:
    rows = [
        "# Script dependency and custody analysis", "",
        "Imports are inspected statically without executing historical scripts.",
        "Namespace imports are NOT proof of engine ownership or science.", "",
        "Result: " + report["status"],
        "Active validation scripts: " + str(report["active_scripts"]),
        "Pending individual review: " + str(report["review_pending"]),
        "Scientific assessment: NOT EVALUATED", "",
        "| Observed import scope (not ownership) | Count |",
        "| --- | ---: |",
    ]
    for label, count in sorted(report["candidate_scope_counts"].items()):
        rows.append("| " + label + " | " + str(count) + " |")
    rows.extend(["", "## Reviewed direct imports", ""])
    for path, item in sorted(report["scripts"].items()):
        if "reviewed_custody" in item:
            claim = item["reviewed_custody"]
            rows.append("- " + path + ": " + claim["context"] +
                        "; imported " + claim["verified_import"])
    rows.extend(["", "Subprocess calls observed: " + str(report["subprocess_calls_observed"]),
                 "Resolved literal child-script references: " + str(report["literal_child_scripts_observed"]),
                 "", "## Limitations", "",
                 "Only exact literal subprocess targets are linked. Dynamic "
                 "launches, indirect imports and file references are NOT proof of "
                 "ownership or completeness. Historical scripts are not executed.", ""])
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--markdown-output", type=Path)
    opts = ap.parse_args()
    result = analyze()
    if opts.output:
        opts.output.parent.mkdir(parents=True, exist_ok=True)
        opts.output.write_text(json.dumps(result, indent=2) + "\n")
    if opts.markdown_output:
        opts.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        opts.markdown_output.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "scripts"}, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
