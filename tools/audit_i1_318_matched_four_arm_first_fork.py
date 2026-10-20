#!/usr/bin/env python3
"""#318 first-fork read-only causal audit over 32 sealed matched-tau WALs.

Runs the independent whole-cohort original-WAL physical authenticator FIRST.
Never creates an actor, executes a command, replays, or writes source WAL.
A four-arm historical contrast is not a proof of ecological superiority.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _check
from audit_i1_318_matched_temperament_q_factorial import (
    ARMS, PRESETS, SEEDS, SOURCE_RUN, SOURCE_SHA, audit as audit_original,
)
from audit_i1_318_local_q_ablation_cohort import (
    physical_history, local_competition_at_fork,
)

SCHEMA = "i1-318-matched-Q-four-arm-first-fork/v1"
# Compare the *complete* first-person Stage3 receipt, including creature
# count and schema. A handpicked subset can hide an important difference.
REQUIRED_CAPTURE_FIELDS = (
    "capture_t_monde", "position", "adjacent_creature_count",
    "dual_scope_visible_body", "agency_visible_inventory",
    "agency_visible_adjacent",
)
EFFECT_FIELDS = ("body_after", "position_after", "effects")
Q_MODES = {
    "local_q_neutral": (False, False),
    "local_q_rank_only": (True, False),
    "local_q_evidence_only": (False, True),
    "local_q_learned": (True, True),
}
CONTRASTS = (
    ("neutral_to_rank", ARMS[0], ARMS[1]),
    ("neutral_to_evidence", ARMS[0], ARMS[2]),
    ("rank_to_both", ARMS[1], ARMS[3]),
    ("evidence_to_both", ARMS[2], ARMS[3]),
)


def first_fork(histories):
    """Return earliest different motor and prior-life physical concordance.

    'aligned' is only asserted for the *physical* fields in the original
    transition; comparing life IDs or per-life hash chains is inappropriate.
    """
    _check(set(histories) == set(ARMS), "incomplete 2x2 motor histories")
    max_step = min(len(histories[a][0]) for a in ARMS)
    fork = None
    first_physical_change = None
    for step in range(1, max_step + 1):
        motor_commands = [
            (histories[a][0][step]["primitive"],
             histories[a][0][step]["parameters"]) for a in ARMS
        ]
        if fork is None and any(m != motor_commands[0] for m in motor_commands[1:]):
            fork = step
        physiology = [
            tuple(json.dumps(histories[a][1][step].get(k),
                             sort_keys=True) for k in EFFECT_FIELDS)
            for a in ARMS
        ]
        if (first_physical_change is None
                and any(p != physiology[0] for p in physiology[1:])):
            first_physical_change = step
    if fork is None and len({len(histories[a][0]) for a in ARMS}) != 1:
        fork = max_step + 1
    return {
        "first_motor_fork_step": fork,
        "first_physical_difference_step": first_physical_change,
        "prior_physical_states_agree": (
            fork is not None
            and (first_physical_change is None
                 or first_physical_change >= fork)),
        "all_same_motor_until_common_horizon": fork is None,
    }


def q_signature_is_prior_lived(event_rows, *, proposal_index, signature):
    """Trace current Q back to a prior in-life TD publication, never World."""
    if type(proposal_index) is not int or proposal_index < 0:
        raise ValueError("invalid index for Q provenance")
    if type(signature) is not str or not signature.startswith("i1:affordance:"):
        return False
    return any(
        item.get("kind") == "td_update_published"
        and signature in item.get("data", {}).get("updated_signatures", ())
        for item in event_rows[:proposal_index]
    )


def inspect_fork(events_by_arm, *, fork):
    _check(type(fork) is int and fork >= 1, "invalid fork for Q trace inspection")
    result = {}
    histories = {}
    for arm in ARMS:
        events = events_by_arm[arm]
        motors, transitions, captures, proposals, admissions, _ = physical_history(events)
        histories[arm] = (motors, transitions, captures)
        _check(fork in motors, "four-arm fork occurs after one physical death")
        captured = captures.get(fork)
        if captured is not None:
            _check(type(captured) is dict
                   and all(key in captured for key in REQUIRED_CAPTURE_FIELDS),
                   "missing canonical first-person fields at observed fork")
        local = local_competition_at_fork(events, step=fork)
        expected_rank, expected_evidence = Q_MODES[arm]
        for candidate in local["local_candidates"]:
            option_ref = candidate["option_ref"]
            matching = [
                e["data"] for e in events
                if (e.get("t_monde") == fork
                    and e.get("kind") == "i1_local_opportunity_proposed"
                    and e.get("data", {}).get("option_ref") == option_ref)
            ]
            _check(len(matching) == 1, "ambiguous local Q provenance")
            proposal = matching[0]
            proposal_rows = [
                idx for idx, event in enumerate(events)
                if event.get("t_monde") == fork
                and event.get("kind") == "i1_local_opportunity_proposed"
                and event.get("data", {}).get("option_ref") == option_ref
            ]
            _check(len(proposal_rows) == 1,
                   "duplicate in-life candidate proof at first fork")
            prior_td = q_signature_is_prior_lived(
                events, proposal_index=proposal_rows[0],
                signature=proposal.get("learning_signature"),
            )
            candidate["prior_lived_td_for_signature"] = prior_td
            if candidate["q_status_at_proposal"] == "learned":
                _check(prior_td,
                       "learned local Q lacks an earlier first-person TD update")
            _check(proposal.get("q_exposure") == arm.removeprefix("local_q_")
                   and proposal.get("q_used_for_candidate_rank") is expected_rank
                   and proposal.get("q_used_for_competition_evidence") is expected_evidence
                   and proposal.get("forced_motor") is False
                   and proposal.get("physical_outcome_known") is False,
                   "fork violates preregistered Q blinding")
        result[arm] = {
            "motor": motors[fork]["primitive"],
            "parameters": motors[fork]["parameters"],
            "perception_recorded": captured is not None,
            "visible": captured,
            "local_competition": local,
        }
    observations = [result[a]["visible"] for a in ARMS]
    all_present = all(v is not None for v in observations)
    comparable = (all_present and
                  all(v == observations[0] for v in observations[1:]))
    return {
        "first_person_capture_present_all": all_present,
        "same_first_person_visible_capture": comparable,
        "arms": result,
    }


def comparisons(first_fork_trace, histories):
    """Four original paired comparisons without post-fork extrapolation."""
    result = {}
    for label, a, b in CONTRASTS:
        x, y = histories[a], histories[b]
        max_common = min(len(x[0]), len(y[0]))
        first = None
        prior_physiology_changed = None
        for step in range(1, max_common + 1):
            ma = x[0][step]
            mb = y[0][step]
            if (first is None and
                    (ma["primitive"], ma["parameters"]) !=
                    (mb["primitive"], mb["parameters"])):
                first = step
            if prior_physiology_changed is None and any(
                x[1][step].get(k) != y[1][step].get(k)
                for k in EFFECT_FIELDS
            ):
                prior_physiology_changed = step
        if first is None and len(x[0]) != len(y[0]):
            first = max_common + 1
        comparable = first is not None and (
            prior_physiology_changed is None or prior_physiology_changed >= first
        )
        visible_agree = False
        trace = None
        if first is not None and first <= max_common:
            cx = x[2].get(first)
            cy = y[2].get(first)
            visible_agree = (cx is not None and cy is not None and cx == cy)
            trace = first_fork_trace if first == first_fork_trace else None
        result[label] = {
            "first_motor_difference": first,
            "physical_history_aligned_before_difference": comparable,
            "same_visible_capture_at_difference": visible_agree,
            "first_physical_difference": prior_physiology_changed,
            "motor_a": (x[0][first]["primitive"] if first is not None
                        and first <= max_common else None),
            "motor_b": (y[0][first]["primitive"] if first is not None
                        and first <= max_common else None),
        }
    return result


def audit_forks(root: Path):
    custody = audit_original(root)
    _check(custody["status"] == "ORIGINAL_32_WAL_AUTHENTICATED"
           and custody["verified_WAL_count"] == 32
           and custody["source_sha"] == SOURCE_SHA,
           "first-fork audit requires original custody first")
    blocks = []
    counts = Counter()
    for world in PRESETS:
        for seed in SEEDS:
            events_by_arm = {}
            histories = {}
            for arm in ARMS:
                filename = root/world/str(seed)/arm/"life-01.wal"
                # Original WAL SHA was authenticated by audit_original.
                events = [
                    json.loads(line)["causal_event"]
                    for line in filename.read_text(encoding="utf-8").splitlines()
                ]
                events_by_arm[arm] = events
                motors, physical, captures, _, _, _ = physical_history(events)
                histories[arm] = (motors, physical, captures)
            fork = first_fork(histories)
            if fork["prior_physical_states_agree"]:
                counts["blocks_prior_physical_agreement"] += 1
            if fork["first_motor_fork_step"] is not None:
                counts["blocks_with_motor_fork"] += 1
            inspection = None
            index = fork["first_motor_fork_step"]
            if index is not None and index <= min(len(histories[a][0]) for a in ARMS):
                inspection = inspect_fork(events_by_arm, fork=index)
                counts["blocks_identical_first_person_at_first_fork"] += int(
                    inspection["same_first_person_visible_capture"])
                for arm in ARMS:
                    q_candidates = inspection["arms"][arm]["local_competition"]["local_candidates"]
                    counts[arm+":local_proposed_at_first_fork"] += int(bool(q_candidates))
                    counts[arm+":learned_Q_at_first_fork"] += int(
                        any(candidate["q_status_at_proposal"] == "learned"
                            for candidate in q_candidates))
            contrast = comparisons(index, histories)
            for name, row in contrast.items():
                counts[name+":motor_forks"] += int(row["first_motor_difference"] is not None)
                counts[name+":prior_physical_agreement"] += int(
                    row["physical_history_aligned_before_difference"])
                counts[name+":visible_capture_agreement"] += int(
                    row["same_visible_capture_at_difference"])
            blocks.append({
                "world": world, "seed": seed,
                "motor": fork,
                "first_fork_chain": inspection,
                "contrasts": contrast,
            })
    _check(len(blocks) == 8, "expected 8 preregistered four-arm blocks")
    return {
        "schema": SCHEMA,
        "status": "ORIGINAL_WAL_FORK_CUSTODY_VERIFIED",
        "scientific_verdict": "INCONCLUSIVE",
        "original_verified_WAL": 32,
        "exact_source_sha": SOURCE_SHA,
        "birth_run": SOURCE_RUN,
        "original_WAL_untouched": True,
        "observational_temporal_lineage_only": True,
        "no_actors_reborn_or_replayed": True,
        "summary": dict(counts),
        "blocks": blocks,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    _check(not args.output.exists(), "never overwrite original evidence")
    report = audit_forks(args.root)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "original_verified_WAL": report["original_verified_WAL"],
        "scientific_verdict": report["scientific_verdict"],
        "summary": report["summary"],
        "first_forks": [
            {
                "world": b["world"], "seed": b["seed"],
                "step": b["motor"]["first_motor_fork_step"],
                "state_aligned": b["motor"]["prior_physical_states_agree"],
                "capture_aligned": (None if b["first_fork_chain"] is None else
                                    b["first_fork_chain"]["same_first_person_visible_capture"]),
                "actions": (None if b["first_fork_chain"] is None else {
                    a: b["first_fork_chain"]["arms"][a]["motor"]
                    for a in ARMS
                }),
                "contrasts": b["contrasts"],
            } for b in report["blocks"]
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
