"""I3 body: five internal channels, one vital currency, vulnerable capacities.

Physics provenance (RAI: ADAPT, no import): the four-channel transition is
copied from ``src/i2/modules/native_body_contract.py::transition`` at commit
f9ca3f4, itself a mirror of I1 natural physiology v4. Adaptations: a fifth
channel (vigilance), cognitive work charged to energy and vigilance, plain
tuples instead of dataclasses for speed. Coefficients here are WORLD LAWS,
never genome genes (ADR-0014, decision 2).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from math import isfinite

CHANNELS = ("energy", "food", "water", "integrity", "vigilance")
E, F, W, I, V = range(5)
VITAL = (F, W, I)  # a vital channel at zero is irreversible death
ACTIONS = ("se_deplacer", "collecter", "manger", "boire", "dormir", "attendre")
ACTION_COSTS = {  # energy per admitted action, I2/I1-v4 values
    "se_deplacer": 2.0, "collecter": 1.0, "manger": 0.5,
    "boire": 0.5, "dormir": 0.25, "attendre": 0.35,
}


@dataclass(frozen=True, slots=True)
class BodyLaws:
    """World laws of the body. Frozen per world; reported in every result."""
    food_decay: float = 0.2
    water_decay: float = 0.4
    sleep_energy_gain: float = 3.0
    sleep_food_cost_per_energy: float = 0.05
    rest_integrity_gain: float = 0.2
    rest_food_cost_per_integrity: float = 0.10
    min_water_for_metabolism: float = 0.05
    # Vital currency: cognition is paid in energy (ADR-0014, decision 2).
    energy_per_cycle: float = 0.02
    energy_per_simulated_step: float = 0.002
    energy_per_memory_item: float = 0.0002
    energy_per_replay: float = 0.005
    # Vigilance: worn by cognitive work, restored only by sleep.
    vigilance_per_cycle: float = 0.05
    vigilance_per_simulated_step: float = 0.002
    vigilance_per_replay: float = 0.01
    sleep_vigilance_gain: float = 4.0
    version: str = "i3-body-laws-v1"

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CognitiveWork:
    """What the mind actually spent during one step, charged by the world."""
    cycles: int = 0
    simulated_steps: int = 0
    memory_items: int = 0
    replays: int = 0

    def __post_init__(self):
        for name in ("cycles", "simulated_steps", "memory_items", "replays"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")


def cognitive_cost(laws: BodyLaws, work: CognitiveWork) -> tuple[float, float]:
    """The declared energy/vigilance bill, not a compute-budget allocator."""
    if not isinstance(work, CognitiveWork):
        raise TypeError("CognitiveWork required")
    rates = (laws.energy_per_cycle, laws.energy_per_simulated_step,
             laws.energy_per_memory_item, laws.energy_per_replay,
             laws.vigilance_per_cycle, laws.vigilance_per_simulated_step,
             laws.vigilance_per_replay)
    if any(not isfinite(rate) or rate < 0 for rate in rates):
        raise ValueError("cognitive cost rates must be finite and nonnegative")
    try:
        energy = (rates[0] * work.cycles + rates[1] * work.simulated_steps
                  + rates[2] * work.memory_items + rates[3] * work.replays)
        vigilance = (rates[4] * work.cycles + rates[5] * work.simulated_steps
                     + rates[6] * work.replays)
    except OverflowError as exc:
        raise ValueError("cognitive bill is not finite") from exc
    if not isfinite(energy) or not isfinite(vigilance):
        raise ValueError("cognitive bill is not finite")
    return energy, vigilance


def _clamp(x: float) -> float:
    return 0.0 if x < 0.0 else 100.0 if x > 100.0 else x


def validate_body(body) -> tuple:
    if type(body) not in (tuple, list) or len(body) != 5:
        raise ValueError("five body channels required")
    body = tuple(float(x) for x in body)
    if any(not isfinite(x) or not 0.0 <= x <= 100.0 for x in body):
        raise ValueError("body channels must be finite in [0,100]")
    return body


def transition(body: tuple, action: str, laws: BodyLaws, work: CognitiveWork, *,
               food_gain: float = 0.0, integrity_delta: float = 0.0,
               water_gain: float = 0.0,
               accounting: dict | None = None) -> tuple[tuple, tuple[str, ...]]:
    """Pure one-step body physics after an admitted action.

    Returns (next_body, death_reasons). Same ordering as I2/I1-v4: decay,
    sleep or action cost, rest repair, then consumption. Cognitive work is
    charged after the action, from the same energy reserve.
    """
    if action not in ACTION_COSTS:
        raise ValueError("unknown physical action")
    if action != "manger" and (food_gain or integrity_delta):
        raise ValueError("food consequence only follows an applied eat")
    if action != "boire" and water_gain:
        raise ValueError("water consequence only follows an applied drink")
    cost_energy, cost_vigilance = cognitive_cost(laws, work)
    energy, food, water, integrity, vigilance = body
    food = _clamp(food - laws.food_decay)
    water = _clamp(water - laws.water_decay)
    hydrated = water >= laws.min_water_for_metabolism
    if action == "dormir":
        possible = min(laws.sleep_energy_gain, max(0.0, 100.0 - energy))
        gained = min(possible, food / laws.sleep_food_cost_per_energy) if hydrated else 0.0
        energy += gained
        food -= gained * laws.sleep_food_cost_per_energy
        vigilance += laws.sleep_vigilance_gain
    else:
        energy -= ACTION_COSTS[action]
    if action in ("attendre", "dormir") and hydrated:
        repair = min(laws.rest_integrity_gain, max(0.0, 100.0 - integrity),
                     food / laws.rest_food_cost_per_integrity)
        integrity += repair
        food -= repair * laws.rest_food_cost_per_integrity
    if action == "manger":
        food += food_gain
        integrity += integrity_delta
    elif action == "boire":
        water += water_gain
    if accounting is not None:
        # Observe the existing v1 debit order without hiding saturation at zero.
        # This is not an overdraft policy or evidence that all work was paid.
        accounting.clear()
        for name, available, requested in (("energy", energy, cost_energy),
                                            ("vigilance", vigilance, cost_vigilance)):
            paid = min(max(0.0, available), requested)
            accounting[name] = {"requested": requested, "paid": paid,
                                "unpaid": requested - paid}
    energy -= cost_energy
    vigilance -= cost_vigilance
    nxt = (_clamp(energy), _clamp(food), _clamp(water), _clamp(integrity),
           _clamp(vigilance))
    reasons = tuple(name for name, idx in (("zero_food", F), ("zero_water", W),
                                           ("zero_integrity", I)) if nxt[idx] <= 0.0)
    return nxt, reasons


def capacities(body: tuple, n_base: float, h_max: float) -> tuple[int, int, float]:
    """Vulnerable capacities: (deliberation cycles, simulation horizon, perception miss).

    Low energy -> fewer cycles; low vigilance -> shorter simulation;
    low integrity -> noisier perception. Forms are spec v1 proposals.
    """
    cycles = max(1, int(round(n_base * min(1.0, body[E] / 50.0))))
    horizon = max(1, int(round(h_max * min(1.0, body[V] / 60.0))))
    miss = 0.2 * (1.0 - body[I] / 100.0)
    return cycles, horizon, miss
