"""Declared Candidate-G support-vs-decision-relevance diagnostic.

Protocol: docs/STAGE1_CANDIDATE_G_SUPPORT_VS_RELEVANCE.md.
Software only: no World, no life, no evidence-branch access.
"""
from __future__ import annotations

from collections import Counter
import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget
from . import stage1_candidate_g_no_omega_integration as I
from . import stage1_candidate_g_projection_dependence as D
from . import stage1_candidate_g_reference_recurrence_falsifier as G

SCHEMA = "i3-stage1-candidate-g-support-vs-relevance/v1"
ORDINARY_PLANS = {
    "wait": (("attendre",),),
    "sleep": (("dormir",),),
    "move": (("se_deplacer",),),
    "move_wait": (("se_deplacer",), ("attendre",)),
}
TOL = 1e-12


def _ordinary_scores(body, horizon, arm):
    values = {}
    work = {}
    for name, plan in ORDINARY_PLANS.items():
        if arm == "reference":
            mind = G.make_mind()
        elif arm == "candidate_f":
            mind = D.make_mind("candidate_f_projection")
        else:
            raise ValueError("unknown ordinary-score arm")
        budget = CognitiveBudget(body, BodyLaws())
        values[name] = mind.simulate(body, plan, horizon, budget)[0]
        work[name] = {
            "cycles": budget.work.cycles,
            "simulated_steps": budget.work.simulated_steps,
            "memory_items": budget.work.memory_items,
            "replays": budget.work.replays,
        }
    best = max(values.values())
    top = tuple(sorted(
        name for name, value in values.items()
        if value >= best - TOL))
    return values, work, top


def _max_pairwise_gap_shift(reference, candidate):
    names = sorted(ORDINARY_PLANS)
    best = 0.0
    pair = None
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            ref_gap = reference[left] - reference[right]
            cand_gap = candidate[left] - candidate[right]
            shift = abs(cand_gap - ref_gap)
            if shift > best:
                best = shift
                pair = (left, right)
    return best, pair


def _class_summary(rows):
    ref_members = Counter()
    cand_members = Counter()
    ref_unique = Counter()
    cand_unique = Counter()
    changed = []
    unique_changes = 0
    ref_steps = []
    cand_steps = []
    max_shift = 0.0
    max_shift_state = None

    for row in rows:
        for name in row["reference_top"]:
            ref_members[name] += 1
        for name in row["candidate_f_top"]:
            cand_members[name] += 1
        if len(row["reference_top"]) == 1:
            ref_unique[row["reference_top"][0]] += 1
        if len(row["candidate_f_top"]) == 1:
            cand_unique[row["candidate_f_top"][0]] += 1

        if row["top_changed"]:
            changed.append({
                "channel": row["channel"],
                "channel_index": row["channel_index"],
                "level": row["level"],
                "horizon": row["horizon"],
                "reference_top": row["reference_top"],
                "candidate_f_top": row["candidate_f_top"],
                "strict_epistemic_selected":
                    row["strict_epistemic_selected"],
                "pairwise_gap_shift": row["max_pairwise_gap_shift"],
            })
        if (len(row["reference_top"]) == 1
                and len(row["candidate_f_top"]) == 1
                and row["reference_top"] != row["candidate_f_top"]):
            unique_changes += 1

        ref_steps.append(sum(
            item["simulated_steps"]
            for item in row["reference_work"].values()))
        cand_steps.append(sum(
            item["simulated_steps"]
            for item in row["candidate_f_work"].values()))

        if row["max_pairwise_gap_shift"] > max_shift:
            max_shift = row["max_pairwise_gap_shift"]
            max_shift_state = {
                "channel": row["channel"],
                "channel_index": row["channel_index"],
                "level": row["level"],
                "horizon": row["horizon"],
                "pair": row["max_pairwise_gap_pair"],
                "shift": row["max_pairwise_gap_shift"],
            }

    return {
        "states": len(rows),
        "top_set_changes": len(changed),
        "unique_winner_changes": unique_changes,
        "reference_top_memberships": dict(sorted(ref_members.items())),
        "candidate_f_top_memberships": dict(sorted(cand_members.items())),
        "reference_unique_winners": dict(sorted(ref_unique.items())),
        "candidate_f_unique_winners": dict(sorted(cand_unique.items())),
        "max_pairwise_gap_shift": max_shift,
        "max_pairwise_gap_shift_state": max_shift_state,
        "mean_paid_simulated_steps_four_plans": {
            "reference": sum(ref_steps) / len(ref_steps) if ref_steps else 0.0,
            "candidate_f": (
                sum(cand_steps) / len(cand_steps) if cand_steps else 0.0),
        },
        "max_paid_simulated_steps_four_plans": {
            "reference": max(ref_steps) if ref_steps else 0,
            "candidate_f": max(cand_steps) if cand_steps else 0,
        },
        "changed_states": changed,
    }


def characterize():
    kernel_rows, kernel = I.evaluate_kernel()
    if len(kernel_rows) != 80:
        raise RuntimeError("canonical Candidate-G kernel grid changed")

    rows = []
    for kernel_row in kernel_rows:
        body = list(G.BASE_BODY)
        body[kernel_row["channel_index"]] = kernel_row["level"]
        body = tuple(body)
        horizon = kernel_row["horizon"]

        ref_values, ref_work, ref_top = _ordinary_scores(
            body, horizon, "reference")
        cand_values, cand_work, cand_top = _ordinary_scores(
            body, horizon, "candidate_f")
        shift, pair = _max_pairwise_gap_shift(
            ref_values, cand_values)
        strict = (
            "TRIAL" in kernel_row["target_choices"]
            and kernel_row["information_value"] > TOL
            and kernel_row["trial_advantage"] > TOL)

        rows.append({
            "channel": kernel_row["channel"],
            "channel_index": kernel_row["channel_index"],
            "level": kernel_row["level"],
            "horizon": horizon,
            "strict_epistemic_selected": strict,
            "kernel_target_choices": kernel_row["target_choices"],
            "kernel_information_value": kernel_row["information_value"],
            "kernel_trial_advantage": kernel_row["trial_advantage"],
            "reference_scores": ref_values,
            "candidate_f_scores": cand_values,
            "reference_top": ref_top,
            "candidate_f_top": cand_top,
            "top_changed": ref_top != cand_top,
            "max_pairwise_gap_shift": shift,
            "max_pairwise_gap_pair": pair,
            "reference_work": ref_work,
            "candidate_f_work": cand_work,
        })

    strict_rows = [
        row for row in rows if row["strict_epistemic_selected"]]
    support_only = [
        row for row in rows if not row["strict_epistemic_selected"]]

    strict_summary = _class_summary(strict_rows)
    support_summary = _class_summary(support_only)
    all_summary = _class_summary(rows)

    classification = (
        "SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_PRESENT"
        if support_summary["top_set_changes"] > 0
        else "NO_SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_ON_GRID")

    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_G_SUPPORT_VS_RELEVANCE.md",
        "world_access": False,
        "lives": 0,
        "evidence_branch_access": False,
        "omega_read": False,
        "support_present_in_all_states": True,
        "kernel": {
            "evaluated": kernel["evaluated"],
            "strict_epistemic_selected": len(strict_rows),
            "support_only_nonselected": len(support_only),
            "declined": kernel["declined"],
            "mean_simulated_steps": kernel["mean_work"]["simulated_steps"],
            "actual_work_ceiling_violations":
                kernel["actual_work_ceiling_violations"],
        },
        "ordinary_plan_set": tuple(sorted(ORDINARY_PLANS)),
        "all_states": all_summary,
        "strict_selected_states": strict_summary,
        "support_only_nonselected_states": support_summary,
        "classification": classification,
        "promotion_authorized": False,
        "candidate_h_implementation_authorized": False,
        "new_live_panel_authorized": False,
        "rows": rows,
    }


def run(out_path):
    report = characterize()
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("CANDIDATE_G_SUPPORT_VS_RELEVANCE " + json.dumps({
        "classification": report["classification"],
        "kernel": report["kernel"],
        "support_only_nonselected_states":
            report["support_only_nonselected_states"],
        "strict_selected_states": report["strict_selected_states"],
        "all_states": report["all_states"],
    }, sort_keys=True))
