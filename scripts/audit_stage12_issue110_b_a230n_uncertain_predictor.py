"""A2.30-N: laboratory-only set-valued *delta* predictor.

Not an EquipmentModel. Never returns a next SimulationState, a command
recommendation, a safety certificate or a calibrated probability. The
"risk_label" is either known harmful FROM observed examples, or unresolved
because hidden physical causes may exist even for an exact known key.

All input features are derived exclusively from SimulationState and the
proposed PrimitiveCommand. The module has no WorldBody/Oracle/Bench access.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Sequence

from i0.equipment import EquipmentCorpusExample, SimulationState
from i0.interfaces import PrimitiveCommand
from lab.determinism import canonical_causal_bytes, sha256_hex

BODY_FIELDS = ("energy", "food", "water", "integrity")
INVENTORY_FIELDS = ("berry_a", "berry_b", "wood", "stone", "tool")
DELTA_FIELDS = (
    "dx", "dy",
    *(f"body.{item}" for item in BODY_FIELDS),
    *(f"inventory.{item}" for item in INVENTORY_FIELDS),
)
_ALLOWED_STATUSES = frozenset({"uncertain_interval", "abstain_unknown_context"})
_ALLOWED_RISKS = frozenset({"observed_harm", "unknown_hidden_risk", "unavailable"})


def observable_context(
    state: SimulationState, command: PrimitiveCommand
) -> dict[str, object]:
    """Frozen feature policy; neither future effects nor hidden configuration."""
    state.validate()
    primitive = command.primitive
    params = command.as_dict()["parameters"]
    features: dict[str, object] = {
        "is_night": bool(state.is_night),
        "primitive": primitive,
        "parameters": params,
    }
    if primitive == "se_deplacer":
        direction = params.get("direction")
        neighbor = next(
            (n for n in state.adjacent if n.direction == direction), None
        )
        features["visible_neighbor"] = (
            {"present": False} if neighbor is None else {
                "present": True,
                "passable": bool(neighbor.passable),
                "creature": bool(neighbor.creature),
            }
        )
    elif primitive == "collecter":
        target = params.get("target")
        features["resource_visible_here"] = target in state.current_resources
        features["tool_present"] = int(state.inventory.get("tool", 0)) > 0
    elif primitive == "manger":
        target = params.get("target")
        features["held_food_available"] = int(state.inventory.get(target, 0)) > 0
    elif primitive == "boire":
        features["water_source_here"] = bool(state.current_water_source)
    elif primitive in ("attendre", "dormir"):
        features["known_shelter_here"] = bool(state.known_shelter_here)
    else:
        # Untrained commands must abstain; we do not infer a fallback rule.
        features["unsupported_feature_policy"] = True
    return features


def observable_group_key(state: SimulationState, command: PrimitiveCommand) -> str:
    return sha256_hex(canonical_causal_bytes(observable_context(state, command)))


def actual_delta(example: EquipmentCorpusExample) -> dict[str, float]:
    """Partial physically observed effects, not complete next perceptions."""
    before = example.state
    after = example.observed_next_state
    result = {
        "dx": float(after.x - before.x),
        "dy": float(after.y - before.y),
    }
    for name in BODY_FIELDS:
        result[f"body.{name}"] = (
            float(after.body[name]) - float(before.body[name])
        )
    for name in INVENTORY_FIELDS:
        result[f"inventory.{name}"] = float(
            after.inventory.get(name, 0) - before.inventory.get(name, 0)
        )
    assert set(result) == set(DELTA_FIELDS)
    return result


def observed_harm(example: EquipmentCorpusExample) -> bool:
    return (
        example.terminal or float(example.observed_next_state.body["integrity"])
        < float(example.state.body["integrity"])
    )


@dataclass(frozen=True, slots=True)
class UncertainDeltaForecast:
    status: str
    group_key: str
    support_count: int
    risk_label: str
    lower: dict[str, float] | None
    upper: dict[str, float] | None
    observed_terminal_values: tuple[bool, ...]

    def validate(self) -> None:
        if self.status not in _ALLOWED_STATUSES:
            raise AssertionError("forecast is not a laboratory uncertainty status")
        if self.risk_label not in _ALLOWED_RISKS:
            raise AssertionError("forecast invented a safety certificate")
        if self.status == "uncertain_interval":
            if (
                self.support_count < 1 or self.lower is None or self.upper is None
                or set(self.lower) != set(DELTA_FIELDS)
                or set(self.upper) != set(DELTA_FIELDS)
                or not self.observed_terminal_values
            ):
                raise AssertionError("improper empirical interval")
            if any(
                self.lower[name] > self.upper[name] for name in DELTA_FIELDS
            ):
                raise AssertionError("lower bound exceeds upper bound")
        else:
            if (self.lower is not None or self.upper is not None
                    or self.support_count or self.observed_terminal_values):
                raise AssertionError("abstention leaked unsupported forecast")


class LaboratoryUncertainDeltaPredictor:
    """Readonly after initialization and intentionally NOT EquipmentModel."""

    def __init__(self, examples: Sequence[EquipmentCorpusExample]):
        if not examples:
            raise ValueError("independent physical training examples required")
        groups: dict[str, list[EquipmentCorpusExample]] = defaultdict(list)
        for ex in examples:
            ex.validate()
            groups[observable_group_key(ex.state, ex.command)].append(ex)
        self._groups: dict[str, UncertainDeltaForecast] = {}
        for key, rows in groups.items():
            deltas = tuple(actual_delta(e) for e in rows)
            out = UncertainDeltaForecast(
                status="uncertain_interval",
                group_key=key,
                support_count=len(rows),
                risk_label=("observed_harm"
                            if any(observed_harm(e) for e in rows)
                            else "unknown_hidden_risk"),
                lower={
                    col: min(d[col] for d in deltas) for col in DELTA_FIELDS
                },
                upper={
                    col: max(d[col] for d in deltas) for col in DELTA_FIELDS
                },
                observed_terminal_values=tuple(sorted({
                    e.terminal for e in rows
                })),
            )
            out.validate()
            self._groups[key] = out
        self.version = "lab-a230n-partial-delta-envelope-v1"
        self.training_examples = len(examples)
        self.group_count = len(self._groups)

    def forecast(
        self, *, state: SimulationState, command: PrimitiveCommand
    ) -> UncertainDeltaForecast:
        key = observable_group_key(state, command)
        existing = self._groups.get(key)
        if existing is not None:
            return existing
        missing = UncertainDeltaForecast(
            status="abstain_unknown_context", group_key=key, support_count=0,
            risk_label="unavailable", lower=None, upper=None,
            observed_terminal_values=(),
        )
        missing.validate()
        return missing


def evaluate_forecast(
    forecast: UncertainDeltaForecast, held_out: EquipmentCorpusExample
) -> dict[str, object]:
    """Scores the frozen forecast; test output never trains the prototype."""
    forecast.validate()
    if forecast.status != "uncertain_interval":
        return {
            "available": False,
            "all_delta_dimensions_covered": None,
            "interval_miss_fields": [],
            "terminal_outside_empirical_set": None,
            "empirical_interval_width_sum": None,
        }
    actual = actual_delta(held_out)
    assert forecast.lower is not None and forecast.upper is not None
    # Only a roundoff tolerance. NOT a safety margin or uncertainty calibration.
    missed = [
        col for col in DELTA_FIELDS
        if actual[col] < forecast.lower[col] - 1e-8
        or actual[col] > forecast.upper[col] + 1e-8
    ]
    return {
        "available": True,
        "all_delta_dimensions_covered": not missed,
        "interval_miss_fields": missed,
        "terminal_outside_empirical_set": (
            held_out.terminal not in forecast.observed_terminal_values
        ),
        "empirical_interval_width_sum": sum(
            forecast.upper[col] - forecast.lower[col] for col in DELTA_FIELDS
        ),
    }
