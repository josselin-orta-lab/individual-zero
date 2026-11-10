"""Stage-2.1 local replay-content selection falsifier; no World or life.

Runs actual Mind._td learning on two detached copies of a synthetic, common
pre-sleep memory state. Both arms authorize identical model-level cognitive
work before replay. No World ever debits the body, so the receipt is a
*prepaid capacity / payable physical tariff*, NOT a claim of biological work.
The existing P1.3 prioritization and every historical policy are untouched.
"""
from __future__ import annotations

from collections import Counter, deque
from copy import deepcopy
from hashlib import sha256
import hmac
import json
from math import fsum, isfinite

from ..modules.body import (BodyLaws, CognitiveBudget, CognitiveWork,
                             cognitive_cost, debit_cognition, validate_body)
from ..modules.genome import generation_zero
from ..modules.mind import Mind, REPLAYS_PER_SLEEP

SCHEMA="i3-stage2-1-local-content-falsifier/v1"
DOMAIN=b"i3-stage2.1/random-replay-content-local/v1"
BODY=(80.,65.,65.,90.,80.)
TRIALS=48
COUNT=3
MEMORIES=12
GENOME_SEED_START=9200000
MIND_SEED_START=9900000


def _digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def select_indices(buffer, count:int, *, mode:str, life_seed:int, trial:int):
    """Choose distinct *memory positions*, not count; avoid Mind's RNG."""
    if type(count) is not int or type(life_seed) is not int or type(trial) is not int:
        raise ValueError("strict integer indices/seed/trial required")
    if count < 0 or life_seed < 0 or trial < 0 or count > min(
            REPLAYS_PER_SLEEP,len(buffer)):
        raise ValueError("replay count must be funded, bounded and eligible")
    if mode=="priority":
        return tuple(sorted(range(len(buffer)),
                            key=lambda i:-buffer[i][0])[:count])
    if mode=="random_content":
        key=sha256(DOMAIN+b"|"+str(life_seed).encode("ascii")).digest()
        ranked=sorted(range(len(buffer)),key=lambda i:(
            hmac.new(key,
                     f"{trial}|{i}".encode("ascii"),sha256).digest(),i))
        return tuple(ranked[:count])
    raise ValueError("unsupported replay selection; no silent fallback")


def _authorize_prepaid_work(mind,body,count,laws):
    """Same up-front finite allowance in each synthetic arm, no World."""
    budget=CognitiveBudget(body,laws)
    budget.spend(CognitiveWork(cycles=1))
    replay=CognitiveWork(simulated_steps=2*len(mind.proj_chunks),replays=1)
    for _ in range(count):
        budget.spend(replay)
    # Debit is the exact World tariff *were* this work applied by World;
    # a synthetic detached clone does NOT physically run through World.
    resulting_body,bill=debit_cognition(body,laws,budget.work)
    e,v=cognitive_cost(laws,budget.work)
    if not (bill["energy"]["unpaid"]==bill["vigilance"]["unpaid"]==0):
        raise ValueError("unpaid synthetic replay work")
    return budget.work,bill,resulting_body,e,v


def apply_detached_replays(source:Mind, *, mode:str, count:int,
                           body=BODY,laws=None,trial:int=0):
    """Exactly same source snapshot; no memory/values/RNG mutation to source."""
    if not isinstance(source,Mind):
        raise TypeError("real I3 Mind learning algorithm expected")
    laws=BodyLaws() if laws is None else laws
    body=validate_body(body)
    if type(trial) is not int or trial < 0:
        raise ValueError("nonnegative fixed trial ordinal required")
    clone=deepcopy(source)
    work,bill,remaining,e,v=_authorize_prepaid_work(clone,body,count,laws)
    selected=select_indices(clone.buffer,count,mode=mode,
                            life_seed=MIND_SEED_START+trial,trial=trial)
    before=deepcopy(clone.values)
    recomputed=[]
    for i in selected:
        _,b0,b1,dead=clone.buffer[i]
        err=clone._td(b0,b1,dead)
        clone.buffer[i]=(abs(err),b0,b1,dead)
        recomputed.append(err)
    magnitude=fsum(abs(clone.values[k][j]-before[k][j])
                   for k in range(len(before)) for j in range(len(before[k])))
    if not isfinite(magnitude):
        raise ValueError("non-finite learned update")
    return {
        "selected_indices":list(selected),
        "replays_executed":len(selected),
        "prepaid_work":{"cycles":work.cycles,
                        "simulated_steps":work.simulated_steps,
                        "memory_items":work.memory_items,"replays":work.replays},
        "would_debit_energy":e,"would_debit_vigilance":v,
        "unpaid_energy":bill["energy"]["unpaid"],
        "unpaid_vigilance":bill["vigilance"]["unpaid"],
        "remaining_body_if_world_debited":list(remaining),
        "learned_values":clone.values,
        "learned_state_sha256":_digest(clone.values),
        "buffer_sha256":_digest(list(clone.buffer)),
        "absolute_update_L1":magnitude,
        "original_mind_unchanged":True, # checked by trial aggregate
        "world_debit_applied":False,
    }


def synthetic_mind(trial:int):
    """Fixed legal internal snapshots, never born into or stepping a World."""
    if type(trial) is not int or not 0 <= trial < TRIALS:
        raise ValueError("outside fixed synthetic trial set")
    mind=Mind(generation_zero(GENOME_SEED_START+trial),
              MIND_SEED_START+trial)
    items=[]
    for i in range(MEMORIES):
        shift=(trial%7)*0.25
        before=(70.+(i%3)*2,55.+(i%4)*4+shift,
                48.+(i%3)*6,85.-(i%4),70.+(i%2)*3)
        after=(before[0]-(i%3+1)*.7,
               before[1]-1.2,
               before[2]-(i%4+1)*.8,
               before[3]-(i%2)*.3,
               before[4]-1.5)
        items.append((float(MEMORIES-i),before,after,False))
    mind.buffer=deque(items)
    return mind


def probe():
    """Exhaustive, fixed 48-trial synthetic test; no outcome tuning/stopping."""
    rows=[]
    for trial in range(TRIALS):
        before=synthetic_mind(trial)
        snap=_digest({"values":before.values,"buffer":list(before.buffer),
                      "rng":repr(before.rng.getstate()),
                      "budget_rng":repr(before._budget_rng.getstate())})
        a=apply_detached_replays(before,mode="priority",count=COUNT,trial=trial)
        b=apply_detached_replays(before,mode="random_content",count=COUNT,trial=trial)
        after=_digest({"values":before.values,"buffer":list(before.buffer),
                       "rng":repr(before.rng.getstate()),
                       "budget_rng":repr(before._budget_rng.getstate())})
        if after!=snap:
            raise ValueError("observer source Mind was mutated")
        if (a["prepaid_work"]!=b["prepaid_work"] or
            a["would_debit_energy"]!=b["would_debit_energy"] or
            a["would_debit_vigilance"]!=b["would_debit_vigilance"] or
            a["replays_executed"]!=b["replays_executed"]!=COUNT):
            raise ValueError("memory selection confounded by different model work")
        if (a["unpaid_energy"]!=0 or b["unpaid_energy"]!=0 or
            a["unpaid_vigilance"]!=0 or b["unpaid_vigilance"]!=0):
            raise ValueError("unpaid replays in local mechanism probe")
        difference=fsum(abs(a["learned_values"][k][j]-
                            b["learned_values"][k][j])
                        for k in range(3) for j in range(6))
        if not isfinite(difference):
            raise ValueError("nonfinite between-arm divergence")
        rows.append({
            "trial":trial,"selected_priority":a["selected_indices"],
            "selected_random_content":b["selected_indices"],
            "same_positions":set(a["selected_indices"])==
                              set(b["selected_indices"]),
            "value_L1_between_arms":difference,
            "priority_L1":a["absolute_update_L1"],
            "random_content_L1":b["absolute_update_L1"],
            "prepaid_energy_per_arm":a["would_debit_energy"],
            "prepaid_vigilance_per_arm":a["would_debit_vigilance"],
        })
    return {
        "schema":SCHEMA,"status":"COMPLETE_SYNTHETIC_MECHANISM_ONLY",
        "trial_count":TRIALS,"memories_per_trial":MEMORIES,
        "equal_actual_replays_per_arm":COUNT,
        "identical_replay_work_and_projected_physical_tariff":True,
        "differing_memory_subsets":sum(not r["same_positions"] for r in rows),
        "differing_learned_value_vectors":
            sum(r["value_L1_between_arms"]>1e-12 for r in rows),
        "mean_L1_between_values":
            fsum(r["value_L1_between_arms"] for r in rows)/TRIALS,
        "mean_absolute_update_priority":
            fsum(r["priority_L1"] for r in rows)/TRIALS,
        "mean_absolute_update_random_content":
            fsum(r["random_content_L1"] for r in rows)/TRIALS,
        "cost_energy_per_trial":rows[0]["prepaid_energy_per_arm"],
        "cost_vigilance_per_trial":rows[0]["prepaid_vigilance_per_arm"],
        "no_source_mutation":True,
        "no_world_or_full_life_executed":True,
        "physical_debit_applied_by_world":False,
        "scientific_survival_verdict":"NOT_ISSUED",
        "family_or_ecology_generalization":False,
        "observations":rows,
    }


def main():
    report=probe()
    print(json.dumps(report,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
