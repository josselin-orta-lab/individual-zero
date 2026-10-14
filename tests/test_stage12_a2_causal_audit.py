"""A2 external cause: autonomously executed, rehashed adversarial tests."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_a2 import run_one
from test_stage12_spatial_integrated_rehash import rechain
from lab.independent_journal_audit import audit_export_bytes
from lab.stage12_a2_causal_audit import audit_stage12_a2_causal_link


class A2CausalAuditTests(unittest.TestCase):
    def test_one_autonomous_a2_world_and_adversarial_rehash(self):
        with TemporaryDirectory() as temp:
            result = run_one(Path(temp) / "a2", "food", True, "audit-fixture")
            self.assertIsNone(result["error"], result["error"])
            self.assertIsNone(result["audit_error"], result["audit_error"])
            raw = (Path(temp) / "a2" / "canonical.jsonl").read_bytes()
            expected = ((2, 3, 1),)
            report = audit_stage12_a2_causal_link(
                raw, expected_interventions=expected)
            self.assertEqual(report.verified_a2_subjective_world_judgements, 1)
            self.assertEqual(report.matching_failure_world_pairs, 1)
            self.assertEqual(report.applied_failure_world_pairs, 1)
            base = [json.loads(l) for l in raw.splitlines()]
            mutations = (
                lambda e: e.__setitem__("phase", "before_step"),
                lambda e: e["payload"]["position"].__setitem__("x", 4),
                lambda e: e.__setitem__("t_monde", 3),
            )
            for mutate in mutations:
                altered = deepcopy(base)
                receipt = next(r["causal_event"] for r in altered
                    if r["causal_event"].get("kind") == "external_input_received"
                    and r["causal_event"].get("phase") == "after_admission")
                mutate(receipt)
                rehashed = rechain(altered)
                # A changed time can already be rejected by the base
                # monotonic-clock auditor; in every case the full audit
                # must reject even a correctly recomputed hash chain.
                with self.assertRaises(ValueError):
                    audit_stage12_a2_causal_link(
                        rehashed, expected_interventions=expected)
            altered = deepcopy(base)
            altered = [r for r in altered if
                r["causal_event"].get("kind") not in
                ("external_input_received", "external_input_applied")]
            rehashed = rechain(altered)
            audit_export_bytes(rehashed)
            with self.assertRaises(ValueError):
                audit_stage12_a2_causal_link(
                    rehashed, expected_interventions=expected)

    def test_free_life_does_not_hallucinate_external_obstacle(self):
        with TemporaryDirectory() as temp:
            r = run_one(Path(temp) / "control", "food", False, "control-fixture")
            self.assertIsNone(r["error"])
            raw = (Path(temp) / "control" / "canonical.jsonl").read_bytes()
            audit = audit_stage12_a2_causal_link(raw, expected_interventions=())
            self.assertEqual(audit.verified_a2_subjective_world_judgements, 0)


if __name__ == "__main__":
    unittest.main()
