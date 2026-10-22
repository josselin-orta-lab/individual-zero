"""Canonical short technical life: personally experienced site, later movement, M11.

This is not a population study. An absent spontaneous sequence is counted rather
than repaired by scripting an action, memory, reward, or motor authorization.
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


class NaturalLivedSiteEvidence(unittest.TestCase):
    def test_short_dry_valley_perception_and_cold_m11(self):
        with TemporaryDirectory(prefix="i1-388-") as directory:
            generated = Path(directory) / "generated"
            generate(generated)
            program = r"""
import json
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

preset, _ = load_preset("dry-valley")
params, _ = _birth_parameters(preset)
params = dict(params, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
identity = "i1:387:dry-valley-lived-site"
TOTAL, SPLIT = 12, 6

def factory():
    return I1Runtime(birth_life_id=identity, wal_path=None,
        autonomous_mortal=True, m11_sqlite_custody=True, **params)

def causal(rt):
    return {owner.owner_id: owner.export_causal_state()
            for owner in rt.causal_owners}

def journal(rt):
    return [dict(entry.causal_event) for entry in rt.journal.entries_since(0)]

def committed_steps(actor, n):
    receipts, locations = [], []
    for unused in range(n):
        receipt = actor.run_step()
        assert receipt.status == "active", ("individual did not survive", receipt)
        receipts.append((receipt.generation, receipt.world_step,
                         receipt.journal_head, receipt.outcome))
        image = actor._runtime.exploration.geographic.export_causal_state()
        capture = image["last_capture"]
        locations.append({
            "world_step": capture[0], "position": tuple(capture[1:]),
            "older_remote_lived_sites": tuple(sorted(
                tuple(site["position"]) for site in image["lived_site_effects"]
                if (site["last_observed_step"] < capture[0]
                    and tuple(site["position"]) != tuple(capture[1:])))),
        })
    return receipts, locations

with TemporaryDirectory(prefix="i1-388-cold-") as directory:
    uninterrupted = str(Path(directory) / "uninterrupted.sqlite")
    recovered = str(Path(directory) / "recovered.sqlite")
    with birth_i1_m11(db_path=uninterrupted, life_id=identity, **params) as actor:
        all_receipts, all_locations = committed_steps(actor, TOTAL)
        final_owners = causal(actor._runtime)
        final_geo = actor._runtime.exploration.geographic.export_causal_state()
        all_events = journal(actor._runtime)
        # Immutable born Competition constants, read only by the external Lab.
        comp = actor._runtime.competition._config
        competition_policy = {
            key: getattr(comp, key) for key in (
                "base_threshold", "leak", "gain", "noise_sigma",
                "urgency_max", "urgency_scale_cycles")
        }
    with birth_i1_m11(db_path=recovered, life_id=identity, **params) as actor:
        first_receipts, first_locations = committed_steps(actor, SPLIT)
        checkpoint_owners = causal(actor._runtime)
    check = SQLiteLifeLedger.audit_read_only(path=recovered,
        expected_individual_id=identity)
    assert check.may_recover and check.generation == SPLIT
    assert not check.pending_intent, "unclosed M11 physical transaction"
    with recover_i1_m11(db_path=recovered, life_id=identity,
                         runtime_factory=factory) as actor:
        assert causal(actor._runtime) == checkpoint_owners
        second_receipts, second_locations = committed_steps(actor, TOTAL-SPLIT)
        assert first_receipts + second_receipts == all_receipts
        assert first_locations + second_locations == all_locations
        assert causal(actor._runtime) == final_owners
        assert actor._runtime.exploration.geographic.export_causal_state() == final_geo
        assert journal(actor._runtime) == all_events
    check = SQLiteLifeLedger.audit_read_only(path=recovered,
        expected_individual_id=identity)
    assert check.may_recover and check.generation == TOTAL
    assert not check.pending_intent

kinds = Counter(event.get("kind") for event in all_events)
physical_actions = Counter(event.get("primitive") for event in all_events
                           if event.get("kind") == "command_experienced")
bodily_events = [event for event in all_events
                 if event.get("kind") == "i1_lived_site_effect_observed"]
route_offers = [event for event in all_events
                if event.get("kind") == "i1_lived_site_option_proposed"]
route_registrations = [event for event in all_events
                       if event.get("kind") == "i1_lived_site_option_registration"]
route_evaluations = [event for event in all_events
                     if event.get("kind") == "stage11_intrinsic_evaluation"
                     and str(event.get("data", {}).get("option_ref", "")).startswith(
                         "option:lived-site:")]
contextual = [event for event in route_evaluations
              if "exploration:lived_site_context_not_causal" in
                 event.get("data", {}).get("intrinsic_producers", ())]
from collections import defaultdict
from math import exp, isfinite

live_traces = []
for event in all_events:
    if event.get("kind") != "competition_cycle":
        continue
    for row in event.get("data", {}).get("traces", ()):
        if not str(row.get("option_ref", "")).startswith("option:lived-site:"):
            continue
        assert all(isfinite(float(row[key])) for key in (
            "accumulator_before", "accumulator_after", "threshold"))
        assert row["threshold"] > 0
        if row.get("evidence") is not None:
            assert isfinite(float(row["evidence"]))
            assert row["crossed"] == (
                row["accumulator_after"] >= row["threshold"])
        live_traces.append((event["t_monde"], event["cycle"], row))
scored = [entry for entry in live_traces if entry[2]["evidence"] is not None]
# A zero-activity test must not pass merely because every count is zero.
# These are observations of the unforced, deterministically seeded canonical life,
# not a command to select a remembered route or an imposed outcome.
assert bodily_events and physical_actions["se_deplacer"] > 0, (
    "canonical life never experienced a bodily site and a real movement"
)
assert any(location["older_remote_lived_sites"] for location in all_locations), (
    "no personally lived remote site became available after movement"
)
assert route_offers, "natural Planning did not propose a witnessed lived site"
assert len(route_registrations) == len(route_offers) and all(
    event["data"].get("registered") is True for event in route_registrations
), "a lived-site offer bypassed or failed ordinary Competition registration"
assert route_evaluations and len(contextual) == len(route_evaluations), (
    "lived-site evidence never reached contextual Stage8 evaluation"
)
assert any(row["evidence"] > 0 for _, _, row in scored), (
    "lived-site experience produced no positive Competition evidence"
)
assert len(scored) == len(route_evaluations), (
    "Competition evidence traces do not match Stage8 lived-site evaluations"
)
live_by_step = defaultdict(list)
for step, cycle, row in scored:
    live_by_step[step].append((cycle, row))
for step, group in live_by_step.items():
    for cycle, row in group:
        assert row["threshold"] > 0 and row["accumulator_after"] >= 0
for event in route_offers:
    data = event["data"]
    assert data["goal_ref"] is None
    assert data["forced_motor_selection"] is False
    assert any(older["t_monde"] < event["t_monde"] and
               tuple(older["data"]["site"]) == tuple(data["target"])
               for older in bodily_events), "unwitnessed/future site selected"
for event in contextual:
    sources = tuple(src for src in event["data"].get("signal_ids", ())
                    if src.startswith("lived-site:"))
    assert sources, "contextual evidence lacks personal source"
    assert all(int(src.rsplit("observed-t", 1)[1]) < event["t_monde"]
               for src in sources), "Stage8 used nonhistorical site observation"

# Read-only three-way audit: personally witnessed source -> paid Stage8
# -> ordinary Competition. No alternative action, Q value, or score is injected.
owner_events = {}
for event in bodily_events:
    key = (tuple(event["data"]["site"]), event["data"]["observed_step"])
    assert key not in owner_events, "duplicate first-person site witness"
    assert event["t_monde"] == key[1]
    assert event["data"]["causality_proven"] is False
    assert any(
        previous["t_monde"] == key[1] - 1
        and previous.get("kind") == "command_experienced"
        and previous.get("emitter") == "action_control"
        and previous.get("primitive") not in (
            "se_deplacer", "attendre", "dormir")
        for previous in all_events
    ), "site body effect without preceding applied local action"
    owner_events[key] = event

def event_key(event):
    return (event["t_monde"], event["cycle"],
            event["data"]["option_ref"])

paid_stage8 = {}
intrinsic_evaluations = {}
competition_evidence = {}
for event in all_events:
    kind = event.get("kind")
    if kind in ("stage8_option_evaluation", "stage11_intrinsic_evaluation"):
        ref = str(event.get("data", {}).get("option_ref", ""))
        if not ref.startswith("option:lived-site:"):
            continue
        store = (paid_stage8 if kind == "stage8_option_evaluation"
                 else intrinsic_evaluations)
        key = event_key(event)
        assert key not in store, "ambiguous per-cycle lived-site evaluation"
        store[key] = event["data"]
    if kind == "competition_cycle":
        for trace in event.get("data", {}).get("traces", ()):
            if not str(trace.get("option_ref", "")).startswith("option:lived-site:"):
                continue
            key = (event["t_monde"], event["cycle"], trace["option_ref"])
            assert key not in competition_evidence, "ambiguous paid Competition trace"
            competition_evidence[key] = trace
assert set(paid_stage8) == set(intrinsic_evaluations) == set(competition_evidence)
assert len(paid_stage8) == len(scored), "authentic score join lost an observation"

context_only = []
mixed_or_other = []
for key in sorted(paid_stage8):
    step, cycle, option_ref = key
    assessed = paid_stage8[key]
    intrinsic = intrinsic_evaluations[key]
    trace = competition_evidence[key]
    assert assessed["status"] == intrinsic["status"] == "evaluated"
    assert intrinsic["intrinsic_value"] == 0.0
    assert assessed["intrinsic_value"] == 0.0
    assert assessed["intrinsic_status"] == "applicable"
    assert trace["evidence"] is not None
    assert abs(float(assessed["evidence"]) - float(trace["evidence"])) < 1e-12
    assert bool(trace["crossed"]) == (
        trace["accumulator_after"] >= trace["threshold"])
    refs = tuple(x for x in intrinsic["signal_ids"]
                 if str(x).startswith("lived-site:"))
    assert refs, "lived-site Stage8 score lacks a first-person source"
    for source in refs:
        prefix, divider, observed = source.partition(":observed-t")
        parts = prefix.split(":")
        assert divider and len(parts) == 3 and parts[0] == "lived-site"
        observed_step = int(observed)
        witnessed_site = (int(parts[1]), int(parts[2]))
        assert observed_step < step, "future personal memory reached evaluation"
        assert (witnessed_site, observed_step) in owner_events, (
            "unwitnessed contextual score reached Competition")
    has_other_value = (
        assessed["learned_value_status"] == "learned"
        or assessed["simulated_value_status"] == "computed"
    )
    item = {"step": step, "cycle": cycle,
            "evidence": float(trace["evidence"]),
            "before": float(trace["accumulator_before"]),
            "after": float(trace["accumulator_after"]),
            "threshold": float(trace["threshold"]),
            "witnessed_site_sources": len(refs)}
    if has_other_value:
        # The combined evidence cannot be assigned wholly to site experience.
        mixed_or_other.append(item)
    else:
        assert assessed["learned_value"] is None
        assert assessed["simulated_value"] is None
        # Stage11's lived-site branch adds context to Stage8's unavailable
        # learned/simulated base. Thus this score is exclusively contextual.
        context_only.append(item)

# Independently replay the born Competition arithmetic for this single cycle
# with the REAL incoming accumulator; it is not a multi-step intervention.
# If a future canonical birth adds noise, leave that part NOT_OBSERVED.
noise_free = competition_policy["noise_sigma"] == 0.0
if noise_free:
    for item in context_only:
        urgency = (1.0 + (competition_policy["urgency_max"] - 1.0) *
            (1.0 - exp(-(item["cycle"] - 1) /
                         competition_policy["urgency_scale_cycles"])))
        without_this_cycle = max(
            0.0, (1.0 - competition_policy["leak"]) * item["before"])
        with_context = max(
            0.0, (1.0 - competition_policy["leak"]) * item["before"]
            + urgency * competition_policy["gain"] * item["evidence"])
        assert abs(item["after"] - with_context) < 1e-10, (
            "actual Competition arithmetic differs from observed Stage8 context")
        item["same_cycle_marginal"] = item["after"] - without_this_cycle
assert context_only, "no authentically witnessed context-only evaluation"
context_attribution = {
    "authentic_observed_site_witnesses": len(owner_events),
    "joined_paid_evaluations": len(paid_stage8),
    "context_only_evaluations": len(context_only),
    "mixed_or_other_value_evaluations": len(mixed_or_other),
    "context_only_positive": sum(item["evidence"] > 0
                                 for item in context_only),
    "context_only_negative": sum(item["evidence"] < 0
                                 for item in context_only),
    "context_only_neutral": sum(item["evidence"] == 0
                                for item in context_only),
    "context_only_max_evidence": max(
        (item["evidence"] for item in context_only), default=None),
    "context_only_max_threshold_ratio": max(
        (item["after"] / item["threshold"] for item in context_only),
        default=None),
    "born_competition_policy": competition_policy,
    "same_cycle_arithmetic_verified": noise_free,
    "context_only_max_single_cycle_increment": (
        max(item["same_cycle_marginal"] for item in context_only)
        if noise_free else None),
    "context_only_threshold_crossings": sum(
        item["after"] >= item["threshold"] for item in context_only),
    "causal_action_effect_proven": False,
    "improved_spatial_choice_proven": False,
    "scientific_l3": "NOT_ESTABLISHED",
}

print("I1_388_NATURAL_LIVED_SITE_MOVE_DIAGNOSTIC " + json.dumps({
    "preset": "dry-valley",
    "context_attribution": context_attribution,
    "physical_moves": physical_actions["se_deplacer"],
    "physical_primitives": dict(sorted(physical_actions.items())),
    "bodily_site_events": len(bodily_events),
    "site_positions": [entry["position"] for entry in final_geo["lived_site_effects"]],
    "site_samples": sum(x["samples"] for x in final_geo["lived_site_effects"]),
    "distinct_visited_positions": len(final_geo["visits"]),
    "first_remote_lived_site_step": next(
        (entry["world_step"] for entry in all_locations
         if entry["older_remote_lived_sites"]), None),
    "lived_site_route_offers": len(route_offers),
    "lived_site_registered": sum(
        event["data"].get("registered") is True
        for event in route_registrations),
    "lived_site_stage8_evaluated": len(route_evaluations),
    "lived_site_contextual_stage8": len(contextual),
    "lived_site_competition_traces": len(live_traces),
    "positive_evidence_traces": sum(row["evidence"] > 0 for _,_,row in scored),
    "negative_evidence_traces": sum(row["evidence"] < 0 for _,_,row in scored),
    "zero_evidence_traces": sum(row["evidence"] == 0 for _,_,row in scored),
    "minimum_evidence": min((row["evidence"] for _,_,row in scored), default=None),
    "maximum_evidence": max((row["evidence"] for _,_,row in scored), default=None),
    "highest_threshold_ratio": max(
        (row["accumulator_after"]/row["threshold"] for _,_,row in scored),
        default=None),
    "crossed": sum(bool(row["crossed"]) for _,_,row in scored),
    "first_four_traces": [
        {"step":step,"cycle":cycle,"evidence":row["evidence"],
         "accumulator_before":row["accumulator_before"],
         "accumulator_after":row["accumulator_after"],
         "threshold":row["threshold"]}
        for step,cycle,row in scored[:4]],
    "lived_site_motor_admissions": sum(
        event.get("kind") == "command_admitted"
        and str(event.get("data", {}).get("option_ref", "")).startswith(
            "option:lived-site:") for event in all_events),
    "geographic_budget_deferrals": kinds.get("i1_geographic_budget_deferred", 0),
    "cold_m11_exact": True,
    "L3": "NOT_ESTABLISHED",
}, sort_keys=True))
print("I1_388_CANONICAL_COLD_PARITY_OK")
"""
            environment = dict(
                os.environ,
                PYTHONPATH=os.pathsep.join((
                    str(generated), str(ROOT / "src"), str(ROOT / "tools"),
                )),
                PYTHONDONTWRITEBYTECODE="1",
            )
            completed = subprocess.run(
                [sys.executable, "-B", "-c", program],
                cwd=ROOT, env=environment, capture_output=True, text=True,
            )
            self.assertEqual(
                completed.returncode, 0, completed.stdout + completed.stderr)
            print(completed.stdout, flush=True)
            self.assertIn("I1_388_CANONICAL_COLD_PARITY_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
