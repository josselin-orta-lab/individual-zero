"""I3 genome: generic innate parameters only (ADR-0014, decisions 4 and 6).

Every gene is indexed by an internal channel or is a scalar cognitive
parameter. No field may name a world object, place, position, action
preference, learned value, memory or map. ``validate`` refuses any other
field; renaming invariance is additionally tested dynamically.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite
import random

from .body import CHANNELS

SCHEMA = "i3-genome-v4"
HISTORICAL_V3_SCHEMA = "i3-genome-v3"

# (name, low, high) per gene. Per-channel genes are expanded to 5 entries.
PER_CHANNEL = {
    "theta": (30.0, 90.0),    # distress threshold
    "p": (1.0, 3.0),          # distress convexity
    "w": (0.2, 2.0),          # distress weight
}
SCALARS = {
    "gamma1": (0.60, 0.90),
    "gamma2": (0.90, 0.98),
    "gamma3": (0.98, 0.998),
    "alpha": (0.01, 0.20),     # value learning rate
    "beta_u": (0.0, 2.0),      # exploration weight of uncertainty
    "lambda_r": (0.0, 1.0),    # prudence toward uncertain effects
    "n_base": (2.0, 8.0),      # base deliberation cycles
    "h_max": (4.0, 24.0),      # maximal simulation horizon
    "m_max": (32.0, 512.0),    # memory capacity (transitions)
    "belief_rate": (0.02, 0.5),  # speed of revising place beliefs (P1.3)
}
TEMPERAMENT = ("reward_sensitivity", "threat_sensitivity", "exploration",
               "goal_protection", "affiliation")
TEMPERAMENT_RANGE = (-1.0, 1.0)
OMEGA_RANGE = (-1.0, 1.0)


def gene_bounds() -> dict[str, tuple[float, float]]:
    bounds = {}
    for name, rng in PER_CHANNEL.items():
        for ch in CHANNELS:
            bounds[f"{name}.{ch}"] = rng
    bounds.update(SCALARS)
    for t in TEMPERAMENT:
        bounds[f"temperament.{t}"] = TEMPERAMENT_RANGE
    # Added genes come last: generation-0 draws of earlier genes are unchanged
    # across schema additions (ADR-0015). belief_rate was the v3 addition;
    # omega is the sole v4 addition and therefore follows every v3 gene.
    bounds["belief_rate"] = bounds.pop("belief_rate")
    bounds["omega"] = OMEGA_RANGE
    return bounds


BOUNDS = gene_bounds()
GENE_ORDER = tuple(BOUNDS)

# Read-only historical contract used only to verify/reconstruct archived P3-P5
# evidence. It is deliberately separate from current validate(): a v3 genome
# cannot enter current Mind/runtime through this compatibility boundary.
HISTORICAL_V3_GENE_ORDER = GENE_ORDER[:-1]
HISTORICAL_V3_BOUNDS = {
    key: BOUNDS[key] for key in HISTORICAL_V3_GENE_ORDER
}


def _validate_mapping(genome: dict, *, schema: str, order, bounds,
                      label: str) -> dict:
    if type(genome) is not dict or genome.get("schema") != schema:
        raise ValueError(f"exact {label} mapping required")
    genes = genome.get("genes")
    if type(genes) is not dict or tuple(sorted(genes)) != tuple(sorted(order)):
        raise ValueError("genome must contain exactly the declared generic genes")
    for name, (lo, hi) in bounds.items():
        v = genes[name]
        if type(v) not in (int, float) or not isfinite(v) or not lo <= v <= hi:
            raise ValueError(f"gene {name} outside its declared bounds")
    extra = set(genome) - {"schema", "genes"}
    if extra:
        raise ValueError("no field other than schema and genes may be inherited")
    if not genes["gamma1"] <= genes["gamma2"] <= genes["gamma3"]:
        raise ValueError("value horizons must be ordered")
    return genome


def validate(genome: dict) -> dict:
    """Current static admissibility. Historical schemas fail closed."""
    return _validate_mapping(
        genome, schema=SCHEMA, order=GENE_ORDER, bounds=BOUNDS,
        label="i3-genome-v4")


def validate_historical_v3(genome: dict) -> dict:
    """Read-only custody validation for immutable v3 scientific evidence.

    This function does not migrate, fill or return a v4 genome. Current Mind
    and runtime continue to call validate(), which rejects v3.
    """
    return _validate_mapping(
        genome, schema=HISTORICAL_V3_SCHEMA,
        order=HISTORICAL_V3_GENE_ORDER,
        bounds=HISTORICAL_V3_BOUNDS,
        label="historical i3-genome-v3")


def _make_for_schema(genes: dict, *, schema: str, order, bounds,
                     validator) -> dict:
    g = {
        "schema": schema,
        "genes": {k: round(float(genes[k]), 6) for k in order},
    }
    g["genes"]["gamma1"], g["genes"]["gamma2"], g["genes"]["gamma3"] = sorted(
        (g["genes"]["gamma1"], g["genes"]["gamma2"], g["genes"]["gamma3"]))
    for k in ("gamma1", "gamma2", "gamma3"):
        lo, hi = bounds[k]
        g["genes"][k] = min(hi, max(lo, g["genes"][k]))
    return validator(g)


def _make(genes: dict) -> dict:
    return _make_for_schema(
        genes, schema=SCHEMA, order=GENE_ORDER, bounds=BOUNDS,
        validator=validate)


def _make_historical_v3(genes: dict) -> dict:
    return _make_for_schema(
        genes, schema=HISTORICAL_V3_SCHEMA,
        order=HISTORICAL_V3_GENE_ORDER,
        bounds=HISTORICAL_V3_BOUNDS,
        validator=validate_historical_v3)


def generation_zero(seed: int) -> dict:
    """Declared broad distribution: independent uniform draws in bounds."""
    rng = random.Random(f"i3-genome-g0:{seed}")
    return _make({k: rng.uniform(lo, hi) for k, (lo, hi) in BOUNDS.items()})


def midpoint() -> dict:
    """Reference genome at the centre of every range (a control, not a choice)."""
    return _make({k: (lo + hi) / 2 for k, (lo, hi) in BOUNDS.items()})


def historical_v3_generation_zero(seed: int) -> dict:
    """Reconstruct an archived v3 G0 without creating a current genome."""
    rng = random.Random(f"i3-genome-g0:{seed}")
    return _make_historical_v3({
        k: rng.uniform(lo, hi)
        for k, (lo, hi) in HISTORICAL_V3_BOUNDS.items()
    })


def canonical_historical_v3(genome: dict) -> str:
    validate_historical_v3(genome)
    return json.dumps(genome, sort_keys=True, separators=(",", ":"))


def digest_historical_v3(genome: dict) -> str:
    return sha256(canonical_historical_v3(genome).encode("ascii")).hexdigest()


def historical_v3_mutate(
        genome: dict, seed: int, scale: float = 0.1) -> dict:
    """Reconstruct archived v3 mutation with its original parent digest."""
    validate_historical_v3(genome)
    rng = random.Random(
        f"i3-mutation:{digest_historical_v3(genome)}:{seed}")
    out = {}
    for k, (lo, hi) in HISTORICAL_V3_BOUNDS.items():
        v = (
            genome["genes"][k]
            + rng.gauss(0.0, scale * (hi - lo)))
        out[k] = min(hi, max(lo, v))
    return _make_historical_v3(out)


def mutate(genome: dict, seed: int, scale: float = 0.1) -> dict:
    """Bounded Gaussian mutation of every gene, sigma = scale x range."""
    validate(genome)
    rng = random.Random(f"i3-mutation:{digest(genome)}:{seed}")
    out = {}
    for k, (lo, hi) in BOUNDS.items():
        v = genome["genes"][k] + rng.gauss(0.0, scale * (hi - lo))
        out[k] = min(hi, max(lo, v))
    return _make(out)


def canonical(genome: dict) -> str:
    validate(genome)
    return json.dumps(genome, sort_keys=True, separators=(",", ":"))


def digest(genome: dict) -> str:
    return sha256(canonical(genome).encode("ascii")).hexdigest()


def channel_vector(genome: dict, name: str) -> tuple[float, ...]:
    return tuple(genome["genes"][f"{name}.{ch}"] for ch in CHANNELS)
