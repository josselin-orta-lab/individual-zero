"""MVP v1.3.3: isolated, laboratory-only visible-delta shadow model.

This intentionally does NOT implement EquipmentModel.predict, create an
EquipmentPrediction/SimulationState, influence Stage-6 search, or dispatch a
command. A2.30-ZO/ZS demonstrated some six-component partial forecasts in
external worlds, NOT physical safety or autonomy. No runtime imports this
module. Training from an individual life requires a separately reviewed
first-person provenance, UC, persistence and release contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from i0.equipment import EquipmentCorpus, SimulationState
from i0.interfaces import PrimitiveCommand


MODEL_VERSION = "stage6-visible-deltas-shadow-v1"
SOURCE_SCOPE = "external_lab"
FIELDS = ("x", "y", "energy", "food", "water", "inventory_berry_b")
ACTIONS = ("MOVE_E", "COLLECT_B")
MIN_EXAMPLES_PER_ACTION = 8
UNRESOLVED = (
    "integrity", "terminality", "next_adjacency", "food_safety",
    "motor_safety", "distal_causal_responsibility",
)


def _action_key(command: PrimitiveCommand) -> str | None:
    # Exact public command signature; never silently accept ingestion,
    # another direction, or an unreviewed primitive.
    if (command.primitive == "se_deplacer"
            and dict(command.parameters) == {"direction": "east"}):
        return "MOVE_E"
    if (command.primitive == "collecter"
            and dict(command.parameters) == {"target": "berry_b"}):
        return "COLLECT_B"
    return None


def _visible_deltas(before: SimulationState, after: SimulationState) -> dict[str, float | int]:
    before.validate()
    after.validate()
    if before.schema_version != after.schema_version:
        raise ValueError("cross-schema transition not permitted")
    if "berry_b" not in before.inventory or "berry_b" not in after.inventory:
        raise ValueError("berry_b inventory must be explicitly observed")
    for state in (before, after):
        for k in ("energy", "food", "water", "integrity"):
            if not isfinite(float(state.body[k])):
                raise ValueError("non-finite body observation")
    return {
        "x": int(after.x - before.x),
        "y": int(after.y - before.y),
        "energy": round(float(after.body["energy"]) - float(before.body["energy"]), 8),
        "food": round(float(after.body["food"]) - float(before.body["food"]), 8),
        "water": round(float(after.body["water"]) - float(before.body["water"]), 8),
        "inventory_berry_b": int(after.inventory["berry_b"] - before.inventory["berry_b"]),
    }


@dataclass(frozen=True, slots=True)
class VisibleDeltaForecast:
    """An incomplete, explicitly non-certifying experimental forecast."""

    model_version: str
    corpus_sha256: str
    status: str
    estimated: Mapping[str, float | int] | None
    sample_count: int
    source_scope: str = SOURCE_SCOPE

    def as_dict(self) -> dict[str, object]:
        # Unknowns are explicit, including when all six numbers are correct.
        return {
            "model_version": self.model_version,
            "corpus_sha256": self.corpus_sha256,
            "source_scope": self.source_scope,
            "status": self.status,
            "estimated": None if self.estimated is None else dict(self.estimated),
            "sample_count": self.sample_count,
            "integrity": None,
            "terminal": None,
            "next_adjacency": None,
            "safe": None,
            "causal_responsibility": None,
            "unresolved": list(UNRESOLVED),
        }


@dataclass(frozen=True, slots=True)
class ShadowVisibleDeltaModel:
    """Frozen external-laboratory diagnostic, never an EquipmentModel.

    The tuple representation prevents accidentally changing a learned delta
    in place; a different model is a different, explicitly versioned fit.
    """

    version: str
    corpus_sha256: str
    deltas: tuple[tuple[str, tuple[tuple[str, float | int | None], ...]], ...]
    counts: tuple[tuple[str, int], ...]
    source_scope: str = SOURCE_SCOPE
    activation: str = "shadow_only"

    def forecast_for_review(
        self, *, state: SimulationState, command: PrimitiveCommand
    ) -> VisibleDeltaForecast:
        """Estimate a few visible effects, NEVER a complete future state."""
        state.validate()
        action = _action_key(command)
        samples = dict(self.counts).get(action, 0) if action is not None else 0

        def abstain(reason: str) -> VisibleDeltaForecast:
            return VisibleDeltaForecast(
                self.version, self.corpus_sha256, reason, None, samples
            )

        if action is None:
            return abstain("abstain_unsupported_action")
        if state.schema_version != "simulation-state-v1":
            # Schema migration needs a new experiment and explicit versioning.
            return abstain("abstain_out_of_distribution")
        if "berry_b" not in state.inventory:
            return abstain("abstain_missing_observation")
        if not all(isfinite(float(state.body[k])) for k in
                   ("energy", "food", "water", "integrity")):
            return abstain("abstain_missing_observation")
        if action == "COLLECT_B" and "berry_b" not in state.current_resources:
            return abstain("abstain_ineligible")
        if action == "MOVE_E":
            adjacent = [n for n in state.adjacent if n.direction == "east"]
            if not adjacent:
                return abstain("abstain_missing_observation")
            east = adjacent[0]
            if not east.passable:
                return abstain("abstain_ineligible")
            if east.x != state.x + 1 or east.y != state.y:
                return abstain("abstain_inconsistent_observation")

        learned = dict(dict(self.deltas).get(action, ()))
        if set(learned) != set(FIELDS) or any(learned[k] is None for k in FIELDS):
            return abstain("abstain_unstable_training")
        estimates: dict[str, float | int] = {
            "x": int(state.x + int(learned["x"])),
            "y": int(state.y + int(learned["y"])),
            "energy": round(float(state.body["energy"]) + float(learned["energy"]), 8),
            "food": round(float(state.body["food"]) + float(learned["food"]), 8),
            "water": round(float(state.body["water"]) + float(learned["water"]), 8),
            "inventory_berry_b": int(state.inventory["berry_b"]) +
                                 int(learned["inventory_berry_b"]),
        }
        if (estimates["x"] < 0 or estimates["y"] < 0
                or estimates["inventory_berry_b"] < 0
                or any(not 0.0 <= estimates[k] <= 100.0
                       for k in ("energy", "food", "water"))):
            # Clamped physics and unknown map bounds are not extrapolated.
            return abstain("abstain_boundary")
        return VisibleDeltaForecast(
            self.version, self.corpus_sha256,
            "empirical_partial_not_certified", estimates, samples
        )


def fit_external_lab_shadow(
    *, corpus: EquipmentCorpus, version: str = MODEL_VERSION,
    source_scope: str = SOURCE_SCOPE,
) -> ShadowVisibleDeltaModel:
    """Fit only archived external, nonterminal, non-ingestive observations.

    The caller must separately audit the source and the temporal split.
    A Git hash is integrity metadata, never independent proof of physics.
    No method here is authorized to learn from I0's runtime or heldout data.
    """
    if source_scope != SOURCE_SCOPE:
        raise ValueError("first-person learning is not authorized by this shadow API")
    if version != MODEL_VERSION:
        raise ValueError("unreviewed experimental model version")
    corpus.validate()
    groups: dict[str, list[dict[str, float | int]]] = {key: [] for key in ACTIONS}
    for ex in corpus.examples:
        key = _action_key(ex.command)
        if key is None:
            raise ValueError("unsupported or ingestive training action")
        if ex.terminal:
            raise ValueError("terminal external data cannot become a lived after-state")
        if ex.state.schema_version != "simulation-state-v1":
            raise ValueError("unsupported pre-action state schema")
        groups[key].append(_visible_deltas(ex.state, ex.observed_next_state))
    if any(len(groups[key]) < MIN_EXAMPLES_PER_ACTION for key in ACTIONS):
        raise ValueError("insufficient training examples for preregistered actions")
    fitted: list[tuple[str, tuple[tuple[str, float | int | None], ...]]] = []
    for key in ACTIONS:
        coefficients: list[tuple[str, float | int | None]] = []
        for field in FIELDS:
            values = {row[field] for row in groups[key]}
            coefficients.append((field, next(iter(values)) if len(values) == 1 else None))
        fitted.append((key, tuple(coefficients)))
    return ShadowVisibleDeltaModel(
        version=version,
        corpus_sha256=corpus.digest(),
        deltas=tuple(fitted),
        counts=tuple((key, len(groups[key])) for key in ACTIONS),
    )
