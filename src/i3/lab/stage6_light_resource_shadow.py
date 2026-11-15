"""Strict source-only replay of *declared* I3 World resource effects.

No native World, Mind, motor or birth import. This reconstructs only the
physical consequence of an already-supplied list of actions and a supplied
WorldSpec snapshot. It cannot prove that the actions happened, their actor,
the timing/provenance of a source file, or any experimental authorization.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite

WORLD_FIELDS = frozenset({"name", "width", "height", "spawn", "body", "laws",
                          "water", "food", "token_effects", "changes"})
WATER_FIELDS = frozenset({"gain", "stock", "max_stock", "restock_every"})
FOOD_FIELDS = frozenset({"token", "quantity", "max_quantity", "restock_every"})
MOVES = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
ACTIONS = frozenset({None, "se_deplacer", "collecter", "manger", "boire",
                     "dormir", "attendre"})


def _integer(value, low=0, high=10_000_000) -> bool:
    return type(value) is int and low <= value <= high


def _number(value) -> bool:
    return type(value) in (float, int) and isfinite(value)


def _positive_name(value) -> bool:
    return type(value) is str and bool(value) and len(value) <= 200


def _coord(value, width, height) -> tuple[int, int]:
    if (type(value) is not list or len(value) != 2 or
            not _integer(value[0], 0, width - 1) or
            not _integer(value[1], 0, height - 1)):
        raise ValueError("invalid resource or movement position")
    return (value[0], value[1])


def _effect(value) -> tuple[float, float]:
    if type(value) is not list or len(value) != 2 or not all(_number(x) for x in value):
        raise ValueError("invalid token effect")
    return (value[0], value[1])


def _water_record(value) -> dict:
    if type(value) is not dict or set(value) != WATER_FIELDS:
        raise ValueError("incomplete water source")
    stock, maximum, period = (value[k] for k in ("stock", "max_stock", "restock_every"))
    if (not _number(value["gain"]) or
            (stock is not None and not _integer(stock)) or
            (maximum is not None and not _integer(maximum)) or
            not _integer(period) or (period and stock is not None and maximum is None)):
        raise ValueError("invalid water stock/restock contract")
    return dict(value)


def _food_record(value) -> dict:
    if type(value) is not dict or set(value) != FOOD_FIELDS:
        raise ValueError("incomplete food patch")
    if (not _positive_name(value["token"]) or not _integer(value["quantity"]) or
            not _integer(value["max_quantity"]) or not _integer(value["restock_every"])):
        raise ValueError("invalid food patch state")
    return dict(value)


def initialize(snapshot: dict) -> dict:
    """Construct a detached dict state from the exact serialized WorldSpec shape."""
    if (type(snapshot) is not dict or set(snapshot) != WORLD_FIELDS or
            not _positive_name(snapshot["name"]) or
            not _integer(snapshot["width"], 1, 1000) or
            not _integer(snapshot["height"], 1, 1000) or
            type(snapshot["water"]) is not list or
            type(snapshot["food"]) is not list or
            type(snapshot["token_effects"]) is not list or
            type(snapshot["changes"]) is not list):
        raise ValueError("incomplete or unsafe supplied WorldSpec")
    width, height = snapshot["width"], snapshot["height"]
    pos = _coord(snapshot["spawn"], width, height)
    water, food, effects = {}, {}, {}
    for entry in snapshot["water"]:
        if type(entry) is not list or len(entry) != 2:
            raise ValueError("invalid water source entry")
        key = _coord(entry[0], width, height)
        if key in water:
            raise ValueError("duplicate water source")
        water[key] = _water_record(entry[1])
    for entry in snapshot["food"]:
        if type(entry) is not list or len(entry) != 2:
            raise ValueError("invalid food source entry")
        key = _coord(entry[0], width, height)
        if key in food:
            raise ValueError("duplicate food patch")
        food[key] = _food_record(entry[1])
    for entry in snapshot["token_effects"]:
        if type(entry) is not list or len(entry) != 2 or not _positive_name(entry[0]):
            raise ValueError("invalid token effect entry")
        if entry[0] in effects:
            raise ValueError("duplicate effect token")
        effects[entry[0]] = _effect(entry[1])
    changes = []
    for event in snapshot["changes"]:
        if type(event) is not list or len(event) != 4 or not _integer(event[0], 1, 400):
            raise ValueError("invalid timed world change")
        tick, kind, key, value = event
        if kind == "token_effect":
            if not _positive_name(key):
                raise ValueError("invalid timed token")
            validated = (tick, kind, key, _effect(value))
        elif kind in ("water_gain", "water_stock", "food_quantity"):
            key = _coord(key, width, height)
            if kind.startswith("water") and key not in water or kind == "food_quantity" and key not in food:
                raise ValueError("timed update targets absent source")
            if kind == "water_gain":
                if not _number(value):
                    raise ValueError("invalid scheduled water gain")
            elif not _integer(value):
                raise ValueError("invalid scheduled stock/quantity")
            validated = (tick, kind, key, value)
        else:
            raise ValueError("unknown native world change")
        changes.append(validated)
    return {"name": snapshot["name"], "width": width, "height": height,
            "pos": pos, "water": water, "food": food, "effects": effects,
            "changes": tuple(changes), "inventory": {}, "t": 0}


def _apply(state: dict, action: str | None, param: object, tick: int) -> dict:
    """Mirror World._step resource/motor state order, not its cognitive physics."""
    if not _integer(tick, 1, 400) or tick != state["t"] + 1:
        raise ValueError("out-of-order declared physical step")
    if action not in ACTIONS:
        raise ValueError("unknown native motor action")
    if action in (None, "attendre", "dormir", "boire") and param is not None:
        raise ValueError("command forbids parameter")
    pos = state["pos"]
    food_gain = integrity_delta = water_gain = 0.0
    if action == "se_deplacer":
        if type(param) is not str or param not in MOVES:
            raise ValueError("invalid cardinal movement")
        dx, dy = MOVES[param]
        nxt = (pos[0] + dx, pos[1] + dy)
        if not (0 <= nxt[0] < state["width"] and 0 <= nxt[1] < state["height"]):
            raise ValueError("unavailable adjacent cell")
        pos = nxt
        state["pos"] = pos
    elif action == "collecter":
        patch = state["food"].get(pos)
        if patch is None or type(param) is not str or patch["token"] != param or patch["quantity"] <= 0:
            raise ValueError("no available token to collect")
        patch["quantity"] -= 1
        state["inventory"][param] = state["inventory"].get(param, 0) + 1
    elif action == "manger":
        if type(param) is not str or state["inventory"].get(param, 0) <= 0 or param not in state["effects"]:
            raise ValueError("cannot consume unowned/unknown token")
        state["inventory"][param] -= 1
        food_gain, integrity_delta = state["effects"][param]
    elif action == "boire":
        source = state["water"].get(pos)
        if source is None or (source["stock"] is not None and source["stock"] <= 0):
            raise ValueError("no available water source")
        if source["stock"] is not None:
            source["stock"] -= 1
        water_gain = source["gain"]
    # World._step: resource effect for this tick precedes automatic restock,
    # then scheduled changes apply only to the NEXT capture/action.
    for source in state["water"].values():
        if source["restock_every"] and tick % source["restock_every"] == 0 and source["stock"] is not None:
            source["stock"] = min(source["max_stock"], source["stock"] + 1)
    for patch in state["food"].values():
        if patch["restock_every"] and tick % patch["restock_every"] == 0:
            patch["quantity"] = min(patch["max_quantity"], patch["quantity"] + 1)
    for scheduled_tick, kind, key, value in state["changes"]:
        if tick != scheduled_tick:
            continue
        if kind == "token_effect":
            state["effects"][key] = value
        elif kind == "water_gain":
            state["water"][key]["gain"] = float(value)
        elif kind == "water_stock":
            state["water"][key]["stock"] = value
        elif kind == "food_quantity":
            state["food"][key]["quantity"] = value
    state["t"] = tick
    return {"pos": list(pos), "food_gain": food_gain,
            "integrity_delta": integrity_delta, "water_gain": water_gain}


def declared_step(state: dict, action: str | None, param: object, tick: int) -> dict:
    """Transactional replay: invalid inputs do not change the caller's state."""
    candidate = deepcopy(state)
    result = _apply(candidate, action, param, tick)
    state.clear()
    state.update(candidate)
    return result


def open_world(*_args, **_kwargs) -> None:
    raise PermissionError("read-only resource reconstruction cannot open a World")


def run_life(*_args, **_kwargs) -> None:
    raise PermissionError("read-only resource reconstruction cannot run a life")


def authorize_science(*_args, **_kwargs) -> None:
    raise PermissionError("read-only resource reconstruction cannot issue authority")
