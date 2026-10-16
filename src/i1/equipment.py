"""Stage-6 equipment contracts and immutable reference model.

Equipment predicts observable consequences only. It owns no preference,
temperament, learned value, accumulator, or oracle capability.

Spec: 12.1-12.5, 20.3 Stage 6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from i0.interfaces import PrimitiveCommand
from lab.determinism import canonical_causal_bytes, sha256_hex


@dataclass(frozen=True, slots=True)
class SimulationNeighbor:
    direction: str
    x: int
    y: int
    passable: bool
    water_source: bool
    resources: tuple[str, ...]
    creature: bool


@dataclass(frozen=True, slots=True)
class SimulationState:
    schema_version: str
    x: int
    y: int
    body: Mapping[str, float]
    inventory: Mapping[str, int]
    current_water_source: bool
    current_resources: tuple[str, ...]
    adjacent: tuple[SimulationNeighbor, ...]
    known_shelter_here: bool
    is_night: bool

    def validate(self) -> None:
        if not self.schema_version:
            raise ValueError("simulation-state schema version must not be empty")
        for name in ("energy", "food", "water", "integrity"):
            if name not in self.body:
                raise ValueError(f"simulation state missing body variable {name}")
            if not 0.0 <= float(self.body[name]) <= 100.0:
                raise ValueError(f"simulation body variable {name} out of range")
        for name, quantity in self.inventory.items():
            if int(quantity) < 0:
                raise ValueError(f"negative inventory quantity for {name}")
        directions = [neighbor.direction for neighbor in self.adjacent]
        if len(directions) != len(set(directions)):
            raise ValueError("duplicate simulation neighbor direction")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "x": self.x,
            "y": self.y,
            "body": dict(sorted((k, float(v)) for k, v in self.body.items())),
            "inventory": dict(sorted((k, int(v)) for k, v in self.inventory.items())),
            "current_water_source": self.current_water_source,
            "current_resources": list(self.current_resources),
            "adjacent": [
                {
                    "direction": item.direction,
                    "x": item.x,
                    "y": item.y,
                    "passable": item.passable,
                    "water_source": item.water_source,
                    "resources": list(item.resources),
                    "creature": item.creature,
                }
                for item in sorted(self.adjacent, key=lambda row: row.direction)
            ],
            "known_shelter_here": self.known_shelter_here,
            "is_night": self.is_night,
        }


@dataclass(frozen=True, slots=True)
class PredictedEffect:
    variable: str
    before: object
    after: object
    confidence: float

    def validate(self) -> None:
        if not self.variable:
            raise ValueError("predicted effect variable must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("prediction confidence must be in [0,1]")


@dataclass(frozen=True, slots=True)
class EquipmentPrediction:
    equipment_version: str
    state_schema_version: str
    horizon: int
    command: PrimitiveCommand
    next_state: SimulationState
    effects: tuple[PredictedEffect, ...]
    confidence: float
    terminal: bool = False

    def validate(self) -> None:
        if not self.equipment_version:
            raise ValueError("equipment version must not be empty")
        if self.horizon < 1:
            raise ValueError("prediction horizon must be >= 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("prediction confidence must be in [0,1]")
        self.next_state.validate()
        for effect in self.effects:
            effect.validate()


@dataclass(frozen=True, slots=True)
class EquipmentCorpusExample:
    family: str
    state: SimulationState
    command: PrimitiveCommand
    observed_next_state: SimulationState
    terminal: bool

    def validate(self) -> None:
        if not self.family:
            raise ValueError("corpus family must not be empty")
        self.state.validate()
        self.observed_next_state.validate()

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "family": self.family,
            "state": self.state.as_dict(),
            "command": self.command.as_dict(),
            "observed_next_state": self.observed_next_state.as_dict(),
            "terminal": self.terminal,
        }


@dataclass(frozen=True, slots=True)
class EquipmentCorpus:
    version: str
    examples: tuple[EquipmentCorpusExample, ...]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("corpus version must not be empty")
        if not self.examples:
            raise ValueError("equipment corpus must not be empty")
        for example in self.examples:
            example.validate()

    def digest(self) -> str:
        self.validate()
        payload = {
            "version": self.version,
            "examples": [example.as_dict() for example in self.examples],
        }
        return sha256_hex(canonical_causal_bytes(payload))

    def families(self) -> tuple[str, ...]:
        return tuple(sorted({example.family for example in self.examples}))


@dataclass(frozen=True, slots=True)
class EquipmentArtifact:
    version: str
    corpus_version: str
    corpus_sha256: str
    model_kind: str
    model_payload: Mapping[str, object]
    training_metadata: Mapping[str, object]

    def validate(self) -> None:
        if not self.version or not self.corpus_version or not self.corpus_sha256:
            raise ValueError("equipment artifact version/corpus metadata required")
        if len(self.corpus_sha256) != 64:
            raise ValueError("equipment corpus hash must be SHA-256 hex")
        if not self.model_kind:
            raise ValueError("equipment model kind must not be empty")
        canonical_causal_bytes(self.model_payload)
        canonical_causal_bytes(self.training_metadata)

    def digest(self) -> str:
        self.validate()
        return sha256_hex(
            canonical_causal_bytes(
                {
                    "version": self.version,
                    "corpus_version": self.corpus_version,
                    "corpus_sha256": self.corpus_sha256,
                    "model_kind": self.model_kind,
                    "model_payload": self.model_payload,
                    "training_metadata": self.training_metadata,
                }
            )
        )


class EquipmentModel(Protocol):
    @property
    def version(self) -> str:
        ...

    @property
    def artifact_digest(self) -> str:
        ...

    def predict(
        self,
        *,
        state: SimulationState,
        command: PrimitiveCommand,
    ) -> EquipmentPrediction:
        ...


@dataclass(frozen=True, slots=True)
class ExactTransitionRecord:
    input_sha256: str
    next_state: SimulationState
    effects: tuple[PredictedEffect, ...]
    terminal: bool


class FrozenTableEquipment:
    """Immutable exact-transition equipment produced from an offline corpus.

    The table intentionally has no fallback. An unseen state/action pair yields
    an unavailable prediction instead of inventing dynamics.
    """

    def __init__(
        self,
        *,
        artifact: EquipmentArtifact,
        records: Mapping[str, ExactTransitionRecord],
    ) -> None:
        artifact.validate()
        if artifact.model_kind != "exact_transition_table":
            raise ValueError("artifact is not an exact-transition table")
        self._artifact = artifact
        self._records = dict(records)

    @property
    def version(self) -> str:
        return self._artifact.version

    @property
    def artifact_digest(self) -> str:
        return self._artifact.digest()

    @staticmethod
    def input_digest(
        state: SimulationState,
        command: PrimitiveCommand,
    ) -> str:
        return sha256_hex(
            canonical_causal_bytes(
                {
                    "state": state.as_dict(),
                    "command": command.as_dict(),
                }
            )
        )

    def predict(
        self,
        *,
        state: SimulationState,
        command: PrimitiveCommand,
    ) -> EquipmentPrediction:
        state.validate()
        key = self.input_digest(state, command)
        record = self._records.get(key)
        if record is None:
            raise LookupError("equipment prediction unavailable for unseen input")
        prediction = EquipmentPrediction(
            equipment_version=self.version,
            state_schema_version=state.schema_version,
            horizon=1,
            command=command,
            next_state=record.next_state,
            effects=record.effects,
            confidence=1.0,
            terminal=record.terminal,
        )
        prediction.validate()
        return prediction


def train_exact_transition_table(
    *,
    corpus: EquipmentCorpus,
    equipment_version: str,
) -> FrozenTableEquipment:
    """Offline deterministic baseline trainer.

    Conflicting observations for an identical accessible input are rejected
    instead of silently averaged; later probabilistic E versions may model that
    uncertainty explicitly.
    """

    corpus.validate()
    records: dict[str, ExactTransitionRecord] = {}

    for example in corpus.examples:
        key = FrozenTableEquipment.input_digest(
            example.state,
            example.command,
        )
        effects: list[PredictedEffect] = []

        before = example.state.as_dict()
        after = example.observed_next_state.as_dict()
        for variable in ("x", "y", "body", "inventory", "current_water_source", "current_resources"):
            if before[variable] != after[variable]:
                effects.append(
                    PredictedEffect(
                        variable=variable,
                        before=before[variable],
                        after=after[variable],
                        confidence=1.0,
                    )
                )

        record = ExactTransitionRecord(
            input_sha256=key,
            next_state=example.observed_next_state,
            effects=tuple(effects),
            terminal=example.terminal,
        )
        previous = records.get(key)
        if previous is not None and previous != record:
            raise ValueError(
                "corpus contains conflicting outcomes for the same accessible input"
            )
        records[key] = record

    artifact = EquipmentArtifact(
        version=equipment_version,
        corpus_version=corpus.version,
        corpus_sha256=corpus.digest(),
        model_kind="exact_transition_table",
        model_payload={
            "record_count": len(records),
            "input_hashes": sorted(records),
        },
        training_metadata={
            "trainer": "train_exact_transition_table-v1",
            "example_count": len(corpus.examples),
            "families": list(corpus.families()),
        },
    )
    return FrozenTableEquipment(
        artifact=artifact,
        records=records,
    )
