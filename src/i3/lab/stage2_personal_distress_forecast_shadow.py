"""Self-experience next-step distress prediction from replayed memory only.

STAGE 2.1 SOFTWARE-ONLY SHADOW CANDIDATE. No World, no learning added to the
living Mind, no action-control connection, no real organism energy/vigilance
debit. Trains a separate direct-outcome mean regressor on personally recorded
(before_body, after_body, terminal) memory tuples, without oracle resources.

This is specifically NOT TD: the outcome target is the actually OBSERVED
next first-person innate distress, not a bootstrap from learned V weights.
Squared error on later observed transitions is a proper mean forecast score,
but on these deterministic synthetic fixtures it cannot imply survival
benefit or policy-independent value. Work tariff is not yet measured/paid.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from math import fsum, isfinite
import json
import sys

from . import stage2_replay_content_local as LOCAL
from . import stage2_replay_predictive_negative_control as NEG
from ..modules.mind import Mind, REPLAYS_PER_SLEEP
from ..modules.stage2_replay_content_selection import random_content_indices

SCHEMA="i3-stage2.1-personal-next-distress-shadow/v1"
TRIALS=48
REPLAYS=3
CENSOR_REASONS=frozenset((
    "HORIZON_BEFORE_NEXT_TRANSITION",
    "NEXT_FIRST_PERSON_OUTCOME_MISSING",
    "TERMINATED_BEFORE_FORECAST_WINDOW",
))


def _sha(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                             allow_nan=False,default=str).encode("utf-8")).hexdigest()


def _body(value):
    if (type(value) not in (tuple,list) or len(value)!=5 or
            any(type(x) not in (int,float) or
                not isfinite(x) or not 0<=x<=100 for x in value)):
        raise ValueError("five-channel actual first-person Body required")
    return tuple(float(x) for x in value)


class PersonalDistressHead:
    """Detached learned correction for expected next-step innate distress."""

    def __init__(self,personal_mind:Mind):
        if not isinstance(personal_mind,Mind):
            raise TypeError("actual first-person I3 Mind required")
        self._mind=deepcopy(personal_mind)
        # Immutable-by-protocol list of memories genuinely present at the
        # PRE-FORK source boundary. Future outcome injection is inadmissible.
        self._eligible_records=tuple(deepcopy(list(self._mind.buffer)))
        self.trained_indices=()
        self.source_identity=_sha({
            "genes":(self._mind.theta,self._mind.p,self._mind.w,
                     self._mind.alpha,self._mind.gammas),
            "values":self._mind.values,
            "buffer":list(self._mind.buffer),
            "effects":repr(self._mind.effects.stats),
        })
        self.weights=[0.0]*6
        self.training_updates=0

    def _features(self,b):
        return self._mind.feats(_body(b))

    def predict(self,before_body):
        phi=self._features(before_body)
        predicted=(-self._mind.distress(phi)+
                   fsum(w*x for w,x in zip(self.weights,phi)))
        if not isfinite(predicted):
            raise RuntimeError("nonfinite next-distress prediction")
        return predicted

    def target_from_actual_outcome(self,after_body,dead):
        if type(dead) is not bool:
            raise TypeError("actual terminal flag must be boolean")
        after=self._features(after_body)
        # Same innate distress semantics as Mind._td's actual learned reward.
        return -self._mind.d_max if dead else -self._mind.distress(after)

    def _fit_record(self,index):
        # Training can read ONLY the fixed pre-fork personal memory snapshot;
        # no arbitrary target or future Body can enter the learning path.
        magnitude,before,after,dead=self._eligible_records[index]
        if type(magnitude) not in (int,float) or not isfinite(magnitude):
            raise ValueError("invalid replay memory provenance")
        phi=self._features(before)
        target=self.target_from_actual_outcome(after,dead)
        prediction=self.predict(before)
        delta=target-prediction
        norm=fsum(x*x for x in phi)
        if not norm>0 or not isfinite(delta):
            raise RuntimeError("invalid self-derived direct prediction error")
        # Use this very individual's existing genome alpha; no hidden
        # labels, prescribed goal state or new preferred survival action.
        step=self._mind.alpha*delta/norm
        self.weights=[w+step*x for w,x in zip(self.weights,phi)]
        if any(not isfinite(w) for w in self.weights):
            raise RuntimeError("unbounded shadow regression")
        self.training_updates+=1

    def apply(self,original_buffer,indices):
        if type(original_buffer) not in (tuple,list) or (
                tuple(original_buffer)!=self._eligible_records):
            raise PermissionError("unrecorded or future outcome cannot train the shadow head")
        if (type(indices) not in (tuple,list) or
                len(indices)+self.training_updates>REPLAYS_PER_SLEEP):
            raise ValueError("invalid replay count or exceeded one-fork physical cap")
        if (len(set(indices))!=len(indices) or
                any(type(i) is not int or
                    not 0<=i<len(self._eligible_records) or
                    i in self.trained_indices for i in indices)):
            raise ValueError("replay indices must be unique eligible past memories")
        for i in indices:
            self._fit_record(i)
        self.trained_indices+=tuple(indices)


class PrequentialDistressAudit:
    """One original observed window, prospective seal, explicit missing data."""

    def __init__(self,personal_mind:Mind):
        self._reference=PersonalDistressHead(personal_mind)
        self._pending=None
        self._ids=set()
        self._receipts=[]

    def freeze(self,*,identity:str,priority_head:PersonalDistressHead,
               random_head:PersonalDistressHead,before_body):
        if (type(identity) is not str or not identity or len(identity)>128 or
                identity in self._ids or self._pending is not None):
            raise PermissionError("a new, unscored prospective identity is mandatory")
        before=_body(before_body)
        if (type(priority_head) is not PersonalDistressHead or
                type(random_head) is not PersonalDistressHead or
                priority_head.source_identity!=random_head.source_identity or
                priority_head.source_identity!=self._reference.source_identity or
                priority_head.training_updates!=random_head.training_updates or
                priority_head.training_updates>REPLAYS_PER_SLEEP or
                priority_head.training_updates!=len(priority_head.trained_indices) or
                random_head.training_updates!=len(random_head.trained_indices)):
            raise PermissionError("not identical initial individual or bounded replay count")
        p=priority_head.predict(before)
        r=random_head.predict(before)
        receipt={
            "schema":SCHEMA,"identity":identity,
            "first_person_before_body":list(before),
            "priority_predicted_next_reward":p,
            "random_predicted_next_reward":r,
            "personal_genome_source_sha256":self._reference.source_identity,
            "replay_updates_per_shadow_arm":priority_head.training_updates,
            "no_future_outcome_at_freeze":True,
            "observer_cpu_not_living_cognition":True,
        }
        seal=_sha(receipt)
        self._pending=(receipt,seal)
        self._ids.add(identity)
        return {
            "schema":SCHEMA,"identity":identity,
            "preoutcome_prediction_sha256":seal,
            "different_forecast":p!=r,
            "future_outcome_observed":False,
            "no_source_world_or_live_mind_modification":True,
        }

    def _pending_receipt(self,identity,seal):
        if self._pending is None:
            raise PermissionError("no pending preoutcome prediction")
        receipt,expected=self._pending
        if (identity!=receipt["identity"] or seal!=expected or
                _sha(receipt)!=expected):
            raise PermissionError("prediction changed or not sealed before outcome")
        return receipt

    def score(self,*,identity,preoutcome_prediction_sha256,
              actual_after_body,actual_dead:bool):
        receipt=self._pending_receipt(identity,preoutcome_prediction_sha256)
        actual=_body(actual_after_body)
        target=self._reference.target_from_actual_outcome(actual,actual_dead)
        p=receipt["priority_predicted_next_reward"]
        r=receipt["random_predicted_next_reward"]
        lp=(p-target)**2
        lr=(r-target)**2
        if not all(isfinite(v) for v in (target,lp,lr)):
            raise RuntimeError("invalid first-person direct outcome or mean loss")
        out={
            "identity":identity,"status":"SCORED_OBSERVED_FIRST_PERSON_OUTCOME",
            "preoutcome_prediction_sha256":preoutcome_prediction_sha256,
            "observed_next_intrinsic_reward":target,
            "terminal_observed":actual_dead,
            "priority_squared_error":lp,
            "random_squared_error":lr,
            "priority_minus_random_squared_error":lp-lr,
            "target_is_actual_next_body_not_TD_bootstrap":True,
            "same_logged_behavior_outcome_not_counterfactual_world":True,
            "no_observer_physical_debit":True,
        }
        self._receipts.append(out)
        self._pending=None
        return dict(out)

    def censor(self,*,identity,preoutcome_prediction_sha256,reason:str):
        self._pending_receipt(identity,preoutcome_prediction_sha256)
        if reason not in CENSOR_REASONS:
            raise ValueError("missing outcome must use registered censor cause")
        out={
            "identity":identity,"status":"CENSORED_NO_TARGET",
            "reason":reason,
            "preoutcome_prediction_sha256":preoutcome_prediction_sha256,
            "observed_next_intrinsic_reward":None,
            "priority_squared_error":None,"random_squared_error":None,
            "priority_minus_random_squared_error":None,
            "zero_error_imputation":False,"no_observer_physical_debit":True,
        }
        self._receipts.append(out)
        self._pending=None
        return dict(out)

    def report(self):
        if self._pending is not None:
            raise PermissionError("incomplete prequential observation, must classify")
        observed=[x for x in self._receipts if x["status"]==
                  "SCORED_OBSERVED_FIRST_PERSON_OUTCOME"]
        return {
            "schema":SCHEMA,
            "status":"SOFTWARE_ONLY_SHADOW_MEAN_FORECAST_SCORING",
            "frozen_predictions":len(self._ids),
            "scored_observed_outcomes":len(observed),
            "explicitly_censored_outcomes":len(self._receipts)-len(observed),
            "all_windows_accounted":len(self._receipts)==len(self._ids),
            "priority_lower_sq_loss":sum(
                x["priority_squared_error"]<x["random_squared_error"]
                for x in observed),
            "random_lower_sq_loss":sum(
                x["random_squared_error"]<x["priority_squared_error"]
                for x in observed),
            "tied_sq_loss":sum(
                x["random_squared_error"]==x["priority_squared_error"]
                for x in observed),
            "sum_priority_sq_loss":fsum(
                x["priority_squared_error"] for x in observed),
            "sum_random_sq_loss":fsum(
                x["random_squared_error"] for x in observed),
            "genuine_life_or_world_executions":0,
            "actual_organism_cognitive_funding":False,
            "shadow_decisions_can_change_live_action":False,
            "scientific_predictive_utility_claim":False,
            "scientific_survival_claim":False,
        }


def _heldout_before(trial):
    """Future observable body, separate from twelve past memory records."""
    i=LOCAL.MEMORIES+(trial%5)
    shift=(trial%7)*.25
    return (70.+(i%3)*2,55.+(i%4)*4+shift,
            48.+(i%3)*6,85.-(i%4),70.+(i%2)*3)


def _heldout_after(trial):
    """Only called AFTER forecasts are committed. No World/hidden effects."""
    i=LOCAL.MEMORIES+(trial%5)
    b=_heldout_before(trial)
    return (b[0]-(i%3+1)*.7,
            b[1]-1.2,
            b[2]-(i%4+1)*.8+.03*(trial%3),
            b[3]-(i%2)*.3,
            b[4]-1.5)


def rehearse():
    results=[]
    for trial in range(TRIALS):
        source=NEG.synthetic_personal_mind(trial)
        original=NEG._mind_seal(source)
        p=PersonalDistressHead(source)
        r=PersonalDistressHead(source)
        memory=tuple(source.buffer)
        count=REPLAYS
        priority=tuple(sorted(range(len(memory)),key=lambda i:-memory[i][0])[:count])
        random=random_content_indices(
            eligible=len(memory),count=count,
            life_seed=LOCAL.MIND_SEED_START+trial,sleep_ordinal=trial+1)
        p.apply(memory,priority)
        r.apply(memory,random)
        evaluator=PrequentialDistressAudit(source)
        stamp=evaluator.freeze(identity=f"shadow-{trial:04d}",
                               priority_head=p,random_head=r,
                               before_body=_heldout_before(trial))
        # Future factual target is constructed only after the forecast seal.
        observed=evaluator.score(
            identity=stamp["identity"],
            preoutcome_prediction_sha256=stamp["preoutcome_prediction_sha256"],
            actual_after_body=_heldout_after(trial),actual_dead=False)
        summary=evaluator.report()
        if (NEG._mind_seal(source)!=original or
                not summary["all_windows_accounted"] or
                summary["scored_observed_outcomes"]!=1):
            raise RuntimeError("shadow learning altered source or lost a future observation")
        results.append({
            "different_selected_memories":set(priority)!=set(random),
            "different_frozen_future_forecast":stamp["different_forecast"],
            "priority_loss":observed["priority_squared_error"],
            "random_loss":observed["random_squared_error"],
            "preoutcome_sha":stamp["preoutcome_prediction_sha256"],
        })
    return {
        "schema":SCHEMA,
        "status":"SYNTHETIC_SHADOW_REPLAY_SENSITIVE_PREQUENTIAL_CAPABILITY",
        "synthetic_cases":TRIALS,
        "replays_per_detached_head":REPLAYS,
        "different_memory_subsets":sum(x["different_selected_memories"]
                                       for x in results),
        "different_frozen_predictions":sum(x["different_frozen_future_forecast"]
                                            for x in results),
        "scored_heldout_future_observations":len(results),
        "priority_lower_synthetic_sq_loss":sum(
            x["priority_loss"]<x["random_loss"] for x in results),
        "random_lower_synthetic_sq_loss":sum(
            x["random_loss"]<x["priority_loss"] for x in results),
        "tied_synthetic_sq_loss":sum(
            x["random_loss"]==x["priority_loss"] for x in results),
        "all_future_forecasts_sealed_before_outcomes":True,
        "no_world_or_live_policy_modification":True,
        "no_physical_cognitive_debit":True,
        "scientific_lives":0,
        "no_independent_iid_ecology":True,
        "no_survival_or_predictive_utility_generalization":True,
    }


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2 or argv[1]!="rehearse":
        raise SystemExit("usage: python -m i3.lab.stage2_personal_distress_forecast_shadow rehearse")
    print(json.dumps(rehearse(),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
