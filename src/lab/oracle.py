"""Bench-only oracle capability for normative Stage 2.

Spec: 19.1-19.4, INV-02, INV-03.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .world import WorldBody


class OracleAccessDenied(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class OracleCapability:
    """Opaque bench capability. It is intentionally not serializable."""

    _token: object


class Oracle:
    """Complete ground truth readable only with the bench capability."""

    def __init__(self, *, world: WorldBody, capability: OracleCapability) -> None:
        self._world = world
        self._capability = capability

    def read_ground_truth(
        self,
        capability: OracleCapability,
    ) -> Mapping[str, object]:
        if capability is not self._capability:
            raise OracleAccessDenied("oracle channel is bench-only")
        return self._world.ground_truth()


def create_oracle(world: WorldBody) -> tuple[Oracle, OracleCapability]:
    token = object()
    capability = OracleCapability(token)
    return Oracle(world=world, capability=capability), capability
