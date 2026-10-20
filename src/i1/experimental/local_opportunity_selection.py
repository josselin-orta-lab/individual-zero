"""Research-only pure filter for available local commands, not a producer."""
from __future__ import annotations

_ALLOWED = frozenset(("boire", "manger", "collecter", "poser_une_pierre", "fabriquer_outil"))
_Q_EXPOSURES = {"neutral":(False,False), "rank_only":(True,False),
                "evidence_only":(False,True), "learned":(True,True)}

def local_q_visibility(exposure: str) -> tuple[bool,bool]:
    if type(exposure) is not str or exposure not in _Q_EXPOSURES:
        raise ValueError("unknown local Q research exposure")
    return _Q_EXPOSURES[exposure]

def local_interaction_choices(available: tuple, *, enabled: bool) -> tuple:
    """Only pre-admitted first-person commands; effects remain UNKNOWN."""
    if type(enabled) is not bool or type(available) is not tuple:
        raise ValueError("research local options require bounded typed input")
    if not enabled:
        return ()
    if len(available) > 128:
        raise ValueError("unbounded candidate commands")
    if any(not isinstance(getattr(c,"primitive",None),str) for c in available):
        raise ValueError("malformed locally available command")
    return tuple(c for c in available if c.primitive in _ALLOWED)
