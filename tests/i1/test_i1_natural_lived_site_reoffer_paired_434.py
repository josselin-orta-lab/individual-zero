"""Two non-directed M11 births: can real food consequences reach site evidence?

This is a paired mechanistic experiment, NOT a population study or a GO for
useful autonomous navigation. Only unseen physical berry nutrition differs
before birth. The model cannot read that operator-only fact from the layout.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class NaturalSiteReofferPhysiologyPair(unittest.TestCase):
    def test_first_person_effect_and_later_spatial_evaluation(self):
        with TemporaryDirectory(prefix="i1-434-paired-") as directory:
            generated = Path(directory) / "generated"
            generate(generated)
            script = r"""
from collections import Counter
from dataclasses import replace
from math import exp, isfinite, tanh
import json
from pathlib import Path
from re import search
from tempfile import TemporaryDirectory

from i1lab.i1_birth import birth_i1_m11
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

preset, preset_digest = load_preset("dry-valley")
raw_params, local = _birth_parameters(preset)
assert local["current_resources"] == ["berry_a"]
assert not any(key in local for key in (
    "oracle_canary", "berry_effects", "food_gain", "reward",
))
life_id = "i1:387:dry-valley-lived-site"
TOTAL = 12
# Preregister the naturally moving birth identity of canonical #387.

def experiment(food_gain, db_path):
    # The one and only intervention is physical berry_a nutrition at birth.
    # Neither the model, perception, goals, TD, UC, sleep nor actions are edited.
    baseline = raw_params["world_config"]
    berry = dict(baseline.berry_effects)
    berry["berry_a"] = replace(berry["berry_a"], food_gain=float(food_gain))
    # Hold physics identity and every other rule fixed. Only the actual
    # nutrition of berry_a changes. The previous probe also changed version,
    # which is an unnecessary second treatment and could confound results.
    physics = replace(baseline, berry_effects=berry)
    assert physics.version == baseline.version
    assert replace(physics, berry_effects=baseline.berry_effects) == baseline, (
        "non-nutritional world physics changed between study arms")
    physics.validate()
    params = dict(
        raw_params, world_config=physics,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
    )
    receipts, bodies, boundaries, td_snapshots = [], [], [], []
    with birth_i1_m11(db_path=str(db_path), life_id=life_id, **params) as actor:
        rt = actor._runtime
        first_local = rt.world.capture_local(t_monde=1).as_dict()
        # This is an operator comparison, not an input to the decision owner.
        assert "food_gain" not in json.dumps(first_local)
        for _ in range(TOTAL):
            # M11 publishes a NEW runtime only after the SQLite commit.
            # Never retain the genesis owner across physical generations.
            before = dict(actor._runtime.world.body.as_dict())
            receipt = actor.run_step()
            rt = actor._runtime
            assert receipt.status in ("active", "dead"), receipt
            bodies.append({
                "step": receipt.world_step, "before": before,
                "after": dict(rt.world.body.as_dict()),
                "position": rt.world.position.as_dict(),
                # Existing world-step temporal condition, no new perception
                # or additional owner update.
                "is_night_at_step": bool(rt.world.is_night(receipt.world_step)),
            })
            receipts.append({
                "generation": receipt.generation,
                "status": receipt.status,
                "journal_head": receipt.journal_head,
            })
            # Real post-commit Competition custody, including sleeping steps.
            registry = rt.competition.export_causal_state()["registry"]
            boundaries.append({
                "step": receipt.world_step,
                "ids": {
                    entry["proposal"]["option"]["id"]: {
                        "expires": entry["proposal"]["option"]["expires_at_step"],
                        "accumulator": entry["accumulator"],
                    }
                    for entry in registry
                    if entry["proposal"]["option"]["id"].startswith(
                        "option:lived-site:")
                },
            })
            # Read only the M11-committed Q owner. Never query a fabricated
            # evaluation state or promote a physical effect to motor evidence.
            td_image = rt.q_active.export_causal_state()
            td_snapshots.append({
                "step": receipt.world_step,
                "weights": {name: tuple(vector) for name, vector
                            in td_image["weights"].items()},
                "update_counts": dict(td_image["update_counts"]),
                "pending_signature": (
                    None if td_image["pending"] is None else
                    td_image["pending"]["signature"]),
                "pending_reward_count": (
                    0 if td_image["pending"] is None else
                    len(td_image["pending"]["rewards"])),
            })
            if receipt.status == "dead":
                break
        events = [dict(e.causal_event) for e in rt.journal.entries_since(0)]
        state = rt.exploration.geographic.export_causal_state()
        td_updates = dict(sorted(rt.q_active.export_causal_state()[
            "update_counts"].items()))
        journal_head = rt.journal.head_hash
    ledger = SQLiteLifeLedger.audit_read_only(
        path=str(db_path), expected_individual_id=life_id)
    assert ledger.generation == len(receipts)
    assert ledger.journal_head == journal_head == receipts[-1]["journal_head"]
    assert not ledger.pending_intent
    assert ledger.status == receipts[-1]["status"]

    applied = {}
    for e in events:
        if e.get("kind") != "command_experienced":
            continue
        step = e["t_monde"]
        assert step not in applied, "two physical commands in one world step"
        applied[step] = e["primitive"]
    assert len(applied) == len(receipts), "missing physical command receipt"
    assert set(applied) == {row["step"] for row in bodies}

    scored = {}
    evaluations = {}
    for e in events:
        d = e.get("data", {})
        if (e.get("kind") == "stage8_option_evaluation"
            and str(d.get("option_ref", "")).startswith("option:lived-site:")):
            key = (e["t_monde"], e["cycle"], d["option_ref"])
            assert key not in evaluations
            evaluations[key] = d
        elif e.get("kind") == "stage11_intrinsic_evaluation" and (
            str(d.get("option_ref", "")).startswith("option:lived-site:")
        ):
            key = (e["t_monde"], e["cycle"], d["option_ref"])
            assert key not in scored
            scored[key] = d
    assert set(scored) == set(evaluations)
    contextual = []
    for (step, cycle, ref), d in sorted(scored.items()):
        if "exploration:lived_site_context_not_causal" not in (
            d.get("intrinsic_producers", ())
        ):
            continue
        sources = [s for s in d.get("signal_ids", ())
                   if str(s).startswith("lived-site:")]
        assert sources, "contextual value without a first-person site witness"
        assert all(
            (match := search(r":observed-t([1-9][0-9]*)$", s))
            and int(match.group(1)) < step for s in sources
        ), "future site observation entered spatial evaluation"
        result = evaluations[(step, cycle, ref)]
        assert result["status"] == "evaluated"
        assert result["evidence"] is not None
        contextual.append({
            "step": step, "cycle": cycle, "ref": ref,
            "evidence": result["evidence"],
            "learned": result["learned_value_status"],
            "simulated": result["simulated_value_status"],
        })
    # The TD event is emitted only after a real next cognitive decision.
    # Equal update counts do not mean equal learned values; inspect both.
    td_events = []
    paid_stage8 = {}
    # Owner-published intrinsic assessment at each real paid cycle.
    paid_intrinsic = {}
    frozen_sleep_by_step = {}
    frozen_sleep_components = {}
    owner_goal_events = {}
    producer_events = {}
    goal_unavailable_events = []
    for e in events:
        d = e.get("data", {})
        if e.get("kind") == "active_goal_changed":
            clock = (e["t_monde"], e["cycle"])
            assert clock not in owner_goal_events
            owner_goal_events[clock] = d["after"]
        elif e.get("kind") in (
            "i1_local_opportunity_proposed",
            "i1_unknown_affordance_proposed",
        ):
            ref = d["option_ref"]
            key = (e["t_monde"], e["cycle"], ref)
            assert key not in producer_events
            producer_events[key] = {
                "event_kind": e["kind"],
                "goal_ref": d.get("goal_ref"),
            }
        elif e.get("kind") == "i1_goal_unavailable_reconsidered":
            goal_unavailable_events.append((
                e["t_monde"], e["cycle"], d["goal_ref"],
                d["goal_released"]))
        if e.get("kind") == "td_update_published":
            assert d["segment_length"] >= 1
            td_events.append({
                "decision_step": e["t_monde"],
                "previous_signature": d["previous_signature"],
                "next_signature": d["next_signature"],
                "segment_length": d["segment_length"],
                "return_g": float(d["return_g"]),
                "delta": float(d["delta"]),
                "updated_signatures": tuple(d["updated_signatures"]),
            })
        elif e.get("kind") == "stage10_sleep_pressure_frozen":
            step = e["t_monde"]
            assert step not in frozen_sleep_by_step, (
                "P-40 was frozen more than once in a waking physical step")
            assert d["world_step"] == step
            frozen_sleep_by_step[step] = d["sleep_pressure"]
            frozen_sleep_components[step] = {
                "fatigue": d["fatigue"],
                "consolidation_pressure": d["consolidation_pressure"],
            }
        elif e.get("kind") == "stage11_intrinsic_evaluation":
            key = (e["t_monde"], e["cycle"], d["option_ref"])
            assert key not in paid_intrinsic
            paid_intrinsic[key] = {
                "status": d["status"],
                "intrinsic_value": d["intrinsic_value"],
                "producers": tuple(d["intrinsic_producers"]),
                "intrinsic_weight": d["P15_intrinsic_weight"],
            }
        elif e.get("kind") == "stage8_option_evaluation":
            key = (e["t_monde"], e["cycle"], d["option_ref"])
            assert key not in paid_stage8
            paid_stage8[key] = {
                "signature": d["learning_signature"],
                "status": d["status"],
                "learned_status": d["learned_value_status"],
                "learned_value": d["learned_value"],
                "simulated_status": d["simulated_value_status"],
                "simulated_value": d["simulated_value"],
                "evidence": d["evidence"],
            }
    # Real paid Competition trace, not inferred from any Stage8 value.
    paid_competition, frames, admissions = {}, {}, {}
    for event in events:
        kind, t, d = (event.get("kind"), event["t_monde"],
                      event.get("data", {}))
        if kind == "competition_cycle":
            k = (t, event["cycle"])
            assert k not in frames
            rows = {}
            for tr in d["traces"]:
                assert tr["option_ref"] not in rows and tr["threshold"] > 0
                assert all(isfinite(float(tr[x])) for x in (
                    "accumulator_before", "accumulator_after", "threshold"))
                if tr["evidence"] is not None:
                    assert isfinite(float(tr["evidence"]))
                    assert bool(tr["crossed"]) == (
                        tr["accumulator_after"] >= tr["threshold"])
                row = {
                    "evidence": tr["evidence"],
                    "ratio": tr["accumulator_after"] / tr["threshold"],
                    "crossed": bool(tr["crossed"]),
                }
                rows[tr["option_ref"]] = row
                joined = (t, event["cycle"], tr["option_ref"])
                assert joined not in paid_competition
                paid_competition[joined] = row
            frames[k] = rows
        elif kind == "command_admitted":
            assert t not in admissions
            admissions[t] = (d.get("option_ref"), d.get("primitive"))
    assert len(admissions) == len(applied)
    assert all(admissions[t][1] == applied[t] for t in applied)
    assert all(key in paid_competition
               for key, d in paid_stage8.items()
               if d["status"] == "evaluated"
               and d["learned_status"] == "learned"), (
        "paid learned Stage8 evaluation absent from Competition")
    # Presence of a command alone cannot be called an adjudicated win.
    decisions = {}
    for t, (ref, primitive) in admissions.items():
        prior = [(cycle, rows) for (step, cycle), rows in frames.items()
                 if step == t]
        if not prior:
            # Physical reflex pathway is permitted to bypass cognitive
            # deliberation. It is a real motor command, not a Competition
            # crossing or deliberative fallback.
            decisions[t] = {
                "option_ref": ref, "primitive": primitive,
                "admitted_crossed": False,
                "fallback_consistent": False,
                "no_competition_cycle": True,
            }
            continue
        final_cycle, rows = max(prior, key=lambda x: x[0])
        decisions[t] = {
            "option_ref": ref, "primitive": primitive,
            "admitted_crossed": bool(ref in rows and rows[ref]["crossed"]),
            "fallback_consistent": (final_cycle == rt.competition._config.c_max
                                   and not any(x["crossed"] for x in rows.values())),
            "no_competition_cycle": False,
        }
    # #438: replay only WAL ATTEMPT ORDER, not fabricated admissibility.
    # Stage3 admission events have no cognitive cycle; the most recent
    # authentic Competition cycle in this world step is their only anchor.
    control_steps = {}
    for ev in events:
        t, kind, d = ev["t_monde"], ev.get("kind"), ev.get("data", {})
        if kind == "competition_cycle":
            current = control_steps.setdefault(t, {
                "cycles": [], "attempts": [], "experienced": []})
            current["cycles"].append(ev["cycle"])
        elif kind in ("command_admitted", "command_vetoed"):
            current = control_steps.setdefault(t, {
                "cycles": [], "attempts": [], "experienced": []})
            current["attempts"].append({
                "cycle": current["cycles"][-1] if current["cycles"] else None,
                "ok": kind == "command_admitted",
                "source": d["source"],
                "option_ref": d.get("option_ref"),
                "primitive": d["primitive"],
                "scope": d.get("scope"),
                "reason": d.get("reason"),
            })
        elif kind == "command_experienced":
            control_steps.setdefault(t, {
                "cycles": [], "attempts": [], "experienced": []}
            )["experienced"].append(ev["primitive"])
    assert set(control_steps) == set(applied)
    custody = Counter()
    examples = []
    for step, row in sorted(control_steps.items()):
        attempts = row["attempts"]
        assert len(row["experienced"]) == 1
        accepted = [x for x in attempts if x["ok"]]
        assert len(accepted) == 1
        assert accepted[0] == attempts[-1]
        assert accepted[0]["primitive"] == row["experienced"][0]
        assert all(not x["ok"] for x in attempts[:-1])
        assert all(x["source"] in ("reflex", "decision", "sleep")
                   for x in attempts)
        if not row["cycles"]:
            # Stage10's already-committed sleep session admits each reduced
            # physical sleep step through Action Control WITHOUT reentering
            # Competition. This is not an unpriced reflex or a fallback.
            assert len(attempts) == 1
            assert attempts[0]["option_ref"] is None
            if attempts[0]["source"] == "sleep":
                assert attempts[0]["primitive"] == "dormir"
                assert any(e.get("kind") == "stage10_sleep_entered"
                           and e["t_monde"] <= step for e in events)
                custody["committed_sleep_steps"] += 1
            else:
                assert attempts[0]["source"] == "reflex"
                custody["reflex_applied_steps"] += 1
            continue
        assert len(row["cycles"]) == len(set(row["cycles"]))
        assert all(x["source"] == "decision" for x in attempts)
        assert accepted[0]["cycle"] == row["cycles"][-1]
        assert accepted[0]["option_ref"] == decisions[step]["option_ref"]
        final = frames[(step, row["cycles"][-1])]
        crossed = sorted(
            (ref for ref, tr in final.items() if tr["crossed"]),
            key=lambda ref: (- (final[ref]["ratio"] - 1.0), ref))
        # With no tie, lexical order is irrelevant. We inspect observed
        # vetoes and do not claim physical admissibility for untried options.
        if len({final[ref]["ratio"] for ref in crossed}) == len(crossed):
            attempted_crossed = [
                x["option_ref"] for x in attempts
                if x["option_ref"] in crossed]
            assert attempted_crossed == crossed[:len(attempted_crossed)]
        if accepted[0]["option_ref"] in crossed:
            custody["crossed_admitted_steps"] += 1
            custody["crossed_vetoes"] += sum(
                not x["ok"] and x["option_ref"] in crossed for x in attempts)
            custody["lower_ranked_admissions_after_veto"] += (
                accepted[0]["option_ref"] != crossed[0])
        else:
            assert row["cycles"][-1] == rt.competition._config.c_max
            custody["fallback_applied_steps"] += 1
        custody["total_vetoes"] += len(attempts) - 1
        examples.append({
            "step": step, "attempts": attempts,
            "crossed_count": len(crossed),
            "admitted_ref": accepted[0]["option_ref"],
            "top_crossed_ref": crossed[0] if crossed else None,
        })
    assert (custody["reflex_applied_steps"] +
            custody["committed_sleep_steps"] +
            custody["crossed_admitted_steps"] +
            custody["fallback_applied_steps"] == len(applied))

    assert td_events, "no TD publication despite ordinary natural decisions"
    for earlier, later in zip(td_snapshots, td_snapshots[1:]):
        for signature, count in earlier["update_counts"].items():
            assert later["update_counts"].get(signature, 0) >= count, (
                "TD owner lost a real update across M11 custody")
    local_effects = state["lived_site_effects"]
    route_offers = [e for e in events
                    if e.get("kind") == "i1_lived_site_option_proposed"]
    route_registrations = [e for e in events
                           if e.get("kind") == "i1_lived_site_option_registration"]
    route_competition = [
        (e["t_monde"], e["cycle"], tr)
        for e in events if e.get("kind") == "competition_cycle"
        for tr in e.get("data", {}).get("traces", ())
        if str(tr.get("option_ref", "")).startswith("option:lived-site:")
    ]

    # Observed candidate-window upper bound, using ONLY paid, actual cycles.
    # Ignore leakage/reset/residual to make a conservative ceiling; do not add
    # fictional extra deliberations, rewards or Q. This is external analysis.
    cfg = rt.competition._config
    assert cfg.noise_sigma == 0.0, "arithmetic replay assumes noiseless birth"
    windows = {}
    traced_keys = set()
    for step, cycle, trace in route_competition:
        key = (step, cycle, trace["option_ref"])
        assert key not in traced_keys and key in evaluations
        traced_keys.add(key)
        assessed = evaluations[key]
        assert assessed["status"] == "evaluated"
        assert assessed["learned_value_status"] == "unlearned"
        assert assessed["simulated_value_status"] != "computed"
        assert float(assessed["intrinsic_value"]) == 0.0
        evidence = trace["evidence"]
        assert evidence is not None and isfinite(float(evidence))
        assert abs(float(assessed["evidence"]) - evidence) < 1e-12
        assert all(isfinite(float(trace[name])) for name in (
            "accumulator_before", "accumulator_after", "threshold"))
        assert trace["threshold"] > 0
        assert type(cycle) is int and 1 <= cycle <= cfg.c_max
        urgency = (1.0 + (cfg.urgency_max - 1.0) *
                   (1.0 - exp(-(cycle - 1) / cfg.urgency_scale_cycles)))
        # Confirm that each observed physical trace obeys the actual,
        # untouched Competition recurrence. No candidate is re-evaluated here.
        expected = max(0.0, (1.0 - cfg.leak) *
                       trace["accumulator_before"] +
                       cfg.gain * urgency * evidence)
        assert abs(expected - trace["accumulator_after"]) < 1e-10
        assert bool(trace["crossed"]) == (
            trace["accumulator_after"] >= trace["threshold"])
        window = windows.setdefault(trace["option_ref"], {
            "paid_cycles": 0, "steps": set(),
            "first_before": float(trace["accumulator_before"]),
            "no_leak_positive_evidence_ceiling": 0.0,
            "min_paid_threshold": float("inf"),
            "peak_actual_threshold_ratio": 0.0,
        })
        window["paid_cycles"] += 1
        window["steps"].add(step)
        window["no_leak_positive_evidence_ceiling"] += (
            cfg.gain * urgency * max(0.0, float(evidence)))
        window["min_paid_threshold"] = min(
            window["min_paid_threshold"], float(trace["threshold"]))
        window["peak_actual_threshold_ratio"] = max(
            window["peak_actual_threshold_ratio"],
            float(trace["accumulator_after"] / trace["threshold"]))
    assert traced_keys == set(evaluations), (
        "spatial Stage8 and paid Competition windows do not match")
    assert windows, "no authentic spatial option exposure to study"
    candidate_windows = [
        {
            "ref": ref,
            "paid_cycles": window["paid_cycles"],
            "physical_steps": len(window["steps"]),
            "first_accumulator_zero": abs(window["first_before"]) < 1e-12,
            "positive_no_leak_ceiling_ratio": (
                window["no_leak_positive_evidence_ceiling"] /
                window["min_paid_threshold"]),
            "actual_peak_threshold_ratio": window["peak_actual_threshold_ratio"],
        }
        for ref, window in sorted(windows.items())
    ]
    bound_applicable = all(
        row["first_accumulator_zero"] for row in candidate_windows)
    # This is limited to the identities and opportunities already witnessed.
    # It says nothing about a future reoffer or a learned-Q-enabled route.
    exposure_limit = {
        "first_seen_from_zero": bound_applicable,
        "exact_noiseless_competition_arithmetic": True,
        "candidate_identities": len(candidate_windows),
        "paid_evaluations": sum(row["paid_cycles"] for row in candidate_windows),
        "max_paid_cycles_one_id": max(
            row["paid_cycles"] for row in candidate_windows),
        "max_physical_steps_one_id": max(
            row["physical_steps"] for row in candidate_windows),
        "max_actual_threshold_ratio": max(
            row["actual_peak_threshold_ratio"] for row in candidate_windows),
        "max_no_leak_positive_evidence_ratio": max(
            row["positive_no_leak_ceiling_ratio"] for row in candidate_windows),
        "recorded_cycles_insufficient_even_without_leak": (
            bound_applicable and all(
                row["positive_no_leak_ceiling_ratio"] < 1.0
                for row in candidate_windows)),
        "windows": candidate_windows,
        "future_unobserved_cycles": "NOT_ESTABLISHED",
    }
    # Distinguish candidate absence from low evidence in actual M11 owner
    # checkpoints. Neither missing candidate nor sleep implies why it left.
    transitions = []
    for before, after in zip(boundaries, boundaries[1:]):
        prior_ids, next_ids = set(before["ids"]), set(after["ids"])
        lost = prior_ids - next_ids
        transitions.append({
            "step": after["step"],
            "lost": len(lost),
            "new": len(next_ids - prior_ids),
            "retained": len(prior_ids & next_ids),
            "deadline_reached_indicator": sum(
                before["ids"][ref]["expires"] <= after["step"]
                for ref in lost),
        })
    owner_boundaries = {
        "physical_snapshots": len(boundaries),
        "snapshots_with_lived_candidate": sum(
            bool(boundary["ids"]) for boundary in boundaries),
        "lost_between_physical_steps": sum(t["lost"] for t in transitions),
        "new_between_physical_steps": sum(t["new"] for t in transitions),
        "retained_between_physical_steps": sum(
            t["retained"] for t in transitions),
        "deadline_reached_indicators": sum(
            t["deadline_reached_indicator"] for t in transitions),
        "no_absence_cause_inferred": True,
    }
    for event in route_offers:
        assert event["data"]["forced_motor_selection"] is False
        assert any(
            witness["t_monde"] < event["t_monde"]
            and tuple(witness["data"]["site"]) == tuple(event["data"]["target"])
            for witness in events if witness.get("kind")
                == "i1_lived_site_effect_observed"
        ), "return route without a first-person past site"
    witnessed = [e for e in events
                 if e.get("kind") == "i1_lived_site_effect_observed"]
    return {
        "food_gain": food_gain,
        "world_physics_version": physics.version,
        "only_food_gain_intervened": True,
        "first_local": first_local,
        "steps": bodies,
        "physical_commands": [applied[t] for t in sorted(applied)],
        "first_manger_step": next(
            (t for t in sorted(applied) if applied[t] == "manger"), None),
        "owner_site_effects": local_effects,
        "witnessed_site_changes": len(witnessed),
        "contextual_values": contextual,
        "spatial_eval_count": len(evaluations),
        "lived_site_route_offers": len(route_offers),
        "lived_site_route_registrations": len(route_registrations),
        "lived_site_competition_exposures": len(route_competition),
        "observed_candidate_windows": exposure_limit,
        "physical_owner_boundaries": owner_boundaries,
        "lived_site_threshold_crossings": sum(
            bool(row["crossed"]) for _, _, row in route_competition),
        "lived_site_motor_admissions": sum(
            e.get("kind") == "command_admitted"
            and str(e.get("data", {}).get("option_ref", "")).startswith(
                "option:lived-site:")
            for e in events),
        "td_update_counts": td_updates,
        "td_snapshots": td_snapshots,
        "td_events": td_events,
        "paid_stage8": paid_stage8,
        "paid_intrinsic": paid_intrinsic,
        "owner_goal_events": owner_goal_events,
        "producer_events": producer_events,
        "goal_unavailable_events": goal_unavailable_events,
        "frozen_sleep_by_step": frozen_sleep_by_step,
        "frozen_sleep_components": frozen_sleep_components,
        # P-40 belongs to Stage10, not to Stage11 Exploration P-15.
        "stage10_sleep_weight": rt._stage10_config.intrinsic_weight,
        "stage11_exploration_weight": rt._stage11_config.intrinsic_weight,
        "stage8_scale": rt.stage8_option_evaluator.config.evidence_scale,
        "stage8_extrinsic_gain": rt.stage8_option_evaluator.config.extrinsic_gain,
        "born_p40_fatigue_weight": rt.sleep_health.rules.config.fatigue_weight,
        "born_p40_consolidation_weight": rt.sleep_health.rules.config.consolidation_weight,
        "born_p40_night_weight": rt.sleep_health.rules.config.night_weight,
        "born_need_setpoints": dict(rt.value_needs.config.setpoints),
        "born_need_scales": dict(rt.value_needs.config.normalization_scales),
        "born_need_weights": dict(rt.value_needs.config.weights),
        "paid_competition": paid_competition,
        "paid_frames": frames,
        "physical_decisions": decisions,
        "action_control_custody": dict(custody),
        "action_control_examples": examples[:12],
        "ledger_status": ledger.status,
        "m11_generation": ledger.generation,
        "head_verified": True,
    }

with TemporaryDirectory(prefix="i1-434-m11-") as directory:
    # Two independent, never recovered lives with identical born individual
    # temperament. The physical intervention is hidden from the individual's
    # first-person capture until a genuine ingestion produces its consequence.
    neutral = experiment(0, Path(directory) / "neutral.sqlite")
    nourishing = experiment(10, Path(directory) / "nourishing.sqlite")

assert neutral["first_local"] == nourishing["first_local"], (
    "hidden food assignment leaked into a first-person birth capture")
assert neutral["world_physics_version"] == nourishing["world_physics_version"]
assert neutral["only_food_gain_intervened"] and nourishing[
    "only_food_gain_intervened"]
assert neutral["m11_generation"] and nourishing["m11_generation"]
first = neutral["first_manger_step"]
other = nourishing["first_manger_step"]
if first is not None and other is not None and first == other:
    # No divergence may precede the first real exposure of hidden nutrition.
    assert neutral["physical_commands"][:first] == (
        nourishing["physical_commands"][:first]
    ), "physical controls diverged before the first hidden food outcome"
    before_neutral = neutral["steps"][first - 1]["before"]
    before_nourish = nourishing["steps"][first - 1]["before"]
    assert before_neutral == before_nourish, (
        "matched bodies differ before hidden nutrition was experienced")
    neutral_gain = (neutral["steps"][first - 1]["after"]["food"]
                    - before_neutral["food"])
    nourish_gain = (nourishing["steps"][first - 1]["after"]["food"]
                    - before_nourish["food"])
    # The physical nutrition intervention is authenticated in the post-step
    # body, not presumed from the operator's treatment label alone.
    assert 9.999999 < nourish_gain - neutral_gain < 10.000001
    authenticated_exposure = True
else:
    authenticated_exposure = False

def keyed(contextual):
    return {(e["step"], e["cycle"], e["ref"]):e for e in contextual}

a,b = keyed(neutral["contextual_values"]),keyed(nourishing["contextual_values"])
paired_contexts = []
for key in sorted(a.keys() & b.keys()):
    left,right = a[key],b[key]
    paired_contexts.append({
        "step": key[0], "cycle": key[1],
        "delta_evidence": right["evidence"] - left["evidence"],
        "both_unlearned": left["learned"] == right["learned"] == "unlearned",
        "both_unsimulated": (
            left["simulated"] != "computed" and
            right["simulated"] != "computed"),
    })
future_motor_divergence = (
    None if not authenticated_exposure else
    neutral["physical_commands"][first:] !=
        nourishing["physical_commands"][first:]
)
# A difference in bodily effect is not automatically a causal attribution to
# the action by I1, a preference for better food, or a return to a known site.

# Report the actual TD response to the genuinely ingested food. The Q owner
# is inspected at real postcommit world boundaries, not scored on a fictional
# later input. Unoffered follow-up options remain NOT_EXPOSED.
def divergent_owner_steps(a, b):
    differences = []
    assert len(a) == len(b)
    for left, right in zip(a, b):
        assert left["step"] == right["step"]
        weights_a, weights_b = left["weights"], right["weights"]
        names = set(weights_a) | set(weights_b)
        mismatched = []
        for name in names:
            va, vb = weights_a.get(name), weights_b.get(name)
            if va is None or vb is None:
                mismatched.append(name)
                continue
            assert len(va) == len(vb)
            if any(abs(x - y) > 1e-12 for x, y in zip(va, vb)):
                mismatched.append(name)
        if mismatched:
            differences.append({
                "step": left["step"],
                "different_learned_signatures": len(mismatched),
                "manger_signature_different": any(
                    ":manger:" in sig for sig in mismatched),
            })
    return differences

td_owner_differences = divergent_owner_steps(
    neutral["td_snapshots"], nourishing["td_snapshots"])
assert not any(
    row["step"] < first for row in td_owner_differences
) if authenticated_exposure else True, (
    "TD owner changed before experience of hidden nutritional difference")
def td_by_decision(row):
    return {(u["decision_step"], u["previous_signature"],
             u["next_signature"], u["segment_length"]): u
            for u in row["td_events"]}
normal_td, nutritious_td = (
    td_by_decision(neutral), td_by_decision(nourishing))
common_td = []
for key in sorted(set(normal_td) & set(nutritious_td)):
    left, right = normal_td[key], nutritious_td[key]
    common_td.append({
        "decision_step": key[0],
        "previous_signature": key[1],
        "reward_return_delta": right["return_g"] - left["return_g"],
        "td_delta_difference": right["delta"] - left["delta"],
    })
assert all(isfinite(value) for row in common_td
           for value in (row["reward_return_delta"],
                         row["td_delta_difference"]))
def stage8_learned(row):
    return {(t, cycle, result["signature"]): result
            for (t, cycle, ref), result in row["paid_stage8"].items()
            if result["status"] == "evaluated"
            and result["learned_status"] == "learned"
            and result["learned_value"] is not None}
normal_reads, nutritious_reads = (
    stage8_learned(neutral), stage8_learned(nourishing))
paired_learned_reads = []
for key in sorted(set(normal_reads) & set(nutritious_reads)):
    x, y = normal_reads[key], nutritious_reads[key]
    paired_learned_reads.append({
        "step": key[0], "cycle": key[1], "signature": key[2],
        "learned_q_delta": y["learned_value"] - x["learned_value"],
        "evidence_delta": y["evidence"] - x["evidence"],
    })
# Only truly paid readbacks count. The same options may have had different
# learned weights without ever being proposed in subsequent lived time.
td_custody = {
    "actual_td_update_count_by_arm": (
        len(neutral["td_events"]), len(nourishing["td_events"])),
    "common_td_published_updates": len(common_td),
    "paired_reward_return_shift": any(
        abs(x["reward_return_delta"]) > 1e-12 for x in common_td
        if (not authenticated_exposure or
            x["decision_step"] > first)),
    "first_td_weight_divergence_step": (
        None if not td_owner_differences else
        td_owner_differences[0]["step"]),
    "different_q_signatures_at_boundaries": td_owner_differences[:12],
    "common_paid_learned_readbacks": len(paired_learned_reads),
    "paid_q_readback_shift": any(
        abs(x["learned_q_delta"]) > 1e-12 for x in paired_learned_reads),
    "paid_readbacks_first": paired_learned_reads[:8],
    "first_common_td_updates": common_td[:8],
    "physical_commands_unchanged": (
        neutral["physical_commands"] == nourishing["physical_commands"]),
    "learned_action_goal_outcome": "NOT_ESTABLISHED",
    "motor_learning_effect": "NOT_ESTABLISHED",
}


# Follow identical Stage8 option IDs through the ACTUAL paid Competition
# cycle and authenticated Action Control outcome. No options are replayed.
joined = []
for key in sorted(set(neutral["paid_stage8"]) &
                  set(nourishing["paid_stage8"]) &
                  set(neutral["paid_competition"]) &
                  set(nourishing["paid_competition"])):
    l, n = neutral["paid_stage8"][key], nourishing["paid_stage8"][key]
    cl = neutral["paid_competition"][key]
    cn = nourishing["paid_competition"][key]
    if (l["status"] != n["status"] or l["status"] != "evaluated"
        or l["learned_status"] != n["learned_status"]
        or l["learned_status"] != "learned"
        or l["signature"] != n["signature"]
        or l["learned_value"] is None or n["learned_value"] is None
        or l["evidence"] is None or n["evidence"] is None
        or cl["evidence"] is None or cn["evidence"] is None):
        continue
    joined.append({
        "step": key[0], "cycle": key[1], "option_ref": key[2],
        "signature": l["signature"],
        "delta_q": n["learned_value"] - l["learned_value"],
        "delta_competition": cn["evidence"] - cl["evidence"],
        "delta_threshold_ratio": cn["ratio"] - cl["ratio"],
        "max_threshold_ratio": max(cl["ratio"], cn["ratio"]),
        "same_stage8_competition": (
            abs(l["evidence"] - cl["evidence"]) < 1e-12
            and abs(n["evidence"] - cn["evidence"]) < 1e-12),
        "crossing_changed": cl["crossed"] != cn["crossed"],
    })
changed = [row for row in joined if abs(row["delta_q"]) > 1e-12]
assert authenticated_exposure and changed
assert all(row["step"] > first for row in changed)
assert all(row["same_stage8_competition"] for row in changed), (
    "changed learned Q did not retain identity into Competition")

# #438: observed paired Stage8 values have TWO potentially moving owners:
# learned TD/Q and Stage6 simulation on a body changed by the real ingestion.
# Retain both already-journaled ingredients at the exact paid option cycle.
# This is read-only attribution, NOT a forged evaluation or Q-only ablation.
paired_evidence_inputs = []
for item in changed:
    step, cycle, ref = item["step"], item["cycle"], item["option_ref"]
    key = (step, cycle, ref)
    left, right = neutral["paid_stage8"][key], nourishing["paid_stage8"][key]
    assert left["status"] == right["status"] == "evaluated"
    assert left["learned_status"] == right["learned_status"] == "learned"
    assert left["learned_value"] is not None
    assert right["learned_value"] is not None
    simulation_in_both = (
        left["simulated_status"] == right["simulated_status"] == "computed"
        and left["simulated_value"] is not None
        and right["simulated_value"] is not None
    )
    sim_delta = (
        float(right["simulated_value"]) - float(left["simulated_value"])
        if simulation_in_both else None
    )
    q_delta, evidence_delta = item["delta_q"], item["delta_competition"]
    signs_opposed = (
        abs(q_delta) > 1e-12 and abs(evidence_delta) > 1e-12
        and (q_delta > 0) != (evidence_delta > 0)
    )
    # Operator observations remain OUTSIDE first-person cognition.
    before_a = neutral["steps"][step - 1]["before"]
    before_b = nourishing["steps"][step - 1]["before"]
    body_delta = {
        name: float(before_b[name]) - float(before_a[name])
        for name in ("energy", "food", "water", "integrity")
    }
    paired_evidence_inputs.append({
        "step": step, "cycle": cycle, "option_ref": ref,
        "learning_signature": item["signature"],
        "delta_q": q_delta, "delta_competition": evidence_delta,
        "q_and_evidence_signs_opposed": signs_opposed,
        "simulated_status_neutral": left["simulated_status"],
        "simulated_status_nourishing": right["simulated_status"],
        "delta_simulated_value": sim_delta,
        "prestep_body_delta": body_delta,
        "physiology_differs": any(abs(x) > 1e-12
                                  for x in body_delta.values()),
    })
assert len(paired_evidence_inputs) == len(changed)
stage8_input_audit = {
    "exact_paid_q_changed_cases": len(paired_evidence_inputs),
    "q_and_competition_signs_opposed": sum(
        x["q_and_evidence_signs_opposed"] for x in paired_evidence_inputs),
    "simulation_computed_in_both": sum(
        x["delta_simulated_value"] is not None
        for x in paired_evidence_inputs),
    "simulated_values_changed": sum(
        x["delta_simulated_value"] is not None
        and abs(x["delta_simulated_value"]) > 1e-12
        for x in paired_evidence_inputs),
    "opposed_sign_with_simulation_shift": sum(
        x["q_and_evidence_signs_opposed"]
        and x["delta_simulated_value"] is not None
        and abs(x["delta_simulated_value"]) > 1e-12
        for x in paired_evidence_inputs),
    "cases_with_different_preaction_physiology": sum(
        x["physiology_differs"] for x in paired_evidence_inputs),
    "opposing_sign_examples": [
        x for x in paired_evidence_inputs
        if x["q_and_evidence_signs_opposed"]
    ][:6],
    "actual_decision_cycle_examples": [
        x for x in paired_evidence_inputs
        if (x["step"], x["cycle"]) in ((3, 4), (11, 3), (12, 3))
    ][:6],
    "isolated_q_only_motor_effect": "NOT_ESTABLISHED",
    "causal_owner_mutation": False,
}

# #438: inspect the already-journaled P-40 owner output at the same paid
# (step, cycle, option ID). This observer may CHECK arithmetic but may never
# supply an evaluation, replay cognition, or change a living individual's Q.
sleep_input_rows = []
for observation in paired_evidence_inputs:
    if observation["learning_signature"] != "primitive:dormir":
        continue
    key = (observation["step"], observation["cycle"],
           observation["option_ref"])
    both_arms = []
    for label, arm in (("neutral", neutral), ("nourishing", nourishing)):
        read = arm["paid_stage8"][key]
        intrinsic = arm["paid_intrinsic"].get(key)
        assert intrinsic is not None, "no real P-40 intrinsic record"
        assert intrinsic["status"] == "evaluated"
        assert intrinsic["intrinsic_value"] is not None
        assert "metacognition_health:p40_sleep_pressure" in intrinsic["producers"]
        assert abs(intrinsic["intrinsic_weight"] -
                   arm["stage11_exploration_weight"]) < 1e-12
        # The generic Stage11 event's P15 weight is for Exploration.
        # Sleep itself is assembled by Stage10's separate born weight.
        frozen_p40 = arm["frozen_sleep_by_step"].get(key[0])
        assert frozen_p40 is not None, "missing actual frozen P-40 step receipt"
        assert abs(intrinsic["intrinsic_value"] - frozen_p40) < 1e-12, (
            "sleep intrinsic assessment differs from P-40 frozen value")
        assert read["simulated_status"] == "unavailable"
        assert read["learned_status"] == "learned"
        assert read["learned_value"] is not None
        assert read["signature"] == "primitive:dormir"
        extrinsic = max(-1.0, min(1.0,
            arm["stage8_extrinsic_gain"] *
            tanh(read["learned_value"] / arm["stage8_scale"])))
        p40_component = (
            arm["stage10_sleep_weight"] * intrinsic["intrinsic_value"])
        reconstructed = max(-1.0, min(1.0, extrinsic + p40_component))
        actual = arm["paid_competition"][key]["evidence"]
        assert actual is not None and isfinite(float(actual))
        assert abs(actual - reconstructed) < 1e-10, (
            f"paid sleep evidence mismatch step={key[0]} cycle={key[1]}"
            f" arm={label} actual={actual} expected={reconstructed}"
            f" Q_component={extrinsic} P40_component={p40_component}"
            f" stage10_weight={arm['stage10_sleep_weight']}"
            f" stage11_exploration_weight={intrinsic['intrinsic_weight']}")
        both_arms.append({
            "arm": label, "q_extrinsic": extrinsic,
            "p40_intrinsic": p40_component, "competition_evidence": actual,
        })
    left, right = both_arms
    delta_q_extrinsic = right["q_extrinsic"] - left["q_extrinsic"]
    delta_p40 = right["p40_intrinsic"] - left["p40_intrinsic"]
    delta_competition = (right["competition_evidence"] -
                         left["competition_evidence"])
    assert abs(delta_q_extrinsic + delta_p40 - delta_competition) < 1e-10
    sleep_input_rows.append({
        "step": key[0], "cycle": key[1], "option_ref": key[2],
        "delta_q_extrinsic": delta_q_extrinsic,
        "delta_p40_intrinsic": delta_p40,
        "delta_competition_evidence": delta_competition,
        "baseline_q_extrinsic": left["q_extrinsic"],
        "baseline_p40_intrinsic": left["p40_intrinsic"],
        "nourishing_q_extrinsic": right["q_extrinsic"],
        "nourishing_p40_intrinsic": right["p40_intrinsic"],
    })
assert sleep_input_rows
assert len(sleep_input_rows) == sum(
    x["learning_signature"] == "primitive:dormir"
    for x in paired_evidence_inputs)
sleep_input_audit = {
    "exact_paid_sleep_cases": len(sleep_input_rows),
    "all_component_identities_verified": True,
    "distinct_real_intrinsic_weights": {
        "stage10_sleep": neutral["stage10_sleep_weight"],
        "stage11_exploration": neutral["stage11_exploration_weight"],
    },
    "frozen_p40_step_receipts_verified": len(sleep_input_rows),
    "opposing_q_and_p40_shifts": sum(
        x["delta_q_extrinsic"] * x["delta_p40_intrinsic"] < 0
        for x in sleep_input_rows),
    "cases_with_competition_opposite_to_q_extrinsic": sum(
        abs(x["delta_q_extrinsic"]) > 1e-12
        and abs(x["delta_competition_evidence"]) > 1e-12
        and ((x["delta_q_extrinsic"] > 0)
             != (x["delta_competition_evidence"] > 0))
        for x in sleep_input_rows),
    "rows": sleep_input_rows,
    "q_only_motor_effect": "NOT_ESTABLISHED",
}

a = neutral["physical_decisions"]
b = nourishing["physical_decisions"]
assert set(a) == set(b)
frames = set(neutral["paid_frames"]) & set(nourishing["paid_frames"])
def nearest(rows):
    scored = [(row["ratio"], ref) for ref, row in rows.items()
              if row["evidence"] is not None]
    return max(scored)[1] if scored else None

# #438: identify genuine same-cycle contender sets, not hypothetical choices.
# A Q-bearing alternative exists only if its own paid Stage8 and Competition
# records agree at the exact physical step / cognitive cycle.
def contender_audit(life):
    counters = Counter()
    rows = []
    for (step, cycle), traces in sorted(life["paid_frames"].items()):
        paid = []
        for ref, tr in sorted(traces.items()):
            read = life["paid_stage8"].get((step, cycle, ref))
            if (read is None or read["status"] != "evaluated"
                or tr["evidence"] is None):
                continue
            assert abs(read["evidence"] - tr["evidence"]) < 1e-12
            paid.append((ref, tr, read))
        learned = [(ref, tr, read) for ref, tr, read in paid
                   if read["learned_status"] == "learned"
                   and read["learned_value"] is not None]
        positive = [(ref, tr, read) for ref, tr, read in paid
                    if tr["evidence"] > 0]
        crossed = [(ref, tr, read) for ref, tr, read in paid
                   if tr["crossed"]]
        counters["cycles"] += 1
        counters["with_paid_candidates"] += bool(paid)
        counters["with_multiple_paid_candidates"] += len(paid) >= 2
        counters["with_any_learned"] += bool(learned)
        counters["with_two_learned"] += len(learned) >= 2
        counters["with_learned_and_positive_rival"] += (
            bool(learned) and any(ref not in {x[0] for x in learned}
                                  for ref, _, _ in positive))
        counters["with_learning_and_crossed_rival"] += (
            bool(learned) and any(ref not in {x[0] for x in learned}
                                  for ref, _, _ in crossed))
        rows.append({
            "step": step, "cycle": cycle,
            "paid_options": len(paid), "learned": len(learned),
            "positive": len(positive), "crossed": len(crossed),
            "learned_signatures": tuple(sorted({
                read["signature"] for _, _, read in learned})),
            "crossed_option_refs": tuple(sorted(x[0] for x in crossed)),
        })
    return dict(sorted(counters.items())), rows

neutral_overlap, neutral_rows = contender_audit(neutral)
nutritious_overlap, nutritious_rows = contender_audit(nourishing)
changed_cycles = sorted({(row["step"], row["cycle"]) for row in changed})
assert changed_cycles
affected_contexts = []
for step, cycle in changed_cycles:
    n = next(x for x in neutral_rows
             if x["step"] == step and x["cycle"] == cycle)
    f = next(x for x in nutritious_rows
             if x["step"] == step and x["cycle"] == cycle)
    affected_contexts.append({
        "step": step, "cycle": cycle,
        "neutral_learned_options": n["learned"],
        "nourishing_learned_options": f["learned"],
        "neutral_paid_options": n["paid_options"],
        "nourishing_paid_options": f["paid_options"],
        "neutral_crossed": n["crossed"],
        "nourishing_crossed": f["crossed"],
    })
overlap_diagnostic = {
    "neutral": neutral_overlap,
    "nourishing": nutritious_overlap,
    "changed_q_cycle_count": len(changed_cycles),
    "changed_q_cycles_with_two_learned": sum(
        x["neutral_learned_options"] >= 2
        and x["nourishing_learned_options"] >= 2
        for x in affected_contexts),
    "changed_q_cycles_with_at_least_two_paid": sum(
        x["neutral_paid_options"] >= 2
        and x["nourishing_paid_options"] >= 2
        for x in affected_contexts),
    "changed_q_cycle_context_first": affected_contexts[:20],
    "physical_admissibility_of_every_competitor": "NOT_ESTABLISHED",
    "independent_effect_of_q_on_motor_choice": "NOT_ESTABLISHED",
    "scientific_l3": "NOT_ESTABLISHED",
}


# #438 follow-up: measure only the exact paid (step, cycle, option ID)
# where BOTH actual Stage8 and Competition verified a changed Q readback.
# Do not count a candidate's earlier/later cycles based on option-ID reuse.
margin_rows = []
margin_pairs = []
for row in changed:
    step, cycle, ref = row["step"], row["cycle"], row["option_ref"]
    two_arms = []
    for treatment, life in (("neutral", neutral), ("nourishing", nourishing)):
        exact = (step, cycle, ref)
        tr = life["paid_competition"][exact]
        read = life["paid_stage8"][exact]
        assert read["status"] == "evaluated"
        assert read["learned_status"] == "learned"
        assert read["learned_value"] is not None
        same = life["paid_frames"][(step, cycle)]
        assert same[ref] == tr
        competitors = []
        for rival_ref, rival in same.items():
            if rival_ref == ref or rival["evidence"] is None:
                continue
            rival_read = life["paid_stage8"].get((step, cycle, rival_ref))
            assert rival_read is not None and rival_read["status"] == "evaluated"
            assert abs(rival_read["evidence"] - rival["evidence"]) < 1e-12
            competitors.append((rival_ref, rival))
        if not competitors:
            measured = {
                "arm": treatment, "step": step, "cycle": cycle,
                "option_ref": ref, "category": "no_paid_rival",
            }
        else:
            best_ref, best = max(
                competitors, key=lambda item: (item[1]["ratio"], item[0]))
            margin = tr["ratio"] - best["ratio"]
            assert isfinite(margin)
            measured = {
                "arm": treatment, "step": step, "cycle": cycle,
                "option_ref": ref, "best_rival": best_ref,
                "rank_margin": margin, "own_ratio": tr["ratio"],
                "rival_ratio": best["ratio"],
                "own_crossed": tr["crossed"],
                "rival_crossed": best["crossed"],
                "category": ("ahead" if margin > 1e-12
                             else "tied" if abs(margin) <= 1e-12
                             else "behind"),
            }
        two_arms.append(measured)
        margin_rows.append(measured)
    neutral_row, nourishing_row = two_arms
    if (neutral_row["category"] == "no_paid_rival"
        or nourishing_row["category"] == "no_paid_rival"):
        comparable = False
    else:
        comparable = True
    margin_pairs.append({
        "step": step, "cycle": cycle, "option_ref": ref,
        "comparable": comparable,
        "best_rival_changed": (
            neutral_row.get("best_rival") != nourishing_row.get("best_rival")),
        "margin_shift": (
            nourishing_row["rank_margin"] - neutral_row["rank_margin"]
            if comparable else None),
        "position_changed": (
            neutral_row["category"] != nourishing_row["category"]),
    })
# Each changed-Q value was genuinely paid once per arm at precisely its own
# cycle; unrelated uses of the same option ID are forbidden by construction.
assert len(margin_rows) == 2 * len(changed)
assert len({(row["arm"], row["step"], row["cycle"], row["option_ref"])
            for row in margin_rows}) == len(margin_rows)
unique_margins = margin_rows

margin_audit = {
    "actual_paid_candidate_arm_observations": len(unique_margins),
    "paired_exact_changed_q_evaluations": len(margin_pairs),
    "paired_rank_position_changes": sum(row["position_changed"]
                                        for row in margin_pairs),
    "paired_best_rival_identity_changes": sum(row["best_rival_changed"]
                                             for row in margin_pairs),
    "max_absolute_paired_margin_shift": max(
        (abs(row["margin_shift"]) for row in margin_pairs
         if row["comparable"]), default=0.0),
    "with_rival": sum(r["category"] != "no_paid_rival"
                      for r in unique_margins),
    "ahead": sum(r["category"] == "ahead" for r in unique_margins),
    "behind": sum(r["category"] == "behind" for r in unique_margins),
    "tied": sum(r["category"] == "tied" for r in unique_margins),
    "no_paid_rival": sum(r["category"] == "no_paid_rival"
                        for r in unique_margins),
    "behind_despite_own_crossing": sum(
        r["category"] == "behind" and r["own_crossed"]
        for r in unique_margins),
    "max_observed_deficit": max(
        (-r["rank_margin"] for r in unique_margins
         if r["category"] == "behind"), default=0.0),
    "smallest_positive_deficit": min(
        (-r["rank_margin"] for r in unique_margins
         if r["category"] == "behind"), default=None),
    "first_observations": unique_margins[:24],
    "physical_admissibility_of_rivals": "NOT_ESTABLISHED",
    "learned_td_caused_motor_choice": "NOT_ESTABLISHED",
}

# #453: join only real owner-published GoalManager changes and real option
# producer events. An awake motor primitive alone proves no vital motive.
motive_custody_rows = []
for label, arm in (("neutral", neutral), ("nourishing", nourishing)):
    owner_changes = arm["owner_goal_events"]
    producer_events = arm["producer_events"]
    for step in sorted(arm["physical_decisions"]):
        paid_cycles = sorted(c for t, c in arm["paid_frames"] if t == step)
        if not paid_cycles:
            continue
        cycle = paid_cycles[-1]
        decision = arm["physical_decisions"][step]
        admitted_ref = decision["option_ref"]
        # GoalManager runs earlier than ordinary Competition in every
        # cognitive cycle; only prior owner changes may apply.
        history = sorted(
            (clock, goal) for clock, goal in owner_changes.items()
            if clock <= (step, cycle))
        active = None if not history else history[-1][1]
        if active is not None:
            assert active["state"] == "active"
        exact_producer = [
            (clock, data) for clock, data in producer_events.items()
            if clock[0] == step and clock[2] == admitted_ref
            and clock[1] <= cycle
        ]
        actual_producer = (
            max(exact_producer, key=lambda x: x[0][1])[1]
            if exact_producer else None)
        matching_sleep = (
            (step, cycle, admitted_ref) in arm["paid_stage8"]
            and admitted_ref is not None
            and admitted_ref.startswith("option:sleep-pressure:")
            and arm["paid_stage8"][(step, cycle, admitted_ref)][
                "signature"] == "primitive:dormir")
        if matching_sleep:
            motive = "owner_frozen_sleep"
            assert decision["primitive"] == "dormir"
        elif actual_producer is not None:
            if actual_producer["event_kind"] == "i1_local_opportunity_proposed":
                assert actual_producer["goal_ref"] is None
                motive = "independent_local_opportunity"
            else:
                motive = ("goal_attached_affordance"
                          if actual_producer["goal_ref"] is not None
                          else "unaffiliated_affordance")
        else:
            motive = "not_attributed_by_these_producers"
        needs = real_need_pressures(arm, step)
        top = max(needs, key=needs.get)
        owner_goal_type = None if active is None else active["goal_type"]
        owner_target = None if active is None else active["target"]
        producer_goal_ref = (
            None if actual_producer is None
            else actual_producer["goal_ref"])
        # A producer goal reference is not an inherited command; for an
        # attached option, verify exact identity where it is current.
        if motive == "goal_attached_affordance":
            assert producer_goal_ref is not None
            assert active is not None
            assert producer_goal_ref == active["id"]
        motive_custody_rows.append({
            "arm": label, "step": step, "cycle": cycle,
            "admitted_option_ref": admitted_ref,
            "primitive": decision["primitive"],
            "owner_goal_type": owner_goal_type,
            "owner_target": owner_target,
            "largest_need_channel": top,
            "largest_need_pressure": needs[top],
            "active_goal_matches_largest_need": owner_target == top,
            "motive_class": motive,
            "producer_goal_ref": producer_goal_ref,
            "admitted_crossed": decision["admitted_crossed"],
        })
assert len(motive_custody_rows) == sum(
    any(t == step for t, _ in arm["paid_frames"])
    for arm in (neutral, nourishing)
    for step in arm["physical_decisions"])
motive_custody_audit = {
    "actual_waking_decisions": len(motive_custody_rows),
    "with_owner_goal": sum(x["owner_goal_type"] is not None
                           for x in motive_custody_rows),
    "owner_goal_different_from_max_pressure": sum(
        x["owner_goal_type"] is not None
        and not x["active_goal_matches_largest_need"]
        for x in motive_custody_rows),
    "independent_local_opportunity_admissions": sum(
        x["motive_class"] == "independent_local_opportunity"
        for x in motive_custody_rows),
    "goal_attached_affordance_admissions": sum(
        x["motive_class"] == "goal_attached_affordance"
        for x in motive_custody_rows),
    "sleep_owner_admissions": sum(
        x["motive_class"] == "owner_frozen_sleep"
        for x in motive_custody_rows),
    "not_attributed_admissions": sum(
        x["motive_class"] == "not_attributed_by_these_producers"
        for x in motive_custody_rows),
    "examples": motive_custody_rows,
    "goal_match_does_not_prove_need_was_satisfied": True,
    "learned_q_caused_action": "NOT_ESTABLISHED",
    "scientific_l3": "NOT_ESTABLISHED",
}

# #451: pre-existing natural cycles only. Sleep is an ordinary paid option
# competing against other candidates, never a source of mandatory action.
# Diagnostic body pressures are recalculated outside the agent from its
# immutable, actually born Stage4 formula and pre-action body, not proposed
# as a goal and never sent back to Competition.
def real_need_pressures(arm, step):
    before = arm["steps"][step - 1]["before"]
    maximum = max(arm["born_need_weights"].values(), default=0.0)
    return {
        name: max(0.0, min(1.0,
            (arm["born_need_weights"][name] / maximum if maximum > 0 else 0.0)
            * max(0.0, min(1.0,
                (float(before[name]) - arm["born_need_setpoints"][name])
                / -arm["born_need_scales"][name]))))
        for name in ("energy", "food", "water", "integrity")
    }

sleep_need_cycles = []
for label, arm in (("neutral", neutral), ("nourishing", nourishing)):
    for (step, cycle), candidates in sorted(arm["paid_frames"].items()):
        sleep_refs = [
            ref for ref in candidates
            if arm["paid_stage8"].get((step, cycle, ref), {}).get(
                "signature") == "primitive:dormir"
            and ref.startswith("option:sleep-pressure:")
        ]
        if not sleep_refs:
            continue
        assert len(sleep_refs) == 1
        sleep_ref = sleep_refs[0]
        sleep_trace = candidates[sleep_ref]
        assessed = arm["paid_intrinsic"].get((step, cycle, sleep_ref))
        assert assessed is not None and assessed["status"] == "evaluated"
        assert "metacognition_health:p40_sleep_pressure" in assessed["producers"]
        frozen = arm["frozen_sleep_components"][step]
        p40 = arm["frozen_sleep_by_step"][step]
        # Reconstruct P-40 from the same actual step's night clock and born
        # coefficients. No physiological channel is part of this intrinsic.
        actual_night = arm["steps"][step - 1]["is_night_at_step"]
        assert type(actual_night) is bool
        weighted_awake = (
            arm["born_p40_fatigue_weight"] * frozen["fatigue"]
            + arm["born_p40_consolidation_weight"] *
              frozen["consolidation_pressure"]
        )
        is_night_component = (
            arm["born_p40_night_weight"] if actual_night else 0.0)
        reconstructed_p40 = min(1.0, weighted_awake + is_night_component)
        assert abs(reconstructed_p40 - p40) < 1e-12, (
            "frozen P40 differs from actual night/fatigue/consolidation")
        assert abs(assessed["intrinsic_value"] - p40) < 1e-12
        need_pressures = real_need_pressures(arm, step)
        rivals = [
            (ref, tr) for ref, tr in candidates.items()
            if ref != sleep_ref and tr["evidence"] is not None
        ]
        # Only the LAST paid cognitive cycle can be associated with the
        # single physical action at this world step. Earlier cycles remain
        # valid competition observations, not extra motor admissions.
        final_cycle = max(c for (t, c) in arm["paid_frames"] if t == step)
        is_final_cycle = cycle == final_cycle
        admitted = (
            arm["physical_decisions"].get(step) if is_final_cycle else None)
        sleep_need_cycles.append({
            "arm": label, "step": step, "cycle": cycle,
            "p40": p40,
            "p40_fatigue": frozen["fatigue"],
            "p40_consolidation": frozen["consolidation_pressure"],
            "p40_exact_night_term": is_night_component,
            "is_night": actual_night,
            "is_final_paid_cycle": is_final_cycle,
            "need_pressures": need_pressures,
            "top_need": max(need_pressures, key=need_pressures.get),
            "max_need_pressure": max(need_pressures.values()),
            "sleep_crossed": sleep_trace["crossed"],
            "sleep_ratio": sleep_trace["ratio"],
            "awake_rival_count": len(rivals),
            "awake_crossed_count": sum(tr["crossed"] for _, tr in rivals),
            "awake_top_ratio": max((tr["ratio"] for _, tr in rivals),
                                    default=None),
            "admitted_primitive": None if admitted is None else admitted["primitive"],
            "admitted_from_competition": (
                admitted is not None and admitted["admitted_crossed"]),
            "sleep_admitted": (admitted is not None
                               and admitted["option_ref"] == sleep_ref),
        })
assert sleep_need_cycles, "no paid sleep vs waking opportunity in natural M11"
# Absence of an awake competitor is evidence of missing choice exposure,
# never a reason to silently discard an authentic paid sleep cycle.
# Preserve undecided cases rather than inferring that any rival was physically
# admissible, or that same-step choices before final cycle were applied.
sleep_need_audit = {
    "actual_paid_sleep_cycles": len(sleep_need_cycles),
    "distinct_awake_physical_steps": len({
        (x["arm"], x["step"]) for x in sleep_need_cycles}),
    "with_awake_rival": sum(x["awake_rival_count"] > 0
                            for x in sleep_need_cycles),
    "without_awake_rival": sum(x["awake_rival_count"] == 0
                               for x in sleep_need_cycles),
    "physical_decisions_counted_once": sum(
        x["is_final_paid_cycle"] for x in sleep_need_cycles),
    "with_crossed_awake_rival": sum(x["awake_crossed_count"] > 0
                                   for x in sleep_need_cycles),
    "awake_admitted_with_sleep_available": sum(
        x["admitted_primitive"] not in (None, "dormir")
        and x["admitted_from_competition"] for x in sleep_need_cycles),
    "sleep_admitted_with_awake_rival": sum(
        x["sleep_admitted"] and x["awake_rival_count"] > 0
        for x in sleep_need_cycles),
    "max_need_pressure_observed": max(
        x["max_need_pressure"] for x in sleep_need_cycles),
    "examples": sleep_need_cycles[:24],
    "paired_sleep_q_changes": sum(
        x["learning_signature"] == "primitive:dormir"
        for x in paired_evidence_inputs),
    "paired_sleep_q_changes_with_matched_p40": sum(
        x["learning_signature"] == "primitive:dormir"
        and abs(neutral["frozen_sleep_by_step"][x["step"]]
                - nourishing["frozen_sleep_by_step"][x["step"]]) < 1e-12
        for x in paired_evidence_inputs),
    "matched_p40_q_only_motor_effect": "NOT_ESTABLISHED",
    "emergency_priority_in_all_possible_worlds": "NOT_ESTABLISHED",
    "scientific_l3": "NOT_ESTABLISHED",
}

adjudication = {
    "matched_paid_learned_options": len(joined),
    "changed_q_through_competition": len(changed),
    "distinct_affected_option_ids": len(set(
        row["option_ref"] for row in changed)),
    "changed_signatures": dict(sorted(Counter(
        row["signature"] for row in changed).items())),
    "max_delta_competition_evidence": max(
        abs(row["delta_competition"]) for row in changed),
    "max_delta_threshold_ratio": max(
        abs(row["delta_threshold_ratio"]) for row in changed),
    "highest_actual_threshold_ratio_affected": max(
        row["max_threshold_ratio"] for row in changed),
    "affected_crossing_changes": sum(
        row["crossing_changed"] for row in changed),
    "matched_paid_cycles": len(frames),
    "threshold_proximity_leader_changed": sum(
        nearest(neutral["paid_frames"][k]) !=
        nearest(nourishing["paid_frames"][k]) for k in frames),
    "admitted_option_id_changed_after_exposure": sum(
        a[t]["option_ref"] != b[t]["option_ref"] for t in a if t > first),
    "neutral_reflex_or_no_competition_steps": sum(
        d["no_competition_cycle"] for d in a.values()),
    "nourishing_reflex_or_no_competition_steps": sum(
        d["no_competition_cycle"] for d in b.values()),
    "neutral_adjudicated_admissions": sum(
        d["admitted_crossed"] for d in a.values()),
    "nourishing_adjudicated_admissions": sum(
        d["admitted_crossed"] for d in b.values()),
    "neutral_fallback_consistent_steps": sum(
        d["fallback_consistent"] for d in a.values()),
    "nourishing_fallback_consistent_steps": sum(
        d["fallback_consistent"] for d in b.values()),
    "no_motor_intervention": True,
    "motor_learning_improvement": "NOT_ESTABLISHED",
    "scientific_l3": "NOT_ESTABLISHED",
}

report = {
    "preset": "dry-valley",
    "preset_sha256": preset_digest,
    "physical_intervention": "berry_a_food_gain_only",
    "identical_physics_version": True,
    "same_first_person_birth_perception": True,
    "authentic_same_step_ingestion": authenticated_exposure,
    "first_ingestion_step": first if authenticated_exposure else None,
    "neutral": {k:v for k,v in neutral.items()
                if k not in ("owner_goal_events", "producer_events", "goal_unavailable_events", "paid_intrinsic", "frozen_sleep_by_step", "frozen_sleep_components", "first_local", "steps", "contextual_values",
                             "td_snapshots", "td_events", "paid_stage8",
                             "paid_competition", "paid_frames",
                             "physical_decisions")},
    "nourishing": {k:v for k,v in nourishing.items()
                  if k not in ("owner_goal_events", "producer_events", "goal_unavailable_events", "paid_intrinsic", "frozen_sleep_by_step", "frozen_sleep_components", "first_local", "steps", "contextual_values",
                               "td_snapshots", "td_events", "paid_stage8",
                               "paid_competition", "paid_frames",
                               "physical_decisions")},
    "common_postexperience_context_evaluations": len(paired_contexts),
    "paired_context_deltas": paired_contexts[:12],
    "context_shift_observed": any(
        abs(item["delta_evidence"]) > 1e-12
        for item in paired_contexts if (
            item["both_unlearned"] and item["both_unsimulated"])),
    "postexperience_motor_trajectories_differ": future_motor_divergence,
    "paired_td_custody": td_custody,
    "paired_stage8_mixed_input_audit": stage8_input_audit,
    "paired_sleep_intrinsic_decomposition": sleep_input_audit,
    "observed_sleep_needs_competition_451": sleep_need_audit,
    "owner_motive_custody_453": motive_custody_audit,
    "paired_td_competition_adjudication": adjudication,
    "paired_action_control_custody": {
        "neutral": neutral["action_control_custody"],
        "nourishing": nourishing["action_control_custody"],
        "neutral_observed_attempts": neutral["action_control_examples"],
        "nourishing_observed_attempts": nourishing["action_control_examples"],
        "unattempted_rival_admissibility": "NOT_ESTABLISHED",
        "learning_caused_motor_choice": "NOT_ESTABLISHED",
    },
    "paired_learned_contender_overlap": overlap_diagnostic,
    "paid_learned_competitor_margins": margin_audit,
    "paired_candidate_identities_match": (
        [r["ref"] for r in neutral["observed_candidate_windows"]["windows"]]
        == [r["ref"] for r in
            nourishing["observed_candidate_windows"]["windows"]]),
    "causal_action_attribution": "NOT_ESTABLISHED",
    "spatially_useful_decision": "NOT_ESTABLISHED",
    "scientific_l3": "NOT_ESTABLISHED",
}
print("I1_434_NATURAL_M11_SITE_REOFFER_MATCHED "
      + json.dumps(report, sort_keys=True), flush=True)
assert neutral["head_verified"] and nourishing["head_verified"]
print("I1_434_INDEPENDENT_MORTAL_WAL_OK", flush=True)
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(generated), str(ROOT / "src"), str(ROOT / "tools"))),
                PYTHONDONTWRITEBYTECODE="1")
            outcome = subprocess.run(
                [sys.executable, "-B", "-c", script],
                cwd=ROOT, env=env, text=True, capture_output=True)
            print(outcome.stdout, flush=True)
            if outcome.returncode:
                print(outcome.stderr, flush=True)
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            self.assertIn("I1_434_INDEPENDENT_MORTAL_WAL_OK", outcome.stdout)


if __name__ == "__main__":
    unittest.main()
