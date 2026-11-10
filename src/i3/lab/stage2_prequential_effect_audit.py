"""Observer-only, strictly prospective first-person *effect* forecast scoring.

A forecast is sealed AFTER the living individual has selected an action but
BEFORE its outcome can be observed. A later actual first-person body
transition yields a mean-squared-error score for the predicted 5-channel
delta. This is a proper squared-error score for a predicted conditional
MEAN, not a survival objective, causal memory effect or independent
confirmation of the I3 model's probabilistic calibration.

The replay P/R negative-control pair must have identical EffectsModel
predictions. An observed score is therefore identical in both branches and
CANNOT certify which TD replay-memory content was more useful. Missing
transitions are explicitly CENSORED, never silently scored as zero.

No World, no active Mind learning, no physical debit and no action feedback.
"""
from __future__ import annotations

from hashlib import sha256
from math import fsum, isfinite
import json

from ..modules.mind import Mind

SCHEMA="i3-stage2.1-prequential-effects-mean-score-negative-control/v1"
CENSOR_REASONS=frozenset((
    "HORIZON_WITHOUT_NEXT_OUTCOME",
    "TERMINAL_BEFORE_NEXT_ACTION",
    "ORIGINAL_OUTCOME_NOT_OBSERVABLE",
))


def _canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      allow_nan=False).encode("utf-8")


def _sha(obj):
    return sha256(_canonical(obj)).hexdigest()


def _body(value):
    if (type(value) not in (tuple,list) or len(value)!=5 or
            any(type(x) not in (float,int) or not isfinite(x) or
                x<0 or x>100 for x in value)):
        raise ValueError("actual five-channel finite bounded first-person Body required")
    return tuple(float(x) for x in value)


def _action_key(key):
    if (type(key) is not tuple or not key or
            type(key[0]) is not str or not key[0] or
            any(type(k) not in (str,type(None)) for k in key)):
        raise ValueError("actual first-person action-key tuple required")
    return tuple(key)


def _prediction(mind,key):
    if not isinstance(mind,Mind):
        raise TypeError("actual I3 Mind effect readout required")
    values,uncertainty=mind._read_plan_prediction(key)
    mean=tuple(float(x) for x in values)
    if (len(mean)!=5 or any(not isfinite(x) for x in mean) or
            type(uncertainty) not in (int,float) or
            not isfinite(uncertainty)):
        raise ValueError("invalid learned first-person effect forecast")
    return mean,float(uncertainty)


class PrequentialEffectAudit:
    """Finite, no-retroactive-forecast, one pending observed decision at a time."""

    def __init__(self):
        self._pending=None
        self._ids=set()
        self._receipts=[]

    def freeze(self,*,identity:str,priority_mind:Mind,random_mind:Mind,
               before_body,actual_action_key:tuple):
        """Pre-outcome commitment; cannot accept any realized result."""
        if type(identity) is not str or not identity or len(identity)>128:
            raise ValueError("source-scoped unique observation identity required")
        if identity in self._ids or self._pending is not None:
            raise PermissionError("duplicate or unresolved pre-outcome forecast")
        before=_body(before_body)
        key=_action_key(actual_action_key)
        p=_prediction(priority_mind,key)
        r=_prediction(random_mind,key)
        if p!=r:
            raise PermissionError(
                "effects prediction changed; not a valid replay-only negative control")
        witness={
            "schema":SCHEMA,"identity":identity,
            "actual_action_key":list(key),
            "before_actual_body":list(before),
            "priority_predicted_delta":list(p[0]),
            "random_predicted_delta":list(r[0]),
            "priority_uncertainty":p[1],"random_uncertainty":r[1],
            "same_effects_prediction":True,
            "result_available_at_forecast_time":False,
            "no_world_or_life":True,
        }
        digest=_sha(witness)
        self._pending=(witness,digest)
        self._ids.add(identity)
        return {
            "schema":SCHEMA,
            "identity":identity,
            "preoutcome_forecast_sha256":digest,
            "same_effects_prediction":True,
            "future_outcome_seen":False,
            "not_a_replay_utility_estimator":True,
        }

    def _verify_pending(self,identity,digest):
        if self._pending is None:
            raise PermissionError("no outstanding pre-outcome forecast")
        witness,original_sha=self._pending
        if (identity!=witness["identity"] or digest!=original_sha or
                _sha(witness)!=original_sha):
            raise PermissionError("wrong, altered or retrospectively substituted forecast")
        return witness

    def score(self,*,identity,preoutcome_forecast_sha256,
              actual_action_key,actual_after_body):
        """Score only a realized transition with matching actual action."""
        witness=self._verify_pending(identity,preoutcome_forecast_sha256)
        key=_action_key(actual_action_key)
        if list(key)!=witness["actual_action_key"]:
            raise PermissionError(
                "not the original executed action; no counterfactual World outcome")
        after=_body(actual_after_body)
        before=tuple(witness["before_actual_body"])
        observed=tuple(a-b for a,b in zip(after,before))
        p=tuple(witness["priority_predicted_delta"])
        r=tuple(witness["random_predicted_delta"])
        loss_p=fsum((o-u)**2 for o,u in zip(observed,p))/len(observed)
        loss_r=fsum((o-u)**2 for o,u in zip(observed,r))/len(observed)
        if not isfinite(loss_p) or not isfinite(loss_r) or loss_p!=loss_r:
            raise RuntimeError("negative-control forecast loss mismatch")
        out={
            "identity":identity,"status":"OBSERVED_SAME_ACTION",
            "preoutcome_forecast_sha256":preoutcome_forecast_sha256,
            "observed_delta":list(observed),
            "priority_mean_squared_error":loss_p,
            "random_mean_squared_error":loss_r,
            "difference_priority_minus_random":0.0,
            "outcome_seen_only_after_forecast_commit":True,
            "replay_content_effect_sensitivity":False,
            "proper_point_mean_score_only":True,
            "no_physical_work_billed_by_observer":True,
        }
        self._receipts.append(out)
        self._pending=None
        return dict(out)

    def censor(self,*,identity,preoutcome_forecast_sha256,reason):
        """Explicit non-outcome; no score imputation, no second attempt."""
        self._verify_pending(identity,preoutcome_forecast_sha256)
        if reason not in CENSOR_REASONS:
            raise ValueError("unknown, unregistered censoring reason")
        out={
            "identity":identity,"status":"CENSORED",
            "reason":reason,
            "preoutcome_forecast_sha256":preoutcome_forecast_sha256,
            "priority_mean_squared_error":None,
            "random_mean_squared_error":None,
            "difference_priority_minus_random":None,
            "not_imputed_as_zero":True,
            "no_physical_work_billed_by_observer":True,
        }
        self._receipts.append(out)
        self._pending=None
        return dict(out)

    def report(self):
        if self._pending is not None:
            raise PermissionError("unresolved prospective forecast; classify, do not omit")
        scored=[r for r in self._receipts if r["status"]=="OBSERVED_SAME_ACTION"]
        censored=[r for r in self._receipts if r["status"]=="CENSORED"]
        return {
            "schema":SCHEMA,
            "status":"COMPLETE_NEGATIVE_CONTROL_NO_REPLAY_PREDICTIVE_CLAIM",
            "forecast_commits":len(self._ids),
            "realized_scored":len(scored),
            "right_censored_no_imputation":len(censored),
            "sum_priority_mean_squared_error":fsum(
                r["priority_mean_squared_error"] for r in scored),
            "sum_random_mean_squared_error":fsum(
                r["random_mean_squared_error"] for r in scored),
            "sum_paired_loss_difference":0.0,
            "all_outcome_windows_classified":len(self._ids)==len(self._receipts),
            "source_mind_not_modified":True,
            "no_world_or_life":True,
            "observer_cpu_not_physically_billed":True,
            "no_evidence_of_replay_predictive_utility":True,
            "no_survival_or_scientific_go":True,
        }
