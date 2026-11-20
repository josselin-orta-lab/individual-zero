"""Stage8-F1 DEVELOPMENT-ONLY paid microdecision candidate, not a life policy.

Never imported or admitted by run_life: NO births, no scientific claim.
The reference Mind/World/BodyLaws and frozen Stage8-E2 roots are unchanged.

The candidate can only run after the existing P1.3 *initial* cognitive bill
was declined without spending anything. It prepays a bounded single model
block before it reads personal learned effects or evaluates options. Only
capture() first-person affordances, the individual's innate distress/genes
and its own learned effect predictions may determine the motor choice.
Abstention is a real, PAID choice; sleep is NEVER an override.

This is NOT a full policy. It excludes token operations, exploration and
learning during its reduced decision branch until separately specified.
"""
from __future__ import annotations

from math import isfinite

from .body import ACTION_COSTS, CognitiveBudget, CognitiveWork, E, F, W, I, V
from .mind import Mind
from .world import DIRECTIONS

# Fixed maximum of seven model queries: sleep, wait, drink, four adjacent moves.
# The 64 memory items cover 5 body channels, 15 innate distress parameters,
# up to seven five-channel learned effects, up to four neighbors and local
# score/control bookkeeping. One pre-authorized model block; no simulation,
# search, memory writes, free replay, phantom learning or hidden World data.
MICRO_WORK = CognitiveWork(cycles=1, memory_items=64)
EVIDENCE = "STAGE8_F1_DEVELOPMENT_ONLY_NOT_NATIVE_ADMISSION"
CANDIDATE = "stage8f1-paid-learnt-local-effect-microdecision/v0"


class PaidMicrodecisionMind(Mind):
    """Opt-in engineering subclass, intentionally NOT wired to runtime/lives."""

    def decide(self, cap, budget: CognitiveBudget):
        action, param, work, info = super().decide(cap, budget)
        if info["funding"] != "NO_PROCESSING_BUDGET":
            # The historical P1.3 decision, cost and authority are untouched.
            return action, param, work, info
        if work != CognitiveWork() or budget.work != CognitiveWork():
            raise RuntimeError("fallback cannot follow any previously paid work")
        return self._development_microdecision(cap, budget)

    def _development_microdecision(self, cap, budget: CognitiveBudget):
        if (type(cap) is not dict or type(budget) is not CognitiveBudget
                or tuple(cap["body"]) != budget.body
                or budget.work != CognitiveWork()):
            raise ValueError("fresh first-person and unfunded allowance required")
        body=budget.body
        if any(body[c] <= 0.0 for c in (F,W,I)):
            raise ValueError("no cognitive choice after vital zero/death")
        # Prepayment must precede learned belief access and score production.
        # If even this work is unaffordable, the old None behavior remains.
        if not budget.try_spend(MICRO_WORK):
            return None, None, budget.work, {
                "funding":"NO_PROCESSING_BUDGET",
                "option":None, "candidate":CANDIDATE,
                "experimental":EVIDENCE}
        cap_here=cap.get("here")
        neighbors=cap.get("neighbors")
        if (type(cap_here) not in (tuple,list) or len(cap_here)!=2
                or type(neighbors) not in (tuple,list)
                or len(neighbors)!=len(DIRECTIONS)):
            raise ValueError("invalid first-person capture after paid read")
        remaining=budget.remaining
        # Motor admission uses the actually EXECUTED historical sleep physics,
        # which has zero motor debit, not the nominal .25 action table.
        # Absolutely no automatic sleep, food, energy or vigilance injection.
        offered=[("dormir","dormir",None,("dormir",))]
        if remaining[E] >= ACTION_COSTS["attendre"]:
            offered.append(("attendre","attendre",None,("attendre",)))
        if cap_here[0] and remaining[E] >= ACTION_COSTS["boire"]:
            offered.append(("boire","boire",None,("boire",)))
        if remaining[E] >= ACTION_COSTS["se_deplacer"]:
            for (direction,_,_),cell in zip(DIRECTIONS,neighbors):
                if cell is not None:
                    offered.append(("move:"+direction, "se_deplacer",direction,
                                    ("se_deplacer",)))
        if len(offered)>7:
            raise RuntimeError("bounded micro-memory access exceeded")
        # A legitimate paid abstention has no claimed passive-world forecast:
        # it anchors the comparison at the individual's current bodily need.
        # Even if the only motor-admissible action is sleep, abstain can win.
        baseline = -self.distress(self.feats(remaining))
        winner=None
        winner_score=baseline
        for oid,action,param,key in offered:
            delta,uncertainty=self._read_plan_prediction(key)
            if (type(delta) not in (tuple,list) or len(delta)!=5
                    or any(type(v) not in (int,float) or not isfinite(v)
                           for v in delta)
                    or type(uncertainty) not in (int,float)
                    or not isfinite(uncertainty) or uncertainty<0):
                raise ValueError("unverified personal outcome forecast")
            predicted=tuple(max(0.,min(100.,remaining[i]+delta[i]))
                            for i in range(5))
            # All values come from the individual's own learned effect model,
            # and all stakes/weights from its personal genome. No sleep bonus
            # or laboratory survival target is smuggled into the score.
            value=-self.distress(self.feats(predicted))
            if any(predicted[c]<=0 for c in (F,W,I)):
                value-=self.d_max
            # On ties, the individual may abstain; no extrinsic action rescue.
            if value>winner_score+1e-12:
                winner=(oid,action,param,key)
                winner_score=value
        if winner is None:
            self.last=None
            return None,None,budget.work,{
                "funding":"F1_PAID_VOLUNTARY_ABSTENTION",
                "option":"abstain", "candidate":CANDIDATE,
                "experimental":EVIDENCE,
                "offered_motor_options":len(offered),
                "paid_model_cycles":MICRO_WORK.cycles}
        oid,action,param,key=winner
        self.last=(body,key,action,param)
        self.intention=oid
        return action,param,budget.work,{
            "funding":"F1_PAID_SELF_SELECTED_ACTION",
            "option":oid, "candidate":CANDIDATE,
            "experimental":EVIDENCE,
            "offered_motor_options":len(offered),
            "paid_model_cycles":MICRO_WORK.cycles}
