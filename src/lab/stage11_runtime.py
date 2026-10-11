"""I0-vNext incremental Stage-11 Exploration runtime.

The historical Stage-9 implementation, results and scientific NO-GO are
untouched. The scheduler, Competition and Action Control retain authority.
"""
from dataclasses import dataclass, replace
from math import isfinite

from i0.modules.exploration import Exploration, ExplorationConfig
from i0.contracts import Contribution
from i0.interfaces import PrimitiveCommand
from i0.modules.geographic_exploration import GeographicExplorationConfig
from i0.modules.geographic_planning import propose_geographic_frontier
from i0.modules.action_control import Admissibility, PreparedCommand
from i0.modules.simulator import state_from_capture
from i0.modules.global_modulation import GlobalModulation, ModulationConfig
from i0.modules.lived_prediction import LivedPredictionConfig, LivedWaterPredictor
from i0.modules.memory import EpisodicMemory
from i0.modules.stage11_evaluator import Stage11OptionEvaluator
from i0.temperament import ParametresTemperament

from .stage9_runtime import Stage9Config, Stage9Runtime


@dataclass(frozen=True)
class Stage11Config:
    version: str
    stage9: Stage9Config
    exploration: ExplorationConfig
    modulation: ModulationConfig
    temperament_parameters: ParametresTemperament
    intrinsic_weight: float
    exploration_envelope_uc: int
    exploration_observe_cost_uc: int
    # None retains the Stage-11 reference's prediction-unavailable behavior.
    prospective_water: LivedPredictionConfig | None = None
    # Off by default: public geographical frontier integration, Stage-11 only.
    geographic: GeographicExplorationConfig | None = None
    # Local physically perceived risk alerts; historical vNext reference OFF.
    local_threat_alerts: bool = False

    def validate(self):
        if not self.version:
            raise ValueError("Stage-11 runtime version required")
        self.stage9.validate()
        self.exploration.validate()
        self.modulation.validate()
        self.temperament_parameters.validate()
        if self.prospective_water is not None:
            self.prospective_water.validate()
        if self.geographic is not None:
            self.geographic.validate()
        if type(self.local_threat_alerts) is not bool:
            raise ValueError("local threat sensor switch must be boolean")
        if not isfinite(self.intrinsic_weight) or self.intrinsic_weight < 0:
            raise ValueError("invalid P-15")
        if (type(self.exploration_envelope_uc) is not int
            or type(self.exploration_observe_cost_uc) is not int
            or self.exploration_envelope_uc < 0
            or self.exploration_observe_cost_uc < 0):
            raise ValueError("invalid P-43 Exploration envelope/cost")

    def with_budget(self):
        stage8 = self.stage9.stage8
        stage7 = replace(
            stage8.stage7,
            memory=replace(
                stage8.stage7.memory,
                version=(
                    stage8.stage7.memory.version
                    + "+atomic-world-step-length-v1"
                ),
            ),
        )
        stage6 = stage7.stage6
        stage4 = stage6.stage4
        budget = stage4.compute_budget
        amended = replace(
            budget, version=budget.version + "+" + self.version,
            module_envelopes={
                **budget.module_envelopes,
                "exploration": self.exploration_envelope_uc,
            },
            operation_costs={
                **budget.operation_costs,
                "exploration_observe": self.exploration_observe_cost_uc,
            },
        )
        return replace(self.stage9, stage8=replace(
            stage8, stage7=replace(
                stage7, stage6=replace(
                    stage6, stage4=replace(stage4, compute_budget=amended),
                ),
            ),
        ))


class Stage11Runtime(Stage9Runtime):
    individual_id = "i0-vnext-stage11"

    def __init__(self, *, world_config, layout, safety_config, safety_facts,
                 protected_integrity_threshold, config: Stage11Config, equipment,
                 scenario_id=None, scenario_version=None, scenario_events=()):
        config.validate()
        self._stage11_config = config
        # Stateless descriptive forecaster: reads the canonical owner's
        # frozen prior physical evidence, never corrects frozen Equipment.
        self.lived_water_predictor = (
            None if config.prospective_water is None
            else LivedWaterPredictor(config.prospective_water)
        )
        self._stage11_prospective_state = None
        self._stage11_prospective_capture = None
        super().__init__(
            world_config=world_config, layout=layout,
            safety_config=safety_config, safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            config=config.with_budget(), equipment=equipment,
            scenario_id=scenario_id, scenario_version=scenario_version,
            scenario_events=scenario_events,
        )
        # Construct the vNext-only Memory variant before the first world
        # step. Stage 7--9 historical Memory objects remain in their
        # original event-level length-boundary mode (and config version).
        if self.memory.episodes or self.memory.intentions:
            raise ValueError("cannot switch Memory boundary contract mid-life")
        self.memory = EpisodicMemory(
            self._stage7_config.memory,
            atomic_world_step_length_boundary=True,
        )
        self.exploration = Exploration(
            config.exploration,
            coefficient=config.temperament_parameters.exploration_coefficient,
            geographic_config=config.geographic,
        )
        self._stage11_geographic_proposals_this_cycle = ()

        self.modulation = GlobalModulation(config.modulation)
        self._stage11_modulation_signals = {
            "boredom": False, "needs_satisfied": False,
        }
        self.stage8_option_evaluator = Stage11OptionEvaluator(
            config=config.stage9.stage8.evaluation,
            stage6=self.option_evaluator, q_values=self.q_active,
            exploration=self.exploration, intrinsic_weight=config.intrinsic_weight,
        )

    @property
    def causal_owners(self):
        return (*super().causal_owners, self.exploration, self.modulation)

    def _gatekeeper_profile_multipliers(self):
        # P-23: per-cycle coefficients; Gatekeeper retains sole scoring state.
        return self.modulation.multipliers()

    def _profile_state(self):
        return {
            "name": self.modulation.profile,
            "version": self._stage11_config.modulation.version,
        }

    def _on_open_step_capture(self, capture) -> None:
        """Account for one physically observed location, even on reflex steps.

        The captured position is known BEFORE the reflex sender's checkpoint.
        No frontier is proposed here: the Phase-1 Exploration producer still
        designates targets from its pre-phase frozen input. A reflex with no
        cognitive cycles therefore cannot hide an actually visited site.
        """
        super()._on_open_step_capture(capture)
        geo = self.exploration.geographic
        if geo is None:
            return
        observed = self.exploration.observe_geographic_capture(capture)
        if observed:
            self._write(
                kind="stage11_geographic_visit_observed",
                cycle=1,
                data={
                    "source": "perception_capture",
                    "world_step": capture.t_monde,
                    "position": [capture.x, capture.y],
                    "new_distinct_sites": geo.distinct_sites,
                    "visit_count": geo.visit_count,
                    "accounting_boundary": "step_open_before_reflex",
                },
            )

    def _st_additional_fixed(self):
        # Captured before phase 1. The next cycle reads it via frozen S_t.
        return {"modulation_signals": dict(self._stage11_modulation_signals)}

    def _geographic_frontier_targets(self, capture):
        """Use Action Control's published *contextual* admissibility service.

        EN normative §9.4 allows early Planning filtering of definitely
        prohibited options. This is not a duplicate or a cache of safety
        facts; only the existing Action Control service can decide.
        "Indeterminate" is still a candidate. Recompute on every phase-0
        snapshot so any later safety fact reclassification takes effect.
        """
        if self.exploration.geographic is None:
            return (), ()
        forbidden = []
        for cell in capture.adjacent:
            if cell.passable is not True or cell.creature is True:
                continue
            prepared = PreparedCommand(
                command=PrimitiveCommand(
                    "se_deplacer", {"direction": cell.direction},
                ),
                source="decision",
            )
            if self.stage3.control.verifier_admissibilite(
                capture=capture, prepared=prepared,
            ) is Admissibility.INADMISSIBLE:
                forbidden.append(
                    (cell.direction, (cell.x, cell.y))
                )
        targets = self.exploration.geographic_cibles(
            capture,
            inadmissible_directions=frozenset(
                direction for direction, _ in forbidden
            ),
        )
        return targets, tuple(sorted(forbidden))

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        # Frozen input precedes all producers of phase 1 (INV-08).
        frozen = self.causal_model.export_causal_state()
        # Read-only frontier inputs are frozen BEFORE phase-1. No Planning
        # producer may read Exploration output from the same phase (INV-08).
        frozen_geo_targets, excluded_geo = self._geographic_frontier_targets(
            capture,
        )
        self._stage11_prospective_state = frozen
        self._stage11_prospective_capture = (
            capture.t_monde, (capture.x, capture.y), float(capture.body["water"]),
        )
        # These phase-2 S_t fields are captured BEFORE phase-1 producers run.
        # The current step's physical needs and previous Exploration state
        # cannot influence the profile until S_t publishes for a NEXT cycle.
        need_state = self._step_need_state
        adjacent = capture.adjacent
        complete_local_scan = (
            len(adjacent) == 4
            and {item.direction for item in adjacent}
            == {"north", "south", "east", "west"}
            and all(type(item.creature) is bool for item in adjacent)
        )
        self._stage11_modulation_signals = {
            "boredom": self.exploration.boredom_detected(),
            "needs_satisfied": (
                False if need_state is None
                else all(float(v) == 0.0 for v in need_state.deficits.values())
            ),
            # An actual full local scan with no adjacent creature is
            # affirmative LOCAL clearance, never a global safety oracle.
            # This field is read only from the subsequently published S_t,
            # and profile exit still requires hysteresis plus confirmed steps.
            **(
                {"threat_clear": True}
                if (self._stage11_config.local_threat_alerts
                    and complete_local_scan
                    and not capture.adjacent_creatures)
                else {}
            ),
        }
        hooks = super()._phase_hooks(
            cycle=cycle, capture=capture, goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )

        previous_modulation_hook = hooks[0]["global_modulation"]

        def modulation_hook(ctx):
            previous_modulation_hook(ctx)
            old = self.modulation.profile
            indicators = self.modulation.indicators_from_st(st_before_cycle)
            new = self.modulation.freeze(
                signals=indicators, world_step=capture.t_monde, cycle=cycle,
            )
            if old != new:
                self._write(
                    kind="stage11_modulation_transition", cycle=cycle,
                    data={
                        "before": old, "after": new,
                        "profile_version": self._stage11_config.modulation.version,
                        "source_st_version": (
                            None if st_before_cycle is None
                            else st_before_cycle.version
                        ),
                    },
                )
        hooks[0]["global_modulation"] = modulation_hook

        previous_perception_hook = hooks[1]["perception"]

        def local_threat_perception_hook(ctx):
            previous_perception_hook(ctx)
            if (
                not self._stage11_config.local_threat_alerts
                or cycle != 1 or not complete_local_scan
                or not capture.adjacent_creatures
            ):
                return
            if not self._charge(
                module="perception", operation="perception_publish",
            ):
                return
            observed = tuple(
                sorted((cell.x, cell.y)
                       for cell in capture.adjacent_creatures)
            )
            event_refs = tuple(
                f"local-percept:{capture.t_monde}:creature:{x}:{y}"
                for x, y in observed
            )
            alert = Contribution(
                id=f"stage11:local-creature-alert:{capture.t_monde}",
                schema_version="mvp-v1.2.1",
                type="alert",
                summary="adjacent creature physically observed",
                subject_ref="local:adjacent-creature-threat",
                emitter_module="perception",
                signal_family="world_symbolic",
                confidence=1.0,
                urgency=1.0,
                risk=1.0,
                value=0.0,
                production_t=capture.t_monde,
                production_cycle=cycle,
                expires_at_step=capture.t_monde + 1,
                payload={
                    "kind": "locally_observed_adjacent_creature",
                    "source": "single_perceptual_capture",
                    "observed_positions": [
                        [x, y] for x, y in observed
                    ],
                    "local_radius": 1,
                    "global_threat_clearance": False,
                },
                provenance_inputs=event_refs,
                signal_ids=event_refs,
            )
            self._publish_contribution(alert)
            self._write(
                kind="stage11_local_threat_alert_proposed", cycle=cycle,
                data={
                    "contribution_ref": alert.id,
                    "source": "local_perception",
                    "observed_positions": [
                        [x, y] for x, y in observed
                    ],
                    "risk": 1.0,
                    "global_threat_clearance": False,
                },
            )

        hooks[1]["perception"] = local_threat_perception_hook

        def exploration_hook(_context):
            if not self._charge(module="exploration", operation="exploration_observe"):
                return
            previous = self.exploration.export_causal_state()
            self.exploration.observe_causal_state(frozen)
            # DC-07: even when the present cycle is degraded, a genuine
            # physical capture may update the visited ledger, but NO new
            # target is designated or retained as offered for that cycle.
            new_geo_visit = self.exploration.observe_geographic_capture(
                capture, frozen_targets=(
                    () if self._cycle_degraded else frozen_geo_targets
                ),
            )
            if new_geo_visit:
                self._write(
                    kind="stage11_geographic_visit_observed", cycle=cycle,
                    data={
                        "source": "perception_capture",
                        "world_step": capture.t_monde,
                        "position": [capture.x, capture.y],
                        "new_distinct_sites": (
                            self.exploration.geographic.distinct_sites
                        ),
                        "visit_count": (
                            self.exploration.geographic.visit_count
                        ),
                    },
                )
            current = self.exploration.export_causal_state()
            if current != previous:
                self._write(
                    kind="stage11_exploration_updated", cycle=cycle,
                    data={
                        "version": self._stage11_config.exploration.version,
                        "question_refs": [ref for ref, _ in current["questions"]],
                        "verified_visits": sum(
                            q["visits"] for _, q in current["questions"]
                        ),
                    },
                )

        hooks[1]["exploration"] = exploration_hook

        # Stage-9's canonical Causal Model still proposes supported tests.
        # In vNext, a *previously known* Exploration target with no
        # remaining information interest must not be converted by Planning
        # into another autonomous option just because the hypothesis
        # remains published. This avoids noisy-TV repetition and clears
        # already registered, now-stale tests via Stage-9 registration.
        #
        # Capture this read-only decision BEFORE phase 1. The Planning
        # producer cannot borrow Exploration state newly written during
        # the same phase; first-seen hypotheses keep the Stage-9 path until
        # their next-cycle Exploration state is available (INV-08).
        known = {
            ref for ref, _ in self.exploration.export_causal_state()["questions"]
        }
        interested = set(self.exploration.cibles())
        previous_plan = hooks[1]["planning"]

        def plan_only_informational_targets(ctx):
            self._stage11_geographic_proposals_this_cycle = ()
            # One diagnostic per real step; never repeatedly charge Planning
            # for a direction that Action Control already said was forbidden.
            if cycle == 1 and excluded_geo:
                self._write(
                    kind="stage11_geographic_admissibility_prefiltered",
                    cycle=cycle,
                    data={
                        "source": "action_control.verifier_admissibilite",
                        "admissibility": "inadmissible",
                        "world_step": capture.t_monde,
                        "excluded": [
                            {
                                "direction": direction,
                                "destination": list(destination),
                            }
                            for direction, destination in excluded_geo
                        ],
                        "count": len(excluded_geo),
                        "cached": False,
                        "global_safety_claim": False,
                    },
                )
            emitted = self._causal_test_targets_this_cycle
            permitted = tuple(
                item for item in emitted
                if item.contingency_ref not in known
                or item.contingency_ref in interested
            )
            for item in emitted:
                if item not in permitted:
                    self._write(
                        kind="stage11_exploration_target_suppressed",
                        cycle=cycle,
                        data={
                            "contingency_ref": item.contingency_ref,
                            "reason": "no_positive_informational_interest",
                            "exploration_version": (
                                self._stage11_config.exploration.version
                            ),
                        },
                    )
            self._causal_test_targets_this_cycle = permitted
            previous_plan(ctx)
            if (
                self.exploration.geographic is None
                or not frozen_geo_targets
                or self._cycle_degraded or st_before_cycle is None
            ):
                return
            initial_state = state_from_capture(
                capture=capture,
                is_night=self.world.is_night(capture.t_monde),
            )
            geo_proposals = []
            for target in frozen_geo_targets:
                if not self._charge(
                    module="planning", operation="planning_build",
                ):
                    break
                proposal = propose_geographic_frontier(
                    target=target, initial_state=initial_state,
                    simulator=self.simulator,
                    st_version=st_before_cycle.version,
                    t_monde=capture.t_monde,
                    ttl_steps=self._stage6_config.planning.option_ttl_steps,
                )
                if proposal is None or (
                    self.stage3.control.verifier_plan_connu(proposal)
                    is Admissibility.INADMISSIBLE
                ) or (
                    proposal is not None
                    and self.stage3.control.verifier_admissibilite(
                        capture=capture,
                        prepared=PreparedCommand(
                            command=proposal.plan.steps[0].command,
                            source="decision",
                            option_ref=proposal.option.id,
                        ),
                    ) is Admissibility.INADMISSIBLE
                ):
                    self._write(
                        kind="stage11_geographic_planning_unavailable",
                        cycle=cycle,
                        data={
                            "target_ref": target.ref,
                            "reason": "simulation_or_admissibility_unavailable",
                        },
                    )
                    continue
                self._publish_contribution(
                    self._planning_contribution(
                        proposal, t_monde=capture.t_monde, cycle=cycle,
                    )
                )
                geo_proposals.append(proposal)
                self._write(
                    kind="stage11_geographic_option_proposed", cycle=cycle,
                    data={
                        "target_ref": target.ref,
                        "option_ref": proposal.option.id,
                        "source": "single_perceptual_capture",
                        "destination": list(target.destination),
                        "direction": target.direction,
                        "goal_ref": None,
                        "simulated": bool(
                            proposal.plan.steps[0].predicted_consequences
                        ),
                        "simulation_status": (
                            "complete" if proposal.plan.steps[0].predicted_consequences
                            else "unavailable"
                        ),
                        "simulation_reason": (
                            None if proposal.plan.steps[0].predicted_consequences
                            else "equipment_input_unseen"
                        ),
                    },
                )
            self._stage11_geographic_proposals_this_cycle = tuple(
                geo_proposals
            )

        hooks[1]["planning"] = plan_only_informational_targets

        previous_register = hooks[3]["competition"]

        def register_geographic_targets(ctx):
            previous_register(ctx)
            current = {
                proposal.option.id
                for proposal in self._stage11_geographic_proposals_this_cycle
            }
            for old in self.competition.candidate_proposals:
                if (
                    old.option.motive_ref.type == "cible_exploration"
                    and old.option.id not in current
                ):
                    self.competition.invalidate_candidate(old.option.id)
                    self.stage3.control.clear_option_step(old.option.id)
            if self._cycle_degraded:
                return
            for proposal in self._stage11_geographic_proposals_this_cycle:
                if not self._charge(
                    module="competition", operation="competition_register",
                ):
                    break
                accepted = self._register_option_proposal(
                    proposal=proposal,
                    active_goal_id=(
                        None if self.goal_manager.active_goal is None
                        else self.goal_manager.active_goal.id
                    ),
                    t_monde=capture.t_monde,
                    cycle=cycle,
                )
                self._write(
                    kind="stage11_geographic_option_registration",
                    cycle=cycle,
                    data={
                        "option_ref": proposal.option.id,
                        "registered": accepted,
                    },
                )
        hooks[3]["competition"] = register_geographic_targets
        return hooks

    def _dispatch_decision(
        self, *, proposal, prepared, admission, cycle, sent_t_monde,
    ):
        # Visit counters follow the verified Action Control application,
        # never phase-1 proposals or Competition threshold crossings.
        # A lethal rollback restores Exploration alongside other owners.
        if (
            self.lived_water_predictor is not None
            and prepared.command.primitive == "boire"
            and not prepared.predicted_consequences
            and self.stage8_option_evaluator._safe_causal_test_shape(proposal)
            and self._stage11_prospective_state is not None
            and self._stage11_prospective_capture is not None
        ):
            captured_t, captured_position, captured_water = (
                self._stage11_prospective_capture
            )
            if captured_t != sent_t_monde:
                raise ValueError("stale prospective Perception capture")
            prior = self.lived_water_predictor.predict(
                canonical_state=self._stage11_prospective_state,
                t_monde=sent_t_monde,
                position=captured_position,
                water_before=captured_water,
            )
            if prior is not None:
                # Add one P-47 prediction BEFORE the send. This is
                # descriptive and comes exclusively from earlier independently
                # Memory-closed real steps. The original Option/Plan, E_sim,
                # and frozen Equipment predictions are not modified.
                prepared = replace(
                    prepared,
                    predicted_consequences=(prior.consequence,),
                )
                self._write(
                    kind="stage11_prospective_prediction_frozen",
                    cycle=cycle,
                    data={
                        "option_ref": proposal.option.id,
                        "sent_t_monde": sent_t_monde,
                        "prediction_source": "prior_closed_lived_observation",
                        "predictor_version": prior.config_version,
                        "variable": prior.consequence.variable,
                        "predicted": prior.consequence.value_or_delta,
                        "precision": prior.consequence.precision,
                        "source_transition_refs": list(
                            prior.source_transition_refs
                        ),
                        "source_episode_refs": list(
                            prior.source_episode_refs
                        ),
                        "source_steps": list(prior.source_steps),
                        "causal_validation": False,
                    },
                )
        execution = super()._dispatch_decision(
            proposal=proposal, prepared=prepared, admission=admission,
            cycle=cycle, sent_t_monde=sent_t_monde,
        )
        if (
            execution.status == "applied"
            and prepared.command.primitive == "boire"
            and self.stage8_option_evaluator._safe_causal_test_shape(proposal)
        ):
            self.exploration.record_applied_causal_test(
                option=proposal.option, sent_step=sent_t_monde,
            )
        return execution

    def _evaluate_competition_cycle(self, *, capture, cycle):
        result = super()._evaluate_competition_cycle(capture=capture, cycle=cycle)
        for assessment in result.evaluations:
            if assessment.intrinsic_status == "applicable":
                self._write(
                    kind="stage11_intrinsic_evaluation", cycle=cycle,
                    data={
                        "option_ref": assessment.option_ref,
                        "status": assessment.status,
                        "intrinsic_value": assessment.intrinsic_value,
                        "signal_ids": list(assessment.signal_ids),
                        "intrinsic_producers": list(assessment.producers),
                        "P15_intrinsic_weight": self._stage11_config.intrinsic_weight,
                    },
                )
        return result
