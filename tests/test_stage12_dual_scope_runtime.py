"""Opt-in B uses one Action Control owner, real UC, and lived receipts."""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_runtime import Stage12Runtime
from lab.independent_journal_audit import audit_export_bytes


def born(path, *, dual=True, join=False, life_id="dual:life:1", m11=False):
    st11=build_stage11_reference_runtime(autonomous_mortal=True)
    st10=build_stage10_reference_runtime(autonomous_mortal=True)
    sleep=replace(st10._stage10_config.sleep,
        fatigue_gain=0.0,night_weight=0.0,consolidation_weight=0.0)
    config=replace(st10._stage10_config,
        stage9=st11._stage11_config.stage9,sleep=sleep)
    return Stage12Runtime(
        world_config=st11.world.config,layout=st11.world._layout,
        safety_config=st11.stage3.substrate.safety._config,
        safety_facts=st11._canonical_safety._innate,
        protected_integrity_threshold=st11.stage3.control._config.protected_integrity_threshold,
        stage11_config=st11._stage11_config,stage10_config=config,
        equipment=st11.equipment,autonomous_mortal=True,
        wal_path=None if m11 else str(path),
        m11_sqlite_custody=m11,birth_life_id=life_id,
        subjective_goal_agency=True,dual_scope_agency=dual,
        dual_scope_cost_uc=1,goal_agency_cost_uc=1,
        attribution_join=join,attribution_join_cost_uc=1,
        diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-dual-scope-live-v1",window=12,
            stagnation_steps=3,stagnation_tolerance=0.05,
            loop_repetitions=2,loop_max_period=2,
            entropy_min_samples=3,entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2,attribution_bias_threshold=0.75),
    )


class DualScopeRuntimeTests(unittest.TestCase):
    def test_birth_rejects_legacy_ga06_join(self):
        with TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"GA-06"):
                born(Path(d)/"x.wal",join=True)

    def test_live_uc_receipts_and_no_distal_causal_claims(self):
        with TemporaryDirectory() as d:
            runtime=born(Path(d)/"dual.wal")
            self.assertIsNotNone(runtime.stage3.control.dual_scope)
            self.assertEqual(len(set(x.owner_id for x in runtime.causal_owners)),
                             len(runtime.causal_owners))
            self.assertIn("dual_scope",runtime.stage3.control.export_causal_state())
            self.assertEqual(runtime._config.compute_budget.operation_costs[
                "goal_outcome_responsibility_assessment"],1)
            for _ in range(14):
                if runtime.stage3.substrate.mortal_status.value!="active":
                    break
                runtime.run_step()
            raw=runtime.journal.canonical_bytes()
            report=audit_export_bytes(raw,expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries))
            self.assertGreaterEqual(report.world_steps_closed,1)
            events=[json.loads(line)["causal_event"] for line in raw.splitlines()]
            commitments=[e for e in events if e["kind"]=="stage12_outcome_responsibility_precommitted"]
            decisions=[e for e in events if e["kind"]=="stage12_outcome_responsibility_judgement"]
            charges=[e for e in events if e["kind"]=="compute_charge"
                and e["data"].get("operation")=="goal_outcome_responsibility_assessment"]
            self.assertEqual(len(decisions),len(charges))
            self.assertGreaterEqual(len(commitments),len(decisions))
            for event in decisions:
                self.assertEqual(event["data"]["subjective_responsibility"],"unknown"
                    if event["data"]["observed_outcome"]!="unavailable" else "unavailable")
                self.assertIn(event["data"]["proximal_agency"],
                              ("self","world","unknown","unavailable"))
            self.assertIsNone(runtime._meta_custody.attribution_pairs)

    def test_legacy_birth_does_not_add_schema_or_credits(self):
        with TemporaryDirectory() as d:
            rt=born(Path(d)/"legacy.wal",dual=False)
            self.assertIsNone(rt.stage3.control.dual_scope)
            self.assertNotIn("dual_scope",rt.stage3.control.export_causal_state())
            self.assertNotIn("goal_outcome_responsibility_assessment",
                             rt._config.compute_budget.operation_costs)


if __name__=="__main__":
    unittest.main()
