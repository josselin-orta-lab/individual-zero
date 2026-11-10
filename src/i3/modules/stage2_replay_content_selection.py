"""Separate stream for opt-in Stage-2.1 random replay *memory identity*.

The frozen P1.3 default always takes largest absolute TD errors. This helper
does not alter the replay count, the individual's RNG or the costs of replay.
It ranks currently eligible memory slots with a life/ordinal-separated HMAC.
No World name, hidden state or outcome is consulted.
"""
from __future__ import annotations

from hashlib import sha256
import hmac

DOMAIN = b"i3-stage2.1-random-content-full-life/v1"


def random_content_indices(*, eligible: int, count: int, life_seed: int,
                           sleep_ordinal: int) -> tuple[int, ...]:
    for value in (eligible, count, life_seed, sleep_ordinal):
        if type(value) is not int or value < 0:
            raise ValueError("strict nonnegative memory, count, seed, ordinal required")
    if count > eligible or count > 16:
        raise ValueError("count exceeds eligible buffer or physical replay cap")
    # Recompute using a fresh fixed key, never the current Mind/global RNG.
    key = sha256(DOMAIN + b"|" + str(life_seed).encode("ascii")).digest()
    ordering = sorted(range(eligible), key=lambda i: (
        hmac.new(key, f"{sleep_ordinal}|{i}".encode("ascii"), sha256).digest(), i))
    return tuple(ordering[:count])
