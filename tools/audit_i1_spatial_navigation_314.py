#!/usr/bin/env python3
"""Read-only, fail-closed, noncausal audit of issue-314 durable life WALs.

This script never resumes a life, changes a world or feeds signals into I1.
Its outputs distinguish a cognitive proposal from a physical consequence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


def audit(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ValueError("WAL must be a regular existing file")
    # Cryptographically audit the *complete* journal before interpreting it.
    from i1lab.journal import HashChainedJournal
    attestation = HashChainedJournal.audit_durable_wal(str(path.resolve()))
    entries = []
    with path.open("rb") as stream:
        for raw in stream:
            record = json.loads(raw)
            entries.append(record["causal_event"])
    if len(entries) != attestation["verified_entries"]:
        raise ValueError("WAL changed during audit")
    kinds = Counter(row.get("kind") for row in entries)
    proposals = {}
    registrations = {}
    crossings = {}
    evaluations = {}
    for row in entries:
        data = row.get("data", {})
        kind = row.get("kind")
        if not isinstance(data, dict):
            continue
        t = row.get("t_monde")
        if kind == "i1_place_memory_option_proposed":
            ref = data.get("option_ref")
            if isinstance(ref, str):
                proposals[(t, ref)] = data
        elif kind == "i1_place_memory_option_registration":
            ref = data.get("option_ref")
            if isinstance(ref, str):
                registrations[(t, ref)] = bool(data.get("registered"))
        elif kind == "competition_cycle":
            for trace in data.get("traces", ()):
                if not isinstance(trace, dict):
                    continue
                ref = trace.get("option_ref")
                if isinstance(ref, str) and ref.startswith("option:place-memory:"):
                    if trace.get("crossed") is True:
                        crossings[(t, ref)] = True
        elif kind == "stage8_option_evaluation":
            ref = data.get("option_ref")
            if isinstance(ref, str) and ref.startswith("option:place-memory:"):
                evaluations[(t, ref)] = data
    return {
        "schema": "i1-spatial-navigation-audit/v1",
        "wal": path.name,
        "journal_entries": attestation["verified_entries"],
        "journal_head": attestation["head_hash"],
        "remembered_sightings": kinds["i1_entity_place_observed"],
        "recall_events": kinds["i1_place_memory_recalled"],
        "proposals": len(proposals),
        "registered": sum(bool(registrations.get(key)) for key in proposals),
        "crossed": sum(key in crossings for key in proposals),
        "evaluated": sum(key in evaluations for key in proposals),
        "unregistered": sum(not registrations.get(key, False) for key in proposals),
        "proposed_not_crossed": sum(key not in crossings for key in proposals),
        "physical_memory_actions": None,
        "physical_arrival_proven": False,
        "causal_learning_proven": False,
        "interpretation": (
            "WAL-only classification, not proof of physical memory navigation. "
            "Physical action/arrival attribution requires a separately verified "
            "life trajectory joined on the same WAL and SHA."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wal", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.wal)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        if args.output.exists():
            raise FileExistsError("audit report must not overwrite evidence")
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
