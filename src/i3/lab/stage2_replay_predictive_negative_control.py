"""Replay TD content versus *actual effect-prediction* negative control.

Software-only Stage 2.1 falsifier. 48 fixed synthetic, personally observed
effect-and-memory fixtures. Real Mind._td on two detached copies with equal
memory count. No World is created; hypothetical CPU is NOT an organism debit.

TD replay updates learned values and buffer, not the EffectsModel. Therefore
a one-step effects forecast cannot rank which replayed memory was useful.
The learned value residual can be sensitive but is NOT a calibrated forecast.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from math import fsum, isfinite
import json
import sys

from . import stage2_replay_content_local as LOCAL
from ..modules.mind import Mind, REPLAYS_PER_SLEEP
from ..modules.stage2_replay_content_selection import random_content_indices

SCHEMA="i3-stage2.1-replay-predictive-negative-control/v1"
TRIALS=48
COUNT=3
BODY=LOCAL.BODY
FORECAST_KEYS=(("attendre",),("dormir",),("boire",),
               ("manger",),("se_deplacer",))


def _sha(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                             allow_nan=False,default=str).encode()).hexdigest()


def _mind_seal(mind):
    return _sha({"values":mind.values,
                 "buffer":list(mind.buffer),
                 "effects":repr(mind.effects.stats),
                 "personal_map":repr(mind.map),
                 "personal_history":repr(mind.hist),
                 "rng":repr(mind.rng.getstate()),
                 "budget_rng":repr(mind._budget_rng.getstate())})


def _effect_readouts(mind,keys):
    result=[]
    for key in keys:
        mean,uncertainty=mind._read_plan_prediction(key)
        vector=tuple(float(v) for v in mean)
        if (len(vector)!=5 or any(not isfinite(v) for v in vector)
                or not isfinite(uncertainty)):
            raise ValueError("nonfinite observed-effects forecast")
        result.append((tuple(key),vector,float(uncertainty)))
    return tuple(result)


def _residual_readout(mind,body):
    # Learned TD correction to innate self-projection at this fixed body.
    # This number is *not* a proper forecast of a future observed target.
    phi=mind.feats(body)
    return tuple(fsum(w*x for w,x in zip(row,phi))
                 for row in mind.values)


def synthetic_personal_mind(trial):
    """Fixed software-only personally observed transitions; no living World."""
    mind=LOCAL.synthetic_mind(trial)
    # Genuine original EffectsModel.observe(), fed only observed-effect
    # fixture deltas. Nonzero learned means prevent a trivial empty model.
    observations=(
        (("attendre",),(-.2,-.7,-1.3,0.,-.4)),
        (("dormir",),(1.3,-1.,-.8,.3,1.8)),
        (("boire",),(-.6,-.7,8.4,0.,-.6)),
        (("manger",),(-.6,5.5,-.9,.2,-.6)),
        (("se_deplacer",),(-1.4,-1.1,-.8,0.,-1.)),
        (("attendre",),(-.2,-.6,-1.1,0.,-.4)),
    )
    for key,delta in observations:
        mind.effects.observe(key,delta)
    return mind


def contrast(source:Mind,*,count:int,life_seed:int,
             sleep_ordinal:int,keys=FORECAST_KEYS,body=BODY):
    """Compare only exact actual TD replay logic, on detached cloned Minds.

    count is a predeclared LOCAL synthetic replay allowance. Its CPU and
    hypothetical tariff are NOT physically funded by a real individual.
    """
    if not isinstance(source,Mind):
        raise TypeError("actual I3 Mind algorithm required")
    if (type(count) is not int or count<0 or
            count>min(REPLAYS_PER_SLEEP,len(source.buffer))):
        raise ValueError("invalid bounded local replay count")
    if (type(life_seed) is not int or life_seed<0 or
            type(sleep_ordinal) is not int or sleep_ordinal<0):
        raise ValueError("invalid life-seeded local replay identity")
    if len(body)!=5 or any(type(v) not in (int,float) or
                           not isfinite(v) or not 0<=v<=100 for v in body):
        raise ValueError("invalid five-channel first-person body")
    if type(keys) not in (tuple,list) or any(
            type(k) is not tuple or not k or type(k[0]) is not str
            for k in keys):
        raise ValueError("invalid first-person action keys")
    source_seal=_mind_seal(source)
    p,r=deepcopy(source),deepcopy(source)
    priority=tuple(sorted(range(len(p.buffer)),key=lambda i:-p.buffer[i][0])[:count])
    random=random_content_indices(
        eligible=len(r.buffer),count=count,
        life_seed=life_seed,sleep_ordinal=sleep_ordinal)
    for clone,indices in ((p,priority),(r,random)):
        for idx in indices:
            _old,before,after,dead=clone.buffer[idx]
            delta=clone._td(before,after,dead)
            clone.buffer[idx]=(abs(delta),before,after,dead)
    if _mind_seal(source)!=source_seal:
        raise RuntimeError("laboratory replay changed original individual")
    if (p.effects.stats!=source.effects.stats or
            r.effects.stats!=source.effects.stats or
            p.drift()!=r.drift()):
        raise RuntimeError("TD replay changed original effects model")
    effects_p=_effect_readouts(p,keys)
    effects_r=_effect_readouts(r,keys)
    if effects_p!=effects_r:
        raise RuntimeError("TD-only memory selection changed effect forecasts")
    val_p,val_r=_residual_readout(p,body),_residual_readout(r,body)
    distance=fsum(abs(a-b) for a,b in zip(val_p,val_r))
    if not isfinite(distance):
        raise RuntimeError("nonfinite learned value readout")
    return {
        "schema":SCHEMA,
        "selected_priority":list(priority),
        "selected_random_content":list(random),
        "replays_in_each_detached_copy":count,
        "different_memory_subset":set(priority)!=set(random),
        "different_values":p.values!=r.values,
        "value_vector_L1":fsum(abs(a-b) for rowp,rowr in zip(p.values,r.values)
                               for a,b in zip(rowp,rowr)),
        "value_residual_readout_L1":distance,
        "same_effects_model_after_replay":True,
        "same_action_effect_predictions":True,
        "effect_forecast_sha256":_sha(effects_p),
        "priority_values_sha256":_sha(p.values),
        "random_values_sha256":_sha(r.values),
        "original_mind_sha256":source_seal,
        "original_mind_unchanged":True,
        "no_world_or_life":True,
        "observer_physical_debit":False,
        "predictive_utility_claim":False,
    }


def rehearse():
    rows=[]
    for trial in range(TRIALS):
        source=synthetic_personal_mind(trial)
        rows.append(contrast(
            source,count=COUNT,
            life_seed=LOCAL.MIND_SEED_START+trial,
            sleep_ordinal=trial+1))
    return {
        "schema":SCHEMA,
        "status":"NEGATIVE_CONTROL_EFFECT_PREDICTION_NOT_REPLAY_SENSITIVE",
        "synthetic_cases":TRIALS,
        "detached_td_replays_per_arm":COUNT,
        "different_memory_subset_cases":sum(x["different_memory_subset"]
                                             for x in rows),
        "different_learned_value_cases":sum(x["different_values"]
                                           for x in rows),
        "different_value_residual_readout_cases":sum(
            x["value_residual_readout_L1"]>1e-12 for x in rows),
        "different_one_step_effect_forecast_cases":sum(
            not x["same_action_effect_predictions"] for x in rows),
        "effects_model_unchanged_in_every_case":all(
            x["same_effects_model_after_replay"] for x in rows),
        "original_mind_unchanged_in_every_case":all(
            x["original_mind_unchanged"] for x in rows),
        "no_world_or_life_executed":True,
        "observer_cpu_is_external":True,
        "scientific_lives":0,"survival_claim":False,
        "prospective_calibrated_predictive_utility":False,
    }


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2 or argv[1]!="rehearse":
        raise SystemExit("usage: python -m i3.lab.stage2_replay_predictive_negative_control rehearse")
    print(json.dumps(rehearse(),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
