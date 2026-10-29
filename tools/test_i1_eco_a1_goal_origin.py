"""A1 read-only goal-origin reconciliation, including adverse M11 claims.

No individual birth, no full I1 CI, and no cohort rerun.
"""
from copy import deepcopy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i1_eco_a1_decision_join import verify_decision_alignment

GOAL_OPTION = "option:i1:affordance:goal:restore_integrity:t1:attendre:here"
SIGNATURE = "i1:affordance:attendre:here"


def events():
    return [
        {"kind": "i1_unknown_affordance_proposed", "t_monde": 1, "cycle": 1,
         "data": {"option_ref": GOAL_OPTION,
                  "command": {"primitive": "attendre", "parameters": {}},
                  "learned_value_status": "unlearned",
                  "learned_value": None}},
        {"kind": "stage8_option_evaluation", "t_monde": 1, "cycle": 2,
         "data": {"option_ref": GOAL_OPTION,
                  "learning_signature": SIGNATURE,
                  "learned_value_status": "unlearned",
                  "learned_value": None}},
        {"kind": "competition_cycle", "t_monde": 1, "cycle": 2,
         "data": {"traces": [{"option_ref": GOAL_OPTION}]}},
        {"kind": "command_admitted", "t_monde": 1,
         "data": {"option_ref": GOAL_OPTION, "primitive": "attendre",
                  "command_hash": "fixed-command-hash"}},
        {"kind": "command_experienced", "t_monde": 1,
         "primitive": "attendre", "command_hash": "fixed-command-hash"},
    ]


READ = {
    "source": "planning_goal", "step": 1, "cycle": 1,
    "option_ref": None, "signature": SIGNATURE,
    "original_status": "unlearned", "original_value": None,
    "original_evidence": None, "update_count": 0, "masked": False,
}
ADAPTER = {
    "source": "stage8_pending_adapter", "step": 1, "cycle": 2,
    "option_ref": GOAL_OPTION, "signature": SIGNATURE,
    "delivered_status": "unlearned", "masked": False,
}


def verify(es, read=READ, adapter=ADAPTER):
    return verify_decision_alignment(
        events=es, reads=[read], adapters=[adapter],
        mode="canonical", generation=1)


def must_reject(es, read=READ, adapter=ADAPTER):
    try:
        verify(es, read=read, adapter=adapter)
    except ValueError:
        return
    raise AssertionError("A1 accepted a counterfeit or future M11 goal origin")


def main():
    result = verify(events())
    assert result["planning_winners_joined"] == 1
    assert result["pending_adapters_joined"] == 1
    assert result["stage8_direct_joined"] == 0
    assert result["scope"] == (
        "M11_ANCHORED_EXTERNAL_OBSERVER_NOT_INDEPENDENT_CAUSAL_GO")
    future = deepcopy(events())
    future[0]["cycle"] = 3
    must_reject(future)
    absent = deepcopy(events())
    absent[0]["data"]["option_ref"] = "foreign-option"
    must_reject(absent)
    false_command = deepcopy(events())
    false_command[0]["data"]["command"]["primitive"] = "dormir"
    must_reject(false_command)
    false_signature = dict(ADAPTER, signature="i1:affordance:dormir:here")
    must_reject(events(), adapter=false_signature)
    false_read = dict(READ, signature="i1:affordance:dormir:here")
    must_reject(events(), read=false_read)
    print("A1 goal-origin positive and five negative contracts: PASS")


if __name__ == "__main__":
    main()
