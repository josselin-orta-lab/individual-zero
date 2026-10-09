"""Lab-only known-cause P-47 probes and preregistered superstition audit.

EN MVP v1.2.1 §§9.6, 13.2, 19.3-19.5, 20.3 Stage 9, INV-02/03/25.

WorldBody and its physical effects are consulted ONLY here by the bench.
AgencyComparator receives only a command, a frozen predicted consequence,
and the later accessible SymbolicPerception capture. The known ground-truth
labels are never transmitted to a cognitive module.

These fixed compatibility probes are not a scientific campaign, and no
acceptance threshold is invented or inferred from their outcomes.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from typing import Iterable

from i0.contracts import PredictedConsequence
from i0.interfaces import PrimitiveCommand
from i0.modules.agency_comparator import AgencyComparator, AgencyComparatorConfig
from i0.modules.causal_model import CausalModel
from i0.modules.perception import SymbolicPerception

from .stage4_reference_fixture import build_stage4_reference_runtime
from .world import Position, WorldBody, WorldLayout


@dataclass(frozen=True, slots=True)
class KnownCauseProbe:
    identifier: str
    sent_t_monde: int
    command: PrimitiveCommand
    layout: WorldLayout
    prediction: PredictedConsequence
    # Bench-only physical truth. 'none' means no new effect was observed:
    # comparator compatibility MUST NOT be called proof of self-causation.
    known_cause: str
    physical_effect: str

    def validate(self) -> None:
        if (
            not self.identifier or self.sent_t_monde < 1
            or self.known_cause not in {"self", "world", "none"}
            or not self.physical_effect
        ):
            raise ValueError("invalid known-cause benchmark protocol")


@dataclass(frozen=True, slots=True)
class KnownCauseResult:
    identifier: str
    t_monde: int
    known_cause: str
    physical_effect: str
    comparator_status: str
    attribution: str
    outcome_status: str
    # Only a positive external-world attribution counts as a correct link.
    # 'uncertain' is an explicit abstention, not counted as an accurate link.
    correct_link: bool
    uncertain: bool
    false_self_link: bool


@dataclass(frozen=True, slots=True)
class KnownCauseMetrics:
    cases: tuple[KnownCauseResult, ...]
    ground_truthed_cases: int
    correct_links: int
    uncertain_cases: int
    false_self_links: int
    accuracy: float | None


def _protocol() -> tuple[KnownCauseProbe, ...]:
    home = Position(2, 2)
    east = Position(3, 2)
    creature = Position(2, 3)
    return (
        KnownCauseProbe(
            "drink-at-water", 1, PrimitiveCommand("boire"),
            WorldLayout(water_sources=frozenset({home})),
            PredictedConsequence("water", 60.0, 0.0),
            "self", "drank",
        ),
        KnownCauseProbe(
            "open-east-move", 1,
            PrimitiveCommand("se_deplacer", {"direction": "east"}),
            WorldLayout(), PredictedConsequence("position_x", 3.0, 0.0),
            "self", "movement:moved",
        ),
        KnownCauseProbe(
            "visible-obstacle", 1,
            PrimitiveCommand("se_deplacer", {"direction": "east"}),
            WorldLayout(obstacles=frozenset({east})),
            PredictedConsequence("position_x", 3.0, 0.0),
            "world", "movement:blocked",
        ),
        KnownCauseProbe(
            "creature-day-control", 1, PrimitiveCommand("attendre"),
            WorldLayout(creatures=frozenset({creature})),
            PredictedConsequence("integrity", 100.0, 0.0),
            "none", "no_creature_damage",
        ),
        KnownCauseProbe(
            "creature-night-harm", 201, PrimitiveCommand("attendre"),
            WorldLayout(creatures=frozenset({creature})),
            PredictedConsequence("integrity", 100.0, 0.0),
            "world", "creature_damage",
        ),
        KnownCauseProbe(
            "two-visible-creatures-night", 201, PrimitiveCommand("attendre"),
            WorldLayout(creatures=frozenset({creature, Position(3, 2)})),
            PredictedConsequence("integrity", 100.0, 0.0),
            "world", "creature_damage",
        ),
        KnownCauseProbe(
            "hidden-danger-harm", 201, PrimitiveCommand("attendre"),
            WorldLayout(danger_zones=frozenset({home})),
            PredictedConsequence("integrity", 100.0, 0.0),
            "world", "danger_zone_damage",
        ),
    )


def _validate_physical_effect(*, effect: str, actual: dict[str, object]) -> None:
    if effect == "drank":
        grounded = actual.get("drank") is True
    elif effect == "no_creature_damage":
        grounded = "creature_damage" not in actual
    elif effect in {"creature_damage", "danger_zone_damage"}:
        grounded = isinstance(actual.get(effect), (int, float)) and actual[effect] > 0
    elif effect.startswith("movement:"):
        grounded = actual.get("movement") == effect.split(":", 1)[1]
    else:
        raise ValueError("unrecognized benchmark physical effect")
    if not grounded:
        raise AssertionError(f"benchmark truth does not match physical effect: {effect}")


def run_known_cause_probes() -> KnownCauseMetrics:
    """Fixed contrastive physical worlds; reference parameters, not calibration."""
    source = build_stage4_reference_runtime().world.config
    world_config = replace(
        source, version="stage9-lab-known-causes-physical-v1",
        creature_damage=12.0,  # explicitly fixed before any probe executes
    )
    config = AgencyComparatorConfig(
        version="p47-stage9-lab-known-causes-v1",
        tolerances={
            name: 0.0 for name in (
                "position_x", "position_y", "energy", "food", "water",
                "integrity",
            )
        },
        max_observation_window_steps=1,
    )
    output = []
    for probe in _protocol():
        probe.validate()
        world = WorldBody(config=world_config, layout=probe.layout)
        perception = SymbolicPerception()
        transition = world.apply(probe.command, t_monde=probe.sent_t_monde)
        _validate_physical_effect(
            effect=probe.physical_effect, actual=dict(transition.effects),
        )
        if transition.lethal:
            raise AssertionError("known-cause benchmark cannot count lethal paths")
        capture = perception.capture(
            local_state=world.capture_local(
                t_monde=probe.sent_t_monde + 1,
            ).as_dict(),
            telemetry=world.telemetry(),
        )
        result = AgencyComparator(config).compare(
            option_ref=f"option:benchmark:{probe.identifier}",
            sent_t_monde=probe.sent_t_monde,
            deadline_t_monde=probe.sent_t_monde + 1,
            predictions=(probe.prediction,),
            capture=capture,
            command=probe.command,
        )
        if result is None or len(result.effects) != 1:
            raise AssertionError("known-cause P-47 comparison unexpectedly missing")
        correct = (
            (probe.known_cause == "self" and result.attribution == "self_compatible")
            or (probe.known_cause == "world" and result.attribution == "world_justified")
        )
        output.append(KnownCauseResult(
            identifier=probe.identifier,
            t_monde=probe.sent_t_monde,
            known_cause=probe.known_cause,
            physical_effect=probe.physical_effect,
            comparator_status=result.status,
            attribution=result.attribution,
            outcome_status=str(result.effects[0].get("status")),
            correct_link=correct,
            uncertain=result.attribution == "uncertain",
            false_self_link=(
                probe.known_cause == "world"
                and result.attribution == "self_compatible"
            ),
        ))
    eligible = sum(row.known_cause != "none" for row in output)
    correct = sum(row.correct_link for row in output)
    return KnownCauseMetrics(
        cases=tuple(output),
        ground_truthed_cases=eligible,
        correct_links=correct,
        uncertain_cases=sum(row.uncertain for row in output),
        false_self_links=sum(row.false_self_link for row in output),
        accuracy=None if eligible == 0 else correct / eligible,
    )


@dataclass(frozen=True, slots=True)
class SuperstitiousRuleAudit:
    """External known-false canaries only; not an individual-owned fact."""
    audited_false_refs: tuple[str, ...]
    established_false_refs: tuple[str, ...]
    observed_rate: float | None
    preregistered_max_rate: float | None
    passes: bool | None


def audit_superstitious_rules(
    *,
    causal_model: CausalModel,
    # Only cases actually exposed and verified by an external preregistered
    # known-cause benchmark are eligible; missing exposure is not evidence.
    eligible_known_false_refs: Iterable[str],
    preregistered_max_rate: float | None,
) -> SuperstitiousRuleAudit:
    """Measure false established rules, never choose a success cutoff post hoc."""
    if preregistered_max_rate is not None and (
        isinstance(preregistered_max_rate, bool)
        or not isinstance(preregistered_max_rate, (int, float))
        or not isfinite(preregistered_max_rate)
        or not 0 <= preregistered_max_rate <= 1
    ):
        raise ValueError("scientific threshold must be a finite preregistered rate")
    eligible = tuple(sorted(set(eligible_known_false_refs)))
    if any(not isinstance(ref, str) or not ref for ref in eligible):
        raise ValueError("known-false reference must be a nonempty string")
    established = {
        row.ref for row in causal_model.contingencies(status="etablie")
    }
    false_rules = tuple(ref for ref in eligible if ref in established)
    rate = None if not eligible else len(false_rules) / len(eligible)
    passed = (
        None
        if rate is None or preregistered_max_rate is None
        else rate <= preregistered_max_rate
    )
    return SuperstitiousRuleAudit(
        audited_false_refs=eligible,
        established_false_refs=false_rules,
        observed_rate=rate,
        preregistered_max_rate=preregistered_max_rate,
        passes=passed,
    )
