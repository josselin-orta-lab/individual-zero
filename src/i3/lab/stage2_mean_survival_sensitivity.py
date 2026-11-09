"""Stage-2.1 population-mean survival sensitivity, software-only.

This is a conservative Hoeffding *scenario* calculation for independent,
bounded (-1..1) population contrasts. It cannot authenticate original
receipts, justify independence/exchangeability, approve margins, certify
power, or authorize any scientific World. It never imports the engine.
"""
from __future__ import annotations

from collections.abc import Mapping
from math import fsum, isfinite, log, sqrt

from . import stage0_design as F0

SCHEMA = "i3-stage2-1-mean-survival-sensitivity-v1"
STATUS = "ARITHMETIC_ONLY_NO_SCIENTIFIC_VERDICT"
DEFAULT_ALPHA = 0.05


def _probability(x, label):
    if type(x) not in (int, float) or not isfinite(x) or not 0 < x < 1:
        raise ValueError(f"{label} must be a finite probability strictly between 0 and 1")
    return float(x)


def mean_survival_lower_bound(deltas: Mapping[int, float], *,
                              alpha: float = DEFAULT_ALPHA) -> dict:
    """A one-sided independent-population bound, NOT an executable gate.

    Each number is a full-population GATE-on-GATE-selected minus
    FIXED-on-FIXED-selected survival proportion (each in [-1,1]).
    Hoeffding's inequality for independent bounded population contrasts:
      P(mu < observed_mean - sqrt(2 log(1/alpha) / n)) <= alpha.
    Population independence AND meaningful population sampling must be
    justified externally; reusing shared worlds can violate assumptions.
    This bound is deliberately not a confidence statement if assumptions fail.
    """
    a = _probability(alpha, "alpha")
    if not isinstance(deltas, Mapping) or set(deltas) != set(range(F0.POPULATIONS)) or any(
            type(p) is not int for p in deltas):
        raise ValueError("exactly eight independently identified populations required")
    values = list(deltas.values())
    if any(type(v) not in (int, float) or not isfinite(v) or not -1 <= v <= 1
           for v in values):
        raise ValueError("survival contrasts must be finite values in [-1,1]")
    n = len(values)
    observed_mean = fsum(values) / n
    radius = sqrt(2.0 * log(1.0 / a) / n)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "observed_population_mean": observed_mean,
        "radius": radius,
        "lower_bound": max(-1.0, observed_mean - radius),
        "alpha_one_sided": a,
        "populations": n,
        "assumptions": "INDEPENDENT_BOUNDED_POPULATION_CONTRASTS_NOT_ESTABLISHED",
        "mean_noninferiority_authorized": False,
        "scientific_worlds_authorized": False,
    }


def hypothetical_minimum_populations(precision: float, *,
                                      alpha: float = DEFAULT_ALPHA) -> int:
    """Necessary size for a target Hoeffding radius; NOT a power calculation.

    Uses conservative population contrast range [-1,+1], independent
    populations, and a prespecified one-sided confidence level. Large
    values are diagnostic of mismatch, never a replacement sampling plan.
    """
    from math import ceil

    p = _probability(precision, "precision")
    a = _probability(alpha, "alpha")
    return ceil(2 * log(1 / a) / (p * p))
