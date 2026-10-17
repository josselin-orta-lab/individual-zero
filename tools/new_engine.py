#!/usr/bin/env python3
"""Preview or create an INACTIVE engine proposal, never register or birth it.

A scaffold has no inherited cognition, no Lab oracle, no active identity and
no scientific evidence. Only an explicit --apply writes fresh files into a
nonexistent destination. Preview is non-mutating. Do not copy current living
individual state or import parent runtime as a hidden fallback.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
GENERATION = re.compile(r"I[2-9][0-9]*\Z")
FOLDERS = ("lab", "modules", "runtime", "config")
ENGINE_SCHEMA = "individual-zero-engine-contract/v1"


def plan(generation: str, parent: str, output: Path) -> dict[str, str]:
    if not GENERATION.fullmatch(generation):
        raise ValueError("proposal generation must be I2 or later")
    if not re.fullmatch(r"I[1-9][0-9]*", parent) or int(parent[1:]) >= int(generation[1:]):
        raise ValueError("parent generation must be earlier and registered")
    reg = json.loads((ROOT / "config/engine-registry.json").read_text())
    if parent not in reg["generations"]:
        raise ValueError("parent is not registered")
    if generation in reg["generations"]:
        raise ValueError("generation already registered")
    out = output.resolve()
    if out == ROOT or ROOT in out.parents:
        # Internal paths are allowed only exactly at the expected motor root.
        if out != (ROOT / "src" / generation.lower()).resolve():
            raise ValueError("repository output must be src/<generation> exactly")
    if out.exists():
        raise FileExistsError("refusing to overwrite an existing engine or directory")
    contract = {
        "schema": ENGINE_SCHEMA,
        "generation": generation,
        "status": "proposal",
        "parent": parent,
        "paths": {
            "engine": "src/" + generation.lower(),
            "lab": "src/" + generation.lower() + "/lab",
            "runtime": "src/" + generation.lower() + "/runtime",
            "tests": "tests/" + generation.lower(),
            "documentation": "docs/engines/" + generation.lower(),
        },
        "entrypoints": {},
        "publication_owners": [],
        "constraints": {
            "first_person_observations_only": True,
            "uc_billed_cognition": True,
            "mortality_irreversible": True,
            "live_state_rollback": False,
            "hidden_oracle_input": False,
            "legacy_h1_h2_default": False,
        },
        "persistence": {"no_postmortem_recovery": True},
        "scientific": {"gate": "not_established"},
        "activation": "NOT_REGISTERED_NOT_EXECUTABLE",
    }
    files = {
        "engine.json": json.dumps(contract, indent=2) + "\n",
        "README.md": f"# {generation}: unregistered engine proposal\n\n"
                     f"Parent for design comparison: {parent}.\n"
                     "Not executable, not registered, not born or scientific GO.\n"
                     "Implement independent Lab, cognition, persistent identity and tests first.\n",
    }
    for folder in FOLDERS:
        files[folder + "/__init__.py"] = (
            f'"""{generation} {folder} proposal. No runnable engine."""\n'
        )
        files[folder + "/README.md"] = (
            f"# {generation} {folder}\n\n"
            "Dedicated generation-owned placeholder. No imported parent runtime.\n"
        )
    return files


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--generation", required=True)
    p.add_argument("--parent", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    try:
        files = plan(args.generation, args.parent, args.output)
        if args.apply:
            dest = args.output.resolve()
            dest.mkdir(parents=True, exist_ok=False)
            for rel, content in files.items():
                path = dest / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
        print(json.dumps({"generation": args.generation, "parent": args.parent,
                          "status": "PROPOSAL_CREATED" if args.apply else "PREVIEW_ONLY",
                          "registered": False, "executable": False,
                          "files": sorted(files)}, indent=2))
        return 0
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"engine proposal rejected: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
