"""A2.38 experimental I1-only interventions, both opt-in at mortal birth.

H1 is a priced report of repeatedly unavailable planning, routed through the
unchanged GoalManager's own refractory machinery. It does NOT choose the next
goal, forge a success, or directly emit a physical command.
H2 is a separately priced decision to expose the agent to an *unknown* cell,
not a hazard classifier. It overrides D2's historical-visit abstention only
for already proposed, perceptually grounded movement and leaves Competition,
Stage9, Action Control and WorldBody completely authoritative.
"""
from __future__ import annotations

from dataclasses import replace

from .determinism import canonical_causal_bytes, sha256_hex
from .i1_d2_runtime import (
    I1WaterPrudentRuntime, DIRECTIONS, POLICY as D2_POLICY, REVIEW as D2_REVIEW,
)

H1_POLICY = "i1-a238-reconsider-unavailable-goal-v1"
H2_POLICY = "i1-a238-priced-unknown-target-commitment-v1"
H1_REVIEW = "i1_a238_unavailable_goal_review"
H2_REVIEW = "i1_a238_unknown_target_review"


class I1A238ExperimentalRuntime(I1WaterPrudentRuntime):
    """Two-factor I1 ablation with no extra action-control authority."""

    def __init__(
        self, *, i1_a238_alternate_need: bool = False,
        i1_a238_bounded_move: bool = False,
        i1_a238_need_review_uc: int = 1,
        i1_a238_move_review_uc: int = 3,
        i1_a238_max_move_reviews: int = 2,
        **kwargs,
    ):
        if type(i1_a238_alternate_need) is not bool or type(i1_a238_bounded_move) is not bool:
            raise ValueError("A2.38 factors must be explicit birth booleans")
        for value in (i1_a238_need_review_uc, i1_a238_move_review_uc,
                      i1_a238_max_move_reviews):
            if type(value) is not int or value < 1:
                raise ValueError("A2.38 UC reviews and lifetime cap must be positive integers")
        if (i1_a238_alternate_need or i1_a238_bounded_move) and (
            kwargs.get("i1_d2_prudence") is not True
            or kwargs.get("i1_model_enabled") is not True
            or kwargs.get("i1_water_learning_enabled") is not True
        ):
            raise ValueError("A2.38 requires active I1 model, water learning and D2")
        self._a238_alternate_need = i1_a238_alternate_need
        self._a238_bounded_move = i1_a238_bounded_move
        self._a238_need_uc = i1_a238_need_review_uc
        self._a238_move_uc = i1_a238_move_review_uc
        self._a238_move_cap = i1_a238_max_move_reviews
        super().__init__(**kwargs)
        # The I1-specific M11 birth contract includes these exact factor/cost
        # values, while the normative I0 contract remains byte-identical.
        self._i1_water_contract = (
            *self._i1_water_contract,
            ("a238", H1_POLICY, i1_a238_alternate_need,
             i1_a238_need_review_uc, H2_POLICY, i1_a238_bounded_move,
             i1_a238_move_review_uc, i1_a238_max_move_reviews),
        )

    def _parent_runtime_config(self, config):
        base = super()._parent_runtime_config(config)
        if not (self._a238_alternate_need or self._a238_bounded_move):
            return base
        s9 = base.stage9
        s8 = s9.stage8
        s7 = s8.stage7
        s6 = s7.stage6
        s4 = s6.stage4
        old = s4.compute_budget
        # The reserve supplies accounting capacity, not free UC. Every
        # requested review still uses _charge and writes an accepted/refused
        # canonical UC event. The agent remains subject to the per-cycle cap.
        reserve_h1 = self._a238_need_uc if self._a238_alternate_need else 0
        reserve_h2 = self._a238_move_uc if self._a238_bounded_move else 0
        budget = replace(
            old, version=old.version+"+i1-a238-factorial-v1",
            cycle_ceiling=old.cycle_ceiling+reserve_h1+reserve_h2,
            module_envelopes={
                **old.module_envelopes,
                "goal_manager": old.module_envelopes["goal_manager"]+reserve_h1,
                "competition": old.module_envelopes["competition"]+reserve_h2,
            },
            operation_costs={
                **old.operation_costs,
                **({H1_REVIEW: self._a238_need_uc} if reserve_h1 else {}),
                **({H2_REVIEW: self._a238_move_uc} if reserve_h2 else {}),
            },
        )
        return replace(base, stage9=replace(s9,stage8=replace(
            s8,stage7=replace(s7,stage6=replace(
                s6,stage4=replace(s4,compute_budget=budget))))))

    @staticmethod
    def _available_context(capture, goal):
        """Only first-person visible topology, never WorldBody private labels."""
        return sha256_hex(canonical_causal_bytes({
            "goal_type": goal.goal_type,
            "target": goal.target,
            "position": [capture.x, capture.y],
            "current_water_source": capture.current_water_source,
            "current_resources": list(capture.current_resources),
            "adjacent": [
                [n.direction, n.passable, n.water_source, list(n.resources)]
                for n in capture.adjacent
            ],
        }))

    def _propose_for_cycle(
        self, *, capture, goal_for_planning, st_before_cycle, cycle,
    ):
        result = super()._propose_for_cycle(
            capture=capture, goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle, cycle=cycle,
        )
        if not self._a238_alternate_need or goal_for_planning is None:
            return result
        active = self.goal_manager.active_goal
        if active is None or active.id != goal_for_planning.id:
            return result
        if result is not None:
            return result
        paid = self._charge(module="goal_manager", operation=H1_REVIEW)
        if not paid:
            self._write(kind="i1_a238_need_reconsideration", cycle=cycle,
                        data={"policy": H1_POLICY, "goal_ref": active.id,
                              "decision": "no_uc", "paid": False})
            return result
        context = self._available_context(capture, active)
        # Existing GoalManager chooses whether enough comparable failures
        # warrant its ordinary temporary refractory interval. No alternate
        # goal is selected here: pressure ordering and hysteresis still own it.
        released = self.goal_manager.note_non_plannable(
            material_context_hash=context, t_monde=capture.t_monde,
        )
        self._write(kind="i1_a238_need_reconsideration", cycle=cycle, data={
            "policy": H1_POLICY, "goal_ref": active.id,
            "visible_context_sha256": context,
            "reason": "no_permitted_plan_from_current_first_person_view",
            "decision": "ordinary_goal_refractory" if released else "retain_and_recheck",
            "paid": True, "secondary_goal_forced": False,
            "success_claimed": False,
        })
        if released:
            self.planning.invalidate_current()
            self.competition.prune_invalid(active_goal_id=None, t_monde=capture.t_monde)
        return result

    def _lived_review_receipts(self):
        """Read the durable personal journal only, never external lab truth."""
        for entry in self.journal.entries:
            event = entry.causal_event
            if event.get("kind") == "i1_a238_unknown_commitment_review":
                yield event.get("data", {})

    def _register_option_proposal(
        self, *, proposal, active_goal_id, t_monde, cycle,
    ):
        if not self._a238_bounded_move or not self._d2_prudence:
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle,
            )
        if (self._water_learner.observed_water_gain is None
                or proposal.plan is None or not proposal.plan.steps
                or proposal.plan.steps[0].command.primitive != "se_deplacer"):
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle,
            )
        capture = self.stage3._capture
        if capture is None or capture.t_monde != t_monde:
            raise RuntimeError("A2.38 risk review requires authorized perception")
        command = proposal.plan.steps[0].command
        direction = command.parameters.get("direction")
        if direction not in DIRECTIONS:
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle,
            )
        dx, dy = DIRECTIONS[direction]
        target = (capture.x+dx, capture.y+dy)
        geo = self.exploration.geographic
        visits = () if geo is None else geo.export_causal_state()["visits"]
        past = frozenset((int(v[0]),int(v[1])) for v in visits)
        if target in past:
            # Previously visited is not a guarantee of unchanged conditions.
            # D2 retains its original paid semantics for these locations.
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle,
            )

        # H2 can act only upon an authentic candidate already proposed for
        # the actually active need, never synthesize an action.
        if proposal.option.goal_ref != active_goal_id or active_goal_id is None:
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle,
            )
        current_goal = self.goal_manager.active_goal
        if current_goal is None or current_goal.id != active_goal_id:
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle,
            )
        neighbor = next((n for n in capture.adjacent
                         if n.direction == direction and n.passable), None)
        if neighbor is None:
            return super()._register_option_proposal(
                proposal=proposal, active_goal_id=active_goal_id,
                t_monde=t_monde, cycle=cycle,
            )
        # Material opportunity must be visible and relevant to the present
        # need; visible berries are not a guarantee that eating is safe.
        relevant = ((current_goal.goal_type == "eat" and bool(neighbor.resources))
                    or (current_goal.goal_type == "drink" and neighbor.water_source))
        physical = capture.body
        move_cost = float(self.world.config.action_energy_costs["se_deplacer"])
        reserve = (float(physical["energy"]) - move_cost >= 2 * move_cost
                   and float(physical["water"]) >=
                   float(self._stage10_config.critical_body_thresholds["water"])
                   and float(physical["integrity"]) >
                   float(self.stage3.control._config.protected_integrity_threshold))
        # Reserve limits are an explicit experimenter constraint, NEVER
        # a learned classifier or a claim that a novel cell is harmless.
        matching = [r for r in self._lived_review_receipts()
                    if r.get("option_ref") == proposal.option.id
                    and r.get("world_step") == t_monde]
        if matching:
            permitted = matching[-1].get("decision") == "commit_unknown"
        else:
            accepted = sum(
                r.get("decision") == "commit_unknown"
                for r in self._lived_review_receipts())
            d2_paid = self._charge(module="competition", operation=D2_REVIEW)
            h2_paid = (self._charge(module="competition", operation=H2_REVIEW)
                       if d2_paid and accepted < self._a238_move_cap
                       and relevant and reserve else False)
            permitted = bool(d2_paid and h2_paid and relevant and reserve
                             and accepted < self._a238_move_cap)
            self._write(kind="i1_d2_movement_commitment_review", cycle=cycle, data={
                "policy": D2_POLICY, "option_ref": proposal.option.id,
                "world_step": t_monde, "origin": [capture.x,capture.y],
                "destination": list(target), "prior_physical_visit": False,
                "review_uc_paid": d2_paid,
                "decision": "delegated_to_i1_a238_risk_review",
                "learned_positive_water_effect": True,
                "hidden_safety_claim": False, "current_safety_known": False,
                "oracle_or_bench_used": False,
            })
            self._write(kind="i1_a238_unknown_commitment_review", cycle=cycle,
                        data={
                            "policy": H2_POLICY, "option_ref": proposal.option.id,
                            "world_step": t_monde, "goal_ref": active_goal_id,
                            "destination": list(target),
                            "visible_opportunity": relevant,
                            "pressure": current_goal.current_pressure,
                            "perceptual_target_water": neighbor.water_source,
                            "perceptual_target_resources": list(neighbor.resources),
                            "novel_target": True, "safety_known": False,
                            "fatal_outcome_possible": True,
                            "energy_after_nominal_move": float(physical["energy"])-move_cost,
                            "conservative_resource_reserve": reserve,
                            "prior_commitment_receipts": accepted,
                            "d2_uc_paid": d2_paid, "extra_uc_paid": h2_paid,
                            "decision": "commit_unknown" if permitted else "abstain",
                            "hidden_world_queried": False,
                        })
        if not permitted:
            self.competition.invalidate_candidate(proposal.option.id)
            self.stage3.control.clear_option_step(proposal.option.id)
            return False
        # Skip ONLY the D2 historical-visit veto after the explicitly
        # journaled override. The normal Stage6 -> Competition -> Action
        # Control pathway still decides whether an action occurs at all.
        return super(I1WaterPrudentRuntime, self)._register_option_proposal(
            proposal=proposal, active_goal_id=active_goal_id,
            t_monde=t_monde, cycle=cycle,
        )
