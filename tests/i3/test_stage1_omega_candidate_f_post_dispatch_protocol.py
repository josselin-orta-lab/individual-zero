"""Lock the fresh omega-F rerun to the exact #1123 falsifier source."""
from hashlib import sha1
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

FROZEN_BLOB = "3a5cb6003d4555e9a62c6b204cfffcdd06c5346f"


class CandidateFOmegaPostDispatchProtocolTests(unittest.TestCase):
    def test_falsifier_source_is_byte_identical_to_invalid_first_rerun(self):
        path = (
            Path(__file__).resolve().parents[2]
            / "src/i3/lab/stage1_omega_candidate_f_falsifier.py")
        data = path.read_bytes()
        payload = (
            b"blob " + str(len(data)).encode("ascii") + b"\0" + data)
        self.assertEqual(sha1(payload).hexdigest(), FROZEN_BLOB)


if __name__ == "__main__":
    unittest.main()
