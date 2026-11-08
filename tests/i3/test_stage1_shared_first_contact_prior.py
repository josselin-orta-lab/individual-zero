"""Frozen shared-first-contact-prior software checks."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_shared_first_contact_prior as S
from i3.lab import stage1_candidate_g_projection_dependence as D
from i3.lab import stage1_candidate_g_reference_recurrence_falsifier as G
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.recent_rms_effect_prior import (
    paid_recent_rms_zero_mean_effect_prior)
from i3.modules.unknown_action_trial import paid_unknown_action_trial_value
from i3.modules.water_recurrence_opportunity import (
    paid_water_personal_recurrence_value)


class SharedFirstContactPriorTests(unittest.TestCase):
    def test_omega_zero_is_backward_identical_on_imagined_recurrence_path(self):
        body = (80., 80., 40., 80., 80.)
        a = paid_water_personal_recurrence_value(
            D.make_mind("candidate_f_projection"),
            G.effect_memory(), G.recurrence_2_6_10(),
            G.EXPLORE, G.ORDINARY, 8,
            CognitiveBudget(body, BodyLaws()))
        b = paid_water_personal_recurrence_value(
            D.make_mind("candidate_f_projection"),
            G.effect_memory(), G.recurrence_2_6_10(),
            G.EXPLORE, G.ORDINARY, 8,
            CognitiveBudget(body, BodyLaws()), omega=0.0)
        self.assertEqual(a, b)

    def test_perceived_trial_accepts_same_paid_rms_prior(self):
        body = (80., 80., 30., 80., 80.)
        memory = G.effect_memory()
        seen = {}

        def prior_source(allowance):
            prior = paid_recent_rms_zero_mean_effect_prior(
                memory, allowance, omega=0.5)
            seen.update(prior)
            return prior

        result = paid_unknown_action_trial_value(
            D.make_mind("candidate_f_projection"),
            ("boire",),
            (("no-trial", ()),),
            (("stop", ()), ("repeat", (("boire",),))),
            6, CognitiveBudget(body, BodyLaws()),
            prior_source=prior_source)
        self.assertEqual(
            result["prior_record"]["status"], seen["status"])
        self.assertEqual(
            result["prior_record"]["rms_scale"],
            tuple(seen["rms_scale"]))
        self.assertEqual(result["prior_record"]["omega"], 0.5)
        self.assertEqual(
            result["prior_record"]["branch_deltas"],
            tuple(tuple(row.probe_delta) for row in seen["outcomes"]))

    def test_perceived_probe_is_token_renaming_invariant(self):
        body = (60., 20., 80., 50., 80.)
        a = S._perceived_probe(
            body, 8, ("manger", "alpha"), 0.5)
        b = S._perceived_probe(
            body, 8, ("manger", "beta"), 0.5)
        for key in (
                "status", "relevant", "ordinary_scores", "scores", "top",
                "work", "forecast_work_ceiling",
                "body_after_computation", "shared_effect_prior"):
            self.assertEqual(a.get(key), b.get(key))

    def test_frozen_gate_runs_without_live_authority_or_prejudged_capacity(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as fh:
            report = S.run(fh.name)
        self.assertFalse(report["world_access"])
        self.assertEqual(report["lives"], 0)
        self.assertFalse(report["runtime_registered"])
        self.assertFalse(report["motor_command_authorized"])
        self.assertFalse(report["runtime_change_authorized"])
        self.assertFalse(report["new_live_panel_authorized"])
        self.assertEqual(
            report["verdict"],
            (
                "SHARED_FIRST_CONTACT_PRIOR_DEFECT"
                if not all(report["rules"].values())
                else
                "SHARED_FIRST_CONTACT_PRIOR_CAPACITY_SHOWN"
                if report["R1_primary_perceived_water_capacity"]
                else "SHARED_FIRST_CONTACT_PRIOR_NO_CAPACITY"
            ))
        self.assertEqual(report["counts"]["K80"]["0.0"]["states"], 80)
        self.assertEqual(report["counts"]["P80"]["0.0"]["states"], 80)
        self.assertEqual(report["counts"]["F108"]["0.0"]["states"], 108)
        print("SHARED_FIRST_CONTACT_PRIOR_TEST " + json.dumps({
            "verdict": report["verdict"],
            "rules": report["rules"],
            "counts": report["counts"],
            "direction_monotone": report["direction_monotone"],
            "newly_relevant_p80_vs_omega0":
                report["newly_relevant_p80_vs_omega0"],
            "renaming_mismatches": report["renaming_mismatches"],
            "shared_prior_mismatches":
                report["shared_prior_mismatches"],
        }, sort_keys=True))

    def test_import_does_not_load_world_or_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_shared_first_contact_prior; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.lab.worldgen' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
