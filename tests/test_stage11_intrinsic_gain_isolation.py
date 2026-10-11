"""Stage-11 public coefficient ablation: intrinsic curiosity never changes g.

Controlled development software fixture, NOT separate full A/B birth
temperaments, independent held-out science, or historical Golden acceptance.
The prospective protocol is stage11-intrinsic-exploration-gain-isolation-protocol.en.md.
"""
from dataclasses import replace
from unittest import TestCase

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.snapshots import SnapshotType
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_runtime import Stage11Runtime
from lab.world import BodyState


class Stage11IntrinsicGainIsolationTests(TestCase):
    def test_low_high_exploration_change_ma_not_competition_gain(self):
        source = build_stage11_reference_runtime(enable_geography=True)
        satisfied = BodyState(
            energy=50, food=60, water=60, integrity=100,
        )
        base_config = source._stage11_config

        def run_once(axis):
            params = replace(
                base_config.temperament_parameters,
                exploration_coefficient=axis,
            )
            version = (
                "stage11-public-intrinsic-axis-A-minus1-v1"
                if axis == -1.0
                else "stage11-public-intrinsic-axis-B-plus1-v1"
            )
            config = replace(
                base_config, version=version,
                temperament_parameters=params,
            )
            runner = Stage11Runtime(
                world_config=replace(
                    source.world.config, initial_body=satisfied,
                ),
                layout=source.world._layout,
                safety_config=source.stage3.substrate.safety._config,
                safety_facts=source._canonical_safety._innate,
                protected_integrity_threshold=(
                    source.stage3.control._config.protected_integrity_threshold
                ),
                config=config, equipment=source.equipment,
            )
            self.assertEqual(runner.exploration.coefficient, axis)
            self.assertEqual(
                runner.competition._config.gain,
                config.stage9.stage8.stage7.stage6.stage4.competition.gain,
            )
            manager = runner.stage3.substrate.snapshots
            physical_actions = []
            captured_snapshot = None
            for step in range(1, 6):
                result = runner.run_step()
                physical_actions.append((
                    result.source, result.execution_status,
                    result.command_primitive, result.option_ref,
                ))
                if step == 4:
                    captured_snapshot = manager.take(
                        snapshot_type=SnapshotType.PERIODIC,
                        individual_id=runner.individual_id,
                        t_monde=step, cycle=0, attempt_ref=None,
                        owners=runner.causal_owners,
                        versions={"stage11":config.version},
                    )
                    self.assertTrue(manager.verify(captured_snapshot.id))
            events = [entry.causal_event for entry in runner.journal.entries]
            intrinsic = [
                event["data"]["intrinsic_value"]
                for event in events
                if event.get("kind") == "stage11_intrinsic_evaluation"
                and event["data"]["option_ref"].startswith("option:geographic:")
            ]
            visits = [
                (
                    event["data"]["position"]["x"],
                    event["data"]["position"]["y"],
                )
                for event in events
                if event.get("kind") == "perceptual_capture"
            ]
            self.assertEqual(len(visits), 5)
            self.assertTrue(intrinsic)
            self.assertTrue(runner.journal.verify())
            raw_state = {
                owner.owner_id: owner.export_causal_state()
                for owner in runner.causal_owners
            }
            self.assertIsNotNone(captured_snapshot)
            before_restore_sha = sha256_hex(runner.journal.canonical_bytes())
            manager.restore(captured_snapshot.id, owners=runner.causal_owners)
            self.assertTrue(manager.verify(captured_snapshot.id))
            self.assertTrue(runner.journal.verify())
            return {
                "axis": axis,
                "stage11_version": version,
                "budget_version": runner._config.compute_budget.version,
                "gain": runner.competition._config.gain,
                "uc_costs": dict(runner._config.compute_budget.operation_costs),
                "uc_envelopes": dict(runner._config.compute_budget.module_envelopes),
                "actions": tuple(physical_actions),
                "visits": tuple(visits),
                "intrinsic": tuple(intrinsic),
                "owner_sha_before_restore": sha256_hex(
                    canonical_causal_bytes(raw_state),
                ),
                "snapshot_id": captured_snapshot.id,
                "snapshot_sha": captured_snapshot.sha256,
                "journal_before_restore": before_restore_sha,
                "journal_after_restore": sha256_hex(
                    runner.journal.canonical_bytes(),
                ),
            }

        low_a = run_once(-1.0)
        low_b = run_once(-1.0)
        high_a = run_once(1.0)
        high_b = run_once(1.0)
        self.assertEqual(low_a, low_b)
        self.assertEqual(high_a, high_b)
        self.assertNotEqual(
            low_a["stage11_version"], high_a["stage11_version"],
        )
        self.assertNotEqual(
            low_a["budget_version"], high_a["budget_version"],
        )
        self.assertEqual(low_a["gain"], high_a["gain"])
        self.assertEqual(low_a["uc_costs"], high_a["uc_costs"])
        self.assertEqual(low_a["uc_envelopes"], high_a["uc_envelopes"])
        self.assertTrue(all(
            value is None or value <= 0.0
            for value in low_a["intrinsic"]
        ))
        self.assertTrue(any(
            value is not None and value > 0.0
            for value in high_a["intrinsic"]
        ))
        self.assertTrue(any(
            status == "applied" and command == "se_deplacer"
            and option is not None
            and option.startswith("option:geographic:")
            for _, status, command, option in high_a["actions"]
        ))
        self.assertGreater(len(set(high_a["visits"])), 1)
        self.assertTrue(all(
            not (status == "applied"
                 and option is not None
                 and option.startswith("option:geographic:"))
            for _, status, _, option in low_a["actions"]
        ))
