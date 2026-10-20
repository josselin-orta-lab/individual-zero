"""Read-only, inactive first-person site observations. Never a reward."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True, slots=True)
class SiteSample:
    position: tuple[int,int]
    sent_step: int
    observed_step: int
    observed_gain: float
    command_hash: str
    option_ref: str
    first_capture_hash: str
    followup_capture_hash: str

def site_samples(owner, *, life_id, site, now_step):
    if (type(life_id) is not str or not life_id.startswith("i1:")
        or getattr(owner,"life_id",None)!=life_id
        or getattr(owner,"enabled",None) is not True
        or type(site) is not tuple or len(site)!=2
        or any(type(x) is not int for x in site)
        or type(now_step) is not int or now_step<1):
        raise ValueError("invalid witness identity or site")
    records=owner.examples
    if type(records) is not tuple or len(records)>10000:
        raise ValueError("invalid witnessed records")
    out=[]
    prev=0
    required={"source_position","sent_world_step","observed_world_step",
              "delta_water","command_hash","option_ref",
              "first_capture_hash","followup_capture_hash"}
    for row in records:
        if type(row) is not dict or set(row)!=required:
            raise ValueError("unattested evidence shape")
        s=row["sent_world_step"];t=row["observed_world_step"]
        loc=row["source_position"];gain=row["delta_water"]
        evidence=(row["command_hash"],row["option_ref"],
                  row["first_capture_hash"],row["followup_capture_hash"])
        if (type(s) is not int or type(t) is not int
            or s<=prev or t!=s+1 or t>now_step
            or type(loc) is not list or len(loc)!=2
            or any(type(x) is not int for x in loc)
            or type(gain) not in (int,float) or not isfinite(gain)
            or not 0<gain<=100
            or any(type(x) is not str or not x for x in evidence)):
            raise ValueError("unattested or future sample")
        prev=s
        if tuple(loc)==site:
            out.append(SiteSample(tuple(loc),s,t,float(gain),*evidence))
    return tuple(out)
