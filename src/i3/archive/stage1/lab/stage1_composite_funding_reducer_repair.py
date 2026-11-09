"""Frozen synthetic gate for Candidate-H composite funding reduction.

Protocol: docs/STAGE1_COMPOSITE_FUNDING_REDUCER_REPAIR.md.
No World, life runner or exposed evidence is accessed.
"""
from __future__ import annotations

from copy import deepcopy
import json
import sys

from i3.lab import stage0_revision as revision

SCHEMA = "i3-stage1-composite-funding-reducer-repair/v1"
WORK = {"cycles": 3, "simulated_steps": 0, "memory_items": 0, "replays": 0}
ZERO = {"cycles": 0, "simulated_steps": 0, "memory_items": 0, "replays": 0}


def _bill():
    return {
        channel: {"requested": 0.0, "paid": 0.0, "unpaid": 0.0}
        for channel in ("energy", "vigilance")
    }


def _life():
    before = [80.0, 70.0, 40.0, 90.0, 100.0]
    physical = [79.0, 69.8, 39.6, 90.0, 99.0]
    phases = {
        phase: {
            "work": dict(WORK),
            "accounting": _bill(),
            "body_before": before[:] if phase == "decision" else physical[:],
            "body_after_debit": physical[:],
        }
        for phase in ("decision", "learning")
    }
    row = {
        "t": 1,
        "action": "attendre",
        "param": None,
        "option": "attendre",
        "body": physical[:],
        "pos": [5, 6],
        "dead": [],
        "funding_phases": phases,
        "info": {
            "funding": "FUNDED",
            "observer": {"decision_outcome": "action_admitted"},
        },
    }
    event = {
        "step": 1,
        "action": "attendre",
        "param": None,
        "chosen_option": "attendre",
        "death_causes": [],
        "world_position_observer_only": [5, 6],
        "personal_position": [0, 0],
        "body_before_decision": before[:],
        "body_after_physics": physical[:],
        "body_after_paid_learning": physical[:],
        "decision_funding": "FUNDED",
        "decision_outcome": "action_admitted",
        "capture_here_water": False,
        "positive_water_uptake": False,
        "water_uptake_above_decay": None,
        "phase_payment": {
            phase: {
                "work": dict(WORK),
                "accounting": _bill(),
            }
            for phase in ("decision", "learning")
        },
        "paid_decision_work": dict(WORK),
        "paid_learning_work": dict(WORK),
    }
    return {
        "manifest": {
            "world": {
                "spawn": [5, 6],
                "laws": {"water_decay": 0.4},
            }
        },
        "trace": [row],
        "observer_resource_acquisition": {
            "schema": "i3-p5d-resource-acquisition-observer/v1",
            "steps": [event],
        },
    }


def _set_decision(life, *, public, outcome, work, nested=None, action=None):
    row = life["trace"][0]
    event = life["observer_resource_acquisition"]["steps"][0]
    row["action"] = action
    row["param"] = None
    row["option"] = None if action is None else action
    row["info"]["funding"] = public
    row["info"]["observer"]["decision_outcome"] = outcome
    if nested is None:
        row["info"].pop("candidate_h_probe_funding", None)
    else:
        row["info"]["candidate_h_probe_funding"] = nested
    row["funding_phases"]["decision"]["work"] = dict(work)
    event["action"] = action
    event["param"] = None
    event["chosen_option"] = row["option"]
    event["decision_funding"] = public
    event["decision_outcome"] = outcome
    event["paid_decision_work"] = dict(work)
    event["phase_payment"]["decision"]["work"] = dict(work)
    return life


def _legacy_rejects(life):
    """Exact old status predicate, before the repair."""
    row = life["trace"][0]
    event = life["observer_resource_acquisition"]["steps"][0]
    funding = event["decision_funding"]
    if funding not in revision.FUNDING:
        return True
    return (
        row["info"]["funding"] != funding
        or event["decision_outcome"] != revision.FUNDING[funding]
        or row["info"]["observer"]["decision_outcome"]
        != revision.FUNDING[funding]
    )


def _accepts(life):
    try:
        joined = revision._resource_events(life)
    except ValueError:
        return False, None
    return True, joined


def _rejects(life):
    try:
        revision._resource_events(life)
    except ValueError:
        return True
    return False


def characterize():
    funded = _life()
    funded_ok, funded_joined = _accepts(funded)

    no_processing = _set_decision(
        _life(),
        public="NO_PROCESSING_BUDGET",
        outcome="no_processing_budget",
        work=ZERO,
        action=None,
    )
    no_processing_ok, no_processing_joined = _accepts(no_processing)

    composite_no_processing = _set_decision(
        _life(),
        public="NO_FUNDED_RELEVANCE_PROBE",
        nested="NO_PROCESSING_BUDGET",
        outcome="no_processing_budget",
        work=ZERO,
        action=None,
    )
    composite_no_score = _set_decision(
        _life(),
        public="NO_FUNDED_RELEVANCE_PROBE",
        nested="NO_FUNDED_SCORE",
        outcome="no_funded_score",
        work=WORK,
        action=None,
    )
    cnp_ok, cnp_joined = _accepts(composite_no_processing)
    cns_ok, cns_joined = _accepts(composite_no_score)

    invalid = {}

    x = _set_decision(
        _life(),
        public="NO_FUNDED_RELEVANCE_PROBE",
        outcome="no_funded_score",
        work=WORK,
        action=None,
    )
    invalid["missing_nested"] = _rejects(x)

    for nested in ("FUNDED", "NO_FUNDED_MOTOR"):
        x = _set_decision(
            _life(),
            public="NO_FUNDED_RELEVANCE_PROBE",
            nested=nested,
            outcome=revision.FUNDING[nested],
            work=WORK,
            action=None,
        )
        invalid["illegal_nested_" + nested] = _rejects(x)

    x = _set_decision(
        _life(),
        public="NO_FUNDED_OTHER_PHASE",
        nested="NO_FUNDED_SCORE",
        outcome="no_funded_score",
        work=WORK,
        action=None,
    )
    invalid["unknown_public_status"] = _rejects(x)

    x = _set_decision(
        _life(),
        public="NO_FUNDED_RELEVANCE_PROBE",
        nested="NO_FUNDED_SCORE",
        outcome="no_processing_budget",
        work=WORK,
        action=None,
    )
    invalid["outcome_disagreement"] = _rejects(x)

    x = _set_decision(
        _life(),
        public="NO_FUNDED_RELEVANCE_PROBE",
        nested="NO_FUNDED_SCORE",
        outcome="no_funded_score",
        work=WORK,
        action=None,
    )
    x["observer_resource_acquisition"]["steps"][0][
        "decision_funding"] = "NO_FUNDED_SCORE"
    invalid["sidecar_trace_public_disagreement"] = _rejects(x)

    x = _set_decision(
        _life(),
        public="NO_FUNDED_RELEVANCE_PROBE",
        nested="NO_PROCESSING_BUDGET",
        outcome="no_processing_budget",
        work=WORK,
        action=None,
    )
    invalid["unpaid_with_work"] = _rejects(x)

    x = _set_decision(
        _life(),
        public="NO_FUNDED_RELEVANCE_PROBE",
        nested="NO_FUNDED_SCORE",
        outcome="no_funded_score",
        work=ZERO,
        action=None,
    )
    invalid["paid_without_base_block"] = _rejects(x)

    x = _set_decision(
        _life(),
        public="NO_FUNDED_RELEVANCE_PROBE",
        nested="NO_FUNDED_SCORE",
        outcome="no_funded_score",
        work=WORK,
        action="attendre",
    )
    invalid["composite_admits_motor"] = _rejects(x)

    custody = _life()
    custody["observer_resource_acquisition"]["steps"][0]["action"] = "dormir"
    invalid["custody_action_disagreement"] = _rejects(custody)

    legacy = {
        "composite_no_processing_rejected":
            _legacy_rejects(composite_no_processing),
        "composite_no_score_rejected":
            _legacy_rejects(composite_no_score),
    }

    rules = {
        "R0_historical_behavior_unchanged":
            funded_ok and no_processing_ok
            and funded_joined[0]["processing_paid"]
            and not no_processing_joined[0]["processing_paid"],
        "R1_exact_synthetic_reproduction":
            all(legacy.values()),
        "R2_narrow_normalization":
            cnp_ok and cns_ok,
        "R3_processing_paid_semantics":
            (not cnp_joined[0]["processing_paid"]
             and cns_joined[0]["processing_paid"]
             and cnp_joined[0]["positive_drink"] is False
             and cns_joined[0]["positive_drink"] is False),
        "R4_fail_closed":
            all(invalid.values()),
        "R5_custody_joins_unchanged":
            invalid["custody_action_disagreement"],
        "R6_authority_boundary": True,
    }
    passed = all(rules.values())
    return {
        "schema": SCHEMA,
        "protocol": "STAGE1_COMPOSITE_FUNDING_REDUCER_REPAIR.md",
        "world_access": False,
        "lives": 0,
        "evidence_branch_access": False,
        "legacy_reproduction": legacy,
        "accepted": {
            "historical_funded": funded_ok,
            "historical_no_processing": no_processing_ok,
            "composite_no_processing": cnp_ok,
            "composite_no_funded_score": cns_ok,
        },
        "invalid_rejections": invalid,
        "rules": rules,
        "verdict": (
            "COMPOSITE_FUNDING_REDUCER_REPAIR_PASS"
            if passed else
            "COMPOSITE_FUNDING_REDUCER_REPAIR_DEFECT"
        ),
        "retroactive_58_59_completion_authorized": False,
        "new_live_panel_authorized": False,
    }


def run(out_path):
    report = characterize()
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("COMPOSITE_FUNDING_REDUCER_REPAIR " + json.dumps({
        "verdict": report["verdict"],
        "rules": report["rules"],
        "legacy_reproduction": report["legacy_reproduction"],
        "invalid_rejections": report["invalid_rejections"],
    }, sort_keys=True))
