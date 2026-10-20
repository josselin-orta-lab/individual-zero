#!/usr/bin/env python3
"""#318 independent read-only certification of prospective local Q exposure.

No world, actor, replay or public birth is invoked. The exact 16 physical
journals from GitHub Actions #39396212562 are authenticated before any
causal interpretation. Treatment is Q exposure to the local candidate only,
not whether the underlying learner runs. Motor differences are observations,
not proof of improved ecological utility.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _verify_arm, _check, _hex, _number
from audit_i1_spatial_navigation_314 import audit as audit_wal

SCHEMA = "i1-318-local-q-ablation-independent-certificate/v1"
BIRTH_SCHEMA = "i1-318-local-Q-ablation-mortal/v1"
SOURCE_SHA = "1ada116666591616a932a8a517e00ec6a0b45452"
RUN_ID = 39396212562
ARMS = ("local_q_neutral", "local_q_learned")
PRESETS = ("memory-corridor", "water-isolated-corridor")
SEEDS = (22111, 22229, 22343, 22453)
POLICY = "i1-local-interaction-goal-independent-v2"
HORIZON = 300
LOCAL = "option:i1:local:"


def physical_history(events):
    """One motor, bodily transition and first-person capture per physical step."""
    motors, transitions, captures = {}, {}, {}
    local = defaultdict(list)
    admissions = defaultdict(list)
    updates = []
    for idx, event in enumerate(events):
        k, t = event.get("kind"), event.get("t_monde")
        data = event.get("data", {})
        if k == "perceptual_capture":
            _check(t not in captures, "multiple first-person captures in one step")
            captures[t] = data
        elif k == "command_experienced":
            _check(t not in motors, "duplicated physical motor step")
            motors[t] = {
                "primitive": event.get("primitive"),
                "parameters": event.get("parameters"),
                "digest": event.get("command_hash"),
                "attempt": event.get("attempt_ref"),
                "index": idx,
            }
        elif k == "world_transition_experienced":
            _check(t not in transitions, "duplicated bodily step")
            transitions[t] = event
        elif k == "i1_local_opportunity_proposed":
            local[t].append((idx, data))
        elif k == "command_admitted":
            admissions[t].append((idx, data))
        elif k == "td_update_published":
            updates.append((idx, t, data))
    # Stage10 may continue physically real sleep without opening a fresh
    # symbolic capture. Never invent a perceptual observation for sleep.
    _check(set(motors) == set(transitions)
           and set(captures).issubset(set(motors))
           and set(motors) == set(range(1, len(motors) + 1))
           and all(t in captures for t in local),
           "missing original physical step or local first-person capture")
    return motors, transitions, captures, local, admissions, updates


def classify_arm(events, *, q_exposure):
    motors, transitions, captures, local, admissions, updates = physical_history(events)
    totals = Counter()
    local_motor = {}
    first_learned_q = None
    longest_drink_streak = current_drink_streak = 0
    last_q_update_by_signature = {}
    update_cursor = 0
    for step in sorted(motors):
        while update_cursor < len(updates) and updates[update_cursor][1] < step:
            _, ut, delta = updates[update_cursor]
            for sig in delta.get("updated_signatures", []):
                if isinstance(sig, str):
                    last_q_update_by_signature[sig] = ut
            update_cursor += 1
        for idx, datum in local.get(step, ()):
            _check(datum.get("policy") == POLICY
                   and datum.get("q_exposure") == q_exposure
                   and datum.get("goal_ref") is None
                   and datum.get("forced_motor") is False
                   and datum.get("physical_outcome_known") is False,
                   "local exposure disagrees with sealed birth intervention")
            sig = datum.get("learning_signature")
            _check(isinstance(sig, str) and sig.startswith("i1:affordance:"),
                   "unidentifiable local option signature")
            totals["local_candidates"] += 1
            if q_exposure == "neutral":
                _check(datum.get("learned_value_status") == "unlearned"
                       and datum.get("learned_value") is None,
                       "neutral arm leaked Q evidence to local producer")
            elif datum.get("learned_value_status") == "learned":
                _check(sig in last_q_update_by_signature
                       and last_q_update_by_signature[sig] < step,
                       "learned local Q is not preceded by same-life TD")
                totals["local_candidates_with_previously_learned_Q"] += 1
                if first_learned_q is None:
                    first_learned_q = step
        motor = motors[step]
        if motor["primitive"] == "boire":
            current_drink_streak += 1
            longest_drink_streak = max(longest_drink_streak, current_drink_streak)
            capture = captures.get(step)
            body_after = transitions[step].get("body_after")
            if (capture is not None
                    and type(capture.get("dual_scope_visible_body")) is dict
                    and type(body_after) is dict
                    and "water" in capture["dual_scope_visible_body"]
                    and "water" in body_after):
                before = _number(capture["dual_scope_visible_body"]["water"])
                after = _number(body_after["water"])
                totals["boire_with_observed_before_after_water"] += 1
                totals["boire_net_water_increase"] += int(after > before)
                totals["boire_no_net_water_increase"] += int(after <= before)
            else:
                totals["boire_without_verifiable_before_after_water"] += 1
        else:
            current_drink_streak = 0
        matched = [
            (i, d) for i, d in admissions.get(step, ())
            if (i < motor["index"] and d.get("source") == "decision"
                and d.get("option_ref", "").startswith(LOCAL)
                and d.get("command_hash") == motor["digest"]
                and d.get("primitive") == motor["primitive"])
        ]
        if matched:
            _check(len(matched) == 1, "ambiguous local command admission")
            local_motor[step] = matched[0][1]["option_ref"]
            totals["local_motor_actions"] += 1
    return {
        "physical_steps": len(motors),
        "first_learned_Q_local_proposal_step": first_learned_q,
        "longest_consecutive_boire": longest_drink_streak,
        "counts": dict(totals),
        "local_motor": local_motor,
        "motor": motors,
        "physical": transitions,
        "captures": captures,
        "proposals": local,
    }


def compare_pair(neutral, learned):
    """Locate the earliest paired motor fork, not downstream action counts."""
    na, lb = neutral["motor"], learned["motor"]
    limit = min(len(na), len(lb))
    motor_first = physical_first = None
    prior_history_is_equal = True
    for t in range(1, limit + 1):
        a, b = na[t], lb[t]
        cmd_a = (a["primitive"], a["parameters"])
        cmd_b = (b["primitive"], b["parameters"])
        if cmd_a != cmd_b and motor_first is None:
            motor_first = t
        p, q = neutral["physical"][t], learned["physical"][t]
        effects = ("body_after", "position_after", "effects")
        if any(p.get(k) != q.get(k) for k in effects):
            if physical_first is None:
                physical_first = t
        if motor_first is None and physical_first is not None:
            prior_history_is_equal = False
    if len(na) != len(lb) and motor_first is None:
        motor_first = limit + 1
    at_fork = {}
    if motor_first is not None and motor_first <= limit:
        n = neutral["captures"].get(motor_first)
        l = learned["captures"].get(motor_first)
        visible = ("position", "dual_scope_visible_body",
                   "agency_visible_inventory", "agency_visible_adjacent")
        same_capture = (n is not None and l is not None and
                        all(n.get(k) == l.get(k) for k in visible))
        local_q_prior = learned["first_learned_Q_local_proposal_step"]
        local_n = [
            row for _, row in neutral["proposals"].get(motor_first, ())
        ]
        local_l = [
            row for _, row in learned["proposals"].get(motor_first, ())
        ]
        at_fork = {
            "step": motor_first,
            "same_first_person_capture": same_capture,
            "same_physical_history_before_motor_fork": (
                physical_first is None or physical_first >= motor_first
            ),
            "exposed_learned_Q_no_later_than_fork": (
                local_q_prior is not None and local_q_prior <= motor_first
            ),
            "learned_local_candidate_at_fork": any(
                row.get("learned_value_status") == "learned"
                for _, row in learned["proposals"].get(motor_first, ())
            ),
            "neutral_local_motor_selected": motor_first in neutral["local_motor"],
            "learned_local_motor_selected": motor_first in learned["local_motor"],
            "neutral_command": na[motor_first]["primitive"],
            "learned_command": lb[motor_first]["primitive"],
            "neutral_local_candidate_signatures": [
                row.get("learning_signature") for row in local_n
            ],
            "learned_local_candidates": [
                {
                    "signature": row.get("learning_signature"),
                    "q_status": row.get("learned_value_status"),
                    "q_value": row.get("learned_value"),
                }
                for row in local_l
            ],
        }
    return {
        "first_motor_divergence": motor_first,
        "first_physical_transition_divergence": physical_first,
        "physical_history_aligned_before_motor_fork": prior_history_is_equal,
        "fork": at_fork,
        "identical_motor_through_common_horizon": motor_first is None,
    }



def local_competition_at_fork(events, *, step):
    """Observe local candidate admission and evidence at the first motor fork.

    This is read-only analysis *after* independent original WAL custody. It
    cannot itself prove that one individual would have chosen differently
    without Q, or that a positive value predicts real-world usefulness.
    """
    _check(type(step) is int and 1 <= step <= HORIZON,
           "invalid physical decision-fork step")
    proposed, receipts, evaluated, traced, admissions = [], [], [], [], []
    motors = []
    for i, event in enumerate(events):
        if event.get("t_monde") != step:
            continue
        kind, data = event.get("kind"), event.get("data", {})
        if kind == "i1_local_opportunity_proposed":
            _check(type(data) is dict and type(data.get("option_ref")) is str
                   and data["option_ref"].startswith(LOCAL),
                   "malformed local fork proposal")
            proposed.append((i, data))
        elif kind == "i1_local_opportunity_registration":
            receipts.append((i, data))
        elif kind == "stage8_option_evaluation":
            evaluated.append((i, data))
        elif kind == "competition_cycle":
            for trace in data.get("traces", ()):
                if type(trace) is dict and type(trace.get("option_ref")) is str:
                    traced.append((i, trace))
        elif kind == "command_admitted":
            admissions.append((i, data))
        elif kind == "command_experienced":
            _check(event.get("emitter") == "action_control",
                   "motor was not admitted through Action Control")
            motors.append((i, event))
    _check(len(motors) == 1, "ambiguous actual first-fork motor")
    motor_idx, motor = motors[0]
    owners = [
        (i, d) for i, d in admissions
        if i < motor_idx and d.get("source") == "decision"
        and d.get("command_hash") == motor.get("command_hash")
        and d.get("primitive") == motor.get("primitive")
    ]
    _check(len(owners) <= 1, "multiple decision owners of one motor")
    owner = owners[0][1] if owners else None
    results = []
    for proposed_idx, p in proposed:
        option = p["option_ref"]
        reg = [(idx, d) for idx, d in receipts
               if idx > proposed_idx and d.get("option_ref") == option
               and d.get("registered") is True]
        first_registration = reg[0][0] if reg else None
        ev = [] if first_registration is None else [
            (idx, d) for idx, d in evaluated
            if idx > first_registration and d.get("option_ref") == option
        ]
        first_evaluation = ev[0][0] if ev else None
        crossing = [] if first_evaluation is None else [
            (idx, d) for idx, d in traced
            if idx > first_evaluation and d.get("option_ref") == option
        ]
        # Some subsequent deliberation cycles can evaluate again; use the
        # actual earliest newly registered option and never invent an outcome.
        chosen = (owner is not None and
                  owner.get("option_ref") == option)
        if chosen:
            _check(first_registration is not None and bool(ev)
                   and any(idx < motor_idx and d.get("crossed") is True
                           for idx, d in crossing),
                   "local physical owner was not verifiably crossed")
        value = p.get("learned_value")
        evaluated_evidence = ev[0][1].get("evidence") if ev else None
        _check(value is None or isinstance(value, dict) or
               type(value) in (int, float),
               "invalid first-fork learned value")
        results.append({
            "option_ref": option,
            "learning_signature": p.get("learning_signature"),
            "q_status_at_proposal": p.get("learned_value_status"),
            "q_exposure": p.get("q_exposure"),
            "q_value_at_proposal": value,
            "registered": bool(reg),
            "evaluated": bool(ev),
            "stage8_evidence": evaluated_evidence,
            "competition_evaluated": bool(crossing),
            "competition_crossed": any(d.get("crossed") is True
                                       for _, d in crossing),
            "motor_owned_by_this_local_option": chosen,
        })
    return {
        "physical_motor": motor.get("primitive"),
        "physical_motor_owned_by_local_producer": any(
            row["motor_owned_by_this_local_option"] for row in results),
        "local_candidates": results,
        "physical_motor_owner_ref": (
            None if owner is None else owner.get("option_ref")),
        "physical_motor_owner_observed": owner is not None,
    }


def classify_first_fork_pathway(neutral_path, learned_path):
    """Classify mechanism without claiming separate pathwise causal effects."""
    old = neutral_path["local_candidates"]
    new = learned_path["local_candidates"]
    old_signatures = [x["learning_signature"] for x in old]
    new_signatures = [x["learning_signature"] for x in new]
    if (not old or not new
            or not all(x["registered"] and x["evaluated"]
                       and x["competition_evaluated"] for x in old + new)):
        return "insufficient_local_Competition_evidence"
    if old_signatures != new_signatures:
        return "local_candidate_rank_changed"
    if (any(x["q_status_at_proposal"] == "learned"
            for x in new)
            and all(x["q_status_at_proposal"] == "unlearned"
                    for x in old)):
        return "same_local_signature_different_Q_evidence"
    return "no_isolated_Q_pathway"



def analyse(root: Path):
    _check(root.is_dir() and not root.is_symlink(), "original artifact directory required")
    expected = {(world, seed) for world in PRESETS for seed in SEEDS}
    reports = {root/world/str(seed)/"report.json" for world, seed in expected}
    _check(set(root.rglob("report.json")) == reports
           and all(p.is_file() and not p.is_symlink() for p in reports),
           "missing, injected, modified or symlinked original report")
    aggregated = {a: Counter() for a in ARMS}
    pairs = []
    for world, seed in sorted(expected):
        report = json.loads((root/world/str(seed)/"report.json").read_text())
        _check(report.get("schema") == BIRTH_SCHEMA
               and report.get("source_sha") == SOURCE_SHA
               and report.get("preset") == world and report.get("seed") == seed
               and report.get("horizon") == HORIZON
               and report.get("status") == "COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
               and report.get("preregistered_arms") == list(ARMS)
               and set(report.get("arms", {})) == set(ARMS)
               and report.get("fixed_local_opportunity_contract") == POLICY
               and report.get("only_local_Q_exposure_changed") is True
               and report.get("goal_conditioned_relevance_treatment_only") is False
               and report.get("no_motor_forcing_or_new_vital_reflex") is True
               and report.get("native_experiential_stage8_opt_in") is False
               and report.get("scientific_verdict") == "NO-GO"
               and _hex(report.get("physics_digest"), 64)
               and _hex(report.get("preset_sha256"), 64),
               "original birth report violates frozen protocol")
        arms = {}
        for name in ARMS:
            original = report["arms"][name]
            expected_exposure = name.removeprefix("local_q_")
            _check(original.get("local_q_exposure") == expected_exposure
                   and original.get("cross_goal_local_opportunities_opt_in") is True
                   and original.get("native_stage8_opt_in") is False
                   and original.get("critical_alert_sleep_guard_opt_in") is False
                   and original.get("option_ranking_adjusted") is True
                   and original.get("option_value_advisory_adjusted") is False
                   and original.get("wal_relative_path") == name + "/life-01.wal",
                   "mismatched active birth parameters or archive provenance")
            wal = root/world/str(seed)/name/"life-01.wal"
            _check(wal.is_file() and not wal.is_symlink(), "missing original mortal WAL")
            _check(sha256(wal.read_bytes()).hexdigest() == original["wal_sha256"],
                   "original mortal WAL SHA mismatch")
            verified = _verify_arm(wal, original, audit_wal)
            events = [
                json.loads(line)["causal_event"]
                for line in wal.read_text(encoding="utf-8").splitlines()
            ]
            chain = classify_arm(events, q_exposure=expected_exposure)
            _check(verified["lived_steps"] == chain["physical_steps"],
                   "physical timeline inconsistent with certified summary")
            arms[name] = {"verified": verified, "chain": chain,
                          "original_events": events}
            totals = aggregated[name]
            totals["lives"] += 1
            totals["deaths"] += int(verified["lifecycle"] == "dead")
            totals["steps"] += verified["lived_steps"]
            totals["consolidated"] += verified["objects_consolidated"]
            totals["UC"] += verified["accepted_cognitive_uc"]
            totals["closed_episodes"] += verified["episode_objects_closed"]
            totals["sleep_commands"] += verified["actions"].get("dormir", 0)
            for action, n in verified["actions"].items():
                totals["motor_"+action] += n
            for key, n in chain["counts"].items():
                totals[key] += n
            totals["max_consecutive_boire_across_lives"] = max(
                totals["max_consecutive_boire_across_lives"],
                chain["longest_consecutive_boire"],
            )
        pair = compare_pair(arms[ARMS[0]]["chain"], arms[ARMS[1]]["chain"])
        first_fork = pair["first_motor_divergence"]
        if first_fork is not None and first_fork <= HORIZON:
            neutral_path = local_competition_at_fork(
                arms["local_q_neutral"]["original_events"],
                step=first_fork)
            learned_path = local_competition_at_fork(
                arms["local_q_learned"]["original_events"],
                step=first_fork)
            pair["fork"]["Competition_provenance"] = {
                "local_q_neutral": neutral_path,
                "local_q_learned": learned_path,
                "observed_Q_pathway": classify_first_fork_pathway(
                    neutral_path, learned_path),
            }
        pairs.append({
            "world": world, "seed": seed,
            "comparison": pair,
            "arms": {name: {
                "lifecycle": arms[name]["verified"]["lifecycle"],
                "lived_steps": arms[name]["verified"]["lived_steps"],
                "consolidated": arms[name]["verified"]["objects_consolidated"],
                "accepted_uc": arms[name]["verified"]["accepted_cognitive_uc"],
                "first_learned_Q_local_proposal_step":
                    arms[name]["chain"]["first_learned_Q_local_proposal_step"],
                "local_candidate_count":
                    arms[name]["chain"]["counts"].get("local_candidates", 0),
                "local_motor_count":
                    arms[name]["chain"]["counts"].get("local_motor_actions", 0),
            } for name in ARMS},
        })
    _check(len(pairs) == 8, "not eight uniquely authenticated physical pairs")
    summary = {a: dict(aggregated[a]) for a in ARMS}
    return {
        "schema": SCHEMA, "status": "ORIGINAL_16_WAL_AUTHENTICATED",
        "birth_run": RUN_ID, "exact_source_sha": SOURCE_SHA,
        "authenticated_WAL_count": 16, "original_WAL_untouched": True,
        "no_actor_instantiated_reborn_or_replayed": True,
        "scientific_verdict": "INCONCLUSIVE",
        "causal_treatment_effect_on_future_survival_proven": False,
        "summary": summary,
        "first_motor_divergences": {
            "local_Q_pathway_counts": dict(Counter(
                p["comparison"]["fork"].get("Competition_provenance", {}).get(
                    "observed_Q_pathway", "no_physical_fork")
                for p in pairs)),
            "pairs_with_same_first_person_capture_at_fork": sum(
                p["comparison"]["fork"].get(
                    "same_first_person_capture") is True for p in pairs),
            "pairs_with_learned_local_candidate_at_fork": sum(
                p["comparison"]["fork"].get(
                    "learned_local_candidate_at_fork") is True for p in pairs),
            "pairs_with_divergent_motor": sum(
                p["comparison"]["first_motor_divergence"] is not None for p in pairs),
            "pairs_with_identical_physical_history_before_fork": sum(
                p["comparison"]["fork"].get(
                    "same_physical_history_before_motor_fork") is True for p in pairs),
            "pairs_exposed_to_learned_Q_before_or_at_fork": sum(
                p["comparison"]["fork"].get(
                    "exposed_learned_Q_no_later_than_fork") is True for p in pairs),
        },
        "pairs": pairs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyse(args.root)
    _check(not args.output.exists(), "certificate must not overwrite original artifact")
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        **{k: report[k] for k in (
            "status", "scientific_verdict", "authenticated_WAL_count",
            "summary", "first_motor_divergences")},
        "pairwise_first_physical_forks": [
            {
                "world": p["world"], "seed": p["seed"],
                "first_motor_step": p["comparison"]["first_motor_divergence"],
                "first_physical_effect_step":
                    p["comparison"]["first_physical_transition_divergence"],
                "fork": p["comparison"]["fork"],
            } for p in report["pairs"]
        ],
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
