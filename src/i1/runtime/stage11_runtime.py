"""I0-vNext incremental Stage-11 Exploration runtime.

The historical Stage-9 implementation, results and scientific NO-GO are
untouched. The scheduler, Competition and Action Control retain authority.
"""
from dataclasses import dataclass, replace
from math import isfinite

from i1.modules.exploration import Exploration, ExplorationConfig
from i1.contracts import Contribution
from i1.interfaces import PrimitiveCommand
from i1.modules.geographic_exploration import GeographicExplorationConfig
from i1.modules.geographic_planning import (
    propose_geographic_frontier, propose_geographic_transit, propose_spatial_return,
)
from i1.modules.observed_frontier_routing import (
    find_observed_frontier_route, GeographicTransitTarget,
)
from i1.modules.spatial_memory import find_spatial_return, PlaceMemory
from i1.modules.action_control import Admissibility, PreparedCommand
from i1.modules.simulator import state_from_capture
from i1.modules.global_modulation import GlobalModulation, ModulationConfig
from i1.modules.lived_prediction import LivedPredictionConfig, LivedWaterPredictor
from i1.modules.memory import EpisodicMemory
from i1.modules.stage11_evaluator import Stage11OptionEvaluator
from i1.temperament import ParametresTemperament

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
    # Public development-only matched legacy/no-prefilter compatibility
    # ablation. Default True when geography is enabled; veto unchanged.
    geographic_preflight: bool = True
    # v4: gate the 1-UC preflight on an existing *raw* physical frontier.
    # False pins the eager-v3 software comparison. No safety cache.
    geographic_preflight_requires_frontier: bool = True
    # Local physically perceived risk alerts; historical vNext reference OFF.
    local_threat_alerts: bool = False
    geographic_route_enabled: bool = False
    # Strict opt-in: passive Scheduler UC admission before paid geo preflight.
    geographic_capacity_guard_enabled: bool = False
    # Public software custody ablation: world-step/attempt/cycle identity
    # is tracked in the causal UC owner; all historical runs default OFF.
    cycle_occurrence_guard_enabled: bool = False
    instrumental_geographic_value: bool = False

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
        if type(self.instrumental_geographic_value) is not bool:
            raise ValueError("instrumental geographic flag must be boolean")
        if self.instrumental_geographic_value and self.geographic is None:
            raise ValueError("instrumental geographic value requires geographic exploration")
        if type(self.geographic_preflight) is not bool:
            raise ValueError("geographic safety preflight flag must be bool")
        if type(self.geographic_preflight_requires_frontier) is not bool:
            raise ValueError("geographic frontier preflight gate flag must be bool")
        if type(self.geographic_route_enabled) is not bool:
            raise ValueError("route enabled flag must be bool")
        if type(self.geographic_capacity_guard_enabled) is not bool:
            raise ValueError("geographic capacity guard must be boolean")
        if type(self.cycle_occurrence_guard_enabled) is not bool:
            raise ValueError("cycle occurrence guard must be boolean")
        if self.geographic_capacity_guard_enabled and (
            self.geographic is None or not self.geographic_preflight
            or not self.geographic_preflight_requires_frontier
        ):
            raise ValueError(
                "capacity guard requires demand-gated charged geographic preflight"
            )
        if self.geographic_route_enabled and (
            self.geographic is None or not self.geographic.observe_routes
            or not self.geographic_preflight
        ):
            raise ValueError("route requires opted-in surveys and charged preflight")
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
            budget, version=(
                budget.version + "+" + self.version
                + (
                    "+geographic-demand-preflight-v1"
                    if (self.geographic is not None
                        and self.geographic_preflight
                        and self.geographic_preflight_requires_frontier)
                    else ""
                )
                + (
                    "+phase1-charged-geographic-preflight-v3"
                    if (
                        self.geographic is not None
                        and self.geographic_preflight
                    ) else ""
                )
                + (
                    "+route-site-cap-stop-v1"
                    if self.geographic_route_enabled else ""
                )
                + (
                    "+scheduler-geo-capacity-guard-v1"
                    if self.geographic_capacity_guard_enabled else ""
                )
                + (
                    "+scheduler-cycle-occurrence-custody-v1"
                    if self.cycle_occurrence_guard_enabled else ""
                )
            ),
            cycle_occurrence_guard=self.cycle_occurrence_guard_enabled,
            module_envelopes={
                **budget.module_envelopes,
                "exploration": self.exploration_envelope_uc,
            },
            operation_costs={
                **budget.operation_costs,
                "exploration_observe": self.exploration_observe_cost_uc,
                **({"geographic_route_search": 1}
                   if self.geographic_route_enabled else {}),
                **(
                    {"geographic_admissibility_preflight": 1}
                    if (
                        self.geographic is not None
                        and self.geographic_preflight
                    ) else {}
                ),
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
    individual_id = "i1-vnext-stage11"

    def _parent_runtime_config(self, config: Stage11Config):
        """Pass the Stage-11 UC profile through an optional later runtime.

        Standalone Stage 11 still constructs the exact Stage-9 substrate.
        Cooperative subclasses can add Stage-10 sleep without a second I0.
        """
        return config.with_budget()

    def __init__(self, *, world_config, layout, safety_config, safety_facts,
                 protected_integrity_threshold, config: Stage11Config, equipment,
                 scenario_id=None, scenario_version=None, scenario_events=(),
                 autonomous_mortal=False):
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
            config=self._parent_runtime_config(config), equipment=equipment,
            scenario_id=scenario_id, scenario_version=scenario_version,
            scenario_events=scenario_events,
            autonomous_mortal=autonomous_mortal,
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
        self._stage11_unregistered_physical_step = None
        self._stage11_place_proposals_this_cycle = ()
        self._stage11_frozen_place_targets = ()

        self.modulation = GlobalModulation(config.modulation)
        self._stage11_modulation_signals = {
            "boredom": False, "needs_satisfied": False,
        }
        self.stage8_option_evaluator = Stage11OptionEvaluator(
            config=config.stage9.stage8.evaluation,
            stage6=self.option_evaluator, q_values=self.q_active,
            exploration=self.exploration, intrinsic_weight=config.intrinsic_weight,
            site_needs_config=(self.value_needs.config if config.geographic is not None
                               and config.geographic.experienced_site_effects else None),
            instrumental_planning=(self.planning if config.instrumental_geographic_value else None),
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
        # Match a previously APPLIED local interaction against the next
        # unique physical Perception, never a simulator or a future map.
        if geo.config.experienced_site_effects:
            witnessed = geo.observe_lived_site_followup(
                world_step=capture.t_monde, position=(capture.x, capture.y),
                body_after=capture.body,
            )
            if witnessed is not None:
                self._write(
                    kind="i1_lived_site_effect_observed", cycle=1,
                    data={
                        "site": list(witnessed.position),
                        "observed_step": witnessed.last_observed_step,
                        "samples": witnessed.samples,
                        "favorable": list(witnessed.favorable),
                        "adverse": list(witnessed.adverse),
                        "scope": "first_person_contextual_association_only",
                        "causality_proven": False,
                    },
                )
        # An externally imposed WorldBody arrival can exceed the bounded
        # *information ledger*. The world is authoritative; do not roll its
        # physical position back, credit a fabricated visit or block reflexes.
        # Preserve GeographicExploration.observe_capture's atomic rejection
        # contract for direct owner callers.
        # The owned visit dictionary answers this question directly.
        # Test capacity first, avoiding a lookup until the bound is reached.
        over_capacity = (
            geo.distinct_sites >= geo.config.max_distinct_sites
            and not geo.has_recorded_site((capture.x, capture.y))
        )
        self._stage11_unregistered_physical_step = (
            capture.t_monde if over_capacity else None
        )
        if over_capacity:
            geo.freeze_targets(())
            geo.freeze_transits(())
            self._write(
                kind="stage11_geographic_physical_capture_unregistered",
                cycle=1,
                data={
                    "world_step": capture.t_monde,
                    "physical_position": [capture.x, capture.y],
                    "source": "actual_perception_capture",
                    "reason": "geographic_visit_register_capacity_exhausted",
                    "registered_distinct_sites": geo.distinct_sites,
                    "max_distinct_sites": geo.config.max_distinct_sites,
                    "new_registered_visit": False,
                    "autonomous_movement_claim": False,
                    "safety_decision": None,
                    "scientific_verdict": None,
                },
            )
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

    def _suspend_geographic_budget_targets(
        self, *, capture, cycle: int, operation: str,
    ) -> None:
        """Withdraw only the owner-local offers after a real budget refusal.

        A budget-incomplete candidate is neither an unsafe frontier nor an
        observed no-novelty result. Keep previously observed physical visits
        and all canonical safety knowledge unchanged. Registration cannot
        borrow any stale intrinsic option from an unfunded cycle (DC-07).
        """
        geo = self.exploration.geographic
        if geo is None:
            return
        geo.freeze_targets(())
        geo.freeze_transits(())
        self._stage11_geographic_proposals_this_cycle = ()
        self._write(
            kind="stage11_geographic_budget_deferred", cycle=cycle,
            data={
                "reason": "incomplete_budget",
                "failed_operation": operation,
                "source": "compute_budget",
                "world_step": capture.t_monde,
                "physical_position": [capture.x, capture.y],
                "new_targets_designated": False,
                "safety_decision": None,
                "novelty_absence_claim": False,
                "physical_visits_preserved": True,
            },
        )

    def _geographic_frontier_targets(self, capture, *, raw_targets=None):
        """Use Action Control's published *contextual* admissibility service.

        EN normative §9.4 allows early Planning filtering of definitely
        prohibited options. This is not a duplicate or a cache of safety
        facts; only the existing Action Control service can decide.
        "Indeterminate" is still a candidate. Re-query in Phase-1 Planning
        from the pre-phase frozen inputs on every eligible cycle so later
        canonical safety reclassification can take effect.
        """
        if self.exploration.geographic is None:
            return (), ()
        if raw_targets is None:
            raw_targets = self.exploration.geographic_cibles(
                capture, candidate_limit=4,
            )
        if not self._stage11_config.geographic_preflight:
            # Public compatibility ablation only. The final canonical
            # Action Control veto always remains authoritative.
            return raw_targets[
                :self.exploration.geographic.config.max_targets_per_cycle
            ], ()
        if (
            self._stage11_config.geographic_preflight_requires_frontier
            and not raw_targets
        ):
            # A bounded read of *existing* Exploration/Perception state
            # proves only absence of a currently NEW navigable frontier.
            # It does not classify any location as safe or dangerous.
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
        # Use ONLY the raw list frozen from the *pre-Phase-1* owner state.
        # Never reread Exploration after its Phase-1 producer has run.
        # Known-inadmissible directions are removed BEFORE the configured
        # target cap, preserving an east alternative when north is denied.
        targets = tuple(
            target for target in raw_targets
            if target.direction not in {
                direction for direction, _ in forbidden
            }
        )[:self.exploration.geographic.config.max_targets_per_cycle]
        return targets, tuple(sorted(forbidden))

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        # Frozen input precedes all producers of phase 1 (INV-08).
        frozen = self.causal_model.export_causal_state()
        # Read-only frontier inputs are frozen BEFORE phase-1. No Planning
        # producer may read Exploration output from the same phase (INV-08).
        # Phase-0 only freezes the previous owner state and one physical
        # capture. It never computes an Action Control safety classification.
        # Up to four candidates are read BEFORE the configured target cap;
        # Phase-1 Planning applies canonical safety and THEN this cap.
        raw_geo_targets = self.exploration.geographic_cibles(
            capture, candidate_limit=4,
        )
        frozen_geo_targets = ()
        frozen_transit_target = None
        frozen_place_targets = ()
        self._stage11_place_proposals_this_cycle = ()
        # Copy only already-owned pre-Phase-1 state; current Phase-1 surveys
        # cannot become same-phase Planning knowledge (INV-08).
        # Phase-0 must freeze route data before Phase-1 observations, but
        # copying the entire ledger is pointless unless a grounded route
        # search can actually be requested in this cycle.
        demand_skip_geo_preflight = (
            self.exploration.geographic is not None
            and self._stage11_config.geographic_preflight
            and self._stage11_config.geographic_preflight_requires_frontier
            and not raw_geo_targets
        )
        want_place_route = (
            self.exploration.geographic is not None
            and self.exploration.geographic.config.remember_entities
            and goal_for_planning is not None
            and bool(self.exploration.geographic.place_memories)
        )
        frozen_geography = (
            self.exploration.geographic.export_causal_state()
            if ((demand_skip_geo_preflight
                 and self._stage11_config.geographic_route_enabled)
                or want_place_route)
            else None
        )
        excluded_geo = ()
        deferred_geo_this_cycle = False

        def defer_geo_once(operation):
            nonlocal deferred_geo_this_cycle
            if deferred_geo_this_cycle:
                return
            deferred_geo_this_cycle = True
            self._suspend_geographic_budget_targets(
                capture=capture, cycle=cycle, operation=operation,
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
            # Only the scheduler freeze and Global Modulation run in Phase-0.
            # The Planning safety service call happens in Planning Phase-1.
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
                defer_geo_once("exploration_observe")
                return
            # Capture questions and immutable geographic markers only.
            # Actual visit/survey writes are checked via operation results.
            previous = self.exploration.phase_observation_probe()
            self.exploration.observe_causal_state(frozen)
            # DC-07: even when the present cycle is degraded, a genuine
            # physical capture may update the visited ledger, but NO new
            # target is designated or retained as offered for that cycle.
            # Phase-1 Exploration observes the real capture but does not
            # consume a same-phase Planning output. The bounded, funded
            # targets will be offered through the phase-3 service instead.
            over_capacity = (
                self._stage11_unregistered_physical_step == capture.t_monde
            )
            new_geo_visit = False
            if not over_capacity:
                new_geo_visit = self.exploration.observe_geographic_capture(
                    capture, frozen_targets=(),
                )
            geo = self.exploration.geographic
            survey_recorded = False
            if geo is not None and geo.config.remember_entities and not over_capacity:
                for memory in geo.observe_entities(
                    capture, observer_id=getattr(self, "_i1_personal_id", self.individual_id),
                ):
                    self._write(kind="i1_entity_place_observed", cycle=cycle,
                                data={"entity_id": memory.entity_id,
                                      "entity_type": memory.entity_type,
                                      "position": list(memory.position),
                                      "first_seen_step": memory.first_seen_step,
                                      "last_seen_step": memory.last_seen_step,
                                      "confidence": memory.confidence,
                                      "contradictions": memory.contradictions,
                                      "source": memory.provenance})
                # A PAID present-world Exploration observation may refute an
                # earlier semantic destination. Competition owns the intent,
                # not the place history. Never infer absence from a remote site.
                for memory in geo.place_memories:
                    if (memory.contradiction_step == capture.t_monde
                        and memory.last_seen_step < capture.t_monde
                        and memory.observer_id == getattr(
                            self, "_i1_personal_id", self.individual_id)
                        and self.competition.invalidate_contradicted_place_intention(
                            semantic_ref=f"memory_place_return:{memory.entity_id}",
                            observed_site=memory.position,
                            contradiction_step=capture.t_monde,
                        )):
                        self._write(
                            kind="i1_place_memory_intention_premise_contradicted",
                            cycle=cycle,
                            data={"semantic_ref": f"memory_place_return:{memory.entity_id}",
                                  "world_step": capture.t_monde,
                                  "motor_admission_inherited": False},
                        )
                for motion in geo.motion_updates:
                    self._write(kind="i1_entity_motion_diagnosed", cycle=cycle,
                                data={"entity_type": motion.entity_type,
                                      "trace_ref": motion.trace_ref,
                                      "diagnosis": motion.diagnosis,
                                      "identity_certainty": motion.identity_certainty,
                                      "recognition_basis": motion.recognition_basis,
                                      "observations": motion.observations,
                                      "observed_moves": motion.observed_moves,
                                      "observed_stays": motion.observed_stays,
                                      "last_position": list(motion.last_position)})

            if geo is not None and geo.config.observe_routes and not over_capacity:
                # After an accepted Phase-1 Exploration observation charge.
                # A v3 revision can only replace topology at the *current*
                # physically captured site; never grant an extra visit.
                earlier_survey = (
                    geo.observed_survey_at((capture.x, capture.y))
                    if geo.config.refresh_surveys else None
                )
                if geo.record_survey(capture):
                    survey_recorded = True
                    current_survey = geo.observed_survey_at(
                        (capture.x, capture.y)
                    )
                    if current_survey is None:
                        raise LookupError("recorded current survey is unavailable")
                    data = {
                        "source": "paid_phase1_exploration_perception",
                        "world_step": capture.t_monde,
                        "position": [capture.x, capture.y],
                        "known_neighbor_count": len(
                            current_survey.free_neighbors
                        ),
                        "hidden_safety_claim": False,
                    }
                    if geo.config.refresh_surveys:
                        data.update({
                            "survey_revision": earlier_survey is not None,
                            "prior_observed_world_step": (
                                None if earlier_survey is None
                                else earlier_survey.world_step
                            ),
                            "previous_free_neighbors": (
                                [] if earlier_survey is None
                                else [list(p) for p in earlier_survey.free_neighbors]
                            ),
                            "observed_free_neighbors": [
                                list(p) for p in current_survey.free_neighbors
                            ],
                            "physical_visit_count_unchanged": (
                                not new_geo_visit
                            ),
                            "hidden_world_oracle_used": False,
                        })
                    self._write(
                        kind="stage11_route_survey_recorded", cycle=cycle,
                        data=data,
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
            # No source-owned counters/observations can change in this
            # hook except via the paid visit and survey operations above.
            # Rebuild the full canonical event state only on a real change.
            if (new_geo_visit or survey_recorded
                    or self.exploration.phase_observation_probe() != previous):
                current = self.exploration.export_causal_state()
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
        # Capture only existing causal question IDs BEFORE Phase-1; do not
        # materialize the full geographic owner to answer a membership test.
        known = self.exploration.known_causal_question_refs()
        interested = set(self.exploration.cibles())
        previous_plan = hooks[1]["planning"]

        def plan_only_informational_targets(ctx):
            nonlocal frozen_geo_targets, frozen_transit_target, frozen_place_targets, excluded_geo
            self._stage11_geographic_proposals_this_cycle = ()
            self._stage11_frozen_place_targets = ()
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
            if self.exploration.geographic is None:
                return
            if self._cycle_degraded:
                defer_geo_once("upstream_cognitive_charge")
                return
            if st_before_cycle is None:
                return
            place_proposals = []
            place_targets = []
            if want_place_route:
                if not self._charge(module="planning", operation="geographic_route_search"):
                    defer_geo_once("geographic_route_search")
                    return
                from i1.modules.observed_frontier_routing import ObservedSurvey
                from i1.modules.spatial_memory import find_spatial_returns
                prior_surveys = tuple(ObservedSurvey(
                    position=tuple(row["position"]),
                    world_step=row["world_step"],
                    free_neighbors=tuple(tuple(p) for p in row["free_neighbors"]),
                ) for row in frozen_geography["surveys"])
                remembered = tuple(PlaceMemory(**{
                    **row, "position": tuple(row["position"]),
                    "observed_from": tuple(row["observed_from"]),
                }) for row in frozen_geography.get("entity_places", ()))
                remembered = tuple(site for site in remembered
                    if site.observer_id == getattr(
                        self, "_i1_personal_id", self.individual_id))
                frozen_place_targets = find_spatial_returns(
                    origin=(capture.x, capture.y),
                    visits=frozenset(tuple(row[:2]) for row in frozen_geography["visits"]),
                    surveys=prior_surveys, places=remembered,
                    current_free_neighbors=frozenset(
                        (cell.x, cell.y) for cell in capture.adjacent
                        if cell.passable is True and cell.creature is False
                    ), current_world_step=capture.t_monde,
                    max_candidates=self.exploration.geographic.config.max_place_candidates,
                )
                self._write(kind="i1_place_memory_recalled", cycle=cycle,
                            data={"candidates": [t.ref for t in frozen_place_targets],
                                  "sites": len(remembered),
                                  "source": "prior_frozen_geographic_owner"})
            memory_initial_state = None
            for target in frozen_place_targets:
                if not self._charge(module="planning",
                                    operation="geographic_admissibility_preflight"):
                    defer_geo_once("geographic_admissibility_preflight")
                    break
                if self.stage3.control.verifier_admissibilite(
                    capture=capture, prepared=PreparedCommand(
                        command=PrimitiveCommand("se_deplacer",
                            {"direction": target.direction}),
                        source="decision")) is Admissibility.INADMISSIBLE:
                    continue
                if not self._charge(module="planning", operation="planning_build"):
                    defer_geo_once("planning_build")
                    break
                # Same physical capture for every competing proposal.
                # A single materialization is sufficient and cannot leak
                # extra world data between alternative one-hop simulations.
                if memory_initial_state is None:
                    memory_initial_state = state_from_capture(
                        capture=capture,
                        is_night=self.world.is_night(capture.t_monde),
                    )
                proposal = propose_spatial_return(
                    target=target, initial_state=memory_initial_state,
                    simulator=self.simulator,
                    st_version=st_before_cycle.version, t_monde=capture.t_monde,
                    ttl_steps=self._stage6_config.planning.option_ttl_steps,
                    goal_ref=goal_for_planning.id,
                )
                if proposal is None or (
                    self.stage3.control.verifier_plan_connu(proposal)
                    is Admissibility.INADMISSIBLE
                ):
                    continue
                self._publish_contribution(self._planning_contribution(
                    proposal, t_monde=capture.t_monde, cycle=cycle))
                place_proposals.append(proposal)
                place_targets.append(target)
                self._write(kind="i1_place_memory_option_proposed", cycle=cycle,
                            data={"option_ref": proposal.option.id,
                                  "entity_id": target.entity_id,
                                  "entity_type": target.entity_type,
                                  "target": list(target.observed_position),
                                  "next": list(target.destination),
                                  "confidence": target.confidence,
                                  "active_goal": goal_for_planning.id})
            self._stage11_place_proposals_this_cycle = tuple(place_proposals)
            self._stage11_frozen_place_targets = tuple(place_targets)
            # The 1-UC Planning charge and the canonical read-only safety
            # lookup both execute here in Phase-1 Planning, using only raw
            # frontier inputs frozen BEFORE all Phase-1 producers (INV-08).
            # No Phase-0 cross-component work or same-phase owner reread.
            if demand_skip_geo_preflight and self._stage11_config.geographic_route_enabled:
                # Capacity is already exhausted in the pre-Phase-1 *physical*
                # visit ledger. A route across old sites cannot produce a
                # lawful new geographic visit. Do not consume search UC or
                # offer endless motivational transits toward that objective.
                # This is no claim about hidden safety or external movement.
                geo = self.exploration.geographic
                if len(frozen_geography["visits"]) >= geo.config.max_distinct_sites:
                    if cycle == 1:
                        self._write(
                            kind="stage11_geographic_route_capacity_exhausted",
                            cycle=cycle,
                            data={
                                "source": "pre_phase1_physical_visit_ledger",
                                "world_step": capture.t_monde,
                                "distinct_sites": len(frozen_geography["visits"]),
                                "max_distinct_sites": geo.config.max_distinct_sites,
                                "route_search_uc_consumed": 0,
                                "safety_decision": None,
                                "scientific_verdict": None,
                            },
                        )
                    return
                if not self._charge(
                    module="planning", operation="geographic_route_search",
                ):
                    defer_geo_once("geographic_route_search")
                    return
                geo = self.exploration.geographic
                from i1.modules.observed_frontier_routing import ObservedSurvey
                prior_surveys = tuple(ObservedSurvey(
                    position=tuple(row["position"]),
                    world_step=row["world_step"],
                    free_neighbors=tuple(tuple(p) for p in row["free_neighbors"]),
                ) for row in frozen_geography["surveys"])
                route = find_observed_frontier_route(
                    origin=(capture.x, capture.y),
                    visits=frozenset(
                        tuple(row[:2]) for row in frozen_geography["visits"]
                    ),
                    surveys=prior_surveys,
                    current_free_neighbors=frozenset(
                        (cell.x, cell.y) for cell in capture.adjacent
                        if cell.passable is True and cell.creature is False
                    ),
                    current_world_step=capture.t_monde,
                )
                self._write(
                    kind="stage11_route_search", cycle=cycle,
                    data={
                        "source": "frozen_prior_exploration_surveys",
                        "charged_operation": "geographic_route_search",
                        "world_step": capture.t_monde,
                        "route_found": route is not None,
                        "oracle_access": False,
                    },
                )
                if route is not None:
                    frozen_transit_target = GeographicTransitTarget(
                        ref=(
                            f"frontier_route:{route.observed_frontier[0]}:"
                            f"{route.observed_frontier[1]}:via:"
                            f"{route.next_position[0]}:{route.next_position[1]}:"
                            f"from:{capture.x}:{capture.y}"
                        ),
                        source_t_monde=capture.t_monde,
                        origin=(capture.x, capture.y),
                        destination=route.next_position,
                        direction=route.direction,
                        observed_frontier=route.observed_frontier,
                        visited_path=route.visited_path,
                        objective_observed_step=route.source_world_step,
                    )
                    frozen_transit_target.validate()
            if demand_skip_geo_preflight and frozen_transit_target is None:
                # Technical accounting only. No missing-budget claim and no
                # false "safe" classification, target or learning reward.
                self._write(
                    kind="stage11_geographic_preflight_skipped",
                    cycle=cycle,
                    data={
                        "reason": "no_currently_novel_accessible_frontier",
                        "source": "perception_and_physical_visit_ledger",
                        "world_step": capture.t_monde,
                        "preflight_uc_avoided_against_eager": 1,
                        "safety_decision": None,
                        "cached": False,
                    },
                )
                return
            if self._stage11_config.geographic_preflight:
                if self._stage11_config.geographic_capacity_guard_enabled:
                    # Scheduler admission bookkeeping only. This does not
                    # consult Action Control or build a speculative plan.
                    # Prior goal-directed Planning has already run first.
                    # If there is no capacity for BOTH real charges, do not
                    # waste the preflight or record a fictional UC refusal.
                    quote = self.compute_budget.quote_operations(
                        module="planning",
                        operations=(
                            "geographic_admissibility_preflight",
                            "planning_build",
                        ),
                    )
                    if not quote.affordable:
                        geo = self.exploration.geographic
                        geo.freeze_targets(())
                        geo.freeze_transits(())
                        self._stage11_geographic_proposals_this_cycle = ()
                        self._write(
                            kind="stage11_geographic_capacity_deferred",
                            cycle=cycle,
                            data={
                                "source": "scheduler_current_cycle_uc_ledger",
                                "world_step": capture.t_monde,
                                "required_uc": quote.required_uc,
                                "available_uc": quote.available_uc,
                                "charged_uc": 0,
                                "canonical_admissibility_consulted": False,
                                "safety_decision": None,
                                "no_new_option": True,
                                "planning_need_priority_preserved": True,
                            },
                        )
                        return
                if not self._charge(
                    module="planning",
                    operation="geographic_admissibility_preflight",
                ):
                    defer_geo_once("geographic_admissibility_preflight")
                    return
                frozen_geo_targets, excluded_geo = (
                    self._geographic_frontier_targets(
                        capture, raw_targets=raw_geo_targets,
                    )
                )
                if frozen_transit_target is not None:
                    transit_status = self.stage3.control.verifier_admissibilite(
                        capture=capture,
                        prepared=PreparedCommand(
                            command=PrimitiveCommand(
                                "se_deplacer",
                                {"direction": frozen_transit_target.direction},
                            ),
                            source="decision",
                        ),
                    )
                    if transit_status is Admissibility.INADMISSIBLE:
                        self._write(
                            kind="stage11_route_transit_prefiltered",
                            cycle=cycle,
                            data={
                                "source": "action_control.verifier_admissibilite",
                                "admissibility": "inadmissible",
                                "destination": list(frozen_transit_target.destination),
                                "cached": False,
                                "global_safety_claim": False,
                                "charged_operation": "geographic_admissibility_preflight",
                            },
                        )
                        frozen_transit_target = None
                self._write(
                    kind="stage11_geographic_preflight_consulted",
                    cycle=cycle,
                    data={
                        "boundary": "phase1_planning_after_accepted_charge",
                        "source": "action_control.verifier_admissibilite",
                        "charged_module": "planning",
                        "charged_operation": (
                            "geographic_admissibility_preflight"
                        ),
                        "charged_uc": 1,
                        "raw_frontier_count": len(raw_geo_targets),
                        "admissible_frontier_count": len(frozen_geo_targets),
                        "inadmissible_directions_count": len(excluded_geo),
                        "safety_policy_modified": False,
                    },
                )
            else:
                frozen_geo_targets = raw_geo_targets[
                    :self.exploration.geographic.config.max_targets_per_cycle
                ]
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
                        "preflight_uc": 1,
                    },
                )
            if not frozen_geo_targets and frozen_transit_target is None:
                return
            initial_state = state_from_capture(
                capture=capture,
                is_night=self.world.is_night(capture.t_monde),
            )
            geo_proposals = []
            for target in (
                frozen_geo_targets + (
                    (frozen_transit_target,)
                    if frozen_transit_target is not None else ()
                )
            ):
                if not self._charge(
                    module="planning", operation="planning_build",
                ):
                    defer_geo_once("planning_build")
                    break
                proposal = (
                    propose_geographic_frontier
                    if not isinstance(target, GeographicTransitTarget)
                    else propose_geographic_transit
                )(
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
                        "source": (
                            "frozen_prior_observed_frontier_route"
                            if isinstance(target, GeographicTransitTarget)
                            else "single_perceptual_capture"
                        ),
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
            # DC-11 explicitly allows Competition's phase-3 service call to
            # Exploration. Only genuinely funded Phase-1 Planning proposals
            # may become currently offered intrinsic targets. No phase-1
            # producer reads another producer's same-phase output.
            geo = self.exploration.geographic
            if geo is not None:
                funded = {
                    proposal.option.motive_ref.id
                    for proposal in self._stage11_geographic_proposals_this_cycle
                }
                geo.freeze_transits(
                    () if self._cycle_degraded
                    or frozen_transit_target is None
                    or frozen_transit_target.ref not in funded
                    else (frozen_transit_target,)
                )
                geo.freeze_targets(
                    ()
                    if self._cycle_degraded
                    else tuple(
                        target for target in frozen_geo_targets
                        if target.ref in funded
                    )
                )
            if geo is not None and geo.config.remember_entities:
                # Phase-1 knowledge is only a *candidate*. Validate it against
                # the now observed owner before spending Competition UC.
                geo.freeze_places(
                    self._stage11_frozen_place_targets
                    if not self._cycle_degraded else ()
                )
            previous_register(ctx)
            approved = set()
            if geo is not None:
                approved = {
                    f"option:place-memory:{target.ref}"
                    for target in geo.place_offered
                }
            # The Competition owner compares its existing applied trace with
            # this step's real Perception; no motor authority is inherited.
            intent_status = self.competition.observe_memory_intention(
                world_step=capture.t_monde,
                observed_position=(capture.x, capture.y),
            )
            intent = self.competition.applied_memory_intention
            if intent_status in ("expired", "contradicted", "suspended"):
                self._write(
                    kind="i1_place_memory_intention_observation", cycle=cycle,
                    data={"status": intent_status,
                          "observed_position": [capture.x, capture.y],
                          "motor_admission_inherited": False},
                )
            for old in self.competition.candidate_proposals:
                if (old.option.motive_ref.type == "place_memory"
                    and old.option.id not in approved):
                    self.competition.invalidate_candidate(old.option.id)
                    self.stage3.control.clear_option_step(old.option.id)
            funded_refs = set()
            if not self._cycle_degraded:
                for proposal in self._stage11_place_proposals_this_cycle:
                    if proposal.option.id not in approved:
                        continue
                    if not self._charge(module="competition",
                                        operation="competition_register"):
                        break
                    accepted = self._register_option_proposal(
                        proposal=proposal,
                        active_goal_id=(
                            None if self.goal_manager.active_goal is None
                            else self.goal_manager.active_goal.id),
                        t_monde=capture.t_monde, cycle=cycle)
                    if accepted:
                        funded_refs.add(proposal.option.id)
                    self._write(kind="i1_place_memory_option_registration",
                                cycle=cycle,
                                data={"option_ref": proposal.option.id,
                                      "registered": accepted})
            if (intent is not None and intent_status == "reconsider"
                and funded_refs and intent.reconsidered_step is None
                and capture.t_monde == intent.applied_step + 1
                and (capture.x, capture.y) == intent.expected_position
                and self.goal_manager.active_goal is not None
                and self.goal_manager.active_goal.id == intent.goal_ref):
                from i1.experimental.intention_continuity import (
                    IntentEvidence, bounded_continuation,
                )
                prior = IntentEvidence(
                    semantic_ref=intent.semantic_ref,
                    last_applied_step=intent.applied_step,
                    observed_destination=intent.expected_position,
                    accumulated=intent.evidence,
                )
                carried = bounded_continuation(
                    prior, intended_ref=intent.semantic_ref,
                    now_step=capture.t_monde,
                    observed_origin=(capture.x, capture.y),
                    ceiling=min(1.0, self._config.competition.base_threshold),
                    residual=self._config.competition.residual,
                    applied=True,
                )
                for target in geo.place_offered:
                    next_ref = f"option:place-memory:{target.ref}"
                    if (next_ref not in funded_refs
                        or target.observed_position != intent.observed_site
                        or f"memory_place_return:{target.entity_id}" != intent.semantic_ref):
                        continue
                    if carried is not None and self.competition.retain_bounded_intention_evidence(
                        option_ref=next_ref, t_monde=capture.t_monde,
                        observed_origin=(capture.x, capture.y), evidence=carried,
                    ):
                        self._write(
                            kind="i1_place_memory_intention_reconsidered",
                            cycle=cycle,
                            data={"source_option_ref": intent.source_option_ref,
                                  "semantic_ref": intent.semantic_ref,
                                  "next_option_ref": next_ref,
                                  "observed_arrival": [capture.x, capture.y],
                                  "carried_evidence": carried,
                                  "forced_motor_selection": False},
                        )
                        break
            # A once-perceived, authentically confirmed semantic destination
            # can be reconsidered after intervening sleep/need/opportunity
            # steps. No evidence, authority or motor admission is inherited.
            intent = self.competition.applied_memory_intention
            if (intent is not None and intent.confirmed_step is not None
                and capture.t_monde > intent.confirmed_step
                and intent.reconsidered_step != capture.t_monde
                and funded_refs and not self._cycle_degraded
                and self.goal_manager.active_goal is not None
                and self.goal_manager.active_goal.id == intent.goal_ref):
                for target in geo.place_offered:
                    ref = f"option:place-memory:{target.ref}"
                    if (ref in funded_refs
                        and target.observed_position == intent.observed_site
                        and f"memory_place_return:{target.entity_id}" == intent.semantic_ref
                        and self.competition.reconsider_confirmed_intention(
                            option_ref=ref, t_monde=capture.t_monde,
                            observed_site=target.observed_position,
                            active_goal_id=self.goal_manager.active_goal.id,
                        )):
                        self._write(
                            kind="i1_place_memory_intention_reconsidered_without_motor_credit",
                            cycle=cycle,
                            data={"option_ref": ref,
                                  "semantic_ref": intent.semantic_ref,
                                  "credited_evidence": 0.0,
                                  "motor_admission_inherited": False},
                        )
                        break
            if geo is not None and geo.config.remember_entities:
                # Only charged and *retained* Competition candidates may
                # remain published. An eligible but unfunded target cannot
                # masquerade as an active option in this cycle.
                geo.freeze_places(tuple(
                    target for target in geo.place_offered
                    if not self._cycle_degraded
                    and f"option:place-memory:{target.ref}"
                       in funded_refs
                    and self.competition.proposal_for(
                        f"option:place-memory:{target.ref}"
                    ) is not None
                ))
                now_funded = {
                    f"option:place-memory:{target.ref}"
                    for target in geo.place_offered
                }
                for old in self.competition.candidate_proposals:
                    if (old.option.motive_ref.type == "place_memory"
                        and old.option.id not in now_funded):
                        self.competition.invalidate_candidate(old.option.id)
                        self.stage3.control.clear_option_step(old.option.id)
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
        # Record a real nonmovement interaction in the existing Exploration
        # owner. Its BODY effect remains UNKNOWN until the next fresh capture.
        geo = self.exploration.geographic
        prior = self.stage3._capture
        if (geo is not None and geo.config.experienced_site_effects
            and execution.status == "applied"
            and not self._fallback_used_this_cycle
            and prior is not None
            and prior.t_monde == sent_t_monde):
            # Command has already committed/closed the physical step.
            # Record only in the M11-owned Exploration state here; a journal
            # event after Action Control dispatch would violate step custody.
            # The NEXT authentic Perception logs its observed followup.
            geo.note_applied_local_action(
                world_step=sent_t_monde, position=(prior.x, prior.y),
                body_before=prior.body, primitive=prepared.command.primitive,
                option_ref=proposal.option.id,
            )
        # A *separately* admitted, paid, physically applied spatial choice
        # can leave an informational intention in Competition's owner state.
        # No inferred arrival yet: the next Perception capture must confirm it.
        geo = self.exploration.geographic
        if (geo is not None and execution.status == "applied"
            and prepared.command.primitive == "se_deplacer"
            and not self._fallback_used_this_cycle):
            target = geo.place_for(proposal.option)
            if target is not None and self.competition.record_applied_memory_intention(
                option_ref=proposal.option.id,
                verified_control_step=self.stage3.control.current_step,
                applied_step=sent_t_monde, expected_position=target.destination,
                observed_site=target.observed_position,
                fallback_used=self._fallback_used_this_cycle,
            ):
                # Action Control already closed the physical scheduler step.
                # Competition is an M11 causal owner; retain the descriptor
                # in its committed image, but do not append a late WAL entry.
                # The next ordinary Perception can journal confirmation.
                pass
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
