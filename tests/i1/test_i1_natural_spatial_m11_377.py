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
from collections import Counter
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

def audit(events):
    counts = Counter(e.get("kind") for e in events)
    sightings = []
    proposed = registered = evaluated = crossed = 0
    proposals_without_prior_sighting_event = 0
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
        if kind == "competition_cycle":
            crossed += sum(
                bool(t.get("crossed"))
                for t in data.get("traces", ())
                if str(t.get("option_ref", "")).startswith("option:place-memory:")
            )
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
    return {
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

    report = audit(events)
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
