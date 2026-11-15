"""No-life tests for Stage6 native G0 engineering transport."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from i3.lab import stage6_light_native_g0_transport as g0

ROOT = "f5b19af3254e2eaaf8459ac7977f58a423dcacfeac141f7973705abcb354d012"
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
SOURCE_MAP = "5a56a9e52d4d2909bf2dfa64a4ec0066e0b3e814da25fd4df70ee56cc180edbf"

class Stage6NativeG0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = g0.make_plan(ROOT, HEAD, SOURCE_MAP)

    def test_counts_unique_and_paired(self):
        p = self.plan
        self.assertEqual((p["worlds_planned"], p["g0_lives_planned"]), (96, 2304))
        self.assertEqual(len(p["founders"]), 384)
        cases = g0.g0_cases(p)
        self.assertEqual(len(cases), 2304)
        self.assertEqual(len({(x["population"], x["slot"], x["family"], x["repeat"]) for x in cases}), 2304)
        self.assertEqual(len({(x["population"], x["family"], x["repeat"]) for x in cases}), 96)
        self.assertEqual(set(x["arm"] for x in cases), {"shared"})
        self.assertEqual(self.plan["worlds"][0]["logical_world"], 0)
        self.assertEqual(self.plan["worlds"][-1]["logical_world"], 275)
        values = [x[k] for x in p["worlds"] for k in ("world_index", "world_seed", "life_seed")]
        values += [x["genome_seed"] for x in p["founders"]]
        self.assertEqual(len(values), len(set(values)))
        self.assertFalse(p["scientific_admission"])
        self.assertFalse(p["full_stage6_rehearsal_complete"])
        self.assertEqual(g0.make_plan(ROOT, HEAD, SOURCE_MAP), p)

    def test_tampering_rejected(self):
        for key, value in (("status", "AUTHORIZED"), ("scientific_admission", True),
                           ("g0_lives_planned", 11), ("full_stage6_rehearsal_complete", True),
                           ("allocation_sha256", "f"*64)):
            with self.subTest(key=key):
                plan = deepcopy(self.plan)
                plan[key] = value
                with self.assertRaises(ValueError):
                    g0.verify_plan(plan)
        for collection, field in (("worlds", "world_seed"), ("founders", "genome_seed")):
            with self.subTest(field=field):
                plan = deepcopy(self.plan)
                plan[collection][0][field] = 1
                with self.assertRaises(ValueError):
                    g0.verify_plan(plan)

    def test_invalid_roots_and_pins(self):
        for root in ("", "a"*64, "A"*64, "0"*63, "x"*64):
            with self.assertRaises(ValueError):
                g0.make_plan(root, HEAD, SOURCE_MAP)
        with self.assertRaises(ValueError):
            g0.make_plan(ROOT, "bad", SOURCE_MAP)

    def test_historic_contract_stays_denied(self):
        method = json.loads(g0.METHOD.read_text(encoding="utf-8"))
        self.assertEqual(method["status"], "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE")
        self.assertFalse(method["authorization"]["worlds_allowed"])
        with patch.object(g0, "METHOD", Path(__file__)):
            with self.assertRaises((ValueError, PermissionError)):
                g0.make_plan(ROOT, HEAD, SOURCE_MAP)

    def test_sha_before_claim_and_atomic_no_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claim"
            with patch.object(g0, "_verify_checkout", side_effect=PermissionError("wrong source")):
                with self.assertRaises(PermissionError):
                    g0.run_g0(self.plan, path, self.plan["allocation_sha256"])
            self.assertFalse(path.exists())
            with self.assertRaises(PermissionError):
                g0.run_g0(self.plan, path, "f"*64)
            self.assertFalse(path.exists())
            g0._claim(path, self.plan)
            self.assertEqual(json.loads((path / "CLAIM.json").read_text())["status"],
                             "CLAIMED_NO_RETRY_EVEN_IF_PARTIAL")
            with self.assertRaises(FileExistsError):
                g0._claim(path, self.plan)

    def test_checkout_archive_refused(self):
        folder = g0.ROOT / "do-not-create-stage6-archive"
        with self.assertRaises(PermissionError):
            g0.run_g0(self.plan, folder, self.plan["allocation_sha256"])
        self.assertFalse(folder.exists())

if __name__ == "__main__":
    unittest.main()
