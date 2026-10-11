"""Public opt-in Stage-11 Scheduler capacity-admission A/B comparison.

The capacity guard inspects only existing UC counters; Lab observes the
subsequent journal, physical captures and snapshots. No safety oracle enters
cognition and none of these public trials are held-out science.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .snapshots import SnapshotType
from .stage11_geographic_probe import _positions
from .stage11_routed_junction_probe import build_public_route_runtime
from .stage11_transient_hidden_route_probe import schedule_for


PROTOCOL = "stage11-public-geo-capacity-admission-guard-dev-v1"
CONDITIONS = (
    ("control", 4, 4),
    ("hidden_transient", 4, 4),
    ("control", 3, 4),
    ("control", 0, 0),
)
STEPS = 10
SNAPSHOT_STEPS = (4, 5)
LEGACY_JOURNAL_SHA256_4UC = {
    "control": "97ce45cb83a16329442d4da94bdde4ecc8d7346c2bebb0ae5dca04a9d234ad41",
    "hidden_transient": "a93ef4d2326eea618be7a47a4db8ab7957c2678cd88fa07040fff15ff413fd6e",
}


@dataclass(frozen=True, slots=True)
class PublicCapacityGuardResult:
    protocol_version: str
    classification: str
    variant: str
    planning_uc: int
    exploration_uc: int
    capacity_guard: bool
    input_sha256: str
    physical_initial_sha256: str
    actions: tuple[tuple[str, str | None, str | None, str], ...]
    captured_positions: tuple[tuple[int, int], ...]
    credited_sites: tuple[tuple[int, int], ...]
    step5_planning_charges: tuple[tuple[int, str, int, bool, str | None], ...]
    step5_capacity_deferrals: tuple[tuple[int, int, int, int, bool, object], ...]
    step5_geographic_proposals: int
    step5_applied_action: tuple[str, str | None, str | None, str]
    hazard_active_at_snapshots: tuple[bool, bool]
    snapshot_ids_and_hashes: tuple[tuple[int, str, str], ...]
    snapshot_state_sha256: tuple[str, str]
    final_owner_sha256_before_restore: str
    journal_sha256_before_restore: str
    journal_head_before_restore: str
    restorations_verified: int
    journal_sha256_after_restore: str
    journal_head_after_restore: str
    heldout: bool = False
    scientific_verdict: None = None

    def to_json(self) -> str:
        payload = asdict(self)
        payload["evidence_sha256"] = sha256_hex(canonical_causal_bytes(payload))
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _owner_states(runtime):
    return {
        owner.owner_id: deepcopy(owner.export_causal_state())
        for owner in runtime.causal_owners
    }


def run_public_capacity_guard(
    *, variant: str, planning_uc: int, exploration_uc: int,
    capacity_guard: bool,
) -> PublicCapacityGuardResult:
    if (
        (variant, planning_uc, exploration_uc) not in CONDITIONS
        or type(planning_uc) is not int
        or type(exploration_uc) is not int
        or type(capacity_guard) is not bool
    ):
        raise ValueError("unregistered public UC capacity guard fixture")
    runtime = build_public_route_runtime(
        layout_variant="junction_open",
        planning_uc=planning_uc, exploration_uc=exploration_uc,
        scenario_events=schedule_for(variant), survey_refresh=True,
        capacity_guard=capacity_guard,
    )
    input_sha = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL,
        "variant": variant, "planning_uc": planning_uc,
        "exploration_uc": exploration_uc, "guard": capacity_guard,
        "steps": STEPS, "snapshots": list(SNAPSHOT_STEPS),
        "scenario": [event.as_dict() for event in schedule_for(variant)],
        "layout": runtime.world._layout.as_dict(),
        "physics": runtime.world.config.as_dict(),
        "config": runtime._stage11_config.version,
        "budget_version": runtime._config.compute_budget.version,
        "equipment_version": runtime.equipment.version,
    }))
    initial_sha = sha256_hex(canonical_causal_bytes(
        runtime.world.capture_local(t_monde=1).as_dict()
    ))
    manager = runtime.stage3.substrate.snapshots
    actions, records, states, truths = [], [], {}, []
    for step in range(1, STEPS + 1):
        result = runtime.run_step()
        actions.append((
            result.execution_status, result.command_primitive,
            result.option_ref, result.source,
        ))
        if step in SNAPSHOT_STEPS:
            states[step] = _owner_states(runtime)
            record = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id=runtime.individual_id,
                t_monde=step, cycle=0, attempt_ref=None,
                owners=runtime.causal_owners,
                versions={"stage11": runtime._stage11_config.version},
            )
            if not manager.verify(record.id):
                raise AssertionError("invalid capacity-guard snapshot")
            records.append((step, record.id, record.sha256))
            truth = runtime.world.export_causal_state()["danger_zones"]
            expected = (
                [{"x": 3, "y": 2}]
                if variant == "hidden_transient" and step == 4 else []
            )
            if truth != expected:
                raise AssertionError("unexpected physical danger truth")
            truths.append(bool(truth))
    if not runtime.journal.verify():
        raise AssertionError("broken capacity-guard journal")
    entries = tuple(entry.causal_event for entry in runtime.journal.entries)
    captures = _positions(runtime)
    visits = tuple(sorted(tuple(row[:2]) for row in
        runtime.exploration.geographic.export_causal_state()["visits"]))
    if len(captures) != STEPS or set(captures) != set(visits):
        raise AssertionError("unobserved geographic visit credited")
    actual_inputs = tuple(
        (e["t_monde"], e["sequence"], e["operation"],
         e["payload"]["active"])
        for e in entries if e.get("kind") == "external_input_received"
    )
    expected_inputs = (
        (3, 0, "set_danger_zone", variant == "hidden_transient"),
        (5, 0, "set_danger_zone", False),
    )
    applied = tuple((e["t_monde"], e["sequence"])
                    for e in entries if e.get("kind") == "external_input_applied")
    if actual_inputs != expected_inputs or applied != ((3, 0), (5, 0)):
        raise AssertionError("unlogged or reordered external physical changes")

    planning = tuple(
        (e["cycle"], d["operation"], d["requested_uc"],
         d["accepted"], d["reason"])
        for e in entries if e.get("kind") == "compute_charge"
        and e.get("t_monde") == 5
        for d in (e["data"],) if d["module"] == "planning"
    )
    deferred = tuple(
        (e["cycle"], d["required_uc"], d["available_uc"],
         d["charged_uc"], d["canonical_admissibility_consulted"],
         d["safety_decision"])
        for e in entries if e.get("kind") == "stage11_geographic_capacity_deferred"
        and e.get("t_monde") == 5 for d in (e["data"],)
    )
    options = sum(
        e.get("kind") == "stage11_geographic_option_proposed"
        and e.get("t_monde") == 5 for e in entries
    )
    before = runtime.journal.canonical_bytes()
    previous_hash = runtime.journal.head_hash
    owner_end = _owner_states(runtime)
    if (not capacity_guard and (planning_uc, exploration_uc) == (4, 4)
        and sha256_hex(before) != LEGACY_JOURNAL_SHA256_4UC[variant]):
        raise AssertionError("legacy 4/4 journal diverged from preregistered results")
    for step, snapshot_id, _ in records:
        manager.restore(snapshot_id, owners=runtime.causal_owners)
        if _owner_states(runtime) != states[step]:
            raise AssertionError("incomplete capacity-guard snapshot restoration")
        if not manager.verify(snapshot_id):
            raise AssertionError("snapshot changed during restore")
    if not runtime.journal.verify():
        raise AssertionError("invalid chain after two restorations")

    return PublicCapacityGuardResult(
        protocol_version=PROTOCOL,
        classification="public_development_only_not_heldout",
        variant=variant, planning_uc=planning_uc,
        exploration_uc=exploration_uc, capacity_guard=capacity_guard,
        input_sha256=input_sha, physical_initial_sha256=initial_sha,
        actions=tuple(actions), captured_positions=captures,
        credited_sites=visits, step5_planning_charges=planning,
        step5_capacity_deferrals=deferred,
        step5_geographic_proposals=options,
        step5_applied_action=actions[4],
        hazard_active_at_snapshots=tuple(truths),
        snapshot_ids_and_hashes=tuple(records),
        snapshot_state_sha256=tuple(
            sha256_hex(canonical_causal_bytes(states[step]))
            for step in SNAPSHOT_STEPS
        ),
        final_owner_sha256_before_restore=sha256_hex(
            canonical_causal_bytes(owner_end)
        ),
        journal_sha256_before_restore=sha256_hex(before),
        journal_head_before_restore=previous_hash,
        restorations_verified=len(records),
        journal_sha256_after_restore=sha256_hex(
            runtime.journal.canonical_bytes()
        ),
        journal_head_after_restore=runtime.journal.head_hash,
    )


if __name__ == "__main__":
    for case in CONDITIONS:
        for guarded in (False, True):
            print("stage11_public_capacity_guard=" +
                  run_public_capacity_guard(
                      variant=case[0], planning_uc=case[1],
                      exploration_uc=case[2], capacity_guard=guarded,
                  ).to_json())
