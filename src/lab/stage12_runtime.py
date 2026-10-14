"""Stage12 lived diagnostics over the one mortal Stage10/11 substrate.

Pure detection is a facet of the EXISTING Metacognition/Health owner.
There is no independent diagnosis executor, no Oracle or Bench, and no
new source of motor authority. Owner provenance stays in I0's causal journal.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from math import isfinite

from i0.config import MVP_PHASE1_PRODUCER_ORDER
from i0.modules.stage12_occupancy import module_occupancy_entropy
from i0.modules.stage12_goal_agency import GOAL_AGENCY_VERSION
from i0.modules.stage12_dual_scope import DUAL_SCOPE_VERSION
from i0.modules.stage12_attribution_pairs import (
    PAIR_VERSION, LivedAttributionPair, Stage12AttributionPairs,
)
from i0.modules.stage12_goal_progress import (
    ALLOWED_MEASURES, CONTRACT_VERSION, LivedGoalProgressIntent,
    LivedSpatialGoalIntent, SPATIAL_CONTRACT_VERSION, SPATIAL_MEASURE,
    Stage12GoalProgressLedger,
)
from i0.modules.stage12_alerts import Stage12AlertLedger, Stage12AlertPolicy
from i0.modules.stage12_detectors import (
    LivedCognitiveObservation, Stage12DetectionPolicy,
    Stage12DetectionReport, Stage12LivedDetectors,
)

from .determinism import canonical_causal_bytes, deterministic_id
from .world import command_digest
from .stage11_sleep_runtime import Stage11SleepRuntime


class _Stage12MetacognitionCustody:
    owner_id = "metacognition_health"
    schema = "stage12-metacognition-sleep-alert-goal-custody-v3"

    def __init__(
        self, *, previous, detectors: Stage12LivedDetectors,
        alerts: Stage12AlertLedger, attribution_enabled: bool = False,
    ):
        if getattr(previous, "owner_id", None) != self.owner_id:
            raise ValueError("detectors require the single canonical metacognition owner")
        self.previous = previous
        self.detectors = detectors
        self.alerts = alerts
        self.goal_progress = Stage12GoalProgressLedger()
        self.attribution_pairs = (Stage12AttributionPairs() if attribution_enabled else None)
        if attribution_enabled:
            self.schema = "stage12-metacognition-sleep-alert-goal-attribution-custody-v4"
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
            "operator_alert_ledger": self.alerts.export_causal_state(),
            "lived_goal_progress": self.goal_progress.export_causal_state(),
            **({"lived_attribution_pairs": self.attribution_pairs.export_causal_state()}
               if self.attribution_pairs is not None else {}),
            "last_visible_goal_deficit": (
                None if self.last_goal_deficit is None
                else dict(self.last_goal_deficit)
            ),
        }

    def install_m11_cold_state(self, state: object, *, capability: object) -> None:
        """Verify SQLite-owned current generation on a never-run private owner.

        Public restore_causal_state remains equality-only, including on every
        active Stage12 runtime. M11 must authenticate the entire current
        SQLite image BEFORE granting the narrow cold-import capability.
        """
        from .m11_transactional_mortal import _M11_COLD_OWNER_TOKEN
        if capability is not _M11_COLD_OWNER_TOKEN:
            raise ValueError("untrusted Stage12 cold state installer")
        if getattr(self, "_m11_cold_installed", False):
            raise ValueError("Stage12 current generation already installed")
        initial = self.export_causal_state()
        if (type(state) is not dict or set(state) != set(initial)
                or state.get("schema") != self.schema
                or state["last_visible_goal_deficit"] is not None
                and (type(state["last_visible_goal_deficit"]) is not dict
                     or set(state["last_visible_goal_deficit"]) !=
                     {"goal_ref", "deficit", "world_step"})):
            raise ValueError("invalid Stage12 cold owner image")
        deficit = state["last_visible_goal_deficit"]
        if deficit is not None:
            if (type(deficit["goal_ref"]) is not str or not deficit["goal_ref"]
                    or type(deficit["world_step"]) is not int
                    or deficit["world_step"] < 1
                    or type(deficit["deficit"]) not in (int, float)
                    or not isfinite(deficit["deficit"]) or deficit["deficit"] < 0):
                raise ValueError("invalid last observed current goal deficit")
        # Validate everything on a detached owner first, then import into the
        # same actual subowner instances held by other Stage12 runtime facets.
        staged = deepcopy(self)
        staged.previous.restore_causal_state(deepcopy(
            state["prior_metacognition_and_sleep"]))
        staged.detectors.restore_causal_state(deepcopy(state["lived_detectors"]))
        staged.alerts.restore_causal_state(deepcopy(state["operator_alert_ledger"]))
        staged.goal_progress.restore_causal_state(deepcopy(state["lived_goal_progress"]))
        if staged.attribution_pairs is not None:
            staged.attribution_pairs.restore_causal_state(deepcopy(state["lived_attribution_pairs"]))
        staged.last_goal_deficit = deepcopy(deficit)
        if canonical_causal_bytes(staged.export_causal_state()) != canonical_causal_bytes(state):
            raise ValueError("Stage12 cold owner image did not validate exactly")
        self.previous.restore_causal_state(deepcopy(
            state["prior_metacognition_and_sleep"]))
        self.detectors.restore_causal_state(deepcopy(state["lived_detectors"]))
        self.alerts.restore_causal_state(deepcopy(state["operator_alert_ledger"]))
        self.goal_progress.restore_causal_state(deepcopy(state["lived_goal_progress"]))
        if self.attribution_pairs is not None:
            self.attribution_pairs.restore_causal_state(deepcopy(state["lived_attribution_pairs"]))
        self.last_goal_deficit = deepcopy(deficit)
        self._m11_cold_installed = True

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
        module_occupancy_cost_uc: int = 1,
        operator_alert_persistence_steps: int = 3,
        subjective_goal_agency: bool = False,
        dual_scope_agency: bool = False,
        dual_scope_cost_uc: int = 1,
        goal_agency_cost_uc: int = 1,
        spatial_goal_progress: bool = False,
        spatial_goal_cost_uc: int = 1,
        spatial_agency_cost_uc: int = 1,
        birth_life_id: str | None = None,
        attribution_join: bool = False,
        attribution_join_cost_uc: int = 1, **kwargs,
    ):
        detector_policy.validate()
        # A scientifically independent life needs its own immutable identity.
        # Preserve the legacy reference runtime ID for existing fixtures;
        # research/operator births must supply a distinct value explicitly.
        if birth_life_id is not None:
            allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                          "0123456789:._-")
            if (type(birth_life_id) is not str
                    or not 1 <= len(birth_life_id) <= 128
                    or birth_life_id[0] not in allowed
                    or any(c not in allowed for c in birth_life_id)):
                raise ValueError("Stage12 birth life identity must be a bounded identifier")
            self.individual_id = birth_life_id
        self._stage12_explicit_birth_identity = birth_life_id is not None
        if type(diagnostic_sample_cost_uc) is not int or diagnostic_sample_cost_uc < 1:
            raise ValueError("Stage12 diagnostics need a positive injected P-43 UC cost")
        if type(module_occupancy_cost_uc) is not int or module_occupancy_cost_uc < 1:
            raise ValueError("Stage12 occupancy work requires a positive versioned UC cost")
        if type(subjective_goal_agency) is not bool:
            raise ValueError("goal agency opt-in must be explicit boolean")
        if type(dual_scope_agency) is not bool or (dual_scope_agency and not subjective_goal_agency):
            raise ValueError("dual-scope requires first-person agency at birth")
        if dual_scope_agency and attribution_join:
            raise ValueError("legacy GA-06 cannot treat proximal action agency as distal responsibility")
        if type(dual_scope_cost_uc) is not int or dual_scope_cost_uc < 1:
            raise ValueError("dual-scope requires positive UC cost")
        if type(goal_agency_cost_uc) is not int or goal_agency_cost_uc < 1:
            raise ValueError("goal agency cognitive service requires positive UC")
        if type(attribution_join) is not bool or (
            attribution_join and not subjective_goal_agency
        ):
            raise ValueError("attribution join requires an enabled cognitive producer")
        if type(attribution_join_cost_uc) is not int or attribution_join_cost_uc < 1:
            raise ValueError("attribution join needs a positive deterministic UC cost")
        if type(spatial_goal_progress) is not bool:
            raise ValueError("spatial goal criterion requires explicit birth opt-in")
        if type(spatial_goal_cost_uc) is not int or spatial_goal_cost_uc < 1:
            raise ValueError("spatial goal criterion requires positive versioned UC")
        if type(spatial_agency_cost_uc) is not int or spatial_agency_cost_uc < 1:
            raise ValueError("spatial agency requires positive declared UC")
        self._spatial_agency_cost_uc = spatial_agency_cost_uc
        self._spatial_goal_enabled = spatial_goal_progress
        self._spatial_goal_cost_uc = spatial_goal_cost_uc
        self._attribution_join_enabled = attribution_join
        self._attribution_join_cost_uc = attribution_join_cost_uc
        self._dual_scope_enabled = dual_scope_agency
        self._dual_scope_cost_uc = dual_scope_cost_uc
        self._goal_agency_enabled = subjective_goal_agency
        self._goal_agency_cost_uc = goal_agency_cost_uc
        self._stage12_occupancy_cost_uc = module_occupancy_cost_uc
        alert_policy = Stage12AlertPolicy(
            version="stage12-alerts-v1+" + detector_policy.version,
            persistence_world_steps=operator_alert_persistence_steps,
        )
        alert_policy.validate()
        self._stage12_alert_policy = alert_policy
        self._stage12_detector_policy = detector_policy
        self._stage12_diagnostic_cost_uc = diagnostic_sample_cost_uc
        super().__init__(**kwargs)
        if self._goal_agency_enabled:
            self.stage3.control.enable_goal_agency()
            if self._dual_scope_enabled:
                self.stage3.control.enable_dual_scope()
        self._stage12_detectors = Stage12LivedDetectors(detector_policy)
        self._stage12_alerts = Stage12AlertLedger(alert_policy)
        self._meta_custody = _Stage12MetacognitionCustody(
            previous=self._meta_custody, detectors=self._stage12_detectors,
            alerts=self._stage12_alerts,
            attribution_enabled=self._attribution_join_enabled,
        )
        self._recent_agency_judgement = None
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
        agency_cost = self._goal_agency_cost_uc if self._goal_agency_enabled else 0
        join_cost = self._attribution_join_cost_uc if self._attribution_join_enabled else 0
        dual_cost = self._dual_scope_cost_uc if self._dual_scope_enabled else 0
        spatial_cost = self._spatial_goal_cost_uc if self._spatial_goal_enabled else 0
        spatial_agency_cost = (
            self._spatial_agency_cost_uc
            if self._spatial_goal_enabled and self._goal_agency_enabled else 0
        )
        budget = replace(
            old, version=(old.version + "+" + self._stage12_detector_policy.version
                          + "+stage12-diagnostics-charged-v1"
                          + "+stage12-st-module-occupancy-v1"
                          + "+" + CONTRACT_VERSION
                          + ("+" + SPATIAL_CONTRACT_VERSION if spatial_cost else "")
                          + ("+" + GOAL_AGENCY_VERSION if agency_cost else "")
                          + ("+" + DUAL_SCOPE_VERSION if dual_cost else "")
                          + ("+" + PAIR_VERSION if join_cost else "")
                          + "+stage12-alerts-v1-p"
                          + str(self._stage12_alert_policy.persistence_world_steps)),
            cycle_ceiling=(old.cycle_ceiling + cost + occupancy_cost
                           + agency_cost + join_cost + spatial_cost
                           + spatial_agency_cost + dual_cost),
            module_envelopes={
                **old.module_envelopes,
                # Stage11 has no Stage10 metacognition envelope yet.
                # Reserve the upcoming sleep proposal AND Stage12 sample,
                # instead of overwriting the diagnostic capacity during the
                # later Stage10 with_budget() configuration step.
                **({"action_control": (
                    old.module_envelopes.get("action_control", 0)
                    + agency_cost + spatial_agency_cost + dual_cost
                )} if agency_cost else {}),
                "metacognition_health": max(
                    old.module_envelopes.get("metacognition_health", 0),
                    base.sleep_option_uc,
                ) + cost + occupancy_cost + join_cost + spatial_cost,
            },
            operation_costs={
                **old.operation_costs,
                "stage12_diagnostic_sample": cost,
                "stage12_occupancy_entropy": occupancy_cost,
                **({"goal_agency_assessment": agency_cost} if agency_cost else {}),
                **({"goal_outcome_responsibility_assessment": dual_cost} if dual_cost else {}),
                **({"stage12_attribution_join": join_cost} if join_cost else {}),
                **({"stage12_spatial_goal_preregistration": spatial_cost}
                   if spatial_cost else {}),
                **({"goal_agency_spatial_assessment": spatial_agency_cost}
                   if spatial_agency_cost else {}),
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


    def _admit_lived_attribution_pair(
        self, *, cycle: int, world_step: int, followup, followup_ref: str,
    ) -> None:
        """GA-06: join independent source receipts after BOTH were published.

        No P-47 verdict, Oracle, Bench or hidden cause can enter this path.
        Results remain invisible to diagnostics until the NEXT physical step.
        """
        ledger = self._meta_custody.attribution_pairs
        if ledger is None or followup.criterion_outcome not in ("success", "failure"):
            return
        source = self._recent_agency_judgement
        if source is None or source[0] != world_step:
            return
        _, judgement_ref, judgement = source
        if (
            judgement.intent_ref != followup.intent_ref
            or judgement.life_id != self.individual_id
            or judgement.observed_world_step != world_step
            or judgement.subjective_agency not in ("self", "world")
            or judgement.cue_ref is None
        ):
            return
        charge = self.compute_budget.charge(
            module="metacognition_health",
            operation="stage12_attribution_join",
        )
        self._write(kind="compute_charge", cycle=cycle, data={
            "module": "metacognition_health",
            "operation": "stage12_attribution_join",
            "requested_uc": charge.requested_uc,
            "accepted": charge.accepted,
            "reason": charge.reason,
        })
        if not charge.accepted:
            self._write(
                kind="stage12_attribution_join_deferred", cycle=cycle,
                data={"intent_ref": followup.intent_ref,
                      "goal_followup_ref": followup_ref,
                      "agency_judgement_ref": judgement_ref,
                      "reason": charge.reason},
            )
            self._cycle_degraded = True
            return
        data = {
            "version": PAIR_VERSION, "life_id": self.individual_id,
            "intent_ref": followup.intent_ref,
            "goal_followup_ref": followup_ref,
            "agency_assessment_ref": judgement.assessment_ref,
            "agency_judgement_ref": judgement_ref,
            "observed_world_step": world_step,
            "outcome": followup.criterion_outcome,
            "agency": judgement.subjective_agency,
        }
        pair_ref = self._write(
            kind="stage12_attribution_pair_admitted", cycle=cycle,
            data=data,
        )
        ledger.admit(LivedAttributionPair(pair_ref=pair_ref, **data))

    def _consume_attribution_diagnostic_pair(
        self, *, cycle: int, world_step: int, uc_refused: bool,
    ):
        """GA-06: explicitly retire pairs if an intervening step was asleep.

        No sleep-cycle cognition is fabricated. The next waking metacognitive
        phase pays its already declared diagnostic UC and records the expired
        provenance rather than silently dropping the pending pair. The
        detector must never apply a pair outside its next physical step.
        """
        ledger = self._meta_custody.attribution_pairs
        if ledger is None:
            return None
        previously_pending = ledger.pending
        pair = ledger.consume(diagnostic_world_step=world_step)
        if (previously_pending is not None
                and world_step > previously_pending.observed_world_step + 1):
            self._write(
                kind="stage12_attribution_sample_unavailable", cycle=cycle,
                data={
                    "pair_ref": previously_pending.pair_ref,
                    "reason": "no_waking_diagnostic_at_due_step",
                    "due_world_step": previously_pending.observed_world_step + 1,
                },
            )
            return None
        if pair is not None and uc_refused:
            self._write(
                kind="stage12_attribution_sample_unavailable", cycle=cycle,
                data={
                    "pair_ref": pair.pair_ref,
                    "reason": "diagnostic_uc_refused",
                },
            )
            return None
        return pair

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
        previous_control = hooks[4]["action_control"]
        
        def close_first_person_assessment(ctx):
            # Phase 4 belongs to Action Control, not to Metacognition.
            # A prior action's sensory evidence is judged before the
            # current action's decision, with explicit independent UC.
            # Action Control owns this optional first-person judgement.
            # The detector still receives no pairs until GA-06 is audited.
            service = self.stage3.control.goal_agency
            if service is not None and service.pending is not None:
                pending_assessment = service.pending
                if capture.t_monde > pending_assessment.sent_world_step:
                    agency_charge = self.compute_budget.charge(
                        module="action_control",
                        operation="goal_agency_assessment",
                    )
                    self._write(kind="compute_charge", cycle=cycle, data={
                        "module": "action_control",
                        "operation": "goal_agency_assessment",
                        "requested_uc": agency_charge.requested_uc,
                        "accepted": agency_charge.accepted,
                        "reason": agency_charge.reason,
                    })
                    spatial_paid = True
                    if (pending_assessment.mechanism ==
                            "witnessed_goal_spatial_target_v1"):
                        spatial_charge = self.compute_budget.charge(
                            module="action_control",
                            operation="goal_agency_spatial_assessment",
                        )
                        self._write(kind="compute_charge", cycle=cycle, data={
                            "module": "action_control",
                            "operation": "goal_agency_spatial_assessment",
                            "requested_uc": spatial_charge.requested_uc,
                            "accepted": spatial_charge.accepted,
                            "reason": spatial_charge.reason,
                        })
                        spatial_paid = spatial_charge.accepted
                    judgement = service.evaluate(
                        capture=capture, world_step=capture.t_monde,
                        cue_ref=deterministic_id(
                            "stage12-authorized-capture-cue-v1",
                            capture.t_monde, capture.x, capture.y,
                            tuple(sorted(capture.inventory.items())),
                        ) if (agency_charge.accepted and spatial_paid) else None,
                        paid=(agency_charge.accepted and spatial_paid),
                    )
                    if judgement is not None:
                        judgement_ref = self._write(
                            kind="stage12_goal_agency_judgement",
                            cycle=cycle, data=judgement.as_dict(),
                        )
                        self._recent_agency_judgement = (
                            capture.t_monde, judgement_ref, judgement,
                        )
            previous_control(ctx)

        hooks[4]["action_control"] = close_first_person_assessment
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
                if self._meta_custody.attribution_pairs is not None:
                    self._consume_attribution_diagnostic_pair(
                        cycle=cycle, world_step=capture.t_monde,
                        uc_refused=True,
                    )
                # Keep the strict debit -> deferral receipt adjacency:
                # unknown goal followups may be published only afterwards.
                pending = self._meta_custody.goal_progress.followup(
                    world_step=capture.t_monde, body=None,
                    diagnostic_paid=False, position=None,
                )
                if pending is not None:
                    self._write(
                        kind="stage12_goal_progress_followup",
                        cycle=cycle, data=pending.as_dict(),
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
            pair = (
                None if self._meta_custody.attribution_pairs is None
                else self._consume_attribution_diagnostic_pair(
                    cycle=cycle, world_step=capture.t_monde,
                    uc_refused=False,
                )
            )
            report = self._stage12_detectors.observe(
                LivedCognitiveObservation(
                    world_step=capture.t_monde, cycle=cycle,
                    context_signature=context,
                    active_goal_ref=goal_ref, option_ref=option_ref,
                    progress_delta=progress,
                    outcome="unknown" if pair is None else pair.outcome,
                    agency="unknown" if pair is None else pair.agency,
                    attribution_ref=None if pair is None else pair.pair_ref,
                    verification_origin=(
                        "none" if pair is None else "lived_physical"
                    ),
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
                    "diagnostic_window": self._stage12_detector_policy.window,
                    **({"attribution_pair_ref": None if pair is None else pair.pair_ref,
                        "verified_successes": report.verified_successes,
                        "verified_failures": report.verified_failures,
                        "bias_min_outcomes_each": (
                            self._stage12_detector_policy.bias_min_outcomes_each
                        ),
                        "attribution_bias_threshold": (
                            self._stage12_detector_policy.attribution_bias_threshold
                        )}
                       if self._attribution_join_enabled else {}),
                    "operator_alert_policy_version": self._stage12_alert_policy.version,
                    "operator_alert_persistence_steps": (
                        self._stage12_alert_policy.persistence_world_steps
                    ),
                },
            )
            # Persistence bookkeeping is included in the already charged
            # metacognitive diagnostic sample, without new motor authority.
            for alert in self._stage12_alerts.observe(report):
                self._write(
                    kind="stage12_operator_alert", cycle=cycle,
                    data={
                        **alert.as_dict(),
                        "diagnostic_policy_version": self._stage12_detector_policy.version,
                    },
                )
            # Preserve debit -> diagnosis -> contiguous operator-alert
            # receipts. Only afterwards publish the separate goal-progress
            # followup, derived from *lived* body telemetry without Oracle.
            # The bounded work is included in the accepted diagnostic UC.
            goal_followup = self._meta_custody.goal_progress.followup(
                world_step=capture.t_monde, body=capture.body,
                diagnostic_paid=True, position=(capture.x, capture.y),
            )
            if goal_followup is not None:
                followup_ref = self._write(
                    kind="stage12_goal_progress_followup",
                    cycle=cycle, data=goal_followup.as_dict(),
                )
                self._admit_lived_attribution_pair(
                    cycle=cycle, world_step=capture.t_monde,
                    followup=goal_followup, followup_ref=followup_ref,
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
            # The declaration must precede the irreversible command. Only
            # an already UC-paid metacognitive step may record it. The
            # declared target must actually belong to the active goal.
            capture = self.stage3._capture
            measure = None if active is None else active.principal_measure
            before = (
                None if capture is None or measure not in ALLOWED_MEASURES
                else capture.body.get(measure)
            )
            if (self.detection_report.world_step == sent_t_monde
                    and active is not None
                    and active.target == measure
                    and proposal.option.goal_ref == active.id
                    and proposal.option.motive_ref.type == "active_goal"
                    and type(before) in (int, float)
                    and isfinite(before) and before >= 0):
                if self._meta_custody.goal_progress.pending is not None:
                    raise RuntimeError("prior lived goal-progress criterion unclosed")
                # Option A: select a *perceived* adjacent target matching
                # the active need. Never infer target coordinates from the
                # world, Oracle, prediction conformity or benchmark scenario.
                spatial = None
                direction = prepared.command.parameters.get("direction")
                if (self._spatial_goal_enabled
                        and prepared.command.primitive == "se_deplacer"
                        and type(direction) is str):
                    choices = []
                    for cell in capture.adjacent:
                        if cell.direction != direction:
                            continue
                        kind = (
                            "water" if measure == "water" and cell.water_source
                            else next((
                                berry for berry in ("berry_a", "berry_b")
                                if measure == "food" and berry in cell.resources
                            ), None)
                        )
                        if kind is not None:
                            choices.append((cell, kind))
                    if len(choices) == 1:
                        spatial = choices[0]
                if spatial is not None:
                    charge = self.compute_budget.charge(
                        module="metacognition_health",
                        operation="stage12_spatial_goal_preregistration",
                    )
                    self._write(kind="compute_charge", cycle=cycle, data={
                        "module": "metacognition_health",
                        "operation": "stage12_spatial_goal_preregistration",
                        "requested_uc": charge.requested_uc,
                        "accepted": charge.accepted,
                        "reason": charge.reason,
                    })
                    if not charge.accepted:
                        self._cycle_degraded = True
                        self._write(
                            kind="stage12_spatial_goal_preregistration_deferred",
                            cycle=cycle,
                            data={"reason": charge.reason,
                                  "option_ref": proposal.option.id},
                        )
                        return super()._dispatch_decision(
                            proposal=proposal, prepared=prepared,
                            admission=admission, cycle=cycle,
                            sent_t_monde=sent_t_monde,
                        )
                    cell, target_kind = spatial
                    registered = {
                        "contract_version": SPATIAL_CONTRACT_VERSION,
                        "goal_ref": active.id,
                        "option_ref": proposal.option.id,
                        "command_hash": command_digest(prepared.command),
                        "measure": SPATIAL_MEASURE,
                        "value_before": 1.0,
                        "sent_world_step": sent_t_monde,
                        "observe_world_step": sent_t_monde + 1,
                        "life_id": self.individual_id,
                        "start_x": capture.x, "start_y": capture.y,
                        "target_x": cell.x, "target_y": cell.y,
                        "target_kind": target_kind, "direction": direction,
                    }
                else:
                    registered = {
                        "contract_version": CONTRACT_VERSION,
                        "goal_ref": active.id,
                        "option_ref": proposal.option.id,
                        "command_hash": command_digest(prepared.command),
                        "measure": measure,
                        "value_before": float(before),
                        "sent_world_step": sent_t_monde,
                        "observe_world_step": sent_t_monde + 1,
                    }
                intent_ref = self._write(
                    kind="stage12_goal_progress_preregistered",
                    cycle=cycle, data=registered,
                )
                self._meta_custody.goal_progress.preregister(
                    (LivedSpatialGoalIntent if spatial is not None
                     else LivedGoalProgressIntent)(
                        intent_ref=intent_ref,
                        **registered,
                    )
                )
                service = self.stage3.control.goal_agency
                if service is not None:
                    assessment = service.preregister(
                        assessment_ref=deterministic_id(
                            "stage12-action-control-agency-commit-v1",
                            self.individual_id, intent_ref,
                            sent_t_monde, registered["command_hash"],
                        ),
                        intent_ref=intent_ref, life_id=self.individual_id,
                        goal_ref=active.id, option_ref=proposal.option.id,
                        command_hash=registered["command_hash"],
                        world_step=sent_t_monde, measure=registered["measure"],
                        command=prepared.command, capture=capture,
                        spatial_target=(
                            None if spatial is None else (
                                registered["target_x"], registered["target_y"],
                                registered["target_kind"],
                            )
                        ),
                    )
                    self._write(
                        kind="stage12_goal_agency_precommitted",
                        cycle=cycle, data=assessment.as_dict(),
                    )
        return super()._dispatch_decision(
            proposal=proposal, prepared=prepared, admission=admission,
            cycle=cycle, sent_t_monde=sent_t_monde,
        )
