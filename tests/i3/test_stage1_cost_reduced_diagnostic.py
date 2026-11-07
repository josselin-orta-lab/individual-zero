"""No study worlds/lives: checks for the frozen cost-reduced diagnostic."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_cost_reduced_diagnostic as d
from i3.lab import stage0_design
from i3.lab import stage1_diagnostic as old


def fixture():
    statuses = (
        "FUNDED", "NO_FUNDED_SCORE", "NO_PROCESSING_BUDGET",
        "NO_PROCESSING_BUDGET", "FUNDED")
    rows, events, comps = [], [], []
    for step, status in enumerate(statuses, 1):
        action = "attendre" if status == "FUNDED" else None
        outcome = (
            "action_admitted" if action else
            "no_funded_score" if status == "NO_FUNDED_SCORE"
            else "no_processing_budget")
        rows.append({
            "t": step, "action": action, "info": {"funding": status},
            "funding_phases": {
                "decision": {"body_before": [40] * 5,
                             "work": {"cycles": 3}}}})
        events.append({
            "step": step, "action": action, "decision_funding": status,
            "decision_outcome": outcome,
            "positive_water_uptake": step == 5})
        comps.append({
            "physical_action": action, "decision_outcome": outcome,
            "paid_option_scores": []})
    return {
        "steps_lived": len(rows), "trace": rows,
        "observer_resource_acquisition": {
            "steps": events,
            "summary": {
                "positive_water_uptakes": 1,
                "positive_food_uptakes": 0,
                "collected_inventory": 0,
                "consumed_inventory": 0,
                "new_personally_mapped_cells": 1}},
        "observer_full_competition": {"steps": comps}}


class CostReducedDiagnosticTests(unittest.TestCase):
    def test_frozen_new_development_only_envelope(self):
        p = d.plan()
        self.assertEqual(len(p["cases"]), 24)
        self.assertEqual(p["maximum_steps"], 9600)
        self.assertEqual({c["cohort"] for c in p["cases"]}, {"development"})
        self.assertEqual({c["index"] for c in p["cases"]}, {46, 47})
        self.assertEqual(
            d.digest(p),
            "d9d8145db42c28108bcf5e3593a4957b7ec86152d89d991be89c4767fdca1025")
        self.assertEqual(
            p["engineering_continuation_rule"],
            "candidate_inactive_fraction_le_0.5_AND_positive_water_uptake_gt_0")

    def test_new_indices_follow_old_exposed_panel_and_stay_in_stage0_development(self):
        self.assertEqual(old.INDICES, (44, 45))
        planned = {r["index"] for r in stage0_design.world_rows("development")}
        self.assertTrue({46, 47}.issubset(planned))
        self.assertTrue({46, 47}.isdisjoint(old.INDICES))

    def test_pairs_share_opportunity_and_new_life_seed_namespace(self):
        cases = d.plan()["cases"]
        self.assertEqual(len({r["case"] for r in cases}), 24)
        self.assertEqual(len({r["life_seed"] for r in cases}), 12)
        self.assertTrue(all(r["life_seed"] >= 7410000 for r in cases))
        for a, b in zip(cases[::2], cases[1::2]):
            self.assertEqual(
                {k: v for k, v in a.items() if k not in ("case", "policy")},
                {k: v for k, v in b.items() if k not in ("case", "policy")})

    def test_plan_is_detached_and_import_does_not_load_runtime(self):
        first = d.plan()
        first["cases"].clear()
        self.assertEqual(len(d.plan()["cases"]), 24)
        root = str(Path(d.__file__).resolve().parents[2])
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "from i3.lab.stage1_cost_reduced_diagnostic import plan; plan(); "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules"], check=True)

    def test_bad_lock_dirty_or_changed_runtime_fails_closed(self):
        with patch.object(d, "_git", side_effect=AssertionError("no git for bad SHA")):
            with self.assertRaises(ValueError):
                d.validate_launch(None, None)
        with patch.object(d, "_git", return_value="a" * 40):
            with self.assertRaises(ValueError):
                d.validate_launch("a" * 40, "wrong")
        for responses in (
            ("a" * 40, " M src/i3/modules/information_mind.py"),
            ("a" * 40, "", "src/i3/modules/information_mind.py"),
        ):
            with patch.object(d, "_git", side_effect=responses):
                with self.assertRaises(ValueError):
                    d.validate_launch("a" * 40, d.digest(d.plan()))

    def test_paralysis_receipt_distinguishes_recovery_after_processing_failure(self):
        life = fixture()
        before = deepcopy(life)
        r = d.behavioral_summary(life)
        self.assertEqual(r["first_funding_failure"]["step"], 2)
        self.assertEqual(r["first_no_processing_step"], 3)
        self.assertEqual(r["funded_after_first_no_processing"], 1)
        self.assertFalse(r["terminal_no_processing_lock"])
        self.assertEqual(r["longest_consecutive_unfunded_steps"], 3)
        self.assertEqual(r["first_positive_water_step"], 5)
        self.assertEqual(r["positive_water_uptakes"], 1)
        self.assertEqual(life, before)

    def test_terminal_processing_lock_is_not_recovery(self):
        life = fixture()
        life["trace"].pop()
        life["observer_resource_acquisition"]["steps"].pop()
        life["observer_full_competition"]["steps"].pop()
        life["steps_lived"] = 4
        life["observer_resource_acquisition"]["summary"]["positive_water_uptakes"] = 0
        r = d.behavioral_summary(life)
        self.assertTrue(r["terminal_no_processing_lock"])
        self.assertEqual(r["funded_after_first_no_processing"], 0)

    def test_sidecar_disagreement_still_fails(self):
        life = fixture()
        life["observer_full_competition"]["steps"][0]["physical_action"] = "boire"
        with self.assertRaises(ValueError):
            d.behavioral_summary(life)

    def test_empty_aggregate_never_becomes_a_gate_result(self):
        r = d.aggregate([])
        self.assertIsNone(r["reference"]["inactive_fraction"])
        self.assertIsNone(r["reference"]["engineering_continuation_rule_met"])
        self.assertFalse(r["local_information_v1"]["engineering_continuation_rule_met"])
        self.assertEqual(
            r["local_information_v1"]["scientific_verdict"], "NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
