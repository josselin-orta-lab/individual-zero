"""Pure Stage8-E2 two-technical-repetition gate, NO SCIENCE.

Never runs a World. Treat all receipts as claims until each full original
archive has been inspected by the independent original-gzip auditor. A receipt
alone or software CI pass does not prove that inspection happened.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from i3.lab import stage8e2_preexposure_schedule as P

SCHEMA = "i3-stage8e2-two-source-exact-technical-repetitions/v0"
RECEIPT_SCHEMA = "i3-stage8e2-full-native-technical-preexposure/v0/technical-receipt"
PASS = "STAGE8E2_FULL_NATIVE_TECHNICAL_ORIGINALS_SEALED_NO_SCIENCE"
HEX = re.compile(r"[0-9a-f]{64}\Z")
HEAD = re.compile(r"[0-9a-f]{40}\Z")
REQUIRED = frozenset((
    "schema", "status", "source_git_head", "source_files_sha256",
    "python_version", "allocation_sha256", "root_commitment_sha256",
    "g2_heldout_worlds_sha256", "archive_root",
    "original_lives_audited", "mutations_reconstructed", "phase_count",
    "phase_chain_sha256", "scientific_admission", "no_retry",
))
EXPECTED_BY_GEN = (P.EXPECTED_G0, P.EXPECTED_G1, P.EXPECTED_G2)


def combine(source_git_head: str, source_files_sha256: str,
            receipts: dict[str, dict]) -> dict:
    """Two same-source technical passes, disjoint roots/custody/Worlds."""
    if (type(source_git_head) is not str or not HEAD.fullmatch(source_git_head)
            or type(source_files_sha256) is not str
            or not HEX.fullmatch(source_files_sha256)
            or type(receipts) is not dict
            or set(receipts) != {"3.11", "3.12"}):
        raise PermissionError("two pinned source-exact technical receipts required")
    for version in ("3.11", "3.12"):
        row = receipts[version]
        if (type(row) is not dict or set(row) != REQUIRED
                or row.get("schema") != RECEIPT_SCHEMA
                or row.get("status") != PASS
                or row.get("source_git_head") != source_git_head
                or row.get("source_files_sha256") != source_files_sha256
                or row.get("python_version") != version
                or type(row.get("original_lives_audited")) is not int
                or row["original_lives_audited"] != P.EXPECTED_TOTAL
                or type(row.get("mutations_reconstructed")) is not int
                or row["mutations_reconstructed"] != 6144
                or type(row.get("phase_count")) is not int
                or row["phase_count"] != 9
                or row.get("scientific_admission") is not False
                or row.get("no_retry") is not True
                or any(type(row.get(k)) is not str or not HEX.fullmatch(row[k])
                       for k in ("allocation_sha256", "root_commitment_sha256",
                                 "g2_heldout_worlds_sha256", "phase_chain_sha256"))):
            raise PermissionError("incomplete or foreign native technical repetition")
        archive = row.get("archive_root")
        if (type(archive) is not str or not archive.startswith("/")
                or str(Path(archive).resolve()) != archive):
            raise PermissionError("noncanonical technical archive root")
    paths = [Path(receipts[v]["archive_root"]) for v in ("3.11", "3.12")]
    if (paths[0] == paths[1] or paths[0].is_relative_to(paths[1])
            or paths[1].is_relative_to(paths[0])):
        raise PermissionError("two technical archives cannot overlap")
    for key in ("allocation_sha256", "root_commitment_sha256",
                "g2_heldout_worlds_sha256", "phase_chain_sha256"):
        if receipts["3.11"][key] == receipts["3.12"][key]:
            raise PermissionError("reused technical entropy, heldout Worlds or evidence chain")
    result = {
        "schema": SCHEMA,
        "status": "TWO_TECHNICAL_RECEIPTS_STRUCTURALLY_ACCEPTED_NO_SCIENCE",
        "source_git_head": source_git_head,
        "source_files_sha256": source_files_sha256,
        "python_versions": ["3.11", "3.12"],
        "per_repetition_lives": P.EXPECTED_TOTAL,
        "total_original_lives_claimed": 2 * P.EXPECTED_TOTAL,
        "total_mutations_claimed": 12288,
        "receipt_sha256": {
            v: sha256(json.dumps(receipts[v], sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest()
            for v in ("3.11", "3.12")
        },
        "original_archives_independently_rehashed_in_this_gate": False,
        "scientific_admission": False,
        "science_lives_generated": 0,
        "science_verdict": "NOT_ISSUED",
    }
    return result


def main() -> None:
    import sys
    if len(sys.argv) != 5:
        raise SystemExit("usage: HEAD SOURCE_SHA TECH311_RECEIPT TECH312_RECEIPT")
    _, head, source, p311, p312 = sys.argv
    a = json.loads(Path(p311).read_bytes())
    b = json.loads(Path(p312).read_bytes())
    print(json.dumps(combine(head, source, {"3.11": a, "3.12": b}),
                     sort_keys=True))


if __name__ == "__main__":
    main()
