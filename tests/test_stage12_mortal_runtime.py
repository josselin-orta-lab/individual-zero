"""Stage12 lived diagnosis is one mortal Metacognition facet, not an Oracle."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory
import unittest

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.independent_journal_audit import audit_export_bytes
from lab.compute_budget import BudgetCharge
from lab.journal import HashChainedJournal
from lab.mortal_execution import MortalStatus
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_runtime import Stage12Runtime
from lab.world import Command


def stage12_runtime(path, *, detector_cost=1):
    stage11 = build_stage11_reference_runtime(autonomous_mortal=True)
    stage10 = build_stage10_reference_runtime(autonomous_mortal=True)
    sleep = replace(
        stage10._stage10_config.sleep,
        fatigue_gain=0.0, night_weight=0.0,
        consolidation_weight=0.0,
    )
    config = replace(
        stage10._stage10_config,
        stage9=stage11._stage11_config.stage9,
        sleep=sleep,
    )
    return Stage12Runtime(
        world_config=stage11.world.config,
        layout=stage11.world._layout,
        safety_config=stage11.stage3.substrate.safety._config,
        safety_facts=stage11._canonical_safety._innate,
        protected_integrity_threshold=(
            stage11.stage3.control._config.protected_integrity_threshold
        ),
        stage11_config=stage11._stage11_config,
        stage10_config=config,
        equipment=stage11.equipment,
        wal_path=path,
        autonomous_mortal=True,
        diagnostic_sample_cost_uc=detector_cost,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-mortal-live-dev-v1",
            window=12, stagnation_steps=3, stagnation_tolerance=0.05,
            loop_repetitions=2, loop_max_period=2,
            entropy_min_samples=3, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        ),
    )


class Stage12RuntimeMortalTests(unittest.TestCase):
    def test_waking_diags_and_durable_journal_share_single_causal_owner(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "i0-stage12.jsonl")
            runtime = stage12_runtime(path)
            owners = [item.owner_id for item in runtime.causal_owners]
            self.assertEqual(owners.count("metacognition_health"), 1)
            self.assertEqual(len(owners), len(set(owners)))
            self.assertIsNone(runtime.stage3.substrate.bench)
            self.assertIsNone(runtime.stage3.substrate.evaluation_trace)
            self.assertTrue(runtime.journal.durable_wal_enabled)

            for _ in range(7):
                result = runtime.run_step()
                self.assertEqual(result.execution_status, "applied")
            reports = [
                row.causal_event
                for row in runtime.journal.entries
                if row.causal_event.get("kind") == "stage12_lived_diagnostics_published"
            ]
            self.assertGreaterEqual(len(reports), 1)
            self.assertEqual(len(reports), runtime.detection_report.evidence_samples)
            self.assertTrue(all(
                entry["data"]["operator_only_diagnostic"] is True
                and entry["data"]["charged_diagnostic_uc"] == 1
                for entry in reports
            ))
            self.assertTrue(all(
                entry["data"]["attribution_bias"] is None
                for entry in reports
            ))
            state = runtime._meta_custody.export_causal_state()
            with self.assertRaises(ValueError):
                runtime._meta_custody.restore_causal_state({
                    **deepcopy(state),
                    "last_visible_goal_deficit": {"goal_ref": "forged"},
                })
            self.assertEqual(runtime._meta_custody.export_causal_state(), state)
            runtime._meta_custody.restore_causal_state(state)

            self.assertTrue(runtime.journal.verify())
            durability = HashChainedJournal.audit_durable_wal(path)
            self.assertEqual(durability["head_hash"], runtime.journal.head_hash)
            offline = audit_export_bytes(
                runtime.journal.canonical_bytes(),
                expected_head=runtime.journal.head_hash,
                expected_count=len(runtime.journal.entries),
            )
            self.assertEqual(offline.world_steps_closed, runtime.scheduler.t_monde)
            self.assertEqual(offline.terminal_deaths, 0)

    def test_stage12_budget_is_additive_to_stage10_sleep_allowance(self):
        # The Stage11 parent config has not yet installed Stage10 sleep UC.
        # Check both independent allowances survive cooperative construction,
        # instead of a missing key, silent overwrite or a second Meta owner.
        for detector_cost in (1, 3):
            with self.subTest(detector_cost=detector_cost), TemporaryDirectory() as directory:
                runtime = stage12_runtime(
                    str(Path(directory) / "additive-stage12-wal.jsonl"),
                    detector_cost=detector_cost,
                )
                before_sleep = (
                    runtime._stage11_config.with_budget()
                    .stage8.stage7.stage6.stage4.compute_budget
                )
                actual = runtime.compute_budget._config
                sleep_uc = runtime._stage10_config.sleep_option_uc
                expected_meta_uc = max(
                    before_sleep.module_envelopes.get("metacognition_health", 0),
                    sleep_uc,
                ) + detector_cost
                self.assertEqual(
                    actual.module_envelopes["metacognition_health"], expected_meta_uc,
                )
                self.assertEqual(
                    actual.cycle_ceiling,
                    before_sleep.cycle_ceiling + sleep_uc + 1 + detector_cost,
                )
                self.assertEqual(
                    actual.operation_costs["sleep_option_prepare"], sleep_uc,
                )
                self.assertEqual(
                    actual.operation_costs["stage12_diagnostic_sample"], detector_cost,
                )
                self.assertEqual(
                    [owner.owner_id for owner in runtime.causal_owners].count(
                        "metacognition_health"
                    ), 1,
                )
                self.assertTrue(runtime.journal.durable_wal_enabled)

    def test_budget_refusal_creates_no_synthetic_metacognitive_observation(self):
        with TemporaryDirectory() as directory:
            runtime = stage12_runtime(str(Path(directory) / "insufficient-uc.jsonl"))
            original = runtime.compute_budget.charge

            def refuse_diagnostic(*, module, operation, count=1):
                if operation == "stage12_diagnostic_sample":
                    return BudgetCharge(
                        accepted=False, module=module, operation=operation,
                        requested_uc=1,
                        consumed_cycle_uc=runtime.compute_budget.consumed_cycle_uc,
                        consumed_module_uc=runtime.compute_budget.consumed_module_uc(module),
                        reason="module_envelope",
                    )
                return original(module=module, operation=operation, count=count)

            with patch.object(runtime.compute_budget, "charge", side_effect=refuse_diagnostic):
                result = runtime.run_step()
            self.assertEqual(result.execution_status, "applied")
            self.assertEqual(runtime.detection_report.evidence_samples, 0)
            kinds = [row.causal_event["kind"] for row in runtime.journal.entries]
            self.assertIn("stage12_lived_diagnostics_deferred", kinds)
            self.assertNotIn("stage12_lived_diagnostics_published", kinds)
            self.assertTrue(runtime.journal.verify())

    def test_invalid_or_free_detector_cost_is_rejected_before_birth(self):
        with TemporaryDirectory() as directory:
            runtime = stage12_runtime(str(Path(directory) / "positive-uc.jsonl"))
            policy = runtime._stage12_detector_policy
            for cost in (0, -1, True, 0.5):
                with self.subTest(cost=cost):
                    with self.assertRaises(ValueError):
                        Stage12Runtime(
                            detector_policy=policy,
                            diagnostic_sample_cost_uc=cost,
                        )

    def test_no_new_diagnostic_after_actual_physical_death(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "terminal-stage12.jsonl")
            runtime = stage12_runtime(path)
            self.assertEqual(runtime.run_step().execution_status, "applied")
            prior_samples = runtime.detection_report.evidence_samples

            runtime.world.apply_scenario_event(
                "set_lethal_zone",
                {"position": runtime.world.position.as_dict(), "active": True},
            )
            substrate = runtime.stage3.substrate
            substrate.open_step()
            physical = substrate.execute(Command("attendre"))
            self.assertEqual(physical.status, "dead")
            self.assertEqual(substrate.mortal_status, MortalStatus.DEAD)
            journal_before = runtime.journal.canonical_bytes()
            with self.assertRaises(RuntimeError):
                runtime.run_step()
            self.assertEqual(runtime.detection_report.evidence_samples, prior_samples)
            self.assertEqual(runtime.journal.canonical_bytes(), journal_before)


if __name__ == "__main__":
    unittest.main()
