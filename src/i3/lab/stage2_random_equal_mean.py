"""Prospective Stage-2.1 RANDOM-EQUAL-MEAN count schedule, software only.

Pure arithmetic for a FUTURE causal control, never a World runner or Mind.
The GATE DEVELOPMENT 80/81 original pilot fixed 5532 / 867 before any
selection or validation exposure. This code schedules *attempts*, not paid
replays: eligibility, affordability, irreversible death and actual work must
still be enforced by a separately approved, source-locked runtime transport.

A counter-derived, domain-separated life-seeded stream avoids perturbing
P1.3's option/action/world RNGs and never needs a mutable global RNG.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256

SCHEMA = "i3-stage2-1-random-equal-mean-v1"
DOMAIN = b"i3/stage2.1/random-equal-mean/v1"
DEVELOPMENT_REPLAYS = 5532
DEVELOPMENT_SLEEP_STEPS = 867
TARGET_MEAN = Fraction(DEVELOPMENT_REPLAYS, DEVELOPMENT_SLEEP_STEPS)
LOW = TARGET_MEAN.numerator // TARGET_MEAN.denominator
HIGH = LOW + 1
HIGH_TICKETS = TARGET_MEAN.numerator % TARGET_MEAN.denominator
TICKETS = TARGET_MEAN.denominator
# The exact schedule is 6 (179/289) or 7 (110/289), not 6.38 rounded.
assert (LOW, HIGH, HIGH_TICKETS, TICKETS) == (6, 7, 110, 289)


def scheduled_replays(life_seed: int, sleep_ordinal: int) -> int:
    """Give the nominal 6-or-7 replay budget for a *reached* sleep step.

    sleep_ordinal is zero-based among actually executed sleep actions,
    not chronological world time; neither hidden world state nor future
    observations enter the control. One schedule value is used at most once
    per actual sleep step. Never redraw to replace an ineligible or unpaid
    replay. Same life seed and ordinal intentionally give common randomness.
    """
    if type(life_seed) is not int or life_seed < 0:
        raise ValueError("life_seed must be a nonnegative integer")
    if type(sleep_ordinal) is not int or sleep_ordinal < 0:
        raise ValueError("sleep_ordinal must be a nonnegative integer")
    prefix = (DOMAIN + b":" + str(life_seed).encode("ascii")
              + b":" + str(sleep_ordinal).encode("ascii") + b":")
    size = 1 << 256
    limit = size - size % TICKETS
    counter = 0
    while True:
        digest = sha256(prefix + str(counter).encode("ascii")).digest()
        value = int.from_bytes(digest, "big")
        if value < limit:  # rejection prevents the tiny modulus bias
            return HIGH if value % TICKETS < HIGH_TICKETS else LOW
        counter += 1
