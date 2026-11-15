"""Stage6 sealed native-shaped originals -> parent claims, strictly NO World.

The 11,520 archive entries in the integration fixture are *manufactured*;
they are not native run_life output, experimental lives or authorized seeds.
No science protocol, active surface, registry, or owner authorisation changes.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from copy import deepcopy
import gzip
from hashlib import sha256
import inspect
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import stage6_light_original_selection_bridge as v

_THIS_DIR = Path(__file__).resolve().parent
_native_helpers = runpy.run_path(str(_THIS_DIR / "test_stage6_light_native_custody_preflight.py"))
_selection_helpers = runpy.run_path(str(_THIS_DIR / "test_stage6_light_selection_parent_preflight.py"))
_native_case = _native_helpers["native_case"]
_source = _native_helpers["_source"]
_mock_fixture = _selection_helpers["fixture"]


def _one_original(root: Path):
    """A stand-alone fictitious original, for negative byte tests only."""
    pin, _ = _source()
    identity, life = _native_case(0, 0, "shared", 0, "stable", 0, pin)
    payload = v.custody._canonical({"identity": identity, "life": life})
    packed = gzip.compress(payload, mtime=0)
    name = "life-000.json.gz"
    (root / name).write_bytes(packed)
    entry = {"file": name, "identity": identity,
             "sha256": sha256(packed).hexdigest(),
             "uncompressed_sha256": sha256(payload).hexdigest()}
    return entry, pin


def _full_fake_archives(root: Path):
    """Construct source-correct *invented* originals and genotype mutation tree."""
    founders, offspring, _, persistence, toy_draws = _mock_fixture(tuple(range(16)))
    gene_map = {(x["population"], 0, "shared", x["slot"]): x["genome"] for x in founders}
    gene_map.update({(x["population"], x["generation"], x["arm"], x["slot"]): x["genome"]
                     for x in offspring})
    persist_map = {(x["population"], x["generation"], x["arm"], x["slot"],
                    x["family"], x["repeat"]): x for x in persistence}
    pin, _ = _source()
    archive_dirs, cases, seals = {}, {}, {}
    for g in (0, 1, 2):
        directory = root / f"G{g}"
        directory.mkdir()
        archive_dirs[g] = directory
        files, cases[g] = [], []
        i = 0
        for p in range(16):
            for arm in (("shared",) if g == 0 else v.ARMS):
                for slot in range(24):
                    genome = gene_map[p, g, arm, slot]
                    digest = v.ancestry._digest(genome)
                    for family in v.custody.FAMILIES:
                        for rep in (0, 1):
                            identity, life = _native_case(p, g, arm, slot, family, rep, pin)
                            identity["genome_sha256"] = digest
                            life["genome"] = digest
                            life["manifest"]["genome"] = genome
                            life["manifest_id"] = v.custody._digest(life["manifest"])
                            if g <= 1:
                                actual = persist_map[p, g, arm, slot, family, rep]
                                life["steps_lived"] = actual["steps_lived"]
                                life["terminal"] = "censored" if actual["censored"] else "dead"
                                life["death_causes"] = [] if actual["censored"] else ["fixture-only"]
                            raw = v.custody._canonical({"identity": identity, "life": life})
                            packed = gzip.compress(raw, mtime=0)
                            name = f"life-{i:03d}.json.gz"
                            (directory / name).write_bytes(packed)
                            files.append({"file": name, "identity": identity,
                                          "sha256": sha256(packed).hexdigest(),
                                          "uncompressed_sha256": sha256(raw).hexdigest()})
                            cases[g].append(identity)
                            i += 1
        meta = {"schema": v.custody.SCHEMA, "status": "GENERATED", "planned": i,
                "generated": i, "files": files, "failure": None}
        manifest = v.custody._canonical(meta)
        seals[g] = sha256(manifest).hexdigest()
        (directory / "MANIFEST.json").write_bytes(manifest)
        (directory / "MANIFEST.sha256").write_text(seals[g] + "\n", encoding="ascii")
    draws = [{"schema": v.DRAW_SCHEMA, "population": x["population"],
              "generation": x["generation"], "arm": x["arm"], "slot": x["slot"],
              "parent_slot": x["parent_slot"], "draw_seed": x["draw_seed"],
              "prior_generation_manifest_sha256": seals[x["generation"] - 1],
              "parent_genome_sha256": x["parent_genome_sha256"],
              "offspring_genome_sha256": x["genome_sha256"]} for x in toy_draws]
    people = defaultdict(dict)
    for row in persistence:
        key = (row["population"], row["generation"], row["arm"], row["slot"])
        people[key][(row["family"], row["repeat"])] = (row["censored"], row["steps_lived"])
    native_index = [
        {"population": p, "generation": g, "arm": arm, "slot": slot,
         "genome_sha256": v.ancestry._digest(genome)}
        for (p, g, arm, slot), genome in gene_map.items()
    ]
    return archive_dirs, cases, founders, offspring, draws, pin, seals, people, native_index


class OriginalSelectionSingleReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="i3-stage6-fake-receipt-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.entry, self.pin = _one_original(self.root)

    def read(self, entry=None):
        return v._read_persistence_original(
            self.root, self.entry if entry is None else entry, generation=0,
            protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED", source_pin=self.pin,
            source_head="c" * 40)

    def test_extract_from_digest_verified_native_shaped_original(self):
        key, censored, steps = self.read()
        self.assertEqual(key, (0, 0, "shared", 0, "stable", 0))
        self.assertIs(censored, True)
        self.assertEqual(steps, 400)

    def test_byte_flip_and_gzip_damage_rejected(self):
        p = self.root / "life-000.json.gz"
        p.write_bytes(p.read_bytes() + b"altered")
        with self.assertRaises(ValueError):
            self.read()

    def test_identity_replacement_and_unsafe_file_refused(self):
        altered = deepcopy(self.entry)
        altered["identity"]["slot"] = 17
        with self.assertRaises(ValueError):
            self.read(altered)
        altered = deepcopy(self.entry)
        altered["file"] = "../../unsealed.json.gz"
        with self.assertRaises(ValueError):
            self.read(altered)

    def test_unpaid_or_invalid_terminal_original_refused_even_if_resealed(self):
        path = self.root / "life-000.json.gz"
        raw = json.loads(gzip.decompress(path.read_bytes()))
        raw["life"]["cognitive_accounting"]["totals"]["vigilance"]["unpaid"] = 0.25
        changed = v.custody._canonical(raw)
        packed = gzip.compress(changed, mtime=0)
        path.write_bytes(packed)
        entry = deepcopy(self.entry)
        entry["sha256"] = sha256(packed).hexdigest()
        entry["uncompressed_sha256"] = sha256(changed).hexdigest()
        with self.assertRaises(ValueError):
            self.read(entry)

    def test_never_runs_biology_or_grants_permission(self):
        with patch.object(v.custody, "_assert_inert", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                v.inspect_original_selection({}, {}, [], [], [], expected_protocol="fake",
                                             source_pin="a"*64, source_head="b"*40)
        for fn in (v.open_world, v.run_life, v.authorize_science):
            with self.assertRaises(PermissionError):
                fn()
        tree = ast.parse(inspect.getsource(v))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, ast.Import):
                imports.extend(x.name for x in node.names)
        self.assertFalse(any(s.startswith(("i3.runtime", "i3.modules")) for s in imports))


class OriginalSelectionCompleteFabricatedPanelTests(unittest.TestCase):
    def test_full_fabricated_originals_bridge_not_science(self):
        with tempfile.TemporaryDirectory(prefix="i3-stage6-11520-fake-originals-") as tmp:
            dirs, cases, founders, offspring, draws, pin, seals, people, native_index = _full_fake_archives(Path(tmp))
            input_manifests = {g: (dirs[g] / "MANIFEST.json").read_bytes() for g in (0, 1, 2)}
            result = v.inspect_original_selection(dirs, cases, founders, offspring, draws,
                          expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED",
                          source_pin=pin, source_head="c"*40)
            self.assertEqual(result["status"], "SUPPLIED_NATIVE_ORIGINAL_SELECTION_SHAPE_MATCH_NOT_ADMITTED")
            self.assertEqual((result["original_lives_structurally_checked"],
                              result["selection_inputs_read_from_original_gzip"],
                              result["genotypes_joined_to_originals"],
                              result["offspring_mutations_reproduced"],
                              result["claimed_parent_draws_reproduced"]),
                             (11520, 6912, 1920, 1536, 1536))
            self.assertFalse(result["owner_authorization"])
            self.assertFalse(result["draw_seeds_independently_precommitted"])
            self.assertFalse(result["g_s_r_chronology_attested"])
            self.assertFalse(result["live_native_actions_replayed_or_verified"])
            self.assertEqual(result["new_lives_created"], 0)
            self.assertEqual(result["new_worlds_opened"], 0)
            self.assertEqual(result["science_verdict"], "NOT_ISSUED")
            self.assertEqual({g: (dirs[g] / "MANIFEST.json").read_bytes() for g in (0, 1, 2)},
                             input_manifests)
            # The *same* original-derived persistence cannot match forged S data.
            altered = deepcopy(draws)
            altered[0]["parent_slot"] = (altered[0]["parent_slot"] + 1) % 24
            with self.assertRaises(ValueError):
                v._verify_draws(draws=altered, offspring=offspring,
                                native_index=native_index, persistence=people,
                                sealed_sha=seals)
            altered = deepcopy(draws)
            altered[0]["prior_generation_manifest_sha256"] = "0"*64
            with self.assertRaises(ValueError):
                v._verify_draws(draws=altered, offspring=offspring,
                                native_index=native_index, persistence=people,
                                sealed_sha=seals)
            # The control draw seed cannot be changed without changing its parent.
            altered = deepcopy(draws)
            control = next(x for x in altered if x["arm"] == "random_parent")
            new_seed = control["draw_seed"] + 1
            import random
            while random.Random(new_seed).randrange(24) == control["parent_slot"]:
                new_seed += 1
            control["draw_seed"] = new_seed
            with self.assertRaises(ValueError):
                v._verify_draws(draws=altered, offspring=offspring,
                                native_index=native_index, persistence=people,
                                sealed_sha=seals)


if __name__ == "__main__":
    unittest.main()
