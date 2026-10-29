"""Research-only A1 decision-read intervention, never a TD learning change.

All current natural-I1 learned_value calls are made by precisely three
decision consumers: local Planning, goal-directed Planning, direct Stage8.
The pending-affordance Stage8 adapter consumes Planning's already-read value.
The wrapper calls the actual Q owner ONCE, and hides only its *decision return*.
No TD updates, features, weights, traces, world effects, or UC charges change.

The external rows are provisional until each M11 step is committed and the
SQLite journal is cold-audited. NEVER present a log row alone as M11 evidence.
"""
from contextlib import contextmanager
from pathlib import Path
import sys
from unittest.mock import patch

_ALLOWED_CALLS = {
    ("i1_natural_runtime.py", "_propose_independent_local"): "planning_local",
    ("i1_active_runtime.py", "_consider_uncertain_affordance"): "planning_goal",
    ("stage8_evaluator.py", "evaluate"): "stage8_direct",
}
_MODES = ("canonical", "td_read_masked")


def _decision_value(actual, *, masked, signature):
    """Pure return transform; keep the original TD owner untouched."""
    from i1.modules.td_values import LearnedValue
    if (type(actual) is not LearnedValue or actual.signature != signature
            or actual.status not in ("learned", "unlearned")):
        raise ValueError("unexpected Q read receipt")
    if actual.status == "unlearned":
        if (actual.value is not None or actual.evidence is not None
                or actual.update_count != 0):
            raise ValueError("unlearned Q return violates native contract")
        return actual
    if (actual.value is None or actual.evidence is None
            or type(actual.update_count) is not int
            or actual.update_count < 1):
        raise ValueError("learned Q return violates native contract")
    if not masked:
        return actual
    return LearnedValue(
        signature=signature, status="unlearned",
        value=None, evidence=None, update_count=0,
    )


@contextmanager
def a1_decision_read_scope(*, mode, reads, adapters):
    """Instrument a single serial M11 arm, not a shared or asynchronous life.

    The caller must keep the scope limited to actor.run_step() and independently
    verify each exported occurrence from the cold M11. Two research arms must
    run separately; this is never installed in canonical production births.
    """
    if mode not in _MODES or type(reads) is not list or type(adapters) is not list:
        raise ValueError("invalid A1 decision-read scope")
    from i1.modules.td_values import LinearTDValues
    from i1lab.i1_active_runtime import I1PartialEvidenceAdapter

    original_read = LinearTDValues.learned_value
    original_adapter = I1PartialEvidenceAdapter.evaluate
    masked = mode == "td_read_masked"

    def read_once(owner, state, signature):
        frame = sys._getframe(1)
        key = (Path(frame.f_code.co_filename).name, frame.f_code.co_name)
        source = _ALLOWED_CALLS.get(key)
        if source is None:
            raise RuntimeError("A1 uncovered learned-value consumer: " + str(key))
        if source == "stage8_direct":
            context = frame.f_locals
            step, cycle = context["t_monde"], context["cycle"]
            option_ref = context["proposal"].option.id
        else:
            context = frame.f_locals
            step, cycle = context["capture"].t_monde, context["cycle"]
            option_ref = None  # Planning has not selected an option yet.
        if (type(step) is not int or step < 1
                or type(cycle) is not int or cycle < 1
                or type(signature) is not str or not signature):
            raise RuntimeError("A1 read has invalid causal context")
        actual = original_read(owner, state, signature)
        result = _decision_value(actual, masked=masked, signature=signature)
        reads.append({
            "source": source, "step": step, "cycle": cycle,
            "option_ref": option_ref, "signature": signature,
            "original_status": actual.status, "original_value": actual.value,
            "original_evidence": actual.evidence,
            "update_count": actual.update_count,
            "masked": masked and actual.status == "learned",
        })
        return result

    def observe_adapter(owner, *, proposal, **kwargs):
        result = original_adapter(owner, proposal=proposal, **kwargs)
        pending = owner._pending
        local = pending.get("local_opportunity_evidence")
        if (proposal.option.provenance == "i1_unknown_affordance"
                and isinstance(local, dict)
                and local.get("option_ref") == proposal.option.id):
            pending = local
        if (proposal.option.id == pending.get("option_ref")
                and pending.get("affordance") is True):
            source_status = pending.get("learned_status")
            delivered = result.evaluation.learned_value_status
            if source_status not in ("learned", "unlearned"):
                raise RuntimeError("A1 adapter pending Q has invalid state")
            if source_status != delivered:
                raise RuntimeError("A1 adapter changed learned Q status")
            if masked and delivered == "learned":
                raise RuntimeError("A1 leaked learned Q through pending Stage8")
            adapters.append({
                "source": "stage8_pending_adapter",
                "step": kwargs["t_monde"], "cycle": kwargs["cycle"],
                "option_ref": proposal.option.id,
                "signature": proposal.option.learning_signature,
                "delivered_status": delivered,
                "masked": masked,
            })
        return result

    with patch.object(LinearTDValues, "learned_value", read_once):
        with patch.object(I1PartialEvidenceAdapter, "evaluate", observe_adapter):
            yield
    if (LinearTDValues.learned_value is not original_read
            or I1PartialEvidenceAdapter.evaluate is not original_adapter):
        raise RuntimeError("A1 read intervention not removed after step scope")
