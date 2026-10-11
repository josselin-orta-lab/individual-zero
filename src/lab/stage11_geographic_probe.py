"""Stage-11 public geometric frontier coverage contrast (software-only).

Known reference world, no sealed seed, oracle, injected target or inferred
scientific acceptance. Both copies have identical initial body, physics,
perception and frozen Equipment. Only I0-vNext enables local Exploration.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage9_reference_fixture import build_stage9_reference_runtime
from .stage9_runtime import Stage9Runtime
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime
from .world import BodyState


PROTOCOL = "stage11-public-frontier-coverage-dev-v4"
START_BODY = BodyState(energy=50.0, food=60.0, water=60.0, integrity=100.0)


@dataclass(frozen=True, slots=True)
class PublicGeographicCoverage:
    protocol_version: str
    classification: str
    steps: int
    reference_world: str
    equipment_version: str
    initial_body: dict[str, float]
    stage9_distinct_perceived_sites: int
    stage11_without_geography_distinct_sites: int
    stage11_distinct_perceived_sites: int
    stage11_confirmed_distinct_visits: int
    stage11_visit_count: int
    stage9_applied_geographic_moves: int
    stage11_without_geography_applied_moves: int
    stage11_applied_geographic_moves: int
    stage11_applied_north_moves: int
    stage11_frontier_proposals: int
    stage11_model_unavailable_frontiers: int
    stage11_autonomous_options_evaluated: int
    stage11_witnessed_positions: tuple[tuple[int, int], ...]
    stage9_journal_sha256: str
    stage11_without_geography_journal_sha256: str
    stage11_journal_sha256: str
    scientific_verdict: None = None
    heldout: bool = False

    def as_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["diagnostic_sha256"] = sha256_hex(
            canonical_causal_bytes(result)
        )
        return result

    def to_json(self) -> str:
        return json.dumps(
            self.as_dict(), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        )


def _positions(runtime) -> tuple[tuple[int, int], ...]:
    positions = []
    for entry in runtime.journal.entries:
        event = entry.causal_event
        if event.get("kind") != "perceptual_capture":
            continue
        loc = event.get("data", {}).get("position", {})
        x, y = loc.get("x"), loc.get("y")
        if type(x) is not int or type(y) is not int:
            raise AssertionError("recorded perceptual position missing")
        positions.append((x, y))
    return tuple(positions)


def run_public_geographic_coverage(*, steps: int = 8) -> PublicGeographicCoverage:
    if type(steps) is not int or not 3 <= steps <= 32:
        raise ValueError("only bounded public geographic software runs supported")
    reference = build_stage9_reference_runtime()
    prepared = build_stage11_reference_runtime(enable_geography=True)
    neutral = build_stage11_reference_runtime(enable_geography=False)
    world_config = replace(
        reference.world.config, initial_body=START_BODY,
    )
    shared = dict(
        world_config=world_config,
        layout=reference.world._layout,
        safety_config=reference.stage3.substrate.safety._config,
        safety_facts=reference._canonical_safety._innate,
        protected_integrity_threshold=(
            reference.stage3.control._config.protected_integrity_threshold
        ),
        equipment=reference.equipment,
    )
    old = Stage9Runtime(
        config=reference._stage9_config, **shared,
    )
    new = Stage11Runtime(
        config=prepared._stage11_config, **shared,
    )
    ablation = Stage11Runtime(
        config=neutral._stage11_config, **shared,
    )
    old_results = [old.run_step() for _ in range(steps)]
    ablation_results = [ablation.run_step() for _ in range(steps)]
    new_results = [new.run_step() for _ in range(steps)]
    if (not old.journal.verify() or not new.journal.verify()
        or not ablation.journal.verify()):
        raise AssertionError("geographic contrast journal integrity failed")
    physical = _positions(new)
    baseline = _positions(old)
    neutral_positions = _positions(ablation)
    geo = new.exploration.geographic
    if geo is None or not physical or not baseline or not neutral_positions:
        raise AssertionError("missing published perception or geographic owner")
    geo_snapshot = new.exploration.export_causal_state()["geography"]
    sites = {tuple(row[:2]) for row in geo_snapshot["visits"]}
    if sites != set(physical):
        raise AssertionError(
            "geographic coverage ledger diverges from actual Perception captures"
        )
    events = tuple(item.causal_event for item in new.journal.entries)
    proposals = [
        event["data"] for event in events
        if event.get("kind") == "stage11_geographic_option_proposed"
    ]
    evaluated = [
        event["data"] for event in events
        if event.get("kind") == "stage11_intrinsic_evaluation"
        and event["data"]["option_ref"].startswith("option:geographic:")
        and event["data"]["status"] == "evaluated"
    ]
    geographic_moves = [
        result for result in new_results
        if result.execution_status == "applied"
        and result.command_primitive == "se_deplacer"
        and result.option_ref is not None
        and result.option_ref.startswith("option:geographic:")
    ]
    previous_plan_options = {
        entry["option_ref"] for entry in proposals
    }
    if any(result.option_ref not in previous_plan_options
           for result in geographic_moves):
        raise AssertionError("geographic move lacks a published Planning target")
    return PublicGeographicCoverage(
        protocol_version=PROTOCOL,
        classification="development_only_not_heldout",
        steps=steps,
        reference_world=world_config.version,
        equipment_version=reference.equipment.version,
        initial_body={
            "energy": float(START_BODY.energy),
            "food": float(START_BODY.food),
            "water": float(START_BODY.water),
            "integrity": float(START_BODY.integrity),
        },
        stage9_distinct_perceived_sites=len(set(baseline)),
        stage11_without_geography_distinct_sites=len(set(neutral_positions)),
        stage11_distinct_perceived_sites=len(set(physical)),
        stage11_confirmed_distinct_visits=geo.distinct_sites,
        stage11_visit_count=geo.visit_count,
        stage9_applied_geographic_moves=sum(
            outcome.execution_status == "applied"
            and outcome.option_ref is not None
            and outcome.option_ref.startswith("option:geographic:")
            for outcome in old_results
        ),
        stage11_without_geography_applied_moves=sum(
            outcome.execution_status == "applied"
            and outcome.option_ref is not None
            and outcome.option_ref.startswith("option:geographic:")
            for outcome in ablation_results
        ),
        stage11_applied_geographic_moves=len(geographic_moves),
        stage11_applied_north_moves=sum(
            any(row["option_ref"] == result.option_ref
                and row["direction"] == "north" for row in proposals)
            for result in geographic_moves
        ),
        stage11_frontier_proposals=len(proposals),
        stage11_model_unavailable_frontiers=sum(
            row["simulation_status"] == "unavailable"
            for row in proposals
        ),
        stage11_autonomous_options_evaluated=len(evaluated),
        stage11_witnessed_positions=physical,
        stage9_journal_sha256=old.journal.head_hash,
        stage11_without_geography_journal_sha256=ablation.journal.head_hash,
        stage11_journal_sha256=new.journal.head_hash,
    )


def main() -> None:
    print(run_public_geographic_coverage().to_json())


if __name__ == "__main__":
    main()
