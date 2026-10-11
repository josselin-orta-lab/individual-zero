#!/usr/bin/env python3
"""Read-only static inventory for post-Stage-10/11 I0 MVP v1.3 migration.

Run AFTER both stages are operator-accepted and the integration SHA is frozen.
This script never mutates source or runtime state and makes NO GO/NO-GO decision.
Matches are candidates for human assessment, not verified defects.

Usage:
    python3 scripts/audit_mvp_v1_3_dependencies.py --root .
    python3 scripts/audit_mvp_v1_3_dependencies.py --root . --json-out /tmp/i0-impact.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    id: str
    priority: str
    pattern: str
    note: str


RULES = (
    Rule("life_rollback", "P0", r"(?i)\b(?:lethal_rollback|rolled_back|rollback_letal|rollback_l[eé]tal|rollback_sequence_mask|new_attempt_after_rollback|restore_after_lethal|resume_after_rollback)\b", "Old lethal retry/restoration control path"),
    Rule("lethal_checkpoint", "P0", r"(?i)\b(?:LETHAL_CHECKPOINT|checkpoint_l[eé]tal|lethal_checkpoint|R_letal_max|R_letal_consecutif)\b", "Removed checkpoint or repeat-lethal counter"),
    Rule("world_rewind", "P0", r"(?i)\b(?:world|_world|snapshots|_snapshots)\.(?:restore_causal_state|restore)\s*\(", "World or snapshot restore: classify actual runtime invocation"),
    Rule("state_restore", "P1", r"\brestore_causal_state\s*\(|\brestore\s*\(", "State import: classify permitted offline current-state load versus forbidden life rewind"),
    Rule("rollback_generic", "P1", r"(?i)\b(?:rollback|rollbacks|revert|compensat(?:e|ion|ing))\b", "May be technical draft abort, legacy comment or forbidden committed-state rollback"),
    Rule("journal_writer", "P1", r"\b(?:HashChainedJournal|JournalViews|AutoSegmentCommit|commit_autobiographical|journal\.append|_journal\.append|JOURNAL\.\w+)\b", "Exhaustive journal producer or autobiographical projection"),
    Rule("journal_reader", "P1", r"\b(?:journal\.entries|journal\.canonical_bytes|_journal\.entries|journal\.updates|journal_updates|technical_journal|JournalEvent)\b", "Potential consumer depending on complete history"),
    Rule("snapshot_history", "P1", r"\b(?:SnapshotManager|SnapshotType|snapshot_taken|periodic_snapshot|snapshot_restored|copy_snapshot)\b", "Separate copying/current persistence from historical restoration"),
    Rule("consolidation_update", "P1", r"(?i)\b(?:rebase|rebasage|post_cutpoint|postcutpoint|consolidation_transaction|consolidation_replay)\b", "Stage 10 post-cutpoint delta and coordinated publish path"),
    Rule("world_lethal_boundary", "CHECK", r"\b(?:transition\.lethal|lethal_reasons|WorldBody\.apply|world\.apply|death_confirmed|count_lethal_transition)\b", "Check world parity and terminal handling"),
    Rule("runtime_terminal", "CHECK", r"\b(?:execution\.status|execution_status|close_step\s*\(|open_step\s*\()\b", "Check no post-death continuation"),
    Rule("operator_stage_gate", "CHECK", r"(?i)\b(?:scientific_verdict|stage_completed|held.out|golden|operator_signoff|no.go)\b", "Keep stage and scientific evidence separated"),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checkout_sha(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=8,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if re.fullmatch(r"[0-9a-f]{40}", value) else None


def scan(root: Path) -> dict[str, object]:
    compiled = [(rule, re.compile(rule.pattern)) for rule in RULES]
    findings: list[dict[str, object]] = []
    files: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []
    paths = sorted(set(
        list((root / "src").rglob("*.py"))
        + list((root / "tests").rglob("*.py"))
        + list((root / "scripts").rglob("*.py"))
    ))
    for path in paths:
        if not path.is_file() or path.resolve() == Path(__file__).resolve():
            continue
        relative = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
            lines = raw.decode("utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            failures.append({"path": relative, "error": type(exc).__name__})
            continue
        files.append({"path": relative, "sha256": sha256(raw), "lines": len(lines)})
        scope = "test_fixture" if relative.startswith("tests/") else "implementation_or_tool"
        for number, line in enumerate(lines, start=1):
            for rule, regex in compiled:
                for match in regex.finditer(line):
                    findings.append({
                        "path": relative,
                        "line": number,
                        "rule": rule.id,
                        "priority": rule.priority,
                        "scope": scope,
                        "snippet": line.strip()[:220],
                        "match": match.group(0),
                        "note": rule.note,
                    })
    counts = Counter(item["rule"] for item in findings)
    return {
        "contract": "i0-mvp-v1.3-audit-static-v1",
        "disposition": "INVENTORY_ONLY_NOT_ACCEPTANCE",
        "source_root": str(root),
        "checkout_sha": checkout_sha(root),
        "files_scanned": len(files),
        "file_digests": files,
        "rule_catalog": [asdict(rule) for rule in RULES],
        "finding_counts": dict(sorted(counts.items())),
        "findings": findings,
        "read_errors": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="Frozen checkout root; source is never changed")
    parser.add_argument("--json-out", type=Path,
                        help="Optional report path, preferably outside the checkout")
    parser.add_argument("--examples", type=int, default=4,
                        help="Number of example locations per rule on stdout")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not (root / "src").is_dir() or not (root / "tests").is_dir():
        parser.error("root must contain src/ and tests/")
    if args.examples < 0:
        parser.error("--examples must be >= 0")
    report = scan(root)
    print("Individual Zero v1.3 — READ-ONLY dependency inventory")
    print("Checkout:", report["checkout_sha"] or "UNKNOWN (not a Git checkout)")
    print("Files scanned:", report["files_scanned"])
    print("This is NOT a validation or a migration GO decision.")
    for rule in RULES:
        hits = [
            row for row in report["findings"] if row["rule"] == rule.id
        ]
        if not hits:
            continue
        print(f"  {rule.priority:5} {rule.id:24} {len(hits):5} matches")
        for row in hits[:args.examples]:
            print(f"      {row['path']}:{row['line']} {row['snippet'][:100]}")
    if args.json_out:
        destination = args.json_out.expanduser().resolve()
        if destination == root or root in destination.parents:
            parser.error("--json-out must be OUTSIDE the audited checkout")
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            print(f"Cannot write JSON report: {exc}", file=sys.stderr)
            return 2
        print("JSON report:", destination)
    if report["read_errors"]:
        print("Unreadable files found; inventory is incomplete.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
