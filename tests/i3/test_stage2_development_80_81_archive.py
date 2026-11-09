"""Read-only original-custody checks for the one-shot Stage-2.1 80/81 panel.

Never opens a World or executes a life. Tests immutable artifact bytes, sealed
hashes, original identities, source lock and prospectively estimated control
parameter, not favorable scientific outcomes or post-hoc success thresholds.
"""
import gzip
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "src/i3/docs/studies/stage2-replay-gate-development-80-81"
ARCHIVE = STUDY / "evidence"
SOURCE = "5d362e226f8e87df226dae5b239e26cc99072a13"
FINGERPRINT = "dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1"
PLAN_SHA = "a28606678d13bb9af18f590c328a63eb9eb82f7130c90656e4f520260d294c92"
MANIFEST_SHA = "c6893bb1b2457890e3d66680f10bf0c14b451e62c2e5c381951f1119f286b76e"
RESULT_SHA = "a6652f4d8cd1f8ccb87d8bf902ecb2eabf68ec0a548b187db140ea61dfc9401b"


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


class Stage21DevelopmentArchiveTests(unittest.TestCase):
    def test_original_manifest_is_sealed_and_all_36_gzip_originals_match(self):
        body = (ARCHIVE / "MANIFEST.json").read_bytes()
        self.assertEqual(sha256(body), MANIFEST_SHA)
        self.assertEqual((ARCHIVE / "MANIFEST.sha256").read_text().strip(), MANIFEST_SHA)
        manifest = json.loads(body)
        self.assertEqual((manifest["status"], manifest["planned"], manifest["generated"]),
                         ("GENERATED", 36, 36))
        originals = sorted(ARCHIVE.glob("life-*.json.gz"))
        self.assertEqual(len(originals), 36)
        self.assertEqual(
            [p.name for p in originals], [f"life-{i:03d}.json.gz" for i in range(36)]
        )
        blocks = set()
        for entry in manifest["files"]:
            identity = entry["identity"]
            self.assertEqual(identity["cohort"], "development")
            self.assertIn(identity["index"], (80, 81))
            self.assertIn(identity["family"], ("stable", "depletion", "pulse"))
            self.assertIn(identity["genome_seed"], (911, 912))
            self.assertIn(identity["policy"], (
                "reference", "p13_replay_gate_v1",
                "p13_replay_gate_zero_perceived_cost_v1"))
            p = ARCHIVE / entry["file"]
            compressed = p.read_bytes()
            self.assertEqual(sha256(compressed), entry["sha256"], p.name)
            self.assertEqual(sha256(gzip.decompress(compressed)),
                             entry["uncompressed_sha256"], p.name)
            blocks.add((identity["family"], identity["index"],
                        identity["genome_seed"], identity["policy"]))
        self.assertEqual(len(blocks), 36)

    def test_full_result_is_exact_and_predeclared_replay_mean_is_frozen(self):
        body = (ARCHIVE / "SCIENTIFIC_RESULT.json").read_bytes()
        self.assertEqual(sha256(body), RESULT_SHA)
        report = json.loads(body)
        self.assertEqual(report["source_sha"], SOURCE)
        self.assertEqual(report["transport_fingerprint"], FINGERPRINT)
        self.assertEqual(report["plan_sha256"], PLAN_SHA)
        self.assertEqual(report["manifest_sha256"], MANIFEST_SHA)
        self.assertEqual(report["status"], "COMPLETE")
        self.assertEqual(report["continuation"], "PASS")
        self.assertTrue(report["no_retry"])
        self.assertEqual((report["planned"], report["generated"], report["reduced"]),
                         (36, 36, 36))
        self.assertEqual(len(report["rows"]), 36)
        self.assertFalse(any(report["invariant_failures"].values()))
        gate = [row for row in report["rows"] if row["policy"] == "p13_replay_gate_v1"]
        self.assertEqual(len(gate), 12)
        replays = sum(row["replays"] for row in gate)
        sleep_steps = sum(row["sleep_steps"] for row in gate)
        self.assertEqual((replays, sleep_steps), (5532, 867))
        self.assertAlmostEqual(
            report["summary"]["random_equal_mean_parameter"]["value"],
            replays / sleep_steps, places=12)

    def test_source_lock_and_frozen_plan_match_exposed_originals(self):
        lock = json.loads((ARCHIVE / "SOURCE_LOCK.json").read_text())
        self.assertEqual(lock["source_sha"], SOURCE)
        self.assertEqual(lock["transport_fingerprint"], FINGERPRINT)
        self.assertEqual(lock["plan_sha256"], PLAN_SHA)
        self.assertEqual(lock["manifest_sha256"], MANIFEST_SHA)
        self.assertEqual(lock["run_id"], "42641395586")
        self.assertEqual(lock["scientific_gate"], "NOT_EXECUTED")
        self.assertTrue(lock["no_retry"])
        self.assertEqual(sha256((STUDY / "PLAN.json").read_bytes()), PLAN_SHA)


if __name__ == "__main__":
    unittest.main()
