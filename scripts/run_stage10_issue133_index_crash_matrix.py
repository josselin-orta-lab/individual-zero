"""Real os._exit crash matrix for Stage10 paid index h publication (issue #133).

Parent audits raw fsynced WAL without instantiating I0 or claiming that a
Stage12 WAL is a recoverable M11 SQLite life.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

POINTS = ("before_h", "after_h_before_retire", "after_retire")
EXPECTED = {
    "before_h": "stage10_consolidation_index_maintenance_charged",
    "after_h_before_retire": "stage10_consolidation_version_activated",
    "after_retire": "stage10_consolidation_index_retired",
}

CHILD = r"""
import os
from pathlib import Path
import sys
from unittest.mock import patch

from scripts.run_stage10_issue133_paid_index import run_life
from i0.modules.consolidation_pending_index import ChargedPendingEpisodeIndex
from lab.stage10_runtime import Stage10Runtime
from lab.consolidation_publication import Stage10PublicationCoordinator

folder, crash_point = sys.argv[1:]
def hard_exit():
    os._exit(76)

orig_publish = Stage10PublicationCoordinator.publish
orig_retire = ChargedPendingEpisodeIndex.acknowledge_published
orig_write = Stage10Runtime._write

def checked_publish(self, *args, **kwargs):
    if crash_point == "before_h":
        hard_exit()
    return orig_publish(self, *args, **kwargs)

def checked_retire(self, *args, **kwargs):
    if crash_point == "after_h_before_retire":
        hard_exit()
    return orig_retire(self, *args, **kwargs)

def checked_write(self, *args, **kwargs):
    value = orig_write(self, *args, **kwargs)
    if (crash_point == "after_retire"
            and kwargs.get("kind") == "stage10_consolidation_index_retired"):
        hard_exit()
    return value

with patch.object(Stage10PublicationCoordinator, "publish", checked_publish), \
     patch.object(ChargedPendingEpisodeIndex, "acknowledge_published", checked_retire), \
     patch.object(Stage10Runtime, "_write", checked_write):
    run_life(Path(folder), "reference_untrained", 20.0, "pass06-batch06-indexed")
raise AssertionError("expected a real fault while publishing first h")
"""


def canonical(row):
    return json.dumps(
        row, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def inspect_wal(path: Path, point: str):
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise AssertionError("incomplete fsynced WAL record")
    previous = "0" * 64
    events = []
    seen = set()
    for i, line in enumerate(raw.splitlines()):
        record = json.loads(line)
        assert canonical(record) == line, ("noncanonical", i)
        assert record["index"] == i and record["previous_hash"] == previous
        assert record["event_id"] not in seen, ("duplicate event ID", i)
        seen.add(record["event_id"])
        expected = sha256(
            bytes.fromhex(previous)
            + canonical({"event_id": record["event_id"],
                         "causal_event": record["causal_event"]})
        ).hexdigest()
        assert record["event_hash"] == expected, ("broken WAL SHA-256", i)
        previous = expected
        events.append(record["causal_event"])
    kinds = [event["kind"] for event in events]
    marker = EXPECTED[point]
    assert kinds[-1] == marker, (point, kinds[-4:])
    assert kinds.count("stage10_consolidation_index_maintenance_charged") == 1
    assert kinds.count("stage10_consolidation_version_activated") == (
        0 if point == "before_h" else 1)
    assert kinds.count("stage10_consolidation_index_retired") == (
        1 if point == "after_retire" else 0)
    charge = next(e["data"] for e in events if e["kind"] ==
                  "stage10_consolidation_index_maintenance_charged")
    assert charge["operation"] == "index_maintenance"
    assert charge["count"] == charge["requested_uc"]
    assert 0 <= charge["consumed_step_uc"] <= 100
    assert 0 <= charge["consumed_period_uc"] <= 600
    if point != "before_h":
        activation = next(e["data"] for e in events if e["kind"] ==
                          "stage10_consolidation_version_activated")
        assert charge["consolidation_id"] == activation["consolidation_id"]
        assert charge["episode_refs"] == activation["batch"]
    if point == "after_retire":
        retired = events[-1]["data"]
        assert retired["episode_refs"] == charge["episode_refs"]
        assert retired["pending_after"] == (
            charge["pending_before"] - charge["count"])
    opened = [e["t_monde"] for e in events if e["kind"] == "step_opened"]
    closed = [e["t_monde"] for e in events if e["kind"] == "step_closed"]
    assert len(opened) == len(closed) + 1, (
        "crash simulation accidentally completed a physical world step", point)
    assert opened[-1] not in closed
    assert not any(e["kind"] == "individual_death_confirmed" for e in events), (
        "test is not a physical death"
    )
    return {
        "point": point, "exit_code": 76,
        "records": len(events), "journal_head": previous,
        "interrupted_world_step": opened[-1],
        "last_kind": kinds[-1],
        "charge_uc": charge["requested_uc"],
        "published_h": point != "before_h",
        "index_retired": point == "after_retire",
        "may_recover_stage12": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    summaries = []
    # Even a failed subprocess leaves its WAL and diagnostic stderr for audit.
    for point in POINTS:
        directory = root / point
        directory.mkdir()
        completed = subprocess.run(
            [sys.executable, "-c", CHILD, str(directory), point],
            capture_output=True, text=True, timeout=160,
        )
        (directory / "child-stdout.txt").write_text(completed.stdout)
        (directory / "child-stderr.txt").write_text(completed.stderr)
        if completed.returncode != 76:
            raise AssertionError(
                f"{point}: child exit {completed.returncode}: "
                f"{completed.stderr[-2000:]}")
        item = inspect_wal(directory / "life.wal", point)
        summaries.append(item)
        (directory / "audit.json").write_text(
            json.dumps(item, indent=2, sort_keys=True) + "\n")
    report = {"source_sha": subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True,
        text=True).stdout.strip(),
        "preregistration":
        "docs/research/stage10-issue133-index-crash-matrix-prereg-2026-10-13.fr.md",
        "mode": "genuine_os_exit_76_no_recovery",
        "audits": summaries, "status": "pass_wal_integrity_only",
        "recovery_certified": False,
        "operator_accepted": False,
    }
    (root / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
