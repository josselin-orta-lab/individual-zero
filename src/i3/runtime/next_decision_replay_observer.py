"""External next-decision counterfactual after first funded different replay.

Two detached minds replay the same count on *one actual past learned state*.
At the following actual perception, each clone makes a decision with its
own detached, identically-funded allowance. This is NOT the living mind's
work, not a second World, not a biological counterfactual trajectory and
not a survival claim. The original random-content branch must match the
live decision exactly; otherwise this experiment fails closed.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from math import isfinite

from i3.modules.body import CognitiveBudget
from i3.modules.stage2_replay_content_selection import random_content_indices

SCHEMA = "i3-stage2.1-next-decision-content-fork-observer/v1"


def _digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                             allow_nan=False,default=str).encode()).hexdigest()


class NextDecisionReplayObserver:
    def __init__(self,mind):
        if mind.replay_gate_mode!="gate_random_content":
            raise PermissionError("only genuine GATE random-content memory selection")
        self.mind=mind
        self.event=None
        self._priority_after_td=None
        self._random_after_td=None
        self._priority_for_next=None
        self._random_for_next=None
        self._pending=None
        self.funded_opportunities=0
        self.different_opportunities=0
        self.next_observed=False

    def replay(self,selected,ranked,priorities):
        """Externally see actual funded memory selection BEFORE live TD replay."""
        k=len(selected)
        if not k:
            return None
        self.funded_opportunities+=1
        expected=random_content_indices(eligible=len(ranked),count=k,
                                        life_seed=self.mind._random_life_seed,
                                        sleep_ordinal=self.mind.content_sleep_ordinal)
        if tuple(selected)!=expected:
            raise RuntimeError("actual random memory selector changed")
        baseline=tuple(ranked[:k])
        if set(baseline)==set(expected):
            return None
        self.different_opportunities+=1
        if self.event is not None:
            return None
        common=deepcopy(self.mind)
        self._priority_after_td=deepcopy(common)
        self._random_after_td=deepcopy(common)
        for clone,indices in ((self._priority_after_td,baseline),
                              (self._random_after_td,expected)):
            for idx in indices:
                _,before,after,dead=clone.buffer[idx]
                delta=clone._td(before,after,dead)
                clone.buffer[idx]=(abs(delta),before,after,dead)
        self.event={
            "first_different_replay_ordinal":self.mind.content_sleep_ordinal,
            "same_pre_replay_state_sha256":_digest({
                "values":common.values,"buffer":list(common.buffer),
                "effects":repr(common.effects.stats),
                "history":repr(common.hist),
                "rng":repr(common.rng.getstate()),
                "budget_rng":repr(common._budget_rng.getstate())}),
            "replays_in_each_detached_copy":k,
            "priority_memory_indices":list(baseline),
            "random_memory_indices":list(expected),
            "post_priority_values_sha256":_digest(self._priority_after_td.values),
            "post_random_values_sha256":_digest(self._random_after_td.values),
            "different_learned_values":(
                self._priority_after_td.values!=self._random_after_td.values),
            "next_decision":None,
            "shared_actual_transition_td_residual":None,
        }
        return None

    def after_learning(self):
        """Join at the complete actual post-learning boundary, no Mind feedback."""
        if self.event is None or self._priority_after_td is None:
            return
        if self._priority_for_next is not None:
            raise RuntimeError("observer lifecycle called twice")
        live=self.mind
        if (self._random_after_td.values!=live.values or
                list(self._random_after_td.buffer)!=list(live.buffer)):
            raise RuntimeError("detached random TD does not match living update")
        # The live Mind has also completed automatic forgetting, if any.
        # Only TD values and replay buffer depend on memory-subset identity
        # in this frozen P1.3 update. Copy complete post-learning state and
        # replace those two learned components for the priority branch.
        self._priority_for_next=deepcopy(live)
        self._priority_for_next.values=deepcopy(self._priority_after_td.values)
        self._priority_for_next.buffer=deepcopy(self._priority_after_td.buffer)
        self._random_for_next=deepcopy(live)
        self._priority_after_td=None
        self._random_after_td=None

    def before_decision(self,cap,laws):
        """Run shadow decisions before live decide at next actual perception."""
        if self.event is None or self.next_observed:
            return None
        if self._priority_for_next is None or self._random_for_next is None:
            # A first differing replay hasn't completed learning yet.
            return None
        if self._pending is not None:
            raise RuntimeError("pending next-decision witness already exists")
        results=[]
        for clone in (self._priority_for_next,self._random_for_next):
            allowance=CognitiveBudget(cap["body"],laws)
            action,param,work,info=clone.decide(deepcopy(cap),allowance)
            if work!=allowance.work:
                raise RuntimeError("detached decision misreported funded work")
            results.append({
                "action":action,"param":param,"option":info["option"],
                "work":work,"mind":clone})
        p,r=results
        self._pending={"priority":p,"random":r,"body_before":tuple(cap["body"])}
        return None

    def after_decision(self,action,param,work,info):
        if self._pending is None:
            return None
        p,r=self._pending["priority"],self._pending["random"]
        if (r["action"],r["param"],r["option"],r["work"])!=(
                action,param,info["option"],work):
            raise RuntimeError("observer random-content next decision differs from live")
        self.event["next_decision"]={
            "priority_action":p["action"],"priority_param":p["param"],
            "priority_option":p["option"],
            "random_action":r["action"],"random_param":r["param"],
            "random_option":r["option"],
            "same_admitted_action_and_param":(
                (p["action"],p["param"])==(r["action"],r["param"])),
            "same_decision_option":p["option"]==r["option"],
            "priority_work":{
                k:getattr(p["work"],k)
                for k in ("cycles","simulated_steps","memory_items","replays")},
            "random_work":{
                k:getattr(r["work"],k)
                for k in ("cycles","simulated_steps","memory_items","replays")},
            "random_branch_matches_actual_live_decision_and_work":True,
            "observer_extra_physical_cost":False,
        }
        self.next_observed=True
        return None

    def after_outcome(self,result):
        """Evaluate same real observed transition ONLY under shared action."""
        if self._pending is None:
            return None
        p,r=self._pending["priority"],self._pending["random"]
        same=(p["action"],p["param"])==(r["action"],r["param"])
        if same and not result["dead"]:
            # This is a bootstrapped TD residual on the realized body, NOT
            # a calibrated model prediction, future-survival oracle or
            # controlled biological effect. Run strictly detached updates.
            residuals=[]
            for row in (p,r):
                clone=deepcopy(row["mind"])
                err=clone._td(self._pending["body_before"],
                              tuple(result["body"]),bool(result["dead"]))
                if not isfinite(err):
                    raise RuntimeError("nonfinite observed TD residual")
                residuals.append(err)
            self.event["shared_actual_transition_td_residual"]={
                "priority":residuals[0],"random":residuals[1],
                "same_actual_transition":True,
                "bootstrapped_not_calibrated_prediction":True,
            }
        self._pending=None
        self._priority_for_next=None
        self._random_for_next=None
        return None

    def report(self):
        if self._pending is not None:
            raise RuntimeError("incomplete shadow prediction step")
        if self.event is None:
            status="NO_DIFFERENT_FUNDED_REPLAY"
        elif self.event["next_decision"] is None:
            status="FIRST_FORK_WITHOUT_SUBSEQUENT_LIVE_DECISION"
        else:
            status="FIRST_FORK_AND_NEXT_DECISION_CAPTURED"
        return {
            "schema":SCHEMA,"status":status,
            "funded_opportunities":self.funded_opportunities,
            "different_opportunities":self.different_opportunities,
            "first_fork":self.event,
            "external_detached_work_only":True,
            "no_second_world":True,
            "no_survival_mediation_inference":True,
            "no_calibrated_predictive_accuracy_claim":True,
        }
