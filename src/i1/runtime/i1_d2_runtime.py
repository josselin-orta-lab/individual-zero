"""I1 D2: explicitly priced abstention on unvisited cognitive movement.

No world truth or independent dispatch. Stage11 Exploration's physical visit
ledger is only a past observation, NOT a safety certification.
"""
from __future__ import annotations
from dataclasses import replace
from i1.interfaces import PrimitiveCommand
from .i1_water_runtime import I1WaterLearningRuntime

REVIEW="i1_water_unknown_move_review"
POLICY="i1-d2-past-visit-commitment-v1"
DIRECTIONS={"north":(0,-1),"south":(0,1),"east":(1,0),"west":(-1,0)}


class I1WaterPrudentRuntime(I1WaterLearningRuntime):
    def __init__(self, *, i1_d2_prudence: bool=False,
                 i1_d2_review_uc: int=1, **kwargs):
        if type(i1_d2_prudence) is not bool or (
                type(i1_d2_review_uc) is not int or i1_d2_review_uc<1):
            raise ValueError("D2 risk review must be birth-frozen and positively priced")
        if i1_d2_prudence and kwargs.get("i1_water_learning_enabled") is not True:
            raise ValueError("D2 review requires the living water model")
        self._d2_prudence=i1_d2_prudence
        self._d2_review_uc=i1_d2_review_uc
        super().__init__(**kwargs)
        self._i1_water_contract=(*self._i1_water_contract,
            ("d2_policy",POLICY,i1_d2_prudence,i1_d2_review_uc))

    def _parent_runtime_config(self, config):
        base=super()._parent_runtime_config(config)
        if not self._d2_prudence:
            return base
        s9=base.stage9;s8=s9.stage8;s7=s8.stage7;s6=s7.stage6;s4=s6.stage4
        old=s4.compute_budget
        # Budget for bounded Stage11+water proposals in the current cycle.
        reserve=12*self._d2_review_uc
        budget=replace(old,version=old.version+"+"+POLICY,
            cycle_ceiling=old.cycle_ceiling+reserve,
            module_envelopes={**old.module_envelopes,
                "competition":old.module_envelopes["competition"]+reserve},
            operation_costs={**old.operation_costs,REVIEW:self._d2_review_uc})
        return replace(base,stage9=replace(s9,stage8=replace(s8,
            stage7=replace(s7,stage6=replace(s6,
                stage4=replace(s4,compute_budget=budget))))))

    def _register_option_proposal(self, *,proposal,active_goal_id,t_monde,cycle):
        if (not self._d2_prudence
                or self._water_learner.observed_water_gain is None
                or proposal.plan is None or not proposal.plan.steps
                or proposal.plan.steps[0].command.primitive!="se_deplacer"):
            return super()._register_option_proposal(
                proposal=proposal,active_goal_id=active_goal_id,
                t_monde=t_monde,cycle=cycle)
        current=self.stage3._capture
        if current is None or current.t_monde!=t_monde:
            raise RuntimeError("D2 requires unique authorized step capture")
        direction=proposal.plan.steps[0].command.parameters.get("direction")
        if direction not in DIRECTIONS:
            raise ValueError("D2 refuses malformed movement direction")
        dx,dy=DIRECTIONS[direction]
        target=(current.x+dx,current.y+dy)
        # Stage11 geography is optional.  Its absence cannot provide a
        # positive visit receipt.  Abstain normally instead of raising after
        # an otherwise valid first-person water-learning proposal.
        geography=self.exploration.geographic
        visits=(geography.export_causal_state()["visits"]
                if geography is not None else ())
        past=frozenset((int(v[0]),int(v[1])) for v in visits)
        paid=self._charge(module="competition",operation=REVIEW)
        previously_visited=target in past
        permitted=paid and previously_visited
        self._write(kind="i1_d2_movement_commitment_review",cycle=cycle,data={
            "policy":POLICY,"option_ref":proposal.option.id,"world_step":t_monde,
            "origin":[current.x,current.y],"destination":list(target),
            "prior_physical_visit":previously_visited,
            "review_uc_paid":paid,"decision":"permit_historically_visited"
                if permitted else "defer_unknown_or_unfunded",
            "learned_positive_water_effect":True,
            "hidden_safety_claim":False,"current_safety_known":False,
            "oracle_or_bench_used":False,
        })
        if not permitted:
            self.competition.invalidate_candidate(proposal.option.id)
            self.stage3.control.clear_option_step(proposal.option.id)
            return False
        return super()._register_option_proposal(
            proposal=proposal,active_goal_id=active_goal_id,
            t_monde=t_monde,cycle=cycle)
