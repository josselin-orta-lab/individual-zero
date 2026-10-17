#!/usr/bin/env python3
"""A registered engine's executable software-test contract.

Read-only by default. --execute runs only checked-in argument vectors under
this Python interpreter, never via a shell. Local Git HEAD is reported as
provenance; GitHub PR state and scientific GO are NEVER inferred from it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_engine_contracts import inspect

SAFE_SUITE = re.compile(r"[a-z][a-z0-9_]*\Z")


def plan(engine: str, suite: str, *, root: Path = ROOT) -> list[list[str]]:
    report = inspect(root)
    if report["status"] != "PASS":
        raise ValueError("engine contracts failed: " + "; ".join(report["errors"]))
    registry = json.loads((root / "config/engine-registry.json").read_text())
    if engine != registry["active_generation"] or engine == "I0":
        raise ValueError("only the registered active engine can execute test suites")
    if not SAFE_SUITE.fullmatch(suite):
        raise ValueError("invalid suite name")
    source = registry["generations"][engine]["source"]
    contract = json.loads((root / source / "engine.json").read_text())
    available = contract.get("validation", {}).get("suites", {})
    if suite not in available:
        raise ValueError("undeclared suite " + suite)
    specs = available[suite]
    if not isinstance(specs, list) or not specs:
        raise ValueError("suite must declare nonempty executable commands")
    validated = []
    for args in specs:
        if (not isinstance(args, list) or len(args) < 2
                or any(not isinstance(x, str) or not x or "\x00" in x
                       for x in args)):
            raise ValueError("invalid suite argv")
        if args[0] == "-m":
            if args[1] != "unittest":
                raise ValueError("only Python unittest module is allowed")
        else:
            path = Path(args[0])
            if (path.is_absolute() or ".." in path.parts
                    or path.parts[0] not in ("scripts", "tools")
                    or path.suffix != ".py"
                    or not (root / path).is_file()):
                raise ValueError("script is outside the registered source tree")
        validated.append(list(args))
    return validated


def head_sha(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root,
        check=False, capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    opts = parser.parse_args()
    try:
        args = plan(opts.engine, opts.suite)
    except (ValueError, KeyError, OSError) as exc:
        print("engine suite refused: " + str(exc), file=sys.stderr)
        return 2
    report = {
        "engine": opts.engine, "suite": opts.suite,
        "local_head": head_sha(ROOT),
        "executed": opts.execute, "scientific_gate": "NOT_EVALUATED",
        "status": "PLANNED", "steps": [],
    }
    for spec in args:
        cmd = [sys.executable, *spec]
        step = {"argv": cmd, "status": "PLANNED"}
        if opts.execute:
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
            step["returncode"] = result.returncode
            step["status"] = "PASS" if result.returncode == 0 else "FAIL"
            if result.stdout:
                print(result.stdout, file=sys.stderr, end="")
            if result.stderr:
                print(result.stderr, file=sys.stderr, end="")
        report["steps"].append(step)
        if step["status"] == "FAIL":
            break
    if opts.execute:
        report["status"] = (
            "PASS" if len(report["steps"]) == len(args)
            and all(x["status"] == "PASS" for x in report["steps"]) else "FAIL"
        )
    if opts.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{opts.engine} {opts.suite}: {report['status']} @ {report['local_head']}")
        for row in report["steps"]:
            print(row["status"] + " " + " ".join(row["argv"]))
    return int(report["status"] == "FAIL")


if __name__ == "__main__":
    sys.exit(main())
