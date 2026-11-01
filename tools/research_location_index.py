#!/usr/bin/env python3
"""Read-only catalog of research documents at their original Git paths.

Filesystem paths and filename hints are navigation only; not scientific verdicts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = Path("docs/research")
STAGE = re.compile(r"^stage(\d+)(?:[-_.]|$)", re.I)
GENERATION = re.compile(r"^(i[012])(?:[-_.]|$)", re.I)


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def classify(filename: str) -> dict[str, str]:
    name = filename.lower()
    stage = STAGE.match(name)
    generation = GENERATION.match(name)
    if stage:
        family = "stage-" + stage.group(1)
    elif generation:
        family = generation.group(1)
    elif name.startswith("m11"):
        family = "m11"
    elif re.match(r"^a\d", name):
        family = "a-series"
    else:
        family = "cross-cutting"
    if "prereg" in name or "pre-registration" in name:
        kind = "preregistration-hint"
    elif "audit" in name:
        kind = "audit-hint"
    elif "result" in name or "report" in name:
        kind = "result-or-report-hint"
    elif "protocol" in name:
        kind = "protocol-hint"
    elif "decision" in name or "verdict" in name:
        kind = "decision-hint"
    elif "test" in name or "validation" in name:
        kind = "test-or-validation-hint"
    else:
        kind = "unclassified"
    return {"family": family, "filename_hint": kind}


def catalog(root: Path = ROOT) -> dict:
    base = root / RESEARCH
    if not base.is_dir() or base.is_symlink():
        raise ValueError("research directory missing or symlinked")
    entries = []
    for path in sorted(base.glob("*.md")):
        if path.is_symlink() or not path.is_file():
            raise ValueError("unsafe research document: " + path.name)
        raw = path.read_bytes()
        entries.append({"path": path.relative_to(root).as_posix(),
                        "blob_sha": blob_sha(raw), "bytes": len(raw),
                        **classify(path.name)})
    groups: dict[str, int] = {}
    for row in entries:
        group = row["family"]
        groups[group] = groups.get(group, 0) + 1
    return {"schema": "individual-zero-research-location-index/v1",
            "status": "PATH_INVENTORY_ONLY", "total": len(entries),
            "families": dict(sorted(groups.items())), "documents": entries,
            "scientific_verdict": "NOT_EVALUATED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", help="Exact family, such as stage-12 or i1")
    parser.add_argument("--match", default="", help="Case-insensitive filename substring")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be nonnegative")
    index = catalog()
    rows = [d for d in index["documents"]
            if (not args.family or d["family"] == args.family)
            and args.match.lower() in d["path"].lower()]
    selected = {key: value for key, value in index.items() if key != "documents"}
    selected["matched"] = len(rows)
    selected["documents"] = rows[:args.limit]
    selected["truncated"] = len(rows) > args.limit
    if args.json:
        print(json.dumps(selected, indent=2))
    else:
        print("Research paths:", index["total"], "matching:", len(rows))
        print("Families:", ", ".join(f"{k}={v}" for k, v in index["families"].items()))
        for item in selected["documents"]:
            print(f"{item['family']} [{item['filename_hint']}] {item['path']} ({item['blob_sha']})")
        if selected["truncated"]:
            print("Refine --family or --match to inspect more.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
