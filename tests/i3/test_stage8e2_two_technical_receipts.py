"""Source-exact two-repetition receipts: pure synthetic evidence tests."""
from copy import deepcopy
import unittest
from i3.lab import stage8e2_two_technical_receipts as C

HEAD = "0123456789abcdef0123456789abcdef01234567"
SOURCE = "a"*64


def claims():
    base = dict(
        schema=C.RECEIPT_SCHEMA, status=C.PASS,
        source_git_head=HEAD, source_files_sha256=SOURCE,
        python_version="3.11", allocation_sha256="b"*64,
        root_commitment_sha256="c"*64, g2_heldout_worlds_sha256="d"*64,
        archive_root="/tmp/new-stage8e2-311",
        original_lives_audited=64512, mutations_reconstructed=6144,
        phase_count=9, phase_chain_sha256="e"*64,
        scientific_admission=False, no_retry=True,
    )
    return {"3.11": base, "3.12": {
        **base, "python_version": "3.12",
        "allocation_sha256": "f"*64,
        "root_commitment_sha256": "1"*64,
        "g2_heldout_worlds_sha256": "2"*64,
        "phase_chain_sha256": "3"*64,
        "archive_root": "/tmp/new-stage8e2-312",
    }}


class TwoTechnicalReceiptsTests(unittest.TestCase):
    def test_both_source_exact_disjoint_complete_and_not_science(self):
        row = C.combine(HEAD, SOURCE, claims())
        self.assertEqual(row["total_original_lives_claimed"], 129024)
        self.assertEqual(row["total_mutations_claimed"], 12288)
        self.assertFalse(row["scientific_admission"])
        self.assertFalse(row["original_archives_independently_rehashed_in_this_gate"])
        self.assertEqual(row["science_verdict"], "NOT_ISSUED")

    def test_reject_duplicate_root_world_or_archive(self):
        for field in ("allocation_sha256", "root_commitment_sha256",
                      "g2_heldout_worlds_sha256", "phase_chain_sha256",
                      "archive_root"):
            data = claims()
            data["3.12"][field] = data["3.11"][field]
            with self.subTest(field=field), self.assertRaises(PermissionError):
                C.combine(HEAD, SOURCE, data)

    def test_reject_missing_broken_source_or_result(self):
        for field, value in (
            ("original_lives_audited", 64511),
            ("mutations_reconstructed", 6143),
            ("phase_count", 8),
            ("scientific_admission", True),
            ("source_git_head", "1"*40),
            ("status", "NOT_COMPLETED"),
        ):
            data = claims()
            data["3.12"][field] = value
            with self.subTest(field=field), self.assertRaises(PermissionError):
                C.combine(HEAD, SOURCE, data)
        with self.assertRaises(PermissionError):
            C.combine(HEAD, SOURCE, {"3.11": claims()["3.11"]})


if __name__ == "__main__":
    unittest.main()
