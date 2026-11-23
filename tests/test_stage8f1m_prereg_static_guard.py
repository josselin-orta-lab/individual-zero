"""Adversarial no-birth tests for the F1M frozen prospective registration.

No i3/Mind/World import; no holder of F1M seed may execute a World.step.
"""
from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools import stage8f1m_prereg_static_guard as P


class TestF1MPreregLockedBeforeAnyExposure(unittest.TestCase):
    def setUp(self):
        self.grid = json.loads(P.GRID.read_bytes())

    def test_exact_git_blobs_reference_and_literal_32_seed_gate(self):
        x=P.check_files()
        self.assertEqual(x["status"], "F1M_PREREG_STATIC_PASS_NO_EXPOSURE")
        self.assertEqual((x["roots"],x["ecologies"],x["within_root_pairs"]),
                         (32,8,64))
        self.assertEqual((x["all_arm_continuations"],x["all_native_R_shams"]),
                         (128,128))

    def test_prereg_cannot_be_turned_into_permission_for_science(self):
        for key in ("scientific_exposure_authorized",
                    "scientific_workflow_dispatch_allowed"):
            q=deepcopy(self.grid)
            q[key]=True
            with self.assertRaises(AssertionError):
                P.validate_grid(q)
        q=deepcopy(self.grid)
        q["phase"]="SCIENTIFIC_RELEASE"
        with self.assertRaises(AssertionError):
            P.validate_grid(q)

    def test_no_heldout_seed_reuse_or_grid_tampering(self):
        q=deepcopy(self.grid)
        q["origins"][0]["seed"]=202611229501
        with self.assertRaises(AssertionError):
            P.validate_grid(q)
        q=deepcopy(self.grid)
        q["origins"][0]["seed"]=self.grid["origins"][1]["seed"]
        with self.assertRaises(AssertionError):
            P.validate_grid(q)
        q=deepcopy(self.grid)
        q["origins"][0]["body"][0]+=1
        with self.assertRaises(AssertionError):
            P.validate_grid(q)
        q=deepcopy(self.grid)
        q["ecologies"][0]["water_restock_every"]=1
        with self.assertRaises(AssertionError):
            P.validate_grid(q)

    def test_motor_vs_adaptive_thresholds_remain_independent(self):
        q=deepcopy(self.grid)
        q["motor_estimand"]["minimum_changed_t6_motor_pairs"]=2
        with self.assertRaises(AssertionError):
            P.validate_grid(q)
        q=deepcopy(self.grid)
        q["adaptive_estimand"]["maximum_negative_survival_pairs"]=1
        with self.assertRaises(AssertionError):
            P.validate_grid(q)
        q=deepcopy(self.grid)
        q["adaptive_estimand"]["secondary_body_pareto"]["verdict"]="SURVIVAL_ADVANTAGE"
        with self.assertRaises(AssertionError):
            P.validate_grid(q)

    def test_cost_gate_and_source_policy_cannot_be_renamed(self):
        q=deepcopy(self.grid)
        q["hard_gates"].pop()
        with self.assertRaises(AssertionError):
            P.validate_grid(q)
        q=deepcopy(self.grid)
        q["source_policy"]="i3.modules.mind.Mind"
        with self.assertRaises(AssertionError):
            P.validate_grid(q)
        q=deepcopy(self.grid)
        q["memory_contents"][1]="synthetic_stats"
        with self.assertRaises(AssertionError):
            P.validate_grid(q)


if __name__=="__main__":
    unittest.main()
