"""Public Stage11 geographic visit-cap and observed-transit boundedness probe.

The Lab instantiates a *known public* junction and scores only real
Perception captures. I0 receives no hidden map, injected objective or
reward. This is a software capacity contract, never scientific acceptance.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage11_geographic_probe import _positions
from .stage11_routed_junction_probe import build_public_route_runtime
from .stage11_runtime import Stage11Runtime

PROTOCOL = "stage11-public-routed-capacity-dev-v1"
CAPS = (3, 4)
STEPS = 10


@dataclass(frozen=True, slots=True)
class PublicRoutedCapacityResult:
    protocol_version: str
    classification: str
    site_cap: int
    steps: int
    input_sha256: str
    config_version: str
    geographic_config_version: str
    budget_version: str
    captured_positions: tuple[tuple[int, int], ...]
    distinct_captured_sites: int
    owner_distinct_sites: int
    owner_visit_count: int
    capped_world_steps: tuple[int, ...]
    capacity_stop_world_steps: tuple[int, ...]
    accepted_route_search_uc: int
    accepted_route_search_uc_at_cap: int
    route_search_events_at_cap: int
    applied_transit_steps: tuple[int, ...]
    applied_transit_steps_at_cap: tuple[int, ...]
    applied_geographic_commands: int
    observed_southern_alternative: bool
    journal_sha256: str
    exploration_sha256: str
    heldout: bool = False
    scientific_verdict: None = None

    def as_dict(self):
        payload = asdict(self)
        payload["evidence_sha256"] = sha256_hex(canonical_causal_bytes(payload))
        return payload

    def to_json(self):
        return json.dumps(
            self.as_dict(), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        )


def run_public_routed_capacity(
    *, site_cap: int, steps: int = STEPS,
) -> PublicRoutedCapacityResult:
    if type(site_cap) is not int or site_cap not in CAPS:
        raise ValueError("only registered public geographic caps 3/4")
    if type(steps) is not int or steps != STEPS:
        raise ValueError("public geographic capacity protocol requires ten steps")
    baseline = build_public_route_runtime(
        layout_variant="junction_open", survey_refresh=True,
    )
    cfg = replace(
        baseline._stage11_config,
        version=f"stage11-public-route-capacity-dev-v1-cap{site_cap}",
        geographic=replace(
            baseline._stage11_config.geographic,
            version=f"p48-public-route-capacity-dev-v1-cap{site_cap}",
            max_distinct_sites=site_cap,
        ),
    )
    runtime = Stage11Runtime(
        world_config=baseline.world.config, layout=baseline.world._layout,
        safety_config=baseline.stage3.substrate.safety._config,
        safety_facts=baseline._canonical_safety._innate,
        protected_integrity_threshold=(
            baseline.stage3.control._config.protected_integrity_threshold
        ),
        config=cfg, equipment=baseline.equipment,
    )
    input_sha = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL, "site_cap": site_cap, "steps": steps,
        "config_version": cfg.version,
        "geographic_config_version": cfg.geographic.version,
        "budget_version": runtime._config.compute_budget.version,
        "world": runtime.world.config.as_dict(),
        "layout": runtime.world._layout.as_dict(),
        "equipment_version": runtime.equipment.version,
    }))
    results = tuple(runtime.run_step() for _ in range(steps))
    if not runtime.journal.verify():
        raise AssertionError("invalid capacity-probe journal")
    positions = _positions(runtime)
    if len(positions) != steps:
        raise AssertionError("missing physical Perception capture")
    geo = runtime.exploration.geographic
    state = runtime.exploration.export_causal_state()
    owner_visits = geo.export_causal_state()["visits"]
    if {tuple(v[:2]) for v in owner_visits} != set(positions):
        raise AssertionError("geographic owner differs from physical captures")
    if len(owner_visits) > site_cap:
        raise AssertionError("owner exceeded registered visit capacity")
    capped = tuple(
        step for step in range(1, steps + 1)
        if len(set(positions[:step])) >= site_cap
    )
    events = tuple(row.causal_event for row in runtime.journal.entries)
    route_searches = tuple(
        row for row in events if row.get("kind") == "stage11_route_search"
    )
    route_charges = tuple(
        row for row in events
        if row.get("kind") == "compute_charge"
        and row.get("data", {}).get("module") == "planning"
        and row["data"].get("operation") == "geographic_route_search"
        and row["data"].get("accepted") is True
    )
    stopped = tuple(
        row for row in events
        if row.get("kind") == "stage11_geographic_route_capacity_exhausted"
    )
    if any(
        row.get("cycle") != 1
        or row["data"].get("source") != "pre_phase1_physical_visit_ledger"
        or row["data"].get("distinct_sites") != site_cap
        or row["data"].get("max_distinct_sites") != site_cap
        or row["data"].get("route_search_uc_consumed") != 0
        or row["data"].get("safety_decision") is not None
        or row["data"].get("scientific_verdict") is not None
        for row in stopped
    ):
        raise AssertionError("unsupported capacity-stop provenance")
    if len(stopped) != len(set(row["t_monde"] for row in stopped)):
        raise AssertionError("multiple capacity-stop markers on one world step")
    transits = tuple(
        i for i, outcome in enumerate(results, 1)
        if outcome.execution_status == "applied"
        and "frontier_route:" in (outcome.option_ref or "")
    )
    actual_geo = sum(
        row.execution_status == "applied"
        and row.option_ref is not None
        and row.option_ref.startswith("option:geographic:")
        for row in results
    )
    return PublicRoutedCapacityResult(
        protocol_version=PROTOCOL,
        classification="public_development_only_not_heldout",
        site_cap=site_cap, steps=steps,
        input_sha256=input_sha,
        config_version=cfg.version,
        geographic_config_version=cfg.geographic.version,
        budget_version=runtime._config.compute_budget.version,
        captured_positions=positions,
        distinct_captured_sites=len(set(positions)),
        owner_distinct_sites=geo.distinct_sites,
        owner_visit_count=geo.visit_count,
        capped_world_steps=capped,
        capacity_stop_world_steps=tuple(
            row["t_monde"] for row in stopped
        ),
        accepted_route_search_uc=sum(
            row["data"]["requested_uc"] for row in route_charges
        ),
        accepted_route_search_uc_at_cap=sum(
            row["data"]["requested_uc"] for row in route_charges
            if row["t_monde"] in capped
        ),
        route_search_events_at_cap=sum(
            row["t_monde"] in capped for row in route_searches
        ),
        applied_transit_steps=transits,
        applied_transit_steps_at_cap=tuple(
            step for step in transits if step in capped
        ),
        applied_geographic_commands=actual_geo,
        observed_southern_alternative=any(
            p in ((2, 3), (2, 4)) for p in positions
        ),
        journal_sha256=runtime.journal.head_hash,
        exploration_sha256=sha256_hex(canonical_causal_bytes(state)),
    )


if __name__ == "__main__":
    for capacity in CAPS:
        print("stage11_public_routed_capacity="
              + run_public_routed_capacity(site_cap=capacity).to_json())
