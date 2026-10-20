#!/usr/bin/env python3
"""#318 passive learning-chain joins over the immutable 16 certified WALs.

These are temporal observations, NOT an oracle of causal consequences. No
living actor is instantiated, no original WAL is mutated, no new birth/replay.
The old original-WAL certificate is rerun before any learning interpretation.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _number, _check
from audit_i1_318_independent_local_cohort import (
    audit_original, ARMS, PRESETS, SEEDS, EXACT_SHA,
)

SCHEMA = "i1-318-original-local-learning-chain/v1"
BODY_FIELDS = ("water", "food", "energy", "integrity")


def observe(events, *, treatment):
    """Classify decisions and bodily changes in verified original WAL order.

    Calling this on synthetic rows tests its interpretation but does NOT
    authenticate those rows. audit_original() must run first on real WALs.
    """
    proposals = {}
    captures = defaultdict(list)
    transitions = defaultdict(list)
    admissions = defaultdict(list)
    motors = defaultdict(list)
    assessments = []
    td_updates = []
    crossings = defaultdict(list)
    for idx, event in enumerate(events):
        kind = event.get("kind")
        t, attempt = event.get("t_monde"), event.get("attempt_ref")
        data = event.get("data", {})
        _check(type(data) is dict, "invalid original event data")
        step_key = (t, attempt)
        if kind == "i1_local_opportunity_proposed":
            _check(treatment, "nonexperimental WAL asserted independent proposal")
            ref, signature = data.get("option_ref"), data.get("learning_signature")
            _check(type(ref) is str and ref.startswith("option:i1:local:")
                   and type(signature) is str
                   and signature.startswith("i1:affordance:")
                   and type(t) is int and type(attempt) is str,
                   "local option lacks signature or physical identity")
            key = (t, attempt, ref)
            _check(key not in proposals, "duplicate independent local option")
            proposals[key] = (idx, signature, data)
        elif kind == "perceptual_capture":
            captures[step_key].append((idx, data))
        elif kind == "world_transition_experienced":
            transitions[step_key].append((idx, event))
        elif kind == "command_admitted":
            admissions[step_key].append((idx, data))
        elif kind == "command_experienced":
            motors[step_key].append((idx, event))
        elif kind == "stage8_option_evaluation":
            if type(data.get("learning_signature")) is str:
                assessments.append((idx, t, attempt, data))
        elif kind == "td_update_published":
            _check(type(data.get("updated_signatures")) is list,
                   "malformed original TD update signatures")
            td_updates.append((idx, t, data))
        elif kind == "competition_cycle":
            for row in data.get("traces", ()):
                if type(row) is dict and type(row.get("option_ref")) is str:
                    crossings[(t, attempt, row["option_ref"])].append((idx, row))
    if not treatment:
        _check(not proposals, "nonexperimental local producer leaked")
    applied = []
    for key, (pi, signature, proposed) in proposals.items():
        step_key = key[:2]
        valid_crossings = [
            i for i, d in crossings.get(key, ())
            if i > pi and d.get("crossed") is True
        ]
        if not valid_crossings:
            continue
        claims = []
        for ai, admission in admissions.get(step_key, ()):
            if (ai <= valid_crossings[0]
                    or admission.get("option_ref") != key[2]
                    or admission.get("source") != "decision"):
                continue
            for mi, motor in motors.get(step_key, ()):
                if (mi > ai and motor.get("emitter") == "action_control"
                        and motor.get("command_hash") ==
                            admission.get("command_hash")
                        and motor.get("primitive") ==
                            proposed["command"]["primitive"]):
                    claims.append((mi, motor))
        if not claims:
            continue
        _check(len(claims) == 1, "nonunique certified physical local command")
        motor_idx, motor = claims[0]
        owned_transitions = [
            (i, tr) for i, tr in transitions.get(step_key, ())
            if i > motor_idx
        ]
        owned_captures = [
            (i, cap) for i, cap in captures.get(step_key, ())
            if i < pi
        ]
        _check(len(owned_transitions) == 1,
               "missing unique original local action physical transition")
        ti, transition = owned_transitions[0]
        body_after = transition.get("body_after")
        _check(type(body_after) is dict, "missing physically observed outcome")
        observed_body = None
        if len(owned_captures) == 1:
            raw = owned_captures[0][1].get("dual_scope_visible_body")
            if type(raw) is dict and all(k in raw for k in BODY_FIELDS):
                observed_body = {
                    field: _number(body_after[field]) - _number(raw[field])
                    for field in BODY_FIELDS
                }
        applied.append({
            "index": motor_idx, "physical_step": key[0],
            "signature": signature, "option_ref": key[2],
            "primitive": motor["primitive"],
            "observed_body_delta": observed_body,
        })

    counters = Counter()
    examples = []
    observed_signatures = set()
    local_origin_signatures = set()
    for action in sorted(applied, key=lambda item: item["index"]):
        ai, sig, t = action["index"], action["signature"], action["physical_step"]
        prior_updates = [
            i for i, _, d in td_updates
            if i < ai and sig in d["updated_signatures"]
        ]
        already_learned = bool(prior_updates)
        later_updates = [
            (i, d) for i, previous_t, d in td_updates
            if i > ai and previous_t > t
            and d.get("previous_signature") == sig
            and sig in d["updated_signatures"]
        ]
        # TD is emitted at the *next* cognitive decision, not retroactively
        # at the prior motor time. A later TD update can be a continuation
        # of the same signature; retain the first grounded update only.
        update_idx = None if not later_updates else later_updates[0][0]
        later_evals = [] if update_idx is None else [
            (i, et, ea, d) for i, et, ea, d in assessments
            if i > update_idx and et > t
            and d["learning_signature"] == sig
            and d.get("learned_value_status") == "learned"
        ]
        # An evaluation is evidence of reusable knowledge, not proof that Q
        # CAUSED a particular motor. A physical later motor is additionally
        # required for a conservative behavioural-reuse observation.
        reused_motor = False
        for ei, et, ea, evaluation in later_evals:
            for mi, motor in motors.get((et, ea), ()):
                if mi <= ei or motor.get("emitter") != "action_control":
                    continue
                if any(
                    ei < admission_idx < mi
                    and admission.get("source") == "decision"
                    and admission.get("option_ref") ==
                        evaluation.get("option_ref")
                    and admission.get("command_hash") ==
                        motor.get("command_hash")
                    for admission_idx, admission in admissions.get((et, ea), ())
                ):
                    reused_motor = True
                    break
            if reused_motor:
                break
        counters["local_physical_actions"] += 1
        counters["previously_updated_Q_at_action"] += int(already_learned)
        counters["TD_segment_confirmed_after_local_motor"] += int(
            update_idx is not None)
        counters["later_learned_Q_assessment"] += int(bool(later_evals))
        counters["later_physically_selected_after_learned_Q"] += int(reused_motor)
        new_origin = update_idx is not None and not already_learned
        counters["first_Q_update_followed_local_motor"] += int(new_origin)
        if new_origin:
            local_origin_signatures.add(sig)
        observed_signatures.add(sig)
        observed = action["observed_body_delta"]
        if observed is None:
            counters["lacks_prior_first_person_body_capture"] += 1
        else:
            counters["physical_bodily_delta_available"] += 1
            for name, value in observed.items():
                # A same-step change includes natural consumption. This is
                # *not* interpreted as proof the command itself was beneficial.
                if value > 0:
                    counters[name + "_positive_same_step_change"] += 1
                elif value < 0:
                    counters[name + "_negative_same_step_change"] += 1
        if len(examples) < 16:
            examples.append({
                "step": t, "signature": sig,
                "primitive": action["primitive"],
                "delta_from_perceived_body": observed,
                "prior_Q_update": already_learned,
                "subsequent_owned_TD": update_idx is not None,
                "later_learned_evaluation": bool(later_evals),
                "later_motor_after_learned_evaluation": reused_motor,
            })
    _check(counters["local_physical_actions"] == len(applied),
           "miscounted actual independent local applications")
    return {
        "counts": dict(counters),
        "signatures_physically_tried": sorted(observed_signatures),
        "signatures_with_first_Q_update_after_local_motor":
            sorted(local_origin_signatures),
        "examples": examples,
        "causal_learning_proven": False,
        "body_delta_causally_attributed_to_action": False,
    }


def analyse(root: Path):
    certificate = audit_original(root)
    _check(certificate["authenticated_wal_count"] == 16
           and certificate["exact_birth_sha"] == EXACT_SHA
           and certificate["scientific_verdict"] == "NO-GO",
           "original WAL first-stage certification failed")
    aggregate = {a: Counter() for a in ARMS}
    details = []
    for world in PRESETS:
        for seed in SEEDS:
            for arm in ARMS:
                wal = root / world / str(seed) / arm / "life-01.wal"
                with wal.open(encoding="utf-8") as stream:
                    events = [json.loads(line)["causal_event"] for line in stream]
                report = observe(events, treatment=(arm == "cross_goal_local"))
                aggregate[arm].update(report["counts"])
                details.append({
                    "world": world, "seed": seed, "arm": arm,
                    "learning": report,
                })
    return {
        "schema": SCHEMA, "source_birth_run": 39385691970,
        "exact_source_sha": EXACT_SHA,
        "original_authenticated_WAL": 16,
        "status": "TEMPORAL_ASSOCIATION_ONLY",
        "scientific_verdict": "INCONCLUSIVE",
        "not_a_causal_Q_ablation": True,
        "no_death_replay_or_new_born_actors": True,
        "summary": {arm: dict(aggregate[arm]) for arm in ARMS},
        "lives": details,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = analyse(args.root)
    _check(not args.output.exists(), "new report must not overwrite evidence")
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "status": report["status"], "summary": report["summary"],
        "original_authenticated_WAL": report["original_authenticated_WAL"],
        "scientific_verdict": report["scientific_verdict"],
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
