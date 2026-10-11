"""Journaled public world-change controls for Stage-11 observed routes.

No hidden world state is read by Exploration/Planning. Scenario truth is
Lab-only evidence; the individual's input is physical local Perception.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .injected_scenario import ScenarioEvent
from .stage11_geographic_probe import _positions
from .stage11_routed_junction_probe import build_public_route_runtime

PROTOCOL = "stage11-public-stale-route-safety-dev-v1"
VARIANTS = (
    "unchanged_control", "creature_blocks_return",
    "creature_removed", "unknown_danger",
)
OBSTRUCTION = (3, 2)


def registered_events(variant: str) -> tuple[ScenarioEvent, ...]:
    if variant not in VARIANTS:
        raise ValueError("unregistered stale-route public fixture")
    place = ScenarioEvent(
        t_monde=3, sequence=0, operation="place_creature",
        payload={"position": {"x": 3, "y": 2}},
    )
    remove = ScenarioEvent(
        t_monde=5, sequence=0, operation="remove_creature",
        payload={"position": {"x": 3, "y": 2}},
    )
    hazard = ScenarioEvent(
        t_monde=3, sequence=0, operation="set_danger_zone",
        payload={"position": {"x": 3, "y": 2}, "active": True},
    )
    return {
        "unchanged_control": (),
        "creature_blocks_return": (place,),
        "creature_removed": (place, remove),
        "unknown_danger": (hazard,),
    }[variant]


@dataclass(frozen=True, slots=True)
class PublicChangedRouteResult:
    protocol_version: str
    classification: str
    variant: str
    steps: int
    input_sha256: str
    initial_local_sha256: str
    initial_safety_status: str
    safety_status_after_step_2: str
    observed_positions: tuple[tuple[int, int], ...]
    confirmed_visit_sites: tuple[tuple[int, int], ...]
    actions: tuple[tuple[str, str | None, str | None], ...]
    external_input_steps: tuple[int, ...]
    external_input_operations: tuple[str, ...]
    external_inputs_applied: int
    route_candidates_found: int
    route_proposals: int
    applied_route_steps: int
    applied_route_into_active_creature: int
    returned_to_junction: bool
    observed_alternate_branch: bool
    danger_damage_total: float
    final_integrity: float
    accepted_route_search_uc: int
    accepted_preflight_uc: int
    accepted_build_uc: int
    journal_sha256: str
    journal_head: str
    owner_state_sha256: str
    heldout: bool = False
    scientific_verdict: None = None

    def to_json(self) -> str:
        row = asdict(self)
        row["evidence_sha256"] = sha256_hex(canonical_causal_bytes(row))
        return json.dumps(row, sort_keys=True, separators=(",", ":"))


def run_public_changed_route(
    *, variant: str, steps: int = 10,
) -> PublicChangedRouteResult:
    if variant not in VARIANTS or type(steps) is not int or steps != 10:
        raise ValueError("only prespecified 10-step public variants allowed")
    event_schedule = registered_events(variant)
    owner = build_public_route_runtime(
        scenario_events=event_schedule,
    )
    first_local = owner.world.capture_local(t_monde=1).as_dict()
    initial_safety = owner._canonical_safety.zone_status(x=3, y=2)
    input_sha = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL, "variant": variant,
        "steps": steps, "layout": owner.world._layout.as_dict(),
        "world": owner.world.config.as_dict(),
        "scenario_events": [event.as_dict() for event in event_schedule],
        "cognition_version": owner._stage11_config.version,
        "budget_version": owner._config.compute_budget.version,
        "equipment_version": owner.equipment.version,
    }))
    results = []
    for _ in range(2):
        results.append(owner.run_step())
    safety_at_two = owner._canonical_safety.zone_status(x=3, y=2)
    for _ in range(steps - 2):
        results.append(owner.run_step())
    if not owner.journal.verify():
        raise AssertionError("public changed-route journal invalid")
    observed = _positions(owner)
    visits = tuple(sorted(tuple(row[:2]) for row in
        owner.exploration.geographic.export_causal_state()["visits"]))
    if len(observed) != steps or set(visits) != set(observed):
        raise AssertionError("unobserved geographic visit recorded")
    events = tuple(entry.causal_event for entry in owner.journal.entries)
    received = tuple(
        e for e in events if e.get("kind") == "external_input_received"
    )
    applied = tuple(
        e for e in events if e.get("kind") == "external_input_applied"
    )
    if len(received) != len(event_schedule) or len(applied) != len(event_schedule):
        raise AssertionError("unlogged or missing external scenario input")
    for index, event in enumerate(event_schedule):
        if (received[index]["t_monde"] != event.t_monde
            or received[index]["operation"] != event.operation
            or applied[index]["t_monde"] != event.t_monde):
            raise AssertionError("external event changed or applied out of order")
    physical = tuple(
        e for e in events if e.get("kind") == "world_transition_experienced"
    )
    if len(physical) != steps:
        raise AssertionError("missing actual world transition")
    active_creature = False
    blocked_step_numbers = set()
    for step in range(1, steps + 1):
        for event in received:
            if event["t_monde"] == step:
                if event["operation"] == "place_creature":
                    active_creature = True
                elif event["operation"] == "remove_creature":
                    active_creature = False
        if active_creature:
            blocked_step_numbers.add(step)
    unsafe_route = sum(
        step in blocked_step_numbers
        and result.execution_status == "applied"
        and result.option_ref is not None
        and "frontier_route:" in result.option_ref
        and ":via:3:2:" in result.option_ref
        for step, result in enumerate(results, start=1)
    )
    after_end = (
        observed[observed.index((4, 2)) + 1:]
        if (4, 2) in observed else ()
    )
    def charged(operation):
        return sum(
            e["data"]["requested_uc"] for e in events
            if e.get("kind") == "compute_charge"
            and e["data"].get("module") == "planning"
            and e["data"].get("operation") == operation
            and e["data"].get("accepted") is True
        )
    return PublicChangedRouteResult(
        protocol_version=PROTOCOL, classification="public_development_only",
        variant=variant, steps=steps,
        input_sha256=input_sha,
        initial_local_sha256=sha256_hex(canonical_causal_bytes(first_local)),
        initial_safety_status=initial_safety,
        safety_status_after_step_2=safety_at_two,
        observed_positions=observed, confirmed_visit_sites=visits,
        actions=tuple((
            result.execution_status, result.command_primitive,
            result.option_ref,
        ) for result in results),
        external_input_steps=tuple(e["t_monde"] for e in received),
        external_input_operations=tuple(e["operation"] for e in received),
        external_inputs_applied=len(applied),
        route_candidates_found=sum(
            e.get("kind") == "stage11_route_search"
            and e["data"].get("route_found") is True for e in events
        ),
        route_proposals=sum(
            e.get("kind") == "stage11_geographic_option_proposed"
            and e["data"].get("source")
            == "frozen_prior_observed_frontier_route"
            for e in events
        ),
        applied_route_steps=sum(
            result.execution_status == "applied"
            and "frontier_route:" in (result.option_ref or "")
            for result in results
        ),
        applied_route_into_active_creature=unsafe_route,
        returned_to_junction=(2, 2) in after_end,
        observed_alternate_branch=any(
            loc in {(2, 3), (2, 4)} for loc in after_end
        ),
        danger_damage_total=sum(
            float(e["effects"].get("danger_zone_damage", 0.0))
            for e in physical
        ),
        final_integrity=float(owner.world.body.integrity),
        accepted_route_search_uc=charged("geographic_route_search"),
        accepted_preflight_uc=charged("geographic_admissibility_preflight"),
        accepted_build_uc=charged("planning_build"),
        journal_sha256=sha256_hex(owner.journal.canonical_bytes()),
        journal_head=owner.journal.head_hash,
        owner_state_sha256=sha256_hex(canonical_causal_bytes(
            owner.exploration.export_causal_state()
        )),
    )


if __name__ == "__main__":
    for public_variant in VARIANTS:
        print("stage11_public_changed_route=" + run_public_changed_route(
            variant=public_variant,
        ).to_json())
