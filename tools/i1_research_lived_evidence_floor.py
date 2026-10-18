"""Experimental I1-only positive-lived-evidence non-attenuation.

This module is a *laboratory intervention*, installed only after the I1 fork
has been generated in a separate process and before a NEW mortal birth.
It does not change I0, safety, physical rules, or action dispatch.
A positive TD trace cannot *lower* the already-perceived need-linked baseline.
Negative lived TD traces retain their full ability to disfavor an action.
"""
from math import isfinite

POLICY = "i1-research-positive-lived-floor-v1"


def effective_learned_signal(*, prior, learned):
    """Signal to the unchanged I1 Stage8 formula; preserve negative evidence."""
    if type(prior) is not float or not isfinite(prior) or not 0 <= prior <= 1:
        raise ValueError("prior must be a finite perceived, need-linked score")
    if learned is None:
        return None
    if type(learned) is not float or not isfinite(learned) or not -1 <= learned <= 1:
        raise ValueError("learned signal must be finite and clipped")
    return max(prior, learned) if learned > 0 else learned


def install_research_positive_floor():
    """Versioned, process-scoped research overlay on I1's usual evaluator.

    Must be called exactly once, before I1 birth; each research arm is its
    own fresh process. All normal Stage8 validations and Action Control remain.
    """
    import i1lab.i1_active_runtime as active

    original = active.I1PartialEvidenceAdapter
    if POLICY in active.I1_AFFORDANCE_POLICY:
        raise ValueError("research overlay installed twice")
    if not active.I1_AFFORDANCE_POLICY.startswith(
        "i1-unknown-action-affordance-v2-general-local"
    ):
        raise ValueError("unrecognized I1 affordance policy")

    class ResearchPositiveFloorAdapter(original):
        def evaluate(self, *, proposal, **kwargs):
            pending = self._pending
            if (getattr(proposal.option, "provenance", None)
                    == "i1_unknown_affordance"
                    and proposal.option.id == pending.get("option_ref")
                    and kwargs.get("t_monde") == pending.get("world_step")
                    and pending.get("affordance") is True
                    and pending.get("learned_status") == "learned"):
                original_learned = pending.get("learned_evidence")
                positive_floor_signal = effective_learned_signal(
                    prior=float(pending["prior_evidence"]),
                    learned=(None if original_learned is None
                             else float(original_learned)),
                )
                if positive_floor_signal != original_learned:
                    pending["learned_evidence"] = positive_floor_signal
                    try:
                        return super().evaluate(proposal=proposal, **kwargs)
                    finally:
                        pending["learned_evidence"] = original_learned
            return super().evaluate(proposal=proposal, **kwargs)

    active.I1PartialEvidenceAdapter = ResearchPositiveFloorAdapter
    active.I1_AFFORDANCE_POLICY = active.I1_AFFORDANCE_POLICY + "+" + POLICY
    return active.I1_AFFORDANCE_POLICY
