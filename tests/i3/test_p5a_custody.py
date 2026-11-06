"""Pure synthetic P5a custody adversarial test: no new study life/world."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p4a_validation, p5a_schedule, p5a_custody


def seal(out):
    out["sha256"] = sha256(json.dumps(
        {k:v for k,v in out.items() if k!="sha256"},
        sort_keys=True, separators=(",",":")).encode()).hexdigest()


def synthetic():
    frozen=p4a_validation.verify_frozen_genomes()
    receipts=[]
    for alloc in p5a_schedule.manifest()["allocation"]:
        p,family,repeat=alloc["population"],alloc["family"],alloc["repeat"]
        for arm in p5a_schedule.ARMS:
            for slot in range(p5a_schedule.GENOTYPES):
                genome=frozen[(p,arm,slot)]["genome_sha256"]
                for mode in p5a_schedule.MODES:
                    i=len(receipts)
                    receipts.append({
                        "population":p,"arm":arm,"slot":slot,"family":family,
                        "repeat":repeat,"mode":mode,
                        "validation_world_index":alloc["index"],
                        "life_seed":alloc["life_seed"],
                        "genome_sha256":genome,
                        "world_sha256":("%064x" % (alloc["index"]+1)),
                        "source_sha256":"a"*64,
                        "manifest_id":f"synthetic-manifest-{i}",
                        "evidence_head":f"synthetic-evidence-{i}",
                        "trace_head":f"synthetic-trace-{i}",
                        "terminal":"censored","censored":True,
                        "steps_lived":400,"death_causes":[],
                        "paid":{"energy":2.0,"vigilance":3.0},
                        "phase_paid":{"decision":{"energy":1.0,"vigilance":2.0},
                                      "learning":{"energy":1.0,"vigilance":1.0}},
                        "phase_work":{
                            "decision":{"cycles":1,"simulated_steps":1,"memory_items":0,"replays":0},
                            "learning":{"cycles":1,"simulated_steps":1,"memory_items":1,"replays":0}},
                        "inactive_steps":0,"learning_computations":1,
                        "replays_executed":0,
                        "outcome_model_sha256":f"model-{i}",
                        "spatial_beliefs_sha256":f"spatial-{i}",
                    })
    out={"schema":p5a_schedule.PROTOCOL,
         "source_sha":p5a_custody.EXPECTED_SOURCE_SHA,
         "schedule_sha256":p5a_custody.EXPECTED_SCHEDULE_SHA,
         "frozen_g2_sha256":p5a_schedule.p4a_schedule.G2_CANONICAL_SHA256,
         "status":"P5A_COMPONENT_SCREEN_NO_P4_RESERVE",
         "total_lives":1152,"lives":receipts}
    seal(out)
    return out


class P5aCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=synthetic()

    def test_complete_synthetic_record_has_no_study_world_exposure(self):
        result=p5a_custody.verify_original(self.fixture)
        self.assertEqual(result["total_lives"],1152)
        self.assertEqual(result["worlds"],24)
        self.assertEqual(result["paired_genomes_modes"],288)
        self.assertTrue(all(x["mean_difference_lives_per_population_of_72"]==0
                            for x in result["comparisons"].values()))

    def test_changing_unsealed_payload_is_rejected(self):
        bad=deepcopy(self.fixture)
        bad["lives"][0]["steps_lived"]=399
        with self.assertRaises(ValueError):
            p5a_custody.verify_original(bad)

    def test_resigned_wrong_world_still_rejected(self):
        bad=deepcopy(self.fixture)
        bad["lives"][0]["validation_world_index"]=0
        seal(bad)
        with self.assertRaises(ValueError):
            p5a_custody.verify_original(bad)

    def test_resigned_inconsistent_phase_payment_rejected(self):
        bad=deepcopy(self.fixture)
        bad["lives"][0]["phase_paid"]["learning"]["energy"]=0.0
        seal(bad)
        with self.assertRaises(ValueError):
            p5a_custody.verify_original(bad)

    def test_identical_behavior_hashes_across_modes_are_valid(self):
        paired=deepcopy(self.fixture)
        paired["lives"][0]["evidence_head"]=paired["lives"][1]["evidence_head"]
        paired["lives"][0]["trace_head"]=paired["lives"][1]["trace_head"]
        seal(paired)
        self.assertEqual(p5a_custody.verify_original(paired)["total_lives"],1152)

    def test_duplicate_experimental_identity_rejected_even_with_new_hash(self):
        bad=deepcopy(self.fixture)
        bad["lives"][0]["mode"]=bad["lives"][1]["mode"]
        bad["lives"][0]["evidence_head"]="changed-but-present"
        seal(bad)
        with self.assertRaises(ValueError):
            p5a_custody.verify_original(bad)


if __name__=="__main__":
    unittest.main()
