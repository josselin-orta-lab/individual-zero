"""Predeclared public Stage-11 longitudinal corridor software diagnostic.

Only the Lab builds ground-truth layouts and scores physical outcomes. The
individual receives the usual Perception, canonical safety, and Action Control
inputs; this module never passes hidden danger-zone locations into cognition.
No held-out seeds, scientific verdicts, or Stage-9 Golden decisions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from i0.modules.action_control import StaticSafetyFacts

from .determinism import canonical_causal_bytes, sha256_hex
from .stage11_degraded_budget_probe import _strict_stage11_config
from .stage11_geographic_probe import START_BODY, _positions
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime
from .world import Position

PROTOCOL = "stage11-public-longitudinal-corridor-dev-v1"
VARIANTS = (
    "corridor_clear",
    "corridor_unknown_danger",
    "corridor_unknown_danger_planning_0",
)
CORRIDOR = frozenset({(2, 2), (3, 2), (4, 2)})
DANGER = Position(3, 2)
WALLS = frozenset(Position(x, y) for x, y in (
    (2, 1), (2, 3), (1, 2), (3, 1),
    (3, 3), (4, 1), (4, 3), (5, 2),
))


@dataclass(frozen=True, slots=True)
class PublicLongitudinalCorridor:
    protocol_version: str
    classification: str
    variant: str
    steps: int
    input_sha256: str
    initially_accessible_local_sha256: str
    initial_canonical_danger_status: str
    final_canonical_danger_status: str
    first_decision: tuple[str, str | None, str | None]
    step_trace: tuple[dict[str, object], ...]
    physical_transitions: tuple[dict[str, object], ...]
    physically_perceived_sites: tuple[tuple[int, int], ...]
    confirmed_visit_sites: tuple[tuple[int, int], ...]
    distinct_physically_perceived_sites: int
    applied_geographic_commands: int
    experienced_danger_damage_events: int
    experienced_danger_damage_total: float
    observed_danger_site_captures: int
    final_integrity: float
    accepted_planning_preflight_uc: int
    accepted_planning_build_uc: int
    rejected_planning_requested_uc: int
    budget_deferred_count: int
    remaining_offered_targets: int
    journal_sha256: str
    journal_head: str
    scientific_verdict: None = None
    heldout: bool = False

    def as_dict(self):
        result = asdict(self)
        result["evidence_sha256"] = sha256_hex(canonical_causal_bytes(result))
        return result

    def to_json(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))


def run_public_longitudinal_corridor(
    *, variant: str, steps: int = 8,
) -> PublicLongitudinalCorridor:
    if variant not in VARIANTS or type(steps) is not int or steps != 8:
        raise ValueError("only three registered public eight-step conditions are allowed")
    reference = build_stage11_reference_runtime(enable_geography=True)
    config = (
        _strict_stage11_config(reference, variant="planning_0")
        if variant == "corridor_unknown_danger_planning_0"
        else reference._stage11_config
    )
    dangerous = variant != "corridor_clear"
    layout = replace(
        reference.world._layout,
        obstacles=WALLS,
        water_sources=frozenset(),
        resources=(),
        creatures=frozenset(),
        danger_zones=frozenset({DANGER}) if dangerous else frozenset(),
        lethal_zones=frozenset(),
        oracle_canary="public-lab-only-not-an-individual-observation",
    )
    world = replace(
        reference.world.config,
        version=reference.world.config.version + "+public-corridor-v1",
        initial_body=START_BODY,
        initial_position=Position(2, 2),
        danger_zone_damage=5.0,
    )
    # The initial source is deliberately *independent* of ground-truth
    # WorldLayout. An unknown hazard must remain unknown to Action Control.
    safety_facts = StaticSafetyFacts()
    runtime = Stage11Runtime(
        world_config=world, layout=layout,
        safety_config=reference.stage3.substrate.safety._config,
        safety_facts=safety_facts,
        protected_integrity_threshold=(
            reference.stage3.control._config.protected_integrity_threshold
        ),
        config=config, equipment=reference.equipment,
    )
    initial_safety = runtime._canonical_safety.zone_status(
        x=DANGER.x, y=DANGER.y,
    )
    # A pure read of the same publicly accessible local observation; unlike
    # ground_truth(), capture_local() excludes hidden danger-zone status.
    local_digest = sha256_hex(canonical_causal_bytes(
        runtime.world.capture_local(t_monde=1).as_dict()
    ))
    input_sha = sha256_hex(canonical_causal_bytes({
        "protocol_version": PROTOCOL,
        "variant": variant,
        "steps": steps,
        "world": world.as_dict(),
        "layout": layout.as_dict(),
        "initial_safety_facts": {
            "lethal": [], "safe": [], "toxic": [], "safe_resources": [],
        },
        "runtime_version": config.version,
        "budget_version": runtime._config.compute_budget.version,
        "planning_envelope_uc": runtime._config.compute_budget.module_envelopes[
            "planning"
        ],
        "equipment_version": reference.equipment.version,
    }))
    outputs = []
    step_integrities = []
    for _ in range(steps):
        outputs.append(runtime.run_step())
        step_integrities.append(float(runtime.world.body.integrity))
    if not runtime.journal.verify():
        raise AssertionError("longitudinal public journal verification failed")

    perceived = _positions(runtime)
    if len(perceived) != steps or not set(perceived) <= CORRIDOR:
        raise AssertionError("unexpected or nonphysical corridor capture")
    visits = tuple(sorted(
        (int(x), int(y))
        for x, y, _ in runtime.exploration.geographic.export_causal_state()["visits"]
    ))
    if set(visits) != set(perceived):
        raise AssertionError("geographic owner credited a non-perceived site")

    events = tuple(entry.causal_event for entry in runtime.journal.entries)
    transitions = tuple({
        "world_step": event["t_monde"],
        "position_after": [
            event["position_after"]["x"], event["position_after"]["y"],
        ],
        "integrity_after": event["body_after"]["integrity"],
        "danger_zone_damage": float(
            event["effects"].get("danger_zone_damage", 0.0)
        ),
    } for event in events
        if event.get("kind") == "world_transition_experienced")
    # Assert the Lab's declared physical hazard truth only *after* obtaining
    # actual experienced world transitions. Never use it as prior knowledge.
    if any(
        transition["danger_zone_damage"] != (
            5.0 if dangerous and tuple(transition["position_after"])
            == (DANGER.x, DANGER.y) else 0.0
        )
        for transition in transitions
    ):
        raise AssertionError("experienced danger effect disagrees with world physics")
    trace = tuple({
        "world_step": i + 1,
        "captured_position": list(perceived[i]),
        "command": result.command_primitive,
        "execution_status": result.execution_status,
        "option_ref": result.option_ref,
        "integrity_after_step": step_integrities[i],
    } for i, result in enumerate(outputs))
    charges = [
        event["data"] for event in events
        if event.get("kind") == "compute_charge"
        and event.get("data", {}).get("module") == "planning"
    ]
    def uc(operation, accepted):
        return sum(
            entry["requested_uc"] for entry in charges
            if entry["operation"] == operation
            and entry["accepted"] is accepted
        )
    applied = sum(
        out.execution_status == "applied"
        and out.option_ref is not None
        and out.option_ref.startswith("option:geographic:")
        for out in outputs
    )
    return PublicLongitudinalCorridor(
        protocol_version=PROTOCOL,
        classification="development_only_not_heldout",
        variant=variant, steps=steps, input_sha256=input_sha,
        initially_accessible_local_sha256=local_digest,
        initial_canonical_danger_status=initial_safety,
        final_canonical_danger_status=runtime._canonical_safety.zone_status(
            x=DANGER.x, y=DANGER.y,
        ),
        first_decision=(
            outputs[0].execution_status,
            outputs[0].command_primitive, outputs[0].option_ref,
        ),
        step_trace=trace, physical_transitions=transitions,
        physically_perceived_sites=perceived,
        confirmed_visit_sites=visits,
        distinct_physically_perceived_sites=len(set(perceived)),
        applied_geographic_commands=applied,
        experienced_danger_damage_events=sum(
            row["danger_zone_damage"] > 0 for row in transitions
        ),
        experienced_danger_damage_total=sum(
            row["danger_zone_damage"] for row in transitions
        ),
        observed_danger_site_captures=sum(
            point == (DANGER.x, DANGER.y) for point in perceived
        ),
        final_integrity=float(runtime.world.body.integrity),
        accepted_planning_preflight_uc=uc(
            "geographic_admissibility_preflight", True,
        ),
        accepted_planning_build_uc=uc("planning_build", True),
        rejected_planning_requested_uc=sum(
            entry["requested_uc"] for entry in charges
            if entry["accepted"] is False
        ),
        budget_deferred_count=sum(
            e.get("kind") == "stage11_geographic_budget_deferred"
            for e in events
        ),
        remaining_offered_targets=len(runtime.exploration.geographic.offered),
        journal_sha256=sha256_hex(runtime.journal.canonical_bytes()),
        journal_head=runtime.journal.head_hash,
    )


if __name__ == "__main__":
    for public_variant in VARIANTS:
        print(run_public_longitudinal_corridor(variant=public_variant).to_json())
