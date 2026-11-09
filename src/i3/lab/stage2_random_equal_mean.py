"""Compatibility import for Stage-2.1 count-design arithmetic.

The runtime-owned implementation is i3.modules.stage2_random_equal_mean;
no active Mind imports a laboratory helper.
"""
from ..modules.stage2_random_equal_mean import (
    SCHEMA, DOMAIN, DEVELOPMENT_REPLAYS, DEVELOPMENT_SLEEP_STEPS,
    TARGET_MEAN, LOW, HIGH, HIGH_TICKETS, TICKETS, scheduled_replays,
)
