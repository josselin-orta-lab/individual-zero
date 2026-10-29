"""Preregistered A1-only M11 birth pairing; never a cognitive/runtime option.

Select the same *innate temperament source* for independently born mortal I1
lives. This operator-side scope touches only the existing single birth
projection site, then immediately restores it. No owner state, memory, Q,
action, world physics, UC, or lifetime runtime method is patched.
"""
from contextlib import contextmanager
from unittest.mock import patch

_WORLD = "eco-a1-confirmatory"
_SEEDS = tuple(range(101, 113))
_PREFIXES = ("i1:eco:a1c:confirmatory:",)


@contextmanager
def a1c_matched_temperament_birth(*, life_id: str, seed: int):
    """Temporarily select the preregistered source for exactly ONE I1 birth.

    Call only around birth_i1_m11() or a *fresh* I1Runtime cold factory.
    The returned life, its M11 file, and every subsequent step are independent
    and use the unpatched canonical motor and learning machinery.
    """
    if (type(life_id) is not str or not life_id.startswith(_PREFIXES)
            or len(life_id) > 128):
        raise ValueError("A1-C needs a bounded, distinct contract/pilot life identity")
    if type(seed) is not int or seed not in _SEEDS:
        raise ValueError("A1-C temperament seed is frozen to 1 or 2")

    from i1lab import i1_natural_runtime
    from i1lab.matched_temperament_research import (
        matched_temperament_configuration,
    )

    original = i1_natural_runtime.configure_birth_temperament
    calls = []

    def select(stage11_config, *, life_id: str):
        if life_id != expected_id:
            raise ValueError("A1-C source intercepted another individual's birth")
        if calls:
            raise RuntimeError("A1-C birth attempted a second temperament projection")
        configured = matched_temperament_configuration(
            stage11_config, life_id=life_id, world=_WORLD, seed=seed,
        )
        calls.append(life_id)
        return configured

    expected_id = life_id
    with patch.object(i1_natural_runtime, "configure_birth_temperament", select):
        yield
    if calls != [expected_id]:
        raise RuntimeError("A1-C birth did not use exactly one matched projection")
    if i1_natural_runtime.configure_birth_temperament is not original:
        raise RuntimeError("A1-C temporary birth selection was not restored")
