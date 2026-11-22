"""F1L engine-free cold tests. Input is archived DEV_L native JSON only.

The cold job imports no Mind, World, producer or i3 engine.
Never generate or inspect L01..L32 reserved scientific roots.
"""
from __future__ import annotations

from copy import deepcopy
import gzip
import json
import os
from pathlib import Path
import unittest

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1l_independent_paid_content_cold_audit as Cold


def reseal_native(report):
    """Re-sign corrupt evidence to ensure cold equations, not SHA alone, reject it."""
    for row in report["rows"]:
        source = row["source"]
        for step in source["source_steps"]:
            step["postaction"]["learning_receipt_sha256"] = I.h({
                k: v for k, v in step["postaction"].items()
                if k != "learning_receipt_sha256"})
            step["receipt_sha256"] = I.h({
                k: v for k, v in step.items() if k != "receipt_sha256"})
        source["source_receipt_sha256"] = I.h({
            k: v for k, v in source.items()
            if k != "source_receipt_sha256"})
        for arm in row["arms"].values():
            for step in arm["steps"]:
                step["postaction"]["learning_receipt_sha256"] = I.h({
                    k: v for k, v in step["postaction"].items()
                    if k != "learning_receipt_sha256"})
                step["receipt_sha256"] = I.h({
                    k: v for k, v in step.items() if k != "receipt_sha256"})
            arm["trajectory_sha256"] = I.h({
                k: v for k, v in arm.items()
                if k != "trajectory_sha256"})
        row["case_sha256"] = I.h({
            k: v for k, v in row.items() if k != "case_sha256"})
    report["provenance_sha256"] = I.h({
        "phase": report["phase"],
        "grid_blob_sha": report["grid_blob_sha"],
        "protocol_blob_sha": report["protocol_blob_sha"],
        "cases": [r["case_sha256"] for r in report["rows"]],
    })


@unittest.skipUnless(os.getenv("I3_F1L_COLD_INPUT"),
                     "independent cold runs with DEV_L native artifact only")
class F1LIndependentCold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(os.environ["I3_F1L_COLD_INPUT"])
        raw = path.read_bytes()
        if path.name.endswith(".gz"):
            raw = gzip.decompress(raw)
        cls.report = json.loads(raw)
        if cls.report.get("phase") != "DEV_ONLY":
            raise AssertionError("cold cannot accept a scientific exposure")

    def test_entire_dev_origin_physics_and_paid_competition(self):
        result = Cold.audit(self.report)
        self.assertEqual(result["cold_status"], "DEV_ONLY_NOT_SCIENTIFIC")
        self.assertEqual(result["personal_paid_sources_verified"], result["roots"])
        self.assertEqual(result["whole_trajectory_shams_verified"],
                         result["roots"])
        self.assertEqual(result["T5_equal_real_decision_cost_pairs"],
                         result["roots"])
        self.assertGreater(result["native_world_steps_verified"], 8)
        self.assertGreater(result["substantive_competition_rounds_verified"], 0)
        self.assertEqual(result["scientific_F1L_holdout_exposures"], 0)

    def test_resigned_fictional_second_competition_cycle_rejected(self):
        forged = deepcopy(self.report)
        s = forged["rows"][0]["arms"]["stale_owned_t1_means"]["steps"][0]
        s["cognitive_work"]["cycles"] += 1
        reseal_native(forged)
        with self.assertRaises((AssertionError, ValueError)):
            Cold.audit(forged)

    def test_resigned_nonpersonal_t1_mean_rejected(self):
        forged = deepcopy(self.report)
        s = forged["rows"][0]["arms"]["stale_owned_t1_means"]["steps"][0]
        exposed = s["exposed_mind_during_decision"]
        items = dict(exposed["data"]["private"]["__dict__"])
        stats = dict(items["effects"]["__effects_model__"]["__dict__"])[
            "stats"]["__dict__"]
        self.assertTrue(stats)
        stats[0][1][1][0] += 3.125
        exposed["sha256"] = I.h(exposed["data"])
        reseal_native(forged)
        with self.assertRaises((AssertionError, ValueError)):
            Cold.audit(forged)

    def test_resigned_fictional_drink_body_rejected(self):
        forged = deepcopy(self.report)
        s = forged["rows"][0]["arms"]["full"]["steps"][0]
        s["native_motor"]["body"][2] += 10.
        reseal_native(forged)
        with self.assertRaises((AssertionError, ValueError)):
            Cold.audit(forged)

    def test_resigned_sham_divergence_rejected(self):
        forged = deepcopy(self.report)
        a = forged["rows"][0]["arms"]["full_sham"]
        a["metrics"]["terminal_body"][0] += 0.5
        reseal_native(forged)
        with self.assertRaises((AssertionError, ValueError)):
            Cold.audit(forged)

    def test_resigned_source_anchor_from_wrong_own_tick_rejected(self):
        forged = deepcopy(self.report)
        s = forged["rows"][0]["source"]
        s["paid_t1_mean_anchor"][0]["stat"][1][0] += 1.0
        reseal_native(forged)
        with self.assertRaises((AssertionError, ValueError)):
            Cold.audit(forged)


if __name__ == "__main__":
    unittest.main()
