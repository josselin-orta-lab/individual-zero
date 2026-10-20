#!/usr/bin/env python3
"""#317 independent WAL diagnosis: critical wake -> freely chosen sleep again.

Cross-cutting evidence for #292, #298 and #317. Strictly operator-only:
there are NO simulated decisions, scripted action priorities, resurrections,
intuitive resource utilities, altered thresholds or engine interventions.
One immutable original WAL snapshot per mortal life is independently audited.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
from tempfile import TemporaryDirectory

from audit_i1_spatial_navigation_314 import audit as audit_wal

SCHEMA = "i1-317-physiological-alert-resleep/v1"
SOURCE_SCHEMA = "i1-317-fresh-current-model-population/v1"


def number(v):
    if type(v) in (int, float):
        f = float(v)
    elif isinstance(v, dict) and set(v) == {"$f64"}:
        f = float.fromhex(v["$f64"])
    else:
        raise ValueError("missing/not first-person body number")
    if not isfinite(f):
        raise ValueError("non-finite first-person body number")
    return f


def data(event):
    value = event.get("data")
    return value if isinstance(value, dict) else {}


def _evaluated_waking_alternatives(rows, *, wake_index, admission_index,
                                   attempt):
    """Evaluate only actually witnessed post-alert option evidence.

    Positive evidence does not imply motor admission, safe navigation or
    physiological utility. Deduplicate repeated cognitive cycles by option
    identity; retain the largest *observed* score for each distinct option.
    """
    alternatives, sleep = {}, {}
    for index, event in rows:
        if (not wake_index < index < admission_index
            or event.get("attempt_ref") != attempt
            or event.get("kind") != "stage8_option_evaluation"):
            continue
        record = data(event)
        option_ref = record.get("option_ref")
        if not isinstance(option_ref, str) or not option_ref:
            raise ValueError("unidentified waking evaluated candidate")
        if record.get("status") != "evaluated" or record.get("evidence") is None:
            continue
        score = number(record["evidence"])
        if not -1.0 <= score <= 1.0:
            raise ValueError("unbounded witnessed waking evidence")
        if option_ref.startswith("option:sleep-pressure:"):
            if record.get("learning_signature") != "primitive:dormir":
                raise ValueError("inconsistent sleep learning signature")
            sleep[option_ref] = (score, record)
        else:
            alternatives[option_ref] = max(
                score, alternatives.get(option_ref, float("-inf")))
    return alternatives, sleep


def _physical(events, expected_steps):
    """A witnessed command + world transition + closure, not a proposal."""
    groups = defaultdict(lambda: defaultdict(list))
    for index, event in enumerate(events):
        t = event.get("t_monde")
        if type(t) is int and t > 0:
            groups[t][event.get("kind")].append((index, event))
    if sorted(t for t, g in groups.items() if g["command_experienced"]) != (
        list(range(1, expected_steps + 1))):
        raise ValueError("gapped/uncommitted lived world steps")
    actions = {}
    for t in range(1, expected_steps + 1):
        by_kind = groups[t]
        wanted = ("command_admitted", "command_experienced",
                  "world_transition_experienced", "step_closed")
        if any(len(by_kind[k]) != 1 for k in wanted):
            raise ValueError(f"ambiguous commanded physical world step {t}")
        (ai, a), (ci, c), (wi, world), (zi, z) = (
            by_kind[k][0] for k in wanted)
        admission, closure = data(a), data(z)
        attempt = a.get("attempt_ref")
        if (not ai < ci < wi < zi or not isinstance(attempt, str)
            or not all(event.get("attempt_ref") == attempt for event in
                       (c, world, z))
            or admission.get("command_hash") != c.get("command_hash")
            or admission.get("primitive") != c.get("primitive")
            or closure.get("world_advance_count") != 1
            or closure.get("applied_command_count") != 1
            or closure.get("outcome") not in {"normal", "dead"}
            or (closure["outcome"] == "dead" and t != expected_steps)):
            raise ValueError(f"mismatched Action Control or physical custody at {t}")
        body = world.get("body_after")
        if not isinstance(body, dict):
            raise ValueError(f"missing physically witnessed body at {t}")
        body = {k: number(body[k])
                for k in ("energy", "food", "water", "integrity")}
        actions[t] = {
            "primitive": c["primitive"], "after_body": body,
            "option_ref": admission.get("option_ref"),
            "attempt": attempt, "admission_index": ai,
            "outcome": closure["outcome"],
        }
    return actions, groups


def classify(events, expected_steps):
    """Pure adversarial-testable classifier; only analyse authenticates WAL."""
    actions, grouped = _physical(events, expected_steps)
    totals = Counter()
    alarm_channels = Counter()
    pressure_values = []
    examples = []
    for t, action in actions.items():
        if action["primitive"] != "dormir":
            continue
        totals["sleep_actions"] += 1
        body = action["after_body"]
        if body["water"] == 0.0:
            totals["sleep_at_zero_water"] += 1
        if body["food"] == 0.0:
            totals["sleep_at_zero_food"] += 1
        if body["energy"] >= 99.0:
            totals["sleep_at_or_above_energy_99"] += 1
        if (body["water"] <= 15.0 or body["food"] <= 10.0):
            totals["sleep_with_low_food_or_water_proxy"] += 1
    for t, by_kind in sorted(grouped.items()):
        wakes = [(idx, event) for idx, event in by_kind[
            "stage10_sleep_woke"] if data(event).get("reason") == "alert"]
        if not wakes:
            continue
        if len(wakes) != 1 or t not in actions:
            raise ValueError(f"ambiguous alert wake world step {t}")
        wi, wake = wakes[0]
        action = actions[t]
        if (wake.get("attempt_ref") != action["attempt"]
            or not wi < action["admission_index"]):
            raise ValueError(f"wake not followed by authenticated cognition at {t}")
        totals["critical_alert_wakes"] += 1
        capture = [event for index, event in by_kind["stage10_reduced_capture"]
                   if index < wi and event.get("attempt_ref") == action["attempt"]]
        if len(capture) != 1:
            raise ValueError(f"waking without actual reduced perception at {t}")
        actual_channels = data(capture[0]).get("critical_body_channels")
        if (not isinstance(actual_channels, list)
            or any(x not in ("energy", "food", "water", "integrity")
                   for x in actual_channels)):
            raise ValueError(f"unverifiable/unknown alert channels at {t}")
        for name in set(actual_channels):
            alarm_channels[name] += 1
        if not actual_channels:
            totals["alerts_without_critical_body_channel"] += 1
        if actions[t]["after_body"]["water"] == 0.0:
            totals["alert_wakes_with_post_action_zero_water"] += 1
        if actions[t]["after_body"]["energy"] >= 99.0:
            totals["alert_wakes_with_post_action_energy_99"] += 1
        if action["primitive"] == "dormir":
            totals["alert_wakes_reselecting_sleep_same_step"] += 1
            alternatives, sleep_values = _evaluated_waking_alternatives(
                by_kind["stage8_option_evaluation"],
                wake_index=wi, admission_index=action["admission_index"],
                attempt=action["attempt"],
            )
            positives = {ref: score for ref, score in alternatives.items()
                         if score > 0}
            if positives:
                totals["resleep_with_positive_other_option"] += 1
                if any(ref.startswith("option:geographic:")
                       for ref in positives):
                    totals["resleep_with_positive_frontier"] += 1
                if any(ref.startswith("option:place-memory:")
                       for ref in positives):
                    totals["resleep_with_positive_place_memory"] += 1
                if any("affordance" in ref for ref in positives):
                    totals["resleep_with_positive_uncertain_action"] += 1
            else:
                totals["resleep_without_positive_other_option"] += 1
            sleep_vote = sleep_values.get(action["option_ref"])
            if sleep_vote is None:
                raise ValueError("resleep lacks evaluated same-option Stage8 score")
            if positives and sleep_vote[0] > max(positives.values()):
                totals["resleep_sleep_evidence_above_positive_alternatives"] += 1
            if sleep_vote[1].get("learned_value_status") == "learned":
                totals["resleep_with_learned_sleep_q"] += 1
            if (sleep_vote[1].get("intrinsic_value") is not None
                and number(sleep_vote[1]["intrinsic_value"]) > 0):
                totals["resleep_with_positive_intrinsic_sleep"] += 1
            ref = action["option_ref"]
            traces = [trace for i, row in by_kind["competition_cycle"]
                      if wi < i < action["admission_index"]
                      for trace in data(row).get("traces", ())
                      if isinstance(trace, dict)
                      and trace.get("option_ref") == ref
                      and trace.get("crossed") is True]
            if traces:
                totals["alert_resleep_with_verified_competition_crossing"] += 1
            else:
                totals["alert_resleep_without_visible_crossing"] += 1
            freezes = [(idx, data(event))
                       for idx, event in by_kind[
                           "stage10_sleep_pressure_frozen"]
                       if wi < idx < action["admission_index"]]
            if len(freezes) != 1:
                raise ValueError(f"missing frozen resleep motivation at {t}")
            pressure_values.append(number(freezes[0][1]["sleep_pressure"]))
            if not 0.0 <= pressure_values[-1] <= 1.0:
                raise ValueError("out-of-range first-person sleep pressure")
            if len(examples) < 12:
                examples.append({
                    "world_step": t,
                    "alarm_channels": sorted(set(actual_channels)),
                    "sleep_pressure": pressure_values[-1],
                    "crossed_competition": bool(traces),
                    "body_after": action["after_body"],
                    "phase": "alert-wake-then-voluntary-sleep",
                })
        if (t+1 in actions and
            actions[t+1]["primitive"] == "dormir"):
            totals["alert_wakes_followed_by_sleep_next_step"] += 1
        if (all(t+j in actions and
                actions[t+j]["primitive"] == "dormir" for j in (1, 2, 3))):
            totals["alert_wakes_followed_by_three_sleep_steps"] += 1
    return {
        "counters": {k: totals[k] for k in (
            "sleep_actions", "sleep_at_zero_water", "sleep_at_zero_food",
            "sleep_at_or_above_energy_99", "sleep_with_low_food_or_water_proxy",
            "critical_alert_wakes", "alerts_without_critical_body_channel",
            "alert_wakes_with_post_action_zero_water",
            "alert_wakes_with_post_action_energy_99",
            "alert_wakes_reselecting_sleep_same_step",
            "alert_resleep_with_verified_competition_crossing",
            "alert_resleep_without_visible_crossing",
            "alert_wakes_followed_by_sleep_next_step",
            "alert_wakes_followed_by_three_sleep_steps",
            "resleep_with_positive_other_option",
            "resleep_without_positive_other_option",
            "resleep_with_positive_frontier",
            "resleep_with_positive_place_memory",
            "resleep_with_positive_uncertain_action",
            "resleep_sleep_evidence_above_positive_alternatives",
            "resleep_with_learned_sleep_q",
            "resleep_with_positive_intrinsic_sleep",
        )},
        "observed_alert_channels": dict(sorted(alarm_channels.items())),
        "mean_intrinsic_sleep_pressure_on_alert_resleep": (
            None if not pressure_values else
            sum(pressure_values) / len(pressure_values)),
        "examples": examples,
        "interpretation": "Actual wake and full cognitive deliberation followed "
                          "by a physically applied sleep action. A sleep action "
                          "after alarm is not evidence of a physiological need "
                          "being successfully addressed. No resource knowledge "
                          "or intervention outcome may be inferred.",
    }


def analyse(root, population_report, *, expected_sha):
    report_raw = population_report.read_bytes()
    report = json.loads(report_raw)
    if (report.get("schema") != SOURCE_SCHEMA
        or report.get("status") !=
            "SEALED_OBSERVATIONAL_POPULATION_NO_SCIENTIFIC_GO"
        or report.get("scientific_verdict") != "NO-GO"
        or report["preregistered_design"]["engine_sha"] != expected_sha):
        raise ValueError("invalid or unpinned 20-life source report")
    expected = {(w, s) for w in
                report["preregistered_design"]["preset_ids"]
                for s in report["preregistered_design"]["fresh_seeds"]}
    if len(expected) != 20 or len(report["individuals"]) != 20:
        raise ValueError("invalid preregistered cohort size")
    observations = []
    total = Counter()
    channels = Counter()
    by_world = defaultdict(Counter)
    seen = set()
    for item in report["individuals"]:
        w, s = item["world"], item["seed"]
        if (w, s) not in expected or (w, s) in seen:
            raise ValueError("duplicated/alien physical life")
        seen.add((w, s))
        rel = root / w / str(s) / "life-01.wal"
        if rel.is_symlink() or not rel.is_file():
            raise ValueError("missing or redirected original mortal WAL")
        raw = rel.read_bytes()
        actual_sha = sha256(raw).hexdigest()
        if actual_sha != item["source_wal_sha256"]:
            raise ValueError("WAL was changed after authentication")
        with TemporaryDirectory(prefix="i1-317-alert-seal-") as tmp:
            sealed = Path(tmp) / "witness.wal"
            sealed.write_bytes(raw)
            proof = audit_wal(sealed)
        if (proof["independent_hash_chain_verified"] is not True
            or proof["journal_head"] != item["journal_head"]
            or proof["journal_entries"] != item["verified_journal_entries"]):
            raise ValueError("physical hash custody mismatch")
        events = [json.loads(line)["causal_event"]
                  for line in raw.splitlines()]
        if len(events) != proof["journal_entries"]:
            raise ValueError("authenticating different event bytes")
        observation = classify(events, item["physically_lived_steps"])
        ct = observation["counters"]
        total.update(ct)
        channels.update(observation["observed_alert_channels"])
        by_world[w].update(ct)
        if (ct["sleep_actions"] != item["actions"].get("dormir", 0)
            or item["engine_sha"] != expected_sha
            or any(type(v) is not int or v < 0 for v in ct.values())):
            raise ValueError("operator sleep analysis disagrees with genuine birth")
        observations.append({
            "world": w, "seed": s,
            "lifecycle": item["lifecycle"],
            "physically_lived_steps": item["physically_lived_steps"],
            "journal_head": proof["journal_head"],
            "wal_sha256": actual_sha,
            **observation,
        })
    if seen != expected:
        raise ValueError("missing world-seed WAL pair")
    if total["sleep_actions"] != report["summary"]["actions"].get("dormir", 0):
        raise ValueError("whole-cohort action checksum failed")
    if (total["alert_wakes_reselecting_sleep_same_step"] >
        total["critical_alert_wakes"] or
        total["resleep_with_positive_other_option"]
        + total["resleep_without_positive_other_option"]
        != total["alert_wakes_reselecting_sleep_same_step"] or
        total["alert_resleep_with_verified_competition_crossing"]
        + total["alert_resleep_without_visible_crossing"]
        != total["alert_wakes_reselecting_sleep_same_step"]):
        raise ValueError("inconsistent alert-to-sleep custody")
    return {
        "schema": SCHEMA, "status": "CERTIFIED_OBSERVATIONAL_NO_GO",
        "source_population_sha256": sha256(report_raw).hexdigest(),
        "physical_engine_sha": expected_sha,
        "births": len(observations),
        "aggregate_counters": dict(sorted(total.items())),
        "alert_channels": dict(sorted(channels.items())),
        "by_world": {w: dict(sorted(c.items()))
                     for w, c in sorted(by_world.items())},
        "individuals": sorted(observations, key=lambda o:
                              (o["world"], o["seed"])),
        "any_causal_sleep_repair_proven": False,
        "entity_causality_proven": False,
        "scientific_verdict": "NO-GO",
        "limitation": "An observed alert wake followed by a fresh decision "
                      "to sleep shows re-entrant competition, not that any "
                      "alternative would improve survival. Refractory rules "
                      "and threshold tuning require matched physical tests.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--population-report", type=Path, required=True)
    p.add_argument("--expected-sha", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError("never overwrite a scientific artifact")
    result = analyse(args.root, args.population_report,
                     expected_sha=args.expected_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print("I1_317_FIRST_PERSON_WAKE_RESLEEP_CERTIFIED")
    print(json.dumps({"births": result["births"],
                      "counters": result["aggregate_counters"],
                      "alert_channels": result["alert_channels"],
                      "scientific_verdict": result["scientific_verdict"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
