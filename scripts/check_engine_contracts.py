#!/usr/bin/env python3
"""Validate registered generation contracts without importing cognitive code."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = re.compile(r"I[1-9][0-9]*\Z")
REQUIRED = ("engine", "lab", "runtime", "tests", "documentation")
TRUE_INVARIANTS = ("first_person_observations_only", "uc_billed_cognition",
                   "mortality_irreversible", "hidden_oracle_input")
OWNER_SET = {"value_and_needs", "causal_model", "perception", "metacognition_health"}


def inspect(root: Path = ROOT) -> dict:
    errors = []
    try:
        registry = json.loads((root / "config/engine-registry.json").read_text())
    except (OSError, ValueError) as exc:
        return {"status": "FAIL", "errors": [f"cannot read registry: {exc}"]}
    generations = registry.get("generations", {})
    active = registry.get("active_generation")
    if active not in generations:
        errors.append("active generation is missing from registry")
    for name, entry in sorted(generations.items()):
        if name == "I0":
            if entry.get("role") != "frozen_reference":
                errors.append("I0 must stay frozen")
            continue
        if not GEN.fullmatch(name):
            errors.append("invalid registered generation " + name)
            continue
        source = entry.get("source", "")
        if source != f"src/{name.lower()}":
            errors.append(name + ": source path mismatch")
            continue
        path = root / source / "engine.json"
        try:
            raw = json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            errors.append(name + ": unreadable engine.json: " + str(exc))
            continue
        if raw.get("schema") != "individual-zero-engine-contract/v1":
            errors.append(name + ": unsupported contract schema")
        if raw.get("generation") != name:
            errors.append(name + ": contract generation mismatch")
        if raw.get("parent") != entry.get("parent"):
            errors.append(name + ": parent mismatch")
        expected_status = "active" if name == active else "inactive"
        if raw.get("status") != expected_status:
            errors.append(name + ": active status mismatch")
        paths = raw.get("paths", {})
        if not isinstance(paths, dict):
            errors.append(name + ": invalid paths")
            continue
        for key in REQUIRED:
            expected = source if key == "engine" else (
                f"tests/{name.lower()}" if key == "tests" else
                f"docs/engines/{name.lower()}" if key == "documentation" else
                f"{source}/{key}"
            )
            if paths.get(key) != expected:
                errors.append(name + ": invalid owned path " + key)
            if not (root / expected).is_dir():
                errors.append(name + ": missing owned directory " + expected)
        if paths.get("lab") != entry.get("lab") or paths.get("runtime") != entry.get("overlays"):
            errors.append(name + ": registry/contract Lab or runtime mismatch")
        if (root / "src/lab").exists():
            errors.append("shared src/lab is prohibited")
        for key in ("runtime", "birth"):
            if raw.get("entrypoints", {}).get(key) != entry.get(key):
                errors.append(name + ": registered " + key + " differs")
        if raw.get("build", {}).get("script") != entry.get("build"):
            errors.append(name + ": build script differs")
        if raw.get("validation", {}).get("workflow") != entry.get("ci"):
            errors.append(name + ": CI workflow differs")
        if raw.get("validation", {}).get("harness") != entry.get("tester"):
            errors.append(name + ": tester differs")
        flags = raw.get("constraints", {})
        if not isinstance(flags, dict) or any(flags.get(x) is not True for x in TRUE_INVARIANTS[:3]):
            errors.append(name + ": essential lifetime constraints are not enabled")
        if (not isinstance(flags, dict) or flags.get("hidden_oracle_input") is not False
                or flags.get("live_state_rollback") is not False
                or flags.get("legacy_h1_h2_default") is not False):
            errors.append(name + ": forbidden oracle, rollback or H1/H2 setting")
        owners = raw.get("publication_owners")
        if not isinstance(owners, list) or len(owners) != 4 or set(owners) != OWNER_SET:
            errors.append(name + ": publication owner roster mismatch")
        if raw.get("persistence", {}).get("no_postmortem_recovery") is not True:
            errors.append(name + ": terminal recovery must be refused")
        if raw.get("scientific", {}).get("gate") == "GO":
            errors.append(name + ": scientific GO cannot be self-declared in contract")
    return {"status": "FAIL" if errors else "PASS",
            "active_generation": active, "checked": sorted(
                x for x in generations if x != "I0"), "errors": errors}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    opts = ap.parse_args()
    result = inspect()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    sys.exit(main())
