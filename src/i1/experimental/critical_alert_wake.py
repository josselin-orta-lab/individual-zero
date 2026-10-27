"""Research-only observation: no suppression of sleep candidates."""
from __future__ import annotations
from collections.abc import Mapping
from math import isfinite

def critical_alert_channels(*, pending, sleep_mode, world_step, capture, thresholds):
    if (pending is None or getattr(pending,"woke",None) is not True
        or getattr(pending,"reason",None)!="alert"
        or sleep_mode!="awake" or getattr(pending,"world_step",None)!=world_step):
        return ()
    if (capture is None or getattr(capture,"t_monde",None)!=world_step
        or not isinstance(getattr(capture,"body",None),Mapping)
        or not isinstance(thresholds,Mapping)):
        raise RuntimeError("alert wake lacks personally observed body")
    observed=capture.body
    names=("energy","food","water","integrity")
    for name in names:
        if (name not in observed or name not in thresholds
            or type(observed[name]) not in (int,float)
            or type(thresholds[name]) not in (int,float)
            or not isfinite(observed[name]) or not isfinite(thresholds[name])
            or not 0<=observed[name]<=100 or not 0<=thresholds[name]<=100):
            raise RuntimeError("invalid physical alert evidence")
    if observed["energy"]<=thresholds["energy"]:
        return ()
    return tuple(name for name in ("water","food","integrity")
                 if observed[name]<=thresholds[name])
