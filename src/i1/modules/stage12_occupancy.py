"""Stage12 read-only module occupancy entropy on the *current* S_t.

This is intentionally distinct from temporal context-signature entropy.
The projection is comprised of actual retained S_t contributions, not the
candidate queue, the Oracle or a claim about cognition that did not occur.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ModuleOccupancy:
    status: str
    normalized_entropy: float | None
    low_entropy: bool | None
    occupied_slots: int
    distinct_modules: int

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "normalized_entropy": self.normalized_entropy,
            "low_entropy": self.low_entropy,
            "occupied_slots": self.occupied_slots,
            "distinct_modules": self.distinct_modules,
        }


def module_occupancy_entropy(
    counts: Mapping[str, int], *, warning_fraction: float,
    module_universe_size: int,
) -> ModuleOccupancy:
    """Normalized Shannon entropy across a fixed, versioned module universe.

    Counts must be derived from retained S_t elements. If a module has no
    elements its occupancy is zero, *not* a missing observation. Empty S_t
    itself is unavailable rather than a falsely reassuring 0.0 entropy.
    """
    if (type(module_universe_size) is not int or module_universe_size < 2
            or type(warning_fraction) not in (float, int)
            or not isfinite(warning_fraction)
            or not 0.0 <= warning_fraction <= 1.0
            or not isinstance(counts, Mapping)):
        raise ValueError("invalid module occupancy policy")
    if any(
        type(module) is not str or not module
        or type(count) is not int or count < 0
        for module, count in counts.items()
    ):
        raise ValueError("invalid module occupancy")
    if len(counts) > module_universe_size:
        raise ValueError("module count exceeds fixed universe")
    total = sum(counts.values())
    if not total:
        return ModuleOccupancy("unavailable_empty_st", None, None, 0, 0)
    entropy = -sum(
        (n / total) * log(n / total) for n in counts.values() if n
    ) / log(module_universe_size)
    entropy = min(1.0, max(0.0, entropy))
    return ModuleOccupancy(
        "evaluated", entropy, entropy <= warning_fraction,
        total, sum(n > 0 for n in counts.values()),
    )
