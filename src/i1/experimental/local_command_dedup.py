"""Pure, inactive I1 local candidate deduplication (issue #340)."""
from math import isfinite

def _freeze(value):
    if value is None or type(value) in (str,bool,int):
        return value
    if type(value) is float:
        if not isfinite(value): raise ValueError("nonfinite parameter")
        return value
    if type(value) in (tuple,list): return tuple(_freeze(x) for x in value)
    if type(value) is dict:
        if any(type(k) is not str for k in value): raise ValueError("invalid parameter key")
        return tuple((k,_freeze(value[k])) for k in sorted(value))
    raise ValueError("untrusted parameter")

def _key(command):
    name=getattr(command,"primitive",None)
    params=getattr(command,"parameters",None)
    if type(name) is not str or not name or not isinstance(params,dict):
        raise ValueError("invalid perceived command")
    return name,_freeze(params)

def distinct_local_commands(available, existing, *, now_step):
    """No world access, UC charge, option creation or motor authority."""
    if (type(available) is not tuple or type(existing) is not tuple
        or len(available)>128 or len(existing)>128
        or type(now_step) is not int or now_step<1):
        raise ValueError("invalid bounded candidate context")
    seen=set()
    for p in existing:
        option=getattr(p,"option",None)
        expiry=getattr(option,"expires_at_step",None)
        if type(expiry) is not int or expiry<1: raise ValueError("invalid expiry")
        if expiry<=now_step: continue
        plan=getattr(p,"plan",None)
        if plan is None: continue
        steps=getattr(plan,"steps",None)
        if type(steps) is not tuple or len(steps)!=1:
            raise ValueError("unexpected local plan")
        seen.add(_key(steps[0].command))
    result=[]
    for command in available:
        key=_key(command)
        if key not in seen:
            seen.add(key)
            result.append(command)
    return tuple(result)
