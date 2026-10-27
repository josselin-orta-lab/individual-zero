"""Issue #336: reject unreviewed, stale or duplicated experimental source pins."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import test_i1_artifact_parity as parity
from unittest.mock import patch
from test_i1_artifact_parity import (
    _ISOLATED_PINS_DIR, _approved_isolated_experimental,
    _load_isolated_source_pins,
)


class IsolatedSourcePinTest(unittest.TestCase):
    def test_exact_reviewed_sources_and_missing_output(self):
        pins=_load_isolated_source_pins(_ISOLATED_PINS_DIR)
        self.assertTrue({
            "i1/experimental/intention_continuity.py",
            "i1/experimental/local_opportunity_selection.py",
            "i1/experimental/experienced_place_relevance.py",
            "i1/experimental/critical_alert_wake.py",
        }.issubset(pins))
        self.assertEqual(len(pins), len(list(_ISOLATED_PINS_DIR.glob("issue-*.json"))))
        with TemporaryDirectory() as folder:
            root=Path(folder)
            for rel in pins:
                artifact=root/rel
                artifact.parent.mkdir(parents=True,exist_ok=True)
                artifact.write_bytes(b"test-output-existence-only")
                self.assertTrue(_approved_isolated_experimental(root,rel),rel)
                artifact.unlink()
                self.assertFalse(_approved_isolated_experimental(root,rel),rel)
            self.assertFalse(_approved_isolated_experimental(root,"i1/experimental/unreviewed.py"))
            self.assertFalse(_approved_isolated_experimental(root,"i1/modules/competition.py"))

    def test_valid_fifth_manifest_and_tampering(self):
        import hashlib
        with TemporaryDirectory() as folder:
            fake=Path(folder)
            pins=fake/"manifests"
            pins.mkdir()
            native=fake/"src/i1/experimental/fifth_module.py"
            native.parent.mkdir(parents=True)
            native.write_bytes(b"# fifth verified source\\n")
            blob=b"blob "+str(len(native.read_bytes())).encode()+b"\0"+native.read_bytes()
            record=dict(schema="i1-isolated-source-pin-v1",issue=410,
                        generated="i1/experimental/fifth_module.py",
                        native="src/i1/experimental/fifth_module.py",
                        blob_sha1=hashlib.sha1(blob).hexdigest())
            (pins/"issue-410.json").write_text(json.dumps(record))
            self.assertIn(record["generated"],_load_isolated_source_pins(pins))
            out=fake/"built"
            generated=out/record["generated"]
            generated.parent.mkdir(parents=True)
            generated.write_text("# generated")
            with patch.object(parity,"_ISOLATED_PINS_DIR",pins), patch.object(parity,"ROOT",fake):
                self.assertTrue(parity._approved_isolated_experimental(out,record["generated"]))
                native.write_bytes(b"# tampered source\\n")
                self.assertFalse(parity._approved_isolated_experimental(out,record["generated"]))

    def test_fail_closed_bad_manifest_and_duplicate(self):
        base=dict(schema="i1-isolated-source-pin-v1",issue=410,
                  generated="i1/experimental/safe_example.py",
                  native="src/i1/experimental/safe_example.py",
                  blob_sha1="a"*40)
        with TemporaryDirectory() as folder:
            root=Path(folder)
            first=root/"issue-410.json"
            def write(row):
                first.write_text(json.dumps(row),encoding="utf-8")
            write(base)
            self.assertEqual(_load_isolated_source_pins(root)[base["generated"]],
                             (base["native"],base["blob_sha1"]))
            for change in (dict(native="../escape.py"),
                           dict(blob_sha1="invalid"),
                           dict(issue=411),
                           dict(generated="i1/experimental/../escape.py"),
                           dict(schema="future")):
                write(base | change)
                with self.subTest(change=change),self.assertRaises(ValueError):
                    _load_isolated_source_pins(root)
            write(base)
            (root/"issue-411.json").write_text(json.dumps(base | {"issue":411}))
            with self.assertRaises(ValueError):
                _load_isolated_source_pins(root)
        with self.assertRaises(ValueError):
            _load_isolated_source_pins(Path("/missing-i1-source-pins-336"))


    def test_stale_but_well_formed_blob_and_absent_native_source(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            record=json.loads((_ISOLATED_PINS_DIR/"issue-326.json").read_text())
            rel=record["generated"]
            output=root/"generated"
            artifact=output/rel
            artifact.parent.mkdir(parents=True,exist_ok=True)
            artifact.write_bytes(b"exists-but-not-an-attestation")
            pins=root/"reviewed-pins"
            pins.mkdir()
            manifest=pins/"issue-326.json"
            record["blob_sha1"]="0"*40
            manifest.write_text(json.dumps(record),encoding="utf-8")
            with patch.object(parity,"_ISOLATED_PINS_DIR",pins):
                self.assertFalse(parity._approved_isolated_experimental(output,rel))
            record["generated"]="i1/experimental/unknown_future_module.py"
            record["native"]="src/"+record["generated"]
            manifest.write_text(json.dumps(record),encoding="utf-8")
            future=output/record["generated"]
            future.write_bytes(b"not-in-native-tree")
            with patch.object(parity,"_ISOLATED_PINS_DIR",pins):
                self.assertFalse(parity._approved_isolated_experimental(
                    output,record["generated"]))


if __name__=="__main__":
    unittest.main()
