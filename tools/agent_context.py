#!/usr/bin/env python3
"""Read-only context router for development agents.

This is navigation metadata, not an engine runner, CI launcher or scientific gate.
Python 3.11+ standard library only. Safe to invoke without installing the project.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAP = "config/agent-context-map.json"
REGISTRY = "config/engine-registry.json"
INVENTORY = "config/tool-inventory.json"
SCHEMA = "individual-zero-agent-context/v1"
GENERATIONS = {"I0", "I1", "I2", "any"}
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")


def load_json(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def safe_path(value: str) -> bool:
    """Allow only repository-relative POSIX paths (including directory prefixes)."""
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        return False
    parts = PurePosixPath(value).parts
    return bool(parts) and not any(p in ("..", ".") for p in parts)


def path_matches(path: str, selector: str) -> bool:
    """A trailing slash means directory; a file-like prefix may match a stem."""
    if selector.endswith("/"):
        return path.startswith(selector)
    if path == selector:
        return True
    if Path(selector).suffix:
        return False
    return path.startswith(selector)


def existing_selector(root: Path, selector: str) -> bool:
    target = root / selector.rstrip("/")
    if target.exists():
        return True
    # Stems such as src/i1/modules/consolidation_ are intentional prefixes.
    return bool(list(target.parent.glob(target.name + "*"))) if target.parent.is_dir() else False


def inspect(root: Path = ROOT) -> dict:
    """Audit only metadata, structure and references; never run an engine."""
    errors: list[str] = []
    try:
        data = load_json(root, MAP)
        registry = load_json(root, REGISTRY)
        inventory = load_json(root, INVENTORY)
    except (OSError, ValueError, TypeError) as exc:
        return {"status": "FAIL", "errors": [f"cannot read metadata: {exc}"],
                "scientific_gate": "NOT_EVALUATED"}
    if data.get("schema") != SCHEMA:
        errors.append("unknown or missing context-map schema")
    routes = data.get("routes", {})
    if not isinstance(routes, dict) or not routes:
        errors.append("routes must be a non-empty object")
        routes = {}
    if data.get("default_route") not in routes:
        errors.append("default route missing")
    active = registry.get("active_generation")
    if active not in registry.get("generations", {}):
        errors.append("active generation absent from registry")
    for route_name, route in routes.items():
        if not isinstance(route, dict) or route.get("generation") not in GENERATIONS:
            errors.append(f"{route_name}: invalid generation")
            continue
        for field in ("summary", "match_paths", "keywords", "documents", "owners",
                      "tests", "invariants", "checks"):
            value = route.get(field)
            if field == "summary":
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{route_name}: missing summary")
            elif not isinstance(value, list) or any(not isinstance(v, str) for v in value):
                errors.append(f"{route_name}: invalid {field}")
        for field in ("match_paths", "documents", "owners", "tests"):
            for path in route.get(field, []):
                if not safe_path(path):
                    errors.append(f"{route_name}: unsafe {field} path: {path}")
                elif not existing_selector(root, path):
                    errors.append(f"{route_name}: missing {field} reference: {path}")
        generation = route.get("generation")
        if generation in ("I1", "I2"):
            contract_path = root / f"src/{generation.lower()}/engine.json"
            try:
                contract = json.loads(contract_path.read_text(encoding="utf-8"))
                if contract.get("generation") != generation:
                    errors.append(f"{route_name}: generation contract mismatch")
            except (ValueError, OSError) as exc:
                errors.append(f"{route_name}: cannot read generation contract: {exc}")
    workflows = data.get("workflows", {})
    if not isinstance(workflows, dict):
        errors.append("workflows must be an object")
        workflows = {}
    for path, info in workflows.items():
        if not safe_path(path) or not path.startswith(".github/workflows/") or not (root / path).is_file():
            errors.append(f"invalid workflow reference: {path}")
        if not isinstance(info, dict) or not all(info.get(f) for f in ("classification", "execution", "note")):
            errors.append(f"workflow needs explicit classification, execution and note: {path}")
    if not isinstance(inventory.get("active_ci_scripts"), list) or not isinstance(inventory.get("research_or_legacy_review"), list):
        errors.append("script inventory has invalid groups")
    overlap = set(inventory.get("active_ci_scripts", [])) & set(inventory.get("research_or_legacy_review", []))
    if overlap:
        errors.append("script inventory groups overlap")
    return {"status": "FAIL" if errors else "PASS", "errors": sorted(set(errors)),
            "routes": len(routes), "classified_workflows": len(workflows),
            "scientific_gate": "NOT_EVALUATED"}


def choose_route(data: dict, paths: list[str], task: str, selected: str | None,
                 generation: str) -> tuple[str | None, list[str]]:
    routes = data["routes"]
    for path in paths:
        if not safe_path(path):
            raise ValueError(f"unsafe repository path: {path}")
    if selected:
        if selected not in routes:
            raise ValueError(f"unknown route: {selected}")
        selected_generation = routes[selected]["generation"]
        if generation != "auto" and selected_generation not in (generation, "any"):
            raise ValueError(f"route {selected} does not belong to {generation}")
        if selected_generation != "any" and any(
            path.startswith("src/i1/") if selected_generation == "I2" else
            path.startswith("src/i2/") for path in paths
        ):
            raise ValueError(f"route {selected} conflicts with requested generation paths")
        return selected, []
    # Resolve every requested path independently. A cross-component change must
    # never silently inherit the longest filename's policy.
    selected_for_paths: set[str] = set()
    for path in paths:
        path_scores: dict[str, int] = {}
        for name, route in routes.items():
            if generation != "auto" and route["generation"] not in (generation, "any"):
                continue
            score = max((len(selector) for selector in route["match_paths"]
                         if path_matches(path, selector)), default=0)
            if score:
                path_scores[name] = score
        if path_scores:
            best = max(path_scores.values())
            selected_for_paths.update(name for name, score in path_scores.items() if score == best)
    if selected_for_paths:
        winners = sorted(selected_for_paths)
        return (winners[0], []) if len(winners) == 1 else (None, winners)
    query = task.lower()
    scores: dict[str, int] = {}
    for name, route in routes.items():
        if generation != "auto" and route["generation"] not in (generation, "any"):
            continue
        score = max((len(keyword) for keyword in route["keywords"]
                     if re.search(r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)", query)), default=0)
        if score:
            scores[name] = score
    if scores:
        specialized = sorted(name for name in scores
                             if name not in ("repository", "i1-core", "i2-proposal"))
        if len(specialized) > 1:
            return None, specialized
        if specialized:
            return specialized[0], []
        top = max(scores.values())
        winners = sorted(name for name, score in scores.items() if score == top)
        return (winners[0], []) if len(winners) == 1 else (None, winners)
    if generation in ("I1", "I2"):
        return ("i1-core" if generation == "I1" else "i2-proposal"), []
    return data["default_route"], []


def describe_path(path: str, data: dict, inventory: dict) -> dict | None:
    if path.startswith("scripts/") and path.endswith(".py"):
        if path in inventory.get("active_ci_scripts", []):
            classification = "ACTIVE_CI_INFRASTRUCTURE"
        elif path in inventory.get("research_or_legacy_review", []):
            classification = "REVIEW_REQUIRED_NOT_PROVEN_OBSOLETE"
        else:
            classification = "UNCLASSIFIED_REVIEW_REQUIRED"
        return {"kind": "script", "path": path, "classification": classification,
                "permission": "NOT_GRANTED_BY_ROUTER"}
    if path.startswith(".github/workflows/"):
        entry = data.get("workflows", {}).get(path)
        return {"kind": "workflow", "path": path,
                "classification": entry["classification"] if entry else "UNREVIEWED",
                "execution": entry["execution"] if entry else "EXPLICIT_REVIEW_REQUIRED",
                "note": entry["note"] if entry else "Inspect actual workflow before requesting execution.",
                "permission": "NOT_GRANTED_BY_ROUTER"}
    return None


def route_context(root: Path = ROOT, *, paths: list[str] | None = None,
                  task: str = "", selected: str | None = None,
                  generation: str = "auto") -> dict:
    paths = paths or []
    data = load_json(root, MAP)
    registry = load_json(root, REGISTRY)
    inventory = load_json(root, INVENTORY)
    route, ambiguous = choose_route(data, paths, task, selected, generation)
    if ambiguous:
        return {"status": "AMBIGUOUS", "candidates": ambiguous,
                "hint": "Specify --route; no context was silently selected.",
                "scientific_gate": "NOT_EVALUATED"}
    entry = data["routes"][route]
    gen = entry["generation"] if entry["generation"] != "any" else (
        registry["active_generation"] if generation in ("auto", "any") else generation)
    contract = load_json(root, f"src/{gen.lower()}/engine.json") if gen in ("I1", "I2") else None
    execution_paths = [item for path in paths if (item := describe_path(path, data, inventory))]
    return {"status": "ROUTED", "route": route, "summary": entry["summary"],
            "requested_paths": paths, "generation": gen,
            "active_generation": registry["active_generation"],
            "contract_status": contract.get("status") if contract else "frozen_reference",
            "activation": contract.get("activation", "NOT_ROUTER_AUTHORIZED") if contract else "NOT_ROUTER_AUTHORIZED",
            "authority": ["AGENTS.md", REGISTRY, f"src/{gen.lower()}/engine.json"] if contract else ["AGENTS.md", REGISTRY],
            "documents": entry["documents"], "owners": entry["owners"],
            "tests_to_inspect": entry["tests"], "invariants": entry["invariants"],
            "suggested_checks_not_executed": entry["checks"],
            "execution_metadata": execution_paths,
            "scientific_gate": "NOT_EVALUATED",
            "warning": "Routing never executes checks, grants engine authority or validates scientific claims. Verify current HEAD and exact-SHA evidence."}


def markdown_context(result: dict) -> str:
    if result["status"] == "AMBIGUOUS":
        return ("# Ambiguous agent route\n\n" + ", ".join(result["candidates"]) +
                "\n\nSpecify --route explicitly. No route has been inferred.\n")
    lines = [f"# Agent context: {result['route']}", "",
             f"**Generation:** {result['generation']} (active: {result['active_generation']})",
             f"**Contract status:** {result['contract_status']}",
             f"**Activation by router:** {result['activation']}",
             "", result["summary"], ""]
    for title, key in (("Authority (read first)", "authority"),
                       ("Focused documentation", "documents"),
                       ("Owned code / boundaries to inspect", "owners"),
                       ("Tests to inspect (NOT_RUN)", "tests_to_inspect"),
                       ("Non-negotiable invariants", "invariants"),
                       ("Suggested commands (NOT_RUN)", "suggested_checks_not_executed")):
        lines += [f"## {title}", ""]
        lines += [f"- {value}" for value in result[key]] or ["- None defined"]
        lines.append("")
    if result["execution_metadata"]:
        lines += ["## Script / workflow custody", "", chr(96) * 3 + "json",
                  json.dumps(result["execution_metadata"], ensure_ascii=False, indent=2),
                  chr(96) * 3, ""]
    lines += [f"**Scientific gate:** {result['scientific_gate']}", "", result["warning"], ""]
    return "\n".join(lines)


def handoff_template(root: Path, route_name: str, sha: str | None) -> str:
    data = load_json(root, MAP)
    if route_name not in data["routes"]:
        raise ValueError(f"unknown route: {route_name}")
    if sha is not None and not SHA40.fullmatch(sha):
        raise ValueError("--sha must contain exactly 40 hexadecimal characters")
    route = data["routes"][route_name]
    base = sha.lower() if sha else "REQUIRED_EXACT_40_CHARACTER_SHA"
    return (f"# Agent handoff: {route_name}\n\n"
            f"- Baseline / exact commit SHA: {base}\n"
            f"- Generation: {route['generation']} (verify live registry at handoff)\n"
            "- Issue / PR: TODO\n- Objective and affected paths: TODO\n"
            "- Dependencies / downstream callers inspected: TODO\n"
            "- Invariants and contracts verified: TODO\n"
            "- Code changes and actual observations: TODO / NOT_OBSERVED\n"
            "- Targeted tests: NOT_RUN (reason: TODO)\n"
            "- CI on this exact SHA: NOT_RUN (reason: TODO)\n"
            "- Scientific evidence / gate: NOT_EVALUATED\n"
            "- Open risks / blockers / next independent step: TODO\n\n"
            "Do not replace NOT_RUN with PASS without exact-SHA results. "
            "This handoff is not scientific validation or permission to activate a generation.\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    route_parser = commands.add_parser("route", help="Select minimal context; never execute commands")
    route_parser.add_argument("--route", dest="selected")
    route_parser.add_argument("--generation", choices=("auto", "I0", "I1", "I2"), default="auto")
    route_parser.add_argument("--path", action="append", default=[], help="Affected repository-relative path; repeatable")
    route_parser.add_argument("--task", default="", help="Task description; ambiguous matches require explicit --route")
    route_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    audit_parser = commands.add_parser("audit", help="Validate navigation map and file references")
    audit_parser.add_argument("--json", action="store_true", help="Machine-readable output (default)")
    commands.add_parser("routes", help="List supported route names")
    handoff_parser = commands.add_parser("handoff", help="Create an unverified Markdown handoff template")
    handoff_parser.add_argument("--route", required=True)
    handoff_parser.add_argument("--sha", default=None)
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            result = inspect()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["status"] == "PASS" else 1
        if args.command == "routes":
            data = load_json(ROOT, MAP)
            print("\n".join(f"{name}: {item['summary']}" for name, item in data["routes"].items()))
            return 0
        if args.command == "handoff":
            print(handoff_template(ROOT, args.route, args.sha))
            return 0
        result = route_context(paths=args.path, task=args.task, selected=args.selected,
                               generation=args.generation)
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(markdown_context(result))
        return 2 if result["status"] == "AMBIGUOUS" else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"agent-context: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
