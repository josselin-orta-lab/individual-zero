"""Public Stage-11 local threat / body recovery modulation fixture.

Development only. All circumstances are declared in external Lab inputs,
which the individual sees solely via Perception -> S_t. This never directly
edits a module owner or injects a modulation profile/target.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .injected_scenario import ScenarioEvent
from .stage11_reference_fixture import build_stage11_reference_runtime
from .stage11_runtime import Stage11Runtime
from .world import BodyState, Position

PROTOCOL = "stage11-public-local-modulation-dev-v1"
NEUTRAL_BODY = BodyState(energy=50.0, food=60.0, water=60.0, integrity=100.0)


@dataclass(frozen=True, slots=True)
class LocalModulationDevelopmentResult:
    protocol_version: str
    classification: str
    variant: str
    steps: int
    input_sha256: str
    journal_sha256: str
    profile_transitions: tuple[tuple[int, str, str], ...]
    local_threat_alert_steps: tuple[int, ...]
    risk_preempted_st_steps: tuple[int, ...]
    positively_scanned_local_clear_steps: tuple[int, ...]
    body_energy_by_step: tuple[tuple[int, float], ...]
    reflex_steps: tuple[int, ...]
    final_profile: str
    scientific_verdict: None = None
    heldout: bool = False

    def as_dict(self):
        obj = asdict(self)
        obj["evidence_sha256"] = sha256_hex(canonical_causal_bytes(obj))
        return obj

    def to_json(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))


def run_public_local_modulation(
    *, variant: str = "trapped_local_creature",
    steps: int = 8,
) -> LocalModulationDevelopmentResult:
    if type(steps) is not int or not 7 <= steps <= 12:
        raise ValueError("public modulation software window is bounded")
    if variant not in (
        "trapped_local_creature", "trapped_no_local_alert",
        "externally_restored_energy",
    ):
        raise ValueError("only enumerated public modulation variants permitted")
    base = build_stage11_reference_runtime(
        enable_local_threats=variant != "trapped_no_local_alert",
    )
    world = replace(
        base.world.config,
        initial_body=(
            BodyState(energy=20, food=60, water=60, integrity=100)
            if variant == "externally_restored_energy" else NEUTRAL_BODY
        ),
        creature_damage=(
            1.0 if variant != "externally_restored_energy" else 0.0
        ),
    )
    layout = base.world._layout
    events = ()
    if variant in ("trapped_local_creature", "trapped_no_local_alert"):
        layout = replace(
            layout,
            # All four adjacent cells blocked: the normatively prior reflex
            # has no safe escape and cannot short-circuit ordinary S_t.
            obstacles=frozenset({
                Position(2,1), Position(2,3),
                Position(1,2), Position(3,2),
            }),
            creatures=frozenset({Position(3,2)}),
        )
        events = (
            ScenarioEvent(
                t_monde=4, sequence=0, operation="remove_creature",
                payload={"position": {"x": 3, "y": 2}},
            ),
        )
    else:
        events = (
            ScenarioEvent(
                t_monde=5, sequence=0, operation="set_body",
                payload={"energy": 80},
            ),
        )
    input_sha = sha256_hex(canonical_causal_bytes({
        "protocol": PROTOCOL,
        "variant": variant,
        "steps": steps,
        "world": world.as_dict(),
        "layout": layout.as_dict(),
        "events": [event.as_dict() for event in events],
        "module": base._stage11_config.modulation.version,
        "local_threat_alerts": base._stage11_config.local_threat_alerts,
    }))
    runtime = Stage11Runtime(
        world_config=world,
        layout=layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=(
            base.stage3.control._config.protected_integrity_threshold
        ),
        config=base._stage11_config,
        equipment=base.equipment,
        scenario_id="stage11-public-modulation-fixture",
        scenario_version=PROTOCOL,
        scenario_events=events,
    )
    preempted = []
    clear = []
    body = []
    reflex = []
    for step in range(1, steps + 1):
        result = runtime.run_step()
        if result.reflex_triggered:
            reflex.append(step)
        st = runtime.s_t.current
        if st is not None and st.t_monde == step:
            signals = st.fixed.get("modulation_signals", {})
            if signals.get("threat_clear") is True:
                clear.append(step)
            if any(
                entry.preempted
                and entry.decomposition.get("risk", 0.0) * entry.reliability
                >= runtime.modulation.config.threat_enter
                for entry in st.competitive
            ):
                preempted.append(step)
            body.append((step, float(st.fixed["body"]["energy"])))
    if not runtime.journal.verify():
        raise AssertionError("public modulation journal integrity failed")
    transitions = []
    alert_steps = []
    for item in runtime.journal.entries:
        e = item.causal_event
        if e.get("kind") == "stage11_modulation_transition":
            d = e["data"]
            transitions.append((e["t_monde"], d["before"], d["after"]))
        if e.get("kind") == "stage11_local_threat_alert_proposed":
            if e["data"].get("source") != "local_perception":
                raise AssertionError("threat alert must be Perception grounded")
            alert_steps.append(e["t_monde"])
    return LocalModulationDevelopmentResult(
        protocol_version=PROTOCOL,
        classification="development_only_not_heldout",
        variant=variant, steps=steps, input_sha256=input_sha,
        journal_sha256=runtime.journal.head_hash,
        profile_transitions=tuple(transitions),
        local_threat_alert_steps=tuple(alert_steps),
        risk_preempted_st_steps=tuple(preempted),
        positively_scanned_local_clear_steps=tuple(clear),
        body_energy_by_step=tuple(body),
        reflex_steps=tuple(reflex),
        final_profile=runtime.modulation.profile,
    )


if __name__ == "__main__":
    for v in (
        "trapped_local_creature", "trapped_no_local_alert",
        "externally_restored_energy",
    ):
        print(run_public_local_modulation(variant=v).to_json())
