"""Public Stage11 physically observed junction versus sealed dead-end.

No layout truth enters the individual; alternate-branch opportunities are
scored only by Lab after physically captured WorldBody/Perception steps.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage11_geographic_probe import START_BODY, _positions
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime
from .world import Position

PROTOCOL = "stage11-public-observed-junction-dev-v1"
VARIANTS = ("junction_open", "junction_sealed")
BASE = frozenset({
    Position(2, 1), Position(1, 2),
    Position(3, 1), Position(3, 3),
    Position(4, 1), Position(4, 3), Position(5, 2),
    Position(1, 3), Position(1, 4),
    Position(3, 4), Position(2, 5),
})
ALLOWED_OPEN = frozenset({(2, 2), (3, 2), (4, 2), (2, 3), (2, 4)})
ALLOWED_SEALED = frozenset({(2, 2), (3, 2), (4, 2)})


@dataclass(frozen=True, slots=True)
class PublicJunctionTrace:
    protocol_version: str
    classification: str
    variant: str
    steps: int
    input_sha256: str
    initial_local_sha256: str
    east_initially_passable: bool
    south_initially_passable: bool
    observed_positions: tuple[tuple[int, int], ...]
    confirmed_visits: tuple[tuple[int, int], ...]
    actions: tuple[tuple[str, str | None, str | None], ...]
    applied_geographic_commands: int
    dead_end_captured: bool
    return_to_junction_after_dead_end: bool
    alternate_branch_captured_after_dead_end: bool
    last_command_unobserved: bool
    journal_sha256: str
    journal_head: str
    scientific_verdict: None = None
    heldout: bool = False

    def to_json(self):
        obj = asdict(self)
        obj["evidence_sha256"] = sha256_hex(canonical_causal_bytes(obj))
        return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def run_public_junction(*, variant: str, steps: int = 10) -> PublicJunctionTrace:
    if variant not in VARIANTS or type(steps) is not int or steps != 10:
        raise ValueError("only prespecified public junction conditions allowed")
    baseline = build_stage11_reference_runtime(enable_geography=True)
    layout = replace(
        baseline.world._layout,
        obstacles=BASE | (
            frozenset({Position(2, 3)}) if variant == "junction_sealed"
            else frozenset()
        ),
        water_sources=frozenset(), resources=(), creatures=frozenset(),
        danger_zones=frozenset(), lethal_zones=frozenset(),
        oracle_canary="lab-only-junction-check",
    )
    world = replace(
        baseline.world.config, initial_body=START_BODY,
        initial_position=Position(2, 2),
        version=baseline.world.config.version + "+public-junction-v1",
    )
    runner = Stage11Runtime(
        world_config=world, layout=layout,
        safety_config=baseline.stage3.substrate.safety._config,
        safety_facts=baseline._canonical_safety._innate,
        protected_integrity_threshold=(
            baseline.stage3.control._config.protected_integrity_threshold
        ),
        config=baseline._stage11_config,
        equipment=baseline.equipment,
    )
    local = runner.world.capture_local(t_monde=1).as_dict()
    cells = {row["direction"]: row for row in local["adjacent"]}
    input_hash = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL, "variant": variant,
        "layout": layout.as_dict(), "world": world.as_dict(),
        "cognition_version": baseline._stage11_config.version,
        "equipment_version": baseline.equipment.version,
    }))
    outputs = tuple(runner.run_step() for _ in range(steps))
    if not runner.journal.verify():
        raise AssertionError("invalid junction journal")
    positions = _positions(runner)
    allowed = ALLOWED_OPEN if variant == "junction_open" else ALLOWED_SEALED
    if len(positions) != steps or not set(positions) <= allowed:
        raise AssertionError("impossible observed junction location")
    visits = tuple(sorted(tuple(row[:2]) for row in
        runner.exploration.geographic.export_causal_state()["visits"]))
    if set(visits) != set(positions):
        raise AssertionError("credited geographic visit without physical capture")
    first_dead_end = next(
        (i for i, point in enumerate(positions) if point == (4, 2)), None,
    )
    after_dead_end = (
        () if first_dead_end is None else positions[first_dead_end + 1:]
    )
    actions = tuple((
        out.execution_status, out.command_primitive, out.option_ref,
    ) for out in outputs)
    return PublicJunctionTrace(
        protocol_version=PROTOCOL,
        classification="development_only_not_heldout",
        variant=variant, steps=steps,
        input_sha256=input_hash,
        initial_local_sha256=sha256_hex(canonical_causal_bytes(local)),
        east_initially_passable=cells["east"]["passable"] is True,
        south_initially_passable=cells["south"]["passable"] is True,
        observed_positions=positions,
        confirmed_visits=visits,
        actions=actions,
        applied_geographic_commands=sum(
            out.execution_status == "applied"
            and out.option_ref is not None
            and out.option_ref.startswith("option:geographic:")
            for out in outputs
        ),
        dead_end_captured=first_dead_end is not None,
        return_to_junction_after_dead_end=(2, 2) in after_dead_end,
        alternate_branch_captured_after_dead_end=any(
            position in {(2, 3), (2, 4)} for position in after_dead_end
        ),
        last_command_unobserved=(
            bool(outputs[-1].command_primitive == "se_deplacer")
        ),
        journal_sha256=sha256_hex(runner.journal.canonical_bytes()),
        journal_head=runner.journal.head_hash,
    )


if __name__ == "__main__":
    for name in VARIANTS:
        print(run_public_junction(variant=name).to_json())
