"""ADR-0017 engineering cohort: worlds for sealed rehearsals, never evidence.

The worlds come from the unchanged P2 ecology generator, on a seed range
disjoint from every P2 cohort and from the excluded historical G2e ranges.

`p2_ecologies.py` itself is not edited: its blob is pinned by the frozen
Stage-0 design (`stage0_design.ECOLOGY_BLOB`). This module therefore declares
the cohort beside it instead of inside `p2_ecologies.COHORTS`. That is a
declared deviation from the letter of ADR-0017 decision 3.2, not from its
intent.

No scientific runner may accept an engineering seed; use `assert_not_engineering`.
"""
from __future__ import annotations

from . import p2_ecologies as P2

ENGINEERING = range(90_000, 91_000)
HISTORICAL_EXCLUDED = (range(100, 130), range(1_000_200, 1_000_300))


def _check_disjoint() -> None:
    for name, cohort in P2.COHORTS.items():
        if not (ENGINEERING.stop <= cohort.start or cohort.stop <= ENGINEERING.start):
            raise RuntimeError(f"engineering cohort overlaps P2 cohort {name}")
    for old in HISTORICAL_EXCLUDED:
        if not (ENGINEERING.stop <= old.start or old.stop <= ENGINEERING.start):
            raise RuntimeError("engineering cohort overlaps an excluded historical range")


_check_disjoint()


def engineering_world(family: str, index: int):
    """An engineering World, from the unchanged generator. Never evidence."""
    if family not in P2.FAMILIES:
        raise ValueError("unknown P2 ecological family")
    if type(index) is not int or not 0 <= index < len(ENGINEERING):
        raise ValueError("engineering index outside its declared range")
    return P2._generate_ecology(family, ENGINEERING[index])


def is_engineering_seed(seed: int) -> bool:
    return type(seed) is int and seed in ENGINEERING


def assert_not_engineering(seed: int) -> None:
    """Scientific runners call this on every world seed they open."""
    if is_engineering_seed(seed):
        raise PermissionError("engineering-cohort worlds are never admissible as evidence")
