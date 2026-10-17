"""Replay verification helpers for the deterministic execution substrate.

These helpers compare re-executed causal outputs. They never substitute a
saved future state for computation.

Spec: 17.1, 17.3, 17.8, 20.3 Stage 1, INV-33.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .determinism import canonical_causal_bytes, sha256_hex


@dataclass(frozen=True, slots=True)
class ReplayComparison:
    identical: bool
    reference_sha256: str
    replay_sha256: str

    def require_identical(self) -> None:
        if not self.identical:
            raise AssertionError(
                "causal replay diverged: "
                f"reference={self.reference_sha256}, replay={self.replay_sha256}"
            )


def compare_causal_state(
    reference: Mapping[str, object],
    replayed: Mapping[str, object],
) -> ReplayComparison:
    """Compare complete causal state byte-for-byte after canonical encoding."""

    reference_bytes = canonical_causal_bytes(reference)
    replay_bytes = canonical_causal_bytes(replayed)
    return ReplayComparison(
        identical=reference_bytes == replay_bytes,
        reference_sha256=sha256_hex(reference_bytes),
        replay_sha256=sha256_hex(replay_bytes),
    )


def verify_reexecution(
    *,
    execute_reference: Callable[[], Mapping[str, object]],
    execute_replay: Callable[[], Mapping[str, object]],
) -> ReplayComparison:
    """Execute both paths independently and compare their causal states."""

    return compare_causal_state(
        execute_reference(),
        execute_replay(),
    )
