"""Issue #336: reject unreviewed, stale or duplicated experimental source pins."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from test_i1_artifact_parity import (
    _ISOLATED_PINS_DIR, _approved_isolated_experimental,
    _load_isolated_source_pins,
)


class IsolatedSourcePinTest(unittest.TestCase):
    def test_exact_reviewed_sources_and_missing_output(self):
        pins=_load_isolated_source_pins(_ISOLATED_PINS_DIR)
        self.assertEqual(set(pins), {
            "i1/experimental/intention_continuity.py",
            "i1/experimental/local_opportunity_selection.py",
            "i1/experimental/experienced_place_relevance.py",
        })
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


if __name__=="__main__":
    unittest.main()
