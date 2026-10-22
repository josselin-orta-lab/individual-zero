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

def owner_boundary(rt):
    owner = rt.competition.export_causal_state()
    spatial = {}
    for row in owner["registry"]:
        option = row["proposal"]["option"]
        if option["id"].startswith("option:place-memory:"):
            spatial[option["id"]] = {
                "signature": option["learning_signature"],
                "goal": option["goal_ref"],
                "expires": option["expires_at_step"],
                "accumulator": row["accumulator"],
                "motive": option["motive_ref"]["id"],
            }
    geo = rt.exploration.geographic.export_causal_state()
    physical = geo["last_capture"]
    active = rt.goal_manager.active_goal
    return {"spatial": spatial, "goal": None if active is None else active.id,
            "capture": physical,
            # Genuine post-physical-step TD owner count, including in M11.
            # Never assign read evidence from a later step to an earlier one.
            "td_update_counts": dict(sorted(
                rt.q_active.export_causal_state()["update_counts"].items()))}

def drive(life, count):
    receipts = []
    boundaries = []
    for _ in range(count):
        receipt = life.run_step()
        assert receipt.status == "active", receipt
        assert receipt.generation == len(receipts) + 1 or receipt.generation > 1
        verify_intention(life._runtime)
        boundaries.append(owner_boundary(life._runtime))
        receipts.append((receipt.generation, receipt.world_step,
                         receipt.journal_count, receipt.journal_head,
                         receipt.status, receipt.outcome))
    return receipts, boundaries

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

def learned_readback(events, boundaries):
    # Audit learned Stage8 readbacks without mutating any causal owner.
    # This reads the authentic WAL and real TD owner after each physical step.
    # A learned Q read alone does not demonstrate selection or usefulness.
    evaluation = {}
    for event in events:
        if event.get("kind") != "stage8_option_evaluation":
            continue
        data = event.get("data", {})
        key = (event["t_monde"], event["cycle"], data["option_ref"])
        assert key not in evaluation, "ambiguous paid Stage8 source"
        evaluation[key] = data
    traces = {}
    for event in events:
        if event.get("kind") != "competition_cycle":
            continue
        for trace in event.get("data", {}).get("traces", ()):
            key = (event["t_monde"], event["cycle"], trace["option_ref"])
            assert key not in traces, "ambiguous Competition cycle trace"
            traces[key] = trace

    admitted = {(e["t_monde"], e.get("data", {}).get("option_ref"))
                for e in events if e.get("kind") == "command_admitted"}
    experienced_steps = {e["t_monde"] for e in events
                         if e.get("kind") == "command_experienced"
                         and e.get("emitter") == "action_control"}
    paid_applied = {
        (step, data["learning_signature"])
        for (step, cycle, ref), data in evaluation.items()
        if (step, ref) in admitted and step in experienced_steps
    }
    # The actual owner count at the previous physical boundary is strictly
    # prior evidence. Changes first observed at this step are not backdated.
    seen = []
    for (step, cycle, ref), data in sorted(evaluation.items()):
        if data.get("status") != "evaluated":
            continue
        signature = data["learning_signature"]
        if data.get("learned_value_status") != "learned":
            continue
        assert type(step) is int and 1 <= step <= len(boundaries)
        value = data.get("learned_value")
        assert value is not None and isfinite(float(value))
        assert data.get("evidence") is not None
        now_count = boundaries[step - 1]["td_update_counts"].get(signature, 0)
        assert now_count > 0, "learned Stage8 value absent from real TD owner"
        prior_count = (boundaries[step - 2]["td_update_counts"].get(signature, 0)
                       if step > 1 else 0)
        trace = traces.get((step, cycle, ref))
        assert trace is not None and trace["evidence"] is not None, (
            "paid learned Stage8 value never entered Competition")
        assert abs(float(trace["evidence"]) - float(data["evidence"])) < 1e-12, (
            "Competition evidence differs from the evaluated learned option")
        previously_applied = any(
            prior_step < step and previous_signature == signature
            for prior_step, previous_signature in paid_applied
        )
        seen.append({
            "signature": signature,
            "world_step": step,
            "owner_updated_before_this_step": prior_count > 0,
            "previously_physically_applied_same_signature": previously_applied,
            "evidence": trace["evidence"],
            "crossed": bool(trace["crossed"]),
            "admitted": (step, ref) in admitted,
        })
    # Repeated Stage8 evaluations are counted as evaluations, never
    # represented as independent physical experiences or TD updates.
    return {
        "paid_stage8_evaluations": len(evaluation),
        "learned_stage8_reaches_competition": len(seen),
        "learned_read_after_prior_td_boundary": sum(
            row["owner_updated_before_this_step"] for row in seen),
        "learned_read_with_prior_applied_same_signature": sum(
            row["previously_physically_applied_same_signature"] for row in seen),
        "learned_competition_crossings": sum(row["crossed"] for row in seen),
        "learned_motor_admissions": sum(row["admitted"] for row in seen),
        "learned_spatial_stage8": sum(
            row["signature"].startswith("memory_place_return:")
            for row in seen),
        "signatures": dict(sorted(Counter(row["signature"] for row in seen).items())),
        "first_readbacks": seen[:6],
        "physical_decision_improvement": "NOT_ESTABLISHED",
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
    # Classify *observed* opportunities for a persistent candidate, not a
    # hypothetical uninterrupted accumulator or a fabricated selected route.
    by_candidate = defaultdict(list)
    for record in spatial_traces:
        by_candidate[record["option_ref"]].append(record)
    exposure = []
    for records in by_candidate.values():
        steps = {r["world_step"] for r in records}
        scored = [r for r in records if r["evidence"] is not None]
        exposure.append({
            "evaluations": len(scored),
            "distinct_steps": len(steps),
            "positive_evaluations": sum(r["evidence"] > 0 for r in scored),
            "max_ratio": max((r["after"] / r["threshold"] for r in scored),
                             default=None),
        })
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
        "candidate_exposure": {
            "maximum_evaluations_per_ref": max(
                (v["evaluations"] for v in exposure), default=0),
            "maximum_distinct_physical_steps_per_ref": max(
                (v["distinct_steps"] for v in exposure), default=0),
            "refs_with_positive_evidence": sum(
                v["positive_evaluations"] > 0 for v in exposure),
            "refs_with_no_paid_evaluation": sum(
                v["evaluations"] == 0 for v in exposure),
            "closest_threshold_shortfall": min(
                (max(0.0, r["threshold"] - r["after"])
                 for r in scored_traces if not r["crossed"]), default=None),
        },
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
        control_receipts, control_boundaries = drive(life, TOTAL)
        final_continuous = image(life._runtime)
        events = journal(life._runtime)
        learned_sources = learning_sources(life._runtime, events)
        born_competition_cfg = life._runtime.competition._config
        born_intrinsic_weight = life._runtime._stage11_config.intrinsic_weight

    with birth_i1_m11(db_path=restored, life_id=individual, **params) as life:
        before_receipts, before_boundaries = drive(life, SPLIT)
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
        after_receipts, after_boundaries = drive(cold, TOTAL - SPLIT)
        assert before_receipts + after_receipts == control_receipts
        assert before_boundaries + after_boundaries == control_boundaries
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
    transitions = []
    for step, (prior, later) in enumerate(
        zip(control_boundaries, control_boundaries[1:]), start=2
    ):
        old, new = prior["spatial"], later["spatial"]
        removed = set(old) - set(new)
        added = set(new) - set(old)
        transitions.append({
            "retained": len(set(old) & set(new)),
            "lost": len(removed),
            "new": len(added),
            "deadline_reached": sum(old[k]["expires"] <= step for k in removed),
            "goal_mismatch": sum(old[k]["goal"] is not None
                and old[k]["goal"] != later["goal"] for k in removed),
            "same_signature_new_motor_id": len({
                old[k]["signature"] for k in removed
            } & {new[k]["signature"] for k in added}),
        })
    # Candidate IDs are canonical physical route descriptions. Compare
    # the witnessed positions and action-control WAL, not semantic memory
    # as if it were a motor privilege.
    physical_commands_by_step = defaultdict(list)
    for event in events:
        if event.get("kind") == "command_experienced":
            physical_commands_by_step[event.get("t_monde")].append(
                event.get("primitive"))
    geometry = []
    for step, (prior, later) in enumerate(
        zip(control_boundaries, control_boundaries[1:]), start=2
    ):
        removed = prior["spatial"].keys() - later["spatial"].keys()
        added = later["spatial"].keys() - prior["spatial"].keys()
        for missing in sorted(removed):
            for appearing in sorted(added):
                before = prior["spatial"][missing]
                after = later["spatial"][appearing]
                if before["signature"] != after["signature"]:
                    continue
                def route(ref):
                    # Stored ID: option:place-memory:place:<entity>:at:x:y:
                    # from:x:y:via:x:y. Parse only trusted canonical delimiters.
                    tail = ref.split(":from:", 1)[1]
                    origin, hop = tail.split(":via:", 1)
                    return (tuple(map(int, origin.split(":"))),
                            tuple(map(int, hop.split(":"))))
                old_origin, old_hop = route(missing)
                new_origin, new_hop = route(appearing)
                captured = later["capture"]
                fresh = captured is not None and captured[0] == step
                if fresh:
                    assert tuple(captured[1:]) == new_origin, (
                        "new spatial motor origin differs from lived capture")
                geometry.append({
                    "physical_step": step,
                    "origin_changed": old_origin != new_origin,
                    "next_hop_changed": old_hop != new_hop,
                    "fresh_paid_capture": fresh,
                    "preceding_experienced_primitives":
                        physical_commands_by_step.get(step - 1, []),
                })
    report["owner_candidate_boundaries"] = {
        "snapshots": len(control_boundaries),
        "lost_between_steps": sum(t["lost"] for t in transitions),
        "new_between_steps": sum(t["new"] for t in transitions),
        "retained_between_steps": sum(t["retained"] for t in transitions),
        "deadline_reached_indicators": sum(
            t["deadline_reached"] for t in transitions),
        "goal_mismatch_indicators": sum(t["goal_mismatch"] for t in transitions),
        "same_signature_new_motor_id": sum(
            t["same_signature_new_motor_id"] for t in transitions),
        "exact_m11_boundary_parity": True,
        "route_geometry": {
            "paired_same_signature_changes": len(geometry),
            "origin_changes": sum(g["origin_changed"] for g in geometry),
            "next_hop_changes": sum(g["next_hop_changed"] for g in geometry),
            "fresh_capture_pairs": sum(g["fresh_paid_capture"] for g in geometry),
            "observed_preceding_commands": dict(sorted(Counter(
                primitive for g in geometry
                for primitive in g["preceding_experienced_primitives"]).items())),
            "transitions": geometry,
        },
    }
    # Negative results matter: a paid reader may never encounter a pending
    # personally remembered site in this particular bounded natural life.
    spatial_reads = [e for e in events
                     if e.get("kind") == "i1_spatial_prospect_consulted"]
    report["spatial_prospect_consulted_count"] = len(spatial_reads)
    report["spatial_prospect_reordered_count"] = sum(
        e["data"].get("consideration_order_changed") is True
        for e in spatial_reads
    )
    # Cold intrinsic-return envelope: actual born Competition and Stage11
    # constants, not fitted to the observed failure or a hypothetical Q.
    from math import exp
    cfg = born_competition_cfg
    intrinsic_weight = born_intrinsic_weight
    intrinsic_cap = min(0.12, intrinsic_weight * 0.12)
    theoretical_gain = sum(
        (1.0 + (cfg.urgency_max - 1.0) *
         (1.0 - exp(-(cycle - 1) / cfg.urgency_scale_cycles)))
        * cfg.gain
        for cycle in range(1, cfg.c_max + 1)
    )
    # No noise and no preexisting candidate accumulation: this is explicitly
    # a first-deliberation bound, not a claim about persistent old options.
    zero_initial_bound = intrinsic_cap * theoretical_gain
    report["cold_spatial_intrinsic_envelope"] = {
        "intrinsic_cap": intrinsic_cap,
        "urgency_gain_sum": theoretical_gain,
        "zero_initial_max_after_cmax_without_leak": zero_initial_bound,
        "born_base_threshold": cfg.base_threshold,
        "cold_intrinsic_alone_cannot_cross": (
            cfg.noise_sigma == 0 and zero_initial_bound < cfg.base_threshold
        ),
        "measured_max_evidence": report["spatial_competition_traces"]["max_evidence"],
        "measured_max_threshold_ratio":
            report["spatial_competition_traces"]["max_accumulator_to_threshold"],
        "first_deliberation_only": True,
        "retained_candidate_future_crossing": "NOT_ESTABLISHED",
        "td_or_simulation_added": False,
        "scientific_l3": "NOT_ESTABLISHED",
    }
    assert cfg.noise_sigma == 0
    assert 0 <= cfg.leak < 1
    assert intrinsic_cap >= max(
        report["spatial_competition_traces"]["intrinsic_values"])
    assert report["cold_spatial_intrinsic_envelope"]["cold_intrinsic_alone_cannot_cross"]
    # Opportunity-limited bounds from EACH actual motor option ID's PAID cycles.
    # Deliberation IDs and UC schedule are not generated by this analysis.
    # All real options began with a zero accumulator at birth; ignoring any
    # later leak, winner residual and registry reset makes this an upper bound
    # for the *observed* option identities, not a prospective intervention.
    trace_rows = [
        row for row in events if row.get("kind") == "competition_cycle"
    ]
    cold_observed = (
        report["spatial_competition_traces"]["stage8_learned_statuses"]
            == {"unlearned": report["stage8_evaluated"]}
        and report["spatial_competition_traces"]["stage8_simulated_statuses"]
            == {"unavailable": report["stage8_evaluated"]}
        and report["spatial_competition_traces"]["contextual_site_contributions"] == 0
        and report["spatial_competition_traces"]["not_evaluated"] == 0
    )
    candidate_windows = {}
    for event in trace_rows:
        for trace in event.get("data", {}).get("traces", ()):
            ref = trace.get("option_ref", "")
            if not ref.startswith("option:place-memory:"):
                continue
            if trace.get("evidence") is None:
                continue
            cycle = event["cycle"]
            assert type(cycle) is int and 1 <= cycle <= cfg.c_max
            assert trace["evidence"] >= 0 and trace["threshold"] > 0
            factor = (1.0 + (cfg.urgency_max - 1.0) *
                      (1.0 - exp(-(cycle - 1) / cfg.urgency_scale_cycles)))
            row = candidate_windows.setdefault(ref, {
                "evaluated_cycles": 0, "steps": set(),
                "observed_evidence_upper": 0.0,
                "max_confidence_intrinsic_upper": 0.0,
                "minimum_observed_threshold": float("inf"),
            })
            row["evaluated_cycles"] += 1
            row["steps"].add(event["t_monde"])
            row["observed_evidence_upper"] += (
                cfg.gain * factor * trace["evidence"])
            row["max_confidence_intrinsic_upper"] += (
                cfg.gain * factor * intrinsic_cap)
            row["minimum_observed_threshold"] = min(
                row["minimum_observed_threshold"], trace["threshold"])
    candidate_summaries = []
    for row in candidate_windows.values():
        limit = row["minimum_observed_threshold"]
        candidate_summaries.append({
            "paid_cycles": row["evaluated_cycles"],
            "distinct_physical_steps": len(row["steps"]),
            "observed_evidence_ratio_ceiling":
                row["observed_evidence_upper"] / limit,
            "full_confidence_ratio_ceiling":
                row["max_confidence_intrinsic_upper"] / limit,
        })
    # No score is fed to Stage8/Competition. A ceiling >= threshold is only
    # "not ruled out", not a predicted or experienced motor admission.
    candidate_windows_report = {
        "verified_intrinsic_only": cold_observed,
        "observed_candidate_identities": len(candidate_summaries),
        "observed_paid_cycles": sum(
            row["paid_cycles"] for row in candidate_summaries),
        "maximum_paid_cycles_one_identity": max(
            (row["paid_cycles"] for row in candidate_summaries), default=0),
        "maximum_distinct_physical_steps_one_identity": max(
            (row["distinct_physical_steps"] for row in candidate_summaries),
            default=0),
        "largest_actual_intrinsic_upper_ratio": max(
            (row["observed_evidence_ratio_ceiling"]
             for row in candidate_summaries), default=None),
        "largest_full_confidence_upper_ratio": max(
            (row["full_confidence_ratio_ceiling"]
             for row in candidate_summaries), default=None),
        "candidates_not_ruled_out_at_full_confidence": sum(
            row["full_confidence_ratio_ceiling"] >= 1.0
            for row in candidate_summaries),
        "candidates_not_ruled_out_with_observed_intrinsic": sum(
            row["observed_evidence_ratio_ceiling"] >= 1.0
            for row in candidate_summaries),
        "no_reset_no_leak_no_residual_assumption": True,
        "no_hypothetical_extra_cycles": True,
        "future_episode_outcome": "NOT_ESTABLISHED",
        "motor_effect": "NONE",
        "scientific_l3": "NOT_ESTABLISHED",
    }
    assert len(candidate_summaries) == (
        report["spatial_competition_traces"]["candidate_refs"])
    assert candidate_windows_report["observed_paid_cycles"] == (
        report["spatial_competition_traces"]["with_evidence"])
    assert all(
        row["observed_evidence_ratio_ceiling"] <= (
            row["full_confidence_ratio_ceiling"] + 1e-12)
        for row in candidate_summaries)
    report["observed_candidate_window_envelope"] = candidate_windows_report
    report["personally_learned_sources"] = learned_sources
    report["experienced_td_readback"] = learned_readback(
        events, control_boundaries)
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
