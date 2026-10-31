"""Counterbalanced synthetic UC-allocation study, NEVER an I2 action policy.

This module compares theoretical exposure under equal per-capture UC ceilings.
No I2 birth, authentic Scheduler debit, M11 proof, or motor admission exists.
The allocator deliberately receives NO candidate values; hidden complete values
are used only after selection to audit missed opportunities offline.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import json
from pathlib import Path
from typing import Mapping

from .competition_preview import MAX_CANDIDATES, MAX_VALUE_MAGNITUDE, _frame
from .intention_continuity import FirstPersonCapture, IntentionContinuity, _ref
from .intention_ingress import ObservationClaim
from .option_reconstruction import CandidateFrame, reconstruct_candidates

SCHEMA = "i2-synthetic-uc-allocation-comparison-v1"
POLICIES = ("full_frame", "fixed_prefix_control", "rotating_quota")
PROFILES = ("ascending", "descending", "tie_positive", "all_zero", "single_adverse")
BASELINE_SHA = "bd4b447423a82bb05300171d22677fffa3464465"


@dataclass(frozen=True, slots=True)
class AllocationPlan:
    """Offline sampling schedule, neither paid receipt nor a motor option."""

    policy: str
    life_ref: str
    frame_ref: str
    capture_ref: str
    all_candidate_refs: tuple[str, ...]
    selected_candidate_refs: tuple[str, ...]
    uc_ceiling: int
    uc_scheduled: int
    phase: int
    status: str
    motor_authority: str = "NONE"


@dataclass(frozen=True, slots=True)
class DiagnosticAdvice:
    """No option admission. Partial top values are explicitly unverified."""

    frame_ref: str
    status: str
    suggested_candidate_ref: str | None
    sampled_refs: tuple[str, ...]
    motor_authority: str = "NONE"


@dataclass(frozen=True, slots=True)
class HoldoutAudit:
    """Retrospective ONLY: inaccessible full-information comparator."""

    frame_ref: str
    unique_positive_oracle_ref: str | None
    matched_unique_oracle: bool | None
    withheld_oracle: bool | None
    suggested_ref: str | None
    motor_authority: str = "NONE"


def _selection(names: tuple[str, ...], policy: str, ceiling: int,
               phase: int) -> tuple[tuple[str, ...], str]:
    """Canonical deterministic sampling rule. Never inspects candidate scores."""
    n = len(names)
    capacity = min(ceiling, n)
    if policy == "full_frame":
        chosen = names if capacity == n else ()
    elif policy == "fixed_prefix_control":
        # Deliberately biased negative control, not a recommended policy.
        chosen = names[:capacity]
    else:
        # No motor evidence or scores carry forward across physical captures.
        # The phase is supplied by this study, not by a living I2 clock.
        start = (phase * capacity) % n if n else 0
        indices = {(start + i) % n for i in range(capacity)}
        chosen = tuple(name for i, name in enumerate(names) if i in indices)
    if not names:
        status = "NO_CANDIDATES"
    elif not chosen:
        status = "UNFUNDED"
    elif len(chosen) == n:
        status = "COMPLETE_DIAGNOSTIC"
    else:
        status = "PARTIAL_DIAGNOSTIC"
    return chosen, status


def _valid_parameters(policy: object, ceiling: object, phase: object) -> None:
    if type(policy) is not str or policy not in POLICIES:
        raise ValueError("unknown non-motor study policy")
    if type(ceiling) is not int or not 0 <= ceiling <= MAX_CANDIDATES:
        raise ValueError("UC ceiling must be a bounded integer")
    if type(phase) is not int or phase < 0:
        raise ValueError("nonnegative synthetic phase required")


def plan_without_values(frame: CandidateFrame, *, policy: str,
                        uc_ceiling: int, phase: int) -> AllocationPlan:
    """Select which candidates may be *sampled* using no value information.

    `phase` is an externally defined synthetic index, NOT an I2 life clock
    or an ability to carry Competition evidence across steps.
    """
    _frame(frame)  # shape check only; no M11 authentication
    _valid_parameters(policy, uc_ceiling, phase)
    names = tuple(x.candidate_ref for x in frame.candidates)
    chosen, status = _selection(names, policy, uc_ceiling, phase)
    return AllocationPlan(policy, frame.life_ref, frame.frame_ref,
                          frame.capture_ref, names, chosen,
                          uc_ceiling, len(chosen), phase, status)


def _checked_plan(plan: AllocationPlan) -> None:
    if type(plan) is not AllocationPlan or plan.motor_authority != "NONE":
        raise ValueError("invalid non-motor study plan")
    for field in ("life_ref", "frame_ref", "capture_ref"):
        _ref(getattr(plan, field), field)
    _valid_parameters(plan.policy, plan.uc_ceiling, plan.phase)
    if (type(plan.all_candidate_refs) is not tuple or
            type(plan.selected_candidate_refs) is not tuple or
            len(plan.all_candidate_refs) > MAX_CANDIDATES or
            len(set(plan.all_candidate_refs)) != len(plan.all_candidate_refs)):
        raise ValueError("noncanonical candidate list")
    for ref in plan.all_candidate_refs:
        _ref(ref, "candidate ref")
        if not ref.startswith("candidate:i2:"):
            raise ValueError("foreign candidate reference")
    expected_selected, expected_status = _selection(
        plan.all_candidate_refs, plan.policy, plan.uc_ceiling, plan.phase)
    if (plan.selected_candidate_refs != expected_selected or
            plan.status != expected_status or
            type(plan.uc_scheduled) is not int or
            plan.uc_scheduled != len(expected_selected)):
        raise ValueError("altered policy selection, status or UC schedule")


def advise_on_sample_only(plan: AllocationPlan,
                          observed_values: Mapping[str, int]) -> DiagnosticAdvice:
    """Only the selected subset is passed. All unseen scores stay unknown."""
    _checked_plan(plan)
    if type(observed_values) is not dict or set(observed_values) != set(plan.selected_candidate_refs):
        raise ValueError("value oracle leak or missing sampled evidence")
    if any(type(value) is not int or abs(value) > MAX_VALUE_MAGNITUDE
           for value in observed_values.values()):
        raise ValueError("unbounded or malformed synthetic value")
    if not plan.selected_candidate_refs:
        status, chosen = plan.status, None
    else:
        top = max(observed_values.values())
        best = [ref for ref, score in observed_values.items() if score == top]
        if top <= 0:
            status, chosen = "NO_POSITIVE_EVIDENCE", None
        elif len(best) > 1:
            status, chosen = "AMBIGUOUS", None
        elif plan.status == "PARTIAL_DIAGNOSTIC":
            status, chosen = "PARTIAL_UNVERIFIED", best[0]
        else:
            status, chosen = "ADVISORY_ONLY", best[0]
    return DiagnosticAdvice(plan.frame_ref, status, chosen,
                            plan.selected_candidate_refs)


def audit_heldout_after_choice(plan: AllocationPlan, advice: DiagnosticAdvice,
                               all_values: Mapping[str, int]) -> HoldoutAudit:
    """Held-out oracle is for scoring only; NEVER supplied to allocation."""
    _checked_plan(plan)
    if (type(advice) is not DiagnosticAdvice or advice.motor_authority != "NONE" or
            advice.frame_ref != plan.frame_ref or advice.sampled_refs != plan.selected_candidate_refs):
        raise ValueError("advice does not belong to allocation")
    if type(all_values) is not dict or set(all_values) != set(plan.all_candidate_refs):
        raise ValueError("complete synthetic holdout required")
    if any(type(value) is not int or abs(value) > MAX_VALUE_MAGNITUDE
           for value in all_values.values()):
        raise ValueError("malformed holdout score")
    oracle = None
    if all_values:
        top = max(all_values.values())
        refs = [ref for ref, v in all_values.items() if v == top]
        if top > 0 and len(refs) == 1:
            oracle = refs[0]
    return HoldoutAudit(
        plan.frame_ref, oracle,
        (advice.suggested_candidate_ref == oracle) if oracle is not None else None,
        (oracle not in plan.selected_candidate_refs) if oracle is not None else None,
        advice.suggested_candidate_ref,
    )


def synthetic_frame(step: int, count: int) -> CandidateFrame:
    """No world or agent. Identical candidate semantics in new synthetic captures."""
    if type(step) is not int or step < 0 or type(count) is not int or not 1 <= count <= 9:
        raise ValueError("invalid synthetic frame settings")
    sem = tuple(f"neutral:option:{i:02d}" for i in range(count))
    capture = FirstPersonCapture(step, f"capture:synthetic:{step}",
                                 "goal:synthetic-neutral", sem)
    claim = ObservationClaim("life:synthetic-allocation", capture,
                             f"source:synthetic:{step}", ("evidence:synthetic",))
    owner = IntentionContinuity()
    transition = owner.observe(capture=capture, work_ref=f"work:synthetic:{step}")
    return reconstruct_candidates(claim=claim, transition=transition, current=None)


def synthetic_values(frame: CandidateFrame, profile: str) -> dict[str, int]:
    """Values available only to the synthetic test evaluator and oracle audit."""
    if profile not in PROFILES:
        raise ValueError("unknown predeclared synthetic profile")
    result: dict[str, int] = {}
    n = len(frame.candidates)
    for i, candidate in enumerate(frame.candidates):
        if profile == "ascending":
            value = i + 1
        elif profile == "descending":
            value = n - i
        elif profile == "tie_positive":
            value = 2
        elif profile == "all_zero":
            value = 0
        else:
            value = -4 if i == n - 1 else 1
        result[candidate.candidate_ref] = value
    return result


def run_comparison() -> dict[str, object]:
    """Fixed deterministic grid; paired frames/caps and values across policies.

    Study assumptions are frozen here, not tuned from observed outcomes.
    No birth, no world physics, no material I2 development claim.
    """
    records = []
    for n in (3, 5):
        for ceiling in (0, 1, 2, 3, 5):
            for profile in PROFILES:
                # Equal horizon within each (n, budget, profile) pair.
                horizon = 2 * n
                frames = [synthetic_frame(i + 1, n) for i in range(horizon)]
                for policy in POLICIES:
                    exposures: Counter[str] = Counter()
                    scheduled_uc = 0
                    full_advice = 0
                    partial_advice = 0
                    unfunded = 0
                    oracle_matches = 0
                    oracle_withheld = 0
                    oracle_opportunities = 0
                    for phase, frame in enumerate(frames):
                        plan = plan_without_values(frame, policy=policy,
                                                   uc_ceiling=ceiling, phase=phase)
                        holdout = synthetic_values(frame, profile)
                        # The allocation and advisory NEVER see unselected scores.
                        sampled = {ref: holdout[ref] for ref in plan.selected_candidate_refs}
                        advice = advise_on_sample_only(plan, sampled)
                        audit = audit_heldout_after_choice(plan, advice, holdout)
                        scheduled_uc += plan.uc_scheduled
                        full_advice += (advice.status == "ADVISORY_ONLY")
                        partial_advice += (advice.status == "PARTIAL_UNVERIFIED")
                        unfunded += (plan.status == "UNFUNDED")
                        oracle_opportunities += (audit.unique_positive_oracle_ref is not None)
                        oracle_matches += (audit.matched_unique_oracle is True)
                        oracle_withheld += (audit.withheld_oracle is True)
                        for ref in plan.selected_candidate_refs:
                            # Count by semantic *position* (not ephemeral ref).
                            index = plan.all_candidate_refs.index(ref)
                            exposures[index] += 1
                    exposure = [exposures.get(i, 0) for i in range(n)]
                    records.append({
                        "candidate_count": n, "uc_ceiling_each_step": ceiling,
                        "profile": profile, "policy": policy, "frames": horizon,
                        "uc_ceiling_total": ceiling * horizon,
                        "uc_scheduled": scheduled_uc,
                        "unfunded_frames": unfunded,
                        "full_advice_frames": full_advice,
                        "partial_diagnostic_frames": partial_advice,
                        "unique_positive_oracle_frames": oracle_opportunities,
                        "oracle_matches": oracle_matches,
                        "oracle_not_sampled_frames": oracle_withheld,
                        "per_semantic_exposure": exposure,
                        "exposure_gap": max(exposure) - min(exposure),
                    })
    return {
        "schema": SCHEMA,
        "status": "SYNTHETIC_ONLY_NOT_SCIENTIFIC_GO",
        "reference_main_sha": BASELINE_SHA,
        "policies": list(POLICIES),
        "profiles": list(PROFILES),
        "candidate_counts": [3, 5],
        "uc_ceilings": [0, 1, 2, 3, 5],
        "frames_per_scenario": "2*candidate_count",
        "paired_scenarios": 2 * 5 * len(PROFILES),
        "records": records,
        "prohibited_inference": "Synthetic oracle audit is not a cognitive input, learning, survival, motor admission or evidence of I2 superiority.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_comparison()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"I2_UC_ALLOCATION_SYNTHETIC_ONLY records={len(report['records'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
