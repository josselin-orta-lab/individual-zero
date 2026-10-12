"""600 actual Stage11 cognitive world steps with NO Oracle/Bench (MVP v1.3.1).

Development evidence only: a fully internal, exhaustive hash-chained life is
checked offline after real, irreversible physical execution. No saved life
state, rollback, re-execution, oracle call, or scientific Golden promotion.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.abc
import json
import sys


STEPS = 600
PROTOCOL = "stage11-autonomous-600-journal-v1"
_DENIED = frozenset({"lab.oracle", "lab.bench", "lab.evaluation_trace"})


class _DenyScience(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in _DENIED:
            raise ImportError("external scientific module is forbidden: " + fullname)
        return None


def run_probe(*, steps: int = STEPS, observer_export_dir: str | None = None) -> dict[str, object]:
    if type(steps) is not int or steps < 1:
        raise ValueError("steps must be a positive physical-step count")
    already = _DENIED.intersection(sys.modules)
    if already:
        raise RuntimeError("external science was already loaded: " + ", ".join(sorted(already)))
    deny = _DenyScience()
    sys.meta_path.insert(0, deny)
    try:
        from .determinism import canonical_causal_bytes, sha256_hex
        from .independent_journal_audit import audit_export_bytes
        from .mortal_execution import MortalStatus
        from .stage11_reference_fixture import build_stage11_reference_runtime
        if observer_export_dir is not None:
            from .observer_world_capture import capture_closed_world, publish_recorded_world
            from pathlib import Path

        individual = build_stage11_reference_runtime(
            enable_geography=True, autonomous_mortal=True,
        )
        if individual.bench is not None:
            raise AssertionError("autonomous I0 unexpectedly owns a Bench")
        if individual.stage3.substrate.evaluation_trace is not None:
            raise AssertionError("autonomous I0 unexpectedly owns EvaluationTrace")
        physical_frames: list[dict] = []
        actions: Counter[str] = Counter()
        anchors: list[dict[str, object]] = []
        anchor_steps = {1, (steps + 1) // 2, steps}

        for world_step in range(1, steps + 1):
            # The real, unchanged ActionControl/WorldBody path is called once.
            # A death is terminal, NOT an invitation to retry or erase it.
            result = individual.run_step()
            if (
                result.execution_status != "applied"
                or individual.scheduler.t_monde != world_step
                or individual.stage3.substrate.mortal_status is not MortalStatus.ACTIVE
            ):
                raise AssertionError(
                    "autonomous reference life did not survive one genuine step "
                    f"{world_step}: {result.execution_status!r}"
                )
            primitive = result.command_primitive
            if not isinstance(primitive, str) or not primitive:
                raise AssertionError("applied world step has no real command")
            actions[primitive] += 1
            if observer_export_dir is not None:
                physical_frames.append(capture_closed_world(
                    individual.world, t_monde=world_step,
                    closed_event=dict(individual.journal.entries[-1].causal_event),
                ))
            if world_step in anchor_steps:
                # Observation-only hash/count receipt. NO snapshot or restore.
                anchors.append({
                    "world_step": world_step,
                    "occurrences": len(individual.journal.entries),
                    "head_hash": individual.journal.head_hash,
                })

        journal = individual.journal
        if not journal.verify():
            raise AssertionError("I0's full internal SHA-256 chain failed")
        entries = journal.entries
        for receipt in anchors:
            cursor = receipt["occurrences"] - 1
            if (cursor < 0 or cursor >= len(entries)
                    or entries[cursor].event_hash != receipt["head_hash"]):
                raise AssertionError(
                    "one observed prefix head no longer matches the complete journal"
                )
        image = journal.canonical_bytes()
        audited = audit_export_bytes(
            image,
            expected_head=journal.head_hash,
            expected_count=len(journal.entries),
        )
        kinds = Counter(entry.causal_event.get("kind") for entry in journal.entries)
        if individual.stage3.substrate.snapshots._snapshots:
            raise AssertionError(
                "mortal I0 created historical life snapshots during the probe"
            )
        if (
            audited.world_steps_closed != steps
            or audited.autobiographical_commits != steps
            or audited.terminal_deaths != 0
            or kinds["perceptual_capture"] != steps
            or kinds["world_transition_experienced"] != steps
            or kinds["auto_segment_commit"] != steps
            or any("rollback" in str(kind) for kind in kinds)
        ):
            raise AssertionError(
                "mortal cognitive journal is incomplete or contains historical rollback"
            )
        loaded = sorted(_DENIED.intersection(sys.modules))
        if loaded:
            raise AssertionError("external science loaded during I0 life: " + ", ".join(loaded))

        report = {
            "protocol_version": PROTOCOL,
            "individual_id": individual.individual_id,
            "classification": "public_development_diagnostic_not_heldout",
            "scientific_verdict": None,
            "operator_stage_acceptance_required": True,
            "steps_requested": steps,
            "steps_physically_executed": audited.world_steps_closed,
            "cognitive_autobiographical_commits": audited.autobiographical_commits,
            "perceptual_captures": kinds["perceptual_capture"],
            "world_transitions": kinds["world_transition_experienced"],
            "terminal_deaths": audited.terminal_deaths,
            "action_counts": dict(sorted(actions.items())),
            "journal_event_count": audited.occurrences,
            "journal_head_sha256": audited.head_hash,
            "journal_bytes_sha256": sha256_hex(image),
            "journal_canonical_bytes": len(image),
            "journal_prefix_anchors": anchors,
            "unexamined_kinds": list(audited.unexamined_event_kinds),
            "offline_audit_completed": True,
            "external_oracle_loaded": False,
            "external_bench_loaded": False,
            "historical_life_snapshot_or_restore_used": False,
            "physical_truth_attested_by_independent_oracle": False,
        }
        report["evidence_sha256"] = sha256_hex(canonical_causal_bytes(report))
        if observer_export_dir is not None:
            publish_recorded_world(
                directory=Path(observer_export_dir),
                individual_id=individual.individual_id,
                config=individual.world.config,
                frames=physical_frames,
                canonical_journal=image,
                journal_head=audited.head_hash,
                journal_count=audited.occurrences,
                journal_sha256=sha256_hex(image),
            )
        return report
    finally:
        sys.meta_path.remove(deny)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--steps", type=int, default=STEPS,
        help="physical steps for a local smoke diagnostic (CI uses 600)",
    )
    parser.add_argument("--observer-export-dir", type=str, default=None,
                        help="operator-only capture directory, never a life checkpoint")
    args = parser.parse_args(argv)
    result = run_probe(steps=args.steps, observer_export_dir=args.observer_export_dir)
    print("stage11_autonomous_600_step=" + json.dumps(
        result, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ))


if __name__ == "__main__":
    main()
