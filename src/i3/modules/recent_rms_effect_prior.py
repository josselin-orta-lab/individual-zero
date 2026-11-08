"""Paid zero-mean unsupported-effect prior scaled by recent personal effects.

Only the magnitude of recent action-agnostic bodily consequences is reused.
Their sign and mean are discarded.

For channel c:
    s_c = sqrt(mean_i(delta_i[c]**2))

The two unsupported-effect hypotheses are +s and -s with probability .5 each.
Thus the external expected delta is exactly zero while the per-channel second
moment matches the recent personal raw second moment.

Optional innate expectation toward the unknown, omega in [-1, 1] (owner
decision A, STAGE1_OMEGA_SOFTWARE_FALSIFIER.md): the hypotheses become
(omega + 1) * s and (omega - 1) * s. The spread s is unchanged; the mean is
omega * s on every channel (uniform, need-agnostic). omega = 0 is exactly the
zero-mean prior. omega is an inherited disposition, never learned and never
derived from World facts.
"""
from __future__ import annotations

from math import fsum, isfinite, sqrt

from .body import CognitiveBudget, CognitiveWork
from .information_value import WORK_KEYS
from .plan_information import PlanSubjectiveOutcome
from .reference_branches import ReferenceBranchMemory
from .personal_outcomes import WINDOW

SCHEMA = "i3-recent-rms-zero-mean-effect-prior/v1"
SIGNAL = "DIRECT_BODY_AFTER_UNSUPPORTED_EFFECT"


def _work_delta(after, before):
    return {
        key: getattr(after, key) - getattr(before, key)
        for key in WORK_KEYS
    }


def _validate_omega(omega):
    if (type(omega) not in (int, float) or type(omega) is bool or
            not isfinite(omega) or not -1.0 <= omega <= 1.0):
        raise ValueError("omega must be a finite number in [-1, 1]")
    return float(omega)


def recent_rms_effect_prior_work_ceiling(
        memory: ReferenceBranchMemory) -> CognitiveWork:
    """Exact structural work quote for one paid RMS-prior construction."""
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    retained = len(memory._samples)
    support = min(retained, WINDOW)
    read = CognitiveWork(cycles=1, memory_items=7 * retained + 2)
    scale = (
        CognitiveWork(cycles=1, memory_items=2)
        if support < 2 else
        CognitiveWork(cycles=2, memory_items=5 * support + 12))
    return CognitiveWork(
        cycles=read.cycles + scale.cycles,
        simulated_steps=0,
        memory_items=read.memory_items + scale.memory_items,
        replays=0)


def paid_recent_rms_zero_mean_effect_prior(
        memory: ReferenceBranchMemory, budget: CognitiveBudget, *,
        work_receipt: dict | None = None, omega: float = 0.0) -> dict:
    """Build two branches from recent personal per-channel RMS scale.

    Symmetric (+s, -s) when omega = 0; otherwise shifted by omega * s.
    """
    omega = _validate_omega(omega)
    if not isinstance(memory, ReferenceBranchMemory):
        raise ValueError("ReferenceBranchMemory required")
    if not isinstance(budget, CognitiveBudget):
        raise ValueError("CognitiveBudget required")
    if work_receipt is not None and type(work_receipt) is not dict:
        raise ValueError("work_receipt must be a plain dict")

    start = budget.work
    read_receipt = {}
    samples = memory.recent_generic_effects(
        budget, work_receipt=read_receipt)
    after_read = budget.work

    if len(samples) < 2:
        budget.spend(CognitiveWork(cycles=1, memory_items=2))
        scale = (0.0,) * 5
        second_moment = (0.0,) * 5
        outcomes = ()
        status = "INSUFFICIENT_GENERIC_SUPPORT"
    else:
        # The generic read is bounded by WINDOW=3. Five channels per sample,
        # then five second moments, five RMS outputs and two branch records.
        budget.spend(CognitiveWork(
            cycles=2, memory_items=5 * len(samples) + 12))
        second_moment = tuple(
            fsum(float(row[c]) ** 2 for row in samples) / len(samples)
            for c in range(5))
        if any(not isfinite(x) or not 0.0 <= x <= 10000.0
               for x in second_moment):
            raise ValueError("invalid recent empirical second moment")
        scale = tuple(sqrt(x) for x in second_moment)
        if all(x <= 1e-15 for x in scale):
            outcomes = ()
            status = "NO_EMPIRICAL_SCALE"
        else:
            positive = tuple((omega + 1.0) * float(x) for x in scale)
            negative = tuple((omega - 1.0) * float(x) for x in scale)
            outcomes = (
                PlanSubjectiveOutcome(.5, SIGNAL, positive),
                PlanSubjectiveOutcome(.5, SIGNAL, negative),
            )
            status = "COMPLETE_TWO_BRANCH_RMS_ZERO_MEAN_PRIOR"

    if outcomes:
        expected = tuple(
            fsum(out.probability * out.probe_delta[c] for out in outcomes)
            for c in range(5))
        branch_second_moment = tuple(
            fsum(
                out.probability * (out.probe_delta[c] ** 2)
                for out in outcomes)
            for c in range(5))
        if any(abs(x - omega * s_c) > 1e-12 for x, s_c in zip(expected, scale)):
            raise RuntimeError("RMS uncertainty prior mean differs from omega * s")
        if any(abs(a - (1.0 + omega * omega) * b) > 1e-10
               for a, b in zip(branch_second_moment, second_moment)):
            raise RuntimeError(
                "RMS uncertainty prior failed second-moment preservation")
    else:
        expected = (0.0,) * 5
        branch_second_moment = (0.0,) * 5

    result = {
        "schema": SCHEMA,
        "status": status,
        "outcomes": outcomes,
        "support_records": len(samples),
        "rms_scale": tuple(scale),
        "recent_raw_second_moment": tuple(second_moment),
        "branch_second_moment": tuple(branch_second_moment),
        "expected_external_delta": tuple(expected),
        "source": "RECENT_ACTION_AGNOSTIC_PERSONAL_BRANCH_MEMORY_SCALE_ONLY",
        "mean_transfer": False,
        "innate_mean_shift_omega": omega,
        "action_identity_used": False,
        "token_identity_used": False,
        "body_need_used": False,
        "world_access": False,
        "branch_count": len(outcomes),
        "work": _work_delta(budget.work, start),
        "work_breakdown": {
            "memory_read": _work_delta(after_read, start),
            "scale_construction": _work_delta(budget.work, after_read),
            "total": _work_delta(budget.work, start),
        },
        "cost_is_physical_settlement_receipt": False,
    }
    if work_receipt is not None:
        work_receipt.clear()
        work_receipt.update({
            "schema": "i3-recent-rms-zero-mean-effect-prior-work/v1",
            "status": status,
            "support_records": len(samples),
            "branches": len(outcomes),
            "work": dict(result["work"]),
        })
    return result


__all__ = [
    "SCHEMA", "SIGNAL", "paid_recent_rms_zero_mean_effect_prior",
    "recent_rms_effect_prior_work_ceiling",
]
