"""P5a screen must not open any scientific world before preregistration."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies, p4a_validation, p5a_schedule, p5a_screen
from i3.modules.genome import generation_zero
from i3.runtime.life import run_life


class P5aScreenTests(unittest.TestCase):
    def test_schedule_unique_untouched_indices(self):
        x=p5a_schedule.manifest()
        self.assertEqual(x,p5a_schedule.manifest())
        self.assertEqual(len(x["allocation"]),24)
        self.assertEqual(x["total_lives"],1152)
        self.assertEqual({w["index"] for w in x["allocation"]},set(range(48,72)))
        self.assertEqual({w["world_seed"] for w in x["allocation"]},set(range(30048,30072)))
        self.assertEqual(x["modes"],["normal","discard_effects","discard_values","discard_replay"])
        self.assertEqual(x["analysis_unit"],"independent_P3_population_n4")
        for bad in ((-1,"stable",0),(4,"stable",0),(0,"bogus",0),(0,"pulse",2),(True,"stable",0)):
            with self.assertRaises(ValueError):
                p5a_schedule.world_index(*bad)

    def test_frozen_genomes_and_no_study_world(self):
        with patch.object(p2_ecologies,"world_for",side_effect=AssertionError("study world opened")):
            self.assertEqual(len(p4a_validation.verify_frozen_genomes()),48)
            self.assertEqual(len(p5a_schedule.manifest()["allocation"]),24)

    def test_launch_without_approval_fails_before_world(self):
        with patch.dict(os.environ,{},clear=True),patch.object(
            p2_ecologies,"world_for",side_effect=AssertionError("study world opened")
        ):
            with self.assertRaises(RuntimeError):
                p5a_screen.run()

    def test_receipt_rejects_fake_incomplete_and_unpaid_life(self):
        # Development only: even this falsifier must never touch selection.
        spec=p2_ecologies.world_for("stable","development",17)
        genome=generation_zero(888)
        from i3.modules.genome import digest as genome_digest
        from i3.runtime.provenance import digest,world_snapshot
        out=run_life(genome,spec,700,400,keep_trace=True,
                     observer_mind_digest=True,learning_mode="normal")
        kw=dict(mode="normal",arm="selected",slot=0,population=0,
                family="stable",repeat=0,index=48,seed=700,
                world_hash=digest(world_snapshot(spec)),
                genome_sha256=genome_digest(genome))
        verified=p5a_screen._receipt(out,**kw)
        self.assertEqual(verified["steps_lived"],len(out["trace"]))
        from copy import deepcopy
        fake=deepcopy(out)
        fake["trace"].pop()
        with self.assertRaises(RuntimeError):
            p5a_screen._receipt(fake,**kw)
        fake=deepcopy(out)
        fake["cognitive_accounting"]["totals"]["energy"]["unpaid"]=1.0
        with self.assertRaises(RuntimeError):
            p5a_screen._receipt(fake,**kw)
        fake=deepcopy(out)
        fake["cognitive_accounting"]["replays_executed"]+=1
        with self.assertRaises(RuntimeError):
            p5a_screen._receipt(fake,**kw)

    def test_sign_flip_n4_resolution_and_holm(self):
        self.assertEqual(p5a_screen._two_sided_sign_flip_p([1,1,1,1]),.125)
        self.assertEqual(p5a_screen._two_sided_sign_flip_p([0,0,0,0]),1)
        self.assertEqual(p5a_screen._holm_adjust({"effects":.02,"values":.03,"replay":.5}),
                         {"effects":.06,"values":.06,"replay":.5})
        self.assertEqual(p5a_screen._two_sided_sign_flip_p([-1,-1,-1,-1]),.125)


if __name__=="__main__":
    unittest.main()
