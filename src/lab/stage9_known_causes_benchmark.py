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

from .journal import HashChainedJournal
from .stage4_reference_fixture import build_stage4_reference_runtime
from .world import Position, WorldBody, WorldLayout, WorldPhysicsConfig


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
    """Lab-only diagnostic, not the Stage-9 scientific acceptance gate."""
    audited_false_refs: tuple[str, ...]
    established_false_refs: tuple[str, ...]
    observed_rate: float | None
    preregistered_max_rate: float | None
    passes: bool | None
    # Do not count unexposed, unverified or invented false canaries as zeroes.
    unverified_false_refs: tuple[str, ...] = ()
    physical_witness_refs: tuple[str, ...] = ()


def _verified_null_drink_witnesses(
    *,
    journal: HashChainedJournal | None,
    world_config: WorldPhysicsConfig | None,
) -> tuple[str, ...]:
    """Ground the one supported null-cause canary in a closed world step.

    The laboratory alone knows that this world's 'boire' action produces
    no water. Verify a paired command + physical world transition in the
    *same nonlethal attempt*, rather than a bare comparator declaration.
    This is a specific diagnostic, not a generic proof of every causal rule.
    """
    if journal is None or world_config is None:
        return ()
    if not journal.verify():
        raise ValueError("false-rule audit requires an intact causal journal")
    if (
        world_config.drink_water_gain != 0.0
        or world_config.water_decay_per_step != 0.0
    ):
        return ()

    # A command+transition pair is not a lived experiment until DC-09
    # commits that exact pair as an autobiographical, nonlethal segment.
    # In particular, discarded death/rollback attempts never get a commit.
    witnesses: set[str] = set()
    for commit in journal.entries:
        record = commit.causal_event
        if record.get("kind") != "auto_segment_commit":
            continue
        refs = record.get("event_refs")
        attempt = record.get("attempt_ref")
        step = record.get("t_monde")
        if (
            not isinstance(refs, list)
            or not refs
            or len(refs) != len(set(refs))
            or not isinstance(attempt, str)
            or not attempt
            or type(step) is not int
        ):
            continue
        entries = tuple(journal.get(ref) for ref in refs)
        if any(
            entry is None or entry.index >= commit.index
            for entry in entries
        ):
            continue
        commands = tuple(
            entry for entry in entries
            if entry.causal_event.get("kind") == "command_experienced"
        )
        transitions = tuple(
            entry for entry in entries
            if entry.causal_event.get("kind") == "world_transition_experienced"
        )
        if len(commands) != 1 or len(transitions) != 1:
            continue
        command = commands[0].causal_event
        physical = transitions[0].causal_event
        if any(
            row.get("attempt_ref") != attempt
            or row.get("t_monde") != step
            for row in (command, physical)
        ):
            continue
        effects = physical.get("effects")
        body = physical.get("body_after")
        if (
            command.get("primitive") != "boire"
            or command.get("parameters") != {}
            or not isinstance(effects, dict)
            or effects.get("drank") is not True
            or not isinstance(body, dict)
            or isinstance(body.get("water"), bool)
            or not isinstance(body.get("water"), (int, float))
            or not isfinite(body["water"])
        ):
            continue
        # The truth of the missing gain is externally known from frozen
        # physics. The segment witnesses that the individual really drank.
        witnesses.add(transitions[0].event_id)
    return tuple(sorted(witnesses))

def audit_superstitious_rules(
    *,
    causal_model: CausalModel,
    eligible_known_false_refs: Iterable[str],
    preregistered_max_rate: float | None,
    physical_journal: HashChainedJournal | None = None,
    known_false_world: WorldPhysicsConfig | None = None,
) -> SuperstitiousRuleAudit:
    """Rate established known-false rules only with lived physical exposure.

    A caller-supplied label is *not* verification. For Stage 9 the only
    supported physically checked canary is a null-water-effect world with
    a completed 'boire' transition. Unknown canaries and unobserved runs
    remain unevaluable, never successful by default.

    'passes' is an arithmetic check against a separately frozen threshold.
    Neither a diagnostic pass nor a threshold provided post hoc completes
    the scientific campaign acceptance gate (19.5 / 20.3).
    """
    if preregistered_max_rate is not None and (
        isinstance(preregistered_max_rate, bool)
        or not isinstance(preregistered_max_rate, (int, float))
        or not isfinite(preregistered_max_rate)
        or not 0 <= preregistered_max_rate <= 1
    ):
        raise ValueError("scientific threshold must be a finite preregistered rate")
    requested = tuple(sorted(set(eligible_known_false_refs)))
    if any(not isinstance(ref, str) or not ref for ref in requested):
        raise ValueError("known-false reference must be a nonempty string")
    if (physical_journal is None) != (known_false_world is None):
        raise ValueError("physical journal and external world must be paired")

    witnessed = _verified_null_drink_witnesses(
        journal=physical_journal, world_config=known_false_world,
    )
    observed = tuple(
        ref for ref in requested
        if ref == "causal:hydration" and witnessed
    )
    unverified = tuple(ref for ref in requested if ref not in observed)
    established = {
        row.ref for row in causal_model.contingencies(status="etablie")
    }
    false_rules = tuple(ref for ref in observed if ref in established)
    rate = None if not observed else len(false_rules) / len(observed)
    passed = (
        None if rate is None or preregistered_max_rate is None
        else rate <= preregistered_max_rate
    )
    return SuperstitiousRuleAudit(
        audited_false_refs=observed,
        established_false_refs=false_rules,
        observed_rate=rate,
        preregistered_max_rate=preregistered_max_rate,
        passes=passed,
        unverified_false_refs=unverified,
        physical_witness_refs=(
            witnessed if observed else ()
        ),
    )
