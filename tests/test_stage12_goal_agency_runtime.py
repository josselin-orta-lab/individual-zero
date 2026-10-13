"""Opt-in GA producer across genuine mortal WorldBody physical steps."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_runtime import Stage12Runtime
from lab.independent_journal_audit import audit_export_bytes


def opt_in_runtime(wal_path: str):
    st11 = build_stage11_reference_runtime(autonomous_mortal=True)
    st10 = build_stage10_reference_runtime(autonomous_mortal=True)
    sleep = replace(st10._stage10_config.sleep, fatigue_gain=0.0,
                    night_weight=0.0, consolidation_weight=0.0)
    config = replace(st10._stage10_config,
                     stage9=st11._stage11_config.stage9, sleep=sleep)
    return Stage12Runtime(
        world_config=st11.world.config, layout=st11.world._layout,
        safety_config=st11.stage3.substrate.safety._config,
        safety_facts=st11._canonical_safety._innate,
        protected_integrity_threshold=st11.stage3.control._config.protected_integrity_threshold,
        stage11_config=st11._stage11_config, stage10_config=config,
        equipment=st11.equipment, autonomous_mortal=True, wal_path=wal_path,
        subjective_goal_agency=True, goal_agency_cost_uc=1,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="issue110-first-person-real-smoke-v1", window=12,
            stagnation_steps=3, stagnation_tolerance=0.05,
            loop_repetitions=2, loop_max_period=2,
            entropy_min_samples=3, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )


class Stage12FirstPersonIntegratedSmokeTests(unittest.TestCase):
    def test_real_life_ga_enabled_does_not_fabricate_pairs(self):
        with TemporaryDirectory() as root:
            rt = opt_in_runtime(str(Path(root) / "life.wal"))
            self.assertIsNotNone(rt.stage3.control.goal_agency)
            self.assertIn("goal_agency", rt.stage3.control.export_causal_state())
            self.assertEqual(len({o.owner_id for o in rt.causal_owners}),
                             len(rt.causal_owners))
            for _ in range(5):
                self.assertEqual(rt.run_step().execution_status, "applied")
            self.assertIsNone(rt.detection_report.attribution_bias)
            raw = rt.journal.canonical_bytes()
            self.assertEqual(audit_export_bytes(
                raw, expected_head=rt.journal.head_hash,
                expected_count=len(rt.journal.entries),
            ).world_steps_closed, 5)
            self.assertTrue(rt.journal.verify())


if __name__ == "__main__":
    unittest.main()
