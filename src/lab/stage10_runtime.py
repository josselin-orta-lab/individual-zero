"""Stage-10 real sleeping runtime above the stable Stage-9 cognitive substrate.

The dormant path opens the Scheduler, obtains *one* physical capture, exposes
only reduced perception, runs the dedicated DC-13 wake rule, then dispatches
through Action Control. A non-reflex wake passes the very same captured physical
state to the ordinary Stage-9 cognitive loop; it never opens a second step.
This intentionally does not claim that the six semantic passes are complete.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from math import isfinite
from typing import Mapping

from i0.interfaces import PrimitiveCommand
from i0.modules.action_control import PreparedCommand
from i0.modules.competition import OptionEvidenceInput
from i0.modules.consolidation_budget import ConsolidationBudgetConfig, ConsolidationWorkBudget
from i0.modules.consolidation_transaction import ConsolidationSlot
from i0.modules.sleep_competition import create_sleep_proposal, assemble_sleep_evidence
from i0.modules.sleep_health import SleepHealth
from i0.modules.sleep_pressure import SleepPressureConfig, WakeSignals
from i0.modules.sleep_reduced import reduced_sleep_capture
from i0.modules.sleep_session import SleepSession
from i0.modules.simulator import state_from_capture

from .consolidation_publication import SlowHistory
from .stage4_runtime import Stage4StepResult
from .stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY
from .stage9_runtime import Stage9Config, Stage9Runtime


@dataclass(frozen=True, slots=True)
class Stage10Config:
    version: str
    stage9: Stage9Config
    sleep: SleepPressureConfig
    sleep_work: ConsolidationBudgetConfig
    intrinsic_weight: float
    memory_reference_capacity: int
    sleep_option_uc: int
    critical_body_thresholds: Mapping[str, float]
    adjacent_threat_intensity: float
    adjacent_threat_risk: float
    critical_body_intensity: float
    critical_body_risk: float
    p_cons_min: float

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage-10 runtime requires version")
        self.stage9.validate()
        self.sleep.validate()
        self.sleep_work.validate()
        if (type(self.memory_reference_capacity) is not int
                or self.memory_reference_capacity < 1
                or type(self.sleep_option_uc) is not int or self.sleep_option_uc < 1):
            raise ValueError("normalized Memory denominator and UC must be positive")
        for value in (
            self.intrinsic_weight, self.adjacent_threat_intensity,
            self.adjacent_threat_risk, self.critical_body_intensity,
            self.critical_body_risk, self.p_cons_min,
        ):
            if type(value) not in (int, float) or not isfinite(value) or value < 0:
                raise ValueError("non-finite or negative Stage-10 parameter")
        if self.p_cons_min > 1:
            raise ValueError("consolidation trigger must be normalized")
        if any(value > 1 for value in (
            self.adjacent_threat_intensity, self.adjacent_threat_risk,
            self.critical_body_intensity, self.critical_body_risk,
        )):
            raise ValueError("wake coefficients must be bounded")
        if (not self.critical_body_thresholds
                or not set(self.critical_body_thresholds).issubset(
                    {"energy", "food", "water", "integrity"})):
            raise ValueError("critical body channels must be versioned")
        for threshold in self.critical_body_thresholds.values():
            if (type(threshold) not in (int, float)
                    or not isfinite(threshold) or not 0 <= threshold <= 100):
                raise ValueError("critical body threshold outside [0,100]")

    def with_budget(self) -> Stage9Config:
        """Explicitly price additional sleep proposal work in ordinary P-43.

        The extra ceiling is a visible versioned allowance, not a free UC
        bypass. Legacy Stages 4-9 are never modified by this configuration.
        """
        base = self.stage9.stage8.stage7.stage6.stage4
        cfg = base.compute_budget
        new_budget = replace(
            cfg, version=cfg.version + "+" + self.version,
            cycle_ceiling=cfg.cycle_ceiling + self.sleep_option_uc + 1,
            module_envelopes={
                **cfg.module_envelopes,
                "metacognition_health": max(
                    cfg.module_envelopes.get("metacognition_health", 0),
                    self.sleep_option_uc,
                ),
                "competition": cfg.module_envelopes["competition"] + 1,
            },
            operation_costs={
                **cfg.operation_costs,
                "sleep_option_prepare": self.sleep_option_uc,
            },
        )
        return replace(
            self.stage9,
            stage8=replace(self.stage9.stage8,stage7=replace(
                self.stage9.stage8.stage7,
                stage6=replace(self.stage9.stage8.stage7.stage6,
                    stage4=replace(base,compute_budget=new_budget)),
            )),
        )


class _MetacognitionAndSleepCustody:
    """One snapshot authority for the existing Meta owner and its new facet."""

    owner_id = "metacognition_health"

    def __init__(self, meta, health):
        self.meta, self.health = meta, health

    def export_causal_state(self):
        return {
            "stage10_custody_schema": "v1",
            "metacognition": self.meta.export_causal_state(),
            "sleep_health": self.health.export_causal_state(),
        }

    def restore_causal_state(self, state):
        if (type(state) is not dict
                or set(state) != {
                    "stage10_custody_schema", "metacognition", "sleep_health",
                } or state["stage10_custody_schema"] != "v1"):
            raise ValueError("incompatible combined metacognition custody")
        old_meta = self.meta.export_causal_state()
        old_health = self.health.export_causal_state()
        try:
            self.meta.restore_causal_state(deepcopy(state["metacognition"]))
            self.health.restore_causal_state(deepcopy(state["sleep_health"]))
        except Exception:
            self.meta.restore_causal_state(old_meta)
            self.health.restore_causal_state(old_health)
            raise


class Stage10Runtime(Stage9Runtime):
    """One causal Stage-10 individual, not a second physical-world executive."""

    individual_id = "i0-vnext-stage10"

    def __init__(self, *, world_config, layout, safety_config, safety_facts,
                 protected_integrity_threshold, config: Stage10Config, equipment,
                 scenario_id=None, scenario_version=None, scenario_events=(),
                 autonomous_mortal=False):
        config.validate()
        self._stage10_config = config
        super().__init__(
            world_config=world_config, layout=layout,
            safety_config=safety_config, safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            config=config.with_budget(), equipment=equipment,
            scenario_id=scenario_id, scenario_version=scenario_version,
            scenario_events=scenario_events,
            autonomous_mortal=autonomous_mortal,
        )
        self.sleep_health = SleepHealth(config.sleep)
        self.sleep_session = SleepSession(wake_policy_version=config.sleep.version)
        if autonomous_mortal:
            self.stage3.substrate.register_nonphysical_step_clock(self.sleep_session)
        self._meta_custody = _MetacognitionAndSleepCustody(
            self.metacognition, self.sleep_health,
        )
        self.slow_history = SlowHistory(
            birth_version="h:birth:"+config.version,
            birth_state={
                "forms": {}, "consolidated_episode_refs": [],
                "hypotheses": [], "procedural": [], "indices": {},
            },
        )
        self.consolidation = ConsolidationSlot()
        self.consolidation_work = ConsolidationWorkBudget(config.sleep_work)
        self._preopened_waking_capture = None
        self._last_applied_decision = None
        self._last_sleep_proposal = None

    @property
    def causal_owners(self):
        original = super().causal_owners
        owners = [
            self._meta_custody if owner.owner_id == "metacognition_health"
            else owner for owner in original
        ]
        owners.extend((
            self.sleep_session, self.slow_history,
            self.consolidation, self.consolidation_work,
        ))
        ids = [owner.owner_id for owner in owners]
        if len(ids) != len(set(ids)):
            raise ValueError("Stage-10 owner duplication")
        return tuple(owners)

    def _open_step_capture(self):
        if self._preopened_waking_capture is not None:
            capture = self._preopened_waking_capture
            self._preopened_waking_capture = None
            if self.scheduler.active_attempt is None:
                raise RuntimeError("waking capture lost its already-open world step")
            if capture.t_monde != self.scheduler.t_monde:
                raise RuntimeError("waking capture changed its physical step")
            return capture
        capture = super()._open_step_capture()
        if self.sleep_session.open_world_step(capture.t_monde) != "awake":
            raise RuntimeError("ordinary cognition cannot run during sleep")
        return capture

    def _on_open_step_capture(self, capture) -> None:
        super()._on_open_step_capture(capture)
        committed = set(self.slow_history.read_committed()["consolidated_episode_refs"])
        pending = sum(episode.id not in committed for episode in self.memory.episodes)
        relevant = min(1.0, len(self.memory.episodes)
                       / self._stage10_config.memory_reference_capacity)
        value = self.sleep_health.begin_waking_step(
            world_step=capture.t_monde, unconsolidated_episodes=pending,
            memory_occupancy=relevant,
            is_night=self.world.is_night(capture.t_monde),
        )
        self._write(kind="stage10_sleep_pressure_frozen",cycle=1,data={
            "world_step":capture.t_monde,
            "sleep_pressure":value.sleep_pressure,
            "consolidation_pressure":value.consolidation_pressure,
            "fatigue":value.fatigue,"source":"previous_published_memory_and_actual_uc",
        })

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        hooks = super()._phase_hooks(
            cycle=cycle, capture=capture,
            goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )
        original_registration = hooks[3]["competition"]
        original_closure = hooks[5]["metacognition_health"]

        def register_sleep(ctx):
            original_registration(ctx)
            st = self.s_t.current
            if st is None or self._cycle_degraded:
                return
            charge = self.compute_budget.charge(
                module="metacognition_health", operation="sleep_option_prepare",
            )
            self._write(kind="compute_charge",cycle=cycle,data={
                "module":"metacognition_health","operation":"sleep_option_prepare",
                "count":1,"requested_uc":charge.requested_uc,
                "accepted":charge.accepted,"reason":charge.reason,
            })
            if not charge.accepted:
                self._cycle_degraded = True
                return
            proposal = create_sleep_proposal(
                health=self.sleep_health,t_monde=capture.t_monde,
                st_version=st.version,charged_preparation=charge,
            )
            if not self._charge(
                module="competition",operation="competition_register",
            ):
                return
            registered = self._register_option_proposal(
                proposal=proposal,
                active_goal_id=(
                    None if self.goal_manager.active_goal is None
                    else self.goal_manager.active_goal.id
                ),
                t_monde=capture.t_monde,cycle=cycle,
            )
            self._last_sleep_proposal = proposal if registered else None
            self._write(kind="stage10_sleep_option_registered",cycle=cycle,data={
                "option_ref":proposal.option.id,"accepted":registered,
                "sleep_pressure":self.sleep_health.frozen.sleep_pressure,
                "planning_inserted":False,
            })

        def close_fatigue(ctx):
            original_closure(ctx)
            fatigue = self.sleep_health.close_waking_cycle(
                world_step=capture.t_monde,cycle=cycle,
                consumed_uc=self.compute_budget.consumed_cycle_uc,
                cycle_ceiling=self._config.compute_budget.cycle_ceiling,
                c_max=self._config.competition.c_max,
            )
            self._write(kind="stage10_fatigue_waking_cycle",cycle=cycle,data={
                "fatigue":fatigue,"consumed_uc":self.compute_budget.consumed_cycle_uc,
            })

        hooks[3]["competition"] = register_sleep
        hooks[5]["metacognition_health"] = close_fatigue
        return hooks

    def _evaluate_competition_cycle(self, *, capture, cycle):
        initial = state_from_capture(
            capture=capture,is_night=self.world.is_night(capture.t_monde),
        )
        state = self._evaluation_state(capture)
        evidence = {}
        for proposal in self.competition.candidate_proposals:
            supplied = self.stage8_option_evaluator.evaluate(
                proposal=proposal,evaluation_state=state,
                initial_state=initial,cycle=cycle,t_monde=capture.t_monde,
            )
            if proposal.option.motive_ref.type == "sleep_pressure":
                supplied = assemble_sleep_evidence(
                    proposal=proposal,base=supplied,health=self.sleep_health,
                    t_monde=capture.t_monde,cycle=cycle,
                    intrinsic_weight=self._stage10_config.intrinsic_weight,
                )
            evidence[proposal.option.id] = supplied
            ev = supplied.evaluation
            self._write(kind="stage8_option_evaluation",cycle=cycle,data={
                "option_ref":proposal.option.id,
                "learning_signature":proposal.option.learning_signature,
                "status":ev.status,
                "learned_value_status":ev.learned_value_status,
                "learned_value":ev.learned_value,
                "simulated_value_status":ev.simulated_value_status,
                "simulated_value":ev.simulated_value,
                "intrinsic_status":ev.intrinsic_status,
                "intrinsic_value":ev.intrinsic_value,
                "evidence":supplied.evidence,
                "equipment_version":self.equipment.version,
                "q_version":self._stage8_config.td.version,
            })
        return self.competition.evaluate(
            cycle=cycle,t_monde=capture.t_monde,evidence_inputs=evidence,
        )

    def _dispatch_decision(self, *, proposal, prepared, admission, cycle, sent_t_monde):
        execution = super()._dispatch_decision(
            proposal=proposal,prepared=prepared,admission=admission,
            cycle=cycle,sent_t_monde=sent_t_monde,
        )
        if execution.status == "applied":
            self._last_applied_decision = (admission,prepared,proposal)
        return execution

    def _wake_score(self, reduced):
        cfg = self._stage10_config
        observed = []
        if reduced.adjacent_creature:
            observed.append(cfg.adjacent_threat_intensity * cfg.adjacent_threat_risk)
        if reduced.critical_body_channels:
            observed.append(cfg.critical_body_intensity * cfg.critical_body_risk)
        return max(observed) if observed else None

    def _sleep_step(self) -> Stage4StepResult:
        # Sleep and reflex are nondecision steps of the existing DC-15 TD
        # segment: their physical rewards must enter G once, at completion.
        body_before = dict(self.world.body.as_dict())
        self.stage3.substrate.open_step()
        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("Stage-10 physical step was not opened")
        t = attempt.t_monde
        local = self.world.capture_local(t_monde=t)
        telemetry = self.world.telemetry()
        observation = reduced_sleep_capture(
            local_state=local.as_dict(),telemetry=telemetry,
            source_capture_ref=f"lived-reduced:{attempt.attempt_ref}",
            world_step=t,
            critical_thresholds=self._stage10_config.critical_body_thresholds,
        )
        before = self.sleep_session.mode
        if self.sleep_session.open_world_step(t) != "sleeping":
            raise ValueError("unadmitted sleep entry")
        if before == "awake":
            self.consolidation_work.begin_period(
                period_ref=f"sleep-period:{t}:{attempt.attempt_ref}",
                entry_step=t,
            )
            self._write(kind="stage10_sleep_entered",data={
                "world_step":t,"from_applied_dormir":True,
            })
        self.consolidation_work.begin_step(world_step=t)
        self._write(kind="stage10_reduced_capture",data={
            "source_ref":observation.source_capture_ref,
            "adjacent_creature":observation.adjacent_creature,
            "critical_body_channels":list(observation.critical_body_channels),
            "full_cognitive_perception":False,
        })
        reflex = self.stage3.control.reflex(observation.capture)
        reflex_admission = None
        if reflex is not None:
            reflex_admission = self.stage3.control.admit(
                capture=observation.capture,prepared=reflex.prepared,
            )
            self.stage3.record_admission(
                prepared=reflex.prepared,admission=reflex_admission,
            )
        admitted_reflex = bool(reflex_admission is not None and reflex_admission.ok)
        due_intention = any(
            deadline <= t for deadline in self.memory.wake_deadline_index.values()
        )
        old = self.consolidation.current
        active = bool(old is not None and old.status == "active")
        frozen = self.sleep_health.frozen
        if frozen is None:
            raise RuntimeError("sleep session missing its last waking pressure")
        outcome = self.sleep_session.evaluate_sleep_step(
            signals=WakeSignals(
                admitted_reflex=admitted_reflex,
                reduced_perception_alert=self._wake_score(observation),
                authorized_dated_intention_due=due_intention,
                consecutive_sleep_steps=self.sleep_session.sleep_duration,
                consolidation_active=active,
            ),
            frozen_sleep_pressure=frozen.sleep_pressure,
            wake_rule=self.sleep_health.rules,
        )
        if outcome.woke:
            if active:
                # The running work unit must cancel its current private pass.
                # Integration of the pass runner is required before activating
                # any live consolidation. Never publish partial work.
                old.interrupt()
            self._write(kind="stage10_sleep_woke",data={
                "world_step":t,"reason":outcome.reason,
                "consolidation_interrupted":active,
            })
            self.consolidation_work.end_period()
            if admitted_reflex:
                execution = self.stage3.control.dispatch_prechecked(
                    admission=reflex_admission,
                    sender=lambda command:self.stage3.substrate.send_admitted_command(
                        command,source="action_control",
                        checkpoint_owners=self.causal_owners,
                        individual_id=self.individual_id,
                        autobiographical_policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
                    ),
                )
                if execution.status == "applied":
                    self.q_active.append_experienced_reward(
                        self.value_needs.reward_between(
                            body_before, dict(self.world.body.as_dict()),
                        ),
                    )
                    self.sleep_session.finish_sleep_step(
                        decision=outcome,admission=reflex_admission,
                        prepared=reflex.prepared,command_sent=True,
                        world_advanced=True,consolidation_interrupted=active,
                    )
                return Stage4StepResult(
                    source="reflex",execution_status=execution.status,
                    command_primitive=reflex.prepared.command.primitive,
                    option_ref=None,
                    st_version=None if self.s_t.current is None else self.s_t.current.version,
                    cycles_used=0,reflex_triggered=True,fallback_used=False,
                )
            # Waking recaptures no world state: the original local, telemetry
            # are reused to make the first ordinary cognitive perception.
            new_capture = self.stage3.perception.capture(
                local_state=local.as_dict(),telemetry=telemetry,
            )
            self.stage3._capture = new_capture
            self.stage3._capture_attempt_ref = attempt.attempt_ref
            self.stage3._captures_this_step = 1
            self.stage3._write(kind="perceptual_capture",data={
                "capture_t_monde":t,
                "position":{"x":new_capture.x,"y":new_capture.y},
                "adjacent_creature_count":len(new_capture.adjacent_creatures),
            })
            self._preopened_waking_capture = new_capture
            self._last_applied_decision = None
            result = super().run_step()
            if result.execution_status == "applied":
                if self._last_applied_decision is None:
                    raise RuntimeError("waking command has no Action Control evidence")
                admission,prepared,_ = self._last_applied_decision
                self.sleep_session.finish_sleep_step(
                    decision=outcome,admission=admission,prepared=prepared,
                    command_sent=True,world_advanced=True,
                    consolidation_interrupted=active,
                )
            return result
        # No cognitive cycle and no re-reading WorldBody while asleep.
        prepared = PreparedCommand(
            command=PrimitiveCommand("dormir"),source="sleep",
        )
        admission = self.stage3.control.admit(
            capture=observation.capture,prepared=prepared,
        )
        self.stage3.record_admission(prepared=prepared,admission=admission)
        if not admission.ok:
            raise RuntimeError("sleep command was refused; no fabricated world advance")
        execution = self.stage3.control.dispatch_prechecked(
            admission=admission,
            sender=lambda command:self.stage3.substrate.send_admitted_command(
                command,source="action_control",
                checkpoint_owners=self.causal_owners,
                individual_id=self.individual_id,
                autobiographical_policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
            ),
        )
        if execution.status == "applied":
            self.q_active.append_experienced_reward(
                self.value_needs.reward_between(
                    body_before, dict(self.world.body.as_dict()),
                ),
            )
            self.sleep_health.recover_sleep_step(world_step=t)
            self.sleep_session.finish_sleep_step(
                decision=outcome,admission=admission,prepared=prepared,
                command_sent=True,world_advanced=True,
                consolidation_interrupted=False,
            )
        return Stage4StepResult(
            source="sleep",execution_status=execution.status,
            command_primitive="dormir",option_ref=None,
            st_version=None if self.s_t.current is None else self.s_t.current.version,
            cycles_used=0,reflex_triggered=reflex is not None,fallback_used=False,
        )

    def run_step(self):
        if (self.sleep_session.mode == "sleeping"
                or self.sleep_session.export_causal_state()["admitted_sleep_step"] is not None):
            return self._sleep_step()
        self._last_applied_decision = None
        result = super().run_step()
        if (result.execution_status == "applied"
                and result.source == "decision"
                and result.command_primitive == "dormir"):
            if self._last_applied_decision is None:
                raise RuntimeError("applied sleep has no matching admission")
            admission,prepared,proposal = self._last_applied_decision
            self.sleep_session.record_applied_sleep_decision(
                world_step=self.scheduler.t_monde,
                admission=admission,prepared=prepared,
                motive_type=proposal.option.motive_ref.type,
                execution_status="applied",
            )
            # The next physical step, not this one, enters sleeping mode.
        return result
