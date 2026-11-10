"""Replay content cannot modify P1.3 learned physical-effects predictions.

48 fixed synthetic personally-experienced Mind fixtures, zero World births.
This is an architectural negative control, not an ecological experiment.
It uses equal replay count and compares the actual algorithms on detached
Mind copies. It never advertises the hypothetical tariff as a physical debit.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from math import fsum
import json
import sys

from . import stage2_replay_content_local as LOCAL

SCHEMA="i3-stage2.1-replay-prediction-channel-negative-control/v1"
ACTIONS=(("attendre",),("dormir",),("boire",),("manger","tok"))
FEAT_BODY=(80.0,65.0,65.0,90.0,80.0)


def _digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def source_mind(trial):
    """Synthetic *personal* effects, never privileged true World laws."""
    mind=LOCAL.synthetic_mind(trial)
    # These are synthetic first-person previously observed body differences
    # via the existing Effects.observe interface, not oracle World stocks.
    entries=(
        (("attendre",),(-0.35,-0.21,-0.39,0.06,-0.08)),
        (("dormir",),(2.20,-0.18,-0.39,0.13,3.20)),
        (("boire",),(-0.55,-0.21,6.60,0.0,-0.08)),
        (("manger","tok"),(-0.60,5.10,-0.39,0.07,-0.08)),
    )
    for key,delta in entries:
        mind.effects.observe(key,delta)
        mind.effects.observe(key,tuple(v*(1+0.01*(trial%5)) for v in delta))
    return mind


def _replay(source,trial,mode):
    clone=deepcopy(source)
    work,bill,_remaining,energy,vigilance=LOCAL._authorize_prepaid_work(
        clone,LOCAL.BODY,LOCAL.COUNT,LOCAL.BodyLaws())
    indices=LOCAL.select_indices(clone.buffer,LOCAL.COUNT,mode=mode,
                                 life_seed=LOCAL.MIND_SEED_START+trial,trial=trial)
    for index in indices:
        _,b0,b1,dead=clone.buffer[index]
        err=clone._td(b0,b1,dead)
        clone.buffer[index]=(abs(err),b0,b1,dead)
    return clone,indices,{
        "work":(work.cycles,work.simulated_steps,work.memory_items,work.replays),
        "would_debit_energy":energy,
        "would_debit_vigilance":vigilance,
        "unpaid":(bill["energy"]["unpaid"],bill["vigilance"]["unpaid"]),
    }


def _effect_channel(mind):
    # This is the actual action-dependent experience predictor read by Mind,
    # not value projection. It has no future personal outcome here.
    return {str(k):mind._read_plan_prediction(k) for k in ACTIONS}


def _value_channel(mind):
    # Same reference physical Body and same model projection. The learned
    # TD residual value channel differs through weights, not effect memory.
    phi=mind.feats(FEAT_BODY)
    projection=mind.project(FEAT_BODY,mind.drift())[0]
    return [mind.value(k,phi,projection) for k in range(len(mind.gammas))]


def probe():
    rows=[]
    for trial in range(LOCAL.TRIALS):
        original=source_mind(trial)
        pristine=_digest({"values":original.values,
                          "buffer":list(original.buffer),
                          "effects":repr(original.effects.stats),
                          "rng":repr(original.rng.getstate())})
        p,pi,pc=_replay(original,trial,"priority")
        r,ri,rc=_replay(original,trial,"random_content")
        after=_digest({"values":original.values,
                       "buffer":list(original.buffer),
                       "effects":repr(original.effects.stats),
                       "rng":repr(original.rng.getstate())})
        if pristine!=after:
            raise RuntimeError("observer modified original Mind")
        if (pc!=rc or pc["unpaid"]!=(0.0,0.0) or
                pc["work"][-1]!=LOCAL.COUNT):
            raise RuntimeError("unequal synthetic prepaid capacity/tariff")
        effect_original=_effect_channel(original)
        effect_p=_effect_channel(p)
        effect_r=_effect_channel(r)
        if (original.effects.stats!=p.effects.stats or
                p.effects.stats!=r.effects.stats or
                effect_original!=effect_p or effect_original!=effect_r):
            raise RuntimeError("TD replay selection improperly changed effects model")
        vp=_value_channel(p)
        vr=_value_channel(r)
        l1=fsum(abs(a-b) for a,b in zip(vp,vr))
        rows.append({
            "trial":trial,
            "different_memory_subsets":set(pi)!=set(ri),
            "same_effects_model_and_action_effect_forecasts":True,
            "different_TD_value_vectors":p.values!=r.values,
            "different_evaluated_value_predictions":l1>1e-12,
            "evaluated_value_L1":l1,
            "same_actual_model_replay_work":pc==rc,
            "projected_energy_tariff":pc["would_debit_energy"],
            "projected_vigilance_tariff":pc["would_debit_vigilance"],
        })
    return {
        "schema":SCHEMA,
        "status":"COMPLETE_SOFTWARE_NEGATIVE_CONTROL_ONLY",
        "fixed_synthetic_units":LOCAL.TRIALS,
        "replay_count_each_detached_copy":LOCAL.COUNT,
        "different_memory_subsets":sum(x["different_memory_subsets"] for x in rows),
        "same_effects_model_and_action_effect_forecasts":sum(
            x["same_effects_model_and_action_effect_forecasts"] for x in rows),
        "different_TD_value_vectors":sum(x["different_TD_value_vectors"] for x in rows),
        "different_evaluated_value_predictions":sum(
            x["different_evaluated_value_predictions"] for x in rows),
        "equal_estimated_energy_vigilance_tariff_per_arm":True,
        "projected_tariff_not_physically_debited":True,
        "no_hidden_World_or_future_actual_outcome_read":True,
        "no_World_or_life_executed":True,
        "scientific_survival_verdict":"NOT_ISSUED",
        "proper_future_predictive_score":"NOT_DEFINED",
        "observations":rows,
    }


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2 or argv[1]!="probe":
        raise SystemExit("usage: python -m i3.lab.stage2_replay_prediction_channel_negative_control probe")
    print(json.dumps(probe(),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
