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
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
GENERATION = re.compile(r"I[2-9][0-9]*\Z")
FOLDERS = ("lab", "modules", "runtime", "config")
ENGINE_SCHEMA = "individual-zero-engine-contract/v1"


def plan(generation: str, parent: str, output: Path, *,
         root: Path = ROOT) -> dict[str, str]:
    if not GENERATION.fullmatch(generation):
        raise ValueError("proposal generation must be I2 or later")
    if not re.fullmatch(r"I[1-9][0-9]*", parent) or int(parent[1:]) >= int(generation[1:]):
        raise ValueError("parent generation must be earlier and registered")
    reg = json.loads((root / "config/engine-registry.json").read_text())
    if parent not in reg["generations"]:
        raise ValueError("parent is not registered")
    if generation in reg["generations"]:
        raise ValueError("generation already registered")
    out = output.resolve()
    if out == root or root in out.parents:
        # Internal paths are allowed only exactly at the expected motor root.
        if out != (root / "src" / generation.lower()).resolve():
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



def plan_workspace(generation: str, parent: str, output: Path, *,
                   root: Path = ROOT) -> dict[str, str]:
    """Plan motor, Lab, tests, documentation and inert CI sample.

    Only the canonical repository layout can own companion paths. Neither a
    registered engine nor an active GitHub Actions workflow is created.
    """
    root = root.resolve()
    output = output.resolve()
    if output != (root / "src" / generation.lower()).resolve():
        raise ValueError("workspace proposal must target src/<generation>")
    engine_files = plan(generation, parent, output, root=root)
    stem = generation.lower()
    tests = root / "tests" / stem
    docs = root / "docs" / "engines" / stem
    if tests.exists() or tests.is_symlink() or docs.exists() or docs.is_symlink():
        raise FileExistsError("generation tests or documentation already exist")
    result = {f"src/{stem}/{name}": data
              for name, data in engine_files.items()}
    result[f"tests/{stem}/test_proposal.py"] = (
        '"""Non-executable, never-registered engine proposal checks."""\n'
        "import json\nfrom pathlib import Path\nimport unittest\n\n"
        "ROOT = Path(__file__).resolve().parents[2]\n\n"
        "class EngineProposalTests(unittest.TestCase):\n"
        "    def test_engine_is_not_activated(self):\n"
        f'        contract = json.loads((ROOT / "src/{stem}/engine.json").read_text())\n'
        '        registry = json.loads((ROOT / "config/engine-registry.json").read_text())\n'
        f'        self.assertEqual(contract["generation"], "{generation}")\n'
        '        self.assertEqual(contract["status"], "proposal")\n'
        '        self.assertFalse(contract["entrypoints"])\n'
        '        self.assertEqual(contract["activation"], "NOT_REGISTERED_NOT_EXECUTABLE")\n'
        f'        self.assertNotIn("{generation}", registry["generations"])\n'
        '        self.assertEqual(contract["scientific"]["gate"], "not_established")\n'
    )
    result[f"docs/engines/{stem}/STATUS.md"] = (
        f"# {generation} engineering status\n\n"
        "**PROPOSAL ONLY. NOT REGISTERED. NOT EXECUTABLE.**\n\n"
        f"Design parent: {parent}. Own Lab: src/{stem}/lab/.\n"
        "No living engine, scientific evidence or approved activation.\n"
        "Before registration: implement independent cognition and tests, review\n"
        "owner roster and durability contracts, then validate cold recovery.\n"
    )
    result[f"docs/engines/{stem}/ARCHITECTURE.md"] = (
        f"# {generation} proposed architecture\n\n"
        "Version-owned lab/, runtime/, modules/ and config/.\n"
        "Do not import the parent's Lab or memory as a fallback.\n"
        "No runtime is instantiated by this scaffold.\n"
    )
    result[f"docs/engines/{stem}/TEST_PLAN.md"] = (
        f"# {generation} test plan (unimplemented)\n\n"
        "1. Structural contract and isolated Lab.\n"
        "2. Real birth and first-person observations.\n"
        "3. Cognition and UC accounting without hidden oracle access.\n"
        "4. Irreversible death and authenticated persistence.\n"
        "5. Independent scientific trials, without inherited oracles.\n\n"
        "**Every item is NOT EVALUATED until implemented.**\n"
    )
    result[f"docs/engines/{stem}/CI_WORKFLOW_TEMPLATE.yml"] = (
        f"name: {generation} structure (example, NOT installed)\n"
        "on:\n"
        "  pull_request:\n"
        "    paths:\n"
        f"      - 'src/{stem}/**'\n"
        f"      - 'tests/{stem}/**'\n"
        "jobs:\n"
        "  structure:\n"
        "    uses: ./.github/workflows/engine-structural.yml\n"
        "    with:\n"
        f"      engine: {generation}\n"
        "# Install under .github/workflows ONLY after the engine is registered\n"
        "# and its structural and full lifecycle gates are implemented.\n"
    )
    return result


def apply_workspace(generation: str, parent: str, output: Path, *,
                    root: Path = ROOT) -> list[str]:
    """Create an inert multi-root proposal only if all destinations are free."""
    root = root.resolve()
    files = plan_workspace(generation, parent, output, root=root)
    stem = generation.lower()
    roots = [root / "src" / stem, root / "tests" / stem,
             root / "docs" / "engines" / stem]
    if any(path.exists() or path.is_symlink() for path in roots):
        raise FileExistsError("generation target already exists")
    made = []
    try:
        for path in roots:
            path.mkdir(parents=True, exist_ok=False)
            made.append(path)
        for rel, content in files.items():
            path = root / rel
            if not any(path.is_relative_to(scope) for scope in roots):
                raise ValueError("refusing to write outside engine-owned paths")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    except Exception:
        # Only freshly created, unregistered source scaffolds are discarded.
        # No living or durable individual state is ever involved here.
        for path in reversed(made):
            shutil.rmtree(path)
        raise
    return sorted(files)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--generation", required=True)
    p.add_argument("--parent", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    try:
        if args.apply:
            created = apply_workspace(args.generation, args.parent, args.output)
            scope = "ENGINE_TESTS_DOCS_AND_INERT_CI_SAMPLE"
        elif args.output.resolve() == (ROOT / "src" / args.generation.lower()).resolve():
            created = sorted(plan_workspace(args.generation, args.parent, args.output))
            scope = "ENGINE_TESTS_DOCS_AND_INERT_CI_SAMPLE"
        else:
            # External previews remain non-mutating, for compatibility.
            created = sorted(plan(args.generation, args.parent, args.output))
            scope = "ENGINE_ONLY_EXTERNAL_PREVIEW"
        print(json.dumps({"generation": args.generation, "parent": args.parent,
                          "status": "PROPOSAL_CREATED" if args.apply else "PREVIEW_ONLY",
                          "scope": scope,
                          "registered": False, "executable": False,
                          "files": created}, indent=2))
        return 0
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"engine proposal rejected: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
