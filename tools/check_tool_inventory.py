#!/usr/bin/env python3
"""Inventory script locations; do not infer historical experimental validity."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "config/tool-inventory.json"
ACTIVE = {"scripts/build_i1_fork.py", "scripts/test_i1_ci.py",
          "scripts/test_i1_artifact_parity.py", "scripts/check_engine_repository.py",
          "scripts/check_engine_contracts.py"}


def check(root: Path = ROOT) -> dict:
    doc = json.loads((root / "config/tool-inventory.json").read_text())
    active = doc["active_ci_scripts"]
    review = doc["research_or_legacy_review"]
    paths = active + review
    found = sorted(p.relative_to(root).as_posix()
                   for p in (root / "scripts").glob("*.py") if p.is_file())
    failures = []
    if len(paths) != len(set(paths)):
        failures.append("duplicate script classifications")
    if sorted(paths) != found:
        failures.append("inventory misses or adds tracked Python scripts")
    if not ACTIVE.issubset(set(active)):
        failures.append("required current I1 infrastructure misclassified")
    if not all(p.startswith("scripts/") and p.endswith(".py") for p in paths):
        failures.append("non-script path in inventory")
    return {"status": "FAIL" if failures else "PASS",
            "active": len(active), "review_required": len(review),
            "total": len(found), "errors": failures}


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, indent=2))
    sys.exit(bool(result["errors"]))
