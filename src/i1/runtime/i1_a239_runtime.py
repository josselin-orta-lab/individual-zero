"""A2.39 I1-only priced, uncertain pre-water movement; no motor authority.

Strict D2 deliberately exposes the legacy pre-water review gap.
The food-first H2 factor permits an *existing* Stage6 food candidate only
after paid review, under an unknown lethal outcome; all existing Competition,
Stage9, Action Control and real WorldBody gates remain unchanged.
"""
from __future__ import annotations

from dataclasses import replace

from .i1_a238_runtime import I1A238ExperimentalRuntime
from .i1_d2_runtime import (
    I1WaterPrudentRuntime, DIRECTIONS, POLICY as D2_POLICY,
    REVIEW as D2_REVIEW,
)

POLICY = "i1-a239-food-first-risk-reviewed-v1"
STRICT_POLICY = "i1-a239-strict-prewater-d2-v1"
RISK_REVIEW = "i1_a239_food_first_risk_review"


class I1A239ExperimentalRuntime(I1A238ExperimentalRuntime):
    """A2.39 five-arm birth-frozen descendant, never modifies I0."""

    individual_id = "i1-a239-experimental"

    def __init__(
        self, *,
        i1_a239_strict_unknown: bool = False,
        i1_a239_food_first_risk: bool = False,
        i1_a239_d2_uc: int = 1,
        i1_a239_risk_uc: int = 3,
        i1_a239_max_commitments: int = 2,
        **kwargs,
    ):
        if (type(i1_a239_strict_unknown) is not bool
                or type(i1_a239_food_first_risk) is not bool):
            raise ValueError("A2.39 flags must be explicit booleans")
        if i1_a239_food_first_risk and not i1_a239_strict_unknown:
            raise ValueError("A2.39 food-first H2 requires strict pre-water D2")
        if any(type(x) is not int or x < 1 for x in
               (i1_a239_d2_uc, i1_a239_risk_uc,
                i1_a239_max_commitments)):
            raise ValueError("A2.39 priced costs and cap are positive integers")
        if (i1_a239_strict_unknown and (
                kwargs.get("i1_d2_prudence") is not True
                or kwargs.get("i1_model_enabled") is not True
                or kwargs.get("i1_water_learning_enabled") is not True
                or kwargs.get("i1_a238_bounded_move") is True
                or kwargs.get("i1_d2_review_uc") != i1_a239_d2_uc)):
            raise ValueError("A2.39 active prior and D2 contracts not aligned")
        self._a239_strict_unknown = i1_a239_strict_unknown
        self._a239_food_first_risk = i1_a239_food_first_risk
        self._a239_d2_uc = i1_a239_d2_uc
        self._a239_risk_uc = i1_a239_risk_uc
        self._a239_cap = i1_a239_max_commitments
        super().__init__(**kwargs)
        # M11 hashes the actual I1 frozen birth fields, not just a runtime
        # label. The I0 source and canonical safety executor are untouched.
        self._i1_water_contract = (
            *self._i1_water_contract,
            ("a239", STRICT_POLICY, i1_a239_strict_unknown, i1_a239_d2_uc,
             POLICY, i1_a239_food_first_risk, i1_a239_risk_uc,
             i1_a239_max_commitments),
        )

    def _parent_runtime_config(self, config):
        base = super()._parent_runtime_config(config)
        if not self._a239_food_first_risk:
            return base
        s9 = base.stage9
        s8 = s9.stage8
        s7 = s8.stage7
        s6 = s7.stage6
        s4 = s6.stage4
        old = s4.compute_budget
        cost = self._a239_risk_uc
        budget = replace(
            old, version=old.version+"+"+POLICY,
            cycle_ceiling=old.cycle_ceiling+cost,
            module_envelopes={
                **old.module_envelopes,
                "competition": old.module_envelopes["competition"]+cost,
            },
            operation_costs={**old.operation_costs, RISK_REVIEW: cost},
        )
        return replace(base,stage9=replace(s9,stage8=replace(
            s8,stage7=replace(s7,stage6=replace(
                s6,stage4=replace(s4,compute_budget=budget))))))

    def _prior_reviews(self):
        # The journal is the life-local causal owner. No operator/Oracle lookup.
        for entry in self.journal.entries:
            event = entry.causal_event
            if event.get("kind") == "i1_a239_prewater_unknown_review":
                yield event.get("data", {})

    def _register_option_proposal(
        self, *, proposal, active_goal_id, t_monde, cycle,
    ):
        if (not self._a239_strict_unknown
                or self._water_learner.observed_water_gain is not None
                or proposal.plan is None or not proposal.plan.steps
                or proposal.plan.steps[0].command.primitive != "se_deplacer"
                or active_goal_id is None
                or proposal.option.goal_ref != active_goal_id):
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle)
        capture = self.stage3._capture
        if capture is None or capture.t_monde != t_monde:
            raise RuntimeError("A2.39 prewater requires sole authorized capture")
        direction = proposal.plan.steps[0].command.parameters.get("direction")
        if direction not in DIRECTIONS:
            raise ValueError("A2.39 invalid proposed direction")
        dx,dy = DIRECTIONS[direction]
        target = (capture.x+dx,capture.y+dy)
        geo = self.exploration.geographic
        visits = () if geo is None else geo.export_causal_state()["visits"]
        past = frozenset((int(v[0]),int(v[1])) for v in visits)
        if target in past:
            # Historical visit is observation, never an immutable safety fact.
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle)
        neighbour = next((n for n in capture.adjacent
                          if n.direction==direction and n.passable),None)
        goal = self.goal_manager.active_goal
        eligible = bool(
            self._a239_food_first_risk and neighbour is not None
            and goal is not None and goal.id == active_goal_id
            and goal.goal_type == "eat"
            and "berry_b" in neighbour.resources
        )
        # Fixed conservative *resource* reserve, never an unseen risk estimate.
        move_cost = float(self.world.config.action_energy_costs["se_deplacer"])
        reserve = bool(
            float(capture.body["energy"]) - move_cost >= 2*move_cost
            and float(capture.body["water"]) >=
                float(self._stage10_config.critical_body_thresholds["water"])
            and float(capture.body["integrity"]) >
                float(self.stage3.control._config.protected_integrity_threshold)
        )
        receipts = list(self._prior_reviews())
        match = next((r for r in reversed(receipts)
                      if r.get("option_ref")==proposal.option.id
                      and r.get("world_step")==t_monde),None)
        if match is not None:
            permit = match.get("decision")=="commit_unknown"
        else:
            previous = sum(r.get("decision")=="commit_unknown"
                           for r in receipts)
            d2_paid = self._charge(module="competition",operation=D2_REVIEW)
            h2_paid = bool(
                d2_paid and eligible and reserve
                and previous < self._a239_cap
                and self._charge(module="competition",operation=RISK_REVIEW)
            )
            permit = bool(d2_paid and h2_paid and eligible and reserve)
            self._write(kind="i1_d2_movement_commitment_review",
                        cycle=cycle, data={
                "policy":STRICT_POLICY,"option_ref":proposal.option.id,
                "world_step":t_monde,
                "origin":[capture.x,capture.y],
                "destination":list(target),
                "prior_physical_visit":False,
                "learned_positive_water_effect":False,
                "review_uc_paid":d2_paid,
                "decision":("delegated_to_i1_a239_risk_review"
                            if eligible else "defer_unknown_or_unfunded"),
                "hidden_safety_claim":False,"current_safety_known":False,
                "oracle_or_bench_used":False,
            })
            self._write(kind="i1_a239_prewater_unknown_review",
                        cycle=cycle, data={
                "policy":POLICY if self._a239_food_first_risk else STRICT_POLICY,
                "option_ref":proposal.option.id,"world_step":t_monde,
                "goal_ref":active_goal_id,
                "destination":list(target),
                "first_person_berry_visible":bool(neighbour and
                                                   "berry_b" in neighbour.resources),
                "eligible":eligible,"resource_reserve":reserve,
                "prior_commitments":previous,
                "d2_uc_paid":d2_paid,"extra_uc_paid":h2_paid,
                "decision":"commit_unknown" if permit else "abstain",
                "safety_known":False,"fatal_outcome_possible":True,
                "hidden_world_queried":False,
            })
        if not permit:
            self.competition.invalidate_candidate(proposal.option.id)
            self.stage3.control.clear_option_step(proposal.option.id)
            return False
        # The only bypass is D2's historical-visit veto. The unchanged
        # upstream Stage6 registration/Competition/Stage9/Action Control
        # are still required for the physical command.
        return super(I1WaterPrudentRuntime,self)._register_option_proposal(
            proposal=proposal,active_goal_id=active_goal_id,
            t_monde=t_monde,cycle=cycle)
