"""Stage12 lived diagnostics over the one mortal Stage10/11 substrate.

Pure detection is a facet of the EXISTING Metacognition/Health owner.
There is no independent diagnosis executor, no Oracle or Bench, and no
new source of motor authority. Owner provenance stays in I0's causal journal.
"""
from __future__ import annotations

from dataclasses import replace
from math import isfinite

from i0.config import MVP_PHASE1_PRODUCER_ORDER
from i0.modules.stage12_occupancy import module_occupancy_entropy
from i0.modules.stage12_detectors import (
    LivedCognitiveObservation, Stage12DetectionPolicy,
    Stage12DetectionReport, Stage12LivedDetectors,
)

from .determinism import canonical_causal_bytes, deterministic_id
from .world import command_digest
from .stage11_sleep_runtime import Stage11SleepRuntime


class _Stage12MetacognitionCustody:
    owner_id = "metacognition_health"
    schema = "stage12-metacognition-sleep-custody-v1"

    def __init__(self, *, previous, detectors: Stage12LivedDetectors):
        if getattr(previous, "owner_id", None) != self.owner_id:
            raise ValueError("detectors require the single canonical metacognition owner")
        self.previous = previous
        self.detectors = detectors
        self.last_goal_deficit: dict[str, object] | None = None

    def observe_goal_progress(
        self, *, goal_ref: str | None, deficit: float | None, world_step: int,
    ) -> float | None:
        """Only a *measured* prior and current deficit establish progress.

        Unknown goals, unmeasured deficits, and a new goal return None:
        never fabricate a zero, and never consult hidden world truth.
        """
        if type(world_step) is not int or world_step < 1:
            raise ValueError("invalid lived progress time")
        if (goal_ref is None or deficit is None):
            self.last_goal_deficit = None
            return None
        if (type(goal_ref) is not str or not goal_ref
                or type(deficit) not in (float, int)
                or not isfinite(deficit) or deficit < 0):
            raise ValueError("invalid observed goal deficit")
        previous = self.last_goal_deficit
        progress = None
        if previous is not None:
            if world_step <= previous["world_step"]:
                raise ValueError("goal progress cannot repeat or rewind world time")
            # A skipped diagnosis (insufficient UC) is not a zero-progress
            # observation. Nor can its next result attribute several physical
            # steps' cumulative progress to a single observed cycle.
            if (previous["goal_ref"] == goal_ref
                    and world_step == previous["world_step"] + 1):
                progress = max(0.0, previous["deficit"] - float(deficit))
        self.last_goal_deficit = {
            "goal_ref": goal_ref, "deficit": float(deficit),
            "world_step": world_step,
        }
        return progress

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "prior_metacognition_and_sleep": self.previous.export_causal_state(),
            "lived_detectors": self.detectors.export_causal_state(),
            "last_visible_goal_deficit": (
                None if self.last_goal_deficit is None
                else dict(self.last_goal_deficit)
            ),
        }

    def restore_causal_state(self, state: object) -> None:
        # An active autonomous mortal cannot turn an old diagnostic snapshot
        # into a rewind of Metacognition, fatigue or health. The only current
        # Stage10 h publication is an identity rebase for unchanged forms.
        # Future mutable rebases must provide an explicitly authorized
        # scheduler-only capability and atomic validation instead.
        if (type(state) is not dict
                or canonical_causal_bytes(state)
                != canonical_causal_bytes(self.export_causal_state())):
            raise ValueError("mortal Stage12 custody forbids historic cognitive restore")


class Stage12Runtime(Stage11SleepRuntime):
    """Opt-in diagnostics: once per genuinely lived waking world step."""

    individual_id = "i0-v1.3.1-stage12-mortal"

    def __init__(
        self, *, detector_policy: Stage12DetectionPolicy,
        diagnostic_sample_cost_uc: int,
        module_occupancy_cost_uc: int = 1, **kwargs,
    ):
        detector_policy.validate()
        if type(diagnostic_sample_cost_uc) is not int or diagnostic_sample_cost_uc < 1:
            raise ValueError("Stage12 diagnostics need a positive injected P-43 UC cost")
        if type(module_occupancy_cost_uc) is not int or module_occupancy_cost_uc < 1:
            raise ValueError("Stage12 occupancy work requires a positive versioned UC cost")
        self._stage12_occupancy_cost_uc = module_occupancy_cost_uc
        self._stage12_detector_policy = detector_policy
        self._stage12_diagnostic_cost_uc = diagnostic_sample_cost_uc
        super().__init__(**kwargs)
        self._stage12_detectors = Stage12LivedDetectors(detector_policy)
        self._meta_custody = _Stage12MetacognitionCustody(
            previous=self._meta_custody, detectors=self._stage12_detectors,
        )
        ids = [owner.owner_id for owner in self.causal_owners]
        if ids.count("metacognition_health") != 1 or len(ids) != len(set(ids)):
            raise RuntimeError("Stage12 must not multiply Metacognition ownership")

    def _parent_runtime_config(self, config):
        """Version P-43 work BEFORE birth; no unpriced Stage12 operation."""
        base = super()._parent_runtime_config(config)
        stage9 = base.stage9
        stage8 = stage9.stage8
        stage7 = stage8.stage7
        stage6 = stage7.stage6
        stage4 = stage6.stage4
        old = stage4.compute_budget
        cost = self._stage12_diagnostic_cost_uc
        occupancy_cost = self._stage12_occupancy_cost_uc
        budget = replace(
            old, version=(old.version + "+" + self._stage12_detector_policy.version
                          + "+stage12-diagnostics-charged-v1"
                          + "+stage12-st-module-occupancy-v1"),
            cycle_ceiling=old.cycle_ceiling + cost + occupancy_cost,
            module_envelopes={
                **old.module_envelopes,
                # Stage11 has no Stage10 metacognition envelope yet.
                # Reserve the upcoming sleep proposal AND Stage12 sample,
                # instead of overwriting the diagnostic capacity during the
                # later Stage10 with_budget() configuration step.
                "metacognition_health": max(
                    old.module_envelopes.get("metacognition_health", 0),
                    base.sleep_option_uc,
                ) + cost + occupancy_cost,
            },
            operation_costs={
                **old.operation_costs,
                "stage12_diagnostic_sample": cost,
                "stage12_occupancy_entropy": occupancy_cost,
            },
        )
        upgraded = replace(stage9, stage8=replace(stage8, stage7=replace(
            stage7, stage6=replace(
                stage6, stage4=replace(stage4, compute_budget=budget),
            ),
        )))
        return replace(base, stage9=upgraded)

    @property
    def detection_report(self) -> Stage12DetectionReport:
        """Detached, warning-only report; never an implicit Action Control veto."""
        return self._stage12_detectors.detecteurs()


    def _publish_module_occupancy(self, *, cycle: int, world_step: int) -> None:
        """Price and publish current S_t producer occupancy, operator-only.

        Stage4 Gatekeeper owns retained contributions; this projection
        merely reads its detached export after phase2 has published S_t.
        No Oracle, technical journal read, reward or motor veto is involved.
        """
        st = self.s_t.current
        if st is None or st.t_monde != world_step or st.cycle != cycle:
            raise RuntimeError("Stage12 cannot sample an unpublished current S_t")
        charge = self.compute_budget.charge(
            module="metacognition_health", operation="stage12_occupancy_entropy",
        )
        self._write(kind="compute_charge", cycle=cycle, data={
            "module": "metacognition_health",
            "operation": "stage12_occupancy_entropy",
            "count": 1,
            "requested_uc": charge.requested_uc,
            "accepted": charge.accepted,
            "reason": charge.reason,
        })
        if not charge.accepted:
            self._cycle_degraded = True
            self._write(
                kind="stage12_st_occupancy_deferred", cycle=cycle,
                data={
                    "st_version": st.version, "world_step": world_step,
                    "reason": charge.reason, "diagnostic_incomplete": True,
                    "policy_version": "stage12-st-module-occupancy-v1",
                },
            )
            return

        # Retained provenance is a bounded owned-state projection. Never
        # use world truth or previously rejected/queued bus messages.
        retained = self.gatekeeper.export_causal_state()["retained"]
        emitters = {entry["id"]: entry["emitter_module"] for entry in retained}
        if len(emitters) != len(retained):
            raise RuntimeError("duplicate retained Gatekeeper contribution")
        refs = tuple(element.contribution_ref for element in st.competitive)
        if len(refs) != len(set(refs)):
            raise RuntimeError("duplicate retained S_t contribution")
        counts = {producer: 0 for producer in MVP_PHASE1_PRODUCER_ORDER}
        for ref in refs:
            emitter = emitters.get(ref)
            if emitter not in counts:
                raise RuntimeError("S_t contribution lacks a known retained emitter")
            counts[emitter] += 1

        ratio = self._stage12_detector_policy.entropy_warning_fraction
        result = module_occupancy_entropy(
            counts, warning_fraction=ratio,
            module_universe_size=len(MVP_PHASE1_PRODUCER_ORDER),
        )
        if result.occupied_slots != len(refs):
            raise RuntimeError("S_t occupancy projection lost a retained slot")
        self._write(
            kind="stage12_st_module_occupancy_published", cycle=cycle,
            data={
                "schema": "stage12-st-module-occupancy-v1",
                "st_version": st.version, "world_step": world_step,
                "module_universe": list(MVP_PHASE1_PRODUCER_ORDER),
                "module_counts": {
                    producer: counts[producer]
                    for producer in MVP_PHASE1_PRODUCER_ORDER if counts[producer]
                },
                "module_universe_size": len(MVP_PHASE1_PRODUCER_ORDER),
                "warning_fraction": ratio,
                "normalized_entropy": result.normalized_entropy,
                "low_entropy": result.low_entropy,
                "status": result.status,
                "occupied_slots": result.occupied_slots,
                "distinct_modules": result.distinct_modules,
                "charged_uc": charge.requested_uc,
                "operator_only_diagnostic": True,
            },
        )

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        hooks = super()._phase_hooks(
            cycle=cycle, capture=capture,
            goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )
        previous = hooks[5]["metacognition_health"]

        def publish_lived_diagnostic(ctx):
            # Occupancy is a separate *per cognitive cycle* S_t measurement.
            # Its UC charge is reflected in the same fatigue closure below.
            self._publish_module_occupancy(cycle=cycle, world_step=capture.t_monde)
            # One actual metacognitive service charge per lived world step.
            # The sample is optional under DC-07, and must be absent, never
            # silently inferred, if its scheduler-owned UC debit is refused.
            if self.detection_report.world_step == capture.t_monde:
                previous(ctx)
                return
            charge = self.compute_budget.charge(
                module="metacognition_health",
                operation="stage12_diagnostic_sample",
            )
            self._write(kind="compute_charge", cycle=cycle, data={
                "module": "metacognition_health",
                "operation": "stage12_diagnostic_sample",
                "requested_uc": charge.requested_uc,
                "accepted": charge.accepted,
                "reason": charge.reason,
            })
            if not charge.accepted:
                # Reflect an actually refused optional module in the *next*
                # cycle's synthetic budget state; do not retrospectively
                # rewrite the already published S_t or invent diagnostic data.
                self._cycle_degraded = True
                self._write(
                    kind="stage12_lived_diagnostics_deferred",
                    cycle=cycle,
                    data={"world_step": capture.t_monde,
                          "reason": charge.reason,
                          "diagnostic_incomplete": True},
                )
                previous(ctx)
                return
            goal = self.goal_manager.active_goal
            goal_ref = None if goal is None else goal.id
            deficit = None
            needs = self._step_need_state
            if (goal is not None and needs is not None
                    and goal.target in needs.deficits):
                deficit = needs.deficits[goal.target]
            progress = self._meta_custody.observe_goal_progress(
                goal_ref=goal_ref, deficit=deficit,
                world_step=capture.t_monde,
            )
            admitted = self._admitted_decision
            option_ref = (
                None if admitted is None
                else admitted[0].option.id
            )
            context = deterministic_id(
                "stage12-lived-perceptual-occupancy-v1",
                {
                    "x": capture.x,
                    "y": capture.y,
                    "water_source_visible": bool(capture.current_water_source),
                    "adjacent_visible": len(capture.adjacent),
                    "active_goal_ref": goal_ref,
                },
            )
            report = self._stage12_detectors.observe(
                LivedCognitiveObservation(
                    world_step=capture.t_monde, cycle=cycle,
                    context_signature=context,
                    active_goal_ref=goal_ref, option_ref=option_ref,
                    progress_delta=progress,
                ),
            )
            self._write(
                kind="stage12_lived_diagnostics_published",
                cycle=cycle,
                data={
                    "world_step": report.world_step,
                    "context_projection_version": "stage12-lived-perceptual-occupancy-v1",
                    "stagnation": report.stagnation,
                    "reasoning_loop": report.reasoning_loop,
                    "low_context_entropy": report.low_context_entropy,
                    "attribution_bias": report.attribution_bias,
                    "evidence_samples": report.evidence_samples,
                    "progress_observed": progress is not None,
                    "operator_only_diagnostic": True,
                    "charged_diagnostic_uc": charge.requested_uc,
                    "diagnostic_policy_version": self._stage12_detector_policy.version,
                },
            )
            # Close fatigue AFTER the accepted cost, so real diagnostic work
            # contributes to the exact same waking cycle's F_cog accounting.
            previous(ctx)

        hooks[5]["metacognition_health"] = publish_lived_diagnostic
        return hooks

    def _dispatch_decision(
        self, *, proposal, prepared, admission, cycle, sent_t_monde,
    ):
        """Witness the admitted motive BEFORE physics, for external audit.

        It does not affect Competition, goals, Action Control or rewards.
        The independent alignment audit counts this witness only if a real
        command with the same digest later executes and the step is closed.
        A fatal physical outcome cannot create postmortem observations.
        """
        if admission.ok is True:
            active = self.goal_manager.active_goal
            self._write(
                kind="stage12_action_motive_attested", cycle=cycle,
                data={
                    "schema": "stage12-action-motive-v1",
                    "option_ref": proposal.option.id,
                    "command_hash": command_digest(prepared.command),
                    "goal_ref": proposal.option.goal_ref,
                    "active_goal_ref": None if active is None else active.id,
                    "motive_type": proposal.option.motive_ref.type,
                    "external_audit_only": True,
                },
            )
        return super()._dispatch_decision(
            proposal=proposal, prepared=prepared, admission=admission,
            cycle=cycle, sent_t_monde=sent_t_monde,
        )
