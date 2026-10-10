"""Stage-11 P-48 evaluation: intrinsic evidence without Stage-9 modifications."""
from dataclasses import replace
from math import isfinite

from .causal_test_planning import Stage9OptionEvaluator
from .competition import OptionEvidenceInput
from .stage8_evaluator import Stage8OptionEvaluator


class Stage11OptionEvaluator(Stage9OptionEvaluator):
    def __init__(self, *, exploration, intrinsic_weight, **kwargs):
        super().__init__(**kwargs)
        if not isfinite(intrinsic_weight) or intrinsic_weight < 0:
            raise ValueError("P-15 intrinsic weight must be finite and nonnegative")
        self._exploration = exploration
        self._intrinsic_weight = intrinsic_weight

    def evaluate(self, *, proposal, evaluation_state, initial_state, cycle, t_monde):
        if proposal.option.motive_ref.type != "test_causal":
            return super().evaluate(
                proposal=proposal, evaluation_state=evaluation_state,
                initial_state=initial_state, cycle=cycle, t_monde=t_monde,
            )
        # Stage-8 supplies only the extrinsic term. The Stage-9 P-48 guard
        # remains unchanged on all pre-vNext runtimes.
        original = Stage8OptionEvaluator.evaluate(
            self, proposal=proposal, evaluation_state=evaluation_state,
            initial_state=initial_state, cycle=cycle, t_monde=t_monde,
        )
        intrinsic = self._exploration.motivation(proposal.option)
        ids = tuple(original.evaluation.signal_ids)
        duplicated = bool(set(ids) & set(intrinsic.signal_ids))
        if intrinsic.status != "available" or duplicated:
            reason = "shared_signal" if duplicated else intrinsic.reason
            assessment = replace(
                original.evaluation, status="not_evaluated",
                intrinsic_status="applicable", intrinsic_value=None,
                producers=tuple(dict.fromkeys(
                    original.evaluation.producers + (f"exploration:{reason}",)
                )),
            )
            result = OptionEvidenceInput(assessment, None)
            result.validate()
            return result
        # No Q and no completed simulation means extrinsic unavailable.
        # DC-01 explicitly defines the missing extrinsic component as zero,
        # without treating it as a negative learned value.
        extrinsic = 0.0 if original.evidence is None else original.evidence
        evidence = max(-1.0, min(1.0, extrinsic + self._intrinsic_weight * intrinsic.value))
        assessment = replace(
            original.evaluation, status="evaluated",
            intrinsic_status="applicable", intrinsic_value=intrinsic.value,
            signal_ids=ids + intrinsic.signal_ids,
            producers=tuple(dict.fromkeys(
                original.evaluation.producers + ("exploration:p48",)
            )),
        )
        result = OptionEvidenceInput(assessment, evidence)
        result.validate()
        return result
