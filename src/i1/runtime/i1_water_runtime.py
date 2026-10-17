"""D1 I1-only birth-opted active water-learning experimental Stage12.

Only first-person captures and actually applied actions enter the evidence
owner. The water source cue is local; future locations, hazards and Oracle
truth remain unknown. No second WorldBody sender or motor bypass exists.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256

from i1.contracts import (
    EvaluationOption, MotiveRef, Option, OptionProposal, Plan, PlanStep,
)
from i1.interfaces import PrimitiveCommand
from i1.modules.competition import OptionEvidenceInput
from i1.experimental.lived_water import I1LivedWaterOwner, SCHEMA
from .determinism import canonical_causal_bytes, sha256_hex
from .scheduler import CyclePhase
from .world import command_digest
from .i1_active_runtime import ExperimentalI1Stage12Runtime

POLICY = "i1-firstperson-water-d1b-tuned-v1"
CONSIDER = "i1_water_consider_option"
ACQUIRE = "i1_water_consume_lived_followup"
PROBE_SCORE = 0.70
LEARNED_SCORE = 0.72


class _I1WaterM11Owner(I1LivedWaterOwner):
    """Cold-capability adapter lives in I1 Lab; pure cognition never imports Lab."""

    def install_m11_cold_state(self, state: object, *, capability: object) -> None:
        from .m11_transactional_mortal import _M11_COLD_OWNER_TOKEN
        if capability is not _M11_COLD_OWNER_TOKEN:
            raise ValueError("water model cold import requires authentic M11 token")
        self._load_trusted_current_on_fresh(state)


class I1WaterEvidenceAdapter:
    """Transient Stage8 option-scoring adapter, not a second Competition."""

    def __init__(self, underlying, pending: dict[str, object]):
        self._underlying = underlying
        self._pending = pending

    def __getattr__(self, key):
        if key.startswith("__"):
            raise AttributeError(key)
        underlying = vars(self).get("_underlying")
        if underlying is None:
            raise AttributeError(key)
        return getattr(underlying, key)

    def evaluate(self, *, proposal, **kwargs):
        receipt = self._pending
        if (proposal.option.provenance != "i1_water_lived_experiment"
                or receipt.get("option_ref") != proposal.option.id
                or kwargs.get("t_monde") != receipt.get("world_step")
                or proposal.plan is None or len(proposal.plan.steps) != 1):
            return self._underlying.evaluate(proposal=proposal, **kwargs)
        e = EvaluationOption(
            option_ref=proposal.option.id,
            option_version=proposal.option.version,
            cycle=kwargs["cycle"], t_monde=kwargs["t_monde"],
            status="evaluated", learned_value_status="unlearned",
            learned_value=None, simulated_value_status="unavailable",
            simulated_value=None, intrinsic_status="not_applicable",
            intrinsic_value=None, risk_status="unknown", risk=None,
            safety_uncertainty=1.0, protection=False, signal_ids=(),
            producers=("i1:water-firstperson-exploratory-instrument-v1",),
        )
        result = OptionEvidenceInput(
            evaluation=e,
            evidence=LEARNED_SCORE if receipt.get("learned") else PROBE_SCORE,
        )
        result.validate()
        return result


class I1WaterLearningRuntime(ExperimentalI1Stage12Runtime):
    """One real Stage12/ActionControl substrate with priced I1 water knowledge."""

    individual_id = "i1-water-firstperson-stage12"

    def __init__(
        self, *, i1_water_probe_enabled: bool = False,
        i1_water_learning_enabled: bool = False,
        i1_water_consider_uc: int = 2,
        i1_water_acquire_uc: int = 2, **kwargs,
    ):
        if (type(i1_water_probe_enabled) is not bool
                or type(i1_water_learning_enabled) is not bool
                or (i1_water_learning_enabled and not i1_water_probe_enabled)):
            raise ValueError("water acquisition requires an explicit common probe")
        if (type(i1_water_consider_uc) is not int or i1_water_consider_uc < 1
                or type(i1_water_acquire_uc) is not int
                or i1_water_acquire_uc < 1):
            raise ValueError("I1 water research consumes positive declared UC")
        if i1_water_probe_enabled and (kwargs.get("autonomous_mortal") is not True
                or not isinstance(kwargs.get("birth_life_id"), str)
                or not kwargs["birth_life_id"].startswith("i1:")):
            raise ValueError("I1 water requires independent opted-in mortal birth")
        self._i1_water_probe_enabled = i1_water_probe_enabled
        self._i1_water_learning_enabled = i1_water_learning_enabled
        self._i1_water_consider_uc = i1_water_consider_uc
        self._i1_water_acquire_uc = i1_water_acquire_uc
        self._i1_water_contract = (
            POLICY, i1_water_probe_enabled, i1_water_learning_enabled,
            i1_water_consider_uc, i1_water_acquire_uc, SCHEMA,
        )
        self._water_pending: dict[str, object] = {}
        self._water_learner = _I1WaterM11Owner(
            life_id=kwargs.get("birth_life_id") or "i1:disabled",
            enabled=i1_water_learning_enabled,
        )
        super().__init__(**kwargs)
        if self.stage3.substrate.bench is not None:
            raise RuntimeError("living water model must not receive Bench truth")

    @property
    def causal_owners(self):
        return (*super().causal_owners, self._water_learner)

    @property
    def lived_water_model(self) -> dict[str, object]:
        """Detached operator-readable diagnostic, not an external update API."""
        return self._water_learner.export_causal_state()

    def _parent_runtime_config(self, config):
        base = super()._parent_runtime_config(config)
        if not self._i1_water_probe_enabled:
            return base
        stage9=base.stage9
        stage8=stage9.stage8
        stage7=stage8.stage7
        stage6=stage7.stage6
        stage4=stage6.stage4
        old=stage4.compute_budget
        reserve=self._i1_water_consider_uc + (
            self._i1_water_acquire_uc if self._i1_water_learning_enabled else 0)
        budget=replace(
            old,
            version=old.version+"+"+POLICY+(
                "+lived" if self._i1_water_learning_enabled else "+frozen"),
            cycle_ceiling=old.cycle_ceiling+reserve,
            module_envelopes={
                **old.module_envelopes,
                "planning":old.module_envelopes["planning"]+reserve,
            },
            operation_costs={
                **old.operation_costs,
                CONSIDER:self._i1_water_consider_uc,
                **({ACQUIRE:self._i1_water_acquire_uc}
                   if self._i1_water_learning_enabled else {}),
            },
        )
        revised=replace(stage9,stage8=replace(stage8,stage7=replace(
            stage7,stage6=replace(stage6,stage4=replace(
                stage4,compute_budget=budget)))))
        return replace(base,stage9=revised)

    def _on_open_step_capture(self, capture):
        self._water_pending.clear()
        return super()._on_open_step_capture(capture)

    @staticmethod
    def _capture_hash(capture) -> str:
        """Digest of authorized first-person input, never private world state."""
        return sha256_hex(canonical_causal_bytes({
            "t_monde":capture.t_monde,
            "x":capture.x,"y":capture.y,
            "body":dict(capture.body),
            "inventory":dict(capture.inventory),
            "current_water_source":capture.current_water_source,
            "adjacent":[{
                "direction":n.direction,"x":n.x,"y":n.y,
                "passable":n.passable,"water_source":n.water_source,
                "resources":list(n.resources),"creature":n.creature
            } for n in capture.adjacent],
        }))

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        hooks = super()._phase_hooks(
            cycle=cycle,capture=capture,goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle)
        original=hooks[CyclePhase.PRODUCTION]["planning"]

        def admitted_lived_followup(ctx):
            # First-person update is AFTER the prior physically closed step
            # and after opening this cycle's legitimate P-43 compute budget.
            if (cycle==1 and self._i1_water_learning_enabled
                    and self._water_learner.needs_followup(capture.t_monde)):
                accepted=self._charge(module="planning",operation=ACQUIRE)
                evidence=self._water_learner.observe_followup(
                    observed_world_step=capture.t_monde,
                    x=capture.x,y=capture.y,
                    observed_water=float(capture.body["water"]),
                    current_water_source=capture.current_water_source,
                    followup_capture_hash=self._capture_hash(capture),
                    paid_uc=accepted)
                if evidence is not None:
                    self._write(kind=(
                        "i1_water_lived_outcome_admitted" if evidence["admitted"]
                        else "i1_water_lived_outcome_unavailable"),
                        cycle=cycle,data=evidence)
            return original(ctx)

        hooks[CyclePhase.PRODUCTION]["planning"] = admitted_lived_followup
        return hooks

    def _evaluate_competition_cycle(self, *, capture, cycle):
        original=self.stage8_option_evaluator
        self.stage8_option_evaluator=I1WaterEvidenceAdapter(
            original,self._water_pending)
        try:
            # Existing I1 food adapter delegates to this evaluator if not
            # its own eligible proposal; Stage8/Competition remain authoritative.
            return super()._evaluate_competition_cycle(
                capture=capture,cycle=cycle)
        finally:
            self.stage8_option_evaluator=original

    def _propose_for_cycle(
        self, *, capture, goal_for_planning, st_before_cycle, cycle,
    ):
        existing=super()._propose_for_cycle(
            capture=capture,goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,cycle=cycle)
        if (existing is not None or not self._i1_water_probe_enabled
                or goal_for_planning is None
                or goal_for_planning.goal_type!="drink"
                or st_before_cycle is None):
            return existing
        evidence=self._water_learner.observed_water_gain
        learned=(evidence is not None and evidence>0)
        if capture.current_water_source:
            command=PrimitiveCommand("boire")
            modality="probe" if not learned else "lived"
        elif learned:
            adjacent=sorted((
                n for n in capture.adjacent
                if n.water_source and n.passable),
                key=lambda n: ("north","east","south","west").index(n.direction))
            if not adjacent:
                return None
            command=PrimitiveCommand("se_deplacer",{
                "direction":adjacent[0].direction})
            modality="lived_transfer"
        else:
            return None
        if not self._charge(module="planning",operation=CONSIDER):
            self._write(kind="i1_water_option_unavailable",cycle=cycle,
                        data={"reason":"insufficient_uc","world_step":capture.t_monde})
            return None
        option_id=(f"option:i1:water:{modality}:{goal_for_planning.id}:"
                   f"t{capture.t_monde}:{command.primitive}")
        plan_id="plan:"+option_id
        plan=Plan(
            id=plan_id,option_ref=option_id,version=POLICY,
            steps=(PlanStep(
                index=0,command=command,preconditions=(),
                predicted_consequences=(),
                observation_window_steps=1),),
            goal_ref=goal_for_planning.id,
            budget_used_uc=self._i1_water_consider_uc,
            status="valid",st_version=st_before_cycle.version,
        )
        refs=tuple(sorted(
            ref for ref in self.stage3.perception.observation_ref_by_entity.values()
            if ref in {element.contribution_ref
                       for element in st_before_cycle.competitive}))
        option=Option(
            id=option_id,version=POLICY,type="primitive",
            learning_signature="i1_water_empirical:"+command.primitive
                if learned else "i1_water_probe:"+command.primitive,
            preconditions=(),success_condition="step_completed",
            failure_condition="outcome_unconfirmed",
            invalidation_condition="new_lived_capture_or_goal_changed",
            motive_ref=MotiveRef(type="active_goal",id=goal_for_planning.id),
            founding_st_version=st_before_cycle.version,
            expires_at_step=capture.t_monde+1,
            provenance="i1_water_lived_experiment",
            grounding_contribution_refs=refs,
            goal_ref=goal_for_planning.id,plan_ref=plan_id,
        )
        proposal=OptionProposal(
            option=option,plan=plan,
            preliminary_admissibility="indeterminate")
        proposal.validate()
        self._water_pending.update(
            option_ref=option_id,world_step=capture.t_monde,learned=learned,
            modality=modality)
        self._write(kind="i1_water_option_proposed",cycle=cycle,data={
            "policy":POLICY,"option_ref":option_id,
            "source_scope":"first_person_lived" if learned else "no_effect_prior",
            "modality":modality,"command":command.as_dict(),
            "observed_water_gain":evidence,
            "model_observation_count":len(self._water_learner.examples),
            "risk_status":"unknown","safety_certificate":None,
            "goal_success_claimed":False,
            "distal_causal_responsibility":None,
        })
        return proposal

    def _dispatch_decision(
        self, *, proposal, prepared, admission, cycle, sent_t_monde,
    ):
        capture=self.stage3._capture
        prior_water=(float(capture.body["water"]) if capture is not None else None)
        capture_ref=(self._capture_hash(capture) if capture is not None else None)
        result=super()._dispatch_decision(
            proposal=proposal,prepared=prepared,admission=admission,
            cycle=cycle,sent_t_monde=sent_t_monde)
        if (self._i1_water_learning_enabled and result.status=="applied"
                and prepared.command.primitive=="boire"
                and capture is not None and prior_water is not None
                and capture_ref is not None):
            self._water_learner.record_applied(
                sent_world_step=sent_t_monde,
                before_water=prior_water,x=capture.x,y=capture.y,
                command_hash=command_digest(prepared.command),
                option_ref=proposal.option.id,
                first_capture_hash=capture_ref)
        return result
