"""P5b read-only custody adversarial tests; synthetic receipt identities only."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p4a_validation, p5b_schedule, p5b_custody


def seal(out):
    out["sha256"] = sha256(json.dumps(
        {k: v for k, v in out.items() if k != "sha256"},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def synthetic():
    frozen = p4a_validation.verify_frozen_genomes()
    lives = []
    for w in p5b_schedule.manifest()["exposure"]:
        p, family, repeat = (w["population"], w["family"], w["repeat"])
        for arm in p5b_schedule.ARMS:
            for slot in range(p5b_schedule.GENOTYPES):
                genome_hash = frozen[(p, arm, slot)]["genome_sha256"]
                for mode in p5b_schedule.READOUTS:
                    i = len(lives)
                    lives.append({
                        "population": p, "arm": arm, "slot": slot,
                        "family": family, "repeat": repeat, "mode": mode,
                        "validation_world_index": w["index"],
                        "life_seed": w["life_seed"],
                        "world_sha256": f"{w['index']+1:064x}",
                        "genome_sha256": genome_hash,
                        "source_sha256": "b"*64,
                        "manifest_id": f"synthetic-manifest-{i}",
                        "trace_head": f"synthetic-trace-{i}",
                        "evidence_head": f"synthetic-evidence-{i}",
                        "terminal": "censored", "censored": True,
                        "death_causes": [], "steps_lived": 400,
                        "inactive_steps": 400,
                        "paid": {"energy": 0.0, "vigilance": 0.0},
                        "phase_paid": {
                            phase: {"energy": 0.0, "vigilance": 0.0}
                            for phase in ("decision", "learning")},
                        "phase_work": {
                            phase: dict.fromkeys(
                                ("cycles", "simulated_steps", "memory_items", "replays"), 0)
                            for phase in ("decision", "learning")},
                        "learning_computations": 0, "replays_executed": 0,
                        "decision_status": {
                            "no_processing_budget": 400, "no_funded_score": 0,
                            "control_rejected": 0, "action_admitted": 0},
                        "early_witness": [
                            {"t": t, "action": None, "param": None,
                             "pre_body": [50]*5,
                             "funding": "NO_PROCESSING_BUDGET", "scores": []}
                            for t in range(1, 13)],
                        "outcome_model_sha256": "a"*64,
                        "spatial_beliefs_sha256": "c"*64,
                    })
    result = {
        "schema": p5b_schedule.PROTOCOL,
        "source_sha": p5b_custody.SOURCE_SHA,
        "schedule_sha256": p5b_custody.SCHEDULE_SHA,
        "frozen_g2_sha256": p5b_schedule.p4a_schedule.G2_CANONICAL_SHA256,
        "status": "P5B_READOUT_HELDOUT_NO_RESERVE",
        "total_lives": 1152,
        "lives": lives,
    }
    seal(result)
    return result


class P5bCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = synthetic()

    def test_synthetic_complete_design_and_identical_behavior_hashes_allowed(self):
        candidate = deepcopy(self.fixture)
        for row in candidate["lives"]:
            row["evidence_head"] = "identical-valid-behavior-hash"
        seal(candidate)
        result = p5b_custody.verify(candidate)
        self.assertEqual(result["original_lives"], 1152)
        self.assertEqual(result["worlds"], 24)
        self.assertEqual(result["paired_genome_world_keys"], 288)
        self.assertEqual(set(result["analysis"]["contrasts"]),
                         set(p5b_schedule.READOUTS[1:]))

    def test_original_payload_cannot_change_without_digest_change(self):
        tampered = deepcopy(self.fixture)
        tampered["lives"][0]["steps_lived"] = 399
        with self.assertRaises(ValueError):
            p5b_custody.verify(tampered)

    def test_resigned_wrong_world_is_still_detected(self):
        tampered = deepcopy(self.fixture)
        tampered["lives"][0]["validation_world_index"] = 0
        seal(tampered)
        with self.assertRaises(ValueError):
            p5b_custody.verify(tampered)

    def test_resigned_duplicate_condition_is_still_detected(self):
        tampered = deepcopy(self.fixture)
        tampered["lives"][0]["mode"] = tampered["lives"][1]["mode"]
        seal(tampered)
        with self.assertRaises(ValueError):
            p5b_custody.verify(tampered)

    def test_resigned_false_phase_bill_is_still_detected(self):
        tampered = deepcopy(self.fixture)
        tampered["lives"][0]["phase_paid"]["decision"]["energy"] = 1.0
        seal(tampered)
        with self.assertRaises(ValueError):
            p5b_custody.verify(tampered)


if __name__ == "__main__":
    unittest.main()
