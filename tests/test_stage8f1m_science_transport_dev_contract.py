"""One honest DEV_M native life through the SCIENCE transport-shaped code path.

Never instantiates M01..M32. Monkeypatches the *source constructor* of the
scientific-only producer to inject an actual independently funded DEV_M root.
No GitHub claim or event emulation; no access to scientific admission is tested.
All native actions, costs, memories and worlds remain real DEV_M trajectories.
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools import stage8f1m_dev_residual_mediation as DEV
from tools import stage8f1m_independent_dev_cold as DC
from tools import stage8f1m_scientific_native as PROD
from tools import stage8f1m_independent_scientific_cold as SCI_COLD
from tools import stage8f1m_one_shot_evidence as E


class TestF1MTransportDevNativeAndEngineFreeCold(unittest.TestCase):
    def test_first_only_12_gzip_native_and_cold_reconstruct_dev_origin(self):
        grid=DEV.dev_grid(full=False)
        DEV.source_gate(grid)
        origin=grid["origins"][0]
        self.assertTrue(origin["id"].startswith("DEV_M"))
        self.assertIn(origin["seed"],DEV.DEV_ONLY_SEEDS)
        self.assertNotIn(origin["seed"],DEV.RESERVED_L)

        with TemporaryDirectory() as temp:
            dest=Path(temp)
            writer=E.CaseWriter(dest/"parts",[origin["id"]])
            def dev_paid_source(world_grid,first_origin,admission):
                self.assertIs(world_grid,grid)
                self.assertEqual(first_origin,origin)
                return DEV._source(world_grid,first_origin)
            with patch.object(PROD,"_paid_source",side_effect=dev_paid_source):
                native_row=PROD._one(grid,origin,writer,object())
            self.assertTrue(native_row["source"]["source_valid"])
            self.assertEqual(writer.completed,[origin["id"]])
            self.assertEqual(len(writer.entries),12)

            metadata={"origin":origin,
                "case_sha256":native_row["case_sha256"],
                "source_valid":True,
                "comparison":native_row["comparison"],
                "sham_t5_neutral":native_row["comparison"]["t5_full_sham_neutral"]}
            report={"rows":[metadata]}
            E.finish(writer,report,dest,{"dev_only":True,"heldout":False})
            audited=[]
            def verify_one(meta,parts):
                with patch.object(SCI_COLD,"origin_world",side_effect=DC._start_world):
                    audited.append(SCI_COLD.cold_root(grid,meta,parts))
            E.read_bundle(dest,[origin["id"]],verify_one)
            self.assertEqual(len(audited),1)
            result,steps,rounds=audited[0]
            self.assertEqual(result["root"],origin["id"])
            self.assertTrue(result["source_valid"])
            self.assertTrue(result["t5_equal_paid"])
            self.assertTrue(result["t5_sham_neutral"])
            self.assertTrue(result["all_shams_neutral"])
            self.assertTrue(result["all_native_continuations"])
            self.assertTrue(result["recent"]["cost_equal"])
            self.assertTrue(result["stale"]["cost_equal"])
            self.assertGreater(steps,100)
            self.assertGreater(rounds,100)
            print(json.dumps({"phase":"DEV_M_NATIVE_ONLY_SCIENTIFIC_CONTRACT",
                "dev_origin":origin["id"],
                "original_gzip_parts":len(writer.entries),
                "cold_verified_native_steps":steps,
                "cold_verified_substantive_rounds":rounds,
                "recent_T6_motor_changed":result["recent"]["motor_changed"],
                "stale_T6_motor_changed":result["stale"]["motor_changed"],
                "M_HELDOUT_World_step":0},sort_keys=True))


if __name__=="__main__":
    unittest.main()
