#!/usr/bin/env python3
"""#318 read-only certification of 16 original independent-local mortal WALs.

No re-birth, no simulator, no movement recommendation. The previous research
report contains two stale textual declarations; preserve them as evidence
rather than rewriting any original birth report. A software PASS is not GO.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from audit_i1_317_two_process_cohort import _verify_arm, _check, _hex
from audit_i1_spatial_navigation_314 import audit as authenticate

SCHEMA = "i1-318-independent-local-original-WAL-certificate/v1"
BIRTH_SCHEMA = "i1-318-independent-local-mortal/v1"
EXACT_SHA = "8b5b731aa80eb4803d6dbb9e5c1ef82bc7ded230"
ORIGINAL_RUN = 39385691970
PRESETS = ("memory-corridor", "water-isolated-corridor")
SEEDS = (21121, 21227, 21341, 21467)
ARMS = ("baseline", "cross_goal_local")
POLICY = "i1-local-interaction-goal-independent-v2"
LEGAL = frozenset((
    "boire", "manger", "collecter", "poser_une_pierre", "fabriquer_outil",
))


def classify(events, *, treatment):
    """Observe each funnel edge, never infer action execution from proposal.

    Original WAL hash-chain and physical closure must be independently
    authenticated BEFORE calling this pure classifier on these events.
    """
    proposed = {}
    registered = {}
    evaluations = defaultdict(list)
    traces = defaultdict(list)
    admissions = defaultdict(list)
    commands = defaultdict(list)
    kinds = Counter()
    perceived = 0
    first_person_water = 0
    first_person_td = 0
    for idx, event in enumerate(events):
        kind = event.get("kind")
        kinds[kind] += 1
        step, attempt, cycle = (
            event.get("t_monde"), event.get("attempt_ref"), event.get("cycle")
        )
        data = event.get("data", {})
        _check(type(data) is dict, "malformed original WAL event data")
        if kind == "i1_water_lived_outcome_admitted" and data.get("admitted") is True:
            first_person_water += 1
        if kind == "td_update_published" and any(
            isinstance(v, str) and v.startswith("i1:affordance:")
            for v in data.get("updated_signatures", ())
        ):
            first_person_td += 1
        if kind == "i1_local_opportunity_perceived":
            _check(treatment, "control generated local research opportunities")
            _check(data.get("policy") == POLICY
                   and data.get("goal_filter_applied") is False
                   and type(data.get("accessible_count")) is int
                   and type(data.get("not_already_proposed")) is int
                   and 0 <= data["not_already_proposed"] <= data["accessible_count"],
                   "unverifiable local first-person opportunity detection")
            perceived += 1
        if kind == "i1_local_opportunity_proposed":
            _check(treatment and type(step) is int and type(attempt) is str
                   and type(cycle) is int, "foreign local proposal")
            ref = data.get("option_ref")
            command = data.get("command")
            _check(type(ref) is str and ref.startswith("option:i1:local:")
                   and type(command) is dict
                   and command.get("primitive") in LEGAL
                   and data.get("policy") == POLICY
                   and data.get("goal_ref") is None
                   and data.get("forced_motor") is False
                   and data.get("physical_outcome_known") is False
                   and type(data.get("visible_input_sha256")) is str
                   and _hex(data["visible_input_sha256"], 64),
                   "proposal assumes utility or lacks physical perception")
            key = (step, attempt, ref)
            _check(key not in proposed, "duplicate local option within a world step")
            proposed[key] = (idx, cycle, data)
        if kind == "i1_local_opportunity_registration":
            ref = data.get("option_ref")
            _check(treatment and type(ref) is str
                   and ref.startswith("option:i1:local:")
                   and type(data.get("registered")) is bool,
                   "invalid local registration receipt")
            key = (step, attempt, ref)
            registered.setdefault(key, []).append((idx, cycle, data["registered"]))
        if kind == "stage8_option_evaluation":
            ref = data.get("option_ref")
            if isinstance(ref, str) and ref.startswith("option:i1:local:"):
                evaluations[(step, attempt, ref)].append((idx, cycle, data))
        if kind == "competition_cycle":
            for t in data.get("traces", ()):
                if type(t) is dict:
                    ref = t.get("option_ref")
                    if isinstance(ref, str) and ref.startswith("option:i1:local:"):
                        _check(type(t.get("crossed")) is bool,
                               "missing original Competition verdict")
                        traces[(step, attempt, ref)].append((idx, cycle, t))
        if kind == "command_admitted":
            admissions[(step, attempt)].append((idx, data))
        if kind == "command_experienced":
            commands[(step, attempt)].append((idx, event))
    if not treatment:
        _check(not any((proposed, registered, evaluations, traces, perceived)),
               "control arm leaked locally generated candidate")

    stages = Counter()
    examples = []
    for key, (pi, pc, pdata) in proposed.items():
        stages["proposed"] += 1
        regs = sorted(
            (i, c) for i, c, ok in registered.get(key, ()) if ok and i > pi
        )
        if not regs:
            stages["proposed_unregistered"] += 1
            continue
        stages["registered"] += 1
        ri, rc = regs[0]
        assessed = [
            (idx, c, d) for idx, c, d in evaluations.get(key, ()) if idx > ri
        ]
        if not assessed:
            stages["registered_not_evaluated"] += 1
            continue
        stages["evaluated"] += 1
        if any(a[2].get("learned_value_status") == "learned" for a in assessed):
            stages["evaluated_with_learned_Q"] += 1
        crossed = [
            (idx, c, t) for idx, c, t in traces.get(key, ())
            if idx > assessed[0][0] and t["crossed"]
        ]
        if not crossed:
            stages["evaluated_not_crossed"] += 1
            continue
        stages["crossed"] += 1
        crossing_idx = crossed[0][0]
        sent = []
        for admission_idx, admitted in admissions.get(key[:2], ()):
            if (admission_idx <= crossing_idx
                    or admitted.get("option_ref") != key[2]
                    or admitted.get("primitive") != pdata["command"]["primitive"]
                    or admitted.get("source") != "decision"):
                continue
            for command_idx, physical in commands.get(key[:2], ()):
                if (command_idx > admission_idx
                        and physical.get("command_hash") ==
                            admitted.get("command_hash")
                        and physical.get("primitive") ==
                            pdata["command"]["primitive"]
                        and physical.get("emitter") == "action_control"):
                    sent.append((command_idx, physical))
        if not sent:
            stages["crossed_without_physically_admitted_command"] += 1
            continue
        # Independent _verify_arm has already proven one ordered world
        # transition, a unique command, physical closure and no resurrection.
        _check(len(sent) == 1, "ambiguous sent local motor command")
        stages["physically_applied"] += 1
        if len(examples) < 10:
            examples.append({
                "world_step": key[0],
                "option_ref": key[2],
                "primitive": pdata["command"]["primitive"],
                "ordinary_candidate_preserved": pdata.get(
                    "ordinary_candidate_preserved"),
                "evaluated_as_learned": any(
                    a[2].get("learned_value_status") == "learned"
                    for a in assessed
                ),
            })
    for key, receipts in registered.items():
        _check(key in proposed, "local candidate registered without proposal")
    for key in evaluations:
        _check(key in proposed, "local Stage8 score without a proposal")
    for key in traces:
        _check(key in proposed, "local Competition trace without a proposal")
    _check(stages["physically_applied"] <= stages["crossed"] <=
           stages["evaluated"] <= stages["registered"] <= stages["proposed"],
           "inconsistent local funnel")
    return {
        "perceived_opportunity_cycles": perceived,
        "funnel": dict(stages),
        "positive_first_person_water_outcomes": first_person_water,
        "td_updates_referencing_affordance_signatures": first_person_td,
        "physically_applied_local_examples": examples,
    }


def audit_original(root: Path):
    _check(root.is_dir() and not root.is_symlink(),
           "missing original unmodified cohort")
    expected = {(w, s) for w in PRESETS for s in SEEDS}
    reports = {root / w / str(s) / "report.json" for w, s in expected}
    _check(set(root.rglob("report.json")) == reports
           and not any(p.is_symlink() for p in reports),
           "injected, altered or incomplete report set")
    per_life, aggregates = [], {a: Counter() for a in ARMS}
    for world, seed in sorted(expected):
        report = json.loads((root / world / str(seed) / "report.json").read_text())
        _check(report.get("schema") == BIRTH_SCHEMA
               and report.get("source_sha") == EXACT_SHA
               and report.get("status") == "COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
               and report.get("preset") == world
               and report.get("seed") == seed
               and report.get("horizon") == 300
               and report.get("preregistered_arms") == list(ARMS)
               and set(report.get("arms", {})) == set(ARMS)
               and report.get("only_local_candidate_scope_changed") is True
               and report.get("same_world_physics_needs_td_competition_action_control")
                   is True
               and report.get("no_motor_forcing_or_new_vital_reflex") is True
               and report.get("native_experiential_stage8_opt_in") is False
               and report.get("scientific_verdict") == "NO-GO"
               and _hex(report.get("physics_digest"), 64)
               and _hex(report.get("preset_sha256"), 64),
               "unverifiable original preregistered birth report")
        # These two stale labels came from the earlier cohort runner. Never
        # rewrite or retroactively 'fix' original scientific records.
        _check(report.get("fixed_local_opportunity_contract") ==
                   "i1-local-interaction-goal-independent-v1"
               and report.get("goal_conditioned_relevance_treatment_only") is True,
               "historical metadata differs from original reported bytes")
        for arm in ARMS:
            record = report["arms"][arm]
            _check(record.get("cross_goal_local_opportunities_opt_in") is
                       (arm == "cross_goal_local")
                   and record.get("native_stage8_opt_in") is False
                   and record.get("critical_alert_sleep_guard_opt_in") is False
                   and record.get("option_ranking_adjusted") is True
                   and record.get("option_value_advisory_adjusted") is False
                   and record.get("wal_relative_path") == arm + "/life-01.wal",
                   "physical arms differ in preregistered birth selectors")
            wal = root / world / str(seed) / arm / "life-01.wal"
            _check(wal.is_file() and not wal.is_symlink(), "original WAL absent")
            _check(sha256(wal.read_bytes()).hexdigest() == record["wal_sha256"],
                   "original WAL archive digest mismatch")
            physical = _verify_arm(wal, record, authenticate)
            with wal.open(encoding="utf-8") as stream:
                events = [json.loads(line)["causal_event"] for line in stream]
            funnel = classify(events, treatment=(arm == "cross_goal_local"))
            counters = aggregates[arm]
            counters["lives"] += 1
            counters["deaths"] += int(physical["lifecycle"] == "dead")
            counters["lived_steps"] += physical["lived_steps"]
            counters["consolidated"] += physical["objects_consolidated"]
            counters["UC"] += physical["accepted_cognitive_uc"]
            for primitive, count in physical["actions"].items():
                counters["motor_" + primitive] += count
            for name, count in funnel["funnel"].items():
                counters["local_" + name] += count
            counters["opportunity_cycles"] += funnel["perceived_opportunity_cycles"]
            counters["positive_water_followups"] += (
                funnel["positive_first_person_water_outcomes"]
            )
            counters["affordance_TD_updates"] += (
                funnel["td_updates_referencing_affordance_signatures"]
            )
            per_life.append({
                "world": world, "seed": seed, "arm": arm,
                "physical": physical, "local": funnel,
                "sha256_original_wal": record["wal_sha256"],
            })
    _check(len(per_life) == 16, "not the 16 original mortal births")
    return {
        "schema": SCHEMA,
        "status": "ORIGINAL_WAL_AUTHENTICATED_PROTOCOL_METADATA_STALE",
        "scientific_verdict": "NO-GO",
        "birth_run": ORIGINAL_RUN,
        "exact_birth_sha": EXACT_SHA,
        "authenticated_wal_count": len(per_life),
        "reported_contract_stale": True,
        "reported_treatment_description_stale": True,
        "original_WAL_untouched": True,
        "no_actor_instantiated_or_replayed": True,
        "summary": {arm: dict(aggregates[arm]) for arm in ARMS},
        "lives": per_life,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_original(args.root)
    _check(not args.output.exists(), "refuse to overwrite original evidence")
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(json.dumps({
        "status": report["status"],
        "authenticated_wal_count": report["authenticated_wal_count"],
        "summary": report["summary"],
        "scientific_verdict": report["scientific_verdict"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
