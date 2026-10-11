"""Matched public total-logical-UC ablation: Stage11 geographic preflight.

This is software-only accounting, not an independent scientific experiment.
The Lab has map truth only to construct predeclared worlds and score
post-hoc physical visits. No map oracle enters I0's Exploration or Planning.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage11_geographic_probe import _positions
from .stage11_geographic_robustness_probe import (
    VARIANTS, _public_variant_inputs,
)
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime

PROTOCOL = "stage11-public-geography-total-uc-ablation-dev-v1"


@dataclass(frozen=True, slots=True)
class UCCondition:
    condition: str
    config_version: str
    preflight_enabled: bool
    accepted_uc_total: int
    rejected_requested_uc: int
    rejected_charge_attempts: int
    accepted_uc_by_module: tuple[tuple[str, int], ...]
    accepted_uc_by_planning_operation: tuple[tuple[str, int], ...]
    accepted_planning_uc: int
    accepted_planning_build_uc: int
    accepted_preflight_uc: int
    cognitive_cycles: int
    planning_unavailable: int
    prefiltered_inadmissible: int
    offered_frontiers: int
    applied_geographic_commands: int
    distinct_physically_perceived_sites: int
    known_lethal_visits: int
    creature_occupied_visits: int
    journal_sha256: str


@dataclass(frozen=True, slots=True)
class GeographicUCAblation:
    protocol_version: str
    classification: str
    public_variant: str
    steps: int
    physics_input_sha256: str
    legacy_compatible: UCCondition
    preflight: UCCondition
    accepted_uc_delta_preflight_minus_legacy: int
    requested_rejected_uc_delta_preflight_minus_legacy: int
    scientific_verdict: None = None
    heldout: bool = False

    def as_dict(self):
        record = asdict(self)
        record["evidence_sha256"] = sha256_hex(canonical_causal_bytes(record))
        return record

    def to_json(self):
        return json.dumps(
            self.as_dict(), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        )


def _run_condition(*, ref, shared, config, condition, steps):
    runtime = Stage11Runtime(config=config, **shared)
    results = [runtime.run_step() for _ in range(steps)]
    if not runtime.journal.verify():
        raise AssertionError("unverified journal in public UC ablation")
    events = [row.causal_event for row in runtime.journal.entries]
    charges = [
        row["data"] for row in events
        if row.get("kind") == "compute_charge"
    ]
    if not charges:
        raise AssertionError("UC accounting absent")
    if any(
        type(row.get("requested_uc")) is not int
        or row["requested_uc"] < 0
        or type(row.get("accepted")) is not bool
        or not isinstance(row.get("module"), str)
        or not isinstance(row.get("operation"), str)
        for row in charges
    ):
        raise AssertionError("malformed cost records in software trace")
    module_cost: dict[str, int] = {}
    planning_operations: dict[str, int] = {}
    for charge in charges:
        if not charge["accepted"]:
            continue
        module = charge["module"]
        cost = charge["requested_uc"]
        module_cost[module] = module_cost.get(module, 0) + cost
        if module == "planning":
            operation = charge["operation"]
            planning_operations[operation] = (
                planning_operations.get(operation, 0) + cost
            )
    total = sum(module_cost.values())
    if total != sum(
        row["requested_uc"] for row in charges if row["accepted"]
    ):
        raise AssertionError("mismatched total UC across accounting views")
    preflight_uc = planning_operations.get(
        "geographic_admissibility_preflight", 0,
    )
    if not config.geographic_preflight and preflight_uc:
        raise AssertionError("legacy preflight ablation was not isolated")
    visits = _positions(runtime)
    if not visits:
        raise AssertionError("missing real Perception captures")
    state = runtime.exploration.geographic.export_causal_state()
    if {tuple(row[:2]) for row in state["visits"]} != set(visits):
        raise AssertionError("geographic visits differ from physical captures")
    layout = shared["layout"]
    blocked_lethal = {(v.x, v.y) for v in layout.lethal_zones}
    occupied = {(v.x, v.y) for v in layout.creatures}
    moves = [
        r for r in results
        if r.execution_status == "applied"
        and r.option_ref is not None
        and r.option_ref.startswith("option:geographic:")
    ]
    return UCCondition(
        condition=condition, config_version=config.version,
        preflight_enabled=config.geographic_preflight,
        accepted_uc_total=total,
        rejected_requested_uc=sum(
            row["requested_uc"] for row in charges
            if not row["accepted"]
        ),
        rejected_charge_attempts=sum(
            not row["accepted"] for row in charges
        ),
        accepted_uc_by_module=tuple(sorted(module_cost.items())),
        accepted_uc_by_planning_operation=tuple(sorted(
            planning_operations.items()
        )),
        accepted_planning_uc=module_cost.get("planning", 0),
        accepted_planning_build_uc=planning_operations.get(
            "planning_build", 0,
        ),
        accepted_preflight_uc=preflight_uc,
        cognitive_cycles=sum(r.cycles_used for r in results),
        planning_unavailable=sum(
            row.get("kind") == "stage11_geographic_planning_unavailable"
            for row in events
        ),
        prefiltered_inadmissible=sum(
            row["data"]["count"] for row in events
            if row.get("kind") == "stage11_geographic_admissibility_prefiltered"
        ),
        offered_frontiers=sum(
            row.get("kind") == "stage11_geographic_option_proposed"
            for row in events
        ),
        applied_geographic_commands=len(moves),
        distinct_physically_perceived_sites=len(set(visits)),
        known_lethal_visits=len(set(visits) & blocked_lethal),
        creature_occupied_visits=len(set(visits) & occupied),
        journal_sha256=runtime.journal.head_hash,
    )


def run_public_geographic_total_uc(
    *, variant: str = "known_lethal_north", steps: int = 6,
) -> GeographicUCAblation:
    if variant not in VARIANTS or type(steps) is not int or steps != 6:
        raise ValueError("only predeclared public six-step UC comparisons")
    ref = build_stage11_reference_runtime(enable_geography=True)
    world, layout, safety_facts = _public_variant_inputs(ref, variant)
    shared = dict(
        world_config=world,
        layout=layout,
        safety_config=ref.stage3.substrate.safety._config,
        safety_facts=safety_facts,
        protected_integrity_threshold=(
            ref.stage3.control._config.protected_integrity_threshold
        ),
        equipment=ref.equipment,
    )
    original = ref._stage11_config
    geographical = replace(
        original.geographic,
        version="p48-geographic-multifrontier-public-dev-v1",
        max_targets_per_cycle=4,
    )
    configs = [
        replace(
            original, geographic=geographical,
            geographic_preflight=enabled,
            version=original.version + (
                "+geo-preflight-dev-v1" if enabled
                else "+geo-legacy-no-preflight-dev-v1"
            ),
        )
        for enabled in (False, True)
    ]
    physics_sha = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL, "world": world.as_dict(),
        "layout": layout.as_dict(), "steps": steps, "variant": variant,
        "equipment_version": ref.equipment.version,
        "safety_facts": {
            "lethal": sorted(safety_facts.known_lethal_positions),
            "safe": sorted(safety_facts.known_safe_positions),
        },
        "geographic_config": asdict(geographical),
        "changed_condition": "geographic_preflight",
        "config_versions": [cfg.version for cfg in configs],
    }))
    legacy = _run_condition(
        ref=ref, shared=shared, config=configs[0],
        condition="legacy_compatible_no_preflight", steps=steps,
    )
    preflight = _run_condition(
        ref=ref, shared=shared, config=configs[1],
        condition="canonical_admissibility_preflight", steps=steps,
    )
    return GeographicUCAblation(
        protocol_version=PROTOCOL,
        classification="development_only_not_heldout",
        public_variant=variant, steps=steps,
        physics_input_sha256=physics_sha,
        legacy_compatible=legacy, preflight=preflight,
        accepted_uc_delta_preflight_minus_legacy=(
            preflight.accepted_uc_total - legacy.accepted_uc_total
        ),
        requested_rejected_uc_delta_preflight_minus_legacy=(
            preflight.rejected_requested_uc - legacy.rejected_requested_uc
        ),
    )


if __name__ == "__main__":
    for public_variant in VARIANTS:
        print(run_public_geographic_total_uc(variant=public_variant).to_json())
