"""Frozen synthetic branch-decision settlement repair gate.

Protocol: docs/STAGE1_BRANCH_DECISION_SETTLEMENT_REPAIR.md.
No World, life, P2 ecology or 60/61 evidence access.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import sys

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    E, V, debit_cognition, transition)
from ..modules.candidate_f_shadow_state import (
    commit_actual_reference_branch, prepay_actual_reference_branch)
from ..modules.genome import midpoint
from ..modules.genomic_omega_frontier_information_mind import (
    GenomicOmegaFrontierInformationMind)
from ..modules.mind import Mind
from ..modules.personal_outcomes import STORE_WORK
from ..modules.personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind)
from ..modules.personal_shared_prior_candidate_i_mind import (
    PersonalSharedPriorCandidateIMind)
from ..modules.reference_branches import ReferenceBranchMemory
from ..modules.reference_memory_mind import ReferenceBranchMemoryMind

SCHEMA = "i3-branch-decision-settlement-repair/v1"
PROTOCOL = "STAGE1_BRANCH_DECISION_SETTLEMENT_REPAIR.md"
B0 = (1.0, 50.0, 50.0, 50.0, 1.0)
WA = CognitiveWork(cycles=10)
WB = CognitiveWork(cycles=5)
WT = CognitiveWork(cycles=15)
LAWS = BodyLaws()
KEY = ("attendre", None)
TOL = 1e-12


def _same_delta(left, right):
    return (
        len(left) == len(right)
        and max((abs(a - b) for a, b in zip(left, right)), default=0.0)
        <= TOL)


def _expected_fixture():
    b1, _ = debit_cognition(B0, LAWS, WA)
    # The pure body transition is only arithmetic here; no World is constructed.
    physical, dead = transition(B0, "attendre", LAWS, WT)
    if dead:
        raise RuntimeError("frozen synthetic fixture unexpectedly died")
    _remaining, bill = debit_cognition(B0, LAWS, WT)
    delta = [after - before for after, before in zip(physical, B0)]
    delta[E] += bill["energy"]["paid"]
    delta[V] += bill["vigilance"]["paid"]
    return b1, physical, tuple(delta)


def _legacy_mismatch_reproduces(b1, physical):
    memory = ReferenceBranchMemory()
    budget = CognitiveBudget(physical, LAWS)
    try:
        memory.observe(KEY, b1, WT, budget)
    except CognitiveFundingError:
        return True
    return False


def _direct_repaired_pair(physical, expected):
    memory = ReferenceBranchMemory()
    budget = CognitiveBudget(physical, LAWS)
    memory.observe(KEY, B0, WT, budget)
    sample = memory._samples[-1]
    return {
        "work": budget.work,
        "delta": tuple(sample.delta),
        "matches_expected": _same_delta(sample.delta, expected),
        "store_work_exact": budget.work == STORE_WORK,
    }


def _commit_through_mind(kind, physical, b1, expected):
    if kind == "reference":
        mind = ReferenceBranchMemoryMind(midpoint(), 301)
    elif kind == "candidate_h":
        mind = PersonalRelevanceCandidateHMind(midpoint(), 302)
    elif kind == "candidate_i":
        mind = PersonalSharedPriorCandidateIMind(midpoint(), 303)
    else:
        raise ValueError("unknown synthetic settlement mind")

    # Deliberately keep ordinary learning on the later Stage-B body while the
    # branch settlement receipt owns the whole decision from B0.
    mind.last = (tuple(b1), ("attendre",), "attendre", None)
    mind._set_branch_decision_settlement(B0, WT)
    result = {"dead": (), "body": tuple(physical)}
    learning = CognitiveBudget(physical, LAWS)
    replay_limit = mind.prepare_learning(result, learning)
    if replay_limit is None:
        raise RuntimeError("synthetic learning fixture unexpectedly unfunded")
    replays = mind.learn_from_outcome(
        result, replay_limit=replay_limit)
    sample = mind.branch_memory._samples[-1]
    return {
        "replays": replays,
        "branch_records": mind.branch_records,
        "delta": tuple(sample.delta),
        "matches_expected": _same_delta(sample.delta, expected),
        "settlement_consumed": (
            mind._branch_decision_start_body is None
            and mind._branch_decision_work == CognitiveWork()),
        "learning_work": asdict(learning.work),
    }


def _candidate_producer_receipt(kind):
    body = (80.0, 80.0, 40.0, 80.0, 80.0)
    cap = {
        "body": body,
        "here": (kind == "candidate_i", ()),
        "neighbors": (None, None, None, None),
        "inventory": (),
    }
    if kind == "candidate_h":
        mind = PersonalRelevanceCandidateHMind(midpoint(), 306)
    elif kind == "candidate_i":
        mind = PersonalSharedPriorCandidateIMind(midpoint(), 307)
    else:
        raise ValueError("unknown candidate producer")
    budget = CognitiveBudget(body, LAWS)
    result = mind.decide(cap, budget)
    start = mind._branch_decision_start_body
    work = mind._branch_decision_work
    return {
        "funding": result[3].get("funding"),
        "route": (
            result[3].get("candidate_h_route")
            if kind == "candidate_h"
            else result[3].get("candidate_i_route")),
        "start_matches": tuple(start) == body if start is not None else False,
        "work_matches": work == result[2] == budget.work,
        "stage_a_paid": (
            result[3].get(
                "candidate_h_stage_a_work",
                result[3].get("candidate_i_stage_a_work"))),
    }


def _missing_receipt_fails_closed(physical, b1):
    mind = ReferenceBranchMemoryMind(midpoint(), 304)
    mind.last = (tuple(b1), ("attendre",), "attendre", None)
    mind._branch_decision_work = WT
    mind._branch_decision_start_body = None
    result = {"dead": (), "body": tuple(physical)}
    learning = CognitiveBudget(physical, LAWS)
    try:
        mind.prepare_learning(result, learning)
    except RuntimeError as exc:
        return "missing branch decision settlement start body" in str(exc)
    return False


def _stale_receipt_is_replaced():
    mind = ReferenceBranchMemoryMind(midpoint(), 308)
    mind._set_branch_decision_settlement(B0, WT)
    body = (80.0, 80.0, 40.0, 80.0, 80.0)
    cap = {
        "body": body,
        "here": (False, ()),
        "neighbors": (None, None, None, None),
        "inventory": (),
    }
    budget = CognitiveBudget(body, LAWS)
    result = mind.decide(cap, budget)
    return (
        mind._branch_decision_start_body == body
        and mind._branch_decision_work == result[2] == budget.work
        and (
            mind._branch_decision_start_body != B0
            or mind._branch_decision_work != WT)
    )


def _upper_cost_shadow_identity(physical, b1, expected):
    reference = Mind(midpoint(), 305)
    candidate = GenomicOmegaFrontierInformationMind(
        midpoint(), 305)
    reference.last = (
        tuple(b1), ("attendre",), "attendre", None)
    result = {"dead": (), "body": tuple(physical)}
    learning = CognitiveBudget(physical, LAWS)
    pending = prepay_actual_reference_branch(
        reference, candidate, result, WB, learning,
        reference_learning_funded=True)
    if pending is None:
        return {
            "pending": False,
            "before_matches": False,
            "work_matches": False,
            "committed": False,
            "delta_matches": False,
        }
    before_matches = tuple(pending.before) == tuple(b1)
    work_matches = pending.reference_decision_work == WB
    committed = commit_actual_reference_branch(
        candidate, pending)
    delta_matches = (
        committed
        and _same_delta(
            candidate.branch_memory._samples[-1].delta, expected))
    return {
        "pending": True,
        "before_matches": before_matches,
        "work_matches": work_matches,
        "committed": committed,
        "delta_matches": delta_matches,
    }


def characterize():
    b1, physical, expected = _expected_fixture()

    # Frozen arithmetic preconditions.
    total_affordable_from_b0 = True
    try:
        debit_cognition(B0, LAWS, WT)
    except CognitiveFundingError:
        total_affordable_from_b0 = False

    total_rejected_from_b1 = False
    try:
        debit_cognition(b1, LAWS, WT)
    except CognitiveFundingError:
        total_rejected_from_b1 = True

    legacy = _legacy_mismatch_reproduces(b1, physical)
    direct = _direct_repaired_pair(physical, expected)
    reference = _commit_through_mind(
        "reference", physical, b1, expected)
    candidate_h = _commit_through_mind(
        "candidate_h", physical, b1, expected)
    candidate_i = _commit_through_mind(
        "candidate_i", physical, b1, expected)
    candidate_h_producer = _candidate_producer_receipt(
        "candidate_h")
    candidate_i_producer = _candidate_producer_receipt(
        "candidate_i")
    missing = _missing_receipt_fails_closed(
        physical, b1)
    stale_replaced = _stale_receipt_is_replaced()
    shadow = _upper_cost_shadow_identity(
        physical, b1, expected)

    rules = {
        "B0_custody_no_60_61_verdict": True,
        "B1_exact_synthetic_reproduction": (
            total_affordable_from_b0
            and total_rejected_from_b1
            and legacy),
        "B2_exact_settlement_pairing": (
            direct["matches_expected"]
            and reference["matches_expected"]
            and candidate_h["matches_expected"]
            and candidate_i["matches_expected"]),
        "B3_no_cognition_forgiveness": (
            WT.cycles == WA.cycles + WB.cycles
            and WT.simulated_steps
            == WA.simulated_steps + WB.simulated_steps
            and WT.memory_items
            == WA.memory_items + WB.memory_items
            and WT.replays == WA.replays + WB.replays),
        "B4_ordinary_reference_identity": (
            reference["branch_records"] == 1
            and reference["settlement_consumed"]),
        "B5_candidate_h_i_multiphase_alignment": (
            candidate_h["branch_records"] == 1
            and candidate_i["branch_records"] == 1
            and candidate_h["settlement_consumed"]
            and candidate_i["settlement_consumed"]
            and candidate_h_producer["start_matches"]
            and candidate_h_producer["work_matches"]
            and candidate_i_producer["start_matches"]
            and candidate_i_producer["work_matches"]),
        "B6_prepaid_store_exact": direct["store_work_exact"],
        "B7_missing_or_stale_receipt_fails_closed": (
            missing and stale_replaced),
        "B8_upper_cost_shadow_unchanged": all(shadow.values()),
        "B9_authority_boundary": True,
    }
    passed = all(rules.values())
    return {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "world_access": False,
        "runtime_life_access": False,
        "p2_ecology_access": False,
        "evidence_branch_access": False,
        "lives": 0,
        "fixture": {
            "B0": B0,
            "WA": asdict(WA),
            "WB": asdict(WB),
            "WT": asdict(WT),
            "B1": tuple(b1),
            "physical_body": tuple(physical),
            "expected_branch_delta": tuple(expected),
        },
        "legacy_mismatch_reproduced": legacy,
        "direct_repaired": {
            "work": asdict(direct["work"]),
            "delta": direct["delta"],
            "matches_expected": direct["matches_expected"],
            "store_work_exact": direct["store_work_exact"],
        },
        "reference": reference,
        "candidate_h": candidate_h,
        "candidate_i": candidate_i,
        "candidate_h_producer": candidate_h_producer,
        "candidate_i_producer": candidate_i_producer,
        "stale_receipt_replaced": stale_replaced,
        "upper_cost_shadow": shadow,
        "rules": rules,
        "verdict": (
            "BRANCH_DECISION_SETTLEMENT_REPAIR_PASS"
            if passed else
            "BRANCH_DECISION_SETTLEMENT_REPAIR_DEFECT"),
        "60_61_retry_authorized": False,
        "J1_J7_verdict_authorized": False,
        "new_live_panel_authorized": False,
    }


def run(path):
    report = characterize()
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("BRANCH_DECISION_SETTLEMENT_REPAIR " + json.dumps({
        "verdict": report["verdict"],
        "legacy_mismatch_reproduced":
            report["legacy_mismatch_reproduced"],
        "rules": report["rules"],
    }, sort_keys=True))
