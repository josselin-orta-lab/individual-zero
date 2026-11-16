"""Pure, no-birth tests for independent Stage7 original-by-original audit."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from i3.lab import stage7_persistence_independent_audit as audit


HEAD = "0123456789abcdef0123456789abcdef01234567"
SOURCE = "1" * 64
GENOME = "2" * 64
WORLD = "3" * 64


def fixture_identity():
    return {
        "population": 0, "generation": 0, "arm": "shared", "slot": 1,
        "family": "stable", "repeat": 0,
        "logical_world": 0, "world_seed": 2 << 60,
        "life_seed": 3 << 60,
        "world_sha256": WORLD, "genome_sha256": GENOME,
        "source_sha256": SOURCE,
    }


def fixture_life(steps=100, terminal="dead"):
    return {
        "steps_lived": steps, "horizon": 400,
        "terminal": terminal, "trace": [{"t": i} for i in range(steps)],
        "death_causes": ["thirst"] if terminal == "dead" else [],
        "genome": GENOME, "life_seed": 3 << 60,
        "manifest": {
            "world_sha256": WORLD,
            "protocol": "stage7-test",
            "execution_model": "i3-funded-v2",
            "source": {
                "sha256": SOURCE, "git_head": HEAD,
                "working_tree_dirty": False,
            },
        },
        "cognitive_accounting": {
            "status": "SETTLED_FOR_DECLARED_WORK",
            "shortfall_steps": 0,
            "totals": {
                "energy": {"unpaid": 0.0},
                "vigilance": {"unpaid": 0.0},
            },
        },
    }


def counts(num_positive=13):
    result = {}
    for pop in range(16):
        for arm in audit.ARMS:
            steps = 130 if pop < num_positive and arm == "selected" else (
                90 if pop >= num_positive and arm == "selected" else 100)
            result[pop, arm] = {
                "lives": 144, "steps": 144 * steps, "censored": 0}
    return result


class Stage7IndependentAuditTests(unittest.TestCase):
    def test_direct_primary_only_16_population_units(self):
        test_cases = ((13, True), (12, False), (16, True), (0, False))
        for n, passed in test_cases:
            with self.subTest(n=n):
                r = audit.primary_from_counts(counts(n))
                self.assertEqual(r["positive"], n)
                self.assertEqual(r["negative"], 16-n)
                self.assertEqual(r["zero"], 0)
                self.assertEqual(r["threshold_met"], passed)
                self.assertEqual(r["status"],
                                 audit.STATUS_POS if passed else audit.STATUS_NEG)
        incomplete = counts(13)
        del incomplete[0, "selected"]
        with self.assertRaises(ValueError):
            audit.primary_from_counts(incomplete)

    def test_zero_contrast_never_counts_for_success(self):
        x = counts(13)
        for p in (0, 1):
            x[p, "selected"]["steps"] = x[p, "random_parent"]["steps"]
        r = audit.primary_from_counts(x)
        self.assertEqual(r["positive"], 11)
        self.assertEqual(r["zero"], 2)
        self.assertFalse(r["threshold_met"])

    def test_native_identity_binds_source_world_and_genome(self):
        identity = fixture_identity()
        plan = {"source_files_sha256": SOURCE}
        world = {(0, 0, "stable", 0): {
            "logical_world": 0, "world_seed": 2 << 60, "life_seed": 3 << 60}}
        self.assertEqual(audit._identity_check(identity, 0, plan, world),
                         (0, 0, "shared", 1, "stable", 0))
        bad = deepcopy(identity)
        bad["life_seed"] = 99
        with self.assertRaises(ValueError):
            audit._identity_check(bad, 0, plan, world)
        bad = deepcopy(identity)
        bad["arm"] = "selected"
        with self.assertRaises(ValueError):
            audit._identity_check(bad, 0, plan, world)

    def test_body_steps_censored_and_paid_work_match_original(self):
        plan = {"protocol": "stage7-test", "source_git_head": HEAD,
                "source_files_sha256": SOURCE}
        identity = fixture_identity()
        self.assertEqual(audit._life_check(fixture_life(), identity, plan),
                         (100, False))
        self.assertEqual(
            audit._life_check(fixture_life(400, "censored"), identity, plan),
            (400, True))
        bad = fixture_life()
        bad["trace"] = []
        with self.assertRaises(ValueError):
            audit._life_check(bad, identity, plan)
        bad = fixture_life()
        bad["cognitive_accounting"]["totals"]["energy"]["unpaid"] = 0.1
        with self.assertRaises(ValueError):
            audit._life_check(bad, identity, plan)
        bad = fixture_life()
        bad["manifest"]["source"]["git_head"] = "0"*40
        with self.assertRaises(ValueError):
            audit._life_check(bad, identity, plan)

    def test_phase_chain_rechecks_every_original_payload(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for g in range(3):
                folder = root / f"G{g}"
                folder.mkdir()
                (folder / "MANIFEST.json").write_text(
                    json.dumps({"generation": g}))
            for g in (1, 2):
                (root / f"SELECT_G{g}.json").write_text(
                    json.dumps({"generation": g, "seed": "fixed"}))
            (root / "R_FINAL_PERSISTENCE_SCIENCE.json").write_text(
                '{"science":true}')
            tip = None
            lines = []
            for i, phase in enumerate(audit.PHASES):
                if phase.startswith("SEAL_"):
                    target = root / phase.split("_")[1] / "MANIFEST.json"
                elif phase.startswith("G"):
                    target = root / phase / "MANIFEST.json"
                elif phase.startswith("SELECT_"):
                    target = root / f"{phase}.json"
                else:
                    target = root / "R_FINAL_PERSISTENCE_SCIENCE.json"
                item = {
                    "ordinal": i, "phase": phase,
                    "payload_sha256": audit.digest(target.read_bytes()),
                    "previous_sha256": tip,
                }
                item["chain_sha256"] = audit.digest(audit.canonical(item))
                tip = item["chain_sha256"]
                lines.append(json.dumps(item))
            (root / "PHASES.jsonl").write_text("\n".join(lines) + "\n")
            self.assertEqual(audit._verify_phases(
                root, {"phase_chain_sha256": tip}), tip)
            (root / "SELECT_G1.json").write_text('{"generation":1,"seed":"changed"}')
            with self.assertRaises(ValueError):
                audit._verify_phases(root, {"phase_chain_sha256": tip})

    def test_no_source_replay_or_archive_generation_on_import(self):
        with TemporaryDirectory() as temp:
            archive = Path(temp) / "never-create"
            with self.assertRaises(FileNotFoundError):
                audit.audit_full(str(Path(temp) / "nonexistent-plan.json"),
                                 str(archive), "no-result.json")
            self.assertFalse(archive.exists())


if __name__ == "__main__":
    unittest.main()
