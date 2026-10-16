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

_PRIVATE_RECALL_VERSION = "i1-private-procedure-advisory-v1"
_PRIVATE_RECALL_OPERATION = "i1_private_procedure_recall"
_PRIVATE_RECALL_COST_UC = 1
_PRIVATE_OBSERVED_FIELDS = {
    "boire": "drank",
    "collecter": "collected",
    "fabriquer_outil": "tool_crafted",
    "poser_une_pierre": "stone_placed",
}

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


class I1Runtime(I1WaterPrudentRuntime):
    """Default I1 actor. H1/H2 are not part of its inheritance graph."""

    individual_id = "i1-natural-default-v1"

    def __init__(self, **kwargs):
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
                version="i1-firstperson-frontier-v1",
                novelty_weight=0.15, max_distinct_sites=1024,
                max_targets_per_cycle=1,
                observe_routes=False, refresh_surveys=False,
            )
            cfg = replace(
                cfg, version=cfg.version + "+i1-firstperson-frontier-v1",
                geographic=geographic, intrinsic_weight=min(cfg.intrinsic_weight, 0.35),
                local_threat_alerts=True,
                geographic_capacity_guard_enabled=True,
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
        kwargs["stage11_config"] = cfg
        # Both integrated stages must agree on the identical frozen Stage9
        # substrate after temperament projection, before creating the body.
        sleep_cfg = kwargs.get("stage10_config")
        if sleep_cfg is None:
            raise ValueError("natural I1 birth requires Stage10 configuration")
        kwargs["stage10_config"] = replace(
            sleep_cfg, version=sleep_cfg.version + "+i1-birth-temperament-v1",
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
        self._i1_last_nonplannable_observation = None
        super().__init__(**kwargs)

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
        budget = replace(
            original,
            version=original.version + "+" + _PRIVATE_RECALL_VERSION,
            cycle_ceiling=original.cycle_ceiling + _PRIVATE_RECALL_COST_UC,
            module_envelopes={
                **original.module_envelopes,
                "planning": original.module_envelopes["planning"]
                + _PRIVATE_RECALL_COST_UC,
            },
            operation_costs={
                **original.operation_costs,
                _PRIVATE_RECALL_OPERATION: _PRIVATE_RECALL_COST_UC,
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
        private = self.slow_history.read_committed()
        rows = private.get("procedural", ())
        if type(rows) is not list:
            raise ValueError("invalid committed private procedure index")
        matched = []
        for item in rows:
            if (type(item) is not dict
                    or item.get("state") != "compiled_private"
                    or item.get("evidence_scope")
                        != "experienced_local_physical_result"
                    or item.get("goal_success_inferred") is not False
                    or item.get("safety_certified") is not False
                    or item.get("primitive") != command.primitive
                    or item.get("parameters") != dict(command.parameters)
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
                "private_history_version": self.slow_history.current_version,
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
