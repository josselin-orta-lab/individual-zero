"""Stage-9 independently testable AgencyComparator, §9.6 / P-47.

The service is owned by Action Control, not a top-level cognitive component.
Predictions are frozen at emission, observations come only from Perception, and
no oracle, raw world state, or simulator can be consulted. This service is
pure: Action Control owns pending predictions and snapshot/restore.

A compatible prediction is not proof of self-causation. World attribution
requires an independently accessible physical obstacle that explains a
nonconforming movement, otherwise attribution remains uncertain.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

from i0.contracts import PredictedConsequence
from i0.interfaces import PrimitiveCommand

from .action_control import AgencyComparison
from .perception import PerceptualCapture


P47_ACCESSIBLE_VARIABLES = frozenset({
    "position_x", "position_y", "energy", "food", "water", "integrity",
})


@dataclass(frozen=True, slots=True)
class AgencyComparatorConfig:
    version: str
    tolerances: Mapping[str, float]
    max_observation_window_steps: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("P-47 comparator version is required")
        if (
            not isinstance(self.max_observation_window_steps, int)
            or isinstance(self.max_observation_window_steps, bool)
            or self.max_observation_window_steps < 1
        ):
            raise ValueError("P-47 maximum observation window must be positive")
        if set(self.tolerances) != P47_ACCESSIBLE_VARIABLES:
            raise ValueError("P-47 must declare tolerances for every accessible variable")
        if any(not isfinite(value) or value < 0 for value in self.tolerances.values()):
            raise ValueError("P-47 tolerances must be finite and nonnegative")


class AgencyComparator:
    """Action-Control subservice; no causal state and no world access."""

    def __init__(self, config: AgencyComparatorConfig) -> None:
        config.validate()
        self.config = config

    @staticmethod
    def _observed(capture: PerceptualCapture, name: str) -> float | None:
        if name == "position_x":
            return float(capture.x)
        if name == "position_y":
            return float(capture.y)
        if name in {"energy", "food", "water", "integrity"}:
            value = capture.body.get(name)
            return float(value) if value is not None and isfinite(float(value)) else None
        return None

    @staticmethod
    def _physical_obstacle_is_accessible(
        *, command: PrimitiveCommand | None, capture: PerceptualCapture
    ) -> bool:
        if command is None or command.primitive != "se_deplacer":
            return False
        direction = command.parameters.get("direction")
        return any(
            cell.direction == direction and not cell.passable
            for cell in capture.adjacent
        )

    @staticmethod
    def _visible_creature_can_explain_integrity_loss(
        *, effects: Sequence[Mapping[str, object]],
        capture: PerceptualCapture,
    ) -> bool:
        """Use accessible external evidence, never the world's true cause.

        One adjacent perceived creature can justify a nonconforming loss of
        integrity inside the declared P-47 window. It is not a causal proof,
        and neither a mere nearby creature nor a predicted integrity gain
        suffices. Multiple visible creatures leave the attribution uncertain.
        """
        visible_creatures = capture.adjacent_creatures
        deviations = tuple(
            effect for effect in effects
            if effect.get("status") == "nonconforming"
        )
        return (
            len(visible_creatures) == 1
            and bool(deviations)
            and all(
                effect.get("variable") == "integrity"
                and isinstance(effect.get("predicted"), (int, float))
                and not isinstance(effect.get("predicted"), bool)
                and isinstance(effect.get("observed"), (int, float))
                and not isinstance(effect.get("observed"), bool)
                and float(effect["observed"]) < float(effect["predicted"])
                for effect in deviations
            )
        )

    def compare(
        self,
        *,
        option_ref: str | None,
        sent_t_monde: int,
        deadline_t_monde: int,
        predictions: Sequence[PredictedConsequence],
        capture: PerceptualCapture,
        command: PrimitiveCommand | None,
    ) -> AgencyComparison | None:
        if capture.t_monde <= sent_t_monde:
            return None
        if (
            deadline_t_monde <= sent_t_monde
            or deadline_t_monde - sent_t_monde
            > self.config.max_observation_window_steps
        ):
            raise ValueError("prediction window exceeds P-47 preregistration")
        if capture.t_monde > deadline_t_monde:
            return AgencyComparison(
                option_ref=option_ref,
                sent_t_monde=sent_t_monde,
                observed_t_monde=capture.t_monde,
                status="indeterminable",
                attribution="uncertain",
                effects=({
                    "status": "expected_effect_missing",
                    "deadline_t_monde": deadline_t_monde,
                    "comparator_version": self.config.version,
                },),
            )

        effects: list[dict[str, object]] = []
        statuses: list[str] = []
        for p in predictions:
            if p.variable not in P47_ACCESSIBLE_VARIABLES:
                effects.append({
                    "variable": p.variable, "status": "indeterminable",
                    "comparator_version": self.config.version,
                })
                statuses.append("indeterminable")
                continue
            observed = self._observed(capture, p.variable)
            if observed is None:
                effects.append({
                    "variable": p.variable, "status": "indeterminable",
                    "comparator_version": self.config.version,
                })
                statuses.append("indeterminable")
                continue
            tolerance = max(p.precision, self.config.tolerances[p.variable])
            if not isfinite(tolerance) or tolerance < 0:
                raise ValueError("invalid effective P-47 tolerance")
            status = (
                "conforming"
                if abs(observed - p.value_or_delta) <= tolerance
                else "nonconforming"
            )
            effects.append({
                "variable": p.variable,
                "predicted": p.value_or_delta,
                "observed": observed,
                "precision": tolerance,
                "status": status,
                "comparator_version": self.config.version,
            })
            statuses.append(status)

        if statuses and all(s == "conforming" for s in statuses):
            overall, attribution = "conforming", "self_compatible"
        elif "nonconforming" in statuses:
            overall = "nonconforming"
            # An accessible obstacle justifies a world factor ONLY for motion.
            only_motion = all(
                e.get("variable") in {"position_x", "position_y"}
                for e in effects if e.get("status") == "nonconforming"
            )
            visible_external_explanation = (
                (
                    only_motion
                    and self._physical_obstacle_is_accessible(
                        command=command, capture=capture,
                    )
                )
                or self._visible_creature_can_explain_integrity_loss(
                    effects=effects, capture=capture,
                )
            )
            attribution = (
                "world_justified"
                if visible_external_explanation
                else "uncertain"
            )
        else:
            overall, attribution = "indeterminable", "uncertain"
        return AgencyComparison(
            option_ref=option_ref,
            sent_t_monde=sent_t_monde,
            observed_t_monde=capture.t_monde,
            status=overall,
            attribution=attribution,
            effects=tuple(effects),
        )

    def compatible_candidates(
        self, candidates: Sequence[AgencyComparison]
    ) -> tuple[str, ...]:
        """Retain all compatible command candidates, not an arbitrary winner."""
        return tuple(sorted({
            c.option_ref for c in candidates
            if c.status == "conforming"
            and c.attribution == "self_compatible"
            and c.option_ref is not None
        }))
