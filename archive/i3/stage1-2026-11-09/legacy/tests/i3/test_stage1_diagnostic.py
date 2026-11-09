"""No study worlds/lives: checks for the frozen diagnostic and reductions."""
from copy import deepcopy
from pathlib import Path
import sys
import subprocess
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import stage1_diagnostic as d


def fixture():
    statuses = ("FUNDED", "NO_FUNDED_SCORE", "NO_PROCESSING_BUDGET", "FUNDED")
    rows, events, comps = [], [], []
    for step, status in enumerate(statuses, 1):
        action = "attendre" if status == "FUNDED" else None
        outcome = "action_admitted" if action else "no_funded_score" if status == "NO_FUNDED_SCORE" else "no_processing_budget"
        rows.append({"t": step, "action": action, "info": {"funding": status},
                     "funding_phases": {"decision": {"body_before": [40]*5, "work": {"cycles": 3}}}})
        events.append({"step": step, "action": action, "decision_funding": status,
                       "decision_outcome": outcome, "positive_water_uptake": False})
        comps.append({"physical_action": action, "decision_outcome": outcome,
                      "paid_option_scores": []})
    return {"steps_lived": 4, "trace": rows,
            "observer_resource_acquisition": {"steps": events, "summary": {
                "positive_water_uptakes": 0, "positive_food_uptakes": 0,
                "collected_inventory": 0, "consumed_inventory": 0,
                "new_personally_mapped_cells": 1}},
            "observer_full_competition": {"steps": comps}}


class DiagnosticTests(unittest.TestCase):
    def test_frozen_development_only_envelope(self):
        p = d.plan()
        self.assertEqual(len(p["cases"]), 24)
        self.assertEqual(p["maximum_steps"], 9600)
        self.assertEqual({c["cohort"] for c in p["cases"]}, {"development"})
        self.assertEqual({c["index"] for c in p["cases"]}, {44, 45})
        self.assertEqual(d.digest(p), "426a8f93bb915a8431654a1cc0945d981d6f83822c98e36fcab94e89af9615cc")

    def test_pairs_and_independent_identifiers_not_population_claims(self):
        cases = d.plan()["cases"]
        self.assertEqual(len({r["case"] for r in cases}), 24)
        self.assertEqual(len({r["life_seed"] for r in cases}), 12)
        for a, b in zip(cases[::2], cases[1::2]):
            self.assertEqual({k:v for k,v in a.items() if k not in ("case", "policy")},
                             {k:v for k,v in b.items() if k not in ("case", "policy")})

    def test_plan_detached_and_never_imports_runtime(self):
        first = d.plan()
        first["cases"].clear()
        self.assertEqual(len(d.plan()["cases"]), 24)
        root = str(Path(d.__file__).resolve().parents[2])
        subprocess.run([sys.executable, "-c",
                        "import sys; sys.path.insert(0, " + repr(root) + "); "
                        "from i3.lab.stage1_diagnostic import plan; plan(); "
                        "assert 'i3.runtime.life' not in sys.modules; "
                        "assert 'i3.modules.world' not in sys.modules"], check=True)

    def test_bad_lock_stops_before_git_and_birth(self):
        with patch.object(d, "_git", side_effect=AssertionError("no git for bad SHA")):
            with self.assertRaises(ValueError):
                d.validate_launch(None, None)
        with patch.object(d, "_git", return_value="a"*40):
            with self.assertRaises(ValueError):
                d.validate_launch("a"*40, "wrong")

    def test_dirty_or_changed_runtime_is_rejected(self):
        for responses in (("a"*40, " M src/i3/modules/mind.py"),
                          ("a"*40, "", "src/i3/modules/mind.py")):
            with patch.object(d, "_git", side_effect=responses):
                with self.assertRaises(ValueError):
                    d.validate_launch("a"*40, d.digest(d.plan()))

    def test_wait_not_inactivity_and_unfunded_run(self):
        life = fixture()
        before = deepcopy(life)
        r = d.behavioral_summary(life)
        self.assertEqual(r["inactive_fraction"], .5)
        self.assertEqual(r["actions"]["attendre"], 2)
        self.assertEqual(r["longest_consecutive_unfunded_steps"], 2)
        self.assertEqual(r["first_funding_failure"]["step"], 2)
        self.assertIsNone(r["first_positive_water_step"])
        self.assertEqual(life, before)

    def test_incomplete_and_disagreeing_sidecars_fail(self):
        for change in ("missing", "action", "funding"):
            life = fixture()
            if change == "missing":
                life["observer_full_competition"]["steps"].pop()
            elif change == "action":
                life["observer_full_competition"]["steps"][0]["physical_action"] = "boire"
            else:
                life["observer_resource_acquisition"]["steps"][0]["decision_funding"] = "NO_FUNDED_SCORE"
            with self.assertRaises(ValueError):
                d.behavioral_summary(life)

    def test_information_counts_are_observed_not_inferred(self):
        life = fixture()
        life["observer_full_competition"]["steps"][0]["paid_option_scores"] = [
            {"score_kind": "local_expected_distress", "information_value": 0.2, "unknown_support_queries": 0},
            {"score_kind": "local_expected_distress", "information_value": 0., "unknown_support_queries": 3},
            {"score_kind": "reference"}]
        r = d.behavioral_summary(life)
        self.assertEqual(r["paid_information_options"], 2)
        self.assertEqual(r["positive_information_options"], 1)
        self.assertEqual(r["fully_empirically_supported_options"], 1)

    def test_empty_aggregate_has_undefined_rates_no_survival_claim(self):
        r = d.aggregate([])
        self.assertIsNone(r["reference"]["inactive_fraction"])
        self.assertIsNone(r["reference"]["paid_per_lived_step"]["energy"])
        self.assertEqual(r["reference"]["scientific_verdict"], "NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
