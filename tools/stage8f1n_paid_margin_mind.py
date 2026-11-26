"""F1N opt-in personally paid confidence margin, frozen F1J round logic.

Only F1N DEV transport may instantiate this subclass for development roots.
The original F1J class, P1.3 Mind, BodyLaws and scientific F1M remain unchanged.
No privileged WorldSpec/observer information enters the individual's policy.
"""
from __future__ import annotations

from math import sqrt,tanh

from i3.modules.body import CognitiveBudget, CognitiveWork, CognitiveFundingError
from i3.modules.mind import GAIN,LEAK,RESIDUAL,THRESHOLD
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind


class F1NMarginMind(F1JFixedRoundMind):
    """One exact genuine paid T5 margin, optionally read at one T6 decision."""

    def __init__(self,genome:dict,life_seed:int):
        super().__init__(genome,life_seed)
        self.f1n_owned_margin=None
        self.f1n_pending_margin=None
        self.f1n_mode="off"
        self.f1n_read_used=False

    def arm_paid_t6_read(self,mode:str):
        if mode not in ("margin","masked") or self.f1n_mode!="off" or self.f1n_read_used:
            raise ValueError("invalid or repeated F1N T6 readout")
        if self.f1n_owned_margin is None:
            raise ValueError("the individual must have paid for its own T5 margin")
        self.f1n_mode=mode

    def _compete(self, scored, cycles, budget=None):
        if not scored or type(cycles) is not int or cycles<1:
            raise ValueError("F1J requires native scored alternatives and positive round limit")
        vals=[score for _,score in scored]
        avg=sum(vals)/len(vals)
        sd=sqrt(sum((x-avg)**2 for x in vals)/len(vals))
        evidence={option:(tanh((score-avg)/sd) if sd>1e-9 else 0.0)
                  for option,score in scored}
        accumulated={option:self.acc.get(option,0.0) for option,_ in scored}
        initial_acc=dict(accumulated)
        # Only on the PRE-ALLOCATED T6 fork; authorize memory read before use.
        mode=self.f1n_mode
        owned=None
        if mode in ("margin", "masked"):
            if budget is None or not budget.try_spend(CognitiveWork(memory_items=1)):
                raise CognitiveFundingError("F1N T6 real memory read unfunded")
            if self.f1n_read_used:
                raise ValueError("F1N own margin already consumed on prior decision")
            owned=self.f1n_owned_margin
            if (type(owned) is not dict or
                    set(owned)!={"key", "q", "source_tick"} or
                    owned["source_tick"] != 5 or
                    type(owned["key"]) is not str or
                    type(owned["q"]) is not float or
                    not 0.0 <= owned["q"] <= 1.0):
                raise ValueError("F1N no authentic paid personal margin")
        # A consumed read cannot be used again at T7, even after a veto.
        self.f1n_mode="off"
        if owned is not None:
            self.f1n_read_used=True
        thresholds={
            option:THRESHOLD*(1.0-self.inertia if option==self.intention else 1.0)
            for option,_ in scored
        }
        # Identity and amplitude come solely from the individual's own
        # privately stored T5 margin, never from a laboratory observer record.
        applied_q=(owned["q"] if mode=="margin" else 0.0) if owned else 0.0
        effective_key=(owned["key"] if owned else None)
        if effective_key in thresholds:
            thresholds[effective_key]*=(1.0-0.5*applied_q)
        witnesses=[]
        used=0
        for _ in range(cycles):
            # Authorize each round BEFORE it runs. No fake work to equalize a
            # cheaper branch, and no score-sensitive stopping condition.
            if budget is not None and not budget.try_spend(CognitiveWork(cycles=1)):
                break
            for option,_ in scored:
                accumulated[option]=max(
                    0.0,(1.0-LEAK)*accumulated[option]+GAIN*evidence[option]
                )
            used+=1
            # Every cycle has applied the original substantive evidence
            # update to ALL scored alternatives, not a padded no-op.
            witnesses.append(dict(accumulated))

        crossed=[
            ((accumulated[option]-thresholds[option])/thresholds[option],option)
            for option,_ in scored
            if accumulated[option]>=thresholds[option]
        ]
        if crossed:
            highest=max(m for m,_ in crossed)
            ties=sorted(option for m,option in crossed if m==highest)
            mechanism="final_round_threshold"
        else:
            best_activation=max(accumulated.values())
            ties=sorted(k for k,v in accumulated.items()
                        if v>=best_activation-1e-12)
            if len(ties)==len(scored) and max(accumulated.values())-min(accumulated.values())<=1e-12:
                max_score=max(vals)
                ties=sorted(option for option,score in scored
                            if score>=max_score-1e-12)
                mechanism="all_activations_equal_raw_score_fallback"
            else:
                mechanism="final_round_activation"

        # The Mind itself owns tie resolution, intention and its random state.
        # The laboratory does NOT select any actual bodily motor command.
        winner=self._tie(ties)
        # Own final native T5 confidence is pending, not yet stored for free.
        # It becomes memory ONLY after the genuine action/learning and
        # the separate real paid write in the native transport.
        others=[(accumulated[k]-thresholds[k])/thresholds[k]
                for k in accumulated if k!=winner]
        valid=(len(others)>0 and accumulated[winner]>=thresholds[winner])
        gap=((accumulated[winner]-thresholds[winner])/thresholds[winner]
             -max(others)) if valid else 0.0
        q=min(1.0,max(0.0,gap))
        self.f1n_pending_margin={"key":winner,"q":float(q),
                                 "crossed":bool(valid),
                                 "paid_rounds":used}
        before_residual=dict(accumulated)
        for option in accumulated:
            accumulated[option]=(
                0.0 if option==winner else accumulated[option]*RESIDUAL
            )
        self.acc=accumulated
        if self.observer_full_competition:
            self._observer_competition={
                "scored_order":[option for option,_ in scored],
                "prior_intention":self.intention,
                "accumulators_before":initial_acc,
                "normalized_evidence":dict(evidence),
                "thresholds":thresholds,
                "f1n_margin_read":{
                    "mode":mode,"own_key":effective_key,
                    "own_q":owned["q"] if owned else None,
                    "applied_q":applied_q,
                    "own_key_scored":effective_key in thresholds,
                    "memory_read_paid":owned is not None},
                "round_capacity_from_actual_body":cycles,
                "paid_competition_cycles":used,
                "actual_substantive_round_snapshots":witnesses,
                "budget_blocked_before_full_round_capacity":used<cycles,
                "selection_mechanism":mechanism,
                "tie_candidates":ties,
                "winner_before_control":winner,
                "accumulators_before_residual":before_residual,
                "accumulators_after_residual":dict(accumulated),
            }
        return winner,used