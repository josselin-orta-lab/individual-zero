"""Stage-3 Action Control: reflex, veto, mask and admissibility.

Action Control decides whether a prepared command may be sent. It does not own
the world and does not read oracle/bench/journal state.

Spec: 9.1-9.4, 20.3 Stage 3, DC-12, INV-12, INV-13, INV-52.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Protocol

from i0.contracts import OptionProposal, PredictedConsequence
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
    grounding_contribution_refs: tuple[str, ...] = ()
    predicted_consequences: tuple[PredictedConsequence, ...] = ()
    observation_window_steps: int = 1


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
class AgencyComparison:
    option_ref: str | None
    sent_t_monde: int
    observed_t_monde: int
    status: str
    attribution: str
    effects: tuple[dict[str, object], ...]


@dataclass(frozen=True, slots=True)
class ReflexProposal:
    prepared: PreparedCommand
    stimulus: dict[str, object]


class ActionControl:
    """Only authority allowed to admit commands toward the world."""

    owner_id = "action_control"

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
        self._current_option_ref: str | None = None
        self._current_plan_ref: str | None = None
        self._current_step_index = 0
        self._pending_prediction: dict[str, object] | None = None
        self._last_comparison: AgencyComparison | None = None
        self._agency_comparator = None

    def attach_agency_comparator(self, comparator) -> None:
        if self._agency_comparator is not None:
            raise ValueError("agency comparator already installed")
        self._agency_comparator = comparator

    @property
    def current_step(self) -> tuple[str | None, str | None, int]:
        return (
            self._current_option_ref,
            self._current_plan_ref,
            self._current_step_index,
        )

    def prepare_option_step(self, proposal: OptionProposal) -> PreparedCommand:
        proposal.validate()
        if proposal.plan is None or not proposal.plan.steps:
            raise ValueError("decided option has no executable plan")

        option_ref = proposal.option.id
        plan_ref = proposal.plan.id
        if (
            self._current_option_ref != option_ref
            or self._current_plan_ref != plan_ref
        ):
            self._current_option_ref = option_ref
            self._current_plan_ref = plan_ref
            self._current_step_index = 0

        if self._current_step_index >= len(proposal.plan.steps):
            self._current_step_index = len(proposal.plan.steps) - 1

        step = proposal.plan.steps[self._current_step_index]
        return PreparedCommand(
            command=step.command,
            source="decision",
            option_ref=option_ref,
            st_version_ref=proposal.option.founding_st_version,
            grounding_contribution_refs=proposal.option.grounding_contribution_refs,
            predicted_consequences=step.predicted_consequences,
            observation_window_steps=step.observation_window_steps,
        )

    def mark_cognitive_step_applied(self, proposal: OptionProposal) -> None:
        if proposal.plan is None:
            return
        if (
            self._current_option_ref != proposal.option.id
            or self._current_plan_ref != proposal.plan.id
        ):
            raise ValueError("applied proposal does not match current control step")
        self._current_step_index += 1

    @property
    def last_comparison(self) -> AgencyComparison | None:
        return self._last_comparison

    def record_sent_prediction(
        self,
        *,
        prepared: PreparedCommand,
        t_monde: int,
    ) -> None:
        if self._agency_comparator is not None and (
            prepared.observation_window_steps < 1
            or prepared.observation_window_steps
            > self._agency_comparator.config.max_observation_window_steps
        ):
            raise ValueError("P-47 observation window outside declared range")
        if not prepared.predicted_consequences:
            self._pending_prediction = None
            return
        self._pending_prediction = {
            "option_ref": prepared.option_ref,
            "sent_t_monde": t_monde,
            "deadline_t_monde": t_monde + prepared.observation_window_steps,
            "consequences": tuple(prepared.predicted_consequences),
            **({"command": prepared.command} if self._agency_comparator is not None else {}),
        }

    def compare_capture(
        self,
        capture: PerceptualCapture,
    ) -> AgencyComparison | None:
        pending = self._pending_prediction
        if pending is None:
            return None
        sent_t = int(pending["sent_t_monde"])
        deadline = int(pending["deadline_t_monde"])
        if capture.t_monde <= sent_t:
            return None
        if capture.t_monde > deadline and self._agency_comparator is not None:
            # Stage 9 P-47 must version *missing effects* too. Preserve the
            # legacy Stage-3-8 branch unchanged when no comparator is attached.
            comparison = self._agency_comparator.compare(
                option_ref=pending["option_ref"],
                sent_t_monde=sent_t,
                deadline_t_monde=deadline,
                predictions=pending["consequences"],
                capture=capture,
                command=pending.get("command"),
            )
            self._pending_prediction = None
            self._last_comparison = comparison
            return comparison
        if capture.t_monde > deadline:
            comparison = AgencyComparison(
                option_ref=(
                    None
                    if pending["option_ref"] is None
                    else str(pending["option_ref"])
                ),
                sent_t_monde=sent_t,
                observed_t_monde=capture.t_monde,
                status="indeterminable",
                attribution="uncertain",
                effects=(
                    {
                        "status": "expected_effect_missing",
                        "deadline_t_monde": deadline,
                    },
                ),
            )
            self._pending_prediction = None
            self._last_comparison = comparison
            return comparison

        if self._agency_comparator is not None:
            comparison = self._agency_comparator.compare(
                option_ref=pending["option_ref"],
                sent_t_monde=sent_t,
                deadline_t_monde=deadline,
                predictions=pending["consequences"],
                capture=capture,
                command=pending.get("command"),
            )
            if comparison is not None:
                self._pending_prediction = None
                self._last_comparison = comparison
            return comparison

        effects: list[dict[str, object]] = []
        statuses: list[str] = []
        for consequence in pending["consequences"]:
            if not isinstance(consequence, PredictedConsequence):
                raise ValueError("invalid pending predicted consequence")
            if consequence.variable == "position_x":
                observed = float(capture.x)
            elif consequence.variable == "position_y":
                observed = float(capture.y)
            elif consequence.variable in {
                "energy",
                "food",
                "water",
                "integrity",
            }:
                observed = float(capture.body[consequence.variable])
            else:
                effects.append(
                    {
                        "variable": consequence.variable,
                        "status": "indeterminable",
                    }
                )
                statuses.append("indeterminable")
                continue

            difference = abs(observed - consequence.value_or_delta)
            status = (
                "conforming"
                if difference <= consequence.precision
                else "nonconforming"
            )
            statuses.append(status)
            effects.append(
                {
                    "variable": consequence.variable,
                    "predicted": consequence.value_or_delta,
                    "observed": observed,
                    "precision": consequence.precision,
                    "status": status,
                }
            )

        if statuses and all(status == "conforming" for status in statuses):
            overall = "conforming"
            attribution = "self_compatible"
        elif "nonconforming" in statuses:
            overall = "nonconforming"
            attribution = "uncertain"
        else:
            overall = "indeterminable"
            attribution = "uncertain"

        comparison = AgencyComparison(
            option_ref=(
                None
                if pending["option_ref"] is None
                else str(pending["option_ref"])
            ),
            sent_t_monde=sent_t,
            observed_t_monde=capture.t_monde,
            status=overall,
            attribution=attribution,
            effects=tuple(effects),
        )
        self._pending_prediction = None
        self._last_comparison = comparison
        return comparison

    def clear_option_step(self, option_ref: str | None = None) -> None:
        if option_ref is not None and self._current_option_ref != option_ref:
            return
        self._current_option_ref = None
        self._current_plan_ref = None
        self._current_step_index = 0

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

        def nearest_creature_distance_squared(cell) -> int:
            return min(
                (cell.x - creature.x) ** 2 + (cell.y - creature.y) ** 2
                for creature in creatures
            )

        # Normative §9.2: an avoidance reflex must move *away* from the
        # adjacent threat. Ranking solely among available movements can
        # otherwise select the creature-occupied cell itself when cornered.
        # Only the actually captured stimulus/adjacency is used; no oracle.
        present_distance_squared = min(
            (capture.x - creature.x) ** 2
            + (capture.y - creature.y) ** 2
            for creature in creatures
        )
        outward = tuple(
            cell for cell in passable
            if nearest_creature_distance_squared(cell)
            > present_distance_squared
        )
        if not outward:
            # No genuine retreat exists. Let ordinary deliberation proceed;
            # never present an approach toward a creature as escape.
            return None
        ranked = sorted(
            outward,
            key=lambda cell: (
                -nearest_creature_distance_squared(cell),
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

    def verifier_plan_connu(
        self,
        proposal: OptionProposal,
    ) -> Admissibility:
        """Prevalidate every plan step whose safety facts are already knowable.

        Future geometry comes only from the plan's predicted consequences. A
        missing destination or an unknown safety fact remains indeterminate;
        it is never upgraded to safe.
        """
        proposal.validate()
        if proposal.plan is None or not proposal.plan.steps:
            return Admissibility.INDETERMINATE

        saw_indeterminate = False
        for step in proposal.plan.steps:
            command = step.command

            if command.primitive == "se_deplacer":
                predicted = {
                    consequence.variable: consequence.value_or_delta
                    for consequence in step.predicted_consequences
                }
                if "position_x" not in predicted or "position_y" not in predicted:
                    saw_indeterminate = True
                else:
                    status = self._facts.zone_status(
                        x=int(predicted["position_x"]),
                        y=int(predicted["position_y"]),
                    )
                    if status == "known_lethal":
                        return Admissibility.INADMISSIBLE
                    if status == "unknown":
                        saw_indeterminate = True

            if command.primitive == "manger":
                resource = str(command.parameters.get("target"))
                status = self._facts.item_status(resource_kind=resource)
                if status == "known_toxic":
                    return Admissibility.INADMISSIBLE
                if status == "unknown":
                    saw_indeterminate = True

            integrity = next(
                (
                    consequence.value_or_delta
                    for consequence in step.predicted_consequences
                    if consequence.variable == "integrity"
                ),
                None,
            )
            if (
                integrity is not None
                and float(integrity)
                < self._config.protected_integrity_threshold
            ):
                return Admissibility.INADMISSIBLE

        return (
            Admissibility.INDETERMINATE
            if saw_indeterminate
            else Admissibility.ADMISSIBLE
        )

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

    def dispatch_if_admitted(
        self,
        *,
        capture: PerceptualCapture,
        prepared: PreparedCommand,
        sender: Callable[[PrimitiveCommand], object],
        on_admission: Callable[[AdmissionResult], None] | None = None,
    ) -> tuple[AdmissionResult, object | None]:
        """Admit first, record admission, then send exactly once if allowed."""

        admission = self.admit(capture=capture, prepared=prepared)
        if on_admission is not None:
            on_admission(admission)
        if not admission.ok:
            return admission, None
        return admission, sender(admission.command)

    def dispatch_prechecked(
        self,
        *,
        admission: AdmissionResult,
        sender: Callable[[PrimitiveCommand], object],
    ) -> object:
        if not admission.ok:
            raise ValueError("cannot dispatch a refused admission")
        return sender(admission.command)

    def export_causal_state(self) -> object:
        return {
            "safety_policy_version": self._config.safety_policy_version,
            "current_option_ref": self._current_option_ref,
            "current_plan_ref": self._current_plan_ref,
            "current_step_index": self._current_step_index,
            "pending_prediction": None
            if self._pending_prediction is None
            else {
                "option_ref": self._pending_prediction["option_ref"],
                "sent_t_monde": self._pending_prediction["sent_t_monde"],
                "deadline_t_monde": self._pending_prediction["deadline_t_monde"],
                **({"command": {
                    "primitive": self._pending_prediction["command"].primitive,
                    "parameters": dict(self._pending_prediction["command"].parameters),
                }} if self._agency_comparator is not None and self._pending_prediction.get("command") is not None else {}),
                "consequences": [
                    {
                        "variable": consequence.variable,
                        "value_or_delta": consequence.value_or_delta,
                        "precision": consequence.precision,
                    }
                    for consequence in self._pending_prediction["consequences"]
                ],
            },
            "last_comparison": None
            if self._last_comparison is None
            else {
                "option_ref": self._last_comparison.option_ref,
                "sent_t_monde": self._last_comparison.sent_t_monde,
                "observed_t_monde": self._last_comparison.observed_t_monde,
                "status": self._last_comparison.status,
                "attribution": self._last_comparison.attribution,
                "effects": list(self._last_comparison.effects),
            },
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, dict):
            raise ValueError("Action Control state must be a mapping")
        if state.get("safety_policy_version") != self._config.safety_policy_version:
            raise ValueError("Action Control safety-policy version mismatch")
        option_ref = state.get("current_option_ref")
        plan_ref = state.get("current_plan_ref")
        step_index = state.get("current_step_index")
        if option_ref is not None and not isinstance(option_ref, str):
            raise ValueError("invalid current option ref")
        if plan_ref is not None and not isinstance(plan_ref, str):
            raise ValueError("invalid current plan ref")
        if not isinstance(step_index, int) or step_index < 0:
            raise ValueError("invalid current step index")
        self._current_option_ref = option_ref
        self._current_plan_ref = plan_ref
        self._current_step_index = step_index

        raw_pending = state.get("pending_prediction")
        if raw_pending is None:
            self._pending_prediction = None
        elif isinstance(raw_pending, dict):
            self._pending_prediction = {
                "option_ref": raw_pending.get("option_ref"),
                "sent_t_monde": int(raw_pending["sent_t_monde"]),
                "deadline_t_monde": int(raw_pending["deadline_t_monde"]),
                **({"command": PrimitiveCommand(
                    primitive=str(raw_pending["command"]["primitive"]),
                    parameters=dict(raw_pending["command"]["parameters"]),
                )} if raw_pending.get("command") is not None else {}),
                "consequences": tuple(
                    PredictedConsequence(
                        variable=str(item["variable"]),
                        value_or_delta=float(item["value_or_delta"]),
                        precision=float(item["precision"]),
                    )
                    for item in raw_pending.get("consequences", [])
                ),
            }
        else:
            raise ValueError("invalid pending prediction state")

        raw_comparison = state.get("last_comparison")
        if raw_comparison is None:
            self._last_comparison = None
        elif isinstance(raw_comparison, dict):
            self._last_comparison = AgencyComparison(
                option_ref=(
                    None
                    if raw_comparison.get("option_ref") is None
                    else str(raw_comparison["option_ref"])
                ),
                sent_t_monde=int(raw_comparison["sent_t_monde"]),
                observed_t_monde=int(raw_comparison["observed_t_monde"]),
                status=str(raw_comparison["status"]),
                attribution=str(raw_comparison["attribution"]),
                effects=tuple(
                    dict(item) for item in raw_comparison.get("effects", [])
                ),
            )
        else:
            raise ValueError("invalid agency comparison state")
