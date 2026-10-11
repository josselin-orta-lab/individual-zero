"""Additional public map variants for Stage-11 geographic safety and coverage.

All layout truth is owned by this external Lab fixture. The living individual
receives only local Perception captures and independently authorized innate
safety facts. No WorldBody/map oracle is passed to Exploration.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from i0.modules.action_control import StaticSafetyFacts

from .determinism import canonical_causal_bytes, sha256_hex
from .stage11_geographic_probe import _positions, START_BODY
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime
from .world import Position

PROTOCOL = "stage11-public-frontier-layout-robustness-dev-v3"
VARIANTS = (
    "north_obstacle", "east_corridor", "visible_creature_north",
    "known_lethal_north",
)


@dataclass(frozen=True, slots=True)
class PublicLayoutCoverage:
    protocol_version: str
    classification: str
    variant: str
    steps: int
    input_sha256: str
    ablation_distinct_sites: int
    geographic_distinct_sites: int
    geographic_applied_commands: int
    proposed_frontiers: int
    proposed_directions: tuple[str, ...]
    blocked_frontier_rejections: int
    prefiltered_inadmissible_frontiers: int
    prefilter_event_steps: tuple[int, ...]
    preflight_uc_accepted: int
    preflight_uc_rejected: int
    known_lethal_visits: int
    creature_occupied_visits: int
    actually_observed_sites: tuple[tuple[int, int], ...]
    ablation_journal_sha256: str
    geographic_journal_sha256: str
    scientific_verdict: None = None
    heldout: bool = False

    def to_json(self):
        data = asdict(self)
        data["evidence_sha256"] = sha256_hex(canonical_causal_bytes(data))
        return json.dumps(data, sort_keys=True, separators=(",", ":"))


def run_public_layout_coverage(
    *, variant: str, steps: int = 6,
) -> PublicLayoutCoverage:
    if variant not in VARIANTS or type(steps) is not int or not 4 <= steps <= 12:
        raise ValueError("only registered bounded public layouts are supported")
    ref = build_stage11_reference_runtime(enable_geography=True)
    no_geo = build_stage11_reference_runtime(enable_geography=False)
    layout = ref.world._layout
    safety_facts = ref._canonical_safety._innate
    world = replace(ref.world.config, initial_body=START_BODY)
    if variant == "north_obstacle":
        layout = replace(
            layout, obstacles=frozenset({Position(2, 1)}),
        )
    elif variant == "east_corridor":
        layout = replace(
            layout, obstacles=frozenset(
                {Position(x, y) for x in range(2, 10)
                 for y in (1, 3)} | {Position(1,2)}
            ),
        )
    elif variant == "visible_creature_north":
        layout = replace(
            layout, creatures=frozenset({Position(2, 1)}),
        )
        world = replace(world, creature_damage=1.0)
    else:
        layout = replace(
            layout, lethal_zones=frozenset({Position(2, 1)}),
        )
        safety_facts = StaticSafetyFacts(
            known_lethal_positions=frozenset({(2, 1)}),
        )
    config = replace(
        ref._stage11_config,
        geographic=replace(
            ref._stage11_config.geographic,
            version="p48-geographic-multifrontier-public-dev-v1",
            max_targets_per_cycle=4,
        ),
    )
    shared = dict(
        world_config=world, layout=layout,
        safety_config=ref.stage3.substrate.safety._config,
        safety_facts=safety_facts,
        protected_integrity_threshold=(
            ref.stage3.control._config.protected_integrity_threshold
        ),
        equipment=ref.equipment,
    )
    input_sha = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL,
        "variant": variant, "steps": steps,
        "world": world.as_dict(), "layout": layout.as_dict(),
        "safety_facts": {
            "lethal": sorted(safety_facts.known_lethal_positions),
            "safe": sorted(safety_facts.known_safe_positions),
        },
        "geo_config": asdict(config.geographic),
    }))
    a = Stage11Runtime(config=no_geo._stage11_config, **shared)
    b = Stage11Runtime(config=config, **shared)
    results_a = [a.run_step() for _ in range(steps)]
    results_b = [b.run_step() for _ in range(steps)]
    if not a.journal.verify() or not b.journal.verify():
        raise AssertionError("invalid public layout journal")
    witnessed = _positions(b)
    if not witnessed:
        raise AssertionError("missing public Perception captures")
    snapshot = b.exploration.geographic.export_causal_state()
    if {tuple(v[:2]) for v in snapshot["visits"]} != set(witnessed):
        raise AssertionError("physical site ledger not aligned to Perception")
    records = [entry.causal_event for entry in b.journal.entries]
    proposed = [
        row["data"] for row in records
        if row.get("kind") == "stage11_geographic_option_proposed"
    ]
    rejected = [
        row["data"] for row in records
        if row.get("kind") == "stage11_geographic_planning_unavailable"
    ]
    prefiltered = [
        row for row in records
        if row.get("kind") == "stage11_geographic_admissibility_prefiltered"
    ]
    if any(
        row["data"].get("source") != "action_control.verifier_admissibilite"
        or row["data"].get("admissibility") != "inadmissible"
        or row["data"].get("cached") is not False
        or row["data"].get("global_safety_claim") is not False
        or row["data"].get("count") != len(row["data"].get("excluded", ()))
        or not row["data"].get("excluded")
        for row in prefiltered
    ):
        raise AssertionError("inadmissible frontier optimization without authoritative provenance")
    if len({row["t_monde"] for row in prefiltered}) != len(prefiltered):
        raise AssertionError("multiple prefilter records for one physically captured step")
    preflight_charges = [
        row["data"] for row in records
        if row.get("kind") == "compute_charge"
        and row.get("data", {}).get("module") == "planning"
        and row.get("data", {}).get("operation")
        == "geographic_admissibility_preflight"
    ]
    if any(
        row["requested_uc"] != 1
        or row["count"] != 1
        for row in preflight_charges
    ):
        raise AssertionError("unbudgeted or incorrectly versioned safety preflight")
    if prefiltered and not any(
        row["accepted"] is True for row in preflight_charges
    ):
        raise AssertionError("prefilter claims without accepted Planning UC")
    excluded_lethal = {(p.x, p.y) for p in layout.lethal_zones}
    excluded_creature = {(p.x, p.y) for p in layout.creatures}
    applied = [
        row for row in results_b
        if row.execution_status == "applied"
        and row.option_ref is not None
        and row.option_ref.startswith("option:geographic:")
    ]
    return PublicLayoutCoverage(
        protocol_version=PROTOCOL,
        classification="development_only_not_heldout",
        variant=variant, steps=steps, input_sha256=input_sha,
        ablation_distinct_sites=len(set(_positions(a))),
        geographic_distinct_sites=len(set(witnessed)),
        geographic_applied_commands=len(applied),
        proposed_frontiers=len(proposed),
        proposed_directions=tuple(row["direction"] for row in proposed),
        blocked_frontier_rejections=len(rejected),
        prefiltered_inadmissible_frontiers=sum(
            row["data"]["count"] for row in prefiltered
        ),
        prefilter_event_steps=tuple(
            row["t_monde"] for row in prefiltered
        ),
        preflight_uc_accepted=sum(
            row["requested_uc"] for row in preflight_charges
            if row["accepted"] is True
        ),
        preflight_uc_rejected=sum(
            row["requested_uc"] for row in preflight_charges
            if row["accepted"] is not True
        ),
        known_lethal_visits=len(set(witnessed) & excluded_lethal),
        creature_occupied_visits=len(set(witnessed) & excluded_creature),
        actually_observed_sites=witnessed,
        ablation_journal_sha256=a.journal.head_hash,
        geographic_journal_sha256=b.journal.head_hash,
    )


if __name__ == "__main__":
    for variant_name in VARIANTS:
        print(run_public_layout_coverage(variant=variant_name).to_json())
