"""Bench-only oracle capability for normative Stage 2.

Spec: 19.1-19.4, INV-02, INV-03.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping, Protocol


class OracleAccessDenied(PermissionError):
    pass


class WorldTruthReader(Protocol):
    """Minimal authorized external world-truth read interface."""

    def ground_truth(self) -> Mapping[str, object]: ...


@dataclass(frozen=True, slots=True)
class OracleCapability:
    """Opaque bench capability. It is intentionally not serializable."""

    _token: object


class Oracle:
    """Complete ground truth readable only with the bench capability."""

    def __init__(self, *, world: WorldTruthReader, capability: OracleCapability) -> None:
        self._world = world
        self._capability = capability
        self._closed = False

    def close(self) -> None:
        """Revoke further truth reads without mutating the observed world."""
        self._closed = True

    def read_ground_truth(
        self,
        capability: OracleCapability,
    ) -> Mapping[str, object]:
        if self._closed:
            raise OracleAccessDenied("Oracle truth channel is closed")
        if capability is not self._capability:
            raise OracleAccessDenied("oracle channel is bench-only")
        truth = self._world.ground_truth()
        if not isinstance(truth, Mapping):
            raise TypeError("authorized truth source must provide a mapping")
        # Detached copy: evaluation cannot mutate physical/cognitive owners
        # by changing any nested field in a received oracle result.
        return deepcopy(dict(truth))


def create_oracle(world: WorldTruthReader) -> tuple[Oracle, OracleCapability]:
    token = object()
    capability = OracleCapability(token)
    return Oracle(world=world, capability=capability), capability
