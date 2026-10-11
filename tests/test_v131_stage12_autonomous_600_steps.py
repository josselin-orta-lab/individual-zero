"""600 actually executed Stage10/11/12 mortal steps with a durable causal log.

This is a DEVELOPMENT HYPOTHESIS, NOT a scientific result or operator GO.
No Oracle, Bench, replay, life snapshot or death rollback is permitted.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal
from lab.mortal_execution import MortalStatus
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_runtime import Stage12Runtime
from test_stage10_live_sixpass_runtime import configured_runtime


class V131MortalStage12SixHundredSteps(unittest.TestCase):
    def test_six_hundred_real_cognitive_world_steps_and_external_stop(self):
        with TemporaryDirectory() as directory:
            wal_path = str(Path(directory) / "i0-stage12-600.jsonl")
            baseline = build_stage11_reference_runtime(
                enable_geography=True, autonomous_mortal=True,
            )
            sleep_baseline = configured_runtime()
            # Stay awake by an explicitly versioned *development* choice,
            # not an oracle-informed intervention or hidden body repair.
            sleeping = replace(
                sleep_baseline._stage10_config.sleep,
                fatigue_gain=0.0, night_weight=0.0,
                consolidation_weight=0.0,
            )
            stage10_config = replace(
                sleep_baseline._stage10_config,
                stage9=baseline._stage11_config.stage9,
                sleep=sleeping,
            )
            individual = Stage12Runtime(
                world_config=baseline.world.config,
                layout=baseline.world._layout,
                safety_config=baseline.stage3.substrate.safety._config,
                safety_facts=baseline._canonical_safety._innate,
                protected_integrity_threshold=(
                    baseline.stage3.control._config.protected_integrity_threshold
                ),
                stage11_config=baseline._stage11_config,
                stage10_config=stage10_config,
                equipment=baseline.equipment,
                autonomous_mortal=True,
                wal_path=wal_path,
                diagnostic_sample_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
                    version="stage12-600-lived-dev-v1",
                    window=12, stagnation_steps=4, stagnation_tolerance=0.05,
                    loop_repetitions=3, loop_max_period=2,
                    entropy_min_samples=4, entropy_warning_fraction=0.25,
                    bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
                ),
            )
            console = Stage12OperatorConsole(
                substrate=individual.stage3.substrate,
                mode="campaign", policy_version="stage12-600-stop-dev-v1",
                maximum_world_steps=600,
            )
            self.assertIsNone(individual.stage3.substrate.bench)
            self.assertIsNone(individual.stage3.substrate.evaluation_trace)
            self.assertTrue(individual.journal.durable_wal_enabled)
            self.assertEqual(
                len({o.owner_id for o in individual.causal_owners}),
                len(individual.causal_owners),
            )
            self.assertEqual(
                sum(o.owner_id == "metacognition_health"
                    for o in individual.causal_owners),
                1,
            )

            actions = Counter()
            for world_step in range(1, 601):
                actual = individual.run_step()
                self.assertEqual(
                    actual.execution_status, "applied",
                    f"world step {world_step} ended {actual.execution_status}",
                )
                self.assertEqual(individual.scheduler.t_monde, world_step)
                self.assertEqual(
                    individual.stage3.substrate.mortal_status,
                    MortalStatus.ACTIVE,
                )
                actions[actual.command_primitive] += 1
            self.assertEqual(sum(actions.values()), 600)
            self.assertEqual(individual.sleep_session.mode, "awake")

            # No 601st world step is invented to enforce the cap.
            with self.assertRaisesRegex(RuntimeError, "cap"):
                individual.run_step()
            self.assertEqual(individual.scheduler.t_monde, 600)
            self.assertEqual(
                individual.stage3.substrate.mortal_status,
                MortalStatus.EXPERIMENT_STOPPED,
            )
            self.assertIsNone(
                individual.stage3.substrate._mortal_boundary.terminal_death,
            )
            journal = individual.journal
            self.assertTrue(journal.verify())
            kinds = Counter(e.causal_event.get("kind") for e in journal.entries)
            self.assertEqual(kinds["perceptual_capture"], 600)
            self.assertEqual(kinds["world_transition_experienced"], 600)
            self.assertEqual(kinds["auto_segment_commit"], 600)
            self.assertEqual(kinds["stage12_lived_diagnostics_published"], 600)
            charges = [
                row.causal_event["data"]
                for row in journal.entries
                if (row.causal_event.get("kind") == "compute_charge"
                    and row.causal_event.get("data", {}).get("operation")
                        == "stage12_diagnostic_sample")
            ]
            self.assertEqual(len(charges), 600)
            self.assertTrue(all(
                charge["accepted"] is True
                and charge["requested_uc"] == 1
                and charge["reason"] is None
                for charge in charges
            ))
            self.assertEqual(kinds["experiment_stopped"], 1)
            self.assertFalse(any("rollback" in str(k) for k in kinds))
            self.assertFalse(individual.stage3.substrate.snapshots._snapshots)
            self.assertEqual(journal.entries[-1].causal_event["kind"], "experiment_stopped")
            audited = audit_export_bytes(
                journal.canonical_bytes(), expected_head=journal.head_hash,
                expected_count=len(journal.entries),
            )
            self.assertEqual(audited.world_steps_closed, 600)
            self.assertEqual(audited.autobiographical_commits, 600)
            self.assertEqual(audited.terminal_deaths, 0)
            durability = HashChainedJournal.audit_durable_wal(wal_path)
            self.assertEqual(durability["verified_entries"], len(journal.entries))
            self.assertEqual(durability["head_hash"], journal.head_hash)
            with self.assertRaises(RuntimeError):
                individual.run_step()


if __name__ == "__main__":
    unittest.main()
