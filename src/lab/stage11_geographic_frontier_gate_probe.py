"""Stage-11 v4: public demand-driven geographic preflight ablation.

Lab owns the fixed public map variants. Individual state observes the world
only through canonical Perception and Action Control. No held-out or science.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from i0.modules.action_control import StaticSafetyFacts

from .determinism import canonical_causal_bytes, sha256_hex
from .stage11_geographic_robustness_probe import (
    VARIANTS as ORIGINAL_VARIANTS, _public_variant_inputs,
)
from .stage11_geographic_uc_probe import UCCondition, _run_condition
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_geographic_probe import START_BODY
from .world import Position

PROTOCOL = "stage11-public-geographic-demand-preflight-dev-v1"
EXTRA_VARIANTS = ("all_adjacent_obstacles", "sole_north_known_lethal")
VARIANTS = (*ORIGINAL_VARIANTS, *EXTRA_VARIANTS)


@dataclass(frozen=True, slots=True)
class DemandPreflightComparison:
    protocol_version: str
    classification: str
    variant: str
    steps: int
    common_physics_sha256: str
    without_preflight: UCCondition
    eager_preflight: UCCondition
    demand_preflight: UCCondition
    eager_empty_frontier_skips: int
    demand_empty_frontier_skips: int
    demand_minus_eager_total_accepted_uc: int
    demand_minus_eager_planning_uc: int
    scientific_verdict: None = None
    heldout: bool = False

    def as_dict(self):
        value = asdict(self)
        value["evidence_sha256"] = sha256_hex(canonical_causal_bytes(value))
        return value

    def to_json(self):
        return json.dumps(
            self.as_dict(), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        )


def _extra_public_inputs(ref, variant):
    """Construction of two new *declared* public Lab-only worlds."""
    world = replace(ref.world.config, initial_body=START_BODY)
    positions = {
        "north": Position(2, 1),
        "east": Position(3, 2),
        "south": Position(2, 3),
        "west": Position(1, 2),
    }
    if variant == "all_adjacent_obstacles":
        layout = replace(
            ref.world._layout,
            obstacles=frozenset(positions.values()),
        )
        return world, layout, ref._canonical_safety._innate
    if variant == "sole_north_known_lethal":
        layout = replace(
            ref.world._layout,
            obstacles=frozenset(
                positions[k] for k in ("east", "south", "west")
            ),
            lethal_zones=frozenset({positions["north"]}),
        )
        safety = StaticSafetyFacts(
            known_lethal_positions=frozenset({(2, 1)}),
        )
        return world, layout, safety
    raise ValueError("undeclared public map")


def run_public_demand_preflight(
    *, variant: str = "all_adjacent_obstacles", steps: int = 6,
) -> DemandPreflightComparison:
    if variant not in VARIANTS or type(steps) is not int or steps != 6:
        raise ValueError("only six prespecified public six-step worlds allowed")
    ref = build_stage11_reference_runtime(enable_geography=True)
    if variant in ORIGINAL_VARIANTS:
        world, layout, safety_facts = _public_variant_inputs(ref, variant)
    else:
        world, layout, safety_facts = _extra_public_inputs(ref, variant)
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
    base = ref._stage11_config
    geographical = replace(
        base.geographic,
        version="p48-geographic-multifrontier-public-dev-v1",
        max_targets_per_cycle=4,
    )
    configurations = (
        replace(
            base, version=base.version + "+geo-compat-no-preflight-v4",
            geographic=geographical, geographic_preflight=False,
            geographic_preflight_requires_frontier=False,
        ),
        replace(
            base, version=base.version + "+geo-eager-preflight-v3-compat",
            geographic=geographical, geographic_preflight=True,
            geographic_preflight_requires_frontier=False,
        ),
        replace(
            base, version=base.version + "+geo-demand-preflight-v4",
            geographic=geographical, geographic_preflight=True,
            geographic_preflight_requires_frontier=True,
        ),
    )
    physics_sha = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL, "variant": variant, "steps": steps,
        "world": world.as_dict(), "layout": layout.as_dict(),
        "equipment_version": ref.equipment.version,
        "safety_facts": {
            "lethal": sorted(safety_facts.known_lethal_positions),
            "safe": sorted(safety_facts.known_safe_positions),
        },
        "geography": asdict(geographical),
        "conditions": [
            {
                "config_version": c.version,
                "preflight": c.geographic_preflight,
                "requires_frontier": c.geographic_preflight_requires_frontier,
            }
            for c in configurations
        ],
    }))
    runs = [
        _run_condition(
            ref=ref, shared=shared, config=config, condition=name,
            steps=steps, report_skip_events=True,
        )
        for config, name in zip(
            configurations,
            ("no_prefilter_compatible", "eager_v3_compatible", "demand_v4"),
        )
    ]
    (off, off_skips), (eager, eager_skips), (demand, demand_skips) = runs
    if off_skips or eager_skips:
        raise AssertionError("previous v3 conditions cannot declare v4 skip")
    return DemandPreflightComparison(
        protocol_version=PROTOCOL,
        classification="development_only_not_heldout",
        variant=variant, steps=steps, common_physics_sha256=physics_sha,
        without_preflight=off,
        eager_preflight=eager,
        demand_preflight=demand,
        eager_empty_frontier_skips=eager_skips,
        demand_empty_frontier_skips=demand_skips,
        demand_minus_eager_total_accepted_uc=(
            demand.accepted_uc_total - eager.accepted_uc_total
        ),
        demand_minus_eager_planning_uc=(
            demand.accepted_planning_uc - eager.accepted_planning_uc
        ),
    )


if __name__ == "__main__":
    for candidate in VARIANTS:
        print("stage11_public_demand_preflight=" + run_public_demand_preflight(
            variant=candidate,
        ).to_json())
