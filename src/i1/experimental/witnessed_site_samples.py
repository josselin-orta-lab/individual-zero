"""Inactive, read-only samples from the current mortal I1 water owner.

Evidence already admitted by that owner is exposed without max, average,
reward, route prediction, or new mutable state (issue #341).
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .lived_water import I1LivedWaterOwner


@dataclass(frozen=True, slots=True)
class SiteSample:
    position: tuple[int, int]
    sent_step: int
    observed_step: int
    observed_gain: float
    command_hash: str
    option_ref: str
    first_capture_hash: str
    followup_capture_hash: str


def site_samples(owner, *, life_id, site, now_step):
    """Return ALL admitted witnessed gains, never derive a site's utility.

    Owner admission is trusted, but this read verifies identity, chronology,
    capture references and the exact published record shape. Hash presence is
    NOT an independent cryptographic verification of the underlying WAL.
    """
    if (type(owner) is not I1LivedWaterOwner
            or type(life_id) is not str or not life_id.startswith("i1:")
            or owner.life_id != life_id or owner.enabled is not True
            or type(site) is not tuple or len(site) != 2
            or any(type(x) is not int for x in site)
            or type(now_step) is not int or now_step < 1):
        raise ValueError("invalid witness owner, identity or site")
    records = owner.examples
    if type(records) is not tuple or len(records) > 10000:
        raise ValueError("invalid witnessed records")
    required = {
        "source_position", "sent_world_step", "observed_world_step",
        "delta_water", "command_hash", "option_ref",
        "first_capture_hash", "followup_capture_hash",
    }
    result = []
    previous_step = 0
    for row in records:
        if type(row) is not dict or set(row) != required:
            raise ValueError("unattested evidence shape")
        sent, observed = row["sent_world_step"], row["observed_world_step"]
        loc, gain = row["source_position"], row["delta_water"]
        references = (
            row["command_hash"], row["option_ref"],
            row["first_capture_hash"], row["followup_capture_hash"],
        )
        if (type(sent) is not int or type(observed) is not int
                or sent <= previous_step or observed != sent + 1
                or observed > now_step
                or type(loc) is not list or len(loc) != 2
                or any(type(x) is not int for x in loc)
                or type(gain) not in (int, float) or not isfinite(gain)
                or not 0 < gain <= 100
                or any(type(x) is not str or not x for x in references)
                or references[2] == references[3]):
            raise ValueError("unattested, contradictory or future sample")
        previous_step = sent
        if tuple(loc) == site:
            result.append(SiteSample(
                tuple(loc), sent, observed, float(gain), *references
            ))
    return tuple(result)
