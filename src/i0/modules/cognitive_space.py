"""S_t owner for Stage 4.

The Gatekeeper supplies candidate content. This store alone publishes and owns
immutable S_t versions.

Spec: 5.3, 6.2, INV-01, INV-04.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from i0.contracts import STElement, STVersion


def _freeze(value):
    if isinstance(value, Mapping):
        return MappingProxyType({
            str(key): _freeze(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        })
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    return value


class CognitiveSpace:
    owner_id = "s_t"

    def __init__(self, *, individual_id: str) -> None:
        if not individual_id:
            raise ValueError("individual_id must not be empty")
        self._individual_id = individual_id
        self._current: STVersion | None = None
        self._version_counter = 0

    @property
    def current(self) -> STVersion | None:
        return self._current

    def publish(
        self,
        *,
        cycle: int,
        t_monde: int,
        fixed: Mapping[str, object],
        competitive: tuple[STElement, ...],
        requests: Mapping[str, str] | None = None,
        diff: Mapping[str, object] | None = None,
    ) -> STVersion:
        self._version_counter += 1
        version = STVersion(
            individual_id=self._individual_id,
            version=f"S_t:{t_monde}:{cycle}:{self._version_counter}",
            cycle=cycle,
            t_monde=t_monde,
            fixed=_freeze(fixed),
            competitive=tuple(competitive),
            requests=_freeze(requests or {}),
            diff=_freeze(diff or {}),
        )
        self._current = version
        return version

    def export_causal_state(self) -> object:
        current = self._current
        return {
            "individual_id": self._individual_id,
            "version_counter": self._version_counter,
            "current": None if current is None else {
                "individual_id": current.individual_id,
                "version": current.version,
                "cycle": current.cycle,
                "t_monde": current.t_monde,
                "fixed": dict(current.fixed),
                "competitive": [
                    {
                        "contribution_ref": element.contribution_ref,
                        "summary": element.summary,
                        "score": element.score,
                        "decomposition": dict(element.decomposition),
                        "reliability": element.reliability,
                        "production_t": element.production_t,
                        "expires_at_step": element.expires_at_step,
                        "preempted": element.preempted,
                    }
                    for element in current.competitive
                ],
                "requests": dict(current.requests),
                "diff": dict(current.diff),
            },
        }
