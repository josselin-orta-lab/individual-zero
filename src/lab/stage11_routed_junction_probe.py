"""Public Stage-11 observed-junction routing and Planning-UC software diagnostic.

This is a deterministic development probe, not a held-out experiment or a
scientific acceptance. World truth is used only by Lab to instantiate/score
the public fixture; Exploration receives physical Perception captures only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .injected_scenario import ScenarioEvent
from .stage11_geographic_probe import START_BODY, _positions
from .stage11_junction_probe import (
    ALLOWED_OPEN, ALLOWED_SEALED, BASE, run_public_junction,
)
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime
from .world import Position


PROTOCOL = "stage11-public-observed-route-integration-dev-v1"
CONDITIONS = (
    ("junction_open", None),
    ("junction_sealed", None),
    ("junction_open", 0),
    ("junction_open", 1),
    ("junction_open", 2),
    ("junction_open", 3),
    ("junction_open", 4),
)


@dataclass(frozen=True, slots=True)
class PublicRoutedJunctionResult:
    protocol_version: str
    classification: str
    layout_variant: str
    planning_uc: int | None
    steps: int
    input_sha256: str
    initial_local_sha256: str
    observed_positions: tuple[tuple[int, int], ...]
    confirmed_visit_sites: tuple[tuple[int, int], ...]
    actions: tuple[tuple[str, str | None, str | None], ...]
    route_searches: int
    searches_with_candidate: int
    accepted_route_search_uc: int
    rejected_route_search_uc: int
    accepted_safety_preflight_uc: int
    accepted_planning_build_uc: int
    route_proposals: int
    applied_route_steps: int
    passed_the_dead_end: bool
    returned_to_junction: bool
    observed_alternate_branch: bool
    safety_prefiltered_transits: int
    offered_transits_remaining: int
    journal_sha256: str
    journal_head: str
    owner_state_sha256: str
    heldout: bool = False
    scientific_verdict: None = None

    def to_dict(self):
        result = asdict(self)
        result["evidence_sha256"] = sha256_hex(canonical_causal_bytes(result))
        return result

    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def build_public_route_runtime(
    *, layout_variant: str = "junction_open",
    planning_uc: int | None = None,
    scenario_events: tuple[ScenarioEvent, ...] = (),
    survey_refresh: bool = False,
    exploration_uc: int | None = None,
) -> Stage11Runtime:
    if layout_variant not in ("junction_open", "junction_sealed"):
        raise ValueError("unregistered public junction layout")
    if type(survey_refresh) is not bool:
        raise ValueError("survey-refresh opt-in must be boolean")
    if exploration_uc is not None and (
        type(exploration_uc) is not int or exploration_uc not in (0, 4)
    ):
        raise ValueError("public Exploration envelope must be None, 0 or 4")
    if (not isinstance(scenario_events, tuple)
        or any(not isinstance(event, ScenarioEvent) for event in scenario_events)):
        raise ValueError("route fixture needs a tuple of logged scenario events")
    if planning_uc is not None and (
        type(planning_uc) is not int or planning_uc not in range(5)
    ):
        raise ValueError("Planning-UC fixture must be None or 0..4")
    reference = build_stage11_reference_runtime(enable_geography=True)
    cfg = replace(
        reference._stage11_config,
        version=(
            "stage11-observed-route-integration-dev-v1+survey-refresh-v1"
            if survey_refresh else "stage11-observed-route-integration-dev-v1"
        ),
        geographic_route_enabled=True,
        geographic=replace(
            reference._stage11_config.geographic,
            version=(
                "p48-observed-route-integrated-v1+survey-refresh-v1"
                if survey_refresh else "p48-observed-route-integrated-v1"
            ),
            observe_routes=True,
            refresh_surveys=survey_refresh,
        ),
    )
    if exploration_uc is not None:
        cfg = replace(
            cfg,
            version=cfg.version + f"+exploration-envelope-{exploration_uc}",
            exploration_envelope_uc=exploration_uc,
        )
    if planning_uc is not None:
        stage9 = cfg.stage9
        stage8 = stage9.stage8
        stage7 = stage8.stage7
        stage6 = stage7.stage6
        stage4 = stage6.stage4
        budget = replace(
            stage4.compute_budget,
            version=stage4.compute_budget.version + f"+route-planning-{planning_uc}",
            module_envelopes={
                **stage4.compute_budget.module_envelopes,
                "planning": planning_uc,
            },
        )
        stage4 = replace(stage4, compute_budget=budget)
        stage6 = replace(stage6, stage4=stage4)
        stage7 = replace(stage7, stage6=stage6)
        stage8 = replace(stage8, stage7=stage7)
        cfg = replace(cfg, stage9=replace(stage9, stage8=stage8))
    return Stage11Runtime(
        world_config=replace(
            reference.world.config,
            initial_body=START_BODY, initial_position=Position(2, 2),
        ),
        layout=replace(
            reference.world._layout,
            obstacles=BASE | (
                frozenset({Position(2, 3)})
                if layout_variant == "junction_sealed" else frozenset()
            ),
            resources=(), water_sources=frozenset(), creatures=frozenset(),
            danger_zones=frozenset(), lethal_zones=frozenset(),
            oracle_canary="public-lab-only-route-scorer",
        ),
        safety_config=reference.stage3.substrate.safety._config,
        safety_facts=reference._canonical_safety._innate,
        protected_integrity_threshold=(
            reference.stage3.control._config.protected_integrity_threshold
        ),
        config=cfg, equipment=reference.equipment,
        scenario_id=(
            "stage11-observed-route-world-change"
            if scenario_events else None
        ),
        scenario_version=("public-v1" if scenario_events else None),
        scenario_events=scenario_events,
    )


def run_public_routed_junction(
    *, layout_variant: str = "junction_open",
    planning_uc: int | None = None, steps: int = 10,
) -> PublicRoutedJunctionResult:
    if type(steps) is not int or steps != 10:
        raise ValueError("public registered route experiment uses ten steps")
    runner = build_public_route_runtime(
        layout_variant=layout_variant, planning_uc=planning_uc,
    )
    initial_capture = runner.world.capture_local(t_monde=1).as_dict()
    input_hash = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL, "variant": layout_variant,
        "planning_uc": planning_uc, "steps": steps,
        "layout": runner.world._layout.as_dict(),
        "world": runner.world.config.as_dict(),
        "runtime_version": runner._stage11_config.version,
        "geographic_config_version": runner.exploration.geographic.config.version,
        "budget_version": runner._config.compute_budget.version,
        "equipment_version": runner.equipment.version,
    }))
    results = tuple(runner.run_step() for _ in range(steps))
    if not runner.journal.verify():
        raise AssertionError("broken physical/cognitive journal chain")
    positions = _positions(runner)
    allowed = ALLOWED_OPEN if layout_variant == "junction_open" else ALLOWED_SEALED
    if len(positions) != steps or not set(positions) <= allowed:
        raise AssertionError("physical corridor capture out of public layout")
    visited = tuple(sorted(tuple(row[:2]) for row in
        runner.exploration.geographic.export_causal_state()["visits"]))
    if set(visited) != set(positions):
        raise AssertionError("Exploration credited site without physical capture")
    after_dead_end = ()
    if (4, 2) in positions:
        after_dead_end = positions[positions.index((4, 2)) + 1:]
    events = tuple(entry.causal_event for entry in runner.journal.entries)
    charges = tuple(
        e["data"] for e in events if e.get("kind") == "compute_charge"
        and e.get("data", {}).get("module") == "planning"
    )

    def total_accepted(operation):
        return sum(
            int(e["requested_uc"]) for e in charges
            if e["operation"] == operation and e["accepted"] is True
        )

    return PublicRoutedJunctionResult(
        protocol_version=PROTOCOL,
        classification="public_development_only_not_heldout",
        layout_variant=layout_variant,
        planning_uc=planning_uc, steps=steps,
        input_sha256=input_hash,
        initial_local_sha256=sha256_hex(canonical_causal_bytes(initial_capture)),
        observed_positions=positions, confirmed_visit_sites=visited,
        actions=tuple((
            o.execution_status, o.command_primitive, o.option_ref,
        ) for o in results),
        route_searches=sum(e.get("kind") == "stage11_route_search" for e in events),
        searches_with_candidate=sum(
            e.get("kind") == "stage11_route_search"
            and e["data"]["route_found"] is True for e in events
        ),
        accepted_route_search_uc=total_accepted("geographic_route_search"),
        rejected_route_search_uc=sum(
            int(e["requested_uc"]) for e in charges
            if e["operation"] == "geographic_route_search"
            and e["accepted"] is False
        ),
        accepted_safety_preflight_uc=total_accepted(
            "geographic_admissibility_preflight"
        ),
        accepted_planning_build_uc=total_accepted("planning_build"),
        route_proposals=sum(
            e.get("kind") == "stage11_geographic_option_proposed"
            and e["data"]["source"] == "frozen_prior_observed_frontier_route"
            for e in events
        ),
        applied_route_steps=sum(
            o.execution_status == "applied"
            and o.option_ref is not None
            and "frontier_route:" in o.option_ref for o in results
        ),
        passed_the_dead_end=(4, 2) in positions,
        returned_to_junction=(2, 2) in after_dead_end,
        observed_alternate_branch=any(
            p in {(2, 3), (2, 4)} for p in after_dead_end
        ),
        safety_prefiltered_transits=sum(
            e.get("kind") == "stage11_route_transit_prefiltered"
            for e in events
        ),
        offered_transits_remaining=len(
            runner.exploration.geographic.transit_offered
        ),
        journal_sha256=sha256_hex(runner.journal.canonical_bytes()),
        journal_head=runner.journal.head_hash,
        owner_state_sha256=sha256_hex(canonical_causal_bytes(
            runner.exploration.export_causal_state()
        )),
    )


if __name__ == "__main__":
    for variant, budget in CONDITIONS:
        print("stage11_public_routed_evidence=" + run_public_routed_junction(
            layout_variant=variant, planning_uc=budget,
        ).to_json())
