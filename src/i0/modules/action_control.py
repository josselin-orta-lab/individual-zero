"""Stage-3 Action Control: reflex, veto, mask and admissibility.

Action Control decides whether a prepared command may be sent. It does not own
the world and does not read oracle/bench/journal state.

Spec: 9.1-9.4, 20.3 Stage 3, DC-12, INV-12, INV-13, INV-52.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Protocol

from i0.interfaces import PrimitiveCommand

from .perception import PerceptualCapture


CANONICAL_DIRECTION_ORDER = ("north", "south", "east", "west")


class SafetyFactSource(Protocol):
    def zone_status(self, *, x: int, y: int) -> str:
        """Return known_safe, known_lethal, or unknown."""

    def item_status(self, *, resource_kind: str) -> str:
        """Return known_safe, known_toxic, or unknown."""


@dataclass(frozen=True, slots=True)
class StaticSafetyFacts:
    """Stage-3 immutable initial fact source, replaced later by Causal Model."""

    known_lethal_positions: frozenset[tuple[int, int]] = frozenset()
    known_safe_positions: frozenset[tuple[int, int]] = frozenset()
    known_toxic_resources: frozenset[str] = frozenset()
    known_safe_resources: frozenset[str] = frozenset()

    def zone_status(self, *, x: int, y: int) -> str:
        position = (x, y)
        if position in self.known_lethal_positions:
            return "known_lethal"
        if position in self.known_safe_positions:
            return "known_safe"
        return "unknown"

    def item_status(self, *, resource_kind: str) -> str:
        if resource_kind in self.known_toxic_resources:
            return "known_toxic"
        if resource_kind in self.known_safe_resources:
            return "known_safe"
        return "unknown"


@dataclass(frozen=True, slots=True)
class ActionControlConfig:
    safety_policy_version: str
    protected_integrity_threshold: float

    def validate(self) -> None:
        if not self.safety_policy_version:
            raise ValueError("safety policy version must not be empty")
        if not 0.0 < self.protected_integrity_threshold < 100.0:
            raise ValueError("P-37 must be strictly inside ]0,100[")


@dataclass(frozen=True, slots=True)
class PreparedCommand:
    command: PrimitiveCommand
    source: str
    trigger_ref: str | None = None
    option_ref: str | None = None
    st_version_ref: str | None = None
    established_integrity_after: float | None = None


class Admissibility(str, Enum):
    ADMISSIBLE = "admissible"
    INADMISSIBLE = "inadmissible"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True, slots=True)
class AdmissionResult:
    ok: bool
    reason: str | None
    scope: str | None
    rule_id: str | None
    rule_type: str | None
    policy_version: str
    command: PrimitiveCommand


@dataclass(frozen=True, slots=True)
class ReflexProposal:
    prepared: PreparedCommand
    stimulus: dict[str, object]


class ActionControl:
    """Only Stage-3 authority allowed to admit commands toward the world."""

    def __init__(
        self,
        *,
        config: ActionControlConfig,
        safety_facts: SafetyFactSource,
        protocol_mask: Callable[[PrimitiveCommand], bool],
    ) -> None:
        config.validate()
        self._config = config
        self._facts = safety_facts
        self._protocol_mask = protocol_mask

    @staticmethod
    def _destination(
        capture: PerceptualCapture,
        command: PrimitiveCommand,
    ) -> tuple[int, int] | None:
        if command.primitive != "se_deplacer":
            return None
        direction = command.parameters.get("direction")
        for cell in capture.adjacent:
            if cell.direction == direction:
                return (cell.x, cell.y)
        return None

    def reflex(self, capture: PerceptualCapture) -> ReflexProposal | None:
        creatures = capture.adjacent_creatures
        if not creatures:
            return None

        passable = capture.passable_moves
        if not passable:
            return None

        def nearest_creature_distance(cell) -> int:
            return min(
                abs(cell.x - creature.x) + abs(cell.y - creature.y)
                for creature in creatures
            )

        ranked = sorted(
            passable,
            key=lambda cell: (
                -nearest_creature_distance(cell),
                CANONICAL_DIRECTION_ORDER.index(cell.direction),
            ),
        )
        selected = ranked[0]
        stimulus = {
            "kind": "adjacent_creature",
            "creatures": [
                {"x": creature.x, "y": creature.y}
                for creature in creatures
            ],
        }
        return ReflexProposal(
            prepared=PreparedCommand(
                command=PrimitiveCommand(
                    primitive="se_deplacer",
                    parameters={"direction": selected.direction},
                ),
                source="reflex",
                trigger_ref="adjacent_creature",
            ),
            stimulus=stimulus,
        )

    def verifier_admissibilite(
        self,
        *,
        capture: PerceptualCapture,
        prepared: PreparedCommand,
    ) -> Admissibility:
        command = prepared.command

        destination = self._destination(capture, command)
        if destination is not None:
            status = self._facts.zone_status(x=destination[0], y=destination[1])
            if status == "known_lethal":
                return Admissibility.INADMISSIBLE
            if status == "unknown":
                return Admissibility.INDETERMINATE

        if command.primitive == "manger":
            resource = str(command.parameters.get("target"))
            status = self._facts.item_status(resource_kind=resource)
            if status == "known_toxic":
                return Admissibility.INADMISSIBLE
            if status == "unknown":
                return Admissibility.INDETERMINATE

        if prepared.established_integrity_after is not None:
            if (
                prepared.established_integrity_after
                < self._config.protected_integrity_threshold
            ):
                return Admissibility.INADMISSIBLE

        return Admissibility.ADMISSIBLE

    def admit(
        self,
        *,
        capture: PerceptualCapture,
        prepared: PreparedCommand,
    ) -> AdmissionResult:
        command = prepared.command
        destination = self._destination(capture, command)

        if destination is not None:
            status = self._facts.zone_status(x=destination[0], y=destination[1])
            if status == "known_lethal":
                return AdmissionResult(
                    ok=False,
                    reason="known_lethal_zone",
                    scope="option",
                    rule_id="lethal_zone_movement",
                    rule_type="semantic_prohibition",
                    policy_version=self._config.safety_policy_version,
                    command=command,
                )

        if command.primitive == "manger":
            resource = str(command.parameters.get("target"))
            if self._facts.item_status(resource_kind=resource) == "known_toxic":
                return AdmissionResult(
                    ok=False,
                    reason="known_toxic_item",
                    scope="option",
                    rule_id="toxic_item_consumption",
                    rule_type="semantic_prohibition",
                    policy_version=self._config.safety_policy_version,
                    command=command,
                )

        if (
            prepared.established_integrity_after is not None
            and prepared.established_integrity_after
            < self._config.protected_integrity_threshold
        ):
            return AdmissionResult(
                ok=False,
                reason="protected_integrity_violation",
                scope="option",
                rule_id="protected_invariant_violation",
                rule_type="protected_invariant",
                policy_version=self._config.safety_policy_version,
                command=command,
            )

        if self._protocol_mask(command):
            return AdmissionResult(
                ok=False,
                reason="protocol_mask",
                scope="protocol",
                rule_id="rollback_sequence_mask",
                rule_type="protocol",
                policy_version=self._config.safety_policy_version,
                command=command,
            )

        return AdmissionResult(
            ok=True,
            reason=None,
            scope=None,
            rule_id=None,
            rule_type=None,
            policy_version=self._config.safety_policy_version,
            command=command,
        )
