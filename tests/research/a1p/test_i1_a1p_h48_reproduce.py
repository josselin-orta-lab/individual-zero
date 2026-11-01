"""Pure negative tests: no historical birth and no archive downloads."""
import io
import unittest
import warnings
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from i1_a1p_h48_reproduce import CAPSULE_NAMES, ORIGINAL_SHA256, _validate_capsule_members, verify_inputs

class HistoricalGateTests(unittest.TestCase):
    def test_pinned_matrix(self):
        self.assertEqual(len(ORIGINAL_SHA256),8)
        self.assertEqual(len(CAPSULE_NAMES),18)
        self.assertTrue(all(len(v)==64 for v in ORIGINAL_SHA256.values()))
    def test_tampered_capsule_is_rejected(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            (root/"capsule.zip").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"):
                verify_inputs(capsule=root/"capsule.zip",originals=root)
    def test_nested_extra_and_duplicate_are_rejected(self):
        for bad in ("../escape","nested/evil.py","audit_h48.py"):
            out=io.BytesIO()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore",UserWarning)
                with zipfile.ZipFile(out,"w") as z:
                    for name in sorted(CAPSULE_NAMES):
                        z.writestr(name,b"harmless")
                    z.writestr(bad,b"unexpected")
            with zipfile.ZipFile(io.BytesIO(out.getvalue())) as z:
                with self.subTest(bad=bad),self.assertRaises(ValueError):
                    _validate_capsule_members(z)
    def test_no_birth_or_network_in_loader(self):
        src=(Path(__file__).resolve().parents[3]/"tools"/"research"/"i1_a1p_h48_reproduce.py").read_text()
        for forbidden in ("birth_i1_m11(", "run_step(", "requests.get(", "urllib.request.urlopen("):
            self.assertNotIn(forbidden,src)

if __name__=="__main__":
    unittest.main()
