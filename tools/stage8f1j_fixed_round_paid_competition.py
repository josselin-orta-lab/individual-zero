"""F1J opt-in fixed-round substantive evidence accumulation.

Exact scope: *only* override Mind._compete early stopping. Every paid round
genuinely integrates every scored option's evidence, even once a threshold
was previously crossed. Self-chosen action still goes through Mind._admit;
no experimenter policy/action, no posthoc work padding, no engine edit.
The P1.3 reference Mind and frozen F1I outcomes are NEVER modified.
This class is NOT imported/accepted by run_life and creates no births.
"""
from __future__ import annotations

from math import sqrt, tanh

from i3.modules.body import CognitiveWork
from i3.modules.mind import Mind, GAIN, LEAK, RESIDUAL, THRESHOLD


class F1JFixedRoundMind(Mind):
    """Development-only new decision method with complete paid evidence rounds."""

    def __init__(self, genome: dict, life_seed: int):
        super().__init__(
            genome,life_seed,observer_full_competition=True,
        )

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
        thresholds={
            option:THRESHOLD*(1.0-self.inertia if option==self.intention else 1.0)
            for option,_ in scored
        }
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
