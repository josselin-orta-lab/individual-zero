"""I3 world: a separate owner of positions, stocks and hidden effects.

The individual never reads this object. It receives only ``capture()``:
its own body, its own inventory and the contents of its cell and of the
four adjacent cells. Hidden token effects and scheduled changes stay here
(ADR-0014: first-person perception, no oracle).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from copy import copy

from .body import (ACTION_COSTS, BodyLaws, CognitiveWork, cognitive_cost,
                   debit_cognition, transition, validate_body, validate_laws)

DIRECTIONS = (("N", 0, -1), ("E", 1, 0), ("S", 0, 1), ("W", -1, 0))
DELTA = {name: (dx, dy) for name, dx, dy in DIRECTIONS}


@dataclass
class WaterSource:
    gain: float
    stock: int | None = None        # None = unlimited
    max_stock: int | None = None
    restock_every: int = 0


@dataclass
class FoodPatch:
    token: str
    quantity: int
    max_quantity: int
    restock_every: int = 0


@dataclass
class WorldSpec:
    """Everything the laboratory fixes before birth. Never shown to the mind."""
    name: str
    width: int
    height: int
    spawn: tuple[int, int]
    body: tuple
    water: dict = field(default_factory=dict)        # (x, y) -> WaterSource
    food: dict = field(default_factory=dict)         # (x, y) -> FoodPatch
    token_effects: dict = field(default_factory=dict)  # token -> (food_gain, integrity_delta)
    changes: tuple = ()  # (step, kind, key, value), applied at step start
    laws: BodyLaws = BodyLaws()


class World:
    def __init__(self, spec: WorldSpec):
        self.spec = spec
        self.laws = spec.laws
        validate_laws(self.laws)
        self.t = 0
        self.pos = tuple(spec.spawn)
        self.body = validate_body(spec.body)
        self.inventory: dict[str, int] = {}
        self.water = {p: WaterSource(s.gain, s.stock, s.max_stock, s.restock_every)
                      for p, s in spec.water.items()}
        self.food = {p: FoodPatch(f.token, f.quantity, f.max_quantity, f.restock_every)
                     for p, f in spec.food.items()}
        self.effects = dict(spec.token_effects)
        self.dead = tuple(name for name, idx in (("zero_food", 1), ("zero_water", 2),
                                                  ("zero_integrity", 3))
                          if self.body[idx] <= 0.0)
        if not (0 <= self.pos[0] < spec.width and 0 <= self.pos[1] < spec.height):
            raise ValueError("spawn outside the world")

    # ---- first-person capture -------------------------------------------------
    def _cell(self, p):
        if not (0 <= p[0] < self.spec.width and 0 <= p[1] < self.spec.height):
            return None
        src = self.water.get(p)
        water = src is not None and (src.stock is None or src.stock > 0)
        patch = self.food.get(p)
        tokens = (patch.token,) if patch is not None and patch.quantity > 0 else ()
        return (water, tokens)

    def capture(self) -> dict:
        x, y = self.pos
        return {
            "body": self.body,
            "inventory": tuple(sorted((k, v) for k, v in self.inventory.items() if v > 0)),
            "here": self._cell(self.pos),
            "neighbors": tuple(self._cell((x + dx, y + dy)) for _, dx, dy in DIRECTIONS),
        }

    # ---- physics ----------------------------------------------------------------
    def _apply_changes(self):
        for step, kind, key, value in self.spec.changes:
            if step != self.t:
                continue
            if kind == "token_effect":
                self.effects[key] = tuple(value)
            elif kind == "water_gain":
                self.water[key].gain = float(value)
            elif kind == "water_stock":
                self.water[key].stock = int(value)
            elif kind == "food_quantity":
                self.food[key].quantity = int(value)
            else:
                raise ValueError("unknown scheduled world change")

    def _restock(self):
        for src in self.water.values():
            if src.restock_every and self.t % src.restock_every == 0 and src.stock is not None:
                src.stock = min(src.max_stock, src.stock + 1)
        for patch in self.food.values():
            if patch.restock_every and self.t % patch.restock_every == 0:
                patch.quantity = min(patch.max_quantity, patch.quantity + 1)

    def step(self, action: str | None, param, work: CognitiveWork) -> dict:
        """Transactionally apply funded computation, one motor effect and time.

        Invalid commands, changed resource availability and unfunded bills do
        not partially advance time, apply scheduled events or consume stock.
        A null command advances passive physiology without sleep or repair.
        """
        if self.dead:
            raise RuntimeError("death is irreversible: no action after death")
        cognitive_cost(self.laws, work)
        staged = copy(self)
        staged.inventory = dict(self.inventory)
        staged.water = {p: copy(v) for p, v in self.water.items()}
        staged.food = {p: copy(v) for p, v in self.food.items()}
        staged.effects = dict(self.effects)
        result = staged._step(action, param, work)
        self.__dict__.update(staged.__dict__)
        return result

    def pay_cognition(self, work: CognitiveWork) -> dict:
        """Pay outcome learning/replay now, before computation, without a new tick."""
        if self.dead:
            raise RuntimeError("no cognition after death")
        body, audit = debit_cognition(self.body, self.laws, work)
        self.body = body
        return audit

    def _step(self, action: str | None, param, work: CognitiveWork) -> dict:
        if self.dead:
            raise RuntimeError("death is irreversible: no action after death")
        funded, _ = debit_cognition(self.body, self.laws, work)
        if action not in (None, "dormir") and (action not in ACTION_COSTS or funded[0] < ACTION_COSTS[action]):
            raise ValueError("unfunded or unknown motor command")
        if action in (None, "attendre", "dormir", "boire") and param is not None:
            raise ValueError("this motor command takes no parameter")
        # Resolve the command against the state actually perceived before this
        # tick. Exogenous changes occur after action/metabolism and are first
        # observable at the following capture; they must not invalidate a
        # previously admissible command between perception and execution.
        self.t += 1
        kw = {}
        moved = False
        if action == "se_deplacer":
            dx, dy = DELTA[param]
            nxt = (self.pos[0] + dx, self.pos[1] + dy)
            if self._cell(nxt) is None or self.body[0] < ACTION_COSTS[action]:
                raise ValueError("inadmissible move reached the world")
            self.pos, moved = nxt, True
        elif action == "collecter":
            patch = self.food.get(self.pos)
            if patch is None or patch.token != param or patch.quantity <= 0:
                raise ValueError("nothing to collect here")
            patch.quantity -= 1
            self.inventory[param] = self.inventory.get(param, 0) + 1
        elif action == "manger":
            if self.inventory.get(param, 0) <= 0:
                raise ValueError("cannot eat what is not carried")
            self.inventory[param] -= 1
            kw["food_gain"], kw["integrity_delta"] = self.effects[param]
        elif action == "boire":
            src = self.water.get(self.pos)
            if src is None or (src.stock is not None and src.stock <= 0):
                raise ValueError("no water here")
            if src.stock is not None:
                src.stock -= 1
            kw["water_gain"] = src.gain
        elif action not in (None, "dormir", "attendre"):
            raise ValueError("unknown action")
        accounting = {}
        self.body, reasons = transition(self.body, action, self.laws, work,
                                        accounting=accounting, **kw)
        self._restock()
        self._apply_changes()  # environment evolves after the action, before next capture
        self.dead = reasons
        return {"t": self.t, "body": self.body, "moved": moved, "dead": reasons,
                "cognitive_accounting": accounting}
