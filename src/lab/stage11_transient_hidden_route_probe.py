"""Public Stage-11 routed junction with transient hidden danger and strict UC.

Development-only software fixture. Lab alone scores the true WorldBody hazard;
no hazard schedule, future oracle, reward or artificial safety fact is passed
to Exploration, Planning, Competition or Action Control. Not held-out science.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .injected_scenario import ScenarioEvent
from .snapshots import SnapshotType
from .stage11_geographic_probe import _positions
from .stage11_routed_junction_probe import build_public_route_runtime


PROTOCOL = "stage11-public-transient-hidden-route-uc-snapshots-dev-v1"
VARIANTS = ("control", "hidden_transient")
BUDGETS = ((0, 0), (3, 4), (4, 4), (4, 0))
HAZARD_POSITION = (3, 2)
STEPS = 10
SNAPSHOT_STEPS = (4, 5)


@dataclass(frozen=True, slots=True)
class BoundarySnapshotEvidence:
    step: int
    snapshot_id: str
    snapshot_sha256: str
    owner_state_sha256: str
    scenario_next_index: int
    physical_hazard_active: bool


@dataclass(frozen=True, slots=True)
class PublicTransientRouteResult:
    protocol_version: str
    classification: str
    variant: str
    planning_uc: int
    exploration_uc: int
    steps: int
    input_sha256: str
    initial_local_sha256: str
    initial_safety_status: str
    pre_change_perception_sha256: str
    captures: tuple[tuple[int, int], ...]
    actions: tuple[tuple[str, str | None, str | None, str], ...]
    registered_sites: tuple[tuple[int, int], ...]
    external_inputs_received: tuple[tuple[int, int, str, bool], ...]
    external_inputs_applied: tuple[tuple[int, int], ...]
    snapshot_evidence: tuple[BoundarySnapshotEvidence, ...]
    safety_status_after_step_4: str
    safety_status_after_step_5: str
    applied_route_steps: int
    applied_reflex_steps: int
    accepted_route_search_uc: int
    rejected_route_search_uc: int
    accepted_preflight_uc: int
    accepted_build_uc: int
    accepted_exploration_observe_uc: int
    rejected_exploration_observe_uc: int
    danger_damage_total: float
    final_integrity_before_restore: float
    final_owner_sha256_before_restore: str
    journal_sha256_before_restore: str
    journal_head_before_restore: str
    snapshot_restorations_verified: int
    journal_sha256_after_restore: str
    journal_head_after_restore: str
    heldout: bool = False
    scientific_verdict: None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["evidence_sha256"] = sha256_hex(canonical_causal_bytes(payload))
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def schedule_for(variant: str) -> tuple[ScenarioEvent, ...]:
    if variant not in VARIANTS:
        raise ValueError("unregistered transient-hazard variant")
    position = {"x": HAZARD_POSITION[0], "y": HAZARD_POSITION[1]}
    return (
        ScenarioEvent(
            t_monde=3, sequence=0, operation="set_danger_zone",
            payload={"position": dict(position),
                     "active": variant == "hidden_transient"},
        ),
        ScenarioEvent(
            t_monde=5, sequence=0, operation="set_danger_zone",
            payload={"position": dict(position), "active": False},
        ),
    )


def _owner_states(runtime) -> dict[str, object]:
    return {
        owner.owner_id: deepcopy(owner.export_causal_state())
        for owner in runtime.causal_owners
    }


def _sha(value: object) -> str:
    return sha256_hex(canonical_causal_bytes(value))


def run_public_transient_hidden_route(
    *, variant: str, planning_uc: int, exploration_uc: int,
) -> PublicTransientRouteResult:
    """Execute only the registered public ten-step + two-snapshot schedule.

    Independent calls may be compared byte-for-byte. Restore is used only
    AFTER the full timeline has closed, never to re-run a cancelled step
    within the same journal occurrence namespace.
    """
    if (
        variant not in VARIANTS
        or type(planning_uc) is not int
        or type(exploration_uc) is not int
        or (planning_uc, exploration_uc) not in BUDGETS
    ):
        raise ValueError("unregistered public Stage-11 budget/variant")
    events = schedule_for(variant)
    runtime = build_public_route_runtime(
        layout_variant="junction_open", survey_refresh=True,
        planning_uc=planning_uc, exploration_uc=exploration_uc,
        scenario_events=events,
    )
    initial_local = runtime.world.capture_local(t_monde=1).as_dict()
    initial_safety = runtime._canonical_safety.zone_status(
        x=HAZARD_POSITION[0], y=HAZARD_POSITION[1],
    )
    input_sha = _sha({
        "protocol": PROTOCOL, "variant": variant,
        "planning_uc": planning_uc, "exploration_uc": exploration_uc,
        "steps": STEPS, "snapshot_steps": list(SNAPSHOT_STEPS),
        "scenario_events": [event.as_dict() for event in events],
        "layout": runtime.world._layout.as_dict(),
        "physics": runtime.world.config.as_dict(),
        "runtime_version": runtime._stage11_config.version,
        "geography_version": runtime.exploration.geographic.config.version,
        "budget_version": runtime._config.compute_budget.version,
        "equipment_version": runtime.equipment.version,
    })

    manager = runtime.stage3.substrate.snapshots
    actions = []
    snapshots = []
    saved_owner_states = {}
    safety_at = {}
    for step in range(1, STEPS + 1):
        outcome = runtime.run_step()
        actions.append((
            outcome.execution_status, outcome.command_primitive,
            outcome.option_ref, outcome.source,
        ))
        if step in SNAPSHOT_STEPS:
            before = _owner_states(runtime)
            record = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id=runtime.individual_id,
                t_monde=step, cycle=0, attempt_ref=None,
                owners=runtime.causal_owners,
                versions={"stage11": runtime._stage11_config.version},
            )
            if not manager.verify(record.id):
                raise AssertionError("snapshot verification failure")
            saved_owner_states[step] = before
            truth = runtime.world.export_causal_state()["danger_zones"]
            if truth not in ([], [{"x": HAZARD_POSITION[0],
                                  "y": HAZARD_POSITION[1]}]):
                raise AssertionError("unexpected physical hazard truth")
            snapshots.append(BoundarySnapshotEvidence(
                step=step, snapshot_id=record.id,
                snapshot_sha256=record.sha256,
                owner_state_sha256=_sha(before),
                scenario_next_index=before["scenario"]["next_index"],
                physical_hazard_active=bool(truth),
            ))
            safety_at[step] = runtime._canonical_safety.zone_status(
                x=HAZARD_POSITION[0], y=HAZARD_POSITION[1],
            )

    if not runtime.journal.verify():
        raise AssertionError("transient-hazard technical journal is invalid")
    received_events = tuple(
        e.causal_event for e in runtime.journal.entries
        if e.causal_event.get("kind") == "external_input_received"
    )
    applied_events = tuple(
        e.causal_event for e in runtime.journal.entries
        if e.causal_event.get("kind") == "external_input_applied"
    )
    received = tuple(
        (e["t_monde"], e["sequence"], e["operation"],
         e["payload"]["active"]) for e in received_events
    )
    applied = tuple(
        (e["t_monde"], e["sequence"]) for e in applied_events
    )
    if (received != (
        (3, 0, "set_danger_zone", variant == "hidden_transient"),
        (5, 0, "set_danger_zone", False),
    ) or applied != ((3, 0), (5, 0))):
        raise AssertionError("external input order/provenance diverged")

    entries = tuple(e.causal_event for e in runtime.journal.entries)
    captures = _positions(runtime)
    sites = tuple(sorted(
        tuple(row[:2]) for row in
        runtime.exploration.geographic.export_causal_state()["visits"]
    ))
    if (len(captures) != STEPS or set(captures) != set(sites)):
        raise AssertionError("Exploration credited an unobserved site")
    perceptions = tuple(
        e["data"] for e in entries if e.get("kind") == "perceptual_capture"
    )
    if len(perceptions) != STEPS:
        raise AssertionError("missing actual Perception capture")
    transitions = tuple(
        e for e in entries if e.get("kind") == "world_transition_experienced"
    )
    if len(transitions) != STEPS:
        raise AssertionError("missing actual physical world transition")

    def uc(module: str, operation: str, accepted: bool) -> int:
        return sum(
            int(e["data"]["requested_uc"])
            for e in entries
            if e.get("kind") == "compute_charge"
            and e["data"].get("module") == module
            and e["data"].get("operation") == operation
            and e["data"].get("accepted") is accepted
        )

    owner_end = _owner_states(runtime)
    final_integrity = float(runtime.world.body.integrity)
    journal_before = runtime.journal.canonical_bytes()
    head_before = runtime.journal.head_hash
    # Verify BOTH captured physical histories after all real world steps.
    # No new physics/cognition is run after a restoration.
    for evidence in snapshots:
        restored = manager.restore(
            evidence.snapshot_id, owners=runtime.causal_owners,
        )
        if restored.id != evidence.snapshot_id:
            raise AssertionError("wrong snapshot restored")
        if _owner_states(runtime) != saved_owner_states[evidence.step]:
            raise AssertionError("incomplete owner snapshot restoration")
        if not manager.verify(evidence.snapshot_id):
            raise AssertionError("restored snapshot digest changed")
        actual_danger = bool(
            runtime.world.export_causal_state()["danger_zones"]
        )
        if actual_danger != evidence.physical_hazard_active:
            raise AssertionError("snapshot restored incorrect physical hazard")
    if not runtime.journal.verify():
        raise AssertionError("post-restoration journal chain changed")

    return PublicTransientRouteResult(
        protocol_version=PROTOCOL,
        classification="public_development_only_not_heldout",
        variant=variant, planning_uc=planning_uc,
        exploration_uc=exploration_uc, steps=STEPS,
        input_sha256=input_sha, initial_local_sha256=_sha(initial_local),
        initial_safety_status=initial_safety,
        pre_change_perception_sha256=_sha(perceptions[:2]),
        captures=captures, actions=tuple(actions),
        registered_sites=sites,
        external_inputs_received=received,
        external_inputs_applied=applied,
        snapshot_evidence=tuple(snapshots),
        safety_status_after_step_4=safety_at[4],
        safety_status_after_step_5=safety_at[5],
        applied_route_steps=sum(
            action[0] == "applied"
            and "frontier_route:" in (action[2] or "")
            for action in actions
        ),
        applied_reflex_steps=sum(
            action[0] == "applied" and action[3] == "reflex"
            for action in actions
        ),
        accepted_route_search_uc=uc("planning", "geographic_route_search", True),
        rejected_route_search_uc=uc("planning", "geographic_route_search", False),
        accepted_preflight_uc=uc(
            "planning", "geographic_admissibility_preflight", True,
        ),
        accepted_build_uc=uc("planning", "planning_build", True),
        accepted_exploration_observe_uc=uc(
            "exploration", "exploration_observe", True,
        ),
        rejected_exploration_observe_uc=uc(
            "exploration", "exploration_observe", False,
        ),
        danger_damage_total=sum(
            float(e["effects"].get("danger_zone_damage", 0.0))
            for e in transitions
        ),
        final_integrity_before_restore=final_integrity,
        final_owner_sha256_before_restore=_sha(owner_end),
        journal_sha256_before_restore=sha256_hex(journal_before),
        journal_head_before_restore=head_before,
        snapshot_restorations_verified=len(snapshots),
        journal_sha256_after_restore=sha256_hex(
            runtime.journal.canonical_bytes()
        ),
        journal_head_after_restore=runtime.journal.head_hash,
    )


if __name__ == "__main__":
    for public_budget in BUDGETS:
        for public_variant in VARIANTS:
            print(
                "stage11_public_transient_hidden_route="
                + run_public_transient_hidden_route(
                    variant=public_variant,
                    planning_uc=public_budget[0],
                    exploration_uc=public_budget[1],
                ).to_json()
            )
