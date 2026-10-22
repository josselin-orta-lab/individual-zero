"""Authentic canonical I1 spatial pipeline and M11 cold-continuation audit.

This is one short technical life replay, NOT a population campaign.
No command, GoalManager state, intention, memory, Q or world observation is injected.
A missing spontaneous spatial admission is reported, never silently fabricated.
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


class CanonicalSpatialM11Audit(unittest.TestCase):
    def test_genuine_m11_split_matches_uninterrupted_owner_images(self):
        with TemporaryDirectory(prefix="i1-377-build-") as temp:
            generated = Path(temp) / "generated"
            generate(generated)
            script = r"""
from collections import Counter, defaultdict
from math import isfinite
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

preset, _ = load_preset("foraging")
params, _ = _birth_parameters(preset)
params = dict(params, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
individual = "i1:377:natural-m11-spatial"
TOTAL = 10
SPLIT = 4

def factory():
    return I1Runtime(
        birth_life_id=individual, autonomous_mortal=True,
        m11_sqlite_custody=True, wal_path=None, **params,
    )

def image(rt):
    # Every genuine causal owner, not a hand-selected synthetic record.
    return {owner.owner_id: owner.export_causal_state()
            for owner in rt.causal_owners}

def journal(rt):
    return [dict(entry.causal_event) for entry in
            rt.journal.entries_since(0)]

def verify_intention(rt):
    intent = rt.competition.applied_memory_intention
    if intent is None:
        return
    intent.validate()
    # A spatial intention requires the actual Action Control/World event at
    # the *historical* applied step, even if currently suspended or confirmed.
    events = journal(rt)
    applied = intent.applied_step
    assert any(
        e.get("kind") == "command_admitted"
        and e.get("t_monde") == applied
        and e.get("data", {}).get("option_ref") == intent.source_option_ref
        and e.get("data", {}).get("primitive") == "se_deplacer"
        for e in events
    ), "semantic spatial intention without physical command admission"
    assert any(
        e.get("kind") == "command_experienced"
        and e.get("t_monde") == applied
        and e.get("emitter") == "action_control"
        and e.get("primitive") == "se_deplacer"
        for e in events
    ), "semantic spatial intention without real command"
    assert any(
        e.get("kind") == "world_transition_experienced"
        and e.get("t_monde") == applied
        for e in events
    ), "spatial intention without physical consequence"
    assert any(
        e.get("kind") == "step_closed"
        and e.get("t_monde") == applied
        and e.get("data", {}).get("applied_command_count") == 1
        for e in events
    ), "spatial intention without step closure"

def drive(life, count):
    receipts = []
    for _ in range(count):
        receipt = life.run_step()
        assert receipt.status == "active", receipt
        assert receipt.generation == len(receipts) + 1 or receipt.generation > 1
        verify_intention(life._runtime)
        receipts.append((receipt.generation, receipt.world_step,
                         receipt.journal_count, receipt.journal_head,
                         receipt.status, receipt.outcome))
    return receipts

def learning_sources(rt, events):
    # Read the actual owner images, not inferred values from event names.
    td = rt.q_active.export_causal_state()
    geographic = rt.exploration.geographic.export_causal_state()
    updates = td["update_counts"]
    sites = geographic.get("lived_site_effects", [])
    site_events = [e for e in events if e.get("kind") ==
                   "i1_lived_site_effect_observed"]
    spatial_applied = [e for e in events if
                       e.get("kind") == "command_admitted"
                       and str(e.get("data", {}).get("option_ref", "")).startswith(
                           "option:place-memory:")]
    learned_place = {
        k: v for k, v in updates.items()
        if k.startswith("memory_place_return:") and v > 0
    }
    # A spatial signature is learned only following its own real applied
    # decision. Never treat a berry sighting or some other primitive as Q.
    if learned_place and not spatial_applied:
        raise AssertionError("spatial Q appeared with no real spatial admission")
    if sites and not site_events:
        raise AssertionError("unlogged personally observed contextual site effect")
    return {
        "td_updated_signature_count": sum(v > 0 for v in updates.values()),
        "td_updated_signatures": sorted(
            [{"signature": k, "updates": v} for k,v in updates.items()
             if v > 0], key=lambda row: row["signature"]),
        "td_spatial_updated_signature_count": len(learned_place),
        "td_pending_segment": (None if td["pending"] is None else {
            "signature": td["pending"]["signature"],
            "decision_world_step": td["pending"]["decision_t_monde"],
            "reward_count": len(td["pending"]["rewards"]),
        }),
        "spatial_options_physically_admitted": len(spatial_applied),
        "physical_primitive_counts": dict(sorted(Counter(
            str(e.get("primitive")) for e in events
            if e.get("kind") == "command_experienced").items())),
        "personally_observed_site_effect_count": len(sites),
        "site_effect_samples": sum(row["samples"] for row in sites),
        "site_effect_journal_events": len(site_events),
        "site_effect_positions": [row["position"] for row in sites],
    }

def audit(events):
    counts = Counter(e.get("kind") for e in events)
    sightings = []
    proposed = registered = evaluated = crossed = 0
    proposals_without_prior_sighting_event = 0
    spatial_traces = []
    spatial_intrinsic = []
    spatial_stage8 = []
    for e in events:
        kind = e.get("kind")
        step = e.get("t_monde")
        data = e.get("data", {})
        if kind == "i1_entity_place_observed":
            sightings.append((step, data.get("entity_id"),
                              tuple(data.get("position", ()))))
        if kind == "i1_place_memory_option_proposed":
            proposed += 1
            if not any(
                t < step and entity == data.get("entity_id")
                and location == tuple(data.get("target", ()))
                for t, entity, location in sightings
            ):
                # Classify missing journal proof separately. It is NOT proof
                # of a forged memory: Exploration/M11 independently owns the
                # historical perception and the exact frozen phase-0 image.
                proposals_without_prior_sighting_event += 1
        if kind == "i1_place_memory_option_registration" and data.get("registered") is True:
            registered += 1
        if kind == "stage8_option_evaluation" and str(data.get("option_ref", "")).startswith("option:place-memory:"):
            evaluated += 1
            spatial_stage8.append(data)
        if kind == "stage11_intrinsic_evaluation" and str(data.get("option_ref", "")).startswith("option:place-memory:"):
            spatial_intrinsic.append(data)
        if kind == "competition_cycle":
            for trace in data.get("traces", ()):
                if not str(trace.get("option_ref", "")).startswith("option:place-memory:"):
                    continue
                crossed += bool(trace.get("crossed"))
                assert all(isfinite(float(trace[field])) for field in (
                    "accumulator_before", "accumulator_after", "threshold"))
                assert float(trace["threshold"]) > 0
                if trace.get("evidence") is not None:
                    assert isfinite(float(trace["evidence"]))
                    assert bool(trace["crossed"]) == (
                        float(trace["accumulator_after"]) >= float(trace["threshold"]))
                spatial_traces.append({
                    "option_ref": trace["option_ref"],
                    "world_step": step,
                    "cycle": e.get("cycle"),
                    "before": trace["accumulator_before"],
                    "after": trace["accumulator_after"],
                    "evidence": trace.get("evidence"),
                    "threshold": trace["threshold"],
                    "crossed": bool(trace.get("crossed")),
                })
        if kind == "i1_place_memory_intention_reconsidered_without_motor_credit":
            assert data.get("credited_evidence") == 0.0
            assert data.get("motor_admission_inherited") is False
    # A deliberate L2 observation: report the first missing genuine link
    # instead of creating a test-only winner or manipulating the motor policy.
    stage = "not_seen"
    if sightings:
        stage = "seen"
    if counts["i1_place_memory_recalled"]:
        stage = "recalled"
    if proposed:
        stage = "proposed"
    if registered:
        stage = "registered"
    if evaluated:
        stage = "evaluated"
    if crossed:
        stage = "crossed"
    if counts["i1_place_memory_intention_reconsidered"]:
        stage = "reconsidered"
    scored_traces = [x for x in spatial_traces if x["evidence"] is not None]
    refs_by_step = defaultdict(set)
    for trace in spatial_traces:
        refs_by_step[trace["option_ref"]].add(trace["world_step"])
    max_evidence = max((r["evidence"] for r in scored_traces), default=None)
    min_evidence = min((r["evidence"] for r in scored_traces), default=None)
    max_accum_ratio = max(
        (r["after"] / r["threshold"] for r in scored_traces), default=None)
    trace_diagnosis = {
        "traces": len(spatial_traces),
        "with_evidence": len(scored_traces),
        "not_evaluated": len(spatial_traces)-len(scored_traces),
        "positive_evidence": sum(r["evidence"] > 0 for r in scored_traces),
        "zero_evidence": sum(r["evidence"] == 0 for r in scored_traces),
        "negative_evidence": sum(r["evidence"] < 0 for r in scored_traces),
        "max_evidence": max_evidence,
        "min_evidence": min_evidence,
        "max_accumulator_to_threshold": max_accum_ratio,
        "max_accumulator": max((r["after"] for r in spatial_traces),default=None),
        "min_threshold": min((r["threshold"] for r in spatial_traces),default=None),
        "accumulator_reset_or_flat": sum(
            r["after"] <= r["before"] for r in scored_traces),
        "candidate_refs": len(refs_by_step),
        "candidate_refs_seen_across_multiple_world_steps": sum(
            len(steps)>1 for steps in refs_by_step.values()),
        "stage11_intrinsic_records": len(spatial_intrinsic),
        "contextual_site_contributions": sum(
            "exploration:lived_site_context_not_causal" in
            row.get("intrinsic_producers", ())
            for row in spatial_intrinsic),
        "intrinsic_values": sorted({
            float(row["intrinsic_value"]) for row in spatial_intrinsic
            if row.get("intrinsic_value") is not None
        }),
        "stage8_records": len(spatial_stage8),
        "stage8_statuses": dict(sorted(Counter(
            str(row.get("status")) for row in spatial_stage8).items())),
        "stage8_learned_statuses": dict(sorted(Counter(
            str(row.get("learned_value_status"))
            for row in spatial_stage8).items())),
        "stage8_simulated_statuses": dict(sorted(Counter(
            str(row.get("simulated_value_status"))
            for row in spatial_stage8).items())),
        "examples": [
            {k: v for k,v in row.items() if k != "option_ref"}
            for row in spatial_traces[:4]
        ],
    }
    assert len(spatial_traces) >= evaluated, "Stage8 evaluated options without Competition traces"
    return {
        "spatial_competition_traces": trace_diagnosis,
        "stage_reached": stage,
        "first_person_sightings": len(sightings),
        "recalls": counts["i1_place_memory_recalled"],
        "proposed": proposed, "registered": registered,
        "proposals_without_prior_sighting_event": proposals_without_prior_sighting_event,
        "stage8_evaluated": evaluated, "competition_crossed": crossed,
        "spatial_intention_next_hop_reconsidered": counts["i1_place_memory_intention_reconsidered"],
        "spatial_intention_after_interruption": counts["i1_place_memory_intention_reconsidered_without_motor_credit"],
        "budget_deferrals": counts["stage11_geographic_budget_deferred"],
        "spatial_observation_statuses": counts["i1_place_memory_intention_observation"],
        "command_admissions": counts["command_admitted"],
        "physical_commands": counts["command_experienced"],
        "step_closures": counts["step_closed"],
        "scientific_benefit": "NOT_ESTABLISHED",
    }

with TemporaryDirectory(prefix="i1-377-ledger-") as home:
    uninterrupted = str(Path(home) / "uninterrupted.sqlite")
    restored = str(Path(home) / "restored.sqlite")

    with birth_i1_m11(db_path=uninterrupted, life_id=individual, **params) as life:
        assert life._runtime.exploration.geographic.config.remember_entities
        control_receipts = drive(life, TOTAL)
        final_continuous = image(life._runtime)
        events = journal(life._runtime)
        learned_sources = learning_sources(life._runtime, events)

    with birth_i1_m11(db_path=restored, life_id=individual, **params) as life:
        before_receipts = drive(life, SPLIT)
        assert before_receipts == control_receipts[:SPLIT]
        before_owners = image(life._runtime)
        pre_head = life._runtime.journal.head_hash

    first_audit = SQLiteLifeLedger.audit_read_only(
        path=restored, expected_individual_id=individual)
    assert first_audit.may_recover and first_audit.generation == SPLIT
    assert not first_audit.pending_intent

    with recover_i1_m11(
        db_path=restored, life_id=individual, runtime_factory=factory,
    ) as cold:
        assert image(cold._runtime) == before_owners
        assert cold._runtime.journal.head_hash == pre_head
        after_receipts = drive(cold, TOTAL - SPLIT)
        assert before_receipts + after_receipts == control_receipts
        assert image(cold._runtime) == final_continuous
        assert journal(cold._runtime) == events

    final_audit = SQLiteLifeLedger.audit_read_only(
        path=restored, expected_individual_id=individual)
    assert final_audit.may_recover and final_audit.generation == TOTAL
    assert not final_audit.pending_intent
    assert final_audit.journal_head == control_receipts[-1][3]

    # The earliest spatial cognition gap: a Stage8-evaluated route may be
    # remembered as a prospective option without ever winning a movement.
    # No seed search, synthetic spatial record, or Q modification.
    prospects = [e for e in events
                 if e.get("kind") == "i1_spatial_option_prospected"]
    assert prospects, "canonical Stage8 route did not reach prospective Memory"
    assert any(row["target"].startswith("memory_place_return:")
               and "considered_step" in row["trigger_value"]
               for row in final_continuous["memory"]["intentions"]), (
        "genuinely paid spatial prospect never survived M11"
    )
    assert all(e["data"]["stage8_evaluated"] is True
               and e["data"]["motor_admission_inherited"] is False
               and e["data"]["action_applied"] is False for e in prospects)
    # A future route may be read as context but receives no motor credit.
    # This asserts the *wired reader*, not yet spontaneous future selection.
    from i1lab.i1_natural_runtime import I1Runtime
    import inspect
    reader = inspect.getsource(I1Runtime._order_considered_spatial_targets)
    assert "self.memory.recalled_applied_option(" in reader
    assert "self._charge(" in reader
    assert '"motor_admission_inherited": False' in reader
    report = audit(events)
    # Negative results matter: a paid reader may never encounter a pending
    # personally remembered site in this particular bounded natural life.
    spatial_reads = [e for e in events
                     if e.get("kind") == "i1_spatial_prospect_consulted"]
    report["spatial_prospect_consulted_count"] = len(spatial_reads)
    report["spatial_prospect_reordered_count"] = sum(
        e["data"].get("consideration_order_changed") is True
        for e in spatial_reads
    )
    report["personally_learned_sources"] = learned_sources
    print("I1_377_CANONICAL_M11_SPATIAL_DIAGNOSTIC "
          + json.dumps(report, sort_keys=True), flush=True)
    assert report["first_person_sightings"] > 0, (
        "Foraging birth saw adjacent entities but never retained a personal sighting"
    )
    assert report["step_closures"] >= TOTAL
    print("I1_377_CANONICAL_M11_SPATIAL_COLD_PARITY_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(generated), str(ROOT / "src"), str(ROOT / "tools"))),
                PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, "-B", "-c", script], cwd=ROOT,
                env=env, text=True, capture_output=True)
            print(result.stdout, flush=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_377_CANONICAL_M11_SPATIAL_COLD_PARITY_OK",
                          result.stdout)


if __name__ == "__main__":
    unittest.main()
