"""Stage 11 fixed 600-step software stability diagnostic, public only.

See docs/research/stage11-600-step-public-software-stability-protocol.en.md.
No parameter tuning, held-out selection, oracle read, or scientific verdict.
"""
from __future__ import annotations

import json

from .determinism import canonical_causal_bytes, sha256_hex
from .snapshots import SnapshotType
from .stage11_reference_fixture import build_stage11_reference_runtime

PROTOCOL = "stage11-public-600-step-software-v1"
STEPS = 600
SNAPSHOT_STEPS = (1, 300, 600)


def run_once() -> dict[str, object]:
    """Run the unchanged Stage-11 geographic reference world once."""
    runner = build_stage11_reference_runtime(enable_geography=True)
    manager = runner.stage3.substrate.snapshots
    initial = {
        "protocol": PROTOCOL,
        "steps": STEPS,
        "snapshot_steps": SNAPSHOT_STEPS,
        "world": runner.world.config.as_dict(),
        "layout": runner.world._layout.as_dict(),
        "stage11_version": runner._stage11_config.version,
        "budget_version": runner._config.compute_budget.version,
        "equipment_version": runner.equipment.version,
    }
    input_hash = sha256_hex(canonical_causal_bytes(initial))
    snapshots: list[tuple[int, str, str]] = []
    actions: dict[str, int] = {}
    for step in range(1, STEPS + 1):
        try:
            result = runner.run_step()
        except Exception as exc:
            raise AssertionError(
                f"public Stage 11 600-step run stopped at physical step {step}: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        if result.execution_status != "applied" or runner.scheduler.t_monde != step:
            raise AssertionError(
                "Stage 11 software probe did not complete world step "
                f"{step}: status={result.execution_status}, "
                f"t_monde={runner.scheduler.t_monde}"
            )
        primitive = result.command_primitive
        if type(primitive) is not str:
            raise AssertionError("applied command has no primitive")
        actions[primitive] = actions.get(primitive, 0) + 1
        if step in SNAPSHOT_STEPS:
            snapshot = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id=runner.individual_id,
                t_monde=step,
                cycle=0,
                attempt_ref=None,
                owners=runner.causal_owners,
                versions={"stage11": runner._stage11_config.version},
            )
            if not manager.verify(snapshot.id):
                raise AssertionError(f"invalid periodic snapshot at step {step}")
            snapshots.append((step, snapshot.id, snapshot.sha256))

    if not runner.journal.verify():
        raise AssertionError("invalid final append-only causal journal")

    events = tuple(entry.causal_event for entry in runner.journal.entries)
    captures = tuple(
        (event["data"]["position"]["x"], event["data"]["position"]["y"])
        for event in events if event.get("kind") == "perceptual_capture"
    )
    if len(captures) != STEPS:
        raise AssertionError(
            f"expected {STEPS} physical captures, received {len(captures)}"
        )
    charges = tuple(
        event["data"] for event in events
        if event.get("kind") == "compute_charge"
    )
    for event in events:
        if event.get("kind") != "stage11_intrinsic_evaluation":
            continue
        ids = event["data"]["signal_ids"]
        if len(ids) != len(set(ids)):
            raise AssertionError(
                "INV-14 duplicate intrinsic signal during long replay"
            )
    states = {
        owner.owner_id: owner.export_causal_state()
        for owner in runner.causal_owners
    }
    if len(states) != len(runner.causal_owners):
        raise AssertionError("duplicate causal owner during long replay")

    return {
        "protocol_version": PROTOCOL,
        "classification": "public_software_diagnostic_not_heldout",
        "scientific_verdict": None,
        "steps_completed": STEPS,
        "input_sha256": input_hash,
        "snapshot_receipts": snapshots,
        "physical_capture_count": len(captures),
        "distinct_physical_sites": len(set(captures)),
        "action_counts": dict(sorted(actions.items())),
        "modulation_transitions": sum(
            e.get("kind") == "stage11_modulation_transition" for e in events
        ),
        "intrinsic_evaluations": sum(
            e.get("kind") == "stage11_intrinsic_evaluation" for e in events
        ),
        "accepted_uc": sum(
            entry["requested_uc"] for entry in charges
            if entry["accepted"] is True
        ),
        "rejected_uc_requests": sum(
            entry["accepted"] is False for entry in charges
        ),
        "journal_event_count": len(events),
        "journal_sha256": sha256_hex(runner.journal.canonical_bytes()),
        "journal_head": runner.journal.head_hash,
        "owner_state_sha256": sha256_hex(canonical_causal_bytes(states)),
    }


def run_probe() -> dict[str, object]:
    first = run_once()
    second = run_once()
    if first != second:
        differing = sorted(
            key for key in first
            if first[key] != second.get(key)
        )
        raise AssertionError(
            "independent 600-step executions diverged in: "
            + ", ".join(differing)
        )
    result = dict(first)
    result["identical_independent_reexecution"] = True
    result["evidence_sha256"] = sha256_hex(canonical_causal_bytes(result))
    return result


def main() -> None:
    print(
        "stage11_600_step_software="
        + json.dumps(run_probe(), sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
