"""Original gzip and first-person chain tampering, no native births."""
import gzip
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from i3.lab import stage8e2_independent_original_audit as A
from i3.lab import two_phase_panel as TP

SOURCE = "a" * 64
HEAD = "b" * 40


def identity():
    return {
        "population": 0, "generation": 0, "arm": "shared",
        "slot": 0, "family": "stable", "repeat": 0,
        "world_seed": 2 << 60, "world_sha256": "c"*64,
        "life_seed": 3 << 60, "genome_sha256": "d"*64,
        "source_sha256": SOURCE,
    }


def synthetic_trace_sealed_life():
    # Test-only synthetic trace with the exact native v2 digest equations.
    genome, world, life_seed, horizon = "d"*64, "fake-f0", 3 << 60, 400
    manifest_id = "e"*64
    head = sha256(json.dumps(
        [genome, world, life_seed, horizon],
        separators=(",", ":")).encode()).hexdigest()
    evidence = manifest_id
    trace = []
    for t in (1, 2):
        core = {
            "t": t, "action": "attendre", "param": None,
            "option": "synthetic", "body": [90.0, 90.0, 90.0, 90.0, 90.0],
            "pos": [0, 0], "dead": [] if t == 1 else ["energy"],
        }
        work = {"cycles": 1, "simulated_steps": 0, "memory_items": 0, "replays": 0}
        accounts = {"energy": {"requested": 0., "paid": 0., "unpaid": 0.},
                    "vigilance": {"requested": 0., "paid": 0., "unpaid": 0.}}
        phases = {"decision": {}, "learning": {}}
        head = sha256((head + json.dumps(
            core, sort_keys=True, separators=(",", ":"))).encode()).hexdigest()
        evidence = sha256(json.dumps({
            "previous": evidence, "record": core, "work": work,
            "accounting": accounts, "funding_phases": phases,
        }, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
        trace.append({
            **core, "cognitive_work": work,
            "cognitive_accounting": accounts,
            "funding_phases": phases, "info": {},
        })
    return {
        "steps_lived": 2, "terminal": "dead", "trace": trace,
        "genome": genome, "world": world, "life_seed": life_seed,
        "horizon": horizon, "manifest_id": manifest_id,
        "trace_head": head, "evidence_head": evidence,
    }


class Stage8E2OriginalCustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.expected = [identity()]
        self.life = synthetic_trace_sealed_life()
        TP.generate(self.expected, lambda _: self.life, self.path)

    def audit(self):
        # Mock ONLY the historic shape validator for a synthetic fixture.
        # The new trace/evidence hash recomputation remains real and active.
        with patch.object(A.C, "_check_native_life", return_value=None):
            return A.audit_original_generation(
                self.path, self.expected, source_pin=SOURCE,
                source_head=HEAD, protocol="synthetic-only", generation=0)

    def _reseal(self, packet):
        path = self.path / "life-000.json.gz"
        raw = TP._dump(packet)
        packed = gzip.compress(raw, mtime=0)
        path.write_bytes(packed)
        manifest_path = self.path / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["files"][0]["sha256"] = sha256(packed).hexdigest()
        manifest["files"][0]["uncompressed_sha256"] = sha256(raw).hexdigest()
        metadata = TP._dump(manifest)
        manifest_path.write_bytes(metadata)
        (self.path / "MANIFEST.sha256").write_text(sha256(metadata).hexdigest() + "\n")

    def test_originals_rehashed_without_running_native_world(self):
        r = self.audit()
        self.assertEqual(r["original_lives_verified"], 1)
        self.assertEqual(r["six_life_rows"][0]["steps_lived"], 2)
        self.assertFalse(r["scientific_claim_authorized"])

    def test_modified_gzip_rejected(self):
        path = self.path / "life-000.json.gz"
        path.write_bytes(path.read_bytes() + b"bad")
        with self.assertRaises(ValueError):
            self.audit()

    def test_missing_original_rejected(self):
        (self.path / "life-000.json.gz").unlink()
        with self.assertRaises(ValueError):
            self.audit()

    def test_tampered_decoded_original_rejected_even_if_gzip_sha_resealed(self):
        manifest_path = self.path / "MANIFEST.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["files"][0]["uncompressed_sha256"] = "0"*64
        raw = TP._dump(manifest)
        manifest_path.write_bytes(raw)
        (self.path / "MANIFEST.sha256").write_text(sha256(raw).hexdigest() + "\n")
        with self.assertRaises(ValueError):
            self.audit()

    def test_trace_corruption_rejected_even_if_both_gzip_hashes_resealed(self):
        packet = json.loads(gzip.decompress(
            (self.path / "life-000.json.gz").read_bytes()))
        packet["life"]["trace"][0]["action"] = "dormir"
        self._reseal(packet)
        with self.assertRaisesRegex(ValueError, "chain"):
            self.audit()

    def test_paid_work_corruption_rejected_even_if_both_hashes_resealed(self):
        packet = json.loads(gzip.decompress(
            (self.path / "life-000.json.gz").read_bytes()))
        packet["life"]["trace"][0]["cognitive_work"]["cycles"] = 99
        self._reseal(packet)
        with self.assertRaisesRegex(ValueError, "chain"):
            self.audit()

    def test_duplicate_or_foreign_case_rejected(self):
        wrong = [dict(self.expected[0], slot=1)]
        with patch.object(A.C, "_check_native_life", return_value=None):
            with self.assertRaises(ValueError):
                A.audit_original_generation(
                    self.path, wrong, source_pin=SOURCE,
                    source_head=HEAD, protocol="synthetic-only", generation=0)


if __name__ == "__main__":
    unittest.main()
