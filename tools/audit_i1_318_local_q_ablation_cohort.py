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

from audit_i1_317_two_process_cohort import _verify_arm, _check, _hex
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
    _check(set(motors) == set(transitions)
           and set(motors) == set(captures)
           and set(motors) == set(range(1, len(motors) + 1)),
           "missing first-person/motor/physical step")
    return motors, transitions, captures, local, admissions, updates


def classify_arm(events, *, q_exposure):
    motors, transitions, captures, local, admissions, updates = physical_history(events)
    totals = Counter()
    local_motor = {}
    first_learned_q = None
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
        n = neutral["captures"][motor_first]
        l = learned["captures"][motor_first]
        visible = ("position", "dual_scope_visible_body",
                   "agency_visible_inventory", "agency_visible_adjacent")
        same_capture = all(n.get(k) == l.get(k) for k in visible)
        local_q_prior = learned["first_learned_Q_local_proposal_step"]
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
        }
    return {
        "first_motor_divergence": motor_first,
        "first_physical_transition_divergence": physical_first,
        "physical_history_aligned_before_motor_fork": prior_history_is_equal,
        "fork": at_fork,
        "identical_motor_through_common_horizon": motor_first is None,
    }


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
            arms[name] = {"verified": verified, "chain": chain}
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
        pair = compare_pair(arms[ARMS[0]]["chain"], arms[ARMS[1]]["chain"])
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
        k: report[k] for k in ("status", "scientific_verdict",
                             "authenticated_WAL_count", "summary",
                             "first_motor_divergences")
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
