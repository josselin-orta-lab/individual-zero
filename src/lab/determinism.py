"""Normative deterministic execution primitives for MVP v1.2.1.

Spec: 5.1, 17.1-17.2, 20.3 Stage 1, INV-22, INV-33.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
import random
import unicodedata
from typing import Mapping, Sequence


DETERMINISTIC_RUNTIME_CONTRACT = "mvp-v1.2.1"
_REQUIRED_CONTRACT_NAMES = (
    "ontology_registry",
    "similarity_schema",
    "signal_family_registry",
    "safety_policy",
    "parameter_registry",
    "schema_registry",
    "equipment",
)


def _normalize(value: object) -> object:
    """Return the normative JSON-compatible causal representation."""

    if value is None or isinstance(value, (bool, int)):
        return value

    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite floats are forbidden in causal data")
        normalized = 0.0 if value == 0.0 else value
        return {"$f64": normalized.hex().lower()}

    if isinstance(value, Mapping):
        normalized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("causal mapping keys must be strings")
            normalized[unicodedata.normalize("NFC", key)] = _normalize(item)
        return normalized

    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]

    if isinstance(value, (set, frozenset)):
        raise TypeError("unordered collections are forbidden in causal data")

    raise TypeError(f"unsupported causal type: {type(value).__name__}")


def canonical_causal_bytes(value: object) -> bytes:
    """Encode causal data using the v1.2.1 canonical UTF-8 JSON contract."""

    normalized = _normalize(value)
    text = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return text.encode("utf-8")


def sha256_hex(data: bytes) -> str:
    """Return a lowercase SHA-256 hexadecimal digest."""

    return sha256(data).hexdigest()


def deterministic_id(namespace: str, *stable_context: object) -> str:
    """Derive a full deterministic identifier from namespace and stable context."""

    if not namespace:
        raise ValueError("namespace must not be empty")
    payload = [namespace, *stable_context]
    return sha256_hex(canonical_causal_bytes(payload))


def derive_stream_seed(campaign_seed: object, stream_id: str) -> int:
    """Derive the normative 128-bit integer seed for one causal RNG stream."""

    if not stream_id:
        raise ValueError("stream_id must not be empty")
    digest = sha256(
        b"I0|rng|"
        + canonical_causal_bytes(campaign_seed)
        + b"|"
        + canonical_causal_bytes(stream_id)
    ).digest()
    return int.from_bytes(digest[:16], byteorder="big", signed=False)


class RandomStreamRegistry:
    """Independent, reproducible random.Random streams keyed by causal source."""

    def __init__(self, *, campaign_seed: object) -> None:
        self._campaign_seed = campaign_seed
        self._streams: dict[str, random.Random] = {}

    def stream(self, stream_id: str) -> random.Random:
        if not stream_id:
            raise ValueError("stream_id must not be empty")
        if stream_id not in self._streams:
            self._streams[stream_id] = random.Random(
                derive_stream_seed(self._campaign_seed, stream_id)
            )
        return self._streams[stream_id]

    def snapshot(self) -> dict[str, object]:
        """Return complete getstate() values for every instantiated stream."""

        return {
            stream_id: generator.getstate()
            for stream_id, generator in sorted(self._streams.items())
        }

    def restore(self, states: Mapping[str, object]) -> None:
        """Restore complete states without consuming any draw."""

        restored: dict[str, random.Random] = {}
        for stream_id in sorted(states):
            if not isinstance(stream_id, str) or not stream_id:
                raise ValueError("stream ids must be non-empty strings")
            generator = random.Random()
            generator.setstate(states[stream_id])  # type: ignore[arg-type]
            restored[stream_id] = generator
        self._streams = restored


@dataclass(frozen=True, slots=True)
class StructuralContractRef:
    """Version and hash of one frozen structural contract artifact."""

    name: str
    version: str
    sha256: str

    def validate(self) -> None:
        if not self.name or not self.version:
            raise ValueError("contract name and version must not be empty")
        if len(self.sha256) != 64:
            raise ValueError("contract sha256 must contain 64 hexadecimal characters")
        try:
            int(self.sha256, 16)
        except ValueError as exc:
            raise ValueError("contract sha256 must be hexadecimal") from exc

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name, "version": self.version, "sha256": self.sha256}


@dataclass(frozen=True, slots=True)
class RunManifest:
    """Immutable causal manifest required before replayable execution."""

    specification_version: str
    deterministic_runtime_contract: str
    python_version: str
    code_commit: str
    campaign_seed: object
    contracts: tuple[StructuralContractRef, ...]

    def validate(self) -> None:
        if self.specification_version != "1.2.1":
            raise ValueError("MVP implementation requires specification version 1.2.1")
        if self.deterministic_runtime_contract != DETERMINISTIC_RUNTIME_CONTRACT:
            raise ValueError("unsupported deterministic runtime contract")
        if not self.python_version.startswith("3.11"):
            raise ValueError("reference runtime family is Python 3.11")
        if not self.code_commit:
            raise ValueError("code_commit must not be empty")

        names: list[str] = []
        for contract in self.contracts:
            contract.validate()
            names.append(contract.name)

        if len(names) != len(set(names)):
            raise ValueError("structural contract names must be unique")

        missing = [name for name in _REQUIRED_CONTRACT_NAMES if name not in names]
        if missing:
            raise ValueError(
                "missing required structural contracts: " + ", ".join(missing)
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "specification_version": self.specification_version,
            "deterministic_runtime_contract": self.deterministic_runtime_contract,
            "python_version": self.python_version,
            "code_commit": self.code_commit,
            "campaign_seed": self.campaign_seed,
            "contracts": [
                contract.as_dict()
                for contract in sorted(self.contracts, key=lambda item: item.name)
            ],
        }

    def canonical_bytes(self) -> bytes:
        self.validate()
        return canonical_causal_bytes(self.as_dict())

    def digest(self) -> str:
        return sha256_hex(self.canonical_bytes())
