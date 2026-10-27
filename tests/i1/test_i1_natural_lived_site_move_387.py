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


class NaturalLivedSiteMovement(unittest.TestCase):
    def test_short_dry_valley_perception_and_cold_m11(self):
        with TemporaryDirectory(prefix="i1-387-") as directory:
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

with TemporaryDirectory(prefix="i1-387-cold-") as directory:
    uninterrupted = str(Path(directory) / "uninterrupted.sqlite")
    recovered = str(Path(directory) / "recovered.sqlite")
    with birth_i1_m11(db_path=uninterrupted, life_id=identity, **params) as actor:
        all_receipts, all_locations = committed_steps(actor, TOTAL)
        final_owners = causal(actor._runtime)
        final_geo = actor._runtime.exploration.geographic.export_causal_state()
        all_events = journal(actor._runtime)
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

print("I1_387_NATURAL_LIVED_SITE_MOVE_DIAGNOSTIC " + json.dumps({
    "preset": "dry-valley",
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
    "lived_site_motor_admissions": sum(
        event.get("kind") == "command_admitted"
        and str(event.get("data", {}).get("option_ref", "")).startswith(
            "option:lived-site:") for event in all_events),
    "geographic_budget_deferrals": kinds.get("i1_geographic_budget_deferred", 0),
    "cold_m11_exact": True,
    "L3": "NOT_ESTABLISHED",
}, sort_keys=True))
print("I1_387_CANONICAL_COLD_PARITY_OK")
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
            self.assertIn("I1_387_CANONICAL_COLD_PARITY_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
