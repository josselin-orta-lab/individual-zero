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
from math import exp, isfinite
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
    for e in events:
        d = e.get("data", {})
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
        elif e.get("kind") == "stage8_option_evaluation":
            key = (e["t_monde"], e["cycle"], d["option_ref"])
            assert key not in paid_stage8
            paid_stage8[key] = {
                "signature": d["learning_signature"],
                "status": d["status"],
                "learned_status": d["learned_value_status"],
                "learned_value": d["learned_value"],
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
        "paid_competition": paid_competition,
        "paid_frames": frames,
        "physical_decisions": decisions,
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
        "step": key[0], "option_ref": key[2],
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
changed_cycles = sorted({(x["step"], cycle) for x in changed
                         for (step, cycle, ref) in neutral["paid_competition"]
                         if step == x["step"] and ref == x["option_ref"]
                         and (step, cycle, ref) in nourishing["paid_competition"]
                         and (step, cycle, ref) in neutral["paid_stage8"]
                         and (step, cycle, ref) in nourishing["paid_stage8"]
                         and abs(neutral["paid_stage8"][(step,cycle,ref)]["learned_value"]
                                 - nourishing["paid_stage8"][(step,cycle,ref)]["learned_value"]) > 1e-12
                         })
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
                if k not in ("first_local", "steps", "contextual_values",
                             "td_snapshots", "td_events", "paid_stage8",
                             "paid_competition", "paid_frames",
                             "physical_decisions")},
    "nourishing": {k:v for k,v in nourishing.items()
                  if k not in ("first_local", "steps", "contextual_values",
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
    "paired_td_competition_adjudication": adjudication,
    "paired_learned_contender_overlap": overlap_diagnostic,
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
