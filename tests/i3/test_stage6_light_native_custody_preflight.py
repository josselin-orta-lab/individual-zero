"""No-World native-original envelope tests using fabricated v2-shaped data.

Every archived record is constructed by this test: no I3 engine, World,
run_life, genome generation or scientific study is imported or executed.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import gzip
from hashlib import sha256
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import stage6_light_native_custody_preflight as v


def _source() -> tuple[str, dict]:
    files = {"modules/mind.py": sha256(b"toy-not-an-engine").hexdigest(),
             "runtime/life.py": sha256(b"toy-not-a-life").hexdigest()}
    return v._digest(files), files


def _genome() -> dict:
    values = {name: 0.5 for name in v.GENE_KEYS}
    values.update({"gamma1": 0.75, "gamma2": 0.94, "gamma3": 0.99,
                   "theta.energy": 60.0, "alpha": 0.08,
                   "beta_u": 1.0, "n_base": 4.0, "h_max": 12.0,
                   "m_max": 128.0})
    for channel in ("energy", "food", "water", "integrity", "vigilance"):
        values[f"theta.{channel}"] = 60.0
        values[f"p.{channel}"] = 2.0
        values[f"w.{channel}"] = 1.0
    return {"schema": "i3-genome-v4", "genes": values}


def native_case(p: int, g: int, arm: str, slot: int,
                family: str, repeat: int, source_pin: str) -> tuple[dict, dict]:
    coord = v.logical_world(p, g, family, repeat)
    world = {"name": f"fake-not-World-{coord}", "width": 5, "height": 5,
             "spawn": [0, 0], "body": [60.0]*5, "laws": {},
             "water": [], "food": [], "token_effects": [], "changes": []}
    genome = _genome()
    life_seed = 100000 + coord
    identity = {
        "population": p, "generation": g, "arm": arm, "slot": slot,
        "family": family, "repeat": repeat, "logical_world": coord,
        "world_seed": 4000000 + coord, "life_seed": life_seed,
        "genome_sha256": v._digest(genome), "world_sha256": v._digest(world),
        "source_sha256": source_pin,
    }
    source_sha, files = _source()
    assert source_sha == source_pin
    manifest = {"schema": "i3-life-manifest/v2", "execution_model": "i3-funded-v2",
                "protocol": "FAKE_NATIVE_SHAPE_NOT_APPROVED", "source": {"sha256": source_pin, "files": files,
                           "git_head": "c"*40, "working_tree_dirty": False},
                "python": {"implementation": "CPython", "version": "3.12.3"},
                "world": world, "world_sha256": identity["world_sha256"],
                "genome": genome, "life_seed": life_seed, "horizon": 400}
    ca = {"schema": "i3-cognitive-funding/v2", "status": "SETTLED_FOR_DECLARED_WORK",
          "totals": {c: {"requested": 0.5, "paid": 0.5, "unpaid": 0.0}
                     for c in ("energy", "vigilance")},
          "shortfall_steps": 0, "pending_replays": 0,
          "pending_energy": 0.0, "pending_vigilance": 0.0,
          "learning_updates": 1, "replays_executed": 0,
          "inactive_steps": 0}
    life = {"manifest": manifest, "manifest_id": v._digest(manifest),
            "evidence_head": "a" * 64, "trace_head": "b" * 64,
            "world": world["name"], "life_seed": life_seed,
            "horizon": 400, "genome": identity["genome_sha256"],
            "steps_lived": 400, "terminal": "censored", "death_causes": [],
            "cognitive_accounting": ca}
    return identity, life


def _write_archive(root: Path, generation: int, source_pin: str) -> list[dict]:
    """Create original-like bytes in a temporary directory, never a native life."""
    cases = []
    files = []
    i = 0
    arms = ("shared",) if generation == 0 else v.ARMS
    for p in range(16):
        for arm in arms:
            for slot in range(24):
                for family in v.FAMILIES:
                    for repeat in range(2):
                        identity, life = native_case(p, generation, arm, slot, family, repeat, source_pin)
                        cases.append(identity)
                        payload = v._canonical({"identity": identity, "life": life})
                        compressed = gzip.compress(payload, mtime=0)
                        name = f"life-{i:03d}.json.gz"
                        (root / name).write_bytes(compressed)
                        files.append({"file": name, "sha256": sha256(compressed).hexdigest(),
                                      "uncompressed_sha256": sha256(payload).hexdigest(),
                                      "identity": identity})
                        i += 1
    manifest = {"schema": v.SCHEMA, "status": "GENERATED", "planned": len(cases),
                "generated": len(cases), "files": files, "failure": None}
    body = v._canonical(manifest)
    (root / "MANIFEST.json").write_bytes(body)
    (root / "MANIFEST.sha256").write_text(sha256(body).hexdigest() + "\n", encoding="ascii")
    return cases


class Stage6NativeCustodyPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="i3-stage6-fake-originals-")
        cls.root = Path(cls.tmp.name)
        cls.source_pin, cls.source_files = _source()
        cls.cases = _write_archive(cls.root, 0, cls.source_pin)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def audit(self):
        return v.inspect_sealed_generation(
            self.root, 0, self.cases,
            expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED", source_pin=self.source_pin,
            source_head="c"*40)

    def test_source_only_no_imports_or_executable_admission(self):
        src = Path(inspect.getfile(v)).read_text(encoding="utf-8")
        tree = ast.parse(src)
        imp = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imp.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imp.append(node.module)
        self.assertFalse(any(x and (x == "i3" or x.startswith("i3.")) for x in imp))
        self.assertNotIn("from i3.", src)
        for fn in (v.open_world, v.run_life, v.authorize_science):
            with self.assertRaises(PermissionError):
                fn(source_pin="fake")

    def test_actual_inert_method_is_required(self):
        m = v._assert_inert()
        self.assertEqual(m["status"], "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE")
        fake = deepcopy(m)
        fake["authorization"]["worlds_allowed"] = True
        with patch("pathlib.Path.read_text", return_value=json.dumps(fake)):
            with self.assertRaises(PermissionError):
                v.inspect_sealed_generation(
                    self.root, 0, self.cases,
                    expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED", source_pin=self.source_pin,
            source_head="c"*40)

    def test_full_fake_g0_original_shape_read_only(self):
        original = (self.root / "MANIFEST.json").read_bytes()
        result = self.audit()
        self.assertEqual(result["status"], "STRUCTURAL_SHAPE_PASS_ONLY_NOT_ADMITTED")
        self.assertEqual(result["checked_native_records"], 2304)
        self.assertEqual(result["paired_opportunities_checked"], 96)
        self.assertEqual(result["genome_contexts_checked"], 384)
        self.assertEqual(result["new_worlds_opened"], 0)
        self.assertEqual(result["new_lives_created"], 0)
        self.assertFalse(result["owner_authorization"])
        self.assertFalse(result["source_bytes_against_checkout_verified"])
        self.assertFalse(result["genome_mutation_chain_verified"])
        self.assertEqual(result["science_verdict"], "NOT_ISSUED")
        self.assertEqual((self.root / "MANIFEST.json").read_bytes(), original)

    def test_required_case_count_and_source_pin_are_not_authorizations(self):
        with self.assertRaises(ValueError):
            v.inspect_sealed_generation(self.root, 0, self.cases[:-1],
                                        expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED", source_pin=self.source_pin,
            source_head="c"*40)
        with self.assertRaises(ValueError):
            v.inspect_sealed_generation(self.root, 0, self.cases,
                                        expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED", source_pin="madeup", source_head="c"*40)
        swapped = deepcopy(self.cases)
        swapped[1] = deepcopy(swapped[0])
        with self.assertRaises(ValueError):
            v.inspect_sealed_generation(self.root, 0, swapped,
                                        expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED", source_pin=self.source_pin,
            source_head="c"*40)

    def test_invalid_native_life_receipts_rejected_before_any_reduction(self):
        identity, life = native_case(0, 0, "shared", 0, "stable", 0, self.source_pin)
        def bad(mutator):
            alt = deepcopy(life)
            mutator(alt)
            with self.assertRaises(ValueError):
                v._check_native_life(identity, alt, self.source_pin, "c"*40,
                                     "FAKE_NATIVE_SHAPE_NOT_APPROVED")
        with self.subTest("source files changed"):
            bad(lambda x: x["manifest"]["source"]["files"].update({"fake.py": "a"*64}))
        with self.subTest("world snapshot changed"):
            bad(lambda x: x["manifest"]["world"].update({"water": "oracle"}))
        with self.subTest("missing terminal hashes"):
            bad(lambda x: x.update({"trace_head": "bad"}))
        with self.subTest("hidden alternate policy"):
            bad(lambda x: x["manifest"].update({"experimental_policy": {"name":"alternative"}}))
        with self.subTest("falsely censored before horizon"):
            bad(lambda x: x.update({"steps_lived": 399}))
        with self.subTest("missing death causes"):
            bad(lambda x: x.update({"terminal": "dead"}))
        with self.subTest("unpaid energy"):
            bad(lambda x: x["cognitive_accounting"]["totals"]["energy"].update({"unpaid": 0.1}))
        with self.subTest("unsettled energy"):
            bad(lambda x: x["cognitive_accounting"].update({"shortfall_steps": 1}))
        with self.subTest("inherited world fact"):
            bad(lambda x: x["manifest"]["genome"].update({"remembered_map": {"water": 1}}))

    def test_nonfinite_and_forged_fields_rejected(self):
        identity, life = native_case(0, 0, "shared", 0, "stable", 0, self.source_pin)
        bad = deepcopy(life)
        bad["cognitive_accounting"]["totals"]["vigilance"]["paid"] = float("nan")
        with self.assertRaises(ValueError):
            v._check_native_life(identity, bad, self.source_pin, "c"*40,
                                 "FAKE_NATIVE_SHAPE_NOT_APPROVED")
        bad = deepcopy(identity)
        bad["oracle_reward"] = 10
        with self.assertRaises(ValueError):
            v._case_key(bad, 0)
        bad = deepcopy(identity)
        bad["generation"] = True
        with self.assertRaises(ValueError):
            v._case_key(bad, 0)
        bad = deepcopy(identity)
        bad["world_seed"] = -1
        with self.assertRaises(ValueError):
            v._case_key(bad, 0)

    def test_corrupted_gzip_is_rejected_with_no_repair_or_retry(self):
        original = self.root / "life-000.json.gz"
        b = original.read_bytes()
        try:
            original.write_bytes(b[:-20] + b"invalid-original")
            with self.assertRaises(ValueError):
                self.audit()
        finally:
            original.write_bytes(b)
        self.assertEqual(original.read_bytes(), b)

    def test_changed_manifest_digest_prevents_archive_access(self):
        f = self.root / "MANIFEST.sha256"
        original = f.read_bytes()
        try:
            f.write_text("0"*64 + "\n")
            with self.assertRaises(ValueError):
                self.audit()
        finally:
            f.write_bytes(original)

    def test_unsafe_manifest_filename_rejected_before_file_read(self):
        f = self.root / "MANIFEST.json"
        h = self.root / "MANIFEST.sha256"
        original, seal = f.read_bytes(), h.read_bytes()
        try:
            decoded = json.loads(original)
            decoded["files"][0]["file"] = "../../outside.json.gz"
            altered = v._canonical(decoded)
            f.write_bytes(altered)
            h.write_text(sha256(altered).hexdigest()+"\n")
            with self.assertRaises(ValueError):
                self.audit()
        finally:
            f.write_bytes(original)
            h.write_bytes(seal)

    def test_extra_original_or_symlink_prevents_claim_of_complete_custody(self):
        extra = self.root / "hidden-original.json.gz"
        extra.write_bytes(b"not-a-sealed-file")
        try:
            with self.assertRaises(ValueError):
                self.audit()
        finally:
            extra.unlink()

    def test_bomb_header_limit_refuses_oversized_original(self):
        bomb = gzip.compress(b"Z"*(v.MAX_ORIGINAL_BYTES+1), mtime=0)
        with self.assertRaises(ValueError):
            v._gzip_limited(bomb)

    def test_three_generation_original_shape_and_disjoint_claims(self):
        # All 11,520 records here are manufactured native-shaped dictionaries,
        # not a single run_life output; no source or World is opened.
        with tempfile.TemporaryDirectory(prefix="i3-stage6-three-generation-fake-") as tmp:
            roots = {0: self.root, 1: Path(tmp) / "G1", 2: Path(tmp) / "G2"}
            expected = {0: self.cases}
            for g in (1, 2):
                roots[g].mkdir()
                expected[g] = _write_archive(roots[g], g, self.source_pin)
            report = v.inspect_three_generation_shape(
                roots, expected, expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED",
                source_pin=self.source_pin, source_head="c"*40)
            self.assertEqual(report["record_counts"], [2304, 4608, 4608])
            self.assertEqual(report["checked_fabricated_or_supplied_records"], 11520)
            self.assertEqual(report["symbolic_world_coordinates_checked"], 288)
            self.assertFalse(report["owner_authorization"])
            self.assertFalse(report["scientific_independence_verified"])
            self.assertFalse(report["parent_selection_and_mutations_verified"])
            altered = deepcopy(expected)
            altered[2][0]["world_seed"] = expected[0][0]["world_seed"]
            with self.assertRaises(ValueError):
                v.inspect_three_generation_shape(
                    roots, altered, expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED",
                    source_pin=self.source_pin, source_head="c"*40)
            altered = deepcopy(expected)
            altered[1][0]["world_seed"] = 90_003
            # First test of this malformed paired claim fails before source reads.
            with self.assertRaises(ValueError):
                v.inspect_three_generation_shape(
                    roots, altered, expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED",
                    source_pin=self.source_pin, source_head="c"*40)

    def test_generation_logical_coordinates_and_no_admitted_seeds(self):
        self.assertEqual(v.logical_world(0,0,"stable",0),0)
        self.assertEqual(v.logical_world(15,2,"pulse",1),287)
        for args in [(-1,0,"stable",0),(0,3,"pulse",1),(0,0,"foo",0),(0,0,"stable",3)]:
            with self.assertRaises(ValueError):
                v.logical_world(*args)


if __name__ == "__main__":
    unittest.main()
