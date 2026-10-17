"""External I1 cognitive observer does not know or expose privileged truth."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from inspect_i1_world_report import inspect


class I1ObserverTests(unittest.TestCase):
    def example(self):
        return {
            "schema": "individual-zero-i1-world-run/v1",
            "engine": "I1",
            "status": "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT",
            "scientific_gate": "NOT_EVALUATED",
            "old_cohorts_used_as_oracles": False,
            "model": "i1lab.i1_natural_runtime.I1Runtime",
            "source": {"preset": "oasis", "sha256": "f"*64},
            "run": {"custody": "wal", "seed": 246},
            "environment": {
                "layout": {"lethal_zones": [[9, 8]]},
                "oracle_canary": "DO_NOT_PUBLISH_THIS"
            },
            "lives": [{
                "individual_id": "i1:sample",
                "lifecycle": "active",
                "journal_head": "abc",
                "steps": [
                    {"world_step": 1, "body": {"energy": 40, "food": 45,
                                               "water": 35, "integrity": 100}},
                    {"world_step": 2, "body": {"energy": 38, "food": 44,
                                               "water": 34, "integrity": 100}},
                ],
            }],
        }

    def test_redacts_operator_truth_and_does_not_claim_cognition(self):
        with TemporaryDirectory() as t:
            p = Path(t) / "source.json"
            original = self.example()
            p.write_text(json.dumps(original))
            out = inspect(p)
            self.assertEqual(json.loads(p.read_text()), original)
            self.assertNotIn("DO_NOT_PUBLISH_THIS", json.dumps(out))
            self.assertNotIn("lethal_zones", json.dumps(out))
            self.assertEqual(out["cognition"]["goal_selection"], "NOT_OBSERVED")
            self.assertEqual(out["scientific_gate"], "NOT_EVALUATED")
            self.assertEqual(out["lives"][0]["physical_delta"]["food"], -1)
            self.assertFalse(out["mutates_individual"])

    def test_m11_without_body_fields_does_not_invent_physiology(self):
        with TemporaryDirectory() as t:
            sample = self.example()
            sample["run"]["custody"] = "m11"
            sample["lives"][0]["steps"] = [{"world_step": 1, "generation": 1}]
            p = Path(t) / "source.json"
            p.write_text(json.dumps(sample))
            out = inspect(p)
            self.assertEqual(out["lives"][0]["physical_state"], "NOT_OBSERVED")

    def test_rejects_incomplete_and_fake_scientific_report(self):
        with TemporaryDirectory() as t:
            p = Path(t) / "source.json"
            sample = self.example()
            sample["scientific_gate"] = "GO"
            p.write_text(json.dumps(sample))
            with self.assertRaises(ValueError):
                inspect(p)
            sample["scientific_gate"] = "NOT_EVALUATED"
            sample["status"] = "TECHNICAL_FAILURE"
            p.write_text(json.dumps(sample))
            with self.assertRaises(ValueError):
                inspect(p)


if __name__ == "__main__":
    unittest.main()
