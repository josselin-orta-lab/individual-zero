"""I1-only birth-opted experimental Stage12 runtime.

This is NOT the I0 runtime and not a second command authority. It may propose
one uncertain, first-person grounded move/collection when the exact Stage6
equipment is incomplete. A sealed external visible-delta model is an inherited
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
        receipt = self._pending.get("receipt")
        if (receipt is None
                or proposal.option.id != self._pending.get("option_ref")
                or proposal.plan is None
                or len(proposal.plan.steps) != 1
                or proposal.option.provenance != "i1_partial_experiment"
                or kwargs.get("t_monde") != self._pending.get("world_step")):
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
        self._i1_model_contract = (
            (I1_POLICY, i1_model_enabled, i1_forecast_cost_uc,
             None if i1_model is None else i1_model.version,
             None if i1_model is None else i1_model.corpus_sha256,
             None if i1_model is None else i1_model.deltas,
             None if i1_model is None else i1_model.counts,
             RECALL_POLICY, i1_lived_recall_enabled, i1_recall_cost_uc)
        )
        self._i1_pending = {}
        super().__init__(**kwargs)
        if self.stage3.substrate.bench is not None:
            raise RuntimeError("autonomous I1 cannot receive Bench access")

    def _parent_runtime_config(self, config):
        base = super()._parent_runtime_config(config)
        if not self._i1_enabled:
            return base
        stage9 = base.stage9
        stage8 = stage9.stage8
        stage7 = stage8.stage7
        stage6 = stage7.stage6
        stage4 = stage6.stage4
        original = stage4.compute_budget
        cost = self._i1_forecast_cost_uc
        extra = self._i1_recall_cost_uc if self._i1_lived_recall_enabled else 0
        budget = replace(
            original,
            version=original.version + "+" + I1_POLICY,
            cycle_ceiling=original.cycle_ceiling + cost + extra,
            module_envelopes={
                **original.module_envelopes,
                "planning": original.module_envelopes["planning"] + cost,
                "competition": original.module_envelopes["competition"] + extra,
            },
            operation_costs={
                **original.operation_costs,
                I1_EXPERIMENTAL_OPERATION: cost,
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

    def _propose_for_cycle(
        self, *, capture, goal_for_planning, st_before_cycle, cycle,
    ):
        exact = super()._propose_for_cycle(
            capture=capture, goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle, cycle=cycle,
        )
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
