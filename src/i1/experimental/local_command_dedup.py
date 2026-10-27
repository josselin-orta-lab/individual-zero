"""Inactive, read-only de-duplication of personally available local commands (#340).

This is not a producer, a Competition admission, or a UC/Q decision.
"""
from __future__ import annotations

from math import isfinite


def _freeze(value, *, depth=0, remaining=None):
    """Canonical, bounded, type-preserving signature (not Python == semantics)."""
    if remaining is None:
        remaining = [2048]
    remaining[0] -= 1
    if remaining[0] < 0 or depth > 16:
        raise ValueError("unbounded command parameter tree")
    kind = type(value)
    if kind is type(None):
        return ("none",)
    if kind is bool:
        return ("bool", value)
    if kind is int:
        return ("int", value)
    if kind is float:
        if not isfinite(value):
            raise ValueError("nonfinite command parameter")
        return ("float", value)
    if kind is str:
        if len(value) > 8192:
            raise ValueError("unbounded command parameter string")
        return ("str", value)
    if kind in (tuple, list):
        if len(value) > 256:
            raise ValueError("unbounded command parameter sequence")
        return (kind.__name__, tuple(
            _freeze(item, depth=depth + 1, remaining=remaining)
            for item in value
        ))
    if kind is dict:
        if len(value) > 256 or any(type(key) is not str for key in value):
            raise ValueError("invalid command parameter mapping")
        return ("dict", tuple(
            (key, _freeze(value[key], depth=depth + 1, remaining=remaining))
            for key in sorted(value)
        ))
    raise ValueError("unsupported or untrusted command parameter")


def _key(command):
    primitive = getattr(command, "primitive", None)
    parameters = getattr(command, "parameters", None)
    if type(primitive) is not str or not primitive or type(parameters) is not dict:
        raise ValueError("invalid perceived command")
    return primitive, _freeze(parameters)


def distinct_local_commands(available, existing, *, now_step):
    """Retain only distinct commands, including across valid registered plans.

    Inputs must already originate from authorised Planning and Competition.
    This function neither senses the world nor registers options or charges UC.
    All inputs and their order are preserved; malformed inputs fail closed.
    """
    if (type(available) is not tuple or type(existing) is not tuple
            or len(available) > 128 or len(existing) > 128
            or type(now_step) is not int or now_step < 1):
        raise ValueError("invalid bounded candidate context")
    seen = set()
    for proposal in existing:
        option = getattr(proposal, "option", None)
        expiry = getattr(option, "expires_at_step", None)
        if type(expiry) is not int or expiry < 1:
            raise ValueError("invalid registered option expiry")
        if expiry <= now_step:
            continue
        plan = getattr(proposal, "plan", None)
        if plan is None:
            continue
        steps = getattr(plan, "steps", None)
        if type(steps) is not tuple or not 1 <= len(steps) <= 128:
            raise ValueError("invalid registered plan")
        # The first command of a longer plan also occupies the local option.
        seen.add(_key(getattr(steps[0], "command", None)))
    result = []
    for command in available:
        key = _key(command)
        if key not in seen:
            seen.add(key)
            result.append(command)
    return tuple(result)
