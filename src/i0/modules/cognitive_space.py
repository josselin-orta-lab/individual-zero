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


def _plain(value):
    if isinstance(value, Mapping):
        return {
            str(key): _plain(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


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
                "fixed": _plain(current.fixed),
                "competitive": [
                    {
                        "contribution_ref": element.contribution_ref,
                        "summary": element.summary,
                        "score": element.score,
                        "decomposition": _plain(element.decomposition),
                        "reliability": element.reliability,
                        "production_t": element.production_t,
                        "expires_at_step": element.expires_at_step,
                        "preempted": element.preempted,
                    }
                    for element in current.competitive
                ],
                "requests": _plain(current.requests),
                "diff": _plain(current.diff),
            },
        }

    def restore_copy_causal_state(self, state: object) -> None:
        """Restore copied cognition while rebinding only the instance identity."""
        if not isinstance(state, Mapping):
            raise ValueError("S_t copy state must be a mapping")
        rebound = dict(state)
        rebound["individual_id"] = self._individual_id
        raw = rebound.get("current")
        if isinstance(raw, Mapping):
            current = dict(raw)
            current["individual_id"] = self._individual_id
            rebound["current"] = current
        self.restore_causal_state(rebound)

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("S_t state must be a mapping")
        if state.get("individual_id") != self._individual_id:
            raise ValueError("S_t individual mismatch")
        counter = state.get("version_counter")
        if not isinstance(counter, int) or counter < 0:
            raise ValueError("invalid S_t version counter")
        self._version_counter = counter
        raw = state.get("current")
        if raw is None:
            self._current = None
            return
        if not isinstance(raw, Mapping):
            raise ValueError("invalid S_t current state")
        elements = tuple(
            STElement(
                contribution_ref=str(item["contribution_ref"]),
                summary=str(item["summary"]),
                score=float(item["score"]),
                decomposition=_freeze(dict(item["decomposition"])),
                reliability=float(item["reliability"]),
                production_t=int(item["production_t"]),
                expires_at_step=int(item["expires_at_step"]),
                preempted=bool(item["preempted"]),
            )
            for item in raw.get("competitive", [])
        )
        self._current = STVersion(
            individual_id=str(raw["individual_id"]),
            version=str(raw["version"]),
            cycle=int(raw["cycle"]),
            t_monde=int(raw["t_monde"]),
            fixed=_freeze(dict(raw.get("fixed", {}))),
            competitive=elements,
            requests=_freeze(dict(raw.get("requests", {}))),
            diff=_freeze(dict(raw.get("diff", {}))),
        )
