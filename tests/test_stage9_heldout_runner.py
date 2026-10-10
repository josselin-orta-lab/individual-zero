"""Synthetic-only regressions for the independently operated Stage-9 runner.

These fixtures are software checks, never preregistered held-out science.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.injected_scenario import ScenarioEvent
from lab.stage9_heldout_runner import (
    ANNOTATIONS_VERSION, EQUIPMENT_VERSION, PARAMETER_VERSION,
    RUN_VERSION, WORLD_VERSION, _cell_run, _external_release,
    _frozen_equipment, _frozen_parameters, _json_file, _scenario,
    _typed, _world, package_evidence,
)
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage9_scientific_preregistration import validate_registration
from lab.world import WorldPhysicsConfig
from lab.world_generation import WorldGenerationConfig
from tests.test_stage9_scientific_preregistration import example_draft


def _plain(value):
    if is_dataclass(value):
        return {field.name: _plain(getattr(value, field.name))
                for field in fields(value)}
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (frozenset, set, tuple, list)):
        return [_plain(item) for item in (
            sorted(value) if isinstance(value, (frozenset, set)) else value
        )]
    return value


def _components():
    example = build_stage9_reference_runtime()
    parameters = {
        "protocol_version": PARAMETER_VERSION,
        "stage9_config": _plain(example._stage9_config),
        "safety_config": _plain(example.stage3.substrate.safety._config),
        "protected_integrity_threshold":
            example.stage3.control._config.protected_integrity_threshold,
        "innate_safety_facts": _plain(example.stage3.control._facts._innate),
    }
    # This is the historical software fixture, not scientifically calibrated
    # equipment. Its exact table is for the synthetic runner regression only.
    artifact = example.equipment._artifact
    records = list(example.equipment._records.values())
    equipment = {
        "protocol_version": EQUIPMENT_VERSION,
        "artifact": _plain(artifact),
        "records": [_plain(record) for record in records],
    }
    return example, parameters, equipment


def _generator():
    return WorldGenerationConfig(
        version="synthetic-heldout-generator-v1",
        water_source_count=0, berry_a_cells=0, berry_b_cells=0,
        wood_cells=0, stone_cells=0, creature_count=0,
        danger_zone_count=0, quantity_per_resource_cell=1,
        nutritious_food_gain=10.0, toxic_food_gain=0.0,
        toxic_integrity_delta=-10.0,
    )


def _run_cell(*, steps=3, seed=41, scenario=None):
    example, params, equip = _components()
    stage9, safety, threshold, innate = _frozen_parameters(params)
    model = _frozen_equipment(equip)
    if scenario is None:
        scenario = ("dev-no-events", "v1", ())
    return _cell_run(
        world_id="development-only", seed=seed, steps=steps,
        physics=example.world.config,
        generator=_generator(), scenario=scenario,
        config=stage9, safety=safety, threshold=threshold,
        innate=innate, equipment=model,
    )


def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True), encoding="utf-8")


class Stage9HeldoutRunnerTests(unittest.TestCase):

    def test_parameter_and_equipment_manifest_roundtrip_real_runtime(self):
        example, params, equip = _components()
        config, safety, threshold, innate = _frozen_parameters(params)
        self.assertEqual(config, example._stage9_config)
        self.assertEqual(safety.mode, "campaign")
        self.assertGreater(threshold, 0)
        self.assertEqual(innate, example.stage3.control._facts._innate)
        rebuilt = _frozen_equipment(equip)
        self.assertEqual(rebuilt.artifact_digest, example.equipment.artifact_digest)
        self.assertEqual(rebuilt.version, example.equipment.version)

    def test_nested_unexpected_config_or_corrupt_equipment_fail_closed(self):
        _, params, equip = _components()
        params["stage9_config"]["stage8"]["extra_calibration"] = 0.0
        with self.assertRaisesRegex(ValueError, "fields"):
            _frozen_parameters(params)
        _, _, equip = _components()
        equip["artifact"]["model_payload"]["input_hashes"] = []
        with self.assertRaisesRegex(ValueError, "differs"):
            _frozen_equipment(equip)

    def test_invalid_parameter_types_and_fake_safety_mode_rejected(self):
        _, original, _ = _components()
        bad = _plain(original)
        bad["safety_config"]["mode"] = "diagnostic"
        with self.assertRaisesRegex(ValueError, "campaign mode"):
            _frozen_parameters(bad)
        bad = _plain(original)
        bad["stage9_config"]["causal"]["n1"] = True
        with self.assertRaisesRegex(ValueError, "integer"):
            _frozen_parameters(bad)
        bad = _plain(original)
        bad["protected_integrity_threshold"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            _frozen_parameters(bad)

    def test_real_stage9_execution_replays_and_external_scenario_is_logged(self):
        journal, state, truth = _run_cell(
            scenario=("dev-scenario", "dev-v1", (
                ScenarioEvent(
                    t_monde=1, sequence=0, operation="set_body",
                    payload={"water": 80.0},
                ),
            )),
        )
        self.assertGreater(len(journal), 0)
        self.assertIn(b"external_input_received", journal)
        self.assertIn(b"external_input_applied", journal)
        self.assertIn(b"auto_segment_commit", journal)
        self.assertIn(b"causal_model", state)
        self.assertIn(b"memory", state)
        self.assertEqual(truth["seed"], 41)
        self.assertEqual(truth["world_id"], "development-only")
        self.assertEqual(truth["scenario_id"], "dev-scenario")
        self.assertEqual(sha256_hex(journal), sha256(journal).hexdigest())

    def test_invalid_scenario_steps_duplicates_and_operation_rejected(self):
        for raw in (
            {"id": "dev", "version": "v1", "events": [
                {"t_monde": 0, "sequence": 0, "operation": "set_body",
                 "payload": {"water": 40}},
            ]},
            {"id": "dev", "version": "v1", "events": [
                {"t_monde": 1, "sequence": 0, "operation": "inject_hypothesis",
                 "payload": {}},
            ]},
            {"id": "dev", "version": "v1", "events": [
                {"t_monde": 1, "sequence": 0, "operation": "set_body",
                 "payload": {"water": 40}},
                {"t_monde": 1, "sequence": 0, "operation": "set_body",
                 "payload": {"water": 50}},
            ]},
        ):
            with self.subTest(events=raw["events"]):
                with self.assertRaises(ValueError):
                    _scenario(raw, 3)

    def test_world_manifest_is_not_a_diagnostic_fixture(self):
        example, _, _ = _components()
        good = {
            "protocol_version": WORLD_VERSION, "world_id": "world-A",
            "physics": example.world.config.as_dict(),
            "scenario": {"id": "dev", "version": "v1", "events": []},
        }
        self.assertIsInstance(_world(good, world_id="world-A", steps=3)[0],
                              WorldPhysicsConfig)
        with self.assertRaisesRegex(ValueError, "registered world"):
            _world(good, world_id="world-B", steps=3)

    def test_approval_record_rejects_missing_or_spoofed_go(self):
        draft = example_draft()
        digest = validate_registration(draft)
        registered = "b" * 40
        record = {
            "protocol_version": "stage9-heldout-operator-release-record-v1",
            "registration_digest": digest,
            "frozen_implementation_commit": draft["frozen_implementation_commit"],
            "registration_commit": registered,
            "authorization": "GO", "research_owner": "owner",
            "custodian": "custodian", "operator": "operator",
            "independent_evaluator": "evaluator",
            "approval_evidence_ref": "operator-only-record",
            "independent_timestamp_ref": "external-timestamp",
        }
        _external_release(record, draft, registered)
        for key, value in (
            ("authorization", "NO-GO"),
            ("registration_digest", "0" * 64),
            ("independent_timestamp_ref", ""),
            ("registration_commit", "c" * 40),
        ):
            with self.subTest(field=key):
                modified = dict(record, **{key: value})
                with self.assertRaisesRegex(ValueError, "GO record"):
                    _external_release(modified, draft, registered)

    def test_json_loader_rejects_duplicate_and_nan_json(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "input.json"
            for content in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}'):
                with self.subTest(raw=content):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        _json_file(path)

    def test_synthetic_archive_packages_only_independently_supplied_labels(self):
        registration = example_draft()
        # Synthetic world labels and 4 cells only, no hidden data or oracle.
        registration["holdout_seeds"] = [41, 42]
        registration["calibration_seeds"] = [13, 14]
        digest = validate_registration(registration)
        with TemporaryDirectory() as folder:
            root = Path(folder)
            registration_path = root / "registration.json"
            _write(registration_path, registration)
            run_root = root / "raw"
            rows = []
            labels = []
            for wi, world in enumerate(registration["holdout_world_ids"]):
                for si, seed in enumerate(registration["holdout_seeds"]):
                    journal, state, _ = _run_cell(seed=seed)
                    directory = f"cell-{wi:03d}-{si:03d}"
                    file_paths = {
                        "journal_path": directory + "/journal.jsonl",
                        "replay_journal_path": directory + "/replay-journal.jsonl",
                        "causal_state_path": directory + "/causal-state.json",
                        "replay_causal_state_path": directory + "/replay-state.json",
                    }
                    for k, file in file_paths.items():
                        destination = run_root / file
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(
                            journal if "journal" in k else state
                        )
                    rows.append({
                        "world_id": world, "seed": seed,
                        "world_sha256": registration["holdout_world_sha256"][world],
                        "journal_sha256": sha256_hex(journal),
                        "causal_state_sha256": sha256_hex(state),
                        **file_paths,
                    })
                    labels.append({
                        "world_id": world, "seed": seed,
                        "known_cause_cases": [],
                        "naturally_acquired_false_candidates": [],
                    })
            _write(run_root / "operator-run-index.json", {
                "protocol_version": RUN_VERSION,
                "registration_digest": digest,
                "frozen_implementation_commit":
                    registration["frozen_implementation_commit"],
                "runs": rows,
            })
            annotations = root / "annotations.json"
            _write(annotations, {
                "protocol_version": ANNOTATIONS_VERSION,
                "registration_digest": digest, "runs": labels,
            })
            evidence = root / "heldout.json"
            custody = root / "raw-index.json"
            report = package_evidence(
                registration_path=registration_path, runs_root=run_root,
                annotations_path=annotations, evidence_path=evidence,
                raw_index_path=custody,
            )
            self.assertEqual(report["assessment"], "not_evaluable")
            self.assertFalse(report["golden_stage9_frozen"])
            self.assertIsNone(report["scientific_verdict"])
            self.assertEqual(
                json.loads(evidence.read_text())["runs"][0]["known_cause_cases"],
                [],
            )
            with self.assertRaisesRegex(ValueError, "exists"):
                package_evidence(
                    registration_path=registration_path, runs_root=run_root,
                    annotations_path=annotations, evidence_path=evidence,
                    raw_index_path=custody,
                )
            # A made-up observation cannot be passed off as bench evidence.
            first = labels[0]
            first["known_cause_cases"] = [{
                "id": "forged-case", "episode_ref": "fake",
                "observation_ref": "not-a-journal-event",
                "ground_truth": "self", "attribution": "self_compatible",
            }]
            _write(annotations, {
                "protocol_version": ANNOTATIONS_VERSION,
                "registration_digest": digest, "runs": labels,
            })
            with self.assertRaisesRegex(ValueError, "absent from raw journal"):
                package_evidence(
                    registration_path=registration_path, runs_root=run_root,
                    annotations_path=annotations, evidence_path=root / "new.json",
                    raw_index_path=root / "new-index.json",
                )


if __name__ == "__main__":
    unittest.main()
