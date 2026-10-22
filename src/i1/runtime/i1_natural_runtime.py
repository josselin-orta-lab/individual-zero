"""Canonical living I1 without A2.38/A2.39 H1/H2 ablation policies.

The historical experimental classes remain available by explicit import for
reproducing the original studies. This default actor inherits the general
perception/needs/planning/Competition/Stage9/Action Control substrate, the
first-person D1 capabilities and the default #229 food affordance, without
inheriting either scripted A2.38 H1/H2 review or A2.39 food-first H2.

Sleep and starvation physics are installed only by this canonical natural
I1 constructor, never by the shared generated Stage11Sleep ancestor. No motor bypass or artificial
prebirth experience is introduced here.
"""
from __future__ import annotations

from .i1_d2_runtime import I1WaterPrudentRuntime
from dataclasses import replace
from .determinism import canonical_causal_bytes, sha256_hex
from i1.modules.geographic_exploration import GeographicExplorationConfig
from .i1_birth_temperament import configure_birth_temperament
from .i1_natural_sleep import enable_natural_sleep_birth
from .i1_cognitive_publication import ActiveConsolidatedOwner
from .i1_active_runtime import (
    I1_AFFORDANCE_POLICY, I1_AFFORDANCE_OPERATION, I1_SCORE,
)
from i1.contracts import MotiveRef, Option, OptionProposal, Plan, PlanStep
from i1.modules.simulator import state_from_capture
from i1.experimental.local_opportunity_selection import local_interaction_choices

_PRIVATE_RECALL_VERSION = "i1-private-procedure-advisory-v1"
_PRIVATE_RECALL_OPERATION = "i1_private_procedure_recall"
_PRIVATE_RECALL_COST_UC = 1
_OPTION_INTENTION_COST_UC = 1
_OPTION_INTENTION_OPERATION = "i1_applied_option_intention"
_PRIVATE_OBSERVED_FIELDS = {
    "boire": "drank",
    "collecter": "collected",
    "fabriquer_outil": "tool_crafted",
    "poser_une_pierre": "stone_placed",
}

def _rank_current_local_opportunity(
    *, learned_evidence: float | None, remembered: bool,
    witnesses: tuple[dict[str, object], ...], rotation: int,
) -> tuple[float, int, int]:
    """Order currently afforded alternatives; no new Q or motor authority.

    Contradiction is a pair of opposite signed, genuinely witnessed bodily
    changes for ANY one channel in the bounded Memory history. A zero-delta
    observation between them is neutral, not a reason to erase uncertainty.
    An exclusively adverse contextual history also removes that tie-break.
    Memory remains subordinate to already learned Q/TD evidence.
    """
    channels = ("energy", "food", "water", "integrity")
    conflict = any(
        any(row["body_delta"][channel] > 0 for row in witnesses)
        and any(row["body_delta"][channel] < 0 for row in witnesses)
        for channel in channels
    )
    favorable = any(
        row["body_delta"][channel] > 0
        for row in witnesses for channel in channels
    )
    adverse = any(
        row["body_delta"][channel] < 0
        for row in witnesses for channel in channels
    )
    # An exclusively adverse *contextual* history cannot reinforce the
    # memory tie-break merely because this option was once considered.
    # Mixed observations remain uncertain; no causality or Q is inferred.
    unconvincing = conflict or (adverse and not favorable)
    return (
        -float(learned_evidence or 0.0),
        -int(remembered and not unconvincing),
        rotation,
    )


# Historical arms remain available explicitly from the independent
# I1A238ExperimentalRuntime / I1A239ExperimentalRuntime classes. They are
# intentionally not accepted by the canonical runtime's constructor.
_ABLATION_SETTINGS = frozenset({
    "i1_a238_alternate_need",
    "i1_a238_bounded_move",
    "i1_a238_need_review_uc",
    "i1_a238_move_review_uc",
    "i1_a238_max_move_reviews",
    "i1_a239_food_first_risk",
    "i1_a239_strict_unknown",
    "i1_a239_d2_uc",
    "i1_a239_risk_uc",
    "i1_a239_max_commitments",
})


# I1-only birth calibration. Historical values remain opt-in for matched
# laboratory counterfactuals; birth_i1 never exposes the research selector.
_I1_GOAL_POLICIES = {
    "natural-004": (0.04, 0.35),
    "historical-010": (0.10, 0.90),
}
_GOAL_POLICY_VERSION = "i1-natural-goal-pressure-v1"


def _configure_birth_goal_policy(config, policy):
    """Freeze one GoalManager owner policy in the actual Stage11 Stage4 tree."""
    if policy not in _I1_GOAL_POLICIES:
        raise ValueError("unregistered I1 natural goal arbitration policy")
    hysteresis, critical = _I1_GOAL_POLICIES[policy]
    s9 = config.stage9
    s8 = s9.stage8
    s7 = s8.stage7
    s6 = s7.stage6
    s4 = s6.stage4
    tag = "+" + _GOAL_POLICY_VERSION + ":" + policy
    goals = replace(
        s4.goals, version=s4.goals.version + tag,
        replacement_hysteresis=hysteresis, critical_pressure=critical,
    )
    s4 = replace(s4, version=s4.version + tag, goals=goals)
    s6 = replace(s6, version=s6.version + tag, stage4=s4)
    s7 = replace(s7, version=s7.version + tag, stage6=s6)
    s8 = replace(s8, version=s8.version + tag, stage7=s7)
    s9 = replace(s9, version=s9.version + tag, stage8=s8)
    configured = replace(config, version=config.version + tag, stage9=s9)
    configured.validate()
    return configured


class I1Runtime(I1WaterPrudentRuntime):
    """Default I1 actor. H1/H2 are not part of its inheritance graph."""

    individual_id = "i1-natural-default-v1"

    def __init__(self, **kwargs):
        # This selector is research-only. The canonical birth_i1 entry point
        # always uses natural-004 and cannot override it.
        goal_policy = kwargs.pop("i1_goal_policy", "natural-004")
        if goal_policy not in _I1_GOAL_POLICIES:
            raise ValueError("unregistered I1 natural goal arbitration policy")
        # Version the prospective I1 configuration instead of modifying the
        # canonical reference fixture or copying A2.38 researcher switches.
        cfg = kwargs.get("stage11_config")
        if cfg is None:
            raise ValueError("natural I1 birth requires an explicit Stage11 config")
        raw_sleep = kwargs.get("stage10_config")
        raw_world = kwargs.get("world_config")
        if raw_sleep is None or raw_world is None:
            raise ValueError("natural I1 birth requires world and sleep configs")
        # Birth-specific, versioned physical fatigue/metabolism only for the
        # canonical actor. Historical experimental Stage12 descendants must
        # retain their explicitly registered physical ablation parameters.
        kwargs["world_config"], kwargs["stage10_config"] = (
            enable_natural_sleep_birth(
                world_config=raw_world, stage10_config=raw_sleep,
            )
        )
        if cfg.geographic is None:
            geographic = GeographicExplorationConfig(
                version="i1-firstperson-frontier-v1+lived-sites-v1",
                novelty_weight=0.15, max_distinct_sites=1024,
                max_targets_per_cycle=1,
                observe_routes=True, refresh_surveys=True, remember_entities=True,
                max_place_candidates=3, experienced_site_effects=True,
            )
            cfg = replace(
                cfg, version=cfg.version + "+i1-firstperson-frontier-v1+lived-sites-v1",
                geographic=geographic, intrinsic_weight=min(cfg.intrinsic_weight, 0.35),
                local_threat_alerts=True,
                geographic_capacity_guard_enabled=True,
                geographic_route_enabled=True,
            )
        # Existing geographic owner, newly enabled current-life site effects.
        # A reference Stage11 with this optional contract disabled remains
        # untouched; the natural birth uses the already mortal owner for M11.
        if (cfg.geographic is not None
            and cfg.geographic.remember_entities
            and not cfg.geographic.experienced_site_effects):
            cfg = replace(
                cfg, version=cfg.version + "+i1-lived-sites-v1",
                geographic=replace(
                    cfg.geographic,
                    version=cfg.geographic.version + "+i1-lived-sites-v1",
                    experienced_site_effects=True,
                ),
            )
        # Ordinary I1 identifies each charged cognitive cycle by the
        # actual Scheduler world-step/attempt/cycle tuple. This prevents a
        # repeated cycle number within one physical occurrence from being
        # mistaken for fresh budget custody after an interrupted phase.
        # A different world step may legitimately begin at cycle 1 again.
        if not cfg.cycle_occurrence_guard_enabled:
            cfg = replace(
                cfg,
                version=cfg.version + "+i1-scheduler-cycle-custody-v1",
                cycle_occurrence_guard_enabled=True,
            )
        # Stage6 reference planning was intentionally one-shot. In a
        # living I1 a proven intermediate physical step must lead to fresh
        # perception and another independent decision, not repeat a cached
        # prediction or mistake berry inventory for physiological satiety.
        # This operates ONLY on the model's genuinely predicted edges;
        # first-person uncertain affordances remain separate.
        s9 = cfg.stage9
        s8 = s9.stage8
        s7 = s8.stage7
        s6 = s7.stage6
        planned = replace(
            s6.planning,
            version=s6.planning.version + "+i1-living-progressive-v1",
            progressive_subgoals=True,
            progressive_evaluation_prefix=False,
            progressive_revalidate_on_new_capture=True,
        )
        s6 = replace(
            s6, version=s6.version + "+i1-living-progressive-v1",
            planning=planned,
        )
        cfg = replace(
            cfg, version=cfg.version + "+i1-living-progressive-v1",
            stage9=replace(
                s9, stage8=replace(
                    s8, stage7=replace(s7, stage6=s6),
                ),
            ),
        )
        life_id = kwargs.get("birth_life_id")
        cfg = configure_birth_temperament(cfg, life_id=life_id)
        # The immutable goal subtree is installed before any owner or body is
        # created. No action, learned value, world fact or survival rule changes.
        cfg = _configure_birth_goal_policy(cfg, goal_policy)
        kwargs["stage11_config"] = cfg
        # Both integrated stages must agree on the identical frozen Stage9
        # substrate after temperament projection, before creating the body.
        sleep_cfg = kwargs.get("stage10_config")
        if sleep_cfg is None:
            raise ValueError("natural I1 birth requires Stage10 configuration")
        kwargs["stage10_config"] = replace(
            sleep_cfg, version=(sleep_cfg.version + "+i1-birth-temperament-v1"
                                + "+" + _GOAL_POLICY_VERSION + ":" + goal_policy),
            stage9=cfg.stage9,
        )
        # First-person proximal action agency, never a claim that a distal
        # outcome was necessarily caused by the individual's intention.
        kwargs["subjective_goal_agency"] = True
        kwargs["dual_scope_agency"] = True
        kwargs["spatial_goal_progress"] = True
        unexpected = sorted(_ABLATION_SETTINGS.intersection(kwargs))
        if unexpected:
            raise ValueError(
                "H1/H2 settings are restricted to historical experimental "
                "runtimes, not the default I1: " + ", ".join(unexpected)
            )
        # No opt-out in the canonical actor: a sensed, UC-priced unknown
        # action may be CONSIDERED, never forced or deemed safe. For
        # experimental ablations use the frozen descendant/runtime class.
        if kwargs.get("i1_unknown_action_enabled", True) is not True:
            raise ValueError("default I1 requires uncertain-action consideration")
        kwargs["i1_unknown_action_enabled"] = True
        # Ordinary embodied water experience is useful without any external
        # pre-trained visible-delta corpus or D2/H2 movement permission.
        if kwargs.get("i1_water_probe_enabled", True) is not True:
            raise ValueError("default I1 requires first-person water probing")
        if kwargs.get("i1_water_learning_enabled", True) is not True:
            raise ValueError("default I1 requires first-person water learning")
        kwargs["i1_water_probe_enabled"] = True
        kwargs["i1_water_learning_enabled"] = True
        kwargs["i1_d2_prudence"] = False
        # Quiescent, step-local accounting only. GoalManager itself owns the
        # durable refractory and failure counters (M11 causal state).
        self._i1_personal_id = life_id
        self._i1_last_nonplannable_observation = None
        super().__init__(**kwargs)
        self._i1_active_owner_views = {
            "causal_model": ActiveConsolidatedOwner(
                self.causal_model, "causal_model",
            ),
            "perception": ActiveConsolidatedOwner(
                self.stage3.perception, "perception",
            ),
            "metacognition_health": ActiveConsolidatedOwner(
                self._meta_custody, "metacognition_health",
            ),
        }

    @property
    def causal_owners(self):
        owners = super().causal_owners
        views = getattr(self, "_i1_active_owner_views", None)
        if views is None:
            return owners
        return tuple(views.get(owner.owner_id, owner) for owner in owners)


    def _parent_runtime_config(self, config):
        """Reserve a real P-43 allowance for optional private lived recall."""
        base = super()._parent_runtime_config(config)
        stage9 = base.stage9
        stage8 = stage9.stage8
        stage7 = stage8.stage7
        stage6 = stage7.stage6
        stage4 = stage6.stage4
        original = stage4.compute_budget
        if _PRIVATE_RECALL_OPERATION in original.operation_costs:
            raise ValueError("I1 private recall operation already registered")
        # A second independent Planning producer may coexist with the
        # existing goal candidate. Reserve its actual paid Planning,
        # Competition register and per-option evaluation costs separately.
        local_planning = original.operation_costs[I1_AFFORDANCE_OPERATION]
        local_registration = original.operation_costs["competition_register"]
        local_evaluation = original.operation_costs["competition_evaluate"]
        budget = replace(
            original,
            version=(original.version + "+" + _PRIVATE_RECALL_VERSION
                     + "+i1-goal-independent-local-v1"),
            cycle_ceiling=(original.cycle_ceiling + _PRIVATE_RECALL_COST_UC
                           + local_planning + local_registration + local_evaluation
                           + _OPTION_INTENTION_COST_UC),
            module_envelopes={
                **original.module_envelopes,
                "planning": (original.module_envelopes["planning"]
                             + _PRIVATE_RECALL_COST_UC + local_planning
                             + _OPTION_INTENTION_COST_UC),
                "competition": (original.module_envelopes["competition"]
                                + local_registration + local_evaluation),
            },
            operation_costs={
                **original.operation_costs,
                _PRIVATE_RECALL_OPERATION: _PRIVATE_RECALL_COST_UC,
                _OPTION_INTENTION_OPERATION: _OPTION_INTENTION_COST_UC,
            },
        )
        return replace(
            base,
            stage9=replace(
                stage9, stage8=replace(
                    stage8, stage7=replace(
                        stage7, stage6=replace(
                            stage6, stage4=replace(
                                stage4, compute_budget=budget,
                            ),
                        ),
                    ),
                ),
            ),
        )

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        """Add a second normal Phase-1 producer, not a replacement GoalManager.

        The existing Planning and Stage11 geographic producers run first.
        Any local option gets its own paid Competition admission path in Phase
        3, with the same Stage8 and Action Control used by other options.
        """
        hooks = super()._phase_hooks(
            cycle=cycle, capture=capture,
            goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )
        normal_plan = hooks[1]["planning"]
        normal_register = hooks[3]["competition"]

        def plan_independent_local(ctx):
            # A new deliberation has no inherited paid admission/prospect.
            self._i1_option_intention_paid = None
            normal_plan(ctx)
            self._i1_local_proposal_this_cycle = None
            if self._cycle_degraded or st_before_cycle is None:
                return
            proposal = self._propose_independent_local(
                capture=capture, cycle=cycle,
                st_version=st_before_cycle.version,
            )
            if proposal is None:
                return
            self._i1_local_proposal_this_cycle = proposal
            self._publish_contribution(
                self._planning_contribution(
                    proposal, t_monde=capture.t_monde, cycle=cycle,
                )
            )

        def register_independent_local(ctx):
            normal_register(ctx)
            proposal = self._i1_local_proposal_this_cycle
            if proposal is None or self._cycle_degraded:
                return
            if not self._charge(
                module="competition", operation="competition_register",
            ):
                self._write(
                    kind="i1_local_opportunity_registration", cycle=cycle,
                    data={"option_ref": proposal.option.id,
                          "registered": False, "reason": "insufficient_uc"},
                )
                return
            accepted = self._register_option_proposal(
                proposal=proposal,
                active_goal_id=(
                    None if self.goal_manager.active_goal is None
                    else self.goal_manager.active_goal.id
                ), t_monde=capture.t_monde, cycle=cycle,
            )
            self._write(
                kind="i1_local_opportunity_registration", cycle=cycle,
                data={"option_ref": proposal.option.id, "registered": accepted,
                      "goal_neutral": proposal.option.goal_ref is None},
            )
            if not accepted:
                self._i1_pending.pop("local_opportunity_evidence", None)

        original_control = hooks[4]["action_control"]

        def remember_prospect_before_motor(ctx):
            # A genuine Stage8-evaluated candidate is a cognitive possibility,
            # even when no option crosses Competition's motor threshold.
            # Do NOT make remembering contingent on Action Control admitting
            # or applying an action: the intention is NOT a motor command.
            candidate = self._i1_local_proposal_this_cycle
            results = self._cycle_result
            if (candidate is not None and results is not None
                and not self._cycle_degraded
                and self._i1_option_intention_paid == candidate.option.id
                and candidate.option.provenance == "i1_unknown_affordance"
                and candidate.option.motive_ref.type == "local_opportunity"
                and candidate.option.expires_at_step > capture.t_monde):
                option_ref = candidate.option.id
                trace = next((
                    trace for trace in results.traces
                    if trace.option_ref == option_ref
                ), None)
                assessment = next((
                    evaluation for evaluation in results.evaluations
                    if evaluation.option_ref == option_ref
                    and evaluation.t_monde == capture.t_monde
                    and evaluation.cycle == cycle
                ), None)
                if (trace is not None and assessment is not None
                    and assessment.status == "evaluated"
                    and trace.evidence is not None
                    and trace.evidence > 0.0
                    and trace.accumulator_after > trace.accumulator_before):
                    created = self.memory.remember_considered_option(
                        signature=candidate.option.learning_signature,
                        source_option_ref=option_ref,
                        considered_step=capture.t_monde,
                        cost_uc=_OPTION_INTENTION_COST_UC,
                    )
                    if created:
                        # Write BEFORE the physical dispatch and WAL close.
                        # This is an auditable, paid cognitive occurrence,
                        # not a claim of action admission or accomplishment.
                        self._write(
                            kind="i1_nonspatial_intention_prospected",
                            cycle=cycle,
                            data={
                                "option_ref": option_ref,
                                "signature": candidate.option.learning_signature,
                                "world_step": capture.t_monde,
                                "stage8_evaluated": True,
                                "competition_crossed": trace.crossed,
                                "paid_operation": _OPTION_INTENTION_OPERATION,
                                "motor_admission_inherited": False,
                                "action_applied": False,
                            },
                        )
            # Spatial prospect: the same paid Memory owner, but no command
            # admission is required or inherited. This runs after Stage8.
            geo = self.exploration.geographic
            results = self._cycle_result
            if (geo is not None and results is not None
                and not self._cycle_degraded):
                evaluated = {
                    row.option_ref: row for row in results.evaluations
                    if row.status == "evaluated"
                    and row.t_monde == capture.t_monde
                    and row.cycle == cycle
                }
                for target in geo.place_offered:
                    ref = f"option:place-memory:{target.ref}"
                    row = evaluated.get(ref)
                    trace = next((
                        tr for tr in results.traces if tr.option_ref == ref
                    ), None)
                    if (row is None or trace is None
                        or trace.evidence is None or trace.evidence <= 0
                        or trace.accumulator_after <= trace.accumulator_before):
                        continue
                    proposal = self.competition.proposal_for(ref)
                    if (proposal is None
                        or proposal.option.learning_signature !=
                           f"memory_place_return:{target.entity_id}"):
                        continue
                    if not self._charge(
                        module="planning", operation=_OPTION_INTENTION_OPERATION,
                    ):
                        break
                    created = self.memory.remember_considered_option(
                        signature=proposal.option.learning_signature,
                        source_option_ref=ref,
                        considered_step=capture.t_monde,
                        cost_uc=_OPTION_INTENTION_COST_UC,
                    )
                    if created:
                        self._write(
                            kind="i1_spatial_option_prospected", cycle=cycle,
                            data={"option_ref": ref,
                                  "semantic_ref": proposal.option.learning_signature,
                                  "stage8_evaluated": True,
                                  "motor_admission_inherited": False,
                                  "action_applied": False},
                        )
                    break
            original_control(ctx)

        hooks[1]["planning"] = plan_independent_local
        hooks[3]["competition"] = register_independent_local
        hooks[4]["action_control"] = remember_prospect_before_motor
        return hooks

    def _propose_independent_local(self, *, capture, cycle, st_version):
        """Consider ONE personally accessible interaction, never its result.

        No fixed food or water priority: action availability originates from
        the normal Planning candidate_commands over Perception's current
        SimulationState. The same personally learned Q owner ranks choices;
        absent learned Q, temperament supplies modest exploratory interest.
        """
        state = state_from_capture(
            capture=capture, is_night=self.world.is_night(capture.t_monde),
        )
        available = tuple(self.planning.candidate_commands(state))
        if len(available) > 128:
            self._write(
                kind="i1_local_opportunity_unavailable", cycle=cycle,
                data={"reason": "unbounded_local_candidates"},
            )
            return None
        interactions = local_interaction_choices(available, enabled=True)

        def key(command):
            return (command.primitive, tuple(
                (k, str(command.parameters[k]))
                for k in sorted(command.parameters)
            ))

        already = set()
        if (self._proposal_this_cycle is not None
            and self._proposal_this_cycle.plan is not None):
            already.add(key(self._proposal_this_cycle.plan.steps[0].command))
        for candidate in self.competition.candidate_proposals:
            if (candidate.option.expires_at_step > capture.t_monde
                and candidate.plan is not None and candidate.plan.steps):
                already.add(key(candidate.plan.steps[0].command))
        choices = tuple(c for c in interactions if key(c) not in already)
        self._write(
            kind="i1_local_opportunity_perceived", cycle=cycle,
            data={"accessible_count": len(interactions),
                  "unique_unregistered_count": len(choices),
                  "goal_relevance_filter": False,
                  "goal_option_preserved": self._proposal_this_cycle is not None},
        )
        if not choices:
            # A memory may need suspension even if no NEW local option can
            # be produced (none visible or all already represented by the
            # GoalManager / Competition). Observed accessibility, not
            # independent candidature, decides whether it stays available.
            if (self.memory.applied_option_intention_count
                and self._charge(
                    module="planning", operation=_OPTION_INTENTION_OPERATION,
                )):
                signatures = frozenset(
                    "i1:affordance:" + c.primitive + ":" +
                    (":".join(
                        f"{k}={c.parameters[k]}" for k in sorted(c.parameters)
                    ) or "here")
                    for c in interactions
                )
                self.memory.reconcile_option_intentions(
                    available_signatures=signatures,
                    world_step=capture.t_monde,
                )
            return None
        if not self._charge(module="planning",
                            operation=I1_AFFORDANCE_OPERATION):
            self._write(
                kind="i1_local_opportunity_unavailable", cycle=cycle,
                data={"reason": "insufficient_uc"},
            )
            return None
        # Charge before any durable Memory intent recall. A matching
        # intention is a historical first-person choice, not learned Q
        # evidence, causal reward or extra motor admission.
        intention_paid = self._charge(
            module="planning", operation=_OPTION_INTENTION_OPERATION,
        )
        if intention_paid:
            signatures = frozenset(
                "i1:affordance:" + c.primitive + ":" +
                (":".join(f"{k}={c.parameters[k]}" for k in sorted(c.parameters))
                 or "here")
                for c in interactions
            )
            self.memory.reconcile_option_intentions(
                available_signatures=signatures, world_step=capture.t_monde,
            )
        lived = self._evaluation_state(capture)
        selected = None
        count = len(choices)
        for index, command in enumerate(choices):
            suffix = ":".join(
                f"{k}={command.parameters[k]}" for k in sorted(command.parameters)
            ) or "here"
            signature = f"i1:affordance:{command.primitive}:{suffix}"
            learned = self.q_active.learned_value(lived, signature)
            remembered = (self.memory.recalled_applied_option(
                signature=signature, world_step=capture.t_monde,
            ) if intention_paid else False)
            # Only already UC-funded, currently afforded recollections may be
            # consulted. Contradictory witnessed body changes reduce the
            # confidence of the *memory tie-break*, never learned Q or motor
            # admissibility. This is epistemic uncertainty, not reward.
            witnesses = (self.memory.observed_option_witnesses(
                signature=signature, world_step=capture.t_monde,
            ) if intention_paid and remembered else ())
            rank = _rank_current_local_opportunity(
                learned_evidence=learned.evidence,
                remembered=remembered, witnesses=witnesses,
                rotation=(capture.t_monde + index) % count,
            )
            if selected is None or rank < selected[0]:
                selected = (rank, command, suffix, signature, learned)
        _, command, suffix, signature, learned = selected
        exploration = float(self.temperament_parameters.exploration_coefficient)
        uncertainty = float(self.temperament_parameters.uncertainty_penalty_scale)
        prior = max(0.0, min(1.0, I1_SCORE *
                            (1.0 + .25 * exploration) /
                            (1.0 + .25 * uncertainty)))
        identity = (f"option:i1:local:t{capture.t_monde}:"
                    f"{command.primitive}:{suffix}")
        plan_id = "plan:" + identity + ":v1"
        policy = I1_AFFORDANCE_POLICY + "+goal-independent-v1"
        plan = Plan(
            id=plan_id, option_ref=identity, version=policy,
            steps=(PlanStep(
                index=0, command=command, preconditions=(),
                predicted_consequences=(), observation_window_steps=1,
            ),), goal_ref=None, budget_used_uc=self._i1_unknown_action_cost_uc,
            status="valid", st_version=st_version,
        )
        retained = (set() if self.s_t.current is None else {
            item.contribution_ref for item in self.s_t.current.competitive
        })
        grounded = tuple(sorted(
            ref for ref in self.stage3.perception.observation_ref_by_entity.values()
            if ref in retained
        ))
        option = Option(
            id=identity, version=policy, type="primitive",
            learning_signature=signature,
            preconditions=(), success_condition="step_completed",
            failure_condition="outcome_unconfirmed",
            invalidation_condition="new_real_capture",
            motive_ref=MotiveRef(type="local_opportunity", id=identity),
            founding_st_version=st_version,
            expires_at_step=capture.t_monde + 1,
            provenance="i1_unknown_affordance",
            grounding_contribution_refs=grounded,
            goal_ref=None, plan_ref=plan_id,
        )
        proposal = OptionProposal(
            option=option, plan=plan,
            preliminary_admissibility="indeterminate",
        )
        proposal.validate()
        # The first-person Memory hint only breaks equal-Q ties; it is
        # not a second utility system and never exempts Competition UC.
        self._i1_option_intention_paid = identity if intention_paid else None
        self._i1_pending["local_opportunity_evidence"] = {
            "option_ref": identity, "world_step": capture.t_monde,
            "affordance": True, "prior_evidence": prior,
            "learned_evidence": learned.evidence,
            "learned_value": learned.value, "learned_status": learned.status,
        }
        self._write(
            kind="i1_local_opportunity_proposed", cycle=cycle,
            data={"option_ref": identity, "goal_ref": None,
                  "learning_signature": signature,
                  "command": command.as_dict(),
                  "learned_value_status": learned.status,
                  "prior_evidence": prior,
                  "motor_command_forced": False,
                  "predicted_result": None},
        )
        return proposal

    def _on_open_step_capture(self, capture) -> None:
        super()._on_open_step_capture(capture)
        # Only the next authentic physical capture can resolve a previously
        # applied option. No causal claim or Q reward is generated.
        self.memory.observe_applied_option_followups(
            world_step=capture.t_monde, body_after=capture.body,
        )

    def _dispatch_decision(self, *, proposal, prepared, admission,
                           cycle, sent_t_monde):
        execution = super()._dispatch_decision(
            proposal=proposal, prepared=prepared, admission=admission,
            cycle=cycle, sent_t_monde=sent_t_monde,
        )
        # No late WAL write. The M11 outer transaction exports owner state
        # after the full natural run_step; Action Control already committed.
        if (execution.status == "applied"
            and not self._fallback_used_this_cycle
            and getattr(self, "_i1_option_intention_paid", None)
                == proposal.option.id
            and proposal.option.provenance == "i1_unknown_affordance"
            and proposal.option.motive_ref.type == "local_opportunity"
            and proposal.plan is not None
            and self.stage3.control.current_step[0] == proposal.option.id):
            self.memory.remember_applied_option(
                signature=proposal.option.learning_signature,
                source_option_ref=proposal.option.id,
                applied_step=sent_t_monde,
                cost_uc=_OPTION_INTENTION_COST_UC,
                body_before=(
                    self.stage3._capture.body
                    if self.stage3._capture is not None
                    and self.stage3._capture.t_monde == sent_t_monde
                    else None
                ),
            )
        return execution

    def _consider_uncertain_affordance(
        self, *, capture, goal, st_version, cycle, exact,
    ):
        """Optional, paid, first-person private evidence on an unknown option.

        An executable Stage6 plan has priority. SlowHistory is not an active
        planner, safety oracle or motor authority: a privately consolidated
        effect can only give a bounded *advisory* preference to an already
        perceived and otherwise admissible action. All outcomes remain unknown
        and Action Control must independently admit any eventual command.
        """
        if exact is not None:
            return None
        proposed = super()._consider_uncertain_affordance(
            capture=capture, goal=goal, st_version=st_version,
            cycle=cycle, exact=exact,
        )
        if proposed is None or proposed.plan is None:
            return proposed
        command = proposed.plan.steps[0].command
        field = _PRIVATE_OBSERVED_FIELDS.get(command.primitive)
        if field is None:
            return proposed
        # Optional recall must not degrade a viable current decision when
        # its planning envelope is exhausted. The Scheduler's pure capacity
        # quote is not a cognitive lookup and consumes no UC; whenever
        # affordable, the real memory inspection is still explicitly priced
        # through _charge BEFORE reading its committed history.
        availability = self.compute_budget.quote_operations(
            module="planning", operations=(_PRIVATE_RECALL_OPERATION,),
        )
        if not availability.affordable:
            return proposed
        if not self._charge(
            module="planning", operation=_PRIVATE_RECALL_OPERATION,
        ):
            return proposed
        # Active advisory belongs to the canonical Value/Needs owner and
        # exists only AFTER the six-pass, coordinator-acknowledged publication.
        # A merely prepared/private skill must not masquerade as active.
        command_parameters = dict(command.parameters)
        rows = self.value_needs.matching_active_observed_procedures(
            primitive=command.primitive,
            parameters=command_parameters,
            observed_field=field,
        )
        if type(rows) is not list:
            raise ValueError("invalid committed active procedural advisory")
        matched = []
        for item in rows:
            if (type(item) is not dict
                    or item.get("state") != "compiled_private"
                    or item.get("evidence_scope")
                        != "experienced_local_physical_result"
                    or item.get("goal_success_inferred") is not False
                    or item.get("safety_certified") is not False
                    or item.get("primitive") != command.primitive
                    or item.get("parameters") != command_parameters
                    or item.get("observed_field") != field):
                continue
            scope = item.get("near_context")
            successes = item.get("distinct_success_count")
            trials = item.get("distinct_trial_count")
            ratio = item.get("success_rate")
            if (type(scope) is not dict
                    or any(type(scope.get(key)) is not int
                           for key in ("x", "y", "radius"))
                    or type(successes) is not int
                    or type(trials) is not int
                    or successes < 2 or trials < successes
                    or type(ratio) not in (float, int)
                    or not 0.0 <= ratio <= 1.0):
                continue
            distance = (abs(capture.x - scope["x"])
                        + abs(capture.y - scope["y"]))
            if distance <= scope["radius"]:
                matched.append(item)
        if not matched:
            return proposed
        # Choose a single private witness family, never count overlapping
        # nearby context summaries as independent evidence.
        match = min(
            matched, key=lambda row: (
                -row["distinct_success_count"], -row["success_rate"],
                row["id"],
            ),
        )
        confidence = (float(match["success_rate"])
                      * min(1.0, match["distinct_success_count"] / 4.0))
        boost = min(0.12, 0.12 * confidence)
        existing = float(self._i1_pending["prior_evidence"])
        self._i1_pending["prior_evidence"] = min(1.0, existing + boost)
        self._i1_pending["private_procedure_refs"] = (match["id"],)
        self._write(
            kind="i1_private_procedure_recall_considered", cycle=cycle,
            data={
                "policy": _PRIVATE_RECALL_VERSION,
                "option_ref": proposed.option.id,
                "active_owner": "value_and_needs",
                "committed_history_version": self.slow_history.current_version,
                "procedure_ref": match["id"],
                "source_episode_refs": list(match["source_episode_refs"]),
                "source_event_refs": list(match["source_event_refs"]),
                "advisory_evidence_increase": boost,
                "effects_predicted": False,
                "goal_success_inferred": False,
                "safety_certified": False,
                "command_forced": False,
            },
        )
        return proposed

    @property
    def temperament_parameters(self):
        """Read the canonical Stage11 birth-frozen Stage5 projection.

        Stage11 does not inherit Stage5Runtime; it carries the projected
        parameters explicitly in its own immutable versioned config. The
        natural actor must not read an absent Stage5 property or raw tau.
        """
        return self._stage11_config.temperament_parameters

    def _propose_for_cycle(
        self, *, capture, goal_for_planning, st_before_cycle, cycle,
    ):
        proposal = super()._propose_for_cycle(
            capture=capture, goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle, cycle=cycle,
        )
        if (proposal is not None or goal_for_planning is None
                or self._cycle_degraded):
            # A rejected UC charge is not proof that a need cannot be met.
            # Do not install a refractory goal after a budget refusal.
            return proposal
        if (self.goal_manager.active_goal is None
                or self.goal_manager.active_goal.id != goal_for_planning.id):
            return proposal
        # A world step can contain multiple paid cognitive cycles, but all
        # those cycles observe the SAME physical capture. Count an inability
        # to plan at most once for that observation and active goal.
        observation_key = (capture.t_monde, goal_for_planning.id)
        if self._i1_last_nonplannable_observation == observation_key:
            return proposal
        # Native GoalManager failure accounting instead of H1's specialist
        # arm. Genuine unchanged first-person context is required; an
        # unmodelled effect is not misrepresented as a successful action.
        context = sha256_hex(canonical_causal_bytes({
            "goal": goal_for_planning.goal_type,
            "target": goal_for_planning.target,
            "position": [capture.x, capture.y],
            # Do not include continuously decaying numeric body values.
            # Otherwise the context SHA changes every step and refractory
            # failures can never accumulate even in identical local geometry.
            "inventory": dict(capture.inventory),
            "current_resources": list(capture.current_resources),
            "current_water_source": capture.current_water_source,
            "adjacent": [
                [cell.direction, cell.passable, cell.water_source,
                 list(cell.resources)]
                for cell in capture.adjacent
            ],
        }))
        # This is a GoalManager operation, charged to the existing canonical
        # goal arbitration budget instead of minting a new H1 UC entitlement.
        if not self._charge(module="goal_manager", operation="goal_arbitrate"):
            return proposal
        self._i1_last_nonplannable_observation = observation_key
        released = self.goal_manager.note_non_plannable(
            material_context_hash=context, t_monde=capture.t_monde
        )
        self._write(kind="i1_goal_unavailable_reconsidered", cycle=cycle, data={
            "goal_ref": goal_for_planning.id,
            "perceived_context_sha256": context,
            "goal_released": released,
            "new_goal_forced": False,
            "success_inferred": False,
        })
        if released:
            self.planning.invalidate_current()
            self.competition.prune_invalid(
                active_goal_id=None, t_monde=capture.t_monde
            )
        return proposal
