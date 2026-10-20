"""I1-only birth-opted experimental Stage12 runtime.

This is NOT the I0 runtime and not a second command authority. It may propose
one uncertain, first-person grounded move/collection when the exact Stage6
equipment is incomplete. An independently opted-in I1 affordance policy may
consider a physically available action without predicting its unknown effects.
A sealed external visible-delta model is an inherited
EXPERIMENTAL PRIOR, never masquerading as the I1 individual's lived memories.
No hidden physics, Oracle, postmortem observations or terminal certifications.

The fully configured opt-in is pinned in I1's M11 runtime-contract digest.
Its sole private pending proposal is cleared at the next real step boundary.
"""
from __future__ import annotations

from dataclasses import replace
from math import isfinite

from i1.contracts import (
    EvaluationOption, MotiveRef, Option, OptionProposal, Plan, PlanStep,
    PredictedConsequence,
)
from i1.equipment import SimulationState
from i1.experimental.stage6_visible_delta_shadow import (
    MODEL_VERSION, ShadowVisibleDeltaModel,
)
from i1.interfaces import PrimitiveCommand
from i1.modules.competition import OptionEvidenceInput
from i1.modules.simulator import state_from_capture

from .determinism import canonical_causal_bytes, sha256_hex
from .stage12_runtime import Stage12Runtime
from .i1_lived_recall import POLICY as RECALL_POLICY, matched_collection_recall
from .stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY
from .stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY


I1_POLICY = "i1-stage6-live-partial-prebirth-v1"
I1_SCORE = 0.35  # fixed *instrumental preference*, NOT predicted E_sim
I1_EXPERIMENTAL_OPERATION = "i1_partial_model_forecast"
I1_AFFORDANCE_POLICY = "i1-unknown-action-affordance-v2-general-local"
I1_AFFORDANCE_OPERATION = "i1_unknown_action_consider"
I1_OPPORTUNISTIC_ACTIONS = frozenset(("boire", "manger", "collecter", "poser_une_pierre", "fabriquer_outil"))
I1_OPPORTUNISTIC_POLICY = "i1-local-interaction-goal-independent-v2"



def _local_q_visibility(exposure: str) -> tuple[bool, bool]:
    """Research-only factorial Q access: (candidate rank, Competition evidence).

    Q/TD learning itself is ALWAYS active. No action gain, species, risk,
    hydration expectation or motor privilege is introduced by this selector.
    """
    policies = {
        "neutral": (False, False),
        "rank_only": (True, False),
        "evidence_only": (False, True),
        "learned": (True, True),
    }
    if type(exposure) is not str or exposure not in policies:
        raise ValueError("invalid I1 independent-local Q exposure")
    return policies[exposure]


def _local_interaction_choices(available, *, enabled):
    """Only executable local actions, never a map or anticipated need relief.

    Planning's canonical candidate_commands has already established physical
    executability from this individual's local Perception state. This helper
    never inspects an entity type, guesses nutritional value, or chooses a
    motor. It is an opt-in *candidate expansion* only.
    """
    if type(enabled) is not bool:
        raise ValueError("local interaction research flag must be boolean")
    if not enabled:
        return ()
    return tuple(command for command in available
                 if command.primitive in I1_OPPORTUNISTIC_ACTIONS)


class I1PartialEvidenceAdapter:
    """Stage8's existing Competition path; never fakes a full rollout."""

    def __init__(self, underlying, pending: dict[str, object]):
        self._underlying = underlying
        self._pending = pending

    def __getattr__(self, key):
        # Never forward copy/pickle protocol methods from the wrapped owner.
        # They must operate on this adapter, not a foreign instance.
        if key.startswith("__"):
            raise AttributeError(key)
        # deepcopy constructs an empty shell before restoring its __dict__.
        # Never recursively call __getattr__ while _underlying is absent.
        underlying = vars(self).get("_underlying")
        if underlying is None:
            raise AttributeError(key)
        return getattr(underlying, key)

    def evaluate(self, *, proposal, **kwargs):
        provenance = proposal.option.provenance
        pending = self._pending
        local = pending.get("local_opportunity_evidence")
        if (provenance == "i1_unknown_affordance"
                and isinstance(local, dict)
                and proposal.option.id == local.get("option_ref")):
            pending = local
        if (proposal.option.id != pending.get("option_ref")
                or proposal.plan is None
                or len(proposal.plan.steps) != 1
                or provenance not in ("i1_partial_experiment",
                                      "i1_unknown_affordance")
                or kwargs.get("t_monde") != pending.get("world_step")):
            return self._underlying.evaluate(proposal=proposal, **kwargs)

        if provenance == "i1_unknown_affordance":
            # Only a previously UC-paid, first-person-grounded candidate may
            # receive exploratory evidence. Unknown effects stay unknown.
            if pending.get("affordance") is not True:
                return self._underlying.evaluate(proposal=proposal, **kwargs)
            prior = float(pending["prior_evidence"])
            learned_evidence = pending.get("learned_evidence")
            evidence = (prior if learned_evidence is None else
                        max(-1.0, min(1.0, 0.25 * prior
                                       + 0.75 * float(learned_evidence))))
            learned = pending.get("learned_status") == "learned"
            e = EvaluationOption(
                option_ref=proposal.option.id,
                option_version=proposal.option.version,
                cycle=kwargs["cycle"], t_monde=kwargs["t_monde"],
                status="evaluated",
                learned_value_status="learned" if learned else "unlearned",
                learned_value=(
                    float(pending["learned_value"]) if learned else None
                ),
                simulated_value_status="unavailable", simulated_value=None,
                intrinsic_status="not_applicable", intrinsic_value=None,
                risk_status="unknown", risk=None, safety_uncertainty=1.0,
                protection=False, signal_ids=(),
                producers=(I1_AFFORDANCE_POLICY,)
                          + (("value_needs.q_active",) if learned else ()),
            )
            result = OptionEvidenceInput(evaluation=e, evidence=evidence)
            result.validate()
            return result

        receipt = self._pending.get("receipt")
        if receipt is None:
            return self._underlying.evaluate(proposal=proposal, **kwargs)
        sources = tuple(self._pending.get("lived_sources", ()))
        evidence = 0.45 if sources else I1_SCORE
        e = EvaluationOption(
            option_ref=proposal.option.id,
            option_version=proposal.option.version,
            cycle=kwargs["cycle"],
            t_monde=kwargs["t_monde"],
            status="evaluated",
            learned_value_status="unlearned",
            learned_value=None,
            simulated_value_status="unavailable",
            simulated_value=None,
            intrinsic_status="not_applicable",
            intrinsic_value=None,
            risk_status="unknown",
            risk=None,
            safety_uncertainty=1.0,
            protection=False,
            signal_ids=tuple("memory:source:"+s for s in sources),
            producers=("i1:partial-experimental-instrumental-v1",)
                      + ((RECALL_POLICY,) if sources else ()),
        )
        result = OptionEvidenceInput(evaluation=e, evidence=evidence)
        result.validate()
        return result


class ExperimentalI1Stage12Runtime(Stage12Runtime):
    """I1-specific single-actor Stage12 with an opt-in active partial model."""

    individual_id = "i1-experimental-stage12"

    def __init__(
        self, *, i1_model: ShadowVisibleDeltaModel | None = None,
        i1_model_enabled: bool = False, i1_forecast_cost_uc: int = 2,
        i1_lived_recall_enabled: bool = False, i1_recall_cost_uc: int = 1,
        i1_unknown_action_enabled: bool = True,
        i1_unknown_action_cost_uc: int = 2,
        **kwargs,
    ) -> None:
        if type(i1_model_enabled) is not bool:
            raise ValueError("I1 active model opt-in must be a boolean")
        if type(i1_forecast_cost_uc) is not int or i1_forecast_cost_uc < 1:
            raise ValueError("I1 partial model requires positive UC cost")
        if type(i1_lived_recall_enabled) is not bool or type(i1_recall_cost_uc) is not int or i1_recall_cost_uc < 1:
            raise ValueError("invalid I1 lived recall opt-in or cost")
        if i1_lived_recall_enabled and not i1_model_enabled:
            raise ValueError("I1 recall requires active I1 predictor")
        if (type(i1_unknown_action_enabled) is not bool
                or type(i1_unknown_action_cost_uc) is not int
                or i1_unknown_action_cost_uc < 1):
            raise ValueError("unknown affordances require explicit positive-UC birth settings")
        if i1_unknown_action_enabled:
            birth_id = kwargs.get("birth_life_id")
            if (kwargs.get("autonomous_mortal") is not True
                    or not isinstance(birth_id, str)
                    or not birth_id.startswith("i1:")):
                raise ValueError("unknown action exploration requires a mortal I1 birth")
        if i1_model_enabled:
            who = kwargs.get("birth_life_id")
            if (not isinstance(who, str) or not who.startswith("i1:")
                    or kwargs.get("autonomous_mortal") is not True):
                raise ValueError("I1 active partial model requires explicit separate mortal birth")
            if type(i1_model) is not ShadowVisibleDeltaModel:
                raise ValueError("I1 model must be the audited frozen visible-delta type")
            if (i1_model.version != MODEL_VERSION
                    or i1_model.source_scope != "external_lab"
                    or i1_model.activation != "shadow_only"):
                raise ValueError("unsupported I1 external training provenance")
            if (len(i1_model.corpus_sha256) != 64
                    or any(c not in "0123456789abcdef" for c in i1_model.corpus_sha256)
                    or set(dict(i1_model.counts)) != {"MOVE_E", "COLLECT_B"}
                    or min(dict(i1_model.counts).values()) < 8):
                raise ValueError("invalid I1 factorized research artifact")
        elif i1_model is not None:
            raise ValueError("a model at birth requires explicit enabled=True")
        self._i1_lived_recall_enabled = i1_lived_recall_enabled
        self._i1_recall_cost_uc = i1_recall_cost_uc
        self._i1_model = i1_model
        self._i1_enabled = i1_model_enabled
        self._i1_forecast_cost_uc = i1_forecast_cost_uc
        self._i1_unknown_action_enabled = i1_unknown_action_enabled
        self._i1_unknown_action_cost_uc = i1_unknown_action_cost_uc
        self._i1_model_contract = (
            (I1_POLICY, i1_model_enabled, i1_forecast_cost_uc,
             None if i1_model is None else i1_model.version,
             None if i1_model is None else i1_model.corpus_sha256,
             None if i1_model is None else i1_model.deltas,
             None if i1_model is None else i1_model.counts,
             RECALL_POLICY, i1_lived_recall_enabled, i1_recall_cost_uc)
        )
        # Append only for opted-in new births. Historical I1 M11 birth hashes
        # and the unmodified A2.38/A2.39 variants retain their exact contract.
        if i1_unknown_action_enabled:
            self._i1_model_contract += (
                I1_AFFORDANCE_POLICY, True, i1_unknown_action_cost_uc,
            )
        self._i1_pending = {}
        super().__init__(**kwargs)
        if self.stage3.substrate.bench is not None:
            raise RuntimeError("autonomous I1 cannot receive Bench access")

    @property
    def temperament_parameters(self):
        """Read Stage11's frozen projection without requiring Stage5 mixin.

        Both historical research arms and the natural I1 inherit this
        substrate. The frozen experimental neutral projection stays neutral;
        only canonical natural birth may configure individual differences.
        """
        return self._stage11_config.temperament_parameters

    def _parent_runtime_config(self, config):
        base = super()._parent_runtime_config(config)
        if not (self._i1_enabled or self._i1_unknown_action_enabled):
            return base
        stage9 = base.stage9
        stage8 = stage9.stage8
        stage7 = stage8.stage7
        stage6 = stage7.stage6
        stage4 = stage6.stage4
        original = stage4.compute_budget
        forecast_cost = self._i1_forecast_cost_uc if self._i1_enabled else 0
        affordance_cost = (self._i1_unknown_action_cost_uc
                           if self._i1_unknown_action_enabled else 0)
        # Original goal-linked alternatives share one Planning charge.
        # The independently registered local proposal is an ADDITIONAL,
        # separately paid candidate, not a free duplicate. Reserve its
        # preparation, registration and evaluation only for opted-in births.
        reserve = max(forecast_cost, affordance_cost)
        local_enabled = getattr(self, "_i1_cross_goal_local_opportunities", False)
        local_plan_cost = affordance_cost if local_enabled else 0
        local_register_cost = (
            original.operation_costs["competition_register"] if local_enabled else 0
        )
        local_evaluate_cost = (
            original.operation_costs["competition_evaluate"] if local_enabled else 0
        )
        extra = self._i1_recall_cost_uc if self._i1_lived_recall_enabled else 0
        budget = replace(
            original,
            version=(original.version
                     + ("+" + I1_POLICY if self._i1_enabled else "")
                     + ("+" + I1_AFFORDANCE_POLICY
                        if self._i1_unknown_action_enabled else "")
                     + ("+" + I1_OPPORTUNISTIC_POLICY if local_enabled else "")),
            cycle_ceiling=(original.cycle_ceiling + reserve + extra
                           + local_plan_cost + local_register_cost
                           + local_evaluate_cost),
            module_envelopes={
                **original.module_envelopes,
                "planning": (original.module_envelopes["planning"]
                             + reserve + local_plan_cost),
                "competition": (original.module_envelopes["competition"] + extra
                                + local_register_cost + local_evaluate_cost),
            },
            operation_costs={
                **original.operation_costs,
                **({I1_EXPERIMENTAL_OPERATION: forecast_cost}
                   if forecast_cost else {}),
                **({I1_AFFORDANCE_OPERATION: affordance_cost}
                   if affordance_cost else {}),
                **({"i1_lived_recall_review": extra} if extra else {}),
            },
        )
        updated = replace(stage9, stage8=replace(stage8, stage7=replace(
            stage7, stage6=replace(stage6, stage4=replace(
                stage4, compute_budget=budget,
            )),
        )))
        return replace(base, stage9=updated)

    def _evaluate_competition_cycle(self, *, capture, cycle):
        # No retained wrapper in causal snapshots or M11 private cloning.
        # Competition remains the one and only decision accumulator.
        if (self._i1_lived_recall_enabled
                and self._i1_pending.get("option_ref")
                and self._i1_pending.get("world_step") == capture.t_monde
                and self._i1_pending.get("command_primitive") == "collecter"
                and not self._i1_pending.get("reviewed")):
            self._i1_pending["reviewed"] = True
            if self._charge(module="competition", operation="i1_lived_recall_review"):
                current = self.s_t.current
                visible_refs = set() if current is None else {
                    element.contribution_ref for element in current.competitive
                }
                recalled = (e.causal_event.get("data", {}) for e in self.journal.entries
                    if e.causal_event.get("kind") == "memory_recall_proposed"
                    and e.causal_event.get("t_monde") == capture.t_monde)
                episodes = tuple(data["episode_ref"] for data in recalled
                    if data.get("contribution_ref") in visible_refs
                    and type(data.get("episode_ref")) is str)
                command = self._i1_pending.get("command_primitive")
                if command == "collecter":
                    autobiography = self.stage3.substrate.views.autobiographical(policies={
                        STAGE2_AUTOBIOGRAPHICAL_POLICY.version: STAGE2_AUTOBIOGRAPHICAL_POLICY,
                        STAGE7_AUTOBIOGRAPHICAL_POLICY.version: STAGE7_AUTOBIOGRAPHICAL_POLICY,
                    })
                    sources = matched_collection_recall(
                        episodes=self.memory.episodes, autobiography=autobiography,
                        admitted_recall_refs=episodes, t_monde=capture.t_monde)
                    self._i1_pending["lived_sources"] = sources
                    self._write(kind="i1_lived_recall_review", cycle=cycle, data={
                        "policy": RECALL_POLICY, "source_event_refs": list(sources),
                        "safety_certified": False,
                    })
            else:
                self._write(kind="i1_lived_recall_abstained", cycle=cycle,
                            data={"reason":"insufficient_uc"})
        original = self.stage8_option_evaluator
        self.stage8_option_evaluator = I1PartialEvidenceAdapter(
            original, self._i1_pending
        )
        try:
            return super()._evaluate_competition_cycle(
                capture=capture, cycle=cycle
            )
        finally:
            self.stage8_option_evaluator = original

    def _on_open_step_capture(self, capture):
        self._i1_pending.clear()
        return super()._on_open_step_capture(capture)


    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        hooks = super()._phase_hooks(
            cycle=cycle, capture=capture,
            goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )
        if not getattr(self, "_i1_cross_goal_local_opportunities", False):
            return hooks
        normal_plan = hooks[1]["planning"]
        normal_register = hooks[3]["competition"]

        def plan_local(ctx):
            normal_plan(ctx)
            self._i1_local_proposal_this_cycle = None
            if self._cycle_degraded or st_before_cycle is None:
                return
            prior = self._i1_pending.get("local_option_ref")
            if prior is not None and self.competition.proposal_for(prior) is not None:
                return
            self._i1_pending.pop("local_option_ref", None)
            self._i1_pending.pop("local_opportunity_evidence", None)
            proposal = self._propose_cross_goal_local(
                capture=capture, cycle=cycle, st_version=st_before_cycle.version,
            )
            if proposal is None:
                return
            self._i1_local_proposal_this_cycle = proposal
            self._publish_contribution(self._planning_contribution(
                proposal, t_monde=capture.t_monde, cycle=cycle,
            ))

        def register_local(ctx):
            normal_register(ctx)
            proposal = self._i1_local_proposal_this_cycle
            if proposal is None or self._cycle_degraded:
                return
            if not self._charge(module="competition", operation="competition_register"):
                self._write(kind="i1_local_opportunity_registration",
                            cycle=cycle, data={
                                "option_ref": proposal.option.id,
                                "registered": False, "reason": "insufficient_uc",
                            })
                return
            registered = self._register_option_proposal(
                proposal=proposal,
                active_goal_id=(None if self.goal_manager.active_goal is None
                                else self.goal_manager.active_goal.id),
                t_monde=capture.t_monde, cycle=cycle,
            )
            self._write(kind="i1_local_opportunity_registration",
                        cycle=cycle, data={
                            "option_ref": proposal.option.id,
                            "registered": registered,
                            "goal_neutral": proposal.option.goal_ref is None,
                        })
            if not registered:
                self._i1_pending.pop("local_option_ref", None)
                self._i1_pending.pop("local_opportunity_evidence", None)

        hooks[1]["planning"] = plan_local
        hooks[3]["competition"] = register_local
        return hooks

    def _propose_cross_goal_local(self, *, capture, cycle, st_version):
        """Bounded, first-person local candidate, not a motor command."""
        if not getattr(self, "_i1_cross_goal_local_opportunities", False):
            return None
        state = state_from_capture(
            capture=capture, is_night=self.world.is_night(capture.t_monde),
        )
        available = _local_interaction_choices(
            self.planning.candidate_commands(state), enabled=True,
        )
        def key(command):
            return (command.primitive, tuple(sorted(command.parameters.items())))
        already = set()
        ordinary = self._proposal_this_cycle
        if ordinary is not None and ordinary.plan is not None:
            already.add(key(ordinary.plan.steps[0].command))
        for previous in self.competition.candidate_proposals:
            if (previous.option.expires_at_step > capture.t_monde
                    and previous.plan is not None and previous.plan.steps):
                already.add(key(previous.plan.steps[0].command))
        choices = tuple(c for c in available if key(c) not in already)
        self._write(kind="i1_local_opportunity_perceived", cycle=cycle,
                    data={
                        "policy": I1_OPPORTUNISTIC_POLICY,
                        "accessible_count": len(available),
                        "not_already_proposed": len(choices),
                        "goal_filter_applied": False,
                    })
        if not choices:
            return None
        if not self._charge(module="planning", operation=I1_AFFORDANCE_OPERATION):
            self._write(kind="i1_local_opportunity_unavailable",
                        cycle=cycle, data={"reason": "insufficient_uc"})
            return None
        context = self._evaluation_state(capture)
        q_exposure = getattr(self, "_i1_local_q_exposure", "learned")
        expose_rank, expose_evidence = _local_q_visibility(q_exposure)
        selected = None
        for index, command in enumerate(choices):
            suffix = ":".join(
                str(k) + "=" + str(command.parameters[k])
                for k in sorted(command.parameters)
            ) or "here"
            signature = "i1:affordance:" + command.primitive + ":" + suffix
            # Charge and update the exact same TD/Q owner in both arms;
            # suppress exposure only for this independent local candidate.
            learned = self.q_active.learned_value(context, signature)
            rank = (-(float(learned.evidence or 0.0)
                      if expose_rank else 0.0),
                    (capture.t_monde + index) % len(choices))
            if selected is None or rank < selected[0]:
                selected = (rank, command, signature, learned, suffix)
        _, command, signature, learned, suffix = selected
        # Q is still learned from real experience by Stage8; the neutral
        # research arm blinds only its exposure to Competition.
        selected_evidence = learned if expose_evidence else None
        exploration = float(self.temperament_parameters.exploration_coefficient)
        uncertainty = float(self.temperament_parameters.uncertainty_penalty_scale)
        prior = max(0.0, min(1.0, I1_SCORE
            * (1.0 + 0.25 * exploration) / (1.0 + 0.25 * uncertainty)))
        option_id = (f"option:i1:local:t{capture.t_monde}:"
                     f"{command.primitive}:{suffix}")
        plan_id = "plan:" + option_id + ":v1"
        plan = Plan(
            id=plan_id, option_ref=option_id, version=I1_OPPORTUNISTIC_POLICY,
            steps=(PlanStep(index=0, command=command, preconditions=(),
                            predicted_consequences=(), observation_window_steps=1),),
            goal_ref=None, budget_used_uc=self._i1_unknown_action_cost_uc,
            status="valid", st_version=st_version,
        )
        st = self.s_t.current
        retained = set() if st is None else {
            item.contribution_ref for item in st.competitive
        }
        grounded = tuple(sorted(
            ref for ref in self.stage3.perception.observation_ref_by_entity.values()
            if ref in retained
        ))
        option = Option(
            id=option_id, version=I1_OPPORTUNISTIC_POLICY,
            type="primitive", learning_signature=signature,
            preconditions=(), success_condition="step_completed",
            failure_condition="outcome_unconfirmed",
            invalidation_condition="new_real_capture",
            motive_ref=MotiveRef(type="local_opportunity",
                                 id=I1_OPPORTUNISTIC_POLICY),
            founding_st_version=st_version,
            expires_at_step=capture.t_monde + 1,
            provenance="i1_unknown_affordance",
            grounding_contribution_refs=grounded,
            goal_ref=None, plan_ref=plan_id,
        )
        proposed = OptionProposal(
            option=option, plan=plan, preliminary_admissibility="indeterminate",
        )
        proposed.validate()
        self._i1_pending["local_option_ref"] = option_id
        self._i1_pending["local_opportunity_evidence"] = {
            "option_ref": option_id, "world_step": capture.t_monde,
            "affordance": True, "prior_evidence": prior,
            "learned_evidence": (
                None if selected_evidence is None else selected_evidence.evidence),
            "learned_value": (
                None if selected_evidence is None else selected_evidence.value),
            "learned_status": (
                "unlearned" if selected_evidence is None else selected_evidence.status),
        }
        self._write(kind="i1_local_opportunity_proposed", cycle=cycle,
                    data={
                        "policy": I1_OPPORTUNISTIC_POLICY,
                        "option_ref": option_id, "command": command.as_dict(),
                        "learning_signature": signature, "goal_ref": None,
                        "ordinary_candidate_preserved": ordinary is not None,
                        "visible_input_sha256": sha256_hex(
                            canonical_causal_bytes(state.as_dict())
                        ),
                        "prior_evidence": prior,
                        "learned_value_status": (
                            "unlearned" if selected_evidence is None
                            else selected_evidence.status),
                        "learned_value": (
                            None if selected_evidence is None
                            else selected_evidence.value),
                        "q_exposure": q_exposure,
                        "q_used_for_candidate_rank": expose_rank,
                        "q_used_for_competition_evidence": expose_evidence,
                        "physical_outcome_known": False, "forced_motor": False,
                    })
        return proposed

    def _consider_uncertain_affordance(
        self, *, capture, goal, st_version, cycle, exact,
    ):
        """One need-linked opportunity from perceived, physically legal actions.

        Unknown effects stay unknown. This is a possibility generator, never
        a fixed collect/eat/move sequence, a food/poison oracle, or dispatch.
        D1 owns water learning when it is active, while Stage10 separately
        proposes intrinsically motivated sleep and Stage11 handles curiosity.
        """
        if not self._i1_unknown_action_enabled or goal is None:
            return None
        if (goal.goal_type == "drink"
                and getattr(self, "_i1_water_probe_enabled", False)):
            # Preserve the original first-person D1 water causal follow-up.
            return None
        if (exact is not None and
                exact.option.success_condition != "step_completed"):
            # A fully predictive goal plan must not be displaced by an
            # exploratory unknown option. Partial stock accumulation is not
            # a physiologically satisfied food goal.
            return None
        state = state_from_capture(
            capture=capture,
            is_night=self.world.is_night(capture.t_monde),
        )
        available = self.planning.candidate_commands(state)
        direct = {
            "eat": {"manger", "collecter"},
            "drink": {"boire"},
            "recover_energy": {"dormir"},
            "restore_integrity": {"attendre"},
        }.get(goal.goal_type, set())
        # The opt-in cross-goal producer owns an independent Planning and
        # Competition slot; it must never rewrite these goal-linked choices.

        def relevant(candidate):
            primitive = candidate.primitive
            if primitive in direct:
                if primitive == "collecter":
                    # Local food can be tried without a nutritional prior.
                    return candidate.parameters.get("target") in ("berry_a", "berry_b")
                return True
            if primitive != "se_deplacer":
                return False
            direction = candidate.parameters.get("direction")
            if goal.goal_type == "eat":
                return any(
                    a.direction == direction and a.passable
                    and set(a.resources).intersection(("berry_a", "berry_b"))
                    for a in state.adjacent
                )
            if goal.goal_type == "drink":
                return any(
                    a.direction == direction and a.passable and a.water_source
                    for a in state.adjacent
                )
            return False

        choices = tuple(cmd for cmd in available if relevant(cmd))
        if not choices:
            return None
        if not self._charge(
            module="planning", operation=I1_AFFORDANCE_OPERATION
        ):
            self._write(kind="i1_unknown_affordance_unavailable",
                        cycle=cycle, data={
                            "reason": "insufficient_uc",
                            "world_step": capture.t_monde,
                            "goal_ref": goal.id,
                        })
            return None

        evaluation_state = self._evaluation_state(capture)
        # Associative TD feedback comes only from earlier physically lived
        # decisions. Unlearned values are neutral, not an edible/safe prior.
        # Stream the exact same learned-value ranking. Only the winning
        # option must be retained; no candidate list or second signature
        # formatting pass is needed. Equal ranks still select the first.
        winner = None
        choice_count = len(choices)
        for ordinal, command in enumerate(choices):
            suffix = ":".join(
                f"{key}={command.parameters[key]}"
                for key in sorted(command.parameters)
            ) or "here"
            signature = ("i1:affordance:" + command.primitive + ":" + suffix)
            learned = self.q_active.learned_value(evaluation_state, signature)
            # Unlearned values remain neutral, not a physical prediction.
            rank = (
                -float(learned.evidence or 0.0),
                (capture.t_monde + ordinal) % choice_count,
            )
            if winner is None or rank < winner[0]:
                winner = (rank, command, signature, learned, suffix)
        _, command, signature, learned, suffix = winner
        cross_goal_local = False  # goal-linked producer
        pressure = max(0.0, min(1.0, float(goal.current_pressure)))
        exploration = float(self.temperament_parameters.exploration_coefficient)
        uncertainty_penalty = float(
            self.temperament_parameters.uncertainty_penalty_scale
        )
        # A bounded motivation to *consider*, not a predicted food reward:
        # genuine need, inherited exploration and uncertainty aversion affect
        # competition. Stage9 and Action Control remain independently binding.
        prior_evidence = max(0.0, min(1.0,
            I1_SCORE * (0.5 + 0.5 * pressure)
            * (1.0 + 0.25 * exploration)
            / (1.0 + 0.25 * uncertainty_penalty)
        ))
        option_id = (
            f"option:i1:affordance:{goal.id}:t{capture.t_monde}:"
            f"{command.primitive}:{suffix}"
        )
        plan_id = "plan:" + option_id + ":v1"
        plan = Plan(
            id=plan_id, option_ref=option_id, version=I1_AFFORDANCE_POLICY,
            steps=(PlanStep(
                index=0, command=command, preconditions=(),
                predicted_consequences=(), observation_window_steps=1,
            ),),
            goal_ref=goal.id, budget_used_uc=self._i1_unknown_action_cost_uc,
            status="valid", st_version=st_version,
        )
        retained = {
            item.contribution_ref for item in self.s_t.current.competitive
        } if self.s_t.current is not None else set()
        grounded = tuple(sorted(
            ref for ref in self.stage3.perception.observation_ref_by_entity.values()
            if ref in retained
        ))
        option = Option(
            id=option_id, version=I1_AFFORDANCE_POLICY, type="primitive",
            learning_signature=signature, preconditions=(),
            success_condition="step_completed",
            failure_condition="outcome_unconfirmed",
            invalidation_condition="new_real_capture_or_goal_changed",
            motive_ref=MotiveRef(type="active_goal", id=goal.id),
            founding_st_version=st_version,
            expires_at_step=capture.t_monde + 1,
            provenance="i1_unknown_affordance",
            grounding_contribution_refs=grounded,
            goal_ref=goal.id, plan_ref=plan_id,
        )
        proposed = OptionProposal(
            option=option, plan=plan,
            preliminary_admissibility="indeterminate",
        )
        proposed.validate()
        self._i1_pending.update(
            option_ref=option_id, world_step=capture.t_monde,
            affordance=True, command_primitive=command.primitive,
            prior_evidence=prior_evidence,
            learned_evidence=learned.evidence,
            learned_value=learned.value, learned_status=learned.status,
        )
        self._write(kind="i1_unknown_affordance_proposed", cycle=cycle,
                    data={
                        "policy": I1_AFFORDANCE_POLICY,
                        "option_ref": option_id,
                        "goal_ref": goal.id,
                        "command": command.as_dict(),
                        "accessible_inventory": dict(state.inventory),
                        "candidate_count": len(choices),
                        "candidate_primitives": [c.primitive for c in choices],
                        "cross_goal_local_interaction": cross_goal_local,
                        "candidate_expansion_policy": None,
                        "ordinary_q_ranking_unchanged": True,
                        "no_interaction_result_assumed": True,
                        "visible_input_sha256": sha256_hex(
                            canonical_causal_bytes(state.as_dict())
                        ),
                        "goal_pressure": pressure,
                        "temperament_exploration": exploration,
                        "uncertainty_penalty_scale": uncertainty_penalty,
                        "prior_evidence": prior_evidence,
                        "learned_value_status": learned.status,
                        "learned_value": learned.value,
                        "predicted_consequences": None,
                        "source_scope": "first_person_affordance_and_lived_q",
                        "risk_status": "unknown", "safety_certificate": None,
                        "goal_success_claimed": False,
                        "command_imposed": False,
                    })
        return proposed

    def _propose_for_cycle(
        self, *, capture, goal_for_planning, st_before_cycle, cycle,
    ):
        exact = super()._propose_for_cycle(
            capture=capture, goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle, cycle=cycle,
        )
        if goal_for_planning is not None and st_before_cycle is not None:
            uncertain = self._consider_uncertain_affordance(
                capture=capture, goal=goal_for_planning,
                st_version=st_before_cycle.version,
                cycle=cycle, exact=exact,
            )
            if uncertain is not None:
                # Producing an option never authorizes its execution.
                return uncertain
        if (exact is not None or not self._i1_enabled
                or goal_for_planning is None
                or goal_for_planning.goal_type != "eat"
                or st_before_cycle is None):
            return exact
        state = state_from_capture(
            capture=capture,
            is_night=self.world.is_night(capture.t_monde),
        )
        # Only directly perceived resources/neighbor cues; no world lookup.
        if "berry_b" in state.current_resources:
            command = PrimitiveCommand("collecter", {"target": "berry_b"})
        else:
            east = [item for item in state.adjacent
                    if item.direction == "east" and item.passable
                    and "berry_b" in item.resources]
            if len(east) != 1:
                return None
            command = PrimitiveCommand("se_deplacer", {"direction": "east"})
        if not self._charge(
            module="planning", operation=I1_EXPERIMENTAL_OPERATION
        ):
            self._write(
                kind="i1_partial_forecast_abstained", cycle=cycle,
                data={"reason": "insufficient_uc", "world_step": capture.t_monde},
            )
            return None
        # The A2.30 prototype used an external receipt-schema label different
        # from the live Stage6 label. Mapping is a *schema adapter*, not a new
        # observable or a conversion from a partial state to a full state.
        if state.schema_version != "stage6-simulation-state-v1":
            raise ValueError("unrecognized I1 lived-state schema")
        model_input = replace(state, schema_version="simulation-state-v1")
        forecast = self._i1_model.forecast_for_review(
            state=model_input, command=command
        )
        receipt = forecast.as_dict()
        self._write(kind="i1_partial_preaction_forecast", cycle=cycle, data={
            "policy": I1_POLICY,
            "individual_id": self.individual_id,
            "world_step": capture.t_monde,
            "cycle": cycle,
            "original_schema": state.schema_version,
            "model_input_schema": model_input.schema_version,
            "source_scope": "external_lab_not_lived_memory",
            "input_hash": sha256_hex(canonical_causal_bytes(state.as_dict())),
            "command": command.as_dict(),
            "result": receipt,
            "physical_safety_certified": False,
            "distal_agency_certified": False,
        })
        if forecast.status != "empirical_partial_not_certified":
            return None
        result = dict(forecast.estimated or {})
        if set(result) != {"x", "y", "energy", "food", "water", "inventory_berry_b"}:
            raise RuntimeError("incomplete I1 model output contract")
        if any(not isfinite(float(v)) for v in result.values()):
            raise RuntimeError("invalid experimental partial forecast")
        # An experimental 1-step prefix; not evidence of the food goal's
        # achievement, never a full-state simulator output or ingestion.
        projected = (
            PredictedConsequence("position_x", float(result["x"]), 0.0),
            PredictedConsequence("position_y", float(result["y"]), 0.0),
            PredictedConsequence("energy", float(result["energy"]), 0.0),
            PredictedConsequence("food", float(result["food"]), 0.0),
            PredictedConsequence("water", float(result["water"]), 0.0),
        )
        option_id = (
            f"option:i1:partial:{goal_for_planning.id}:"
            f"t{capture.t_monde}:{command.primitive}"
        )
        plan_id = "plan:" + option_id + ":v1"
        plan = Plan(
            id=plan_id, option_ref=option_id, version=I1_POLICY,
            steps=(PlanStep(
                index=0, command=command, preconditions=(),
                predicted_consequences=projected,
                observation_window_steps=1,
            ),),
            goal_ref=goal_for_planning.id,
            budget_used_uc=self._i1_forecast_cost_uc,
            status="valid",
            st_version=st_before_cycle.version,
        )
        option = Option(
            id=option_id, version=I1_POLICY, type="primitive",
            learning_signature="i1_partial:" + command.primitive,
            preconditions=(),
            success_condition="step_completed",
            failure_condition="outcome_unconfirmed",
            invalidation_condition="new_real_capture_or_goal_changed",
            motive_ref=MotiveRef(type="active_goal", id=goal_for_planning.id),
            founding_st_version=st_before_cycle.version,
            expires_at_step=capture.t_monde + 1,
            provenance="i1_partial_experiment",
            grounding_contribution_refs=tuple(sorted(
                ref for ref in self.stage3.perception.observation_ref_by_entity.values()
                if ref in {element.contribution_ref
                           for element in st_before_cycle.competitive}
            )),
            goal_ref=goal_for_planning.id,
            plan_ref=plan_id,
        )
        proposed = OptionProposal(
            option=option, plan=plan,
            preliminary_admissibility="indeterminate",
        )
        proposed.validate()
        self._i1_pending.update(
            option_ref=option_id, world_step=capture.t_monde, receipt=receipt,
            command_primitive=command.primitive
        )
        self._write(kind="i1_partial_instrumental_option_proposed",
                    cycle=cycle, data={
                        "policy": I1_POLICY,
                        "option_ref": option_id,
                        "command": command.as_dict(),
                        "value_kind": "bounded_instrumental_preference_not_E_sim",
                        "evidence_score": I1_SCORE,
                        "risk_status": "unknown",
                        "source_corpus_sha256": self._i1_model.corpus_sha256,
                        "safety_certificate": None,
                        "goal_success_claimed": False,
                    })
        return proposed
